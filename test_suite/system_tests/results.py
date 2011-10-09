###############################################################################
#                                                                             #
# Copyright (C) 2008-2011 Edward d'Auvergne                                   #
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
from tempfile import mktemp

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


class Results(SystemTestCase):
    """TestCase class for the functional tests for the relax results files."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create a data pipe.
        self.interpreter.pipe.create('test', 'relax_fit')

        # Create a temporary file name.
        ds.tmpfile = mktemp()


    def test_read_empty_results(self):
        """Test the reading of an empty results file."""

        # Read the results.
        self.interpreter.results.read(file='empty', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'results_files'+sep)


    def test_write_empty_results(self):
        """Test the writing of an empty results file."""

        # Write the results.
        self.interpreter.results.write(file=ds.tmpfile, dir=None)
