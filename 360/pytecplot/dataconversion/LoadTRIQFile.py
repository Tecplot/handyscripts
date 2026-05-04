# coding: utf-8
#!/usr/bin/env python
"""
This file demonstrates how to read in a Cart3D "triq" file into Tecplot 360
using the PyTecplot Python module. It includes a generic reader for binary
files that adhere to the FORTRAN Record-Array format which is then used to
read in the triq file. Once the data has been read, it is then put into a
Tecplot dataset object.

Usage:
    python LoadTRIQFile.py datafile.triq
"""
import collections
import contextlib
import logging
import numpy as np
import tecplot as tp
from tecplot.constant import ZoneType, ValueLocation, PlotType

log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)


class open_fortran_record_file(object):
    """Generic FORTRAN Record file reader.

    This class is a Python context that opens a binary FORTRAN Record data file
    and allows for reading the data into numpy arrays. Here is an example of
    using this to read a Cart3D "triq" file::

        with open_fortran_record_file('data.triq') as fin:
            nVerts, nTri, nScal = fin.read_record('i4')
            verts = fin.read_record('f4', (-1, 3))
            conn = fin.read_record('i4', (-1, 3))
            comp = fin.read_record('i4')
            scalars = fin.read_record('f4', (nVerts, nScal))
    """
    def __init__(self, infile):
        self.infile = infile

    def open(self):
        self.istream = open(self.infile, 'rb')

    def close(self):
        self.istream.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def dtype(self):
        if not hasattr(self, '_dtype'):
            here = self.istream.tell()
            log.debug('here: {}'.format(here))
            try:
                for dt in ['<i4', '>i4', '<i8', '>i8']:
                    log.debug('attempt to read record using type {}'.format(dt))
                    try:
                        n = np.dtype(dt).itemsize
                        nbytes, = np.frombuffer(self.istream.read(n), dtype=dt)
                        log.debug('nbytes: {}'.format(nbytes))
                        self.istream.seek(here + n + nbytes)
                        check, = np.frombuffer(self.istream.read(n), dtype=dt)
                        log.debug('check: {}'.format(check))
                        if nbytes == check:
                            self._dtype = np.dtype(dt)
                            break
                        else:
                            log.debug('{} != {}'.format(nbytes, check))
                    except:
                        log.debug('could not seek {} bytes, resetting.'.format(nbytes))
                        self.istream.seek(here)
                        continue
                if not hasattr(self, '_dtype'):
                    raise Exception('Could not determine data type')
            finally:
                self.istream.seek(here)
        return self._dtype

    @property
    def byteorder(self):
        return self.dtype.byteorder

    @property
    def continuation_nbytes(self):
        return np.iinfo(self.dtype).max - 1

    @contextlib.contextmanager
    def reset_on_error(self):
        here = self.istream.tell()
        try:
            yield
        except:
            self.istream.seek(here)
            raise

    def read_buffer(self, dtype, size):
        with self.reset_on_error():
            buf = self.istream.read(dtype.itemsize * size)
            return np.frombuffer(buf, dtype=dtype)

    def read_single_record(self, dtype):
        with self.reset_on_error():
            nbytes, = self.read_buffer(self.dtype, 1)
            data = self.read_buffer(dtype, nbytes // dtype.itemsize)
            check, = self.read_buffer(self.dtype, 1)
            if nbytes != check:
                msg = 'Error reading array of type {}: {} != {}'
                raise Exception(msg.format(dtype, nbytes, check))
            return data

    def read_record(self, dtype, shape=(-1,)):
        """Read array data from the record file.

        The dtype can be any of the supported numpy dtypes and are probably
        either ``i4`` for 32-bit signed integers or ``f4`` for 32-bit floats.
        The endianness is handled automatically by this reader as well as
        large "continued" arrays. The array is then reshaped as per the
        **shape** parameter where ``(-1,)`` results in a ``1D`` array of the
        full size of the data.
        """
        with self.reset_on_error():
            dtype = np.dtype(dtype)
            if dtype.byteorder != self.byteorder:
                dtype = dtype.newbyteorder(self.byteorder)
            data = []
            data.append(self.read_single_record(dtype))
            while data[-1].nbytes == self.continuation_nbytes:
                data.append(self.read_single_record(dtype))
            data = np.concatenate(data)
            data.shape = shape
            return data


def read_triq_file_binary(infile):
    """Read a Cart3D triq file into local memory arrays.

    The resulting tuple contains these named arrays:
        `verts`: ``(nVerts, 3)`` array of all vertices.
        `conn`: ``(nTri, 3)`` connectivity array of all triangles.
        `comp`: Triangle component numbers. This is an array of length ``nTri``.
        `scalars`: ``(nVerts, nScal)`` array of scalars for each vertex.
    """
    with open_fortran_record_file(infile) as fin:
        nVerts, nTri, nScal = fin.read_record('i4')
        log.info('nVerts nTri nScal: {} {} {}'.format(nVerts, nTri, nScal))
        verts = fin.read_record('f4', (-1, 3))
        log.info('verts:\n{}'.format(verts))
        conn = fin.read_record('i4', (-1, 3))
        log.info('conn:\n{}'.format(conn))
        comp = fin.read_record('i4')
        log.info('comp:\n{}'.format(comp))
        scalars = fin.read_record('f4', (nVerts, nScal))
        log.info('scalars:\n{}'.format(scalars))
    Ret = collections.namedtuple('Ret', 'verts conn comp scalars')
    return Ret(verts, conn, comp, scalars)

def get_triq_data_binary(file_name):
    data = read_triq_file_binary(file_name)
    node_count = len(data.verts)
    cell_count = len(data.conn)
    num_scalars = len(data.scalars[0])
    nodes = data.verts.T
    verts = data.conn
    components = data.comp.T
    scalars = data.scalars.T
    return node_count, cell_count, num_scalars, nodes, verts, components, scalars

def get_triq_data_ascii(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        node_count, cell_count, num_scalars = lines[0].split()
        node_count = int(node_count)
        cell_count = int(cell_count)
        num_scalars = int(num_scalars)

        values = []
        for line in lines[1:]:
            values.extend(line.split())

        start = 0
        end = node_count*3
        nodes = list(map(float, values[start:end]))

        start = end
        end = start + cell_count*3
        verts = list(map(int, values[start:end]))

        start = end
        end = start + cell_count
        components = list(map(int, values[start:end]))

        start = end
        end = start + node_count*num_scalars
        scalars = list(map(float, values[start:end]))
        
        return node_count, cell_count, num_scalars, nodes, verts, components, scalars

def load_triq_file(file_name):
    """Load a Cart3D triq file into Tecplot 360.

    This will create a new dataset in the active frame or create a new frame
    if the active frame already has a dataset.
    """
    import os
    try:
        node_count, cell_count, num_scalars, nodes, verts, components, scalars = get_triq_data_ascii(file_name)
        print("Loading ASCII file")
    except:
        print("ASCII failed, trying binary")
        node_count, cell_count, num_scalars, nodes, verts, components, scalars = get_triq_data_binary(file_name)
        print("Loading binary file")

    with tp.session.suspend():
        frame = tp.active_frame()
        if frame.has_dataset:
            frame = tp.active_page().add_frame()
        ds = tp.active_frame().dataset
        ds.add_variable("X")
        ds.add_variable("Y")
        ds.add_variable("Z")
        ds.add_variable("Component")
        value_locations = [ValueLocation.Nodal, ValueLocation.Nodal, ValueLocation.Nodal, ValueLocation.CellCentered]
        for i in range(num_scalars):
            if i == 0:
                ds.add_variable("Cp")
            else:
                ds.add_variable("Scalar_{}".format(i))
            value_locations.append(ValueLocation.Nodal)
        zone = ds.add_fe_zone(ZoneType.FETriangle, os.path.basename(file_name), node_count, cell_count, locations=value_locations)
    
        xvals = nodes[0:node_count*3:3]
        yvals = nodes[1:node_count*3:3]
        zvals = nodes[2:node_count*3:3]
        
        zone.values('X')[:] = xvals
        zone.values('Y')[:] = yvals
        zone.values('Z')[:] = zvals
        zone.values('Component')[:] = components
    
        for offset,var_num in enumerate(range(4, 4+num_scalars)):
            var_values = scalars[offset:node_count*num_scalars:num_scalars]
            zone.values(var_num)[:] = var_values
    
        zero_based_verts = [v-1 for v in verts]
        zone.nodemap.array[:] = zero_based_verts
    
        tp.active_frame().plot_type = PlotType.Cartesian3D
        tp.active_frame().plot().contour(0).variable = ds.variable("Cp")
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Load or convert binary TRIQ files")
    parser.add_argument("infile", help="TRIQ file to load")
    parser.add_argument("-outfile", help="Specify an output file if you want to convert to PLT file", default=None)
    args = parser.parse_args()
    
    if not args.outfile:
        tp.session.connect()
        
    log.info('reading in file: {}'.format(args.infile))
    load_triq_file(args.infile)
    tp.active_frame().plot_type = PlotType.Cartesian3D

    if args.outfile:
        log.info('writing to file: {}'.format(args.outfile))
        tp.data.save_tecplot_plt(args.outfile)
