# relax script for generating a RDC and PCS test model with missing data.
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
seq_path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'pcs_data'

# Create the data pipe.
pipe.create('missing', 'N-state')

# Load the structure.
structure.read_pdb(file='LE_trunc.pdb', dir=str_path, set_mol_name='LE')

# Load the sequence information.
structure.load_spins()

# Load the bond vectors.
structure.vectors('H*')

# Init the alignment tensors.
A_5D = []
A_5D.append([1.42219822168827662867e-04, -1.44543001566521341940e-04, -7.07796211648713973798e-04, -6.01619494082773244303e-04, 2.02008007072950861996e-04])
A_5D.append([3.56720663040924505435e-04, -2.68385787902088840916e-04, -1.69361406642305853832e-04, 1.71873715515064501074e-04, -3.05790155096090983822e-04])
A_5D.append([2.32088908680377300801e-07, 2.08076808579168379617e-06, -2.21735465435989729223e-06, -3.74311563209448033818e-06, -2.40784858070560310370e-06])
A_5D.append([-2.62495279588228071048e-04, 7.35617367964106275147e-04, 6.39754192258981332648e-05, 6.27880171180572523460e-05, 2.01197582457700226708e-04])
A = zeros((len(A_5D), 3, 3), float64)
for i in range(len(A)):
    A[i, 0, 0] = A_5D[i][0]
    A[i, 1, 1] = A_5D[i][1]
    A[i, 2, 2] = -A_5D[i][0] -A_5D[i][1]
    A[i, 0, 1] = A[i, 1, 0] = A_5D[i][2]
    A[i, 0, 2] = A[i, 2, 0] = A_5D[i][3]
    A[i, 1, 2] = A[i, 2, 1] = A_5D[i][4]
    print("\nTensor %i:\n%s\n" % (i, A[i]))

# True Ln3+ position.
ln_pos = array([1, 2, -30])

# Physical constants.
h = 6.62606876e-34          # Planck constant.
h_bar = h / ( 2.0*pi )      # Dirac constant.
T = 298.0                   # Temp.
g1H = 26.7522212 * 1e7      # 1H gyromagnetic ratio.
g13C = 6.728 * 1e7          # 13C gyromagnetic ratio.
mu0 = 4.0 * pi * 1e-7       # Permeability of free space.
kB = 1.380650424 * 1e-23    # Boltzmann's constant.
r_CH = 1.100e-10            # CH bond length.


# PCS.
######

# The PCS constant.
B0 = 2.0 * pi * 799.75376122 * 1e6 / g1H
const = mu0 / (4.0 * pi)  *  (15.0 * kB * T) / B0**2
print("PCS const: %s\n" % const)

# The missing PCS list.
missing = [[(6, "H1'"), (6, "C2'"), (8, "H6"), (10, "C6"), (16, "H1'")],
           [(6, "H1'"), (6, "C2'"), (7, "H5"), (10, "C6"), (7, "H6"), (16, "H1'")],
           [],
           [(6, "H1'"), (6, "C2'"), (10, "C6"), (16, "H1'"), (22, "H8")]
]

# Generate the PCS data.
for i in range(len(A)):
    # Skip the PCS.
    if i == 2:
        continue

    # Output file.
    out = open('missing_pcs_%i' % i, 'w')

    # Header.
    out.write('%-10s %-10s %-10s %-10s %-10s %20s\n' % ('mol_name', 'res_num', 'res_name', 'spin.num', 'spin.name', 'pcs'))

    # Loop over the spins.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # Skip spin.
        skip = False
        for j in range(len(missing[i])):
            if res_num == missing[i][j][0] and spin.name == missing[i][j][1]:
                skip = True
        if skip:
            continue

        # The Ln3+/proton vector.
        vect = spin.pos - ln_pos

        # Length and unit vector.
        r = norm(vect)
        unit = vect / r

        # Convert Angstrom to meter.
        r = r * 1e-10

        # Calculate the PCS.
        pcs = const / r**3 * dot(unit, dot(A[i], unit))

        # Convert to ppm.
        pcs = pcs * 1e6

        # Output the pcs.
        out.write('%-10s %-10s %-10s %-10s %-10s %20s\n' % (mol_name, res_num, res_name, spin.num, spin.name, pcs))


# RDC.
######

# The dipolar constant.
kappa = -3. * 1.0/(2.0*pi) * mu0/(4.0*pi) * g13C * g1H * h_bar
const = kappa / r_CH**3

# The missing RDC list.
missing = [[(6, "C1'"), (6, "C2'"), (6, "C5"), (7, "C6"), (8, "*"), (15, "*"), (16, "*"), (23, "*")],
           [],
           [(6, "C1'"), (6, "C2'"), (6, "C5"), (7, "C6")],
           [(6, "C1'"), (6, "C2'"), (6, "C5"), (7, "C6"), (10, "C2'")]
]

# Generate the RDC data.
for i in range(len(A)):
    # Skip the RDC.
    if i == 1:
        continue

    # Output file.
    out = open('missing_rdc_%i' % i, 'w')

    # Header.
    out.write('%-10s %-10s %-10s %-10s %-10s %20s\n' % ('mol_name', 'res_num', 'res_name', 'spin.num', 'spin.name', 'rdc'))

    # Loop over the spins.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # Skip protons.
        if spin.element == 'H':
            continue

        # Skip spin.
        skip = False
        for j in range(len(missing[i])):
            if missing[i][j][1] == '*' and res_num == missing[i][j][0]:
                skip = True
            elif res_num == missing[i][j][0] and spin.name == missing[i][j][1]:
                skip = True
        if skip:
            continue

        # No vector.
        if not hasattr(spin, 'xh_vect'):
            continue

        # Unit vector.
        unit = spin.xh_vect / norm(spin.xh_vect)

        # Calculate the RDC.
        rdc = const * dot(unit, dot(A[i], unit))

        # Output the rdc.
        out.write('%-10s %-10s %-10s %-10s %-10s %20s\n' % (mol_name, res_num, res_name, spin.num, spin.name, rdc))
