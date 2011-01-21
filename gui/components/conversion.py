###############################################################################
#                                                                             #
# Copyright (C) 2010 Michael Bieri                                            #
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

# Package docstring.
"""Package for the different conversion tools used to bring together the GUI and API of relax."""

from string import replace, strip, split


def str_to_float(string):
    """Function to convert a float in a string object to a real float object.

    such as:    "3.5 * 1e6" to 3.5*1e6


    @param string:  Float in string that will be converted to float object.
    @type string:   str
    """

    # Delete whitespace.
    string = replace(string, ' ','')

    # Strip string.
    values = split(string, '*')

    # Detect exponent.
    if '1e' in values[1]:
        exponent = float(replace(values[1], '1e', ''))
    if '10^' in values[1]:
        exponent = float(replace(values[1], '10^', ''))

    # Calculate float.
    float_obj = float(values[0]) * 10**exponent

    return float_obj
