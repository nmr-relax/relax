###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
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


class Vectors:
    def __init__(self, relax):
        """Class containing the macro to calculate XH vectors from the structure."""

        self.relax = relax


    def vectors(self, heteronuc='N', proton='H'):
        """Macro for calculating XH vectors from the structure.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        heteronuc:  The heteronucleus name as specified in the PDB file.

        proton:  The name of the proton as specified in the PDB file.


        Example
        ~~~~~~~

        To calculate the XH vectors of the backbone amide nitrogens where in the PDB file the
        backbone nitrogen is called 'N' and the attached proton is called 'H', type:

        relax> vectors()
        relax> vectors('N')
        relax> vectors('N', 'H')
        relax> vectors(heteronuc='N', proton='H')

        If the attached proton is called 'HN', type:

        relax> vectors(proton='HN')
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "vectors("
            text = text + "heteronuc=" + `heteronuc`
            text = text + ", proton=" + `proton` + ")"
            print text

        # The heteronucleus argument.
        if type(heteronuc) != str:
            raise RelaxStrError, ('heteronucleus', heteronuc)

        # The proton argument.
        if type(proton) != str:
            raise RelaxStrError, ('proton', proton)

        # Execute the functional code.
        self.relax.vectors.vectors(heteronuc=heteronuc, proton=proton)
