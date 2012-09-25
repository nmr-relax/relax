###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
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

# Python module imports.
from re import search
from warnings import warn

# relax module imports.
from api_base import API_base
from api_common import API_common
from generic_fns.interatomic import return_interatom_list
from generic_fns.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from generic_fns import pipes
from maths_fns.jw_mapping import Mapping
from physical_constants import N15_CSA, NH_BOND_LENGTH, h_bar, mu0, return_gyromagnetic_ratio
from relax_errors import RelaxError, RelaxFuncSetupError, RelaxNoSequenceError, RelaxNoValueError, RelaxSpinTypeError
from relax_warnings import RelaxDeselectWarning
import specific_fns
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container


class Jw_mapping(API_base, API_common):
    """Class containing functions specific to reduced spectral density mapping."""

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Execute the base class __init__ method.
        super(Jw_mapping, self).__init__()

        # Place methods into the API.
        self.base_data_loop = self._base_data_loop_spin
        self.create_mc_data = self._create_mc_relax_data
        self.model_loop = self._model_loop_spin
        self.return_conversion_factor = self._return_no_conversion_factor
        self.return_error = self._return_error_relax_data
        self.return_value = self._return_value_general
        self.set_param_values = self._set_param_values_spin
        self.set_selected_sim = self._set_selected_sim_spin
        self.sim_pack_data = self._sim_pack_relax_data

        # Set up the spin parameters.
        self.PARAMS.add('j0', scope='spin', string='J(0)', desc='Spectral density value at 0 MHz', py_type=float, set='params', grace_string='\\qJ(0)\\Q', err=True, sim=True)
        self.PARAMS.add('jwx', scope='spin', string='J(wX)', desc='Spectral density value at the frequency of the heteronucleus', py_type=float, set='params', grace_string='\\qJ(\\xw\\f{}\\sX\\N)\\Q', err=True, sim=True)
        self.PARAMS.add('jwh', scope='spin', string='J(wH)', desc='Spectral density value at the frequency of the proton', py_type=float, set='params', grace_string='\\qJ(\\xw\\f{}\\sH\\N)\\Q', err=True, sim=True)
        self.PARAMS.add('csa', scope='spin', default=N15_CSA, units='ppm', desc='CSA value', py_type=float, grace_string='\\qCSA\\Q')


    def _set_frq(self, frq=None):
        """Function for selecting which relaxation data to use in the J(w) mapping."""

        # Test if the current pipe exists.
        pipes.test()

        # Test if the pipe type is set to 'jw'.
        function_type = cdp.pipe_type
        if function_type != 'jw':
            raise RelaxFuncSetupError(specific_fns.setup.get_string(function_type))

        # Test if the frequency has been set.
        if hasattr(cdp, 'jw_frq'):
            raise RelaxError("The frequency has already been set.")

        # Create the data structure if it doesn't exist.
        if not hasattr(cdp, 'jw_frq'):
            cdp.jw_frq = {}

        # Set the frequency.
        cdp.jw_frq = frq


    def calculate(self, spin_id=None, verbosity=1, sim_index=None):
        """Calculation of the spectral density values.

        @keyword spin_id:   The spin identification string.
        @type spin_id:      None or str
        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        @keyword sim_index: The optional MC simulation index.
        @type sim_index:    None or int
        """

        # Test if the frequency has been set.
        if not hasattr(cdp, 'jw_frq') or not isinstance(cdp.jw_frq, float):
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
        if cdp.jw_frq not in cdp.frq.values():
            raise RelaxError("No relaxation data corresponding to the frequency " + repr(cdp.jw_frq) + " has been loaded.")

        # Reduced spectral density mapping.
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
                if cdp.frq[ri_id] != cdp.jw_frq:
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
                gx = return_gyromagnetic_ratio(spin.isotope)
                gh = return_gyromagnetic_ratio(spin2.isotope)

                # The interatomic distance.
                r = interatoms[i].r

            # Initialise the function to calculate.
            self.jw = Mapping(frq=cdp.jw_frq, gx=gx, gh=gh, mu0=mu0, h_bar=h_bar)

            # Calculate the spectral density values.
            j0, jwx, jwh = self.jw.func(r=r, csa=spin.csa, r1=r1, r2=r2, noe=noe)

            # Reduced spectral density values.
            if sim_index == None:
                spin.j0 = j0
                spin.jwx = jwx
                spin.jwh = jwh

            # Monte Carlo simulated reduced spectral density values.
            else:
                # Initialise the simulation data structures.
                self.data_init(spin, sim=1)
                if spin.j0_sim == None:
                    spin.j0_sim = []
                    spin.jwx_sim = []
                    spin.jwh_sim = []

                # Reduced spectral density values.
                spin.j0_sim.append(j0)
                spin.jwx_sim.append(jwx)
                spin.jwh_sim.append(jwh)


    def data_init(self, data_cont, sim=False):
        """Initialise the data structures.

        @param data_cont:   The data container.
        @type data_cont:    instance
        @keyword sim:       The Monte Carlo simulation flag, which if true will initialise the simulation data structure.
        @type sim:          bool
        """

        # Get the data names.
        data_names = self.data_names()

        # Loop over the data structure names.
        for name in data_names:
            # Simulation data structures.
            if sim:
                # Add '_sim' to the names.
                name = name + '_sim'

            # If the name is not in 'data_cont', add it.
            if not hasattr(data_cont, name):
                # Set the attribute.
                setattr(data_cont, name, None)


    default_value_doc = Desc_container("Reduced spectral density mapping default values")
    default_value_doc.add_paragraph("These default values are found in the file 'physical_constants.py'.")
    _table = uf_tables.add_table(label="table: J(w) default values", caption="Reduced spectral density mapping default values.")
    _table.add_headings(["Data type", "Object name", "Value"])
    _table.add_row(["CSA", "'csa'", "-172 * 1e-6"])
    default_value_doc.add_table(_table.label)


    def overfit_deselect(self, data_check=True, verbose=True):
        """Deselect spins which _have insufficient data to support calculation.

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
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Check if data exists.
            if not hasattr(spin, 'ri_data'):
                warn(RelaxDeselectWarning(spin_id, 'missing relaxation data'))
                spin.select = False
                deselect_flag = True
                continue

            # Require 3 or more data points.
            else:
                # Count the points.
                data_points = 0
                for id in cdp.ri_ids:
                    if spin.ri_data.has_key(id) and spin.ri_data[id] != None:
                        data_points += 1

                # Not enough.
                if data_points < 3:
                    warn(RelaxDeselectWarning(spin_id, 'insufficient relaxation data, 3 or more data points are required'))
                    spin.select = False
                    deselect_flag = True
                    continue

        # Final printout.
        if verbose and not deselect_flag:
            print("No spins have been deselected.")


    return_data_name_doc = Desc_container("Reduced spectral density mapping data type string matching patterns")
    _table = uf_tables.add_table(label="table: J(w) data types", caption="Reduced spectral density mapping data type string matching patterns.")
    _table.add_headings(["Data type", "Object name"])
    _table.add_row(["J(0)", "'j0'"])
    _table.add_row(["J(wX)", "'jwx'"])
    _table.add_row(["J(wH)", "'jwh'"])
    _table.add_row(["CSA", "'csa'"])
    return_data_name_doc.add_table(_table.label)


    set_doc = Desc_container("Reduced spectral density mapping set details")
    set_doc.add_paragraph("In reduced spectral density mapping, three values must be set prior to the calculation of spectral density values:  the bond length, CSA, and heteronucleus type.")


    def set_error(self, model_info, index, error):
        """Set the parameter errors.

        @param model_info:  The spin container originating from model_loop().
        @type model_info:   SpinContainer instance
        @param index:       The index of the parameter to set the errors for.
        @type index:        int
        @param error:       The error value.
        @type error:        float
        """

        # Alias.
        spin = model_info

        # Return J(0) sim data.
        if index == 0:
            spin.j0_err = error

        # Return J(wX) sim data.
        if index == 1:
            spin.jwx_err = error

        # Return J(wH) sim data.
        if index == 2:
            spin.jwh_err = error


    def sim_return_param(self, model_info, index):
        """Return the array of simulation parameter values.

        @param model_info:  The spin container originating from model_loop().
        @type model_info:   SpinContainer instance
        @param index:       The index of the parameter to return the array of values for.
        @type index:        int
        @return:            The array of simulation parameter values.
        @rtype:             list of float
        """

        # Alias.
        spin = model_info

        # Skip deselected spins.
        if not spin.select:
            return

        # Return J(0) sim data.
        if index == 0:
            return spin.j0_sim

        # Return J(wX) sim data.
        if index == 1:
            return spin.jwx_sim

        # Return J(wH) sim data.
        if index == 2:
            return spin.jwh_sim


    def sim_return_selected(self, model_info):
        """Return the array of selected simulation flags.

        @param model_info:  The spin container originating from model_loop().
        @type model_info:   SpinContainer instance
        @return:            The array of selected simulation flags.
        @rtype:             list of int
        """

        # Alias.
        spin = model_info

        # Multiple spins.
        return spin.select_sim
