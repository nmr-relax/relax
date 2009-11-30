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

# Python module imports.
from copy import deepcopy

# relax module imports.
from generic_fns.mol_res_spin import count_spins, exists_mol_res_spin_data, return_spin, spin_loop
from relax_errors import RelaxError, RelaxImplementError, RelaxLenError, RelaxNoSequenceError


class API_base:
    """Base class defining the specific_fns API.

    Most objects are prototype methods, although a few are operational generic base methods.
    """

    def base_data_loop(self):
        """Generator method for looping over the base data of the specific analysis type.

        This default method simply loops over the spins, returning the spin identification string.

        Specific implementations of this generator method are free to yield any type of data.  The data which is yielded is then passed into the specific functions such as return_data(), return_error(), create_mc_data(), pack_sim_data(), etc., so these methods should handle the data thrown at them.  If multiple data is yielded, this is caught as a tuple and passed into the dependent methods as a tuple.


        @return:    Information concerning the base data of the analysis.  For this base class method, the loop is over the spins and the yielded value is the spin identification string.
        @rtype:     anything
        """

        # Loop over the spins.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Yield the spin id string.
            yield spin_id


    def calculate(self, spin_id=None, verbosity=1, sim_index=None):
        """Prototype method for the calculation of the chi-squared value.

        @keyword spin_id:   The spin identification string.
        @type spin_id:      None or str
        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        @keyword sim_index: The optional MC simulation index.
        @type sim_index:    None or int
        """

        # Not implemented.
        raise RelaxImplementError


    def create_mc_data(self, spin_id=None):
        """Prototype method for creating the Monte Carlo data.

        @keyword spin_id:   The spin identification string, as yielded by the base_data_loop() generator method.
        @type spin_id:      str
        @return:            The Monte Carlo simulation data.
        @rtype:             list of floats
        """

        # Not implemented.
        raise RelaxImplementError


    def data_init(self, data_cont, sim=False):
        """Dummy method for initialising data structures.

        This method does nothing!


        @param data_cont:   The data container.
        @type data_cont:    instance
        @keyword sim:       The Monte Carlo simulation flag, which if true will initialise the simulation data structure.
        @type sim:          bool
        """


    def data_names(self, set='all', error_names=False, sim_names=False):
        """Prototype method for returning a list of names of data structures.

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


    # Empty documentation string.
    default_value_doc = ""
    def default_value(self, param):
        """Prototype method for returning the default parameter values.

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
        """Dummy method for model elimination.

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

        # Don't eliminate.
        return False


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
        """Prototype grid search method.

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
        """Function for testing if errors exist for the run.

        @return:    The answer to the question of whether errors exist.
        @rtype:     bool
        """

        # Diffusion tensor errors.
        if hasattr(cdp, 'diff'):
            for object_name in dir(cdp.diff):
                # The object error name.
                object_error = object_name + '_err'

                # Error exists.
                if hasattr(cdp.diff, object_error):
                    return True

        # Loop over the sequence.
        for spin in spin_loop():
            # Parameter errors.
            for object_name in dir(spin):
                # The object error name.
                object_error = object_name + '_err'

                # Error exists.
                if hasattr(spin, object_error):
                    return True

        # No errors found.
        return False


    def is_spin_param(self, name):
        """Determine whether the given parameter is spin specific.

        This base class method always returns true, hence all parameters will be considered
        residents of a SpinContainer object unless this method is overwritten.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        True
        @rtype:         bool
        """

        # Return the default of True.
        return True


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
        """Prototype minimisation method.

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
        """Default generator method for looping over the models.

        In this case only a single model per spin system is assumed.  Hence the yielded data is the
        spin container object.


        @return:    Information about the model which for this analysis is the spin container.
        @rtype:     SpinContainer instance
        """

        # Loop over the sequence.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Yield the spin container.
            yield spin


    def model_statistics(self, model_info=None, spin_id=None, global_stats=None):
        """Prototype method for returning the k, n, and chi2 model statistics.

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


    def molmol_macro(self, param, style=None, colour_start=None, colour_end=None, colour_list=None, spin_id=None):
        """Create and return an array of Molmol macros.

        @param param:           The parameter name.
        @type param:            str
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
        """Function for returning the number of instances.

        The default in this base class is to return the number of spins.

        @return:    The number of instances (equal to the number of spins).
        @rtype:     int
        """

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Return the number of spins.
        return count_spins()


    def overfit_deselect(self):
        """Dummy function, nornally for deselecting spins with insufficient data for minimisation."""


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
        """Dummy function for returning 1.0.

        @param param:       The parameter name.
        @type param:        str
        @param spin:        Spin container.
        @type spin:         SpinContainer instance
        @return:            A conversion factor of 1.0.
        @rtype:             float
        """

        return 1.0


    def return_data(self, spin):
        """Function for returning the Ri data structure for the given spin.

        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer instance
        @return:        The array of relaxation data values.
        @rtype:         list of float
        """

        return spin.relax_data


    def return_data_desc(self, name, spin=None):
        """Return a description of the spin specific object.

        @param name:    The name of the spin specific object.
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
        """Prototype method for returning a unique identifying string for the given parameter.

        @param param:   The parameter name.
        @type param:    str
        @return:        The unique parameter identifying string.
        @rtype:         str
        """

        # Not implemented.
        raise RelaxImplementError


    def return_error(self, spin_id):
        """Return the Ri error structure for the corresponding spin.

        @param spin_id: The spin identification string, as yielded by the base_data_loop() generator method.
        @type spin_id:  str
        @return:        The array of relaxation data error values.
        @rtype:         list of float
        """

        # Get the spin container.
        spin = return_spin(spin_id)

        # Return the data.
        return spin.relax_error


    def return_grace_string(self, param):
        """Prototype method for returning the Grace string representation of the parameter

        This is used for axis labelling.


        @param param:   The specific analysis parameter.
        @type param:    str
        @return:        The Grace string representation of the parameter.
        @rtype:         str
        """

        # Not implemented.
        raise RelaxImplementError


    def return_units(self, param, spin=None, spin_id=None):
        """Prototype method for returning a string representing the parameters units.

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


    def return_value(self, spin, param, sim=None):
        """Return the value and error corresponding to the parameter 'param'.

        If sim is set to an integer, return the value of the simulation and None.  The values are
        taken from the given SpinContainer object.


        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        @param param:   The name of the parameter to return values for.
        @type param:    str
        @param sim:     The Monte Carlo simulation index.
        @type sim:      None or int
        @return:        The value and error corresponding to
        @rtype:         tuple of length 2 of floats or None
        """

        # Initialise.
        index = None

        # Get the object name.
        object_name = self.return_data_name(param)

        # The error and simulation names.
        if object_name:
            object_error = object_name + '_err'
            object_sim = object_name + '_sim'

        # The data type does not exist.
        else:
            # Is it a spectrum id?
            if param in cdp.spectrum_ids:
                index = cdp.spectrum_ids.index(param)
                object_name = 'intensities'
                object_error = 'intensity_err'
                object_sim = 'intensity_sim'

            # Unknown data type.
            else:
                raise RelaxError("The parameter " + repr(param) + " does not exist.")

        # Initial values.
        value = None
        error = None

        # Value and error.
        if sim == None:
            # Get the value.
            if hasattr(spin, object_name):
                value = getattr(spin, object_name)
                if index != None:
                    value = value[index]
            elif hasattr(cdp, object_name):
                value = getattr(cdp, object_name)
                if index != None:
                    value = value[index]

            # Get the error.
            if hasattr(spin, object_error):
                error = getattr(spin, object_error)
                if index != None:
                    error = error[index]
            elif hasattr(cdp, object_error):
                error = getattr(cdp, object_error)
                if index != None:
                    error = error[index]

        # Simulation value.
        else:
            # Get the value.
            if hasattr(spin, object_sim):
                object = getattr(spin, object_sim)
                if index != None:
                    object = object[index]
                value = object[sim]
            elif hasattr(cdp, object_sim):
                object = getattr(cdp, object_sim)
                if index != None:
                    object = object[index]
                value = object[sim]

        # Return the data.
        return value, error


    # Empty documentation string.
    set_doc = ""


    def set_error(self, model_info, index, error):
        """Set the parameter errors.

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @param index:       The index of the parameter to set the errors for.
        @type index:        int
        @param error:       The error value.
        @type error:        float
        """

        # Assume the default of a spin container.
        spin = model_info

        # Parameter increment counter.
        inc = 0

        # Loop over the residue specific parameters.
        for param in self.data_names(set='params'):
            # Return the parameter array.
            if index == inc:
                setattr(spin, param + "_err", error)

            # Increment.
            inc = inc + 1


    def set_param_values(self, param=None, value=None, spin_id=None, force=True):
        """Prototype method for setting model parameter values.

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

        # Assume the default of a spin container.
        spin = model_info

        # Set the array.
        spin.select_sim = deepcopy(select_sim)


    def set_update(self, param, spin):
        """Dummy function to do nothing!

        @param param:   The name of the parameter which has been changed.
        @type param:    str
        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        """

        return


    def sim_init_values(self):
        """Initialise the Monte Carlo parameter values."""

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min')


        # Test if Monte Carlo parameter values have already been set.
        #############################################################

        # Loop over the spins.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Loop over all the parameter names.
            for object_name in param_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(spin, sim_object_name):
                    raise RelaxError("Monte Carlo parameter values have already been set.")


        # Set the Monte Carlo parameter values.
        #######################################

        # Loop over the residues.
        for spin in spin_loop():
            # Skip deselected residues.
            if not spin.select:
                continue

            # Loop over all the data names.
            for object_name in param_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(spin, sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(spin, sim_object_name)

                # Loop over the simulations.
                for j in xrange(cdp.sim_number):
                    # Copy and append the data.
                    sim_object.append(deepcopy(getattr(spin, object_name)))

            # Loop over all the minimisation object names.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(spin, sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(spin, sim_object_name)

                # Loop over the simulations.
                for j in xrange(cdp.sim_number):
                    # Copy and append the data.
                    sim_object.append(deepcopy(getattr(spin, object_name)))


    def sim_pack_data(self, spin_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param spin_id:     The spin identification string, as yielded by the base_data_loop() generator method.
        @type spin_id:      str
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

        # Assume the default of a spin container.
        spin = model_info

        # Index.
        if index != None:
            return spin.chi2_sim[index]

        # List of vals.
        else:
            return spin.chi2_sim


    def sim_return_param(self, model_info, index):
        """Return the array of simulation parameter values.

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @param index:       The index of the parameter to return the array of values for.
        @type index:        int
        @return:            The array of simulation parameter values.
        @rtype:             list of float
        """

        # Assume the default of a spin container.
        spin = model_info

        # Parameter increment counter.
        inc = 0

        # Loop over the residue specific parameters.
        for param in self.data_names(set='params'):
            # Return the parameter array.
            if index == inc:
                return getattr(spin, param + "_sim")

            # Increment.
            inc = inc + 1


    def sim_return_selected(self, model_info):
        """Return the array of selected simulation flags for the spin.

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @return:            The array of selected simulation flags.
        @rtype:             list of int
        """

        # Assume the default of a spin container.
        spin = model_info

        # Return the array.
        return spin.select_sim


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
        """Function for testing that the grid search options are reasonable.

        @param lower:   The lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:    array of numbers
        @param upper:   The upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:    array of numbers
        @param inc:     The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.
        @type inc:      array of int
        @param n:       The number of parameters in the model.
        @type n:        int
        """

        # Lower bounds test.
        if lower != None:
            if len(lower) != n:
                raise RelaxLenError('lower bounds', n)

        # Upper bounds.
        if upper != None:
            if len(upper) != n:
                raise RelaxLenError('upper bounds', n)

        # Increment.
        if isinstance(inc, list):
            if len(inc) != n:
                raise RelaxLenError('increment', n)
