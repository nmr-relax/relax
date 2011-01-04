###############################################################################
#                                                                             #
# Copyright (C) 2008 Sebastien Morin                                          #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
from os import sep
import sys
from shutil import rmtree
from tempfile import mkdtemp

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from relax_io import test_binary
from status import Status; status = Status()


class Dasha(SystemTestCase):
    """Class for testing various aspects specific to model-free analysis using the program
    'Dasha'.
    """


    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('dasha', 'mf')

        # Create a temporary directory for Dasha outputs.
        ds.tmpdir = mkdtemp()


    def tearDown(self):
        """Reset the relax data storage object."""

        # Remove the temporary directory.
        rmtree(ds.tmpdir)


        # Reset the relax data storage object.
        ds.__reset__()


    def test_dasha(self):
        """Test a complete model-free analysis using the program 'Dasha'."""

        # Test for the presence of the Dasha binary (skip the test if not present).
        try:
            test_binary('dasha')
        except:
            return

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'dasha.py')
