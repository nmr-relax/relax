###############################################################################
#                                                                             #
# Copyright (C) 2008-2011 Edward d'Auvergne                                   #
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
from numpy import array
from numpy.linalg import norm
from os import listdir, sep
from tempfile import mkdtemp

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.align_tensor import calc_chi_tensor
from generic_fns.mol_res_spin import return_spin, spin_loop
from status import Status; status = Status()


class N_state_model(SystemTestCase):
    """Class for testing various aspects specific to the N-state model."""

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
            print("The loaded vector:    %s" % cdp.mol[0].res[0].spin[0].xh_vect[i])

        # Check.
        for i in range(3):
            self.assertAlmostEqual(norm(vect[ds.order_new[i]] - cdp.mol[0].res[0].spin[0].xh_vect[i]), 0.0)
        for i in range(3):
            self.assertAlmostEqual(norm(C_pos[ds.order_new[i]] - cdp.mol[0].res[0].spin[0].pos[i]), 0.0)


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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'5_state_xz.py')

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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'A_to_chi.py')

        # Test the optimised values.
        for i in range(3):
            self.assertAlmostEqual(cdp.chi[i, i] * 1e32, cdp.chi_ref[i] * 1e32, 2)


    def test_align_fit(self):
        """Test the use of RDCs and PCSs to find the alignment tensor."""

        # Set the mode to use both RDCs and PCSs.
        ds.mode = 'all'
        tag = 'synth'

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

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

            # Check the RDC and PCS values.
            self.assertAlmostEqual(spin.rdc[tag], -8.9193269604999994)
            self.assertAlmostEqual(spin.rdc_bc[tag], -9.1030018792821394)
            self.assertAlmostEqual(spin.pcs[tag], -0.41430390310999998)
            self.assertAlmostEqual(spin.pcs_bc[tag], -0.39723010845807194)

            # MC sims so next round can check if values change.
            if i == 0:
                # Set some errors.
                for spin in spin_loop():
                    spin.rdc_err = {tag: 1.0}
                    spin.pcs_err = {tag: 0.1}

                # MC sims.
                self.interpreter.monte_carlo.setup(number=3)
                self.interpreter.monte_carlo.create_data()
                self.interpreter.monte_carlo.initial_values()
                self.interpreter.minimise('simplex', constraints=False, max_iter=5)
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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'align_fit.py')

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


    def test_lactose_n_state_fixed(self):
        """The 4-state model analysis of lactose using RDCs and PCSs."""

        # The model.
        ds.model = 'fixed'

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'lactose_n_state.py')


    def test_lactose_n_state_population(self):
        """The 4-state model analysis of lactose using RDCs and PCSs."""

        # The model.
        ds.model = 'population'

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'lactose_n_state.py')


    def test_metal_pos_opt(self):
        """Test a certain algorithm for the optimisation of the lanthanide position using RDCs and PCSs (with missing data)."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'metal_pos_opt.py')

        # Check the metal position.
        self.assertAlmostEqual(cdp.paramag_centre[0], -14.845)
        self.assertAlmostEqual(cdp.paramag_centre[1], 0.969)
        self.assertAlmostEqual(cdp.paramag_centre[2], 0.265)

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


    def test_missing_data(self):
        """Test the use of RDCs and PCSs to find the alignment tensor with missing data."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'missing_data_test.py')

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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'monte_carlo_testing.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000)
        self.assertAlmostEqual(cdp.chi2, 1745860.0485368515)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)
        self.assertAlmostEqual(cdp.q_pcs, 0.0)

        # The tensor key.
        key = 'synth'

        # The spin data.
        for spin in spin_loop():
            # Print out.
            print(spin)

            # Check for simulation data.
            if spin.name == 'N':
                self.assert_(hasattr(spin, 'rdc_sim'))
                self.assert_(spin.rdc_sim.has_key(key))
            self.assert_(hasattr(spin, 'pcs_sim'))
            self.assert_(spin.pcs_sim.has_key(key))

            # Check the values of the simulated data.
            for i in range(cdp.sim_number):
                if spin.name == 'N':
                    self.assertAlmostEqual(spin.rdc[key], spin.rdc_sim[key][i], 5)
                self.assertAlmostEqual(spin.pcs[key], spin.pcs_sim[key][i])

        # Test the optimised simluation values.
        for i in range(cdp.sim_number):
            self.assertAlmostEqual(cdp.align_tensors[0].Axx, -0.351261/2000)
            self.assertAlmostEqual(cdp.align_tensors[0].Ayy, 0.556994/2000)
            self.assertAlmostEqual(cdp.align_tensors[0].Axy, -0.506392/2000)
            self.assertAlmostEqual(cdp.align_tensors[0].Axz, 0.560544/2000)
            self.assertAlmostEqual(cdp.align_tensors[0].Ayz, -0.286367/2000)
            self.assertAlmostEqual(cdp.chi2, 1745860.0485368515)

        # Test the tensor error values.
        self.assertAlmostEqual(cdp.align_tensors[0].Axx_err, 0.0)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayy_err, 0.0)
        self.assertAlmostEqual(cdp.align_tensors[0].Axy_err, 0.0)
        self.assertAlmostEqual(cdp.align_tensors[0].Axz_err, 0.0)
        self.assertAlmostEqual(cdp.align_tensors[0].Ayz_err, 0.0)


    def test_paramag_centre_fit(self):
        """Test the use of RDCs and PCSs to find the alignment tensor."""

        # Set the mode to use both RDCs and PCSs.
        ds.mode = 'all'

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'paramag_centre_fit.py')

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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'pcs_back_calc.py')

        # Test the optimised values.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].pcs_bc['A'],  0.061941887563792014)
        self.assertAlmostEqual(cdp.mol[0].res[1].spin[0].pcs_bc['A'], -0.077886567972081502)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].pcs_bc['A'], -0.13928519099517916)


    def test_pcs_fit_true_pos(self):
        """Test the fit of DNA PCSs at the true Ln3+ position."""

        # Set the Ln3+ position.
        ds.para_centre = 'true'

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'dna_pcs_fit.py')

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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'dna_pcs_fit.py')

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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'pcs_to_rdc.py')

        # Test the values.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].rdc_bc['A'], 4.1319413321530014)
        self.assertAlmostEqual(cdp.mol[0].res[1].spin[0].rdc_bc['A'], -9.5802642470087989)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].rdc_bc['A'], -16.244078605100817)


    def test_rdc_tensor(self):
        """Test the calculation of an alignment tensor from RDC data."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'rdc_tensor.py')


    def test_stereochem_analysis(self):
        """The full relative stereochemistry analysis."""

        # Create a temporary directory for all result files.
        ds.tmpdir = mkdtemp()

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'stereochem_analysis.py')

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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'populations.py')

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

        # Check the populations.
        self.assertEqual(len(cdp.probs), 3)
        self.assertAlmostEqual(cdp.probs[0], 0.3)
        self.assertAlmostEqual(cdp.probs[1], 0.6)
        self.assertAlmostEqual(cdp.probs[2], 0.1)

        # Test the optimised values.
        self.assertAlmostEqual(cdp.chi2, 0.0)
        self.assertAlmostEqual(cdp.q_rdc, 0.0)
        self.assertAlmostEqual(cdp.q_pcs, 0.0)


    def test_vector_loading1(self):
        """Test the loading of inter-atomic vectors in the 'population' N-state model."""

        # Order.
        ds.order_struct = [1, 2, 0]
        ds.order_model  = [0, 1, 2]

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'vector_loading.py')

        # Check the vectors.
        self.check_vectors()


    def test_vector_loading2(self):
        """Test the loading of inter-atomic vectors in the 'population' N-state model."""

        # Order.
        ds.order_struct = [0, 1, 2]
        ds.order_model  = [2, 0, 1]

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'vector_loading.py')

        # Check the vectors.
        self.check_vectors()


    def test_vector_loading3(self):
        """Test the loading of inter-atomic vectors in the 'population' N-state model."""

        # Order.
        ds.order_struct = [1, 0, 2]
        ds.order_model  = [2, 0, 1]

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'vector_loading.py')

        # Check the vectors.
        self.check_vectors()
