# relax script for generating a PCS test model.
# Note:  relax is only used to read the PDB info!

# Python module imports.
import __main__
from numpy import array, dot, float64, zeros
from numpy.linalg import norm
from os import sep

# relax imports.
from generic_fns.mol_res_spin import spin_loop


# Path of the files.
str_path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'dna'

# Create the data pipe.
pipe.create('DNA', 'N-state')

# Load the structure.
structure.read_pdb(file='LE.pdb', dir=str_path, set_mol_name='LE')

# Load the sequence information, and get the atomic positions.
sequence.read(file='PCSflos.txt', spin_name_col=3, res_name_col=4, res_num_col=5)
molecule.name(name='LE')
structure.get_pos()

# Init the alignment tensor.
A = zeros((3, 3), float64)
A_5D = [1.42219822168827662867e-04, -1.44543001566521341940e-04, -7.07796211648713973798e-04, -6.01619494082773244303e-04, 2.02008007072950861996e-04]
A[0, 0] = A_5D[0]
A[1, 1] = A_5D[1]
A[2, 2] = -A_5D[0] -A_5D[1]
A[0, 1] = A[1, 0] = A_5D[2]
A[0, 2] = A[2, 0] = A_5D[3]
A[1, 2] = A[2, 1] = A_5D[4]
print("\nTensor:\n%s\n" % A)

# True Ln3+ position.
ln_pos = array([25.8279, -11.6382, -2.5931])

# Physical constants.
T = 298.0
g1H = 26.7522212 * 1e7
B0 = 2.0 * pi * 799.75376122 * 1e6 / g1H
mu0 = 4.0 * pi * 1e-7
kB = 1.380650424 * 1e-23

# The PCS constant.
const = mu0 / (4.0 * pi)  *  (15.0 * kB * T) / B0**2
print("PCS const: %s\n" % const)


# Output file.
out = open('LE_dna', 'w')

# Header.
out.write('%-10s %-10s %-10s %-10s %-10s %20s\n' % ('mol_name', 'res_num', 'res_name', 'spin.num', 'spin.name', 'pcs'))

# Loop over the spins.
for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
    # The Ln3+/proton vector.
    vect = spin.pos - ln_pos

    # Length and unit vector.
    r = norm(vect)
    unit = vect / r

    # Convert Angstrom to meter.
    r = r * 1e-10

    # Calculate the PCS.
    pcs = const / r**3 * dot(unit, dot(A, unit))

    # Convert to ppm.
    pcs = pcs * 1e6

    # Output the data.
    out.write('%-10s %-10s %-10s %-10s %-10s %20s\n' % (mol_name, res_num, res_name, spin.num, spin.name, pcs))
