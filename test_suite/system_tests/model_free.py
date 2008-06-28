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
from relax_io import DummyFileObject, open_read_file


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
        path = sys.path[-1] + '/test_suite/shared_data/model_free/S2_0.970_te_2048_Rex_0.149'

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
        path = sys.path[-1] + '/test_suite/shared_data/model_free/S2_0.970_te_2048_Rex_0.149'

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
        elif SYSTEM == 'Windows' and ARCH[0] == '32bit':
            iter = 156
            f_count = 701
            g_count = 163

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
        elif SYSTEM == 'Windows' and ARCH[0] == '32bit':
            f_count = 165
            g_count = 165

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
        path = sys.path[-1] + '/test_suite/shared_data/model_free/S2_0.970_te_2048_Rex_0.149'

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
        self.relax.interpreter._Results.read(file='results_1.2', dir=sys.path[-1] + '/test_suite/shared_data/model_free')

        # Alias the current data pipe.
        cdp = ds[ds.current_pipe]

        # Debugging print out.
        print cdp

        # The spin specific data.
        num = [3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35]
        select = [False, False, False, False, False, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False, False, False]
        model = ['m6', 'm8', 'm6', 'm6', 'm5', 'm5', 'm6', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm8']
        params = [['S2f', 'tf', 'S2', 'ts'], ['S2f', 'tf', 'S2', 'ts', 'Rex'], ['S2f', 'tf', 'S2', 'ts'], ['S2f', 'tf', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'tf', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'S2', 'ts'], ['S2f', 'tf', 'S2', 'ts', 'Rex']]
        s2 = [0.36670427146403667, 0.29007016882193892, 0.32969827132809559, 0.32795333510352148, 0.48713005133752196, 0.40269538236298569, 0.40700811448591556, 0.4283551026406261, 0.51176783207279875, 0.40593664887508263, 0.39437732735324443, 0.51457448574034614, 0.3946900969237977, 0.44740698217286901, 0.48527716982891644, 0.40845486062540021, 0.45839900995265137, 0.52650140958170921, 0.4293599736020427, 0.4057313062564018, 0.49877862202992485, 0.2592017578673716]
        s2f = [0.74487419686217116, 0.75358958979175727, 0.77751085082436211, 0.79095600331751026, 0.81059857999556584, 0.83190224667917501, 0.80119109731193627, 0.83083248649122576, 0.86030420847112021, 0.84853537580616367, 0.82378413185968968, 0.82419108009774422, 0.85121172821954216, 0.8736616181472916, 0.84117641395909415, 0.82881488883235521, 0.82697284935760407, 0.85172375147802715, 0.81366357660551614, 0.80525752789388483, 0.87016608774434312, 0.72732036363757913]
        s2s = [0.49230363061145249, 0.38491796164819009, 0.4240433056059994, 0.41462904855388333, 0.60095102971952741, 0.48406574687168274, 0.50800379067049317, 0.51557336720143987, 0.59486845122178478, 0.47839684761453399, 0.47873867934666214, 0.62433881919629686, 0.46368028522041266, 0.51210557140148982, 0.57690296800513374, 0.49281795745831319, 0.55430962492751434, 0.61815983018913379, 0.5276873464009153, 0.50385285725620466, 0.57319933407525203, 0.35637907423767778]
        tf = [51.972302580836775, 40.664901270582988, 28.130299965023671, 33.804249387275249, None, None, 39.01236115991609, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 44.039078787981225]
        ts = [4485.91415175767, 4102.7781982031429, 3569.2837792404325, 6879.5308400989479, 3372.9879908647699, 4029.0617588044606, 4335.5290462417324, 4609.1336532777468, 2628.5638771308277, 3618.1332115807745, 6208.3028336637644, 3763.0843884066526, 3847.9994107906346, 2215.2061317769703, 2936.1282626562524, 3647.0715185456729, 3803.6990762708042, 2277.5259401416288, 3448.4496004396187, 3884.6917561878495, 1959.3267951363712, 4100.8496898773756]
        rex = [None, 0.37670424516405815, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 0.71472288436387088]
        r1_500 = [2.2480000000000002, 2.2679999999999998, 2.2309999999999999, 2.383, 2.1960000000000002, 2.3570000000000002, 2.3340000000000001, 2.3999999999999999, 2.2839999999999998, 2.3889999999999998, 2.375, 2.274, 2.407, 2.3220000000000001, 2.2130000000000001, 2.351, 2.3260000000000001, 2.2949999999999999, 2.2829999999999999, 2.302, 2.2719999999999998, 2.2280000000000002]
        r2_500 = [5.3419999999999996, 5.3730000000000002, 5.1280000000000001, 5.6749999999999998, 5.9669999999999996, 5.8410000000000002, 5.774, 6.0419999999999998, 6.3129999999999997, 5.9210000000000003, 6.1269999999999998, 6.1120000000000001, 6.0570000000000004, 5.6399999999999997, 6.2809999999999997, 5.8890000000000002, 5.875, 6.1429999999999998, 5.7370000000000001, 5.5490000000000004, 5.7110000000000003, 5.4020000000000001]
        noe_500 = [0.4617, 0.46560000000000001, 0.61670000000000003, 0.60860000000000003, 0.68869999999999998, 0.6663, 0.58620000000000005, 0.64939999999999998, 0.61070000000000002, 0.61180000000000001, 0.73129999999999995, 0.69650000000000001, 0.65139999999999998, 0.4929, 0.65920000000000001, 0.63029999999999997, 0.64380000000000004, 0.53500000000000003, 0.63839999999999997, 0.65000000000000002, 0.49909999999999999, 0.45979999999999999]
        r1_600 = [1.8879999999999999, 1.992, 2.0270000000000001, 1.9790000000000001, 1.9399999999999999, 2.0550000000000002, 2.0030000000000001, 2.0139999999999998, 1.982, 2.1000000000000001, 2.008, 1.927, 2.1019999999999999, 2.0830000000000002, 1.9910000000000001, 2.036, 1.9990000000000001, 1.9490000000000001, 1.976, 1.9870000000000001, 2.0, 1.9379999999999999]
        r2_600 = [5.6100000000000003, 5.7869999999999999, 5.4029999999999996, 6.1849999999999996, 6.3150000000000004, 5.9809999999999999, 6.1600000000000001, 6.2460000000000004, 6.4340000000000002, 6.0069999999999997, 6.399, 6.6799999999999997, 6.1369999999999996, 5.952, 6.3239999999999998, 5.9699999999999998, 6.3979999999999997, 6.4379999999999997, 6.1139999999999999, 6.0960000000000001, 6.3250000000000002, 6.1050000000000004]
        noe_600 = [0.62929999999999997, 0.64429999999999998, 0.5393, 0.71509999999999996, 0.73870000000000002, 0.75580000000000003, 0.64239999999999997, 0.74429999999999996, 0.69440000000000002, 0.73140000000000005, 0.7681, 0.73399999999999999, 0.75680000000000003, 0.62470000000000003, 0.73529999999999995, 0.73740000000000006, 0.73080000000000001, 0.6603, 0.70899999999999996, 0.69040000000000001, 0.59199999999999997, 0.56830000000000003]
        r1_750 = [1.6220000000000001, 1.706, 1.73, 1.665, 1.627, 1.768, 1.706, 1.7030000000000001, 1.7649999999999999, 1.8129999999999999, 1.675, 1.6339999999999999, 1.845, 1.7829999999999999, 1.764, 1.7470000000000001, 1.681, 1.647, 1.6850000000000001, 1.667, 1.7010000000000001, 1.6850000000000001]
        r2_750 = [6.2619999999999996, 6.5359999999999996, 5.8959999999999999, 6.6840000000000002, 6.8819999999999997, 6.7569999999999997, 6.5620000000000003, 7.0030000000000001, 6.9740000000000002, 6.649, 6.9829999999999997, 7.2309999999999999, 6.4429999999999996, 6.6840000000000002, 6.8070000000000004, 6.4850000000000003, 6.9400000000000004, 6.944, 6.4640000000000004, 6.4889999999999999, 6.9009999999999998, 6.9539999999999997]
        noe_750 = [0.61909999999999998, 0.65890000000000004, 0.72009999999999996, 0.71009999999999995, 0.75219999999999998, 0.80420000000000003, 0.70020000000000004, 0.81999999999999995, 0.81040000000000001, 0.83409999999999995, 0.81299999999999994, 0.81910000000000005, 0.7782, 0.74760000000000004, 0.8115, 0.7379, 0.81100000000000005, 0.78249999999999997, 0.75729999999999997, 0.78259999999999996, 0.75139999999999996, 0.65210000000000001]
        r1_500_err = [0.044999999999999998, 0.044999999999999998, 0.044499999999999998, 0.048000000000000001, 0.043999999999999997, 0.047, 0.0465, 0.048000000000000001, 0.045499999999999999, 0.048000000000000001, 0.047500000000000001, 0.045499999999999999, 0.048000000000000001, 0.0465, 0.044499999999999998, 0.047, 0.0465, 0.045499999999999999, 0.045499999999999999, 0.045999999999999999, 0.045499999999999999, 0.044499999999999998]
        r2_500_err = [0.107, 0.1075, 0.10249999999999999, 0.1135, 0.11899999999999999, 0.11650000000000001, 0.11600000000000001, 0.121, 0.1265, 0.11799999999999999, 0.123, 0.122, 0.1215, 0.1125, 0.17599999999999999, 0.11749999999999999, 0.11749999999999999, 0.123, 0.1145, 0.111, 0.1145, 0.108]
        noe_500_err = [0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003]
        r1_600_err = [0.037999999999999999, 0.040000000000000001, 0.040500000000000001, 0.0395, 0.0385, 0.041000000000000002, 0.040000000000000001, 0.040500000000000001, 0.040000000000000001, 0.042000000000000003, 0.041500000000000002, 0.039, 0.042000000000000003, 0.042000000000000003, 0.0395, 0.040500000000000001, 0.040000000000000001, 0.039, 0.0395, 0.040000000000000001, 0.040500000000000001, 0.039]
        r2_600_err = [0.1125, 0.11550000000000001, 0.108, 0.1235, 0.1265, 0.1275, 0.123, 0.125, 0.1285, 0.12, 0.128, 0.13350000000000001, 0.1225, 0.11899999999999999, 0.1265, 0.1195, 0.128, 0.129, 0.1225, 0.122, 0.1265, 0.1225]
        noe_600_err = [0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003]
        r1_750_err = [0.032500000000000001, 0.034000000000000002, 0.035000000000000003, 0.033500000000000002, 0.032500000000000001, 0.035499999999999997, 0.034000000000000002, 0.034000000000000002, 0.035499999999999997, 0.036499999999999998, 0.033500000000000002, 0.032500000000000001, 0.036999999999999998, 0.035499999999999997, 0.035499999999999997, 0.035000000000000003, 0.033500000000000002, 0.033000000000000002, 0.034000000000000002, 0.033000000000000002, 0.034000000000000002, 0.033500000000000002]
        r2_750_err = [0.1255, 0.1305, 0.11799999999999999, 0.13400000000000001, 0.13800000000000001, 0.13550000000000001, 0.13150000000000001, 0.14050000000000001, 0.13950000000000001, 0.13300000000000001, 0.14000000000000001, 0.14449999999999999, 0.129, 0.13400000000000001, 0.13600000000000001, 0.1295, 0.13850000000000001, 0.13900000000000001, 0.1295, 0.13, 0.13800000000000001, 0.13900000000000001]
        noe_750_err = [0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003]

        # Misc tests.
        self.assertEqual(cdp.pipe_type, 'mf')
        self.assertEqual(cdp.hybrid_pipes, [])

        # Diffusion tensor tests.
        self.assertEqual(cdp.diff_tensor.type, 'sphere')
        self.assertEqual(cdp.diff_tensor.tm, 6.2029050826362826e-09)

        # Global minimisation statistic tests.
        self.assertEqual(cdp.chi2, 88.0888600975)
        self.assertEqual(cdp.iter, 1)
        self.assertEqual(cdp.f_count, 20)
        self.assertEqual(cdp.g_count, 2)
        self.assertEqual(cdp.h_count, 1)
        self.assertEqual(cdp.warning, None)

        # Global relaxation data tests.
        self.assertEqual(cdp.ri_labels, ['R1','R2','NOE','R1','R2','NOE','R1','R2','NOE'])
        self.assertEqual(cdp.remap_table, [0,0,0,1,1,1,2,2,2])
        self.assertEqual(cdp.frq_labels, ['500','600','750'])
        self.assertEqual(cdp.frq, [500000000.0,600000000.0,750000000.0])
        self.assertEqual(cdp.noe_r1_table, [None, None, 0, None, None, 3, None, None, 6])
        self.assertEqual(cdp.num_frq, 3)
        self.assertEqual(cdp.num_ri, 9)

        # Loop over the residues of the original data.
        j = 0
        for i in xrange(len(cdp.mol[0].res)):
            # Aliases
            res = cdp.mol[0].res[i]
            spin = cdp.mol[0].res[i].spin[0]

            # Debugging print out.
            print res
            print spin

            # Spin info tests.
            self.assertEqual(res.num, num[i])
            self.assertEqual(res.name, 'XXX')
            self.assertEqual(spin.num, None)
            self.assertEqual(spin.name, None)
            self.assertEqual(spin.select, select[i])
            self.assertEqual(spin.fixed, False)

            # Skip deselected spins.
            if not select[i]:
                continue

            # Structural info.
            self.assertEqual(spin.heteronuc_type, '15N')
            self.assertEqual(spin.proton_type, '1H')
            self.assertEqual(spin.attached_proton, None)
            self.assertEqual(spin.nucleus, None)

            # Model-free tests.
            self.assertEqual(spin.model, model[j])
            self.assertEqual(spin.equation, 'mf_ext')
            self.assertEqual(spin.params, params[j])
            self.assertEqual(spin.s2, s2[j])
            self.assertEqual(spin.s2f, s2f[j])
            self.assertEqual(spin.s2s, s2s[j])
            self.assertEqual(spin.local_tm, None)
            self.assertEqual(spin.te, None)
            if tf[j] != None:
                tf[j] = tf[j]*1e-12
            self.assertEqual(spin.tf, tf[j])
            self.assertEqual(spin.ts, ts[j]*1e-12)
            if rex[j] != None:
                rex[j] = rex[j]/(2.0*pi*500000000.0)**2
            self.assertEqual(spin.rex, rex[j])
            self.assertEqual(spin.r, 1.0200000000000001e-10)
            self.assertEqual(spin.csa, -0.00016999999999999999)

            # Minimisation statistic tests.
            self.assertEqual(spin.chi2, None)
            self.assertEqual(spin.iter, None)
            self.assertEqual(spin.f_count, None)
            self.assertEqual(spin.g_count, None)
            self.assertEqual(spin.h_count, None)
            self.assertEqual(spin.warning, None)

            # Relaxation data tests.
            self.assertEqual(spin.ri_labels, ['R1','R2','NOE','R1','R2','NOE','R1','R2','NOE'])
            self.assertEqual(spin.remap_table, [0,0,0,1,1,1,2,2,2])
            self.assertEqual(spin.frq_labels, ['500','600','750'])
            self.assertEqual(spin.frq, [500000000.0,600000000.0,750000000.0])
            self.assertEqual(spin.noe_r1_table, [None, None, 0, None, None, 3, None, None, 6])
            self.assertEqual(spin.num_frq, 3)
            self.assertEqual(spin.num_ri, 9)
            self.assertEqual(spin.relax_data, [r1_500[j], r2_500[j], noe_500[j], r1_600[j], r2_600[j], noe_600[j], r1_750[j], r2_750[j], noe_750[j]])
            self.assertEqual(spin.relax_error, [r1_500_err[j], r2_500_err[j], noe_500_err[j], r1_600_err[j], r2_600_err[j], noe_600_err[j], r1_750_err[j], r2_750_err[j], noe_750_err[j]])

            # Secondary index.
            j = j + 1


    def test_select_m4(self):
        """Selecting model m4 with parameters {S2, te, Rex} using model_free.select_model()."""

        # Path of the files.
        path = sys.path[-1] + '/test_suite/shared_data/model_free/S2_0.970_te_2048_Rex_0.149'

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
        path = sys.path[-1] + '/test_suite/shared_data/model_free/S2_0.970_te_2048_Rex_0.149'

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
        path = sys.path[-1] + '/test_suite/shared_data/model_free/S2_0.970_te_2048_Rex_0.149'

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
        path = sys.path[-1] + '/test_suite/shared_data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='noe.500.out', dir=path)

        # Set the CSA value and bond length simultaneously.
        self.relax.interpreter._Value.set([N15_CSA, NH_BOND_LENGTH], ['csa', 'bond_length'])

        # Alias the current data pipe.
        cdp = ds[ds.current_pipe]

        # Test the values.
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, N15_CSA)
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, NH_BOND_LENGTH)


    def test_write_results(self):
        """Writing of model-free results using the user function results.write()."""

        # Path of the files.
        path = sys.path[-1] + '/test_suite/shared_data/model_free/OMP'

        # Read the results file.
        self.relax.interpreter._Results.read(file='final_results_trunc_1.2', dir=path)

        # A dummy file object for catching the results.write() output.
        file = DummyFileObject()

        # Write the results file into a dummy file.
        self.relax.interpreter._Results.write(file=file, dir=path)

        # Now, get the contents of that file, and then 'close' that file.
        lines_test = file.readlines()
        file.close()

        # Read the 1.3 results file, extract the data, then close it again.
        file = open_read_file(file_name='final_results_trunc_1.3', dir=path)
        lines_true = file.readlines()
        file.close()

        # Test the rest of the lines.
        for i in xrange(len(lines_test)):
            # Skip the second line, as it contains the date and hence should not be the same.
            # Also skip the third line, as the pipe names are different.
            if i == 1 or i == 2:
                continue

            # Test that the line is the same.
            self.assertEqual(lines_test[i], lines_true[i])


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
