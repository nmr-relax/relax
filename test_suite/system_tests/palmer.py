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
from math import pi
from os import sep
import sys
from shutil import rmtree
from tempfile import mkdtemp

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes
from generic_fns.mol_res_spin import return_spin
from relax_errors import RelaxError
from relax_io import test_binary


class Palmer(SystemTestCase):
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
        self.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'palmer.py')

        # Determine if the Gnu gcc or Portland C compiler version is being used.
        spin = return_spin(':0', pipe='m2')
        if spin.te == 1.951*1e-12:
            compiler = 'gcc'    # Gnu gcc modelfree4 version.
        else:
            compiler = 'pgf'    # Portland C compiler modelfree4 version.

        # Checks for model m1, m2, and m3 mfout file reading.
        models = ['m1', 'm2', 'm3']
        params = [['S2'], ['S2', 'te'], ['S2', 'Rex']]
        spin_names = [':-2&:Gly', ':-1&:Gly', ':0&:Gly']
        if compiler == 'gcc':
            s2 = [[0.869, 0.732, None], [0.869, 0.730, None], [0.715, 0.643, None]]
            te = [[None, None, None], [0.0, 1.951, None], [None, None, None]]    # Gnu gcc modelfree4 version.
            rex = [[None, None, None], [None, None, None], [4.308, 4.278, None]]
        else:
            s2 = [[0.869, 0.732, None], [0.869, 0.730, None], [0.715, 0.643, None]]
            te = [[None, None, None], [0.0, 1.952, None], [None, None, None]]    # Portland C compiler modelfree4 version.
            rex = [[None, None, None], [None, None, None], [4.308, 4.278, None]]
        chi2 = [[36.6223, 20.3954, None], [36.6223, 20.3299, None], [1.9763, 0.6307, None]]
        for model_index in xrange(3):
            print(("Model " + repr(models[model_index])))
            for spin_index in xrange(3):
                print(("Spin " + repr(spin_names[spin_index])))

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
                if te[model_index][spin_index] == None:
                    self.assertEqual(spin.te, te[model_index][spin_index])
                else:
                    self.assertAlmostEqual(spin.te, te[model_index][spin_index])
                self.assertEqual(spin.tf, None)
                self.assertEqual(spin.ts, None)
                self.assertEqual(spin.rex, rex[model_index][spin_index])
                self.assertEqual(spin.chi2, chi2[model_index][spin_index])

        # Checks for the final mfout file reading.
        models = ['m3', 'm3']
        params = [['S2', 'Rex'], ['S2', 'Rex']]
        s2 = [0.844, 0.760]
        te = [None, None]
        rex = [0.005, 0.404]
        chi2 = [1.7966, 0.7389]
        for spin_index in xrange(3):
            # Get the spin.
            spin = return_spin(spin_names[spin_index], pipe='aic')

            # Deselected spin.
            if not spin.select:
                continue

            # Conversions.
            if te[spin_index]:
                te[spin_index] = te[spin_index] * 1e-12
            if rex[spin_index]:
                rex[spin_index] = rex[spin_index] / (2.0 * pi * spin.frq[0])**2

            # Checks.
            self.assertEqual(spin.model, models[spin_index])
            self.assertEqual(spin.params, params[spin_index])
            self.assertEqual(spin.s2, s2[spin_index])
            self.assertEqual(spin.s2f, None)
            self.assertEqual(spin.s2s, None)
            self.assertEqual(spin.te, te[spin_index])
            self.assertEqual(spin.tf, None)
            self.assertEqual(spin.ts, None)
            self.assertEqual(spin.rex, rex[spin_index])
            self.assertEqual(spin.chi2, chi2[spin_index])

        # Final global values.
        final_pipe = pipes.get_pipe('aic')
        self.assertEqual(final_pipe.chi2, 2.5356)
        self.assertEqual(final_pipe.diff_tensor.tm, 12.045)


    def test_palmer_omp(self):
        """Test a complete model-free analysis using 'Modelfree4' with the OMP relaxation data, a PDB file, and a spheroid tensor."""

        # Test for the presence of the Modelfree4 binary (skip the test if not present).
        try:
            test_binary('modelfree4')
        except:
            return

        # Execute the script.
        self.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'palmer_omp.py')

        # Catch a the old, buggy modelfree4 versions and complain loudly!
        spin = return_spin(':9', pipe='m2')
        if spin.s2 == 0.855:
            raise RelaxError("You are using an old, buggy Modelfree4 version!  You must upgrade to version 4.20 or later.")

        # Determine if the Gnu gcc or Portland C compiler version is being used.
        if spin.te == 20.043*1e-12:
            compiler = 'gcc'    # Gnu gcc modelfree4 version.
        else:
            compiler = 'pgf'    # Portland C compiler modelfree4 version.

        # Model m1, m2, and m3 mfout file data.
        models = ['m1', 'm2', 'm3']
        params = [['S2'], ['S2', 'te'], ['S2', 'Rex']]
        spin_names = [':9', ':10', ':11']
        s2 = [[0.822, 0.799, 0.823], [0.788, 0.777, 0.812], [0.822, 0.799, 0.823]]
        if compiler == 'gcc':
            te = [[None, None, None], [61.506, 36.084, 20.043], [None, None, None]]
        else:
            te = [[None, None, None], [61.506, 36.087, 20.039], [None, None, None]]
        rex = [[None, None, None], [None, None, None], [0.0, 0.0, 0.0]]
        chi2 = [[143.6773, 105.1767, 61.6684], [40.9055, 57.1562, 48.4927], [143.6773, 105.1767, 61.6684]]

        # Checks for model m1, m2, and m3 mfout file reading.
        for model_index in xrange(3):
            print(("Model " + repr(models[model_index])))
            for spin_index in xrange(3):
                print(("Spin " + repr(spin_names[spin_index])))

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

        # Final mfout file data.
        models = ['m2', 'm2', 'm2']
        params = [['S2', 'te'], ['S2', 'te'], ['S2', 'te']]
        if compiler == 'gcc':
            s2 = [0.782, 0.760, 0.785]
            te = [60.009, 29.134, 12.590]
            chi2 = [24.0495, 8.1168, 0.5332]
        else:
            s2 = [0.755, 0.761, 0.787]
            te = [52.197, 29.361, 12.677]
            chi2 = [7.254, 8.0437, 0.5327]

        # Checks for the final mfout file reading.
        for spin_index in xrange(3):
            # Get the spin.
            spin = return_spin(spin_names[spin_index], pipe='aic')

            # Conversions.
            if te[spin_index]:
                te[spin_index] = te[spin_index] * 1e-12

            # Checks.
            self.assertEqual(spin.model, models[spin_index])
            self.assertEqual(spin.params, params[spin_index])
            self.assertEqual(spin.s2, s2[spin_index])
            self.assertEqual(spin.s2f, None)
            self.assertEqual(spin.s2s, None)
            self.assertAlmostEqual(spin.te, te[spin_index])
            self.assertEqual(spin.tf, None)
            self.assertEqual(spin.ts, None)
            self.assertEqual(spin.rex, None)
            self.assertEqual(spin.chi2, chi2[spin_index])

        # Final global values.
        final_pipe = pipes.get_pipe('aic')
        if compiler == 'gcc':
            self.assertEqual(final_pipe.chi2, 32.6995)
            self.assertEqual(final_pipe.diff_tensor.tm, 8.964)
            self.assertEqual(final_pipe.diff_tensor.Dratio, 1.324)
            self.assertEqual(final_pipe.diff_tensor.theta, (-52.070 / 360.0) * 2.0 * pi + pi)
            self.assertEqual(final_pipe.diff_tensor.phi, (2.377 / 360.0) * 2.0 * pi)
        else:
            self.assertEqual(final_pipe.chi2, 15.8304)
            self.assertEqual(final_pipe.diff_tensor.tm, 8.443)
            self.assertEqual(final_pipe.diff_tensor.Dratio, 1.053)
            self.assertEqual(final_pipe.diff_tensor.theta, (68.864 / 360.0) * 2.0 * pi)
            self.assertEqual(final_pipe.diff_tensor.phi, (73.913 / 360.0) * 2.0 * pi)
