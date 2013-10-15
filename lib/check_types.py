###############################################################################
#                                                                             #
# Copyright (C) 2012-2013 Edward d'Auvergne                                   #
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
from numpy import complex64, complex128, float32, float64
try:
    from numpy import complex256
except ImportError:
    complex256 = complex128    # Support for 32-bit numpy versions.
try:
    from numpy import float16
except ImportError:
    float16 = float32    # Support for old numpy versions.
try:
    from numpy import float128
except ImportError:
    float128 = float64    # Support for 32-bit numpy versions.


def is_complex(num):
    """Check if the given number is a Python or numpy complex.

    @param num: The number to check.
    @type num:  anything.
    @return:    True if the number is a complex, False otherwise.
    @rtype:     bool
    """

    # Standard complex.
    if isinstance(num, complex):
        return True

    # Numpy complex numbers.
    if isinstance(num, complex64):
        return True
    if isinstance(num, complex128):
        return True
    if isinstance(num, complex256):
        return True

    # Not a complex.
    return False


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


def is_float(num):
    """Check if the given number is a Python or numpy float.

    @param num: The number to check.
    @type num:  anything.
    @return:    True if the number is a float, False otherwise.
    @rtype:     bool
    """

    # Standard float.
    if isinstance(num, float):
        return True

    # Numpy floats.
    if isinstance(num, float16):
        return True
    if isinstance(num, float32):
        return True
    if isinstance(num, float64):
        return True
    if isinstance(num, float128):
        return True

    # Not a float.
    return False


def is_unicode(obj):
    """Check if the given Python object is a unicode string.

    @param obj:     The Python object.
    @type obj:      anything
    @return:        True if the object is a unicode string, False otherwise.
    @rtype:         bool
    """

    # Check using the unicode type (set in the compat module for Python 3).
    return isinstance(obj, unicode)
