# relax script for generating synthetic RDC and PCS data for testing Monte Carlo simulations.

# Python module imports.
from numpy import dot, float64, sum, transpose, zeros
from numpy.linalg import eigvals, norm
from os import sep
import sys

# relax module imports.
from pipe_control.interatomic import return_interatom
from pipe_control.mol_res_spin import generate_spin_id, return_spin, spin_loop
from status import Status; status = Status()


def convert_tensor(A):
    """Convert the rank-1, 5D tensor form into a rank-2, 3D tensor."""

    # Convert the tensor into numpy matrix form.
    tensor = zeros((3, 3), float64)
    tensor[0, 0] = A[0]
    tensor[0, 1] = tensor[1, 0] = A[2]
    tensor[0, 2] = tensor[2, 0] = A[3]
    tensor[1, 1] = A[1]
    tensor[1, 2] = tensor[2, 1] = A[4]
    tensor[2, 2] = -A[0]-A[1]

    # Return the tensor.
    return tensor

# A randomly rotated, synthetic tensor {Cxx, Cyy, Cxy, Cxz, Cyz} with Ca=1 and Cr=0.5.
C = [-0.351261, 0.556994, -0.506392, 0.560544, -0.286367]

# Convert to a 3D matrix.
tensor = convert_tensor(C)

# Scale to become a realistic alignment tensor (Pr matrix elements between 0 and 1, and small tensor).
tensor = tensor / 2000.0

# The dipolar constant.
h = 6.62606876e-34      # Planck constant.
h_bar = h / ( 2.0*pi )  # Dirac constant.
mu0 = 4.0 * pi * 1e-7   # Permeability of free space.
r = 1.041e-10            # NH bond length.
gn = -2.7126e7          # 15N gyromagnetic ratio.
gh = 26.7522212e7       # 1H gyromagnetic ratio.
kappa = -3. * 1.0/(2.0*pi) * mu0/(4.0*pi) * gn * gh * h_bar
dip_const = kappa / r**3    # The dipolar constant.

# PCS constant.
T = 303.0               # Temp in Kelvin.
B0 = 600e6 * 2*pi / gh  # Magnetic field strength (600 MHz).
k = 1.3806504e-23     # Boltzman constant.
pcs_const = B0**2 / (15.0 * mu0 * k * T)

# The magnetic susceptibility tensor.
chi_tensor = tensor / pcs_const

# Path to files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'sphere'

# Create a data pipe.
pipe.create('synth', 'N-state')

# Load the structure.
structure.read_pdb('sphere.pdb', dir=path)

# Load all atoms as spins.
structure.load_spins()

# Load the NH vectors.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.unit_vectors(ave=False)

# Set the Ln3+ position 10 Angstrom away.
centre = [10.0, 0.0, 0.0]

# Open the results files.
rdc_file = open('synth_rdc', 'w')
pcs_file = open('synth_pcs', 'w')

# Loop over the N spins.
for spin, mol, res_num, res_name in spin_loop(full_info=True):
    # Skip deselected spins.
    if not spin.select:
        continue

    # Skip calciums.
    if spin.name == "CA":
        continue

    # Calculate the distance between the PCS centre and the atom (in metres).
    r = spin.pos - centre
    r = r * 1e-10

    # Unit vector.
    r_hat = r / norm(r)

    # The PCS (in ppm).
    pcs = 1.0 / (4.0 * pi * norm(r)**3) * dot(transpose(r_hat), dot(chi_tensor, r_hat))
    pcs = pcs * 1e6

    # Write the PCS.
    pcs_file.write("%20s%10s%10s%10s%10s%30.11g%30.11g\n" % (mol, res_num, res_name, spin.num, spin.name, pcs, 1e-10))

    # RDC time, so skip protons now.
    if spin.name == "H":
        continue

    # Get the interatomic data container.
    spin_id1 = generate_spin_id(res_num=res_num, res_name=res_name, spin_num=spin.num, spin_name=spin.name)
    spin_id2 = generate_spin_id(res_num=res_num, res_name=res_name, spin_name='H')
    interatom = return_interatom(spin_id1, spin_id2)

    # Skip interatoms without vectors.
    if not hasattr(interatom, 'vector'):
        continue

    # Calculate and write the RDC.
    rdc = dip_const * dot(transpose(interatom.vector), dot(tensor, interatom.vector))
    rdc_file.write("%-10s %-10s %20.11f %20.11g\n" % (repr(spin_id1), repr(spin_id2), rdc, 1e-10))

# Print outs.
print("\nAlignment tensor (A):\n" + repr(tensor))
print("Eigenvalues: " + repr(eigvals(tensor)))
print("Dipolar constant: " + repr(dip_const))

print("\nSaupe order matrix (S):\n" + repr(tensor * 1.5))
print("Eigenvalues: " + repr(eigvals(tensor * 1.5)))

print("\nMagnetic susceptibility tensor (Chi):\n" + repr(chi_tensor))
print("Eigenvalues: " + repr(eigvals(chi_tensor)))
print("PCS constant: " + repr(pcs_const))
print("PCS centre: " + repr(centre))
