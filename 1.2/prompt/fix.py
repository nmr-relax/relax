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


class Fix:
    def __init__(self, relax):
        """Class containing the function for fixing or allowing parameter values to change."""

        self.relax = relax


    def fix(self, run=None, element=None, fixed=1):
        """Function for either fixing or allowing parameter values to change.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        element:  Which element to fix.

        fixed:  A flag specifying if the parameters should be fixed or allowed to change.


        Description
        ~~~~~~~~~~~

        The keyword argument 'element' can be any of the following:

        'diff' - the diffusion tensor parameters.  This will allow all diffusion tensor parameters
        to be toggled.

        an integer - if an integer number is given, then all parameters for the residue
        corresponding to that number will be toggled.

        'all_res' - using this keyword, all parameters from all residues will be toggled.

        'all' - all parameter will be toggled.  This is equivalent to combining both 'diff' and
        'all_res'.


        The flag 'fixed', if set to 1, will fix parameters, while a value of 0 will allow parameters
        to vary.


        Only parameters corresponding to the given run will be affected.
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "fix("
            text = text + "run=" + `run`
            text = text + ", element=" + `element`
            text = text + ", fixed=" + `fixed` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The element argument.
        if type(element) != str and type(element) != int:
            raise RelaxIntStrError, ('element', element)

        # The fixed argument.
        if type(fixed) != int or (fixed != 0 and fixed != 1):
            raise RelaxBinError, ('fixed', fixed)

        # Execute the functional code.
        self.relax.generic.fix.fix(run=run, element=element, fixed=fixed)
