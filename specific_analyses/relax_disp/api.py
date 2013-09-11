###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
from minfx.generic import generic_minimise
from minfx.grid import grid
from numpy import array, average, dot, float64, identity, log, ones, zeros
from numpy.linalg import inv
from random import gauss
from re import match, search
import sys
from types import MethodType

# relax module imports.
from dep_check import C_module_exp_fn
from lib.dispersion.two_point import calc_two_point_r2eff, calc_two_point_r2eff_err
from lib.errors import RelaxError, RelaxLenError, RelaxNoModelError, RelaxNoSpectraError
from lib.list import count_unique_elements, unique_elements
from lib.mathematics import round_to_next_order
from lib.statistics import std
from lib.text.sectioning import subsection
from pipe_control import pipes, sequence
from pipe_control.mol_res_spin import check_mol_res_spin_data, return_spin, spin_loop
from specific_analyses.api_base import API_base
from specific_analyses.api_common import API_common
from specific_analyses.relax_disp.checks import check_c_modules, check_disp_points, check_exp_type, check_exp_type_fixed_time, check_model_type, check_pipe_type, check_spectra_id_setup
from specific_analyses.relax_disp.disp_data import average_intensity, find_intensity_keys, get_curve_type, has_exponential_exp_type, loop_cluster, loop_exp_frq, loop_exp_frq_point, loop_exp_frq_point_time, loop_frq, loop_frq_point, loop_frq_point_key, loop_frq_point_time, loop_point, loop_time, relax_time, return_cpmg_frqs, return_index_from_disp_point, return_index_from_exp_type, return_index_from_frq, return_key_from_disp_point_index, return_offset_data, return_param_key_from_data, return_r1_data, return_r2eff_arrays, return_spin_lock_nu1, return_value_from_frq_index, spin_ids_to_containers
from specific_analyses.relax_disp.parameters import assemble_param_vector, assemble_scaling_matrix, disassemble_param_vector, linear_constraints, loop_parameters, param_conversion, param_index_to_param_info, param_num
from specific_analyses.relax_disp.variables import MODEL_LIST_FULL, MODEL_LM63, MODEL_LM63_3SITE, MODEL_CR72, MODEL_CR72_FULL, MODEL_DPL94, MODEL_IT99, MODEL_M61, MODEL_M61B, MODEL_NOREX, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_R1RHO_2SITE, MODEL_R2EFF, MODEL_TP02, MODEL_TSMFK01
from target_functions.relax_disp import Dispersion
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container

# C modules.
if C_module_exp_fn:
    from target_functions.relax_fit import setup, func, dfunc, d2func, back_calc_I


class Relax_disp(API_base, API_common):
    """Class containing functions for relaxation dispersion curve fitting."""

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Execute the base class __init__ method.
        super(Relax_disp, self).__init__()

        # Place methods into the API.
        self.data_init = self._data_init_spin
        self.model_type = self._model_type_local
        self.return_conversion_factor = self._return_no_conversion_factor
        self.return_value = self._return_value_general
        self.set_param_values = self._set_param_values_spin

        # Set up the spin parameters.
        self.PARAMS.add('intensities', scope='spin', py_type=dict, grace_string='\\qPeak intensities\\Q')
        self.PARAMS.add('relax_times', scope='spin', py_type=dict, grace_string='\\qRelaxation time period (s)\\Q')
        self.PARAMS.add('cpmg_frqs', scope='spin', py_type=dict, grace_string='\\qCPMG pulse train frequency (Hz)\\Q')
        self.PARAMS.add('spin_lock_nu1', scope='spin', py_type=dict, grace_string='\\qSpin-lock field strength (Hz)\\Q')
        self.PARAMS.add('r2eff', scope='spin', default=15.0, desc='The effective transversal relaxation rate', set='params', py_type=dict, grace_string='\\qR\\s2,eff\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('i0', scope='spin', default=10000.0, desc='The initial intensity', py_type=dict, set='params', grace_string='\\qI\\s0\\Q', err=True, sim=True)
        self.PARAMS.add('r2', scope='spin', default=15.0, desc='The transversal relaxation rate', set='params', py_type=list, grace_string='\\qR\\s2\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('r2a', scope='spin', default=15.0, desc='The transversal relaxation rate for state A in the absence of exchange', set='params', py_type=list, grace_string='\\qR\\s2,A\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('r2b', scope='spin', default=15.0, desc='The transversal relaxation rate for state B in the absence of exchange', set='params', py_type=list, grace_string='\\qR\\s2,B\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('pA', scope='spin', default=0.5, desc='The population for state A', set='params', py_type=float, grace_string='\\qp\\sA\\N\\Q', err=True, sim=True)
        self.PARAMS.add('pB', scope='spin', default=0.5, desc='The population for state B', set='params', py_type=float, grace_string='\\qp\\sB\\N\\Q', err=True, sim=True)
        self.PARAMS.add('phi_ex', scope='spin', default=5.0, desc='The phi_ex = pA.pB.dw**2 value (ppm^2)', set='params', py_type=float, grace_string='\\xF\\B\\sex\\N = \\q p\\sA\\N.p\\sB\\N.\\xDw\\B\\S2\\N\\Q  (ppm\\S2\\N)', err=True, sim=True)
        self.PARAMS.add('phi_ex_B', scope='spin', default=5.0, desc='The fast exchange factor between sites A and B (ppm^2)', set='params', py_type=float, grace_string='\\xF\\B\\sex,B\\N (ppm\\S2\\N)', err=True, sim=True)
        self.PARAMS.add('phi_ex_C', scope='spin', default=5.0, desc='The fast exchange factor between sites A and C (ppm^2)', set='params', py_type=float, grace_string='\\xF\\B\\sex,C\\N (ppm\\S2\\N)', err=True, sim=True)
        self.PARAMS.add('padw2', scope='spin', default=1.0, desc='The pA.dw**2 value (ppm^2)', set='params', py_type=float, grace_string='\\qp\\sA\\N.\\xDw\\B\\S2\\N\\Q  (ppm\\S2\\N)', err=True, sim=True)
        self.PARAMS.add('dw', scope='spin', default=0.0, desc='The chemical shift difference between states A and B (in ppm)', set='params', py_type=float, grace_string='\\q\\xDw\\B\\Q (ppm)', err=True, sim=True)
        self.PARAMS.add('kex', scope='spin', default=10000.0, desc='The exchange rate', set='params', py_type=float, grace_string='\\qk\\sex\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('kB', scope='spin', default=10000.0, desc='Approximate chemical exchange rate constant between sites A and B (rad.s^-1)', set='params', py_type=float, grace_string='\\qk\\sB\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('kC', scope='spin', default=10000.0, desc='Approximate chemical exchange rate constant between sites A and C (rad.s^-1)', set='params', py_type=float, grace_string='\\qk\\sC\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('tex', scope='spin', default=1.0/20000.0, desc='The time of exchange (tex = 1/(2kex))', set='params', py_type=float, grace_string='\\q\\xt\\B\\sex\\N\\Q (s.rad\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('k_AB', scope='spin', default=10000.0, desc='The exchange rate from state A to state B', set='params', py_type=float, grace_string='\\qk\\sAB\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('k_BA', scope='spin', default=10000.0, desc='The exchange rate from state B to state A', set='params', py_type=float, grace_string='\\qk\\sBA\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('params', scope='spin', desc='The model parameters', py_type=list)

        # Add the minimisation data.
        self.PARAMS.add_min_data(min_stats_global=False, min_stats_spin=True)


    def _back_calc_r2eff(self, spin=None, spin_id=None):
        """Back-calculation of R2eff/R1rho values for the given spin.

        @keyword spin:      The specific spin data container.
        @type spin:         SpinContainer instance
        @keyword spin_id:   The spin ID string for the spin container.
        @type spin_id:      str
        @return:            The back-calculated R2eff/R1rho value for the given spin.
        @rtype:             numpy rank-1 float array
        """

        # Create the initial parameter vector.
        param_vector = assemble_param_vector(spins=[spin])

        # Create a scaling matrix.
        scaling_matrix = assemble_scaling_matrix(spins=[spin], scaling=False)

        # Number of spectrometer fields.
        fields = [None]
        field_count = 1
        if hasattr(cdp, 'spectrometer_frq_count'):
            fields = cdp.spectrometer_frq_list
            field_count = cdp.spectrometer_frq_count

        # Initialise the data structures for the target function.
        values, errors, missing, frqs, exp_types = return_r2eff_arrays(spins=[spin], spin_ids=[spin_id], fields=fields, field_count=field_count)

        # The offset and R1 data for R1rho off-resonance models.
        chemical_shifts, offsets, tilt_angles, r1 = None, None, None, None
        if spin.model in [MODEL_DPL94, MODEL_TP02, MODEL_NS_R1RHO_2SITE]:
            chemical_shifts, offsets, tilt_angles = return_offset_data(spins=[spin], spin_ids=[spin_id], fields=fields, field_count=field_count)
            r1 = return_r1_data(spins=[spin], spin_ids=[spin_id], fields=fields, field_count=field_count)

        # Initialise the relaxation dispersion fit functions.
        model = Dispersion(model=spin.model, num_params=param_num(spins=[spin]), num_spins=1, num_frq=field_count, num_disp_points=cdp.dispersion_points, exp_types=exp_types, values=values, errors=errors, missing=missing, frqs=frqs, cpmg_frqs=return_cpmg_frqs(ref_flag=False), spin_lock_nu1=return_spin_lock_nu1(ref_flag=False), chemical_shifts=chemical_shifts, spin_lock_offsets=offsets, tilt_angles=tilt_angles, r1=r1, relax_time=cdp.relax_time_list[0], scaling_matrix=scaling_matrix)

        # Make a single function call.  This will cause back calculation and the data will be stored in the class instance.
        model.func(param_vector)

        # Convert to a dictionary matching the R2eff data structure.
        results = {}
        for exp_type, frq, point in loop_exp_frq_point():
            # The indices.
            exp_type_index = return_index_from_exp_type(exp_type=exp_type)
            frq_index = return_index_from_frq(frq)
            point_index = return_index_from_disp_point(point, exp_type=exp_type)

            # The parameter key.
            param_key = return_param_key_from_data(frq=frq, point=point)

            # Skip missing data.
            if missing[exp_type_index, 0, frq_index, point_index]:
                continue

            # Store the result.
            results[param_key] = model.back_calc[0, frq_index, point_index]

        # Return the back calculated R2eff values.
        return results


    def _back_calc_peak_intensities(self, spin=None, exp_type=None, frq=None, point=None):
        """Back-calculation of peak intensity for the given relaxation time.

        @keyword spin:      The specific spin data container.
        @type spin:         SpinContainer instance
        @keyword exp_type:  The experiment type.
        @type exp_type:     str
        @keyword frq:       The spectrometer frequency.
        @type frq:          float
        @keyword point:     The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
        @type point:        float
        @return:            The back-calculated peak intensities for the given exponential curve.
        @rtype:             numpy rank-1 float array
        """

        # Check.
        if not has_exponential_exp_type():
            raise RelaxError("Back-calculation is not allowed for the fixed time experiment types.")

        # The key.
        param_key = return_param_key_from_data(frq=frq, point=point)

        # Create the initial parameter vector.
        param_vector = assemble_param_vector(spins=[spin], key=param_key)

        # Create a scaling matrix.
        scaling_matrix = assemble_scaling_matrix(spins=[spin], key=param_key, scaling=False)

        # The peak intensities and times.
        values = []
        errors = []
        times = []
        for time in cdp.relax_time_list:
            # The data.
            values.append(average_intensity(spin=spin, exp_type=exp_type, frq=frq, point=point, time=time))
            errors.append(average_intensity(spin=spin, exp_type=exp_type, frq=frq, point=point, time=time, error=True))
            times.append(time)

        # The scaling matrix in a diagonalised list form.
        scaling_list = []
        for i in range(len(scaling_matrix)):
            scaling_list.append(scaling_matrix[i, i])

        # Initialise the relaxation fit functions.
        setup(num_params=len(param_vector), num_times=len(times), values=values, sd=errors, relax_times=times, scaling_matrix=scaling_list)

        # Make a single function call.  This will cause back calculation and the data will be stored in the C module.
        func(param_vector)

        # Get the data back.
        results = back_calc_I()

        # Return the correct peak height.
        return results


    def _cluster(self, cluster_id=None, spin_id=None):
        """Define spin clustering.

        @keyword cluster_id:    The cluster ID string.
        @type cluster_id:       str
        @keyword spin_id:       The spin ID string for the spin or group of spins to add to the cluster.
        @type spin_id:          str
        """

        # Initialise.
        if not hasattr(cdp, 'clustering'):
            # Create the dictionary.
            cdp.clustering = {}
            cdp.clustering['free spins'] = []

            # Add all spin IDs to the cluster.
            for spin, id in spin_loop(return_id=True):
                cdp.clustering['free spins'].append(id)

        # Add the key.
        if cluster_id not in cdp.clustering:
            cdp.clustering[cluster_id] = []

        # Loop over the spins to add to the cluster.
        for spin, id in spin_loop(selection=spin_id, return_id=True):
            # First remove the ID from all clusters.
            for key in cdp.clustering.keys():
                if id in cdp.clustering[key]:
                    cdp.clustering[key].pop(cdp.clustering[key].index(id))

            # Then add the ID to the cluster.
            cdp.clustering[cluster_id].append(id)

        # Clean up - delete any empty clusters (except the free spins).
        clean = []
        for key in cdp.clustering.keys():
            if key == 'free spins':
                continue
            if cdp.clustering[key] == []:
                clean.append(key)
        for key in clean:
            cdp.clustering.pop(key)


    def _cluster_ids(self):
        """Return the current list of cluster ID strings.

        @return:    The list of cluster IDs.
        @rtype:     list of str
        """

        # Initialise.
        ids = ['free spins']

        # Add the defined IDs.
        if hasattr(cdp, 'cluster'):
            for key in list(cdp.cluster.keys()):
                if key not in ids:
                    ids.append(key)

        # Return the IDs.
        return ids


    def _grid_search_setup(self, spins=None, param_vector=None, lower=None, upper=None, inc=None, scaling_matrix=None):
        """The grid search setup function.

        @keyword spins:             The list of spin data containers for the block.
        @type spins:                list of SpinContainer instances
        @keyword param_vector:      The parameter vector.
        @type param_vector:         numpy array
        @keyword lower:             The lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  array of int
        @keyword scaling_matrix:    The scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        @return:                    A tuple of the grid size and the minimisation options.  For the minimisation options, the first dimension corresponds to the model parameter.  The second dimension is a list of the number of increments, the lower bound, and upper bound.
        @rtype:                     (int, list of lists [int, float, float])
        """

        # The length of the parameter array.
        n = len(param_vector)

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            raise RelaxError("Cannot run a grid search on a model with zero parameters.")

        # Lower bounds.
        if lower != None and len(lower) != n:
            raise RelaxLenError('lower bounds', n)

        # Upper bounds.
        if upper != None and len(upper) != n:
            raise RelaxLenError('upper bounds', n)

        # Increment.
        if isinstance(inc, list) and len(inc) != n:
            raise RelaxLenError('increment', n)
        elif isinstance(inc, int):
            inc = [inc]*n

        # Set up the default bounds.
        if not lower:
            # Init.
            lower = []
            upper = []

            # The R2eff model.
            if cdp.model_type == 'R2eff':
                for spin_index in range(len(spins)):
                    # Alias the spin.
                    spin = spins[spin_index]

                    # Loop over each spectrometer frequency and dispersion point.
                    for exp_type, frq, point in loop_exp_frq_point():
                        # Loop over the parameters.
                        for i in range(len(spin.params)):
                            # R2eff relaxation rate (from 1 to 40 s^-1).
                            if spin.params[i] == 'r2eff':
                                lower.append(1.0)
                                upper.append(40.0)

                            # Intensity.
                            elif spin.params[i] == 'i0':
                                lower.append(0.0001)
                                upper.append(max(spin.intensities.values()))

            # All other models.
            else:
                # The spin specific parameters.
                for spin in spins:
                    for i in range(len(spin.params)):
                        # R2 relaxation rates (from 1 to 40 s^-1).
                        if spin.params[i] in ['r2', 'r2a', 'r2b']:
                            lower.append(1.0)
                            upper.append(40.0)

                        # The pA.pB.dw**2 and pA.dw**2 parameters.
                        elif spin.params[i] in ['phi_ex', 'phi_ex_B', 'phi_ex_C', 'padw2']:
                            lower.append(0.0)
                            upper.append(10.0)

                        # Chemical shift difference between states A and B.
                        elif spin.params[i] == 'dw':
                            lower.append(0.0)
                            upper.append(10.0)

                # The cluster specific parameters (only use the values from the first spin of the cluster).
                spin = spins[0]
                for i in range(len(spin.params)):
                    # The population of state A.
                    if spin.params[i] == 'pA':
                        if spin.model == MODEL_M61B:
                            lower.append(0.85)
                        else:
                            lower.append(0.5)
                        upper.append(1.0)

                    # Exchange rates.
                    elif spin.params[i] in ['kex', 'k_AB', 'kB', 'kC']:
                        lower.append(1.0)
                        upper.append(100000.0)

                    # Time of exchange.
                    elif spin.params[i] in ['tex']:
                        lower.append(1/200000.0)
                        upper.append(0.5)

        # The full grid size.
        grid_size = 1
        for i in range(n):
            grid_size *= inc[i]

        # Diagonal scaling of minimisation options.
        lower_new = []
        upper_new = []
        for i in range(n):
            lower_new.append(lower[i] / scaling_matrix[i, i])
            upper_new.append(upper[i] / scaling_matrix[i, i])

        # Return the data structures.
        return grid_size, inc, lower_new, upper_new


    def _minimise_r2eff(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Optimise the R2eff model by fitting the 2-parameter exponential curves.

        This mimics the R1 and R2 relax_fit analysis.


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
        @keyword inc:               The increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  array of int
        """

        # Check that the C modules have been compiled.
        if not C_module_exp_fn:
            raise RelaxError("Relaxation curve fitting is not available.  Try compiling the C modules on your platform.")

        # Loop over the spins.
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            # Skip spins which have no data.
            if not hasattr(spin, 'intensities'):
                continue

            # Loop over each spectrometer frequency and dispersion point.
            for exp_type, frq, point in loop_exp_frq_point():
                # The parameter key.
                param_key = return_param_key_from_data(frq=frq, point=point)

                # The initial parameter vector.
                param_vector = assemble_param_vector(spins=[spin], key=param_key, sim_index=sim_index)

                # Diagonal scaling.
                scaling_matrix = assemble_scaling_matrix(spins=[spin], key=param_key, scaling=scaling)
                if len(scaling_matrix):
                    param_vector = dot(inv(scaling_matrix), param_vector)

                # Get the grid search minimisation options.
                lower_new, upper_new = None, None
                if match('^[Gg]rid', min_algor):
                    grid_size, inc_new, lower_new, upper_new = self._grid_search_setup(spins=[spin], param_vector=param_vector, lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix)

                # Linear constraints.
                A, b = None, None
                if constraints:
                    A, b = linear_constraints(spins=[spin], scaling_matrix=scaling_matrix)

                # Print out.
                if verbosity >= 1:
                    # Individual spin section.
                    top = 2
                    if verbosity >= 2:
                        top += 2
                    text = "Fitting to spin %s, frequency %s and dispersion point %s" % (spin_id, frq, point)
                    subsection(file=sys.stdout, text=text, prespace=top)

                    # Grid search printout.
                    if match('^[Gg]rid', min_algor):
                        print("Unconstrained grid search size: %s (constraints may decrease this size).\n" % grid_size)

                # The peak intensities, errors and times.
                values = []
                errors = []
                times = []
                for time in cdp.relax_time_list:
                    values.append(average_intensity(spin=spin, exp_type=exp_type, frq=frq, point=point, time=time, sim_index=sim_index))
                    errors.append(average_intensity(spin=spin, exp_type=exp_type, frq=frq, point=point, time=time, error=True))
                    times.append(time)

                # The scaling matrix in a diagonalised list form.
                scaling_list = []
                for i in range(len(scaling_matrix)):
                    scaling_list.append(scaling_matrix[i, i])

                # Initialise the function to minimise.
                setup(num_params=len(param_vector), num_times=len(times), values=values, sd=errors, relax_times=times, scaling_matrix=scaling_list)

                # Grid search.
                if search('^[Gg]rid', min_algor):
                    results = grid(func=func, args=(), num_incs=inc_new, lower=lower_new, upper=upper_new, A=A, b=b, verbosity=verbosity)

                    # Unpack the results.
                    param_vector, chi2, iter_count, warning = results
                    f_count = iter_count
                    g_count = 0.0
                    h_count = 0.0

                # Minimisation.
                else:
                    results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=True, print_flag=verbosity)

                    # Unpack the results.
                    if results == None:
                        return
                    param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

                # Scaling.
                if scaling:
                    param_vector = dot(scaling_matrix, param_vector)

                # Disassemble the parameter vector.
                disassemble_param_vector(param_vector=param_vector, spins=[spin], key=param_key, sim_index=sim_index)

                # Monte Carlo minimisation statistics.
                if sim_index != None:
                    # Chi-squared statistic.
                    spin.chi2_sim[sim_index] = chi2

                    # Iterations.
                    spin.iter_sim[sim_index] = iter_count

                    # Function evaluations.
                    spin.f_count_sim[sim_index] = f_count

                    # Gradient evaluations.
                    spin.g_count_sim[sim_index] = g_count

                    # Hessian evaluations.
                    spin.h_count_sim[sim_index] = h_count

                    # Warning.
                    spin.warning_sim[sim_index] = warning

                # Normal statistics.
                else:
                    # Chi-squared statistic.
                    spin.chi2 = chi2

                    # Iterations.
                    spin.iter = iter_count

                    # Function evaluations.
                    spin.f_count = f_count

                    # Gradient evaluations.
                    spin.g_count = g_count

                    # Hessian evaluations.
                    spin.h_count = h_count

                    # Warning.
                    spin.warning = warning


    def _model_setup(self, model, params):
        """Update various model specific data structures.

        @param model:   The relaxation dispersion curve type.
        @type model:    str
        @param params:  A list consisting of the model parameters.
        @type params:   list of str
        """

        # The model group.
        if model == MODEL_R2EFF:
            cdp.model_type = 'R2eff'
        else:
            cdp.model_type = 'disp'

        # Loop over the sequence.
        for spin in spin_loop(skip_desel=True):
            # The model and parameter names.
            spin.model = model
            spin.params = params

            # Initialise the data structures (if needed).
            self.data_init(spin)


    def _select_model(self, model=MODEL_R2EFF):
        """Set up the model for the relaxation dispersion analysis.

        @keyword model: The relaxation dispersion analysis type.
        @type model:    str
        """

        # Data checks.
        pipes.test()
        check_pipe_type()
        check_mol_res_spin_data()
        check_exp_type()
        if model == MODEL_R2EFF:
            check_c_modules()

        # The curve type.
        curve_type = get_curve_type()

        # R2eff/R1rho model.
        if model == MODEL_R2EFF:
            print("R2eff/R1rho value and error determination.")
            if curve_type == 'exponential':
                params = ['r2eff', 'i0']
            else:
                params = ['r2eff']

        # The model for no chemical exchange relaxation.
        elif model == MODEL_NOREX:
            print("The model for no chemical exchange relaxation.")
            params = []
            for frq in loop_frq():
                params.append('r2')

        # LM63 model.
        elif model == MODEL_LM63:
            print("The Luz and Meiboom (1963) 2-site fast exchange model.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['phi_ex', 'kex']

        # LM63 3-site model.
        elif model == MODEL_LM63_3SITE:
            print("The Luz and Meiboom (1963) 3-site fast exchange model.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['phi_ex_B', 'phi_ex_C', 'kB', 'kC']

        # Full CR72 model.
        elif model == MODEL_CR72_FULL:
            print("The full Carver and Richards (1972) 2-site model for all time scales.")
            params = []
            for frq in loop_frq():
                params.append('r2a')
            for frq in loop_frq():
                params.append('r2b')
            params += ['pA', 'dw', 'kex']

        # Reduced CR72 model.
        elif model == MODEL_CR72:
            print("The reduced Carver and Richards (1972) 2-site model for all time scales, whereby the simplification R20A = R20B is assumed.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['pA', 'dw', 'kex']

        # IT99 model.
        elif model == MODEL_IT99:
            print("The Ishima and Torchia (1999) CPMG 2-site model for all time scales with pA >> pB.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['phi_ex', 'padw2', 'tex']

        # TSMFK01 model.
        elif model == MODEL_TSMFK01:
            print("The Tollinger et al. (2001) 2-site very-slow exchange model, range of microsecond to second time scale.")
            params = []
            for frq in loop_frq():
                params.append('r2a')
            params += ['dw', 'k_AB']

        # Full NS CPMG 2-site 3D model.
        elif model == MODEL_NS_CPMG_2SITE_3D_FULL:
            print("The full numerical solution for the 2-site Bloch-McConnell equations for CPMG data using 3D magnetisation vectors.")
            params = []
            for frq in loop_frq():
                params.append('r2a')
            for frq in loop_frq():
                params.append('r2b')
            params += ['pA', 'dw', 'kex']

        # Reduced NS CPMG 2-site 3D model.
        elif model == MODEL_NS_CPMG_2SITE_3D:
            print("The reduced numerical solution for the 2-site Bloch-McConnell equations for CPMG data using 3D magnetisation vectors, whereby the simplification R20A = R20B is assumed.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['pA', 'dw', 'kex']

        # NS CPMG 2-site expanded model.
        elif model == MODEL_NS_CPMG_2SITE_EXPANDED:
            print("The numerical solution for the 2-site Bloch-McConnell equations for CPMG data expanded using Maple by Nikolai Skrynnikov.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['pA', 'dw', 'kex']

        # Full NS CPMG 2-site star model.
        elif model == MODEL_NS_CPMG_2SITE_STAR_FULL:
            print("The full numerical solution for the 2-site Bloch-McConnell equations for CPMG data using complex conjugate matrices.")
            params = []
            for frq in loop_frq():
                params.append('r2a')
            for frq in loop_frq():
                params.append('r2b')
            params += ['pA', 'dw', 'kex']

        # Reduced NS CPMG 2-site star model.
        elif model == MODEL_NS_CPMG_2SITE_STAR:
            print("The numerical reduced solution for the 2-site Bloch-McConnell equations for CPMG data using complex conjugate matrices, whereby the simplification R20A = R20B is assumed.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['pA', 'dw', 'kex']

        # M61 model.
        elif model == MODEL_M61:
            print("The Meiboom (1961) 2-site fast exchange model for R1rho-type experiments.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['phi_ex', 'kex']

        # M61 skew model.
        elif model == MODEL_M61B:
            print("The Meiboom (1961) on-resonance 2-site model with skewed populations (pA >> pB) for R1rho-type experiments.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['pA', 'dw', 'kex']

        # DPL94 model.
        elif model == MODEL_DPL94:
            print("The Davis, Perlman and London (1994) 2-site fast exchange model for R1rho-type experiments.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['phi_ex', 'kex']

        # TP02 model.
        elif model == MODEL_TP02:
            print("The Trott and Palmer (2002) off-resonance 2-site model for R1rho-type experiments.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['pA', 'dw', 'kex']

        # Reduced NS R1rho 2-site model.
        elif model == MODEL_NS_R1RHO_2SITE:
            print("The reduced numerical solution for the 2-site Bloch-McConnell equations for R1rho data using 3D magnetisation vectors, whereby the simplification R20A = R20B is assumed.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['pA', 'dw', 'kex']

        # Invalid model.
        else:
            raise RelaxError("The model '%s' must be one of %s." % (model, MODEL_LIST_FULL))

        # Set up the model.
        self._model_setup(model, params)


    def base_data_loop(self):
        """Custom generator method for looping over the base data.

        For the R2eff model, the base data is the peak intensity data defining a single exponential curve.  For all other models, the base data is the R2eff/R1rho values for individual spins.


        @return:    For the R2eff model, a tuple of the spin container and the exponential curve identifying key (the CPMG frequency or R1rho spin-lock field strength).  For all other models, the spin container and ID from the spin loop.
        @rtype:     (tuple of SpinContainer instance and float) or (SpinContainer instance and str)
        """

        # The R2eff model data (the base data is peak intensities).
        if cdp.model_type == 'R2eff':
            # Loop over the sequence.
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins with no peak intensity data.
                if not hasattr(spin, 'intensities'):
                    continue

                # Loop over each spectrometer frequency and dispersion point.
                for exp_type, frq, point in loop_exp_frq_point():
                    yield spin, exp_type, frq, point

        # All other models (the base data is the R2eff/R1rho values).
        else:
            # Loop over the sequence.
            for spin, spin_id in spin_loop(return_id=True):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins with no R2eff/R1rho values.
                if not hasattr(spin, 'r2eff'):
                    continue

                # Yield the spin container and ID.
                yield spin, spin_id


    def calculate(self, spin_id=None, verbosity=1, sim_index=None):
        """Calculate the R2eff values for fixed relaxation time period data.

        @keyword spin_id:   The spin identification string.
        @type spin_id:      None or str
        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        @keyword sim_index: The MC simulation index (unused).
        @type sim_index:    None
        """

        # Data checks.
        pipes.test()
        check_mol_res_spin_data()
        check_exp_type()
        check_model_type()
        check_disp_points()
        check_exp_type_fixed_time()

        # Printouts.
        print("Calculating the R2eff/R1rho values for fixed relaxation time period data.")

        # Loop over the spins.
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            # Spin ID printout.
            print("Spin '%s'." % spin_id)

            # Skip spins which have no data.
            if not hasattr(spin, 'intensities'):
                continue

            # Initialise the data structures.
            if not hasattr(spin, 'r2eff'):
                spin.r2eff = {}
            if not hasattr(spin, 'r2eff_err'):
                spin.r2eff_err = {}

            # Loop over all the data.
            for exp_type, frq, point, time in loop_exp_frq_point_time():
                # The three keys.
                ref_keys = find_intensity_keys(exp_type=exp_type, frq=frq, point=None, time=time)
                int_keys = find_intensity_keys(exp_type=exp_type, frq=frq, point=point, time=time)
                param_key = return_param_key_from_data(frq=frq, point=point)

                # Check for missing data.
                missing = False
                for i in range(len(ref_keys)):
                    if ref_keys[i] not in spin.intensities:
                        missing = True
                for i in range(len(int_keys)):
                    if int_keys[i] not in spin.intensities:
                        missing = True
                if missing:
                    continue

                # Average the reference intensity data and errors.
                ref_intensity = average_intensity(spin=spin, exp_type=exp_type, frq=frq, point=None, time=time)
                ref_intensity_err = average_intensity(spin=spin, exp_type=exp_type, frq=frq, point=None, time=time, error=True)

                # Average the intensity data and errors.
                intensity = average_intensity(spin=spin, exp_type=exp_type, frq=frq, point=point, time=time)
                intensity_err = average_intensity(spin=spin, exp_type=exp_type, frq=frq, point=point, time=time, error=True)

                # Calculate the R2eff value.
                spin.r2eff[param_key] = calc_two_point_r2eff(relax_time=time, I_ref=ref_intensity, I=intensity)

                # Calculate the R2eff error.
                spin.r2eff_err[param_key] = calc_two_point_r2eff_err(relax_time=time, I_ref=ref_intensity, I=intensity, I_ref_err=ref_intensity_err, I_err=intensity_err)


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
        if cdp.model_type == 'R2eff':
            # Unpack the data.
            spin, exp_type, frq, point = data_id

            # Back calculate the peak intensities.
            values = self._back_calc_peak_intensities(spin=spin, exp_type=exp_type, frq=frq, point=point)

        # All other models (with R2eff/R1rho base data).
        else:
            # Unpack the data.
            spin, spin_id = data_id

            # Back calculate the R2eff/R1rho data.
            values = self._back_calc_r2eff(spin=spin, spin_id=spin_id)

        # Return the MC data.
        return values


    default_value_doc = Desc_container("Relaxation dispersion default values")
    _table = uf_tables.add_table(label="table: dispersion default values", caption="Relaxation dispersion default values.")
    _table.add_headings(["Data type", "Object name", "Value"])
    _table.add_row(["Transversal relaxation rate (rad/s)", "'r2'", "15.0"])
    _table.add_row(["Transversal relaxation rate for state A (rad/s)", "'r2a'", "15.0"])
    _table.add_row(["Transversal relaxation rate for state B (rad/s)", "'r2b'", "15.0"])
    _table.add_row(["Population of state A", "'pA'", "0.5"])
    _table.add_row(["Population of state B", "'pB'", "0.5"])
    _table.add_row(["The pA.pB.dw**2 parameter (ppm^2)", "'phi_ex'", "5.0"])
    _table.add_row(["The pA.pB.dw**2 parameter of state B (ppm^2)", "'phi_ex_B'", "5.0"])
    _table.add_row(["The pA.pB.dw**2 parameter of state C (ppm^2)", "'phi_ex_C'", "5.0"])
    _table.add_row(["The pA.dw**2 parameter (ppm^2)", "'padw2'", "1.0"])
    _table.add_row(["Chemical shift difference between states A and B (ppm)", "'dw'", "0.0"])
    _table.add_row(["Exchange rate (rad/s)", "'kex'", "10000.0"])
    _table.add_row(["Exchange rate between sites A and B (rad/s)", "'kB'", "10000.0"])
    _table.add_row(["Exchange rate between sites A and C (rad/s)", "'kC'", "10000.0"])
    _table.add_row(["Time of exchange (s/rad)", "'tex'", "1.0/20000.0"])
    _table.add_row(["Exchange rate from state A to state B (rad/s)", "'k_AB'", "10000.0"])
    _table.add_row(["Exchange rate from state B to state A (rad/s)", "'k_BA'", "10000.0"])
    default_value_doc.add_table(_table.label)


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


    def grid_search(self, lower=None, upper=None, inc=None, constraints=True, verbosity=1, sim_index=None):
        """The relaxation dispersion curve fitting grid search function.

        @keyword lower:         The lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:            array of numbers
        @keyword upper:         The upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:            array of numbers
        @keyword inc:           The increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.
        @type inc:              array of int
        @keyword constraints:   If True, constraints are applied during the grid search (eliminating parts of the grid).  If False, no constraints are used.
        @type constraints:      bool
        @keyword verbosity:     A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:        int
        @keyword sim_index:     The index of the simulation to apply the grid search to.  If None, the normal model is optimised.
        @type sim_index:        int
        """

        # Minimisation.
        self.minimise(min_algor='grid', lower=lower, upper=upper, inc=inc, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
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
        @keyword inc:               The increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  array of int
        """

        # Data checks.
        check_mol_res_spin_data()
        check_spectra_id_setup()
        check_model_type()

        # Initialise some empty data pipe structures so that the target function set up does not fail.
        if not hasattr(cdp, 'cpmg_frqs_list'):
            cdp.cpmg_frqs_list = []
        if not hasattr(cdp, 'spin_lock_nu1_list'):
            cdp.spin_lock_nu1_list = []

        # Special exponential curve-fitting for the 'R2eff' model.
        if cdp.model_type == 'R2eff':
            # Sanity checks.
            if not has_exponential_exp_type():
                raise RelaxError("The R2eff model with the fixed time period dispersion experiments cannot be optimised.")

            # Optimisation.
            self._minimise_r2eff(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, verbosity=verbosity, sim_index=sim_index, lower=lower, upper=upper, inc=inc)

            # Exit the method.
            return

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
        for spin_ids in self.model_loop():
            # The spin containers.
            spins = spin_ids_to_containers(spin_ids)

            # Skip deselected clusters.
            skip = True
            for spin in spins:
                if spin.select:
                    skip = False
            if skip:
                continue

            # Test if the spectrometer frequencies have been set.
            if spins[0].model in [MODEL_LM63, MODEL_CR72, MODEL_CR72_FULL, MODEL_M61, MODEL_TP02] and not hasattr(cdp, 'spectrometer_frq'):
                raise RelaxError("The spectrometer frequency information has not been specified.")

            # The R2eff/R1rho data.
            values, errors, missing, frqs, exp_types = return_r2eff_arrays(spins=spins, spin_ids=spin_ids, fields=fields, field_count=field_count, sim_index=sim_index)

            # The offset and R1 data for R1rho off-resonance models.
            chemical_shifts, offsets, tilt_angles, r1 = None, None, None, None
            if spins[0].model in [MODEL_DPL94, MODEL_TP02, MODEL_NS_R1RHO_2SITE]:
                chemical_shifts, offsets, tilt_angles = return_offset_data(spins=spins, spin_ids=spin_ids, fields=fields, field_count=field_count)
                r1 = return_r1_data(spins=spins, spin_ids=spin_ids, fields=fields, field_count=field_count, sim_index=sim_index)

            # Create the initial parameter vector.
            param_vector = assemble_param_vector(spins=spins)

            # Diagonal scaling.
            scaling_matrix = assemble_scaling_matrix(spins=spins, scaling=scaling)
            if len(scaling_matrix):
                param_vector = dot(inv(scaling_matrix), param_vector)

            # Get the grid search minimisation options.
            lower_new, upper_new = None, None
            if match('^[Gg]rid', min_algor):
                grid_size, inc_new, lower_new, upper_new = self._grid_search_setup(spins=spins, param_vector=param_vector, lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix)

            # Linear constraints.
            A, b = None, None
            if constraints:
                A, b = linear_constraints(spins=spins, scaling_matrix=scaling_matrix)

            # Print out.
            if verbosity >= 1:
                # Individual spin block section.
                top = 2
                if verbosity >= 2:
                    top += 2
                subsection(file=sys.stdout, text="Fitting to the spin block %s"%spin_ids, prespace=top)

                # Grid search printout.
                if match('^[Gg]rid', min_algor):
                    print("Unconstrained grid search size: %s (constraints may decrease this size).\n" % grid_size)

            # Initialise the function to minimise.
            model = Dispersion(model=spins[0].model, num_params=param_num(spins=spins), num_spins=len(spins), num_frq=field_count, num_disp_points=cdp.dispersion_points, exp_types=exp_types, values=values, errors=errors, missing=missing, frqs=frqs, cpmg_frqs=return_cpmg_frqs(ref_flag=False), spin_lock_nu1=return_spin_lock_nu1(ref_flag=False), chemical_shifts=chemical_shifts, spin_lock_offsets=offsets, tilt_angles=tilt_angles, r1=r1, relax_time=cdp.relax_time_list[0], scaling_matrix=scaling_matrix)

            # Grid search.
            if search('^[Gg]rid', min_algor):
                results = grid(func=model.func, args=(), num_incs=inc_new, lower=lower_new, upper=upper_new, A=A, b=b, verbosity=verbosity)

                # Unpack the results.
                param_vector, chi2, iter_count, warning = results
                f_count = iter_count
                g_count = 0.0
                h_count = 0.0

            # Minimisation.
            else:
                results = generic_minimise(func=model.func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=True, print_flag=verbosity)

                # Unpack the results.
                if results == None:
                    return
                param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

            # Scaling.
            if scaling:
                param_vector = dot(scaling_matrix, param_vector)

            # Disassemble the parameter vector.
            disassemble_param_vector(param_vector=param_vector, spins=spins, sim_index=sim_index)
            param_conversion(spins=spins, sim_index=sim_index)

            # Monte Carlo minimisation statistics.
            if sim_index != None:
                for spin in spins:
                    # Chi-squared statistic.
                    spin.chi2_sim[sim_index] = chi2

                    # Iterations.
                    spin.iter_sim[sim_index] = iter_count

                    # Function evaluations.
                    spin.f_count_sim[sim_index] = f_count

                    # Gradient evaluations.
                    spin.g_count_sim[sim_index] = g_count

                    # Hessian evaluations.
                    spin.h_count_sim[sim_index] = h_count

                    # Warning.
                    spin.warning_sim[sim_index] = warning

            # Normal statistics.
            else:
                for spin in spins:
                    # Chi-squared statistic.
                    spin.chi2 = chi2

                    # Iterations.
                    spin.iter = iter_count

                    # Function evaluations.
                    spin.f_count = f_count

                    # Gradient evaluations.
                    spin.g_count = g_count

                    # Hessian evaluations.
                    spin.h_count = h_count

                    # Warning.
                    spin.warning = warning

            # Store the back-calculated values.
            if sim_index == None:
                for spin_index in range(len(spins)):
                    # Alias the spin.
                    spin = spins[spin_index]

                    # No data.
                    if not hasattr(spin, 'r2eff'):
                        continue

                    # Initialise.
                    if not hasattr(spin, 'r2eff_bc'):
                        spin.r2eff_bc = {}

                    # Loop over the R2eff data.
                    for exp_type, frq, point in loop_exp_frq_point():
                        # The indices.
                        exp_type_index = return_index_from_exp_type(exp_type=exp_type)
                        disp_pt_index = return_index_from_disp_point(point, exp_type=exp_type)
                        frq_index = return_index_from_frq(frq)

                        # Missing data.
                        if missing[exp_type_index, spin_index, frq_index, disp_pt_index]:
                            continue

                        # The R2eff key.
                        key = return_param_key_from_data(frq=frq, point=point)

                        # Store the back-calculated data.
                        spin.r2eff_bc[key] = model.back_calc[spin_index, frq_index, disp_pt_index]

            # Optimisation printout.
            if verbosity:
                print("\nOptimised parameter values:")
                for param_name, param_index, spin_index, frq_index in loop_parameters(spins=spins):
                    # The parameter with additional details.
                    param_text = param_name
                    if param_name in ['r2', 'r2a', 'r2b']:
                        frq = return_value_from_frq_index(frq_index)
                        if frq:
                            param_text += " (%.3f MHz)" % (frq / 1e6) 
                    param_text += ":"

                    # The printout.
                    print("%-20s %25.15f" % (param_text, param_vector[param_index]))


    def model_desc(self, model_info):
        """Return a description of the model.

        @param model_info:  The model index from model_info().
        @type model_info:   int
        @return:            The model description.
        @rtype:             str
        """

        # The model loop is over the spin clusters, so return a description of the cluster.
        return "The spin cluster %s." % model_info


    def model_loop(self):
        """Loop over the spin groupings for one model applied to multiple spins.

        @return:    The list of spins per block will be yielded, as well as the list of spin IDs.
        @rtype:     tuple of list of SpinContainer instances and list of spin IDs
        """

        # The cluster loop.
        for spin_ids in loop_cluster():
            yield spin_ids


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

        # Unpack the data.
        spin_ids = model_info
        spins = spin_ids_to_containers(spin_ids)

        # The number of parameters for the cluster.
        k = param_num(spins=spins)

        # The number of points from all spins.
        n = 0
        for spin in spins:
            n += len(spin.r2eff)

        # Take the chi-squared from the first spin of the cluster.
        chi2 = spins[0].chi2

        # Return the values.
        return k, n, chi2


    def overfit_deselect(self, data_check=True, verbose=True):
        """Deselect spins which have insufficient data to support minimisation.

        @keyword data_check:    A flag to signal if the presence of base data is to be checked for.
        @type data_check:       bool
        @keyword verbose:       A flag which if True will allow printouts.
        @type verbose:          bool
        """

        # Test the sequence data exists.
        check_mol_res_spin_data()

        # Loop over spin data.
        for spin in spin_loop():
            # Check if data exists.
            if not hasattr(spin, 'intensities'):
                spin.select = False
                continue

            # Require 3 or more data points.
            if len(spin.intensities) < 3:
                spin.select = False
                continue


    def return_data(self, data_id=None):
        """Return the peak intensity data structure.

        @param data_id: The spin ID string, as yielded by the base_data_loop() generator method.
        @type data_id:  str
        @return:        The peak intensity data structure.
        @rtype:         list of float
        """

        # Get the spin container.
        spin = return_spin(spin_id)

        # Return the data.
        return spin.intensities


    return_data_name_doc =  Desc_container("Relaxation dispersion curve fitting data type string matching patterns")
    _table = uf_tables.add_table(label="table: dispersion curve-fit data type patterns", caption="Relaxation dispersion curve fitting data type string matching patterns.")
    _table.add_headings(["Data type", "Object name"])
    _table.add_row(["Transversal relaxation rate (rad/s)", "'r2'"])
    _table.add_row(["Transversal relaxation rate for state A (rad/s)", "'r2a'"])
    _table.add_row(["Transversal relaxation rate for state B (rad/s)", "'r2b'"])
    _table.add_row(["Population of state A", "'pA'"])
    _table.add_row(["Population of state B", "'pB'"])
    _table.add_row(["The pA.pB.dw**2 parameter (ppm^2)", "'phi_ex'"])
    _table.add_row(["The pA.dw**2 parameter (ppm^2)", "'padw2'"])
    _table.add_row(["Chemical shift difference between states A and B (ppm)", "'dw'"])
    _table.add_row(["Exchange rate (rad/s)", "'kex'"])
    _table.add_row(["Exchange rate from state A to state B (rad/s)", "'k_AB'"])
    _table.add_row(["Exchange rate from state B to state A (rad/s)", "'k_BA'"])
    _table.add_row(["Time of exchange (s/rad)", "'tex'"])
    _table.add_row(["Peak intensities (series)", "'intensities'"])
    _table.add_row(["CPMG pulse train frequency (series, Hz)", "'cpmg_frqs'"])
    return_data_name_doc.add_table(_table.label)


    def return_error(self, data_id=None):
        """Return the standard deviation data structure.

        @param data_id: The tuple of the spin container and the exponential curve identifying key, as yielded by the base_data_loop() generator method.
        @type data_id:  SpinContainer instance and float
        @return:        The standard deviation data structure.
        @rtype:         list of float
        """

        # The R2eff model.
        if cdp.model_type == 'R2eff':
            # Unpack the data.
            spin, exp_type, frq, point = data_id

            # Generate the data structure to return.
            errors = []
            for time in cdp.relax_time_list:
                errors.append(average_intensity(spin=spin, exp_type=exp_type, frq=frq, point=point, time=time, error=True))

        # All other models.
        else:
            # Unpack the data.
            spin, spin_id = data_id

            # The errors.
            return spin.r2eff_err

        # Return the error list.
        return errors


    set_doc = Desc_container("Relaxation dispersion curve fitting set details")
    set_doc.add_paragraph("Only three parameters can be set for either the slow- or the fast-exchange regime. For the slow-exchange regime, these parameters include the transversal relaxation rate for state A (R2A), the exchange rate from state A to state (k_AB) and the chemical shift difference between states A and B (dw). For the fast-exchange regime, these include the transversal relaxation rate (R2), the chemical exchange contribution to R2 (Rex) and the exchange rate (kex). Setting parameters for a non selected model has no effect.")


    def set_error(self, model_info, index, error):
        """Set the parameter errors.

        @param model_info:  The spin container originating from model_loop().
        @type model_info:   unknown
        @param index:       The index of the parameter to set the errors for.
        @type index:        int
        @param error:       The error value.
        @type error:        float
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
            param_name, spin_index, frq_index = param_index_to_param_info(index=index, spins=spins)
        else:
            param_name = aux_params[index - total_param_num]
            spin_index = 0
            frq_index = 0

        # The parameter error name.
        err_name = param_name + "_err"

        # The exponential curve parameters.
        if param_name in ['r2eff', 'i0']:
            # Initialise if needed.
            if not hasattr(spins[spin_index], err_name):
                setattr(spins[spin_index], err_name, {})

            # Set the value.
            setattr(spins[spin_index], err_name, error)

        # Model and auxiliary parameters.
        else:
            for spin in spins:
                setattr(spin, err_name, error)


    def set_selected_sim(self, model_info, select_sim):
        """Set the simulation selection flag.

        @param model_info:  The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:   tuple of list of SpinContainer instances and list of spin IDs
        @param select_sim:  The selection flag for the simulations.
        @type select_sim:   bool
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

        # Loop over the residues.
        for spin in spin_loop():
            # Skip deselected residues.
            if not spin.select:
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
        if cdp.model_type == 'R2eff':
            # Unpack the data.
            spin, exp_type, frq, point = data_id

            # Initialise the data structure if needed.
            if not hasattr(spin, 'intensity_sim'):
                spin.intensity_sim = {}

            # Loop over each time point.
            time_index = 0
            for time in loop_time():
                # Get the intensity keys.
                int_keys = find_intensity_keys(exp_type=exp_type, frq=frq, point=point, time=time)

                # Loop over the intensity keys.
                for int_key in int_keys:
                    # Test if the simulation data point already exists.
                    if int_key in spin.intensity_sim:
                        raise RelaxError("Monte Carlo simulation data for the key '%s' already exists." % int_key)

                    # Initialise the list.
                    spin.intensity_sim[int_key] = []

                    # Loop over the simulations, appending the corresponding data.
                    for i in range(cdp.sim_number):
                        spin.intensity_sim[int_key].append(sim_data[i][time_index])

                # Increment the time index.
                time_index += 1

        # All other models (with R2eff/R1rho base data).
        else:
            # Unpack the data.
            spin, spin_id = data_id

            # Pack the data.
            spin.r2eff_sim = sim_data


    def sim_return_param(self, model_info, index):
        """Return the array of simulation parameter values.

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @param index:       The index of the parameter to return the array of values for.
        @type index:        int
        @return:            The array of simulation parameter values.
        @rtype:             list of float
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

        # No more auxiliary parameters.
        total_aux_num = total_param_num + len(aux_params)
        if index >= total_aux_num:
            return

        # Convert the parameter index.
        if model_param:
            param_name, spin_index, frq_index = param_index_to_param_info(index=index, spins=spins)
            if not param_name in ['r2eff', 'i0']:
                spin_index = 0
        else:
            param_name = aux_params[index - total_param_num]
            spin_index = 0
            frq_index = 0

        # The exponential curve parameters.
        sim_data = []
        if param_name == 'r2eff':
            for i in range(cdp.sim_number):
                sim_data.append(spins[spin_index].r2eff_sim[i])
        elif param_name == 'i0':
            for i in range(cdp.sim_number):
                sim_data.append(spins[spin_index].i0_sim[i])

        # Model and auxiliary parameters.
        else:
            sim_data = getattr(spins[spin_index], param_name + "_sim")

        # Set the sim data to None if empty.
        if sim_data == []:
            sim_data = None

        # Return the object.
        return sim_data


    def sim_return_selected(self, model_info):
        """Return the array of selected simulation flags.

        @param model_info:  The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:   tuple of list of SpinContainer instances and list of spin IDs
        @return:            The array of selected simulation flags.
        @rtype:             list of int
        """

        # Unpack the data.
        spin_ids = model_info
        spins = spin_ids_to_containers(spin_ids)

        # Return the array from the first spin, as this array will be identical for all spins in the cluster.
        return spins[0].select_sim
