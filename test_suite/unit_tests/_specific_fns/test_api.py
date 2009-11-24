###############################################################################
#                                                                             #
# Copyright (C) 2008-2009 Edward d'Auvergne                                   #
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
from specific_fns.api_base import API_base
from specific_fns.frame_order import Frame_order


class Test_api(TestCase):
    """Unit tests for the specific_fns API."""

    def __format_method(self, name, args, varargs, varkw, defaults):
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


    def __check_method_args(self, analysis_obj):
        """Check the args of all API methods.

        @param analysis_obj:    The specific analysis object.
        @type analysis_obj:     instance
        """

        # The base object.
        base = API_base()

        # Loop over the objects of the specific analysis.
        for name in dir(analysis_obj):
            # Skip anything starting with '_'.
            if search('^_', name):
                continue

            # Get the object in the two classes.
            obj_base = getattr(base, name)
            obj = getattr(analysis_obj, name)

            # Skip non-method objects.
            if not isinstance(obj_base, types.MethodType):
                continue

            # Get the args and their default values.
            args_base, varargs_base, varkw_base, defaults_base = getargspec(obj_base)
            args, varargs, varkw, defaults = getargspec(obj)

            # Check the args.
            if args_base != args or varargs_base != varargs or varkw_base != varkw or defaults_base != defaults:
                # Get string representations of the methods.
                doc_base = self.__format_method(name, args_base, varargs_base, varkw_base, defaults_base)
                doc = self.__format_method(name, args, varargs, varkw, defaults)
                print(doc_base)

                # Fail.
                self.fail('The args of the method\n\t' + doc + '\ndo not match those of the API method\n\t' + doc_base)


    def __check_objects(self, analysis_obj):
        """Check the args of all API methods.

        @param analysis_obj:    The specific analysis object.
        @type analysis_obj:     instance
        """

        # The base object.
        base = API_base()

        # The objects in the base class.
        base_names = dir(base)

        # Loop over the objects of the specific analysis.
        for name in dir(analysis_obj):
            # Skip anything starting with '_'.
            if search('^_', name):
                continue

            # Get the object in the derived class.
            obj = getattr(analysis_obj, name)

            # Not present.
            if name not in base_names:
                self.fail('The object ' + repr(name) + ' ' + repr(type(obj)) + ' cannot be found in the API base class.')


    def test_frame_order_method_args(self):
        """The args of the public methods of the frame order object must be the same as the API base class."""

        # Check.
        self.__check_method_args(Frame_order())


    def test_frame_order_objects(self):
        """Are the initial public objects of the frame order object all within the API base class?"""

        # Check.
        self.__check_objects(Frame_order())
