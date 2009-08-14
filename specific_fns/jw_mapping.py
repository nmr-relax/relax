###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
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

# relax module imports.
from base_class import Common_functions
from generic_fns.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from generic_fns import pipes
from maths_fns.jw_mapping import Mapping
from physical_constants import N15_CSA, NH_BOND_LENGTH, h_bar, mu0, return_gyromagnetic_ratio
from relax_errors import RelaxError, RelaxFuncSetupError, RelaxNoSequenceError, RelaxNoValueError, RelaxProtonTypeError, RelaxSpinTypeError


class Jw_mapping(Common_functions):
    def __init__(self):
        """Class containing functions specific to reduced spectral density mapping."""


    def calculate(self, verbosity=1, sim_index=None, spin_id=None):
        """Calculation of the spectral density values."""

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the frequency has been set.
        if not hasattr(cdp, 'jw_frq') or type(cdp.jw_frq) != float:
            raise RelaxError, "The frequency has not been set up."

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the CSA and bond length values have been set.
        for spin in spin_loop(spin_id):
            # Skip deselected residues.
            if not spin.select:
                continue

            # Test if the CSA value has been set.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError, "CSA"

            # Test if the bond length has been set.
            if not hasattr(spin, 'r') or spin.r == None:
                raise RelaxNoValueError, "bond length"

            # Test if the spin type has been set.
            if not hasattr(spin, 'heteronuc_type'):
                raise RelaxSpinTypeError

            # Test if the type attached proton has been set.
            if not hasattr(spin, 'proton_type'):
                raise RelaxProtonTypeError

        # Frequency index.
        if cdp.jw_frq not in cdp.frq:
            raise RelaxError, "No relaxation data corresponding to the frequency " + `cdp.jw_frq` + " has been loaded."

        # Reduced spectral density mapping.
        for spin in spin_loop(spin_id):

            # Skip deselected residues.
            if not spin.select:
                continue

            # Residue specific frequency index.
            frq_index = None
            for j in xrange(spin.num_frq):
                if spin.frq[j] == cdp.jw_frq:
                    frq_index = j
            if frq_index == None:
                continue

            # Set the r1, r2, and NOE to None.
            r1 = None
            r2 = None
            noe = None

            # Get the R1, R2, and NOE values corresponding to the set frequency.
            for j in xrange(spin.num_ri):
                # R1.
                if spin.remap_table[j] == frq_index and spin.ri_labels[j] == 'R1':
                    if sim_index == None:
                        r1 = spin.relax_data[j]
                    else:
                        r1 = spin.relax_sim_data[sim_index][j]

                # R2.
                if spin.remap_table[j] == frq_index and spin.ri_labels[j] == 'R2':
                    if sim_index == None:
                        r2 = spin.relax_data[j]
                    else:
                        r2 = spin.relax_sim_data[sim_index][j]

                # NOE.
                if spin.remap_table[j] == frq_index and spin.ri_labels[j] == 'NOE':
                    if sim_index == None:
                        noe = spin.relax_data[j]
                    else:
                        noe = spin.relax_sim_data[sim_index][j]

            # Skip the residue if not all of the three value exist.
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


    def create_mc_data(self, spin_id):
        """Return the Ri data structure for the corresponding spin.

        @param spin_id: The spin identification string, as yielded by the base_data_loop() generator
                        method.
        @type spin_id:  str
        @return:        The Monte Carlo simulation data.
        @rtype:         list of floats
        """

        # Get the spin container.
        spin = return_spin(spin_id)

        # Return the data.
        return spin.relax_data


    def data_init(self, data, sim=0):
        """Function for initialising the data structures."""

        # Get the data names.
        data_names = self.data_names()

        # Loop over the data structure names.
        for name in data_names:
            # Simulation data structures.
            if sim:
                # Add '_sim' to the names.
                name = name + '_sim'

            # If the name is not in 'data', add it.
            if not hasattr(data, name):
                # Set the attribute.
                setattr(data, name, None)


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

        # Test the sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over spin data.
        for spin in spin_loop():
            # Check if data exists.
            if not hasattr(spin, 'relax_data'):
                spin.select = False
                continue

            # Require 3 or more data points.
            if len(spin.relax_data) < 3:
                spin.select = False
                continue


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

    def return_data_name(self, name):
        """Return a unique identifying string for the J(w) mapping parameter.

        @param name:    The J(w) mapping parameter.
        @type name:     str
        @return:        The unique parameter identifying string.
        @rtype:         str
        """

        # J(0).
        if search('^[Jj]0$', name) or search('[Jj]\(0\)', name):
            return 'j0'

        # J(wX).
        if search('^[Jj]w[Xx]$', name) or search('[Jj]\(w[Xx]\)', name):
            return 'jwx'

        # J(wH).
        if search('^[Jj]w[Hh]$', name) or search('[Jj]\(w[Hh]\)', name):
            return 'jwh'

        # Bond length.
        if search('^r$', name) or search('[Bb]ond[ -_][Ll]ength', name):
            return 'r'

        # CSA.
        if search('^[Cc][Ss][Aa]$', name):
            return 'csa'

        # Heteronucleus type.
        if search('^[Hh]eteronucleus$', name):
            return 'heteronuc_type'

        # Proton type.
        if search('^[Pp]roton$', name):
            return 'proton_type'


    def return_grace_string(self, data_type):
        """Function for returning the Grace string representing the data type for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(data_type)

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


    def return_units(self, data_type, spin=None, spin_id=None):
        """Function for returning a string representing the parameters units.

        For example, the internal representation of te is in seconds, whereas the external
        representation is in picoseconds, therefore this function will return the string
        'picoseconds' for te.

        @param data_type:   The name of the parameter to return the units string for.
        @type data_type:    str
        @param spin:        The spin container.
        @type spin:         SpinContainer instance
        @param spin_id:     The spin identification string (ignored if the spin container is
                            supplied).
        @type spin_id:      str
        @return:            The string representation of the units.
        @rtype:             str
        """

        # Get the object name.
        object_name = self.return_data_name(data_type)

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


    def set_frq(self, frq=None):
        """Function for selecting which relaxation data to use in the J(w) mapping."""

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the current pipe exists.
        pipes.test()

        # Test if the pipe type is set to 'jw'.
        function_type = cdp.pipe_type
        if function_type != 'jw':
            raise RelaxFuncSetupError, specific_fns.setup.get_string(function_type)

        # Test if the frequency has been set.
        if hasattr(cdp, 'jw_frq'):
            raise RelaxError, "The frequency has already been set."

        # Create the data structure if it doesn't exist.
        if not hasattr(cdp, 'jw_frq'):
           cdp.jw_frq = {}

        # Set the frequency.
        cdp.jw_frq = frq


    def set_error(self, spin, index, error):
        """Function for setting parameter errors."""

        # Return J(0) sim data.
        if index == 0:
            spin.j0_err = error

        # Return J(wX) sim data.
        if index == 1:
            spin.jwx_err = error

        # Return J(wH) sim data.
        if index == 2:
            spin.jwh_err = error


    def sim_return_param(self, spin, index):
        """Function for returning the array of simulation parameter values."""

        # Skip deselected residues.
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


    def sim_return_selected(self, spin):
        """Function for returning the array of selected simulation flags."""

        # Multiple spins.
        return spin.select_sim


    def sim_pack_data(self, spin_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param spin_id:     The spin identification string, as yielded by the base_data_loop()
                            generator method.
        @type spin_id:      str
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # Get the spin container.
        spin = return_spin(spin_id)

        # Test if the simulation data already exists.
        if hasattr(spin, 'relax_sim_data'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        spin.relax_sim_data = sim_data
