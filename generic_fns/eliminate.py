###############################################################################
#                                                                             #
# Copyright (C) 2003-2005, 2007-2009 Edward d'Auvergne                        #
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
"""Module implementing the mathematical modelling step of model elimination."""

# relax module imports.
from generic_fns import pipes
from relax_errors import RelaxError
from specific_fns.setup import get_specific_fn



def eliminate(function=None, args=None):
    """Model elimination.

    @keyword function:  A user supplied function for model elimination.  This function should accept
                        five arguments, a string defining a certain parameter, the value of the
                        parameter, the minimisation instance (ie the residue index if the model
                        is residue specific), and the function arguments.  If the model is rejected,
                        the function should return True, otherwise it should return False.  The
                        function will be executed multiple times, once for each parameter of the model. 
    @type function:     function
    @param args:        The arguments to be passed to the user supplied function.
    @type args:         tuple
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Specific eliminate, parameter names, parameter values, number of instances, and deselect function setup.
    eliminate = get_specific_fn('eliminate', cdp.pipe_type)
    model_loop = get_specific_fn('model_loop', cdp.pipe_type)
    get_param_names = get_specific_fn('get_param_names', cdp.pipe_type)
    get_param_values = get_specific_fn('get_param_values', cdp.pipe_type)
    deselect = get_specific_fn('deselect', cdp.pipe_type)

    # Determine if simulations are active.
    if hasattr(cdp, 'sim_state') and cdp.sim_state == True:
        sim_state = True
    else:
        sim_state = False


    # Get the number of instances and loop over them.
    for model_info in model_loop():
        # Model elimination.
        ####################

        if not sim_state:
            # Get the parameter names and values.
            names = get_param_names(model_info)
            values = get_param_values(model_info)

            # No data.
            if names == None or values == None:
                continue

            # Test that the names and values vectors are of equal length.
            if len(names) != len(values):
                raise RelaxError("The names vector " + repr(names) + " is of a different length to the values vector " + repr(values) + ".")

            # Loop over the parameters.
            flag = False
            for j in xrange(len(names)):
                # Eliminate function.
                if eliminate(names[j], values[j], model_info, args):
                    flag = True

            # Deselect.
            if flag:
                deselect(model_info)


        # Simulation elimination.
        #########################

        else:
            # Loop over the simulations.
            for j in xrange(cdp.sim_number):
                # Get the parameter names and values.
                names = get_param_names(model_info)
                values = get_param_values(model_info, sim_index=j)

                # No data.
                if names == None or values == None:
                    continue

                # Test that the names and values vectors are of equal length.
                if len(names) != len(values):
                    raise RelaxError("The names vector " + repr(names) + " is of a different length to the values vector " + repr(values) + ".")

                # Loop over the parameters.
                flag = False
                for k in xrange(len(names)):
                    # Eliminate function.
                    if eliminate(names[k], values[k], model_info, args, sim=j):
                        flag = True

                # Deselect.
                if flag:
                    deselect(model_info, sim_index=j)
