import tecplot as tp
tp.session.connect()

#
# This script uses the Extract Blanked Zones add-on to extract the unblanked region of a specific
# time strand through time. It will properly assign a new StrandID to the resulting zones
#
source_strand = int(input("Enter the strand number from which you want to extract: ")) 

with tp.session.suspend():
    dataset = tp.active_frame().dataset
    max_strand = max(z.strand for z in dataset.zones())
    # Get the zones associated with the supplied StrandID
    source_zones = [z for z in dataset.zones() if z.strand == source_strand]
    # Extract the zones and assign the proper StrandID
    new_zones = tp.data.extract.extract_blanked_zones(source_zones)
    for zone in new_zones:
        zone.strand = max_strand+1
    print("Extracted {} new zones".format(len(new_zones)))

