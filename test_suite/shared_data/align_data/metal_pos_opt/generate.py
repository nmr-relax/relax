# relax script for generating a RDC and PCS test model with missing data.
# Note:  relax is only used to read the PDB info!

# Python module imports.
from numpy import array, dot, float64, zeros
from numpy.linalg import norm
from os import sep
from re import search

# relax imports.
from generic_fns.mol_res_spin import spin_loop
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'
seq_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'pcs_data'

# Create the data pipe.
pipe.create('population', 'N-state')

# Load the structures.
NUM_STR = 3
for i in range(1, NUM_STR+1):
    structure.read_pdb(file='lactose_MCMM4_S1_%i.pdb' % i, dir=str_path, set_model_num=i, set_mol_name='LE')

# Load the sequence information.
structure.load_spins(spin_id=':UNK@C*', ave_pos=False)
structure.load_spins(spin_id=':UNK@H*', ave_pos=False)

# Deselect the CH2 protons (the rotation of these doesn't work in the model, but the carbon doesn't move).
deselect.spin(spin_id=':UNK@H6')
deselect.spin(spin_id=':UNK@H7')
deselect.spin(spin_id=':UNK@H17')
deselect.spin(spin_id=':UNK@H18')

# Load the CH vectors for the C atoms.
structure.vectors(spin_id='@C*', attached='H*', ave=False)

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

# The Ln3+ position.
ln_pos = array([ -14.845,    0.969,    0.265])

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
missing = [[[900, 'C2'], [900, 'C10']],
           [[900, 'C.*']],
           [[900, 'C2'], [900, 'H.*']],
           [[900, 'C2'], [900, 'H17']]
]

# Generate the PCS data.
for i in range(len(A)):
    # Output file.
    out = open('missing_pcs_%i' % i, 'w')

    # Header.
    out.write('%-10s %-10s %-10s %-10s %-10s %20s\n' % ('mol_name', 'res_num', 'res_name', 'spin.num', 'spin.name', 'pcs'))

    # Loop over the spins.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # Skip spin.
        skip = False
        for j in range(len(missing[i])):
            if res_num == missing[i][j][0] and search(missing[i][j][1], spin.name):
                skip = True
        if skip:
            continue

        # Loop over the states.
        pcs_full = 0.0
        for j in range(NUM_STR):
            # The Ln3+/proton vector.
            vect = spin.pos[j] - ln_pos

            # Length and unit vector.
            r = norm(vect)
            unit = vect / r

            # Convert Angstrom to meter.
            r = r * 1e-10

            # Calculate the PCS.
            pcs = const / r**3 * dot(unit, dot(A[i], unit))

            # Convert to ppm.
            pcs = pcs * 1e6

            # Add to the full PCS.
            pcs_full += pcs

        # Average the PCS.
        pcs_full = pcs_full / NUM_STR

        # Output the pcs.
        out.write('%-10s %-10s %-10s %-10s %-10s %20s\n' % (mol_name, res_num, res_name, spin.num, spin.name, pcs_full))


# RDC.
######

# The dipolar constant.
kappa = -3. * 1.0/(2.0*pi) * mu0/(4.0*pi) * g13C * g1H * h_bar
const = kappa / r_CH**3

# The missing RDC list.
missing = [[[900, 'C5']],
           [[900, 'C5']],
           [[900, 'C5']],
           [[900, 'C5'], [900, 'C10']]
]

# Generate the RDC data.
for i in range(len(A)):
    # Output file.
    out = open('missing_rdc_%i' % i, 'w')

    # Skip the RDC.
    if i == 1:
        continue

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

        # Loop over the states.
        rdc_full = 0.0
        for j in range(NUM_STR):
            # Unit vector.
            unit = spin.xh_vect[j] / norm(spin.xh_vect[j])

            # Calculate the RDC.
            rdc = const * dot(unit, dot(A[i], unit))

            # Add to the full RDC.
            rdc_full += rdc

        # Average the RDC.
        rdc_full = rdc_full / NUM_STR

        # Output the rdc.
        out.write('%-10s %-10s %-10s %-10s %-10s %20s\n' % (mol_name, res_num, res_name, spin.num, spin.name, rdc_full))
