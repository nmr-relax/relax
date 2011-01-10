# relax script for generating synthetic RDC and PCS data for the bax_C_1J7P_N_H_Ca.pdb structure.

# Python module imports.
from numpy import dot, float64, sum, transpose, zeros
from numpy.linalg import eigvals, norm
from os import sep
import sys

# relax module imports.
from generic_fns.mol_res_spin import return_spin, spin_loop
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
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep

# Create a data pipe.
pipe.create('synth', 'N-state')

# Load the structure.
structure.read_pdb('bax_C_1J7P_N_H_Ca.pdb', dir=path+sep+'structures')

# Load all atoms as spins.
structure.load_spins()

# Deselect unresolved residues.
deselect.read(file='unresolved', mol_name_col=0, res_num_col=1, res_name_col=2, spin_num_col=3, spin_name_col=4)

# Calculate NH bond vectors for the N spins.
structure.vectors('H', spin_id='@N')

# Get the first calcium position.
spin = return_spin(':1000@CA')
centre = spin.pos

# Open the results files.
rdc_file = open('synth_rdc', 'w')
pcs_file = open('synth_pcs', 'w')

# Open the Pales input file.
pales_file = open('pales.in', 'w')

# The Pales header.
pales_file.write("DATA SEQUENCE ADQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLT\n")
pales_file.write("DATA SEQUENCE MMARKMKDTDSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREANIDGDGQVNYEE\n")
pales_file.write("DATA SEQUENCE FVQMMTAK\n\n")
pales_file.write("VARS   RESID_I RESNAME_I ATOMNAME_I RESID_J RESNAME_J ATOMNAME_J D      DD    W\n")
pales_file.write("FORMAT %5d     %6s       %6s        %5d     %6s       %6s    %9.3f   %9.3f %.2f\n\n")

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
    pcs_file.write("%20s%10s%10s%10s%10s%30.11g\n" % (mol, res_num, res_name, spin.num, spin.name, pcs))

    # RDC time, so skip protons now.
    if spin.name == "H":
        continue

    # Skip spins without vectors.
    if not hasattr(spin, 'xh_vect'):
        continue

    # Calculate and write the RDC.
    rdc = dip_const * dot(transpose(spin.xh_vect), dot(tensor, spin.xh_vect))
    rdc_file.write("%20s%10s%10s%10s%10s%30.11f\n" % (mol, res_num, res_name, spin.num, spin.name, rdc))

    # The Pales data line (equal weight, no errors).
    pales_file.write("%5d     %6s       %6s        %5d     %6s       %6s    %9.3f   %9.3f %.2f\n" % (res_num, res_name, spin.name, res_num, res_name, spin.attached_atom, rdc, 0.0, 1.0))

# Print outs.
print(("\nAlignment tensor (A):\n" + repr(tensor)))
print(("Eigenvalues: " + repr(eigvals(tensor))))
print(("Dipolar constant: " + repr(dip_const)))

print(("\nSaupe order matrix (S):\n" + repr(tensor * 1.5)))
print(("Eigenvalues: " + repr(eigvals(tensor * 1.5))))

print(("\nMagnetic susceptibility tensor (Chi):\n" + repr(chi_tensor)))
print(("Eigenvalues: " + repr(eigvals(chi_tensor))))
print(("PCS constant: " + repr(pcs_const)))
print(("PCS centre: " + repr(centre)))
