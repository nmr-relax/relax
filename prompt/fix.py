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


    def fix(self, run=None, param_type='diff', fixed=0):
        """Function for either fixing or allowing parameter values to change.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        param_type:  The parameter type to be fixed or allowed to change.

        fixed:  A flag specifying if the parameters should be fixed or allowed to change.


        Description
        ~~~~~~~~~~~

        Currently, the only param_type value supported is 'diff'.
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "fix("
            text = text + "run=" + `run`
            text = text + "param_type=" + `param_type`
            text = text + "fixed=" + `fixed` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The param_type argument.
        if type(param_type) != str:
            raise RelaxStrError, ('param_type', param_type)

        # The fixed argument.
        if type(fixed) != int or (fixed != 0 and fixed != 1):
            raise RelaxBinError, ('fixed', fixed)

        # Execute the functional code.
        self.relax.fix.fix(run=run, param_type=param_type, fixed=fixed)
