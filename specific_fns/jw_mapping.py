###############################################################################
#                                                                             #
# Copyright (C) 2004-2011 Edward d'Auvergne                                   #
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
from re import search
from warnings import warn

# relax module imports.
from api_base import API_base
from api_common import API_common
from generic_fns.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from generic_fns import pipes
from maths_fns.jw_mapping import Mapping
from physical_constants import N15_CSA, NH_BOND_LENGTH, h_bar, mu0, return_gyromagnetic_ratio
from relax_errors import RelaxError, RelaxFuncSetupError, RelaxNoSequenceError, RelaxNoValueError, RelaxProtonTypeError, RelaxSpinTypeError
from relax_warnings import RelaxDeselectWarning


class Jw_mapping(API_base, API_common):
    """Class containing functions specific to reduced spectral density mapping."""

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

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

        # Test if the CSA and bond length values have been set.
        for spin in spin_loop(spin_id):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Test if the CSA value has been set.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError("CSA")

            # Test if the bond length has been set.
            if not hasattr(spin, 'r') or spin.r == None:
                raise RelaxNoValueError("bond length")

            # Test if the spin type has been set.
            if not hasattr(spin, 'heteronuc_type'):
                raise RelaxSpinTypeError

            # Test if the type attached proton has been set.
            if not hasattr(spin, 'proton_type'):
                raise RelaxProtonTypeError

        # Frequency index.
        if cdp.jw_frq not in cdp.frq.values():
            raise RelaxError("No relaxation data corresponding to the frequency " + repr(cdp.jw_frq) + " has been loaded.")

        # Reduced spectral density mapping.
        for spin in spin_loop(spin_id):
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

            # Initialise the function to calculate.
            self.jw = Mapping(frq=cdp.jw_frq, gx=return_gyromagnetic_ratio(spin.heteronuc_type), gh=return_gyromagnetic_ratio(spin.proton_type), mu0=mu0, h_bar=h_bar)

            # Calculate the spectral density values.
            j0, jwx, jwh = self.jw.func(r=spin.r, csa=spin.csa, r1=r1, r2=r2, noe=noe)

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


    def data_names(self, set=None, error_names=False, sim_names=False):
        """Return a list of all spin container specific J(w) mapping object names.

        Description
        ===========

        The names are as follows:

            - 'r', bond length.
            - 'csa', CSA value.
            - 'heteronuc_type', the heteronucleus type.
            - 'j0', spectral density value at 0 MHz.
            - 'jwx', spectral density value at the frequency of the heteronucleus.
            - 'jwh', spectral density value at the frequency of the heteronucleus.


        @keyword set:           An unused variable.
        @type set:              ignored
        @keyword error_names:   A flag which if True will add the error object names as well.
        @type error_names:      bool
        @keyword sim_names:     A flag which if True will add the Monte Carlo simulation object
                                names as well.
        @type sim_names:        bool
        @return:                The list of object names.
        @rtype:                 list of str
        """

        # Initialise.
        names = []

        # Values.
        names.append('r')
        names.append('csa')
        names.append('heteronuc_type')

        # Spectral density values.
        names.append('j0')
        names.append('jwx')
        names.append('jwh')

        # Return the names.
        return names


    default_value_doc = """
        Reduced spectral density mapping default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        These default values are found in the file 'physical_constants.py'.

        _______________________________________________________________________________________
        |                                       |                    |                        |
        | Data type                             | Object name        | Value                  |
        |_______________________________________|____________________|________________________|
        |                                       |                    |                        |
        | Bond length                           | 'r'                | 1.02 * 1e-10           |
        |                                       |                    |                        |
        | CSA                                   | 'csa'              | -172 * 1e-6            |
        |                                       |                    |                        |
        | Heteronucleus type                    | 'heteronuc_type'   | '15N'                  |
        |                                       |                    |                        |
        | Proton type                           | 'proton_type'      | '1H'                   |
        |_______________________________________|____________________|________________________|

        """

    def default_value(self, param):
        """The default J(w) mapping parameter values.

        @param param:   The J(w) mapping parameter.
        @type param:    str
        @return:        The default value.
        @rtype:         float
        """

        # Bond length.
        if param == 'r':
            return NH_BOND_LENGTH

        # CSA.
        elif param == 'csa':
            return N15_CSA

        # Heteronucleus type.
        elif param == 'heteronuc_type':
            return '15N'

        # Proton type.
        elif param == 'proton_type':
            return '1H'


    def overfit_deselect(self):
        """Deselect spins which have insufficient data to support calculation."""

        # Print out.
        print("\n\nOver-fit spin deselection.\n")

        # Test the sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over spin data.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Check if data exists.
            if not hasattr(spin, 'ri_data'):
                warn(RelaxDeselectWarning(spin_id, 'missing relaxation data'))
                spin.select = False

            # Require 3 or more data points.
            elif len(spin.ri_data) < 3:
                warn(RelaxDeselectWarning(spin_id, 'insufficient relaxation data, 3 or more data points are required'))
                spin.select = False


    return_data_name_doc = """
        Reduced spectral density mapping data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |                  |                                              |
        | Data type              | Object name      | Patterns                                     |
        |________________________|__________________|______________________________________________|
        |                        |                  |                                              |
        | J(0)                   | 'j0'             | '^[Jj]0$' or '[Jj]\(0\)'                     |
        |                        |                  |                                              |
        | J(wX)                  | 'jwx'            | '^[Jj]w[Xx]$' or '[Jj]\(w[Xx]\)'             |
        |                        |                  |                                              |
        | J(wH)                  | 'jwh'            | '^[Jj]w[Hh]$' or '[Jj]\(w[Hh]\)'             |
        |                        |                  |                                              |
        | Bond length            | 'r'              | '^r$' or '[Bb]ond[ -_][Ll]ength'             |
        |                        |                  |                                              |
        | CSA                    | 'csa'            | '^[Cc][Ss][Aa]$'                             |
        |                        |                  |                                              |
        | Heteronucleus type     | 'heteronuc_type' | '^[Hh]eteronucleus$'                         |
        |                        |                  |                                              |
        | Proton type            | 'proton_type'    | '^[Pp]roton$'                                |
        |________________________|__________________|______________________________________________|

        """

    def return_data_name(self, param):
        """Return a unique identifying string for the J(w) mapping parameter.

        @param param:   The J(w) mapping parameter name.
        @type param:    str
        @return:        The unique parameter identifying string.
        @rtype:         str
        """

        # J(0).
        if search('^[Jj]0$', param) or search('[Jj]\(0\)', param):
            return 'j0'

        # J(wX).
        if search('^[Jj]w[Xx]$', param) or search('[Jj]\(w[Xx]\)', param):
            return 'jwx'

        # J(wH).
        if search('^[Jj]w[Hh]$', param) or search('[Jj]\(w[Hh]\)', param):
            return 'jwh'

        # Bond length.
        if search('^r$', param) or search('[Bb]ond[ -_][Ll]ength', param):
            return 'r'

        # CSA.
        if search('^[Cc][Ss][Aa]$', param):
            return 'csa'

        # Heteronucleus type.
        if search('^[Hh]eteronucleus$', param):
            return 'heteronuc_type'

        # Proton type.
        if search('^[Pp]roton$', param):
            return 'proton_type'


    def return_grace_string(self, param):
        """Return the Grace string representing the given parameter.

        This is used for axis labelling.

        @param param:   The specific analysis parameter.
        @type param:    str
        @return:        The Grace string representation of the parameter.
        @rtype:         str
        """

        # Get the object name.
        object_name = self.return_data_name(param)

        # J(0).
        if object_name == 'j0':
            return '\\qJ(0)\\Q'

        # J(wX).
        elif object_name == 'jwx':
            return '\\qJ(\\xw\\f{}\\sX\\N)\\Q'

        # J(wH).
        elif object_name == 'jwh':
            return '\\qJ(\\xw\\f{}\\sH\\N)\\Q'

        # Bond length.
        elif object_name == 'r':
            return 'Bond length'

        # CSA.
        elif object_name == 'csa':
            return '\\qCSA\\Q'


    def return_units(self, param, spin=None, spin_id=None):
        """Function for returning a string representing the parameters units.

        For example, the internal representation of te is in seconds, whereas the external
        representation is in picoseconds, therefore this function will return the string
        'picoseconds' for te.

        @param param:   The name of the parameter to return the units string for.
        @type param:    str
        @param spin:    The spin container.
        @type spin:     SpinContainer instance
        @param spin_id: The spin identification string (ignored if the spin container is supplied).
        @type spin_id:  str
        @return:        The string representation of the units.
        @rtype:         str
        """

        # Get the object name.
        object_name = self.return_data_name(param)

        # Bond length (Angstrom).
        if object_name == 'r':
            return 'Angstrom'

        # CSA (ppm).
        elif object_name == 'csa':
            return 'ppm'


    set_doc = """
        Reduced spectral density mapping set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        In reduced spectral density mapping, three values must be set prior to the calculation of
        spectral density values:  the bond length, CSA, and heteronucleus type.
        """


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
