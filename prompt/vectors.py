###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


class Vectors:
    def __init__(self, relax):
        """Class containing the function to calculate XH vectors from the structure."""

        self.relax = relax


    def vectors(self, run=None, heteronuc='N', proton='H'):
        """Function for calculating unit XH vectors from the structure.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the vectors to.

        heteronuc:  The name of the heteronucleus as specified in the PDB file.

        proton:  The name of the proton as specified in the PDB file.


        Description
        ~~~~~~~~~~~

        This function is essential for model-free analysis and should be executed after loading a
        PDB file.  If the previously loaded PDB file contained multiple structures, this function
        will calculate unit XH vectors for all structures and then average them.


        Example
        ~~~~~~~

        To calculate the XH vectors of the backbone amide nitrogens where in the PDB file the
        backbone nitrogen is called 'N' and the attached proton is called 'H', assuming the run
        'test', type:

        relax> vectors('test')
        relax> vectors('test', 'N')
        relax> vectors('test', 'N', 'H')
        relax> vectors('test', heteronuc='N', proton='H')

        If the attached proton is called 'HN', type:

        relax> vectors('test', proton='HN')
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "vectors("
            text = text + "run=" + `run`
            text = text + ", heteronuc=" + `heteronuc`
            text = text + ", proton=" + `proton` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The heteronucleus argument.
        if type(heteronuc) != str:
            raise RelaxStrError, ('heteronucleus', heteronuc)

        # The proton argument.
        if type(proton) != str:
            raise RelaxStrError, ('proton', proton)

        # Execute the functional code.
        self.relax.generic.vectors.vectors(run=run, heteronuc=heteronuc, proton=proton)
