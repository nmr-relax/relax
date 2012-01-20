###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
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
from math import sqrt
from re import match
from warnings import warn

# relax module imports.
from generic_fns import pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data, spin_loop
from relax_errors import RelaxArgNotInListError, RelaxError, RelaxNoSequenceError
from relax_warnings import RelaxDeselectWarning
from specific_fns.api_common import API_common


class Noe_main:
    """Class containing functions for relaxation data."""

    def _assign_function(self, spin=None, intensity=None, spectrum_type=None):
        """Place the peak intensity data into the spin container.

        The intensity data can be either that of the reference or saturated spectrum.

        @keyword spin:          The spin container.
        @type spin:             SpinContainer instance
        @keyword intensity:     The intensity value.
        @type intensity:        float
        @keyword spectrum_type: The type of spectrum, one of 'ref' or 'sat'.
        @type spectrum_type:    str
        """

        # Add the data.
        if spectrum_type == 'ref':
            spin.ref = intensity
        elif spectrum_type == 'sat':
            spin.sat = intensity
        else:
            raise RelaxError("The spectrum type '%s' is unknown." % spectrum_type)


    def _spectrum_type(self, spectrum_type=None, spectrum_id=None):
        """Set the spectrum type corresponding to the spectrum_id.

        @keyword spectrum_type: The type of NOE spectrum, one of 'ref' or 'sat'.
        @type spectrum_type:    str
        @keyword spectrum_id:   The spectrum id string.
        @type spectrum_id:      str
        """

        # Test if the current pipe exists
        pipes.test()

        # Test the spectrum id string.
        if spectrum_id not in cdp.spectrum_ids:
            raise RelaxError("The peak intensities corresponding to the spectrum id '%s' does not exist." % spectrum_id)

        # Initialise or update the spectrum_type data structure as necessary.
        if not hasattr(cdp, 'spectrum_type'):
            cdp.spectrum_type = {}

        # Set the error.
        cdp.spectrum_type[spectrum_id] = spectrum_type


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

            # Average intensities (if required).
            sat = 0.0
            sat_err = 0.0
            ref = 0.0
            ref_err = 0.0
            for id in cdp.spectrum_ids:
                # Sat spectra.
                if cdp.spectrum_type[id] == 'sat':
                    sat = sat + spin.intensities[id]
                    sat_err = sat_err + spin.intensity_err[id]

                # Ref spectra.
                if cdp.spectrum_type[id] == 'ref':
                    ref = ref + spin.intensities[id]
                    ref_err = ref_err + spin.intensity_err[id]

            # Calculate the NOE.
            spin.noe = sat / ref

            # Calculate the error.
            spin.noe_err = sqrt((sat_err * ref)**2 + (ref_err * sat)**2) / ref**2


    def data_names(self, set='all', error_names=False, sim_names=False):
        """Return a list of all spin container specific model-free object names.

        Description
        ===========

        The names are as follows:

            - 'model', the model-free model name.
            - 'equation', the model-free equation type.
            - 'params', an array of the model-free parameter names associated with the model.
            - 's2', S2.
            - 's2f', S2f.
            - 's2s', S2s.
            - 'local_tm', local tm.
            - 'te', te.
            - 'tf', tf.
            - 'ts', ts.
            - 'rex', Rex.
            - 'r', bond length.
            - 'csa', CSA value.
            - 'nucleus', the heteronucleus type.
            - 'chi2', chi-squared value.
            - 'iter', iterations.
            - 'f_count', function count.
            - 'g_count', gradient count.
            - 'h_count', hessian count.
            - 'warning', minimisation warning.


        @keyword set:           The set of object names to return.  This can be set to 'all' for all
                                names, to 'generic' for generic object names, 'params' for
                                model-free parameter names, or to 'min' for minimisation specific
                                object names.
        @type set:              str
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

        # Generic.
        if set == 'all' or set == 'generic':
            names.append('select')
            names.append('fixed')
            names.append('ref')
            names.append('sat')

        # Parameters.
        if set == 'all' or set == 'params':
            names.append('noe')

        # Parameter errors.
        if error_names and (set == 'all' or set == 'params'):
            names.append('noe_err')

        # Return the names.
        return names


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

            # Check for sufficient data.
            if not hasattr(spin, 'intensities') or not len(spin.intensities) == 2:
                warn(RelaxDeselectWarning(spin_id, 'insufficient data'))
                spin.select = False

            # Check for sufficient errors.
            elif not hasattr(spin, 'intensity_err') or not len(spin.intensity_err) == 2:
                warn(RelaxDeselectWarning(spin_id, 'missing errors'))
                spin.select = False


    return_data_name_doc = ["NOE calculation data type string matching patterns", """
        _________________________________________
        |                        |              |
        | Data type              | Object name  |
        |________________________|______________|
        |                        |              |
        | Reference intensity    | 'ref'        |
        |                        |              |
        | Saturated intensity    | 'sat'        |
        |                        |              |
        | NOE                    | 'noe'        |
        |________________________|______________|

        """]


    def return_units(self, param):
        """Dummy function which returns None as the stats have no units.

        @param param:   The name of the parameter to return the units string for.
        @type param:    str
        @return:        Nothing.
        @rtype:         None
        """

        return None
