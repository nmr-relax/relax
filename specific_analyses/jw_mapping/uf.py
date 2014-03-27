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

# Package docstring.
"""Module for all of the reduced spectral density mapping specific user functions."""

# relax module imports.
from lib.errors import RelaxError, RelaxFuncSetupError
from lib.physical_constants import N15_CSA
from pipe_control import pipes
import specific_analyses
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container


# Default value documentation.
default_value_doc = Desc_container("Reduced spectral density mapping default values")
default_value_doc.add_paragraph("These default values are found in the file 'physical_constants.py'.")
table = uf_tables.add_table(label="table: J(w) default values", caption="Reduced spectral density mapping default values.")
table.add_headings(["Data type", "Object name", "Value"])
table.add_row(["CSA", "'csa'", N15_CSA])
default_value_doc.add_table(table.label)

# Data name documentation.
return_data_name_doc = Desc_container("Reduced spectral density mapping data type string matching patterns")
table = uf_tables.add_table(label="table: J(w) data types", caption="Reduced spectral density mapping data type string matching patterns.")
table.add_headings(["Data type", "Object name"])
table.add_row(["J(0)", "'j0'"])
table.add_row(["J(wX)", "'jwx'"])
table.add_row(["J(wH)", "'jwh'"])
table.add_row(["CSA", "'csa'"])
return_data_name_doc.add_table(table.label)

# Value setting documentation.
set_doc = Desc_container("Reduced spectral density mapping set details")
set_doc.add_paragraph("In reduced spectral density mapping, three values must be set prior to the calculation of spectral density values:  the bond length, CSA, and heteronucleus type.")


def set_frq(frq=None):
    """Function for selecting which relaxation data to use in the J(w) mapping."""

    # Test if the current pipe exists.
    pipes.test()

    # Test if the pipe type is set to 'jw'.
    function_type = cdp.pipe_type
    if function_type != 'jw':
        raise RelaxFuncSetupError(specific_analyses.setup.get_string(function_type))

    # Test if the frequency has been set.
    if hasattr(cdp, 'jw_frq'):
        raise RelaxError("The frequency has already been set.")

    # Create the data structure if it doesn't exist.
    if not hasattr(cdp, 'jw_frq'):
        cdp.jw_frq = {}

    # Set the frequency.
    cdp.jw_frq = frq
