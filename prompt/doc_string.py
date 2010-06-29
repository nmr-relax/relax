###############################################################################
#                                                                             #
# Copyright (C) 2005, 2009-2010 Edward d'Auvergne                             #
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

# Module docstring.
"""Module containing various shared docstrings."""
__docformat__ = 'plaintext'


class Regexp:
    """Class containing regular expression docstrings."""

    doc = """

        Regular expression
        ~~~~~~~~~~~~~~~~~~

        The python function 'match', which uses regular expression, is used to determine which data
        type to set values to, therefore various data_type strings can be used to select the same
        data type.  Patterns used for matching for specific data types are listed below.

        This is a short description of python regular expression, for more information see the
        regular expression syntax section of the Python Library Reference.  Some of the regular
        expression syntax used in this function is:

            '[]':  A sequence or set of characters to match to a single character.  For example,
            '[Ss]2' will match both 'S2' and 's2'.

            '^':  Match the start of the string.

            '$':  Match the end of the string.  For example, '^[Ss]2$' will match 's2' but not 'S2f'
            or 's2s'.

            '.':  Match any character.

            'x*':  Match the character 'x' any number of times, for example 'x' will match, as will
            'xxxxx'

            '.*':  Match any sequence of characters of any length.

        Importantly, do not supply a string for the data type containing regular expression.  The
        regular expression is implemented so that various strings can be supplied which all match
        the same data type.
    """


class Strings:
    """The docstring object containing class containers of docstrings."""

    def __init__(self):
        """Initialise docstring object."""

        # The regular expression.
        self.regexp = Regexp()


# The object.
docs = Strings()
