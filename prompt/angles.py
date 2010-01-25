###############################################################################
#                                                                             #
# Copyright (C) 2003-2005, 2009-2010 Edward d'Auvergne                        #
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

# Module docstring.
"""Module containing the 'angles' user function class."""
__docformat__ = 'plaintext'

# Python module imports.

# relax module imports.
from base_class import Basic_class
from generic_fns import angles


class Angles(Basic_class):
    """Class containing the function for calculating XH bond angles."""

    def angle_diff_frame(self):
        """Calculate the angles defining the XH bond vector within the diffusion frame.

        Description
        ~~~~~~~~~~~

        If the diffusion tensor is isotropic, then nothing will be done.

        If the diffusion tensor is axially symmetric, then the angle alpha will be calculated for
        each XH bond vector.

        If the diffusion tensor is asymmetric, then the three angles will be calculated.
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "angle_diff_frame()"
            print(text)

        # Execute the functional code.
        angles.angle_diff_frame()
