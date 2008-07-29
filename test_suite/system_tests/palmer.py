###############################################################################
#                                                                             #
# Copyright (C) 2008 Sebastien Morin                                          #
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
import sys
from shutil import rmtree
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from relax_io import test_binary


class Palmer(TestCase):
    """Class for testing various aspects specific to model-free analysis using the program
    'Modelfree4'.
    """


    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('palmer', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()

        # Remove the temporary directory created during the execution of the test_palmer() function.
        rmtree(sys.path[-1] + '/test_suite/system_tests/data/temp_palmer/')


    def test_palmer(self):
        """Test a complete model-free analysis using the program 'Modelfree4'."""

        # Test for the presence of the Modelfree4 binary (skip the test if not present).
        try:
            test_binary('modelfree4')
        except:
            return

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/palmer.py')
