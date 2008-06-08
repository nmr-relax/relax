###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
from unittest import TestCase

# relax module imports.
from specific_fns import relax_data
from relax_errors import RelaxError
from test_suite.unit_tests.relax_data_testing_base import Relax_data_base_class


class Container:
    """Empty class to act as a container."""


class Test_relax_data(Relax_data_base_class, TestCase):
    """Unit tests for the functions of the 'specific_fns.relax_data' module."""

    # Place the specific_fns.relax_data module into the class namespace.
    relax_data_fns = relax_data.Rx_data()


    def test_data_init_spin(self):
        """Initial relaxation data structures placed into a spin container.

        The function tested is specific_fns.relax_data.data_init().
        """

        # Get a container instance.
        container = Container()

        # Set the global flag to zero - hence the container will be treated as a spin.
        self.relax_data_fns.global_flag = 0

        # Fill the container.
        self.relax_data_fns.data_init(container)

        # Test the contents.
        self.assertEqual(container.frq, []) 
        self.assertEqual(container.frq_labels, []) 
        self.assertEqual(container.noe_r1_table, []) 
        self.assertEqual(container.num_frq, 0) 
        self.assertEqual(container.num_ri, 0) 
        self.assertEqual(container.relax_data, []) 
        self.assertEqual(container.relax_error, []) 
        self.assertEqual(container.remap_table, []) 
        self.assertEqual(container.ri_labels, []) 


    def test_data_init_pipe(self):
        """Initial relaxation data structures placed into a pipe container.

        The function tested is specific_fns.relax_data.data_init().
        """

        # Get a container instance.
        container = Container()

        # Set the global flag to zero - hence the container will be treated as a pipe.
        self.relax_data_fns.global_flag = 1

        # Fill the container.
        self.relax_data_fns.data_init(container)

        # Test the contents.
        self.assertEqual(container.frq, []) 
        self.assertEqual(container.frq_labels, []) 
        self.assertEqual(container.noe_r1_table, []) 
        self.assertEqual(container.num_frq, 0) 
        self.assertEqual(container.num_ri, 0) 
        self.assertEqual(container.remap_table, []) 
        self.assertEqual(container.ri_labels, []) 
