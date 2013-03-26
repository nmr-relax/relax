###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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

# Module docsting.
"""Module for executing OpenDX."""


# Python module imports.
from os import system

# relax module imports.
from lib.io import test_binary


def run(file_prefix="map", dir="dx", dx_exe="dx", vp_exec=True):
    """Execute OpenDX.

    @keyword file_prefix:   The file prefix for all the created files.
    @type file_prefix:      str
    @keyword dir:           The directory to place the files into.
    @type dir:              str or None
    @keyword dx_exe:        The path to the OpenDX executable file.  This can be changed if the
                            binary 'dx' is not located in the system path.
    @type dx_exe:           str
    @keyword vp_exec:       If True, then the OpenDX visual program will be launched.
    @type vp_exec:          bool
    """

    # Text for changing to the directory dir.
    dir_text = ""
    if dir != None:
        dir_text = " -directory " + dir

    # Text for executing OpenDX.
    execute_text = ""
    if vp_exec:
        execute_text = " -execute"

    # Test the binary file string corresponds to a valid executable.
    test_binary(dx_exe)

    # Run OpenDX.
    system(dx_exe + dir_text + " -program " + file_prefix + ".net" + execute_text + " &")
