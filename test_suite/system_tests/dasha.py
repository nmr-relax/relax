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
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import spin_loop
from lib.io import test_binary
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Dasha(SystemTestCase):
    """Class for testing various aspects specific to model-free analysis using the program 'Dasha'."""

    def __init__(self, methodName='runTest'):
        """Skip the tests if the subprocess module is not available (Python 2.3 and earlier).

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(Dasha, self).__init__(methodName)

        # Missing module.
        if not dep_check.subprocess_module:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'subprocess', self._skip_type])

        # Test for the presence of the Dasha binary (skip the test if not present).
        try:
            test_binary('dasha')
        except:
            status.skipped_tests.append([methodName, 'Dasha model-free software', self._skip_type])


    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('dasha', 'mf')

        # Create a temporary directory for Dasha outputs.
        ds.tmpdir = mkdtemp()


    def test_dasha(self):
        """Test a complete model-free analysis using the program 'Dasha'."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'dasha.py')

        # Check the global data.
        self.assertEqual(len(cdp.ri_ids), 3)
        for ri_id in cdp.ri_ids:
            self.assertEqual(cdp.spectrometer_frq[ri_id], 600000000.0)
        self.assertEqual(cdp.ri_type['R1_600'], 'R1')
        self.assertEqual(cdp.ri_type['R2_600'], 'R2')
        self.assertEqual(cdp.ri_type['NOE_600'], 'NOE')

        # The spin data.
        select = [True, True, False, False]
        fixed = [False, False, False, False]
        isotope = ['15N', '15N', '15N', '15N']
        model = ['m3', 'm3', 'm3', 'm3']
        equation = ['mf_orig', 'mf_orig', 'mf_orig', 'mf_orig']
        params = [['s2', 'rex'], ['s2', 'rex'], ['s2', 'rex'], ['s2', 'rex']]
        s2 = [0.71510, 0.64359, None, None]
        s2f = [None, None, None, None]
        s2s = [None, None, None, None]
        local_tm = [None, None, None, None]
        te = [None, None, None, None]
        tf = [None, None, None, None]
        ts = [None, None, None, None]
        rex_scale = 1.0 / (2.0 * pi * cdp.spectrometer_frq[cdp.ri_ids[0]]) ** 2
        rex = [4.32701*rex_scale, 4.29432*rex_scale, None, None]
        csa = [-172e-6, -172e-6, -172e-6, -172e-6]
        chi2 = [1.9657, 0.63673, None, None]
        ri_data = [{'R1_600': 1.0, 'R2_600': 15.0, 'NOE_600': 0.9},
                   {'R1_600': 0.9, 'R2_600': 13.9, 'NOE_600': 0.79},
                   {'R2_600': 12.0, 'NOE_600': 0.6},
                   None]
        ri_data_err = [{'R1_600': 0.05, 'R2_600': 0.5, 'NOE_600': 0.05},
                       {'R1_600': 0.05, 'R2_600': 0.8, 'NOE_600': 0.05},
                       {'R2_600': 0.5, 'NOE_600': 0.05},
                       None]

        # Check the spin data.
        i = 0
        for spin in spin_loop():
            # Protons.
            if spin.isotope == '1H':
                self.assertEqual(spin.select, False)
                continue

            # Check the data.
            self.assertEqual(spin.select, select[i])
            self.assertEqual(spin.fixed, fixed[i])
            self.assertEqual(spin.isotope, isotope[i])
            self.assertEqual(spin.model, model[i])
            self.assertEqual(spin.equation, equation[i])
            self.assertEqual(spin.params, params[i])
            self.assertEqual(spin.s2, s2[i])
            self.assertEqual(spin.s2f, s2f[i])
            self.assertEqual(spin.s2s, s2s[i])
            self.assertEqual(spin.local_tm, local_tm[i])
            self.assertEqual(spin.te, te[i])
            self.assertEqual(spin.tf, tf[i])
            self.assertEqual(spin.ts, ts[i])
            self.assertEqual(spin.rex, rex[i])
            self.assertAlmostEqual(spin.csa, csa[i])
            self.assertEqual(spin.chi2, chi2[i])
            if ri_data[i] == None:
                self.assert_(not hasattr(spin, 'ri_data'))
            else:
                for ri_id in cdp.ri_ids:
                    if ri_id in ri_data[i]:
                        self.assertEqual(spin.ri_data[ri_id], ri_data[i][ri_id])

            # Increment the spin index.
            i += 1

        # Check the interatomic data.
        r = [1.02e-10, 1.02e-10, 1.02e-10, 1.02e-10]
        i = 0
        for interatom in interatomic_loop():
            self.assertAlmostEqual(interatom.r, r[i])
            i += 1
