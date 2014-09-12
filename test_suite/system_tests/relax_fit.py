###############################################################################
#                                                                             #
# Copyright (C) 2006-2014 Edward d'Auvergne                                   #
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
from re import search
from tempfile import mkdtemp

# relax module imports.
from auto_analyses import relax_fit
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from pipe_control.mol_res_spin import count_spins, return_spin, spin_index_loop, spin_loop
from pipe_control import pipes
from lib.errors import RelaxError
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Relax_fit(SystemTestCase):
    """Class for testing various aspects specific to relaxation curve-fitting."""

    def __init__(self, methodName='runTest'):
        """Skip the tests if the C modules are non-functional.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(Relax_fit, self).__init__(methodName)

        # Missing module.
        if not dep_check.C_module_exp_fn:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'Relax curve-fitting C module', self._skip_type])


    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()


    def check_curve_fitting(self):
        """Check the results of the curve-fitting."""

        # Data.
        relax_times = [0.0176, 0.0176, 0.0352, 0.0704, 0.0704, 0.1056, 0.1584, 0.1584, 0.1936, 0.1936]
        chi2 = [None, None, None, 2.916952651567855, 5.4916923952919632, 16.21182245065274, 4.3591263759462926, 9.8925377583244316, None, None, None, 6.0238341559877782]
        rx = [None, None, None, 8.0814894819820662, 8.6478971039559642, 9.5710638183013845, 10.716551838066295, 11.143793935455122, None, None, None, 12.82875370075309]
        i0 = [None, None, None, 1996050.9679875025, 2068490.9458927638, 1611556.5194095275, 1362887.2331948928, 1877670.5623875158, None, None, None, 897044.17382064369]

        # Some checks.
        self.assertEqual(cdp.curve_type, 'exp')
        self.assertEqual(cdp.int_method, ds.int_type)
        self.assertEqual(len(cdp.relax_times), 10)
        cdp_relax_times = sorted(cdp.relax_times.values())
        for i in range(10):
            self.assertEqual(cdp_relax_times[i], relax_times[i])

        # Check the errors.
        for key in cdp.sigma_I:
            self.assertAlmostEqual(cdp.sigma_I[key], 10578.039482421433, 6)
            self.assertAlmostEqual(cdp.var_I[key], 111894919.29166669)

        # Spin data check.
        i = 0
        for spin in spin_loop():
            # No data present.
            if chi2[i] == None:
                self.assert_(not hasattr(spin, 'chi2'))

            # Data present.
            else:
                self.assertAlmostEqual(spin.chi2, chi2[i])
                self.assertAlmostEqual(spin.rx, rx[i])
                self.assertAlmostEqual(spin.i0/1e6, i0[i]/1e6)

            # Increment the spin index.
            i = i + 1
            if i >= 12:
                break


    def check_curve_fitting_manual(self):
        """Check the results of the curve-fitting."""

        # Data.
        relax_times = [0.0176, 0.0176, 0.0352, 0.0704, 0.0704, 0.1056, 0.1584, 0.1584, 0.1936, 0.1936]
        chi2 = [2.916952651567855, 5.4916923952919632, 16.21182245065274, 4.3591263759462926, 9.8925377583244316, 6.0238341559877782]
        rx = [8.0814894819820662, 8.6478971039559642, 9.5710638183013845, 10.716551838066295, 11.143793935455122, 12.82875370075309]
        i0 = [1996050.9679875025, 2068490.9458927638, 1611556.5194095275, 1362887.2331948928, 1877670.5623875158, 897044.17382064369]

        # Some checks.
        self.assertEqual(cdp.curve_type, 'exp')
        self.assertEqual(cdp.int_method, ds.int_type)
        self.assertEqual(len(cdp.relax_times), 10)
        cdp_relax_times = sorted(cdp.relax_times.values())
        for i in range(10):
            self.assertEqual(cdp_relax_times[i], relax_times[i])

        # Check the errors.
        for key in cdp.sigma_I:
            self.assertAlmostEqual(cdp.sigma_I[key], 10578.039482421433, 6)
            self.assertAlmostEqual(cdp.var_I[key], 111894919.29166669)

        # Spin data check.
        i = 0
        for spin in spin_loop(skip_desel=True):
            self.assertAlmostEqual(spin.chi2, chi2[i])
            self.assertAlmostEqual(spin.rx, rx[i])
            self.assertAlmostEqual(spin.i0/1e6, i0[i]/1e6)

            # Increment the spin index.
            i = i + 1


    def test_bug_12670_12679(self):
        """Test the relaxation curve fitting, replicating U{bug #12670<https://gna.org/bugs/?12670>} and U{bug #12679<https://gna.org/bugs/?12679>}."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'1UBQ_relax_fit.py')

        # Open the intensities.agr file.
        file = open(ds.tmpdir + sep + 'intensities.agr')
        lines = file.readlines()
        file.close()

        # Loop over all lines.
        for i in range(len(lines)):
            # Find the "@target G0.S0" line.
            if search('@target', lines[i]):
                index = i + 2

            # Split up the lines.
            lines[i] = lines[i].split()

        # Check some of the Grace data.
        self.assertEqual(len(lines[index]), 3)
        self.assertEqual(lines[index][0], '0.004')
        self.assertEqual(lines[index][1], '487178.000000000000000')
        self.assertEqual(lines[index][2], '20570.000000000000000')


    def test_bug_18789(self):
        """Test for zero errors in Grace plots, replicating U{bug #18789<https://gna.org/bugs/?18789>}."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'curve_fitting'+sep+'bug_18789_no_grace_errors.py')

        # Open the Grace file.
        file = open(ds.tmpdir + sep + 'rx.agr')
        lines = file.readlines()
        file.close()

        # Loop over all lines.
        for i in range(len(lines)):
            # Find the "@target G0.S0" line.
            if search('@target', lines[i]):
                index = i + 2

            # Split up the lines.
            lines[i] = lines[i].split()

        # Check for zero errors.
        self.assertEqual(len(lines[index]), 3)
        self.assertNotEqual(float(lines[index][2]), 0.0)
        self.assertNotEqual(float(lines[index+1][2]), 0.0)


    def test_bug_19887_curvefit_fail(self):
        """Test for the failure of relaxation curve-fitting, replicating U{bug #19887<https://gna.org/bugs/?19887>}."""

        # Execute the script.
        try:
            self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'curve_fitting'+sep+'bug_19887_curvefit_fail.py')

        # A RelaxError is expected (but assertRaises() does not work with the script_exec method).
        except RelaxError:
            pass


    def test_curve_fitting_height(self):
        """Test the relaxation curve fitting C modules."""

        # The intensity type.
        ds.int_type = 'height'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_fit.py')

        # Check the curve-fitting results.
        self.check_curve_fitting()


    def test_curve_fitting_height_estimate_error(self):
        """Test the relaxation curve fitting C modules and estimate error."""

        # Reset
        self.interpreter.reset()

        # Create pipe.
        pipe_name = 'base pipe'
        pipe_bundle = 'relax_fit'
        self.interpreter.pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_fit')

        # The intensity type.
        ds.int_type = 'height'

        # Create the data pipe and load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting'

        # Create the spins
        self.interpreter.spectrum.read_spins(file="T2_ncyc1_ave.list", dir=data_path)

        # Relaxation times (in seconds).
        times = [
            0.0176,
            0.0176,
            0.0352,
            0.0704,
            0.0704,
            0.1056,
            0.1584,
            0.1584,
            0.1936,
            0.1936
            ]

        # Spectrum names.
        names = [
            'T2_ncyc1_ave',
            'T2_ncyc1b_ave',
            'T2_ncyc2_ave',
            'T2_ncyc4_ave',
            'T2_ncyc4b_ave',
            'T2_ncyc6_ave',
            'T2_ncyc9_ave',
            'T2_ncyc9b_ave',
            'T2_ncyc11_ave',
            'T2_ncyc11b_ave'
        ]


        # Loop over Spectrum names.
        for i, sname in enumerate(names):
            # Get the time.
            time = times[i]

            # Load the peak intensities.
            self.interpreter.spectrum.read_intensities(file=sname+'.list', dir=data_path, spectrum_id=sname, int_method=ds.int_type)

            # Set the relaxation times.
            self.interpreter.relax_fit.relax_time(time=time, spectrum_id=sname)

        self.interpreter.deselect.spin(':3,11,18,19,23,31,42,44,54,66,82,92,94,99,101,113,124,126,136,141,145,147,332,345,346,358,361')

        GRID_INC = 11
        MC_SIM = 3
        results_dir = mkdtemp()
        #min_method = 'simplex'
        #min_method = 'BFGS'
        min_method = 'newton'

        # De select one more.
        self.interpreter.deselect.spin(':512@ND2')

        # Do automatic
        if True:
            relax_fit.Relax_fit(pipe_name=pipe_name, pipe_bundle=pipe_bundle, file_root='R2', results_dir=results_dir, grid_inc=GRID_INC, mc_sim_num=MC_SIM, view_plots=False)

        else:
            # Prepare for finding dublictes.

            # Collect all times, and matching spectrum id.
            all_times = []
            all_id = []
            for s_id, time in cdp.relax_times.iteritems():
                all_times.append(time)
                all_id.append(s_id)
    
            # Get the dublicates.
            dublicates = map(lambda val: (val, [i for i in xrange(len(all_times)) if all_times[i] == val]), all_times)
    
            # Loop over the list of the mapping of times and duplications.
            list_dub_mapping = []
            for i, dub in enumerate(dublicates):
                # Get current spectum id.
                cur_spectrum_id = all_id[i]
    
                # Get the tuple of time and indexes of duplications.
                time, list_index_occur = dub
    
                # Collect mapping of index to id.
                id_list = []
                if len(list_index_occur) > 1:
                    for list_index in list_index_occur:
                        id_list.append(all_id[list_index])
    
                # Store to list
                list_dub_mapping.append((cur_spectrum_id, id_list))
    
            # Assign dublicates.
            for spectrum_id, dub_pair in list_dub_mapping:
                print spectrum_id, dub_pair
                if len(dub_pair) > 0:
                    self.interpreter.spectrum.replicated(spectrum_ids=dub_pair)
    
            # Test the number of replicates stored in cdp, is 4.
            self.assertEqual(len(cdp.replicates), 4)


            # Peak intensity error analysis.
            self.interpreter.spectrum.error_analysis()

            # Set the relaxation curve type.
            self.interpreter.relax_fit.select_model('exp')

            # Grid search.
            self.interpreter.minimise.grid_search(inc=GRID_INC)

            # Minimise.
            self.interpreter.minimise.execute(min_method, scaling=False, constraints=False)

            # Monte Carlo simulations.
            self.interpreter.monte_carlo.setup(number=MC_SIM)
            self.interpreter.monte_carlo.create_data()
            self.interpreter.monte_carlo.initial_values()
            self.interpreter.minimise.execute(min_method, scaling=False, constraints=False)
            self.interpreter.monte_carlo.error_analysis()

        # Test seq
        tseq = [ [4, 'GLY', ':4@N'],
                 [5, 'SER', ':5@N'],
                 [6, 'MET', ':6@N'],
                 [7, 'ASP', ':7@N'],
                 [8, 'SER', ':8@N'],
                 [12, 'GLY', ':12@N']]

        # Print spins
        i = 0
        for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            print(resi, resn, spin_id)
            self.assertEqual(resi, tseq[i][0])
            self.assertEqual(resn, tseq[i][1])
            self.assertEqual(spin_id, tseq[i][2])

            i += 1

        # Test the number of spins.
        self.assertEqual(count_spins(), 6)

        # Check the curve-fitting results.
        self.check_curve_fitting_manual()

        # Compare rx errors.
        if True:
            # Estimate rx and i0 errors.
            self.interpreter.error_analysis.covariance_matrix()

            # Collect:
            i0_est = []
            i0_err_est = []
            rx_est = []
            rx_err_est = []
            for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
                i0_est.append(cur_spin.i0)
                i0_err_est.append(cur_spin.i0_err)
                rx_est.append(cur_spin.rx)
                rx_err_est.append(cur_spin.rx_err)

            # Set number of MC simulati0ns
            MC_SIM = 200

            # Monte Carlo simulations.
            self.interpreter.monte_carlo.setup(number=MC_SIM)
            self.interpreter.monte_carlo.create_data()
            self.interpreter.monte_carlo.initial_values()
            self.interpreter.minimise.execute(min_method, scaling=False, constraints=False)
            self.interpreter.monte_carlo.error_analysis()

            # Collect:
            i0_mc = []
            i0_err_mc = []
            rx_mc = []
            rx_err_mc = []
            for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
                i0_mc.append(cur_spin.i0)
                i0_err_mc.append(cur_spin.i0_err)
                rx_mc.append(cur_spin.rx)
                rx_err_mc.append(cur_spin.rx_err)

            # Now print and compare
            i = 0
            print("Comparison between error estimation from Jacobian co-variance matrix and Monte-Carlo simulations.")
            print("Spin ID: rx_err_diff=est-MC, i0_err_diff=est-MC, rx_err=est/MC, i0_err=est/MC, i0=est/MC, rx=est/MC.")
            for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
                # Extract for estimation.
                i0_est_i = i0_est[i]
                i0_err_est_i = i0_err_est[i]
                rx_est_i = rx_est[i]
                rx_err_est_i = rx_err_est[i]

                # Extract from monte carlo.
                i0_mc_i = i0_mc[i]
                i0_err_mc_i = i0_err_mc[i]
                rx_mc_i = rx_mc[i]
                rx_err_mc_i = rx_err_mc[i]

                # Add to counter.
                i += 1

                # Prepare text.
                rx_err_diff = rx_err_est_i - rx_err_mc_i
                i0_err_diff = i0_err_est_i - i0_err_mc_i

                text = "Spin '%s': rx_err_diff=%3.4f, i0_err_diff=%3.3f, rx_err=%3.4f/%3.4f, i0_err=%3.3f/%3.3f, rx=%3.3f/%3.3f, i0=%3.3f/%3.3f" % (spin_id, rx_err_diff, i0_err_diff, rx_err_est_i, rx_err_mc_i, i0_err_est_i, i0_err_mc_i, rx_est_i, rx_mc_i, i0_est_i, i0_mc_i)
                print(text)


    def test_curve_fitting_volume(self):
        """Test the relaxation curve fitting C modules."""

        # The intensity type.
        ds.int_type = 'point sum'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_fit.py')

        # Check the curve-fitting results.
        self.check_curve_fitting()


    def test_read_sparky(self):
        """The Sparky peak height loading test."""

        # Load the original state.
        self.interpreter.state.load(state='basic_heights_T2_ncyc1', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'saved_states', force=True)

        # Create a new data pipe for the new data.
        self.interpreter.pipe.create('new', 'relax_fit')

        # Load the Lupin Ap4Aase sequence.
        self.interpreter.sequence.read(file="Ap4Aase.seq", dir=status.install_path + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

        # Name the spins so they can be matched to the assignments.
        self.interpreter.spin.name(name='N')

        # Read the peak heights.
        self.interpreter.spectrum.read_intensities(file="T2_ncyc1_ave.list", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting', spectrum_id='0.0176')


        # Test the integrity of the data.
        #################################

        # Get the data pipes.
        dp_new = pipes.get_pipe('new')
        dp_rx = pipes.get_pipe('rx')

        # Loop over the spins of the original data.
        for mol_index, res_index, spin_index in spin_index_loop():
            # Alias the spin containers.
            new_spin = dp_new.mol[mol_index].res[res_index].spin[spin_index]
            orig_spin = dp_rx.mol[mol_index].res[res_index].spin[spin_index]

            # Check the sequence info.
            self.assertEqual(dp_new.mol[mol_index].name, dp_rx.mol[mol_index].name)
            self.assertEqual(dp_new.mol[mol_index].res[res_index].num, dp_rx.mol[mol_index].res[res_index].num)
            self.assertEqual(dp_new.mol[mol_index].res[res_index].name, dp_rx.mol[mol_index].res[res_index].name)
            self.assertEqual(new_spin.num, orig_spin.num)
            self.assertEqual(new_spin.name, orig_spin.name)

            # Skip deselected spins.
            if not orig_spin.select:
                continue

            # Check intensities (if they exist).
            if hasattr(orig_spin, 'peak_intensity'):
                for id in dp_new.spectrum_ids:
                    self.assertEqual(orig_spin.peak_intensity[id], new_spin.peak_intensity[id])


    def test_zooming_grid_search(self):
        """Test the relaxation curve fitting C modules."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_fit_zooming_grid.py')

        # Check the curve-fitting results (the values are from the optimisation of test_curve_fitting_height()).
        spin = return_spin(":4@N")
        self.assertAlmostEqual(spin.chi2, 2.9169526515678883)
        self.assertAlmostEqual(spin.rx, 8.0814894974893967)
        self.assertAlmostEqual(spin.i0/1e6, 1996050.9699629977/1e6)
