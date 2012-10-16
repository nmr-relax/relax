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
"""Special module for checking types."""

# Python module imports.
io_module = True
try:
    from io import IOBase    # Python 2.5+ import.
    file = None
except ImportError:
    io_module = False


def is_filetype(obj):
    """Check if the given Python object is a file.

    @param obj:     The Python object.
    @type obj:      anything
    @return:        True if the object is a file, False otherwise.
    @rtype:         bool
    """

    # New style check.
    if io_module:
        return isinstance(obj, IOBase)

    # Old style check.
    else:
        return isinstance(obj, file)
