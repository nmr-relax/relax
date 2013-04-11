###############################################################################
#                                                                             #
# Copyright (C) 2006-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
from os import sep
from shutil import rmtree
from tempfile import mkdtemp

# relax module imports.
from auto_analyses import relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


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


    def test_hansen_cpmg_data_fast_2site(self):
        """Optimisation of Fleming Hansen's CPMG data to the fast 2-site dispersion model."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'hansen_data_fast_2site.py')


    def test_hansen_cpmg_data_slow_2site(self):
        """Optimisation of Fleming Hansen's CPMG data to the slow 2-site dispersion model."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'hansen_data_slow_2site.py')


    def test_exp_fit(self):
        """Test the relaxation dispersion 'exp_fit' model curve fitting."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'exp_fit.py')

        # The original exponential curve parameters.
        res_data = [
            [15., 10., 20000., 25000.],
            [12., 11., 50000., 51000.],
            [17., 9., 100000., 96000.]
        ]

        # List of parameters which do not belong to the model.
        blacklist = ['cpmg_frqs', 'r2', 'rex', 'kex', 'r2a', 'ka', 'dw']

        # Checks for each residue.
        for i in range(len(res_data)):
            # Printout.
            print("\nResidue number %s." % (i+1))

            # Check the fitted parameters.
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].r2eff[1000.0], res_data[i][0], places=2)
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].r2eff[2000.0], res_data[i][1], places=2)
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].i0[1000.0]/10000, res_data[i][2]/10000, places=3)
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].i0[2000.0]/10000, res_data[i][3]/10000, places=3)

            # Check the simulation errors.
            self.assert_(cdp.mol[0].res[i].spin[0].r2eff_err[1000.0] < 5.0)
            self.assert_(cdp.mol[0].res[i].spin[0].r2eff_err[2000.0] < 5.0)
            self.assert_(cdp.mol[0].res[i].spin[0].i0_err[1000.0]/10000 < 5.0)
            self.assert_(cdp.mol[0].res[i].spin[0].i0_err[2000.0]/10000 < 5.0)

            # Check that certain parameters are not present.
            for param in blacklist:
                print("\tChecking for the absence of the '%s' parameter." % param)
                self.assert_(not hasattr(cdp.mol[0].res[i].spin[0], param))


    def test_read_r2eff(self):
        """Test the reading of a file containing r2eff values."""

        # Create the sequence data, and name the spins.
        self.interpreter.residue.create(1, 'Gly')
        self.interpreter.residue.create(2, 'Gly')
        self.interpreter.residue.create(3, 'Gly')

        # Read the file.
        self.interpreter.relax_data.read(ri_id='R2eff.600', ri_type='R2eff', frq=600*1e6, file='r2eff.out', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting_disp'+sep+'r2eff', res_num_col=1, res_name_col=2, data_col=3, error_col=4)

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].ri_data['R2eff.600'], 15.000)
        self.assertEqual(cdp.mol[0].res[1].spin[0].ri_data['R2eff.600'], 4.2003)
        self.assertEqual(cdp.mol[0].res[2].spin[0].ri_data['R2eff.600'], 7.2385)
