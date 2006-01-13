# Script for relaxation curve fitting.

# Create the run.
name = 'rx'
run.create(name, 'relax_fit')

# Load the sequence from a PDB file.
pdb(name, 'Ap4Aase_new_3.pdb', load_seq=1)

# Load the peak intensities.
relax_fit.read(name, file='T2_ncyc1.list', relax_time=0.0176)
relax_fit.read(name, file='T2_ncyc1b.list', relax_time=0.0176)
relax_fit.read(name, file='T2_ncyc2.list', relax_time=0.0352)
relax_fit.read(name, file='T2_ncyc4.list', relax_time=0.0704)
relax_fit.read(name, file='T2_ncyc4b.list', relax_time=0.0704)
relax_fit.read(name, file='T2_ncyc6.list', relax_time=0.1056)
relax_fit.read(name, file='T2_ncyc9.list', relax_time=0.1584)
relax_fit.read(name, file='T2_ncyc9b.list', relax_time=0.1584)
relax_fit.read(name, file='T2_ncyc11.list', relax_time=0.1936)
relax_fit.read(name, file='T2_ncyc11b.list', relax_time=0.1936)

# Calculate the peak intensity averages and the standard deviation of all spectra.
relax_fit.mean_and_error(name)

# Unselect unresolved residues.
unselect.read(name, file='unresolved')

# Set the relaxation curve type.
relax_fit.select_model(name, 'exp')

# Grid search.
grid_search(name, inc=11)

# Minimise.
minimise('simplex', run=name, scaling=0, constraints=0)

# Monte Carlo simulations.
monte_carlo.setup(name, number=500)
monte_carlo.create_data(name)
monte_carlo.initial_values(name)
minimise('simplex', run=name, scaling=0, constraints=0)
monte_carlo.error_analysis(name)

# Save the relaxation rates.
value.write(name, param='rx', file='rx.out', force=1)

# Grace plots of the relaxation rate.
grace.write(name, y_data_type='rx', file='rx.agr', force=1)
grace.view(file='rx.agr')

# Save the program state.
state.save(file=name + '.save', force=1)
