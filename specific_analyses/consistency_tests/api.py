###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
# Copyright (C) 2007-2009 Sebastien Morin                                     #
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
"""The consistency testing analysis API object."""

# Python module imports.
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxNoSequenceError, RelaxNoValueError, RelaxSpinTypeError
from lib.float import isInf
from lib.periodic_table import periodic_table
from lib.physical_constants import h_bar, mu0
from lib.warnings import RelaxDeselectWarning
from pipe_control.interatomic import return_interatom_list
from pipe_control.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from specific_analyses.api_base import API_base
from specific_analyses.api_common import API_common
from specific_analyses.consistency_tests.parameter_object import Consistency_tests_params
from target_functions.consistency_tests import Consistency


class Consistency_tests(API_base, API_common):
    """Class containing functions specific to consistency testing."""

    # Class variable for storing the class instance (for the singleton design pattern).
    instance = None

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Place methods into the API.
        self.base_data_loop = self._base_data_loop_spin
        self.create_mc_data = self._create_mc_relax_data
        self.model_loop = self._model_loop_spin
        self.print_model_title = self._print_model_title_spin
        self.return_conversion_factor = self._return_no_conversion_factor
        self.return_error = self._return_error_relax_data
        self.return_value = self._return_value_general
        self.set_param_values = self._set_param_values_spin
        self.set_selected_sim = self._set_selected_sim_spin
        self.sim_pack_data = self._sim_pack_relax_data

        # Place a copy of the parameter list object in the instance namespace.
        self._PARAMS = Consistency_tests_params()


    def calculate(self, spin_id=None, scaling_matrix=None, verbosity=1, sim_index=None):
        """Calculation of the consistency functions.

        @keyword spin_id:           The spin identification string.
        @type spin_id:              None or str
        @keyword scaling_matrix:    The per-model list of diagonal and square scaling matrices.
        @type scaling_matrix:       list of numpy rank-2, float64 array or list of None
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The optional MC simulation index.
        @type sim_index:            None or int
        """

        # Test if the frequency has been set.
        if not hasattr(cdp, 'ct_frq') or not isinstance(cdp.ct_frq, float):
            raise RelaxError("The frequency has not been set up.")

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the spin data has been set.
        for spin, id in spin_loop(spin_id, return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Test if the nuclear isotope type has been set.
            if not hasattr(spin, 'isotope'):
                raise RelaxSpinTypeError

            # Test if the CSA value has been set.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError("CSA")

            # Test if the angle Theta has been set.
            if not hasattr(spin, 'orientation') or spin.orientation == None:
                raise RelaxNoValueError("angle Theta")

            # Test if the correlation time has been set.
            if not hasattr(spin, 'tc') or spin.tc == None:
                raise RelaxNoValueError("correlation time")

            # Test the interatomic data.
            interatoms = return_interatom_list(id)
            for interatom in interatoms:
                # No relaxation mechanism.
                if not interatom.dipole_pair:
                    continue

                # The interacting spin.
                if id != interatom.spin_id1:
                    spin_id2 = interatom.spin_id1
                else:
                    spin_id2 = interatom.spin_id2
                spin2 = return_spin(spin_id2)

                # Test if the nuclear isotope type has been set.
                if not hasattr(spin2, 'isotope'):
                    raise RelaxSpinTypeError

                # Test if the interatomic distance has been set.
                if not hasattr(interatom, 'r') or interatom.r == None:
                    raise RelaxNoValueError("interatomic distance", spin_id=spin_id, spin_id2=spin_id2)

        # Frequency index.
        if cdp.ct_frq not in cdp.spectrometer_frq.values():
            raise RelaxError("No relaxation data corresponding to the frequency %s has been loaded." % cdp.ct_frq)

        # Consistency testing.
        for spin, id in spin_loop(spin_id, return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Set the r1, r2, and NOE to None.
            r1 = None
            r2 = None
            noe = None

            # Get the R1, R2, and NOE values corresponding to the set frequency.
            for ri_id in cdp.ri_ids:
                # The frequency does not match.
                if cdp.spectrometer_frq[ri_id] != cdp.ct_frq:
                    continue

                # R1.
                if cdp.ri_type[ri_id] == 'R1':
                    if sim_index == None:
                        r1 = spin.ri_data[ri_id]
                    else:
                        r1 = spin.ri_data_sim[ri_id][sim_index]

                # R2.
                if cdp.ri_type[ri_id] == 'R2':
                    if sim_index == None:
                        r2 = spin.ri_data[ri_id]
                    else:
                        r2 = spin.ri_data_sim[ri_id][sim_index]

                # NOE.
                if cdp.ri_type[ri_id] == 'NOE':
                    if sim_index == None:
                        noe = spin.ri_data[ri_id]
                    else:
                        noe = spin.ri_data_sim[ri_id][sim_index]

            # Skip the spin if not all of the three value exist.
            if r1 == None or r2 == None or noe == None:
                continue

            # Loop over the interatomic data.
            interatoms = return_interatom_list(id)
            for i in range(len(interatoms)):
                # No relaxation mechanism.
                if not interatoms[i].dipole_pair:
                    continue

                # The surrounding spins.
                if id != interatoms[i].spin_id1:
                    spin_id2 = interatoms[i].spin_id1
                else:
                    spin_id2 = interatoms[i].spin_id2
                spin2 = return_spin(spin_id2)

                # Gyromagnetic ratios.
                gx = periodic_table.gyromagnetic_ratio(spin.isotope)
                gh = periodic_table.gyromagnetic_ratio(spin2.isotope)

                # The interatomic distance.
                r = interatoms[i].r

            # Initialise the function to calculate.
            ct = Consistency(frq=cdp.ct_frq, gx=gx, gh=gh, mu0=mu0, h_bar=h_bar)

            # Calculate the consistency tests values.
            j0, f_eta, f_r2 = ct.func(orientation=spin.orientation, tc=spin.tc, r=r, csa=spin.csa, r1=r1, r2=r2, noe=noe)

            # Consistency tests values.
            if sim_index == None:
                spin.j0 = j0
                spin.f_eta = f_eta
                spin.f_r2 = f_r2

            # Monte Carlo simulated consistency tests values.
            else:
                # Initialise the simulation data structures.
                self.data_init(id, sim=1)
                if spin.j0_sim == None:
                    spin.j0_sim = []
                    spin.f_eta_sim = []
                    spin.f_r2_sim = []

                # Consistency tests values.
                spin.j0_sim.append(j0)
                spin.f_eta_sim.append(f_eta)
                spin.f_r2_sim.append(f_r2)


    def data_init(self, data, sim=False):
        """Initialise the data structures.

        @param data:    The spin ID string from the _base_data_loop_spin() method.
        @type data:     str
        @keyword sim:   The Monte Carlo simulation flag, which if true will initialise the simulation data structure.
        @type sim:      bool
        """

        # Get the spin container.
        spin = return_spin(data)

        # Get the data names.
        data_names = self.data_names()

        # Loop over the data structure names.
        for name in data_names:
            # Simulation data structures.
            if sim:
                # Add '_sim' to the names.
                name = name + '_sim'

            # If the name is not in the spin container, add it.
            if not hasattr(spin, name):
                # Set the attribute.
                setattr(spin, name, None)


    def get_param_names(self, model_info=None):
        """Return a vector of parameter names.

        @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() method.
        @type model_info:       SpinContainer instance, str
        @return:                The vector of parameter names.
        @rtype:                 list of str
        """

        # Return the fixed list.
        return ['j0', 'f_eta', 'f_r2']


    def overfit_deselect(self, data_check=True, verbose=True):
        """Deselect spins which have insufficient data to support calculation.

        @keyword data_check:    A flag to signal if the presence of base data is to be checked for.
        @type data_check:       bool
        @keyword verbose:       A flag which if True will allow printouts.
        @type verbose:          bool
        """

        # Print out.
        if verbose:
            print("\nOver-fit spin deselection:")

        # Test the sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over spin data.
        deselect_flag = False
        spin_count = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # The interatomic data.
            interatoms = return_interatom_list(spin_id)

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
                if data_points < 3:
                    warn(RelaxDeselectWarning(spin_id, 'insufficient relaxation data, 3 or more data points are required'))
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


    def set_error(self, index, error, model_info=None):
        """Set the parameter errors.

        @param index:           The index of the parameter to set the errors for.
        @type index:            int
        @param error:           The error value.
        @type error:            float
        @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() method.
        @type model_info:       SpinContainer instance, str
        """

        # Unpack the data.
        spin, spin_id = model_info

        # Return J(0) sim data.
        if index == 0:
            spin.j0_err = error

        # Return F_eta sim data.
        if index == 1:
            spin.f_eta_err = error

        # Return F_R2 sim data.
        if index == 2:
            spin.f_r2_err = error


    def sim_return_param(self, index, model_info=None):
        """Return the array of simulation parameter values.

        @param index:           The index of the parameter to return the array of values for.
        @type index:            int
        @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() method.
        @type model_info:       SpinContainer instance, str
        @return:                The array of simulation parameter values.
        @rtype:                 list of float
        """

        # Unpack the data.
        spin, spin_id = model_info

        # Skip deselected spins.
        if not spin.select:
                return

        # Return J(0) sim data.
        if index == 0:
            return spin.j0_sim

        # Return F_eta sim data.
        if index == 1:
            return spin.f_eta_sim

        # Return F_R2 sim data.
        if index == 2:
            return spin.f_r2_sim


    def sim_return_selected(self, model_info=None):
        """Return the array of selected simulation flags.

        @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() method.
        @type model_info:       SpinContainer instance, str
        @return:                The array of selected simulation flags.
        @rtype:                 list of int
        """

        # Unpack the data.
        spin, spin_id = model_info

        # Multiple spins.
        return spin.select_sim
