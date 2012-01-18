###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
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

# Python module imports.
from copy import deepcopy

# relax module imports.
from generic_fns.mol_res_spin import count_spins, exists_mol_res_spin_data, return_spin, spin_loop
from relax_errors import RelaxError, RelaxImplementError, RelaxLenError, RelaxNoSequenceError
from specific_fns.api_objects import Param_list


class API_base:
    """Base class defining the specific_fns API.

    All the methods here are prototype methods.  To identify that the method is not available for certain analysis types, if called a RelaxImplementError is raised if called.
    """

    # Class variables.
    SPIN_PARAMS = Param_list()


    def back_calc_ri(self, spin_index=None, ri_id=None, ri_type=None, frq=None):
        """Back-calculation of relaxation data.

        @keyword spin_index:    The global spin index.
        @type spin_index:       int
        @keyword ri_id:         The relaxation data ID string.
        @type ri_id:            str
        @keyword ri_type:       The relaxation data type.
        @type ri_type:          str
        @keyword frq:           The field strength.
        @type frq:              float
        @return:                The back calculated relaxation data value corresponding to the index.
        @rtype:                 float
        """

        # Not implemented.
        raise RelaxImplementError


    def base_data_loop(self):
        """Generator method for looping over the base data of the specific analysis type.

        Specific implementations of this generator method are free to yield any type of data.  The data which is yielded is then passed into API methods such as return_data(), return_error(), create_mc_data(), pack_sim_data(), etc., so these methods should handle the data thrown at them.  If multiple data is yielded, this is caught as a tuple and passed into the dependent methods as a tuple.


        @return:    Information concerning the base data of the analysis.
        @rtype:     anything
        """

        # Not implemented.
        raise RelaxImplementError


    def bmrb_read(self, file_path, version=None, sample_conditions=None):
        """Prototype method for reading the data from a BMRB NMR-STAR formatted file.

        @param file_path:   The full file path.
        @type file_path:    str
        """

        # Not implemented.
        raise RelaxImplementError


    def bmrb_write(self, file_path, version=None):
        """Prototype method for writing the data to a BMRB NMR-STAR formatted file.

        @param file_path:   The full file path.
        @type file_path:    str
        @keyword version:   The BMRB NMR-STAR dictionary format to output to.
        @type version:      str
        """

        # Not implemented.
        raise RelaxImplementError


    def calculate(self, spin_id=None, verbosity=1, sim_index=None):
        """Calculate the chi-squared value.

        @keyword spin_id:   The spin identification string.
        @type spin_id:      None or str
        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        @keyword sim_index: The optional MC simulation index.
        @type sim_index:    None or int
        """

        # Not implemented.
        raise RelaxImplementError


    def create_mc_data(self, data_id=None):
        """Create the Monte Carlo data.

        @keyword data_id:   The data identification information, as yielded by the base_data_loop() generator method.
        @type data_id:      str
        @return:            The Monte Carlo simulation data.
        @rtype:             list of floats
        """

        # Not implemented.
        raise RelaxImplementError


    def data_init(self, data_cont, sim=False):
        """Initialise the data structures.

        @param data_cont:   The data container.
        @type data_cont:    instance
        @keyword sim:       The Monte Carlo simulation flag, which if true will initialise the simulation data structure.
        @type sim:          bool
        """

        # Not implemented.
        raise RelaxImplementError


    def data_names(self, set='all', error_names=False, sim_names=False):
        """Return a list of names of data structures.

        @keyword set:           The set of object names to return.  This can be set to 'all' for all names, to 'generic' for generic object names, 'params' for analysis specific parameter names, or to 'min' for minimisation specific object names.
        @type set:              str
        @keyword error_names:   A flag which if True will add the error object names as well.
        @type error_names:      bool
        @keyword sim_names:     A flag which if True will add the Monte Carlo simulation object names as well.
        @type sim_names:        bool
        @return:                The list of object names.
        @rtype:                 list of str
        """

        # Not implemented.
        raise RelaxImplementError


    def data_type(self, param=None):
        """Return the type of data that the parameter should be.

        @keyword param:     The parameter name.
        @type param:        list of str
        @return:            The type of the parameter.  I.e. the special Python type objects of int, float, str, bool, [str], {bool}, etc.
        @rtype:             any type
        """

        # Not implemented.
        raise RelaxImplementError


    # Empty documentation string.
    default_value_doc = ""
    def default_value(self, param):
        """Return the default parameter values.

        @param param:   The specific analysis parameter.
        @type param:    str
        @return:        The default value.
        @rtype:         float
        """

        # Not implemented.
        raise RelaxImplementError


    def deselect(self, model_info, sim_index=None):
        """Deselect models or simulations.

        @param model_info:      The model index from model_info().
        @type model_info:       int
        @keyword sim_index:     The optional Monte Carlo simulation index.  If None, then models will be deselected, otherwise the given simulation will.
        @type sim_index:        None or int
        """

        # Not implemented.
        raise RelaxImplementError


    def duplicate_data(self, pipe_from=None, pipe_to=None, model_info=None, global_stats=False, verbose=True):
        """Duplicate the data specific to a single model.

        @keyword pipe_from:     The data pipe to copy the data from.
        @type pipe_from:        str
        @keyword pipe_to:       The data pipe to copy the data to.
        @type pipe_to:          str
        @keyword model_info:    The model index from model_info().
        @type model_info:       int
        @keyword global_stats:  The global statistics flag.
        @type global_stats:     bool
        @keyword verbose:       A flag which if True will cause info to be printed out.
        @type verbose:          bool
        """

        # Not implemented.
        raise RelaxImplementError


    # Empty documentation string.
    eliminate_doc = ""
    def eliminate(self, name, value, model_info, args, sim=None):
        """Model elimination method.

        @param name:        The parameter name.
        @type name:         str
        @param value:       The parameter value.
        @type value:        float
        @param model_info:  The model index from model_info().
        @type model_info:   int
        @param args:        The elimination constant overrides.
        @type args:         None or tuple of float
        @keyword sim:       The Monte Carlo simulation index.
        @type sim:          int
        @return:            True if the model is to be eliminated, False otherwise.
        @rtype:             bool
        """

        # Not implemented.
        raise RelaxImplementError


    def get_param_names(self, model_info=None):
        """Return a vector of parameter names.

        @keyword model_info:    The model index from model_info().
        @type model_info:       int
        @return:                The vector of parameter names.
        @rtype:                 list of str
        """

        # Not implemented.
        raise RelaxImplementError


    def get_param_values(self, model_info=None, sim_index=None):
        """Return a vector of parameter values.

        @keyword model_info:    The model index from model_info().
        @type model_info:       int
        @keyword sim_index:     The optional Monte Carlo simulation index.
        @type sim_index:        int
        @return:                The vector of parameter values.
        @rtype:                 list of str
        """

        # Not implemented.
        raise RelaxImplementError


    def grid_search(self, lower=None, upper=None, inc=None, constraints=True, verbosity=1, sim_index=None):
        """Grid search method.

        @keyword lower:         The lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:            array of numbers
        @keyword upper:         The upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:            array of numbers
        @keyword inc:           The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.
        @type inc:              array of int
        @keyword constraints:   If True, constraints are applied during the grid search (eliminating parts of the grid).  If False, no constraints are used.
        @type constraints:      bool
        @keyword verbosity:     A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:        int
        @keyword sim_index:     The index of the simulation to apply the grid search to.  If None, the normal model is optimised.
        @type sim_index:        int
        """

        # Not implemented.
        raise RelaxImplementError


    def has_errors(self):
        """Test if errors exist for the current data pipe.

        @return:    The answer to the question of whether errors exist.
        @rtype:     bool
        """

        # Not implemented.
        raise RelaxImplementError


    def is_spin_param(self, name):
        """Determine whether the given parameter is spin specific.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        True if the parameter is spin specific, False otherwise.
        @rtype:         bool
        """

        # Not implemented.
        raise RelaxImplementError


    def map_bounds(self, param, spin_id=None):
        """Create bounds for the OpenDX mapping function.

        @param param:       The name of the parameter to return the lower and upper bounds of.
        @type param:        str
        @param spin_id:     The spin identification string.
        @type spin_id:      None or str
        @return:            The upper and lower bounds of the parameter.
        @rtype:             list of float
        """

        # Not implemented.
        raise RelaxImplementError


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Minimisation method.

        @keyword min_algor:         The minimisation algorithm to use.
        @type min_algor:            str
        @keyword min_options:       An array of options to be used by the minimisation algorithm.
        @type min_options:          array of str
        @keyword func_tol:          The function tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type func_tol:             None or float
        @keyword grad_tol:          The gradient tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type grad_tol:             None or float
        @keyword max_iterations:    The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        @keyword constraints:       If True, constraints are used during optimisation.
        @type constraints:          bool
        @keyword scaling:           If True, diagonal scaling is enabled during optimisation to allow the problem to be better conditioned.
        @type scaling:              bool
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:            None or int
        @keyword lower:             The lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  array of int
        """

        # Not implemented.
        raise RelaxImplementError


    def model_desc(self, model_info):
        """Return a description of the model.

        @param model_info:  The model index from model_info().
        @type model_info:   int
        @return:            The model description.
        @rtype:             str
        """

        # Not implemented.
        raise RelaxImplementError


    def model_loop(self):
        """Generator method for looping over the models.

        @return:    Information identifying the model.
        @rtype:     anything
        """

        # Not implemented.
        raise RelaxImplementError


    def model_statistics(self, model_info=None, spin_id=None, global_stats=None):
        """Return the k, n, and chi2 model statistics.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.


        @keyword model_info:    The model index from model_info().
        @type model_info:       None or int
        @keyword spin_id:       The spin identification string.  This is ignored in the N-state model.
        @type spin_id:          None or str
        @keyword global_stats:  A parameter which determines if global or local statistics are returned.  For the N-state model, this argument is ignored.
        @type global_stats:     None or bool
        @return:                The optimisation statistics, in tuple format, of the number of parameters (k), the number of data points (n), and the chi-squared value (chi2).
        @rtype:                 tuple of (int, int, float)
        """

        # Not implemented.
        raise RelaxImplementError


    def model_type(self):
        """Return the type of the model, either being 'local' or 'global'.

        @return:            The model type, one of 'local' or 'global'.
        @rtype:             str
        """

        # Not implemented.
        raise RelaxImplementError


    def molmol_macro(self, data_type, style=None, colour_start=None, colour_end=None, colour_list=None, spin_id=None):
        """Create and return an array of Molmol macros.

        @param data_type:       The parameter name or data type.
        @type data_type:        str
        @keyword style:         The Molmol style.
        @type style:            None or str
        @keyword colour_start:  The starting colour (must be a MOLMOL or X11 name).
        @type colour_start:     str
        @keyword colour_end:    The ending colour (must be a MOLMOL or X11 name).
        @type colour_end:       str
        @keyword colour_list:   The colour list used, either 'molmol' or 'x11'.
        @type colour_list:      str
        @keyword spin_id:       The spin identification string.
        @type spin_id:          str
        """

        # Not implemented.
        raise RelaxImplementError


    def num_instances(self):
        """Return the number of instances (depreciated).

        @return:    The number of instances.
        @rtype:     int
        """

        # Not implemented.
        raise RelaxImplementError


    def overfit_deselect(self):
        """Deselect models with insufficient data for minimisation."""

        # Not implemented.
        raise RelaxImplementError


    def pymol_macro(self, data_type, style=None, colour_start=None, colour_end=None, colour_list=None, spin_id=None):
        """Create and return an array of PyMOL macros.

        @param data_type:       The parameter name or data type.
        @type data_type:        str
        @keyword style:         The PyMOL style.
        @type style:            None or str
        @keyword colour_start:  The starting colour (must be a MOLMOL or X11 name).
        @type colour_start:     str
        @keyword colour_end:    The ending colour (must be a MOLMOL or X11 name).
        @type colour_end:       str
        @keyword colour_list:   The colour list used, either 'molmol' or 'x11'.
        @type colour_list:      str
        @keyword spin_id:       The spin identification string.
        @type spin_id:          str
        """

        # Not implemented.
        raise RelaxImplementError


    def read_columnar_results(self, file_data, verbosity=1):
        """Read the columnar formatted results file.

        @param file_data:   The processed results file data.
        @type file_data:    list of lists of str
        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        """

        # Not implemented.
        raise RelaxImplementError


    def return_conversion_factor(self, param, spin=None, spin_id=None):
        """Return the conversion factor.

        @param param:       The parameter name.
        @type param:        str
        @param spin:        Spin container.
        @type spin:         SpinContainer instance
        @return:            A conversion factor of 1.0.
        @rtype:             float
        """

        # Not implemented.
        raise RelaxImplementError


    def return_data(self, spin):
        """Return the data points used in optimisation.

        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer instance
        @return:        The array of relaxation data values.
        @rtype:         list of float
        """

        # Not implemented.
        raise RelaxImplementError


    def return_data_desc(self, name, spin=None):
        """Return a description of the parameter.

        @param name:    The name or description of the parameter.
        @type name:     str
        @param spin:    The spin container.
        @type spin:     SpinContainer instance
        @return:        The object description, or None.
        @rtype:         str or None
        """

        # Not implemented.
        raise RelaxImplementError


    # Empty documentation string.
    return_data_name_doc = ""
    def return_data_name(self, param):
        """Return a unique identifying string for the given parameter.

        @param param:   The parameter name.
        @type param:    str
        @return:        The unique parameter identifying string.
        @rtype:         str
        """

        # Not implemented.
        raise RelaxImplementError


    def return_error(self, data_id):
        """Return the error points corresponding to the data points used in optimisation.

        @param data_id: The data identification information, as yielded by the base_data_loop() generator method.
        @type data_id:  str
        @return:        The array of relaxation data error values.
        @rtype:         list of float
        """

        # Not implemented.
        raise RelaxImplementError


    def return_grace_string(self, param):
        """Return the Grace string representation of the parameter.

        This is used for axis labelling.


        @param param:   The specific analysis parameter.
        @type param:    str
        @return:        The Grace string representation of the parameter.
        @rtype:         str
        """

        # Not implemented.
        raise RelaxImplementError


    def return_units(self, param, spin=None, spin_id=None):
        """Return a string representing the parameters units.

        @param param:       The name of the parameter to return the units string for.
        @type param:        str
        @keyword spin:      The spin container.
        @type spin:         SpinContainer instance
        @keyword spin_id:   The spin identification string (ignored if the spin container is supplied).
        @type spin_id:      str
        @return:            The parameter units string.
        @rtype:             str
        """

        # Not implemented.
        raise RelaxImplementError


    def return_value(self, spin, param, sim=None, bc=False):
        """Return the value and error corresponding to the parameter.

        If sim is set to an integer, return the value of the simulation and None.


        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        @param param:   The name of the parameter to return values for.
        @type param:    str
        @keyword sim:   The Monte Carlo simulation index.
        @type sim:      None or int
        @keyword bc:    The back-calculated data flag.  If True, then the back-calculated data will be returned rather than the actual data.
        @type bc:       bool
        @return:        The value and error corresponding to
        @rtype:         tuple of length 2 of floats or None
        """

        # Not implemented.
        raise RelaxImplementError


    # Empty documentation string.
    set_doc = ""


    def set_error(self, model_info, index, error):
        """Set the model parameter errors.

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @param index:       The index of the parameter to set the errors for.
        @type index:        int
        @param error:       The error value.
        @type error:        float
        """

        # Not implemented.
        raise RelaxImplementError


    def set_param_values(self, param=None, value=None, spin_id=None, force=True):
        """Set the model parameter values.

        @keyword param:     The parameter name list.
        @type param:        list of str
        @keyword value:     The parameter value list.
        @type value:        list
        @keyword spin_id:   The spin identification string, only used for spin specific parameters.
        @type spin_id:      None or str
        @keyword force:     A flag which if True will cause current values to be overwritten.  If False, a RelaxError will raised if the parameter value is already set.
        @type force:        bool
        """

        # Not implemented.
        raise RelaxImplementError


    def set_selected_sim(self, model_info, select_sim):
        """Set the simulation selection flag.

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @param select_sim:  The selection flag for the simulations.
        @type select_sim:   bool
        """

        # Not implemented.
        raise RelaxImplementError


    def set_update(self, param, spin):
        """Update other parameter values.

        @param param:   The name of the parameter which has been changed.
        @type param:    str
        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        """

        # Not implemented.
        raise RelaxImplementError


    def sim_init_values(self):
        """Initialise the Monte Carlo parameter values."""

        # Not implemented.
        raise RelaxImplementError


    def sim_pack_data(self, data_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param data_id:     The data identification information, as yielded by the base_data_loop() generator method.
        @type data_id:      str
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # Not implemented.
        raise RelaxImplementError


    def sim_return_chi2(self, model_info, index=None):
        """Return the simulation chi-squared values.

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @keyword index:     The optional simulation index.
        @type index:        int
        @return:            The list of simulation chi-squared values.  If the index is supplied, only a single value will be returned.
        @rtype:             list of float or float
        """

        # Not implemented.
        raise RelaxImplementError


    def sim_return_param(self, model_info, index):
        """Return the array of simulation parameter values.

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @param index:       The index of the parameter to return the array of values for.
        @type index:        int
        @return:            The array of simulation parameter values.
        @rtype:             list of float
        """

        # Not implemented.
        raise RelaxImplementError


    def sim_return_selected(self, model_info):
        """Return the array of selected simulation flags for the spin.

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @return:            The array of selected simulation flags.
        @rtype:             list of int
        """

        # Not implemented.
        raise RelaxImplementError


    def skip_function(self, model_info):
        """Skip certain data.

        @param model_info:  The model index from model_loop().
        @type model_info:   int
        @return:            True if the data should be skipped, False otherwise.
        @rtype:             bool
        """

        # Not implemented.
        raise RelaxImplementError


    def test_grid_ops(self, lower=None, upper=None, inc=None, n=None):
        """Test that the grid search options are reasonable.

        @param lower:   The lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:    array of numbers
        @param upper:   The upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:    array of numbers
        @param inc:     The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.
        @type inc:      array of int
        @param n:       The number of parameters in the model.
        @type n:        int
        """

        # Not implemented.
        raise RelaxImplementError
