# Script for relaxation curve fitting.

# Create the run.
run = 'r1'
create_run(run, 'relax_fit')

# Load the sequence from a PDB file.
pdb(run, 'Ap4Aase_new_3.pdb', load_seq=1)

# Load the peak intensities.
relax_fit.read(run, file='T2_ncyc1_ave.list', relax_time=0.0176)
