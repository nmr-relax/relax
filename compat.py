###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""Temporary module for allowing relax to support both Python 2 and 3."""

# Python module imports.
import sys

# The Python version.
py_version = sys.version_info[0]

# Python 2 hacks.
if py_version == 2:
    # Python 2 only imports.
    import __builtin__

    # Switch all range() calls to xrange() for increased speed and memory reduction.
    # This should work as all range() usage for Python 3 in relax must match the old xrange() usage.
    __builtin__.range = __builtin__.xrange


# Python 3 work-arounds.
if py_version == 3:
    # Python 3 only imports.
    import builtins

    # The unicode conversion function - essential for the GUI in Python 2.
    builtins.unicode = builtins.str
