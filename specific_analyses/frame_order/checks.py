###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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
"""Module for checks for the frame order analysis."""

# Python module imports.
from warnings import warn

# relax module imports.
from lib.errors import RelaxError
from lib.warnings import RelaxWarning
from pipe_control.pipes import cdp_name, get_pipe


def check_domain(domain=None, escalate=0):
    """Check if the domain has been defined.

    @keyword domain:        The domain to check for.  If None, then the check will be for any domain being defined.
    @type domain:           None or str
    @keyword escalate:      The feedback to give if the domain is not defined.  This can be 0 for no printouts, 1 to throw a RelaxWarning, or 2 to raise a RelaxError.
    @type escalate:         int
    @raises RelaxError:     If escalate is set to 2 and the domain is not defined.
    @return:                True if the domain is defined, False otherwise.
    @rtype:                 bool
    """

    # Init.
    defined = True
    msg = ''

    # Check that the domain is defined.
    if not hasattr(cdp, 'domain'):
        defined = False
        msg = "No domains have been defined.  Please use the domain user function."
    if domain != None and domain not in cdp.domain:
        defined = False
        msg = "The domain '%s' has not been defined.  Please use the domain user function." % domain

    # Warnings and errors.
    if not defined and escalate == 1:
        warn(RelaxWarning(msg))
    elif not defined and escalate == 2:
        raise RelaxError(msg)

    # Return the answer.
    return defined


def check_model(escalate=0):
    """Check if the frame order model has been set up.

    @keyword escalate:      The feedback to give if the model is not set up.  This can be 0 for no printouts, 1 to throw a RelaxWarning, or 2 to raise a RelaxError.
    @type escalate:         int
    @raises RelaxError:     If escalate is set to 2 and the model is not set up.
    @return:                True if the model is set up, False otherwise.
    @rtype:                 bool
    """

    # Init.
    flag = True
    msg = ''

    # Check that the model is set up.
    if not hasattr(cdp, 'model'):
        flag = False
        msg = "The frame order model has not been set up, please use the frame_order.select_model user function."

    # Warnings and errors.
    if not flag and escalate == 1:
        warn(RelaxWarning(msg))
    elif not flag and escalate == 2:
        raise RelaxError(msg)

    # Return the answer.
    return flag


def check_parameters(escalate=0):
    """Check if the frame order parameters exist.

    @keyword escalate:      The feedback to give if the check fails.  This can be 0 for no printouts, 1 to throw a RelaxWarning, or 2 to raise a RelaxError.
    @type escalate:         int
    @raises RelaxError:     If escalate is set to 2 and the check fails.
    @return:                True if the check passes, False otherwise.
    @rtype:                 bool
    """

    # Init.
    flag = True
    msg = ''
    missing = []

    # The model has not been set up.
    if not hasattr(cdp, 'params'):
        flag = False
        msg = "The frame order model has not been set up, no parameters have been defined."

    # The model has been set up.
    else:
        # Loop over all parameters.
        for param in cdp.params:
            # Check that the parameters exists.
            if not hasattr(cdp, param):
                missing.append(param)

            # Check that it has a value.
            else:
                obj = getattr(cdp, param)
                if obj == None:
                    missing.append(param)

        # Failure.
        if len(missing):
            flag = False
            msg = "The frame order parameters %s have not been set up." % missing

    # Warnings and errors.
    if not flag and escalate == 1:
        warn(RelaxWarning(msg))
    elif not flag and escalate == 2:
        raise RelaxError(msg)

    # Return the answer.
    return flag


def check_pivot(pipe_name=None):
    """Check that the pivot point has been set.

    @keyword pipe_name: The data pipe to check the pivot for.  This defaults to the current data pipe if not set.
    @type pipe_name:    str
    @raises RelaxError: If the pivot point has not been set.
    """

    # The data pipe.
    if pipe_name == None:
        pipe_name = cdp_name()

    # Get the data pipe.
    dp = get_pipe(pipe_name)

    # Check for the pivot_x parameter.
    if not hasattr(dp, 'pivot_x'):
        raise RelaxError("The pivot point has not been set, please use the frame_order.pivot user function to define the point.")


