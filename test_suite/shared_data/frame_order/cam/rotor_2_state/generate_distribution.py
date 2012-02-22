# Script for generating the distribution of PDB structures.

# Modify the system path to load the base module.
import sys
sys.path.append('..')

# Python module imports.
from math import pi

# relax module imports.
from maths_fns.rotation_matrix import axis_angle_to_R

# Base module import.
from generate_base import Main


class Generate(Main):
    # The number of structures.
    N = 2
    TILT_ANGLE = 85.0

    def __init__(self):
        """Model specific setup."""

        # Alias the required methods.
        self.axes_to_pdb = self.axes_to_pdb_main_axis
        self.build_axes = self.build_axes_alt


    def rotation(self, i):
        """Set up the rotation for state i."""

        # The rotation angle.
        angle = (i - 0.5) * 10.0 / 360.0 * 2.0 * pi
        print("Rotation angle: %s" % angle)

        # The rotation matrix.
        axis_angle_to_R(self.axes[:,2], angle, self.R)
        print("Rotation matrix:\n%s\n" % self.R)


# Execute the code.
generate = Generate()
generate.run()
