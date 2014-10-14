###############################################################################
#                                                                             #
# Copyright (C) 2008 Sebastien Morin                                          #
# Copyright (C) 2010-2014 Edward d'Auvergne                                   #
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
from math import pi
from os import sep
from tempfile import mkdtemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from pipe_control import pipes
from pipe_control.mol_res_spin import return_spin
from lib.errors import RelaxError
from lib.io import test_binary
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Palmer(SystemTestCase):
    """Class for testing various aspects specific to model-free analysis using the program 'Modelfree4'."""

    def __init__(self, methodName='runTest'):
        """Skip the tests if the subprocess module is not available (Python 2.3 and earlier).

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(Palmer, self).__init__(methodName)

        # Missing module.
        if not dep_check.subprocess_module:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'subprocess', self._skip_type])

        # Test for the presence of the Modelfree4 binary (skip the test if not present).
        try:
            test_binary('modelfree4')
        except:
            status.skipped_tests.append([methodName, "Art Palmer's Modelfree4 software", self._skip_type])


    def setUp(self):
        """Set up for all the functional tests."""

        # Create a temporary directory for ModelFree4 outputs.
        ds.tmpdir = mkdtemp()


    def test_palmer(self):
        """Test a complete model-free analysis using the program 'Modelfree4'."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'palmer.py')

        # Determine if the Gnu gcc or Portland C compiler version is being used.
        spin = return_spin(':0@N', pipe='m2')
        if spin.te == 1.951*1e-12:
            binary = 'linux-i386-gcc'   # Linux Gnu gcc modelfree4 version.
        else:
            binary = 'linux-i386-pgf'   # Linux Portland C compiler modelfree4 version.
        spin = return_spin(':-2@N', pipe='m1')
        if spin.chi2 == 36.62:
            binary = 'mac-i386'         # Mac OS X intel binary.
        if not binary:
            raise RelaxError("The Modelfree4 binary cannot be identified, therefore the parameters cannot be meaningfully checked.")
        print("\nDetected the '%s' Modelfree4 binary." % binary)

        # Checks for model m1, m2, and m3 mfout file reading.
        models = ['m1', 'm2', 'm3']
        params = [['s2'], ['s2', 'te'], ['s2', 'rex']]
        spin_names = [':-2@N', ':-1@N', ':0@N']
        s2 = [[0.869, 0.732, None], [0.869, 0.730, None], [0.715, 0.643, None]]
        if binary == 'linux-i386-gcc':
            te = [[None, None, None], [0.0, 1.951, None], [None, None, None]]
        else:
            te = [[None, None, None], [0.0, 1.952, None], [None, None, None]]
        rex = [[None, None, None], [None, None, None], [4.308, 4.278, None]]
        chi2 = [[36.6223, 20.3954, None], [36.6223, 20.3299, None], [1.9763, 0.6307, None]]
        if binary == 'mac-i386':
            chi2 = [[36.62, 20.40, None], [36.62, 20.33, None], [1.976, 0.6307, None]]
        for model_index in range(3):
            print("Model " + repr(models[model_index]))
            for spin_index in range(3):
                print("Spin " + repr(spin_names[spin_index]))

                # Get the spin.
                spin = return_spin(spin_names[spin_index], pipe=models[model_index])

                # Conversions.
                if te[model_index][spin_index]:
                    te[model_index][spin_index] = te[model_index][spin_index] * 1e-12
                if rex[model_index][spin_index]:
                    rex[model_index][spin_index] = rex[model_index][spin_index] / (2.0 * pi * cdp.spectrometer_frq[cdp.ri_ids[0]])**2

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
        params = [['s2', 'rex'], ['s2', 'rex']]
        s2 = [0.844, 0.760]
        te = [None, None]
        rex = [0.005, 0.404]
        chi2 = [1.7966, 0.7389]
        if binary == 'mac-i386':
            chi2 = [1.796, 0.7392]
        for spin_index in range(3):
            # Get the spin.
            spin = return_spin(spin_names[spin_index], pipe='aic')

            # Deselected spin.
            if not spin.select:
                continue

            # Conversions.
            if te[spin_index]:
                te[spin_index] = te[spin_index] * 1e-12
            if rex[spin_index]:
                rex[spin_index] = rex[spin_index] / (2.0 * pi * cdp.spectrometer_frq[cdp.ri_ids[0]])**2

            # Checks.
            self.assertEqual(spin.model, models[spin_index])
            self.assertEqual(spin.params, params[spin_index])
            self.assertAlmostEqual(spin.s2, s2[spin_index])
            self.assertEqual(spin.s2f, None)
            self.assertEqual(spin.s2s, None)
            if te[spin_index]:
                self.assertAlmostEqual(spin.te, te[spin_index])
            else:
                self.assertEqual(spin.te, None)
            self.assertEqual(spin.tf, None)
            self.assertEqual(spin.ts, None)
            self.assertAlmostEqual(spin.rex, rex[spin_index])
            self.assertEqual(spin.chi2, chi2[spin_index])

        # Final global values.
        final_pipe = pipes.get_pipe('aic')
        if binary == 'mac-i386':
            self.assertAlmostEqual(final_pipe.chi2, 2.5355)
            self.assertAlmostEqual(final_pipe.diff_tensor.tm, 12.051)
        else:
            self.assertAlmostEqual(final_pipe.chi2, 2.5356)
            self.assertAlmostEqual(final_pipe.diff_tensor.tm, 12.045)


    def test_palmer_omp(self):
        """Test a complete model-free analysis using 'Modelfree4' with the OMP relaxation data, a PDB file, and a spheroid tensor."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'palmer_omp.py')

        # Catch a the old, buggy modelfree4 versions and complain loudly!
        spin = return_spin(':9@N', pipe='m2')
        if spin.s2 == 0.855:
            raise RelaxError("You are using an old, buggy Modelfree4 version!  You must upgrade to version 4.20 or later.")

        # Determine the Modelfree4 binary type used.
        spin = return_spin(':9@N', pipe='aic')
        binary = None
        if spin.te * 1e12 == 52.195:
            binary = 'linux-i386-gcc'   # Linux Gnu gcc modelfree4 version.
        elif spin.te * 1e12 == 52.197:
            binary = 'linux-i386-pgf'   # Linux Portland C compiler modelfree4 version.
        elif spin.te * 1e12 == 52.194:
            binary = 'linux-x86_64-gcc'   # 64-bit Linux Gnu gcc modelfree4 version.
        spin = return_spin(':9@N', pipe='m1')
        if binary == None and spin.chi2 == 143.7:
            binary = 'mac-i386'         # Mac OS X intel binary.
        if not binary:
            raise RelaxError("The Modelfree4 binary cannot be identified, therefore the parameters cannot be meaningfully checked.")
        print("\nDetected the '%s' Modelfree4 binary." % binary)

        # Model m1, m2, and m3 mfout file data.
        models = ['m1', 'm2', 'm3']
        params = [['s2'], ['s2', 'te'], ['s2', 'rex']]
        spin_names = [':9@N', ':10@N', ':11@N']
        s2 = [[0.822, 0.799, 0.823], [0.788, 0.777, 0.812], [0.822, 0.799, 0.823]]
        te = [[None, None, None], [61.506, 36.087, 20.039], [None, None, None]]
        if binary in ['mac-i386', 'linux-x86_64-gcc']:
            te = [[None, None, None], [61.504, 36.087, 20.039], [None, None, None]]
        rex = [[None, None, None], [None, None, None], [0.0, 0.0, 0.0]]
        chi2 = [[143.6773, 105.1767, 61.6684], [40.9055, 57.1562, 48.4927], [143.6773, 105.1767, 61.6684]]
        if binary in ['mac-i386', 'linux-x86_64-gcc']:
            chi2 = [[143.7, 105.2, 61.67], [40.91, 57.16, 48.49], [143.7, 105.2, 61.67]]

        # Checks for model m1, m2, and m3 mfout file reading.
        for model_index in range(3):
            print("Model " + repr(models[model_index]))
            for spin_index in range(3):
                print("Spin " + repr(spin_names[spin_index]))

                # Get the spin.
                spin = return_spin(spin_names[spin_index], pipe=models[model_index])
                print spin

                # Conversions.
                if rex[model_index][spin_index]:
                    rex[model_index][spin_index] = rex[model_index][spin_index] / (2.0 * pi * cdp.spectrometer_frq[cdp.ri_ids[0]])**2

                # Checks.
                self.assertEqual(spin.model, models[model_index])
                self.assertEqual(spin.params, params[model_index])
                self.assertAlmostEqual(spin.s2, s2[model_index][spin_index])
                self.assertEqual(spin.s2f, None)
                self.assertEqual(spin.s2s, None)
                if te[model_index][spin_index]:
                    self.assertAlmostEqual(spin.te * 1e12, te[model_index][spin_index])
                self.assertEqual(spin.tf, None)
                self.assertEqual(spin.ts, None)
                self.assertEqual(spin.rex, rex[model_index][spin_index])
                self.assertEqual(spin.chi2, chi2[model_index][spin_index])

        # Final mfout file data.
        models = ['m2', 'm2', 'm2']
        params = [['s2', 'te'], ['s2', 'te'], ['s2', 'te']]
        s2 = [0.755, 0.761, 0.787]
        if binary == 'linux-i386-gcc':
            te = [52.195, 29.356, 12.678]
        elif binary == 'linux-i386-pgf':
            te = [52.197, 29.361, 12.677]
        elif binary == 'mac-i386':
            te = [52.197, 29.357, 12.676]
        elif binary == 'linux-x86_64-gcc':
            te = [52.194, 29.359, 12.677]
        chi2 = [7.254, 8.0437, 0.5327]
        if binary in ['mac-i386', 'linux-x86_64-gcc']:
            chi2 = [7.254, 8.044, 0.5327]

        # Checks for the final mfout file reading.
        for spin_index in range(3):
            # Get the spin.
            spin = return_spin(spin_names[spin_index], pipe='aic')

            # Checks.
            self.assertEqual(spin.model, models[spin_index])
            self.assertEqual(spin.params, params[spin_index])
            self.assertAlmostEqual(spin.s2, s2[spin_index])
            self.assertEqual(spin.s2f, None)
            self.assertEqual(spin.s2s, None)
            if te[spin_index]:
                self.assertAlmostEqual(spin.te * 1e12, te[spin_index])
            self.assertEqual(spin.tf, None)
            self.assertEqual(spin.ts, None)
            self.assertEqual(spin.rex, None)
            self.assertAlmostEqual(spin.chi2, chi2[spin_index])

        # Final global values.
        final_pipe = pipes.get_pipe('aic')
        self.assertEqual(final_pipe.chi2, 15.8304)
        if binary == 'linux-i386-gcc':
            self.assertAlmostEqual(final_pipe.diff_tensor.tm, 8.443)
            self.assertAlmostEqual(final_pipe.diff_tensor.Dratio, 1.053)
            self.assertAlmostEqual(final_pipe.diff_tensor.theta * 360 / 2.0 / pi, 68.592)
            self.assertAlmostEqual(final_pipe.diff_tensor.phi * 360 / 2.0 / pi, 73.756)
        elif binary == 'linux-i386-pgf':
            self.assertAlmostEqual(final_pipe.diff_tensor.tm, 8.443)
            self.assertAlmostEqual(final_pipe.diff_tensor.Dratio, 1.053)
            self.assertAlmostEqual(final_pipe.diff_tensor.theta * 360 / 2.0 / pi, 68.864)
            self.assertAlmostEqual(final_pipe.diff_tensor.phi * 360 / 2.0 / pi, 73.913)
        elif binary == 'mac-i386':
            self.assertAlmostEqual(final_pipe.diff_tensor.tm, 8.459)
            self.assertAlmostEqual(final_pipe.diff_tensor.Dratio, 1.049)
            self.assertAlmostEqual(final_pipe.diff_tensor.theta * 360 / 2.0 / pi, 64.611)
            self.assertAlmostEqual(final_pipe.diff_tensor.phi * 360 / 2.0 / pi, 79.281)
        elif binary == 'linux-x86_64-gcc':
            self.assertAlmostEqual(final_pipe.diff_tensor.tm, 8.445)
            self.assertAlmostEqual(final_pipe.diff_tensor.Dratio, 1.052)
            self.assertAlmostEqual(final_pipe.diff_tensor.theta * 360 / 2.0 / pi, 68.245)
            self.assertAlmostEqual(final_pipe.diff_tensor.phi * 360 / 2.0 / pi, 74.290)
