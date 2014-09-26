from __future__ import absolute_import
###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the Check class based on the strategy design pattern."""

# Python module imports.
from types import MethodType
from warnings import warn

# relax module imports.
from lib.errors import RelaxError
from lib.warnings import RelaxWarning


class Check:
    """Data checking class based on the U{strategy design pattern<https://en.wikipedia.org/wiki/Strategy_pattern>}."""

    def __init__(self, function):
        """Convert the function argument into a class instance method.

        @param function:    The function to convert into the self.checks class instance method which is called from the __call__ method.
        @type function:     function
        """

        # Convert the function into a method of this class instance.
        self.checks = MethodType(function, self, Check)


    def __call__(self, *args, **kargs):
        """Make the object callable, and perform the checks.

        This will call the function used to initialise the class and then


        @keyword escalate:      The feedback to give if the check fails.  This can be 0 for no printouts, 1 to throw a RelaxWarning, or 2 to raise a RelaxError.
        @type escalate:         int
        @raises RelaxError:     If escalate is set to 2 and the check fails.
        @return:                True if the check passes, False otherwise.
        @rtype:                 bool
        """

        # Remove the escalate keyword argument.
        if 'escalate' not in kargs:
            escalate = 2
        else:
            escalate = kargs['escalate']
            del kargs['escalate']

        # Perform the check.
        error = self.checks(*args, **kargs)

        # No errors.
        if error == None:
            return True

        # Send the text of the RelaxError object into the RelaxWarning system.
        if escalate == 1:
            warn(RelaxWarning(error.text))
            return False

        # The error system.
        if escalate == 2:
            raise error
