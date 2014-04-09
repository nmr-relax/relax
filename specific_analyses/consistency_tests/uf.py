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
"""The consistency testing analysis user functions."""

# relax module imports.
from lib.errors import RelaxError, RelaxFuncSetupError
from lib.physical_constants import N15_CSA, NH_BOND_LENGTH
from pipe_control import pipes
import specific_analyses
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container


# Default value documentation.
default_value_doc = Desc_container("Consistency testing default values")
default_value_doc.add_paragraph("These default values are found in the file 'physical_constants.py'.")
table = uf_tables.add_table(label="table: consistency testing default values", caption="Consistency testing default values.")
table.add_headings(["Data type", "Object name", "Value"])
table.add_row(["Bond length", "'r'", repr(NH_BOND_LENGTH)])
table.add_row(["CSA", "'csa'", repr(N15_CSA)])
table.add_row(["Heteronucleus type", "'heteronuc_type'", "'15N'"])
table.add_row(["Angle theta", "'proton_type'", "'1H'"])
table.add_row(["Proton type", "'orientation'", "15.7"])
table.add_row(["Correlation time", "'tc'", "13 * 1e-9"])
default_value_doc.add_table(table.label)

# Data name documentation.
return_data_name_doc = Desc_container("Consistency testing data type string matching patterns")
table = uf_tables.add_table(label="table: Consistency testing data types", caption="Consistency testing data type string matching patterns.")
table.add_headings(["Data type", "Object name"])
table.add_row(["J(0)", "'j0'"])
table.add_row(["F_eta", "'f_eta'"])
table.add_row(["F_R2", "'f_r2'"])
table.add_row(["Bond length", "'r'"])
table.add_row(["CSA", "'csa'"])
table.add_row(["Heteronucleus type", "'heteronuc_type'"])
table.add_row(["Proton type", "'proton_type'"])
table.add_row(["Angle theta", "'orientation'"])
table.add_row(["Correlation time", "'tc'"])
return_data_name_doc.add_table(table.label)

# Value setting documentation.
set_doc = Desc_container("Consistency testing set details")
set_doc.add_paragraph("In consistency testing, only four values can be set, the bond length, CSA, angle Theta ('orientation') and correlation time values. These must be set prior to the calculation of consistency functions.")


def set_frq(frq=None):
    """Function for selecting which relaxation data to use in the consistency tests."""

    # Test if the current pipe exists.
    pipes.test()

    # Test if the pipe type is set to 'ct'.
    function_type = cdp.pipe_type
    if function_type != 'ct':
        raise RelaxFuncSetupError(specific_analyses.setup.get_string(function_type))

    # Test if the frequency has been set.
    if hasattr(cdp, 'ct_frq'):
        raise RelaxError("The frequency for the run has already been set.")

    # Create the data structure if it doesn't exist.
    if not hasattr(cdp, 'ct_frq'):
        cdp.ct_frq = {}

    # Set the frequency.
    cdp.ct_frq = frq
