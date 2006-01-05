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

# Save the program state.
state.save(file='save', force=1)
