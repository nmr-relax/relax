###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006-2009 Edward d'Auvergne                             #
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

# relax module imports.
from specific_fns.consistency_tests import Consistency_tests
from specific_fns.frame_order import Frame_order
from specific_fns.hybrid import Hybrid
from specific_fns.jw_mapping import Jw_mapping
from specific_fns.model_free import Model_free
from specific_fns.n_state_model import N_state_model
from specific_fns.noe import Noe
from specific_fns.relax_disp import Relax_disp
from specific_fns.relax_fit import Relax_fit
from specific_fns.srls import SRLS
from relax_errors import RelaxError, RelaxFuncSetupError


# Instantiate all classes.
consistency_tests_obj = Consistency_tests()
frame_order_obj = Frame_order()
hybrid_obj = Hybrid()
jw_mapping_obj = Jw_mapping()
model_free_obj = Model_free()
n_state_model_obj = N_state_model()
noe_obj = Noe()
relax_disp_obj = Relax_disp()
relax_fit_obj = Relax_fit()
srls_obj = SRLS()


# The function for returning the requested specific function.
def get_specific_fn(eqi, function_type, raise_error=True):
    """The function for returning the requested specific function."""

    # Initialise.
    function = None

    # Get the class instance corresponding to function_type.
    inst = get_instance(function_type)

    # Attempt to retrieve the function.
    try:
        # Back calculation of relaxation data.
        if eqi == 'back_calc_ri':
            function = inst.back_calc_ri

        # Base data loop generator function.
        if eqi == 'base_data_loop':
            function = inst.base_data_loop

        # Calculate function.
        if eqi == 'calculate':
            function = inst.calculate

        # Create Monte Carlo data function.
        if eqi == 'create_mc_data':
            function = inst.create_mc_data

        # Data structure initialisation function.
        if eqi == 'data_init':
            function = inst.data_init

        # List of parameter names returning function.
        if eqi == 'data_names':
            function = inst.data_names

        # Default parameter value returning function.
        if eqi == 'default_value':
            function = inst.default_value

        # Duplicate data function.
        if eqi == 'duplicate_data':
            function = inst.duplicate_data

        # Eliminate models.
        if eqi == 'eliminate':
            function = inst.eliminate

        # Parameter names function.
        if eqi == 'get_param_names':
            function = inst.get_param_names

        # Parameter values function.
        if eqi == 'get_param_values':
            function = inst.get_param_values

        # Grid search function.
        if eqi == 'grid_search':
            function = inst.grid_search

        # Initial Monte Carlo parameter value search function.
        if eqi == 'init_sim_values':
            function = inst.sim_init_values

        # Spin specific parameter determining function.
        if eqi == 'is_spin_param':
            function = inst.is_spin_param

        # Map bounds function.
        if eqi == 'map_bounds':
            function = inst.map_bounds

        # Minimise function.
        if eqi == 'minimise':
            function = inst.minimise

        # Model loop.
        if eqi == 'model_desc':
            function = inst.model_desc

        # Model loop.
        if eqi == 'model_loop':
            function = inst.model_loop

        # Model statistics.
        if eqi == 'model_stats':
            function = inst.model_statistics

        # Model type.
        if eqi == 'model_type':
            function = inst.model_type

        # Molmol macro creation.
        if eqi == 'molmol_macro':
            function = inst.molmol_macro

        # Number of instances.
        if eqi == 'num_instances':
            function = inst.num_instances

        # Overfit deselect.
        if eqi == 'overfit_deselect':
            function = inst.overfit_deselect

        # Pack Monte Carlo simulation data function.
        if eqi == 'pack_sim_data':
            function = inst.sim_pack_data

        # Pymol macro creation.
        if eqi == 'pymol_macro':
            function = inst.pymol_macro

        # Read results file function (Columnar format).
        if eqi == 'read_columnar_results':
            function = inst.read_columnar_results

        # Read results file function (XML format).
        #if eqi == 'read_xml_results':
        #    function = inst.read_xml_results

        # Data returning function.
        if eqi == 'return_data':
            function = inst.return_data

        # Parameter description returning function.
        if eqi == 'return_data_desc':
            function = inst.return_data_desc

        # Data or parameter name returning function.
        if eqi == 'return_data_name':
            function = inst.return_data_name

        # Data error returning function.
        if eqi == 'return_error':
            function = inst.return_error

        # Factor of conversion between different parameter units returning function.
        if eqi == 'return_conversion_factor':
            function = inst.return_conversion_factor

        # Grace string returning function.
        if eqi == 'return_grace_string':
            function = inst.return_grace_string

        # Selected simulation array returning function.
        if eqi == 'return_selected_sim':
            function = inst.sim_return_selected

        # Simulation chi-squared array returning function.
        if eqi == 'return_sim_chi2':
            function = inst.sim_return_chi2

        # Simulation parameter array returning function.
        if eqi == 'return_sim_param':
            function = inst.sim_return_param

        # String of the external parameter units returning function.
        if eqi == 'return_units':
            function = inst.return_units

        # Value and error returning function.
        if eqi == 'return_value':
            function = inst.return_value

        # Set error function.
        if eqi == 'set_error':
            function = inst.set_error

        # Set parameter values function.
        if eqi == 'set_param_values':
            function = inst.set_param_values

        # Set the selected simulations array.
        if eqi == 'set_selected_sim':
            function = inst.set_selected_sim

        # Set update function.
        if eqi == 'set_update':
            function = inst.set_update

        # Skip function.
        if eqi == 'skip_function':
            function = inst.skip_function

        # Deselection function.
        if eqi == 'deselect':
            function = inst.deselect

    # Catch if the function is missing.
    except AttributeError:
        function = None

    # Raise an error if the function doesn't exist.
    if raise_error and function == None:
        # Raise the error.
        raise RelaxFuncSetupError(get_string(function_type))

    # Return the function.
    return function


def get_instance(function_type):
    """Function for returning the class instance corresponding to the function type."""

    # Consistency testing.
    if function_type == 'ct':
        return consistency_tests_obj

    # The Frame Order theories.
    if function_type == 'frame order':
        return frame_order_obj

    # NOE calculation.
    if function_type == 'noe':
        return noe_obj

    # The N-state model.
    if function_type == 'N-state':
        return n_state_model_obj

    # Relaxation dispersion curve fitting.
    if function_type == 'relax_disp':
        return relax_disp_obj

    # Relaxation curve fitting.
    if function_type == 'relax_fit':
        return relax_fit_obj

    # Reduced spectral density mapping.
    if function_type == 'jw':
        return jw_mapping_obj

    # Model-free analysis.
    if function_type == 'mf':
        return model_free_obj

    # Hybrid models.
    if function_type == 'hybrid':
        return hybrid_obj

    # SRLS.
    if function_type == 'srls':
        return srls_obj

    # Unknown analysis.
    raise RelaxError("The function_type " + repr(function_type) + " is unknown.")


def get_string(function_type):
    """Function for returning a string corresponding to the function type."""

    # Consistency testing.
    if function_type == 'ct':
        return "consistency testing"

    # The Frame Order theories.
    if function_type == 'frame order':
        return "Frame Order theories"

    # NOE calculation.
    if function_type == 'noe':
        return "NOE calculations"

    # The N-state model.
    if function_type == 'N-state':
        return "the N-state model"

    # Relaxation dispersion curve fitting.
    if function_type == 'relax_disp':
        return "relaxation dispersion curve fitting"

    # Relaxation curve fitting.
    if function_type == 'relax_fit':
        return "relaxation curve fitting"

    # Reduced spectral density mapping.
    if function_type == 'jw':
        return "reduced spectral density mapping"

    # Model-free analysis.
    if function_type == 'mf':
        return "Model-free analysis"

    # Hybrid models.
    if function_type == 'hybrid':
        return "hybrid models"

    # SRLS
    if function_type == 'srls':
        return "SRLS analysis"

    # Unknown analysis.
    raise RelaxError("The function_type " + repr(function_type) + " is unknown.")
