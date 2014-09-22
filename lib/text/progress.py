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
"""Text based progress meters."""

# Python module imports.
import locale
import sys


def progress_meter(i, a=250, b=10000, file=sys.stderr):
    """A simple progress write out (which defaults to the terminal STDERR).

    @param i:       The current iteration.
    @type i:        int
    @keyword a:     The step size for spinning the spinner.
    @type a:        int
    @keyword b:     The step size for printing out the progress.
    @type b:        int
    @keyword file:  The file object to write the output to.
    @type file:     file object
    """

    # The spinner characters.
    chars = ['-', '\\', '|', '/']

    # A spinner.
    if i % a == 0:
        file.write('\b%s' % chars[i%4])
        if hasattr(file, 'flush'):
            file.flush()

    # Dump the progress.
    if i % b == 0:
        num = locale.format("%d", i, grouping=True)
        file.write('\b%12s\n' % num)
