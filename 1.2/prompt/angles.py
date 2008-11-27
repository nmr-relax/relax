###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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
        """Class containing the function for calculating XH bond angles."""

        self.relax = relax


    def angles(self, run=None):
        """Function for calculating the angles between the XH bond vector and the diffusion tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.


        Description
        ~~~~~~~~~~~

        If the diffusion tensor is isotropic for the run, then nothing will be done.

        If the diffusion tensor is axially symmetric, then the angle alpha will be calculated for
        each XH bond vector.

        If the diffusion tensor is asymmetric, then the three angles will be calculated.
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "angles("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.relax.generic.angles.angles(run=run)
