###############################################################################
#                                                                             #
# Copyright (C) 2006-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
from os import F_OK, access, sep
from shutil import rmtree
from tempfile import mkdtemp

# relax module imports.
from auto_analyses import relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from pipe_control.mol_res_spin import spin_loop
from specific_analyses.relax_disp.disp_data import get_curve_type
from specific_analyses.relax_disp.variables import MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_LIST_CPMG, MODEL_LM63, MODEL_M61B, MODEL_NOREX, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_R2EFF
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Relax_disp(SystemTestCase):
    """Class for testing various aspects specific to relaxation dispersion curve-fitting."""

    def __init__(self, methodName='runTest'):
        """Skip certain tests if the C modules are non-functional.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(Relax_disp, self).__init__(methodName)

        # Missing module.
        if not dep_check.C_module_exp_fn:
            # The list of tests to skip.
            to_skip = [
                "test_exp_fit",
                "test_m61_exp_data_to_m61"
            ]

            # Store in the status object. 
            if methodName in to_skip:
                status.skipped_tests.append([methodName, 'Relax curve-fitting C module', self._skip_type])


    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('relax_disp', 'relax_disp')

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()
        self.tmpdir = ds.tmpdir


    def tearDown(self):
        """Reset the relax data storage object."""

        # Remove the temporary directory.
        rmtree(self.tmpdir)

        # Reset the relax data storage object.
        ds.__reset__()


    def setup_hansen_cpmg_data(self, model=None):
        """Set up the data for the test_hansen_cpmg_data_*() system tests.

        @keyword model: The name of the model which will be tested.
        @type model:    str
        """

        # Create the data pipe and load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'
        self.interpreter.pipe.create(pipe_name='base pipe', pipe_type='relax_disp')
        self.interpreter.results.read(data_path+sep+'base_pipe')

        # Set the nuclear isotope data.
        self.interpreter.spin.isotope('15N')

        # Create the R2eff data pipe and load the results.
        self.interpreter.pipe.create(pipe_name='R2eff', pipe_type='relax_disp')
        self.interpreter.pipe.switch(pipe_name='R2eff')
        self.interpreter.results.read(data_path+sep+'r2eff_pipe')

        # The model data pipe.
        self.interpreter.pipe.copy(pipe_from='base pipe', pipe_to=model, bundle_to='relax_disp')
        self.interpreter.pipe.switch(pipe_name=model)

        # Set the model.
        self.interpreter.relax_disp.select_model(model=model)

        # Copy the data.
        self.interpreter.value.copy(pipe_from='R2eff', pipe_to=model, param='r2eff')


    def setup_kteilum_fmpoulsen_makke_cpmg_data(self, model=None, expfolder=None):
        """Set up the data for the test_kteilum_fmpoulsen_makke_cpmg_data_*() system tests.

        @keyword model: The name of the model which will be tested.
        @type model:    str
        """

        # Create the data pipe and load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'KTeilum_FMPoulsen_MAkke_2006'+sep+expfolder
        self.interpreter.pipe.create(pipe_name='base pipe', pipe_type='relax_disp')
        self.interpreter.results.read(data_path+sep+'ini_setup_trunc')

        # Create the R2eff data pipe and load the results.
        self.interpreter.pipe.create(pipe_name='R2eff', pipe_type='relax_disp')
        self.interpreter.pipe.switch(pipe_name='R2eff')
        self.interpreter.results.read(data_path+sep+'r2eff_pipe_trunc')

        # The model data pipe.
        self.interpreter.pipe.copy(pipe_from='base pipe', pipe_to=model, bundle_to='relax_disp')
        self.interpreter.pipe.switch(pipe_name=model)

        # Set the model.
        self.interpreter.relax_disp.select_model(model=model)

        # Copy the data.
        self.interpreter.value.copy(pipe_from='R2eff', pipe_to=model, param='r2eff')


    def test_bug_21081_disp_cluster_fail(self):
        """U{Bug #21081<https://gna.org/bugs/?21081>} catch, the failure of a cluster analysis when spins are deselected."""

        # Clear the data store.
        self.interpreter.reset()

        # Load the state.
        state = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'saved_states'+sep+'bug_21081_disp_cluster_fail.bz2'
        self.interpreter.state.load(state, force=True)

        # Model selection - to catch the failure.
        self.interpreter.model_selection(method='AIC', modsel_pipe='final', bundle='relax_disp', pipes=['No Rex', 'CR72'])


    def test_curve_type_cpmg_fixed_time(self):
        """Test the curve type detection using the Dr. Flemming Hansen's CPMG fixed time test data."""

        # Reset.
        self.interpreter.reset()

        # Load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'
        self.interpreter.state.load(data_path+sep+'r2eff_values')

        # The type.
        curve_type = get_curve_type(id='500_133.33.in')
        self.assertEqual(curve_type, 'fixed time')


    def test_curve_type_r1rho_exponential(self, model=None):
        """Test the curve type detection using the 'M61' exponential test data."""

        # Reset.
        self.interpreter.reset()

        # Load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'r1rho_on_res_m61'
        self.interpreter.state.load(data_path+sep+'r2eff_values')

        # The type.
        curve_type = get_curve_type(id='nu_2000_ncyc9')
        self.assertEqual(curve_type, 'exponential')


    def test_curve_type_r1rho_fixed_time(self, model=None):
        """Test the curve type detection using the 'TP02' fixed time test data."""

        # Reset.
        self.interpreter.reset()

        # Load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'r1rho_off_res_tp02'
        self.interpreter.state.load(data_path+sep+'r2eff_values')

        # The type.
        curve_type = get_curve_type(id='nu_1000.0_500MHz')
        self.assertEqual(curve_type, 'fixed time')


    def test_dpl94_data_to_dpl94(self):
        """Test the relaxation dispersion 'DPL94' model curve fitting to fixed time synthetic data."""

        # Fixed time variable.
        ds.fixed = True

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'r1rho_on_res_dpl94.py')

        # The original parameters.
        i0 = [100000.0, 20000.0]
        r1rho_prime = [2.25, 24.0]
        pA = 0.7
        kex = 1000.0
        delta_omega = [1.0, 2.0]
        phi_ex = []
        for i in range(2):
            phi_ex.append(pA * (1.0 - pA) * delta_omega[i]**2)

        # Switch to the 'DPL94' model data pipe, then check for each spin.
        self.interpreter.pipe.switch('DPL94')
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[0]/10, r1rho_prime[spin_index]/10, 2)
            self.assertAlmostEqual(spin.phi_ex, phi_ex[spin_index], 2)
            self.assertAlmostEqual(spin.kex/1000.0, kex/1000.0, 2)

            # Increment the spin index.
            spin_index += 1


    def test_exp_fit(self):
        """Test the relaxation dispersion 'exp_fit' model curve fitting."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'exp_fit.py')

        # The original exponential curve parameters.
        res_data = [
            [15., 10., 20000., 25000.],
            [12., 11., 50000., 51000.],
            [17., 9., 100000., 96000.]
        ]

        # List of parameters which do not belong to the model.
        blacklist = ['cpmg_frqs', 'r2', 'rex', 'kex', 'r2a', 'k_AB', 'dw']

        # Checks for each residue.
        for i in range(len(res_data)):
            # Printout.
            print("\nResidue number %s." % (i+1))

            # Check the fitted parameters.
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].r2eff['1200.00000000_1000.000'], res_data[i][0], places=2)
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].r2eff['1200.00000000_2000.000'], res_data[i][1], places=2)
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].i0['1200.00000000_1000.000']/10000, res_data[i][2]/10000, places=3)
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].i0['1200.00000000_2000.000']/10000, res_data[i][3]/10000, places=3)

            # Check the simulation errors.
            self.assert_(cdp.mol[0].res[i].spin[0].r2eff_err['1200.00000000_1000.000'] < 5.0)
            self.assert_(cdp.mol[0].res[i].spin[0].r2eff_err['1200.00000000_2000.000'] < 5.0)
            self.assert_(cdp.mol[0].res[i].spin[0].i0_err['1200.00000000_1000.000']/10000 < 5.0)
            self.assert_(cdp.mol[0].res[i].spin[0].i0_err['1200.00000000_2000.000']/10000 < 5.0)

            # Check that certain parameters are not present.
            for param in blacklist:
                print("\tChecking for the absence of the '%s' parameter." % param)
                self.assert_(not hasattr(cdp.mol[0].res[i].spin[0], param))

        # Check the clustering information.
        self.assert_(hasattr(cdp, 'clustering'))
        keys = ['free spins', 'cluster']
        for key in keys:
            self.assert_(key in cdp.clustering)
        self.assert_('test' not in cdp.clustering)
        self.assertEqual(cdp.clustering['free spins'], [':2@N'])
        self.assertEqual(cdp.clustering['cluster'], [':1@N', ':3@N'])


    def test_hansen_catia_input(self):
        """Conversion of Dr. Flemming Hansen's CPMG R2eff values into input files for CATIA.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Load the state, preserving the temp directory.
        tmpdir = ds.tmpdir
        state = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'+sep+'r2eff_values'
        self.interpreter.state.load(state, force=True)
        ds.tmpdir = tmpdir

        # The spin isotopes.
        self.interpreter.spin.isotope("15N")

        # Generate the input files.
        self.interpreter.relax_disp.catia_input(dir=ds.tmpdir, force=True)

        # Check the r2eff set files.
        print("\nChecking the R2eff input set files.")
        files = ['data_set_500.inp', 'data_set_500.inp']
        for file in files:
            self.assert_(access(tmpdir+sep+file, F_OK))
        data_set_500 = [
            "ID=500\n",
            "Sfrq = 500\n",
            "Temperature = 0.0\n",
            "Nucleus = N15\n",
            "Couplednucleus = H1\n",
            "Time_equil = 0.0\n",
            "Pwx_cp = 0.0\n",
            "Taub = 0.0\n",
            "Time_T2 = 0.03\n",
            "Xcar = 0.0\n",
            "Seqfil = CW_CPMG\n",
            "Minerror = (2.%;0.5/s)\n",
            "Basis = (Iph_7)\n",
            "Format = (0;1;2)\n",
            "DataDirectory = /tmp/tmpNjOGNG/input_r2eff\n",
            "Data = (\n",
            " [70N;spin_70_N_500.cpmg];\n",
            " [71N;spin_71_N_500.cpmg];\n",
            ")\n",
        ]
        file = open(tmpdir+sep+files[0])
        lines = file.readlines()
        file.close()
        for i in range(len(data_set_500)):
            # Skip the data directory, as this is a random file name.
            if i == 14:
                continue

            self.assertEqual(data_set_500[i], lines[i])

        # Check the r2eff files.
        print("\nChecking the R2eff input files.")
        files = ['spin_70_N_500.cpmg', 'spin_70_N_800.cpmg', 'spin_71_N_500.cpmg', 'spin_71_N_800.cpmg']
        for file in files:
            self.assert_(access(tmpdir+sep+'input_r2eff'+sep+file, F_OK))
        spin_70_N_500 = [
            "#        nu_cpmg(Hz)              R2(1/s)              Esd(R2)\n",
            "  66.666600000000003   16.045540885533605    0.489669451336779\n",
            " 133.333300000000008   14.877924861181727    0.477531187340500\n",
            " 200.000000000000000   14.357820247260586    0.472298099353208\n",
            " 266.666600000000017   12.664494620416516    0.455978606729610\n",
            " 333.333300000000008   12.363204802467891    0.453187241985999\n",
            " 400.000000000000000   11.092532381134513    0.441776288331164\n",
            " 466.666600000000017   10.566090057649893    0.437216362327354\n",
            " 533.333300000000008    9.805806894657803    0.430799912332094\n",
            " 600.000000000000000    9.564300692201730    0.428802849204706\n",
            " 666.666600000000017    9.015633750407980    0.424338378820437\n",
            " 733.333300000000008    8.607764958055581    0.421084079770695\n",
            " 800.000000000000000    8.279997179221338    0.418508231707648\n",
            " 866.666600000000017    8.474535940963516    0.420032859678987\n",
            " 933.333300000000008    8.158972897365194    0.417565915034600\n",
            "1000.000000000000000    7.988630509501972    0.416247574098482\n"
        ]
        file = open(tmpdir+sep+'input_r2eff'+sep+files[0])
        lines = file.readlines()
        file.close()
        for i in range(len(lines)):
            print(lines[i][:-1])
        for i in range(len(spin_70_N_500)):
            self.assertEqual(spin_70_N_500[i], lines[i])

        # Check the main file.
        print("\nChecking the main CATIA execution file.")
        main_file = [
            "ReadDataset(data_set_500.inp)\n",
            "ReadDataset(data_set_800.inp)\n",
            "ReadParam_Global(ParamGlobal.inp)\n",
            "ReadParam_Local(ParamSet1.inp)\n",
            "\n",
            "FreeLocalParam(all;Omega;false)\n",
            "FreeLocalParam(all;R1iph_500;false)\n",
            "FreeLocalParam(all;R1iph_800;false)\n",
            "\n",
            "Minimize(print=y;tol=1e-25;maxiter=10000000)\n",
            "\n",
            "PrintParam(output/GlobalParam.fit;global)\n",
            "PrintParam(output/DeltaOmega.fit;DeltaO)\n",
            "PrintData(output/)\n",
            "\n",
            "ChiSq(all;all)\n",
            "exit(0)\n"
        ]
        file = open("%s%sFit.catia" % (ds.tmpdir, sep))
        lines = file.readlines()
        file.close()
        for i in range(len(main_file)):
            self.assertEqual(main_file[i], lines[i])


    def test_hansen_cpmg_data_auto_analysis(self):
        """Test of the dispersion auto-analysis using Dr. Flemming Hansen's CPMG data.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Set the model.
        ds.models = [
            MODEL_NOREX,
            MODEL_LM63,
            MODEL_CR72,
            MODEL_IT99
        ]

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'hansen_data.py')

        # The 'No Rex' model checks.
        self.interpreter.pipe.switch(pipe_name='No Rex')
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[0], 10.5340573632181, 4)
        self.assertAlmostEqual(spin70.r2[1], 16.1113049920324, 4)
        self.assertAlmostEqual(spin70.chi2, 2832.28562307, 4)
        self.assertAlmostEqual(spin71.r2[0], 5.83137814994754, 4)
        self.assertAlmostEqual(spin71.chi2, 73.6219146835821, 4)

        # The 'LM63' model checks.
        self.interpreter.pipe.switch(pipe_name='LM63')
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.15g %20.15g" % ("phi_ex", spin70.phi_ex, spin71.phi_ex))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[0], 6.7725779040626, 4)
        self.assertAlmostEqual(spin70.r2[1], 6.6495102881274, 4)
        self.assertAlmostEqual(spin70.phi_ex, 0.308228782539112, 4)
        self.assertAlmostEqual(spin70.kex/10000, 4644.35027966526/10000, 4)
        self.assertAlmostEqual(spin70.chi2, 137.64638621224, 4)
        self.assertAlmostEqual(spin71.r2[0], 4.92986568906445, 4)
        self.assertAlmostEqual(spin71.phi_ex, 0.0595701347673553, 4)
        self.assertAlmostEqual(spin71.kex/10000, 2566.66176813506/10000, 4)
        self.assertAlmostEqual(spin71.chi2, 2.31424715490254, 4)

        # The 'CR72' model checks.  These models have not reached the minima due to the low quality optimisation!
        self.interpreter.pipe.switch(pipe_name='CR72')
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[0], 6.97532271825192, 4)
        self.assertAlmostEqual(spin70.r2[1], 9.45051817816538, 4)
        self.assertAlmostEqual(spin70.pA, 0.989800346795472, 4)
        self.assertAlmostEqual(spin70.dw, 5.61326926915313, 4)
        self.assertAlmostEqual(spin70.kex/10000, 1713.02295468519/10000, 4)
        self.assertAlmostEqual(spin70.chi2, 17.3955972313639, 4)
        self.assertAlmostEqual(spin71.r2[0], 0.589453313816438, 2)
        self.assertAlmostEqual(spin71.pA, 0.500005674625128, 2)
        self.assertAlmostEqual(spin71.dw, 199.873875627265, 2)
        self.assertAlmostEqual(spin71.kex, 10.7154862578618, 2)
        self.assertAlmostEqual(spin71.chi2, 57.9468501661789, 2)


    def test_hansen_cpmg_data_auto_analysis_numeric(self):
        """Test of the numeric model only dispersion auto-analysis using Dr. Flemming Hansen's CPMG data.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Set the model and numeric flag.
        ds.models = [
            MODEL_NOREX,
            MODEL_CR72,
            MODEL_NS_CPMG_2SITE_EXPANDED
        ]
        ds.numeric_only = True

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'hansen_data.py')

        # The 'No Rex' model checks.
        self.interpreter.pipe.switch(pipe_name='No Rex')
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[0], 10.5340573632181, 4)
        self.assertAlmostEqual(spin70.r2[1], 16.1113049920324, 4)
        self.assertAlmostEqual(spin70.chi2, 2832.28562307, 4)
        self.assertAlmostEqual(spin71.r2[0], 5.83137814994754, 4)
        self.assertAlmostEqual(spin71.chi2, 73.6219146835821, 4)

        # The 'CR72' model checks.  These models have not reached the minima due to the low quality optimisation!
        self.interpreter.pipe.switch(pipe_name='CR72')
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[0], 6.97532271825192, 4)
        self.assertAlmostEqual(spin70.r2[1], 9.45051817816538, 4)
        self.assertAlmostEqual(spin70.pA, 0.989800346795472, 4)
        self.assertAlmostEqual(spin70.dw, 5.61326926915313, 4)
        self.assertAlmostEqual(spin70.kex/10000, 1713.02295468519/10000, 4)
        self.assertAlmostEqual(spin70.chi2, 17.3955972313639, 4)
        self.assertAlmostEqual(spin71.r2[0], 0.589453313816438, 2)
        self.assertAlmostEqual(spin71.pA, 0.500005674625128, 2)
        self.assertAlmostEqual(spin71.dw, 199.873875627265, 2)
        self.assertAlmostEqual(spin71.kex, 10.7154862578618, 2)
        self.assertAlmostEqual(spin71.chi2, 57.9468501661789, 2)

        # The 'NS CPMG 2-site expanded' model checks.  These models have not reached the minima due to the low quality optimisation!
        self.interpreter.pipe.switch(pipe_name='NS CPMG 2-site expanded')
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[0], 6.96101862173876, 4)
        self.assertAlmostEqual(spin70.r2[1], 9.43558150234607, 4)
        self.assertAlmostEqual(spin70.pA, 0.989640734323076, 4)
        self.assertAlmostEqual(spin70.dw, 5.67778572185308, 4)
        self.assertAlmostEqual(spin70.kex/10000, 1675.71048406429/10000, 4)
        self.assertAlmostEqual(spin70.chi2, 16.9361822411228, 4)
        self.assertAlmostEqual(spin71.r2[0], 0.000848665494171463, 2)
        self.assertAlmostEqual(spin71.pA, 0.655296796352596, 2)
        self.assertAlmostEqual(spin71.dw, 250.635584872988, 2)
        self.assertAlmostEqual(spin71.kex, 16.910452128491, 2)
        self.assertAlmostEqual(spin71.chi2, 69.4759976405928, 2)

        # The final data pipe checks.
        self.interpreter.pipe.switch(pipe_name='final')
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]
        self.assertEqual(spin70.model, 'NS CPMG 2-site expanded')
        self.assertEqual(spin71.model, 'No Rex')


    def test_hansen_cpmg_data_to_cr72(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the CR72 dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='CR72')

        # Alias the spins.
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]

        # Set the initial parameter values.
        spin70.r2 = [7, 9]
        spin70.pA = 0.9
        spin70.dw = 6.0
        spin70.kex = 1500.0
        spin71.r2 = [5, 9]
        spin71.pA = 0.9
        spin71.dw = 4.0
        spin71.kex = 1900.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[0], 6.9752522000508, 4)
        self.assertAlmostEqual(spin70.r2[1], 9.4502142463071, 4)
        self.assertAlmostEqual(spin70.pA, 0.989800155102415, 4)
        self.assertAlmostEqual(spin70.dw, 5.61343657055352, 4)
        self.assertAlmostEqual(spin70.kex/1000, 1712.96280544115/1000, 4)
        self.assertAlmostEqual(spin70.chi2, 17.395594997608, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[0], 4.98082001120432, 4)
        self.assertAlmostEqual(spin71.pA, 0.996612995705823, 4)
        self.assertAlmostEqual(spin71.dw, 4.34893375911521, 4)
        self.assertAlmostEqual(spin71.kex/1000, 1937.1784079176/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 2.22439157827035, 4)

        # Test the conversion to k_AB from kex and pA.
        self.assertEqual(spin70.k_AB, spin70.kex * (1.0 - spin70.pA))
        self.assertEqual(spin71.k_AB, spin71.kex * (1.0 - spin71.pA))

        # Test the conversion to k_BA from kex and pA.
        self.assertEqual(spin70.k_BA, spin70.kex * spin70.pA)
        self.assertEqual(spin71.k_BA, spin71.kex * spin71.pA)


    def test_hansen_cpmg_data_to_cr72_full(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the CR72 full dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='CR72 full')

        # Alias the spins.
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]

        # Set the initial parameter values.
        spin70.r2a = [7, 9]
        spin70.r2b = [7, 9]
        spin70.pA = 0.9
        spin70.dw = 6.0
        spin70.kex = 1500.0
        spin71.r2a = [5, 9]
        spin71.r2b = [5, 9]
        spin71.pA = 0.9
        spin71.dw = 4.0
        spin71.kex = 1900.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2A (500 MHz)", spin70.r2a[0], spin71.r2a[0]))
        print("%-20s %20.15g %20.15g" % ("R2B (500 MHz)", spin70.r2b[0], spin71.r2b[0]))
        print("%-20s %20.15g %20.15g" % ("R2A (800 MHz)", spin70.r2a[1], spin71.r2a[1]))
        print("%-20s %20.15g %20.15g" % ("R2B (800 MHz)", spin70.r2b[1], spin71.r2b[1]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2a[0], 7.01193443499926, 4)
        self.assertAlmostEqual(spin70.r2b[0], 6.21781284622842e-05, 4)
        self.assertAlmostEqual(spin70.r2a[1], 9.30618449313396, 4)
        self.assertAlmostEqual(spin70.r2b[1], 27.7706293556294, 4)
        self.assertAlmostEqual(spin70.pA, 0.989690841471004, 4)
        self.assertAlmostEqual(spin70.dw, 5.58311178274918, 4)
        self.assertAlmostEqual(spin70.kex/1000, 1727.86626749975/1000, 4)
        self.assertAlmostEqual(spin70.chi2, 16.479033262968, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2a[0], 4.92135078444124, 4)
        self.assertAlmostEqual(spin71.r2b[0], 22.276785581656, 4)
        self.assertAlmostEqual(spin71.pA, 0.996537558351309, 4)
        self.assertAlmostEqual(spin71.dw, 4.33777787825605, 4)
        self.assertAlmostEqual(spin71.kex/1000, 1922.12839512671/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 2.22439040805535, 4)

        # Test the conversion to k_AB from kex and pA.
        self.assertEqual(spin70.k_AB, spin70.kex * (1.0 - spin70.pA))
        self.assertEqual(spin71.k_AB, spin71.kex * (1.0 - spin71.pA))

        # Test the conversion to k_BA from kex and pA.
        self.assertEqual(spin70.k_BA, spin70.kex * spin70.pA)
        self.assertEqual(spin71.k_BA, spin71.kex * spin71.pA)


    def test_hansen_cpmg_data_to_it99(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the IT99 dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='IT99')

        # Alias the spins.
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]

        # Set the initial parameter values.
        spin70.r2 = [7, 10]
        spin70.phi_ex = 0.8
        spin70.padw2 = 260.0
        spin70.tex = 2e-4
        spin71.r2 = [5, 9]
        spin71.phi_ex = 0.1
        spin71.padw2 = 0.0001
        spin71.tex = 1e-4

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-10, grad_tol=None, max_iter=10000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.15g %20.15g" % ("phi_ex", spin70.phi_ex, spin71.phi_ex))
        print("%-20s %20.15g %20.15g" % ("padw2", spin70.padw2, spin71.padw2))
        print("%-20s %20.15g %20.15g" % ("tex", spin70.tex, spin71.tex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[0], 7.24913359483782, 4)
        self.assertAlmostEqual(spin70.r2[1], 10.0721943688644, 4)
        self.assertAlmostEqual(spin70.phi_ex, 0.824075664284934, 4)
        self.assertAlmostEqual(spin70.padw2, 264.941131087762, 4)
        self.assertAlmostEqual(spin70.tex*1000, 0.00020445116006575*1000, 4)
        self.assertAlmostEqual(spin70.chi2, 29.7980427316775, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[0], 4.96765137715714, 4)
        self.assertAlmostEqual(spin71.phi_ex, 0.16487619476159, 4)
        self.assertAlmostEqual(spin71.padw2, 0.000896297985759929, 3)
        self.assertAlmostEqual(spin71.tex*1000, 0.000125225494546911*1000, 4)
        self.assertAlmostEqual(spin71.chi2, 2.33683739438351, 4)


    def test_hansen_cpmg_data_to_lm63(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the LM63 dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='LM63')

        # Alias the spins.
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]

        # Set the initial parameter values.
        spin70.r2 = [7, 7]
        spin70.phi_ex = 0.3
        spin70.kex = 5000.0
        spin71.r2 = [5, 9]
        spin71.phi_ex = 0.1
        spin71.kex = 2500.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.15g %20.15g" % ("phi_ex", spin70.phi_ex, spin71.phi_ex))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[0], 6.77242822209793)
        self.assertAlmostEqual(spin70.r2[1], 6.64980731657647)
        self.assertAlmostEqual(spin70.phi_ex, 0.308216165020969)
        self.assertAlmostEqual(spin70.kex, 4644.14994939979)
        self.assertAlmostEqual(spin70.chi2, 137.646385919032)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[0], 4.93018206884413)
        self.assertAlmostEqual(spin71.phi_ex, 0.0595427749251471)
        self.assertAlmostEqual(spin71.kex, 2566.18404917873)
        self.assertAlmostEqual(spin71.chi2, 2.31424598896425)


    def test_hansen_cpmg_data_to_ns_cpmg_2site_3D(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the 'NS CPMG 2-site 3D' dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='NS CPMG 2-site 3D')

        # Alias the spins.
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]

        # Set the initial parameter values.
        spin70.r2 = [6.994165925, 9.428129427]
        spin70.pA = 0.9897754407
        spin70.dw = 5.642418428
        spin70.kex = 1743.666375
        spin71.r2 = [4.978654237, 9.276918959]
        spin71.pA = 0.9968032899
        spin71.dw = 4.577891393
        spin71.kex = 1830.044597

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=False, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[0], 6.96115756572771, 4)
        self.assertAlmostEqual(spin70.r2[1], 9.43526089661722, 4)
        self.assertAlmostEqual(spin70.pA, 0.989640708131005, 4)
        self.assertAlmostEqual(spin70.dw, 5.67767848775396, 4)
        self.assertAlmostEqual(spin70.kex/1000, 1675.90756479742/1000, 4)
        self.assertAlmostEqual(spin70.chi2, 16.9360832313278, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[0], 4.98289464865291, 4)
        self.assertAlmostEqual(spin71.pA, 0.996737413473986, 4)
        self.assertAlmostEqual(spin71.dw, 4.51876106236011, 4)
        self.assertAlmostEqual(spin71.kex/1000, 1862.79421871514/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 2.21065383641839, 4)

        # Test the conversion to k_AB from kex and pA.
        self.assertEqual(spin70.k_AB, spin70.kex * (1.0 - spin70.pA))
        self.assertEqual(spin71.k_AB, spin71.kex * (1.0 - spin71.pA))

        # Test the conversion to k_BA from kex and pA.
        self.assertEqual(spin70.k_BA, spin70.kex * spin70.pA)
        self.assertEqual(spin71.k_BA, spin71.kex * spin71.pA)


    def test_hansen_cpmg_data_to_ns_cpmg_2site_3D_full(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the 'NS CPMG 2-site 3D full' dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='NS CPMG 2-site 3D full')

        # Alias the spins.
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]

        # Set the initial parameter values.
        spin70.r2a = [6.644753428, 7.891776687]
        spin70.r2b = [7.163478485, 138.5170395]
        spin70.pA = 0.9884781357
        spin70.dw = 5.456507396
        spin70.kex = 1906.521189
        spin71.r2a = [4.928192157, 58.63630533]
        spin71.r2b = [28.1567729, 70.82765862]
        spin71.pA = 0.9971352426
        spin71.dw = 5.000821345
        spin71.kex = 1654.484828

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=False, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2A (500 MHz)", spin70.r2a[0], spin71.r2a[0]))
        print("%-20s %20.15g %20.15g" % ("R2B (500 MHz)", spin70.r2b[0], spin71.r2b[0]))
        print("%-20s %20.15g %20.15g" % ("R2A (800 MHz)", spin70.r2a[1], spin71.r2a[1]))
        print("%-20s %20.15g %20.15g" % ("R2B (800 MHz)", spin70.r2b[1], spin71.r2b[1]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2a[0], 6.64075224170421, 4)
        self.assertAlmostEqual(spin70.r2b[0], 7.33185783828255, 4)
        self.assertAlmostEqual(spin70.r2a[1], 7.8705138674419, 4)
        self.assertAlmostEqual(spin70.r2b[1], 137.845238420039, 4)
        self.assertAlmostEqual(spin70.pA, 0.988417593666782, 4)
        self.assertAlmostEqual(spin70.dw, 5.43959484783964, 4)
        self.assertAlmostEqual(spin70.kex/1000, 1912.04840067751/1000, 4)
        self.assertAlmostEqual(spin70.chi2, 14.4219294450958, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2a[0], 4.98208888908847, 4)
        self.assertAlmostEqual(spin71.r2b[0], 5.3141913798609, 4)
        self.assertAlmostEqual(spin71.pA, 0.996740417356211, 4)
        self.assertAlmostEqual(spin71.dw, 4.52175288147293, 4)
        self.assertAlmostEqual(spin71.kex/1000, 1859.89477123506/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 2.21065763538548, 4)

        # Test the conversion to k_AB from kex and pA.
        self.assertEqual(spin70.k_AB, spin70.kex * (1.0 - spin70.pA))
        self.assertEqual(spin71.k_AB, spin71.kex * (1.0 - spin71.pA))

        # Test the conversion to k_BA from kex and pA.
        self.assertEqual(spin70.k_BA, spin70.kex * spin70.pA)
        self.assertEqual(spin71.k_BA, spin71.kex * spin71.pA)


    def test_hansen_cpmg_data_to_ns_cpmg_2site_expanded(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the 'NS CPMG 2-site expanded' dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='NS CPMG 2-site expanded')

        # Alias the spins.
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]

        # Set the initial parameter values.
        spin70.r2 = [7, 9]
        spin70.pA = 0.9
        spin70.dw = 6.0
        spin70.kex = 1500.0
        spin71.r2 = [5, 9]
        spin71.pA = 0.9
        spin71.dw = 4.0
        spin71.kex = 1900.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[0], 6.96088065283431, 4)
        self.assertAlmostEqual(spin70.r2[1], 9.43547681910753, 4)
        self.assertAlmostEqual(spin70.pA, 0.989640848538, 4)
        self.assertAlmostEqual(spin70.dw, 5.6777500010395, 4)
        self.assertAlmostEqual(spin70.kex/1000, 1675.85201862474/1000, 4)
        self.assertAlmostEqual(spin70.chi2, 16.9361845456949, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[0], 4.98214991947236, 4)
        self.assertAlmostEqual(spin71.pA, 0.996719201570109, 4)
        self.assertAlmostEqual(spin71.dw, 4.50406877899137, 4)
        self.assertAlmostEqual(spin71.kex/1000, 1868.30341816249/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 2.21068411745903, 4)

        # Test the conversion to k_AB from kex and pA.
        self.assertEqual(spin70.k_AB, spin70.kex * (1.0 - spin70.pA))
        self.assertEqual(spin71.k_AB, spin71.kex * (1.0 - spin71.pA))

        # Test the conversion to k_BA from kex and pA.
        self.assertEqual(spin70.k_BA, spin70.kex * spin70.pA)
        self.assertEqual(spin71.k_BA, spin71.kex * spin71.pA)


    def test_hansen_cpmg_data_to_ns_cpmg_2site_star(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the 'NS CPMG 2-site star' dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='NS CPMG 2-site star')

        # Alias the spins.
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]

        # Set the initial parameter values.
        spin70.r2 = [6.996327746, 9.452051268]
        spin70.pA = 0.9897519798
        spin70.dw = 5.644862195
        spin70.kex = 1723.820567
        spin71.r2 = [4.978654237, 9.276918959]
        spin71.pA = 0.9968032899
        spin71.dw = 4.577891393
        spin71.kex = 1830.044597

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=False, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[0], spin71.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[1], spin71.r2[1]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[0], 6.96152150644329, 2)
        self.assertAlmostEqual(spin70.r2[1], 9.43115345962684, 1)
        self.assertAlmostEqual(spin70.pA, 0.98964747321538, 3)
        self.assertAlmostEqual(spin70.dw, 5.67631785444106, 2)
        self.assertAlmostEqual(spin70.kex/1000, 1680.88938143021/1000, 1)
        self.assertAlmostEqual(spin70.chi2, 16.9325748871342, 1)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[0], 4.98447588852395, 1)
        self.assertAlmostEqual(spin71.pA, 0.996819131151691, 4)
        self.assertAlmostEqual(spin71.dw, 4.58710928881276, 1)
        self.assertAlmostEqual(spin71.kex/1000, 1835.89358409825/1000, 1)
        self.assertAlmostEqual(spin71.chi2, 2.2089749579694, 1)

        # Test the conversion to k_AB from kex and pA.
        self.assertEqual(spin70.k_AB, spin70.kex * (1.0 - spin70.pA))
        self.assertEqual(spin71.k_AB, spin71.kex * (1.0 - spin71.pA))

        # Test the conversion to k_BA from kex and pA.
        self.assertEqual(spin70.k_BA, spin70.kex * spin70.pA)
        self.assertEqual(spin71.k_BA, spin71.kex * spin71.pA)


    def test_hansen_cpmg_data_to_ns_cpmg_2site_star_full(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the 'NS CPMG 2-site star full' dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='NS CPMG 2-site star full')

        # Alias the spins.
        spin70 = cdp.mol[0].res[0].spin[0]
        spin71 = cdp.mol[0].res[1].spin[0]

        # Set the initial parameter values.
        spin70.r2a = [6.6669125505612326, 7.9099620524116832]
        spin70.r2b = [5.1682435163389273, 136.91254775378511]
        spin70.pA = 0.98850730705658107
        spin70.dw = 5.4558153872989479
        spin70.kex = 1912.8933749215912
        spin71.r2a = [4.7063177761402863, 82.050179213698851]
        spin71.r2b = [89.166191921335241, 82.326667994585918]
        spin71.pA = 0.99654076024302629
        spin71.dw = 4.6216529767646399
        spin71.kex = 1726.0473405563631

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=False, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2A (500 MHz)", spin70.r2a[0], spin71.r2a[0]))
        print("%-20s %20.15g %20.15g" % ("R2B (500 MHz)", spin70.r2b[0], spin71.r2b[0]))
        print("%-20s %20.15g %20.15g" % ("R2A (800 MHz)", spin70.r2a[1], spin71.r2a[1]))
        print("%-20s %20.15g %20.15g" % ("R2B (800 MHz)", spin70.r2b[1], spin71.r2b[1]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2a[0], 6.65078481090512, 2)
        self.assertAlmostEqual(spin70.r2b[0]/10, 5.32381715451347/10, 1)
        self.assertAlmostEqual(spin70.r2a[1], 7.88179635634578, 2)
        self.assertAlmostEqual(spin70.r2b[1]/100, 135.301813064895/100, 2)
        self.assertAlmostEqual(spin70.pA, 0.988476350902883, 4)
        self.assertAlmostEqual(spin70.dw, 5.45783086803889, 1)
        self.assertAlmostEqual(spin70.kex/1000, 1917.34123861444/1000, 1)
        self.assertAlmostEqual(spin70.chi2/10, 14.4236787048135/10, 1)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2a[0], 4.70924605140312, 2)
        self.assertAlmostEqual(spin71.r2b[0]/100, 90.5967627165153/100, 2)
        self.assertAlmostEqual(spin71.pA, 0.996552640812467, 4)
        self.assertAlmostEqual(spin71.dw, 4.63014545224382, 2)
        self.assertAlmostEqual(spin71.kex/1000, 1737.36993910397/1000, 2)
        self.assertAlmostEqual(spin71.chi2, 2.2100492324449, 1)

        # Test the conversion to k_AB from kex and pA.
        self.assertEqual(spin70.k_AB, spin70.kex * (1.0 - spin70.pA))
        self.assertEqual(spin71.k_AB, spin71.kex * (1.0 - spin71.pA))

        # Test the conversion to k_BA from kex and pA.
        self.assertEqual(spin70.k_BA, spin70.kex * spin70.pA)
        self.assertEqual(spin71.k_BA, spin71.kex * spin71.pA)


    def test_hansen_cpmgfit_input(self):
        """Conversion of Dr. Flemming Hansen's CPMG R2eff values into input files for CPMGFit.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Load the state, preserving the temp directory.
        tmpdir = ds.tmpdir
        state = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'+sep+'r2eff_values'
        self.interpreter.state.load(state, force=True)
        ds.tmpdir = tmpdir

        # Set up the model.
        self.interpreter.relax_disp.select_model('LM63')

        # Generate the input files.
        self.interpreter.relax_disp.cpmgfit_input(force=True, dir=ds.tmpdir)

        # What the files should contain.
        batch_file = ['#! /bin/sh\n', '\n', 'cpmgfit -grid -xmgr -f spin_70_N.in | tee spin_70_N.out\n', 'cpmgfit -grid -xmgr -f spin_71_N.in | tee spin_71_N.out\n']
        spin1 = [
            'title :70@N\n',
            'fields 2 11.7432964915 18.7892743865\n',
            'function CPMG\n',
            'R2 1 10 20\n',
            'Rex 0 100.0 100\n',
            'Tau 0 10.0 100\n',
            'xmgr\n',
            '@ xaxis label "1/tcp (1/ms)"\n',
            '@ yaxis label "R2(tcp) (rad/s)"\n',
            '@ xaxis ticklabel format decimal\n',
            '@ yaxis ticklabel format decimal\n',
            '@ xaxis ticklabel char size 0.8\n',
            '@ yaxis ticklabel char size 0.8\n',
            '@ world xmin 0.0\n',
            'data\n',
            '0.066667             16.045541            0.489669             11.743296           \n',
            '0.133333             14.877925            0.477531             11.743296           \n',
            '0.200000             14.357820            0.472298             11.743296           \n',
            '0.266667             12.664495            0.455979             11.743296           \n',
            '0.333333             12.363205            0.453187             11.743296           \n',
            '0.400000             11.092532            0.441776             11.743296           \n',
            '0.466667             10.566090            0.437216             11.743296           \n',
            '0.533333             9.805807             0.430800             11.743296           \n',
            '0.600000             9.564301             0.428803             11.743296           \n',
            '0.666667             9.015634             0.424338             11.743296           \n',
            '0.733333             8.607765             0.421084             11.743296           \n',
            '0.800000             8.279997             0.418508             11.743296           \n',
            '0.866667             8.474536             0.420033             11.743296           \n',
            '0.933333             8.158973             0.417566             11.743296           \n',
            '1.000000             7.988631             0.416248             11.743296           \n',
            '0.066667             22.224914            0.302364             18.789274           \n',
            '0.133333             21.230874            0.295355             18.789274           \n',
            '0.200000             20.603704            0.291062             18.789274           \n',
            '0.266667             20.327797            0.289205             18.789274           \n',
            '0.333333             18.855377            0.279607             18.789274           \n',
            '0.400000             18.537531            0.277603             18.789274           \n',
            '0.466667             17.508069            0.271274             18.789274           \n',
            '0.533333             16.035604            0.262639             18.789274           \n',
            '0.600000             15.168192            0.257776             18.789274           \n',
            '0.666667             14.431802            0.253772             18.789274           \n',
            '0.733333             14.034137            0.251658             18.789274           \n',
            '0.800000             12.920148            0.245906             18.789274           \n',
            '0.866667             12.653673            0.244567             18.789274           \n',
            '0.933333             12.610864            0.244354             18.789274           \n',
            '1.000000             11.969303            0.241193             18.789274           \n'
        ]
        spin2 = [
            'title :71@N\n',
            'fields 2 11.7432964915 18.7892743865\n',
            'function CPMG\n',
            'R2 1 10 20\n',
            'Rex 0 100.0 100\n',
            'Tau 0 10.0 100\n',
            'xmgr\n',
            '@ xaxis label "1/tcp (1/ms)"\n',
            '@ yaxis label "R2(tcp) (rad/s)"\n',
            '@ xaxis ticklabel format decimal\n',
            '@ yaxis ticklabel format decimal\n',
            '@ xaxis ticklabel char size 0.8\n',
            '@ yaxis ticklabel char size 0.8\n',
            '@ world xmin 0.0\n',
            'data\n',
            '0.066667             7.044342             0.267785             11.743296           \n',
            '0.133333             6.781033             0.266514             11.743296           \n',
            '0.200000             6.467623             0.265020             11.743296           \n',
            '0.266667             6.333340             0.264385             11.743296           \n',
            '0.333333             6.323238             0.264338             11.743296           \n',
            '0.400000             6.005245             0.262851             11.743296           \n',
            '0.466667             5.767052             0.261750             11.743296           \n',
            '0.533333             5.476968             0.260424             11.743296           \n',
            '0.600000             5.469949             0.260392             11.743296           \n',
            '0.666667             5.295113             0.259601             11.743296           \n',
            '0.733333             5.435648             0.260236             11.743296           \n',
            '0.800000             5.410400             0.260122             11.743296           \n',
            '0.866667             5.437554             0.260245             11.743296           \n',
            '0.933333             5.176844             0.259069             11.743296           \n',
            '1.000000             5.227232             0.259295             11.743296           \n'
        ]

        # Check the batch file.
        print("\nChecking the batch file.")
        file = open("%s%sbatch_run.sh" % (ds.tmpdir, sep))
        lines = file.readlines()
        file.close()
        for i in range(len(lines)):
            self.assertEqual(batch_file[i], lines[i])

        # Check spin :70@N.
        print("\nChecking the spin :70@N input file.")
        file = open("%s%sspin%s.in" % (ds.tmpdir, sep, '_70_N'))
        lines = file.readlines()
        file.close()
        for i in range(len(lines)):
            print(lines[i][:-1])
        for i in range(len(lines)):
            self.assertEqual(spin1[i], lines[i])

        # Check spin :71@N.
        print("\nChecking the spin :71@N input file.")
        file = open("%s%sspin%s.in" % (ds.tmpdir, sep, '_71_N'))
        lines = file.readlines()
        file.close()
        for i in range(len(lines)):
            print(lines[i][:-1])
        for i in range(len(lines)):
            self.assertEqual(spin2[i], lines[i])


    def test_kteilum_fmpoulsen_makke_cpmg_data_048m_guhcl_to_cr72(self):
        """Optimisation of Kaare Teilum, Flemming M Poulsen, Mikael Akke 2006 "acyl-CoA binding protein" CPMG data to the CR72 dispersion model.

        This uses the data from paper at U{http://dx.doi.org/10.1073/pnas.0509100103}.  This is CPMG data with a fixed relaxation time period.  Experiment in 0.48 M GuHCl (guanidine hydrochloride).
        """

        # Base data setup.
        self.setup_kteilum_fmpoulsen_makke_cpmg_data(model='CR72', expfolder="acbp_cpmg_disp_048MGuHCl_40C_041223")

        # Alias the spins.
        res61L = cdp.mol[0].res[0].spin[0]

        # Set the initial parameter values.
        res61L.r2 = [8]
        res61L.pA = 0.9
        res61L.dw = 6.0
        res61L.kex = 600.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:61)"))
        print("%-20s %20.15g" % ("R2 (600 MHz)", res61L.r2[0]))
        print("%-20s %20.15g" % ("pA", res61L.pA))
        print("%-20s %20.15g" % ("dw", res61L.dw))
        print("%-20s %20.15g" % ("kex", res61L.kex))
        print("%-20s %20.15g\n" % ("chi2", res61L.chi2))

        # Checks for residue :61. Calculated for 500 Monte Carlo simulations.
        self.assertAlmostEqual(res61L.r2[0], 8.69277980194016, 4)
        self.assertAlmostEqual(res61L.pA, 0.9943781590842946, 5)
        self.assertAlmostEqual(res61L.dw, 6.389453131263374, 3)
        self.assertAlmostEqual(res61L.kex, 609.262167216419, 0)
        self.assertAlmostEqual(res61L.chi2, 65.99987828889657, 5)

        # Test the conversion to k_AB from kex and pA.
        self.assertEqual(res61L.k_AB, res61L.kex * (1.0 - res61L.pA))

        # Test the conversion to k_BA from kex and pA.
        self.assertEqual(res61L.k_BA, res61L.kex * res61L.pA)


    def test_kteilum_fmpoulsen_makke_cpmg_data_048m_guhcl_to_cr72_full(self):
        """Optimisation of Kaare Teilum, Flemming M Poulsen, Mikael Akke 2006 "acyl-CoA binding protein" CPMG data to the CR72 dispersion model.

        This uses the data from paper at U{http://dx.doi.org/10.1073/pnas.0509100103}.  This is CPMG data with a fixed relaxation time period.  Experiment in 0.48 M GuHCl (guanidine hydrochloride).
        """

        # Base data setup.
        self.setup_kteilum_fmpoulsen_makke_cpmg_data(model='CR72 full', expfolder="acbp_cpmg_disp_048MGuHCl_40C_041223")

        # Alias the spins.
        res61L = cdp.mol[0].res[0].spin[0]

        # Set the initial parameter values.
        res61L.r2a = [8]
        res61L.r2b = [105]
        res61L.pA = 0.9
        res61L.dw = 6.0
        res61L.kex = 500.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:61)"))
        print("%-20s %20.15g" % ("R2A (600 MHz)", res61L.r2a[0]))
        print("%-20s %20.15g" % ("R2B (600 MHz)", res61L.r2b[0]))
        print("%-20s %20.15g" % ("pA", res61L.pA))
        print("%-20s %20.15g" % ("dw", res61L.dw))
        print("%-20s %20.15g" % ("kex", res61L.kex))
        print("%-20s %20.15g\n" % ("chi2", res61L.chi2))

        # Checks for residue :61. Calculated for 500 Monte Carlo simulations.
        self.assertAlmostEqual(res61L.r2a[0], 8.044428899438309, 0)
        self.assertAlmostEqual(res61L.r2b[0], 105.11894506392449, -2)
        self.assertAlmostEqual(res61L.pA, 0.992066883657578, 2)
        self.assertAlmostEqual(res61L.dw, 6.389453586338883, 3)
        self.assertAlmostEqual(res61L.kex, 513.483608742063, -2)
        self.assertAlmostEqual(res61L.chi2, 65.99987828890289, 5)


    def test_kteilum_fmpoulsen_makke_cpmg_data_048m_guhcl_to_tsmfk01(self):
        """Optimisation of Kaare Teilum, Flemming M Poulsen, Mikael Akke 2006 "acyl-CoA binding protein" CPMG data to the CR72 dispersion model.

        This uses the data from paper at U{http://dx.doi.org/10.1073/pnas.0509100103}.  This is CPMG data with a fixed relaxation time period.  Experiment in 0.48 M GuHCl (guanidine hydrochloride).

        Figure 3 shows the ln( k_a [s^-1]) for different concentrations of GuHCl. The precise values are:

          - [GuHCL][M] ln(k_a[s^-1]) k_a[s^-1] 
          - 0.483 0.89623903 2.4503699912708878
          - 0.545 1.1694838
          - 0.545 1.1761503
          - 0.622 1.294
          - 0.669 1.5176493
          - 0.722 1.6238791
          - 0.813 1.9395758
          - 1.011 2.3558415 10.547000429321157
        """

        # Base data setup.
        self.setup_kteilum_fmpoulsen_makke_cpmg_data(model='TSMFK01', expfolder="acbp_cpmg_disp_048MGuHCl_40C_041223")

        # Alias the spins.
        res61L = cdp.mol[0].res[0].spin[0]

        # Set the initial parameter values.
        res61L.r2a = [8]
        res61L.dw = 6.5
        res61L.k_AB = 2.5

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:61)"))
        print("%-20s %20.15g" % ("R2A (600 MHz)", res61L.r2a[0]))
        print("%-20s %20.15g" % ("dw", res61L.dw))
        print("%-20s %20.15g" % ("k_AB", res61L.k_AB))
        print("%-20s %20.15g\n" % ("chi2", res61L.chi2))

        # Checks for residue :61. Reference values from paper

        self.assertAlmostEqual(res61L.k_AB, 2.45, 1)


    def test_kteilum_fmpoulsen_makke_cpmg_data_101m_guhcl_to_tsmfk01(self):
        """Optimisation of Kaare Teilum, Flemming M Poulsen, Mikael Akke 2006 "acyl-CoA binding protein" CPMG data to the CR72 dispersion model.

        This uses the data from paper at U{http://dx.doi.org/10.1073/pnas.0509100103}.  This is CPMG data with a fixed relaxation time period.  Experiment in 1.01 M GuHCl (guanidine hydrochloride).

        The comparison is to Figure 2, which is for dataset with 1 M GuHCl.  The reported results are expected to be in rad.s^-1.  Conversion into relax stored values is preferably.

        Representative 15N CPMG relaxation dispersion curve measured on the cross peaks from residue L61 in folded ACBP at pH 5.3, 1 M GuHCl, and 40C:

          1. The dotted line represents a residue-specific fit of all parameters in Eq. 1:
            - k_AB = 11.3 +/- 0.7 s^-1,
            - dw = (2.45 +/- 0.09) * 10^3 s^-1,
            - R2 = 8.0 +/- 0.5 s^-1.

          2. The solid line represents a global fit of k_AB to all protein residues and a residue-specific fit of dw and R2.:
            - k_AB = 10.55 +/- 0.08 s^-1,
            - dw = (2.44 +/- 0.08) * 10^3 s^-1,
            - R2 = 8.4 +/- 0.3 s^-1.

        Conversion of paper results to relax results is performed by:

          - dw(ppm) = dw(rad.s^-1) * 10^6 * 1/(2*pi) * (gyro1H/(gyro15N*spectrometer_freq)) = 2.45E3 * 1E6 / (2 * math.pi) * (26.7522212E7/(-2.7126E7 * 599.8908622E6)) = -6.41 ppm.

        Figure 3 shows the ln( k_a [s^-1]) for different concentrations of GuHCl.  The precise values are:

          - [GuHCL][M] ln(k_a[s^-1]) k_a[s^-1] 
          - 0.483 0.89623903 2.4503699912708878
          - 0.545 1.1694838
          - 0.545 1.1761503
          - 0.622 1.294
          - 0.669 1.5176493
          - 0.722 1.6238791
          - 0.813 1.9395758
          - 1.011 2.3558415 10.547000429321157
        """

        # Base data setup.
        self.setup_kteilum_fmpoulsen_makke_cpmg_data(model='TSMFK01', expfolder="acbp_cpmg_disp_101MGuHCl_40C_041223")

        # Alias the spins.
        res61L = cdp.mol[0].res[0].spin[0]

        # Set the initial parameter values.
        res61L.r2a = [8]
        res61L.dw = 6.5
        res61L.k_AB = 11.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:61)"))
        print("%-20s %20.15g" % ("R2A (600 MHz)", res61L.r2a[0]))
        print("%-20s %20.15g" % ("dw", res61L.dw))
        print("%-20s %20.15g" % ("k_AB", res61L.k_AB))
        print("%-20s %20.15g\n" % ("chi2", res61L.chi2))

        # Checks for residue :61. Reference values from paper

        self.assertAlmostEqual(res61L.r2a[0], 8.4, 0)
        self.assertAlmostEqual(res61L.dw, 6.41, 0)
        self.assertAlmostEqual(res61L.k_AB, 10.55, 0)


    def test_m61_data_to_m61(self):
        """Test the relaxation dispersion 'M61' model curve fitting to fixed time synthetic data."""

        # Fixed time variable.
        ds.fixed = True

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'r1rho_on_res_m61.py')

        # The original parameters.
        i0 = [100000.0, 20000.0]
        r1rho_prime = [2.25, 24.0]
        pA = 0.7
        kex = 1000.0
        delta_omega = [1.0, 2.0]
        keys = ['800.00000000_1000.000', '800.00000000_1500.000', '800.00000000_2000.000', '800.00000000_2500.000', '800.00000000_3000.000', '800.00000000_3500.000', '800.00000000_4000.000', '800.00000000_4500.000', '800.00000000_5000.000', '800.00000000_5500.000', '800.00000000_6000.000']
        phi_ex = []
        for i in range(2):
            phi_ex.append(pA * (1.0 - pA) * delta_omega[i]**2)
        rates = [[3.59768160399, 2.85730469783, 2.59328084312, 2.47019857325, 2.40310451058, 2.36256876552, 2.33622716364, 2.31815271355, 2.30521680479, 2.29564174079, 2.28835686631], [29.390726416, 26.4292187913, 25.3731233725, 24.880794293, 24.6124180423, 24.4502750621, 24.3449086546, 24.2726108542, 24.2208672192, 24.1825669632, 24.1534274652]]

        # Switch to the 'R2eff' model data pipe, then check for each spin.
        self.interpreter.pipe.switch('R2eff')
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            for i in range(len(keys)):
                self.assertAlmostEqual(spin.r2eff[keys[i]]/10.0, rates[spin_index][i]/10.0, 2)

            # Increment the spin index.
            spin_index += 1

        # Switch to the 'M61' model data pipe, then check for each spin.
        self.interpreter.pipe.switch('M61')
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[0]/10, r1rho_prime[spin_index]/10, 2)
            self.assertAlmostEqual(spin.phi_ex, phi_ex[spin_index], 2)
            self.assertAlmostEqual(spin.kex/1000.0, kex/1000.0, 2)

            # Increment the spin index.
            spin_index += 1


    def test_m61_exp_data_to_m61(self):
        """Test the relaxation dispersion 'M61' model curve fitting to the full exponential synthetic data."""

        # Fixed time variable.
        ds.fixed = False

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'r1rho_on_res_m61.py')

        # The original parameters.
        i0 = [100000.0, 20000.0]
        r1rho_prime = [2.25, 24.0]
        pA = 0.7
        kex = 1000.0
        delta_omega = [1.0, 2.0]
        keys = ['800.00000000_1000.000', '800.00000000_1500.000', '800.00000000_2000.000', '800.00000000_2500.000', '800.00000000_3000.000', '800.00000000_3500.000', '800.00000000_4000.000', '800.00000000_4500.000', '800.00000000_5000.000', '800.00000000_5500.000', '800.00000000_6000.000']
        phi_ex = []
        for i in range(2):
            phi_ex.append(pA * (1.0 - pA) * delta_omega[i]**2)
        rates = [[3.59768160399, 2.85730469783, 2.59328084312, 2.47019857325, 2.40310451058, 2.36256876552, 2.33622716364, 2.31815271355, 2.30521680479, 2.29564174079, 2.28835686631], [29.390726416, 26.4292187913, 25.3731233725, 24.880794293, 24.6124180423, 24.4502750621, 24.3449086546, 24.2726108542, 24.2208672192, 24.1825669632, 24.1534274652]]

        # Switch to the 'R2eff' model data pipe, then check for each spin.
        self.interpreter.pipe.switch('R2eff')
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            for i in range(len(keys)):
                self.assertAlmostEqual(spin.r2eff[keys[i]]/10.0, rates[spin_index][i]/10.0, 2)

            # Increment the spin index.
            spin_index += 1

        # Switch to the 'M61' model data pipe, then check for each spin.
        self.interpreter.pipe.switch('M61')
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[0]/10, r1rho_prime[spin_index]/10, 2)
            self.assertAlmostEqual(spin.phi_ex, phi_ex[spin_index], 2)
            self.assertAlmostEqual(spin.kex/1000.0, kex/1000.0, 2)

            # Increment the spin index.
            spin_index += 1


    def xxx_test_m61b_data_to_m61b(self):
        """Test the relaxation dispersion 'M61 skew' model curve fitting to fixed time synthetic data."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'r1rho_on_res_m61b.py')

        # The original parameters.
        i0 = [100000.0, 20000.0]
        r1rho_prime = [10.0, 24.0]
        pA = 0.95
        kex = 2000.0
        delta_omega = [1.0, 2.0]

        # Switch to the 'M61 skew' model data pipe, then check for each spin.
        self.interpreter.pipe.switch(MODEL_M61B)
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[0]/10, r1rho_prime[spin_index]/10, 2)
            self.assertAlmostEqual(spin.pA, pA, 2)
            self.assertAlmostEqual(spin.dw, dw[spin_index], 2)
            self.assertAlmostEqual(spin.kex/1000.0, kex/1000.0, 2)

            # Increment the spin index.
            spin_index += 1


    def test_r2eff_fit_fixed_time(self):
        """Test the relaxation dispersion 'R2eff' model for fixed time data in the auto-analysis."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'r2eff_calc.py')


    def test_read_r2eff(self):
        """Test the reading of a file containing r2eff values."""

        # Create the sequence data, and name the spins.
        self.interpreter.residue.create(1, 'Gly')
        self.interpreter.residue.create(2, 'Gly')
        self.interpreter.residue.create(3, 'Gly')

        # Read the file.
        self.interpreter.relax_data.read(ri_id='R2eff.600', ri_type='R2eff', frq=600*1e6, file='r2eff.out', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'r2eff', res_num_col=1, res_name_col=2, data_col=3, error_col=4)

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].ri_data['R2eff.600'], 15.000)
        self.assertEqual(cdp.mol[0].res[1].spin[0].ri_data['R2eff.600'], 4.2003)
        self.assertEqual(cdp.mol[0].res[2].spin[0].ri_data['R2eff.600'], 7.2385)


    def test_sprangers_data_to_mq_cr72(self, model=None):
        """Test the 'MQ CR72' model fitting against Remco Sprangers' ClpP data.

        This uses the data from Remco Sprangers' paper at http://dx.doi.org/10.1073/pnas.0507370102.  This is MQ CPMG data with a fixed relaxation time period.
        """

        # Reset.
        self.interpreter.reset()

        # Create the data pipe and load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Sprangers_ClpP'
        self.interpreter.state.load(data_path+sep+'r2eff_values')

        # The model data pipe.
        model = 'MQ CR72'
        self.interpreter.pipe.copy(pipe_from='base pipe', pipe_to=model, bundle_to='relax_disp')
        self.interpreter.pipe.switch(pipe_name=model)

        # Set the model.
        self.interpreter.relax_disp.select_model(model=model)

        # Cluster everything.
        self.interpreter.relax_disp.cluster(cluster_id='all', spin_id=":135-137")

        # Copy the data.
        self.interpreter.value.copy(pipe_from='R2eff', pipe_to=model, param='r2eff')

        # Alias the spins.
        spin135S = cdp.mol[0].res[0].spin[0]
        spin135F = cdp.mol[0].res[0].spin[1]
        spin137S = cdp.mol[0].res[1].spin[0]
        spin137F = cdp.mol[0].res[1].spin[1]

        # Set the cluster specific parameters (only for the first spin).
        spin135S.pA = 0.864737982511210
        spin135S.kex = 286.743720388766860

        # Set the initial parameter values.
        spin135S.r2 = [ 31.529250951747834, 38.638249554769878]
        spin135S.dw = 0.586224611058921
        spin135S.dwH = 0.000000337605456

        spin135F.r2 = [ 42.635298355865039, 58.200580875711417]
        spin135F.dw = 0.857710423308549
        spin135F.dwH = 0.022554924428825

        spin137S.r2 = [ 26.852049534997846, 32.856936362980065]
        spin137S.dw = 0.712087594614247
        spin137S.dwH = 0.122253576682791

        spin137F.r2 = [ 46.014039109842983, 57.798402024518595]
        spin137F.dw = 0.980787017888634
        spin137F.dwH = 0.000011599527196

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=100, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s %-20s %-20s" % ("Parameter", "Value (:135@S)", "Value (:135@F)", "Value (:137@S)", "Value (:137@F)"))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("R2 (500 MHz)", spin135S.r2[0], spin135F.r2[0], spin137S.r2[0], spin137F.r2[0]))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("R2 (800 MHz)", spin135S.r2[1], spin135F.r2[1], spin137S.r2[1], spin137F.r2[1]))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("pA", spin135S.pA, spin135F.pA, spin137S.pA, spin137F.pA))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("dw", spin135S.dw, spin135F.dw, spin137S.dw, spin137F.dw))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("dwH", spin135S.dwH, spin135F.dwH, spin137S.dwH, spin137F.dwH))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("kex", spin135S.kex, spin135F.kex, spin137S.kex, spin137F.kex))
        print("%-20s %20.15g %20.15g %20.15g %20.15g\n" % ("chi2", spin135S.chi2, spin135F.chi2, spin137S.chi2, spin137F.chi2))
        print("\n        # Set the cluster specific parameters (only for the first spin).")
        print("        spin135S.pA = %s" % spin135S.pA)
        print("        spin135S.kex = %s" % spin135S.kex)
        print("\n        # Set the initial parameter values.")
        print("        spin135S.r2 = [%s, %s]" % (spin135S.r2[0], spin135S.r2[1]))
        print("        spin135S.dw = %s" % spin135S.dw)
        print("        spin135S.dwH = %s" % spin135S.dwH)
        print("\n        spin135F.r2 = [%s, %s]" % (spin135F.r2[0], spin135F.r2[1]))
        print("        spin135F.dw = %s" % spin135F.dw)
        print("        spin135F.dwH = %s" % spin135F.dwH)
        print("\n        spin137S.r2 = [%s, %s]" % (spin137S.r2[0], spin137S.r2[1]))
        print("        spin137S.dw = %s" % spin137S.dw)
        print("        spin137S.dwH = %s" % spin137S.dwH)
        print("\n        spin137F.r2 = [%s, %s]" % (spin137F.r2[0], spin137F.r2[1]))
        print("        spin137F.dw = %s" % spin137F.dw)
        print("        spin137F.dwH = %s" % spin137F.dwH)

        # Checks for residue :135S.
        self.assertAlmostEqual(spin135S.r2[0], 31.5292509517478, 4)
        self.assertAlmostEqual(spin135S.r2[1], 38.6382495547699, 4)
        self.assertAlmostEqual(spin135S.pA, 0.86473798251121, 4)
        self.assertAlmostEqual(spin135S.dw, 0.586224611058921, 4)
        self.assertAlmostEqual(spin135S.dwH, 3.544857288e-07, 4)
        self.assertAlmostEqual(spin135S.kex, 286.743720388767, 4)
        self.assertAlmostEqual(spin135S.chi2, 15.2088757872867, 4)

        # Checks for residue :135F.
        self.assertAlmostEqual(spin135F.r2[0], 42.635298355865, 4)
        self.assertAlmostEqual(spin135F.r2[1], 58.2005808757114, 4)
        self.assertAlmostEqual(spin135F.pA, 0.86473798251121, 4)
        self.assertAlmostEqual(spin135F.dw, 0.857710423308549, 4)
        self.assertAlmostEqual(spin135F.dwH, 0.022554924428825, 4)
        self.assertAlmostEqual(spin135F.kex, 286.743720388767, 4)
        self.assertAlmostEqual(spin135F.chi2, 15.2088757872867, 4)

        # Checks for residue :137S.
        self.assertAlmostEqual(spin137S.r2[0], 26.8520495349978, 4)
        self.assertAlmostEqual(spin137S.r2[1], 32.8569363629801, 4)
        self.assertAlmostEqual(spin137S.pA, 0.86473798251121, 4)
        self.assertAlmostEqual(spin137S.dw, 0.712087594614247, 4)
        self.assertAlmostEqual(spin137S.dwH, 0.122253576682791, 4)
        self.assertAlmostEqual(spin137S.kex, 286.743720388767, 4)
        self.assertAlmostEqual(spin137S.chi2, 15.2088757872867, 4)

        # Checks for residue :137F.
        self.assertAlmostEqual(spin137F.r2[0], 46.014039109843, 4)
        self.assertAlmostEqual(spin137F.r2[1], 57.7984020245186, 4)
        self.assertAlmostEqual(spin137F.pA, 0.86473798251121, 4)
        self.assertAlmostEqual(spin137F.dw, 0.980787017888634, 4)
        self.assertAlmostEqual(spin137F.dwH, 1.1599527196e-05, 4)
        self.assertAlmostEqual(spin137F.kex, 286.743720388767, 4)
        self.assertAlmostEqual(spin137F.chi2, 15.2088757872867, 4)


    def test_sprangers_data_to_mq_ns_cpmg_2site(self, model=None):
        """Test the 'MQ NS CPMG 2-site' model fitting against Remco Sprangers' ClpP data.

        This uses the data from Remco Sprangers' paper at http://dx.doi.org/10.1073/pnas.0507370102.  This is MQ CPMG data with a fixed relaxation time period.
        """

        # Reset.
        self.interpreter.reset()

        # Create the data pipe and load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Sprangers_ClpP'
        self.interpreter.state.load(data_path+sep+'r2eff_values')

        # The model data pipe.
        model = 'MQ NS CPMG 2-site'
        self.interpreter.pipe.copy(pipe_from='base pipe', pipe_to=model, bundle_to='relax_disp')
        self.interpreter.pipe.switch(pipe_name=model)

        # Set the model.
        self.interpreter.relax_disp.select_model(model=model)

        # Cluster everything.
        self.interpreter.relax_disp.cluster(cluster_id='all', spin_id=":135-137")

        # Copy the data.
        self.interpreter.value.copy(pipe_from='R2eff', pipe_to=model, param='r2eff')

        # Alias the spins.
        spin135S = cdp.mol[0].res[0].spin[0]
        spin135F = cdp.mol[0].res[0].spin[1]
        spin137S = cdp.mol[0].res[1].spin[0]
        spin137F = cdp.mol[0].res[1].spin[1]

        # Set the cluster specific parameters (only for the first spin).
        spin135S.pA = 0.847378444499757
        spin135S.kex = 264.055604934724329

        # Set the initial parameter values.
        spin135S.r2 = [ 30.315119723745390, 37.411874745645299]
        spin135S.dw = 0.585574008745351
        spin135S.dwH = 0.000000000000002

        spin135F.r2 = [ 41.440843383778287, 56.989726795397893]
        spin135F.dw = 0.856699277665748
        spin135F.dwH = 0.000000000582587

        spin137S.r2 = [ 23.051695938570266, 28.352806483953824]
        spin137S.dw = 0.772904450844973
        spin137S.dwH = 0.183351478512970

        spin137F.r2 = [ 44.702032074210429, 56.453146052685319]
        spin137F.dw = 0.984568590342831
        spin137F.dwH = 0.000000001993458

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-5, grad_tol=None, max_iter=100, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s %-20s %-20s" % ("Parameter", "Value (:135@S)", "Value (:135@F)", "Value (:137@S)", "Value (:137@F)"))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("R2 (500 MHz)", spin135S.r2[0], spin135F.r2[0], spin137S.r2[0], spin137F.r2[0]))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("R2 (800 MHz)", spin135S.r2[1], spin135F.r2[1], spin137S.r2[1], spin137F.r2[1]))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("pA", spin135S.pA, spin135F.pA, spin137S.pA, spin137F.pA))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("dw", spin135S.dw, spin135F.dw, spin137S.dw, spin137F.dw))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("dwH", spin135S.dwH, spin135F.dwH, spin137S.dwH, spin137F.dwH))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("kex", spin135S.kex, spin135F.kex, spin137S.kex, spin137F.kex))
        print("%-20s %20.15g %20.15g %20.15g %20.15g\n" % ("chi2", spin135S.chi2, spin135F.chi2, spin137S.chi2, spin137F.chi2))

        # Checks for residue :135S.
        self.assertAlmostEqual(spin135S.r2[0], 30.3151197237454, 4)
        self.assertAlmostEqual(spin135S.r2[1], 37.4118747456453, 4)
        self.assertAlmostEqual(spin135S.pA, 0.847378444499757, 4)
        self.assertAlmostEqual(spin135S.dw, 0.585574008745351, 4)
        self.assertAlmostEqual(spin135S.dwH, 2e-15, 4)
        self.assertAlmostEqual(spin135S.kex, 264.055604934724, 4)
        self.assertAlmostEqual(spin135S.chi2, 13.859423588071, 1)

        # Checks for residue :135F.
        self.assertAlmostEqual(spin135F.r2[0], 41.4408433837783, 4)
        self.assertAlmostEqual(spin135F.r2[1], 56.9897267953979, 4)
        self.assertAlmostEqual(spin135F.pA, 0.847378444499757, 4)
        self.assertAlmostEqual(spin135F.dw, 0.856699277665748, 4)
        self.assertAlmostEqual(spin135F.dwH, 5.82587e-10, 4)
        self.assertAlmostEqual(spin135F.kex, 264.055604934724, 4)
        self.assertAlmostEqual(spin135F.chi2, 13.859423588071, 1)

        # Checks for residue :137S.
        self.assertAlmostEqual(spin137S.r2[0], 23.0516959385703, 4)
        self.assertAlmostEqual(spin137S.r2[1], 28.3528064839538, 4)
        self.assertAlmostEqual(spin137S.pA, 0.847378444499757, 4)
        self.assertAlmostEqual(spin137S.dw, 0.772904450844973, 4)
        self.assertAlmostEqual(spin137S.dwH, 0.18335147851297, 4)
        self.assertAlmostEqual(spin137S.kex, 264.055604934724, 4)
        self.assertAlmostEqual(spin137S.chi2, 13.859423588071, 1)

        # Checks for residue :137F.
        self.assertAlmostEqual(spin137F.r2[0], 44.7020320742104, 4)
        self.assertAlmostEqual(spin137F.r2[1], 56.4531460526853, 4)
        self.assertAlmostEqual(spin137F.pA, 0.847378444499757, 4)
        self.assertAlmostEqual(spin137F.dw, 0.984568590342831, 4)
        self.assertAlmostEqual(spin137F.dwH, 2.0931309e-09, 4)
        self.assertAlmostEqual(spin137F.kex, 264.055604934724, 4)
        self.assertAlmostEqual(spin137F.chi2, 13.859423588071, 1)


    def test_tp02_data_to_ns_r1rho_2site(self, model=None):
        """Test the relaxation dispersion 'NS R1rho 2-site' model fitting against the 'TP02' test data."""

        # Reset.
        self.interpreter.reset()

        # Create the data pipe and load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'r1rho_off_res_tp02'
        self.interpreter.state.load(data_path+sep+'r2eff_values')

        # The model data pipe.
        model = 'NS R1rho 2-site'
        self.interpreter.pipe.copy(pipe_from='base pipe', pipe_to=model, bundle_to='relax_disp')
        self.interpreter.pipe.switch(pipe_name=model)

        # Set the model.
        self.interpreter.relax_disp.select_model(model=model)

        # Copy the data.
        self.interpreter.value.copy(pipe_from='R2eff', pipe_to=model, param='r2eff')

        # Alias the spins.
        spin1 = cdp.mol[0].res[0].spin[0]
        spin2 = cdp.mol[0].res[1].spin[0]

        # Set the initial parameter values.
        spin1.r2 = [9.9963793866185, 15.0056724422684]
        spin1.pA = 0.779782428085762
        spin1.dw = 7.57855284496424
        spin1.kex = 1116.7911285203
        spin2.r2 = [11.9983346935434, 18.0076097513337]
        spin2.pA = 0.826666229688602
        spin2.dw = 9.5732624231366
        spin2.kex = 1380.46162655657

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:1)", "Value (:2)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin1.r2[0], spin2.r2[0]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin1.r2[1], spin2.r2[1]))
        print("%-20s %20.15g %20.15g" % ("pA", spin1.pA, spin2.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin1.dw, spin2.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin1.kex, spin2.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin1.chi2, spin2.chi2))

        # Checks for residue :1.
        self.assertAlmostEqual(spin1.r2[0], 9.9963793866185, 4)
        self.assertAlmostEqual(spin1.r2[1], 15.0056724422684, 4)
        self.assertAlmostEqual(spin1.pA, 0.779782428085762, 4)
        self.assertAlmostEqual(spin1.dw, 7.57855284496424, 4)
        self.assertAlmostEqual(spin1.kex/1000, 1116.7911285203/1000, 4)
        self.assertAlmostEqual(spin1.chi2, 0.0180437453493939, 4)

        # Checks for residue :2.
        self.assertAlmostEqual(spin2.r2[0], 11.9980071986823, 4)
        self.assertAlmostEqual(spin2.r2[1], 18.0073617211812, 4)
        self.assertAlmostEqual(spin2.pA, 0.827043369462035, 4)
        self.assertAlmostEqual(spin2.dw, 9.55524394456733, 4)
        self.assertAlmostEqual(spin2.kex/1000, 1387.8774707803/1000, 4)
        self.assertAlmostEqual(spin2.chi2, 0.000133191682505916, 4)


    def test_tp02_data_to_tp02(self):
        """Test the relaxation dispersion 'TP02' model curve fitting to fixed time synthetic data."""

        # Fixed time variable.
        ds.fixed = True

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'r1rho_off_res_tp02.py')

        # The original parameters.
        r1rho_prime = [[10.0, 15.0], [12.0, 18.0]]
        pA = 0.7654321
        kex = 1234.56789
        delta_omega = [7.0, 9.0]

        # Switch to the 'TP02' model data pipe, then check for each spin.
        self.interpreter.pipe.switch('TP02')
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[0]/10, r1rho_prime[spin_index][0]/10, 4)
            self.assertAlmostEqual(spin.r2[1]/10, r1rho_prime[spin_index][1]/10, 4)
            self.assertAlmostEqual(spin.dw, delta_omega[spin_index], 3)
            self.assertAlmostEqual(spin.kex/1000.0, kex/1000.0, 3)

            # Increment the spin index.
            spin_index += 1
