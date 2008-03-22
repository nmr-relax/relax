###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
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
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store
from physical_constants import N15_CSA, NH_BOND_LENGTH


class Mf(TestCase):
    """TestCase class for the functional tests of model-free analysis."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_create_m4(self):
        """Creating model m4 with parameters {S2, te, Rex} using model_free.create_model()."""

        # Execute the script.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/create_m4.py')

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test the model.
        self.assertEqual(cdp.mol[0].res[1].spin[0].model, 'm4')
        self.assertEqual(cdp.mol[0].res[1].spin[0].params, ['S2', 'te', 'Rex'])


    def test_opendx_s2_te_rex(self):
        """Mapping the {S2, te, Rex} chi2 space through the OpenDX user function dx.map()."""

        # Execute the script.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/opendx_s2_te_rex.py')


    def test_opendx_theta_phi_da(self):
        """Mapping the {theta, phi, Da} chi2 space through the OpenDX user function dx.map()."""

        # Path of the files.
        path = sys.path[-1] + '/test_suite/system_tests/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='noe.500.out', dir=path)

        # Read the PDF file and set the vectors.
        self.relax.interpreter._Structure.read_pdb(file='pdb', dir=path, model=1, load_seq=0)
        self.relax.interpreter._Structure.vectors(heteronuc='N', proton='H')

        # Read the relaxation data.
        self.relax.interpreter._Relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)
        self.relax.interpreter._Relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out', dir=path)
        self.relax.interpreter._Relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out', dir=path)
        self.relax.interpreter._Relax_data.read('R1', '500', 500.0 * 1e6, 'r1.500.out', dir=path)
        self.relax.interpreter._Relax_data.read('R2', '500', 500.0 * 1e6, 'r2.500.out', dir=path)
        self.relax.interpreter._Relax_data.read('NOE', '500', 500.0 * 1e6, 'noe.500.out', dir=path)

        # Setup other values.
        self.relax.interpreter._Diffusion_tensor.init((1.601 * 1e7, 1.34, 72.4, 90-77.9), param_types=4)
        self.relax.interpreter._Value.set([N15_CSA, NH_BOND_LENGTH], ['csa', 'bond_length'])
        self.relax.interpreter._Value.set([0.8, 50 * 1e-12, 0.0], ['S2', 'te', 'Rex'])
        self.relax.interpreter._Value.set('N', 'nucleus')

        # Select the model.
        self.relax.interpreter._Model_free.select_model(model='m4')

        # Map the space.
        self.relax.interpreter._OpenDX.map(params=['theta', 'phi', 'Da'], res_num=2, inc=2, lower=[0, 0, -0.5*1e7], upper=[pi, 2.0*pi, 1.0*1e7], file='devnull')


    def test_opendx_tm_s2_te(self):
        """Mapping the {local_tm, S2, te} chi2 space through the OpenDX user function dx.map()."""

        # Path of the files.
        path = sys.path[-1] + '/test_suite/system_tests/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='noe.500.out', dir=path)

        # Read the relaxation data.
        self.relax.interpreter._Relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)
        self.relax.interpreter._Relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out', dir=path)
        self.relax.interpreter._Relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out', dir=path)
        self.relax.interpreter._Relax_data.read('R1', '500', 500.0 * 1e6, 'r1.500.out', dir=path)
        self.relax.interpreter._Relax_data.read('R2', '500', 500.0 * 1e6, 'r2.500.out', dir=path)
        self.relax.interpreter._Relax_data.read('NOE', '500', 500.0 * 1e6, 'noe.500.out', dir=path)

        # Setup other values.
        self.relax.interpreter._Value.set([N15_CSA, NH_BOND_LENGTH], ['csa', 'bond_length'])
        self.relax.interpreter._Value.set('N', 'nucleus')

        # Select the model.
        self.relax.interpreter._Model_free.select_model(model='tm2')

        # Map the space.
        self.relax.interpreter._OpenDX.map(params=['local_tm', 'S2', 'te'], res_num=2, inc=2, file='devnull')


    def test_opt_constr_bfgs_back_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained BFGS opt, backtracking line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            BFGS optimisation.
            Backtracking line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set([1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('bfgs', 'back')

        # Alias the relevent spin container.
        spin = relax_data_store[relax_data_store.current_pipe].mol[0].res[1].spin[0]

        # Test the values.
        self.assertEqual(relax_data_store[relax_data_store.current_pipe].mol[0].res[0].spin[0].select, 0)
        self.assertEqual(spin.select, 1)
        self.assertAlmostEqual(spin.s2, 0.970)
        self.assertAlmostEqual(spin.te, 2048 * 1e-12)
        self.assertAlmostEqual(spin.rex, 0.149 / (2.0 * pi * spin.frq[0])**2)
        self.assertAlmostEqual(spin.chi2, 3.1024517431117421e-27)
        self.assertEqual(spin.iter, 203)
        self.assertEqual(spin.f_count, 955)
        self.assertEqual(spin.g_count, 209)
        self.assertEqual(spin.h_count, 0)
        self.assertEqual(spin.warning, None)


    def test_opt_constr_bfgs_mt_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained BFGS opt, More and Thuente line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            BFGS optimisation.
            More and Thuente line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set([1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('bfgs', 'mt')

        # Alias the relevent spin container.
        spin = relax_data_store[relax_data_store.current_pipe].mol[0].res[1].spin[0]

        # Test the values.
        self.assertEqual(relax_data_store[relax_data_store.current_pipe].mol[0].res[0].spin[0].select, 0)
        self.assertEqual(spin.select, 1)
        self.assertAlmostEqual(spin.s2, 0.970)
        self.assertAlmostEqual(spin.te, 2048 * 1e-12)
        self.assertAlmostEqual(spin.rex, 0.149 / (2.0 * pi * spin.frq[0])**2)
        self.assertAlmostEqual(spin.chi2, 3.1024517431117421e-27)
        self.assertEqual(spin.iter, 203)
        self.assertEqual(spin.f_count, 955)
        self.assertEqual(spin.g_count, 209)
        self.assertEqual(spin.h_count, 0)
        self.assertEqual(spin.warning, None)


    def test_opt_constr_cd_back_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained coordinate descent opt, backtracking line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            Coordinate descent optimisation.
            Backtracking line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set([1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('cd', 'back', max_iter=50)

        # Alias the relevent spin container.
        spin = relax_data_store[relax_data_store.current_pipe].mol[0].res[1].spin[0]

        # Test the values.
        self.assertEqual(relax_data_store[relax_data_store.current_pipe].mol[0].res[0].spin[0].select, 0)
        self.assertEqual(spin.select, 1)
        self.assertAlmostEqual(spin.s2, 0.9097900390625)
        self.assertAlmostEqual(spin.te, 2.5000000000000001e-11)
        self.assertAlmostEqual(spin.rex, 1.24017333984375 / (2.0 * pi * spin.frq[0])**2)
        self.assertAlmostEqual(spin.chi2, 53.476155463267176)
        self.assertEqual(spin.iter, 50)
        self.assertEqual(spin.f_count, 131)
        self.assertEqual(spin.g_count, 51)
        self.assertEqual(spin.h_count, 0)
        self.assertEqual(spin.warning, None or 'Maximum number of iterations reached')


    def test_opt_constr_cd_mt_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained coordinate descent opt, More and Thuente line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            Coordinate descent optimisation.
            More and Thuente line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set([1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('cd', 'mt', max_iter=50)

        # Alias the relevent spin container.
        spin = relax_data_store[relax_data_store.current_pipe].mol[0].res[1].spin[0]

        # Test the values.
        self.assertEqual(relax_data_store[relax_data_store.current_pipe].mol[0].res[0].spin[0].select, 0)
        self.assertEqual(spin.select, 1)
        self.assertAlmostEqual(spin.s2, 1.0)
        self.assertAlmostEqual(spin.te, 0.0)
        self.assertAlmostEqual(spin.rex, 0.0)
        self.assertAlmostEqual(spin.chi2, 3.9844117908982288)
        self.assertEqual(spin.iter, 0)
        self.assertEqual(spin.f_count, 1)
        self.assertEqual(spin.g_count, 1)
        self.assertEqual(spin.h_count, 0)
        self.assertEqual(spin.warning, None or 'Maximum number of iterations reached')


    def test_opt_constr_newton_gmw_back_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained Newton opt, GMW Hessian mod, backtracking line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            Newton optimisation.
            GMW Hessian modification.
            Backtracking line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set([1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('newton', 'gmw', 'back')

        # Alias the relevent spin container.
        spin = relax_data_store[relax_data_store.current_pipe].mol[0].res[1].spin[0]

        # Test the values.
        self.assertEqual(relax_data_store[relax_data_store.current_pipe].mol[0].res[0].spin[0].select, 0)
        self.assertEqual(spin.select, 1)
        self.assertAlmostEqual(spin.s2, 0.970)
        self.assertAlmostEqual(spin.te, 2048 * 1e-12)
        self.assertAlmostEqual(spin.rex, 0.149 / (2.0 * pi * spin.frq[0])**2)
        self.assertAlmostEqual(spin.chi2, 7.3040158179665562e-28)
        self.assertEqual(spin.iter, 18)
        self.assertEqual(spin.f_count, 96)
        self.assertEqual(spin.g_count, 23)
        self.assertEqual(spin.h_count, 18)
        self.assertEqual(spin.warning, None)


    def test_opt_constr_newton_gmw_mt_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained Newton opt, GMW Hessian mod, More and Thuente line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            Newton optimisation.
            GMW Hessian modification.
            More and Thuente line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set([1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('newton', 'gmw', 'mt')

        # Alias the relevent spin container.
        spin = relax_data_store[relax_data_store.current_pipe].mol[0].res[1].spin[0]

        # Test the values.
        self.assertEqual(relax_data_store[relax_data_store.current_pipe].mol[0].res[0].spin[0].select, 0)
        self.assertEqual(spin.select, 1)
        self.assertAlmostEqual(spin.s2, 0.970)
        self.assertAlmostEqual(spin.te, 2048 * 1e-12)
        self.assertAlmostEqual(spin.rex, 0.149 / (2.0 * pi * spin.frq[0])**2)
        self.assertAlmostEqual(spin.chi2, 6.8756889983348349e-28)
        self.assertEqual(spin.iter, 22)
        self.assertEqual(spin.f_count, 159)
        self.assertEqual(spin.g_count, 159)
        self.assertEqual(spin.h_count, 22)
        self.assertEqual(spin.warning, None)


    def test_opt_constr_sd_back_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained steepest descent opt, backtracking line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            Steepest descent optimisation.
            Backtracking line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set([1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('sd', 'back', max_iter=50)

        # Alias the relevent spin container.
        spin = relax_data_store[relax_data_store.current_pipe].mol[0].res[1].spin[0]

        # Test the values.
        self.assertEqual(relax_data_store[relax_data_store.current_pipe].mol[0].res[0].spin[0].select, 0)
        self.assertEqual(spin.select, 1)
        self.assertAlmostEqual(spin.s2, 0.91579220834688024)
        self.assertAlmostEqual(spin.te, 3.056865872253173e-13)
        self.assertAlmostEqual(spin.rex, 0.34008409798366124 / (2.0 * pi * spin.frq[0])**2)
        self.assertAlmostEqual(spin.chi2, 68.321956795264342)
        self.assertEqual(spin.iter, 50)
        self.assertEqual(spin.f_count, 134)
        self.assertEqual(spin.g_count, 51)
        self.assertEqual(spin.h_count, 0)
        self.assertEqual(spin.warning, None or 'Maximum number of iterations reached')


    def test_opt_constr_sd_mt_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained steepest descent opt, More and Thuente line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            Steepest descent optimisation.
            More and Thuente line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set([1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('sd', 'mt', max_iter=50)

        # Alias the relevent spin container.
        spin = relax_data_store[relax_data_store.current_pipe].mol[0].res[1].spin[0]

        # Test the values.
        self.assertEqual(relax_data_store[relax_data_store.current_pipe].mol[0].res[0].spin[0].select, 0)
        self.assertEqual(spin.select, 1)
        self.assertAlmostEqual(spin.s2, 0.91619994957822126)
        self.assertAlmostEqual(spin.te, 1.2319687570987945e-13)
        self.assertAlmostEqual(spin.rex, 0.16249110942961512 / (2.0 * pi * spin.frq[0])**2)
        self.assertAlmostEqual(spin.chi2, 73.843613546506191)
        self.assertEqual(spin.iter, 50)
        self.assertEqual(spin.f_count, 108)
        self.assertEqual(spin.g_count, 108)
        self.assertEqual(spin.h_count, 0)
        self.assertEqual(spin.warning, None or 'Maximum number of iterations reached')


    def test_opt_grid_search_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained grid search {S2=0.970, te=2048, Rex=0.149}.

        The optimisation options are:
            Constrained grid search.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Grid search.
        self.relax.interpreter._Minimisation.grid_search(inc=11)

        # Alias the relevent spin container.
        spin = relax_data_store[relax_data_store.current_pipe].mol[0].res[1].spin[0]

        # Test the values.
        self.assertEqual(relax_data_store[relax_data_store.current_pipe].mol[0].res[0].spin[0].select, 0)
        self.assertEqual(spin.select, 1)
        self.assertAlmostEqual(spin.s2, 1.0)
        self.assertAlmostEqual(spin.te, 0.0)
        self.assertAlmostEqual(spin.rex, 0.0)
        self.assertAlmostEqual(spin.chi2, 3.9844117908982288)
        self.assertEqual(spin.iter, 1331)
        self.assertEqual(spin.f_count, 1331)
        self.assertEqual(spin.g_count, 0)
        self.assertEqual(spin.h_count, 0)
        self.assertEqual(spin.warning, None)


    def test_read_relax_data(self):
        """Reading of relaxation data using the user function relax_data.read()."""

        # Path of the files.
        path = sys.path[-1] + '/test_suite/system_tests/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='noe.500.out', dir=path)

        # Read the relaxation data.
        self.relax.interpreter._Relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test the data and error.
        self.assertEqual(cdp.mol[0].res[1].spin[0].relax_data[0], 1.3874977659397683)
        self.assertEqual(cdp.mol[0].res[1].spin[0].relax_error[0], 0.027749955318795365)


    def test_read_results(self):
        """The reading of model-free results using the user function results.read()."""

        # Load the original state.
        self.relax.interpreter._State.load(state='orig_state', dir_name=sys.path[-1] + '/test_suite/system_tests/data/model_free')

        # Read the results.
        self.relax.interpreter._Results.read(dir=sys.path[-1] + '/test_suite/system_tests/data/model_free')

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Diffusion tensor type.
        self.assertEqual(relax_data_store['orig'].diff.type, cdp.diff.type)

        # tm.
        self.assertEqual(relax_data_store['orig'].diff.tm, cdp.diff.tm)

        # Loop over the residues of the original data.
        for i in xrange(len(cdp.mol[0].res)):
            # Aliases
            orig_data_res = relax_data_store['orig'].mol[0].res[i]
            new_data_res = cdp.mol[0].res[i]
            orig_data = relax_data_store['orig'].mol[0].res[i].spin[0]
            new_data = cdp.mol[0].res[i].spin[0]

            # Spin info tests.
            self.assertEqual(orig_data_res.num, new_data_res.num)
            self.assertEqual(orig_data_res.name, new_data_res.name)
            self.assertEqual(orig_data.num, new_data.num)
            self.assertEqual(orig_data.name, new_data.name)
            self.assertEqual(orig_data.select, new_data.select)

            # Skip unselected residues.
            if not orig_data.select:
                continue

            # Model-free tests.
            self.assertEqual(orig_data.model, new_data.model)
            self.assertEqual(orig_data.params, new_data.params)
            self.assertEqual(orig_data.s2, new_data.s2)
            self.assertEqual(orig_data.s2f, new_data.s2f)
            self.assertEqual(orig_data.s2s, new_data.s2s)
            self.assertEqual(orig_data.local_tm, new_data.local_tm)
            self.assertEqual(orig_data.te, new_data.te)
            self.assertEqual(orig_data.tf, new_data.tf)
            self.assertEqual(orig_data.ts, new_data.ts)
            self.assertEqual(orig_data.rex, new_data.rex)
            self.assertEqual(orig_data.r, new_data.r)
            self.assertEqual(orig_data.csa, new_data.csa)

            # Minimisation statistic tests.
            self.assertEqual(orig_data.chi2, new_data.chi2)
            self.assertEqual(orig_data.iter, new_data.iter)
            self.assertEqual(orig_data.f_count, new_data.f_count)
            self.assertEqual(orig_data.g_count, new_data.g_count)
            self.assertEqual(orig_data.h_count, new_data.h_count)
            self.assertEqual(orig_data.warning, new_data.warning)

            # Relaxation data tests.
            self.assertEqual(orig_data.ri_labels, new_data.ri_labels)
            self.assertEqual(orig_data.remap_table, new_data.remap_table)
            self.assertEqual(orig_data.frq_labels, new_data.frq_labels)
            self.assertEqual(orig_data.relax_data, new_data.relax_data)
            self.assertEqual(orig_data.relax_error, new_data.relax_error)


    def test_select_m4(self):
        """Selecting model m4 with parameters {S2, te, Rex} using model_free.select_model()."""

        # Path of the files.
        path = sys.path[-1] + '/test_suite/system_tests/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='noe.500.out', dir=path)

        # Select the model.
        self.relax.interpreter._Model_free.select_model(model='m4')

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test the model.
        self.assertEqual(cdp.mol[0].res[1].spin[0].model, 'm4')
        self.assertEqual(cdp.mol[0].res[1].spin[0].params, ['S2', 'te', 'Rex'])


    def test_set_bond_length(self):
        """Setting the bond length through the user function value.set()."""

        # Path of the files.
        path = sys.path[-1] + '/test_suite/system_tests/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='noe.500.out', dir=path)

        # Set the CSA value.
        self.relax.interpreter._Value.set(NH_BOND_LENGTH, 'bond_length')

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test the value.
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, NH_BOND_LENGTH)


    def test_set_csa(self):
        """Setting the CSA value through the user function value.set()."""

        # Path of the files.
        path = sys.path[-1] + '/test_suite/system_tests/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='noe.500.out', dir=path)

        # Set the CSA value.
        self.relax.interpreter._Value.set(N15_CSA, 'csa')

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test the value.
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, N15_CSA)


    def test_set_csa_bond_length(self):
        """Setting both the CSA value and bond length through the user function value.set()."""

        # Path of the files.
        path = sys.path[-1] + '/test_suite/system_tests/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='noe.500.out', dir=path)

        # Set the CSA value and bond length simultaneously.
        self.relax.interpreter._Value.set([N15_CSA, NH_BOND_LENGTH], ['csa', 'bond_length'])

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test the values.
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, N15_CSA)
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, NH_BOND_LENGTH)
