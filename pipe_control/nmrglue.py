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
"""Module for the using of nmrglue."""

# relax module imports.
from lib.errors import RelaxError
from lib.software.nmrglue import read_spectrum
from pipe_control.pipes import check_pipe
from pipe_control.spectrum import add_spectrum_id, check_spectrum_id, delete


def add_nmrglue_data(spectrum_id=None, nmrglue_data=None):
    """Add the nmrglue_data to the data store.

    @keyword spectrum_id:   The spectrum ID string.
    @type spectrum_id:      str
    @keyword nmrglue_data:  The nmrglue data as class instance object.
    @type nmrglue_data:     lib.spectrum.objects.Nmrglue_data instance
    """

    # Initialise the structure, if needed.
    if not hasattr(cdp, 'ngdata'):
        cdp.ngdata = {}

    # Add the data under the spectrum ID.
    cdp.ngdata[spectrum_id] = nmrglue_data[0]


def read(file=None, dir=None, spectrum_id=None):
    """Read the spectrum file.

    @keyword file:          The name of the file(s) containing the spectrum.
    @type file:             str or list of str
    @keyword dir:           The directory where the file is located.
    @type dir:              str
    @keyword spectrum_id:   The spectrum identification string.
    @type spectrum_id:      str or list of str
    """

    # Data checks.
    check_pipe()

    # Check the file name.
    if file == None:
        raise RelaxError("The file name must be supplied.")

    # Add spectrum ID.
    add_spectrum_id(spectrum_id)

    # Read the spectrum, and get it back as a class instance object.
    nmrglue_data = read_spectrum(file=file, dir=dir)

    # Store the data.
    add_nmrglue_data(spectrum_id=spectrum_id, nmrglue_data=nmrglue_data)
