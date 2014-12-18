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
from lib.io import file_root, open_write_file, swap_extension
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

    # Set the plot type.
    output.write("\n# Set the plot type.\n")
    output.write("set pm3d map\n")

    # Set up the terminal type and make the plot square.
    output.write("\n# Make the plot square.\n")
    output.write("set terminal postscript eps size 10,10 enhanced color font 'Helvetica,20' linewidth 0.1\n")

    # The blue-red colour map.
    output.write("\n# Blue-red colour map.\n")
    colours = [
        "#000090",
        "#000fff",
        "#0090ff",
        "#0fffee",
        "#90ff70",
        "#ffee00",
        "#ff7000",
        "#ee0000",
        "#7f0000"
    ]
    output.write("set palette defined (")
    for i in range(len(colours)):
        if i != 0:
            output.write(", ")
        output.write("%s \"%s\"" % (i, colours[i]))
    output.write(")\n")

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

    # Output to EPS by default.
    output.write("\n# Output to EPS by default.\n")
    output.write("set output \"%s.eps\"\n" % file_root(file))

    # Load and show the text data.
    output.write("\n# Load and show the text data\n")
    output.write("splot \"%s\" matrix\n" % file)

    # Close the file.
    output.close()


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
