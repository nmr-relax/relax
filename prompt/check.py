###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Argument checking functions for the relax user functions."""

# relax module imports.
from relax_errors import RelaxBoolError, RelaxIntError, RelaxNoneIntError, RelaxNoneStrError, RelaxStrError


def is_bool(arg, name):
    """Test if the argument is a Boolean.

    @param arg:                 The argument.
    @type arg:                  anything
    @param name:                The plain English name of the argument.
    @type name:                 str
    @raise RelaxBoolError:      If not a Boolean.
    """

    # Check for a Boolean.
    if isinstance(arg, bool):
        return

    # Fail.
    else:
        raise RelaxBoolError(name, arg)


def is_int(arg, name, can_be_none=True):
    """Test if the argument is an integer.

    @param arg:                 The argument.
    @type arg:                  anything
    @param name:                The plain English name of the argument.
    @type name:                 str
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @raise RelaxIntError:       If not an integer.
    @raise RelaxNoneIntError:   If not an integer or not None.
    """

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Check for an integer (avoiding Booleans).
    elif isinstance(arg, int) and not isinstance(arg, bool):
        return

    # Fail.
    else:
        if not can_be_none:
            raise RelaxIntError(name, arg)
        else:
            raise RelaxNoneIntError(name, arg)


def is_str(arg, name, can_be_none=True):
    """Test if the argument is a string.

    @param arg:                 The argument.
    @type arg:                  anything
    @param name:                The plain English name of the argument.
    @type name:                 str
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @raise RelaxStrError:       If not an integer.
    @raise RelaxNoneStrError:   If not an integer or not None.
    """

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Check for a string.
    elif isinstance(arg, str):
        return

    # Fail.
    else:
        if not can_be_none:
            raise RelaxStrError(name, arg)
        else:
            raise RelaxNoneStrError(name, arg)
