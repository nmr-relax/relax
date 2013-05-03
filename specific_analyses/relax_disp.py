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
"""The relaxation dispersion curve fitting specific code."""

# Python module imports.
from copy import deepcopy
from minfx.generic import generic_minimise
from minfx.grid import grid
from numpy import array, average, dot, float64, identity, log, zeros
from numpy.linalg import inv
from re import match, search
import sys

# relax module imports.
from dep_check import C_module_exp_fn
from lib.errors import RelaxError, RelaxFuncSetupError, RelaxLenError, RelaxNoModelError, RelaxNoSequenceError, RelaxNoSpectraError
from lib.io import get_file_path, open_write_file
from lib.list import count_unique_elements, unique_elements
from lib.mathematics import round_to_next_order
from lib.software.grace import write_xy_data, write_xy_header
from lib.text.sectioning import subsection
from pipe_control import pipes
from pipe_control.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from pipe_control.result_files import add_result_file
from specific_analyses.api_base import API_base
from specific_analyses.api_common import API_common
from target_functions.relax_disp import Dispersion
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container

# C modules.
if C_module_exp_fn:
    from target_functions.relax_fit import setup, func, dfunc, d2func, back_calc_I


# Some module variables.
FIXED_TIME_EXP = ['cpmg fixed']
VAR_TIME_EXP = ['cpmg', 'r1rho']
CPMG_EXP = ['cpmg', 'cpmg fixed']
R1RHO_EXP = ['r1rho']


class Relax_disp(API_base, API_common):
    """Class containing functions for relaxation dispersion curve fitting."""

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Execute the base class __init__ method.
        super(Relax_disp, self).__init__()

        # Place methods into the API.
        self.data_init = self._data_init_spin
        self.return_conversion_factor = self._return_no_conversion_factor
        self.return_value = self._return_value_general
        self.set_param_values = self._set_param_values_spin
        self.sim_init_values = self._sim_init_values_spin

        # Set up the spin parameters.
        self.PARAMS.add('intensities', scope='spin', py_type=dict, grace_string='\\qPeak intensities\\Q')
        self.PARAMS.add('relax_times', scope='spin', py_type=dict, grace_string='\\qRelaxation time period (s)\\Q')
        self.PARAMS.add('cpmg_frqs', scope='spin', py_type=dict, grace_string='\\qCPMG pulse train frequency (Hz)\\Q')
        self.PARAMS.add('spin_lock_nu1', scope='spin', py_type=dict, grace_string='\\qSpin-lock field strength (Hz)\\Q')
        self.PARAMS.add('r2eff', scope='spin', default=15.0, desc='The effective transversal relaxation rate', set='params', py_type=dict, grace_string='\\qR\\s2,eff\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('i0', scope='spin', default=10000.0, desc='The initial intensity', py_type=dict, set='params', grace_string='\\qI\\s0\\Q', err=True, sim=True)
        self.PARAMS.add('r2', scope='spin', default=15.0, desc='The transversal relaxation rate', set='params', py_type=float, grace_string='\\qR\\s2\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('rex', scope='spin', default=5.0, desc='The chemical exchange contribution to R2', set='params', py_type=float, grace_string='\\qR\\sex\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('kex', scope='spin', default=10000.0, desc='The exchange rate', set='params', py_type=float, grace_string='\\qk\\sex\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('r2a', scope='spin', default=15.0, desc='The transversal relaxation rate for state A', set='params', py_type=float, grace_string='\\qR\\s2,A\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('ka', scope='spin', default=10000.0, desc='The exchange rate from state A to state B', set='params', py_type=float, grace_string='\\qk\\sA\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('dw', scope='spin', default=1000.0, desc='The chemical shift difference between states A and B', set='params', py_type=float, grace_string='\\q\\xDw\\f{}\\Q (Hz)', err=True, sim=True)
        self.PARAMS.add('params', scope='spin', desc='The model parameters', py_type=list)

        # Add the minimisation data.
        self.PARAMS.add_min_data(min_stats_global=False, min_stats_spin=True)


    def _assemble_param_vector(self, spins=None, key=None, sim_index=None):
        """Assemble the dispersion relaxation dispersion curve fitting parameter vector.

        @keyword spins:         The list of spin data containers for the block.
        @type spins:            list of SpinContainer instances
        @keyword key:           The key for the R2eff and I0 parameters.
        @type key:              str or None
        @keyword sim_index:     The optional MC simulation index.
        @type sim_index:        int
        @return:                An array of the parameter values of the dispersion relaxation model.
        @rtype:                 numpy float array
        """

        # Initialise.
        param_vector = []

        # First add the spin specific parameters.
        for spin_index in range(len(spins)):
            # Alias the spin.
            spin = spins[spin_index]

            # A specific exponential curve.
            if key:
                # Loop over the model parameters.
                for i in range(len(spin.params)):
                    # Effective transversal relaxation rate.
                    if spin.params[i] == 'r2eff':
                        if sim_index != None:
                            param_vector.append(spin.r2eff_sim[sim_index][key])
                        elif spin.r2eff == None or key not in spin.r2eff:
                            param_vector.append(0.0)
                        else:
                            param_vector.append(spin.r2eff[key])

                    # Initial intensity.
                    elif spin.params[i] == 'i0':
                        if sim_index != None:
                            param_vector.append(spin.i0_sim[sim_index][key])
                        elif spin.i0 == None or key not in spin.i0:
                            param_vector.append(0.0)
                        else:
                            param_vector.append(spin.i0[key])


            # Loop over each exponential curve.
            else:
                for exp_i, key in self._exp_curve_loop():
                    # Loop over the model parameters.
                    for i in range(len(spin.params)):
                        # Effective transversal relaxation rate.
                        if spin.params[i] == 'r2eff':
                            if sim_index != None:
                                param_vector.append(spin.r2eff_sim[sim_index][key])
                            elif spin.r2eff == None or key not in spin.r2eff:
                                param_vector.append(0.0)
                            else:
                                param_vector.append(spin.r2eff[key])

                        # Initial intensity.
                        elif spin.params[i] == 'i0':
                            if sim_index != None:
                                param_vector.append(spin.i0_sim[sim_index][key])
                            elif spin.i0 == None or key not in spin.i0:
                                param_vector.append(0.0)
                            else:
                                param_vector.append(spin.i0[key])

        # Then the spin block specific parameters, taking the values from the first spin.
        spin = spins[0]
        for i in range(len(spin.params)):
            # Transversal relaxation rate.
            if spin.params[i] == 'r2':
                if sim_index != None:
                    param_vector.append(spin.r2_sim[sim_index])
                elif spin.r2 == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.r2)

            # Chemical exchange contribution to 'R2'.
            if spin.params[i] == 'rex':
                if sim_index != None:
                    param_vector.append(spin.rex_sim[sim_index])
                elif spin.rex == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.rex)

            # Exchange rate.
            elif spin.params[i] == 'kex':
                if sim_index != None:
                    param_vector.append(spin.kex_sim[sim_index])
                elif spin.kex == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.kex)

            # Transversal relaxation rate for state A.
            if spin.params[i] == 'r2a':
                if sim_index != None:
                    param_vector.append(spin.r2a_sim[sim_index])
                elif spin.r2a == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.r2a)

            # Exchange rate from state A to state B.
            if spin.params[i] == 'ka':
                if sim_index != None:
                    param_vector.append(spin.ka_sim[sim_index])
                elif spin.ka == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.ka)

            # Chemical shift difference between states A and B.
            if spin.params[i] == 'dw':
                if sim_index != None:
                    param_vector.append(spin.dw_sim[sim_index])
                elif spin.dw == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.dw)

        # Return a numpy array.
        return array(param_vector, float64)


    def _assemble_scaling_matrix(self, spins=None, key=None, scaling=True):
        """Create and return the scaling matrix.

        @keyword spins:         The list of spin data containers for the block.
        @type spins:            list of SpinContainer instances
        @keyword key:           The key for the R2eff and I0 parameters.
        @type key:              str or None
        @keyword scaling:       A flag which if False will cause the identity matrix to be returned.
        @type scaling:          bool
        @return:                The diagonal and square scaling matrix.
        @rtype:                 numpy diagonal matrix
        """

        # Initialise.
        scaling_matrix = identity(self._param_num(spins=spins), float64)
        i = 0

        # No diagonal scaling.
        if not scaling:
            return scaling_matrix

        # First scale the spin specific parameters.
        param_index = 0
        for spin_index in range(len(spins)):
            # Alias the spin.
            spin = spins[spin_index]

            # A specific exponential curve.
            if key:
                # Effective transversal relaxation rate scaling.
                scaling_matrix[param_index, param_index] = 10
                param_index += 1

                # Initial intensity scaling.
                scaling_matrix[param_index, param_index] = round_to_next_order(max(spin.intensities.values()))
                param_index += 1

            # Loop over each exponential curve.
            else:
                for exp_i, key in self._exp_curve_loop():
                    # Effective transversal relaxation rate scaling.
                    scaling_matrix[param_index, param_index] = 10
                    param_index += 1

                    # Initial intensity scaling.
                    scaling_matrix[param_index, param_index] = round_to_next_order(max(spin.intensities.values()))
                    param_index += 1

        # Then the spin block specific parameters.
        spin = spins[0]
        for i in range(len(spin.params)):
            # Transversal relaxation rate scaling.
            if spin.params[i] == 'r2':
                scaling_matrix[param_index, param_index] = 10

            # Chemical exchange contribution to 'R2' scaling.
            elif spin.params[i] == 'rex':
                scaling_matrix[param_index, param_index] = 10

            # Exchange rate scaling.
            elif spin.params[i] == 'kex':
                scaling_matrix[param_index, param_index] = 10000

            # Transversal relaxation rate for state A scaling
            elif spin.params[i] == 'r2a':
                scaling_matrix[param_index, param_index] = 10

            # Exchange rate from state A to state B scaling.
            elif spin.params[i] == 'ka':
                scaling_matrix[param_index, param_index] = 10000

            # Chemical shift difference between states A and B scaling.
            elif spin.params[i] == 'dw':
                scaling_matrix[param_index, param_index] = 1000

            # Increment the parameter index.
            param_index += 1

        # Return the scaling matrix.
        return scaling_matrix


    def _back_calc(self, spin=None, index=None):
        """Back-calculation of peak intensity for the given spin and exponential curve index.

        @keyword spin:  The specific spin data container.
        @type spin:     SpinContainer instance
        @keyword index: The index for the specific exponential curve.
        @type index:    int
        @return:        The back-calculated peak intensities for the given exponential curve
        @rtype:         numpy rank-1 float array
        """

        # The R2eff model.
        if cdp.model == 'R2eff':
            # Check.
            if cdp.exp_type in FIXED_TIME_EXP:
                raise RelaxError("Back-calculation is not allowed for the fixed time experiment types.")

            # Return the results from special back-calculation method.
            return self._back_calc_r2eff(spin=spin, index=index)

        # Create the initial parameter vector.
        param_vector = self._assemble_param_vector(spins=[spin])

        # Create a scaling matrix.
        scaling_matrix = self._assemble_scaling_matrix(spins=[spin], scaling=False)

        # Initialise the data structures for the target function.
        values = zeros((1, cdp.dispersion_points, cdp.num_time_pts), float64)
        errors = zeros((1, cdp.dispersion_points, cdp.num_time_pts), float64)

        # Initialise the relaxation dispersion fit functions.
        model = Dispersion(model=cdp.model, num_params=self._param_num(spins=[spin]), num_spins=1, num_exp_curves=cdp.dispersion_points, num_times=cdp.num_time_pts, values=values, errors=errors, cpmg_frqs=cdp.cpmg_frqs_list, spin_lock_nu1=cdp.spin_lock_nu1_list, relax_times=cdp.relax_time_list, scaling_matrix=scaling_matrix)

        # Make a single function call.  This will cause back calculation and the data will be stored in the class instance.
        model.func(param_vector)

        # Get the data back.
        results = model.back_calc

        # Return the correct peak intensity series.
        return results[0, index]


    def _back_calc_r2eff(self, spin=None, index=None):
        """Back-calculation of peak intensity for the given relaxation time.

        @keyword spin:  The specific spin data container.
        @type spin:     SpinContainer instance
        @keyword index: The index for the specific exponential curve.
        @type index:    int
        @return:        The back-calculated peak intensities for the given exponential curve
        @rtype:         numpy rank-1 float array
        """

        # The key.
        key = self._exp_curve_key_from_index(index)

        # Create the initial parameter vector.
        param_vector = self._assemble_param_vector(spins=[spin], key=key)

        # Create a scaling matrix.
        scaling_matrix = self._assemble_scaling_matrix(spins=[spin], key=key, scaling=False)

        # The peak intensities and times.
        values = []
        errors = []
        times = []
        for time in cdp.relax_time_list:
            # The key.
            spectra_key = self._intensity_key(exp_key=key, relax_time=time)

            # The data.
            values.append(spin.intensities[spectra_key])
            errors.append(spin.intensity_err[spectra_key])
            times.append(cdp.relax_times[spectra_key])

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
        for key in cdp.clustering.keys():
            if key == 'free spins':
                continue
            if cdp.clustering[key] == []:
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


    def _cpmg_frq(self, spectrum_id=None, cpmg_frq=None):
        """Set the CPMG frequency associated with a given spectrum.

        @keyword spectrum_id:   The spectrum identification string.
        @type spectrum_id:      str
        @keyword cpmg_frq:      The frequency, in Hz, of the CPMG pulse train.
        @type cpmg_frq:         float
        """

        # Test if the spectrum id exists.
        if spectrum_id not in cdp.spectrum_ids:
            raise RelaxNoSpectraError(spectrum_id)

        # Initialise the global CPMG frequency data structures if needed.
        if not hasattr(cdp, 'cpmg_frqs'):
            cdp.cpmg_frqs = {}
        if not hasattr(cdp, 'cpmg_frqs_list'):
            cdp.cpmg_frqs_list = []

        # Add the frequency at the correct position, converting to a float if needed.
        if cpmg_frq == None:
            cdp.cpmg_frqs[spectrum_id] = cpmg_frq
        else:
            cdp.cpmg_frqs[spectrum_id] = float(cpmg_frq)

        # The unique curves for the R2eff fitting (CPMG).
        if cdp.cpmg_frqs[spectrum_id] not in cdp.cpmg_frqs_list:
            cdp.cpmg_frqs_list.append(cdp.cpmg_frqs[spectrum_id])
        cdp.cpmg_frqs_list.sort()

        # Update the exponential curve count.
        cdp.dispersion_points = len(cdp.cpmg_frqs_list)

        # Printout.
        print("Setting the '%s' spectrum CPMG frequency %s Hz." % (spectrum_id, cdp.cpmg_frqs[spectrum_id]))


    def _disassemble_param_vector(self, param_vector=None, key=None, spins=None, sim_index=None):
        """Disassemble the parameter vector.

        @keyword param_vector:  The parameter vector.
        @type param_vector:     numpy array
        @keyword key:           The key for the R2eff and I0 parameters.
        @type key:              str or None
        @keyword spins:         The list of spin data containers for the block.
        @type spins:            list of SpinContainer instances
        @keyword sim_index:     The optional MC simulation index.
        @type sim_index:        int
        """

        # Initialise.
        param_index = 0

        # First add the spin specific parameters.
        for spin_index in range(len(spins)):
            # Alias the spin.
            spin = spins[spin_index]

            # A specific exponential curve.
            if key:
                param_index += 2

                # Loop over the model parameters.
                for i in range(len(spin.params)):
                    # Effective transversal relaxation rate.
                    if spin.params[i] == 'r2eff':
                        if sim_index != None:
                            spin.r2eff_sim[sim_index][key] = param_vector[0]
                        else:
                            spin.r2eff[key] = param_vector[0]

                    # Initial intensity.
                    elif spin.params[i] == 'i0':
                        if sim_index != None:
                            spin.i0_sim[sim_index][key] = param_vector[1]
                        else:
                            spin.i0[key] = param_vector[1]

            # Loop over each exponential curve.
            else:
                for exp_index, key in self._exp_curve_loop():
                    index = spin_index * 2 * cdp.dispersion_points + exp_index * cdp.dispersion_points
                    param_index += 2

                    # Loop over the model parameters.
                    for i in range(len(spin.params)):
                        # Effective transversal relaxation rate.
                        if spin.params[i] == 'r2eff':
                            if sim_index != None:
                                spin.r2eff_sim[sim_index][key] = param_vector[index]
                            else:
                                spin.r2eff[key] = param_vector[index]

                        # Initial intensity.
                        elif spin.params[i] == 'i0':
                            if sim_index != None:
                                spin.i0_sim[sim_index][key] = param_vector[index+1]
                            else:
                                spin.i0[key] = param_vector[index+1]

        # Then the spin block specific parameters, taking the values from the first spin.
        spin = spins[0]
        for i in range(len(spin.params)):
            # Transversal relaxation rate.
            if spin.params[i] == 'r2':
                if sim_index != None:
                    spin.r2_sim[sim_index] = param_vector[param_index]
                else:
                    spin.r2 = param_vector[param_index]

            # Chemical exchange contribution to 'R2'.
            if spin.params[i] == 'rex':
                if sim_index != None:
                    spin.rex_sim[sim_index] = param_vector[param_index]
                else:
                    spin.rex = param_vector[param_index]

            # Exchange rate.
            elif spin.params[i] == 'kex':
                if sim_index != None:
                    spin.kex_sim[sim_index] = param_vector[param_index]
                else:
                    spin.kex = param_vector[param_index]

            # Transversal relaxation rate for state A.
            if spin.params[i] == 'r2a':
                if sim_index != None:
                    spin.r2a_sim[sim_index] = param_vector[param_index]
                else:
                    spin.r2a = param_vector[param_index]

            # Exchange rate from state A to state B.
            if spin.params[i] == 'ka':
                if sim_index != None:
                    spin.ka_sim[sim_index] = param_vector[param_index]
                else:
                    spin.ka = param_vector[param_index]

            # Chemical shift difference between states A and B.
            if spin.params[i] == 'dw':
                if sim_index != None:
                    spin.dw_sim[sim_index] = param_vector[param_index]
                else:
                    spin.dw = param_vector[param_index]

            # Increment the parameter index.
            param_index = param_index + 1


    def _dispersion_point_loop(self):
        """Generator method for looping over all dispersion points (either spin-lock field or nu_CPMG points).

        @return:    Either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz.
        @rtype:     float
        """

        # CPMG type data.
        if cdp.exp_type in ['cpmg']:
            fields = unique_elements(cdp.cpmg_frqs_list.values())
        elif cdp.exp_type in ['r1rho']:
            fields = unique_elements(cdp.spin_lock_nu1.values())
        else:
            raise RelaxError("The experiment type '%s' is unknown." % cdp.exp_type)
        fields.sort()

        # Yield each unique field strength or frequency.
        for field in fields:
            yield field


    def _exp_curve_index_from_key(self, key):
        """Convert the exponential curve key into the corresponding index.

        @param key: The exponential curve key - either the CPMG frequency or R1rho spin-lock field strength.
        @type key:  float
        @return:    The corresponding index.
        @rtype:     int
        """

        # CPMG data.
        if cdp.exp_type == 'cpmg':
            return cdp.cpmg_frqs_list.index(key)

        # R1rho data.
        else:
            return cdp.spin_lock_nu1_list.index(key)


    def _exp_curve_key_from_index(self, index):
        """Convert the exponential curve key into the corresponding index.

        @param index:   The exponential curve index.
        @type index:    int
        @return:        The exponential curve key - either the CPMG frequency or R1rho spin-lock field strength.
        @rtype:         float
        """

        # CPMG data.
        if cdp.exp_type == 'cpmg':
            return cdp.cpmg_frqs_list[index]

        # R1rho data.
        else:
            return cdp.spin_lock_nu1_list[index]


    def _exp_curve_loop(self):
        """Generator method looping over the exponential curves, yielding the index and key pair.

        @return:    The index of the exponential curve and the floating point number key used in the R2eff and I0 spin data structures.
        @rtype:     int and float
        """

        # Loop over each exponential curve.
        for i in range(cdp.dispersion_points):
            # The experiment specific key.
            if cdp.exp_type in ['cpmg', 'cpmg fixed']:
                key = cdp.cpmg_frqs_list[i]
            else:
                key = cdp.spin_lock_nu1_list[i]

            # Yield the data.
            yield i, key


    def _exp_type(self, exp_type='cpmg'):
        """Select the relaxation dispersion experiment type performed.

        @keyword exp: The relaxation dispersion experiment type.  Can be one of 'cpmg' or 'r1rho'.
        @type exp:    str
        """

        # Test if the current pipe exists.
        pipes.test()

        # CPMG relaxation dispersion experiments (exponential curves with varying relax_T).
        if exp_type == 'cpmg':
            print("CPMG experiments with exponential curves from varying the relaxation period.")
            cdp.exp_type = 'cpmg'

        # CPMG relaxation dispersion experiments (fixed relax_T).
        elif exp_type == 'cpmg fixed':
            print("CPMG experiments with a fixed relaxation period.")
            cdp.exp_type = 'cpmg fixed'

        # R1rho relaxation dispersion experiments.
        elif exp_type == 'r1rho':
            print("R1rho experiments with exponential curves from varying the time of application of the spin-lock field.")
            cdp.exp_type = 'r1rho'

        # Invalid relaxation dispersion experiment.
        else:
            raise RelaxError("The relaxation dispersion experiment '%s' is invalid." % exp_type)

        # Sanity check.
        if exp_type not in FIXED_TIME_EXP and exp_type not in VAR_TIME_EXP:
            raise RelaxError("The experiment type '%s' is neither a fixed relaxation time period or variable relaxation time period experiment." % exp_type)


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

            # First the spin specific parameters.
            for spin_index in range(len(spins)):
                # Alias the spin.
                spin = spins[spin_index]

                # Loop over each exponential curve.
                for exp_i, key in self._exp_curve_loop():
                    # Loop over the parameters.
                    for i in range(len(spin.params)):
                        # R2eff relaxation rate (from 0 to 40 s^-1).
                        if spin.params[i] == 'r2eff':
                            lower.append(0.0)
                            upper.append(40.0)

                        # Intensity.
                        elif spin.params[i] == 'i0':
                            lower.append(0.0)
                            upper.append(max(spin.intensities.values()))

            # Then the spin block specific parameters.
            spin = spins[0]
            for i in range(len(spin.params)):
                # R2 relaxation rate (from 0 to 40 s^-1).
                if spin.params[i] == 'r2':
                    lower.append(0.0)
                    upper.append(40.0)

                # Chemical exchange contribution to 'R2'.
                elif spin.params[i] == 'rex':
                    lower.append(0.0)
                    upper.append(20.0)

                # Exchange rate.
                elif spin.params[i] == 'kex':
                    lower.append(0.0)
                    upper.append(100000.0)

                # Transversal relaxation rate for state A.
                elif spin.params[i] == 'r2a':
                    lower.append(0.0)
                    upper.append(20.0)

                # Exchange rate from state A to state B.
                elif spin.params[i] == 'ka':
                    lower.append(0.0)
                    upper.append(100000.0)

                # Chemical shift difference between states A and B.
                elif spin.params[i] == 'dw':
                    lower.append(0.0)
                    upper.append(10000.0)

        # The full grid size.
        grid_size = 1
        for i in range(n):
            grid_size *= inc[i]

        # Test if the grid is too large.
        if isinstance(grid_size, long):
            raise RelaxError("A grid search of size %s is too large." % grid_size)

        # Diagonal scaling of minimisation options.
        lower_new = []
        upper_new = []
        for i in range(n):
            lower_new.append(lower[i] / scaling_matrix[i, i])
            upper_new.append(upper[i] / scaling_matrix[i, i])

        # Return the data structures.
        return grid_size, inc, lower_new, upper_new


    def _intensity_key(self, exp_key=None, relax_time=None):
        """Return the intensity key corresponding to the given exponential curve key and relaxation time.

        @keyword exp_key:       The CPMG frequency or R1rho spin-lock field strength used as a key to identify each exponential curve.
        @type exp_key:          float
        @keyword relax_time:    The time, in seconds, of the relaxation period.
        @type relax_time:       float
        """

        # Find all keys corresponding to the given relaxation time.
        time_keys = []
        for key in cdp.relax_times:
            if cdp.relax_times[key] == relax_time:
                time_keys.append(key)

        # Find all keys corresponding to the given exponential key.
        exp_keys = []
        if cdp.exp_type == 'cpmg':
            data = cdp.cpmg_frqs
        else:
            data = cdp.spin_lock_nu1
        for key in data:
            if data[key] == exp_key:
                exp_keys.append(key)

        # The common key.
        common_key = []
        for key in time_keys:
            if key in exp_keys:
                common_key.append(key)

        # Sanity checks.
        if len(common_key) == 0:
            raise RelaxError("No intensity key could be found for the CPMG frequency or R1rho spin-lock field strength of %s and relaxation time period of %s seconds." % (exp_key, relax_time))
        if len(common_key) != 1:
            raise RelaxError("More than one intensity key %s found for the CPMG frequency or R1rho spin-lock field strength of %s and relaxation time period of %s seconds." % (common_key, exp_key, relax_time))

        # Return the unique key.
        return common_key[0]


    def _linear_constraints(self, spins=None, scaling_matrix=None):
        """Set up the relaxation dispersion curve fitting linear constraint matrices A and b.

        Standard notation
        =================

        The different constraints are::

            R2 >= 0
            Rex >= 0
            kex >= 0

            R2A >= 0
            kA >= 0
            dw >= 0


        Matrix notation
        ===============

        In the notation A.x >= b, where A is a matrix of coefficients, x is an array of parameter values, and b is a vector of scalars, these inequality constraints are::

            | 1  0  0 |     |  R2  |      |    0    |
            |         |     |      |      |         |
            | 1  0  0 |  .  |  Rex |      |    0    |
            |         |     |      |      |         |
            | 1  0  0 |     |  kex |      |    0    |
            |         |     |      |  >=  |         |
            | 1  0  0 |     |  R2A |      |    0    |
            |         |     |      |      |         |
            | 1  0  0 |     |  kA  |      |    0    |
            |         |     |      |      |         |
            | 1  0  0 |     |  dw  |      |    0    |


        @keyword spins:             The list of spin data containers for the block.
        @type spins:                list of SpinContainer instances
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        """

        # Initialisation (0..j..m).
        A = []
        b = []
        n = self._param_num(spins=spins)
        zero_array = zeros(n, float64)
        i = 0
        j = 0

        # First the spin specific parameters.
        for spin_index in range(len(spins)):
            # Alias the spin.
            spin = spins[spin_index]

            # Loop over each exponential curve.
            for exp_i, key in self._exp_curve_loop():
                # Loop over the parameters.
                for k in range(len(spin.params)):
                    # The transversal relaxation rate >= 0.
                    if spin.params[k] == 'r2':
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        b.append(0.0)
                        j += 1

        # Then the spin block specific parameters.
        spin = spins[0]
        for k in range(len(spin.params)):
            # The transversal relaxation rate >= 0.
            if spin.params[k] == 'r2':
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j += 1

            # Relaxation rates and Rex.
            elif search('^r', spin.params[k]):
                # Rex, R2A >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j += 1

            # Exchange rates.
            elif search('^k', spin.params[k]):
                # kex, kA >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j += 1

            # Chemical exchange difference.
            elif spin.params[k] == 'dw':
                # dw >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j += 1

            # Increment i.
            i += 1

        # Convert to numpy data structures.
        A = array(A, float64)
        b = array(b, float64)

        # Return the matrices.
        return A, b


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

        # Loop over the spins.
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            # Skip spins which have no data.
            if not hasattr(spin, 'intensities'):
                continue

            # Loop over each exponential curve.
            for exp_i, key in self._exp_curve_loop():
                # The initial parameter vector.
                param_vector = self._assemble_param_vector(spins=[spin], key=key, sim_index=sim_index)

                # Diagonal scaling.
                scaling_matrix = self._assemble_scaling_matrix(spins=[spin], key=key, scaling=scaling)
                if len(scaling_matrix):
                    param_vector = dot(inv(scaling_matrix), param_vector)

                # Get the grid search minimisation options.
                lower_new, upper_new = None, None
                if match('^[Gg]rid', min_algor):
                    grid_size, inc_new, lower_new, upper_new, = self._grid_search_setup(spins=[spin], param_vector=param_vector, lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix)

                # Linear constraints.
                A, b = None, None
                if constraints:
                    A, b = self._linear_constraints(spins=[spin], scaling_matrix=scaling_matrix)

                # Print out.
                if verbosity >= 1:
                    # Individual spin section.
                    top = 2
                    if verbosity >= 2:
                        top += 2
                    text = "Fitting to spin %s, dispersion point %s" % (spin_id, key)
                    subsection(file=sys.stdout, text=text, prespace=top)

                    # Grid search printout.
                    if match('^[Gg]rid', min_algor):
                        print("Unconstrained grid search size: %s (constraints may decrease this size).\n" % grid_size)

                # The peak intensities, errors and times.
                values = []
                errors = []
                times = []
                for time in cdp.relax_time_list:
                    # The key.
                    spectra_key = self._intensity_key(exp_key=key, relax_time=time)

                    # The values.
                    if sim_index == None:
                        values.append(spin.intensities[spectra_key])
                    else:
                        values.append(spin.intensity_sim[spectra_key][sim_index])

                    # The errors.
                    errors.append(spin.intensity_err[spectra_key])

                    # The relaxation times.
                    times.append(cdp.relax_times[spectra_key])

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
                self._disassemble_param_vector(param_vector=param_vector, spins=[spin], key=key, sim_index=sim_index)

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

        # Set the model.
        cdp.model = model

        # Loop over the sequence.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # The model and parameter names.
            spin.model = model
            spin.params = params

            # Initialise the data structures (if needed).
            self.data_init(spin)


    def _param_index_to_param_info(self, index=None, spins=None):
        """Convert the given parameter array index to parameter identifying information.
        
        The parameter index will be converted to the parameter name, the relevant spin index in the cluster, and relevant exponential curve key.

        @keyword index: The index of the parameter array.
        @type index:    int
        @keyword spins: The list of spin data containers for the block.
        @type spins:    list of SpinContainer instances
        @return:        The parameter name and spin cluster index
        @rtype:         str, int
        """

        # Initialise.
        param_name = None
        spin_index = 0

        # The number of spin specific parameters (R2eff and I0 per spin).
        num = len(spins) * 2

        # The exponential curve parameters.
        if index < num:
            # Even indices are R2eff, odd are I0.
            if index % 2:
                param_name = 'i0'
            else:
                param_name = 'r2eff'

            # The spin index.
            spin_index = int(index / 2)

        # All other parameters.
        else:
            names = self.data_names(set='params')
            param_name = names[index-num+2]

        # Return the data.
        return param_name, spin_index


    def _param_num(self, spins=None):
        """Determine the number of parameters in the model.

        @keyword spins:         The list of spin data containers for the block.
        @type spins:            list of SpinContainer instances
        @return:                The number of model parameters.
        @rtype:                 int
        """

        # The R2eff model.
        if cdp.model == 'R2eff':
            # Exponential curves (with clustering).
            if cdp.exp_type in VAR_TIME_EXP:
                return 2 * len(spins)

            # Fixed time period experiments (with clustering).
            else:
                return 1 * len(spins)

        # The number of spin specific parameters (R2eff and I0 per spin), times the total number of exponential curves.
        num = len(spins) * 2 * cdp.dispersion_points

        # The block specific parameters.
        num += len(spins[0].params) - 2

        # Return the number.
        return num


    def _plot_exp_curves(self, file=None, dir=None, force=None, norm=None):
        """Custom 2D Grace plotting function for the exponential curves.

        @keyword file:          The name of the Grace file to create.
        @type file:             str
        @keyword dir:           The optional directory to place the file into.
        @type dir:              str
        @param force:           Boolean argument which if True causes the file to be overwritten if it already exists.
        @type force:            bool
        @keyword norm:          The normalisation flag which if set to True will cause all graphs to be normalised to a starting value of 1.
        @type norm:             bool
        """

        # Test if the current pipe exists.
        pipes.test()

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Open the file for writing.

        file_path = get_file_path(file, dir)
        file = open_write_file(file, dir, force)

        # Initialise some data structures.
        data = []
        set_labels = []
        x_err_flag = False
        y_err_flag = False

        # Loop over the spectrometer frequencies.
        graph_index = 0
        err = False
        for field in self._spectrometer_loop():
            # Loop over the dispersion points.
            for disp_point in self._dispersion_point_loop():
                # Create a new graph.
                data.append([])

                # Loop over each spin.
                for spin, id in spin_loop(return_id=True, skip_desel=True):
                    # Append a new set structure and set the name to the spin ID.
                    data[graph_index].append([])
                    if graph_index == 0:
                        set_labels.append("Spin %s" % id)

                    # Loop over the relaxation time periods.
                    for time in cdp.relax_time_list:
                        # The key.
                        key = self._intensity_key(exp_key=disp_point, relax_time=time)

                        # Add the data.
                        if hasattr(spin, 'intensity_err'):
                            data[graph_index][-1].append([time, spin.intensities[key], spin.intensity_err[key]])
                            err = True
                        else:
                            data[graph_index][-1].append([time, spin.intensities[key]])

                # Increment the field index.
                graph_index += 1

        # The axis labels.
        axis_labels = ['Relaxation time period (s)', 'Peak intensities']

        # Write the header.
        write_xy_header(sets=len(data[0]), file=file, set_names=set_labels, axis_labels=axis_labels, norm=norm)

        # Write the data.
        graph_type = 'xy'
        if err:
            graph_type = 'xydy'
        write_xy_data(data, file=file, graph_type=graph_type, norm=norm)

        # Close the file.
        file.close()

        # Add the file to the results file list.
        add_result_file(type='grace', label='Grace', file=file_path)


    def _relax_time(self, time=0.0, spectrum_id=None):
        """Set the relaxation time period associated with a given spectrum.

        @keyword time:          The time, in seconds, of the relaxation period.
        @type time:             float
        @keyword spectrum_id:   The spectrum identification string.
        @type spectrum_id:      str
        """

        # Test if the spectrum id exists.
        if spectrum_id not in cdp.spectrum_ids:
            raise RelaxNoSpectraError(spectrum_id)

        # Initialise the global relaxation time data structures if needed.
        if not hasattr(cdp, 'relax_times'):
            cdp.relax_times = {}
        if not hasattr(cdp, 'relax_time_list'):
            cdp.relax_time_list = []

        # Add the time, converting to a float if needed.
        cdp.relax_times[spectrum_id] = float(time)

        # The unique time points.
        if cdp.relax_times[spectrum_id] not in cdp.relax_time_list:
            cdp.relax_time_list.append(cdp.relax_times[spectrum_id])
        cdp.relax_time_list.sort()

        # Update the exponential time point count.
        cdp.num_time_pts = len(cdp.relax_time_list)

        # Printout.
        print("Setting the '%s' spectrum relaxation time period to %s s." % (spectrum_id, cdp.relax_times[spectrum_id]))


    def _select_model(self, model='R2eff'):
        """Set up the model for the relaxation dispersion analysis.

        @keyword model: The relaxation dispersion analysis type.  This can be one of 'R2eff', 'fast 2-site', 'slow 2-site'.
        @type model:    str
        """

        # Test if the current pipe exists.
        pipes.test()

        # Test if the pipe type is set to 'relax_disp'.
        function_type = cdp.pipe_type
        if function_type != 'relax_disp':
            raise RelaxFuncSetupError(specific_setup.get_string(function_type))

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the experiment type is set.
        if not hasattr(cdp, 'exp_type'):
            raise RelaxError("The relaxation dispersion experiment type has not been set.")

        # Test for the C-modules.
        if model == 'R2eff' and cdp.exp_type in VAR_TIME_EXP and not C_module_exp_fn:
            raise RelaxError("The exponential curve-fitting C module cannot be found.")

        # Fast-exchange regime.
        if model == 'R2eff':
            print("R2eff value and error determination.")
            params = ['r2eff', 'i0']

        # Fast-exchange regime.
        elif model == 'fast 2-site':
            print("2-site fast-exchange.")
            params = ['r2', 'rex', 'kex']

        # Slow-exchange regime.
        elif model == 'slow 2-site':
            print("2-site slow-exchange.")
            params = ['r2', 'r2a', 'ka', 'dw']

        # Invalid model.
        else:
            raise RelaxError("The model '%s' is invalid." % model)

        # Set up the model.
        self._model_setup(model, params)


    def _spectrometer_loop(self):
        """Generator method for looping over all spectrometer field data.

        @return:    The field strength in Hz.
        @rtype:     float
        """

        # The number of spectrometer field strengths.
        field_count = 1
        fields = [None]
        if hasattr(cdp, 'frq'):
            field_count = count_unique_elements(cdp.frq.values())
            fields = unique_elements(cdp.frq.values())
            fields.sort()

        # Yield each unique spectrometer field strength.
        for field in fields:
            yield field


    def _spin_lock_field(self, spectrum_id=None, field=None):
        """Set the spin-lock field strength (nu1) for the given spectrum.

        @keyword spectrum_id:   The spectrum ID string.
        @type spectrum_id:      str
        @keyword field:         The spin-lock field strength (nu1) in Hz.
        @type field:            int or float
        """

        # Test if the spectrum ID exists.
        if spectrum_id not in cdp.spectrum_ids:
            raise RelaxNoSpectraError(spectrum_id)

        # Initialise the global nu1 data structures if needed.
        if not hasattr(cdp, 'spin_lock_nu1'):
            cdp.spin_lock_nu1 = {}
        if not hasattr(cdp, 'spin_lock_nu1_list'):
            cdp.spin_lock_nu1_list = []

        # Add the frequency, converting to a float if needed.
        cdp.spin_lock_nu1[spectrum_id] = float(field)

        # The unique curves for the R2eff fitting (R1rho).
        if cdp.spin_lock_nu1[spectrum_id] not in cdp.spin_lock_nu1_list:
            cdp.spin_lock_nu1_list.append(cdp.spin_lock_nu1[spectrum_id])
        cdp.spin_lock_nu1_list.sort()

        # Update the exponential curve count.
        cdp.dispersion_points = len(cdp.spin_lock_nu1_list)

        # Printout.
        print("Setting the '%s' spectrum spin-lock field strength to %s kHz." % (spectrum_id, cdp.spin_lock_nu1[spectrum_id]/1000.0))


    def base_data_loop(self):
        """Custom generator method for looping over spins and exponential curves.

        The base data is hereby identified as the peak intensity data defining a single exponential curve.


        @return:    The tuple of the spin container and the exponential curve identifying key (the CPMG frequency or R1rho spin-lock field strength).
        @rtype:     tuple of SpinContainer instance and float
        """

        # Loop over the sequence.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip spins with no peak intensity data.
            if not hasattr(spin, 'intensities'):
                continue

            # Loop over each exponential curve.
            for exp_index, key in self._exp_curve_loop():
                yield spin, key


    def create_mc_data(self, data_id):
        """Create the Monte Carlo peak intensity data.

        @param data_id: The tuple of the spin container and the exponential curve identifying key, as yielded by the base_data_loop() generator method.
        @type data_id:  SpinContainer instance and float
        @return:        The Monte Carlo simulation data.
        @rtype:         list of floats
        """

        # Unpack the data.
        spin, key = data_id

        # The exponential curve index.
        index = self._exp_curve_index_from_key(key)

        # Back calculate the peak intensities.
        values = self._back_calc(spin=spin, index=index)

        # Return the MC data.
        return values


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

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the model has been set.
        if not hasattr(cdp, 'exp_type'):
            raise RelaxError("The relaxation dispersion experiment type has not been specified.")

        # Test if the model has been set.
        if not hasattr(cdp, 'model'):
            raise RelaxError("The relaxation dispersion model has not been specified.")

        # Test if the curve count exists.
        if not hasattr(cdp, 'dispersion_points'):
            if cdp.exp_type == 'cpmg':
                raise RelaxError("The CPMG frequencies have not been set up.")
            elif cdp.exp_type == 'r1rho':
                raise RelaxError("The spin-lock field strengths have not been set up.")

        # Initialise some empty data pipe structures so that the target function set up does not fail.
        if not hasattr(cdp, 'cpmg_frqs_list'):
            cdp.cpmg_frqs_list = []
        if not hasattr(cdp, 'spin_lock_nu1_list'):
            cdp.spin_lock_nu1_list = []

        # Special exponential curve-fitting for the 'R2eff' model.
        if cdp.model == 'R2eff':
            # Sanity checks.
            if cdp.exp_type in ['cpmg fixed']:
                raise RelaxError("The R2eff model with the fixed time period CPMG experiment cannot be optimised.")

            # Optimisation.
            self._minimise_r2eff(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, verbosity=verbosity, sim_index=sim_index, lower=lower, upper=upper, inc=inc)

            # Exit the method.
            return

        # The number of spectrometer field strengths.
        field_count = 1
        fields = []
        if hasattr(cdp, 'frq'):
            field_count = count_unique_elements(cdp.frq.values())
            fields = unique_elements(cdp.frq.values())
            fields.sort()

        # The number of time points for the exponential curves (if present).
        num_time_pts = 1
        if hasattr(cdp, 'num_time_pts'):
            num_time_pts = cdp.num_time_pts

        # Loop over the spin blocks.
        for spins, spin_ids in self.model_loop():
            # The spin count.
            spin_num = len(spins)

            # Initialise the data structures for the target function.
            values = zeros((spin_num, field_count, cdp.dispersion_points, num_time_pts), float64)
            errors = zeros((spin_num, field_count, cdp.dispersion_points, num_time_pts), float64)

            # Pack the peak intensity data.
            for spin_index in range(spin_num):
                # Alias the spin.
                spin = spins[spin_index]

                # The keys.
                keys = list(spin.intensities.keys())

                # Loop over the spectral data.
                for key in keys:
                    # The indices.
                    disp_pt_index = 0
                    if cdp.exp_type == 'cpmg':
                        disp_pt_index = cdp.cpmg_frqs_list.index(cdp.cpmg_frqs[key])
                    elif cdp.exp_type == 'r1rho':
                        disp_pt_index = cdp.spin_lock_nu1_list.index(cdp.spin_lock_nu1[key])
                    time_index = 0
                    if hasattr(cdp, 'relax_time_list'):
                        time_index = cdp.relax_time_list.index(cdp.relax_times[key])
                    field_index = 0
                    if hasattr(cdp, 'frqs'):
                        field_index = fields.index(cdp.frqs[keys])

                    # The values.
                    if sim_index == None:
                        values[spin_index, field_index, disp_pt_index, time_index] = spin.intensities[key]
                    else:
                        values[spin_index, field_index, disp_pt_index, time_index] = spin.intensity_sim[key][sim_index]

                    # The errors.
                    errors[spin_index, field_index, disp_pt_index, time_index] = spin.intensity_err[key]


            # Create the initial parameter vector.
            param_vector = self._assemble_param_vector(spins=spins)

            # Diagonal scaling.
            scaling_matrix = self._assemble_scaling_matrix(spins=spins, scaling=scaling)
            if len(scaling_matrix):
                param_vector = dot(inv(scaling_matrix), param_vector)

            # Get the grid search minimisation options.
            lower_new, upper_new = None, None
            if match('^[Gg]rid', min_algor):
                grid_size, inc_new, lower_new, upper_new, sparseness = self._grid_search_setup(spins=spins, param_vector=param_vector, lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix)

            # Linear constraints.
            A, b = None, None
            if constraints:
                A, b = self._linear_constraints(spins=spins, scaling_matrix=scaling_matrix)

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
            model = Dispersion(model=cdp.model, num_params=self._param_num(spins=spins), num_spins=spin_num, num_exp_curves=cdp.dispersion_points, num_times=cdp.num_time_pts, values=values, errors=errors, cpmg_frqs=cdp.cpmg_frqs_list, spin_lock_nu1=cdp.spin_lock_nu1_list, relax_times=cdp.relax_time_list, scaling_matrix=scaling_matrix)

            # Grid search.
            if search('^[Gg]rid', min_algor):
                results = grid(func=model.func, args=(), num_incs=inc_new, lower=lower_new, upper=upper_new, A=A, b=b, sparseness=sparseness, verbosity=verbosity)

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
            self._disassemble_param_vector(param_vector=param_vector, spins=spins, sim_index=sim_index)

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


    def model_loop(self):
        """Loop over the spin groupings for one model applied to multiple spins.

        @return:    The list of spins per block will be yielded, as well as the list of spin IDs.
        @rtype:     tuple of list of SpinContainer instances and list of spin IDs
        """

        # No clustering, so loop over the sequence.
        if not hasattr(cdp, 'clustering'):
            for spin, spin_id in spin_loop(return_id=True):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Return the spin container as a stop-gap measure.
                yield [spin], [spin_id]

        # Loop over the clustering.
        else:
            # The clusters.
            for key in cdp.clustering.keys():
                # Skip the free spins.
                if key == 'free spins':
                    continue

                # Create the spin container and ID lists.
                spin_list = []
                spin_id_list = []
                for spin_id in cdp.clustering[key]:
                    spin_list.append(return_spin(spin_id))
                    spin_id_list.append(spin_id)

                # Yield the cluster.
                yield spin_list, spin_id_list

            # The free spins.
            for spin_id in cdp.clustering['free spins']:
                # Get the spin container.
                spin = return_spin(spin_id)

                # Yield each spin individually.
                yield [spin], [spin_id]


    def overfit_deselect(self, data_check=True, verbose=True):
        """Deselect spins which have insufficient data to support minimisation.

        @keyword data_check:    A flag to signal if the presence of base data is to be checked for.
        @type data_check:       bool
        @keyword verbose:       A flag which if True will allow printouts.
        @type verbose:          bool
        """

        # Test the sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

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
    _table.add_row(["Transversal relaxation rate", "'r2'"])
    _table.add_row(["Chemical exchange contribution to 'R2'", "'rex'"])
    _table.add_row(["Exchange rate", "'kex'"])
    _table.add_row(["Transversal relaxation rate for state A", "'r2a'"])
    _table.add_row(["Exchange rate from state A to state B", "'ka'"])
    _table.add_row(["Chemical shift difference between states A and B", "'dw'"])
    _table.add_row(["Peak intensities (series)", "'intensities'"])
    _table.add_row(["CPMG pulse train frequency (series)", "'cpmg_frqs'"])
    return_data_name_doc.add_table(_table.label)


    def return_error(self, data_id=None):
        """Return the standard deviation data structure.

        @param data_id: The tuple of the spin container and the exponential curve identifying key, as yielded by the base_data_loop() generator method.
        @type data_id:  SpinContainer instance and float
        @return:        The standard deviation data structure.
        @rtype:         list of float
        """

        # Unpack the data.
        spin, key = data_id

        # Generate the data structure to return.
        errors = []
        for time in cdp.relax_time_list:
            # Get the intensity key.
            int_key = self._intensity_key(exp_key=key, relax_time=time)

            # Add the data.
            errors.append(spin.intensity_err[int_key])

        # Return the error list.
        return errors


    set_doc = Desc_container("Relaxation dispersion curve fitting set details")
    set_doc.add_paragraph("Only three parameters can be set for either the slow- or the fast-exchange regime. For the slow-exchange regime, these parameters include the transversal relaxation rate for state A (R2A), the exchange rate from state A to state (kA) and the chemical shift difference between states A and B (dw). For the fast-exchange regime, these include the transversal relaxation rate (R2), the chemical exchange contribution to R2 (Rex) and the exchange rate (kex). Setting parameters for a non selected model has no effect.")


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
        spins, spin_ids = model_info

        # Convert the parameter index.
        param_name, spin_index = self._param_index_to_param_info(index=index, spins=spins)

        # The parameter error name.
        err_name = param_name + "_err"

        # The exponential curve parameters.
        if param_name in ['r2eff', 'i0']:
            # Initialise if needed.
            if not hasattr(spins[spin_index], err_name):
                setattr(spins[spin_index], err_name, {})

            # Set the value.
            setattr(spins[spin_index], err_name, error)

        # All other parameters.
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
        spins, spin_ids = model_info

        # Loop over the spins, storing the structure for each spin.
        for spin in spins:
            spin.select_sim = deepcopy(select_sim)


    def sim_pack_data(self, data_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param data_id:     The tuple of the spin container and the exponential curve identifying key, as yielded by the base_data_loop() generator method.
        @type data_id:      SpinContainer instance and float
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # Unpack the data.
        spin, key = data_id

        # Initialise the data structure if needed.
        if not hasattr(spin, 'intensity_sim'):
            spin.intensity_sim = {}

        # Loop over each time point.
        for time_index in range(cdp.num_time_pts):
            # Get the intensity key.
            int_key = self._intensity_key(exp_key=key, relax_time=cdp.relax_time_list[time_index])

            # Test if the simulation data point already exists.
            if int_key in spin.intensity_sim:
                raise RelaxError("Monte Carlo simulation data for the key '%s' already exists." % int_key)

            # Initialise the list.
            spin.intensity_sim[int_key] = []

            # Loop over the simulations, appending the corresponding data.
            for i in range(cdp.sim_number):
                spin.intensity_sim[int_key].append(sim_data[i][time_index])


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
        spins, spin_ids = model_info

        # The number of parameters.
        total_param_num = self._param_num(spins=spins)

        # No more parameters.
        if index >= total_param_num:
            return

        # Convert the parameter index.
        param_name, spin_index = self._param_index_to_param_info(index=index, spins=spins)

        # The exponential curve parameters.
        sim_data = []
        if param_name == 'r2eff':
            for i in range(cdp.sim_number):
                sim_data.append(spins[spin_index].r2eff_sim[i])
        elif param_name == 'i0':
            for i in range(cdp.sim_number):
                sim_data.append(spins[spin_index].i0_sim[i])

        # All other parameters.
        else:
            sim_data = getattr(spins[0], param_name + "_sim")

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
        spins, spin_ids = model_info

        # Return the array from the first spin, as this array will be identical for all spins in the cluster.
        return spins[0].select_sim
