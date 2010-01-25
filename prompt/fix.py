###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2008-2010 Edward d'Auvergne                       #
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
"""Module containing the 'fix' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import Basic_class
import arg_check
from generic_fns import fix


class Fix(Basic_class):
    """Class containing the function for fixing or allowing parameter values to change."""

    def fix(self, element=None, fixed=True):
        """Function for either fixing or allowing parameter values to change during optimisation.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        element:  Which element to fix.

        fixed:  A flag specifying if the parameters should be fixed or allowed to change.


        Description
        ~~~~~~~~~~~

        The keyword argument 'element' can be any of the following:

        'diff' - the diffusion tensor parameters.  This will allow all diffusion tensor parameters
        to be toggled.

        'all_spins' - using this keyword, all parameters from all spins will be toggled.

        'all' - all parameter will be toggled.  This is equivalent to combining both 'diff' and
        'all_spins'.


        The flag 'fixed', if set to True, will fix parameters during optimisation whereas a value of
        False will allow parameters to vary.
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "fix("
            text = text + "element=" + repr(element)
            text = text + ", fixed=" + repr(fixed) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(element, 'element')
        arg_check.is_bool(fixed, 'fixed')

        # Execute the functional code.
        fix.fix(element=element, fixed=fixed)
