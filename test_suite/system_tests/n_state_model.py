###############################################################################
#                                                                             #
# Copyright (C) 2008-2014 Edward d'Auvergne                                   #
# Copyright (C) 2013 Troels E. Linnet                                         #
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
from numpy import array, float64
from numpy.linalg import norm
from os import listdir, sep
from tempfile import mkdtemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from pipe_control.align_tensor import calc_chi_tensor
from pipe_control.interatomic import interatomic_loop, return_interatom
from pipe_control.mol_res_spin import return_spin, spin_index_loop, spin_loop
from pipe_control.pipes import get_pipe
from pipe_control.rdc import return_rdc_data
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class N_state_model(SystemTestCase):
    """Class for testing various aspects specific to the N-state model."""

    def __init__(self, methodName='runTest'):
        """Skip some tests if scipy is not installed.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(N_state_model, self).__init__(methodName)

        # Missing module.
        if not dep_check.scipy_module and methodName == 'test_frame_order_align_fit':
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'Scipy', self._skip_type])


    def check_vectors(self):
        """Auxiliary method for checking the correct loading of bond vectors."""

        # The new order.
        ds.order_new = array([ds.order_struct[ds.order_model[ds.order_model[0]]],
                              ds.order_struct[ds.order_model[ds.order_model[1]]],
                              ds.order_struct[ds.order_model[ds.order_model[2]]]])

        # The atom positions.
        C_pos = []
        C_pos.append(array([6.250,   0.948,   1.968]))
        C_pos.append(array([6.438,  -0.139,   1.226]))
        C_pos.append(array([6.108,  -0.169,   0.378]))

        H_pos = []
        H_pos.append(array([7.243,   0.580,   1.676]))
        H_pos.append(array([7.271,  -0.291,   0.525]))
        H_pos.append(array([5.735,   0.003,  -0.639]))

        # The real vectors.
        vect = []
        for i in range(3):
            vect.append(H_pos[i] - C_pos[i])

        # Normalise.
        for i in range(3):
            vect[i] = vect[i] / norm(vect[i])

        # Print out.
        print("Structure order: %s" % ds.order_struct)
        print("Model order:     %s" % ds.order_model)
        print("New order:       %s" % ds.order_new)
        for i in range(3):
            print("\ni = %i" % i)
            print("The real vector:      %s" % vect[i])
            print("The reordered vector: %s" % vect[ds.order_new[i]])
            print("The loaded vector:    %s" % cdp.interatomic[0].vector[i])

        # Check.
        for i in range(3):
            self.assertAlmostEqual(norm(C_pos[ds.order_new[i]] - cdp.mol[0].res[0].spin[0].pos[i]), 0.0)
            self.assertAlmostEqual(norm(H_pos[ds.order_new[i]] - cdp.mol[0].res[0].spin[1].pos[i]), 0.0)
        for i in range(3):
            self.assertAlmostEqual(norm(vect[ds.order_new[i]] - cdp.interatomic[0].vector[i]), 0.0)


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
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'5_state_xz.py')

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


    def test_A_to_chi(self):
        """Test the conversion of the alignment tensor to the chi tensor."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'A_to_chi.py')

        # Test the optimised values.
        for i in range(3):
            self.assertAlmostEqual(cdp.chi[i, i] * 1e32, cdp.chi_ref[i] * 1e32, 2)


    def test_absolute_rdc(self):
        """Test the fitting of signless RDCs."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'absolute_rdcs.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000)
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)

        # The signless RDC data.
        rdcs = [5.59633342475, 13.31357940769, 7.03826972130, 3.39286328073, 2.09118060289, 11.44314950665, 9.06351706695, 2.33713806872, 5.81432510092, 13.10212128419, 2.52845064335, 4.70528375938, 4.07965480340, 6.28030444828, 4.69179757106, 2.34216201798, 3.89567105101, 5.51427513007, 0.72184322202, 3.81502890358, 10.88354253947, 1.66151988717, 4.29930397984, 4.46950447650, 6.99742077188, 2.27879506276, 3.64303288709, 6.83945430255, 3.19585334782]

        # Back calc.
        self.interpreter.rdc.back_calc('abs')

        # Check the spin data.
        i = 0
        for spin in spin_loop():
            # No PCS.
            if not hasattr(spin, 'rdc'):
                continue

            # Check the loaded and back-calculated absolute values.
            self.assertAlmostEqual(spin.rdc['abs'], abs(rdcs[i]))
            self.assertAlmostEqual(spin.rdc_bc['abs'], abs(rdcs[i]))

            # Increment the spin index.
            i += 1


    def test_absolute_rdc_menthol(self):
        """Test the fitting of signless RDCs for menthol."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'absolute_rdcs_menthol.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -2.183595975281820e-04)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, -7.014379141006286e-05)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -1.744959310458587e-05)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 3.646699595026552e-05)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, 2.592895195459969e-04)
        self.assertAlmostEqual(cdp.chi2, 728.32717233107246)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)
        self.assertAlmostEqual(cdp.q_rdc_norm2, 0.7547452273747645)


    def test_absolute_T(self):
        """Test the fitting of signless T values (J+D)."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'absolute_T.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -1.436586299657e-04)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, -5.004443735044e-04)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -5.017832275009e-05)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz,  1.366097786433e-04)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -1.614772175671e-04)
        self.assertAlmostEqual(cdp.chi2, 311.70348701353225)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)
        self.assertAlmostEqual(cdp.q_rdc_norm2, 0.086891848854541404)

        # The signless T data.
        T = [195.2, 205.9, 109.4, 113.8, 127.4, 156.0, 92.1, 173.2, 183.0, 174.3, 152.2, 97.3, 136.0, 129.2, 145.5, 156.0, 121.6, 128.0, 154.5, 94.2]
        T_bc = [
            195.009353539915281,
            205.456622836526037,
            112.285085032859712,
            113.628896345578610,
            127.440986667041187,
            155.505017063790831,
            94.332271833299316,
            172.408496922639102,
            181.972859458051403,
            173.655640981746103,
            153.402585241137388,
            92.115389822570464,
            139.743303992644570,
            131.399101601878243,
            146.219317894376132,
            153.945261372587538,
            119.541444938794172,
            126.620471670822312,
            155.940753902549545,
            90.813638474619523
        ]

        # Back calc.
        self.interpreter.rdc.back_calc('Gel')

        # Check the spin data.
        i = 0
        for interatom in interatomic_loop():
            # No PCS.
            if not hasattr(interatom, 'rdc'):
                continue

            # Check the loaded and back-calculated absolute values.
            self.assertAlmostEqual(interatom.rdc['Gel'], T[i])
            self.assertAlmostEqual(interatom.rdc_bc['Gel'], T_bc[i], 5)

            # Increment the spin index.
            i += 1


    def test_align_fit(self):
        """Test the use of RDCs and PCSs to find the alignment tensor."""

        # Set the mode to use both RDCs and PCSs.
        ds.mode = 'all'
        tag = 'synth'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000)
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)
        self.assertAlmostEqual(cdp.q_pcs, 0.0)

        # The spin data.
        pcs = [1.0261275236, 0.75832284646, 0.65377417467, 0.88410306916, 0.83665620282, 1.887881182, 1.6564530832, 1.8489841033, -1.1143070855, -0.52863087918, -0.67600660991, -0.36996952054, -0.50720205688, -0.39889489474, -0.41237130008, -0.71313422816, -0.58642013802, -1.2160818959, -1.3990341569, -1.4084215541, -1.2007391713, -2.1392542193, -2.0165726596, -1.7623442985, -1.6437792517, -1.2415832517, -1.3008765368, -1.5872391105, -1.8060331465, -1.9063640494, -1.9817787999, -0.85264936663, -0.98332177588, -0.13370651687, -0.41762890604, -0.038212181921, -0.37986098085, 0.63582157322, 0.48346482178, 1.7566240094, 1.5694652222, 1.9914499872, 2.5316890107, 1.4559940851, 1.8661428328, 0.65003087965, 0.91690449156, 3.2096229388, 3.5547526651, 3.0579308183, 3.5933428117, 2.9062016872, 3.3750576279, 2.1848555929, 2.4769802024, 1.6466129291, 1.7719619979, 1.1373876736, 1.2182451528]
        i = 0
        for spin in spin_loop():
            # No PCS.
            if not hasattr(spin, 'pcs'):
                continue

            # Check the value.
            self.assertAlmostEqual(spin.pcs[tag], pcs[i])

            # Check the back-calculated value.
            self.assertAlmostEqual(spin.pcs_bc[tag], pcs[i])

            # Check the simulation values.
            for sim_index in range(cdp.sim_number):
                self.assert_(abs(spin.pcs_sim[tag][sim_index] - spin.pcs[tag]) < 6.0*spin.pcs_err[tag])

            # Increment the spin index.
            i += 1

        # Back calc.
        self.interpreter.pcs.back_calc(tag)

        # Check the spin data.
        i = 0
        for spin in spin_loop():
            # No PCS.
            if not hasattr(spin, 'pcs'):
                continue

            # Check the back-calculated value.
            self.assertAlmostEqual(spin.pcs_bc[tag], pcs[i])

            # Increment the spin index.
            i += 1


    def test_align_fit_rand(self):
        """Test the use of randomised RDCs and PCSs to find the alignment tensor."""

        # Set the mode to use both RDCs and PCSs.
        ds.mode = 'all'

        # Select the randomised data.
        ds.rand = True

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

        # The tag.
        tag = 'synth'

        # Loop a few times.
        for i in range(4):
            # Test the optimised values (these values are from relax, so are not 100% reliable as a check).
            self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.000189412096996)
            self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.000271130087923)
            self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.000264898401302)
            self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.000284115871058)
            self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.000152207413184)
            self.assertAlmostEqual(cdp.chi2, 783.530808266)
            self.assertAlmostEqual(cdp.q_pcs, 0.063345784112045375)
            self.assertAlmostEqual(cdp.q_rdc, 0.084926009099013003)

            # Get a spin to check.
            spin = return_spin(':114@N')
            interatom = return_interatom(':114@N', ':114@H')

            # Check the RDC and PCS values.
            self.assertAlmostEqual(interatom.rdc[tag], -8.9193269604999994)
            self.assertAlmostEqual(interatom.rdc_bc[tag], -9.1030018792821394)
            self.assertAlmostEqual(spin.pcs[tag], -0.41430390310999998)
            self.assertAlmostEqual(spin.pcs_bc[tag], -0.39723010845807194)

            # MC sims so next round can check if values change.
            if i == 0:
                # Set some errors.
                for interatom in interatomic_loop():
                    interatom.rdc_err = {tag: 1.0}
                for spin in spin_loop():
                    spin.pcs_err = {tag: 0.1}

                # MC sims.
                self.interpreter.monte_carlo.setup(number=3)
                self.interpreter.monte_carlo.create_data()
                self.interpreter.monte_carlo.initial_values()
                self.interpreter.minimise.execute('simplex', constraints=False, max_iter=5)
                self.interpreter.monte_carlo.error_analysis()

            # Back-calc so next round can check if values change.
            if i == 2:
                self.interpreter.rdc.back_calc(tag)
                self.interpreter.pcs.back_calc(tag)

            # Calc Q factors so next round can check if values change.
            if i == 1:
                self.interpreter.rdc.calc_q_factors()
                self.interpreter.pcs.calc_q_factors()


    def test_align_fit_pcs(self):
        """Test the use of PCSs to find the alignment tensor."""

        # Set the mode to use PCSs.
        ds.mode = 'pcs'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

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
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

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
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

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
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

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
        self.assertAlmostEqual(cdp.q_rdc_norm2, 0.14049691097282743)       # Pales (Q RDC_RMS): 0.141


    def test_data_copying(self):
        """The copying of RDC and PCS data from one pipe to another."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'data_copying.py')

        # Get the data pipes.
        orig = get_pipe('orig')
        new = get_pipe('new')

        # Check the data.
        self.assertEqual(orig.rdc_ids, new.rdc_ids)
        self.assertEqual(orig.pcs_ids, new.pcs_ids)
        self.assertEqual(orig.align_ids, new.align_ids)

        # Check the spin data.
        for mol_index, res_index, spin_index in spin_index_loop():
            # Alias the spin containers.
            spin_orig = orig.mol[mol_index].res[res_index].spin[spin_index]
            spin_new = new.mol[mol_index].res[res_index].spin[spin_index]

            # Loop over the alignments.
            for id in orig.align_ids:
                # RDC checks.
                if hasattr(spin_orig, 'rdc'):
                    # Check the keys.
                    self.assertEqual(spin_orig.rdc.keys(), spin_new.rdc.keys())

                    # Check the values.
                    if id in spin_orig.rdc:
                        self.assertEqual(spin_orig.rdc[id], spin_new.rdc[id])

                # PCS checks.
                if hasattr(spin_orig, 'pcs'):
                    # Check the keys.
                    self.assertEqual(spin_orig.pcs.keys(), spin_new.pcs.keys())

                    # Check the values.
                    if id in spin_orig.pcs:
                        self.assertEqual(spin_orig.pcs[id], spin_new.pcs[id])


    def test_frame_order_align_fit(self):
        """Test the use of alignment tensors, RDCs and PCSs from a frame order data pipe for the N-state model."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'frame_order_align_fit.py')

        # The actual tensors.
        A_5D = []
        A_5D.append([1.42219822168827662867e-04, -1.44543001566521341940e-04, -7.07796211648713973798e-04, -6.01619494082773244303e-04, 2.02008007072950861996e-04])
        A_5D.append([3.56720663040924505435e-04, -2.68385787902088840916e-04, -1.69361406642305853832e-04, 1.71873715515064501074e-04, -3.05790155096090983822e-04])
        A_5D.append([2.32088908680377300801e-07, 2.08076808579168379617e-06, -2.21735465435989729223e-06, -3.74311563209448033818e-06, -2.40784858070560310370e-06])
        A_5D.append([-2.62495279588228071048e-04, 7.35617367964106275147e-04, 6.39754192258981332648e-05, 6.27880171180572523460e-05, 2.01197582457700226708e-04])

        # Check the tensors.
        for i in range(1):
            self.assertAlmostEqual(cdp.align_tensors[i].Axx, A_5D[i][0])
            self.assertAlmostEqual(cdp.align_tensors[i].Ayy, A_5D[i][1])
            self.assertAlmostEqual(cdp.align_tensors[i].Axy, A_5D[i][2])
            self.assertAlmostEqual(cdp.align_tensors[i].Axz, A_5D[i][3])
            self.assertAlmostEqual(cdp.align_tensors[i].Ayz, A_5D[i][4])

        # Test the optimised values.
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)
        self.assertAlmostEqual(cdp.q_pcs, 0.0)


    def test_lactose_n_state_fixed(self):
        """The 4-state model analysis of lactose using RDCs and PCSs."""

        # The model.
        ds.model = 'fixed'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'lactose_n_state.py')


    def test_lactose_n_state_population(self):
        """The 4-state model analysis of lactose using RDCs and PCSs."""

        # The model.
        ds.model = 'population'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'lactose_n_state.py')


    def test_mc_sim_failure(self):
        """Test the setup of the Monte Carlo simulations
        
        This failed when this test was added, and is probably due to missing data.
        """

        # Reset and load the state.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'saved_states'+sep+'n_state_model_mc_fail.bz2'
        self.interpreter.reset()
        self.interpreter.state.load(path)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=3)
        self.interpreter.monte_carlo.create_data()
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise.execute('newton', constraints=False)
        self.interpreter.monte_carlo.error_analysis()

        # Activate the optimisation of the paramagnetic centre position and try again.
        self.interpreter.paramag.centre(fix=False)
        self.interpreter.monte_carlo.setup(number=3)
        self.interpreter.monte_carlo.create_data()
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise.execute('bfgs', constraints=False, max_iter=100)
        self.interpreter.monte_carlo.error_analysis()


    def test_metal_pos_opt(self):
        """Test a certain algorithm for the optimisation of the lanthanide position using RDCs and PCSs (with missing data)."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'metal_pos_opt.py')

        # Check the metal position.
        self.assertAlmostEqual(cdp.paramagnetic_centre[0], -14.845)
        self.assertAlmostEqual(cdp.paramagnetic_centre[1], 0.969)
        self.assertAlmostEqual(cdp.paramagnetic_centre[2], 0.265)

        # The actual tensors.
        A_5D = []
        A_5D.append([1.42219822168827662867e-04, -1.44543001566521341940e-04, -7.07796211648713973798e-04, -6.01619494082773244303e-04, 2.02008007072950861996e-04])
        A_5D.append([3.56720663040924505435e-04, -2.68385787902088840916e-04, -1.69361406642305853832e-04, 1.71873715515064501074e-04, -3.05790155096090983822e-04])
        A_5D.append([2.32088908680377300801e-07, 2.08076808579168379617e-06, -2.21735465435989729223e-06, -3.74311563209448033818e-06, -2.40784858070560310370e-06])
        A_5D.append([-2.62495279588228071048e-04, 7.35617367964106275147e-04, 6.39754192258981332648e-05, 6.27880171180572523460e-05, 2.01197582457700226708e-04])

        # Check the tensors.
        for i in range(len(A_5D)):
            self.assertAlmostEqual(cdp.align_tensors[i].Axx, A_5D[i][0])
            self.assertAlmostEqual(cdp.align_tensors[i].Ayy, A_5D[i][1])
            self.assertAlmostEqual(cdp.align_tensors[i].Axy, A_5D[i][2])
            self.assertAlmostEqual(cdp.align_tensors[i].Axz, A_5D[i][3])
            self.assertAlmostEqual(cdp.align_tensors[i].Ayz, A_5D[i][4])

        # Test the optimised values.
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)
        self.assertAlmostEqual(cdp.q_pcs, 0.0)

        # The spin data.
        pcs = {
                'Dy': [ 0.257602207272000,  0.068336164014900,  0.110603133551000,  0.283488541078000,  0.339904760907000,  0.987042929223000,  0.442512226783000,  0.369383947069000,  0.576421001305000,  0.414840770458000,  0.332707187464000, -0.029503579631700,  0.134647155776000,  0.112481223655000,  0.355198596515000, -0.046913037723100, -0.118710220626000,  0.029273074820300,  0.302949891871000,  1.312854817740000,  0.040875625448800,  0.608281919748000,  0.023360076276000,  0.811293913028000,  0.258701382871000,  0.056025797668300,  0.609547727298000,  0.906885191563000],
                'Tb': [0.644225239812000, 0.677797993460000, 0.492912191403000, 0.524119985177000, 0.600493382214000, 0.501470795483000, 0.516761193931000, 0.702967176951000, 0.914836321239000, 1.318114995620000, 1.350055099220000, 0.893477362442000, 0.999911636071000, 1.065232203160000, 0.996395971540000, 0.720982749003000, 1.374318729640000, 2.106902457600000],
                'Tm': [ 0.000125066528687, -0.000564062193363, -0.000607973317902,  0.000090266635200,  0.000174865797403,  0.002488010156480,  0.000830246873289,  0.000762523870219, -0.000096933008248,  0.000742665143642, -0.000215152849719],
                'Er': [-0.481445160767000, -0.361046693640000, -0.370098680342000, -0.413514467402000, -0.410802287329000, -1.081011578870000, -0.963176128222000, -0.745366702244000, -0.674570724880000, -0.751320872646000, -0.684906087274000, -0.461253969271000, -0.443680922437000, -0.344056233315000, -0.328118573270000, -0.395048353548000, -0.356220572284000, -0.324533952261000, -0.411777498713000, -0.511811581196000, -1.018565433020000, -0.959481602761000, -0.734022165690000, -0.660034918889000, -0.709085634512000, -0.878775632044000, -0.553464480425000, -0.765371835675000, -1.548006987460000]
        }
        spin_deselect_blacklist = ['pcs_bc', 'pcs_sim']

        # Loop over the align IDs.
        for tag in ['Dy', 'Tb', 'Tm', 'Er']:
            i = 0
            for spin, spin_id in spin_loop(return_id=True):
                # Deselected spin.
                if not spin.select:
                    print("Checking the deselected spin '%s'" % spin_id)

                    # Check that the container is clean.
                    for name in spin_deselect_blacklist:
                        print("    Checking the blacklisted object %s." % name)
                        self.assert_(not hasattr(spin, name))

                    # Skip the rest of the checks.
                    continue

                # No PCS.
                if not hasattr(spin, 'pcs'):
                    print("No PCS for spin '%s'." % spin_id)
                    continue
                if not tag in spin.pcs:
                    print("No PCS for the '%s' alignment ID for spin '%s'." % (tag, spin_id))
                    continue
                print("Checking '%s' PCS data for spin '%s'" % (tag, spin_id))

                # Check the value.
                self.assertAlmostEqual(spin.pcs[tag], pcs[tag][i])

                # Check the back-calculated value.
                self.assertAlmostEqual(spin.pcs_bc[tag], pcs[tag][i])

                # Check the simulation values.
                for sim_index in range(cdp.sim_number):
                    self.assert_(abs(spin.pcs_sim[tag][sim_index] - spin.pcs[tag]) < 6.0*spin.pcs_err[tag])

                # Increment the spin index.
                i += 1

        # The interatomic data.
        rdc = {
            'Dy': [-30.671893754700001, -31.307246147099999, -29.358121961700000,  -7.235977742280000, -45.562589405399997, -42.816624411200003, -41.019354747700000, -25.361318450599999, -44.1129977796],
            'Tm': [-0.057386340972700, -0.045650398398700, -0.074873514450400,  0.099056143214600,  0.021275817005300,  0.037132036464200,  0.047340390362400,  0.128745838536000,  0.010906407989400],
            'Er': [ 22.944150028900001,  23.363231565100001,  25.948323446000000,   6.955380304960000,   1.784067087050000,   7.228324193240000,   8.271072502000001,  -7.403618580470000]
        }
        interatom_deselect_blacklist = ['rdc_bc', 'rdc_sim']

        # Loop over the align IDs.
        for tag in ['Dy', 'Tm', 'Er']:
            i = 0
            for interatom in interatomic_loop():
                # Deselected interatomic container.
                if not interatom.select:
                    print("Checking the deselected interatom '%s-%s'" % (interatom.spin_id1, interatom.spin_id2))

                    # Check that the container is clean.
                    for name in interatom_deselect_blacklist:
                        print("    Checking the blacklisted object %s." % name)
                        self.assert_(not hasattr(interatom, name))

                    # Skip the rest of the checks.
                    continue

                # No RDC.
                if not hasattr(interatom, 'rdc'):
                    print("No RDC for interatom '%s-%s'." % (interatom.spin_id1, interatom.spin_id2))
                    continue
                if not tag in interatom.rdc:
                    print("No RDC for the '%s' alignment ID for interatom '%s-%s'." % (tag, interatom.spin_id1, interatom.spin_id2))
                    continue
                print("Checking '%s' RDC data for interatom '%s-%s'" % (tag, interatom.spin_id1, interatom.spin_id2))

                # Check the value.
                self.assertAlmostEqual(interatom.rdc[tag], rdc[tag][i])

                # Check the back-calculated value.
                self.assertAlmostEqual(interatom.rdc_bc[tag], rdc[tag][i])

                # Check the simulation values.
                for sim_index in range(cdp.sim_number):
                    self.assert_(abs(interatom.rdc_sim[tag][sim_index] - interatom.rdc[tag]) < 6.0*interatom.rdc_err[tag])

                # Increment the interatom index.
                i += 1


    def test_missing_data(self):
        """Test the use of RDCs and PCSs to find the alignment tensor with missing data."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'missing_data_test.py')

        # The actual tensors.
        A_5D = []
        A_5D.append([1.42219822168827662867e-04, -1.44543001566521341940e-04, -7.07796211648713973798e-04, -6.01619494082773244303e-04, 2.02008007072950861996e-04])
        A_5D.append([3.56720663040924505435e-04, -2.68385787902088840916e-04, -1.69361406642305853832e-04, 1.71873715515064501074e-04, -3.05790155096090983822e-04])
        A_5D.append([2.32088908680377300801e-07, 2.08076808579168379617e-06, -2.21735465435989729223e-06, -3.74311563209448033818e-06, -2.40784858070560310370e-06])
        A_5D.append([-2.62495279588228071048e-04, 7.35617367964106275147e-04, 6.39754192258981332648e-05, 6.27880171180572523460e-05, 2.01197582457700226708e-04])

        # Check the tensors.
        for i in range(len(A_5D)):
            self.assertAlmostEqual(cdp.align_tensors[i].Axx, A_5D[i][0])
            self.assertAlmostEqual(cdp.align_tensors[i].Ayy, A_5D[i][1])
            self.assertAlmostEqual(cdp.align_tensors[i].Axy, A_5D[i][2])
            self.assertAlmostEqual(cdp.align_tensors[i].Axz, A_5D[i][3])
            self.assertAlmostEqual(cdp.align_tensors[i].Ayz, A_5D[i][4])

        # Test the optimised values.
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)
        self.assertAlmostEqual(cdp.q_pcs, 0.0)


    def test_monte_carlo_sims(self):
        """Test the Monte Carlo simulation data of fitting RDCs and PCSs."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'monte_carlo_testing.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000)
        self.assertAlmostEqual(cdp.chi2 / 1e6, 1745860.0485368515 / 1e6, 6)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)
        self.assertAlmostEqual(cdp.q_pcs, 0.0)

        # The tensor key.
        key = 'synth'

        # The spin data.
        for spin in spin_loop():
            # Print out.
            print(spin)

            # Check for simulation data.
            self.assert_(hasattr(spin, 'pcs_sim'))
            self.assert_(key in spin.pcs_sim)

            # Check the values of the simulated data.
            for i in range(cdp.sim_number):
                self.assertAlmostEqual(spin.pcs[key], spin.pcs_sim[key][i])

        # The interatomic data.
        for interatom in interatomic_loop():
            # Print out.
            print(interatom)

            # Check for simulation data.
            self.assert_(hasattr(interatom, 'rdc_sim'))
            self.assert_(key in interatom.rdc_sim)

            # Check the values of the simulated data.
            for i in range(cdp.sim_number):
                self.assertAlmostEqual(interatom.rdc[key], interatom.rdc_sim[key][i], 5)

        # Test the optimised simluation values.
        for i in range(cdp.sim_number):
            self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000)
            self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000)
            self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000)
            self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000)
            self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000)
            self.assertAlmostEqual(cdp.chi2 / 1e6, 1745860.0485368515 / 1e6, 5)

        # Test the tensor error values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx_err, 0.0)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy_err, 0.0)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy_err, 0.0)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz_err, 0.0)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz_err, 0.0)


    def test_paramag_align_fit(self):
        """Test the use of RDCs and PCSs to find the alignment tensor."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'paramag_align_fit.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[1].Axx,  0.001414718232784)
        self.assertAlmostEqual(cdp.align_tensors[1].Ayy,  0.001530457843766)
        self.assertAlmostEqual(cdp.align_tensors[1].Axy,  0.001689957281873)
        self.assertAlmostEqual(cdp.align_tensors[1].Axz,  0.000838692329704)
        self.assertAlmostEqual(cdp.align_tensors[1].Ayz, -0.000984302159683)
        self.assertAlmostEqual(cdp.q_factors_rdc['Er'], 0.0, 7)
        self.assertAlmostEqual(cdp.q_factors_rdc_norm2['Er'], 0.0, 7)
        self.assertAlmostEqual(cdp.q_factors_pcs['Er'], 0.0, 7)
        self.assertAlmostEqual(cdp.q_rdc, 0.0, 7)
        self.assertAlmostEqual(cdp.q_pcs, 0.0, 7)


    def test_paramag_centre_fit(self):
        """Test the use of RDCs and PCSs to find the alignment tensor."""

        # Set the mode to use both RDCs and PCSs.
        ds.mode = 'all'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'paramag_centre_fit.py')

        # Check the paramagnetic centre position.
        self.assertAlmostEqual(cdp.paramagnetic_centre[0], 32.555, 1)
        self.assertAlmostEqual(cdp.paramagnetic_centre[1], -19.130, 1)
        self.assertAlmostEqual(cdp.paramagnetic_centre[2], 27.775, 1)

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000, 5)
        self.assertAlmostEqual(cdp.chi2, 0.0, 2)
        self.assertAlmostEqual(cdp.q_rdc, 0.0, 2)
        self.assertAlmostEqual(cdp.q_pcs, 0.0, 2)


    def test_pcs_back_calc(self):
        """Test the back-calculation of PCSs for ubiquitin."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'pcs_back_calc.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].pcs_bc['A'],  0.061941887563792014)
        self.assertAlmostEqual(cdp.mol[0].res[1].spin[0].pcs_bc['A'], -0.077886567972081502)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].pcs_bc['A'], -0.13928519099517916)


    def test_pcs_fit_true_pos(self):
        """Test the fit of DNA PCSs at the true Ln3+ position."""

        # Set the Ln3+ position.
        ds.para_centre = 'true'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'dna_pcs_fit.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx,  1.42219822168827662867e-04)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, -1.44543001566521341940e-04)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -7.07796211648713973798e-04)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, -6.01619494082773244303e-04)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz,  2.02008007072950861996e-04)
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_pcs, 0.0)


    def test_pcs_fit_zero_pos(self):
        """Test the fit of DNA PCSs at a Ln3+ position of [0, 0, 0]."""

        # Set the Ln3+ position.
        ds.para_centre = 'zero'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'dna_pcs_fit.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx,  9.739588118243e-07)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, -1.077401299806e-05)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -2.321033328910e-06)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz,  5.105903556692e-07)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz,  1.676638764825e-05)
        self.assertAlmostEqual(cdp.chi2, 2125.9562247877066)
        self.assertAlmostEqual(cdp.q_pcs, 0.76065986767333704)

        # The chi tensor.
        chi_diag = calc_chi_tensor(cdp.align_tensors[0].A_diag, 799.75376122 * 1e6, 298)
        chi_diag = chi_diag * 1e33
        self.assertAlmostEqual((chi_diag[2, 2] - (chi_diag[0, 0] + chi_diag[1, 1])/2.0), -6.726159808496, 5)
        self.assertAlmostEqual((chi_diag[0, 0] - chi_diag[1, 1]), -3.960936794864, 6)


    def test_pcs_to_rdc(self):
        """Test the back-calculation of RDCs from a PCS derived tensor."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'pcs_to_rdc.py')

        # Test the values.
        self.assertAlmostEqual(cdp.interatomic[0].rdc_bc['A'], 4.1319413321530014)
        self.assertAlmostEqual(cdp.interatomic[1].rdc_bc['A'], -9.5802642470087989)
        self.assertAlmostEqual(cdp.interatomic[2].rdc_bc['A'], -16.244078605100817)


    def test_pyrotartaric_anhydride_absT(self):
        """Pyrotarctic anhydride alignment tensor optimisation using long range (1J, 2J & 3J) absolute T (J+D) data."""

        # The setup.
        ds.abs_data = 'T'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'pyrotartaric_anhydride.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.0001756305, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.000278497, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.000253196, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.000280272, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.0001431835, 5)
        self.assertAlmostEqual(cdp.chi2, 0.0, 2)
        self.assertAlmostEqual(cdp.q_rdc, 0.0, 2)


    def test_pyrotartaric_anhydride_mix(self):
        """Pyrotarctic anhydride alignment tensor optimisation using short range RDC and long range (1J, 2J & 3J) absolute T (J+D) data."""

        # The setup.
        ds.abs_data = 'mix'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'pyrotartaric_anhydride.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.0001756305, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.000278497, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.000253196, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.000280272, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.0001431835, 5)
        self.assertAlmostEqual(cdp.chi2, 0.0, 2)
        self.assertAlmostEqual(cdp.q_rdc, 0.0, 2)


    def test_pyrotartaric_anhydride_rdcs(self):
        """Pyrotarctic anhydride alignment tensor optimisation using long range (1J, 2J & 3J) RDC data."""

        # The setup.
        ds.abs_data = 'D'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'pyrotartaric_anhydride.py')

        # Get the RDC data.
        rdcs, rdc_err, rdc_weight, rdc_vector, rdc_dj, absolute_rdc, T_flags, j_couplings, rdc_pseudo_flags = return_rdc_data()

        # The data as it should be.
        ids = ['@9 - @Q9', '@4 - @6', '@5 - @7', '@5 - @8', '@1 - @6', '@3 - @6', '@5 - @6', '@9 - @6', '@1 - @7', '@3 - @7', '@4 - @7', '@9 - @7', '@1 - @8', '@3 - @8', '@4 - @8', '@9 - @8', '@3 - @Q9', '@4 - @Q9', '@5 - @Q9']
        real_rdcs = array([7.051710295953332, 14.64956993990, -9.80224941614,  4.49085022708,  1.16041049951,  0.57071216172,  3.68667449742, -2.26063357144, -4.77232431456, -0.17007443173,  2.37501105989,  1.64523216045, -0.94447557779,  0.06213688971,  1.48958862680,  0.21349779284, -1.2400897128766667, -1.8997427023766667, -0.0129325208733333], float64)

        # Check the RDC data.
        for i in range(len(ids)):
            print("Spin pair '%s'." % ids[i])
            self.assertEqual(real_rdcs[i], rdcs[0, i])

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.0001756305, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.000278497, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.000253196, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.000280272, 5)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.0001431835, 5)
        self.assertAlmostEqual(cdp.chi2, 0.0, 2)
        self.assertAlmostEqual(cdp.q_rdc, 0.0, 2)


    def test_rdc_tensor(self):
        """Test the calculation of an alignment tensor from RDC data."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'rdc_tensor.py')


    def test_stereochem_analysis(self):
        """The full relative stereochemistry analysis."""

        # Create a temporary directory for all result files.
        ds.tmpdir = mkdtemp()

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'stereochem_analysis.py')

        # Check the base directory files.
        files = listdir(ds.tmpdir)
        for file in files:
            print("Checking file %s." % file)
            self.assert_(file in ['NOE_viol_S_sorted', 'ensembles_superimposed', 'RDC_PAN_dist.agr', 'Q_factors_S', 'NOE_viol_curve.agr', 'NOE_viol_dist.agr', 'RDC_PAN_curve.agr', 'NOE_viol_S', 'Q_factors_R_sorted', 'NOE_results', 'Q_factors_R', 'NOE_viol_R_sorted', 'logs', 'NOE_viol_R', 'Q_factors_S_sorted', 'RDC_PAN_results', 'correlation_plot.agr', 'correlation_plot_scaled.agr'])

        # Check the sub-directory files.
        subdirs = ['ensembles_superimposed', 'logs', 'NOE_results', 'RDC_PAN_results']
        files = [['S0.pdb', 'S2.pdb', 'R0.pdb', 'R1.pdb', 'S1.pdb', 'R2.pdb'],
                 ['RDC_PAN_analysis.log', 'NOE_viol.log'],
                 ['S_results_0.bz2', 'S_results_1.bz2', 'R_results_2.bz2', 'R_results_0.bz2', 'S_results_2.bz2', 'R_results_1.bz2'],
                 ['S_results_0.bz2', 'S_results_1.bz2', 'R_results_2.bz2', 'R_results_0.bz2', 'S_results_2.bz2', 'R_results_1.bz2']]
        for i in range(len(subdirs)):
            for file in listdir(ds.tmpdir + sep + subdirs[i]):
                print("Checking file %s." % file)
                self.assert_(file in files[i])


    def test_populations(self):
        """Test the 'population' N-state model optimisation using RDCs and PCSs (with missing data)."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'populations.py')

        # The actual tensors.
        A_5D = []
        A_5D.append([1.42219822168827662867e-04, -1.44543001566521341940e-04, -7.07796211648713973798e-04, -6.01619494082773244303e-04, 2.02008007072950861996e-04])
        A_5D.append([3.56720663040924505435e-04, -2.68385787902088840916e-04, -1.69361406642305853832e-04, 1.71873715515064501074e-04, -3.05790155096090983822e-04])
        A_5D.append([2.32088908680377300801e-07, 2.08076808579168379617e-06, -2.21735465435989729223e-06, -3.74311563209448033818e-06, -2.40784858070560310370e-06])
        A_5D.append([-2.62495279588228071048e-04, 7.35617367964106275147e-04, 6.39754192258981332648e-05, 6.27880171180572523460e-05, 2.01197582457700226708e-04])

        # Check the tensors.
        for i in range(len(A_5D)):
            self.assertAlmostEqual(cdp.align_tensors[i].Axx, A_5D[i][0], 5)
            self.assertAlmostEqual(cdp.align_tensors[i].Ayy, A_5D[i][1], 5)
            self.assertAlmostEqual(cdp.align_tensors[i].Axy, A_5D[i][2], 5)
            self.assertAlmostEqual(cdp.align_tensors[i].Axz, A_5D[i][3], 5)
            self.assertAlmostEqual(cdp.align_tensors[i].Ayz, A_5D[i][4], 5)

        # Check the populations.
        self.assertEqual(len(cdp.probs), 3)
        self.assertAlmostEqual(cdp.probs[0], 0.3, 3)
        self.assertAlmostEqual(cdp.probs[1], 0.6, 3)
        self.assertAlmostEqual(cdp.probs[2], 0.1, 3)

        # Test the optimised values.
        self.assertAlmostEqual(cdp.chi2, 0.0, 2)
        self.assertAlmostEqual(cdp.q_rdc, 0.0, 2)
        self.assertAlmostEqual(cdp.q_pcs, 0.0, 1)


    def test_vector_loading1(self):
        """Test the loading of inter-atomic vectors in the 'population' N-state model."""

        # Order.
        ds.order_struct = [1, 2, 0]
        ds.order_model  = [0, 1, 2]

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'vector_loading.py')

        # Check the vectors.
        self.check_vectors()


    def test_vector_loading2(self):
        """Test the loading of inter-atomic vectors in the 'population' N-state model."""

        # Order.
        ds.order_struct = [0, 1, 2]
        ds.order_model  = [2, 0, 1]

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'vector_loading.py')

        # Check the vectors.
        self.check_vectors()


    def test_vector_loading3(self):
        """Test the loading of inter-atomic vectors in the 'population' N-state model."""

        # Order.
        ds.order_struct = [1, 0, 2]
        ds.order_model  = [2, 0, 1]

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'vector_loading.py')

        # Check the vectors.
        self.check_vectors()
