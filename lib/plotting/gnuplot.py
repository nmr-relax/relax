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

# Python module imports.
from os import chmod
from stat import S_IRWXU, S_IRGRP, S_IROTH

# relax module imports.
from lib.io import file_root, get_file_path, open_write_file, swap_extension
from lib.plotting import text


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

    # The dimensions.
    n = len(matrix)

    # Generate the text file for loading into gnuplot.
    text.correlation_matrix(matrix=matrix, labels=labels, file=file, dir=dir, force=force)

    # The script file name with the extension swapped.
    file_name = swap_extension(file=file, ext='gnu')

    # Open the script file for writing.
    output = open_write_file(file_name, dir=dir, force=force)

    # Gnuplot script setup. 
    output.write("#!/usr/bin/env gnuplot\n\n")


    # Set up the terminal type and make the plot square.
    output.write("# Set up the terminal type and make the plot square.\n")
    output.write("set terminal postscript eps size 10,10 enhanced color font 'Helvetica,20' linewidth 0.1\n")
    output.write("set size square\n")

    # The colour map.
    output.write("\n# Blue-red colour map.\n")
    output.write("set palette model RGB\n")
    output.write("set palette defined\n")

    # The labels.
    if labels != None:
        output.write("\n# Labels.\n")
        for axis in ['x', 'y']:
            output.write("set %stics out " % axis)
            if axis == 'x':
                output.write("rotate ")
            output.write("font \",8\" (")
            for i in range(n):
                if i != 0:
                    output.write(", ")
                output.write("\"%s\" %s" % (format_enhanced(labels[i]), i))
            output.write(")\n")

    # Output to EPS.
    output.write("\n# Output to EPS.\n")
    output.write("set output \"%s.eps\"\n" % file_root(file))

    # Load and show the text data.
    output.write("\n# Load and show the text data\n")
    output.write("plot \"%s\" matrix with image\n" % file)

    # Close the file.
    output.close()

    # Make the script executable.
    chmod(get_file_path(file_name=file_name, dir=dir), S_IRWXU|S_IRGRP|S_IROTH)


def format_enhanced(text):
    """Convert and return the text to handle enhanced postscript.

    @param text:    The text to convert to enhanced mode.
    @type text:     str
    @return:        The formatted text for enhanced postscript mode.
    @rtype:         str
    """

    # Handle the '@' character.
    text = text.replace('@', '\\\\@')

    # Return the text.
    return text
