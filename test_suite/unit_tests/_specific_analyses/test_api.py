###############################################################################
#                                                                             #
# Copyright (C) 2008-2009,2013-2014 Edward d'Auvergne                         #
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
from re import search
import types
from unittest import TestCase

# relax module imports.
from lib.compat import getfullargspec
from specific_analyses.api_base import API_base
from specific_analyses.consistency_tests.api import Consistency_tests
from specific_analyses.frame_order.api import Frame_order
from specific_analyses.hybrid import Hybrid
from specific_analyses.jw_mapping.api import Jw_mapping
from specific_analyses.model_free.api import Model_free
from specific_analyses.n_state_model.api import N_state_model
from specific_analyses.noe.api import Noe
from specific_analyses.relax_disp.api import Relax_disp
from specific_analyses.relax_fit.api import Relax_fit


class Test_api(TestCase):
    """Unit tests for the specific analyses API."""

    def __format_method(self, name, args, varargs, varkw, defaults):
        """Method for formatting the method."""

        # Method start.
        text = name + '('

        # No keywords.
        if defaults == None:
            defaults = ()

        # Counts.
        num_args = len(args) - len(defaults)
        num_kw = len(defaults)

        # Args.
        for i in range(num_args):
            # Separator.
            if i != 0:
                text = text + ', '

            # The arg.
            text = text + args[i]

        # Keyword args.
        for j in range(num_kw):
            # Separator.
            if num_args or j != 0:
                text = text + ', '

            # The keyword.
            text = text + args[num_args+j] + '=' + repr(defaults[j])

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

            # Skip the singleton instance.
            if name == 'instance':
                continue

            # Get the object in the two classes.
            obj_base = getattr(base, name)
            obj = getattr(analysis_obj, name)

            # Skip non-method objects.
            if not isinstance(obj_base, types.MethodType):
                continue

            # Get the args and their default values.
            args_base, varargs_base, varkw_base, defaults_base, kwonlyargs_base, kwonlydefaults_base, annotations_base = getfullargspec(obj_base)
            args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = getfullargspec(obj)

            # Check the args.
            if args_base != args or varargs_base != varargs or varkw_base != varkw:
                # Get string representations of the methods.
                doc_base = self.__format_method(name, args_base, varargs_base, varkw_base, defaults_base)
                doc = self.__format_method(name, args, varargs, varkw, defaults)
                print(doc_base)

                # Fail.
                self.fail('The args of the method:\n\t' + doc + '\ndo not match those of the API method:\n\t' + doc_base)


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

            # Skip the singleton instance.
            if name == 'instance':
                continue

            # Get the object in the derived class.
            obj = getattr(analysis_obj, name)

            # Not present.
            if name not in base_names:
                self.fail('The object ' + repr(name) + ' ' + repr(type(obj)) + ' cannot be found in the API base class.')


    def test_consistency_tests_method_args(self):
        """The consistency tests object public method args check."""

        # Check.
        self.__check_method_args(Consistency_tests())


    def test_consistency_tests_objects(self):
        """The consistency tests object public objects check."""

        # Check.
        self.__check_objects(Consistency_tests())


    def test_frame_order_method_args(self):
        """The frame order object public method args check."""

        # Check.
        self.__check_method_args(Frame_order())


    def test_frame_order_objects(self):
        """The frame order object public objects check."""

        # Check.
        self.__check_objects(Frame_order())


    def test_hybrid_method_args(self):
        """The hybrid object public method args check."""

        # Check.
        self.__check_method_args(Hybrid())


    def test_hybrid_objects(self):
        """The hybrid object public objects check."""

        # Check.
        self.__check_objects(Hybrid())


    def test_jw_mapping_method_args(self):
        """The reduced spectral density mapping object public method args check."""

        # Check.
        self.__check_method_args(Jw_mapping())


    def test_jw_mapping_objects(self):
        """The reduced spectral density mapping object public objects check."""

        # Check.
        self.__check_objects(Jw_mapping())


    def test_model_free_method_args(self):
        """The model-free object public method args check."""

        # Check.
        self.__check_method_args(Model_free())


    def test_model_free_objects(self):
        """The model-free object public objects check."""

        # Check.
        self.__check_objects(Model_free())


    def test_n_state_model_method_args(self):
        """The N-state model object public method args check."""

        # Check.
        self.__check_method_args(N_state_model())


    def test_n_state_model_objects(self):
        """The N-state model object public objects check."""

        # Check.
        self.__check_objects(N_state_model())


    def test_noe_method_args(self):
        """The NOE object public method args check."""

        # Check.
        self.__check_method_args(Noe())


    def test_noe_objects(self):
        """The NOE object public objects check."""

        # Check.
        self.__check_objects(Noe())


    def test_relax_fit_method_args(self):
        """The relaxation curve fitting object public method args check."""

        # Check.
        self.__check_method_args(Relax_fit())


    def test_relax_fit_objects(self):
        """The relaxation curve fitting object public objects check."""

        # Check.
        self.__check_objects(Relax_fit())


    def test_relax_disp_method_args(self):
        """The relaxation dispersion curve fitting object public method args check."""

        # Check.
        self.__check_method_args(Relax_disp())


    def test_relax_disp_objects(self):
        """The relaxation dispersion curve fitting object public objects check."""

        # Check.
        self.__check_objects(Relax_disp())
