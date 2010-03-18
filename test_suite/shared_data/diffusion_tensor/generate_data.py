###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

"""relax script for creating a PDB file and relaxation data.

The PDB file consists of uniformly distributed bond vectors.  The relaxation data is that of a NH bond vector with an ellipsoidal diffusion tensor and no internal motion.
"""

# Python module imports.
from math import sqrt
from numpy import array, cross, dot, eye, float64, transpose, zeros
from numpy.linalg import eig, inv, norm

# relax module imports.
from maths_fns.rotation_matrix import axis_angle_to_R, euler_to_R_zyz, R_to_euler_zyz
from generic_fns.structure.geometric import angles_uniform, vect_dist_spherical_angles
from generic_fns.structure.internal import Internal
from relax_io import open_write_file


def ri_data(Dx=None, Dy=None, Dz=None, vectors=None, frq_label=None, wH=None, csa=None):
    """Calculate the relaxation data for the given vectors."""

    # Diff parameters.
    Diso = (Dx + Dy + Dz) / 3.0
    L2 = (Dx*Dy + Dx*Dz + Dy*Dz) / 3.0
    mux = (Dx - Diso) / sqrt(Diso**2 - L2)
    muy = (Dy - Diso) / sqrt(Diso**2 - L2)
    muz = (Dz - Diso) / sqrt(Diso**2 - L2)

    # The five time constants.
    tau = zeros(5, float64)
    tau[0] = 6 * (Diso - sqrt(Diso**2 - L2))
    tau[1] = 4*Dx + Dy + Dz
    tau[2] = Dx + 4*Dy + Dz
    tau[3] = Dx + Dy + 4*Dz
    tau[4] = 6 * (Diso + sqrt(Diso**2 - L2))
    tau = 1.0 / tau
    print("\nTime constants, tau: %s" % tau)

    # The dipolar constant.
    h = 6.62606876e-34      # Planck constant.
    h_bar = h / ( 2.0*pi )  # Dirac constant.
    mu0 = 4.0 * pi * 1e-7   # Permeability of free space.
    r = 1.041e-10            # NH bond length.
    gn = -2.7126e7          # 15N gyromagnetic ratio.
    gh = 26.7522212e7       # 1H gyromagnetic ratio.
    dip_const = 0.25 * (mu0/(4.0*pi))**2 * (gn * gh * h_bar)**2 / r**6    # The dipolar constant.
    print("Dipolar constant: %s" % dip_const)

    # The five frequencies.
    wN = wH * gn/gh
    w = zeros(5, float64)
    w[0] = 0
    w[1] = wN
    w[2] = wH - wN
    w[3] = wH
    w[4] = wH + wN
    print("\nFrequencies, w: %s" % w)

    # CSA constant.
    csa_const = (wN * csa)**2 / 3.0
    print("CSA constant: %s" % csa_const)

    # The files.
    R1_file = open('R1.%s.out' % frq_label, 'w')
    R2_file = open('R2.%s.out' % frq_label, 'w')
    NOE_file = open('NOE.%s.out' % frq_label, 'w')

    # Loop over the vectors.
    c = zeros(5, float64)
    for i in range(len(vectors)):
        print("\ni: %s" % i)
        print("vector: %s" % vectors[i])

        # Direction cosines.
        delta_x, delta_y, delta_z = vectors[i]

        # The d and e factors.
        d = 3.0 * (delta_x**4 + delta_y**4 + delta_z**4) - 1.0
        e =     mux * (delta_x**4 + 2.0*delta_y**2 * delta_z**2)
        e = e + muy * (delta_y**4 + 2.0*delta_x**2 * delta_z**2)
        e = e + muz * (delta_z**4 + 2.0*delta_x**2 * delta_y**2)

        # The weights.
        c[0] = (d + e) / 4.0
        c[1] = 3 * delta_y**2 * delta_z**2
        c[2] = 3 * delta_x**2 * delta_z**2
        c[3] = 3 * delta_x**2 * delta_y**2
        c[4] = (d - e) / 4.0
        print("Weights, c: %s" % c)

        # The spectral density function.
        Jw = zeros(5, float64)
        for j in range(5):
            for k in range(5):
                Jw[j] = Jw[j] + 2.0/5.0 * c[k] * tau[k] / (1.0 + (w[j]*tau[k])**2)
        print("Jw: %s" % c)

        # The relaxation data.
        R1 = dip_const * (Jw[2] + 3.0*Jw[1] + 6.0*Jw[4])  +  csa_const * Jw[1]
        R2 = dip_const/2.0 * (4.0*Jw[0] + Jw[2] + 3.0*Jw[1] + 6.0*Jw[3] + 6.0*Jw[4])  +  csa_const/6.0 * (4.0*Jw[0] + 3.0*Jw[1])
        sigma_noe = dip_const * (6.0*Jw[4] - Jw[2])
        NOE = 1 + gh/gn * sigma_noe / R1
        print("R1: %s" % R1)
        print("R2: %s" % R2)
        print("NOE: %s" % NOE)

        # Write the data.
        R1_file.write("%s %s\n" % (i+1, R1))
        R2_file.write("%s %s\n" % (i+1, R2))
        NOE_file.write("%s %s\n" % (i+1, NOE))


def tensor_setup(Dx=None, Dy=None, Dz=None, alpha=None, beta=None, gamma=None):
    """Set up the diffusion tensor according to the correct Euler angle convention."""

    # Print out.
    print("\n\n")
    print("# Angles to diff tensor.")
    print("########################")

    # Init.
    ROT = False

    # The rotation matrix (in the rotating axis system).
    R = zeros((3, 3), float64)
    R_rev = zeros((3, 3), float64)
    euler_to_R_zyz(gamma, beta, alpha, R)
    R_rev = transpose(R)
    print("\nEuler angels: [%s, %s, %s]" % (alpha, beta, gamma))
    print("R:\n%s" % R)
    print("R_rev:\n%s" % R_rev)
    print("X x Y: %s" % cross(R[:, 0], R[:, 1]))

    # Axis rotations.
    if ROT:
        R_x180 = zeros((3, 3), float64)
        R_y180 = zeros((3, 3), float64)
        R_z180 = zeros((3, 3), float64)
        axis_angle_to_R(R_rev[:, 0], pi, R_x180)
        axis_angle_to_R(R_rev[:, 1], pi, R_y180)
        axis_angle_to_R(R_rev[:, 2], pi, R_z180)
        print("\nR (x 180):\n%s" % R_x180)
        print("\nR (y 180):\n%s" % R_y180)
        print("\nR (z 180):\n%s" % R_z180)

    # A test vector.
    mu = array([1, 2, -3], float64)
    mu = mu / norm(mu)

    # Tensor in eigenframe.
    D_prime = zeros((3, 3), float64)
    D_prime[0, 0] = 1e7
    D_prime[1, 1] = 2e7
    D_prime[2, 2] = 3e7
    print("\nD':\n%s" % D_prime)

    # Rotate tensor from the eigenframe to the ref frame.
    D = dot(R_rev, dot(D_prime, transpose(R_rev)))
    print("\nD:\n%s" % D)
    print("\n\n")

    # Return the forward and reverse rotation, and the diffusion tensors.
    return R, R_rev, D_prime, D


def pdb(R=eye(3), r=1.02, file_name='uniform.pdb', inc=None):
    """Create the bond vector distribution and save the PDB file."""

    # Create the structural object.
    structure = Internal()

    # Add a molecule.
    structure.add_molecule(name='dist')

    # Alias the single molecule from the single model.
    mol = structure.structural_data[0].mol[0]

    # Get the polar and azimuthal angles for the distribution.
    phi, theta = angles_uniform(inc)

    # Get the uniform vector distribution.
    vectors = vect_dist_spherical_angles(inc=inc, distribution='uniform')

    # Loop over the radial array of vectors (change in longitude).
    atom_num = 1
    for i in range(len(theta)):
        # Loop over the vectors of the radial array (change in latitude).
        for j in range(len(phi)):
            # Rotate the vector into the diffusion frame.
            vector = dot(R, vectors[i + j*len(theta)])

            # Scale the vector.
            vector = vector * r

            # Residue number.
            res = (atom_num + 1) / 2

            # Add the vector as a N-H atom pair.
            mol.atom_add(pdb_record='HETATM', atom_num=atom_num,   atom_name='N', res_name='NH', res_num=res, pos=zeros(3), element='N')
            mol.atom_add(pdb_record='HETATM', atom_num=atom_num+1, atom_name='H', res_name='NH', res_num=res, pos=vector,   element='H')

            # Connect.
            mol.atom_connect(atom_num-1, atom_num)

            # Move 2 atoms forwards.
            atom_num += 2

    # The PDB file.
    file = open_write_file(file_name, force=True)
    structure.write_pdb(file)
    file.close()

    # Return the vectors.
    return vectors


# The tensor values.
Dx = 1e7
Dy = 2e7
Dz = 3e7
alpha = 1.0
beta = 2.0
gamma = 0.5

# Other data.
frq = array([500, 600, 700, 800], float64)
wH = frq * 1e6 * 2*pi
csa = -172e-6

# The tensor.
R, R_rev, D_prime, D = tensor_setup(Dx, Dy, Dz, alpha, beta, gamma)

# The bond vector distribution.
vectors = pdb(R=R, file_name='uniform.pdb', inc=8)

# The relaxation data.
for i in range(len(frq)):
    ri_data(Dx=Dx, Dy=Dy, Dz=Dz, vectors=vectors, frq_label=str(int(frq[i])), wH=wH[i], csa=csa)
