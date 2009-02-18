###############################################################################
#                                                                             #
# Copyright (C) 2008-2009 Edward d'Auvergne                                   #
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
import sys
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes


class N_state_model(TestCase):
    """Class for testing various aspects specific to the N-state model."""

    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_5_state_xz(self):
        """A 5-state model in the xz-plane (no pivotting of alpha).

        The 5 states correspond to the Euler angles (z-y-z notation):
            State 1:    {0, pi/4, 0}
            State 2:    {0, pi/8, 0}
            State 3:    {0, 0, 0}
            State 4:    {0, -pi/8, 0}
            State 5:    {0, -pi/4, 0}
        """

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/5_state_xz.py')

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

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


    def test_align_fit(self):
        """Test the use of RDCs and PCSs to find the alignment tensor."""

        # Set the mode to use both RDCs and PCSs.
        ds.mode = 'all'

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/align_fit.py')

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

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
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/align_fit.py')

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000)
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)
        self.assertAlmostEqual(cdp.q_pcs, 0.0)


    def test_align_fit_pcs(self):
        """Test the use of PCSs to find the alignment tensor."""

        # Set the mode to use PCSs.
        ds.mode = 'pcs'

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/align_fit.py')

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

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
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/align_fit.py')

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000)
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_pcs, 0.0)


    def test_align_fit_rdc(self):
        """Test the use of RDCs to find the alignment tensor."""

        # Set the mode to use RDCs.
        ds.mode = 'rdc'

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/align_fit.py')

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

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
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/align_fit.py')

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000)
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)


    def test_lactose_n_state(self):
        """The 4-state model analysis of lactose using RDCs and PCSs."""

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/lactose_n_state.py')
