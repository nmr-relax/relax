###############################################################################
#                                                                             #
# Copyright (C) 2006-2012 Edward d'Auvergne                                   #
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
from os import sep
from re import search
from shutil import copytree
from tempfile import mkdtemp

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
import dep_check
from generic_fns import pipes
from generic_fns.mol_res_spin import spin_loop
from physical_constants import N15_CSA, NH_BOND_LENGTH
from relax_io import DummyFileObject, open_read_file
from status import Status; status = Status()


# Get the platform/version information.
SYSTEM = platform.system()
RELEASE = platform.release()
VERSION = platform.version()
WIN32_VER = platform.win32_ver()
DIST = platform.dist()
ARCH = platform.architecture()
MACH = platform.machine()
PROC = platform.processor()
PY_VER = platform.python_version()
NUMPY_VER = numpy.__version__
LIBC_VER = platform.libc_ver()

# Windows system name pain.
if SYSTEM == 'Windows' or SYSTEM == 'Microsoft':
    # Set the system to 'Windows' no matter what.
    SYSTEM = 'Windows'



class Mf(SystemTestCase):
    """TestCase class for the functional tests of model-free analysis."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')


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
        string = string + "%-18s%-25s\n" % ("System: ", SYSTEM)
        string = string + "%-18s%-25s\n" % ("Release: ", RELEASE)
        string = string + "%-18s%-25s\n" % ("Version: ", VERSION)
        string = string + "%-18s%-25s\n" % ("Win32 version: ", (WIN32_VER[0] + " " + WIN32_VER[1] + " " + WIN32_VER[2] + " " + WIN32_VER[3]))
        string = string + "%-18s%-25s\n" % ("Distribution: ", (DIST[0] + " " + DIST[1] + " " + DIST[2]))
        string = string + "%-18s%-25s\n" % ("Architecture: ", (ARCH[0] + " " + ARCH[1]))
        string = string + "%-18s%-25s\n" % ("Machine: ", MACH)
        string = string + "%-18s%-25s\n" % ("Processor: ", PROC)
        string = string + "%-18s%-25s\n" % ("Python version: ", PY_VER)
        string = string + "%-18s%-25s\n" % ("Numpy version: ", NUMPY_VER)
        string = string + "%-18s%-25s\n" % ("Libc version: ", (LIBC_VER[0] + " " + LIBC_VER[1]))


        # Minimisation info.
        string = string + '\n'
        if spin.local_tm != None:
            string = string + "%-15s %30.16g\n" % ('local_tm (ns):',    spin.local_tm * 1e9)
        if spin.s2 != None:
            string = string + "%-15s %30.16g\n" % ('s2:',               spin.s2)
        if spin.s2f != None:
            string = string + "%-15s %30.16g\n" % ('s2f:',              spin.s2f)
        if spin.s2s != None:
            string = string + "%-15s %30.16g\n" % ('s2s:',              spin.s2s)
        if spin.te != None:
            string = string + "%-15s %30.13g\n" % ('te (ps):',          spin.te * 1e12)
        if spin.tf != None:
            string = string + "%-15s %30.13g\n" % ('tf (ps):',          spin.tf * 1e12)
        if spin.ts != None:
            string = string + "%-15s %30.13g\n" % ('ts (ps):',          spin.ts * 1e12)
        if spin.rex != None:
            string = string + "%-15s %30.17g\n" % ('rex:',      spin.rex * (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2)
        string = string +   "%-15s %30.17g\n" % ('chi2:',   spin.chi2)
        string = string +   "%-15s %30i\n"   % ('iter:',    spin.iter)
        string = string +   "%-15s %30i\n"   % ('f_count:', spin.f_count)
        string = string +   "%-15s %30i\n"   % ('g_count:', spin.g_count)
        string = string +   "%-15s %30i\n"   % ('h_count:', spin.h_count)
        string = string +   "%-15s %30s\n"   % ('warning:', spin.warning)

        # Return the string.
        return string


    def monte_carlo(self):
        """Run Monte Carlo simulations for the optimised model-free model."""

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=3)
        self.interpreter.monte_carlo.create_data()
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise('newton')
        #self.interpreter.eliminate()
        self.interpreter.monte_carlo.error_analysis()


    def object_comparison(self, obj1=None, obj2=None, skip=None):
        """Check if the contents of 2 objects are the same."""

        # The names are the same.
        self.assertEqual(dir(obj1), dir(obj2))

        # Loop over the objects in the base objects.
        for name in dir(obj1):
            # Skip special objects.
            if skip and name in skip:
                continue

            # Skip objects starting with '_'.
            if search('^_', name):
                continue

            # Skip original class methods.
            if name in list(obj1.__class__.__dict__.keys()):
                continue

            # Print out.
            print(("\t" + name))

            # Get the sub-objects.
            sub_obj1 = getattr(obj1, name)
            sub_obj2 = getattr(obj2, name)

            # Check that they are of the same type.
            self.assertEqual(type(sub_obj1), type(sub_obj2))

            # Check that they are equal (converting to strings to avoid comparison nastiness).
            self.assertEqual(str(sub_obj1), str(sub_obj2))


    def test_bug_14872_unicode_selection(self):
        """Test catching bug #14872, the unicode string selection failure as submitted by Olivier Serve."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'bug_14872_unicode_selection.py')


    def test_bug_14941_local_tm_global_selection(self):
        """Test catching bug #14941, the local tm global model selection problem as submitted by Mikaela Stewart (mikaela dot stewart att gmail dot com)."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'bug_14941_local_tm_global_selection.py')


    def test_bug_15050(self):
        """Test catching bug #15050, 'PipeContainer' object has no attribute 'diff_tensor' error as submitted by Tiago Pais (https://gna.org/users/tpais)."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'bug_15050.py')


    def test_bugs_12582_12591_12607(self):
        """Test catching bugs #12582, #12591 and #12607 as submitted by Chris Brosey."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'bugs_12582_12591_12607.py')

        # Test for bug #12607 (S2 changes because it is in the grid search when it should not be).
        self.assertNotEqual(cdp.mol[0].res[1].spin[0].s2, 1.0)


    def test_bug_18790(self):
        """Test catching bug #18790, the negative relaxation data RelaxError reported by Vitaly Vostrikov."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'bug_18790_negative_error.py')


    def test_create_m4(self):
        """Creating model m4 with parameters {S2, te, Rex} using model_free.create_model()."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'create_m4.py')

        # Test the model.
        self.assertEqual(cdp.mol[0].res[1].spin[0].model, 'm4')
        self.assertEqual(cdp.mol[0].res[1].spin[0].params, ['s2', 'te', 'rex'])


    def test_dauvergne_protocol(self):
        """Check the execution of auto_analyses.dauvergne_protocol."""

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'dauvergne_protocol.py')

        # Check the diffusion tensor.
        self.assertEqual(cdp.diff_tensor.type, 'sphere')
        self.assertAlmostEqual(cdp.diff_tensor.tm, 1e-8)
        self.assertEqual(cdp.diff_tensor.fixed, True)

        # The global minimisation info.
        self.assertAlmostEqual(cdp.chi2, 4e-19)

        # The spin ID info.
        mol_names = ["sphere_mol1"] * 9
        res_names = ["GLY"] * 9
        res_nums = range(1, 10)
        spin_names = ["N"] * 9
        spin_nums = numpy.array(range(9)) * 2 + 1

        # Check the spin data.
        i = 0
        for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
            # The ID info.
            self.assertEqual(mol_name, mol_names[i])
            self.assertEqual(res_name, res_names[i])
            self.assertEqual(res_num,  res_nums[i])
            self.assertEqual(spin.name, spin_names[i])
            self.assertEqual(spin.num,  spin_nums[i])

            # The data.
            self.assertEqual(spin.select, True)
            self.assertEqual(spin.fixed, False)
            self.assertEqual(spin.proton_type, '1H')
            self.assertEqual(spin.heteronuc_type, '15N')
            self.assertEqual(spin.attached_proton, None)
            self.assertEqual(spin.nucleus, None)
            self.assertAlmostEqual(spin.r, 1.02 * 1e-10)
            self.assertAlmostEqual(spin.csa, -172e-6)

            # The model-free data.
            self.assertEqual(spin.model, 'm2')
            self.assertEqual(spin.equation, 'mf_orig')
            self.assertEqual(len(spin.params), 2)
            self.assertEqual(spin.params[0], 's2')
            self.assertEqual(spin.params[1], 'te')
            self.assertAlmostEqual(spin.s2, 0.8)
            self.assertEqual(spin.s2f, None)
            self.assertEqual(spin.s2s, None)
            self.assertEqual(spin.local_tm, None)
            self.assertAlmostEqual(spin.te, 20e-12)
            self.assertEqual(spin.tf, None)
            self.assertEqual(spin.ts, None)
            self.assertEqual(spin.rex, None)

            # The spin minimisation info.
            self.assertEqual(spin.chi2, None)
            self.assertEqual(spin.iter, None)
            self.assertEqual(spin.f_count, None)
            self.assertEqual(spin.g_count, None)
            self.assertEqual(spin.h_count, None)
            self.assertEqual(spin.warning, None)

            # Increment the index.
            i += 1


    def test_generate_ri(self):
        """Back-calculate relaxation data."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'generate_ri.py')


    def test_latex_table(self):
        """Test the creation of a LaTeX table of model-free results, mimicking the latex_mf_table.py sample script."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'latex_mf_table.py')


    def test_local_tm_10_S2_0_8_te_40(self):
        """Test the optimisation of the test set {tm=10, S2=0.8, te=40}."""

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_setup_local_tm_10_S2_0_8_te_40.py')

        # The proton frequencies in MHz.
        frq = ['400', '500', '600', '700', '800', '900', '1000']

        # Load the relaxation data.
        for i in range(len(frq)):
            self.interpreter.relax_data.read('NOE_%s'%frq[i], 'NOE', float(frq[i])*1e6, 'noe.%s.out' % frq[i], dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
            self.interpreter.relax_data.read('R1_%s'%frq[i],  'R1',  float(frq[i])*1e6, 'r1.%s.out' % frq[i],  dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
            self.interpreter.relax_data.read('R2_%s'%frq[i],  'R2',  float(frq[i])*1e6, 'r2.%s.out' % frq[i],  dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.interpreter.value.set([15.0e-9, 1.0, 0.0], ['local_tm', 's2', 'te'])

        # Minimise.
        self.interpreter.minimise('newton', 'gmw', 'back')

        # Alias the relevent spin container.
        spin = cdp.mol[0].res[0].spin[0]

        # Check the values.
        self.value_test(spin, local_tm=10, s2=0.8, te=40, chi2=0.0)


    def test_local_tm_10_S2_0_8_te_40_test2(self):
        """Test the optimisation of the test set {tm=10, S2=0.8, te=40}."""

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_setup_local_tm_10_S2_0_8_te_40.py')

        # The proton frequencies in MHz.
        frq = ['400', '500', '600', '700', '800', '900', '1000']

        # Load the relaxation data.
        for i in range(len(frq)):
            self.interpreter.relax_data.read('NOE_%s'%frq[i], 'NOE', float(frq[i])*1e6, 'noe.%s.out' % frq[i], dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
            self.interpreter.relax_data.read('R1_%s'%frq[i],  'R1',  float(frq[i])*1e6, 'r1.%s.out' % frq[i],  dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
            self.interpreter.relax_data.read('R2_%s'%frq[i],  'R2',  float(frq[i])*1e6, 'r2.%s.out' % frq[i],  dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.interpreter.value.set([15.0e-9, 1.0, 0.0], ['local_tm', 's2', 'te'])

        # Minimise.
        self.interpreter.minimise('newton', 'gmw', 'back')

        # Alias the relevent spin container.
        spin = cdp.mol[0].res[0].spin[0]

        # Check the values.
        self.value_test(spin, local_tm=10, s2=0.8, te=40, chi2=0.0)


    def test_local_tm_10_S2_0_8_te_40_test3(self):
        """Test the optimisation of the test set {tm=10, S2=0.8, te=40}."""

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_setup_local_tm_10_S2_0_8_te_40.py')

        # Load the relaxation data.
        self.interpreter.relax_data.read('R2_700',  'R2',  700*1e6, 'r2.700.out',  dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('NOE_500', 'NOE', 500*1e6, 'noe.500.out', dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('R1_500',  'R1',  500*1e6, 'r1.500.out',  dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('R1_900',  'R1',  900*1e6, 'r1.900.out',  dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('NOE_900', 'NOE', 900*1e6, 'noe.900.out', dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('R2_900',  'R2',  900*1e6, 'r2.900.out',  dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('R1_700',  'R1',  700*1e6, 'r1.700.out',  dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('NOE_700', 'NOE', 700*1e6, 'noe.700.out', dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('R2_500',  'R2',  500*1e6, 'r2.500.out',  dir=cdp.path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.interpreter.value.set([15.0e-9, 1.0, 0.0], ['local_tm', 's2', 'te'])

        # Minimise.
        self.interpreter.minimise('newton', 'gmw', 'back')

        # Alias the relevent spin container.
        spin = cdp.mol[0].res[0].spin[0]

        # Check the values.
        self.value_test(spin, local_tm=10, s2=0.8, te=40, chi2=0.0)


    def test_m0_grid(self):
        """Test the optimisation of the m0 model-free model against the tm0 parameter grid."""

        # Initialise.
        cdp._model = 'm0'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm0_grid.py')


    def test_m0_grid_vs_m1(self):
        """Test the optimisation of the m1 model-free model against the tm0 parameter grid."""

        # Initialise.
        cdp._model = 'm1'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm0_grid.py')


    def test_m0_grid_vs_m2(self):
        """Test the optimisation of the m2 model-free model against the tm0 parameter grid."""

        # Initialise.
        cdp._model = 'm2'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm0_grid.py')


    def test_m0_grid_vs_m3(self):
        """Test the optimisation of the m3 model-free model against the tm0 parameter grid."""

        # Initialise.
        cdp._model = 'm3'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm0_grid.py')


    def test_m0_grid_vs_m4(self):
        """Test the optimisation of the m4 model-free model against the tm0 parameter grid."""

        # Initialise.
        cdp._model = 'm4'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm0_grid.py')


    def test_m1_grid(self):
        """Test the optimisation of the m1 model-free model against the tm1 parameter grid."""

        # Initialise.
        cdp._model = 'm1'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm1_grid.py')


    def test_m2_grid(self):
        """Test the optimisation of the m2 model-free model against the tm2 parameter grid."""

        # Initialise.
        cdp._model = 'm2'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm2_grid.py')


    def test_m2_grid_vs_m4(self):
        """Test the optimisation of the m4 model-free model against the tm2 parameter grid."""

        # Initialise.
        cdp._model = 'm4'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm2_grid.py')


    def test_m3_grid(self):
        """Test the optimisation of the m3 model-free model against the tm3 parameter grid."""

        # Initialise.
        cdp._model = 'm3'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm3_grid.py')


    def test_m4_grid(self):
        """Test the optimisation of the m4 model-free model against the tm4 parameter grid."""

        # Initialise.
        cdp._model = 'm4'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm4_grid.py')


    def test_m5_grid(self):
        """Test the optimisation of the m5 model-free model against the tm5 parameter grid."""

        # Initialise.
        cdp._model = 'm5'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm5_grid.py')


    def test_m6_grid(self):
        """Test the optimisation of the m6 model-free model against the tm6 parameter grid."""

        # Initialise.
        cdp._model = 'm6'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm6_grid.py')


    def test_m7_grid(self):
        """Test the optimisation of the m7 model-free model against the tm7 parameter grid."""

        # Initialise.
        cdp._model = 'm7'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm7_grid.py')


    def test_m8_grid(self):
        """Test the optimisation of the m8 model-free model against the tm8 parameter grid."""

        # Initialise.
        cdp._model = 'm8'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm8_grid.py')


    def test_m9_grid(self):
        """Test the optimisation of the m9 model-free model against the tm9 parameter grid."""

        # Initialise.
        cdp._model = 'm9'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm9_grid.py')


    def test_omp_analysis(self):
        """Try a very minimal model-free analysis on the OMP relaxation data."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'omp_model_free.py')

        # Alias the final data pipe.
        dp = pipes.get_pipe('final')

        # Some checks.
        self.assertEqual(dp.mol[0].res[0].spin[0].select_sim, [True, False, True])
        self.assertEqual(dp.mol[0].res[1].spin[0].select_sim, [True, True, False])
        self.assertEqual(dp.mol[0].res[2].spin[0].select_sim, [True, True, True])
        self.assert_(not hasattr(dp.mol[0].res[3].spin[0], 'select_sim'))


    def test_opendx_s2_te_rex(self):
        """Mapping the {S2, te, Rex} chi2 space through the OpenDX user function dx.map()."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opendx_s2_te_rex.py')


    def test_opendx_theta_phi_da(self):
        """Mapping the {theta, phi, Da} chi2 space through the OpenDX user function dx.map()."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

        # Read the PDF file and set the vectors.
        self.interpreter.structure.read_pdb(file='pdb', dir=path, read_model=1)
        self.interpreter.structure.load_spins('@N')
        self.interpreter.structure.vectors(attached='H')

        # Read the relaxation data.
        self.interpreter.relax_data.read('R1_600',  'R1',  600.0*1e6, 'r1.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('R2_600',  'R2',  600.0*1e6, 'r2.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('NOE_600', 'NOE', 600.0*1e6, 'noe.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('R1_500',  'R1',  500.0*1e6, 'r1.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('R2_500',  'R2',  500.0*1e6, 'r2.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('NOE_500', 'NOE', 500.0*1e6, 'noe.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)

        # Setup other values.
        self.interpreter.diffusion_tensor.init((1.601 * 1e7, 1.34, 72.4, 90-77.9), param_types=4)
        self.interpreter.value.set([N15_CSA, NH_BOND_LENGTH], ['csa', 'r'])
        self.interpreter.value.set([0.8, 50 * 1e-12, 0.0], ['s2', 'te', 'rex'])
        self.interpreter.value.set('15N', 'heteronuc_type')
        self.interpreter.value.set('1H', 'proton_type')

        # Select the model.
        self.interpreter.model_free.select_model(model='m4')

        # Map the space.
        self.interpreter.dx.map(params=['theta', 'phi', 'Da'], spin_id=':2', inc=2, lower=[0, 0, -0.5*1e7], upper=[pi, 2.0*pi, 1.0*1e7], file_prefix='devnull')


    def test_opendx_tm_s2_te(self):
        """Mapping the {local_tm, S2, te} chi2 space through the OpenDX user function dx.map()."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.interpreter.sequence.read(file='noe.500.out', dir=path, res_num_col=1, res_name_col=2)

        # Read the relaxation data.
        self.interpreter.relax_data.read('R1_600',  'R1',  600.0*1e6, 'r1.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('R2_600',  'R2',  600.0*1e6, 'r2.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('NOE_600', 'NOE', 600.0*1e6, 'noe.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('R1_500',  'R1',  500.0*1e6, 'r1.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('R2_500',  'R2',  500.0*1e6, 'r2.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)
        self.interpreter.relax_data.read('NOE_500', 'NOE', 500.0*1e6, 'noe.500.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)

        # Setup other values.
        self.interpreter.value.set([N15_CSA, NH_BOND_LENGTH], ['csa', 'r'])
        self.interpreter.value.set('15N', 'heteronuc_type')
        self.interpreter.value.set('1H', 'proton_type')

        # Select the model.
        self.interpreter.model_free.select_model(model='tm2')

        # Map the space.
        self.interpreter.dx.map(params=['local_tm', 's2', 'te'], spin_id=':2', inc=2, lower=[5e-9, 0.0, 0.0], file_prefix='devnull')


    def test_opt_constr_bfgs_back_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained BFGS opt, backtracking line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            - BFGS optimisation.
            - Backtracking line search.
            - Constrained.

        The true data set is:
            - S2  = 0.970
            - te  = 2048 ps
            - Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.interpreter.value.set([1.0, 0.0, 0.0], ['s2', 'te', 'rex'])

        # Minimise.
        self.interpreter.minimise('bfgs', 'back')

        # Alias the relevent spin container.
        spin = cdp.mol[0].res[1].spin[0]

        # Optimisation differences.
        ###########################

        # 32-bit Linux.
        # iter: 203
        # f_count: 955
        # g_count: 209

        # 32-bit i686 Linux (https://mail.gna.org/public/relax-devel/2009-05/msg00003.html).
        # System: Linux
        # Release: 2.6.28-gentoo-r5
        # Version: #1 SMP Sat Apr 25 13:31:51 EDT 2009
        # Win32 version:
        # Distribution:
        # Architecture: 32bit ELF
        # Machine: i686
        # Processor: Intel(R) Pentium(R) M processor 1.80GHz
        # Python version: 2.5.4
        # numpy version: 1.2.1
        # 
        # s2:       0.9700000000012307
        # te:       2048.0000002299716
        # rex:      0.14899999997647859
        # chi2:     1.9223825944220359e-20
        # iter:     157
        # f_count:  722
        # g_count:  164
        # h_count:  0
        # warning:  None

        # 32-bit i686 Linux.
        # System:           Linux                    
        # Release:          2.6.33.7-desktop-2mnb    
        # Version:          #1 SMP Mon Sep 20 19:00:25 UTC 2010
        # Win32 version:                             
        # Distribution:     mandrake 2010.2 Official 
        # Architecture:     32bit ELF                
        # Machine:          i686                     
        # Processor:        i686                     
        # Python version:   2.6.5                    
        # Numpy version:    1.4.1                    
        # Libc version:     glibc 2.0                
        # 
        # s2:                         0.9700000000016741
        # te (ps):                        2048.000000312
        # rex:                       0.14899999996808433
        # chi2:                   3.5466670276032307e-20
        # iter:                                      158
        # f_count:                                   744
        # g_count:                                   165
        # h_count:                                     0
        # warning:                                  None

        # 32-bit i686 Linux.
        # System:           Linux                    
        # Release:          2.6.33.7-desktop-2mnb    
        # Version:          #1 SMP Mon Sep 20 19:00:25 UTC 2010
        # Win32 version:                             
        # Distribution:     mandrake 2010.2 Official 
        # Architecture:     32bit ELF                
        # Machine:          i686                     
        # Processor:        i686                     
        # Python version:   2.6.5                    
        # Numpy version:    1.4.1                    
        # Libc version:     glibc 2.0                
        # 
        # s2:                         0.9700000000016741
        # te:                             2048.000000312
        # rex:                       0.14899999996808433
        # chi2:                   3.5466670276032307e-20
        # iter:                                      158
        # f_count:                                   744
        # g_count:                                   165
        # h_count:                                     0
        # warning:                                  None

        # 32-bit i686 Linux (https://mail.gna.org/public/relax-users/2011-01/msg00029.html).
        # System:           Linux
        # Release:          2.6.28-17-generic
        # Version:          #58-Ubuntu SMP Tue Dec 1 18:57:07 UTC 2009
        # Win32 version:
        # Distribution:     Ubuntu 9.04 jaunty
        # Architecture:     32bit ELF
        # Machine:          i686
        # Processor:
        # Python version:   2.6.2
        # Numpy version:    1.2.1
        # Libc version:     glibc 2.4
        # 
        # s2:                          0.970000000000951
        # te (ps):                        2048.000000178
        # rex:                       0.14899999998189395
        # chi2:                   1.1498599057727952e-20
        # iter:                                      154
        # f_count:                                   598
        # g_count:                                   161
        # h_count:                                     0
        # warning:                                  None

        # 64-bit x86_64 Linux.
        # System:           Linux
        # Release:          2.6.24.7-server-2mnb
        # Version:          #1 SMP Thu Oct 30 14:50:37 EDT 2008
        # Win32 version:
        # Distribution:     mandriva 2008.1 Official
        # Architecture:     64bit ELF
        # Machine:          x86_64
        # Processor:        Intel(R) Core(TM)2 Duo CPU     E8400  @ 3.00GHz
        # Python version:   2.5.2
        # Numpy version:    1.2.0
        # Libc version:     glibc 2.2.5
        # 
        # s2:                         0.9699999999999785
        # te:                         2047.9999999962433
        # rex:                       0.14900000000039709
        # chi2:                   5.2479491342506911e-24
        # iter:                                      162
        # f_count:                                   758
        # g_count:                                   169
        # h_count:                                     0
        # warning:                                  None

        # 32-bit Windows.
        # iter: 156
        # f_count: 701
        # g_count: 163

        # 32-bit powerpc Darwin (http://gna.org/bugs/?12573, https://mail.gna.org/public/relax-users/2008-10/msg00089.html).
        # System: Darwin
        # Release: 9.5.0
        # Version: Darwin Kernel Version 9.5.0: Wed Sep  3 11:31:44 PDT 2008; root:xnu-1228.7.58~1/RELEASE_PPC
        # Win32 version:
        # Distribution:
        # Architecture: 32bit
        # Machine: Power Macintosh
        # Processor: powerpc
        # Python version: 2.5.2
        # numpy version: 1.1.1
        # 
        # s2:       0.9699999999999861
        # te:       2047.9999999978033
        # rex:      0.14900000000028032
        # chi2:     1.8533903598853284e-24
        # iter:     156
        # f_count:  695
        # g_count:  162
        # h_count:  0
        # warning:  None

        # 32-bit i386 Darwin (http://gna.org/bugs/?14173).
        # System: Darwin
        # Release: 9.8.0
        # Version: Darwin Kernel Version 9.8.0: Wed Jul 15 16:55:01 PDT 2009; root:xnu-1228.15.4~1/RELEASE_I386
        # Win32 version:
        # Distribution:
        # Architecture: 32bit
        # Machine: i386
        # Processor: i386
        # Python version: 2.6.2
        # numpy version: 1.3.0
        # 
        # s2: 0.9700000000009170
        # te: 2048.0000001751678
        # rex: 0.14899999998256069
        # chi2: 1.1151721805269898e-20
        # iter: 175
        # f_count: 735
        # g_count: 182
        # h_count: 0
        # warning: None 

        # 64-bit i386 Darwin (http://gna.org/bugs/?14173).
        # System: Darwin
        # Release: 9.8.0
        # Version: Darwin Kernel Version 9.8.0: Wed Jul 15 16:55:01 PDT 2009; root:xnu-1228.15.4~1/RELEASE_I386
        # Win32 version:
        # Distribution:
        # Architecture: 64bit
        # Machine: i386
        # Processor: i386
        # Python version: 2.6.2
        # numpy version: 1.3.0
        # 
        # s2: 0.9699999999999785
        # te: 2047.9999999962433
        # rex: 0.14900000000039709
        # chi2: 5.2479491342506911e-24
        # iter: 162
        # f_count: 758
        # g_count: 169
        # h_count: 0
        # warning: None

        # Optimisation values.
        select = True
        s2 = 0.9699999999999995
        te = 2048.000000000022283
        rex = 0.14900000000000566 / (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2
        chi2 = 3.1024517431117421e-27
        iter = [154, 156, 157, 158, 162, 175, 203]
        f_count = [598, 695, 701, 722, 735, 744, 758, 955]
        g_count = [161, 162, 163, 164, 165, 169, 182, 209]
        h_count = 0
        warning = None

        # Test the values.
        self.assertEqual(cdp.mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select=select, s2=s2, te=te, rex=rex, chi2=chi2)


    def test_opt_constr_bfgs_mt_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained BFGS opt, More and Thuente line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            - BFGS optimisation.
            - More and Thuente line search.
            - Constrained.

        The true data set is:
            - S2  = 0.970
            - te  = 2048 ps
            - Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.interpreter.value.set([1.0, 0.0, 0.0], ['s2', 'te', 'rex'])

        # Minimise.
        self.interpreter.minimise('bfgs', 'mt')

        # Alias the relevent spin container.
        spin = cdp.mol[0].res[1].spin[0]

        # Optimisation differences.
        ###########################

        # 32-bit Linux.
        # f_count: 388
        # g_count: 388

        # 32-bit i686 Linux (https://mail.gna.org/public/relax-devel/2009-05/msg00003.html).
        # System: Linux
        # Release: 2.6.28-gentoo-r5
        # Version: #1 SMP Sat Apr 25 13:31:51 EDT 2009
        # Win32 version:
        # Distribution:
        # Architecture: 32bit ELF
        # Machine: i686
        # Processor: Intel(R) Pentium(R) M processor 1.80GHz
        # Python version: 2.5.4
        # numpy version: 1.2.1
        # 
        # s2:       0.9700000000000604
        # te:       2048.0000000114946
        # rex:      0.14899999999885985
        # chi2:     4.762657780645096e-23
        # iter:     120
        # f_count:  386
        # g_count:  386
        # h_count:  0
        # warning:  None

        # 32-bit i686 Linux (https://mail.gna.org/public/relax-users/2011-01/msg00029.html).
        # System:           Linux
        # Release:          2.6.28-17-generic
        # Version:          #58-Ubuntu SMP Tue Dec 1 18:57:07 UTC 2009
        # Win32 version:
        # Distribution:     Ubuntu 9.04 jaunty
        # Architecture:     32bit ELF
        # Machine:          i686
        # Processor:
        # Python version:   2.6.2
        # Numpy version:    1.2.1
        # Libc version:     glibc 2.4
        # 
        # s2:                         0.9700000000000614
        # te (ps):                        2048.000000012
        # rex:                       0.14899999999883881
        # chi2:                   4.9272178768519757e-23
        # iter:                                      120
        # f_count:                                   381
        # g_count:                                   381
        # h_count:                                     0
        # warning:                                  None

        # 64-bit x86_64 Linux.
        # System:           Linux
        # Release:          2.6.24.7-server-2mnb
        # Version:          #1 SMP Thu Oct 30 14:50:37 EDT 2008
        # Win32 version:
        # Distribution:     mandriva 2008.1 Official
        # Architecture:     64bit ELF
        # Machine:          x86_64
        # Processor:        Intel(R) Core(TM)2 Duo CPU     E8400  @ 3.00GHz
        # Python version:   2.5.2
        # Numpy version:    1.2.0
        # Libc version:     glibc 2.2.5
        # 
        # s2:                         0.9700000000000603
        # te:                         2048.0000000114601
        # rex:                       0.14899999999886163
        # chi2:                   4.7289676642197204e-23
        # iter:                                      120
        # f_count:                                   384
        # g_count:                                   384
        # h_count:                                     0
        # warning:                                  None

        # 32-bit powerpc Darwin (http://gna.org/bugs/?12573, https://mail.gna.org/public/relax-users/2008-10/msg00089.html).
        # System: Darwin
        # Release: 9.5.0
        # Version: Darwin Kernel Version 9.5.0: Wed Sep  3 11:31:44 PDT 2008; 
        # root:xnu-1228.7.58~1/RELEASE_PPC
        # Win32 version:
        # Distribution:
        # Architecture: 32bit
        # Machine: Power Macintosh
        # Processor: powerpc
        # Python version: 2.5.2
        # numpy version: 1.1.1
        # 
        # s2:       0.9700000000000607
        # te:       2048.0000000115510
        # rex:      0.14899999999885080
        # chi2:     4.8056261450870388e-23
        # iter:     120
        # f_count:  377
        # g_count:  377
        # h_count:  0
        # warning:  None

        # 32-bit i386 Darwin (http://gna.org/bugs/?14174).
        # System: Darwin
        # Release: 9.8.0
        # Version: Darwin Kernel Version 9.8.0: Wed Jul 15 16:55:01 PDT 2009; root:xnu-1228.15.4~1/RELEASE_I386
        # Win32 version:
        # Distribution:
        # Architecture: 32bit
        # Machine: i386
        # Processor: i386
        # Python version: 2.6.2
        # numpy version: 1.3.0
        # 
        # s2: 0.9700000000000604
        # te: 2048.0000000114997
        # rex: 0.14899999999886168
        # chi2: 4.7647467884964078e-23
        # iter: 120
        # f_count: 386
        # g_count: 386
        # h_count: 0
        # warning: None 

        # 64-bit i386 Darwin (http://gna.org/bugs/?14174).
        # System: Darwin
        # Release: 9.8.0
        # Version: Darwin Kernel Version 9.8.0: Wed Jul 15 16:55:01 PDT 2009; root:xnu-1228.15.4~1/RELEASE_I386
        # Win32 version:
        # Distribution:
        # Architecture: 64bit
        # Machine: i386
        # Processor: i386
        # Python version: 2.6.2
        # numpy version: 1.3.0
        # 
        # s2: 0.9700000000000603
        # te: 2048.0000000114601
        # rex: 0.14899999999886163
        # chi2: 4.7289676642197204e-23
        # iter: 120
        # f_count: 384
        # g_count: 384
        # h_count: 0
        # warning: None

        # Optimisation values.
        select = True
        s2 = 0.9700000000000580
        te = 2048.000000011044449
        rex = 0.148999999998904 / (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2
        chi2 = 4.3978813282102374e-23
        iter = 120
        f_count = [377, 381, 384, 386, 388]
        g_count = [377, 381, 384, 386, 388]
        h_count = 0
        warning = None

        # Test the values.
        self.assertEqual(cdp.mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select=select, s2=s2, te=te, rex=rex, chi2=chi2)


    def test_opt_constr_cd_back_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained coordinate descent opt, backtracking line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            - Coordinate descent optimisation.
            - Backtracking line search.
            - Constrained.

        The true data set is:
            - S2  = 0.970
            - te  = 2048 ps
            - Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.interpreter.value.set([1.0, 0.0, 0.0], ['s2', 'te', 'rex'])

        # Minimise.
        self.interpreter.minimise('cd', 'back', max_iter=50)

        # Alias the relevent spin container.
        spin = cdp.mol[0].res[1].spin[0]

        # Optimisation differences.
        ###########################

        # 64-bit x86_64 Linux.
        # System:           Linux
        # Release:          2.6.24.7-server-2mnb
        # Version:          #1 SMP Thu Oct 30 14:50:37 EDT 2008
        # Win32 version:
        # Distribution:     mandriva 2008.1 Official
        # Architecture:     64bit ELF
        # Machine:          x86_64
        # Processor:        Intel(R) Core(TM)2 Duo CPU     E8400  @ 3.00GHz
        # Python version:   2.5.2
        # Numpy version:    1.2.0
        # Libc version:     glibc 2.2.5
        # 
        # s2:                         0.9097900390625000
        # te:                           25.0000000000000
        # rex:                       1.24017333984375000
        # chi2:                       53.476155463267176
        # iter:                                       50
        # f_count:                                   131
        # g_count:                                    51
        # h_count:                                     0
        # warning:        Maximum number of iterations reached

        # Optimisation values.
        select = True
        s2 = 0.9097900390625
        te = 25.00000000000000
        rex = 1.24017333984375 / (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2
        chi2 = 53.476155463267176
        iter = 50
        f_count = 131
        g_count = 51
        h_count = 0
        warning = 'Maximum number of iterations reached'

        # Test the values.
        self.assertEqual(cdp.mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select=select, s2=s2, te=te, rex=rex, chi2=chi2)


    def test_opt_constr_cd_mt_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained coordinate descent opt, More and Thuente line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            - Coordinate descent optimisation.
            - More and Thuente line search.
            - Constrained.

        The true data set is:
            - S2  = 0.970
            - te  = 2048 ps
            - Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.interpreter.value.set([1.0, 0.0, 0.0], ['s2', 'te', 'rex'])

        # Minimise.
        self.interpreter.minimise('cd', 'mt')

        # Alias the relevent spin container.
        spin = cdp.mol[0].res[1].spin[0]

        # Optimisation differences.
        ###########################

        # 32-bit Linux.
        # f_count: 738
        # g_count: 738

        # 32-bit i686 Linux.
        # System:           Linux                    
        # Release:          2.6.33.7-desktop-2mnb    
        # Version:          #1 SMP Mon Sep 20 19:00:25 UTC 2010
        # Win32 version:                             
        # Distribution:     mandrake 2010.2 Official 
        # Architecture:     32bit ELF                
        # Machine:          i686                     
        # Processor:        i686                     
        # Python version:   2.6.5                    
        # Numpy version:    1.4.1                    
        # Libc version:     glibc 2.0                
        # 
        # s2:                         0.9700000000219662
        # te:                             2048.000001534
        # rex:                       0.14899999946980566
        # chi2:                   2.3474910055938013e-18
        # iter:                                      200
        # f_count:                                   874
        # g_count:                                   874
        # h_count:                                     0
        # warning:                                  None

        # 64-bit x86_64 Linux.
        # System:           Linux
        # Release:          2.6.24.7-server-2mnb
        # Version:          #1 SMP Thu Oct 30 14:50:37 EDT 2008
        # Win32 version:
        # Distribution:     mandriva 2008.1 Official
        # Architecture:     64bit ELF
        # Machine:          x86_64
        # Processor:        Intel(R) Core(TM)2 Duo CPU     E8400  @ 3.00GHz
        # Python version:   2.5.2
        # Numpy version:    1.2.0
        # Libc version:     glibc 2.2.5
        #
        # s2:                         0.9700000000219674
        # te:                         2048.0000015341870
        # rex:                       0.14899999946977982
        # chi2:                   2.3477234248531005e-18
        # iter:                                      198
        # f_count:                                   757
        # g_count:                                   757
        # h_count:                                     0
        # warning:                                  None

        # 32-bit powerpc Darwin (http://gna.org/bugs/?12573, https://mail.gna.org/public/relax-users/2008-10/msg00089.html).
        # System: Darwin
        # Release: 9.5.0
        # Version: Darwin Kernel Version 9.5.0: Wed Sep  3 11:31:44 PDT 2008; 
        # root:xnu-1228.7.58~1/RELEASE_PPC
        # Win32 version:
        # Distribution:
        # Architecture: 32bit
        # Machine: Power Macintosh
        # Processor: powerpc
        # Python version: 2.5.2
        # numpy version: 1.1.1
        # 
        # s2:       0.9700000000219674
        # te:       2048.0000015341870
        # rex:      0.14899999946977982
        # chi2:     2.3477234248531005e-18
        # iter:     198
        # f_count:  757
        # g_count:  757
        # h_count:  0
        # warning:  None

        # 64-bit i386 Darwin (http://gna.org/bugs/?14175).
        # System: Darwin
        # Release: 9.8.0
        # Version: Darwin Kernel Version 9.8.0: Wed Jul 15 16:55:01 PDT 2009; root:xnu-1228.15.4~1/RELEASE_I386
        # Win32 version:
        # Distribution:
        # Architecture: 64bit
        # Machine: i386
        # Processor: i386
        # Python version: 2.6.2
        # numpy version: 1.3.0
        # 
        # s2: 0.9700000000219674
        # te: 2048.0000015341870
        # rex: 0.14899999946977982
        # chi2: 2.3477234248531005e-18
        # iter: 198
        # f_count: 757
        # g_count: 757
        # h_count: 0
        # warning: None 

        # Optimisation values.
        select = True
        s2 = 0.9700000000219674
        te = 2048.000001534187049
        rex = 0.14899999946977982 / (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2
        chi2 = 2.3477234248531005e-18
        iter = [198, 200]
        f_count = [738, 757, 874]
        g_count = [738, 757, 874]
        h_count = 0
        warning = None

        # Test the values.
        self.assertEqual(cdp.mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select=select, s2=s2, te=te, rex=rex, chi2=chi2)


    def test_opt_constr_newton_gmw_back_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained Newton opt, GMW Hessian mod, backtracking line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            - Newton optimisation.
            - GMW Hessian modification.
            - Backtracking line search.
            - Constrained.

        The true data set is:
            - S2  = 0.970
            - te  = 2048 ps
            - Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.interpreter.value.set([1.0, 0.0, 0.0], ['s2', 'te', 'rex'])

        # Minimise.
        self.interpreter.minimise('newton', 'gmw', 'back')

        # Alias the relevent spin container.
        spin = cdp.mol[0].res[1].spin[0]

        # Optimisation differences.
        ###########################

        # 32-bit Linux.
        # f_count: 55
        # g_count: 23

        # 32-bit i686 Linux.
        # System:           Linux                    
        # Release:          2.6.33.7-desktop-2mnb    
        # Version:          #1 SMP Mon Sep 20 19:00:25 UTC 2010
        # Win32 version:                             
        # Distribution:     mandrake 2010.2 Official 
        # Architecture:     32bit ELF                
        # Machine:          i686                     
        # Processor:        i686                     
        # Python version:   2.6.5                    
        # Numpy version:    1.4.1                    
        # Libc version:     glibc 2.0                
        # 
        # s2:                         0.9699999999999992
        # te:                                       2048
        # rex:                       0.14900000000002034
        # chi2:                   1.1701970207791308e-27
        # iter:                                       18
        # f_count:                                    57
        # g_count:                                    23
        # h_count:                                    18
        # warning:                                  None

        # 64-bit x86_64 Linux.
        # System:           Linux
        # Release:          2.6.24.7-server-2mnb
        # Version:          #1 SMP Thu Oct 30 14:50:37 EDT 2008
        # Win32 version:
        # Distribution:     mandriva 2008.1 Official
        # Architecture:     64bit ELF
        # Machine:          x86_64
        # Processor:        Intel(R) Core(TM)2 Duo CPU     E8400  @ 3.00GHz
        # Python version:   2.5.2
        # Numpy version:    1.2.0
        # Libc version:     glibc 2.2.5
        #
        # s2:                         0.9699999999999995
        # te:                         2048.0000000000473
        # rex:                       0.14900000000001926
        # chi2:                   7.9357208397255696e-28
        # iter:                                       18
        # f_count:                                    55
        # g_count:                                    23
        # h_count:                                    18
        # warning:                                  None
        
        # 32-bit powerpc Darwin (http://gna.org/bugs/?12573, https://mail.gna.org/public/relax-users/2008-10/msg00089.html).
        # System: Darwin
        # Release: 9.5.0
        # Version: Darwin Kernel Version 9.5.0: Wed Sep  3 11:31:44 PDT 2008; 
        # root:xnu-1228.7.58~1/RELEASE_PPC
        # Win32 version:
        # Distribution:
        # Architecture: 32bit
        # Machine: Power Macintosh
        # Processor: powerpc
        # Python version: 2.5.2
        # numpy version: 1.1.1
        # 
        # s2:       0.9699999999999993
        # te:       2048.0000000000427
        # rex:      0.14900000000002098
        # chi2:     5.7085251917483392e-28
        # iter:     18
        # f_count:  94
        # g_count:  23
        # h_count:  18
        # warning:  None

        # 64-bit i386 Darwin (http://gna.org/bugs/?14177).
        # System: Darwin
        # Release: 9.8.0
        # Version: Darwin Kernel Version 9.8.0: Wed Jul 15 16:55:01 PDT 2009; root:xnu-1228.15.4~1/RELEASE_I386
        # Win32 version:
        # Distribution:
        # Architecture: 32bit
        # Machine: i386
        # Processor: i386
        # Python version: 2.6.2
        # numpy version: 1.3.0
        # 
        # s2: 0.9699999999999994
        # te: 2048.0000000000455
        # rex: 0.14900000000001823
        # chi2: 7.3040158179665562e-28
        # iter: 18
        # f_count: 55
        # g_count: 23
        # h_count: 18
        # warning: None 

        # Optimisation values.
        select = True
        s2 = 0.9699999999999994
        te = 2048.000000000045020
        rex = 0.14900000000001817 / (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2
        chi2 = 7.3040158179665562e-28
        iter = 18
        f_count = [55, 57, 94]
        g_count = [23]
        h_count = 18
        warning = None

        # Test the values.
        self.assertEqual(cdp.mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select=select, s2=s2, te=te, rex=rex, chi2=chi2)


    def test_opt_constr_newton_gmw_mt_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained Newton opt, GMW Hessian mod, More and Thuente line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            - Newton optimisation.
            - GMW Hessian modification.
            - More and Thuente line search.
            - Constrained.

        The true data set is:
            - S2  = 0.970
            - te  = 2048 ps
            - Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.interpreter.value.set([1.0, 0.0, 0.0], ['s2', 'te', 'rex'])

        # Minimise.
        self.interpreter.minimise('newton', 'gmw', 'mt')

        # Monte Carlo simulations.
        self.monte_carlo()

        # Alias the relevent spin container.
        spin = cdp.mol[0].res[1].spin[0]

        # Optimisation differences.
        ###########################

        # 32-bit Linux.
        # f_count: 159, 95
        # g_count: 159

        # 32-bit i686 Linux.
        # System:           Linux                    
        # Release:          2.6.33.7-desktop-2mnb    
        # Version:          #1 SMP Mon Sep 20 19:00:25 UTC 2010
        # Win32 version:                             
        # Distribution:     mandrake 2010.2 Official 
        # Architecture:     32bit ELF                
        # Machine:          i686                     
        # Processor:        i686                     
        # Python version:   2.6.5                    
        # Numpy version:    1.4.1                    
        # Libc version:     glibc 2.0                
        # 
        # s2:                         0.9699999999999994
        # te:                                       2048
        # rex:                       0.14900000000002014
        # chi2:                   7.9326439528899843e-28
        # iter:                                       22
        # f_count:                                    95
        # g_count:                                    95
        # h_count:                                    22
        # warning:                                  None

        # 64-bit x86_64 Linux.
        # System:           Linux
        # Release:          2.6.24.7-server-2mnb
        # Version:          #1 SMP Thu Oct 30 14:50:37 EDT 2008
        # Win32 version:
        # Distribution:     mandriva 2008.1 Official
        # Architecture:     64bit ELF
        # Machine:          x86_64
        # Processor:        Intel(R) Core(TM)2 Duo CPU     E8400  @ 3.00GHz
        # Python version:   2.5.2
        # Numpy version:    1.2.0
        # Libc version:     glibc 2.2.5
        #
        # s2:                         0.9699999999999994
        # te:                         2048.0000000000446
        # rex:                       0.14900000000001615
        # chi2:                   8.3312601381368332e-28
        # iter:                                       22
        # f_count:                                    91
        # g_count:                                    91
        # h_count:                                    22
        # warning:                                  None
        
        # 64-bit x86_64 Linux (Not sure why there is a difference here, maybe this is gcc or blas/lapack - Python and numpy versions are identical).
        # f_count: 153
        # g_count: 153

        # 32-bit powerpc Darwin (http://gna.org/bugs/?12573, https://mail.gna.org/public/relax-users/2008-10/msg00089.html).
        # System: Darwin
        # Release: 9.5.0
        # Version: Darwin Kernel Version 9.5.0: Wed Sep  3 11:31:44 PDT 2008; 
        # root:xnu-1228.7.58~1/RELEASE_PPC
        # Win32 version:
        # Distribution:
        # Architecture: 32bit
        # Machine: Power Macintosh
        # Processor: powerpc
        # Python version: 2.5.2
        # numpy version: 1.1.1
        # 
        # s2:       0.9699999999999993
        # te:       2048.0000000000409
        # rex:      0.14900000000002178
        # chi2:     6.8756889983348349e-28
        # iter:     22
        # f_count:  160
        # g_count:  160
        # h_count:  22
        # warning:  None

        # 32-bit Windows.
        # f_count: 165
        # g_count: 165

        # 32-bit i386 Darwin (http://gna.org/bugs/?14176).
        # System: Darwin
        # Release: 9.8.0
        # Version: Darwin Kernel Version 9.8.0: Wed Jul 15 16:55:01 PDT 2009; root:xnu-1228.15.4~1/RELEASE_I386
        # Win32 version:
        # Distribution:
        # Architecture: 32bit
        # Machine: i386
        # Processor: i386
        # Python version: 2.6.2
        # numpy version: 1.3.0
        # 
        # s2: 0.9699999999999994
        # te: 2048.0000000000446
        # rex: 0.14900000000001609
        # chi2: 8.3312601381368332e-28
        # iter: 22
        # f_count: 91
        # g_count: 91
        # h_count: 22
        # warning: None 

        # 64-bit i386 Darwin (http://gna.org/bugs/?14176).
        # System: Darwin
        # Release: 9.8.0
        # Version: Darwin Kernel Version 9.8.0: Wed Jul 15 16:55:01 PDT 2009; root:xnu-1228.15.4~1/RELEASE_I386
        # Win32 version:
        # Distribution:
        # Architecture: 64bit
        # Machine: i386
        # Processor: i386
        # Python version: 2.6.2
        # numpy version: 1.3.0
        # 
        # s2: 0.9699999999999994
        # te: 2048.0000000000446
        # rex: 0.14900000000001609
        # chi2: 8.3312601381368332e-28
        # iter: 22
        # f_count: 91
        # g_count: 91
        # h_count: 22
        # warning: None 

        # Optimisation values.
        select = True
        s2 = 0.9699999999999993
        te = 2048.000000000041837
        rex = 0.14900000000002225 / (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2
        chi2 = 6.8756889983348349e-28
        iter = 22
        f_count = [91, 95, 153, 159, 160, 165]
        g_count = [91, 95, 153, 159, 160, 165]
        h_count = 22
        warning = None

        # Test the values.
        self.assertEqual(cdp.mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select=select, s2=s2, te=te, rex=rex, chi2=chi2)


    def test_opt_constr_sd_back_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained steepest descent opt, backtracking line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            - Steepest descent optimisation.
            - Backtracking line search.
            - Constrained.

        The true data set is:
            - S2  = 0.970
            - te  = 2048 ps
            - Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.interpreter.value.set([1.0, 0.0, 0.0], ['s2', 'te', 'rex'])

        # Minimise.
        self.interpreter.minimise('sd', 'back', max_iter=50)

        # Alias the relevent spin container.
        spin = cdp.mol[0].res[1].spin[0]

        # Optimisation differences.
        ###########################

        # 64-bit x86_64 Linux.
        # System:           Linux
        # Release:          2.6.24.7-server-2mnb
        # Version:          #1 SMP Thu Oct 30 14:50:37 EDT 2008
        # Win32 version:
        # Distribution:     mandriva 2008.1 Official
        # Architecture:     64bit ELF
        # Machine:          x86_64
        # Processor:        Intel(R) Core(TM)2 Duo CPU     E8400  @ 3.00GHz
        # Python version:   2.5.2
        # Numpy version:    1.2.0
        # Libc version:     glibc 2.2.5
        #
        # s2:                         0.9157922083468916
        # te:                            0.3056865872253
        # rex:                       0.34008409798064831
        # chi2:                       68.321956795340569
        # iter:                                       50
        # f_count:                                   134
        # g_count:                                    51
        # h_count:                                     0
        # warning:        Maximum number of iterations reached
        
        # Optimisation values.
        select = True
        s2 = 0.91579220834688024
        te = 0.30568658722531733
        rex = 0.34008409798366124 / (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2
        chi2 = 68.321956795264342
        iter = 50
        f_count = 134
        g_count = 51
        h_count = 0
        warning = 'Maximum number of iterations reached'

        # Test the values.
        self.assertEqual(cdp.mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select=select, s2=s2, te=te, rex=rex, chi2=chi2)


    def test_opt_constr_sd_mt_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained steepest descent opt, More and Thuente line search {S2=0.970, te=2048, Rex=0.149}

        The optimisation options are:
            - Steepest descent optimisation.
            - More and Thuente line search.
            - Constrained.

        The true data set is:
            - S2  = 0.970
            - te  = 2048 ps
            - Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.interpreter.value.set([1.0, 0.0, 0.0], ['s2', 'te', 'rex'])

        # Minimise.
        self.interpreter.minimise('sd', 'mt', max_iter=50)

        # Alias the relevent spin container.
        spin = cdp.mol[0].res[1].spin[0]

        # Optimisation differences.
        ###########################

        # 64-bit x86_64 Linux.
        # System:           Linux
        # Release:          2.6.24.7-server-2mnb
        # Version:          #1 SMP Thu Oct 30 14:50:37 EDT 2008
        # Win32 version:
        # Distribution:     mandriva 2008.1 Official
        # Architecture:     64bit ELF
        # Machine:          x86_64
        # Processor:        Intel(R) Core(TM)2 Duo CPU     E8400  @ 3.00GHz
        # Python version:   2.5.2
        # Numpy version:    1.2.0
        # Libc version:     glibc 2.2.5
        #
        # s2:                         0.9161999495781851
        # te:                            0.1231968757090
        # rex:                       0.16249110939079675
        # chi2:                       73.843613548025075
        # iter:                                       50
        # f_count:                                   108
        # g_count:                                   108
        # h_count:                                     0
        # warning:        Maximum number of iterations reached
        
        # Optimisation values.
        select = True
        s2 = 0.91619994957822126
        te = 0.12319687570987945
        rex = 0.16249110942961512 / (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2
        chi2 = 73.843613546506191
        iter = 50
        f_count = 108
        g_count = 108
        h_count = 0
        warning = 'Maximum number of iterations reached'

        # Test the values.
        self.assertEqual(cdp.mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select=select, s2=s2, te=te, rex=rex, chi2=chi2)


    def test_opt_grid_search_S2_0_970_te_2048_Rex_0_149(self):
        """Constrained grid search {S2=0.970, te=2048, Rex=0.149}.

        The optimisation options are:
            - Constrained grid search.

        The true data set is:
            - S2  = 0.970
            - te  = 2048 ps
            - Rex = 0.149 s^-1
        """

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_setup_S2_0_970_te_2048_Rex_0_149.py')

        # Grid search.
        self.interpreter.grid_search(inc=11)

        # Alias the relevent spin container.
        spin = cdp.mol[0].res[1].spin[0]

        # Optimisation differences.
        ###########################

        # 64-bit x86_64 Linux.
        # System:           Linux
        # Release:          2.6.24.7-server-2mnb
        # Version:          #1 SMP Thu Oct 30 14:50:37 EDT 2008
        # Win32 version:
        # Distribution:     mandriva 2008.1 Official
        # Architecture:     64bit ELF
        # Machine:          x86_64
        # Processor:        Intel(R) Core(TM)2 Duo CPU     E8400  @ 3.00GHz
        # Python version:   2.5.2
        # Numpy version:    1.2.0
        # Libc version:     glibc 2.2.5
        #
        # s2:                                          1
        # te:                                          0
        # rex:                                         0
        # chi2:                       3.9844117908982288
        # iter:                                     1331
        # f_count:                                  1331
        # g_count:                                     0
        # h_count:                                     0
        # warning:                                  None

        # Optimisation values.
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
        self.assertEqual(cdp.mol[0].res[0].spin[0].select, False)
        self.value_test(spin, select=select, s2=s2, te=te, rex=rex, chi2=chi2)


    def test_read_relax_data(self):
        """Reading of relaxation data using the user function relax_data.read()."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.interpreter.sequence.read(file='noe.500.out', dir=path, res_num_col=1, res_name_col=2)

        # Read the relaxation data.
        self.interpreter.relax_data.read(ri_id='R1_600', ri_type='R1', frq=600.0 * 1e6, file='r1.600.out', dir=path, res_num_col=1, res_name_col=2, data_col=3, error_col=4)

        # Test the data and error.
        self.assertEqual(cdp.mol[0].res[1].spin[0].ri_data['R1_600'], 1.3874977659397683)
        self.assertEqual(cdp.mol[0].res[1].spin[0].ri_data_err['R1_600'], 0.027749955318795365)


    def test_read_results_1_2(self):
        """Read a relax 1.2 model-free results file using the user function results.read()."""

        # Read the results.
        self.interpreter.results.read(file='results_1.2', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free')

        # Debugging print out.
        print(cdp)

        # The spin specific data.
        num = [3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35]
        select = [False, False, False, False, False, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False, False, False]
        model = ['m6', 'm8', 'm6', 'm6', 'm5', 'm5', 'm6', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm5', 'm8']
        params = [['s2f', 'tf', 's2', 'ts'], ['s2f', 'tf', 's2', 'ts', 'rex'], ['s2f', 'tf', 's2', 'ts'], ['s2f', 'tf', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 'tf', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 's2', 'ts'], ['s2f', 'tf', 's2', 'ts', 'rex']]
        s2 = [0.36670427146403667, 0.29007016882193892, 0.32969827132809559, 0.32795333510352148, 0.48713005133752196, 0.40269538236298569, 0.40700811448591556, 0.4283551026406261, 0.51176783207279875, 0.40593664887508263, 0.39437732735324443, 0.51457448574034614, 0.3946900969237977, 0.44740698217286901, 0.48527716982891644, 0.40845486062540021, 0.45839900995265137, 0.52650140958170921, 0.4293599736020427, 0.4057313062564018, 0.49877862202992485, 0.2592017578673716]
        s2f = [0.74487419686217116, 0.75358958979175727, 0.77751085082436211, 0.79095600331751026, 0.81059857999556584, 0.83190224667917501, 0.80119109731193627, 0.83083248649122576, 0.86030420847112021, 0.84853537580616367, 0.82378413185968968, 0.82419108009774422, 0.85121172821954216, 0.8736616181472916, 0.84117641395909415, 0.82881488883235521, 0.82697284935760407, 0.85172375147802715, 0.81366357660551614, 0.80525752789388483, 0.87016608774434312, 0.72732036363757913]
        s2s = [0.49230363061145249, 0.38491796164819009, 0.4240433056059994, 0.41462904855388333, 0.60095102971952741, 0.48406574687168274, 0.50800379067049317, 0.51557336720143987, 0.59486845122178478, 0.47839684761453399, 0.47873867934666214, 0.62433881919629686, 0.46368028522041266, 0.51210557140148982, 0.57690296800513374, 0.49281795745831319, 0.55430962492751434, 0.61815983018913379, 0.5276873464009153, 0.50385285725620466, 0.57319933407525203, 0.35637907423767778]
        tf = [51.972302580836775, 40.664901270582988, 28.130299965023671, 33.804249387275249, None, None, 39.01236115991609, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 44.039078787981225]
        ts = [4485.91415175767, 4102.7781982031429, 3569.2837792404325, 6879.5308400989479, 3372.9879908647699, 4029.0617588044606, 4335.5290462417324, 4609.1336532777468, 2628.5638771308277, 3618.1332115807745, 6208.3028336637644, 3763.0843884066526, 3847.9994107906346, 2215.2061317769703, 2936.1282626562524, 3647.0715185456729, 3803.6990762708042, 2277.5259401416288, 3448.4496004396187, 3884.6917561878495, 1959.3267951363712, 4100.8496898773756]
        rex = [None, 0.37670424516405815, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 0.71472288436387088]

        # Relaxation data.
        ri_ids = ['R1_500', 'R2_500', 'NOE_500', 'R1_600', 'R2_600', 'NOE_600', 'R1_750', 'R2_750', 'NOE_750']
        types_list = ['R1', 'R2', 'NOE', 'R1', 'R2', 'NOE', 'R1', 'R2', 'NOE']
        frqs_list = [500000000.0] * 3 + [600000000.0] * 3 + [750000000.0] * 3
        ri_type = {}
        frqs = {}
        for i in range(len(ri_ids)):
            ri_type[ri_ids[i]] = types_list[i]
            frqs[ri_ids[i]] = frqs_list[i]

        ri_data = {}
        ri_data['R1_500'] = [2.2480000000000002, 2.2679999999999998, 2.2309999999999999, 2.383, 2.1960000000000002, 2.3570000000000002, 2.3340000000000001, 2.3999999999999999, 2.2839999999999998, 2.3889999999999998, 2.375, 2.274, 2.407, 2.3220000000000001, 2.2130000000000001, 2.351, 2.3260000000000001, 2.2949999999999999, 2.2829999999999999, 2.302, 2.2719999999999998, 2.2280000000000002]
        ri_data['R2_500'] = [5.3419999999999996, 5.3730000000000002, 5.1280000000000001, 5.6749999999999998, 5.9669999999999996, 5.8410000000000002, 5.774, 6.0419999999999998, 6.3129999999999997, 5.9210000000000003, 6.1269999999999998, 6.1120000000000001, 6.0570000000000004, 5.6399999999999997, 6.2809999999999997, 5.8890000000000002, 5.875, 6.1429999999999998, 5.7370000000000001, 5.5490000000000004, 5.7110000000000003, 5.4020000000000001]
        ri_data['NOE_500'] = [0.4617, 0.46560000000000001, 0.61670000000000003, 0.60860000000000003, 0.68869999999999998, 0.6663, 0.58620000000000005, 0.64939999999999998, 0.61070000000000002, 0.61180000000000001, 0.73129999999999995, 0.69650000000000001, 0.65139999999999998, 0.4929, 0.65920000000000001, 0.63029999999999997, 0.64380000000000004, 0.53500000000000003, 0.63839999999999997, 0.65000000000000002, 0.49909999999999999, 0.45979999999999999]
        ri_data['R1_600'] = [1.8879999999999999, 1.992, 2.0270000000000001, 1.9790000000000001, 1.9399999999999999, 2.0550000000000002, 2.0030000000000001, 2.0139999999999998, 1.982, 2.1000000000000001, 2.008, 1.927, 2.1019999999999999, 2.0830000000000002, 1.9910000000000001, 2.036, 1.9990000000000001, 1.9490000000000001, 1.976, 1.9870000000000001, 2.0, 1.9379999999999999]
        ri_data['R2_600'] = [5.6100000000000003, 5.7869999999999999, 5.4029999999999996, 6.1849999999999996, 6.3150000000000004, 5.9809999999999999, 6.1600000000000001, 6.2460000000000004, 6.4340000000000002, 6.0069999999999997, 6.399, 6.6799999999999997, 6.1369999999999996, 5.952, 6.3239999999999998, 5.9699999999999998, 6.3979999999999997, 6.4379999999999997, 6.1139999999999999, 6.0960000000000001, 6.3250000000000002, 6.1050000000000004]
        ri_data['NOE_600'] = [0.62929999999999997, 0.64429999999999998, 0.5393, 0.71509999999999996, 0.73870000000000002, 0.75580000000000003, 0.64239999999999997, 0.74429999999999996, 0.69440000000000002, 0.73140000000000005, 0.7681, 0.73399999999999999, 0.75680000000000003, 0.62470000000000003, 0.73529999999999995, 0.73740000000000006, 0.73080000000000001, 0.6603, 0.70899999999999996, 0.69040000000000001, 0.59199999999999997, 0.56830000000000003]
        ri_data['R1_750'] = [1.6220000000000001, 1.706, 1.73, 1.665, 1.627, 1.768, 1.706, 1.7030000000000001, 1.7649999999999999, 1.8129999999999999, 1.675, 1.6339999999999999, 1.845, 1.7829999999999999, 1.764, 1.7470000000000001, 1.681, 1.647, 1.6850000000000001, 1.667, 1.7010000000000001, 1.6850000000000001]
        ri_data['R2_750'] = [6.2619999999999996, 6.5359999999999996, 5.8959999999999999, 6.6840000000000002, 6.8819999999999997, 6.7569999999999997, 6.5620000000000003, 7.0030000000000001, 6.9740000000000002, 6.649, 6.9829999999999997, 7.2309999999999999, 6.4429999999999996, 6.6840000000000002, 6.8070000000000004, 6.4850000000000003, 6.9400000000000004, 6.944, 6.4640000000000004, 6.4889999999999999, 6.9009999999999998, 6.9539999999999997]
        ri_data['NOE_750'] = [0.61909999999999998, 0.65890000000000004, 0.72009999999999996, 0.71009999999999995, 0.75219999999999998, 0.80420000000000003, 0.70020000000000004, 0.81999999999999995, 0.81040000000000001, 0.83409999999999995, 0.81299999999999994, 0.81910000000000005, 0.7782, 0.74760000000000004, 0.8115, 0.7379, 0.81100000000000005, 0.78249999999999997, 0.75729999999999997, 0.78259999999999996, 0.75139999999999996, 0.65210000000000001]

        ri_data_err = {}
        ri_data_err['R1_500'] = [0.044999999999999998, 0.044999999999999998, 0.044499999999999998, 0.048000000000000001, 0.043999999999999997, 0.047, 0.0465, 0.048000000000000001, 0.045499999999999999, 0.048000000000000001, 0.047500000000000001, 0.045499999999999999, 0.048000000000000001, 0.0465, 0.044499999999999998, 0.047, 0.0465, 0.045499999999999999, 0.045499999999999999, 0.045999999999999999, 0.045499999999999999, 0.044499999999999998]
        ri_data_err['R2_500'] = [0.107, 0.1075, 0.10249999999999999, 0.1135, 0.11899999999999999, 0.11650000000000001, 0.11600000000000001, 0.121, 0.1265, 0.11799999999999999, 0.123, 0.122, 0.1215, 0.1125, 0.17599999999999999, 0.11749999999999999, 0.11749999999999999, 0.123, 0.1145, 0.111, 0.1145, 0.108]
        ri_data_err['NOE_500'] = [0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003]
        ri_data_err['R1_600'] = [0.037999999999999999, 0.040000000000000001, 0.040500000000000001, 0.0395, 0.0385, 0.041000000000000002, 0.040000000000000001, 0.040500000000000001, 0.040000000000000001, 0.042000000000000003, 0.041500000000000002, 0.039, 0.042000000000000003, 0.042000000000000003, 0.0395, 0.040500000000000001, 0.040000000000000001, 0.039, 0.0395, 0.040000000000000001, 0.040500000000000001, 0.039]
        ri_data_err['R2_600'] = [0.1125, 0.11550000000000001, 0.108, 0.1235, 0.1265, 0.1275, 0.123, 0.125, 0.1285, 0.12, 0.128, 0.13350000000000001, 0.1225, 0.11899999999999999, 0.1265, 0.1195, 0.128, 0.129, 0.1225, 0.122, 0.1265, 0.1225]
        ri_data_err['NOE_600'] = [0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003]
        ri_data_err['R1_750'] = [0.032500000000000001, 0.034000000000000002, 0.035000000000000003, 0.033500000000000002, 0.032500000000000001, 0.035499999999999997, 0.034000000000000002, 0.034000000000000002, 0.035499999999999997, 0.036499999999999998, 0.033500000000000002, 0.032500000000000001, 0.036999999999999998, 0.035499999999999997, 0.035499999999999997, 0.035000000000000003, 0.033500000000000002, 0.033000000000000002, 0.034000000000000002, 0.033000000000000002, 0.034000000000000002, 0.033500000000000002]
        ri_data_err['R2_750'] = [0.1255, 0.1305, 0.11799999999999999, 0.13400000000000001, 0.13800000000000001, 0.13550000000000001, 0.13150000000000001, 0.14050000000000001, 0.13950000000000001, 0.13300000000000001, 0.14000000000000001, 0.14449999999999999, 0.129, 0.13400000000000001, 0.13600000000000001, 0.1295, 0.13850000000000001, 0.13900000000000001, 0.1295, 0.13, 0.13800000000000001, 0.13900000000000001]
        ri_data_err['NOE_750'] = [0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003, 0.050000000000000003]

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
        self.assertEqual(cdp.ri_ids, ri_ids)
        for ri_id in ri_ids:
            self.assertEqual(cdp.ri_type[ri_id], ri_type[ri_id])
            self.assertEqual(cdp.frq[ri_id], frqs[ri_id])

        # Loop over the residues of the original data.
        j = 0
        for i in xrange(len(cdp.mol[0].res)):
            # Aliases
            res = cdp.mol[0].res[i]
            spin = cdp.mol[0].res[i].spin[0]

            # Debugging print out.
            print(res)
            print(spin)

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
            for ri_id in cdp.ri_ids:
                print(ri_id)
                self.assertEqual(spin.ri_data[ri_id], ri_data[ri_id][j])
                self.assertEqual(spin.ri_data_err[ri_id], ri_data_err[ri_id][j])

            # Secondary index.
            j = j + 1


    def test_read_results_1_2_pse4(self):
        """Read the truncated relax 1.2 model-free results file for PSE-4."""

        # Read the results.
        self.interpreter.results.read(file='pse4_trunc', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free')

        # Debugging print out.
        print(cdp)

        # The spin specific data.
        num = [24, 27]
        name = ['ser', 'gln']
        eqi = [None, 'mf_ext']
        select = [False, True]
        model = [None, 'm5']
        params = [[], ['s2f', 's2', 'ts']]
        s2 = [None, 0.86578779694713515]
        s2f = [None, 0.88618694421409949]
        s2s = [None, 0.97698098871784322]
        s2s_sim = [[None, None, None],
                [0.95852080081635382, 0.97574415413309512, 0.97293450506144197]]
        tf = [None, None]
        ts = [None, 598.8142249659868e-12]
        rex = [None, None]
        r = [None, 1.0200000000000001e-10]
        csa = [None, -0.00017199999999999998]
        ri_ids = ['R1_800', 'NOE_800', 'R1_600', 'R2_600', 'NOE_600', 'R1_500', 'R2_500', 'NOE_500']
        ri_type_list = ['R1', 'NOE', 'R1', 'R2', 'NOE', 'R1', 'R2', 'NOE']
        frq_list = [799744000.0]*2 + [599737000.0]*3 + [499719000.0]*3
        ri_data_list = [[],
                [0.6835, 0.81850000000000001, 0.98409999999999997, 16.5107, 0.79796699999999998, 1.3174999999999999, 15.381500000000001, 0.73046900000000003]]
        ri_data_err_list = [[],
                [0.026957200000000001, 0.025881000000000001, 0.0243073, 0.497137, 0.028663000000000001, 0.038550000000000001, 0.40883999999999998, 0.022016299999999999]]
        ri_type = {}
        frq = {}
        ri_data = [{}, {}]
        ri_data_err = [{}, {}]
        for i in range(len(ri_ids)):
            ri_type[ri_ids[i]] = ri_type_list[i]
            frq[ri_ids[i]] = frq_list[i]
            ri_data[1][ri_ids[i]] = ri_data_list[1][i]
            ri_data_err[1][ri_ids[i]] = ri_data_err_list[1][i]

        # Misc tests.
        self.assertEqual(cdp.pipe_type, 'mf')
        self.assertEqual(cdp.hybrid_pipes, [])

        # Diffusion tensor tests.
        self.assertEqual(cdp.diff_tensor.type, 'ellipsoid')
        self.assertEqual(cdp.diff_tensor.tm, 1.2682770910095516e-08)
        self.assertEqual(cdp.diff_tensor.tm_err, 2.4053909822304126e-11)
        self.assertEqual(cdp.diff_tensor.tm_sim[0], 1.2666656725867738e-08)
        self.assertEqual(cdp.diff_tensor.tm_sim[1], 1.2689812011679408e-08)
        self.assertEqual(cdp.diff_tensor.tm_sim[2], 1.2698266641804573e-08)

        # Global minimisation statistic tests.
        self.assertEqual(cdp.chi2, 935.13348627485448)
        self.assertEqual(cdp.chi2_sim[0], 898.0981500197106)
        self.assertEqual(cdp.chi2_sim[1], 904.11113814725172)
        self.assertEqual(cdp.chi2_sim[2], 902.03890817023728)
        self.assertEqual(cdp.iter, 1)
        self.assertEqual(cdp.iter_sim[0], 23)
        self.assertEqual(cdp.iter_sim[1], 30)
        self.assertEqual(cdp.iter_sim[2], 16)
        self.assertEqual(cdp.f_count, 21)
        self.assertEqual(cdp.f_count_sim[0], 61)
        self.assertEqual(cdp.f_count_sim[1], 501)
        self.assertEqual(cdp.f_count_sim[2], 59)
        self.assertEqual(cdp.g_count, 2)
        self.assertEqual(cdp.g_count_sim[0], 27)
        self.assertEqual(cdp.g_count_sim[1], 34)
        self.assertEqual(cdp.g_count_sim[2], 20)
        self.assertEqual(cdp.h_count, 1)
        self.assertEqual(cdp.h_count_sim[0], 23)
        self.assertEqual(cdp.h_count_sim[1], 30)
        self.assertEqual(cdp.h_count_sim[2], 16)
        self.assertEqual(cdp.warning, None)
        self.assertEqual(cdp.warning_sim[0], None)
        self.assertEqual(cdp.warning_sim[1], None)
        self.assertEqual(cdp.warning_sim[2], None)

        # Global relaxation data tests.
        self.assertEqual(cdp.ri_ids, ri_ids)
        for ri_id in ri_ids:
            self.assertEqual(cdp.ri_type[ri_id], ri_type[ri_id])
            self.assertEqual(cdp.frq[ri_id], frq[ri_id])

        # Loop over the residues of the original data.
        for i in xrange(len(cdp.mol[0].res)):
            # Aliases
            res = cdp.mol[0].res[i]
            spin = cdp.mol[0].res[i].spin[0]

            # Debugging print out.
            print(res)
            print(spin)

            # Spin info tests.
            self.assertEqual(res.num, num[i])
            self.assertEqual(res.name, name[i])
            self.assertEqual(spin.num, None)
            self.assertEqual(spin.name, None)
            self.assertEqual(spin.select, select[i])
            self.assertEqual(spin.fixed, False)

            # Structural info.
            self.assertEqual(spin.heteronuc_type, '15N')
            self.assertEqual(spin.proton_type, '1H')
            self.assertEqual(spin.attached_proton, 'H')
            #FIXME
            #self.assertEqual(spin.nucleus, 'N')

            # Model-free tests.
            self.assertEqual(spin.model, model[i])
            self.assertEqual(spin.equation, eqi[i])
            self.assertEqual(spin.params, params[i])
            self.assertEqual(spin.s2, s2[i])
            self.assertEqual(spin.s2f, s2f[i])
            self.assertEqual(spin.s2s, s2s[i])
            self.assertEqual(spin.local_tm, None)
            self.assertEqual(spin.te, None)
            self.assertEqual(spin.tf, tf[i])
            self.assertEqual(spin.ts, ts[i])
            self.assertEqual(spin.rex, rex[i])
            self.assertEqual(spin.r, r[i])
            self.assertEqual(spin.csa, csa[i])
            for j in range(3):
                self.assertEqual(spin.s2s_sim[j], s2s_sim[i][j])

            # Minimisation statistic tests.
            self.assertEqual(spin.chi2, None)
            self.assertEqual(spin.iter, None)
            self.assertEqual(spin.f_count, None)
            self.assertEqual(spin.g_count, None)
            self.assertEqual(spin.h_count, None)
            self.assertEqual(spin.warning, None)

            # Relaxation data tests.
            if i == 0:
                self.assertEqual(spin.ri_data, {})
                self.assertEqual(spin.ri_data_err, {})
            else:
                for ri_id in ri_ids:
                    self.assertEqual(spin.ri_data[ri_id], ri_data[i][ri_id])
                    self.assertEqual(spin.ri_data_err[ri_id], ri_data_err[i][ri_id])


    def test_read_results_1_2_tem1(self):
        """Read the truncated relax 1.2 model-free results file for TEM-1."""

        # Read the results.
        self.interpreter.results.read(file='tem1_trunc', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free')

        # Debugging print out.
        print(cdp)

        # The spin specific data.
        num = [26, 27, 29, 30, 31, 32, 33, 34]
        name = ['His', 'Pro', 'Thr', 'Leu', 'Val', 'Lys', 'Val', 'Lys']
        eqi = [None, None, None, 'mf_ext', 'mf_orig', 'mf_orig', None, 'mf_orig']
        select = [False, False, False, True, True, True, False, True]
        model = [None, None, None, 'm5', 'm2', 'm1', None, 'm1']
        params = [None, None, None, ['s2f', 's2', 'ts'], ['s2', 'te'], ['s2'], None, ['s2']]
        s2 = [None, None, None, 0.85674161305142216, 0.89462664243726608, 0.90201790111143165, None, 0.92099297347361675]
        s2f = [None, None, None, 0.88220054271390302, None, None, None, None]
        s2s = [None, None, None, 0.97114156200339452, None, None, None, None]
        te = [None, None, None, None, 43.262426916926735*1e-12, None, None, None]
        tf = [None, None, None, None, None, None, None, None]
        ts = [None, None, None, 2385.912514843546*1e-12, None, None, None, None]
        rex = [None, None, None, None, None, None, None, None]
        r = [None, None, None, 1.0200000000000001e-10, 1.0200000000000001e-10, 1.0200000000000001e-10, None, 1.0200000000000001e-10]
        csa = [None, None, None, -0.00017199999999999998, -0.00017199999999999998, -0.00017199999999999998, None, -0.00017199999999999998]
        ri_ids = ['R1_800', 'R2_800', 'R1_600', 'R2_600', 'NOE_600', 'R1_500', 'R2_500', 'NOE_500']
        ri_type_list = ['R1', 'R2', 'R1', 'R2', 'NOE', 'R1', 'R2', 'NOE']
        frq_list = [799812000.0]*2 + [599739000.0]*3 + [499827000.0]*3
        ri_data_list = [[],
                        [],
                        [],
                        [0.75680000000000003, 18.797999999999998, 1.0747, 16.477, 0.86873100000000003, 1.2625999999999999, 15.3367, 0.77803197999999996],
                        [0.75019999999999998, 19.201599999999999, 1.0617000000000001, 17.652899999999999, 0.73757200000000001, 1.3165, 15.949, 0.72442474000000001],
                        [0.75860000000000005, 19.303799999999999, 1.0605, 16.593699999999998, 0.79137500000000005, 1.3425, 15.327199999999999, 0.83449132000000004],
                        [],
                        [0.71919999999999995, 20.165400000000002, 1.0729, 17.291899999999998, 0.80444599999999999, 1.2971999999999999, 15.9963, 0.73164684999999996]]
        ri_data_err_list = [[],
                            [],
                            [],
                            [0.028001600000000001, 0.21729999999999999, 0.031166300000000001, 0.44487900000000002, 0.043210699999999998, 0.054291800000000001, 0.69015199999999999, 0.038901600000000001],
                            [0.028899999999999999, 0.25640000000000002, 0.030789299999999999, 0.476628, 0.036686799999999999, 0.0566095, 0.71770500000000004, 0.036221200000000002],
                            [0.033399999999999999, 0.2233, 0.030754500000000001, 0.44802999999999998, 0.039363000000000002, 0.057727500000000001, 0.689724, 0.041724600000000001],
                            [],
                            [0.027699999999999999, 0.52810000000000001, 0.031399999999999997, 0.46688099999999999, 0.040013100000000003, 0.055779599999999999, 0.71983399999999997, 0.036582299999999998]]
        ri_type = {}
        frq = {}
        ri_data = []
        ri_data_err = []
        for i in range(len(ri_data_list)):
            ri_data.append({})
            ri_data_err.append({})

        for i in range(len(ri_ids)):
            ri_type[ri_ids[i]] = ri_type_list[i]
            frq[ri_ids[i]] = frq_list[i]
            for j in range(len(ri_data_list)):
                if len(ri_data_list[j]):
                    ri_data[j][ri_ids[i]] = ri_data_list[j][i]
                    ri_data_err[j][ri_ids[i]] = ri_data_err_list[j][i]

        chi2 = [None, None, None, 7.9383923597292441, 10.93852890925343, 3.1931459495488084, None, 8.3598891989018611]
        iter = [None, None, None, 55, 10, 3, None, 3]
        f_count = [None, None, None, 170, 148, 10, None, 10]
        g_count = [None, None, None, 60, 14, 6, None, 6]
        h_count = [None, None, None, 55, 10, 3, None, 3]

        # Misc tests.
        self.assertEqual(cdp.pipe_type, 'mf')
        self.assertEqual(cdp.hybrid_pipes, [])

        # Diffusion tensor tests.
        self.assertEqual(cdp.diff_tensor.type, 'ellipsoid')
        self.assertEqual(cdp.diff_tensor.tm, 1.2526607261882971e-08)
        self.assertEqual(cdp.diff_tensor.Da, 2784606.8835473624)
        self.assertEqual(cdp.diff_tensor.Dr, 0.097243698709517518)
        self.assertEqual(cdp.diff_tensor.alpha, 48.852555276419558 / 360.0 * 2.0 * pi)
        self.assertEqual(cdp.diff_tensor.beta, 9.7876096346750447 / 360.0 * 2.0 * pi)
        self.assertEqual(cdp.diff_tensor.gamma, 42.15815798778408 / 360.0 * 2.0 * pi)

        # Global relaxation data tests.
        self.assertEqual(cdp.ri_ids, ri_ids)
        for ri_id in ri_ids:
            self.assertEqual(cdp.ri_type[ri_id], ri_type[ri_id])
            self.assertEqual(cdp.frq[ri_id], frq[ri_id])

        # Loop over the residues of the original data.
        for i in xrange(len(cdp.mol[0].res)):
            # Aliases
            res = cdp.mol[0].res[i]
            spin = cdp.mol[0].res[i].spin[0]

            # Debugging print out.
            print(res)
            print(spin)

            # Spin info tests.
            self.assertEqual(res.num, num[i])
            self.assertEqual(res.name, name[i])
            self.assertEqual(spin.num, None)
            self.assertEqual(spin.name, None)
            self.assertEqual(spin.select, select[i])
            self.assertEqual(spin.fixed, False)

            # Structural info.
            self.assertEqual(spin.heteronuc_type, '15N')
            self.assertEqual(spin.proton_type, '1H')
            self.assertEqual(spin.attached_proton, 'H')
            #FIXME
            #self.assertEqual(spin.nucleus, 'N')

            # Model-free tests.
            self.assertEqual(spin.model, model[i])
            self.assertEqual(spin.equation, eqi[i])
            self.assertEqual(spin.params, params[i])
            self.assertEqual(spin.s2, s2[i])
            self.assertEqual(spin.s2f, s2f[i])
            self.assertEqual(spin.s2s, s2s[i])
            self.assertEqual(spin.local_tm, None)
            self.assertEqual(spin.te, te[i])
            self.assertEqual(spin.tf, tf[i])
            self.assertEqual(spin.ts, ts[i])
            self.assertEqual(spin.rex, rex[i])
            self.assertEqual(spin.r, r[i])
            self.assertEqual(spin.csa, csa[i])

            # Minimisation statistic tests.
            self.assertEqual(spin.chi2, chi2[i])
            self.assertEqual(spin.iter, iter[i])
            self.assertEqual(spin.f_count, f_count[i])
            self.assertEqual(spin.g_count, g_count[i])
            self.assertEqual(spin.h_count, h_count[i])
            self.assertEqual(spin.warning, None)

            # Relaxation data tests.
            print ri_data
            if not ri_data[i].keys():
                self.assertEqual(spin.ri_data, {})
                self.assertEqual(spin.ri_data_err, {})
            else:
                for ri_id in ri_ids:
                    self.assertEqual(spin.ri_data[ri_id], ri_data[i][ri_id])
                    self.assertEqual(spin.ri_data_err[ri_id], ri_data_err[i][ri_id])


    def test_read_results_1_3(self):
        """Read a relax 1.3 model-free results file using the user function results.read()."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'OMP'

        # Read the results file.
        self.interpreter.pipe.create('1.3', 'mf')
        self.interpreter.results.read(file='final_results_trunc_1.3', dir=path)

        # Read the equivalent 1.2 results file for the checks.
        self.interpreter.pipe.create('1.2', 'mf')
        self.interpreter.results.read(file='final_results_trunc_1.2', dir=path)

        # Get the two data pipes.
        pipe_12 = pipes.get_pipe('1.2')
        pipe_13 = pipes.get_pipe('1.3')

        # Test that the objects in the base pipes are the same.
        print("Comparison of the objects of the base data pipe:")
        self.object_comparison(obj1=pipe_12, obj2=pipe_13, skip=['mol', 'diff_tensor'])

        # Test that the diffusion tensor data is the same.
        print("Comparison of the objects of the diffusion tensor:")
        self.object_comparison(obj1=pipe_12.diff_tensor, obj2=pipe_13.diff_tensor)

        # Test the number of molecules.
        self.assertEqual(len(pipe_12.mol), len(pipe_13.mol))

        # Loop over the molecules.
        for i in xrange(len(pipe_12.mol)):
            # Test the objects.
            print("Comparison of the objects of the molecule:")
            self.object_comparison(obj1=pipe_12.mol[i], obj2=pipe_13.mol[i], skip=['res'])

            # Test the number of residues.
            self.assertEqual(len(pipe_12.mol[i].res), len(pipe_13.mol[i].res))

            # Loop over the residues.
            for j in xrange(len(pipe_12.mol[i].res)):
                # Ok, really don't need to do a full comparison of all 162 residues for this test!
                if j > 10:
                    break

                # Test the objects.
                print("Comparison of the objects of the residue:")
                self.object_comparison(obj1=pipe_12.mol[i].res[j], obj2=pipe_13.mol[i].res[j], skip=['spin'])

                # Test the number of spins.
                self.assertEqual(len(pipe_12.mol[i].res[j].spin), len(pipe_13.mol[i].res[j].spin))

                # Loop over the spins.
                for k in xrange(len(pipe_12.mol[i].res[j].spin)):
                    # Test the objects.
                    print("Comparison of the objects of the spin:")
                    self.object_comparison(obj1=pipe_12.mol[i].res[j].spin[k], obj2=pipe_13.mol[i].res[j].spin[k])



    def test_select_m4(self):
        """Selecting model m4 with parameters {S2, te, Rex} using model_free.select_model()."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.interpreter.sequence.read(file='noe.500.out', dir=path, res_num_col=1, res_name_col=2)

        # Select the model.
        self.interpreter.model_free.select_model(model='m4')

        # Test the model.
        self.assertEqual(cdp.mol[0].res[1].spin[0].model, 'm4')
        self.assertEqual(cdp.mol[0].res[1].spin[0].params, ['s2', 'te', 'rex'])


    def test_set_bond_length(self):
        """Setting the bond length through the user function value.set()."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.interpreter.sequence.read(file='noe.500.out', dir=path, res_num_col=1, res_name_col=2)

        # Set the CSA value.
        self.interpreter.value.set(NH_BOND_LENGTH, 'r')

        # Test the value.
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, NH_BOND_LENGTH)


    def test_set_csa(self):
        """Setting the CSA value through the user function value.set()."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.interpreter.sequence.read(file='noe.500.out', dir=path, res_num_col=1, res_name_col=2)

        # Set the CSA value.
        self.interpreter.value.set(N15_CSA, 'csa')

        # Test the value.
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, N15_CSA)


    def test_set_csa_bond_length(self):
        """Setting both the CSA value and bond length through the user function value.set()."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.interpreter.sequence.read(file='noe.500.out', dir=path, res_num_col=1, res_name_col=2)

        # Set the CSA value and bond length simultaneously.
        self.interpreter.value.set([N15_CSA, NH_BOND_LENGTH], ['csa', 'r'])

        # Test the values.
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, N15_CSA)
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, NH_BOND_LENGTH)


    def test_tm0_grid(self):
        """Test the optimisation of the tm0 model-free parameter grid."""

        # Initialise.
        cdp._model = 'tm0'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm0_grid.py')


    def test_tm1_grid(self):
        """Test the optimisation of the tm1 model-free parameter grid."""

        # Initialise.
        cdp._model = 'tm1'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm1_grid.py')


    def test_tm2_grid(self):
        """Test the optimisation of the tm2 model-free parameter grid."""

        # Initialise.
        cdp._model = 'tm2'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm2_grid.py')


    def test_tm3_grid(self):
        """Test the optimisation of the tm3 model-free parameter grid."""

        # Initialise.
        cdp._model = 'tm3'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm3_grid.py')


    def test_tm4_grid(self):
        """Test the optimisation of the tm4 model-free parameter grid."""

        # Initialise.
        cdp._model = 'tm4'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm4_grid.py')


    def test_tm5_grid(self):
        """Test the optimisation of the tm5 model-free parameter grid."""

        # Initialise.
        cdp._model = 'tm5'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm5_grid.py')


    def test_tm6_grid(self):
        """Test the optimisation of the tm6 model-free parameter grid."""

        # Initialise.
        cdp._model = 'tm6'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm6_grid.py')


    def test_tm7_grid(self):
        """Test the optimisation of the tm7 model-free parameter grid."""

        # Initialise.
        cdp._model = 'tm7'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm7_grid.py')


    def test_tm8_grid(self):
        """Test the optimisation of the tm8 model-free parameter grid."""

        # Initialise.
        cdp._model = 'tm8'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm8_grid.py')


    def test_tm9_grid(self):
        """Test the optimisation of the tm9 model-free parameter grid."""

        # Initialise.
        cdp._model = 'tm9'
        cdp._value_test = self.value_test

        # Setup the data pipe for optimisation.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'opt_tm9_grid.py')


    def test_tylers_peptide(self):
        """Try a component of model-free analysis on Tyler Reddy's peptide data (truncated)."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'model_free'+sep+'tylers_peptide.py')


    def test_write_results(self):
        """Writing of model-free results using the user function results.write()."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'OMP'

        # Read the results file.
        self.interpreter.results.read(file='final_results_trunc_1.2', dir=path)

        # A dummy file object for catching the results.write() output.
        file = DummyFileObject()

        # Write the results file into a dummy file.
        self.interpreter.results.write(file=file, dir=path)

        # Now, get the contents of that file, and then 'close' that file.
        test_lines = file.readlines()
        file.close()

        # Read the 1.3 results file, extract the data, then close it again.
        a, b, c = platform.python_version_tuple()
        if dep_check.xml_type == 'internal' and int(a) >= 2 and int(b) >= 7 and int(c) >= 3:
            file = open_read_file(file_name='final_results_trunc_1.3_new', dir=path)
        else:
            file = open_read_file(file_name='final_results_trunc_1.3', dir=path)
        true_lines = file.readlines()
        file.close()

        # Test the rest of the lines.
        for i in xrange(len(test_lines)):
            # Skip the second line, as it contains the date and hence should not be the same.
            # Also skip the third line, as the pipe names are different.
            if i == 1 or i == 2:
                continue

            # Try to convert the test line into a python object (for cross-platform support).
            try:
                test_line = eval(test_lines[i])
            except:
                test_line = test_lines[i]

            # Try to convert the true line into a python object (for cross-platform support).
            try:
                true_line = eval(true_lines[i])
            except:
                true_line = true_lines[i]

            # Test that the line is the same.
            self.assertEqual(test_line, true_line)


    def value_test(self, spin, select=True, local_tm=None, s2=None, s2f=None, s2s=None, te=None, tf=None, ts=None, rex=None, chi2=None, iter=None, f_count=None, g_count=None, h_count=None, warning=None):
        """Test the optimisation values."""

        # Get the debugging message.
        mesg = self.mesg_opt_debug(spin)

        # Convert to lists.
        if iter != None and not isinstance(iter, list):
            iter = [iter]
        if f_count != None and not isinstance(f_count, list):
            f_count = [f_count]
        if g_count != None and not isinstance(g_count, list):
            g_count = [g_count]
        if h_count != None and not isinstance(h_count, list):
            h_count = [h_count]

        # Test all the values.
        ######################

        # Spin selection.
        self.assertEqual(spin.select, select, msg=mesg)

        # The local tm correlation time.
        if local_tm != None:
            self.assertAlmostEqual(spin.local_tm / 1e-9, local_tm, msg=mesg)
        else:
            self.assertEqual(spin.local_tm, None, msg=mesg)

        # S2 order parameter.
        if s2 != None:
            self.assertAlmostEqual(spin.s2, s2, msg=mesg)
        else:
            self.assertEqual(spin.s2, None, msg=mesg)

        # S2f order parameter.
        if s2f != None:
            self.assertAlmostEqual(spin.s2f, s2f, 5, msg=mesg)
        else:
            self.assertEqual(spin.s2f, None, msg=mesg)

        # S2s order parameter.
        if s2s != None:
            self.assertAlmostEqual(spin.s2s, s2s, 5, msg=mesg)
        else:
            self.assertEqual(spin.s2s, None, msg=mesg)

        # te correlation time.
        if isinstance(te, float):
            self.assertAlmostEqual(spin.te / 1e-12, te, 5, msg=mesg)
        elif te == None:
            self.assertEqual(spin.te, None, msg=mesg)

        # tf correlation time.
        if isinstance(tf, float):
            self.assertAlmostEqual(spin.tf / 1e-12, tf, 4, msg=mesg)
        elif tf == None:
            self.assertEqual(spin.tf, None, msg=mesg)

        # ts correlation time.
        if isinstance(ts, float):
            self.assertAlmostEqual(spin.ts / 1e-12, ts, 4, msg=mesg)
        elif ts == None:
            self.assertEqual(spin.ts, None, msg=mesg)

        # Chemical exchange.
        if isinstance(rex, float):
            self.assertAlmostEqual(spin.rex * (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2, rex * (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2, msg=mesg)
        elif rex == None:
            self.assertEqual(spin.rex, None, msg=mesg)

        # The optimisation stats.
        if chi2 != None:
            self.assertAlmostEqual(spin.chi2, chi2, msg=mesg)
        if iter != None:
            self.assert_(spin.iter in iter, msg=mesg)
        if f_count != None:
            self.assert_(spin.f_count in f_count, msg=mesg)
        if g_count != None:
            self.assert_(spin.g_count in g_count, msg=mesg)
        if h_count != None:
            self.assert_(spin.h_count in h_count, msg=mesg)
        if warning != None:
            self.assertEqual(spin.warning, warning, msg=mesg)
