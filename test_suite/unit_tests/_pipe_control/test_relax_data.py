###############################################################################
#                                                                             #
# Copyright (C) 2007-2013 Edward d'Auvergne                                   #
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
from unittest import TestCase

# relax module imports.
from pipe_control import relax_data
from test_suite.unit_tests.relax_data_testing_base import Relax_data_base_class


class Container:
    """Empty class to act as a container."""


class Test_relax_data(Relax_data_base_class, TestCase):
    """Unit tests for the functions of the 'pipe_control.relax_data' module."""

    # Place the pipe_control.relax_data module into the class namespace.
    relax_data_fns = relax_data
