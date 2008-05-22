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
import platform
import numpy
import sys
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from physical_constants import N15_CSA, NH_BOND_LENGTH


# Get the platform information.
SYSTEM = platform.system()
RELEASE = platform.release()
VERSION = platform.version()
WIN32_VER = platform.win32_ver()
DIST = platform.dist()
ARCH = platform.architecture()
MACH = platform.machine()
PROC = platform.processor()
PY_VER = platform.python_version()

# Windows system name pain.
if SYSTEM == 'Windows' or SYSTEM == 'Microsoft':
    # Set the system to 'Windows' no matter what.
    SYSTEM = 'Windows'



class Mf(TestCase):
    """TestCase class for the functional tests of model-free analysis."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def mesg_opt_debug(self, spin):
        """Method for returning a string to help debug the minimisation.

        @param spin:    The SpinContainer of the optimised spin.
        @type spin:     SpinContainer instance
        @return:        The debugging string.
        @rtype:         str
        """

        # Initialise the string.
        string = 'Optimisation failure.\n\n'

        # Create the string.
        string = string + "System: " + SYSTEM + "\n"
        string = string + "Release: " + RELEASE + "\n"
        string = string + "Version: " + VERSION + "\n"
        string = string + "Win32 version: " + WIN32_VER[0] + " " + WIN32_VER[1] + " " + WIN32_VER[2] + " " + WIN32_VER[3] + "\n"
        string = string + "Distribution: " + DIST[0] + " " + DIST[1] + " " + DIST[2] + "\n"
        string = string + "Architecture: " + ARCH[0] + " " + ARCH[1] + "\n"
        string = string + "Machine: " + MACH + "\n"
        string = string + "Processor: " + PROC + "\n"
        string = string + "Python version: " + PY_VER + "\n"
        string = string + "numpy version: " + numpy.__version__ + "\n"


        # Minimisation info.
        string = string + "\n\n%-10s%10.16f" % ('s2:', spin.s2)
        string = string + "\n%-10s%10.13f" % ('te:', spin.te * 1e12)
        string = string + "\n%-10s%10.17f" % ('rex:', spin.rex * (2.0 * pi * spin.frq[0])**2)
        string = string + "\n%-10s%10.17g" % ('chi2:', spin.chi2)
        string = string + "\n%-10s%-10i" % ('iter:', spin.iter)
        string = string + "\n%-10s%-10i" % ('f_count:', spin.f_count)
        string = string + "\n%-10s%-10i" % ('g_count:', spin.g_count)
        string = string + "\n%-10s%-10i" % ('h_count:', spin.h_count)
        string = string + "\n%-10s%-10s" % ('warning:', spin.warning)

        # Return the string.
        return string


    def test_create_m4(self):
        """Creating model m4 with parameters {S2, te, Rex} using model_free.create_model()."""

        # Execute the script.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/create_m4.py')

        # Alias the current data pipe.
        cdp = ds[ds.current_pipe]

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
        self.relax.interpreter._Structure.read_pdb(file='pdb', dir=path, model=1)
        self.relax.interpreter._Structure.load_spins('@N')
        self.relax.interpreter._Structure.vectors(proton='H')

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
        self.relax.interpreter._Value.set('15N', 'heteronucleus')
        self.relax.interpreter._Value.set('1H', 'proton')

        # Select the model.
        self.relax.interpreter._Model_free.select_model(model='m4')

        # Map the space.
        self.relax.interpreter._OpenDX.map(params=['theta', 'phi', 'Da'], spin_id=':2', inc=2, lower=[0, 0, -0.5*1e7], upper=[pi, 2.0*pi, 1.0*1e7], file_prefix='devnull')


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
        self.relax.interpreter._Value.set('15N', 'heteronucleus')
        self.relax.interpreter._Value.set('1H', 'proton')

        # Select the model.
        self.relax.interpreter._Model_free.select_model(model='tm2')

        # Map the space.
        self.relax.interpreter._OpenDX.map(params=['local_tm', 'S2', 'te'], spin_id=':2', inc=2, lower=[5e-9, 0.0, 0.0], file_prefix='devnull')


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
        spin = ds[ds.current_pipe].mol[0].res[1].spin[0]

        # Optimisation values (from 32 bit Linux as the standard).
        select = True
        s2 = 0.9699999999999995
        te = 2048.000000000022283
        rex = 0.14900000000000566
        chi2 = 3.1024517431117421e-27
        iter = 203
        f_count = 955
        g_count = 209
        h_count = 0
        warning = None

        # Optimisation differences.
        if SYSTEM == 'Linux' and ARCH[0] == '64bit':
            iter = 162
            f_count = 758
            g_count = 169

        # Test the values.
        self.assertEqual(ds[ds.current_pipe].mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select, s2, te, rex, chi2, iter, f_count, g_count, h_count, warning)


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
        spin = ds[ds.current_pipe].mol[0].res[1].spin[0]

        # Optimisation values (from 32 bit Linux as the standard).
        select = True
        s2 = 0.9700000000000580
        te = 2048.000000011044449
        rex = 0.148999999998904
        chi2 = 4.3978813282102374e-23
        iter = 120
        f_count = 388
        g_count = 388
        h_count = 0
        warning = None

        # Optimisation differences.
        if SYSTEM == 'Linux' and ARCH[0] == '64bit':
            f_count = 384
            g_count = 384

        # Test the values.
        self.assertEqual(ds[ds.current_pipe].mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select, s2, te, rex, chi2, iter, f_count, g_count, h_count, warning)


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
        spin = ds[ds.current_pipe].mol[0].res[1].spin[0]

        # Optimisation values (from 32 bit Linux as the standard).
        select = True
        s2 = 0.9097900390625
        te = 25.00000000000000
        rex = 1.24017333984375
        chi2 = 53.476155463267176
        iter = 50
        f_count = 131
        g_count = 51
        h_count = 0
        warning = 'Maximum number of iterations reached'

        # Test the values.
        self.assertEqual(ds[ds.current_pipe].mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select, s2, te, rex, chi2, iter, f_count, g_count, h_count, warning)


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
        self.relax.interpreter._Minimisation.minimise('cd', 'mt')

        # Alias the relevent spin container.
        spin = ds[ds.current_pipe].mol[0].res[1].spin[0]

        # Optimisation values (from 32 bit Linux as the standard).
        select = True
        s2 = 0.9700000000219674
        te = 2048.000001534187049
        rex = 0.14899999946977982
        chi2 = 2.3477234248531005e-18
        iter = 198
        f_count = 738
        g_count = 738
        h_count = 0
        warning = None

        # Optimisation differences.
        if SYSTEM == 'Linux' and ARCH[0] == '64bit':
            f_count = 757
            g_count = 757

        # Test the values.
        self.assertEqual(ds[ds.current_pipe].mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select, s2, te, rex, chi2, iter, f_count, g_count, h_count, warning)


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
        spin = ds[ds.current_pipe].mol[0].res[1].spin[0]

        # Optimisation values (from 32 bit Linux as the standard).
        select = True
        s2 = 0.9699999999999994
        te = 2048.000000000045020
        rex = 0.14900000000001817
        chi2 = 7.3040158179665562e-28
        iter = 18
        f_count = 55
        g_count = 23
        h_count = 18
        warning = None

        # Test the values.
        self.assertEqual(ds[ds.current_pipe].mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select, s2, te, rex, chi2, iter, f_count, g_count, h_count, warning)


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
        spin = ds[ds.current_pipe].mol[0].res[1].spin[0]

        # Optimisation values (from 32 bit Linux as the standard).
        select = True
        s2 = 0.9699999999999993
        te = 2048.000000000041837
        rex = 0.14900000000002225
        chi2 = 6.8756889983348349e-28
        iter = 22
        f_count = 159
        g_count = 159
        h_count = 22
        warning = None

        # Optimisation differences.
        if SYSTEM == 'Linux' and ARCH[0] == '64bit':
            f_count = 91
            g_count = 91

        # Test the values.
        self.assertEqual(ds[ds.current_pipe].mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select, s2, te, rex, chi2, iter, f_count, g_count, h_count, warning)


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
        spin = ds[ds.current_pipe].mol[0].res[1].spin[0]

        # Optimisation values (from 32 bit Linux as the standard).
        select = True
        s2 = 0.91579220834688024
        te = 0.30568658722531733
        rex = 0.34008409798366124
        chi2 = 68.321956795264342
        iter = 50
        f_count = 134
        g_count = 51
        h_count = 0
        warning = 'Maximum number of iterations reached'

        # Test the values.
        self.assertEqual(ds[ds.current_pipe].mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select, s2, te, rex, chi2, iter, f_count, g_count, h_count, warning)


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
        spin = ds[ds.current_pipe].mol[0].res[1].spin[0]

        # Get the debugging message.
        mesg = self.mesg_opt_debug(spin)

        # Test the values.
        self.assertEqual(ds[ds.current_pipe].mol[0].res[0].spin[0].select, False, msg=mesg)
        self.assertEqual(spin.select, True, msg=mesg)
        self.assertAlmostEqual(spin.s2, 0.91619994957822126, msg=mesg)
        self.assertAlmostEqual(spin.te, 1.2319687570987945e-13, msg=mesg)
        self.assertAlmostEqual(spin.rex, 0.16249110942961512 / (2.0 * pi * spin.frq[0])**2, msg=mesg)
        self.assertAlmostEqual(spin.chi2, 73.843613546506191, msg=mesg)
        self.assertEqual(spin.iter, 50, msg=mesg)
        self.assertEqual(spin.f_count, 108, msg=mesg)
        self.assertEqual(spin.g_count, 108, msg=mesg)
        self.assertEqual(spin.h_count, 0, msg=mesg)
        self.assertEqual(spin.warning, None or 'Maximum number of iterations reached', msg=mesg)


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
        spin = ds[ds.current_pipe].mol[0].res[1].spin[0]

        # Optimisation values (from 32 bit Linux as the standard).
        select = True
        s2 = 1.0
        te = 0.0
        rex = 0.0
        chi2 = 3.9844117908982288
        iter = 1331
        f_count = 1331
        g_count = 0
        h_count = 0
        warning = None

        # Test the values.
        self.assertEqual(ds[ds.current_pipe].mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select, s2, te, rex, chi2, iter, f_count, g_count, h_count, warning)


    def test_read_relax_data(self):
        """Reading of relaxation data using the user function relax_data.read()."""

        # Path of the files.
        path = sys.path[-1] + '/test_suite/system_tests/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='noe.500.out', dir=path)

        # Read the relaxation data.
        self.relax.interpreter._Relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)

        # Alias the current data pipe.
        cdp = ds[ds.current_pipe]

        # Test the data and error.
        self.assertEqual(cdp.mol[0].res[1].spin[0].relax_data[0], 1.3874977659397683)
        self.assertEqual(cdp.mol[0].res[1].spin[0].relax_error[0], 0.027749955318795365)


    def test_read_results_1_2(self):
        """Read a relax 1.2 model-free results file using the user function results.read()."""

        # Read the results.
        self.relax.interpreter._Results.read(file='results_1.2', dir=sys.path[-1] + '/test_suite/system_tests/data/model_free')

        # Alias the current data pipe.
        cdp = ds[ds.current_pipe]

        # Diffusion tensor type.
        self.assertEqual(ds['orig'].diff.type, cdp.diff.type)

        # tm.
        self.assertEqual(ds['orig'].diff.tm, cdp.diff.tm)

        # Loop over the residues of the original data.
        for i in xrange(len(cdp.mol[0].res)):
            # Aliases
            orig_data_res = ds['orig'].mol[0].res[i]
            new_data_res = cdp.mol[0].res[i]
            orig_data = ds['orig'].mol[0].res[i].spin[0]
            new_data = cdp.mol[0].res[i].spin[0]

            # Spin info tests.
            self.assertEqual(orig_data_res.num, new_data_res.num)
            self.assertEqual(orig_data_res.name, new_data_res.name)
            self.assertEqual(orig_data.num, new_data.num)
            self.assertEqual(orig_data.name, new_data.name)
            self.assertEqual(orig_data.select, new_data.select)

            # Skip deselected residues.
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
        cdp = ds[ds.current_pipe]

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
        cdp = ds[ds.current_pipe]

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
        cdp = ds[ds.current_pipe]

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
        cdp = ds[ds.current_pipe]

        # Test the values.
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, N15_CSA)
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, NH_BOND_LENGTH)


    def value_test(self, spin, select, s2, te, rex, chi2, iter, f_count, g_count, h_count, warning):
        """Method for testing the optimisation values.

        """

        # Get the debugging message.
        mesg = self.mesg_opt_debug(spin)

        # Test all the values.
        self.assertEqual(spin.select, select, msg=mesg)
        self.assertAlmostEqual(spin.s2, s2, msg=mesg)
        self.assertAlmostEqual(spin.te / 1e-12, te, msg=mesg)
        self.assertAlmostEqual(spin.rex * (2.0 * pi * spin.frq[0])**2, rex, msg=mesg)
        self.assertAlmostEqual(spin.chi2, chi2, msg=mesg)
        self.assertEqual(spin.iter, iter, msg=mesg)
        self.assertEqual(spin.f_count, f_count, msg=mesg)
        self.assertEqual(spin.g_count, g_count, msg=mesg)
        self.assertEqual(spin.h_count, h_count, msg=mesg)
        self.assertEqual(spin.warning, warning, msg=mesg)
