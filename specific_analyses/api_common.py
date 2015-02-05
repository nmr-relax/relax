###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
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
"""Common API methods for use in different specific analyses."""

# Python module imports.
from copy import deepcopy
import sys

# relax module imports.
import lib.arg_check
from lib.errors import RelaxError, RelaxNoSequenceError
from lib.text.sectioning import subsection
from pipe_control.mol_res_spin import count_spins, exists_mol_res_spin_data, return_spin, spin_loop


class API_common:
    """Base class containing API methods common to multiple analysis types."""

    def _base_data_loop_spin(self):
        """Generator method for looping over the base data of the specific analysis type (spin system specific).

        This method simply loops over the spins, returning the spin identification string.

        @return:    The spin identification string
        @rtype:     str
        """

        # Loop over the spins.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Yield the spin id string.
            yield spin_id


    def _create_mc_relax_data(self, data_id):
        """Return the Monte Carlo relaxation data list for the corresponding spin.

        @param data_id:     The spin identification string, as yielded by the base_data_loop() generator method.
        @type data_id:      str
        """

        # Get the spin container.
        spin = return_spin(data_id)

        # Initialise the data structure.
        data = []

        # Add the data.
        for ri_id in cdp.ri_ids:
            data.append(spin.ri_data[ri_id])

        # Return the data.
        return data


    def _data_init_dummy(self, data, sim=False):
        """Dummy method for initialising data structures.

        This method does nothing!


        @param data:    The data from the base_data_loop() method.
        @type data:     instance
        @keyword sim:   The unused Monte Carlo simulation flag.
        @type sim:      bool
        """


    def _data_init_spin(self, data, sim=False):
        """Initialise data structures (spin system specific).

        @param data:    The spin ID string from the _base_data_loop_spin() method.
        @type data:     str
        @keyword sim:   The Monte Carlo simulation flag, which if true will initialise the simulation data structure.
        @type sim:      bool
        """

        # Alias the data and get the spin container.
        spin_id = data
        spin = return_spin(spin_id)

        # Loop over the parameters.
        for name in self._PARAMS.loop(set='params', scope='spin', error_names=False, sim_names=sim):
            # Not a parameter of the model.
            if name not in spin.params:
                continue

            # The value already exists.
            if hasattr(spin, name):
                continue

            # The default value.
            param_type = self._PARAMS.type(name)
            if param_type == dict:
                value = {}
            elif param_type == list:
                value = []
            else:
                value = None

            # Set the value.
            setattr(spin, name, value)


    def _deselect_global(self, sim_index=None, model_info=None):
        """Common method for deselecting a global model.

        @keyword sim_index:     The optional Monte Carlo simulation index.  If None, then models will be deselected, otherwise the given simulation will.
        @type sim_index:        None or int
        @keyword model_info:    The model information from _model_loop_single_global().  This should be zero for the single global model.
        @type model_info:       int
        """

        # The simulation structure.
        if sim_index != None:
            cdp.select_sim[sim_index] = False

        # The model.
        else:
            cdp.select = False


    def _eliminate_false(self, name, value, args, sim=None, model_info=None):
        """Dummy method for model elimination.

        This simply returns False to signal that no model elimination is to be performed.


        @param name:            The parameter name.
        @type name:             str
        @param value:           The parameter value.
        @type value:            float
        @param args:            The elimination constant overrides.
        @type args:             None or tuple of float
        @keyword sim:           The Monte Carlo simulation index.
        @type sim:              int
        @keyword model_info:    The model information from model_loop().
        @type model_info:       unknown
        @return:                False to prevent model elimination.
        @rtype:                 bool
        """

        # Don't eliminate.
        return False


    def _has_errors_spin(self):
        """Testing if errors exist for the current data pipe (spin system specific).

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


    def _is_spin_param_false(self, name):
        """Common method stating that the parameter is not spin specific.

        This method always returns False, hence all parameters will be considered global.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        False
        @rtype:         bool
        """

        # Return the default of False.
        return False


    def _is_spin_param_true(self, name):
        """Common method stating that the parameter is spin specific.

        This method always returns true, hence all parameters will be considered residents of a SpinContainer object.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        True
        @rtype:         bool
        """

        # Return the default of True.
        return True


    def _model_loop_spin(self):
        """Default generator method for looping over the models, where each spin has a separate model.

        In this case only a single model per spin system is assumed.  The yielded data is the spin container object.  The spin ID string is also yielded to allow the corresponding spin container to be identified.


        @return:    The spin container and the spin ID string.
        @rtype:     SpinContainer instance, str
        """

        # Loop over the sequence.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Yield the spin container and ID.
            yield spin, spin_id


    def _model_loop_single_global(self):
        """Default generator method for looping over a single global (non-spin specific) model.

        The loop will yield a single index, zero, once to indicate a single model.


        @return:    The global model index of zero.
        @rtype:     int
        """

        # Yield the index zero.
        yield 0


    def _model_type_global(self):
        """Return the type of the model as being 'global'.

        @return:            The model type of 'global'.
        @rtype:             str
        """

        # Global models.
        return 'global'


    def _model_type_local(self):
        """Return the type of the model as being 'local'.

        @return:            The model type of 'local'.
        @rtype:             str
        """

        # Local models.
        return 'local'


    def _num_instances_spin(self):
        """Return the number of instances, equal to the number of selected spins.

        @return:    The number of instances (equal to the number of spins).
        @rtype:     int
        """

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Return the number of spins.
        return count_spins()


    def _overfit_deselect_dummy(self, data_check=True, verbose=True):
        """Dummy method, normally for deselecting spins with insufficient data for minimisation."""


    def _print_model_title_global(self, prefix=None, model_info=None):
        """Default method for when the model_loop() method simply loops over a single global model.

        @keyword prefix:        The starting text of the title.  This should be printed out first, followed by the model information text.
        @type prefix:           str
        @keyword model_info:    The model information from _model_loop_single_global().  This should be zero for the single global model.
        @type model_info:       int
        """

        # Create the text from the prefix and model info.
        text = ''
        if prefix:
            text += prefix
        else:
            text += 'Model '
        text += repr(model_info)

        # The printout.
        subsection(file=sys.stdout, text=text, prespace=2)


    def _print_model_title_spin(self, prefix=None, model_info=None):
        """Default method for when the model_loop() method simply loops over spins.

        @keyword prefix:        The starting text of the title.  This should be printed out first, followed by the model information text.
        @type prefix:           str
        @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() method.
        @type model_info:       SpinContainer instance, str
        """

        # The printout.
        spin_id = model_info[1]
        text = prefix + "The spin %s" % spin_id
        subsection(file=sys.stdout, text=text, prespace=2)


    def _return_no_conversion_factor(self, param):
        """Method for returning 1.0.

        @param param:       The parameter name.
        @type param:        str
        @return:            A conversion factor of 1.0.
        @rtype:             float
        """

        return 1.0


    def _return_data_relax_data(self, spin):
        """Return the Ri data structure for the given spin.

        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer instance
        @return:        The array of relaxation data values.
        @rtype:         list of float
        """

        # Convert to a list.
        data = []
        for ri_id in cdp.ri_ids:
            # Handle missing data.
            if ri_id not in spin.ri_data:
                data.append(None)

            # Append the value.
            else:
                data.append(spin.ri_data[ri_id])

        # Return the list.
        return data


    def _return_error_relax_data(self, data_id):
        """Return the Ri error structure for the corresponding spin.

        @param data_id: The data identification information, as yielded by the base_data_loop() generator method.
        @type data_id:  str
        @return:        The array of relaxation data error values.
        @rtype:         list of float
        """

        # Get the spin container.
        spin = return_spin(data_id)

        # Convert to a list.
        error = []
        for ri_id in cdp.ri_ids:
            # Handle missing data/errors.
            if ri_id not in spin.ri_data_err:
                error.append(None)

            # Append the value.
            else:
                error.append(spin.ri_data_err[ri_id])

        # Return the list.
        return error


    def _return_value_general(self, spin, param, sim=None, bc=False):
        """Return the value and error corresponding to the parameter 'param'.

        If sim is set to an integer, return the value of the simulation and None.  The values are taken from the given SpinContainer object.


        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        @param param:   The name of the parameter to return values for.
        @type param:    str
        @param sim:     The Monte Carlo simulation index.
        @type sim:      None or int
        @keyword bc:    The back-calculated data flag.  If True, then the back-calculated data will be returned rather than the actual data.
        @type bc:       bool
        @return:        The value and error corresponding to
        @rtype:         tuple of length 2 of floats or None
        """

        # Initialise.
        index = None

        # The error, simulation and back calculated names.
        if param:
            object_error = param + '_err'
            object_sim = param + '_sim'
            object_bc = param + '_bc'
            key = None

        # The data type does not exist.
        else:
            # Is it a spectrum id?
            if hasattr(cdp, 'spectrum_ids') and param in cdp.spectrum_ids:
                param = 'intensity'
                object_error = 'intensity_err'
                object_sim = 'intensity_sim'
                object_bc = 'intensity_bc'
                key = param

            # Unknown data type.
            else:
                raise RelaxError("The parameter " + repr(param) + " does not exist.")

        # Initial values.
        value = None
        error = None

        # Switch to back calculated data.
        if bc:
            param = object_bc

        # Value or sim value?
        if sim != None:
            param = object_sim

        # The spin value.
        if hasattr(spin, param):
            value = getattr(spin, param)

        # The spin error.
        if hasattr(spin, object_error):
            error = getattr(spin, object_error)

        # The global value.
        elif hasattr(cdp, param):
            value = getattr(cdp, param)

            # The error.
            if hasattr(cdp, object_error):
                error = getattr(cdp, object_error)

        # List object.
        if index != None:
            value = value[index]
            if error:
                error = error[index]

        # Dictionary object.
        if key:
            # Handle missing data.
            if key not in value:
                value = None
            else:
                value = value[key]

            if error:
                # Handle missing errors.
                if key not in error:
                    error = None
                else:
                    error = error[key]

        # Return the data.
        if sim == None:
            return value, error
        elif value == None:
            return value, error
        else:
            return value[sim], error


    def _set_error_spin(self, index, error, model_info=None):
        """Set the parameter errors (spin system specific).

        @param index:           The index of the parameter to set the errors for.
        @type index:            int
        @param error:           The error value.
        @type error:            float
        @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() method.
        @type model_info:       SpinContainer instance, str
        """

        # Unpack the data.
        spin, spin_id = model_info

        # Parameter increment counter.
        inc = 0

        # Loop over the residue specific parameters.
        for param in self.data_names(set='params'):
            # Return the parameter array.
            if index == inc:
                setattr(spin, param + "_err", error)

            # Increment.
            inc = inc + 1


    def _set_param_values_global(self, param=None, value=None, index=None, spin_id=None, error=False, force=True):
        """Set the global parameter values in the top layer of the data pipe.

        @keyword param:     The parameter name list.
        @type param:        list of str
        @keyword value:     The parameter value list.
        @type value:        list
        @keyword index:     The index for parameters which are of the list-type.  This is unused.
        @type index:        None or int
        @keyword spin_id:   The spin identification string (unused).
        @type spin_id:      None
        @keyword error:     A flag which if True will allow the parameter errors to be set instead of the values.
        @type error:        bool
        @keyword force:     A flag which if True will cause current values to be overwritten.  If False, a RelaxError will raised if the parameter value is already set.
        @type force:        bool
        """

        # Checks.
        lib.arg_check.is_str_list(param, 'parameter name')
        lib.arg_check.is_list(value, 'parameter value')

        # Loop over the parameters.
        for i in range(len(param)):
            # Is the parameter is valid?
            if not param[i]:
                raise RelaxError("The parameter '%s' is not valid for this data pipe type." % param[i])

            # Error object.
            if error:
                param[i] += '_err'

            # Is the parameter already set.
            if not force and hasattr(cdp, param[i]) and getattr(cdp, param[i]) != None:
                raise RelaxError("The parameter '%s' already exists, set the force flag to True to overwrite." % param[i])

            # Set the parameter.
            setattr(cdp, param[i], value[i])


    def _set_param_values_spin(self, param=None, value=None, index=None, spin_id=None, error=False, force=True):
        """Set the spin specific parameter values.

        @keyword param:     The parameter name list.
        @type param:        list of str
        @keyword value:     The parameter value list.
        @type value:        list
        @keyword index:     The index for parameters which are of the list-type.  This is unused.
        @type index:        None or int
        @keyword spin_id:   The spin identification string, only used for spin specific parameters.
        @type spin_id:      None or str
        @keyword error:     A flag which if True will allow the parameter errors to be set instead of the values.
        @type error:        bool
        @keyword force:     A flag which if True will cause current values to be overwritten.  If False, a RelaxError will raised if the parameter value is already set.
        @type force:        bool
        """

        # Checks.
        lib.arg_check.is_str_list(param, 'parameter name')
        lib.arg_check.is_list(value, 'parameter value')

        # Loop over the parameters.
        for i in range(len(param)):
            # Is the parameter is valid?
            if not self._PARAMS.contains(param[i]):
                raise RelaxError("The parameter '%s' is not valid for this data pipe type." % param[i])

            # Spin loop.
            for spin in spin_loop(spin_id):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # The object name.
                obj_name = param[i]
                if error:
                    obj_name += '_err'

                # Set the parameter.
                param_type = self._PARAMS.type(param[i])
                if param_type == dict:
                    obj = getattr(spin, obj_name)
                    for key in obj:
                        obj[key] = value[i]
                elif param_type == list:
                    obj = getattr(spin, obj_name)
                    for j in range(len(obj)):
                        obj[j] = value[i]
                else:
                    setattr(spin, obj_name, value[i])


    def _set_selected_sim_global(self, select_sim, model_info=None):
        """Set the simulation selection flag (for a single global model).

        @param select_sim:      The selection flag for the simulations.
        @type select_sim:       bool
        @keyword model_info:    The model information from _model_loop_single_global().  This should be zero for the single global model.
        @type model_info:       int
        """

        # Set the array.
        cdp.select_sim = deepcopy(select_sim)


    def _set_selected_sim_spin(self, select_sim, model_info=None):
        """Set the simulation selection flag (spin system specific).

        @param select_sim:      The selection flag for the simulations.
        @type select_sim:       bool
        @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() method.
        @type model_info:       SpinContainer instance, str
        """

        # Unpack the data.
        spin, spin_id = model_info

        # Set the array.
        spin.select_sim = deepcopy(select_sim)


    def _set_update(self, param, spin):
        """Dummy method to do nothing!

        @param param:   The name of the parameter which has been changed.
        @type param:    str
        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        """


    def _sim_init_values_spin(self):
        """Initialise the Monte Carlo parameter values (spin system specific)."""

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


        # Set the Monte Carlo parameter values.
        #######################################

        # Loop over the residues.
        for spin in spin_loop():
            # Skip deselected residues.
            if not spin.select:
                continue

            # Loop over all the data names.
            for object_name in param_names:
                # Not a parameter of the model.
                if object_name not in spin.params:
                    continue

                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(spin, sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(spin, sim_object_name)

                # Loop over the simulations.
                for j in range(cdp.sim_number):
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
                for j in range(cdp.sim_number):
                    # Copy and append the data.
                    sim_object.append(deepcopy(getattr(spin, object_name)))


    def _sim_pack_relax_data(self, data_id, sim_data):
        """Pack the Monte Carlo simulation relaxation data into the corresponding spin container.

        @param data_id:     The spin identification string, as yielded by the base_data_loop() generator method.
        @type data_id:      str
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # Get the spin container.
        spin = return_spin(data_id)

        # Initialise the data structure.
        spin.ri_data_sim = {}

        # Loop over the relaxation data.
        for i in range(len(cdp.ri_ids)):
            # The ID.
            ri_id = cdp.ri_ids[i]

            # Initialise the MC data list.
            spin.ri_data_sim[ri_id] = []

            # Loop over the simulations.
            for j in range(cdp.sim_number):
                spin.ri_data_sim[ri_id].append(sim_data[j][i])


    def _sim_return_chi2_spin(self, index=None, model_info=None):
        """Return the simulation chi-squared values (spin system specific).

        @keyword index:         The optional simulation index.
        @type index:            int
        @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() method.
        @type model_info:       SpinContainer instance, str
        @return:                The list of simulation chi-squared values.  If the index is supplied, only a single value will be returned.
        @rtype:                 list of float or float
        """

        # Unpack the data.
        spin, spin_id = model_info

        # Index.
        if index != None:
            return spin.chi2_sim[index]

        # List of vals.
        else:
            return spin.chi2_sim


    def _sim_return_param_spin(self, index, model_info=None):
        """Return the array of simulation parameter values (spin system specific).

        @param index:           The index of the parameter to return the array of values for.
        @type index:            int
        @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() method.
        @type model_info:       SpinContainer instance, str
        @return:                The array of simulation parameter values.
        @rtype:                 list of float
        """

        # Unpack the data.
        spin, spin_id = model_info

        # Parameter increment counter.
        inc = 0

        # Loop over the residue specific parameters.
        for param in self.data_names(set='params'):
            # Not a parameter of the model.
            if param not in spin.params:
                continue

            # Return the parameter array.
            if index == inc:
                return getattr(spin, param + "_sim")

            # Increment.
            inc = inc + 1


    def _sim_return_selected_global(self, model_info=None):
        """Return the array of selected simulation flags for the global model.

        @keyword model_info:    The model information from _model_loop_single_global().  This should be zero for the single global model.
        @type model_info:       int
        @return:                The array of selected simulation flags.
        @rtype:                 list of int
        """

        # Return the array.
        return cdp.select_sim


    def _sim_return_selected_spin(self, model_info=None):
        """Return the array of selected simulation flags (spin system specific).

        @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() method.
        @type model_info:       SpinContainer instance, str
        @return:                The array of selected simulation flags.
        @rtype:                 list of int
        """

        # Unpack the data.
        spin, spin_id = model_info

        # Return the array.
        return spin.select_sim
