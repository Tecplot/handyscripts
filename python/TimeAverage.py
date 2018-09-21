import tecplot as tp
import tpmath
import tputils

tp.session.connect()
in_strand = input("Which strand do you want to average? Enter the strand number or enter 'all': ")

with tp.session.suspend():
    dataset = tp.active_frame().dataset

    #variables_to_average = [dataset.variable("z"), dataset.variable("salinity"), dataset.variable("temp")]
    #constant_variables = [dataset.variable("x"), dataset.variable("y")]
    variables_to_average = dataset.variables()
    constant_variables = None

    zones_by_strand = tputils.get_zones_by_strand(dataset)
    try: 
        strand_to_average = int(in_strand)
        source_zones = zones_by_strand[strand_to_average]
        tpmath.compute_average(source_zones, variables_to_average, constant_variables)
    except (TypeError,ValueError): # Assume the user typed "all"
        for strand, source_zones in zones_by_strand.items():
            tpmath.compute_average(source_zones, variables_to_average, constant_variables)
  
