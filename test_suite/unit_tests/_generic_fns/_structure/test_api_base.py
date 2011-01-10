###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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

# Python module imports.
from inspect import getargspec
from re import search
import types
from unittest import TestCase

# relax module imports.
import dep_check
from generic_fns.structure.api_base import Base_struct_API
from generic_fns.structure.internal import Internal
from generic_fns.structure.scientific import Scientific_data
from status import Status; status = Status()


class Test_api_base(TestCase):
    """Unit tests for the structural API base class."""

    def __init__(self, methodName='runTest'):
        """Skip scientific Python tests if not installed.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Scientific python tests.
        scientific_tests = ['test_Scientific_method_args', 'test_Scientific_objects']

        # Missing module.
        if methodName in scientific_tests and not dep_check.scientific_module:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'Scientific Python', 'unit'])

        # Execute the base class method.
        super(Test_api_base, self).__init__(methodName)



    def format_method(self, name, args, varargs, varkw, defaults):
        """Method for formatting the method."""

        # Method start.
        text = name + '('

        # No keywords.
        if defaults == None:
            defaults = ()

        # Args.
        for i in xrange(len(args) - len(defaults)):
            # Separator.
            if i != 0:
                text = text + ', '

            # The arg.
            text = text + args[i]

        # Shifted index.
        index = i+1

        # Keyword args.
        for i in xrange(index, len(defaults)+1):
            # Separator.
            if i != 0:
                text = text + ', '

            # The keyword.
            text = text + args[i] + '=' + repr(defaults[i-index])

        # End.
        text = text + ')'
        return text


    def test_Internal_method_args(self):
        """The args of the public methods of the Internal structural object must be the same as the API base class."""

        # The base and internal objects.
        base = Base_struct_API()
        intern = Internal()

        # Loop over the objects in the internal object.
        for name in dir(intern):
            # Skip anything starting with '_'.
            if search('^_', name):
                continue

            # Get the object in the two classes.
            obj_base = getattr(base, name)
            obj_intern = getattr(intern, name)

            # Skip non-method objects.
            if not isinstance(obj_base, types.MethodType):
                continue

            # Get the args and their default values.
            args_base, varargs_base, varkw_base, defaults_base = getargspec(obj_base)
            args_intern, varargs_intern, varkw_intern, defaults_intern = getargspec(obj_intern)

            # Check the args.
            if args_base != args_intern or varargs_base != varargs_intern or varkw_base != varkw_intern or defaults_base != defaults_intern:
                # Get string representations of the methods.
                doc_base = self.format_method(name, args_base, varargs_base, varkw_base, defaults_base)
                doc_intern = self.format_method(name, args_intern, varargs_intern, varkw_intern, defaults_intern)
                print(doc_base)

                # Fail.
                self.fail('The args of the method\n\t' + doc_intern + '\ndo not match those of the API method\n\t' + doc_base)


    def test_Internal_objects(self):
        """Are the initial public objects of the Internal structural object all within the API base class?"""

        # The base and internal objects.
        base = Base_struct_API()
        internal = Internal()

        # The objects in the base class.
        base_names = dir(base)

        # Loop over the objects in the internal object.
        for name in dir(internal):
            # Skip anything starting with '_'.
            if search('^_', name):
                continue

            # Get the object in the derived class.
            obj = getattr(internal, name)

            # Not present.
            if name not in base_names:
                self.fail('The object ' + repr(name) + ' ' + repr(type(obj)) + ' cannot be found in the structural API base class.')


    def test_Scientific_method_args(self):
        """The args of the public methods of the Scientific structural object must be the same as the API base class."""

        # The base and Scientific objects.
        base = Base_struct_API()
        sci = Scientific_data()

        # Loop over the objects in the Scientific object.
        for name in dir(sci):
            # Skip anything starting with '_'.
            if search('^_', name):
                continue

            # Get the object in the two classes.
            obj_base = getattr(base, name)
            obj_sci = getattr(sci, name)

            # Skip non-method objects.
            if not isinstance(obj_base, types.MethodType):
                continue

            # Get the args and their default values.
            args_base, varargs_base, varkw_base, defaults_base = getargspec(obj_base)
            args_sci, varargs_sci, varkw_sci, defaults_sci = getargspec(obj_sci)

            # Check the args.
            if args_base != args_sci or varargs_base != varargs_sci or varkw_base != varkw_sci or defaults_base != defaults_sci:
                # Get string representations of the methods.
                doc_base = self.format_method(name, args_base, varargs_base, varkw_base, defaults_base)
                doc_sci = self.format_method(name, args_sci, varargs_sci, varkw_sci, defaults_sci)

                # Fail.
                self.fail('The args of the method\n\t' + doc_sci + '\ndo not match those of the API method\n\t' + doc_base)


    def test_Scientific_objects(self):
        """Are the initial public objects of the Scientific structural object all within the API base class?"""

        # The base and Scientific objects.
        base = Base_struct_API()
        sci = Scientific_data()

        # The objects in the base class.
        base_names = dir(base)

        # Loop over the objects in the Scientific object.
        for name in dir(sci):
            # Skip anything starting with '_'.
            if search('^_', name):
                continue

            # Get the object in the derived class.
            obj = getattr(sci, name)

            # Not present.
            if name not in base_names:
                self.fail('The object ' + repr(name) + ' ' + repr(type(obj)) + ' cannot be found in the structural API base class.')
