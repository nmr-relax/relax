###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""Argument checking functions for the relax user functions."""

# Python module imports.
from numpy import ndarray

# relax module imports.
import lib.check_types
from lib.errors import RelaxBoolError, RelaxFloatError, RelaxFunctionError, RelaxIntError, RelaxIntListIntError, RelaxListFloatError, RelaxListIntError, RelaxMatrixFloatError, RelaxNoneFloatError, RelaxNoneFunctionError, RelaxListNumError, RelaxListStrError, RelaxNoneError, RelaxNoneIntError, RelaxNoneIntListIntError, RelaxNoneListFloatError, RelaxNoneListIntError, RelaxNoneMatrixFloatError, RelaxNoneListNumError, RelaxNoneListStrError, RelaxNoneNumError, RelaxNoneNumStrListNumStrError, RelaxNoneNumTupleNumError, RelaxNoneStrError, RelaxNoneStrFileError, RelaxNoneStrListNumError, RelaxNoneStrListStrError, RelaxNoneTupleError, RelaxNumError, RelaxNumStrListNumStrError, RelaxNumTupleNumError, RelaxStrError, RelaxStrFileError, RelaxStrListNumError, RelaxStrListStrError, RelaxTupleError, RelaxTupleNumError, RelaxNoneValListValError, RelaxValListValError
from lib.io import DummyFileObject
from types import FunctionType, MethodType


def is_bool(arg, name=None, raise_error=True):
    """Test if the argument is a Boolean.

    @param arg:                 The argument.
    @type arg:                  anything
    @keyword name:              The plain English name of the argument.
    @type name:                 str
    @keyword raise_error:       A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:          bool
    @raise RelaxBoolError:      If not a Boolean (and the raise_error flag is set).
    @return:                    The answer to the question (if raise_error is not set).
    @rtype:                     bool
    """

    # Check for a Boolean.
    if isinstance(arg, bool):
        return True

    # Fail.
    if not raise_error:
        return False
    else:
        raise RelaxBoolError(name, arg)


def is_float(arg, name=None, can_be_none=False, raise_error=True):
    """Test if the argument is a float.

    @param arg:                 The argument.
    @type arg:                  anything
    @keyword name:              The plain English name of the argument.
    @type name:                 str
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword raise_error:       A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:          bool
    @raise RelaxFloatError:     If not an integer (and the raise_error flag is set).
    @raise RelaxNoneFloatError: If not an integer or not None (and the raise_error flag is set).
    @return:                    The answer to the question (if raise_error is not set).
    @rtype:                     bool
    """

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # Check for a float.
    if lib.check_types.is_float(arg):
        return True

    # Fail.
    if not raise_error:
        return False
    if not can_be_none:
        raise RelaxFloatError(name, arg)
    else:
        raise RelaxNoneFloatError(name, arg)


def is_float_array(arg, name=None, size=None, can_be_none=False, raise_error=True):
    """Test if the argument is an array of floats.

    @param arg:                     The argument.
    @type arg:                      anything
    @keyword name:                  The plain English name of the argument.
    @type name:                     str
    @keyword size:                  The dimension of the array.
    @type size:                     None or int
    @keyword can_be_none:           A flag specifying if the argument can be none.
    @type can_be_none:              bool
    @keyword raise_error:           A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:              bool
    @raise RelaxListFloatError:     If not a matrix of floats (and the raise_error flag is set).
    @raise RelaxNoneListFloatError: If not a matrix of floats or not None (and the raise_error flag is set).
    @return:                        The answer to the question (if raise_error is not set).
    @rtype:                         bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

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
            if not lib.check_types.is_float(arg[i]):
                fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneListFloatError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneListFloatError(name, arg)
        elif size != None:
            raise RelaxListFloatError(name, arg, size)
        else:
            raise RelaxListFloatError(name, arg)

    # Success.
    return True


def is_float_matrix(arg, name=None, dim=None, can_be_none=False, none_elements=False, raise_error=True):
    """Test if the argument is a matrix of floats.

    @param arg:                         The argument.
    @type arg:                          anything
    @keyword name:                      The plain English name of the argument.
    @type name:                         str
    @keyword dim:                       The m,n dimensions of the matrix.
    @type dim:                          tuple of int
    @keyword can_be_none:               A flag specifying if the argument can be none.
    @type can_be_none:                  bool
    @keyword none_elements:             A flag which if True allows the list to contain None.
    @type none_elements:                bool
    @keyword raise_error:               A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:                  bool
    @raise RelaxMatrixFloatError:       If not a matrix of floats (and the raise_error flag is set).
    @raise RelaxNoneMatrixFloatError:   If not a matrix of floats or not None (and the raise_error flag is set).
    @return:                            The answer to the question (if raise_error is not set).
    @rtype:                             bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # Fail if not a list.
    if not isinstance(arg, list) and not isinstance(arg, ndarray):
        fail = True

    # Fail on empty lists.
    elif not len(arg):
        fail = True

    # Fail if not a matrix.
    elif not isinstance(arg[0], list) and not isinstance(arg[0], ndarray):
        fail = True

    # Fail if not the right dimension.
    elif dim != None and len(arg) != dim[0]:
        fail = True

    # Loop over the first dimension.
    else:
        for i in range(len(arg)):
            # Catch None elements.
            if arg[i] == None:
                if not none_elements:
                    fail = True
                continue

            # Fail if not a list.
            if not (isinstance(arg[i], list) or isinstance(arg[i], ndarray)):
                fail = True

            # Fail if not the right dimension.
            elif dim != None and len(arg[i]) != dim[1]:
                fail = True

            # Check for float elements.
            for j in range(len(arg[i])):
                if not lib.check_types.is_float(arg[i][j]):
                    fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and dim != None:
            raise RelaxNoneMatrixFloatError(name, arg, dim)
        elif can_be_none:
            raise RelaxNoneMatrixFloatError(name, arg)
        elif dim != None:
            raise RelaxMatrixFloatError(name, arg, dim)
        else:
            raise RelaxMatrixFloatError(name, arg)

    # Success.
    return True


def is_float_object(arg, name=None, dim=(3, 3), can_be_none=False, raise_error=True):
    """Test if the argument is a rank-N array of floats.

    @param arg:                         The argument.
    @type arg:                          anything
    @keyword name:                      The plain English name of the argument.
    @type name:                         str
    @keyword dim:                       The m,n dimensions of the matrix.
    @type dim:                          tuple of int
    @keyword can_be_none:               A flag specifying if the argument can be none.
    @type can_be_none:                  bool
    @keyword raise_error:               A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:                  bool
    @raise RelaxMatrixFloatError:       If not a matrix of floats (and the raise_error flag is set).
    @raise RelaxNoneMatrixFloatError:   If not a matrix of floats or not None (and the raise_error flag is set).
    @return:                            The answer to the question (if raise_error is not set).
    @rtype:                             bool
    """

    # Init.
    fail = False
    if isinstance(dim, int):
        dim = [dim]

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # Fail if not a list.
    if not isinstance(arg, list) and not isinstance(arg, ndarray):
        fail = True

    # Fail on empty lists.
    elif not len(arg):
        fail = True

    # Fail if not the right dimension.
    elif dim != None and len(arg) != dim[0]:
        fail = True

    # Fail if not a rank-2 array.
    elif dim != None and len(dim) == 2 and not isinstance(arg[0], list) and not isinstance(arg[0], ndarray):
        fail = True

    # Fail if not a rank-3 array.
    elif dim != None and len(dim) == 3 and not isinstance(arg[0][0], list) and not isinstance(arg[0][0], ndarray):
        fail = True

    # Fail if not a rank-4 array.
    elif dim != None and len(dim) == 4 and not isinstance(arg[0][0][0], list) and not isinstance(arg[0][0][0], ndarray):
        fail = True

    # Individual element checks.
    else:
        # Create a flat list.
        if isinstance(arg[0], list) or isinstance(arg[0], ndarray):
            elements = [item for sublist in arg for item in sublist]
        else:
            elements = arg

        # Check for float elements.
        for i in range(len(elements)):
            if not lib.check_types.is_float(elements[i]):
                fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and dim != None:
            raise RelaxNoneListFloatError(name, arg, dim)
        elif can_be_none:
            raise RelaxNoneListFloatError(name, arg)
        elif dim != None:
            raise RelaxListFloatError(name, arg, dim)
        else:
            raise RelaxListFloatError(name, arg)

    # Success.
    return True


def is_func(arg, name=None, can_be_none=False, raise_error=True):
    """Test if the argument is a function.

    @param arg:                     The argument.
    @type arg:                      anything
    @keyword name:                  The plain English name of the argument.
    @type name:                     str
    @keyword can_be_none:           A flag specifying if the argument can be none.
    @type can_be_none:              bool
    @keyword raise_error:           A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:              bool
    @raise RelaxFunctionError:      If not a function (and the raise_error flag is set).
    @raise RelaxNoneFunctionError:  If not a function or not None (and the raise_error flag is set).
    @return:                        The answer to the question (if raise_error is not set).
    @rtype:                         bool
    """

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # Check for a function.
    if isinstance(arg, FunctionType) or isinstance(arg, MethodType):
        return True

    # Fail.
    if not raise_error:
        return False
    if not can_be_none:
        raise RelaxFunctionError(name, arg)
    else:
        raise RelaxNoneFunctionError(name, arg)


def is_int(arg, name=None, can_be_none=False, raise_error=True):
    """Test if the argument is an integer.

    @param arg:                 The argument.
    @type arg:                  anything
    @keyword name:              The plain English name of the argument.
    @type name:                 str
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword raise_error:       A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:          bool
    @raise RelaxIntError:       If not an integer (and the raise_error flag is set).
    @raise RelaxNoneIntError:   If not an integer or not None (and the raise_error flag is set).
    @return:                    The answer to the question (if raise_error is not set).
    @rtype:                     bool
    """

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # Check for an integer (avoiding Booleans).
    if isinstance(arg, int) and not isinstance(arg, bool):
        return True

    # Fail.
    if not raise_error:
        return False
    if not can_be_none:
        raise RelaxIntError(name, arg)
    else:
        raise RelaxNoneIntError(name, arg)


def is_int_list(arg, name=None, size=None, can_be_none=False, can_be_empty=False, none_elements=False, list_of_lists=False, raise_error=True):
    """Test if the argument is a list of integers.

    @param arg:                         The argument.
    @type arg:                          anything
    @keyword name:                      The plain English name of the argument.
    @type name:                         str
    @keyword size:                      The number of elements required.
    @type size:                         None or int
    @keyword can_be_none:               A flag specifying if the argument can be none.
    @type can_be_none:                  bool
    @keyword can_be_empty:              A flag which if True allows the list to be empty.
    @type can_be_empty:                 bool
    @keyword none_elements:             A flag which if True allows the list to contain None.
    @type none_elements:                bool
    @keyword list_of_lists:             A flag which if True allows the argument to be a list of lists.
    @type list_of_lists:                bool
    @keyword raise_error:               A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:                  bool
    @raise RelaxIntListIntError:        If not an integer or a list of integers (and the raise_error flag is set).
    @raise RelaxNoneIntListIntError:    If not an integer, a list of integers, or None (and the raise_error flag is set).
    @return:                            The answer to the question (if raise_error is not set).
    @rtype:                             bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

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

        # Fail if not ints.
        for i in range(len(arg)):
            # None.
            if arg[i] == None and none_elements:
                continue

            # List of lists.
            if list_of_lists and isinstance(arg[i], list):
                for j in range(len(arg[i])):
                    if not isinstance(arg[i][j], int):
                        fail = True

            # Simple list.
            else:
                if not isinstance(arg[i], int):
                    fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneListIntError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneListIntError(name, arg)
        elif size != None:
            raise RelaxListIntError(name, arg, size)
        else:
            raise RelaxListIntError(name, arg)

    # Success.
    return True


def is_int_or_int_list(arg, name=None, size=None, can_be_none=False, can_be_empty=False, none_elements=False, raise_error=True):
    """Test if the argument is an integer or a list of integers.

    @param arg:                         The argument.
    @type arg:                          anything
    @keyword name:                      The plain English name of the argument.
    @type name:                         str
    @keyword size:                      The number of elements required.
    @type size:                         None or int
    @keyword can_be_none:               A flag specifying if the argument can be none.
    @type can_be_none:                  bool
    @keyword can_be_empty:              A flag which if True allows the list to be empty.
    @type can_be_empty:                 bool
    @keyword none_elements:             A flag which if True allows the list to contain None.
    @type none_elements:                bool
    @keyword raise_error:               A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:                  bool
    @raise RelaxIntListIntError:        If not an integer or a list of integers (and the raise_error flag is set).
    @raise RelaxNoneIntListIntError:    If not an integer, a list of integers, or None (and the raise_error flag is set).
    @return:                            The answer to the question (if raise_error is not set).
    @rtype:                             bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # An integer
    if not isinstance(arg, list):
        if not is_int(arg, raise_error=False):
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
            if not is_int(arg[i], raise_error=False):
                fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneIntListIntError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneIntListIntError(name, arg)
        elif size != None:
            raise RelaxIntListIntError(name, arg, size)
        else:
            raise RelaxIntListIntError(name, arg)

    # Success.
    return True


def is_list(arg, name=None, size=None, can_be_none=False, can_be_empty=False, list_of_lists=False, raise_error=True):
    """Test if the argument is a list.

    @param arg:                     The argument.
    @type arg:                      anything
    @keyword name:                  The plain English name of the argument.
    @type name:                     str
    @keyword size:                  The number of elements required.
    @type size:                     None or int
    @keyword can_be_none:           A flag specifying if the argument can be none.
    @type can_be_none:              bool
    @keyword can_be_empty:          A flag which if True allows the list to be empty.
    @type can_be_empty:             bool
    @keyword list_of_lists:         A flag which if True allows the argument to be a list of lists of strings.
    @type list_of_lists:            bool
    @keyword raise_error:           A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:              bool
    @raise RelaxListStrError:       If not a list of strings (and the raise_error flag is set).
    @raise RelaxNoneListStrError:   If not a list of strings or None (and the raise_error flag is set).
    @return:                        The answer to the question (if raise_error is not set).
    @rtype:                         bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

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
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneListError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneListError(name, arg)
        elif size != None:
            raise RelaxListError(name, arg, size)
        else:
            raise RelaxListError(name, arg)

    # Success.
    return True


def is_list_val_or_list_of_list_val(arg, name=None, size=None, can_be_none=False, can_be_empty=False, list_of_lists=False, raise_error=True):
    """Test if the argument is a list of values or list of list with values.

    @param arg:                             The argument.
    @type arg:                              anything
    @keyword name:                          The plain English name of the argument.
    @type name:                             str
    @keyword size:                          The number of elements required.
    @type size:                             None or int
    @keyword can_be_none:                   A flag specifying if the argument can be none.
    @type can_be_none:                      bool
    @keyword can_be_empty:                  A flag which if True allows the list to be empty.
    @type can_be_empty:                     bool
    @keyword list_of_lists:                 A flag which if True allows the argument to be a list of lists of values.
    @type list_of_lists:                    bool
    @keyword raise_error:                   A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:                      bool
    @raise RelaxNumStrListNumStrError:      If not a float, a string, or a list of floats or strings (and the raise_error flag is set).
    @raise RelaxNoneNumStrListNumStrError:  If not a float, a string, a list of floats or strings, or None (and the raise_error flag is set).
    @return:                                The answer to the question (if raise_error is not set).
    @rtype:                                 bool
    """

    # FIXME:  This still needs to be implemented as a check for is_list_val_or_list_of_list_val:

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # A list.
    if not isinstance(arg, list):
        fail = True

    # Success.
    return True


def is_none(arg, name, raise_error=True):
    """Test if the argument is None.

    @param arg:                 The argument.
    @type arg:                  anything
    @keyword name:              The plain English name of the argument.
    @type name:                 str
    @keyword raise_error:       A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:          bool
    @raise RelaxNoneError:      If not None (and the raise_error flag is set).
    @return:                    The answer to the question (if raise_error is not set).
    @rtype:                     bool
    """

    # Check for None.
    if arg == None:
        return True

    # Fail.
    if not raise_error:
        return False
    else:
        raise RelaxNoneError(name)


def is_num(arg, name=None, can_be_none=False, raise_error=True):
    """Test if the argument is a number.

    @param arg:                 The argument.
    @type arg:                  anything
    @keyword name:              The plain English name of the argument.
    @type name:                 str
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword raise_error:       A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:          bool
    @raise RelaxNumError:       If not a number (and the raise_error flag is set).
    @raise RelaxNoneNumError:   If not a number or not None (and the raise_error flag is set).
    @return:                    The answer to the question (if raise_error is not set).
    @rtype:                     bool
    """

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # Check for floats and integers (avoiding Booleans).
    if (lib.check_types.is_float(arg) or isinstance(arg, int)) and not isinstance(arg, bool):
        return True

    # Fail.
    if not raise_error:
        return False
    if not can_be_none:
        raise RelaxNumError(name, arg)
    else:
        raise RelaxNoneNumError(name, arg)


def is_num_list(arg, name=None, size=None, can_be_none=False, can_be_empty=False, raise_error=True):
    """Test if the argument is a list of numbers.

    @param arg:                 The argument.
    @type arg:                  anything
    @keyword name:              The plain English name of the argument.
    @type name:                 str
    @keyword size:              The number of elements required.
    @type size:                 None or int
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword can_be_empty:      A flag which if True allows the list to be empty.
    @type can_be_empty:         bool
    @keyword raise_error:       A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:          bool
    @raise RelaxListError:      If not a list (and the raise_error flag is set).
    @raise RelaxListNumError:   If not a list of numbers (and the raise_error flag is set).
    @return:                    The answer to the question (if raise_error is not set).
    @rtype:                     bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

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
            if (not lib.check_types.is_float(arg[i]) and not isinstance(arg[i], int)) or isinstance(arg, bool):
                fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneListNumError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneListNumError(name, arg)
        elif size != None:
            raise RelaxListNumError(name, arg, size)
        else:
            raise RelaxListNumError(name, arg)

    # Success.
    return True


def is_num_or_num_tuple(arg, name=None, size=None, can_be_none=False, can_be_empty=False, raise_error=True):
    """Test if the argument is a tuple of numbers.

    @param arg:                 The argument.
    @type arg:                  anything
    @keyword name:              The plain English name of the argument.
    @type name:                 str
    @keyword size:              The number of elements required.
    @type size:                 None or int
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword can_be_empty:      A flag which if True allows the list to be empty.
    @type can_be_empty:         bool
    @keyword raise_error:       A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:          bool
    @raise RelaxTupleError:     If not a tuple (and the raise_error flag is set).
    @raise RelaxTupleNumError:  If not a tuple of numbers (and the raise_error flag is set).
    @return:                    The answer to the question (if raise_error is not set).
    @rtype:                     bool
    """

    # Init.
    fail = False
    if size != None and not isinstance(size, list):
        size = [size]

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # A number.
    if not isinstance(arg, tuple):
        if not is_num(arg, raise_error=False):
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
            if not (is_num(arg[i], raise_error=False) or (can_be_none and arg[i] == None)):
                fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneNumTupleNumError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneNumTupleNumError(name, arg)
        elif size != None:
            raise RelaxNumTupleNumError(name, arg, size)
        else:
            raise RelaxNumTupleNumError(name, arg)

    # Success.
    return True


def is_num_tuple(arg, name=None, size=None, can_be_none=False, can_be_empty=False, raise_error=True):
    """Test if the argument is a tuple of numbers.

    @param arg:                 The argument.
    @type arg:                  anything
    @keyword name:              The plain English name of the argument.
    @type name:                 str
    @keyword size:              The number of elements required.
    @type size:                 None or int
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword can_be_empty:      A flag which if True allows the list to be empty.
    @type can_be_empty:         bool
    @keyword raise_error:       A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:          bool
    @raise RelaxTupleError:     If not a tuple (and the raise_error flag is set).
    @raise RelaxTupleNumError:  If not a tuple of numbers (and the raise_error flag is set).
    @return:                    The answer to the question (if raise_error is not set).
    @rtype:                     bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

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
            if (not lib.check_types.is_float(arg[i]) and not isinstance(arg[i], int)) or isinstance(arg, bool):
                fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneNumTupleNumError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneNumTupleNumError(name, arg)
        elif size != None:
            raise RelaxTupleNumError(name, arg, size)
        else:
            raise RelaxTupleNumError(name, arg)

    # Success.
    return True


def is_str(arg, name=None, can_be_none=False, raise_error=True):
    """Test if the argument is a string.

    @param arg:                 The argument.
    @type arg:                  anything
    @keyword name:              The plain English name of the argument.
    @type name:                 str
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword raise_error:       A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:          bool
    @raise RelaxStrError:       If not an integer (and the raise_error flag is set).
    @raise RelaxNoneStrError:   If not an integer or not None (and the raise_error flag is set).
    @return:                    The answer to the question (if raise_error is not set).
    @rtype:                     bool
    """

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # Check for a string.
    if isinstance(arg, str):
        return True

    # Fail.
    if not raise_error:
        return False
    if not can_be_none:
        raise RelaxStrError(name, arg)
    else:
        raise RelaxNoneStrError(name, arg)


def is_str_list(arg, name=None, size=None, can_be_none=False, can_be_empty=False, list_of_lists=False, raise_error=True):
    """Test if the argument is a list of strings.

    @param arg:                     The argument.
    @type arg:                      anything
    @keyword name:                  The plain English name of the argument.
    @type name:                     str
    @keyword size:                  The number of elements required.
    @type size:                     None or int
    @keyword can_be_none:           A flag specifying if the argument can be none.
    @type can_be_none:              bool
    @keyword can_be_empty:          A flag which if True allows the list to be empty.
    @type can_be_empty:             bool
    @keyword list_of_lists:         A flag which if True allows the argument to be a list of lists of strings.
    @type list_of_lists:            bool
    @keyword raise_error:           A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:              bool
    @raise RelaxListStrError:       If not a list of strings (and the raise_error flag is set).
    @raise RelaxNoneListStrError:   If not a list of strings or None (and the raise_error flag is set).
    @return:                        The answer to the question (if raise_error is not set).
    @rtype:                         bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

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
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneListStrError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneListStrError(name, arg)
        elif size != None:
            raise RelaxListStrError(name, arg, size)
        else:
            raise RelaxListStrError(name, arg)

    # Success.
    return True


def is_str_or_inst(arg, name=None, can_be_none=False, raise_error=True):
    """Test if the argument is a string.

    @param arg:                 The argument.
    @type arg:                  anything
    @keyword name:              The plain English name of the argument.
    @type name:                 str
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword raise_error:       A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:          bool
    @raise RelaxStrError:       If not an integer (and the raise_error flag is set).
    @raise RelaxNoneStrError:   If not an integer or not None (and the raise_error flag is set).
    @return:                    The answer to the question (if raise_error is not set).
    @rtype:                     bool
    """

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # Check for a string.
    if isinstance(arg, str) or lib.check_types.is_filetype(arg) or isinstance(arg, DummyFileObject) or hasattr(arg, 'write'):
        return True

    # Fail.
    if not raise_error:
        return False
    if not can_be_none:
        raise RelaxStrFileError(name, arg)
    else:
        raise RelaxNoneStrFileError(name, arg)


def is_str_or_num_or_str_num_list(arg, name=None, size=None, can_be_none=False, can_be_empty=False, raise_error=True):
    """Test if the argument is a number, a string, a list of numbers, or a list of strings.

    @param arg:                             The argument.
    @type arg:                              anything
    @keyword name:                          The plain English name of the argument.
    @type name:                             str
    @keyword size:                          The number of elements required.
    @type size:                             None or int
    @keyword can_be_none:                   A flag specifying if the argument can be none.
    @type can_be_none:                      bool
    @keyword can_be_empty:                  A flag which if True allows the list to be empty.
    @type can_be_empty:                     bool
    @keyword raise_error:                   A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:                      bool
    @raise RelaxNumStrListNumStrError:      If not a float, a string, or a list of floats or strings (and the raise_error flag is set).
    @raise RelaxNoneNumStrListNumStrError:  If not a float, a string, a list of floats or strings, or None (and the raise_error flag is set).
    @return:                                The answer to the question (if raise_error is not set).
    @rtype:                                 bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # A number or a string.
    if not isinstance(arg, list):
        # Check if it is a string or number.
        if not (is_str(arg, raise_error=False) or is_num(arg, raise_error=False)):
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
            if not (is_str(arg[i], raise_error=False) or is_num(arg[i], raise_error=False)):
                fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneNumStrListNumStrError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneNumStrListNumStrError(name, arg)
        elif size != None:
            raise RelaxNumStrListNumStrError(name, arg, size)
        else:
            raise RelaxNumStrListNumStrError(name, arg)

    # Success.
    return True


def is_str_or_num_list(arg, name=None, size=None, can_be_none=False, can_be_empty=False, raise_error=True):
    """Test if the argument is a string or a list of numbers.

    @param arg:                         The argument.
    @type arg:                          anything
    @keyword name:                      The plain English name of the argument.
    @type name:                         str
    @keyword size:                      The number of elements required.
    @type size:                         None or int
    @keyword can_be_none:               A flag specifying if the argument can be none.
    @type can_be_none:                  bool
    @keyword can_be_empty:              A flag which if True allows the list to be empty.
    @type can_be_empty:                 bool
    @keyword raise_error:               A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:                  bool
    @raise RelaxStrListNumError:        If not a string or a list of strings (and the raise_error flag is set).
    @raise RelaxNoneStrListNumError:    If not a string, a list of strings, or None (and the raise_error flag is set).
    @return:                            The answer to the question (if raise_error is not set).
    @rtype:                             bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # A string.
    if not isinstance(arg, list):
        if not is_str(arg, raise_error=False):
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
            if not is_num(arg[i], raise_error=False):
                fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneStrListNumError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneStrListNumError(name, arg)
        elif size != None:
            raise RelaxStrListNumError(name, arg, size)
        else:
            raise RelaxStrListNumError(name, arg)

    # Success.
    return True


def is_str_or_str_list(arg, name=None, size=None, can_be_none=False, can_be_empty=False, raise_error=True):
    """Test if the argument is a string or a list of strings.

    @param arg:                         The argument.
    @type arg:                          anything
    @keyword name:                      The plain English name of the argument.
    @type name:                         str
    @keyword size:                      The number of elements required.
    @type size:                         None or int
    @keyword can_be_none:               A flag specifying if the argument can be none.
    @type can_be_none:                  bool
    @keyword can_be_empty:              A flag which if True allows the list to be empty.
    @type can_be_empty:                 bool
    @keyword raise_error:               A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:                  bool
    @raise RelaxStrListStrError:        If not a string or a list of strings (and the raise_error flag is set).
    @raise RelaxNoneStrListStrError:    If not a string, a list of strings, or None (and the raise_error flag is set).
    @return:                            The answer to the question (if raise_error is not set).
    @rtype:                             bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # A string.
    if not isinstance(arg, list):
        if not is_str(arg, raise_error=False):
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
            if not is_str(arg[i], raise_error=False):
                fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneStrListStrError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneStrListStrError(name, arg)
        elif size != None:
            raise RelaxStrListStrError(name, arg, size)
        else:
            raise RelaxStrListStrError(name, arg)

    # Success.
    return True


def is_tuple(arg, name=None, size=None, can_be_none=False, can_be_empty=False, raise_error=True):
    """Test if the argument is a tuple.

    @param arg:                 The argument.
    @type arg:                  anything
    @keyword name:              The plain English name of the argument.
    @type name:                 str
    @keyword size:              The number of elements required.
    @type size:                 None or int
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword can_be_empty:      A flag which if True allows the list to be empty.
    @type can_be_empty:         bool
    @keyword raise_error:       A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:          bool
    @raise RelaxTupleError:     If not a tuple (and the raise_error flag is set).
    @raise RelaxNoneTupleError: If not a tuple or not None (and the raise_error flag is set).
    @return:                    The answer to the question (if raise_error is not set).
    @rtype:                     bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

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
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneTupleError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneTupleError(name, arg)
        elif size != None:
            raise RelaxTupleError(name, arg, size)
        else:
            raise RelaxTupleError(name, arg)

    # Success.
    return True


def is_val_or_list(arg, name=None, size=None, can_be_none=False, can_be_empty=False, raise_error=True):
    """Test if the argument is a value or a list of values.

    @param arg:                             The argument.
    @type arg:                              anything
    @keyword name:                          The plain English name of the argument.
    @type name:                             str
    @keyword size:                          The number of elements required.
    @type size:                             None or int
    @keyword can_be_none:                   A flag specifying if the argument can be none.
    @type can_be_none:                      bool
    @keyword can_be_empty:                  A flag which if True allows the list to be empty.
    @type can_be_empty:                     bool
    @keyword raise_error:                   A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:                      bool
    @raise RelaxNumStrListNumStrError:      If not a float, a string, or a list of floats or strings (and the raise_error flag is set).
    @raise RelaxNoneNumStrListNumStrError:  If not a float, a string, a list of floats or strings, or None (and the raise_error flag is set).
    @return:                                The answer to the question (if raise_error is not set).
    @rtype:                                 bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg == None:
        return True

    # A value.
    if not isinstance(arg, list):
        # Check for all types of value.
        if not (is_bool(arg, raise_error=False) or is_str(arg, raise_error=False) or is_num(arg, raise_error=False)):
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
            # Check for all types of value.
            if not (is_bool(arg[i], raise_error=False) or is_str(arg[i], raise_error=False) or is_num(arg[i], raise_error=False)):
                fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneValListValError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneValListValError(name, arg)
        elif size != None:
            raise RelaxValListValError(name, arg, size)
        else:
            raise RelaxValListValError(name, arg)

    # Success.
    return True
