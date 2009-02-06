# relax script for generating synthetic RDC and PCS data for the bax_C_1J7P_N_H_Ca.pdb structure.

# Python module imports.
from numpy import dot, float64, sum, transpose, zeros
from numpy.linalg import eigvals
from os import sep
import sys

# relax module imports.
from generic_fns.mol_res_spin import spin_loop



def convert_tensor(A):
    """Convert the rank-1, 5D tensor form into a rank-2, 3D tensor."""

    # Convert the tensor into numpy matrix form.
    tensor = zeros((3,3), float64)
    tensor[0,0] = A[0]
    tensor[0,1] = tensor[1,0] = A[2]
    tensor[0,2] = tensor[2,0] = A[3]
    tensor[1,1] = A[1]
    tensor[1,2] = tensor[2,1] = A[4]
    tensor[2,2] = -A[0]-A[1]

    # Return the tensor.
    return tensor

# A randomly rotated, synthetic tensor {Cxx, Cyy, Cxy, Cxz, Cyz} with Ca=1 and Cr=0.5.
C = [-0.351261, 0.556994, -0.506392, 0.560544, -0.286367]

# Convert to a 3D matrix.
tensor = convert_tensor(C)

# Scale to become a realistic alignment tensor (Pr matrix elements between 0 and 1, and small tensor).
tensor = tensor / 1000.0

# The dipolar constant.
h = 6.62606876e-34
h_bar = h / ( 2.0*pi )
mu0 = 4.0 * pi * 1e-7
r = 1.02e-10
gn = -2.7126e7
gh = 26.7522212e7
kappa = -3./(8*pi**2)*gn*gh*mu0*h_bar
dip_const = kappa / r**3

# Print out.
print "Alignment tensor:\n" + `tensor`
print "Eigenvalues: " + `eigvals(tensor)`
print "Eigenvalue sum: " + `sum(eigvals(tensor))`
print "Dipolar constant: " + `dip_const`

# Path to files.
path = sys.path[-1] + '/test_suite/shared_data/'

# Create a data pipe.
pipe.create('synth', 'N-state')

# Load the structure.
structure.read_pdb('bax_C_1J7P_N_H_Ca.pdb', dir=path+sep+'structures')

# Load all atoms as spins.
structure.load_spins()

# Calculate NH bond vectors for the N spins.
structure.vectors('H', spin_id='@N')

# Loop over the N spins.
rdc_file = open('synth_rdc', 'w')
for spin, mol, res_num, res_name in spin_loop(selection='@N', full_info=True):
    # Skip spins without vectors.
    if not hasattr(spin, 'xh_vect'):
        continue

    # Calculate the RDC.
    rdc = dip_const * dot(transpose(spin.xh_vect), dot(tensor, spin.xh_vect))

    rdc_file.write("%20s%10s%10s%10s%10s%30.11f\n" % (mol, res_num, res_name, spin.num, spin.name, rdc))
