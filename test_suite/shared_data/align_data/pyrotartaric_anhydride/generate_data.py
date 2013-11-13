# Python module imports.
from numpy import dot, float64, transpose, zeros
from os import sep
from re import search

# relax module imports.
from pipe_control.interatomic import return_interatom
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


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# Create the data pipe.
pipe.create('pcb3lyp_R', 'N-state')

# Load the structure.
structure.read_pdb(file='pyrotartaric_anhydride.pdb', dir=str_path)

# Set up the 13C and 1H spins information.
structure.load_spins(spin_id='@C*', ave_pos=False)
structure.load_spins(spin_id='@H*', ave_pos=False)

# Set up the pseudo-atoms.
spin.create_pseudo(spin_name='Q9', members=['@10', '@11', '@12'], averaging="linear")
sequence.display()

# Define the nuclear isotopes of all spins and pseudo-spins.
spin.isotope(isotope='13C', spin_id='@C*')
spin.isotope(isotope='1H', spin_id='@H*')
spin.isotope(isotope='1H', spin_id='@Q*')

# Define the magnetic dipole-dipole relaxation interaction.
interatom.read_dist(file='R_prop_car.txt', unit='Angstrom', spin_id1_col=1, spin_id2_col=2, data_col=5)
interatom.unit_vectors(ave=False)

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
gc = 6.728 * 1e7        # 13C gyromagnetic ratio.
gh = 26.7522212e7       # 1H gyromagnetic ratio.
kappa = -3. * 1.0/(2.0*pi) * mu0/(4.0*pi) * gc * gh * h_bar

# The input data.
file = open('R_prop_car.txt')
data = file.readlines()
file.close()

# Open the results files.
rdc_file = open('R_rdcs', 'w')
rdc_file.write("%-10s %-10s %20s %20s %20s %10s %20s\n" % ("#spin_id1", "spin_id2", "RDC", "abs(T)", "abs(J)", "J_sign", "dist"))

# Loop over the data.
for line in data:
    # Skip lines with no data.
    if not search('^ ', line):
        continue

    # Split up the line.
    spin_id1, spin_id2, j, j_sign, dist = line.split()

    # Get the interatomic data container.
    interatom = return_interatom(spin_id1, spin_id2)

    # The dipolar constant.
    r = float(dist) * 1e-10
    if r == 0.0:
        dip_const = 1e100
    else:
        dip_const = kappa / r**3

    # J-coupling.
    j = float(j) * int(j_sign)

    # Calculate the RDC.
    rdc = dip_const * dot(transpose(interatom.vector), dot(tensor, interatom.vector))

    # T value.
    t = abs(j + rdc)

    # Write out the data.
    rdc_file.write("%-10s %-10s %20.11f %20.11f %20.11f %10s %20s\n" % (spin_id1, spin_id2, rdc, t, abs(j), j_sign, dist))

# Print out the tensor.
print('\n')
print("The tensor to find is:")
print(tensor)
print('\n')
