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
from math import pi
import sys
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import return_spin
from relax_io import test_binary


class Palmer(TestCase):
    """Class for testing various aspects specific to model-free analysis using the program
    'Modelfree4'.
    """


    def setUp(self):
        """Set up for all the functional tests."""

        # Create a temporary directory for ModelFree4 outputs.
        ds.tmpdir = mkdtemp()


    def tearDown(self):
        """Reset the relax data storage object."""

        # Remove the temporary directory.
        rmtree(ds.tmpdir)

        # Reset the relax data storage object.
        ds.__reset__()


    def test_palmer(self):
        """Test a complete model-free analysis using the program 'Modelfree4'."""

        # Test for the presence of the Modelfree4 binary (skip the test if not present).
        try:
            test_binary('modelfree4')
        except:
            return

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/palmer.py')

        # Checks for model m1 mfout file reading.
        models = ['m1', 'm2', 'm3']
        params = [['S2'], ['S2', 'te'], ['S2', 'Rex']]
        spin_names = [':-2&:Gly', ':-1&:Gly', ':0&:Gly']
        s2 = [[0.869, 0.732, 0.802], [0.869, 0.730, 0.755], [0.715, 0.643, 0.734]]
        te = [[None, None, None], [0.0, 1.951, 1319.171], [None, None, None]]
        rex = [[None, None, None], [None, None, None], [4.308, 4.278, 1.017]]
        chi2 = [[36.6223, 20.3954, 5.2766], [36.6223, 20.3299, 0.0], [1.9763, 0.6307, 5.2766]]
        for model_index in xrange(3):
            print "Model " + `models[model_index]`
            for spin_index in xrange(3):
                print "Spin " + `spin_names[spin_index]`

                # Get the spin.
                spin = return_spin(spin_names[spin_index], pipe=models[model_index])

                # Conversions.
                if te[model_index][spin_index]:
                    te[model_index][spin_index] = te[model_index][spin_index] * 1e-12
                if rex[model_index][spin_index]:
                    rex[model_index][spin_index] = rex[model_index][spin_index] / (2.0 * pi * spin.frq[0])**2

                # Checks.
                self.assertEqual(spin.model, models[model_index])
                self.assertEqual(spin.params, params[model_index])
                self.assertEqual(spin.s2, s2[model_index][spin_index])
                self.assertEqual(spin.s2f, None)
                self.assertEqual(spin.s2s, None)
                self.assertEqual(spin.te, te[model_index][spin_index])
                self.assertEqual(spin.tf, None)
                self.assertEqual(spin.ts, None)
                self.assertEqual(spin.rex, rex[model_index][spin_index])
                self.assertEqual(spin.chi2, chi2[model_index][spin_index])
