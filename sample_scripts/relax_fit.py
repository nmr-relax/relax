# Script for relaxation curve fitting.

# Create the run.
name = 'rx'
pipe.create(name, 'relax_fit')

# Load the backbone amide 15N spins from a PDB file.
structure.read_pdb('Ap4Aase_new_3.pdb')
structure.load_spins(spin_id='@N')

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

# Create Grace plots of the data.
grace.write(name, y_data_type='chi2', file='chi2.agr', force=1)    # Minimised chi-squared value.
grace.write(name, y_data_type='i0', file='i0.agr', force=1)    # Initial peak intensity.
grace.write(name, y_data_type='rx', file='rx.agr', force=1)    # Relaxation rate.
grace.write(name, x_data_type='relax_times', y_data_type='ave_int', file='intensities.agr', force=1)    # Average peak intensities.
grace.write(name, x_data_type='relax_times', y_data_type='ave_int', norm=1, file='intensities_norm.agr', force=1)    # Average peak intensities (normalised).

# Display the Grace plots.
grace.view(file='chi2.agr')
grace.view(file='i0.agr')
grace.view(file='rx.agr')
grace.view(file='intensities.agr')
grace.view(file='intensities_norm.agr')

# Save the program state.
state.save(file=name + '.save', force=1)
