###############################################################################
#                                                                             #
# Copyright (C) 2007-2014 Edward d'Auvergne                                   #
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
"""The steady-state heteronuclear NOE API object."""

# Python module imports.
from math import sqrt
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxNoSequenceError
from lib.warnings import RelaxDeselectWarning
from pipe_control import pipes
from pipe_control.mol_res_spin import exists_mol_res_spin_data, spin_loop
from specific_analyses.api_base import API_base
from specific_analyses.api_common import API_common
from specific_analyses.noe.parameter_object import Noe_params


class Noe(API_base, API_common):
    """Specific analysis API class for the steady-state heternuclear NOE analysis."""

    # Class variable for storing the class instance (for the singleton design pattern).
    instance = None

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Place methods into the API.
        self.return_conversion_factor = self._return_no_conversion_factor
        self.return_value = self._return_value_general

        # Place a copy of the parameter list object in the instance namespace.
        self._PARAMS = Noe_params()


    def calculate(self, spin_id=None, verbosity=1, sim_index=None):
        """Calculate the NOE and its error.

        The error for each peak is calculated using the formula::
                          ___________________________________________
                       \/ {sd(sat)*I(unsat)}^2 + {sd(unsat)*I(sat)}^2
            sd(NOE) = -----------------------------------------------
                                          I(unsat)^2

        @keyword spin_id:   The spin identification string.
        @type spin_id:      None or str
        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        @keyword sim_index: The MC simulation index (unused).
        @type sim_index:    None
        """

        # Test if the current pipe exists.
        pipes.test()

        # The spectrum types have not been set.
        if not hasattr(cdp, 'spectrum_type'):
            raise RelaxError("The spectrum types have not been set.")

        # Test if the 2 spectra types 'ref' and 'sat' exist.
        if not 'ref' in cdp.spectrum_type.values() or not 'sat' in cdp.spectrum_type.values():
            raise RelaxError("The reference and saturated NOE spectra have not been loaded.")

        # Loop over the spins.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Average intensities and squared errors (if required).
            sat = 0.0
            sat_err2 = 0.0
            sat_count = 0
            ref = 0.0
            ref_err2 = 0.0
            ref_count = 0
            for id in cdp.spectrum_ids:
                # Sat spectra.
                if cdp.spectrum_type[id] == 'sat':
                    sat += spin.peak_intensity[id]
                    sat_err2 += spin.peak_intensity_err[id]**2
                    sat_count += 1

                # Ref spectra.
                if cdp.spectrum_type[id] == 'ref':
                    ref += spin.peak_intensity[id]
                    ref_err2 += spin.peak_intensity_err[id]**2
                    ref_count += 1

            # Average the values and errors (variance averaging).
            sat = sat / sat_count
            sat_err2 = sat_err2 / sat_count
            ref = ref / ref_count
            ref_err2 = ref_err2 / ref_count

            # Calculate the NOE.
            spin.noe = sat / ref

            # Calculate the error.
            spin.noe_err = sqrt(sat_err2 * ref**2 + ref_err2 * sat**2) / ref**2


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
        all_desel = True
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # No intensity data.
            if not hasattr(spin, 'peak_intensity'):
                warn(RelaxDeselectWarning(spin_id, 'the absence of intensity data'))
                spin.select = False
                deselect_flag = True
                continue

            # Check for sufficient data.
            if not len(spin.peak_intensity) >= 2:
                warn(RelaxDeselectWarning(spin_id, 'insufficient data (less than two data points)'))
                spin.select = False
                deselect_flag = True
                continue

            # No error data.
            if not hasattr(spin, 'peak_intensity_err'):
                warn(RelaxDeselectWarning(spin_id, 'the absence of errors'))
                spin.select = False
                deselect_flag = True
                continue

            # Check for sufficient errors.
            if not len(spin.peak_intensity_err) >= 2:
                warn(RelaxDeselectWarning(spin_id, 'missing errors (less than two error points)'))
                spin.select = False
                deselect_flag = True
                continue

            # Not all spins have been deselected.
            all_desel = False

        # Final printout.
        if verbose and not deselect_flag:
            print("No spins have been deselected.")

        # Catch complete failures - i.e. no spins are selected.
        if all_desel:
            raise RelaxError("All spins have been deselected.")
