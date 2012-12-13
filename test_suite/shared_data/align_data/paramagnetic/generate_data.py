# Python module imports.
from math import pi
from numpy import dot, float64, array
from numpy.linalg import norm

# relax module imports.
from generic_fns.interatomic import interatomic_loop
from generic_fns.mol_res_spin import spin_loop


# Some constants.
kB = 1.380650424 * 1e-23                    # Boltzmann's constant in SI units of J.K^-1B.
mu0 = 4.0 * pi * 1e-7                       # The permeability of vacuum.
h_bar = 6.62606876 * 1e-34 / (2.0 * pi)     # Dirac's constant.
g1H = 26.7522212 * 1e7                      # The 1H gyromagnetic ratio.
g15N = -2.7126 * 1e7                        # The 15N gyromagnetic ratio.
r_nh = 1.041 * 1e-10                        # The NH bond length for the RDC.


def mag_constant(B0=None, T=None):
    """Calculate the constant for conversion of alignment tensor to magnetic susceptibility tensors.

    The conversion constant is defined as::

            15.mu0.k.T 
        d = ---------- .
              Bo**2


    @keyword B0:    The magnetic field strength.
    @type B0:       float
    @keyword T:     The temperature in Kalvin.
    @type T:        float
    """

    # Return the constant.
    return 15.0 * mu0 * kB * T / B0**2



# Create a data pipe.
pipe.create('generate data', 'N-state')

# Load the structure.
structure.read_pdb("bax_C_1J7P_N_H_Ca.pdb", dir="../../structures/", set_mol_name="CaM")

# Load the spins.
structure.load_spins("@N")
structure.load_spins("@H")

# Create the NH vector containers.
dipole_pair.define('@N', '@H')
dipole_pair.unit_vectors()

# Set up some alignment tensors (from the random_tensors.py script).
align_tensor.init(tensor='tensor 0', params=(0.0006157864417437287, -0.00027914923898849156, 0.0002715095515843512, 0.0009842872030009584, -0.00031390384563948447), scale=1.0, angle_units='deg', param_types=2, errors=False)
align_tensor.init(tensor='tensor 2', params=(0.0006287636590147914, 0.0006802034861179492, 0.0007510921252766747, 0.00037275214653516623, -0.0004374676265261981), scale=1.0, angle_units='deg', param_types=2, errors=False)

# Alias the tensors.
A0 = cdp.align_tensors[0].A
A2 = cdp.align_tensors[1].A

# The frequencies of the two alignments.
frq0 = 900e6 * 2.0 * pi / g1H
frq2 = 600e6 * 2.0 * pi / g1H

# Convert to magnetic susceptibility tensors.
chi0 = A0 * mag_constant(B0=frq0, T=303)
chi2 = A2 * mag_constant(B0=frq2, T=303)
print("\nChi tensor 0:\n%s" % chi0)
print("\nChi tensor 2:\n%s" % chi2)


# RDCs.
#######

# Open the RDC files.
dy_500_rdc = open('dy_500_rdc', 'w')
dy_700_rdc = open('dy_700_rdc', 'w')
er_900_rdc = open('er_900_rdc', 'w')

# The dipolar constant.
d = - 3.0/(2.0*pi) * mu0 / (4.0*pi) * g1H * g15N * h_bar / r_nh**3

# Loop over the interatomic data containers and calculate RDCs.
for interatom in interatomic_loop():
    # Calculate the RDC at 500 MHz for the first tensor, and write out the data.
    A = chi0 / mag_constant(B0=500e6 * 2.0 * pi / g1H, T=303)
    rdc = d * dot(dot(interatom.vector, A), interatom.vector)
    dy_500_rdc.write("%-20s %-20s %20f\n" % (repr(interatom.spin_id1), repr(interatom.spin_id2), rdc))

    # Calculate the RDC at 700 MHz for the first tensor, and write out the data.
    A = chi0 / mag_constant(B0=700e6 * 2.0 * pi / g1H, T=303)
    rdc = d * dot(dot(interatom.vector, A), interatom.vector)
    dy_700_rdc.write("%-20s %-20s %20f\n" % (repr(interatom.spin_id1), repr(interatom.spin_id2), rdc))

    # Calculate the RDC at 900 MHz for the second tensor, and write out the data.
    A = chi2 / mag_constant(B0=900e6 * 2.0 * pi / g1H, T=303)
    rdc = d * dot(dot(interatom.vector, A), interatom.vector)
    er_900_rdc.write("%-20s %-20s %20f\n" % (repr(interatom.spin_id1), repr(interatom.spin_id2), rdc))

# Close the RDC files.
dy_500_rdc.close()
dy_700_rdc.close()
er_900_rdc.close()


# PCSs.
#######

# Open the PCS files.
dy_pcs = open('dy_pcs', 'w')
er_pcs = open('er_pcs', 'w')

# Set the PCS centre to the atom :1000 of the Bax structure.
pcs_centre = array([32.555, -19.130, 27.775], float64)

# Loop over the atoms and calculate the PCS.
for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
    # The vector.
    vect = spin.pos - pcs_centre
    r = norm(vect) * 1e-10
    unit_vect = vect / norm(vect)

    # The PCS constant (in ppm).
    d = 1.0 / (4.0 * pi * r**3) * 1e6

    # Calculate the PCS for the first tensor, and write out the data.
    pcs = d * dot(dot(unit_vect, chi0), unit_vect)
    dy_pcs.write("%-15s %-10s %-10s %-10s %-10s %20f\n" % (mol_name, res_num, res_name, spin.num, spin.name, pcs))

    # Calculate the PCS for the first tensor, and write out the data.
    pcs = d * dot(dot(unit_vect, chi2), unit_vect)
    er_pcs.write("%-15s %-10s %-10s %-10s %-10s %20f\n" % (mol_name, res_num, res_name, spin.num, spin.name, pcs))

# Close the PCS files.
dy_pcs.close()
er_pcs.close()


# Write out a results file.
results.write(file='generate_data', dir=None, force=True)
