import tecplot as tp
from tecplot.constant import *
import math

# --- INPUTS ----
origin = (0,0,0)
axis_of_rot = 'x' # accepts x, y, or z
start_angle  = 0.0 # angle you want, in radian
finish_angle = math.pi / 2
total_slices = 10



tp.session.connect()
ds = tp.active_frame().dataset
axis_dict = {'x': (1,0,0), 'y': (0,1,0), 'z': (0,0,1)}

def starting_normal_from_axis(axis_of_rot):
    # any perp axis is valid, just not collinear.
    if axis_of_rot == 'x':
        return (0,1,0)
    elif axis_of_rot == 'y':
        return (1,0,0)
    elif axis_of_rot == 'z':
        return (0,1,0)
    else:
        raise "axis must be 'x', 'y', or 'z' "

def rotate_vector(n, axis, theta):
    # apparently, full 3D rotation matrix is needed...
    nx, ny, nz = n
    kx, ky, kz = axis

    ct = math.cos(theta)
    st = math.sin(theta)

    # cross prod k x n
    cx = ky*nz - kz*ny
    cy = kz*nx - kx*nz
    cz = kx*ny - ky*nx

    # dot prod k n
    dot = kx*nx + ky*ny + kz*nz

    return (
        nx*ct + cx*st + kx*dot*(1-ct),
        ny*ct + cy*st + ky*dot*(1-ct),
        nz*ct + cz*st + kz*dot*(1-ct))


if __name__ == "__main__":

    tot = max(total_slices, 2)
    angle_interval = abs(finish_angle - start_angle) / (tot - 1)
    angles = [start_angle + i*angle_interval for i in range(total_slices)]

    axis_vec = axis_dict[axis_of_rot]
    n0 = starting_normal_from_axis(axis_of_rot)
    for i, angle in enumerate(angles):

        # apply rotation to given normal
        n = rotate_vector(n0, axis_vec, angle)
        tp.data.extract.extract_slice(
            origin=origin,
            normal=n,
            source=SliceSource.VolumeZones,
            mode=ExtractMode.SingleZone,
            transient_mode=TransientOperationMode.AllSolutionTimes
        )

        # rename zone to something clear
        ds.zone(-1).name = f"Slice {i}: {axis_of_rot} angle: {round(angle,3)}"