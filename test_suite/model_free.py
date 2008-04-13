###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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

from math import pi
import sys


class Mf:
    def __init__(self, relax, test_name):
        """Class for testing various aspects specific to model-free analysis."""

        self.relax = relax

        # Relaxation data reading test.
        if test_name == 'read relaxation data':
            # The name of the test.
            self.name = "The user function relax_data.read()"

            # The test.
            self.test = self.read_relax_data

        # Test of setting the CSA.
        if test_name == 'set csa':
            # The name of the test.
            self.name = "Setting the CSA value through the user function value.set()"

            # The test.
            self.test = self.set_csa

        # Test of setting the bond length.
        if test_name == 'set bond length':
            # The name of the test.
            self.name = "Setting the bond length through the user function value.set()"

            # The test.
            self.test = self.set_csa

         # Test of setting the CSA and the bond length.
        if test_name == 'set csa and bond length':
            # The name of the test.
            self.name = "Setting both the CSA value and bond length through the user function value.set()"

            # The test.
            self.test = self.set_csa_bond_length

       # Test of selecting model-free model m4.
        if test_name == 'select m4':
            # The name of the test.
            self.name = "Selecting model m4 with parameters {S2, te, Rex} using model_free.select_model()"

            # The test.
            self.test = self.select_m4

        # Test of creating model-free model m4.
        if test_name == 'create m4':
            # The name of the test.
            self.name = "Creating model m4 with parameters {S2, te, Rex} using model_free.create_model()"

            # The test.
            self.test = self.select_m4

        # Results reading test.
        if test_name == 'read results':
            # The name of the test.
            self.name = "The user function results.read()"

            # The test.
            self.test = self.read_results

        # OpenDX {S2, te, Rex} mapping test.
        if test_name == 'opendx {S2, te, Rex} map':
            # The name of the test.
            self.name = "Mapping the {S2, te, Rex} chi2 space through the OpenDX user function dx.map()"

            # The test.
            self.test = self.opendx_s2_te_rex

        # OpenDX {theta, phi, Da} mapping test.
        if test_name == 'opendx {theta, phi, Da} map':
            # The name of the test.
            self.name = "Mapping the {theta, phi, Da} chi2 space through the OpenDX user function dx.map()"

            # The test.
            self.test = self.opendx_theta_phi_da

        # OpenDX {local_tm, S2, te} mapping test.
        if test_name == 'opendx {local_tm, S2, te} map':
            # The name of the test.
            self.name = "Mapping the {local_tm, S2, te} chi2 space through the OpenDX user function dx.map()"

            # The test.
            self.test = self.opendx_tm_s2_te


        # Optimisation:  Constrained grid search {S2=0.970, te=2048, Rex=0.149}.
        if test_name == 'Constrained grid search {S2=0.970, te=2048, Rex=0.149}':
            # The name of the test.
            self.name = "Constrained grid search {S2=0.970, te=2048, Rex=0.149}"

            # The test.
            self.test = self.opt_grid_search_S2_0_970_te_2048_Rex_0_149


        # Optimisation:  Constrained SD, backtracking {S2=0.970, te=2048, Rex=0.149}.
        if test_name == 'Constrained SD, backtracking opt {S2=0.970, te=2048, Rex=0.149}':
            # The name of the test.
            self.name = "Constrained steepest descent opt, backtracking line search {S2=0.970, te=2048, Rex=0.149}"

            # The test.
            self.test = self.opt_constr_sd_back_S2_0_970_te_2048_Rex_0_149


        # Optimisation:  Constrained SD, MT {S2=0.970, te=2048, Rex=0.149}.
        if test_name == 'Constrained SD, MT opt {S2=0.970, te=2048, Rex=0.149}':
            # The name of the test.
            self.name = "Constrained steepest descent opt, More and Thuente line search {S2=0.970, te=2048, Rex=0.149}"

            # The test.
            self.test = self.opt_constr_sd_mt_S2_0_970_te_2048_Rex_0_149


        # Optimisation:  Constrained CD, backtracking {S2=0.970, te=2048, Rex=0.149}.
        if test_name == 'Constrained CD, backtracking opt {S2=0.970, te=2048, Rex=0.149}':
            # The name of the test.
            self.name = "Constrained coordinate descent opt, backtracking line search {S2=0.970, te=2048, Rex=0.149}"

            # The test.
            self.test = self.opt_constr_cd_back_S2_0_970_te_2048_Rex_0_149


        # Optimisation:  Constrained CD, MT {S2=0.970, te=2048, Rex=0.149}.
        if test_name == 'Constrained CD, MT opt {S2=0.970, te=2048, Rex=0.149}':
            # The name of the test.
            self.name = "Constrained coordinate descent opt, More and Thuente line search {S2=0.970, te=2048, Rex=0.149}"

            # The test.
            self.test = self.opt_constr_cd_mt_S2_0_970_te_2048_Rex_0_149


        # Optimisation:  Constrained BFGS, backtracking {S2=0.970, te=2048, Rex=0.149}.
        if test_name == 'Constrained BFGS, backtracking opt {S2=0.970, te=2048, Rex=0.149}':
            # The name of the test.
            self.name = "Constrained BFGS opt, backtracking line search {S2=0.970, te=2048, Rex=0.149}"

            # The test.
            self.test = self.opt_constr_bfgs_back_S2_0_970_te_2048_Rex_0_149


        # Optimisation:  Constrained BFGS, MT {S2=0.970, te=2048, Rex=0.149}.
        if test_name == 'Constrained BFGS, MT opt {S2=0.970, te=2048, Rex=0.149}':
            # The name of the test.
            self.name = "Constrained BFGS opt, More and Thuente line search {S2=0.970, te=2048, Rex=0.149}"

            # The test.
            self.test = self.opt_constr_bfgs_mt_S2_0_970_te_2048_Rex_0_149


        # Optimisation:  Constrained Newton, GMW, backtracking {S2=0.970, te=2048, Rex=0.149}.
        if test_name == 'Constrained Newton, GMW, backtracking opt {S2=0.970, te=2048, Rex=0.149}':
            # The name of the test.
            self.name = "Constrained Newton opt, GMW Hessian mod, backtracking line search {S2=0.970, te=2048, Rex=0.149}"

            # The test.
            self.test = self.opt_constr_newton_gmw_back_S2_0_970_te_2048_Rex_0_149


        # Optimisation:  Constrained Newton, GMW, MT {S2=0.970, te=2048, Rex=0.149}.
        if test_name == 'Constrained Newton, GMW, MT opt {S2=0.970, te=2048, Rex=0.149}':
            # The name of the test.
            self.name = "Constrained Newton opt, GMW Hessian mod, More and Thuente line search {S2=0.970, te=2048, Rex=0.149}"

            # The test.
            self.test = self.opt_constr_newton_gmw_mt_S2_0_970_te_2048_Rex_0_149


    def create_m4(self, run):
        """Testing the creation of model-free model m4."""

        # Arguments.
        self.run = run

        # Create the run.
        self.relax.generic.runs.create(self.run, 'mf')

        # Path of the files.
        path = sys.path[-1] + '/test_suite/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(self.run, file='noe.500.out', dir=path)

        # Select the model.
        self.relax.interpreter._Model_free.create_model(self.run, model='m4', equation='mf_orig', params=['S2', 'te', 'Rex'])

        # Test the model.
        if self.relax.data.res[self.run][1].model != 'm4':
            print "The model has not been selected."
            return

        # Test the parameters.
        if self.relax.data.res[self.run][1].params != ['S2', 'te', 'Rex']:
            print "The parameters are incorrect."
            return

        return 1


    def opendx_s2_te_rex(self, run):
        """The OpenDX {S2, te, Rex} mapping test."""

        # Arguments.
        self.run = run

        # Create the run.
        self.relax.generic.runs.create(self.run, 'mf')

        # Path of the files.
        path = sys.path[-1] + '/test_suite/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Nuclei type
        self.relax.interpreter._Nuclei.nuclei('N')

        # Read the sequence.
        self.relax.interpreter._Sequence.read(self.run, file='noe.500.out', dir=path)

        # Read the relaxation data.
        self.relax.interpreter._Relax_data.read(self.run, 'R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'R2', '600', 600.0 * 1e6, 'r2.600.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'NOE', '600', 600.0 * 1e6, 'noe.600.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'R1', '500', 500.0 * 1e6, 'r1.500.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'R2', '500', 500.0 * 1e6, 'r2.500.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'NOE', '500', 500.0 * 1e6, 'noe.500.out', dir=path)

        # Setup other values.
        self.relax.interpreter._Diffusion_tensor.init(self.run, 1e-8, fixed=1)
        self.relax.interpreter._Value.set(self.run, [-172 * 1e-6, 1.02 * 1e-10], ['csa', 'bond_length'])

        # Select the model.
        self.relax.interpreter._Model_free.select_model(self.run, model='m4')

        # Map the space.
        self.relax.interpreter._OpenDX.map(self.run, params=['S2', 'te', 'Rex'], res_num=2, inc=2, lower=[0.0, 0, 0], upper=[1.0, 10000e-12, 3.0 / (2.0 * pi * 600000000.0)**2], point=[0.970, 2048.0e-12, 0.149 / (2.0 * pi * 600000000.0)**2], file='devnull', point_file='devnull')

        return 1


    def opendx_theta_phi_da(self, run):
        """The OpenDX {theta, phi, Da} mapping test."""

        # Arguments.
        self.run = run

        # Create the run.
        self.relax.generic.runs.create(self.run, 'mf')

        # Path of the files.
        path = sys.path[-1] + '/test_suite/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Nuclei type
        self.relax.interpreter._Nuclei.nuclei('N')

        # Read the sequence.
        self.relax.interpreter._Sequence.read(self.run, file='noe.500.out', dir=path)

        # Read the PDF file.
        self.relax.interpreter._PDB.pdb(run, file='pdb', dir=path, model=1, heteronuc='N', proton='H', load_seq=0)

        # Read the relaxation data.
        self.relax.interpreter._Relax_data.read(self.run, 'R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'R2', '600', 600.0 * 1e6, 'r2.600.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'NOE', '600', 600.0 * 1e6, 'noe.600.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'R1', '500', 500.0 * 1e6, 'r1.500.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'R2', '500', 500.0 * 1e6, 'r2.500.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'NOE', '500', 500.0 * 1e6, 'noe.500.out', dir=path)

        # Setup other values.
        self.relax.interpreter._Diffusion_tensor.init(self.run, (1.601 * 1e7, 1.34, 72.4, 90-77.9), param_types=4)
        self.relax.interpreter._Value.set(self.run, [-172 * 1e-6, 1.02 * 1e-10], ['csa', 'bond_length'])
        self.relax.interpreter._Value.set(self.run, [0.8, 50 * 1e-12, 0.0], ['S2', 'te', 'Rex'])

        # Select the model.
        self.relax.interpreter._Model_free.select_model(self.run, model='m4')

        # Map the space.
        self.relax.interpreter._OpenDX.map(self.run, params=['theta', 'phi', 'Da'], res_num=2, inc=2, lower=[0, 0, -0.5*1e7], upper=[pi, 2.0*pi, 1.0*1e7], file='devnull')

        return 1


    def opendx_tm_s2_te(self, run):
        """The OpenDX {local_tm, S2, te} mapping test."""

        # Arguments.
        self.run = run

        # Create the run.
        self.relax.generic.runs.create(self.run, 'mf')

        # Path of the files.
        path = sys.path[-1] + '/test_suite/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Nuclei type
        self.relax.interpreter._Nuclei.nuclei('N')

        # Read the sequence.
        self.relax.interpreter._Sequence.read(self.run, file='noe.500.out', dir=path)

        # Read the relaxation data.
        self.relax.interpreter._Relax_data.read(self.run, 'R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'R2', '600', 600.0 * 1e6, 'r2.600.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'NOE', '600', 600.0 * 1e6, 'noe.600.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'R1', '500', 500.0 * 1e6, 'r1.500.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'R2', '500', 500.0 * 1e6, 'r2.500.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'NOE', '500', 500.0 * 1e6, 'noe.500.out', dir=path)

        # Setup other values.
        self.relax.interpreter._Value.set(self.run, [-172 * 1e-6, 1.02 * 1e-10], ['csa', 'bond_length'])

        # Select the model.
        self.relax.interpreter._Model_free.select_model(self.run, model='tm2')

        # Map the space.
        self.relax.interpreter._OpenDX.map(self.run, params=['local_tm', 'S2', 'te'], res_num=2, inc=2, file='devnull')

        return 1


    def opt_constr_bfgs_back_S2_0_970_te_2048_Rex_0_149(self, run):
        """Optimisation test.

        The optimisation options are:
            BFGS optimisation.
            Backtracking line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the run for optimisation.
        self.opt_setup_S2_0_970_te_2048_Rex_0_149(run)

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set(self.run, [1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('bfgs', 'back', run=self.run)


        # Test the optimisation statistics and parameter values.
        ########################################################

        # Alias the data structure.
        data = self.relax.data.res[self.run][1]

        # Error tolerance.
        error = 1e-8

        # Test the values.
        success = 1
        if not self.test_values(val1=0.970, val2=data.s2, error=error, name='S2 value'):
            success = 0
        if not self.test_values(val1=2048 * 1e-12, val2=data.te, error=error, name='te value (ns)', scale=1e9):
            success = 0
        if not self.test_values(val1=0.149 / (2.0 * pi * data.frq[0])**2, val2=data.rex, error=error, name='Rex value', scale=(2.0 * pi * data.frq[0])**2):
            success = 0
        if not self.test_values(val1=3.1024517431117421e-27, val2=data.chi2, error=1e-20, name='chi-squared value'):
            success = 0
        if not self.test_values(val1=203, val2=data.iter, name='iteration count', max=1):
            success = 0
        if not self.test_values(val1=955, val2=data.f_count, name='function count', max=1):
            success = 0
        if not self.test_values(val1=209, val2=data.g_count, name='gradient count', max=1):
            success = 0
        if not self.test_values(val1=0, val2=data.h_count, name='Hessian count', max=1):
            success = 0

        # Warning.
        if data.warning:
            print data.warning
            success = 0

        # Success.
        return success


    def opt_constr_bfgs_mt_S2_0_970_te_2048_Rex_0_149(self, run):
        """Optimisation test.

        The optimisation options are:
            BFGS optimisation.
            More and Thuente line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the run for optimisation.
        self.opt_setup_S2_0_970_te_2048_Rex_0_149(run)

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set(self.run, [1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('bfgs', 'mt', run=self.run)


        # Test the optimisation statistics and parameter values.
        ########################################################

        # Alias the data structure.
        data = self.relax.data.res[self.run][1]

        # Error tolerance.
        error = 1e-8

        # Test the values.
        success = 1
        if not self.test_values(val1=0.970, val2=data.s2, error=error, name='S2 value'):
            success = 0
        if not self.test_values(val1=2048 * 1e-12, val2=data.te, error=error, name='te value (ns)', scale=1e9):
            success = 0
        if not self.test_values(val1=0.149 / (2.0 * pi * data.frq[0])**2, val2=data.rex, error=error, name='Rex value', scale=(2.0 * pi * data.frq[0])**2):
            success = 0
        if not self.test_values(val1=3.1024517431117421e-27, val2=data.chi2, error=1e-20, name='chi-squared value'):
            success = 0
        if not self.test_values(val1=203, val2=data.iter, name='iteration count', max=1):
            success = 0
        if not self.test_values(val1=955, val2=data.f_count, name='function count', max=1):
            success = 0
        if not self.test_values(val1=209, val2=data.g_count, name='gradient count', max=1):
            success = 0
        if not self.test_values(val1=0, val2=data.h_count, name='Hessian count', max=1):
            success = 0

        # Warning.
        if data.warning:
            print data.warning
            success = 0

        # Success.
        return success


    def opt_constr_cd_back_S2_0_970_te_2048_Rex_0_149(self, run):
        """Optimisation test.

        The optimisation options are:
            Coordinate descent optimisation.
            Backtracking line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the run for optimisation.
        self.opt_setup_S2_0_970_te_2048_Rex_0_149(run)

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set(self.run, [1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('cd', 'back', max_iter=50, run=self.run)


        # Test the optimisation statistics and parameter values.
        ########################################################

        # Alias the data structure.
        data = self.relax.data.res[self.run][1]

        # Error tolerance.
        error = 1e-8

        # Test the values.
        success = 1
        if not self.test_values(val1=0.9097900390625, val2=data.s2, error=error, name='S2 value'):
            success = 0
        if not self.test_values(val1=2.5000000000000001e-11, val2=data.te, error=error, name='te value (ns)', scale=1e9):
            success = 0
        if not self.test_values(val1=1.24017333984375 / (2.0 * pi * data.frq[0])**2, val2=data.rex, error=error, name='Rex value', scale=(2.0 * pi * data.frq[0])**2):
            success = 0
        if not self.test_values(val1=53.476155463267176, val2=data.chi2, error=error, name='chi-squared value'):
            success = 0
        if not self.test_values(val1=50, val2=data.iter, name='iteration count', max=1):
            success = 0
        if not self.test_values(val1=131, val2=data.f_count, name='function count', max=1):
            success = 0
        if not self.test_values(val1=51, val2=data.g_count, name='gradient count', max=1):
            success = 0
        if not self.test_values(val1=0, val2=data.h_count, name='Hessian count', max=1):
            success = 0

        # Warning.
        if data.warning and not data.warning == 'Maximum number of iterations reached':
            print data.warning
            success = 0

        # Success.
        return success


    def opt_constr_cd_mt_S2_0_970_te_2048_Rex_0_149(self, run):
        """Optimisation test.

        The optimisation options are:
            Coordinate descent optimisation.
            More and Thuente line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the run for optimisation.
        self.opt_setup_S2_0_970_te_2048_Rex_0_149(run)

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set(self.run, [1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('cd', 'mt', run=self.run)


        # Test the optimisation statistics and parameter values.
        ########################################################

        # Alias the data structure.
        data = self.relax.data.res[self.run][1]

        # Error tolerance.
        error = 1e-8

        # Test the values.
        success = 1
        if not self.test_values(val1=0.970, val2=data.s2, error=error, name='S2 value'):
            success = 0
        if not self.test_values(val1=2048 * 1e-12, val2=data.te, error=error, name='te value (ns)', scale=1e9):
            success = 0
        if not self.test_values(val1=0.149 / (2.0 * pi * data.frq[0])**2, val2=data.rex, error=error, name='Rex value'):
            success = 0
        if not self.test_values(val1=2.34772342485e-18, val2=data.chi2, error=error, name='chi-squared value'):
            success = 0
        if not self.test_values(val1=198, val2=data.iter, name='iteration count', max=1):
            success = 0
        if not self.test_values(val1=757, val2=data.f_count, name='function count', max=1):
            success = 0
        if not self.test_values(val1=757, val2=data.g_count, name='gradient count', max=1):
            success = 0
        if not self.test_values(val1=0, val2=data.h_count, name='Hessian count', max=1):
            success = 0

        # Warning.
        if data.warning:
            print data.warning
            success = 0

        # Success.
        return success


    def opt_constr_newton_gmw_back_S2_0_970_te_2048_Rex_0_149(self, run):
        """Optimisation test.

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

        # Setup the run for optimisation.
        self.opt_setup_S2_0_970_te_2048_Rex_0_149(run)

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set(self.run, [1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('newton', 'gmw', 'back', run=self.run)


        # Test the optimisation statistics and parameter values.
        ########################################################

        # Alias the data structure.
        data = self.relax.data.res[self.run][1]

        # Error tolerance.
        error = 1e-8

        # Test the values.
        success = 1
        if not self.test_values(val1=0.970, val2=data.s2, error=error, name='S2 value'):
            success = 0
        if not self.test_values(val1=2048 * 1e-12, val2=data.te, error=error, name='te value (ns)', scale=1e9):
            success = 0
        if not self.test_values(val1=0.149 / (2.0 * pi * data.frq[0])**2, val2=data.rex, error=error, name='Rex value', scale=(2.0 * pi * data.frq[0])**2):
            success = 0
        if not self.test_values(val1=7.3040158179665562e-28, val2=data.chi2, error=1e-20, name='chi-squared value'):
            success = 0
        if not self.test_values(val1=18, val2=data.iter, name='iteration count', max=1):
            success = 0
        if not self.test_values(val1=96, val2=data.f_count, name='function count', max=1):
            success = 0
        if not self.test_values(val1=23, val2=data.g_count, name='gradient count', max=1):
            success = 0
        if not self.test_values(val1=18, val2=data.h_count, name='Hessian count', max=1):
            success = 0

        # Warning.
        if data.warning:
            print data.warning
            success = 0

        # Success.
        return success


    def opt_constr_newton_gmw_mt_S2_0_970_te_2048_Rex_0_149(self, run):
        """Optimisation test.

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

        # Setup the run for optimisation.
        self.opt_setup_S2_0_970_te_2048_Rex_0_149(run)

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set(self.run, [1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('newton', 'gmw', 'mt', run=self.run)


        # Test the optimisation statistics and parameter values.
        ########################################################

        # Alias the data structure.
        data = self.relax.data.res[self.run][1]

        # Error tolerance.
        error = 1e-8

        # Test the values.
        success = 1
        if not self.test_values(val1=0.970, val2=data.s2, error=error, name='S2 value'):
            success = 0
        if not self.test_values(val1=2048 * 1e-12, val2=data.te, error=error, name='te value (ns)', scale=1e9):
            success = 0
        if not self.test_values(val1=0.149 / (2.0 * pi * data.frq[0])**2, val2=data.rex, error=error, name='Rex value', scale=(2.0 * pi * data.frq[0])**2):
            success = 0
        if not self.test_values(val1=6.8756889983348349e-28, val2=data.chi2, error=1e-20, name='chi-squared value'):
            success = 0
        if not self.test_values(val1=22, val2=data.iter, name='iteration count', max=1):
            success = 0
        if not self.test_values(val1=159, val2=data.f_count, name='function count', max=1):
            success = 0
        if not self.test_values(val1=159, val2=data.g_count, name='gradient count', max=1):
            success = 0
        if not self.test_values(val1=22, val2=data.h_count, name='Hessian count', max=1):
            success = 0

        # Warning.
        if data.warning:
            print data.warning
            success = 0

        # Success.
        return success


    def opt_constr_sd_back_S2_0_970_te_2048_Rex_0_149(self, run):
        """Optimisation test.

        The optimisation options are:
            Steepest descent optimisation.
            Backtracking line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the run for optimisation.
        self.opt_setup_S2_0_970_te_2048_Rex_0_149(run)

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set(self.run, [1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('sd', 'back', max_iter=50, run=self.run)


        # Test the optimisation statistics and parameter values.
        ########################################################

        # Alias the data structure.
        data = self.relax.data.res[self.run][1]

        # Error tolerance.
        error = 1e-8

        # Test the values.
        success = 1
        if not self.test_values(val1=0.91579220834688024, val2=data.s2, error=error, name='S2 value'):
            success = 0
        if not self.test_values(val1=3.056865872253173e-13, val2=data.te, error=error, name='te value (ns)', scale=1e9):
            success = 0
        if not self.test_values(val1=0.34008409798366124 / (2.0 * pi * data.frq[0])**2, val2=data.rex, error=error, name='Rex value', scale=(2.0 * pi * data.frq[0])**2):
            success = 0
        if not self.test_values(val1=68.321956795264342, val2=data.chi2, error=error, name='chi-squared value'):
            success = 0
        if not self.test_values(val1=50, val2=data.iter, name='iteration count', max=1):
            success = 0
        if not self.test_values(val1=134, val2=data.f_count, name='function count', max=1):
            success = 0
        if not self.test_values(val1=51, val2=data.g_count, name='gradient count', max=1):
            success = 0
        if not self.test_values(val1=0, val2=data.h_count, name='Hessian count', max=1):
            success = 0

        # Warning.
        if data.warning and not data.warning == 'Maximum number of iterations reached':
            print data.warning
            success = 0

        # Success.
        return success


    def opt_constr_sd_mt_S2_0_970_te_2048_Rex_0_149(self, run):
        """Optimisation test.

        The optimisation options are:
            Steepest descent optimisation.
            More and Thuente line search.
            Constrained.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the run for optimisation.
        self.opt_setup_S2_0_970_te_2048_Rex_0_149(run)

        # Set up the initial model-free parameter values (bypass the grid search for speed).
        self.relax.interpreter._Value.set(self.run, [1.0, 0.0, 0.0], ['S2', 'te', 'Rex'])

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('sd', 'mt', max_iter=50, run=self.run)


        # Test the optimisation statistics and parameter values.
        ########################################################

        # Alias the data structure.
        data = self.relax.data.res[self.run][1]

        # Error tolerance.
        error = 1e-8

        # Test the values.
        success = 1
        if not self.test_values(val1=0.91619994957822126, val2=data.s2, error=error, name='S2 value'):
            success = 0
        if not self.test_values(val1=1.2319687570987945e-13, val2=data.te, error=error, name='te value (ns)', scale=1e9):
            success = 0
        if not self.test_values(val1=0.16249110942961512 / (2.0 * pi * data.frq[0])**2, val2=data.rex, error=error, name='Rex value', scale=(2.0 * pi * data.frq[0])**2):
            success = 0
        if not self.test_values(val1=73.843613546506191, val2=data.chi2, error=error, name='chi-squared value'):
            success = 0
        if not self.test_values(val1=50, val2=data.iter, name='iteration count', max=1):
            success = 0
        if not self.test_values(val1=108, val2=data.f_count, name='function count', max=1):
            success = 0
        if not self.test_values(val1=108, val2=data.g_count, name='gradient count', max=1):
            success = 0
        if not self.test_values(val1=0, val2=data.h_count, name='Hessian count', max=1):
            success = 0

        # Warning.
        if data.warning and not data.warning == 'Maximum number of iterations reached':
            print data.warning
            success = 0

        # Success.
        return success


    def opt_grid_search_S2_0_970_te_2048_Rex_0_149(self, run):
        """Optimisation test.

        The optimisation options are:
            Constrained grid search.

        The true data set is:
            S2  = 0.970
            te  = 2048 ps
            Rex = 0.149 s^-1
        """

        # Setup the run for optimisation.
        self.opt_setup_S2_0_970_te_2048_Rex_0_149(run)

        # Grid search.
        self.relax.interpreter._Minimisation.grid_search(self.run, inc=11)

        # Test the optimisation statistics and parameter values.
        ########################################################

        # Alias the data structure.
        data = self.relax.data.res[self.run][1]

        # Error tolerance.
        error = 1e-8

        # Test the values.
        success = 1
        if not self.test_values(val1=1.0, val2=data.s2, error=error, name='S2 value'):
            success = 0
        if not self.test_values(val1=0.0, val2=data.te, error=error, name='te value (ns)', scale=1e9):
            success = 0
        if not self.test_values(val1=0.0, val2=data.rex, error=error, name='Rex value'):
            success = 0
        if not self.test_values(val1=3.9844117908982288, val2=data.chi2, error=error, name='chi-squared value'):
            success = 0
        if not self.test_values(val1=1331, val2=data.iter, name='iteration count', max=1):
            success = 0
        if not self.test_values(val1=1331, val2=data.f_count, name='function count', max=1):
            success = 0
        if not self.test_values(val1=0, val2=data.g_count, name='gradient count', max=1):
            success = 0
        if not self.test_values(val1=0, val2=data.h_count, name='Hessian count', max=1):
            success = 0

        # Warning.
        if data.warning:
            print data.warning
            success = 0

        # Success.
        return success


    def opt_setup_S2_0_970_te_2048_Rex_0_149(self, run):
        """Setup the run for testing optimisation.

        The data set is:
            S2 = 0.970.
            te = 2048 ps.
            Rex = 0.149 s^-1.
        """

        # Create the run.
        self.run = run
        self.relax.generic.runs.create(self.run, 'mf')

        # Path of the files.
        path = sys.path[-1] + '/test_suite/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Nuclei type
        self.relax.interpreter._Nuclei.nuclei('N')

        # Load the sequence.
        self.relax.interpreter._Sequence.read(self.run, 'noe.500.out', dir=path)

        # Load the relaxation data.
        self.relax.interpreter._Relax_data.read(self.run, 'R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'R2', '600', 600.0 * 1e6, 'r2.600.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'NOE', '600', 600.0 * 1e6, 'noe.600.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'R1', '500', 500.0 * 1e6, 'r1.500.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'R2', '500', 500.0 * 1e6, 'r2.500.out', dir=path)
        self.relax.interpreter._Relax_data.read(self.run, 'NOE', '500', 500.0 * 1e6, 'noe.500.out', dir=path)

        # Setup other values.
        self.relax.interpreter._Diffusion_tensor.init(self.run, 10e-9, fixed=1)
        self.relax.interpreter._Value.set(self.run, 1.02 * 1e-10, 'bond_length')
        self.relax.interpreter._Value.set(self.run, -160 * 1e-6, 'csa')

        # Select the model-free model.
        self.relax.interpreter._Model_free.select_model(run=self.run, model='m4')


    def read_relax_data(self, run):
        """The relaxation data reading test."""

        # Arguments.
        self.run = run

        # Create the run.
        self.relax.generic.runs.create(self.run, 'mf')

        # Path of the files.
        path = sys.path[-1] + '/test_suite/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(self.run, file='noe.500.out', dir=path)

        # Read the relaxation data.
        self.relax.interpreter._Relax_data.read(self.run, 'R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)

        # Test the data.
        if self.relax.data.res[self.run][1].relax_data[0] != 1.3874977659397683:
            print "The relaxation data does not match."
            return

        # Test the error.
        if self.relax.data.res[self.run][1].relax_error[0] != 0.027749955318795365:
            print "The relaxation error does not match."
            return

        return 1


    def read_results(self, run):
        """The results reading test."""

        # Arguments.
        self.run = run

        # Load the original state.
        self.relax.interpreter._State.load(file='orig_state', dir=sys.path[-1] + '/test_suite/data/model_free')

        # Create the run.
        self.relax.generic.runs.create(self.run, 'mf')

        # Read the results.
        self.relax.interpreter._Results.read(self.run, dir=sys.path[-1] + '/test_suite/data/model_free')

        # Print out.
        print "\nTesting the integrity of the loaded data.\n"

        # Diffusion tensor type.
        if self.relax.data.diff['orig'].type != self.relax.data.diff[self.run].type:
            print "The diffusion tensor types do not match."
            return

        # tm.
        if self.relax.data.diff['orig'].tm != self.relax.data.diff[self.run].tm:
            print "The tm values do not match."
            return

        # Loop over the residues of the original data.
        for i in xrange(len(self.relax.data.res['orig'])):
            # Aliases
            orig_data = self.relax.data.res['orig'][i]
            new_data = self.relax.data.res[self.run][i]

            # Residue alias.
            self.orig_res = `orig_data.num` + orig_data.name
            self.new_res = `new_data.num` + new_data.name

            # Residue numbers.
            if orig_data.num != new_data.num:
                self.print_error('residue numbers')
                return

            # Residue names.
            if orig_data.name != new_data.name:
                self.print_error('residue names')
                return

            # Selection.
            if orig_data.select != new_data.select:
                self.print_error('selection flags')
                return

            # Skip unselected residues.
            if not orig_data.select:
                continue

            # Model-free model test.
            if orig_data.model != new_data.model:
                self.print_error('model-free models')
                return

            # Model-free parameter set test.
            if orig_data.params != new_data.params:
                self.print_error('model-free parameter sets')
                return

            # S2 test.
            if orig_data.s2 != new_data.s2:
                self.print_error('S2 values')
                return

            # S2f test.
            if orig_data.s2f != new_data.s2f:
                self.print_error('S2f values')
                return

            # S2s test.
            if orig_data.s2s != new_data.s2s:
                self.print_error('S2s values')
                return

            # local tm test.
            if orig_data.local_tm != new_data.local_tm:
                self.print_error('local tm values')
                return

            # te test.
            if orig_data.te != new_data.te:
                self.print_error('te values')
                return

            # tf test.
            if orig_data.tf != new_data.tf:
                self.print_error('tf values')
                return

            # ts test.
            if orig_data.ts != new_data.ts:
                self.print_error('ts values')
                return

            # Rex test.
            if orig_data.rex != new_data.rex:
                self.print_error('Rex values')
                return

            # bond length test.
            if orig_data.r != new_data.r:
                self.print_error('bond length values')
                return

            # CSA test.
            if orig_data.csa != new_data.csa:
                self.print_error('CSA values')
                return

            # Chi-squared test.
            if orig_data.chi2 != new_data.chi2:
                self.print_error('Chi-squared values')
                return

            # Iteration number test.
            if orig_data.iter != new_data.iter:
                self.print_error('iteration numbers')
                return

            # Function count test.
            if orig_data.f_count != new_data.f_count:
                self.print_error('function counts')
                return

            # Gradient count test.
            if orig_data.g_count != new_data.g_count:
                self.print_error('gradient counts')
                return

            # Hessian count test.
            if orig_data.h_count != new_data.h_count:
                self.print_error('Hessian counts')
                return

            # Warning test.
            if orig_data.warning != new_data.warning:
                self.print_error('warnings')
                return

            # Relaxation data lables test.
            if orig_data.ri_labels != new_data.ri_labels:
                self.print_error('relaxation data labels')
                return

            # Relaxation data remap table test.
            if orig_data.remap_table != new_data.remap_table:
                self.print_error('relaxation data remap tables')
                return

            # Frequency lables test.
            if orig_data.frq_labels != new_data.frq_labels:
                self.print_error('frequency labels')
                return

            # Relaxation data test.
            if orig_data.relax_data != new_data.relax_data:
                self.print_error('relaxation data')
                return

            # Relaxation data error test.
            if orig_data.relax_error != new_data.relax_error:
                self.print_error('relaxation data errors')
                return

        # Success.
        print "The data structures have been created successfully."
        return 1


    def print_error(self, name):
        """Function for printing a residue mismatch."""

        print "The " + name + " of " + self.orig_res + " and " + self.new_res + " do not match."


    def select_m4(self, run):
        """Testing the selection of model-free model m4."""

        # Arguments.
        self.run = run

        # Create the run.
        self.relax.generic.runs.create(self.run, 'mf')

        # Path of the files.
        path = sys.path[-1] + '/test_suite/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(self.run, file='noe.500.out', dir=path)

        # Select the model.
        self.relax.interpreter._Model_free.select_model(self.run, model='m4')

        # Test the model.
        if self.relax.data.res[self.run][1].model != 'm4':
            print "The model has not been selected."
            return

        # Test the parameters.
        if self.relax.data.res[self.run][1].params != ['S2', 'te', 'Rex']:
            print "The parameters are incorrect."
            return

        return 1


    def set_bond_length(self, run):
        """Testing the setting of the bond length."""

        # Arguments.
        self.run = run

        # Create the run.
        self.relax.generic.runs.create(self.run, 'mf')

        # Path of the files.
        path = sys.path[-1] + '/test_suite/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(self.run, file='noe.500.out', dir=path)

        # Set the CSA value.
        self.relax.interpreter._Value.set(self.run, 1.02 * 1e-10, 'bond_length')

        # Test the value.
        if self.relax.data.res[self.run][1].r != 1.02 * 1e-10:
            print "The bond length has not been set correctly."
            return

        return 1


    def set_csa(self, run):
        """Testing the setting of the CSA value."""

        # Arguments.
        self.run = run

        # Create the run.
        self.relax.generic.runs.create(self.run, 'mf')

        # Path of the files.
        path = sys.path[-1] + '/test_suite/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(self.run, file='noe.500.out', dir=path)

        # Set the CSA value.
        self.relax.interpreter._Value.set(self.run, -172 * 1e-6, 'csa')

        # Test the value.
        if self.relax.data.res[self.run][1].csa != -172*1e-6:
            print "The CSA value has not been set correctly."
            return

        return 1


    def set_csa_bond_length(self, run):
        """Testing the setting of the CSA value and bond length simultaneously."""

        # Arguments.
        self.run = run

        # Create the run.
        self.relax.generic.runs.create(self.run, 'mf')

        # Path of the files.
        path = sys.path[-1] + '/test_suite/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(self.run, file='noe.500.out', dir=path)

        # Set the CSA value and bond length simultaneously.
        self.relax.interpreter._Value.set(self.run, [-172 * 1e-6, 1.02 * 1e-10], ['csa', 'bond_length'])

        # Test the CSA value.
        if self.relax.data.res[self.run][1].csa != -172*1e-6:
            print "The CSA value has not been set correctly."
            return

        # Test the bond length.
        if self.relax.data.res[self.run][1].r != 1.02 * 1e-10:
            print "The bond length has not been set correctly."
            return

        return 1


    def test_values(self, val1, val2, error=None, name=None, scale=1.0, max=0):
        """Test that value 1 is equal to value 2, within the error."""

        # Failure (with an error tolerance).
        if error:
            if val2*scale < val1*scale - error or val2*scale > val1*scale + error:
                print "The " + name + " of " + `val2*scale` + " should be within +/- " + `error` + " of " + `val1*scale` + "."
                return

        # Failure (val2 is greater than val1).
        elif max:
            if val2 > val1:
                print "The " + name + " of " + `val2*scale` + " should be less than " + `val1*scale` + "."
                return

        # Failure (with no error tolerance).
        else:
            if val2 != val1:
                print "The " + name + " of " + `val2*scale` + " should be " + `val1*scale` + "."
                return

        # Success.
        return 1


