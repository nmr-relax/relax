###############################################################################
#                                                                             #
# Copyright (C) 2008-2010 Edward d'Auvergne                                   #
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
from math import pi, sqrt
from os import sep
import sys

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()


class N_state_model(SystemTestCase):
    """Class for testing various aspects specific to the N-state model."""

    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_5_state_xz(self):
        """A 5-state model in the xz-plane (no pivotting of alpha).

        The 5 states correspond to the Euler angles (z-y-z notation):
            - State 1:    {0, pi/4, 0}
            - State 2:    {0, pi/8, 0}
            - State 3:    {0, 0, 0}
            - State 4:    {0, -pi/8, 0}
            - State 5:    {0, -pi/4, 0}
        """

        # Execute the script.
        self.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'5_state_xz.py')

        # Test the optimised probabilities.
        self.assertAlmostEqual(cdp.probs[0], 0.2)
        self.assertAlmostEqual(cdp.probs[1], 0.2)
        self.assertAlmostEqual(cdp.probs[2], 0.2)
        self.assertAlmostEqual(cdp.probs[3], 0.2)
        self.assertAlmostEqual(cdp.probs[4], 0.2)

        # Test the optimised alpha Euler angles.
        self.assertAlmostEqual(cdp.alpha[0], 0.0)
        self.assertAlmostEqual(cdp.alpha[1], 0.0)
        self.assertAlmostEqual(cdp.alpha[2], 0.0)
        self.assertAlmostEqual(cdp.alpha[3], 0.0)
        self.assertAlmostEqual(cdp.alpha[4], 0.0)

        # Test the optimised beta Euler angles.
        self.assertAlmostEqual(cdp.beta[0], pi/4)
        self.assertAlmostEqual(cdp.beta[1], pi/8)
        self.assertAlmostEqual(cdp.beta[2], 0.0)
        self.assertAlmostEqual(cdp.beta[3], -pi/8)
        self.assertAlmostEqual(cdp.beta[4], -pi/4)

        # Test the optimised gamma Euler angles.
        self.assertAlmostEqual(cdp.gamma[0], 0.0)
        self.assertAlmostEqual(cdp.gamma[1], 0.0)
        self.assertAlmostEqual(cdp.gamma[2], 0.0)
        self.assertAlmostEqual(cdp.gamma[3], 0.0)
        self.assertAlmostEqual(cdp.gamma[4], 0.0)

        # Test the chi-squared.
        self.assertAlmostEqual(cdp.chi2, 3.15009916529e-32)


    def test_align_fit(self):
        """Test the use of RDCs and PCSs to find the alignment tensor."""

        # Set the mode to use both RDCs and PCSs.
        ds.mode = 'all'

        # Execute the script.
        self.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000)
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)
        self.assertAlmostEqual(cdp.q_pcs, 0.0)


    def test_align_fit_rand(self):
        """Test the use of randomised RDCs and PCSs to find the alignment tensor."""

        # Set the mode to use both RDCs and PCSs.
        ds.mode = 'all'

        # Select the randomised data.
        ds.rand = True

        # Execute the script.
        self.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

        # Test the optimised values (these values are from relax, so are not 100% reliable as a check).
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.000189412096996)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.000271130087923)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.000264898401302)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.000284115871058)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.000152207413184)
        self.assertAlmostEqual(cdp.chi2, 783.530808266)
        self.assertAlmostEqual(cdp.q_pcs, 0.063345784112045375)
        self.assertAlmostEqual(cdp.q_rdc, 0.084926009099013003)


    def test_align_fit_pcs(self):
        """Test the use of PCSs to find the alignment tensor."""

        # Set the mode to use PCSs.
        ds.mode = 'pcs'

        # Execute the script.
        self.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000)
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_pcs, 0.0)


    def test_align_fit_pcs_rand(self):
        """Test the use of randomised PCSs to find the alignment tensor."""

        # Set the mode to use PCSs.
        ds.mode = 'pcs'

        # Select the randomised data.
        ds.rand = True

        # Execute the script.
        self.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

        # Test the optimised values (these values are from relax, so are not 100% reliable as a check).
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.000189165581069)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.000271897288335)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.000264627388896)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.000284180080857)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.00015165641132)
        self.assertAlmostEqual(cdp.chi2, 756.268087443)
        self.assertAlmostEqual(cdp.q_pcs, 0.063341567973121266)


    def test_align_fit_rdc(self):
        """Test the use of RDCs to find the alignment tensor."""

        # Set the mode to use RDCs.
        ds.mode = 'rdc'

        # Execute the script.
        self.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000)
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)


    def test_align_fit_rdc_rand(self):
        """Test the use of randomised RDCs to find the alignment tensor."""

        # Set the mode to use RDCs.
        ds.mode = 'rdc'

        # Select the randomised data.
        ds.rand = True

        # Execute the script.
        self.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

        # Test the optimised values (these are about ~10% different from Pales).
        # Pales:      S(zz)       S(xx-yy)      S(xy)      S(xz)      S(yz)
        # Pales:  -9.8124e-05 -5.2533e-04 -3.4446e-04  3.7369e-04 -1.8949e-04
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.00017045)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.00024905)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.00027502)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.00029833)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.00015125)
        self.assertAlmostEqual(cdp.chi2, 23.5877482365)                 # Pales: 23.709
        self.assertAlmostEqual(cdp.q_rdc, 0.078460000413257444)       # Pales (Q Saupe): 0.079


    def test_lactose_n_state(self):
        """The 4-state model analysis of lactose using RDCs and PCSs."""

        # Execute the script.
        self.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'lactose_n_state.py')
