###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2013-2014 Troels E. Linnet                                    #
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
"""The relaxation dispersion API object."""

# Python module imports.
from copy import deepcopy
from re import match, search
import sys
from types import MethodType

# relax module imports.
from lib.arg_check import is_list, is_str_list
from lib.errors import RelaxError, RelaxImplementError
from lib.text.sectioning import subsection
from multi import Processor_box
from pipe_control import pipes, sequence
from pipe_control.mol_res_spin import check_mol_res_spin_data, return_spin, spin_loop
from pipe_control.sequence import return_attached_protons
from specific_analyses.api_base import API_base
from specific_analyses.api_common import API_common
from specific_analyses.relax_disp.checks import check_model_type
from specific_analyses.relax_disp.data import average_intensity, calc_rotating_frame_params, find_intensity_keys, generate_r20_key, has_exponential_exp_type, has_proton_mmq_cpmg, loop_cluster, loop_exp_frq, loop_exp_frq_offset_point, loop_time, pack_back_calc_r2eff, return_param_key_from_data, spin_ids_to_containers
from specific_analyses.relax_disp.optimisation import Disp_memo, Disp_minimise_command, back_calc_peak_intensities, back_calc_r2eff, calculate_r2eff, minimise_r2eff
from specific_analyses.relax_disp.parameter_object import Relax_disp_params
from specific_analyses.relax_disp.parameters import get_param_names, get_value, loop_parameters, param_index_to_param_info, param_num
from specific_analyses.relax_disp.variables import EXP_TYPE_CPMG_PROTON_MQ, EXP_TYPE_CPMG_PROTON_SQ, MODEL_LIST_MMQ, MODEL_R2EFF, PARAMS_R20


class Relax_disp(API_base, API_common):
    """Class containing functions for relaxation dispersion curve fitting."""

    # Class variable for storing the class instance (for the singleton design pattern).
    instance = None

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Place methods into the API.
        self.data_init = self._data_init_spin
        self.model_type = self._model_type_local
        self.return_conversion_factor = self._return_no_conversion_factor
        self.return_value = self.return_value

        # Place a copy of the parameter list object in the instance namespace.
        self._PARAMS = Relax_disp_params()


    def base_data_loop(self):
        """Custom generator method for looping over the base data.

        For the R2eff model, the base data is the peak intensity data defining a single exponential curve.  For all other models, the base data is the R2eff/R1rho values for individual spins.


        @return:    For the R2eff model, a tuple of the spin container and the exponential curve identifying key (the CPMG frequency or R1rho spin-lock field strength).  For all other models, the spin container and ID from the spin loop.
        @rtype:     (tuple of SpinContainer instance and float) or (SpinContainer instance and str)
        """

        # The R2eff model data (the base data is peak intensities).
        if cdp.model_type == MODEL_R2EFF:
            # Loop over the sequence.
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins with no peak intensity data.
                if not hasattr(spin, 'peak_intensity'):
                    continue

                # Loop over each spectrometer frequency and dispersion point.
                for exp_type, frq, offset, point in loop_exp_frq_offset_point():
                    yield spin, exp_type, frq, offset, point

        # All other models (the base data is the R2eff/R1rho values).
        else:
            # 1H MMQ flag.
            proton_mmq_flag = has_proton_mmq_cpmg()

            # Loop over the sequence.
            for spin, spin_id in spin_loop(return_id=True):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip protons for MMQ data.
                if spin.model in MODEL_LIST_MMQ and spin.isotope == '1H':
                    continue

                # Get the attached proton.
                proton = None
                if proton_mmq_flag:
                    proton = return_attached_protons(spin_id)[0]

                # Skip spins with no R2eff/R1rho values.
                if not hasattr(spin, 'r2eff') and not hasattr(proton, 'r2eff'):
                    continue

                # Yield the spin container and ID.
                yield spin, spin_id


    def calculate(self, spin_id=None, scaling_matrix=None, verbosity=1, sim_index=None):
        """Calculate the model chi-squared value or the R2eff values for fixed time period data.

        @keyword spin_id:           The spin identification string.
        @type spin_id:              None or str
        @keyword scaling_matrix:    The per-model list of diagonal and square scaling matrices.
        @type scaling_matrix:       list of numpy rank-2, float64 array or list of None
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The MC simulation index (unused).
        @type sim_index:            None
        """

        # Data checks.
        pipes.test()
        check_mol_res_spin_data()
        check_model_type()

        # Special exponential curve-fitting for the R2eff model.
        if cdp.model_type == MODEL_R2EFF:
            calculate_r2eff()

        # Calculate the chi-squared value.
        else:
            # 1H MMQ flag.
            proton_mmq_flag = has_proton_mmq_cpmg()

            # Loop over all spins.
            for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
                # Skip protons for MMQ data.
                if spin.model in MODEL_LIST_MMQ and spin.isotope == '1H':
                    continue

                # Get the attached proton.
                proton = None
                if proton_mmq_flag:
                    proton = return_attached_protons(spin_id)[0]

                # The back calculated values.
                back_calc = back_calc_r2eff(spin=spin, spin_id=spin_id, store_chi2=True)

                # Pack the data.
                pack_back_calc_r2eff(spin=spin, spin_id=spin_id, si=0, back_calc=back_calc, proton_mmq_flag=proton_mmq_flag)


    def constraint_algorithm(self):
        """Return the 'Log barrier' optimisation constraint algorithm.

        @return:    The 'Log barrier' constraint algorithm.
        @rtype:     str
        """

        # The log barrier algorithm, as required by minfx.
        return 'Log barrier'


    def create_mc_data(self, data_id):
        """Create the Monte Carlo peak intensity data.

        @param data_id: The tuple of the spin container and the exponential curve identifying key, as yielded by the base_data_loop() generator method.
        @type data_id:  SpinContainer instance and float
        @return:        The Monte Carlo simulation data.
        @rtype:         list of floats
        """

        # The R2eff model (with peak intensity base data).
        if cdp.model_type == MODEL_R2EFF:
            # Unpack the data.
            spin, exp_type, frq, offset, point = data_id

            # Back calculate the peak intensities.
            values = back_calc_peak_intensities(spin=spin, exp_type=exp_type, frq=frq, offset=offset, point=point)

        # All other models (with R2eff/R1rho base data).
        else:
            # 1H MMQ flag.
            proton_mmq_flag = has_proton_mmq_cpmg()

            # Unpack the data.
            spin, spin_id = data_id

            # Back calculate the R2eff/R1rho data.
            back_calc = back_calc_r2eff(spin=spin, spin_id=spin_id)

            # Get the attached proton data.
            if proton_mmq_flag:
                proton = return_attached_protons(spin_id)[0]
                proton_back_calc = back_calc_r2eff(spin=proton, spin_id=spin_id)

            # Convert to a dictionary matching the R2eff data structure.
            values = {}
            for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
                # Alias the correct data.
                current_bc = back_calc
                current_spin = spin
                if exp_type in [EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_PROTON_MQ]:
                    current_spin = proton
                    current_bc = proton_back_calc

                # The parameter key.
                param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

                # Skip missing data.
                if not hasattr(current_spin, 'r2eff') or param_key not in current_spin.r2eff.keys():
                    continue

                # Store the result.
                values[param_key] = back_calc[ei][0][mi][oi][di]

        # Return the MC data.
        return values


    def deselect(self, sim_index=None, model_info=None):
        """Deselect models or simulations.

        @keyword sim_index:     The optional Monte Carlo simulation index.  If None, then models will be deselected, otherwise the given simulation will.
        @type sim_index:        None or int
        @keyword model_info:    The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:       list of SpinContainer instances, list of str
        """

        # Loop over all the spins and deselect them.
        for spin_id in model_info:
            # Get the spin.
            spin = return_spin(spin_id)

            # Spin deselection.
            if sim_index == None:
                spin.select = False

            # Simulation deselection.
            else:
                spin.select_sim[sim_index] = False


    def duplicate_data(self, pipe_from=None, pipe_to=None, model_info=None, global_stats=False, verbose=True):
        """Duplicate the data specific to a single model.

        @keyword pipe_from:     The data pipe to copy the data from.
        @type pipe_from:        str
        @keyword pipe_to:       The data pipe to copy the data to.
        @type pipe_to:          str
        @keyword model_info:    The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:       list of SpinContainer instances, list of str
        @keyword global_stats:  The global statistics flag.
        @type global_stats:     bool
        @keyword verbose:       A flag which if True will cause info to be printed out.
        @type verbose:          bool
        """

        # First create the pipe_to data pipe, if it doesn't exist, but don't switch to it.
        if not pipes.has_pipe(pipe_to):
            pipes.create(pipe_to, pipe_type='relax_disp', switch=False)

        # Get the data pipes.
        dp_from = pipes.get_pipe(pipe_from)
        dp_to = pipes.get_pipe(pipe_to)

        # Duplicate all non-sequence specific data.
        for data_name in dir(dp_from):
            # Skip the container objects.
            if data_name in ['mol', 'interatomic', 'structure', 'exp_info', 'result_files']:
                continue

            # Skip dispersion specific parameters.
            if data_name in ['model']:
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

        # No sequence data, so skip the rest.
        if dp_from.mol.is_empty():
            return

        # Duplicate the sequence data if it doesn't exist.
        if dp_to.mol.is_empty():
            sequence.copy(pipe_from=pipe_from, pipe_to=pipe_to, preserve_select=True, verbose=verbose)

        # Loop over the cluster.
        for id in model_info:
            # The original spin container.
            spin = return_spin(id, pipe=pipe_from)

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


    def eliminate(self, name, value, args, sim=None, model_info=None):
        """Relaxation dispersion model elimination, parameter by parameter.

        @param name:            The parameter name.
        @type name:             str
        @param value:           The parameter value.
        @type value:            float
        @param args:            The c1 and c2 elimination constant overrides.
        @type args:             None or tuple of float
        @keyword sim:           The Monte Carlo simulation index.
        @type sim:              int
        @keyword model_info:    The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:       list of SpinContainer instances, list of str
        @return:                True if the model is to be eliminated, False otherwise.
        @rtype:                 bool
        """

        # Skip the R2eff model parameters.
        if name in ['r2eff', 'i0']:
            return False

        # Default limits.
        c1 = 0.501
        c2 = 0.999
        c3 = 1.0

        # Depack the arguments.
        if args != None:
            c1, c2, c3 = args

        # Elimination text.
        elim_text = "Data pipe '%s':  The %s parameter of %.5f is %s, eliminating " % (pipes.cdp_name(), name, value, "%s")
        if sim == None:
            elim_text += "the spin cluster %s." % model_info
        else:
            elim_text += "simulation %i of the spin cluster %s." % (sim, model_info)

        # The pA parameter.
        if name == 'pA':
            if value < c1:
                print(elim_text % ("less than  %.5f" % c1))
                return True
            if value > c2:
                print(elim_text % ("greater than  %.5f" % c2))
                return True

        # The tex parameter.
        if name == 'tex':
            if value > c3:
                print(elim_text % ("greater than  %.5f" % c3))
                return True

        # Accept model.
        return False


    def get_param_names(self, model_info=None):
        """Return a vector of parameter names.

        @keyword model_info:    The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:       list of SpinContainer instances, list of str
        @return:                The vector of parameter names.
        @rtype:                 list of str
        """

        # Get the spin containers.
        spins = []
        for spin_id in model_info:
            # Get the spin.
            spin = return_spin(spin_id)

            # Skip deselected spins.
            if not spin.select:
                continue

            # Add the spin.
            spins.append(spin)

        # No spins.
        if not len(spins):
            return None

        # Call the get_param_names() function.
        return get_param_names(spins)


    def get_param_values(self, model_info=None, sim_index=None):
        """Return a vector of parameter values.

        @keyword model_info:    The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:       list of SpinContainer instances, list of str
        @keyword sim_index:     The Monte Carlo simulation index.
        @type sim_index:        int
        @return:                The vector of parameter values.
        @rtype:                 list of str
        """

        # Get the spin containers.
        spins = []
        for spin_id in model_info:
            # Get the spin.
            spin = return_spin(spin_id)

            # Skip deselected spins.
            if not spin.select:
                continue

            # Add the spin.
            spins.append(spin)

        # No spins.
        if not len(spins):
            return None

        # Loop over the parameters of the cluster, fetching their values.
        values = []
        for param_name, param_index, si, r20_key in loop_parameters(spins=spins):
            values.append(get_value(spins=spins, sim_index=sim_index, param_name=param_name, spin_index=si, r20_key=r20_key))

        # Return all values.
        return values


    def grid_search(self, lower=None, upper=None, inc=None, scaling_matrix=None, constraints=True, verbosity=1, sim_index=None):
        """The relaxation dispersion curve fitting grid search function.

        @keyword lower:             The per-model lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:                list of list of numbers
        @keyword upper:             The per-model upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:                list of list of numbers
        @keyword inc:               The per-model increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.
        @type inc:                  list of list of int
        @keyword scaling_matrix:    The per-model list of diagonal and square scaling matrices.
        @type scaling_matrix:       list of numpy rank-2, float64 array or list of None
        @keyword constraints:       If True, constraints are applied during the grid search (eliminating parts of the grid).  If False, no constraints are used.
        @type constraints:          bool
        @keyword verbosity:         A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to apply the grid search to.  If None, the normal model is optimised.
        @type sim_index:            int
        """

        # Minimisation.
        self.minimise(min_algor='grid', lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def map_bounds(self, param, spin_id=None):
        """Create bounds for the OpenDX mapping function.

        @param param:       The name of the parameter to return the lower and upper bounds of.
        @type param:        str
        @param spin_id:     The spin identification string (unused).
        @type spin_id:      None
        @return:            The upper and lower bounds of the parameter.
        @rtype:             list of float
        """

        # Is the parameter is valid?
        if not self._PARAMS.contains(param):
            raise RelaxError("The parameter '%s' is not valid for this data pipe type." % param)

        # Return the spin.
        spin = return_spin(spin_id)

        # Loop over each spectrometer frequency and dispersion point to collect param_keys.
        param_keys = []
        for exp_type, frq, offset, point in loop_exp_frq_offset_point():
            # The parameter key.
            param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

            # Collect the key.
            param_keys.append(param_key)

        # The initial parameter vector.
        param_vector = []

        # Collect param_names.
        param_names = []
        for param_name, param_index, si, r20_key in loop_parameters(spins=[spin]):
            # Add to the param vector.
            param_vector.append([0.0])

            # Collect parameter names.
            param_names.append(param_name)

        # Loop over the parameter names.
        for i in range(len(param_names)):
            # Test if the parameter is in the list:

            if param_names[i] == param:
                return [self._PARAMS.grid_lower(param, incs=0, model_info=[spin_id]), self._PARAMS.grid_upper(param, incs=0, model_info=[spin_id])]


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling_matrix=None, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Relaxation dispersion curve fitting function.

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
        @keyword scaling_matrix:    The per-model list of diagonal and square scaling matrices.
        @type scaling_matrix:       list of numpy rank-2, float64 array or list of None
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:            None or int
        @keyword lower:             The per-model lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:                list of list of numbers
        @keyword upper:             The per-model upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:                list of list of numbers
        @keyword inc:               The per-model increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  list of list of int
        """

        # Data checks.
        check_mol_res_spin_data()
        check_model_type()

        # Check the optimisation algorithm.
        algor = min_algor
        if min_algor == 'Log barrier':
            algor = min_options[0]

        allow = False
        # Check the model type.
        if hasattr(cdp, 'model_type'):
            # Set the model type:
            model_type = cdp.model_type

            if model_type == MODEL_R2EFF:
                if match('^[Gg]rid$', algor):
                    allow = True

                elif match('^[Ss]implex$', algor):
                    allow = True

                # Quasi-Newton BFGS minimisation.
                elif match('^[Bb][Ff][Gg][Ss]$', algor):
                    allow = True

                # Newton minimisation.
                elif match('^[Nn]ewton$', algor):
                    allow = True

                # Newton minimisation.
                elif match('^[Nn]ewton$', algor):
                    allow = True

                # Constrained method, Method of Multipliers.
                elif match('^[Mm][Oo][Mm]$', algor) or match('[Mm]ethod of [Mm]ultipliers$', algor):
                    allow = True
                    
                # Constrained method, Logarithmic barrier function.
                elif match('^[Ll]og [Bb]arrier$', algor):
                    allow = True

            # If the Jacobian and Hessian matrix have not been specified for fitting, 'simplex' should be used.
            else:
                if match('^[Gg]rid$', algor):
                    allow = True

                elif match('^[Ss]implex$', algor):
                    allow = True

        # Do not allow, if no model has been specified.
        else:
            model_type = 'None'
            # Do not allow.
            allow = False

        if not allow:
            raise RelaxError("Minimisation algorithm '%s' is not allowed, since function gradients for model '%s' is not implemented.  Only the 'simplex' minimisation algorithm is supported for the relaxation dispersion analysis of this model."%(algor, model_type))

        # Initialise some empty data pipe structures so that the target function set up does not fail.
        if not hasattr(cdp, 'cpmg_frqs_list'):
            cdp.cpmg_frqs_list = []
        if not hasattr(cdp, 'spin_lock_nu1_list'):
            cdp.spin_lock_nu1_list = []

        # Get the Processor box singleton (it contains the Processor instance) and alias the Processor.
        processor_box = Processor_box() 
        processor = processor_box.processor

        # The number of time points for the exponential curves (if present).
        num_time_pts = 1
        if hasattr(cdp, 'num_time_pts'):
            num_time_pts = cdp.num_time_pts

        # Number of spectrometer fields.
        fields = [None]
        field_count = 1
        if hasattr(cdp, 'spectrometer_frq'):
            fields = cdp.spectrometer_frq_list
            field_count = cdp.spectrometer_frq_count

        # Loop over the spin blocks.
        model_index = -1
        for spin_ids in self.model_loop():
            # Increment the model index.
            model_index += 1

            # The spin containers.
            spins = spin_ids_to_containers(spin_ids)

            # Skip deselected clusters.
            skip = True
            for spin in spins:
                if spin.select:
                    skip = False
            if skip:
                continue

            # Alias the grid options.
            lower_i, upper_i, inc_i = None, None, None
            if min_algor == 'grid':
                lower_i = lower[model_index]
                upper_i = upper[model_index]
                inc_i = inc[model_index]

            # Special exponential curve-fitting for the R2eff model.
            if cdp.model_type == MODEL_R2EFF:
                # Sanity checks.
                if not has_exponential_exp_type():
                    raise RelaxError("The R2eff model with the fixed time period dispersion experiments cannot be optimised.")

                # Optimisation.
                minimise_r2eff(spins=spins, spin_ids=spin_ids, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling_matrix=scaling_matrix[model_index], verbosity=verbosity, sim_index=sim_index, lower=lower_i, upper=upper_i, inc=inc_i)

                # Skip the rest.
                continue

            # Set up the slave command object.
            command = Disp_minimise_command(spins=spins, spin_ids=spin_ids, sim_index=sim_index, scaling_matrix=scaling_matrix[model_index], min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, verbosity=verbosity, lower=lower_i, upper=upper_i, inc=inc_i, fields=fields, param_names=get_param_names(spins=spins, full=True))

            # Set up the memo.
            memo = Disp_memo(spins=spins, spin_ids=spin_ids, sim_index=sim_index, scaling_matrix=scaling_matrix[model_index], verbosity=verbosity)

            # Add the slave command and memo to the processor queue.
            processor.add_to_queue(command, memo)


    def model_desc(self, model_info=None):
        """Return a description of the model.

        @keyword model_info:    The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:       list of SpinContainer instances, list of str
        @return:                The model description.
        @rtype:                 str
        """

        # The model loop is over the spin clusters, so return a description of the cluster.
        return "The spin cluster %s." % model_info


    def model_loop(self):
        """Loop over the spin groupings for one model applied to multiple spins.

        @return:    The list of spins per block will be yielded, as well as the list of spin IDs.
        @rtype:     tuple of list of SpinContainer instances and list of str
        """

        # Loop over individual spins for the R2eff model.
        if cdp.model_type == MODEL_R2EFF:
            # The spin loop.
            for spin, spin_id in spin_loop(return_id=True):
                # Skip deselected spins
                if not spin.select:
                    continue

                # Yield the spin ID as a list.
                yield [spin_id]

         # The cluster loop.
        else:
            for spin_ids in loop_cluster(skip_desel=False):
                yield spin_ids


    def model_statistics(self, model_info=None, spin_id=None, global_stats=None):
        """Return the k, n, and chi2 model statistics.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.


        @keyword model_info:    The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:       list of SpinContainer instances, list of str
        @keyword spin_id:       The spin ID string to override the model_info argument.  This is ignored in the N-state model.
        @type spin_id:          None or str
        @keyword global_stats:  A parameter which determines if global or local statistics are returned.  For the N-state model, this argument is ignored.
        @type global_stats:     None or bool
        @return:                The optimisation statistics, in tuple format, of the number of parameters (k), the number of data points (n), and the chi-squared value (chi2).
        @rtype:                 tuple of (int, int, float)
        """

        # Get the spin containers (the spin ID overrides the model info).
        if spin_id != None:
            spins = [return_spin(spin_id)]
        else:
            spins = spin_ids_to_containers(model_info)

        # The number of parameters for the cluster.
        k = param_num(spins=spins)

        # The number of points from all spins.
        n = 0
        for spin in spins:
            # Skip deselected spins.
            if not spin.select:
                continue

            n += len(spin.r2eff)

        # Take the chi-squared from the first spin of the cluster (which has a value).
        chi2 = None
        for spin in spins:
            # Skip deselected spins.
            if not spin.select:
                continue

            if hasattr(spin, 'chi2'):
                chi2 = spin.chi2
                break

        # Return the values.
        return k, n, chi2


    def overfit_deselect(self, data_check=True, verbose=True):
        """Deselect spins which have insufficient data to support minimisation.

        @keyword data_check:    A flag to signal if the presence of base data is to be checked for.
        @type data_check:       bool
        @keyword verbose:       A flag which if True will allow printouts.
        @type verbose:          bool
        """

        # Test the sequence data exists and the model is setup.
        check_mol_res_spin_data()
        check_model_type()

        # 1H MMQ flag.
        proton_mmq_flag = has_proton_mmq_cpmg()

        # Loop over spin data.
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            # Skip protons for MMQ data.
            if spin.model in MODEL_LIST_MMQ and spin.isotope == '1H':
                continue

            # Get the attached proton.
            proton = None
            if proton_mmq_flag:
                # Get all protons.
                proton_spins = return_attached_protons(spin_id)

                # Only one allowed.
                if len(proton_spins) > 1:
                    print("Multiple protons attached to the spin '%s', but one one attached proton is supported for the MMQ-type models." % spin_id)
                    spin.select = False
                    continue

                # Alias the single proton.
                if len(proton_spins):
                    proton = proton_spins[0]

            # Check if data exists.
            if not hasattr(spin, 'r2eff') and not hasattr(proton, 'r2eff'):
                print("No R2eff data could be found, deselecting the '%s' spin." % spin_id)
                spin.select = False
                continue


    def print_model_title(self, prefix=None, model_info=None):
        """Print out the model title.

        @keyword prefix:        The starting text of the title.  This should be printed out first, followed by the model information text.
        @type prefix:           str
        @keyword model_info:    The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:       list of SpinContainer instances, list of str
        """

        # The printout.
        subsection(file=sys.stdout, text=prefix+"the spin block %s"%model_info, prespace=2)


    def return_data(self, data_id=None):
        """Return the peak intensity data structure.

        @param data_id: The spin ID string, as yielded by the base_data_loop() generator method.
        @type data_id:  str
        @return:        The peak intensity data structure.
        @rtype:         list of float
        """

        # The R2eff model.
        if cdp.model_type == MODEL_R2EFF:
            # Unpack the data.
            spin, exp_type, frq, offset, point = data_id

            # Return the data.
            return spin.peak_intensity

        # All other models.
        else:
            raise RelaxImplementError


    def return_error(self, data_id=None):
        """Return the standard deviation data structure.

        @param data_id: The tuple of the spin container and the exponential curve identifying key, as yielded by the base_data_loop() generator method.
        @type data_id:  SpinContainer instance and float
        @return:        The standard deviation data structure.
        @rtype:         list of float
        """

        # The R2eff model.
        if cdp.model_type == MODEL_R2EFF:
            # Unpack the data.
            spin, exp_type, frq, offset, point = data_id

            # Generate the data structure to return.
            errors = []
            for time in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point):
                errors.append(average_intensity(spin=spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time, error=True))

        # All other models.
        else:
            # Unpack the data.
            spin, spin_id = data_id

            # 1H MMQ flag.
            proton_mmq_flag = has_proton_mmq_cpmg()

            # Get the attached proton.
            proton = None
            if proton_mmq_flag:
                proton = return_attached_protons(spin_id)[0]

            # The errors.
            r2eff_err = {}
            if hasattr(spin, 'r2eff_err'):
                r2eff_err.update(spin.r2eff_err)
            if hasattr(proton, 'r2eff_err'):
                r2eff_err.update(proton.r2eff_err)
            return r2eff_err

        # Return the error list.
        return errors


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

        # Define list of special parameters.
        special_parameters = ['theta', 'w_eff']

        # Use api_common function for paramets not defined in special_parameters.
        if param not in special_parameters:
            returnval = self._return_value_general(spin=spin, param=param, sim=sim, bc=bc)
            return returnval

        # If parameter in special_parameters, the do the following.

        # Initial values.
        value = None
        error = None

        # Return the data
        theta_spin_dic, Domega_spin_dic, w_eff_spin_dic, dic_key_list = calc_rotating_frame_params(spin=spin)

        # Return for parameter theta
        if param == "theta":
            value = theta_spin_dic

        # Return for parameter theta
        elif param == "w_eff":
            value = w_eff_spin_dic

        # Return the data.
        return value, error


    def set_error(self, index, error, model_info=None):
        """Set the parameter errors.

        @param index:           The index of the parameter to set the errors for.
        @type index:            int
        @param error:           The error value.
        @type error:            float
        @keyword model_info:    The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:       list of SpinContainer instances, list of str
        """

        # Unpack the data.
        spin_ids = model_info
        spins = spin_ids_to_containers(spin_ids)

        # The number of parameters.
        total_param_num = param_num(spins=spins)

        # No more model parameters.
        model_param = True
        if index >= total_param_num:
            model_param = False

        # The auxiliary cluster parameters.
        aux_params = []
        if 'pA' in spins[0].params:
            aux_params.append('pB')
        if 'pB' in spins[0].params:
            aux_params.append('pA')
        if 'kex' in spins[0].params:
            aux_params.append('tex')
        if 'tex' in spins[0].params:
            aux_params.append('kex')

        # Convert the parameter index.
        if model_param:
            param_name, si, mi = param_index_to_param_info(index=index, spins=spins)
        else:
            param_name = aux_params[index - total_param_num]
            si = 0
            mi = 0

        # The parameter error name.
        err_name = param_name + "_err"

        # The exponential curve parameters.
        if param_name in ['r2eff', 'i0']:
            # Initialise if needed.
            if not hasattr(spins[si], err_name):
                setattr(spins[si], err_name, {})

            # Set the value.
            setattr(spins[si], err_name, error)

        # Model and auxiliary parameters.
        else:
            for spin in spins:
                setattr(spin, err_name, error)


    def set_param_values(self, param=None, value=None, index=None, spin_id=None, error=False, force=True):
        """Set the spin specific parameter values.

        @keyword param:     The parameter name list.
        @type param:        list of str
        @keyword value:     The parameter value list.
        @type value:        list
        @keyword index:     The index for parameters which are of the list-type.
        @type index:        None or int
        @keyword spin_id:   The spin identification string, only used for spin specific parameters.
        @type spin_id:      None or str
        @keyword error:     A flag which if True will allow the parameter errors to be set instead of the values.
        @type error:        bool
        @keyword force:     A flag which if True will cause current values to be overwritten.  If False, a RelaxError will raised if the parameter value is already set.
        @type force:        bool
        """

        # Checks.
        is_str_list(param, 'parameter name')
        is_list(value, 'parameter value')

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

                # Handle the R10 parameters.
                if param[i] in ['r1']:
                    # Loop over the current keys.
                    for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):
                        # The parameter key.
                        key = generate_r20_key(exp_type=exp_type, frq=frq)

                        # Initialise the structure if needed.
                        if not hasattr(spin, obj_name):
                            setattr(spin, obj_name, {})

                        # Set the value.
                        if index == None:
                            obj = getattr(spin, obj_name)
                            obj[key] = value[i]

                        # If the index is specified, let it match the frequency index
                        elif mi == index:
                            obj = getattr(spin, obj_name)
                            obj[key] = value[i]

                # Handle the R20 parameters.
                elif param[i] in PARAMS_R20:
                    # Loop over the current keys.
                    for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):
                        # The parameter key.
                        key = generate_r20_key(exp_type=exp_type, frq=frq)

                        # Initialise the structure if needed.
                        if not hasattr(spin, obj_name):
                            setattr(spin, obj_name, {})

                        # Set the value.
                        if index == None:
                            obj = getattr(spin, obj_name)
                            obj[key] = value[i]

                        # If the index is specified, let it match the frequency index
                        elif mi == index:
                            obj = getattr(spin, obj_name)
                            obj[key] = value[i]

                # Handle the R2eff and I0 parameters.
                elif param[i] in ['r2eff', 'i0'] and not isinstance(value[i], dict):
                    # Loop over all the data.
                    for exp_type, frq, offset, point in loop_exp_frq_offset_point():
                        # The parameter key.
                        key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

                        # Initialise the structure if needed.
                        if not hasattr(spin, obj_name):
                            setattr(spin, obj_name, {})

                        # Set the value.
                        obj = getattr(spin, obj_name)
                        obj[key] = value[i]

                # Set the other parameters.
                else:
                    setattr(spin, obj_name, value[i])


    def set_selected_sim(self, select_sim, model_info=None):
        """Set the simulation selection flag.

        @param select_sim:      The selection flag for the simulations.
        @type select_sim:       bool
        @keyword model_info:    The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:       list of SpinContainer instances, list of str
        """

        # Unpack the data.
        spin_ids = model_info
        spins = spin_ids_to_containers(spin_ids)

        # Loop over the spins, storing the structure for each spin.
        for spin in spins:
            spin.select_sim = deepcopy(select_sim)


    def sim_init_values(self):
        """Initialise the Monte Carlo parameter values."""

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # Add the names of kex-tex pair.
        pairs = {}
        pairs['kex'] = 'tex'
        pairs['tex'] = 'kex'

        # Add the names of pA-pB pair.
        pairs['pA'] = 'pB'
        pairs['pB'] = 'pA'

        # Add the names of kex-k_AB pair and kex-k_BA pair.
        pairs['k_AB'] = 'kex'
        pairs['k_BA'] = 'kex'

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

        # Loop over the spins.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip protons for MMQ data.
            if spin.model in MODEL_LIST_MMQ and spin.isotope == '1H':
                continue

            # Loop over all the data names.
            for object_name in param_names:
                # Not a parameter of the model.
                if not (object_name in spin.params or (object_name in pairs and pairs[object_name] in spin.params)):
                    continue

                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(spin, sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(spin, sim_object_name)

                # Loop over the simulations.
                for j in range(cdp.sim_number):
                    # The non-simulation value.
                    if object_name not in spin.params:
                        value = deepcopy(getattr(spin, pairs[object_name]))
                    else:
                        value = deepcopy(getattr(spin, object_name))

                    # Copy and append the data.
                    sim_object.append(value)

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


    def sim_pack_data(self, data_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param data_id:     The tuple of the spin container and the exponential curve identifying key, as yielded by the base_data_loop() generator method.
        @type data_id:      SpinContainer instance and float
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # The R2eff model (with peak intensity base data).
        if cdp.model_type == MODEL_R2EFF:
            # Unpack the data.
            spin, exp_type, frq, offset, point = data_id

            # Initialise the data structure if needed.
            if not hasattr(spin, 'peak_intensity_sim'):
                spin.peak_intensity_sim = {}

            # Loop over each time point.
            ti = 0
            for time in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point):
                # Get the intensity keys.
                int_keys = find_intensity_keys(exp_type=exp_type, frq=frq, offset=offset, point=point, time=time)

                # Loop over the intensity keys.
                for int_key in int_keys:
                    # Test if the simulation data point already exists.
                    if int_key in spin.peak_intensity_sim:
                        raise RelaxError("Monte Carlo simulation data for the key '%s' already exists." % int_key)

                    # Initialise the list.
                    spin.peak_intensity_sim[int_key] = []

                    # Loop over the simulations, appending the corresponding data.
                    for i in range(cdp.sim_number):
                        spin.peak_intensity_sim[int_key].append(sim_data[i][ti])

                # Increment the time index.
                ti += 1

        # All other models (with R2eff/R1rho base data).
        else:
            # Unpack the data.
            spin, spin_id = data_id

            # 1H MMQ flag.
            proton_mmq_flag = has_proton_mmq_cpmg()

            # Get the attached proton.
            proton = None
            if proton_mmq_flag:
                proton = return_attached_protons(spin_id)[0]

            # Pack the data.
            spin.r2eff_sim = sim_data
            if proton != None:
                proton.r2eff_sim = sim_data


    def sim_return_param(self, index, model_info=None):
        """Return the array of simulation parameter values.

        @param index:           The index of the parameter to return the array of values for.
        @type index:            int
        @keyword model_info:    The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:       list of SpinContainer instances, list of str
        @return:                The array of simulation parameter values.
        @rtype:                 list of float
        """

        # Unpack the data.
        spin_ids = model_info
        spins = spin_ids_to_containers(spin_ids)

        # The number of parameters.
        total_param_num = param_num(spins=spins)

        # No more model parameters.
        model_param = True
        if index >= total_param_num:
            model_param = False

        # The auxiliary cluster parameters.
        aux_params = []
        for spin in spins:
            if not spin.select:
                continue
            if 'pA' in spin.params:
                aux_params.append('pB')
            if 'pB' in spin.params:
                aux_params.append('pA')
            if 'kex' in spin.params:
                aux_params.append('tex')
            if 'tex' in spin.params:
                aux_params.append('kex')
            break

        # No more auxiliary parameters.
        total_aux_num = total_param_num + len(aux_params)
        if index >= total_aux_num:
            return

        # Convert the parameter index.
        if model_param:
            param_name, si, mi = param_index_to_param_info(index=index, spins=spins)
            if not param_name in ['r2eff', 'i0']:
                si = 0
        else:
            param_name = aux_params[index - total_param_num]
            si = 0
            mi = 0

        # The exponential curve parameters.
        sim_data = []
        if param_name == 'r2eff':
            for i in range(cdp.sim_number):
                sim_data.append(spins[si].r2eff_sim[i])
        elif param_name == 'i0':
            for i in range(cdp.sim_number):
                sim_data.append(spins[si].i0_sim[i])

        # Model and auxiliary parameters.
        else:
            sim_data = getattr(spins[si], param_name + "_sim")

        # Set the sim data to None if empty.
        if sim_data == []:
            sim_data = None

        # Return the object.
        return sim_data


    def sim_return_selected(self, model_info=None):
        """Return the array of selected simulation flags.

        @keyword model_info:    The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:       list of SpinContainer instances, list of str
        @return:                The array of selected simulation flags.
        @rtype:                 list of int
        """

        # Unpack the data.
        spin_ids = model_info
        spins = spin_ids_to_containers(spin_ids)

        # Return the array from the first spin, as this array will be identical for all spins in the cluster.
        return spins[0].select_sim
