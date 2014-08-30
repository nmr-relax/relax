# Calculate the R and I0 errors via bootstrapping.
# As this is an exact solution, bootstrapping is identical to Monte Carlo simulations.

# Python module imports.
from collections import OrderedDict
#import pickle
import cPickle as pickle

# Open data.
dic = pickle.load( open( "estimate_errors.p", "rb" ) )


# Make plots?
make_plots = False
if make_plots:
    from pylab import show, plot

#    if make_plots:
#        plot(times, I, 'b.', label='I')
#        plot(times, I_err, 'r.', label='I_err')


# Loop over dic.
if False:
    for i, i_dic in dic.iteritems():
        print i, i_dic

if make_plots:
    show()