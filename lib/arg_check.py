###############################################################################
#                                                                             #
# Copyright (C) 2009-2014,2019 Edward d'Auvergne                              #
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
import itertools
from numpy import float64, int32, ndarray

# relax module imports.
import lib.check_types
from lib.errors import RelaxError, \
        RelaxArrayError, \
        RelaxArrayFloatError, \
        RelaxArrayIntError, \
        RelaxArrayNumError, \
        RelaxBoolError, \
        RelaxBoolListBoolError, \
        RelaxFloatError, \
        RelaxFunctionError, \
        RelaxIntError, \
        RelaxIntListIntError, \
        RelaxInvalidError, \
        RelaxListError, \
        RelaxListBoolError, \
        RelaxListFloatError, \
        RelaxListIntError, \
        RelaxListNumError, \
        RelaxListStrError, \
        RelaxMatrixFloatError, \
        RelaxNoneError, \
        RelaxNoneBoolError, \
        RelaxNoneBoolListBoolError, \
        RelaxNoneFloatError, \
        RelaxNoneFunctionError, \
        RelaxNoneIntError, \
        RelaxNoneIntListIntError, \
        RelaxNoneListError, \
        RelaxNoneListFloatError, \
        RelaxNoneListIntError, \
        RelaxNoneListNumError, \
        RelaxNoneListStrError, \
        RelaxNoneMatrixFloatError, \
        RelaxNoneNumError, \
        RelaxNoneNumStrListNumStrError, \
        RelaxNoneNumTupleNumError, \
        RelaxNoneStrError, \
        RelaxNoneStrFileError, \
        RelaxNoneStrListNumError, \
        RelaxNoneStrListStrError, \
        RelaxNoneTupleError, \
        RelaxNoneTupleNumError, \
        RelaxNoneValListValError, \
        RelaxNumError, \
        RelaxNumStrListNumStrError, \
        RelaxNumTupleNumError, \
        RelaxNumpyFloatError, \
        RelaxNumpyIntError, \
        RelaxNumpyNumError, \
        RelaxStrError, \
        RelaxStrFileError, \
        RelaxStrListNumError, \
        RelaxStrListStrError, \
        RelaxTupleError, \
        RelaxTupleNumError, \
        RelaxValListValError
from lib.io import DummyFileObject
from types import FunctionType, MethodType


def is_bool(arg, name=None, can_be_none=False, raise_error=True):
    """Test if the argument is a Boolean.

    @param arg:                 The argument.
    @type arg:                  anything
    @keyword name:              The plain English name of the argument.
    @type name:                 str
    @keyword can_be_none:       A flag specifying if the argument can be none.
    @type can_be_none:          bool
    @keyword raise_error:       A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:          bool
    @raise RelaxBoolError:      If not a Boolean (and the raise_error flag is set).
    @raise RelaxNoneBoolError:  If not a Boolean or None (and the raise_error flag is set).
    @return:                    The answer to the question (if raise_error is not set).
    @rtype:                     bool
    """

    # Check for a Boolean.
    if isinstance(arg, bool):
        return True

    # An argument of None is allowed.
    if can_be_none and arg is None:
        return True

    # Fail.
    if not raise_error:
        return False
    if not can_be_none:
        raise RelaxBoolError(name, arg)
    else:
        raise RelaxNoneBoolError(name, arg)


def is_bool_or_bool_list(arg, name=None, size=None, can_be_none=False, can_be_empty=False, none_elements=False, raise_error=True):
    """Test if the argument is a Boolean or a list of Booleans.

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
    @raise RelaxBoolListBoolError:      If not a Boolean or a list of Booleans (and the raise_error flag is set).
    @raise RelaxNoneBoolListBoolError:  If not a Boolean, a list of Booleans, or None (and the raise_error flag is set).
    @return:                            The answer to the question (if raise_error is not set).
    @rtype:                             bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg is None:
        return True

    # A Boolean.
    if not isinstance(arg, list):
        if not is_bool(arg, raise_error=False):
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

            # Check if it is a Boolean.
            if not is_bool(arg[i], raise_error=False):
                fail = True

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneBoolListBoolError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneBoolListBoolError(name, arg)
        elif size != None:
            raise RelaxBoolListBoolError(name, arg, size)
        else:
            raise RelaxBoolListBoolError(name, arg)

    # Success.
    return True


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
    if can_be_none and arg is None:
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
    """Test if the argument is a list or a numpy array of floats.

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
    if can_be_none and arg is None:
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
    if can_be_none and arg is None:
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
            if arg[i] is None:
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
    if can_be_none and arg is None:
        return True

    # Flatten the structure and determine its rank and dimensionality.
    flat = arg
    rank = 1
    shape = []
    if isinstance(arg, list) and len(arg):
        shape.append(len(arg))
        while 1:
            if isinstance(flat[0], list) and len(flat[0]):
                shape.append(len(flat[0]))
                for element in flat:
                    if shape[-1] != len(element):
                        shape[-1] == None
                flat = list(itertools.chain.from_iterable(flat))
                rank += 1
            else:
                break
    if isinstance(arg, ndarray):
        flat = arg.flatten()
        shape = arg.shape
        rank = len(shape)
    shape = tuple(shape)

    # Fail if not a list or numpy array.
    if not isinstance(arg, list) and not isinstance(arg, ndarray):
        fail = True

    # Fail if not the right rank.
    elif dim != None and len(dim) != rank:
        fail = True

    # Fail if not the right dimensionality.
    elif dim != None and dim != shape:
        fail = True

    # Individual element checks.
    else:
        for i in range(len(flat)):
            if not lib.check_types.is_float(flat[i]):
                fail = True
                break

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
    if can_be_none and arg is None:
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
    if can_be_none and arg is None:
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
    @keyword none_elements:         A flag which if True allows the list to contain None.
    @type none_elements:            bool
    @keyword list_of_lists:         A flag which if True allows the argument to be a list of lists.
    @type list_of_lists:            bool
    @keyword raise_error:           A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:              bool
    @raise RelaxListIntError:       If not a list of integers (and the raise_error flag is set).
    @raise RelaxNoneListIntError:   If a list of integers or None (and the raise_error flag is set).
    @return:                        The answer to the question (if raise_error is not set).
    @rtype:                         bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg is None:
        return True

    # Fail if not a list.
    if not isinstance(arg, list):
        fail = True

    # Fail size is wrong.
    elif size != None and len(arg) != size:
        fail = True

    # Fail if empty.
    elif not can_be_empty and len(arg) == 0:
        fail = True

    # Fail if not ints.
    elif len(arg):
        for element in arg:
            # None.
            if element == None and none_elements:
                continue

            # Booleans.
            if isinstance(element, bool):
                fail = True
                break

            # List of lists.
            if list_of_lists and isinstance(element, list):
                for i in range(len(element)):
                    if not isinstance(element[i], int):
                        fail = True
                        break

            # Simple list.
            elif not isinstance(element, int):
                fail = True
                break

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
    if can_be_none and arg is None:
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
    @raise RelaxListError:          If not a list (and the raise_error flag is set).
    @raise RelaxNoneListError:      If not a list or None (and the raise_error flag is set).
    @return:                        The answer to the question (if raise_error is not set).
    @rtype:                         bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg is None:
        return True

    # Fail if not a list.
    if not isinstance(arg, list):
        fail = True

    # Fail size is wrong.
    elif size != None and len(arg) != size:
        fail = True

    # Fail if empty.
    elif not can_be_empty and len(arg) == 0:
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
    if can_be_none and arg is None:
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
    if arg is None:
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
    if can_be_none and arg is None:
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
    """Test if the argument is a list or numpy array of numbers.

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
    @keyword raise_error:           A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:              bool
    @raise RelaxListNumError:       If not a list of numbers (and the raise_error flag is set).
    @raise RelaxNoneListNumError:   If not a list of numbers or None (and the raise_error flag is set).
    @return:                        The answer to the question (if raise_error is not set).
    @rtype:                         bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg is None:
        return True

    # Fail if not a list or numpy array.
    if not isinstance(arg, list) and not isinstance(arg, ndarray):
        fail = True

    # Fail size is wrong.
    elif size != None and len(arg) != size:
        fail = True

    # Fail if empty.
    elif not can_be_empty and len(arg) == 0:
        fail = True

    # Fail if not numbers.
    elif len(arg):
        for element in arg:
            if isinstance(element, bool):
                fail = True
                break

            if not lib.check_types.is_float(element) and not isinstance(element, int):
                fail = True
                break

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
    @raise RelaxNumTupleNumError:       If not a number or a tuple (and the raise_error flag is set).
    @raise RelaxNoneNumTupleNumError:   If not a number, tuple of numbers, or None (and the raise_error flag is set).
    @return:                            The answer to the question (if raise_error is not set).
    @rtype:                             bool
    """

    # Init.
    fail = False
    if size != None and not isinstance(size, list):
        size = [size]

    # An argument of None is allowed.
    if can_be_none and arg is None:
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
    @keyword raise_error:           A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:              bool
    @raise RelaxTupleNumError:      If not a tuple of number (and the raise_error flag is set).
    @raise RelaxNoneTupleNumError:  If not a tuple of numbers or None (and the raise_error flag is set).
    @return:                        The answer to the question (if raise_error is not set).
    @rtype:                         bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg is None:
        return True

    # Fail if not a tuple.
    if not isinstance(arg, tuple):
        fail = True

    # Fail size is wrong.
    elif size != None and len(arg) != size:
        fail = True

    # Fail if empty.
    elif not can_be_empty and len(arg) == 0:
        fail = True

    # Fail if not numbers.
    elif len(arg):
        for element in arg:
            if isinstance(element, bool):
                fail = True
                break

            if not lib.check_types.is_float(element) and not isinstance(element, int):
                fail = True
                break

    # Fail.
    if fail:
        if not raise_error:
            return False
        if can_be_none and size != None:
            raise RelaxNoneTupleNumError(name, arg, size)
        elif can_be_none:
            raise RelaxNoneTupleNumError(name, arg)
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
    if can_be_none and arg is None:
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
    if can_be_none and arg is None:
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
    """Test if the argument is a string or writable instance (file-like object).

    @param arg:                     The argument.
    @type arg:                      anything
    @keyword name:                  The plain English name of the argument.
    @type name:                     str
    @keyword can_be_none:           A flag specifying if the argument can be none.
    @type can_be_none:              bool
    @keyword raise_error:           A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:              bool
    @raise RelaxStrFileError:       If not a string or writeable instance (and the raise_error flag is set).
    @raise RelaxNoneStrFileError:   If not a string, writeable instance or not None (and the raise_error flag is set).
    @return:                        The answer to the question (if raise_error is not set).
    @rtype:                         bool
    """

    # An argument of None is allowed.
    if can_be_none and arg is None:
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
    if can_be_none and arg is None:
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
    @raise RelaxStrListNumError:        If not a string or a list of numbers (and the raise_error flag is set).
    @raise RelaxNoneStrListNumError:    If not a string, a list of numbers, or None (and the raise_error flag is set).
    @return:                            The answer to the question (if raise_error is not set).
    @rtype:                             bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg is None:
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
    if can_be_none and arg is None:
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
    if can_be_none and arg is None:
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
    """Test if the argument is a value (bool, str, or number) or a list of values.

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
    @raise RelaxValListValError:        If not a value or list of values (and the raise_error flag is set).
    @raise RelaxNoneValListValError:    If not a value, a list of values, or None (and the raise_error flag is set).
    @return:                            The answer to the question (if raise_error is not set).
    @rtype:                             bool
    """

    # Init.
    fail = False

    # An argument of None is allowed.
    if can_be_none and arg is None:
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


def validate_arg(arg, name=None, dim=tuple(), basic_types=[], container_types=[], can_be_none=False, can_be_empty=False, raise_error=True):
    """Generic validation function for any argument type.

    This function can be used to validate the value of any argument, raising a RelaxError specific
    for the argument for detailed user feedback.

    Types
    =====

    The basic Python data types allowed for the argument are specified via the basic_types argument.
    The currently supported values include:

        - bool
        - float
        - func
        - int
        - number
        - str

    The 'number' value is special in that it allows for both 'int' and 'float' values.  If the
    argument should be a higher rank object, then the container_types argument should be supplied.
    The allowed values currently include:

        - list
        - number array
        - numpy array
        - set
        - tuple

    Here, the 'number array' is also special and allows for both 'list' and 'numpy array'
    containers.  Note that only the basic types 'float', 'int', and 'number' are allowed with this
    value.


    Rank and dimensionality
    =======================

    To distinguish between basic Python data types and higher rank container types, as well as
    fixing the dimensionality of the higher rank objects, the 'dim' parameter should be supplied.
    This should be a tuple with elements consisting of integers or None.  If multiple ranks or
    dimensionality are allowed, then a list of tuples can be supplied.


    Rank
    ----

    The number of elements of the 'dim' tuples define the rank.  For example a number is rank 0, a
    vector is rank 1, and a matrix is rank 2.


    Dimensionality
    --------------

    The dimensionality, or number of elements, for each rank are fixed by supplying integers in the
    'dim' tuple.  If the dimensionality can be variable, the value of None should be supplied
    instead.


    Examples
    --------

    For basic Python data types, use the empty tuple:

        - dim=()

    For a list of basic data types of unknown length, use:

        - dim=(None,)

    For a numpy array of 5 elements, use:

        - dim=(5,)

    For a numpy 3D matrix, use:

        - dim=(3,3)


    Fall back error
    ===============

    For arguments which do not currently have a specific RelaxError for telling the user what the
    did wrong, the fall back RelaxInvalidError object will be raised.  If more detailed feedback to
    the user is desired, then a new RelaxError object should be created and added in the failure
    section of this function.


    @param arg:                         The argument.
    @type arg:                          anything
    @keyword name:                      The plain English name of the argument, used in the RelaxError printout.
    @type name:                         str
    @keyword dim:                       The dimensions of the object to check.
    @type dim:                          tuple of (int or None) or list of tuples of (int or None)
    @keyword basic_types:               The types of values are allowed for the argument.
    @type basic_types:                  list of str
    @keyword container_types:           The container types allowed for the argument.
    @type container_types:              list of str
    @keyword can_be_none:               A flag specifying if the argument can be none.
    @type can_be_none:                  bool
    @keyword can_be_empty:              A flag which if True allows container types to be empty.
    @type can_be_empty:                 bool
    @keyword raise_error:               A flag which if True will cause RelaxErrors to be raised.
    @type raise_error:                  bool
    @raise RelaxListError:              If a list of different basic types was expected (and the raise_error flag is set)
    @raise RelaxNoneListError:          If a list of different basic types or no argument was expected (and the raise_error flag is set)
    @raise RelaxInvalidError:           For all argument combinations that do not have a specific RelaxError (and the raise_error flag is set).
    @return:                            The answer to the question (if raise_error is not set).
    @rtype:                             bool
    """

    # Init.
    fail = False

    # Checks.
    if 'number array' in container_types:
        for type in basic_types:
            if type not in ['float', 'int', 'number']:
                raise RelaxError("The 'number array' container type does not support the '%s' basic Python data type." % type)
    if 'number' in basic_types and ('int' in basic_types or 'float' in basic_types):
        raise RelaxError("The 'int' or 'float' basic data types cannot be supplied if 'number' is a basic type.")


    # Process the expected dimensionality.
    allowed_rank = []
    allowed_shape = []
    if isinstance(dim, list):
        for i in range(len(dim)):
            allowed_rank.append(len(dim[i]))
            allowed_shape.append(dim[i])
    else:
        allowed_rank.append(len(dim))
        allowed_shape.append(dim)

    # Determine the argument's rank and dimensionality, and create a flatten version of the structure.
    flat = arg
    shape = []
    rank = 1
    numpy_type = None
    if isinstance(arg, set):
        if 'set' not in container_types:
            fail = True
        shape = [len(arg)]
        flat = list(arg)
    elif isinstance(arg, list) or isinstance(arg, tuple):
        if isinstance(arg, list) and ('list' not in container_types and 'number array' not in container_types):
            fail = True
        if isinstance(arg, tuple) and 'tuple' not in container_types:
            fail = True
        shape.append(len(arg))
        while 1:
            if len(flat) and (isinstance(flat[0], list) or isinstance(flat[0], tuple)):
                shape.append(len(flat[0]))
                for element in flat:
                    if isinstance(element, list) and ('list' not in container_types and 'number array' not in container_types):
                        fail = True
                    if isinstance(element, tuple) and 'tuple' not in container_types:
                        fail = True
                    if shape[-1] != len(element):
                        shape[-1] == None
                flat = list(itertools.chain.from_iterable(flat))
                rank += 1
            else:
                break
        shape = tuple(shape)
    elif isinstance(arg, ndarray):
        if 'numpy array' not in container_types and 'number array' not in container_types:
            fail = True
        flat = arg.flatten()
        shape = arg.shape
        rank = len(shape)
        numpy_type = str(arg.dtype)
    else:
        flat = [arg]
        rank = 0
        shape = tuple()

    # Already failed, so skip.
    if fail:
        pass

    # Skip arguments of None when None is allowed.
    elif can_be_none and arg == None:
        pass

    # Fail if empty.
    elif rank and shape[-1] == 0 and not can_be_empty:
        fail = True

    # Fail if not the right rank.
    elif rank not in allowed_rank:
        fail = True

    # Fail if not the right dimensionality.
    elif shape not in allowed_shape:
        index = allowed_rank.index(rank)
        for i in range(rank):
            if allowed_shape[index][i] != None and allowed_shape[index][i] != shape[i]:
                fail = True

    # Type checking (skip if the argument can be, and is, None).
    if not fail and not (can_be_none and arg == None):
        # Numpy types.
        if numpy_type:
            # Integers.
            if numpy_type == 'int32' and 'int' not in basic_types and 'number' not in basic_types:
                fail = True

            # Floats.
            elif numpy_type == 'float64' and 'float' not in basic_types and 'number' not in basic_types:
                fail = True


        # Individual element checks.
        for element in flat:
            # Booleans.
            if isinstance(element, bool):
                if 'bool' not in basic_types:
                    fail = True

            # Integers.
            elif isinstance(element, int) or isinstance(element, int32):
                if 'int' not in basic_types and 'number' not in basic_types:
                    fail = True

            # Floats.
            elif isinstance(element, float) or isinstance(element, float64):
                if 'float' not in basic_types and 'number' not in basic_types:
                    fail = True

            # Strings.
            elif isinstance(element, str):
                if 'str' not in basic_types:
                    fail = True

            # Functions.
            elif isinstance(element, FunctionType) or isinstance(element, MethodType):
                if 'func' not in basic_types:
                    fail = True

            # Unhandled type.
            else:
                fail = True

            # No need to continue.
            if fail:
                break

    # Failure.
    if fail:
        # No error.
        if not raise_error:
            return False

        # Multiple types.
        if len(basic_types) > 1:
            # Array types.
            if len(allowed_rank) == 1 and 1 in allowed_rank:
                # List or numpy array.
                if 'list' in container_types and 'numpy array' in container_types:
                    raise RelaxArrayError(name, arg, can_be_none=can_be_none)

                # Lists.
                elif 'list' in container_types:
                    raise RelaxListError(name, arg, can_be_none=can_be_none)

                # Numpy arrays.
                elif 'numpy array' in container_types:
                    raise RelaxNumpyNumError(name, arg, can_be_none=can_be_none)

        # Boolean errors.
        elif 'bool' in basic_types:
            # Boolean or list of Booleans.
            if len(allowed_rank) == 2 and 0 in allowed_rank and 1 in allowed_rank:
                raise RelaxBoolListBoolError(name, arg, can_be_none=can_be_none)

            # Basic Boolean type.
            elif len(allowed_rank) == 1 and 0 in allowed_rank:
                raise RelaxBoolError(name, arg, can_be_none=can_be_none)

            # Boolean list.
            elif len(allowed_rank) == 1 and 1 in allowed_rank:
                raise RelaxListBoolError(name, arg, can_be_none=can_be_none)

        # Float errors.
        elif 'float' in basic_types:
            # Basic float type.
            if len(allowed_rank) == 1 and 0 in allowed_rank:
                raise RelaxFloatError(name, arg, can_be_none=can_be_none)

            # List or numpy array of floats.
            elif 'number array' in container_types:
                raise RelaxArrayFloatError(name, arg, dim=dim, can_be_none=can_be_none)

            # Numpy integer array.
            elif 'numpy array' in container_types:
                raise RelaxNumpyFloatError(name, arg, dim=dim, can_be_none=can_be_none)

            # List of floats.
            elif len(allowed_rank) == 1 and 1 in allowed_rank:
                raise RelaxListFloatError(name, arg, can_be_none=can_be_none)

        # Integer errors.
        elif 'int' in basic_types:
            # Integer or list of integers.
            if len(allowed_rank) == 2 and 0 in allowed_rank and 1 in allowed_rank:
                raise RelaxIntListIntError(name, arg, can_be_none=can_be_none)

            # Basic integer type.
            elif len(allowed_rank) == 1 and 0 in allowed_rank:
                raise RelaxIntError(name, arg, can_be_none=can_be_none)

            # List or numpy array of integers.
            elif 'number array' in container_types:
                raise RelaxArrayIntError(name, arg, dim=dim, can_be_none=can_be_none)

            # Numpy integer array.
            elif 'numpy array' in container_types:
                raise RelaxNumpyIntError(name, arg, dim=dim, can_be_none=can_be_none)

            # Integer list.
            elif len(allowed_rank) == 1 and 1 in allowed_rank:
                raise RelaxListIntError(name, arg, can_be_none=can_be_none)


        # Number errors.
        elif 'number' in basic_types:
            # Rank-0.
            if len(container_types) == 0:
                raise RelaxNumError(name, arg, can_be_none=can_be_none)

            # Mixed types.
            elif len(container_types) > 1:
                pass

            # List or numpy array of numbers.
            elif 'number array' in container_types:
                raise RelaxArrayNumError(name, arg, dim=dim, can_be_none=can_be_none)

            # Numpy arrays.
            elif 'numpy array' in container_types:
                raise RelaxNumpyNumError(name, arg, dim=dim, can_be_none=can_be_none)

            # List of numbers.
            elif 'list' in container_types:
                raise RelaxListNumError(name, arg, dim=dim, can_be_none=can_be_none)

        # String errors.
        elif 'str' in basic_types:
            # String or list of strings.
            if len(allowed_rank) == 2 and 0 in allowed_rank and 1 in allowed_rank:
                raise RelaxStrListStrError(name, arg, can_be_none=can_be_none)

            # Basic string type.
            elif len(allowed_rank) == 1 and 0 in allowed_rank:
                raise RelaxStrError(name, arg, can_be_none=can_be_none)

            # List of strings.
            elif len(allowed_rank) == 1 and 1 in allowed_rank:
                raise RelaxListStrError(name, arg, can_be_none=can_be_none)

        # Function errors.
        elif 'func' in basic_types:
            # Basic function type.
            if len(allowed_rank) == 1 and 0 in allowed_rank:
                raise RelaxFunctionError(name, arg, can_be_none=can_be_none)

        # Final fall back.
        raise RelaxInvalidError(name, arg)

    # Success.
    return True
