# Script for relaxation curve fitting.

# Create the run.
name = 'r1'
run.create(name, 'relax_fit')

# Load the sequence from a PDB file.
pdb(name, 'Ap4Aase_new_3.pdb', load_seq=1)

# Load the peak intensities.
relax_fit.read(name, file='T2_ncyc1_ave.list', relax_time=0.0176)
relax_fit.read(name, file='T2_ncyc1b_ave.list', relax_time=0.0176)
relax_fit.read(name, file='T2_ncyc2_ave.list', relax_time=0.0352)
relax_fit.read(name, file='T2_ncyc4_ave.list', relax_time=0.0704)
relax_fit.read(name, file='T2_ncyc4b_ave.list', relax_time=0.0704)
relax_fit.read(name, file='T2_ncyc6_ave.list', relax_time=0.1056)
relax_fit.read(name, file='T2_ncyc9_ave.list', relax_time=0.1584)
relax_fit.read(name, file='T2_ncyc9b_ave.list', relax_time=0.1584)
relax_fit.read(name, file='T2_ncyc11_ave.list', relax_time=0.1936)
relax_fit.read(name, file='T2_ncyc11b_ave.list', relax_time=0.1936)

# Calculate the peak intensity averages and the standard deviation of all spectra.
relax_fit.mean_and_error(name)

# Unselect unresolved residues.
unselect.read(name, file='unresolved')

# Set the relaxation curve type.
relax_fit.select_model(name, 'exp')

# Select just G4
select.res(name, num=4, change_all=1)

# Grid search.
grid_search(name, inc=11)

# Minimise.
minimise('simplex', run=name, scaling=0, constraints=0)

# Monte Carlo simulations.
monte_carlo.setup(name, number=100)
monte_carlo.create_data(name)
#monte_carlo.initial_values(name)
#minimise('newton', run=name)
#monte_carlo.error_analysis(name)

# Save the relaxation rates.
value.write(name, param='rx', file='rx.out', force=1)

# Write the results.
#results.write(name, file='results', dir=None, force=1)

# Save the program state.
state.save(file='save', force=1)
