# Script for generating the distribution of PDB structures.

# Modify the system path to load the base module.
import sys
sys.path.append('..')

# Python module imports.
from math import cos, pi, sin, sqrt
from numpy import dot, transpose

# relax module imports.
from generic_fns.angles import wrap_angles
from maths_fns.rotation_matrix import R_random_hypersphere, R_to_tilt_torsion

# Base module import.
from generate_base import Main


class Generate(Main):
    # The number of structures.
    N = 1000000

    # Cone parameters.
    THETA_X = 30.0 * 2.0 * pi / 360.0
    THETA_Y = 50.0 * 2.0 * pi / 360.0
    SIGMA_MAX = 60.0 * 2.0 * pi / 360.0

    def __init__(self):
        """Model specific setup."""

        # Alias the required methods.
        self.axes_to_pdb = self.axes_to_pdb_full
        self.build_axes = self.build_axes_pivot_com


    def rotation(self, i):
        """Set up the rotation for state i."""

        # Loop until a valid rotation matrix is found.
        while 1:
            # The random rotation matrix.
            R_random_hypersphere(self.R)

            # Rotation in the eigenframe.
            R_eigen = dot(transpose(self.axes), dot(self.R, self.axes))

            # The angles.
            phi, theta, sigma = R_to_tilt_torsion(R_eigen)
            sigma = wrap_angles(sigma, -pi, pi)

            # Determine theta_max.
            theta_max = 1.0 / sqrt((cos(phi) / self.THETA_X)**2 + (sin(phi) / self.THETA_Y)**2)

            # Skip the rotation if the cone angle is violated.
            if theta > theta_max:
                continue

            # Skip the rotation if the torsion angle is violated.
            if sigma > self.SIGMA_MAX or sigma < -self.SIGMA_MAX:
                continue

            # Rotation is ok, so stop looping.
            break


# Execute the code.
generate = Generate()
generate.run()
