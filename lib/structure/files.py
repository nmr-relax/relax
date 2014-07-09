###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
"""Module for handling different structural file formats."""

# Python module imports.
from os import F_OK, access, sep


def find_pdb_files(path=None, file_root=None):
    """Find all PDB files in the given path corresponding to the file root.

    This will find all *.pdb, *.pdb.gz, and *.pdb.bz2 files, package them into a list, and return the list.


    @keyword path:      The file system path to search for the files in.
    @type path:         str
    @keyword file_root: The file root of the files to find.  For example if the file is 'test.pdb.gz', then the file root is 'test'.
    @type file_root:    str
    """

    # Initialise.
    files = []

    # The uncompressed version.
    file = path+sep+file_root+'.pdb'
    if access(file, F_OK):
        files.append(file)

    # The gzipped version.
    file = path+sep+file_root+'.pdb.gz'
    if access(file, F_OK):
        files.append(file)

    # The bzipped version.
    file = path+sep+file_root+'.pdb.bz2'
    if access(file, F_OK):
        files.append(file)

    # Return the file list.
    return files
