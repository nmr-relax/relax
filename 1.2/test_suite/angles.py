###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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

import sys


class Angles:
    def __init__(self, relax):
        """Class for testing the angle calculation function."""

        self.relax = relax

        # The name of the test.
        self.name = "The user function angles()"


    def test(self, run):
        """The actual test."""

        # Create the run.
        self.relax.interpreter._Run.create(run, 'mf')

        # Read a PDB file.
        self.relax.interpreter._PDB.pdb(run, file='test.pdb', dir=sys.path[-1] + '/test_suite/data', model=1, heteronuc='N', proton='H')

        # Initialise a diffusion tensor.
        self.relax.interpreter._Diffusion_tensor.init(run, (1.698e7, 1.417e7, 67.174, -83.718), param_types=3)

        # Calculate the angles.
        self.relax.interpreter._Angles.angles(run)

        # Success.
        return 1
