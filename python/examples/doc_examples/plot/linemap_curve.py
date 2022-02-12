import numpy as np
from os import path
import tecplot as tp
from tecplot.constant import PlotType, CurveType

examples_dir = tp.session.tecplot_examples_directory()
infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
dataset = tp.data.load_tecplot(infile)
dataset.add_variable('Weight')

# convert error to weighting to be used for fitting below
# This converts the error to  (1 / error)
# and normalizes to the range [1,100]
zone = dataset.zone('ZONE 1')
err1 = zone.values('Error 1')
wvar = zone.values('Weight')
err = err1.as_numpy_array()
sigma = 1. / err
dsigma = sigma.max() - sigma.min()
sigma = (99 * (sigma - sigma.min()) / dsigma) + 1
wvar[:] = sigma

frame = tp.active_frame()
frame.plot_type = PlotType.XYLine
plot = frame.plot()

lmaps = plot.linemaps()

lmaps.show = True
lmaps.x_variable = dataset.variable(0)

for lmap, var in zip(lmaps, list(dataset.variables())[1:4]):
    lmap.y_variable = var

#{DOC:highlight}[
curves = [lmap.curve for lmap in plot.linemaps()]

curves[0].curve_type = CurveType.PolynomialFit
curves[0].num_points = 1000
curves[0].polynomial_order = 10

curves[1].curve_type = CurveType.PowerFit
curves[1].use_fit_range = True
curves[1].fit_range = 4,8
curves[1].weight_variable = dataset.variable('Weight')
curves[1].use_weight_variable = True

curves[2].curve_type = CurveType.Spline
curves[2].clamp_spline = True
curves[2].spline_derivative_at_ends = 0,0
#]

tp.export.save_png('linemap_curve.png', 600, supersample=3)
