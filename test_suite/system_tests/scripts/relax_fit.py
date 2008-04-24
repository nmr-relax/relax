# Script for relaxation curve fitting.

# Create the data pipe.
pipe.create('rx', 'relax_fit')

# Load the sequence.
sequence.read('Ap4Aase.seq', dir='..')

# Load the peak intensities.
relax_fit.read(file='T2_ncyc1_ave.list', relax_time=0.0176)
relax_fit.read(file='T2_ncyc1b_ave.list', relax_time=0.0176)
relax_fit.read(file='T2_ncyc2_ave.list', relax_time=0.0352)
relax_fit.read(file='T2_ncyc4_ave.list', relax_time=0.0704)
relax_fit.read(file='T2_ncyc4b_ave.list', relax_time=0.0704)
relax_fit.read(file='T2_ncyc6_ave.list', relax_time=0.1056)
relax_fit.read(file='T2_ncyc9_ave.list', relax_time=0.1584)
relax_fit.read(file='T2_ncyc9b_ave.list', relax_time=0.1584)
relax_fit.read(file='T2_ncyc11_ave.list', relax_time=0.1936)
relax_fit.read(file='T2_ncyc11b_ave.list', relax_time=0.1936)

# Calculate the peak intensity averages and the standard deviation of all spectra.
relax_fit.mean_and_error()

# Unselect unresolved residues.
unselect.read(file='unresolved')

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
grid_search(inc=11)

# Minimise.
minimise('simplex', constraints=0)

# Monte Carlo simulations.
monte_carlo.setup(number=10)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', constraints=0)
monte_carlo.error_analysis()
