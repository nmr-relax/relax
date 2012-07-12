###############################################################################
#                                                                             #
# Copyright (C) 2005-2012 Edward d'Auvergne                                   #
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
"""Module containing various shared docstrings."""


# relax module imports.
from user_functions.objects import Desc_container


# Regular expression.
regexp_doc = Desc_container("Regular expression")
regexp_doc.add_paragraph("The python function 'match', which uses regular expression, is used to determine which data type to set values to, therefore various data_type strings can be used to select the same data type.  Patterns used for matching for specific data types are listed below.")
regexp_doc.add_paragraph("This is a short description of python regular expression, for more information see the regular expression syntax section of the Python Library Reference.  Some of the regular expression syntax used in this function is:")
regexp_doc.add_item_list_element("'[]'", "A sequence or set of characters to match to a single character.  For example, '[sS]2' will match both 'S2' and 's2'.")
regexp_doc.add_item_list_element("'^'", "Match the start of the string.")
regexp_doc.add_item_list_element("'$'", "Match the end of the string.  For example, '^[Ss]2$' will match 's2' but not 'S2f' or 's2s'.")
regexp_doc.add_item_list_element("'.'", "Match any character.")
regexp_doc.add_item_list_element("'x*'", "Match the character 'x' any number of times, for example 'x' will match, as will 'xxxxx'.")
regexp_doc.add_item_list_element("'.*'", "Match any sequence of characters of any length.")
regexp_doc.add_paragraph("Importantly, do not supply a string for the data type containing regular expression.  The regular expression is implemented so that various strings can be supplied which all match the same data type.")
