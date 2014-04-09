###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
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
"""The R1 and R2 exponential relaxation curve fitting user functions."""

# relax module imports.
from lib.errors import RelaxError, RelaxFuncSetupError, RelaxNoSequenceError
from pipe_control import pipes
from pipe_control.mol_res_spin import exists_mol_res_spin_data, spin_loop
from specific_analyses.relax_fit.api import Relax_fit
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container

# The API object.
api_relax_fit = Relax_fit()


# Default value documentation.
default_value_doc = Desc_container("Relaxation curve fitting default values")
default_value_doc.add_paragraph("These values are completely arbitrary as peak heights (or volumes) are extremely variable and the Rx value is a compensation for both the R1 and R2 values.")
table = uf_tables.add_table(label="table: curve-fit default values", caption="Relaxation curve fitting default values.")
table.add_headings(["Data type", "Object name", "Value"])
table.add_row(["Relaxation rate", "'rx'", "8.0"])
table.add_row(["Initial intensity", "'i0'", "10000.0"])
table.add_row(["Intensity at infinity", "'iinf'", "0.0"])
default_value_doc.add_table(table.label)

# Data name documentation.
return_data_name_doc = Desc_container("Relaxation curve fitting data type string matching patterns")
table = uf_tables.add_table(label="table: curve-fit data type patterns", caption="Relaxation curve fitting data type string matching patterns.")
table.add_headings(["Data type", "Object name"])
table.add_row(["Relaxation rate", "'rx'"])
table.add_row(["Peak intensities (series)", "'peak_intensity'"])
table.add_row(["Initial intensity", "'i0'"])
table.add_row(["Intensity at infinity", "'iinf'"])
table.add_row(["Relaxation period times (series)", "'relax_times'"])
return_data_name_doc.add_table(table.label)

# Value setting documentation.
set_doc = Desc_container("Relaxation curve fitting set details")
set_doc.add_paragraph("Only three parameters can be set, the relaxation rate (Rx), the initial intensity (I0), and the intensity at infinity (Iinf).  Setting the parameter Iinf has no effect if the chosen model is that of the exponential curve which decays to zero.")


def model_setup(model, params):
    """Update various model specific data structures.

    @param model:   The exponential curve type.
    @type model:    str
    @param params:  A list consisting of the model parameters.
    @type params:   list of str
    """

    # Set the model.
    cdp.curve_type = model

    # Loop over the sequence.
    for spin in spin_loop():
        # Skip deselected spins.
        if not spin.select:
            continue

        # Initialise the data structures (if needed).
        api_relax_fit.data_init(spin)

        # The model and parameter names.
        spin.model = model
        spin.params = params


def relax_time(time=0.0, spectrum_id=None):
    """Set the relaxation time period associated with a given spectrum.

    @keyword time:          The time, in seconds, of the relaxation period.
    @type time:             float
    @keyword spectrum_id:   The spectrum identification string.
    @type spectrum_id:      str
    """

    # Test if the spectrum id exists.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxError("The peak heights corresponding to spectrum id '%s' have not been loaded." % spectrum_id)

    # Initialise the global relaxation time data structure if needed.
    if not hasattr(cdp, 'relax_times'):
        cdp.relax_times = {}

    # Add the time at the correct position.
    cdp.relax_times[spectrum_id] = time


def select_model(model='exp'):
    """Function for selecting the model of the exponential curve.

    @keyword model: The exponential curve type.  Can be one of 'exp' or 'inv'.
    @type model:    str
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the pipe type is set to 'relax_fit'.
    function_type = cdp.pipe_type
    if function_type != 'relax_fit':
        raise RelaxFuncSetupError(specific_setup.get_string(function_type))

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Two parameter exponential fit.
    if model == 'exp':
        print("Two parameter exponential fit.")
        params = ['rx', 'i0']

    # Three parameter inversion recovery fit.
    elif model == 'inv':
        print("Three parameter inversion recovery fit.")
        params = ['rx', 'i0', 'iinf']

    # Invalid model.
    else:
        raise RelaxError("The model '" + model + "' is invalid.")

    # Set up the model.
    model_setup(model, params)
