from os import path
import tecplot as tp

examples_dir = tp.session.tecplot_examples_directory()
datafile = path.join(examples_dir,'SimpleData','DownDraft.plt')
dataset = tp.data.load_tecplot(datafile)
result = tp.data.query.probe_at_position(0,0.1,0.3)
data = dataset.VariablesNamedTuple(*result.data)

# prints: (RHO, E) = (1.17, 252930.37)
msg = '(RHO, E) = ({:.2f}, {:.2f})'
print(msg.format(data.RHO, data.E))
