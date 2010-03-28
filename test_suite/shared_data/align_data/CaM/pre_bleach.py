# relax script for generating synthetic RDC and PCS data for the bax_C_1J7P_N_H_Ca.pdb structure.

# Python module imports.
import __main__
from numpy import dot, float64, sum, transpose, zeros
from numpy.linalg import eigvals, norm
from os import sep
import sys

# relax module imports.
from generic_fns.mol_res_spin import return_spin, spin_loop


# PRE cut-off (in Angstrom).
PRE = 15.0


# Path to files.
path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep

# Create a data pipe.
pipe.create('pre', 'N-state')

# Load the structure.
structure.read_pdb('bax_C_1J7P_N_H_Ca.pdb', dir=path+sep+'structures')

# Load all atoms as spins.
structure.load_spins()

# Get the first calcium position.
spin = return_spin(':1000@CA')
centre = spin.pos

# Open the unresolved file.
file = open('unresolved', 'w')

# Find the atoms within X Angstrom.
print("\n\nBleached spins:")
for spin, mol, res_num, res_name in spin_loop(full_info=True):
    # Skip calciums.
    if spin.name == "CA":
        continue

    # Calculate the distance between the PCS centre and the atom (in metres).
    r = spin.pos - centre

    # PRE.
    if norm(r) < PRE:
        # Print out.
        print(("\t%20s %20s %20s %20s %20s" % (mol, res_num, res_name, spin.num, spin.name)))

        file.write("%20s %20s %20s %20s %20s\n" % (mol, res_num, res_name, spin.num, spin.name))

# Close the file.
file.close()
