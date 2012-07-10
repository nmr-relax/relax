###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""Unit test module for the prompt.uf_objects module."""

# Python module imports.
from unittest import TestCase

# relax module imports.
from prompt.uf_objects import Class_container, Uf_object
from user_functions.data import Uf_info; uf_info = Uf_info()


class Test_uf_objects(TestCase):
    """Unit test case for the prompt.uf_objects module."""

    def test_uf_class_build_doc(self):
        """Test the _build_doc() method of all the prompt user function classes."""

        # Loop over the classes.
        for name, data in uf_info.class_loop():
            # Print out.
            print(name)

            # Generate a new container.
            obj = Class_container(name, data.title)

            # Create the documentation and print it.
            text = obj._build_doc()


    def test_uf_object_build_doc(self):
        """Test the _build_doc() method of all the prompt user function objects."""

        # Loop over the classes.
        for name, data in uf_info.uf_loop():
            # Print out.
            print(name)

            # Generate a new container.
            obj = Uf_object(name, title=data.title, kargs=data.kargs, backend=data.backend, desc=data.desc)

            # Create the documentation and print it.
            text = obj._build_doc()
