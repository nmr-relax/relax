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


class Nuclei:
    def __init__(self, relax):
        """Class containing the function for setting the gyromagnetic ratio of the heteronucleus."""

        self.relax = relax


    def nuclei(self, heteronuc='N'):
        """Function for setting the gyromagnetic ratio of the heteronucleus.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        heteronuc:  The type of heteronucleus.


        Description
        ~~~~~~~~~~~

        The heteronuc argument can be set to the following strings:

            N:  Nitrogen, -2.7126e7
            C:  Carbon, 2.2e7
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "nuclei("
            text = text + "heteronuc=" + `heteronuc` + ")"
            print text

        # The heteronucleus argument.
        if type(heteronuc) != str:
            raise RelaxStrError, ('heteronucleus', heteronuc)

        # Execute the functional code.
        self.relax.generic.nuclei.set_values(heteronuc=heteronuc)
