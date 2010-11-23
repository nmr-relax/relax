###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
import __main__
from os import sep
from shutil import rmtree
from tempfile import mkdtemp

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()


class Relax_disp(SystemTestCase):
    """Class for testing various aspects specific to relaxation dispersion curve-fitting."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('relax_disp', 'relax_disp')

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()
        self.tmpdir = ds.tmpdir


    def tearDown(self):
        """Reset the relax data storage object."""

        # Remove the temporary directory.
        rmtree(self.tmpdir)

        # Reset the relax data storage object.
        ds.__reset__()


    def test_curve_fitting_cpmg_fast(self):
        """Test the relaxation dispersion curve fitting C modules for CPMG data in the
        fast-exchange limit."""

        # Execute the script.
        self.interpreter.run(script_file=__main__.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp_cpmg_fast.py')


    def test_curve_fitting_cpmg_slow(self):
        """Test the relaxation dispersion curve fitting C modules for CPMG data in the
        slow-exchange limit."""

        # Execute the script.
        self.interpreter.run(script_file=__main__.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp_cpmg_slow.py')


    def test_read_r2eff(self):
        """Test the reading of a file containing r2eff values."""

        # Create the sequence data, and name the spins.
        self.interpreter.residue.create(1, 'Gly')
        self.interpreter.residue.create(2, 'Gly')
        self.interpreter.residue.create(3, 'Gly')

        # Read the file.
        self.interpreter.relax_data.read('R2eff', '600', 600 * 1e6, 'r2eff.out', dir=__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting_disp'+sep+'r2eff')

        # Test the data.

        self.assertEqual(cdp.mol[0].res[0].spin[0].relax_data[0], 15.000)
        self.assertEqual(cdp.mol[0].res[1].spin[0].relax_data[0], 4.2003)
        self.assertEqual(cdp.mol[0].res[2].spin[0].relax_data[0], 7.2385)
