###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Edward d'Auvergne                                   #
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

# Python module imports.
from numpy import ndarray

# relax module imports.
from relax_errors import RelaxBoolError, RelaxFloatError, RelaxFunctionError, RelaxIntError, RelaxIntListIntError,RelaxListFloatError, RelaxListIntError, RelaxMatrixFloatError, RelaxNoneFloatError, RelaxNoneFunctionError, RelaxListNumError, RelaxListStrError, RelaxNoneIntError, RelaxNoneIntListIntError, RelaxNoneListFloatError, RelaxNoneListIntError, RelaxNoneMatrixFloatError, RelaxNoneListNumError, RelaxNoneListStrError, RelaxNoneNumError, RelaxNoneNumStrListNumStrError, RelaxNoneNumTupleNumError, RelaxNoneStrError, RelaxNoneStrFileError, RelaxNoneStrListNumError, RelaxNoneStrListStrError, RelaxNumError, RelaxNumStrListNumStrError, RelaxNumTupleNumError, RelaxStrError, RelaxStrFileError, RelaxStrListNumError, RelaxStrListStrError, RelaxTupleError, RelaxTupleNumError
from relax_io import DummyFileObject
from types import FunctionType


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
        fail = True

    # The RelaxError.
    raise RelaxBoolError(name, arg)


def is_float(arg, name, can_be_none=False):
    """Test if the argument is a float.

    @param arg:                 The argument.
    @type arg:                  anything
    @param name:                The plain English name of the argument.
    @type name:                 str
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @raise RelaxFloatError:     If not an integer.
    @raise RelaxNoneFloatError: If not an integer or not None.
    """

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Check for a float.
    if isinstance(arg, float):
        return

    # Fail.
    if not can_be_none:
        raise RelaxFloatError(name, arg)
    else:
        raise RelaxNoneFloatError(name, arg)


def is_float_array(arg, name, size=None, can_be_none=False):
    """Test if the argument is an array of floats.

    @param arg:                     The argument.
    @type arg:                      anything
    @param name:                    The plain English name of the argument.
    @type name:                     str
    @keyword size:                  The dimension of the array.
    @type size:                     None or int
    @keyword can_be_none:           A flag specifying if the argument can be none.
    @type can_be_none:              bool
    @raise RelaxListFloatError:     If not a matrix of floats.
    @raise RelaxNoneListFloatError: If not a matrix of floats or not None.
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Fail if not a list.
    if not isinstance(arg, list) and not isinstance(arg, ndarray):
        fail = True

    # Fail if not the right dimension.
    elif size != None and len(arg) != size:
        fail = True

    # Loop over the array.
    else:
        for i in range(len(arg)):
            # Fail if not a float.
            if not isinstance(arg[i], float):
                fail = True

    # Fail.
    if fail:
        if can_be_none and size != None:
            raise RelaxNoneListFloatError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneListFloatError(name, arg)
        elif size != None:
            raise RelaxListFloatError(name, arg, size)
        else:
            raise RelaxListFloatError(name, arg)


def is_float_matrix(arg, name, dim=(3,3), can_be_none=False):
    """Test if the argument is a matrix of floats.

    @param arg:                         The argument.
    @type arg:                          anything
    @param name:                        The plain English name of the argument.
    @type name:                         str
    @keyword dim:                       The m,n dimensions of the matrix.
    @type dim:                          tuple of int
    @keyword can_be_none:               A flag specifying if the argument can be none.
    @type can_be_none:                  bool
    @raise RelaxMatrixFloatError:       If not a matrix of floats.
    @raise RelaxNoneMatrixFloatError:   If not a matrix of floats or not None.
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Fail if not a list.
    if not isinstance(arg, list) and not isinstance(arg, ndarray):
        fail = True

    # Fail if not the right dimension.
    elif dim != None and len(arg) != dim[0]:
        fail = True

    # Loop over the first dimension.
    else:
        for i in range(len(arg)):
            # Fail if not a list.
            if not isinstance(arg[i], list) and not isinstance(arg, ndarray):
                fail = True

            # Fail if not the right dimension.
            elif len(arg[i]) != dim[1]:
                fail = True

            # Check for float elements.
            for j in range(len(arg[i])):
                if not isinstance(arg[i][j], float):
                    fail = True

    # Fail.
    if fail:
        if can_be_none and dim != None:
            raise RelaxNoneMatrixFloatError(name, arg, dim)
        elif can_be_none:
            raise RelaxNoneMatrixFloatError(name, arg)
        elif dim != None:
            raise RelaxMatrixFloatError(name, arg, dim)
        else:
            raise RelaxMatrixFloatError(name, arg)


def is_func(arg, name, can_be_none=False):
    """Test if the argument is a function.

    @param arg:                     The argument.
    @type arg:                      anything
    @param name:                    The plain English name of the argument.
    @type name:                     str
    @keyword can_be_none:           A flag specifying if the argument can be none.
    @type can_be_none:              bool
    @raise RelaxFunctionError:      If not a function.
    @raise RelaxNoneFunctionError:  If not a function or not None.
    """

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Check for a function.
    if isinstance(arg, FunctionType):
        return

    # Fail.
    if not can_be_none:
        raise RelaxFunctionError(name, arg)
    else:
        raise RelaxNoneFunctionError(name, arg)


def is_int(arg, name, can_be_none=False):
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
    if isinstance(arg, int) and not isinstance(arg, bool):
        return

    # Fail.
    if not can_be_none:
        raise RelaxIntError(name, arg)
    else:
        raise RelaxNoneIntError(name, arg)


def is_int_list(arg, name, size=None, can_be_none=False, can_be_empty=False, none_elements=False):
    """Test if the argument is a list of integers.

    @param arg:                         The argument.
    @type arg:                          anything
    @param name:                        The plain English name of the argument.
    @type name:                         str
    @keyword size:                      The number of elements required.
    @type size:                         None or int
    @keyword can_be_none:               A flag specifying if the argument can be none.
    @type can_be_none:                  bool
    @keyword can_be_empty:              A flag which if True allows the list to be empty.
    @type can_be_empty:                 bool
    @keyword none_elements:             A flag which if True allows the list to contain None.
    @type none_elements:                bool
    @raise RelaxIntListIntError:        If not an integer or a list of integers.
    @raise RelaxNoneIntListIntError:    If not an integer, a list of integers, or None.
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Not a list.
    if not isinstance(arg, list):
        fail = True

    # A list.
    else:
        # Fail size is wrong.
        if size != None and len(arg) != size:
            fail = True

        # Fail if empty.
        if not can_be_empty and arg == []:
            fail = True

        # Check the arguments.
        for i in range(len(arg)):
            # None.
            if arg[i] == None and none_elements:
                continue

            # Check if it is an integer.
            if not isinstance(arg[i], int):
                fail = True

    # Fail.
    if fail:
        if can_be_none and size != None:
            raise RelaxNoneListIntError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneListIntError(name, arg)
        elif size != None:
            raise RelaxListIntError(name, arg, size)
        else:
            raise RelaxListIntError(name, arg)


def is_int_or_int_list(arg, name, size=None, can_be_none=False, can_be_empty=False, none_elements=False):
    """Test if the argument is an integer or a list of integers.

    @param arg:                         The argument.
    @type arg:                          anything
    @param name:                        The plain English name of the argument.
    @type name:                         str
    @keyword size:                      The number of elements required.
    @type size:                         None or int
    @keyword can_be_none:               A flag specifying if the argument can be none.
    @type can_be_none:                  bool
    @keyword can_be_empty:              A flag which if True allows the list to be empty.
    @type can_be_empty:                 bool
    @keyword none_elements:             A flag which if True allows the list to contain None.
    @type none_elements:                bool
    @raise RelaxIntListIntError:        If not an integer or a list of integers.
    @raise RelaxNoneIntListIntError:    If not an integer, a list of integers, or None.
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # An integer
    if not isinstance(arg, list):
        # Check if it is an integer.
        try:
            is_int(arg, name)
        except:
            fail = True    # Not an integer.

    # A list.
    else:
        # Fail size is wrong.
        if size != None and len(arg) != size:
            fail = True

        # Fail if empty.
        if not can_be_empty and arg == []:
            fail = True

        # Check the arguments.
        for i in range(len(arg)):
            # None.
            if arg[i] == None and none_elements:
                continue

            # Check if it is an integer.
            try:
                is_int(arg[i], name)
            except:
                fail = True    # Not an integer.

    # Fail.
    if fail:
        if can_be_none and size != None:
            raise RelaxNoneIntListIntError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneIntListIntError(name, arg)
        elif size != None:
            raise RelaxIntListIntError(name, arg, size)
        else:
            raise RelaxIntListIntError(name, arg)


def is_list(arg, name, size=None, can_be_none=False, can_be_empty=False, list_of_lists=False):
    """Test if the argument is a list.

    @param arg:                     The argument.
    @type arg:                      anything
    @param name:                    The plain English name of the argument.
    @type name:                     str
    @keyword size:                  The number of elements required.
    @type size:                     None or int
    @keyword can_be_none:           A flag specifying if the argument can be none.
    @type can_be_none:              bool
    @keyword can_be_empty:          A flag which if True allows the list to be empty.
    @type can_be_empty:             bool
    @keyword list_of_lists:         A flag which if True allows the argument to be a list of lists of strings.
    @type list_of_lists:            bool
    @raise RelaxListStrError:       If not a list of strings.
    @raise RelaxNoneListStrError:   If not a list of strings or None.
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Fail if not a list.
    if not isinstance(arg, list):
        fail = True

    # Other checks.
    else:
        # Fail size is wrong.
        if size != None and len(arg) != size:
            fail = True

        # Fail if empty.
        if not can_be_empty and arg == []:
            fail = True

    # Fail.
    if fail:
        if can_be_none and size != None:
            raise RelaxNoneListError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneListError(name, arg)
        elif size != None:
            raise RelaxListError(name, arg, size)
        else:
            raise RelaxListError(name, arg)


def is_none(arg, name):
    """Test if the argument is None.

    @param arg:                 The argument.
    @type arg:                  anything
    @param name:                The plain English name of the argument.
    @type name:                 str
    @raise RelaxNoneError:      If not None.
    """

    # Check for None.
    if arg == None:
        return

    # The RelaxError.
    raise RelaxNoneError(name, arg)


def is_num(arg, name, can_be_none=False):
    """Test if the argument is a number.

    @param arg:                 The argument.
    @type arg:                  anything
    @param name:                The plain English name of the argument.
    @type name:                 str
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @raise RelaxNumError:       If not a number.
    @raise RelaxNoneNumError:   If not a number or not None.
    """

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Check for floats and integers (avoiding Booleans).
    if (isinstance(arg, float) or isinstance(arg, int)) and not isinstance(arg, bool):
        return

    # Fail.
    if not can_be_none:
        raise RelaxNumError(name, arg)
    else:
        raise RelaxNoneNumError(name, arg)


def is_num_list(arg, name, size=None, can_be_none=False, can_be_empty=False):
    """Test if the argument is a list of numbers.

    @param arg:                 The argument.
    @type arg:                  anything
    @param name:                The plain English name of the argument.
    @type name:                 str
    @keyword size:              The number of elements required.
    @type size:                 None or int
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword can_be_empty:      A flag which if True allows the list to be empty.
    @type can_be_empty:         bool
    @raise RelaxListError:      If not a list.
    @raise RelaxListNumError:   If not a list of numbers.
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Fail if not a list.
    if not isinstance(arg, list) and not isinstance(arg, ndarray):
        fail = True

    # Other checks.
    else:
        # Fail size is wrong.
        if size != None and len(arg) != size:
            fail = True

        # Fail if empty.
        if not can_be_empty and arg == []:
            fail = True

        # Fail if not numbers.
        for i in range(len(arg)):
            if (not isinstance(arg[i], float) and not isinstance(arg[i], int)) or isinstance(arg, bool):
                fail = True

    # Fail.
    if fail:
        if can_be_none and size != None:
            raise RelaxNoneListNumError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneListNumError(name, arg)
        elif size != None:
            raise RelaxListNumError(name, arg, size)
        else:
            raise RelaxListNumError(name, arg)


def is_num_or_num_tuple(arg, name, size=None, can_be_none=False, can_be_empty=False):
    """Test if the argument is a tuple of numbers.

    @param arg:                 The argument.
    @type arg:                  anything
    @param name:                The plain English name of the argument.
    @type name:                 str
    @keyword size:              The number of elements required.
    @type size:                 None or int
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword can_be_empty:      A flag which if True allows the list to be empty.
    @type can_be_empty:         bool
    @raise RelaxTupleError:     If not a tuple.
    @raise RelaxTupleNumError:  If not a tuple of numbers.
    """

    # Init.
    fail = False
    if size != None and not isinstance(size, list):
        size = [size]

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # A number.
    if not isinstance(arg, tuple):
        # Check if it is a number.
        try:
            is_num(arg, name)
        except:
            fail = True

    # Other checks.
    else:
        # Fail size is wrong.
        if size != None and len(arg) not in size:
            fail = True

        # Fail if empty.
        if not can_be_empty and not len(arg):
            fail = True

        # Fail if not numbers.
        for i in range(len(arg)):
            if (not isinstance(arg[i], float) and not isinstance(arg[i], int)) or isinstance(arg, bool):
                fail = True

    # Fail.
    if fail:
        if can_be_none and size != None:
            raise RelaxNoneNumTupleNumError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneNumTupleNumError(name, arg)
        elif size != None:
            raise RelaxNumTupleNumError(name, arg, size)
        else:
            raise RelaxNumTupleNumError(name, arg)


def is_num_tuple(arg, name, size=None, can_be_none=False, can_be_empty=False):
    """Test if the argument is a tuple of numbers.

    @param arg:                 The argument.
    @type arg:                  anything
    @param name:                The plain English name of the argument.
    @type name:                 str
    @keyword size:              The number of elements required.
    @type size:                 None or int
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword can_be_empty:      A flag which if True allows the list to be empty.
    @type can_be_empty:         bool
    @raise RelaxTupleError:     If not a tuple.
    @raise RelaxTupleNumError:  If not a tuple of numbers.
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Fail if not a tuple.
    if not isinstance(arg, tuple):
        fail = True

    # Other checks.
    else:
        # Fail size is wrong.
        if size != None and len(arg) != size:
            fail = True

        # Fail if empty.
        if not can_be_empty and arg == []:
            fail = True

        # Fail if not numbers.
        for i in range(len(arg)):
            if (not isinstance(arg[i], float) and not isinstance(arg[i], int)) or isinstance(arg, bool):
                fail = True

    # Fail.
    if fail:
        if can_be_none and size != None:
            raise RelaxNoneTupleNumError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneTupleNumError(name, arg)
        elif size != None:
            raise RelaxTupleNumError(name, arg, size)
        else:
            raise RelaxTupleNumError(name, arg)


def is_str(arg, name, can_be_none=False):
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
    if isinstance(arg, str):
        return

    # Fail.
    if not can_be_none:
        raise RelaxStrError(name, arg)
    else:
        raise RelaxNoneStrError(name, arg)


def is_str_list(arg, name, size=None, can_be_none=False, can_be_empty=False, list_of_lists=False):
    """Test if the argument is a list of strings.

    @param arg:                     The argument.
    @type arg:                      anything
    @param name:                    The plain English name of the argument.
    @type name:                     str
    @keyword size:                  The number of elements required.
    @type size:                     None or int
    @keyword can_be_none:           A flag specifying if the argument can be none.
    @type can_be_none:              bool
    @keyword can_be_empty:          A flag which if True allows the list to be empty.
    @type can_be_empty:             bool
    @keyword list_of_lists:         A flag which if True allows the argument to be a list of lists
                                    of strings.
    @type list_of_lists:            bool
    @raise RelaxListStrError:       If not a list of strings.
    @raise RelaxNoneListStrError:   If not a list of strings or None.
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Fail if not a list.
    if not isinstance(arg, list):
        fail = True

    # Other checks.
    else:
        # Fail size is wrong.
        if size != None and len(arg) != size:
            fail = True

        # Fail if empty.
        if not can_be_empty and arg == []:
            fail = True

        # Fail if not strings.
        for i in range(len(arg)):
            # List of lists.
            if list_of_lists and isinstance(arg[i], list):
                for j in range(len(arg[i])):
                    if not isinstance(arg[i][j], str):
                        fail = True


            # Simple list.
            else:
                if not isinstance(arg[i], str):
                    fail = True

    # Fail.
    if fail:
        if can_be_none and size != None:
            raise RelaxNoneListStrError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneListStrError(name, arg)
        elif size != None:
            raise RelaxListStrError(name, arg, size)
        else:
            raise RelaxListStrError(name, arg)


def is_str_or_inst(arg, name, can_be_none=False):
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
    if isinstance(arg, str) or isinstance(arg, file) or isinstance(arg, DummyFileObject):
        return

    # Fail.
    if not can_be_none:
        raise RelaxStrFileError(name, arg)
    else:
        raise RelaxNoneStrFileError(name, arg)


def is_str_or_num_or_str_num_list(arg, name, size=None, can_be_none=False, can_be_empty=False):
    """Test if the argument is a number, a string, a list of numbers, or a list of strings.

    @param arg:                             The argument.
    @type arg:                              anything
    @param name:                            The plain English name of the argument.
    @type name:                             str
    @keyword size:                          The number of elements required.
    @type size:                             None or int
    @keyword can_be_none:                   A flag specifying if the argument can be none.
    @type can_be_none:                      bool
    @keyword can_be_empty:                  A flag which if True allows the list to be empty.
    @type can_be_empty:                     bool
    @raise RelaxNumStrListNumStrError:      If not a float, a string, or a list of floats or
                                            strings.
    @raise RelaxNoneNumStrListNumStrError:  If not a float, a string, a list of floats or strings,
                                        or None.
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # A number or a string.
    if not isinstance(arg, list):
        # Check if it is a string.
        try:
            is_str(arg, name)
        except:
            # Not a string, therefore check if it is a number.
            try:
                is_num(arg, name)
            except:
                fail = True    # Neither a number or a string.

    # A list.
    else:
        # Fail size is wrong.
        if size != None and len(arg) != size:
            fail = True

        # Fail if empty.
        if not can_be_empty and arg == []:
            fail = True

        # Check the arguments.
        for i in range(len(arg)):
            # Check if it is a string.
            try:
                is_str(arg[i], name)
            except:
                # Not a string, therefore check if it is a number.
                try:
                    is_num(arg[i], name)
                except:
                    fail = True    # Neither a number or a string.

    # Fail.
    if fail:
        if can_be_none and size != None:
            raise RelaxNoneNumStrListNumStrError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneNumStrListNumStrError(name, arg)
        elif size != None:
            raise RelaxNumStrListNumStrError(name, arg, size)
        else:
            raise RelaxNumStrListNumStrError(name, arg)


def is_str_or_num_list(arg, name, size=None, can_be_none=False, can_be_empty=False):
    """Test if the argument is a string or a list of numbers.

    @param arg:                         The argument.
    @type arg:                          anything
    @param name:                        The plain English name of the argument.
    @type name:                         str
    @keyword size:                      The number of elements required.
    @type size:                         None or int
    @keyword can_be_none:               A flag specifying if the argument can be none.
    @type can_be_none:                  bool
    @keyword can_be_empty:              A flag which if True allows the list to be empty.
    @type can_be_empty:                 bool
    @raise RelaxStrListNumError:        If not a string or a list of strings.
    @raise RelaxNoneStrListNumError:    If not a string, a list of strings, or None.
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # A string.
    if not isinstance(arg, list):
        # Check if it is a string.
        try:
            is_str(arg, name)
        except:
            fail = True    # Not a string.

    # A list.
    else:
        # Fail size is wrong.
        if size != None and len(arg) != size:
            fail = True

        # Fail if empty.
        if not can_be_empty and arg == []:
            fail = True

       # Check the arguments.
        for i in range(len(arg)):
            # Check if it is a number.
            try:
                is_num(arg[i], name)
            except:
                fail = True    # Not a number.

    # Fail.
    if fail:
        if can_be_none and size != None:
            raise RelaxNoneStrListNumError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneStrListNumError(name, arg)
        elif size != None:
            raise RelaxStrListNumError(name, arg, size)
        else:
            raise RelaxStrListNumError(name, arg)


def is_str_or_str_list(arg, name, size=None, can_be_none=False, can_be_empty=False):
    """Test if the argument is a string or a list of strings.

    @param arg:                         The argument.
    @type arg:                          anything
    @param name:                        The plain English name of the argument.
    @type name:                         str
    @keyword size:                      The number of elements required.
    @type size:                         None or int
    @keyword can_be_none:               A flag specifying if the argument can be none.
    @type can_be_none:                  bool
    @keyword can_be_empty:              A flag which if True allows the list to be empty.
    @type can_be_empty:                 bool
    @raise RelaxStrListStrError:        If not a string or a list of strings.
    @raise RelaxNoneStrListStrError:    If not a string, a list of strings, or None.
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # A string.
    if not isinstance(arg, list):
        # Check if it is a string.
        try:
            is_str(arg, name)
        except:
            fail = True    # Not a string.

    # A list.
    else:
        # Fail size is wrong.
        if size != None and len(arg) != size:
            fail = True

        # Fail if empty.
        if not can_be_empty and arg == []:
            fail = True

       # Check the arguments.
        for i in range(len(arg)):
            # Check if it is a string.
            try:
                is_str(arg[i], name)
            except:
                fail = True    # Not a string.

    # Fail.
    if fail:
        if can_be_none and size != None:
            raise RelaxNoneStrListStrError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneStrListStrError(name, arg)
        elif size != None:
            raise RelaxStrListStrError(name, arg, size)
        else:
            raise RelaxStrListStrError(name, arg)


def is_tuple(arg, name, size=None, can_be_none=False, can_be_empty=False):
    """Test if the argument is a tuple.

    @param arg:                 The argument.
    @type arg:                  anything
    @param name:                The plain English name of the argument.
    @type name:                 str
    @keyword size:              The number of elements required.
    @type size:                 None or int
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword can_be_empty:      A flag which if True allows the list to be empty.
    @type can_be_empty:         bool
    @raise RelaxTupleError:     If not a tuple.
    @raise RelaxNoneTupleError: If not a tuple or not None.
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return

    # Fail if not a tuple.
    if not isinstance(arg, tuple):
        fail = True

    # Other checks.
    else:
        # Fail size is wrong.
        if size != None and len(arg) != size:
            fail = True

        # Fail if empty.
        if not can_be_empty and arg == []:
            fail = True

    # Fail.
    if fail:
        if can_be_none and size != None:
            raise RelaxNoneTupleError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneTupleError(name, arg)
        elif size != None:
            raise RelaxTupleError(name, arg, size)
        else:
            raise RelaxTupleError(name, arg)
