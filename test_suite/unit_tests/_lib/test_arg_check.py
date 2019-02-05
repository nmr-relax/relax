###############################################################################
#                                                                             #
# Copyright (C) 2019 Edward d'Auvergne                                        #
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

# Python module imports.
from numpy import array, float64, int32
from re import search
import sys

# relax module imports.
from lib.arg_check import is_bool, \
        is_bool_or_bool_list, \
        is_float, \
        is_float_array, \
        is_float_matrix, \
        is_float_object, \
        is_func, \
        is_int, \
        is_int_list, \
        is_int_or_int_list, \
        is_list, \
        is_list_val_or_list_of_list_val, \
        is_none, \
        is_num, \
        is_num_list, \
        is_num_or_num_tuple, \
        is_num_tuple, \
        is_str, \
        is_str_list, \
        is_str_or_inst, \
        is_str_or_num_or_str_num_list, \
        is_str_or_num_list, \
        is_str_or_str_list, \
        is_tuple, \
        is_val_or_list, \
        validate_arg
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
        RelaxNoneBoolError, \
        RelaxNoneBoolListBoolError, \
        RelaxNoneFloatError, \
        RelaxNoneFunctionError, \
        RelaxNoneError, \
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
from test_suite.unit_tests.base_classes import UnitTestCase


def dummy_function():
    pass


class Dummy_class:
    pass


class Dummy_writable_class:
    def write(self):
        pass


class Test_arg_check(UnitTestCase):
    """Unit tests for the functions of the 'lib.arg_check' module."""

    def check_function(self, func=None, allowed_types=None, dim=None, error=None, none_error=None, can_be_empty=False):
        """Check the operation of the given function.

        @keyword func:          The lib.arg_check function to check.
        @type func:             func
        @keyword allowed_types: A list of Python data type names that should result in the function returning True.
        @type allowed_types:    list of str
        @keyword dim:           The 'dim' argument used in some lib.arg_check functions.  This should be a list matching the length of allowed_types.
        @type dim:              list of tuples
        @keyword error:         The expected RelaxError for a normal failure.
        @type error:            RelaxError instance
        @keyword none_error:    The expected RelaxError for a normal failure when can_be_none is set.
        @type none_error:       RelaxError instance
        @keyword can_be_empty:  Pass this argument onto the function if True.
        @type can_be_empty:     bool
        """

        # Sanity checks.
        if error == None:
            raise RelaxError("The 'error' argument cannot be None.")
        if none_error == None:
            raise RelaxError("The 'none_error' argument cannot be None.")

        # Loop over all objects.
        for type in self.object_types:
            # Printout to help debugging.
            value_str = repr(self.objects[type])
            if search("^array", value_str):
                value_str = value_str.replace("\n", "")
                value_str = ''.join(value_str.split())
            print("Checking %s: %s" % (type, value_str))

            # None handling.
            if type in ['none']:
                self.assertEqual(func(self.objects[type], name=type, can_be_none=True), True)
                self.assertRaises(error, func, self.objects[type], name=type)

            # Positive tests.
            elif type in allowed_types:
                if dim:
                    if can_be_empty:
                        self.assertEqual(func(self.objects[type], name=type, dim=dim[allowed_types.index(type)], can_be_empty=True), True)
                    else:
                        self.assertEqual(func(self.objects[type], name=type, dim=dim[allowed_types.index(type)]), True)
                else:
                    if can_be_empty:
                        self.assertEqual(func(self.objects[type], name=type, can_be_empty=True), True)
                    else:
                        self.assertEqual(func(self.objects[type], name=type), True)

            # Negative tests.
            else:
                if can_be_empty:
                    self.assertEqual(func(self.objects[type], name=type, raise_error=False, can_be_empty=True), False)
                    self.assertRaises(error, func, self.objects[type], name=type, can_be_empty=True)
                    self.assertRaises(none_error, func, self.objects[type], name=type, can_be_none=True, can_be_empty=True)
                else:
                    self.assertEqual(func(self.objects[type], name=type, raise_error=False), False)
                    self.assertRaises(error, func, self.objects[type], name=type)
                    self.assertRaises(none_error, func, self.objects[type], name=type, can_be_none=True)


    def check_validate_arg(self, allowed_types=None, error=None, dim=(), basic_types=[], container_types=[], can_be_none=False, can_be_empty=False):
        """Check the operation of lib.arg_check.validate_arg().

        @keyword allowed_types: A list of Python data type names that should result in the function returning True.
        @type allowed_types:    list of str
        @keyword error:         The expected RelaxError for a normal failure.
        @type error:            RelaxError instance
        @keyword dim:           The validate_arg() 'dim' argument.  This should be a list matching the length of allowed_types.
        @type dim:              list of tuples
        @keyword can_be_none:   The validate_arg() 'can_be_none' argument.  A flag specifying if the argument can be none.
        @type can_be_none:      bool
        @keyword can_be_empty:  The validate_arg() 'can_be_empty' argument.  A flag which if True allows container types to be empty.
        @type can_be_empty:     bool
        """

        # Sanity checks.
        if error == None:
            raise RelaxError("The 'error' argument cannot be None.")

        # Loop over all objects.
        for type in self.object_types:
            # Printout to help debugging.
            value_str = repr(self.objects[type])
            if search("^array", value_str):
                value_str = value_str.replace("\n", "")
                value_str = ''.join(value_str.split())
            print("Checking %s: %s" % (type, value_str))

            # Positive tests.
            if type in allowed_types:
                self.assertEqual(validate_arg(self.objects[type], name=type, dim=dim, basic_types=basic_types, container_types=container_types, can_be_none=can_be_none, can_be_empty=can_be_empty), True)

            # Negative tests.
            else:
                self.assertEqual(validate_arg(self.objects[type], name=type, dim=dim, basic_types=basic_types, container_types=container_types, can_be_none=can_be_none, can_be_empty=can_be_empty, raise_error=False), False)
                self.assertRaises(error, validate_arg, self.objects[type], name=type, dim=dim, basic_types=basic_types, container_types=container_types, can_be_none=can_be_none, can_be_empty=can_be_empty)


    def setUp(self):
        """Set up function for all tests."""

        # The objects to check.
        self.objects = {
            'bool':                     True,
            'bool_list':                [True, False],
            'bool_tuple':               (True, False),
            'class':                    Dummy_class,
            'empty_list':               list(),
            'empty_list_of_lists':      [[]],
            'empty_set':                set(),
            'empty_tuple':              tuple(),
            'file_object':              sys.stdout,
            'float':                    1.0,
            'float_list':               [1.],
            'float_list_of_lists':      [[1.]],
            'float_list_rank3':         [[[1., 2.], [3., 4.]], [[5., 6.], [7., 8.]]],
            'float_numpy_array':        array([1., 2.], float64),
            'float_numpy_array_empty':  array([], float64),
            'float_numpy_matrix':       array([[1., 2.], [3., 4.]], float64),
            'float_numpy_matrix_empty': array([[]], float64),
            'float_numpy_object':       array([[[1., 2.], [3., 4.]], [[5., 6.], [7., 8.]]], float64),
            'float_numpy_object_empty': array([[[]]], float64),
            'float_set':                set([1., 2.]),
            'float_tuple':              (1., 2.),
            'float_tuple_of_tuples':    ((1., 2.), (3., 4.)),
            'float_tuple_rank3':        (((1., 2.), (3., 4.)), ((5., 6.), (7., 8.))),
            'func':                     dummy_function,
            'int':                      2,
            'int_list':                 [1, 2],
            'int_list_of_lists':        [[1, 2], [3, 4]],
            'int_list_rank3':           [[[1, 2], [3, 4]], [[5, 6], [7, 8]]],
            'int_numpy_array':          array([1, 2], int32),
            'int_numpy_array_empty':    array([], int32),
            'int_numpy_matrix':         array([[1, 2], [3, 4]], int32),
            'int_numpy_matrix_empty':   array([[]], int32),
            'int_numpy_object':         array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], int32),
            'int_numpy_object_empty':   array([[[]]], int32),
            'int_set':                  set([1, 2]),
            'int_tuple':                (1, 2),
            'int_tuple_of_tuples':      ((1, 2), (3, 4)),
            'int_tuple_rank3':          (((1, 2), (3, 4)), ((5, 6), (7, 8))),
            'inst':                     Dummy_class(),
            'inst_file':                Dummy_writable_class(),
            'none':                     None,
            'str':                      'test',
            'str_list':                 ['test'],
            'str_list_of_lists':        [['test']],
            'str_num_list':             [1, 'test'],
            'str_set':                  set(['test']),
            'str_tuple':                ('test',),
            'str_tuple_of_tuples':      (('test1', 'test2'), ('test3', 'test4')),
            'str_tuple_rank3':          ((('test1', 'test2'), ('test3', 'test4')), (('test5', 'test6'), ('test7', 'test8'))),
        }
        self.object_types = list(self.objects.keys())
        self.object_types.sort()


    def test_is_bool(self):
        """Test the lib.arg_check.is_bool() function."""

        self.check_function(func=is_bool, allowed_types=['bool'], error=RelaxBoolError, none_error=RelaxNoneBoolError)


    def test_is_bool_or_bool_list(self):
        """Test the lib.arg_check.is_bool_or_bool_list() function."""

        self.check_function(func=is_bool_or_bool_list, allowed_types=['bool', 'bool_list'], error=RelaxBoolListBoolError, none_error=RelaxNoneBoolListBoolError)


    def test_is_float(self):
        """Test the lib.arg_check.is_float() function."""

        self.check_function(func=is_float, allowed_types=['float'], error=RelaxFloatError, none_error=RelaxNoneFloatError)


    def test_is_float_array(self):
        """Test the lib.arg_check.is_float_array() function."""

        self.check_function(func=is_float_array, allowed_types=['empty_list', 'float_numpy_array', 'float_numpy_array_empty', 'float_list'], error=RelaxListFloatError, none_error=RelaxNoneListFloatError)


    def test_is_float_matrix(self):
        """Test the lib.arg_check.is_float_matrix() function."""

        self.check_function(func=is_float_matrix, allowed_types=['empty_list_of_lists', 'float_list_of_lists', 'float_numpy_matrix', 'float_numpy_matrix_empty'], error=RelaxMatrixFloatError, none_error=RelaxNoneMatrixFloatError)


    def test_is_float_object(self):
        """Test the lib.arg_check.is_float_object() function."""

        self.check_function(func=is_float_object, allowed_types=['float_list', 'float_list_of_lists', 'float_list_rank3', 'float_numpy_array', 'float_numpy_array_empty', 'float_numpy_matrix', 'float_numpy_object'], dim=[(1,), (1, 1), (2,2,2), (2,), (0,), (2,2), (2,2,2)], error=RelaxListFloatError, none_error=RelaxNoneListFloatError)


    def test_is_func(self):
        """Test the lib.arg_check.is_func() function."""

        self.check_function(func=is_func, allowed_types=['func'], error=RelaxFunctionError, none_error=RelaxNoneFunctionError)


    def test_is_int(self):
        """Test the lib.arg_check.is_int() function."""

        self.check_function(func=is_int, allowed_types=['int'], error=RelaxIntError, none_error=RelaxNoneIntError)


    def test_is_int_list(self):
        """Test the lib.arg_check.is_int_list() function."""

        self.check_function(func=is_int_list, allowed_types=['int_list'], error=RelaxListIntError, none_error=RelaxNoneListIntError)


    def test_is_int_or_int_list(self):
        """Test the lib.arg_check.is_int_or_int_list() function."""

        self.check_function(func=is_int_or_int_list, allowed_types=['int', 'int_list' ], error=RelaxIntListIntError, none_error=RelaxNoneIntListIntError)


    def test_is_list(self):
        """Test the lib.arg_check.is_list() function."""

        self.check_function(func=is_list, allowed_types=['bool_list', 'empty_list', 'empty_list_of_lists', 'float_list', 'float_list_of_lists', 'float_list_rank3', 'int_list', 'int_list_of_lists', 'int_list_rank3', 'str_list', 'str_list_of_lists', 'str_num_list'], error=RelaxListError, none_error=RelaxNoneListError, can_be_empty=True)
        self.check_function(func=is_list, allowed_types=['bool_list', 'empty_list_of_lists', 'float_list', 'float_list_of_lists', 'float_list_rank3', 'int_list', 'int_list_of_lists', 'int_list_rank3', 'str_list', 'str_list_of_lists', 'str_num_list'], error=RelaxListError, none_error=RelaxNoneListError, can_be_empty=False)


    def test_is_list_val_or_list_of_list_val(self):
        """Test the lib.arg_check.is_list_val_or_list_of_list_val() function."""

        self.check_function(func=is_list_val_or_list_of_list_val, allowed_types=['float_list', 'float_list_of_lists', 'int_list', 'int_list_of_lists'], error=RelaxNumStrListNumStrError, none_error=RelaxNoneNumStrListNumStrError)


    def test_is_none(self):
        """Test the lib.arg_check.is_none() function."""

        # Loop over all objects.
        for type in self.object_types:
            if type in ['none']:
                self.assertEqual(is_none(self.objects[type], name=type), True)
            else:
                self.assertRaises(RelaxNoneError, is_none, self.objects[type], name=type)


    def test_is_num(self):
        """Test the lib.arg_check.is_num() function."""

        self.check_function(func=is_num, allowed_types=['float', 'int'], error=RelaxNumError, none_error=RelaxNoneNumError)


    def test_is_num_list(self):
        """Test the lib.arg_check.is_num_list() function."""

        self.check_function(func=is_num_list, allowed_types=['float_list', 'float_numpy_array', 'int_list', 'int_numpy_array'], error=RelaxListNumError, none_error=RelaxNoneListNumError)


    def test_is_num_or_num_tuple(self):
        """Test the lib.arg_check.is_num_or_num_tuple() function."""

        self.check_function(func=is_num_or_num_tuple, allowed_types=['float', 'float_tuple', 'int', 'int_tuple'], error=RelaxNumTupleNumError, none_error=RelaxNoneNumTupleNumError)


    def test_is_num_tuple(self):
        """Test the lib.arg_check.is_num_tuple() function."""

        self.check_function(func=is_num_tuple, allowed_types=['float_tuple', 'int_tuple'], error=RelaxTupleNumError, none_error=RelaxNoneTupleNumError)


    def test_is_str(self):
        """Test the lib.arg_check.is_str() function."""

        self.check_function(func=is_str, allowed_types=['str'], error=RelaxStrError, none_error=RelaxNoneStrError)


    def test_is_str_list(self):
        """Test the lib.arg_check.is_str_list() function."""

        self.check_function(func=is_str_list, allowed_types=['str_list'], error=RelaxListStrError, none_error=RelaxNoneListStrError)


    def test_is_str_or_inst(self):
        """Test the lib.arg_check.is_str_or_inst() function."""

        self.check_function(func=is_str_or_inst, allowed_types=['str', 'file_object', 'inst_file'], error=RelaxStrFileError, none_error=RelaxNoneStrFileError)


    def test_is_str_or_num_or_str_num_list(self):
        """Test the lib.arg_check.is_str_or_num_or_str_num_list() function."""

        self.check_function(func=is_str_or_num_or_str_num_list, allowed_types=['float', 'float_list', 'int', 'int_list', 'str', 'str_list', 'str_num_list'], error=RelaxNumStrListNumStrError, none_error=RelaxNoneNumStrListNumStrError)


    def test_is_str_or_num_list(self):
        """Test the lib.arg_check.is_str_or_num_list() function."""

        self.check_function(func=is_str_or_num_list, allowed_types=['float_list', 'int_list', 'str'], error=RelaxStrListNumError, none_error=RelaxNoneStrListNumError)


    def test_is_str_or_str_list(self):
        """Test the lib.arg_check.is_str_or_str_list() function."""

        self.check_function(func=is_str_or_str_list, allowed_types=['str', 'str_list'], error=RelaxStrListStrError, none_error=RelaxNoneStrListStrError)


    def test_is_tuple(self):
        """Test the lib.arg_check.is_tuple() function."""

        self.check_function(func=is_tuple, allowed_types=['bool_tuple', 'empty_tuple', 'float_tuple', 'float_tuple_of_tuples', 'float_tuple_rank3', 'int_tuple', 'int_tuple_of_tuples', 'int_tuple_rank3', 'str_tuple', 'str_tuple_of_tuples', 'str_tuple_rank3'], error=RelaxTupleError, none_error=RelaxNoneTupleError)


    def test_is_val_or_list(self):
        """Test the lib.arg_check.is_val_or_list() function."""

        self.check_function(func=is_val_or_list, allowed_types=['bool', 'bool_list', 'float', 'float_list', 'int', 'int_list', 'str', 'str_list', 'str_num_list'], error=RelaxValListValError, none_error=RelaxNoneValListValError)


    def test_validate_arg_all_basic_types(self):
        """Test lib.arg_check.validate_arg() with basic data type-checking off."""

        self.check_validate_arg(allowed_types=['bool', 'class', 'file_object', 'float', 'func', 'int', 'inst', 'inst_file', 'none', 'str'], error=RelaxInvalidError, basic_types=['all'])


    def test_validate_arg_all_containers(self):
        """Test lib.arg_check.validate_arg() with container type-checking off."""

        self.check_validate_arg(allowed_types=self.object_types, error=RelaxInvalidError, basic_types=['all'], container_types=['all'])


    def test_validate_arg_all_basic_types_and_all_containers(self):
        """Test lib.arg_check.validate_arg() with all type-checking off."""

        self.check_validate_arg(allowed_types=self.object_types, error=RelaxInvalidError, basic_types=['all'], container_types=['all'])


    def test_validate_arg_bool(self):
        """Test lib.arg_check.validate_arg() for a basic Boolean type."""

        self.check_validate_arg(allowed_types=['bool'], error=RelaxBoolError, dim=(), basic_types=['bool'])


    def test_validate_arg_bool_list(self):
        """Test lib.arg_check.validate_arg() for a list of Booleans."""

        self.check_validate_arg(allowed_types=['bool_list'], error=RelaxListBoolError, dim=(None,), basic_types=['bool'], container_types=['list'])
        self.check_validate_arg(allowed_types=[], error=RelaxListBoolError, dim=(5,), basic_types=['bool'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'bool_list'], error=RelaxListBoolError, dim=(None,), basic_types=['bool'], container_types=['list'], can_be_none=True)


    def test_validate_arg_bool_list_of_lists(self):
        """Test lib.arg_check.validate_arg() for a list of lists of Booleans."""

        self.check_validate_arg(allowed_types=['bool_list_of_lists'], error=RelaxInvalidError, dim=(None,None), basic_types=['bool'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'bool_list_of_lists'], error=RelaxInvalidError, dim=(None,None), basic_types=['bool'], container_types=['list'], can_be_none=True)


    def test_validate_arg_bool_or_bool_list(self):
        """Test lib.arg_check.validate_arg() for a Boolean or a list of Booleans."""

        self.check_validate_arg(allowed_types=['bool', 'bool_list'], error=RelaxBoolListBoolError, dim=[(), (None,)], basic_types=['bool'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'bool', 'bool_list'], error=RelaxBoolListBoolError, dim=[(), (None,)], basic_types=['bool'], container_types=['list'], can_be_none=True)


    def test_validate_arg_float(self):
        """Test lib.arg_check.validate_arg() for a basic float type."""

        self.check_validate_arg(allowed_types=['float'], error=RelaxFloatError, dim=(), basic_types=['float'])
        self.check_validate_arg(allowed_types=['none', 'float'], error=RelaxFloatError, dim=(), basic_types=['float'], can_be_none=True)


    def test_validate_arg_float_list(self):
        """Test lib.arg_check.validate_arg() for a list of floats."""

        self.check_validate_arg(allowed_types=['float_list'], error=RelaxListFloatError, dim=(None,), basic_types=['float'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'float_list'], error=RelaxListFloatError, dim=(None,), basic_types=['float'], container_types=['list'], can_be_none=True)


    def test_validate_arg_float_list_of_lists(self):
        """Test lib.arg_check.validate_arg() for a list of lists of floats."""

        self.check_validate_arg(allowed_types=['float_list_of_lists'], error=RelaxInvalidError, dim=(None,None), basic_types=['float'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'float_list_of_lists'], error=RelaxInvalidError, dim=(None,None), basic_types=['float'], container_types=['list'], can_be_none=True)


    def test_validate_arg_float_or_float_list(self):
        """Test lib.arg_check.validate_arg() for a float or list of floats."""

        self.check_validate_arg(allowed_types=['float', 'float_list'], error=RelaxInvalidError, dim=[(), (None,)], basic_types=['float'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'float', 'float_list'], error=RelaxInvalidError, dim=[(), (None,)], basic_types=['float'], container_types=['list'], can_be_none=True)


    def test_validate_arg_func(self):
        """Test lib.arg_check.validate_arg() for a basic function type."""

        self.check_validate_arg(allowed_types=['func'], error=RelaxFunctionError, dim=(), basic_types=['func'])
        self.check_validate_arg(allowed_types=['none', 'func'], error=RelaxFunctionError, dim=(), basic_types=['func'], can_be_none=True)


    def test_validate_arg_int(self):
        """Test lib.arg_check.validate_arg() for a basic integer type."""

        self.check_validate_arg(allowed_types=['int'], error=RelaxIntError, dim=(), basic_types=['int'])
        self.check_validate_arg(allowed_types=['none', 'int'], error=RelaxIntError, dim=(), basic_types=['int'], can_be_none=True)


    def test_validate_arg_int_list(self):
        """Test lib.arg_check.validate_arg() for a list of integers."""

        self.check_validate_arg(allowed_types=['int_list'], error=RelaxListIntError, dim=(None,), basic_types=['int'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'int_list'], error=RelaxListIntError, dim=(None,), basic_types=['int'], container_types=['list'], can_be_none=True)


    def test_validate_arg_int_list_of_lists(self):
        """Test lib.arg_check.validate_arg() for a list of lists of integers."""

        self.check_validate_arg(allowed_types=['int_list_of_lists'], error=RelaxInvalidError, dim=(None,None), basic_types=['int'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'int_list_of_lists'], error=RelaxInvalidError, dim=(None,None), basic_types=['int'], container_types=['list'], can_be_none=True)


    def test_validate_arg_int_or_int_list(self):
        """Test lib.arg_check.validate_arg() for a integer or a list of integers."""

        self.check_validate_arg(allowed_types=['int', 'int_list'], error=RelaxIntListIntError, dim=[(), (None,)], basic_types=['int'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'int', 'int_list'], error=RelaxIntListIntError, dim=[(), (None,)], basic_types=['int'], container_types=['list'], can_be_none=True)


    def test_validate_arg_list(self):
        """Test lib.arg_check.validate_arg() for a list of anything."""

        self.check_validate_arg(allowed_types=['bool_list', 'empty_list', 'float_list', 'int_list', 'str_list', 'str_num_list'], error=RelaxListError, dim=(None,), basic_types=['bool', 'float', 'int', 'str'], container_types=['list'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'bool_list', 'empty_list', 'float_list', 'int_list', 'str_list', 'str_num_list'], error=RelaxListError, dim=(None,), basic_types=['bool', 'float', 'int', 'str'], container_types=['list'], can_be_empty=True, can_be_none=True)


    def test_validate_arg_list_or_numpy_array(self):
        """Test lib.arg_check.validate_arg() for a list of anything or numpy array."""

        self.check_validate_arg(allowed_types=['bool_list', 'float_list', 'float_numpy_array', 'int_list', 'int_numpy_array', 'str_list', 'str_num_list'], error=RelaxArrayError, dim=(None,), basic_types=['bool', 'float', 'int', 'str'], container_types=['list', 'numpy array'])
        self.check_validate_arg(allowed_types=['bool_list', 'empty_list', 'float_list', 'float_numpy_array', 'float_numpy_array_empty', 'int_list', 'int_numpy_array', 'int_numpy_array_empty', 'str_list', 'str_num_list'], error=RelaxArrayError, dim=(None,), basic_types=['bool', 'float', 'int', 'str'], container_types=['list', 'numpy array'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'bool_list', 'float_list', 'float_numpy_array', 'int_list', 'int_numpy_array', 'str_list', 'str_num_list'], error=RelaxArrayError, dim=(None,), basic_types=['bool', 'float', 'int', 'str'], container_types=['list', 'numpy array'], can_be_none=True)


    def test_validate_arg_number(self):
        """Test lib.arg_check.validate_arg() for a number."""

        self.check_validate_arg(allowed_types=['float', 'int'], error=RelaxNumError, dim=(), basic_types=['number'])
        self.check_validate_arg(allowed_types=['none', 'float', 'int'], error=RelaxNumError, dim=(), basic_types=['number'], can_be_none=True)


    def test_validate_arg_number_array_rank1(self):
        """Test lib.arg_check.validate_arg() for a rank-1 list or numpy array of numbers."""

        self.check_validate_arg(allowed_types=['float_list', 'float_numpy_array', 'int_list', 'int_numpy_array'], error=RelaxArrayNumError, dim=(None,), basic_types=['number'], container_types=['number array'])
        self.check_validate_arg(allowed_types=['empty_list', 'float_list', 'float_numpy_array', 'float_numpy_array_empty', 'int_list', 'int_numpy_array', 'int_numpy_array_empty'], error=RelaxArrayNumError, dim=(None,), basic_types=['number'], container_types=['number array'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'float_list', 'float_numpy_array', 'int_list', 'int_numpy_array'], error=RelaxArrayNumError, dim=(None,), basic_types=['number'], container_types=['number array'], can_be_none=True)


    def test_validate_arg_number_array_rank2(self):
        """Test lib.arg_check.validate_arg() for a rank-2 list or numpy array of numbers."""

        self.check_validate_arg(allowed_types=['float_list_of_lists', 'float_numpy_matrix', 'int_list_of_lists', 'int_numpy_matrix'], error=RelaxArrayNumError, dim=(None,None), basic_types=['number'], container_types=['number array'])
        self.check_validate_arg(allowed_types=['empty_list_of_lists', 'float_list_of_lists', 'float_numpy_matrix', 'float_numpy_matrix_empty', 'int_list_of_lists', 'int_numpy_matrix', 'int_numpy_matrix_empty'], error=RelaxArrayNumError, dim=(None,None), basic_types=['number'], container_types=['number array'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'float_list_of_lists', 'float_numpy_matrix', 'int_list_of_lists', 'int_numpy_matrix'], error=RelaxArrayNumError, dim=(None,None), basic_types=['number'], container_types=['number array'], can_be_none=True)


    def test_validate_arg_number_array_rank3(self):
        """Test lib.arg_check.validate_arg() for a rank-3 list or numpy array of numbers."""

        self.check_validate_arg(allowed_types=['float_list_rank3', 'float_numpy_object', 'int_list_rank3', 'int_numpy_object'], error=RelaxArrayNumError, dim=(None,None,None), basic_types=['number'], container_types=['number array'])
        self.check_validate_arg(allowed_types=['float_list_rank3', 'float_numpy_object', 'int_list_rank3', 'int_numpy_object'], error=RelaxArrayNumError, dim=(None,None,None), basic_types=['number'], container_types=['number array'])
        self.check_validate_arg(allowed_types=['none', 'float_list_rank3', 'float_numpy_object', 'float_numpy_object_empty', 'int_list_rank3', 'int_numpy_object', 'int_numpy_object_empty'], error=RelaxArrayNumError, dim=(None,None,None), basic_types=['number'], container_types=['number array'], can_be_empty=True, can_be_none=True)


    def test_validate_arg_number_list(self):
        """Test lib.arg_check.validate_arg() for a rank-1 list of numbers."""

        self.check_validate_arg(allowed_types=['float_list', 'int_list'], error=RelaxListNumError, dim=(None,), basic_types=['number'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'float_list', 'int_list'], error=RelaxListNumError, dim=(None,), basic_types=['number'], container_types=['list'], can_be_none=True)


    def test_validate_arg_number_list_of_lists(self):
        """Test lib.arg_check.validate_arg() for a rank-2 list of numbers."""

        self.check_validate_arg(allowed_types=['float_list_of_lists', 'int_list_of_lists'], error=RelaxListNumError, dim=(None,None), basic_types=['number'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'float_list_of_lists', 'int_list_of_lists'], error=RelaxListNumError, dim=(None,None), basic_types=['number'], container_types=['list'], can_be_none=True)


    def test_validate_arg_number_list_rank3(self):
        """Test lib.arg_check.validate_arg() for a rank-3 list of numbers."""

        self.check_validate_arg(allowed_types=['float_list_rank3', 'int_list_rank3'], error=RelaxListNumError, dim=(None,None,None), basic_types=['number'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'float_list_rank3', 'int_list_rank3'], error=RelaxListNumError, dim=(None,None,None), basic_types=['number'], container_types=['list'], can_be_none=True)


    def test_validate_arg_number_numpy_array_rank1(self):
        """Test lib.arg_check.validate_arg() for a rank-1 numpy array of numbers."""

        self.check_validate_arg(allowed_types=['float_numpy_array', 'int_numpy_array'], error=RelaxNumpyNumError, dim=(None,), basic_types=['number'], container_types=['numpy array'])
        self.check_validate_arg(allowed_types=['float_numpy_array', 'float_numpy_array_empty', 'int_numpy_array', 'int_numpy_array_empty'], error=RelaxNumpyNumError, dim=(None,), basic_types=['number'], container_types=['numpy array'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'float_numpy_array', 'int_numpy_array'], error=RelaxNumpyNumError, dim=(None,), basic_types=['number'], container_types=['numpy array'], can_be_none=True)


    def test_validate_arg_number_numpy_array_rank2(self):
        """Test lib.arg_check.validate_arg() for a rank-2 numpy array of numbers."""

        self.check_validate_arg(allowed_types=['float_numpy_matrix', 'int_numpy_matrix'], error=RelaxNumpyNumError, dim=(2,2), basic_types=['number'], container_types=['numpy array'])
        self.check_validate_arg(allowed_types=['float_numpy_matrix', 'float_numpy_matrix_empty', 'int_numpy_matrix', 'int_numpy_matrix_empty'], error=RelaxNumpyNumError, dim=(None,None), basic_types=['number'], container_types=['numpy array'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'float_numpy_matrix', 'int_numpy_matrix'], error=RelaxNumpyNumError, dim=(None,None), basic_types=['number'], container_types=['numpy array'], can_be_none=True)


    def test_validate_arg_number_numpy_array_rank3(self):
        """Test lib.arg_check.validate_arg() for a rank-3 numpy array of numbers."""

        self.check_validate_arg(allowed_types=['float_numpy_object', 'int_numpy_object'], error=RelaxNumpyNumError, dim=(2,2,2), basic_types=['number'], container_types=['numpy array'])
        self.check_validate_arg(allowed_types=['float_numpy_object', 'float_numpy_object_empty', 'int_numpy_object', 'int_numpy_object_empty'], error=RelaxNumpyNumError, dim=(None,None,None), basic_types=['number'], container_types=['numpy array'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'float_numpy_object', 'int_numpy_object'], error=RelaxNumpyNumError, dim=(2,2,2), basic_types=['number'], container_types=['numpy array'], can_be_none=True)


    def test_validate_arg_number_tuple(self):
        """Test lib.arg_check.validate_arg() for a rank-1 tuple of numbers."""

        self.check_validate_arg(allowed_types=['float_tuple', 'int_tuple'], error=RelaxTupleNumError, dim=(None,), basic_types=['number'], container_types=['tuple'])
        self.check_validate_arg(allowed_types=['none', 'float_tuple', 'int_tuple'], error=RelaxTupleNumError, dim=(None,), basic_types=['number'], container_types=['tuple'], can_be_none=True)


    def test_validate_arg_number_tuple_of_tuples(self):
        """Test lib.arg_check.validate_arg() for a rank-2 tuple of numbers."""

        self.check_validate_arg(allowed_types=['float_tuple_of_tuples', 'int_tuple_of_tuples'], error=RelaxTupleNumError, dim=(None,None), basic_types=['number'], container_types=['tuple'])
        self.check_validate_arg(allowed_types=['none', 'float_tuple_of_tuples', 'int_tuple_of_tuples'], error=RelaxTupleNumError, dim=(None,None), basic_types=['number'], container_types=['tuple'], can_be_none=True)


    def test_validate_arg_number_tuple_rank3(self):
        """Test lib.arg_check.validate_arg() for a rank-3 tuple of numbers."""

        self.check_validate_arg(allowed_types=['float_tuple_rank3', 'int_tuple_rank3'], error=RelaxTupleNumError, dim=(None,None,None), basic_types=['number'], container_types=['tuple'])
        self.check_validate_arg(allowed_types=['none', 'float_tuple_rank3', 'int_tuple_rank3'], error=RelaxTupleNumError, dim=(None,None,None), basic_types=['number'], container_types=['tuple'], can_be_none=True)


    def test_validate_arg_numpy_float_array(self):
        """Test lib.arg_check.validate_arg() for a numpy float array."""

        self.check_validate_arg(allowed_types=['float_numpy_array'], error=RelaxNumpyFloatError, dim=(None,), basic_types=['float'], container_types=['numpy array'])
        self.check_validate_arg(allowed_types=['float_numpy_array', 'float_numpy_array_empty'], error=RelaxNumpyFloatError, dim=(None,), basic_types=['float'], container_types=['numpy array'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'float_numpy_array'], error=RelaxNumpyFloatError, dim=(None,), basic_types=['float'], container_types=['numpy array'], can_be_none=True)


    def test_validate_arg_numpy_float_matrix(self):
        """Test lib.arg_check.validate_arg() for a numpy matrix of floats."""

        self.check_validate_arg(allowed_types=['float_numpy_matrix'], error=RelaxNumpyFloatError, dim=(None,None), basic_types=['float'], container_types=['numpy array'])
        self.check_validate_arg(allowed_types=['float_numpy_matrix', 'float_numpy_matrix_empty'], error=RelaxNumpyFloatError, dim=(None,None), basic_types=['float'], container_types=['numpy array'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'float_numpy_matrix'], error=RelaxNumpyFloatError, dim=(None,None), basic_types=['float'], container_types=['numpy array'], can_be_none=True)


    def test_validate_arg_numpy_float_rank3(self):
        """Test lib.arg_check.validate_arg() for a numpy rank-3 object of floats."""

        self.check_validate_arg(allowed_types=['float_numpy_object'], error=RelaxNumpyFloatError, dim=(2,2,2), basic_types=['float'], container_types=['numpy array'])
        self.check_validate_arg(allowed_types=['float_numpy_object', 'float_numpy_object_empty'], error=RelaxNumpyFloatError, dim=(None,None,None), basic_types=['float'], container_types=['numpy array'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'float_numpy_object'], error=RelaxNumpyFloatError, dim=(2,2,2), basic_types=['float'], container_types=['numpy array'], can_be_none=True)


    def test_validate_arg_numpy_int_array(self):
        """Test lib.arg_check.validate_arg() for a numpy int array."""

        self.check_validate_arg(allowed_types=['int_numpy_array'], error=RelaxNumpyIntError, dim=(2,), basic_types=['int'], container_types=['numpy array'])
        self.check_validate_arg(allowed_types=['int_numpy_array', 'int_numpy_array_empty'], error=RelaxNumpyIntError, dim=(None,), basic_types=['int'], container_types=['numpy array'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'int_numpy_array'], error=RelaxNumpyIntError, dim=(2,), basic_types=['int'], container_types=['numpy array'], can_be_none=True)


    def test_validate_arg_numpy_int_matrix(self):
        """Test lib.arg_check.validate_arg() for a numpy matrix of ints."""

        self.check_validate_arg(allowed_types=['int_numpy_matrix'], error=RelaxNumpyIntError, dim=(None,None), basic_types=['int'], container_types=['numpy array'])
        self.check_validate_arg(allowed_types=['int_numpy_matrix', 'int_numpy_matrix_empty'], error=RelaxNumpyIntError, dim=(None,None), basic_types=['int'], container_types=['numpy array'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'int_numpy_matrix'], error=RelaxNumpyIntError, dim=(None,None), basic_types=['int'], container_types=['numpy array'], can_be_none=True)


    def test_validate_arg_numpy_int_rank3(self):
        """Test lib.arg_check.validate_arg() for a numpy rank-3 object of ints."""

        self.check_validate_arg(allowed_types=['int_numpy_object'], error=RelaxNumpyIntError, dim=(2,2,2), basic_types=['int'], container_types=['numpy array'])
        self.check_validate_arg(allowed_types=['int_numpy_object', 'int_numpy_object_empty'], error=RelaxNumpyIntError, dim=(None,None,None), basic_types=['int'], container_types=['numpy array'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'int_numpy_object'], error=RelaxNumpyIntError, dim=(2,2,2), basic_types=['int'], container_types=['numpy array'], can_be_none=True)


    def test_validate_arg_str(self):
        """Test lib.arg_check.validate_arg() for a basic string type."""

        self.check_validate_arg(allowed_types=['str'], error=RelaxStrError, dim=(), basic_types=['str'])
        self.check_validate_arg(allowed_types=['none', 'str'], error=RelaxStrError, dim=(), basic_types=['str'], can_be_none=True)


    def test_validate_arg_str_list(self):
        """Test lib.arg_check.validate_arg() for a list of strings."""

        self.check_validate_arg(allowed_types=['str_list'], error=RelaxListStrError, dim=(None,), basic_types=['str'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'str_list'], error=RelaxListStrError, dim=(None,), basic_types=['str'], container_types=['list'], can_be_none=True)


    def test_validate_arg_str_list_of_lists(self):
        """Test lib.arg_check.validate_arg() for a list of lists of strings."""

        self.check_validate_arg(allowed_types=['str_list_of_lists'], error=RelaxInvalidError, dim=(None,None), basic_types=['str'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'str_list_of_lists'], error=RelaxInvalidError, dim=(None,None), basic_types=['str'], container_types=['list'], can_be_none=True)


    def test_validate_arg_str_or_file_object(self):
        """Test lib.arg_check.validate_arg() for a string or list of strings."""

        self.check_validate_arg(allowed_types=['str', 'file_object', 'inst_file'], error=RelaxStrFileError, dim=[(), (None,)], basic_types=['str', 'file object'])
        self.check_validate_arg(allowed_types=['none', 'str', 'file_object', 'inst_file'], error=RelaxStrFileError, dim=[(), (None,)], basic_types=['str', 'file object'], can_be_none=True)


    def test_validate_arg_str_or_str_list(self):
        """Test lib.arg_check.validate_arg() for a string or list of strings."""

        self.check_validate_arg(allowed_types=['str', 'str_list'], error=RelaxStrListStrError, dim=[(), (None,)], basic_types=['str'], container_types=['list'])
        self.check_validate_arg(allowed_types=['none', 'str', 'str_list'], error=RelaxStrListStrError, dim=[(), (None,)], basic_types=['str'], container_types=['list'], can_be_none=True)


    def test_validate_arg_tuple(self):
        """Test lib.arg_check.validate_arg() for a tuple of anything."""

        self.check_validate_arg(allowed_types=['bool_tuple', 'empty_tuple', 'float_tuple', 'int_tuple', 'str_tuple', 'str_num_tuple'], error=RelaxTupleError, dim=(None,), container_types=['tuple'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'bool_tuple', 'empty_tuple', 'float_tuple', 'int_tuple', 'str_tuple', 'str_num_tuple'], error=RelaxTupleError, dim=(None,), container_types=['tuple'], can_be_empty=True, can_be_none=True)
        self.check_validate_arg(allowed_types=['bool_tuple', 'empty_tuple', 'float_tuple', 'int_tuple', 'str_tuple', 'str_num_tuple'], error=RelaxTupleError, dim=(None,), basic_types=['bool', 'number', 'str'], container_types=['tuple'], can_be_empty=True)
        self.check_validate_arg(allowed_types=['none', 'bool_tuple', 'empty_tuple', 'float_tuple', 'int_tuple', 'str_tuple', 'str_num_tuple'], error=RelaxTupleError, dim=(None,), basic_types=['bool', 'number', 'str'], container_types=['tuple'], can_be_empty=True, can_be_none=True)
