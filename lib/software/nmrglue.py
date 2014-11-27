###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""Module for the wrapper functions around the nmrglue module."""

# Python module imports.
from re import search, split

# relax module imports.
from extern import nmrglue
from lib.errors import RelaxError
from lib.io import get_file_path
from lib.spectrum.objects import Nmrglue_data


def read_spectrum(file=None, dir=None):
    """Read the spectrum data.

    @keyword file:          The name of the file containing the spectrum.
    @type file:             str
    @keyword dir:           The directory where the file is located.
    @type dir:              str
    @return:                The nmrglue data object containing all relevant data in the spectrum.
    @rtype:                 lib.spectrum.objects.Nmrglue_data instance
    """

    # File path.
    file_path = get_file_path(file, dir)

    # Open file
    dic, data = nmrglue.pipe.read(file_path)
    udic = nmrglue.pipe.guess_udic(dic, data)

    # Initialise the nmrglue data object.
    nmrglue_data = Nmrglue_data()

    # Add the data.
    nmrglue_data.add(file_path=file_path, dic=dic, udic=udic, data=data)

    # Return the nmrglue data object.
    return nmrglue_data
