###############################################################################
#                                                                             #
# Copyright (C) 2008 Sebastien Morin                                          #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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
from tempfile import mkdtemp

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import spin_loop
from relax_io import test_binary
from status import Status; status = Status()


class Dasha(SystemTestCase):
    """Class for testing various aspects specific to model-free analysis using the program 'Dasha'."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('dasha', 'mf')

        # Create a temporary directory for Dasha outputs.
        ds.tmpdir = mkdtemp()


    def test_dasha(self):
        """Test a complete model-free analysis using the program 'Dasha'."""

        # Test for the presence of the Dasha binary (skip the test if not present).
        try:
            test_binary('dasha')
        except:
            return

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'dasha.py')

        # Check the global data.
        self.assertEqual(cdp.chi2, 0.63673000000000002)
        self.assertEqual(len(cdp.ri_ids), 3)
        for ri_id in cdp.ri_ids:
            self.assertEqual(cdp.frq[ri_id], 600000000.0)
        self.assertEqual(cdp.ri_type['R1_600'], 'R1')
        self.assertEqual(cdp.ri_type['R2_600'], 'R2')
        self.assertEqual(cdp.ri_type['NOE_600'], 'NOE')

        # The spin data.
        select = [True, True, False]
        fixed = [None, None, None]
        proton_type = [None, None, None]
        heteronuc_type = ['15N', '15N', '15N']
        attached_proton = [None, None, None]
        nucleus = [None, None, None]
        model = ['m3', 'm3', 'm3']
        equation = ['mf_orig', 'mf_orig', 'mf_orig']
        params = [['S2', 'Rex'], ['S2', 'Rex'], ['S2', 'Rex']]
        xh_vect = [None, None, None]
        s2 = [0.64359, 0.64359, 0.64359]
        s2f = [None, None, 0.8]
        s2s = [None, None, 0.8]
        local_tm = [None, None, None]
        te = [None, None, 0.01]
        tf = [None, None, 0.001]
        ts = [None, None, 0.1]
        rex = [4.29432, 4.29432, 4.29432]
        r = [1.02e-10, 1.02e-10, 1.02e-10]
        csa = [-172e-6, -172e-6, -172e-6]
        chi2 = [None, None, None]
        ri_data = [{'R1_600': 1.0, 'R2_600': 15.0, 'NOE_600': 0.9},
                   {'R1_600': 0.9, 'R2_600': 13.9, 'NOE_600': 0.79},
                   {'R2_600': 12.0, 'NOE_600': 0.6}]
        ri_data_err = [{'R1_600': 0.05, 'R2_600': 0.5, 'NOE_600': 0.05},
                       {'R1_600': 0.05, 'R2_600': 0.8, 'NOE_600': 0.05},
                       {'R2_600': 0.5, 'NOE_600': 0.05}]

        # Check the spin data.
        i = 0
        for spin in spin_loop():
            # Check the data.
            self.assertEqual(spin.select, select[i])
            self.assertEqual(spin.fixed, fixed[i])
            self.assertEqual(spin.proton_type, proton_type[i])
            self.assertEqual(spin.heteronuc_type, heteronuc_type[i])
            self.assertEqual(spin.attached_proton, attached_proton[i])
            self.assertEqual(spin.nucleus, nucleus[i])
            self.assertEqual(spin.model, model[i])
            self.assertEqual(spin.equation, equation[i])
            self.assertEqual(spin.params, params[i])
            self.assertEqual(spin.xh_vect, xh_vect[i])
            self.assertEqual(spin.s2, s2[i])
            self.assertEqual(spin.s2f, s2f[i])
            self.assertEqual(spin.s2s, s2s[i])
            self.assertEqual(spin.local_tm, local_tm[i])
            self.assertEqual(spin.te, te[i])
            self.assertEqual(spin.tf, tf[i])
            self.assertEqual(spin.ts, ts[i])
            self.assertEqual(spin.rex, rex[i])
            self.assertAlmostEqual(spin.r, r[i])
            self.assertAlmostEqual(spin.csa, csa[i])
            self.assertEqual(spin.chi2, chi2[i])
            for ri_id in cdp.ri_ids:
                if ri_id in ri_data[i].keys():
                    self.assertEqual(spin.ri_data[ri_id], ri_data[i][ri_id])

            # Increment the spin index.
            i += 1
