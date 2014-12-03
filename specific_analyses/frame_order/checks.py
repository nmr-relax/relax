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
from lib.checks import Check
from lib.errors import RelaxError
from lib.warnings import RelaxWarning
from pipe_control.pipes import cdp_name, get_pipe


def check_domain_func(domain=None):
    """Check if the domain has been defined.

    @keyword domain:    The domain to check for.  If None, then the check will be for any domain being defined.
    @type domain:       None or str
    @return:            The initialised RelaxError object if the domain is not defined, or nothing.
    @rtype:             None or RelaxError instance
    """

    # Check that the domain is defined.
    if not hasattr(cdp, 'domain'):
        return RelaxError("No domains have been defined.  Please use the domain user function.")
    if domain != None and domain not in cdp.domain:
        return RelaxError("The domain '%s' has not been defined.  Please use the domain user function." % domain)

# Create the checking object.
check_domain = Check(check_domain_func)


def check_model_func(pipe_name=None):
    """Check if the frame order model has been set up.

    @keyword pipe_name: The data pipe to check for, if not the current pipe.
    @type pipe_name:    None or str
    @return:            The initialised RelaxError object if the model is not set up, or nothing.
    @rtype:             None or RelaxError instance
    """

    # The data pipe.
    if pipe_name == None:
        pipe_name = cdp_name()

    # Get the data pipe.
    dp = get_pipe(pipe_name)

    # Check that the model is set up.
    if not hasattr(dp, 'model'):
        return RelaxError("The frame order model has not been set up, please use the frame_order.select_model user function.")

# Create the checking object.
check_model = Check(check_model_func)


def check_parameters_func():
    """Check if the frame order parameters exist.

    @return:    The initialised RelaxError object if the model parameters have not been setup, or nothing.
    @rtype:     None or RelaxError instance
    """

    # The model has not been set up.
    if not hasattr(cdp, 'params'):
        return RelaxError("The frame order model has not been set up, no parameters have been defined.")

    # The model has been set up.
    else:
        # Find missing parameters.
        missing = []
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
            return RelaxError("The frame order parameters %s have not been set up." % missing)

# Create the checking object.
check_parameters = Check(check_parameters_func)


def check_pivot_func(pipe_name=None):
    """Check that the pivot point has been set.

    @keyword pipe_name: The data pipe to check the pivot for.  This defaults to the current data pipe if not set.
    @type pipe_name:    str
    @return:            The initialised RelaxError object if the pivot point has not been set, or nothing.
    @rtype:             None or RelaxError instance
    """

    # The data pipe.
    if pipe_name == None:
        pipe_name = cdp_name()

    # Get the data pipe.
    dp = get_pipe(pipe_name)

    # Check for the pivot_x parameter.
    if not hasattr(dp, 'pivot_x'):
        return RelaxError("The pivot point has not been set, please use the frame_order.pivot user function to define the point.")

# Create the checking object.
check_pivot = Check(check_pivot_func)
