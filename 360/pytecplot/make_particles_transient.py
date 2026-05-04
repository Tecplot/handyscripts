import numpy as np
import tecplot as tp
import time

tp.session.connect()

def split_particle_zone_to_file(zone, min_time, max_time, strand, outfile):
    num_points = zone.num_points
    variable_values = dict()
    variables = list(zone.dataset.variables())
    for v in variables:
        variable_values[v.index] = zone.values(v).as_numpy_array()

    time_steps = np.linspace(min_time, max_time, num_points)
    for time_idx in range(num_points):
        outfile.write("""
ZONE T="{name} Transient"
STRANDID={strand}, SOLUTIONTIME={solution_time}
I=1, J=1, K=1, ZONETYPE=Ordered
DATAPACKING=BLOCK
DT=(""".format(name=zone.name,strand=strand, solution_time=time_steps[time_idx]))

        for v in variables:
            # Assuming all variables are single precision
            outfile.write("{} ".format("SINGLE"))
        outfile.write(")")

        for v in variables:
            outfile.write("{}\n".format(variable_values[v.index][time_idx]))

def split_particle_zone(zone, min_time, max_time, strand):
    num_points = zone.num_points

    variable_values = dict()
    variables = list(zone.dataset.variables())
    for v in variables:
        variable_values[v.index] = zone.values(v).as_numpy_array()

    time_steps = np.linspace(min_time, max_time, num_points)
    for time_idx in range(num_points):
        z = zone.dataset.add_ordered_zone("{} Transient".format(zone.name), (1,1,1), strand_id=strand, solution_time=time_steps[time_idx])
        for v in variables:
            z.values(v)[0] = variable_values[v.index][time_idx]

with tp.session.suspend():
    start = time.time()
    ds = tp.active_frame().dataset
    min_time = ds.solution_times[0]
    max_time = ds.solution_times[-1]
    max_strand = 0
    for z in ds.zones():
        max_strand = max(max_strand, z.strand)
    strand = max_strand+1
    particle_zones = [z for z in ds.zones("*Particle*") if 'Transient' not in z.name] 

    # Using a temporary file is faster than writing 100s of zones via PyTecplot
    use_temp_file = True
    if use_temp_file:
        import tempfile
        import os
        outfile = tempfile.TemporaryFile(mode='w', delete=False)
        outfile.write("""
TITLE     = "Transient Particles"
VARIABLES = """)
        for v in ds.variables():
            outfile.write('\"{}\"\n'.format(v.name))
        for z in particle_zones:
            print("Splitting ", z.name)
            split_particle_zone_to_file(z, min_time, max_time, strand, outfile)
            strand = strand+1
        outfile.close()
        tp.data.load_tecplot(outfile.name, reset_style=False)
        os.unlink(outfile.name)
    else:
        for z in particle_zones:
            print("Splitting ", z.name)
            split_particle_zone(z, min_time, max_time, strand)
            strand = strand+1
    print("Elapsed: ", time.time()-start)

