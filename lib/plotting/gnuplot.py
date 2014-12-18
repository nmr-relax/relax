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
"""Module for data plotting using gnuplot."""

# relax module imports.
from lib.io import open_write_file, swap_extension


def correlation_matrix(matrix=None, labels=None, file=None, dir=None, force=False):
    """Gnuplot plotting function for representing correlation matrices.

    @keyword matrix:    The correlation matrix.  This must be a square matrix.
    @type matrix:       numpy rank-2 array.
    @keyword labels:    The labels for each element of the matrix.  The same label is assumed for each [i, i] pair in the matrix.
    @type labels:       list of str
    @keyword file:      The name of the file to create.
    @type file:         str
    @keyword dir:       The directory where the PDB file will be placed.  If set to None, then the file will be placed in the current directory.
    @type dir:          str or None
    """

    # The script file name.
    file_name = swap_extension(file=file, ext='gnu')

    # Open the script file for writing.
    output = open_write_file(file_name, dir=dir, force=force)

    # Set the plot type.
    output.write("set pm3d map\n")

    # Load and show the text data.
    output.write("splot \"%s\" matrix\n" % file)

    # Close the file.
    output.close()
