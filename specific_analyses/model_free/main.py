###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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
"""The main methods of the specific API for model-free analysis."""

# Python module imports.
from copy import deepcopy
from math import pi
from numpy import float64, array, identity, zeros
from re import match, search
from types import MethodType
from warnings import warn

# relax module imports.
import lib.arg_check
from lib.errors import RelaxError, RelaxFault, RelaxFuncSetupError, RelaxNoModelError, RelaxNoSequenceError, RelaxNoTensorError, RelaxTensorError
from lib.float import isInf
from lib.warnings import RelaxDeselectWarning, RelaxWarning
from pipe_control import diffusion_tensor, interatomic, pipes, sequence
from pipe_control.mol_res_spin import count_spins, exists_mol_res_spin_data, find_index, return_spin, return_spin_from_index, return_spin_indices, spin_loop
import specific_analyses
from specific_analyses.model_free.parameters import assemble_param_names, assemble_param_vector, determine_model_type


class Model_free_main:
    """Class containing functions specific to model-free analysis."""

    def back_calc_ri(self, spin_index=None, ri_id=None, ri_type=None, frq=None):
        """Back-calculation of relaxation data from the model-free parameter values.

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

        # Get the spin container.
        spin, spin_id = return_spin_from_index(global_index=spin_index, return_spin_id=True)

        # Missing interatomic vectors.
        if hasattr(cdp, 'diff_tensor') and (cdp.diff_tensor.type == 'spheroid' or cdp.diff_tensor.type == 'ellipsoid'):
            interatoms = interatomic.return_interatom_list(spin_id)
            for i in range(len(interatoms)):
                # No dipolar relaxation mechanism.
                if not interatoms[i].dipole_pair:
                    continue

                # Check the unit vectors.
                if not hasattr(interatoms[i], 'vector') or interatoms[i].vector == None:
                    warn(RelaxDeselectWarning(spin_id, 'missing structural data'))
                    return

        # Execute the over-fit deselection.
        self.overfit_deselect(data_check=False, verbose=False)

        # Get the relaxation value from the minimise function.
        value = self.minimise(min_algor='back_calc', min_options=(spin_index, ri_id, ri_type, frq))

        # Return the relaxation value.
        return value


    def _compare_objects(self, object_from, object_to, pipe_from, pipe_to):
        """Compare the contents of the two objects and raise RelaxErrors if they are not the same.

        @param object_from: The first object.
        @type object_from:  any object
        @param object_to:   The second object.
        @type object_to:    any object
        @param pipe_from:   The name of the data pipe containing the first object.
        @type pipe_from:    str
        @param pipe_to:     The name of the data pipe containing the second object.
        @type pipe_to:      str
        """

        # Loop over the modifiable objects.
        for data_name in dir(object_from):
            # Skip special objects (starting with _, or in the original class and base class namespaces).
            if search('^_', data_name) or data_name in list(object_from.__class__.__dict__.keys()) or (hasattr(object_from.__class__, '__bases__') and len(object_from.__class__.__bases__) and data_name in list(object_from.__class__.__bases__[0].__dict__.keys())):
                continue

            # Skip some more special objects.
            if data_name in ['structural_data']:
                continue

            # Get the original object.
            data_from = None
            if hasattr(object_from, data_name):
                data_from = getattr(object_from, data_name)

            # Get the target object.
            if data_from and not hasattr(object_to, data_name):
                raise RelaxError("The structural object " + repr(data_name) + " of the " + repr(pipe_from) + " data pipe is not located in the " + repr(pipe_to) + " data pipe.")
            elif data_from:
                data_to = getattr(object_to, data_name)
            else:
                continue

            # The data must match!
            if data_from != data_to:
                raise RelaxError("The object " + repr(data_name) + " is not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")


    def create_mc_data(self, data_id=None):
        """Create the Monte Carlo Ri data.

        @keyword data_id:   The spin identification string, as yielded by the base_data_loop() generator method.
        @type data_id:      str
        @return:            The Monte Carlo simulation data.
        @rtype:             list of floats
        """

        # Initialise the MC data structure.
        mc_data = []

        # Get the spin container and global spin index.
        spin = return_spin(data_id)
        global_index = find_index(data_id)

        # Skip deselected spins.
        if not spin.select:
            return

        # Test if the model is set, returning None to signal that the spin should be skipped.
        if not hasattr(spin, 'model') or not spin.model:
            return None

        # Loop over the relaxation data.
        for ri_id in cdp.ri_ids:
            # Back calculate the value.
            value = self.back_calc_ri(spin_index=global_index, ri_id=ri_id, ri_type=cdp.ri_type[ri_id], frq=cdp.spectrometer_frq[ri_id])

            # Append the value.
            mc_data.append(value)

        # Return the data.
        return mc_data


    def data_init(self, data_cont, sim=False):
        """Initialise the spin specific data structures.

        @param data_cont:   The spin data container.
        @type data_cont:    SpinContainer instance
        @keyword sim:       The Monte Carlo simulation flag, which if true will initialise the simulation data structure.
        @type sim:          bool
        """

        # Loop over the data structure names.
        for name in self.PARAMS.loop(scope='spin'):
            # Blacklisted data structures.
            if name in ['ri_data', 'ri_data_bc', 'ri_data_err']:
                continue

            # Data structures which are initially empty arrays.
            list_data = [ 'params' ]
            if name in list_data:
                init_data = []

            # Set everything else initially to None or False.
            init_data = None
            if self.PARAMS.get_type(name) == bool:
                init_data = False
                if name == 'select':
                    init_data = True

            # If the name is not in 'data_cont', add it.
            if not hasattr(data_cont, name):
                setattr(data_cont, name, init_data)


    def data_type(self, param=None):
        """Return the type of data, as a string, that the parameter should be.

        @keyword param:     The parameter name.
        @type param:        list of str
        @return:            The type of the parameter, as a string.  I.e. 'int', 'float', 'str', 'bool', 'list of str', 'dict of bool', etc.
        @rtype:             str
        """

        # A dictionary of all the types.
        types = {
            'select':           bool,
            'fixed':            bool,
            'nucleus':          str,
            'model':            str,
            'equation':         str,
            'params':           [str],
            's2':               float,
            's2f':              float,
            's2s':              float,
            'local_tm':         float,
            'te':               float,
            'tf':               float,
            'ts':               float,
            'rex':              float,
            'csa':              float,
            'chi2':             float,
            'iter':             int,
            'f_count':          int,
            'g_count':          int,
            'h_count':          int,
            'warning':          str
        }

        # Return the type, if in the list.
        if param in types:
            return types[param]


    def default_value(self, param):
        """The default model-free parameter values.

        @param param:   The model-free parameter.
        @type param:    str
        @return:        The default value.
        @rtype:         float
        """

        # Diffusion tensor parameter.
        diff_val = diffusion_tensor.default_value(param)
        if diff_val != None:
            return diff_val

        # Model-free parameter.
        return self.PARAMS.get_default(param)


    def deselect(self, model_info, sim_index=None):
        """Deselect models or simulations.

        @param model_info:      The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @keyword sim_index:     The optional Monte Carlo simulation index.  If None, then models will be deselected, otherwise the given simulation will.
        @type sim_index:        None or int
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Local models.
        if model_type == 'mf' or model_type == 'local_tm':
            # Get the spin.
            spin = return_spin_from_index(model_info)

            # Spin deselection.
            if sim_index == None:
                spin.select = False

            # Simulation deselection.
            else:
                spin.select_sim[sim_index] = False

        # Global models.
        else:
            # Global model deselection.
            if sim_index == None:
                raise RelaxError("Cannot deselect the global model.")

            # Simulation deselection.
            else:
                # Deselect.
                cdp.select_sim[sim_index] = False


    def duplicate_data(self, pipe_from=None, pipe_to=None, model_info=None, global_stats=False, verbose=True):
        """Duplicate the data specific to a single model-free model.

        @keyword pipe_from:     The data pipe to copy the data from.
        @type pipe_from:        str
        @keyword pipe_to:       The data pipe to copy the data to.
        @type pipe_to:          str
        @param model_info:      The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @keyword global_stats:  The global statistics flag.
        @type global_stats:     bool
        @keyword verbose:       A flag which if True will cause info about each spin to be printed out as the sequence is generated.
        @type verbose:          bool
        """

        # Arg tests.
        if model_info == None:
            raise RelaxError("The model_info argument cannot be None.")

        # First create the pipe_to data pipe, if it doesn't exist, but don't switch to it.
        if not pipes.has_pipe(pipe_to):
            pipes.create(pipe_to, pipe_type='mf', switch=False)

        # Get the data pipes.
        dp_from = pipes.get_pipe(pipe_from)
        dp_to = pipes.get_pipe(pipe_to)

        # Duplicate all non-sequence specific data.
        for data_name in dir(dp_from):
            # Skip the container objects.
            if data_name in ['diff_tensor', 'mol', 'interatomic', 'structure', 'exp_info']:
                continue

            # Skip special objects.
            if search('^_', data_name) or data_name in list(dp_from.__class__.__dict__.keys()):
                continue

            # Get the original object.
            data_from = getattr(dp_from, data_name)

            # The data already exists.
            if hasattr(dp_to, data_name):
                # Get the object in the target pipe.
                data_to = getattr(dp_to, data_name)

                # The data must match!
                if data_from != data_to:
                    raise RelaxError("The object " + repr(data_name) + " is not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")

                # Skip the data.
                continue

            # Duplicate the data.
            setattr(dp_to, data_name, deepcopy(data_from))

        # Diffusion tensor comparison.
        if hasattr(dp_from, 'diff_tensor'):
            # Duplicate the tensor if it doesn't exist.
            if not hasattr(dp_to, 'diff_tensor'):
                setattr(dp_to, 'diff_tensor', deepcopy(dp_from.diff_tensor))

            # Otherwise compare the objects inside the container.
            else:
                # Loop over the modifiable objects.
                for data_name in dp_from.diff_tensor._mod_attr:
                    # Get the original object.
                    data_from = None
                    if hasattr(dp_from.diff_tensor, data_name):
                        data_from = getattr(dp_from.diff_tensor, data_name)

                    # Get the target object.
                    if data_from and not hasattr(dp_to.diff_tensor, data_name):
                        raise RelaxError("The diffusion tensor object " + repr(data_name) + " of the " + repr(pipe_from) + " data pipe is not located in the " + repr(pipe_to) + " data pipe.")
                    elif data_from:
                        data_to = getattr(dp_to.diff_tensor, data_name)
                    else:
                        continue

                    # The data must match!
                    if data_from != data_to:
                        raise RelaxError("The object " + repr(data_name) + " is not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")

        # Structure comparison.
        if hasattr(dp_from, 'structure'):
            # Duplicate the tensor if it doesn't exist.
            if not hasattr(dp_to, 'structure'):
                setattr(dp_to, 'structure', deepcopy(dp_from.structure))

            # Otherwise compare the objects inside the container.
            else:
                # Modifiable object checks.
                self._compare_objects(dp_from.structure, dp_to.structure, pipe_from, pipe_to)

                # Tests for the model and molecule containers.
                if len(dp_from.structure.structural_data) != len(dp_from.structure.structural_data):
                    raise RelaxError("The number of structural models is not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")

                # Loop over the models.
                for i in range(len(dp_from.structure.structural_data)):
                    # Alias.
                    model_from = dp_from.structure.structural_data[i]
                    model_to = dp_to.structure.structural_data[i]

                    # Model numbers.
                    if model_from.num != model_to.num:
                        raise RelaxError("The structure models are not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")

                    # Molecule number.
                    if len(model_from.mol) != len(model_to.mol):
                        raise RelaxError("The number of molecules is not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")

                    # Loop over the models.
                    for mol_index in range(len(model_from.mol)):
                        # Modifiable object checks.
                        self._compare_objects(model_from.mol[mol_index], model_to.mol[mol_index], pipe_from, pipe_to)

        # No sequence data, so skip the rest.
        if dp_from.mol.is_empty():
            return

        # Duplicate the sequence data if it doesn't exist.
        if dp_to.mol.is_empty():
            sequence.copy(pipe_from=pipe_from, pipe_to=pipe_to, preserve_select=True, verbose=verbose)

        # Duplicate the interatomic data if it doesn't exist.
        if dp_to.interatomic.is_empty():
            interatomic.copy(pipe_from=pipe_from, pipe_to=pipe_to, verbose=verbose)

        # Determine the model type of the original data pipe.
        pipes.switch(pipe_from)
        model_type = determine_model_type()

        # Sequence specific data.
        spin, spin_id = return_spin_from_index(model_info, pipe=pipe_from, return_spin_id=True)
        if model_type == 'mf' or (model_type == 'local_tm' and not global_stats):
            # Duplicate the spin specific data.
            for name in dir(spin):
                # Skip special objects.
                if search('^__', name):
                    continue

                # Get the object.
                obj = getattr(spin, name)

                # Skip methods.
                if isinstance(obj, MethodType):
                    continue

                # Duplicate the object.
                new_obj = deepcopy(getattr(spin, name))
                setattr(dp_to.mol[spin._mol_index].res[spin._res_index].spin[spin._spin_index], name, new_obj)

            # Duplicate the relaxation active spins which have not been copied yet.
            interatoms = interatomic.return_interatom_list(spin_id)
            for interatom in interatoms:
                # No relaxation mechanism.
                if not interatom.dipole_pair:
                    continue

                # The interacting spin.
                if spin_id != interatom.spin_id1:
                    spin_id2 = interatom.spin_id1
                else:
                    spin_id2 = interatom.spin_id2
                spin2 = return_spin(spin_id2)

                # Duplicate the spin specific data.
                mol_index, res_index, spin_index = return_spin_indices(spin_id2)
                dp_to.mol[mol_index].res[res_index].spin[spin_index] = deepcopy(spin2)

        # Other data types.
        else:
            # Duplicate all the spin specific data.
            dp_to.mol = deepcopy(dp_from.mol)


    def eliminate(self, name, value, model_info, args, sim=None):
        """Model-free model elimination, parameter by parameter.

        @param name:        The parameter name.
        @type name:         str
        @param value:       The parameter value.
        @type value:        float
        @param model_info:  The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:   int
        @param args:        The c1 and c2 elimination constant overrides.
        @type args:         None or tuple of float
        @keyword sim:       The Monte Carlo simulation index.
        @type sim:          int
        @return:            True if the model is to be eliminated, False otherwise.
        @rtype:             bool
        """

        # Default values.
        c1 = 50.0 * 1e-9
        c2 = 1.5

        # Depack the arguments.
        if args != None:
            c1, c2 = args

        # Determine the model type.
        model_type = determine_model_type()

        # Can't handle this one yet!
        if model_type != 'mf' and model_type != 'local_tm':
            raise RelaxError("Elimination of the global model is not yet supported.")

        # Get the spin and it's id string.
        spin, spin_id = return_spin_from_index(model_info, return_spin_id=True)

        # Get the tm value.
        if model_type == 'local_tm':
            tm = spin.local_tm
        else:
            tm = cdp.diff_tensor.tm

        # No tm value set, so skip the tests (no elimination).
        if tm == None:
            return False

        # Local tm.
        if name == 'local_tm' and value >= c1:
            if sim == None:
                print("Data pipe '%s':  The local tm parameter of %.5g is greater than %.5g, eliminating spin system '%s'." % (pipes.cdp_name(), value, c1, spin_id))
            else:
                print("Data pipe '%s':  The local tm parameter of %.5g is greater than %.5g, eliminating simulation %i of spin system '%s'." % (pipes.cdp_name(), value, c1, sim, spin_id))
            return True

        # Internal correlation times.
        if match('t[efs]', name) and value >= c2 * tm:
            if sim == None:
                print("Data pipe '%s':  The %s value of %.5g is greater than %.5g, eliminating spin system '%s'." % (pipes.cdp_name(), name, value, c2*tm, spin_id))
            else:
                print("Data pipe '%s':  The %s value of %.5g is greater than %.5g, eliminating simulation %i of spin system '%s'." % (pipes.cdp_name(), name, value, c2*tm, sim, spin_id))
            return True

        # Accept model.
        return False


    def get_param_names(self, model_info=None):
        """Return a vector of parameter names.

        @keyword model_info:    The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @return:                The vector of parameter names.
        @rtype:                 list of str
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Get the spin ids.
        if model_type == 'mf' or model_type == 'local_tm':
            # Get the spin and it's id string.
            spin, spin_id = return_spin_from_index(model_info, return_spin_id=True)
        else:
            spin_id = None

        # Assemble and return the parameter names.
        return assemble_param_names(model_type, spin_id=spin_id)


    def get_param_values(self, model_info=None, sim_index=None):
        """Return a vector of parameter values.

        @keyword model_info:    The model index from model_info().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @keyword sim_index:     The Monte Carlo simulation index.
        @type sim_index:        int
        @return:                The vector of parameter values.
        @rtype:                 list of str
        """

        # Test if the model-free models have been set up.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Not setup.
            if not spin.model:
                raise RelaxNoModelError

        # Determine the model type.
        model_type = determine_model_type()

        # Set the spin container (to None if the model is global).
        if model_type == 'mf' or model_type == 'local_tm':
            spin = return_spin_from_index(model_info)
        else:
            spin = None

        # Assemble the parameter values and return them.
        return assemble_param_vector(spin=spin, sim_index=sim_index, model_type=model_type)


    def is_spin_param(self, name):
        """Determine whether the given parameter is spin specific.

        Unless a diffusion parameter is encountered, this method will return true.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        If the parameter is a diffusion parameter, False I returned.  Otherwise True
                        is returned.
        @rtype:         bool
        """

        # Catch a diffusion parameter.
        if diffusion_tensor.return_data_name(name):
            return False

        # All the rest:
        else:
            return True


    def map_bounds(self, param, spin_id=None):
        """Create bounds for the OpenDX mapping function.

        @param param:       The name of the parameter to return the lower and upper bounds of.
        @type param:        str
        @param spin_id:     The spin identification string.
        @type spin_id:      str
        @return:            The upper and lower bounds of the parameter.
        @rtype:             list of float
        """

        # Get the spin.
        spin = return_spin(spin_id)

        # {s2, s2f, s2s}.
        if search('^s2', param):
            return [0.0, 1.0]

        # {local tm, te, tf, ts}.
        elif search('^t', param) or param == 'local_tm':
            return [0.0, 1e-8]

        # Rex.
        elif param == 'rex':
            return [0.0, 30.0 / (2.0 * pi * cdp.spectrometer_frq[cdp.ri_ids[0]])**2]

        # Interatomic distances.
        elif param == 'r':
            return [1.0 * 1e-10, 1.1 * 1e-10]

        # CSA.
        elif param == 'csa':
            return [-100 * 1e-6, -300 * 1e-6]


    def model_desc(self, model_info):
        """Return a description of the model.

        @param model_info:  The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:   int
        @return:            The model description.
        @rtype:             str
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Global models.
        if model_type == 'all':
            return "Global model - all diffusion tensor parameters and spin specific model-free parameters."
        elif model_type == 'diff':
            return "Diffusion tensor model."

        # Spin specific model.
        else:
            # Get the spin container.
            spin, spin_id = return_spin_from_index(model_info, return_spin_id=True)

            # Return the description.
            return "Model-free model of spin '%s'." % spin_id


    def model_loop(self):
        """Generator method for looping over the models (global or local).

        If the model type is 'all' or 'diff', then this yields the single value of zero.  Otherwise
        the global spin index is yielded.


        @return:    The model index.  This is zero for the global models or equal to the global spin
                    index (which covers the molecule, residue, and spin indices).
        @rtype:     int
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Global model.
        if model_type == 'all' or model_type == 'diff':
            yield 0

        # Spin specific models.
        else:
            # Loop over the spins.
            global_index = -1
            for spin in spin_loop():
                # Increment the global spin index.
                global_index = global_index + 1

                # Yield the spin index.
                yield global_index


    def model_statistics(self, model_info=None, spin_id=None, global_stats=None):
        """Return the k, n, and chi2 model statistics.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.


        @keyword model_info:    The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @keyword spin_id:       The spin identification string.  Either this or the instance keyword argument must be supplied.
        @type spin_id:          None or str
        @keyword global_stats:  A parameter which determines if global or local statistics are returned.  If None, then the appropriateness of global or local statistics is automatically determined.
        @type global_stats:     None or bool
        @return:                The optimisation statistics, in tuple format, of the number of parameters (k), the number of data points (n), and the chi-squared value (chi2).
        @rtype:                 tuple of (int, int, float)
        """

        # Bad argument combination.
        if model_info == None and spin_id == None:
            raise RelaxError("Either the model_info or spin_id argument must be supplied.")
        elif model_info != None and spin_id != None:
            raise RelaxError("The model_info arg " + repr(model_info) + " and spin_id arg " + repr(spin_id) + " clash.  Only one should be supplied.")

        # Determine the model type.
        model_type = determine_model_type()

        # Determine if local or global statistics will be returned.
        if global_stats == None:
            if model_type in ['mf', 'local_tm']:
                global_stats = False
            else:
                global_stats = True

        # Statistics for a single residue.
        if not global_stats:
            # Get the SpinContainer.
            if spin_id:
                spin = return_spin(spin_id)
            else:
                spin = return_spin_from_index(model_info)

            # Skip deselected residues.
            if not spin.select:
                return None, None, None

            # Missing data sets.
            if not hasattr(spin, 'ri_data'):
                return None, None, None

            # Count the number of parameters.
            param_vector = assemble_param_vector(spin=spin)
            k = len(param_vector)

            # Count the number of data points.
            n = len(spin.ri_data)

            # The chi2 value.
            chi2 = spin.chi2

        # Global stats.
        elif global_stats:
            # Count the number of parameters.
            param_vector = assemble_param_vector()
            k = len(param_vector)

            # Count the number of data points.
            n = 0
            chi2 = 0
            for spin in spin_loop():
                # Skip deselected residues.
                if not spin.select:
                    continue

                # Skip residues with no relaxation data.
                if not hasattr(spin, 'ri_data') or not len(spin.ri_data):
                    continue

                n = n + len(spin.ri_data)

                # Local tm models.
                if model_type == 'local_tm':
                    chi2 = chi2 + spin.chi2

            # The chi2 value.
            if model_type != 'local_tm':
                if not hasattr(cdp, 'chi2'):
                    raise RelaxError("Global statistics are not available, most likely because the global model has not been optimised.")
                chi2 = cdp.chi2

        # Return the data.
        return k, n, chi2


    def model_type(self):
        """Return the type of the model, either being 'local' or 'global'.

        @return:            The model type, one of 'local' or 'global'.
        @rtype:             str
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Global models.
        if model_type in ['all', 'diff']:
            return 'global'

        # Local models.
        else:
            return 'local'


    def num_instances(self):
        """Function for returning the number of instances.

        @return:    The number of instances used for optimisation.  Either the number of spins if
                    the local optimisations are setup ('mf' and 'local_tm'), or 1 for the global
                    models.
        @rtype:     int
        """

        # Test if sequence data exists.
        if not exists_mol_res_spin_data():
            return 0

        # Determine the model type.
        model_type = determine_model_type()

        # Sequence specific data.
        if model_type == 'mf' or model_type == 'local_tm':
            return count_spins()

        # Other data.
        elif model_type == 'diff' or model_type == 'all':
            return 1

        # Should not be here.
        else:
            raise RelaxFault


    def overfit_deselect(self, data_check=True, verbose=True):
        """Deselect spins which have insufficient data to support minimisation.

        @keyword data_check:    A flag to signal if the presence of base data is to be checked for.
        @type data_check:       bool
        @keyword verbose:       A flag which if True will allow printouts.
        @type verbose:          bool
        """

        # Print out.
        if verbose:
            print("\nOver-fit spin deselection:")

        # Test if sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Is structural data required?
        need_vect = False
        if hasattr(cdp, 'diff_tensor') and (cdp.diff_tensor.type == 'spheroid' or cdp.diff_tensor.type == 'ellipsoid'):
            need_vect = True

        # Loop over the sequence.
        deselect_flag = False
        spin_count = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # The interatomic data.
            interatoms = interatomic.return_interatom_list(spin_id)

            # Loop over the interatomic data.
            dipole_relax = False
            for i in range(len(interatoms)):
                # No dipolar relaxation mechanism.
                if not interatoms[i].dipole_pair:
                    continue

                # The surrounding spins.
                if spin_id != interatoms[i].spin_id1:
                    spin_id2 = interatoms[i].spin_id1
                else:
                    spin_id2 = interatoms[i].spin_id2
                spin2 = return_spin(spin_id2)

                # Dipolar relaxation flag.
                dipole_relax = True

            # No relaxation mechanism.
            if not dipole_relax or not hasattr(spin, 'csa') or spin.csa == None:
                warn(RelaxDeselectWarning(spin_id, 'an absence of relaxation mechanisms'))
                spin.select = False
                deselect_flag = True
                continue

            # Data checks.
            if data_check:
                # The number of relaxation data points (and for infinite data).
                data_points = 0
                inf_data = False
                if hasattr(cdp, 'ri_ids') and hasattr(spin, 'ri_data'):
                    for id in cdp.ri_ids:
                        if id in spin.ri_data and spin.ri_data[id] != None:
                            data_points += 1

                            # Infinite data!
                            if isInf(spin.ri_data[id]):
                                inf_data = True

                # Infinite data.
                if inf_data:
                    warn(RelaxDeselectWarning(spin_id, 'infinite relaxation data'))
                    spin.select = False
                    deselect_flag = True
                    continue

                # Relaxation data must exist!
                if not hasattr(spin, 'ri_data'):
                    warn(RelaxDeselectWarning(spin_id, 'missing relaxation data'))
                    spin.select = False
                    deselect_flag = True
                    continue

                # Require 3 or more relaxation data points.
                elif data_points < 3:
                    warn(RelaxDeselectWarning(spin_id, 'insufficient relaxation data, 3 or more data points are required'))
                    spin.select = False
                    deselect_flag = True
                    continue

                # Require at least as many data points as params to prevent over-fitting.
                elif hasattr(spin, 'params') and spin.params and len(spin.params) > data_points:
                    warn(RelaxDeselectWarning(spin_id, 'over-fitting - more parameters than data points'))
                    spin.select = False
                    deselect_flag = True
                    continue

            # Test for structural data if required.
            for i in range(len(interatoms)):
                # No dipolar relaxation mechanism.
                if not interatoms[i].dipole_pair:
                    continue

                # Check the unit vectors.
                if need_vect:
                    if not hasattr(interatoms[i], 'vector') or interatoms[i].vector == None:
                        warn(RelaxDeselectWarning(spin_id, 'missing structural data'))
                        spin.select = False
                        deselect_flag = True
                        continue

            # Increment the spin number.
            spin_count += 1

        # No spins selected, so fail hard to prevent the user from going any further.
        if spin_count == 0:
            warn(RelaxWarning("No spins are selected therefore the optimisation or calculation cannot proceed."))

        # Final printout.
        if verbose and not deselect_flag:
            print("No spins have been deselected.")


    def set_error(self, model_info, index, error):
        """Set the parameter errors.

        @param model_info:  The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:   int
        @param index:       The index of the parameter to set the errors for.
        @type index:        int
        @param error:       The error value.
        @type error:        float
        """

        # Parameter increment counter.
        inc = 0

        # Determine the model type.
        model_type = determine_model_type()

        # Get the parameter object names.
        param_names = self.data_names(set='params', scope='spin')


        # Diffusion tensor parameter errors.
        ####################################

        if model_type == 'diff' or model_type == 'all':
            # Spherical diffusion.
            if cdp.diff_tensor.type == 'sphere':
                # Return the parameter array.
                if index == 0:
                    cdp.diff_tensor.set(param='tm', value=error, category='err')

                # Increment.
                inc = inc + 1

            # Spheroidal diffusion.
            elif cdp.diff_tensor.type == 'spheroid':
                # Return the parameter array.
                if index == 0:
                    cdp.diff_tensor.set(param='tm', value=error, category='err')
                elif index == 1:
                    cdp.diff_tensor.set(param='Da', value=error, category='err')
                elif index == 2:
                    cdp.diff_tensor.set(param='theta', value=error, category='err')
                elif index == 3:
                    cdp.diff_tensor.set(param='phi', value=error, category='err')

                # Increment.
                inc = inc + 4

            # Ellipsoidal diffusion.
            elif cdp.diff_tensor.type == 'ellipsoid':
                # Return the parameter array.
                if index == 0:
                    cdp.diff_tensor.set(param='tm', value=error, category='err')
                elif index == 1:
                    cdp.diff_tensor.set(param='Da', value=error, category='err')
                elif index == 2:
                    cdp.diff_tensor.set(param='Dr', value=error, category='err')
                elif index == 3:
                    cdp.diff_tensor.set(param='alpha', value=error, category='err')
                elif index == 4:
                    cdp.diff_tensor.set(param='beta', value=error, category='err')
                elif index == 5:
                    cdp.diff_tensor.set(param='gamma', value=error, category='err')

                # Increment.
                inc = inc + 6


        # Model-free parameter errors for the model type 'all'.
        #######################################################

        if model_type == 'all':
            # Loop over the spins.
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Loop over the residue specific parameters.
                for param in param_names:
                    # Return the parameter array.
                    if index == inc:
                        setattr(spin, param + "_err", error)

                    # Increment.
                    inc = inc + 1


        # Model-free parameters for the model types 'mf' and 'local_tm'.
        ################################################################

        if model_type == 'mf' or model_type == 'local_tm':
            # Get the spin container.
            spin = return_spin_from_index(model_info)

            # Skip deselected residues.
            if not spin.select:
                return

            # Loop over the residue specific parameters.
            for param in param_names:
                # Return the parameter array.
                if index == inc:
                    setattr(spin, param + "_err", error)

                # Increment.
                inc = inc + 1


    def set_param_values(self, param=None, value=None, spin_id=None, error=False, force=True):
        """Set the model-free parameter values.

        @keyword param:     The parameter name list.
        @type param:        list of str
        @keyword value:     The parameter value list.
        @type value:        list
        @keyword spin_id:   The spin identification string, only used for spin specific parameters.
        @type spin_id:      None or str
        @keyword error:     A flag which if True will allow the parameter errors to be set instead of the values.
        @type error:        bool
        @keyword force:     A flag which if True will cause current values to be overwritten.  If False, a RelaxError will raised if the parameter value is already set.
        @type force:        bool
        """

        # Checks.
        lib.arg_check.is_str_list(param, 'parameter name')

        # Separate out the diffusion tensor parameters from the model-free parameters.
        diff_params = []
        diff_vals = []
        mf_params = []
        mf_vals = []
        for i in range(len(param)):
            # Diffusion tensor parameter.
            diff_obj = diffusion_tensor.return_data_name(param[i])
            if diff_obj:
                if error:
                    diff_params.append(param[i] + '_err')
                else:
                    diff_params.append(param[i])
                diff_vals.append(value[i])

            # Model-free parameter.
            else:
                mf_params.append(param[i])
                mf_vals.append(value[i])

        # Set the diffusion tensor parameters.
        if diff_params:
            diffusion_tensor.set(value=diff_vals, param=diff_params)

        # Set the model-free parameters.
        for i in range(len(mf_params)):
            # The object name.
            obj_name = self.return_data_name(mf_params[i])

            # Check if it is a model-free parameter.
            if obj_name not in self.data_names(set='params', scope='spin') and obj_name not in self.data_names(set='generic', scope='spin'):
                raise RelaxError("The parameter '%s' is unknown.  It should be one of %s or %s" % (mf_params[i], self.data_names(set='params', scope='spin'), self.data_names(set='generic', scope='spin')))

            # The error object name.
            if error:
                obj_name += '_err'

            # Set the parameter.
            for spin in spin_loop(spin_id):
                setattr(spin, obj_name, mf_vals[i])


    def set_selected_sim(self, model_info, select_sim):
        """Set all simulation selection flags.

        @param model_info:  The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:   int
        @param select_sim:  The selection flags.
        @type select_sim:   bool
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Global model.
        if model_type == 'all' or model_type == 'diff':
            cdp.select_sim = select_sim

        # Spin specific model.
        else:
            # Get the spin container.
            spin = return_spin_from_index(model_info)

            # Skip if deselected.
            if not spin.select:
                return

            # Set the simulation flags.
            spin.select_sim = deepcopy(select_sim)


    def set_update(self, param, spin):
        """Function to update the other model-free parameters.

        @param param:   The name of the parameter which has been changed.
        @type param:    str
        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        """

        # S2f parameter.
        if param == 's2f':
            # Update S2 if S2s exists.
            if hasattr(spin, 's2s') and spin.s2s != None:
                spin.s2 = spin.s2f * spin.s2s


        # S2s parameter.
        if param == 's2s':
            # Update S2 if S2f exists.
            if hasattr(spin, 's2f') and spin.s2f != None:
                spin.s2 = spin.s2f * spin.s2s


    def sim_init_values(self):
        """Initialise the Monte Carlo parameter values."""

        # Determine the model type.
        model_type = determine_model_type()

        # Get the parameter object names.
        param_names = self.data_names(set='params', scope='spin')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min', scope='spin')

        # List of diffusion tensor parameters.
        if model_type == 'diff' or model_type == 'all':
            # Spherical diffusion.
            if cdp.diff_tensor.type == 'sphere':
                diff_params = ['tm']

            # Spheroidal diffusion.
            elif cdp.diff_tensor.type == 'spheroid':
                diff_params = ['tm', 'Da', 'theta', 'phi']

            # Ellipsoidal diffusion.
            elif cdp.diff_tensor.type == 'ellipsoid':
                diff_params = ['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma']


        # Test if Monte Carlo parameter values have already been set.
        #############################################################

        # Diffusion tensor parameters and non spin specific minimisation statistics.
        if model_type == 'diff' or model_type == 'all':
            # Loop over the parameters.
            for object_name in diff_params:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(cdp.diff_tensor, sim_object_name):
                    raise RelaxError("Monte Carlo parameter values have already been set.")

            # Loop over the minimisation stats objects.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(cdp, sim_object_name):
                    raise RelaxError("Monte Carlo parameter values have already been set.")

        # Spin specific parameters.
        if model_type != 'diff':
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

        # Loop over the global minimisation stats objects.
        for object_name in min_names:
            # Skip non-existent objects.
            if not hasattr(cdp, object_name):
                continue

            # Name for the simulation object.
            sim_object_name = object_name + '_sim'

            # Create the simulation object.
            setattr(cdp, sim_object_name, [])

            # Get the simulation object.
            sim_object = getattr(cdp, sim_object_name)

            # Loop over the simulations.
            for j in range(cdp.sim_number):
                # Get the object.
                object = getattr(cdp, object_name)

                # Copy and append the data.
                sim_object.append(deepcopy(object))

        # Diffusion tensor parameters and non spin specific minimisation statistics.
        if model_type == 'diff' or model_type == 'all':
            # Set up the number of simulations.
            cdp.diff_tensor.set_sim_num(cdp.sim_number)

            # Loop over the parameters, setting the initial simulation values to those of the parameter value.
            for object_name in diff_params:
                for j in range(cdp.sim_number):
                    cdp.diff_tensor.set(param=object_name, value=deepcopy(getattr(cdp.diff_tensor, object_name)), category='sim', sim_index=j)

        # Spin specific parameters.
        if model_type != 'diff':
            for spin in spin_loop():
                # Skip deselected spins.
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


    def sim_return_chi2(self, model_info, index=None):
        """Return the simulation chi-squared values.

        @param model_info:  The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:   int
        @keyword index:     The optional simulation index.
        @type index:        int
        @return:            The list of simulation chi-squared values.  If the index is supplied, only a single value will be returned.
        @rtype:             list of float or float
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Single instance.
        if model_type == 'all' or model_type == 'diff':
            return cdp.chi2_sim

        # Multiple instances.
        else:
            # Get the spin container.
            spin = return_spin_from_index(model_info)

            # Return the list.
            return spin.chi2_sim


    def sim_return_param(self, model_info, index):
        """Return the array of simulation parameter values.

        @param model_info:  The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:   int
        @param index:       The index of the parameter to return the array of values for.
        @type index:        int
        @return:            The array of simulation parameter values.
        @rtype:             list of float
        """

        # Parameter increment counter.
        inc = 0

        # Determine the model type.
        model_type = determine_model_type()

        # Get the parameter object names.
        param_names = self.data_names(set='params', scope='spin')


        # Diffusion tensor parameters.
        ##############################

        if model_type == 'diff' or model_type == 'all':
            # Spherical diffusion.
            if cdp.diff_tensor.type == 'sphere':
                # Return the parameter array.
                if index == 0:
                    return cdp.diff_tensor.tm_sim

                # Increment.
                inc = inc + 1

            # Spheroidal diffusion.
            elif cdp.diff_tensor.type == 'spheroid':
                # Return the parameter array.
                if index == 0:
                    return cdp.diff_tensor.tm_sim
                elif index == 1:
                    return cdp.diff_tensor.Da_sim
                elif index == 2:
                    return cdp.diff_tensor.theta_sim
                elif index == 3:
                    return cdp.diff_tensor.phi_sim

                # Increment.
                inc = inc + 4

            # Ellipsoidal diffusion.
            elif cdp.diff_tensor.type == 'ellipsoid':
                # Return the parameter array.
                if index == 0:
                    return cdp.diff_tensor.tm_sim
                elif index == 1:
                    return cdp.diff_tensor.Da_sim
                elif index == 2:
                    return cdp.diff_tensor.Dr_sim
                elif index == 3:
                    return cdp.diff_tensor.alpha_sim
                elif index == 4:
                    return cdp.diff_tensor.beta_sim
                elif index == 5:
                    return cdp.diff_tensor.gamma_sim

                # Increment.
                inc = inc + 6


        # Model-free parameters for the model type 'all'.
        #################################################

        if model_type == 'all':
            # Loop over the spins.
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Loop over the spin specific parameters.
                for param in param_names:
                    # Return the parameter array.
                    if index == inc:
                        return getattr(spin, param + "_sim")

                    # Increment.
                    inc = inc + 1


        # Model-free parameters for the model types 'mf' and 'local_tm'.
        ################################################################

        if model_type == 'mf' or model_type == 'local_tm':
            # Get the spin container.
            spin = return_spin_from_index(model_info)

            # Skip deselected spins.
            if not spin.select:
                return

            # Loop over the spin specific parameters.
            for param in param_names:
                # Return the parameter array.
                if index == inc:
                    return getattr(spin, param + "_sim")

                # Increment.
                inc = inc + 1


    def sim_return_selected(self, model_info):
        """Return the array of selected simulation flags for the spin.

        @param model_info:  The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:   int
        @return:            The array of selected simulation flags.
        @rtype:             list of int
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Single instance.
        if model_type == 'all' or model_type == 'diff':
            return cdp.select_sim

        # Multiple instances.
        else:
            # Get the spin container.
            spin = return_spin_from_index(model_info)

            # Skip if deselected.
            if not spin.select:
                return

            # Return the list.
            return spin.select_sim


    def skip_function(self, model_info):
        """Skip certain data.

        @param model_info:      The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @return:                True if the data should be skipped, False otherwise.
        @rtype:                 bool
        """

        # Determine the model type.
        model_type = determine_model_type()

        # Sequence specific data.
        if (model_type == 'mf' or model_type == 'local_tm') and not return_spin_from_index(model_info).select:
            return True

        # Don't skip.
        return False
