# Script for relaxation curve fitting.

# Create the run.
name = 'r1'
run.create(name, 'relax_fit')

# Load the sequence from a PDB file.
pdb(name, 'Ap4Aase_new_3.pdb', load_seq=1)

# Load the peak intensities.
relax_fit.read(name, file='T2_ncyc1_ave.list', relax_time=0.0176)
