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
from os import remove
import sys
from tempfile import mktemp
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


class Bmrb(TestCase):
    """TestCase class for functional tests of the reading and writing of BMRB STAR formatted files."""

    def setUp(self):
        """Common set up for these system tests."""

        # Create a temporary file name.
        ds.tmpfile = mktemp()


    def tearDown(self):
        """Reset the relax data storage object."""

        # Delete the temporary file.
        try:
            remove(ds.tmpfile)
        except OSError:
            pass

        # Reset the relax data storage object.
        ds.__reset__()


    def test_rw_bmrb_3_0_model_free(self):
        """Write and then read a BRMB STAR formatted file containing model-free results."""

        # Set the NMR-STAR version.
        ds.version = '3.0'

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/bmrb_rw.py')


    def test_rw_bmrb_3_1_model_free(self):
        """Write and then read a BRMB STAR formatted file containing model-free results."""

        # Set the NMR-STAR version.
        ds.version = '3.1'

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/bmrb_rw.py')


    def test_rw_bmrb_3_2_model_free(self):
        """Write and then read a BRMB STAR formatted file containing model-free results."""

        # Set the NMR-STAR version.
        ds.version = '3.2'

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/bmrb_rw.py')
