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
from tempfile import mkdtemp

# relax module imports.
from auto_analyses import relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from pipe_control.mol_res_spin import return_spin, spin_loop
from specific_analyses.relax_disp.disp_data import generate_r20_key, get_curve_type
from specific_analyses.relax_disp.variables import EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_PROTON_MQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_ZQ, EXP_TYPE_R1RHO, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_LIST_CPMG, MODEL_LM63, MODEL_M61B, MODEL_NOREX, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_R2EFF
from status import Status; status = Status()
from test_suite.clean_up import deletion
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


    def setup_hansen_cpmg_data(self, model=None):
        """Set up the data for the test_hansen_cpmg_data_*() system tests.

        @keyword model: The name of the model which will be tested.
        @type model:    str
        """

        # Create the data pipe and load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'
        self.interpreter.pipe.create(pipe_name='base pipe', pipe_type='relax_disp')
        self.interpreter.results.read(data_path+sep+'base_pipe')
        self.interpreter.deselect.spin(':4')

        # Set the nuclear isotope data.
        self.interpreter.spin.isotope('15N')

        # Create the R2eff data pipe and load the results.
        self.interpreter.pipe.create(pipe_name='R2eff', pipe_type='relax_disp')
        self.interpreter.pipe.switch(pipe_name='R2eff')
        self.interpreter.results.read(data_path+sep+'r2eff_pipe')
        self.interpreter.deselect.spin(':4')

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


    def setup_korzhnev_2005_data(self, data_list=[]):
        """Set up the data for the test_korzhnev_2005_data_*() system tests using the 'NS MMQ 2-site' model.

        This loads the proton-heteronuclear SQ, ZQ, DQ, and MQ (MMQ) data from:

            - Dmitry M. Korzhnev, Philipp Neudecker, Anthony Mittermaier, Vladislav Yu. Orekhov, and Lewis E. Kay (2005)  Multiple-site exchange in proteins studied with a suite of six NMR relaxation dispersion experiments: An application to the folding of a Fyn SH3 domain mutant.  127, 15602-15611 (U{DOI: 10.1021/ja054550e<http://dx.doi.org/10.1021/ja054550e>}).

        It consists of the 1H SQ, 15N SQ, ZQ, DQ, 1H MQ and 15N MQ data for residue Asp 9 of the Fyn SH3 domain mutant.


        @keyword data_list: The list of data to load.  It can contain 'SQ', '1H SQ', 'ZQ', 'DQ', 'MQ', and '1H MQ'.
        @type data_list:    list of str
        """

        # Create the data pipe and load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Korzhnev_et_al_2005'
        self.interpreter.pipe.create(pipe_name='Korzhnev et al., 2005', pipe_type='relax_disp')

        # Create the spin system.
        self.interpreter.spin.create(res_name='Asp', res_num=9, spin_name='H')
        self.interpreter.spin.create(res_name='Asp', res_num=9, spin_name='N')
        self.interpreter.spin.element('H', spin_id='@H')
        self.interpreter.spin.element('N', spin_id='@N')
        self.interpreter.spin.isotope('1H', spin_id='@H')
        self.interpreter.spin.isotope('15N', spin_id='@N')

        # Define the magnetic dipole-dipole relaxation interaction.
        self.interpreter.interatom.define(spin_id1=':9@N', spin_id2=':9@H', direct_bond=True)

        # The spectral data - experiment ID, R2eff file name, experiment type, spin ID string, spectrometer frequency in Hertz, relaxation time.
        data = [
            ['1H SQ', '1H_SQ_CPMG_500_MHz',  'hs_500.res', EXP_TYPE_CPMG_PROTON_SQ, ':9@H', 500e6, 0.03],
            ['1H SQ', '1H_SQ_CPMG_600_MHz',  'hs_600.res', EXP_TYPE_CPMG_PROTON_SQ, ':9@H', 600e6, 0.03],
            ['1H SQ', '1H_SQ_CPMG_800_MHz',  'hs_800.res', EXP_TYPE_CPMG_PROTON_SQ, ':9@H', 800e6, 0.03],
            ['SQ',    '15N_SQ_CPMG_500_MHz', 'ns_500.res', EXP_TYPE_CPMG_SQ,        ':9@N', 500e6, 0.04],
            ['SQ',    '15N_SQ_CPMG_600_MHz', 'ns_600.res', EXP_TYPE_CPMG_SQ,        ':9@N', 600e6, 0.04],
            ['SQ',    '15N_SQ_CPMG_800_MHz', 'ns_800.res', EXP_TYPE_CPMG_SQ,        ':9@N', 800e6, 0.04],
            ['DQ',    '15N_DQ_CPMG_500_MHz', 'dq_500.res', EXP_TYPE_CPMG_DQ,        ':9@N', 500e6, 0.03],
            ['DQ',    '15N_DQ_CPMG_600_MHz', 'dq_600.res', EXP_TYPE_CPMG_DQ,        ':9@N', 600e6, 0.03],
            ['DQ',    '15N_DQ_CPMG_800_MHz', 'dq_800.res', EXP_TYPE_CPMG_DQ,        ':9@N', 800e6, 0.03],
            ['ZQ',    '15N_ZQ_CPMG_500_MHz', 'zq_500.res', EXP_TYPE_CPMG_ZQ,        ':9@N', 500e6, 0.03],
            ['ZQ',    '15N_ZQ_CPMG_600_MHz', 'zq_600.res', EXP_TYPE_CPMG_ZQ,        ':9@N', 600e6, 0.03],
            ['ZQ',    '15N_ZQ_CPMG_800_MHz', 'zq_800.res', EXP_TYPE_CPMG_ZQ,        ':9@N', 800e6, 0.03],
            ['1H MQ', '1H_MQ_CPMG_500_MHz',  'hm_500.res', EXP_TYPE_CPMG_PROTON_MQ, ':9@H', 500e6, 0.02],
            ['1H MQ', '1H_MQ_CPMG_600_MHz',  'hm_600.res', EXP_TYPE_CPMG_PROTON_MQ, ':9@H', 600e6, 0.02],
            ['1H MQ', '1H_MQ_CPMG_800_MHz',  'hm_800.res', EXP_TYPE_CPMG_PROTON_MQ, ':9@H', 800e6, 0.02],
            ['MQ',    '15N_MQ_CPMG_500_MHz', 'nm_500.res', EXP_TYPE_CPMG_MQ,        ':9@N', 500e6, 0.02],
            ['MQ',    '15N_MQ_CPMG_600_MHz', 'nm_600.res', EXP_TYPE_CPMG_MQ,        ':9@N', 600e6, 0.02],
            ['MQ',    '15N_MQ_CPMG_800_MHz', 'nm_800.res', EXP_TYPE_CPMG_MQ,        ':9@N', 800e6, 0.02]
        ]
        cpmg_frqs_1h_sq = [67.0, 133.0, 267.0, 400.0, 533.0, 667.0, 800.0, 933.0, 1067.0, 1600.0, 2133.0, 2667.0]
        cpmg_frqs_sq = [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0]
        cpmg_frqs_dq = [33.0, 67.0, 133.0, 200.0, 267.0, 333.0, 400.0, 467.0, 533.0, 667.0, 800.0, 933.0, 1067.0]
        cpmg_frqs_zq = [33.0, 67.0, 133.0, 200.0, 267.0, 333.0, 400.0, 467.0, 533.0, 667.0, 800.0, 933.0, 1067.0]
        cpmg_frqs_1h_mq = [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 1000.0, 1500.0, 2000.0, 2500.0]
        cpmg_frqs_mq = [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0]

        # Loop over the files, reading in the data.
        for data_type, id, file, exp_type, spin_id, H_frq, relax_time in data:
            # Skip undesired data.
            if data_type not in data_list:
                continue

            # Alias the CPMG frequencies.
            if data_type == 'SQ':
                cpmg_frqs = cpmg_frqs_sq
            elif data_type == '1H SQ':
                cpmg_frqs = cpmg_frqs_1h_sq
            elif data_type == 'DQ':
                cpmg_frqs = cpmg_frqs_dq
            elif data_type == 'ZQ':
                cpmg_frqs = cpmg_frqs_zq
            elif data_type == '1H MQ':
                cpmg_frqs = cpmg_frqs_1h_mq
            elif data_type == 'MQ':
                cpmg_frqs = cpmg_frqs_mq

            # Loop over each CPMG frequency.
            for cpmg_frq in cpmg_frqs:
                # The id.
                new_id = "%s_%s" % (id, cpmg_frq)

                # Set the NMR field strength.
                self.interpreter.spectrometer.frequency(id=new_id, frq=H_frq)

                # Set the relaxation dispersion experiment type.
                self.interpreter.relax_disp.exp_type(spectrum_id=new_id, exp_type=exp_type)

                # Relaxation dispersion CPMG constant time delay T (in s).
                self.interpreter.relax_disp.relax_time(spectrum_id=new_id, time=relax_time)

                # Set the CPMG frequency.
                self.interpreter.relax_disp.cpmg_frq(spectrum_id=new_id, cpmg_frq=cpmg_frq)

            # Read the R2eff data.
            self.interpreter.relax_disp.r2eff_read_spin(id=id, file=file, dir=data_path, spin_id=spin_id, disp_point_col=1, data_col=2, error_col=3)

        # Change the model.
        self.interpreter.relax_disp.select_model('NS MMQ 2-site')


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
            self.assertAlmostEqual(spin.r2['R1rho - 800.00000000 MHz']/10, r1rho_prime[spin_index]/10, 2)
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
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].r2eff['r1rho_1200.00000000_0.000_1000.000'], res_data[i][0], places=2)
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].r2eff['r1rho_1200.00000000_0.000_2000.000'], res_data[i][1], places=2)
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].i0['r1rho_1200.00000000_0.000_1000.000']/10000, res_data[i][2]/10000, places=3)
            self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].i0['r1rho_1200.00000000_0.000_2000.000']/10000, res_data[i][3]/10000, places=3)

            # Check the simulation errors.
            self.assert_(cdp.mol[0].res[i].spin[0].r2eff_err['r1rho_1200.00000000_0.000_1000.000'] < 5.0)
            self.assert_(cdp.mol[0].res[i].spin[0].r2eff_err['r1rho_1200.00000000_0.000_2000.000'] < 5.0)
            self.assert_(cdp.mol[0].res[i].spin[0].i0_err['r1rho_1200.00000000_0.000_1000.000']/10000 < 5.0)
            self.assert_(cdp.mol[0].res[i].spin[0].i0_err['r1rho_1200.00000000_0.000_2000.000']/10000 < 5.0)

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

        # Load the R2eff results file.
        file_name = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'+sep+'r2eff_pipe'
        self.interpreter.results.read(file_name)
        self.interpreter.deselect.spin(':4')

        # The spin isotopes.
        self.interpreter.spin.isotope("15N")

        # Generate the input files.
        self.interpreter.relax_disp.catia_input(dir=ds.tmpdir, force=True)

        # Check the r2eff set files.
        print("\nChecking the R2eff input set files.")
        files = ['data_set_500.inp', 'data_set_500.inp']
        for file in files:
            self.assert_(access(ds.tmpdir+sep+file, F_OK))
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
        file = open(ds.tmpdir+sep+files[0])
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
            self.assert_(access(ds.tmpdir+sep+'input_r2eff'+sep+file, F_OK))
        spin_70_N_500 = [
            "#        nu_cpmg(Hz)              R2(1/s)              Esd(R2)\n",
            "  66.666600000000003   16.045540885533605    0.310924686180635\n",
            " 133.333300000000008   14.877924861181727    0.303217270671013\n",
            " 200.000000000000000   14.357820247260586    0.299894424543361\n",
            " 266.666600000000017   12.664494620416516    0.289532060485796\n",
            " 333.333300000000008   12.363204802467891    0.287759631749322\n",
            " 400.000000000000000   11.092532381134513    0.280514035409862\n",
            " 466.666600000000017   10.566090057649893    0.277618625949722\n",
            " 533.333300000000008    9.805806894657803    0.273544382200754\n",
            " 600.000000000000000    9.564300692201730    0.272276309984954\n",
            " 666.666600000000017    9.015633750407980    0.269441511838159\n",
            " 733.333300000000008    8.607764958055581    0.267375134391053\n",
            " 800.000000000000000    8.279997179221338    0.265739551961997\n",
            " 866.666600000000017    8.474535940963516    0.266707642726566\n",
            " 933.333300000000008    8.158972897365194    0.265141210539941\n",
            "1000.000000000000000    7.988630509501972    0.264304105548559\n",
        ]
        file = open(ds.tmpdir+sep+'input_r2eff'+sep+files[0])
        lines = file.readlines()
        file.close()
        for i in range(len(lines)):
            print("%s\"%s\\n\"," % (" "*12, lines[i][:-1]))
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
        self.interpreter.state.save('analysis_heights', dir=ds.tmpdir, force=True)

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # The 'No Rex' model checks.
        self.interpreter.pipe.switch(pipe_name='No Rex')
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[r20_key1], 10.5340593984683, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 16.1112170102734, 3)
        self.assertAlmostEqual(spin70.chi2, 8973.84810025761, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.83139953954648, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 8.90856319376098, 3)
        self.assertAlmostEqual(spin71.chi2, 3908.00127830003, 3)

        # The 'LM63' model checks.
        self.interpreter.pipe.switch(pipe_name='LM63')
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("phi_ex", spin70.phi_ex, spin71.phi_ex))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.74326615264889, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 6.57331164382438, 3)
        self.assertAlmostEqual(spin70.phi_ex, 0.312767653822936, 3)
        self.assertAlmostEqual(spin70.kex/10000, 4723.44390412119/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 363.534049046805, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.00778024769786, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.83343630016037, 3)
        self.assertAlmostEqual(spin71.phi_ex, 0.0553791362097596, 3)
        self.assertAlmostEqual(spin71.kex/10000, 2781.67925957068/10000, 3)
        self.assertAlmostEqual(spin71.chi2, 17.0776426190574, 3)

        # The 'CR72' model checks.
        self.interpreter.pipe.switch(pipe_name='CR72')
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.97233943292193, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.409506394526, 3)
        self.assertAlmostEqual(spin70.pA, 0.989856804525044, 3)
        self.assertAlmostEqual(spin70.dw, 5.60889078920945, 3)
        self.assertAlmostEqual(spin70.kex/10000, 1753.01607073019/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 53.8382158551706, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.003171547206, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.90210797727492, 3)
        self.assertAlmostEqual(spin71.pA, 0.985922406455826, 3)
        self.assertAlmostEqual(spin71.dw, 2.00500965892672, 3)
        self.assertAlmostEqual(spin71.kex/10000, 2481.10839579617/10000, 3)
        self.assertAlmostEqual(spin71.chi2, 15.6595374286822, 3)


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

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # The 'No Rex' model checks.
        self.interpreter.pipe.switch(pipe_name='No Rex')
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[r20_key1], 10.5340593984683, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 16.1112170102734, 3)
        self.assertAlmostEqual(spin70.chi2/10000, 8973.84810025761/10000, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.83139953954648, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 8.90856319376098, 3)
        self.assertAlmostEqual(spin71.chi2/10000, 3908.00127830003/10000, 3)

        # The 'CR72' model checks.
        self.interpreter.pipe.switch(pipe_name='CR72')
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.97233943292193, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.409506394526, 3)
        self.assertAlmostEqual(spin70.pA, 0.989856804525044, 3)
        self.assertAlmostEqual(spin70.dw, 5.60889078920945, 3)
        self.assertAlmostEqual(spin70.kex/10000, 1753.01607073019/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 53.8382158551706, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.003171547206, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.90210797727492, 3)
        self.assertAlmostEqual(spin71.pA, 0.985922406455826, 3)
        self.assertAlmostEqual(spin71.dw, 2.00500965892672, 3)
        self.assertAlmostEqual(spin71.kex/10000, 2481.10839579617/10000, 3)
        self.assertAlmostEqual(spin71.chi2, 15.6595374286822, 3)

        # The 'NS CPMG 2-site expanded' model checks.
        self.interpreter.pipe.switch(pipe_name='NS CPMG 2-site expanded')
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.95812089063457, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.39651467124235, 3)
        self.assertAlmostEqual(spin70.pA, 0.989700942551209, 3)
        self.assertAlmostEqual(spin70.dw, 5.67324269421426, 3)
        self.assertAlmostEqual(spin70.kex/10000, 1713.59762249271/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 52.5106889105996, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 4.99897355555516, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.89823239900183, 3)
        self.assertAlmostEqual(spin71.pA, 0.986704447530285, 3)
        self.assertAlmostEqual(spin71.dw, 2.09198758585969, 3)
        self.assertAlmostEqual(spin71.kex/10000, 2438.29751770245/10000, 3)
        self.assertAlmostEqual(spin71.chi2, 15.1644904768219, 3)

        # The final data pipe checks.
        self.interpreter.pipe.switch(pipe_name='final')
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        self.assertEqual(spin70.model, 'NS CPMG 2-site expanded')
        self.assertEqual(spin71.model, 'NS CPMG 2-site expanded')


    def test_hansen_cpmg_data_auto_analysis_r2eff(self):
        """Test of the dispersion auto-analysis using Dr. Flemming Hansen's CPMG data (using the R2eff data directly instead of peak intensities).

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
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'hansen_r2eff_data.py')
        self.interpreter.state.save('analysis_r2eff', dir=ds.tmpdir, force=True)

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # The 'No Rex' model checks.
        self.interpreter.pipe.switch(pipe_name='No Rex')
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[r20_key1], 10.5340593984683, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 16.1112170102734, 3)
        self.assertAlmostEqual(spin70.chi2, 8973.84810025761, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.83139953954648, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 8.90856319376098, 3)
        self.assertAlmostEqual(spin71.chi2, 3908.00127830003, 3)

        # The 'LM63' model checks.
        self.interpreter.pipe.switch(pipe_name='LM63')
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("phi_ex", spin70.phi_ex, spin71.phi_ex))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.74326615264889, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 6.57331164382438, 3)
        self.assertAlmostEqual(spin70.phi_ex, 0.312767653822936, 3)
        self.assertAlmostEqual(spin70.kex/10000, 4723.44390412119/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 363.534049046805, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.00778024769786, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.83343630016037, 3)
        self.assertAlmostEqual(spin71.phi_ex, 0.0553791362097596, 3)
        self.assertAlmostEqual(spin71.kex/10000, 2781.67925957068/10000, 3)
        self.assertAlmostEqual(spin71.chi2, 17.0776426190574, 3)

        # The 'CR72' model checks.
        self.interpreter.pipe.switch(pipe_name='CR72')
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.97233943292193, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.409506394526, 3)
        self.assertAlmostEqual(spin70.pA, 0.989856804525044, 3)
        self.assertAlmostEqual(spin70.dw, 5.60889078920945, 3)
        self.assertAlmostEqual(spin70.kex/10000, 1753.01607073019/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 53.8382158551706, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.00317154730225, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.90210797713541, 3)
        self.assertAlmostEqual(spin71.pA, 0.985922406429147, 3)
        self.assertAlmostEqual(spin71.dw, 2.00500965887772, 3)
        self.assertAlmostEqual(spin71.kex/10000, 2481.10839579804/10000, 3)
        self.assertAlmostEqual(spin71.chi2, 15.6595374288635, 3)


    def test_hansen_cpmg_data_missing_auto_analysis(self):
        """Test of the dispersion auto-analysis using Dr. Flemming Hansen's CPMG data with parts missing.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Set the model.
        ds.models = [
            MODEL_R2EFF,
            MODEL_NOREX,
            MODEL_CR72,
            MODEL_NS_CPMG_2SITE_EXPANDED
        ]

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'hansen_data_missing.py')
        self.interpreter.state.save('analysis_heights', dir=ds.tmpdir, force=True)

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # The 'No Rex' model checks.
        self.interpreter.pipe.switch(pipe_name='No Rex')
        spin4 = return_spin(":4")
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s %-20s" % ("Parameter", "Value (:4)", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g %20.15g" % ("R2 (500 MHz)", spin4.r2[r20_key1], spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g %20.15g" % ("R2 (800 MHz)", spin4.r2[r20_key2], spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g %20.15g\n" % ("chi2", spin4.chi2, spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin4.r2[r20_key1], 1.60463084515171, 3)
        self.assertAlmostEqual(spin4.r2[r20_key2], 1.63220784651911, 3)
        self.assertAlmostEqual(spin4.chi2, 29.2929926382771, 3)
        self.assertAlmostEqual(spin70.r2[r20_key1], 10.534285641325, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 16.1112794857068, 3)
        self.assertAlmostEqual(spin70.chi2, 9634.52343363306, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.83136858890037, 3)
        self.assertAlmostEqual(spin71.chi2, 127.636629246204, 3)

        # The 'CR72' model checks.
        self.interpreter.pipe.switch(pipe_name='CR72')
        spin4 = return_spin(":4")
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s %-20s" % ("Parameter", "Value (:4)", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g %20.15g" % ("R2 (500 MHz)", spin4.r2[r20_key1], spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g %20.15g" % ("R2 (800 MHz)", spin4.r2[r20_key2], spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g %20.15g" % ("pA", spin4.pA, spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g %20.15g" % ("dw", spin4.dw, spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g %20.15g" % ("kex", spin4.kex, spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g %20.15g\n" % ("chi2", spin4.chi2, spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin4.r2[r20_key1], 1.57151065615839, 2)
        self.assertAlmostEqual(spin4.r2[r20_key2], 1.58059682984398, 3)
        self.assertAlmostEqual(spin4.pA, 0.500019733844535, 3)
        self.assertAlmostEqual(spin4.dw, 6.57514296850066, 3)
        self.assertAlmostEqual(spin4.kex/10000, 0.209808727621065/10000, 3)
        self.assertAlmostEqual(spin4.chi2, 19.2950428365527, 3)
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.97326447937972, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.3417810084784, 3)
        self.assertAlmostEqual(spin70.pA, 0.98993823805518, 3)
        self.assertAlmostEqual(spin70.dw, 5.5907147782533, 3)
        self.assertAlmostEqual(spin70.kex/10000, 1828.31716745568/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 55.2887487843661, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 4.92979173044978, 3)
        self.assertAlmostEqual(spin71.pA, 0.528883026272818, 3)
        self.assertAlmostEqual(spin71.dw, 0.488914314879541, 3)
        self.assertAlmostEqual(spin71.kex/10000, 2568.1215115528/10000, 3)
        self.assertAlmostEqual(spin71.chi2, 4.01287787463568, 3)


    def test_hansen_cpmg_data_to_cr72(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the CR72 dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='CR72')

        # Alias the spins.
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # Set the initial parameter values.
        spin70.r2 = {r20_key1: 7.0, r20_key2: 9.0}
        spin70.pA = 0.9
        spin70.dw = 6.0
        spin70.kex = 1500.0
        spin71.r2 = {r20_key1: 5, r20_key2: 9.0}
        spin71.pA = 0.9
        spin71.dw = 4.0
        spin71.kex = 1900.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.97260604007474, 4)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.41009302654463, 4)
        self.assertAlmostEqual(spin70.pA, 0.989856764756131, 4)
        self.assertAlmostEqual(spin70.dw, 5.60887354423638, 4)
        self.assertAlmostEqual(spin70.kex/1000, 1752.75852303464/1000, 4)
        self.assertAlmostEqual(spin70.chi2, 53.8382124791236, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.00310788169096, 4)
        self.assertAlmostEqual(spin71.pA, 0.985946406482083, 4)
        self.assertAlmostEqual(spin71.dw, 2.00673221077749, 4)
        self.assertAlmostEqual(spin71.kex/1000, 2480.52477627298/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 15.6595392846911, 4)

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
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # Set the initial parameter values.
        spin70.r2a = {r20_key1: 7.0, r20_key2: 9.0}
        spin70.r2b = {r20_key1: 7.0, r20_key2: 9.0}
        spin70.pA = 0.9
        spin70.dw = 6.0
        spin70.kex = 1500.0
        spin71.r2a = {r20_key1: 5.0, r20_key2: 9.0}
        spin71.r2b = {r20_key1: 5.0, r20_key2: 9.0}
        spin71.pA = 0.9
        spin71.dw = 4.0
        spin71.kex = 1900.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2A (500 MHz)", spin70.r2a[r20_key1], spin71.r2a[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2B (500 MHz)", spin70.r2b[r20_key1], spin71.r2b[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2A (800 MHz)", spin70.r2a[r20_key2], spin71.r2a[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("R2B (800 MHz)", spin70.r2b[r20_key2], spin71.r2b[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2a[r20_key1], 6.69755822995605, 4)
        self.assertAlmostEqual(spin70.r2b[r20_key1], 2.75294308690228, 4)
        self.assertAlmostEqual(spin70.r2a[r20_key2], 8.18393516578432, 4)
        self.assertAlmostEqual(spin70.r2b[r20_key2], 97.3047470071814, 4)
        self.assertAlmostEqual(spin70.pA, 0.988929729034413, 4)
        self.assertAlmostEqual(spin70.dw, 5.51938354518713, 4)
        self.assertAlmostEqual(spin70.kex/1000, 1892.82682092974/1000, 4)
        self.assertAlmostEqual(spin70.chi2, 48.5815698897158, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2a[r20_key1], 4.79839795614044, 4)
        self.assertAlmostEqual(spin71.r2b[r20_key1], 12.8793124032989, 4)
        self.assertAlmostEqual(spin71.pA, 0.978971448838756, 4)
        self.assertAlmostEqual(spin71.dw, 1.67873004594096, 4)
        self.assertAlmostEqual(spin71.kex/1000, 2527.80893069607/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 14.3394771268074, 4)

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
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # Set the initial parameter values.
        spin70.r2 = {r20_key1: 8.8, r20_key2: 16.6}
        spin70.dw = 10.0
        spin70.pA = 0.5
        spin70.tex = 1000.09
        spin71.r2 = {r20_key1: 1.0, r20_key2: 1.0}
        spin71.dw = 10.0
        spin71.pA = 0.95
        spin71.tex = 0.1

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-10, grad_tol=None, max_iter=10000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("tex", spin70.tex, spin71.tex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[r20_key1], 7.24471197811838, 4)
        self.assertAlmostEqual(spin70.r2[r20_key2], 10.0571040704729, 4)
        self.assertAlmostEqual(spin70.dw, 5.2116923222744, 4)
        self.assertAlmostEqual(spin70.pA, 0.990253627907212, 4)
        self.assertAlmostEqual(spin70.tex*1000, 0.000638394793480444*1000, 4)
        self.assertAlmostEqual(spin70.chi2, 93.5135798618747, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.05971235970214, 4)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.96641194493447, 4)
        self.assertAlmostEqual(spin71.dw, 0.435389946897141, 4)
        self.assertAlmostEqual(spin71.pA, 0.500000000213519, 3)
        self.assertAlmostEqual(spin71.tex*1000, 0.000372436400585538*1000, 4)
        self.assertAlmostEqual(spin71.chi2, 23.7895798801404, 4)


    def test_hansen_cpmg_data_to_lm63(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the LM63 dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='LM63')

        # Alias the spins.
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # Set the initial parameter values.
        spin70.r2 = {r20_key1: 7.0, r20_key2: 7.0}
        spin70.phi_ex = 0.3
        spin70.kex = 5000.0
        spin71.r2 = {r20_key1: 5.0, r20_key2: 9.0}
        spin71.phi_ex = 0.1
        spin71.kex = 2500.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-25, grad_tol=None, max_iter=10000000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("phi_ex", spin70.phi_ex, spin71.phi_ex))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.74362294539099)
        self.assertAlmostEqual(spin70.r2[r20_key2], 6.57406797067481)
        self.assertAlmostEqual(spin70.phi_ex, 0.312733013751449)
        self.assertAlmostEqual(spin70.kex/1000, 4723.09897146338/1000)
        self.assertAlmostEqual(spin70.chi2, 363.534044873483)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.00776657712558)
        self.assertAlmostEqual(spin71.phi_ex, 0.0553787828347638)
        self.assertAlmostEqual(spin71.kex/1000, 2781.72293906248/1000)
        self.assertAlmostEqual(spin71.chi2, 17.0776399916287)


    def test_hansen_cpmg_data_to_ns_cpmg_2site_3D(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the 'NS CPMG 2-site 3D' dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='NS CPMG 2-site 3D')

        # Alias the spins.
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # Set the initial parameter values.
        spin70.r2 = {r20_key1: 6.994165925, r20_key2: 9.428129427}
        spin70.pA = 0.9897754407
        spin70.dw = 5.642418428
        spin70.kex = 1743.666375
        spin71.r2 = {r20_key1: 4.978654237, r20_key2: 9.276918959}
        spin71.pA = 0.9968032899
        spin71.dw = 4.577891393
        spin71.kex = 1830.044597

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=False, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.95797760459016, 4)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.39628959312699, 4)
        self.assertAlmostEqual(spin70.pA, 0.989700985380975, 4)
        self.assertAlmostEqual(spin70.dw, 5.6733714171086, 4)
        self.assertAlmostEqual(spin70.kex/1000, 1713.63101361545/1000, 4)
        self.assertAlmostEqual(spin70.chi2, 52.5106928523775, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[r20_key1], 4.99893565849977, 4)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.89825625944034, 4)
        self.assertAlmostEqual(spin71.pA, 0.986716058519642, 4)
        self.assertAlmostEqual(spin71.dw, 2.09292495350993, 4)
        self.assertAlmostEqual(spin71.kex/1000, 2438.04423541463/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 15.164490242352, 4)

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
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # Set the initial parameter values.
        spin70.r2a = {r20_key1: 6.644753428, r20_key2: 7.891776687}
        spin70.r2b = {r20_key1: 7.163478485, r20_key2: 138.5170395}
        spin70.pA = 0.9884781357
        spin70.dw = 5.456507396
        spin70.kex = 1906.521189
        spin71.r2a = {r20_key1: 4.99893524108981, r20_key2: 100.0}
        spin71.r2b = {r20_key1: 8.27456243639973, r20_key2: 100.0}
        spin71.pA = 0.986709616684097
        spin71.dw = 2.09245158280905
        spin71.kex = 2438.2766211401

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=False, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2A (500 MHz)", spin70.r2a[r20_key1], spin71.r2a[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2B (500 MHz)", spin70.r2b[r20_key1], spin71.r2b[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2A (800 MHz)", spin70.r2a[r20_key2], spin71.r2a[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("R2B (800 MHz)", spin70.r2b[r20_key2], spin71.r2b[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2a[r20_key1], 6.61176004043484, 4)
        self.assertAlmostEqual(spin70.r2b[r20_key1], 7.4869316381241, 4)
        self.assertAlmostEqual(spin70.r2a[r20_key2], 7.78200386067591, 4)
        self.assertAlmostEqual(spin70.r2b[r20_key2], 141.703593742468, 4)
        self.assertAlmostEqual(spin70.pA, 0.988404987055969, 4)
        self.assertAlmostEqual(spin70.dw, 5.4497360203213, 4)
        self.assertAlmostEqual(spin70.kex/1000, 1934.09304607082/1000, 4)
        self.assertAlmostEqual(spin70.chi2, 44.6793752187925, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2a[r20_key1], 4.6013095731966, 4)
        self.assertAlmostEqual(spin71.r2b[r20_key1], 13.3245678276332, 4)
        self.assertAlmostEqual(spin71.r2a[r20_key2], 2.08243621257779, 4)
        self.assertAlmostEqual(spin71.r2b[r20_key2], 153.355765094575, 4)
        self.assertAlmostEqual(spin71.pA, 0.9665748685124, 4)
        self.assertAlmostEqual(spin71.dw, 1.41898001408953, 4)
        self.assertAlmostEqual(spin71.kex/1000, 2580.65795560688/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 13.4937006732165, 4)

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
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # Set the initial parameter values.
        spin70.r2 = {r20_key1: 7.0, r20_key2: 9.0}
        spin70.pA = 0.9
        spin70.dw = 6.0
        spin70.kex = 1500.0
        spin71.r2 = {r20_key1: 5.0, r20_key2: 9.0}
        spin71.pA = 0.9
        spin71.dw = 4.0
        spin71.kex = 1900.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.9580924599737, 4)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.39653925942454, 4)
        self.assertAlmostEqual(spin70.pA, 0.989701162762885, 4)
        self.assertAlmostEqual(spin70.dw, 5.67331932250604, 4)
        self.assertAlmostEqual(spin70.kex/1000, 1713.56202177775/1000, 4)
        self.assertAlmostEqual(spin70.chi2, 52.510685225092, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[r20_key1], 4.99888477245306, 4)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.89804393936759, 4)
        self.assertAlmostEqual(spin71.pA, 0.986705757536079, 4)
        self.assertAlmostEqual(spin71.dw, 2.09219403018313, 4)
        self.assertAlmostEqual(spin71.kex/1000, 2438.48401194464/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 15.1644881118593, 4)

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
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # Set the initial parameter values.
        spin70.r2 = {r20_key1: 6.996327746, r20_key2: 9.452051268}
        spin70.pA = 0.9897519798
        spin70.dw = 5.644862195
        spin70.kex = 1723.820567
        spin71.r2 = {r20_key1: 4.978654237, r20_key2: 9.276918959}
        spin71.pA = 0.9968032899
        spin71.dw = 4.577891393
        spin71.kex = 1830.044597

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=False, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin70.pA, spin71.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin70.dw, spin71.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.95543947938561, 1)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.38991914134929, 1)
        self.assertAlmostEqual(spin70.pA, 0.989702750971153, 3)
        self.assertAlmostEqual(spin70.dw, 5.67527122494516, 1)
        self.assertAlmostEqual(spin70.kex/1000, 1715.72032391817/1000, 1)
        self.assertAlmostEqual(spin70.chi2, 52.5011991483842, 1)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[r20_key1], 4.992594256544, 1)
        self.assertAlmostEqual(spin71.pA, 0.992258541625787, 2)
        self.assertAlmostEqual(spin71.dw/100, 2.75140650899058/100, 2)
        self.assertAlmostEqual(spin71.kex/100000, 2106.60885247431/100000, 2)
        self.assertAlmostEqual(spin71.chi2/100, 17.3293856656588/100, 1)

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
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # Set the initial parameter values.
        spin70.r2a = {r20_key1: 6.44836878645126, r20_key2: 7.00382877393494}
        spin70.r2b = {r20_key1: 12.2083127421994, r20_key2: 199.862962628402}
        spin70.pA = 0.987648082613451
        spin70.dw = 5.30679853807572
        spin70.kex = 2033.25380420666
        spin71.r2a = {r20_key1: 4.992594256544, r20_key2: 6.98674718938435}
        spin71.r2b = {r20_key1: 4.992594256544, r20_key2: 6.98674718938435}
        spin71.pA = 0.992258541625787
        spin71.dw = 2.75140650899058
        spin71.kex = 2106.60885247431

        # Low precision optimisation.
        self.interpreter.calc()

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.chi2/10, 45.773987568491123/10, 2)
        self.assertAlmostEqual(spin71.chi2/10, 17.329385665659192/10, 2)


    def test_hansen_cpmgfit_input(self):
        """Conversion of Dr. Flemming Hansen's CPMG R2eff values into input files for CPMGFit.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Load the R2eff results file.
        file_name = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'+sep+'r2eff_pipe'
        self.interpreter.results.read(file_name)
        self.interpreter.deselect.spin(':4')

        # Set up the model.
        self.interpreter.relax_disp.select_model('LM63')

        # Generate the input files.
        self.interpreter.relax_disp.cpmgfit_input(force=True, dir=ds.tmpdir)

        # What the files should contain.
        batch_file = ['#! /bin/sh\n', '\n', 'cpmgfit -grid -xmgr -f spin_70_N.in | tee spin_70_N.out\n', 'cpmgfit -grid -xmgr -f spin_71_N.in | tee spin_71_N.out\n']
        spin1 = [
            "title :70@N\n",
            "fields 2 11.7432964915 18.7892743865\n",
            "function CPMG\n",
            "R2 1 10 20\n",
            "Rex 0 100.0 100\n",
            "Tau 0 10.0 100\n",
            "xmgr\n",
            "@ xaxis label \"1/tcp (1/ms)\"\n",
            "@ yaxis label \"R2(tcp) (rad/s)\"\n",
            "@ xaxis ticklabel format decimal\n",
            "@ yaxis ticklabel format decimal\n",
            "@ xaxis ticklabel char size 0.8\n",
            "@ yaxis ticklabel char size 0.8\n",
            "@ world xmin 0.0\n",
            "data\n",
            "0.133333             16.045541            0.310925             11.743296           \n",
            "0.266667             14.877925            0.303217             11.743296           \n",
            "0.400000             14.357820            0.299894             11.743296           \n",
            "0.533333             12.664495            0.289532             11.743296           \n",
            "0.666667             12.363205            0.287760             11.743296           \n",
            "0.800000             11.092532            0.280514             11.743296           \n",
            "0.933333             10.566090            0.277619             11.743296           \n",
            "1.066667             9.805807             0.273544             11.743296           \n",
            "1.200000             9.564301             0.272276             11.743296           \n",
            "1.333333             9.015634             0.269442             11.743296           \n",
            "1.466667             8.607765             0.267375             11.743296           \n",
            "1.600000             8.279997             0.265740             11.743296           \n",
            "1.733333             8.474536             0.266708             11.743296           \n",
            "1.866667             8.158973             0.265141             11.743296           \n",
            "2.000000             7.988631             0.264304             11.743296           \n",
            "0.133333             22.224914            0.166231             18.789274           \n",
            "0.266667             21.230874            0.162377             18.789274           \n",
            "0.400000             20.603704            0.160017             18.789274           \n",
            "0.533333             20.327797            0.158996             18.789274           \n",
            "0.666667             18.855377            0.153719             18.789274           \n",
            "0.800000             18.537531            0.152617             18.789274           \n",
            "0.933333             17.508069            0.149138             18.789274           \n",
            "1.066667             16.035604            0.144391             18.789274           \n",
            "1.200000             15.168192            0.141717             18.789274           \n",
            "1.333333             14.431802            0.139516             18.789274           \n",
            "1.466667             14.034137            0.138354             18.789274           \n",
            "1.600000             12.920148            0.135192             18.789274           \n",
            "1.733333             12.653673            0.134456             18.789274           \n",
            "1.866667             12.610864            0.134338             18.789274           \n",
            "2.000000             11.969303            0.132601             18.789274           \n"
        ]
        spin2 = [
            "title :71@N\n",
            "fields 2 11.7432964915 18.7892743865\n",
            "function CPMG\n",
            "R2 1 10 20\n",
            "Rex 0 100.0 100\n",
            "Tau 0 10.0 100\n",
            "xmgr\n",
            "@ xaxis label \"1/tcp (1/ms)\"\n",
            "@ yaxis label \"R2(tcp) (rad/s)\"\n",
            "@ xaxis ticklabel format decimal\n",
            "@ yaxis ticklabel format decimal\n",
            "@ xaxis ticklabel char size 0.8\n",
            "@ yaxis ticklabel char size 0.8\n",
            "@ world xmin 0.0\n",
            "data\n",
            "0.133333             7.044342             0.170035             11.743296           \n",
            "0.266667             6.781033             0.169228             11.743296           \n",
            "0.400000             6.467623             0.168279             11.743296           \n",
            "0.533333             6.333340             0.167876             11.743296           \n",
            "0.666667             6.323238             0.167846             11.743296           \n",
            "0.800000             6.005245             0.166902             11.743296           \n",
            "0.933333             5.767052             0.166203             11.743296           \n",
            "1.066667             5.476968             0.165361             11.743296           \n",
            "1.200000             5.469949             0.165341             11.743296           \n",
            "1.333333             5.295113             0.164838             11.743296           \n",
            "1.466667             5.435648             0.165242             11.743296           \n",
            "1.600000             5.410400             0.165169             11.743296           \n",
            "1.733333             5.437554             0.165247             11.743296           \n",
            "1.866667             5.176844             0.164501             11.743296           \n",
            "2.000000             5.227232             0.164644             11.743296           \n",
            "0.133333             11.530903            0.081928             18.789274           \n",
            "0.266667             10.983094            0.081041             18.789274           \n",
            "0.400000             10.512403            0.080294             18.789274           \n",
            "0.533333             9.984805             0.079473             18.789274           \n",
            "0.666667             9.573163             0.078845             18.789274           \n",
            "0.800000             9.178810             0.078253             18.789274           \n",
            "0.933333             8.935719             0.077893             18.789274           \n",
            "1.066667             8.610147             0.077416             18.789274           \n",
            "1.200000             8.353778             0.077045             18.789274           \n",
            "1.333333             8.173729             0.076787             18.789274           \n",
            "1.466667             8.091607             0.076670             18.789274           \n",
            "1.600000             7.706420             0.076126             18.789274           \n",
            "1.733333             7.709125             0.076129             18.789274           \n",
            "1.866667             7.610856             0.075992             18.789274           \n",
            "2.000000             7.552584             0.075911             18.789274           \n",
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
            print("%s\"%s\\n\"," % (" "*12, lines[i][:-1]))
        for i in range(len(lines)):
            self.assertEqual(spin1[i], lines[i])

        # Check spin :71@N.
        print("\nChecking the spin :71@N input file.")
        file = open("%s%sspin%s.in" % (ds.tmpdir, sep, '_71_N'))
        lines = file.readlines()
        file.close()
        for i in range(len(lines)):
            print("%s\"%s\\n\"," % (" "*12, lines[i][:-1]))
        for i in range(len(lines)):
            self.assertEqual(spin2[i], lines[i])


    def test_korzhnev_2005_15n_dq_data(self):
        """Optimisation of the Korzhnev et al., 2005 15N DQ CPMG data using the 'NS MMQ 2-site' model.

        This uses the data from Dmitry Korzhnev's paper at U{DOI: 10.1021/ja054550e<http://dx.doi.org/10.1021/ja054550e>}.  This is the 1H SQ, 15N SQ, ZQ, DQ, 1H MQ and 15N MQ data for residue Asp 9 of the Fyn SH3 domain mutant.

        Here only the 15N DQ data will be optimised.  The values found by cpmg_fit using just this data are:

            - r2 = {'500': 9.487269007171426, '600': 11.718267257562591, '800': 13.624551743116887},
            - pA = 0.965402506690231,
            - dw = 0.805197170133360,
            - dwH = -0.595536627771890,
            - kex = 569.003663067619868,
            - chi2 = 9.297671357952812.
        """

        # Base data setup.
        self.setup_korzhnev_2005_data(data_list=['DQ'])

        # Alias the spin.
        spin = return_spin(":9@N")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=600e6)
        r20_key3 = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=800e6)

        # Set the initial parameter values.
        spin.r2 = {r20_key1: 9.48527908326952, r20_key2: 11.7135951595536, r20_key3: 13.6153887849344}
        spin.pA = 0.965638501551899
        spin.dw = 2.8537583461577
        spin.dwH = -0.387633062766635
        spin.kex = 573.704033851592

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', func_tol=1e-05, max_iter=1000)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise(min_algor='simplex', max_iter=10)
        self.interpreter.monte_carlo.error_analysis()

        # Plot the dispersion curves.
        self.interpreter.relax_disp.plot_disp_curves(dir=ds.tmpdir, force=True)

        # Save the results.
        self.interpreter.state.save('state', dir=ds.tmpdir, compress_type=1, force=True)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:9)"))
        print("%-20s %20.15g" % ("R2 (500 MHz)", spin.r2[r20_key1]))
        print("%-20s %20.15g" % ("R2 (600 MHz)", spin.r2[r20_key2]))
        print("%-20s %20.15g" % ("R2 (800 MHz)", spin.r2[r20_key3]))
        print("%-20s %20.15g" % ("pA", spin.pA))
        print("%-20s %20.15g" % ("dw", spin.dw))
        print("%-20s %20.15g" % ("dwH", spin.dwH))
        print("%-20s %20.15g" % ("kex", spin.kex))
        print("%-20s %20.15g\n" % ("chi2", spin.chi2))

        # Checks for residue :9.
        self.assertAlmostEqual(spin.r2[r20_key1], 9.48527908326952, 2)
        self.assertAlmostEqual(spin.r2[r20_key2], 11.7135951595536, 3)
        self.assertAlmostEqual(spin.r2[r20_key3], 13.6153887849344, 2)
        self.assertAlmostEqual(spin.pA, 0.965638501551899, 4)
        self.assertAlmostEqual(spin.dw, 2.8537583461577, 2)
        self.assertAlmostEqual(spin.dwH, -0.387633062766635, 3)
        self.assertAlmostEqual(spin.kex/1000, 573.704033851592/1000, 3)
        self.assertAlmostEqual(spin.chi2, 9.29563496654824, 2)


    def test_korzhnev_2005_15n_mq_data(self):
        """Optimisation of the Korzhnev et al., 2005 15N MQ CPMG data using the 'NS MMQ 2-site' model.

        This uses the data from Dmitry Korzhnev's paper at U{DOI: 10.1021/ja054550e<http://dx.doi.org/10.1021/ja054550e>}.  This is the 1H SQ, 15N SQ, ZQ, DQ, 1H MQ and 15N MQ data for residue Asp 9 of the Fyn SH3 domain mutant.

        Here only the 15N MQ data will be optimised.  The values found by cpmg_fit using just this data are:

            - r2 = {'500': 5.993083514798655, '600': 6.622184438384841, '800': 8.640765919352019},
            - pA = 0.930027999814003,
            - dw = 4.338620619954370,
            - dwH = -0.274250775560818,
            - kex = 344.613362916544475,
            - chi2 = 10.367733168217050.
        """

        # Base data setup.
        self.setup_korzhnev_2005_data(data_list=['MQ'])

        # Alias the spin.
        spin = return_spin(":9@N")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=600e6)
        r20_key3 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=800e6)

        # Set the initial parameter values.
        spin.r2 = {r20_key1: 6.02016436619016, r20_key2: 6.65421500772308, r20_key3: 8.6729591487622}
        spin.pA = 0.930083249288083
        spin.dw = 4.33890689462363
        spin.dwH = -0.274316585638047
        spin.kex = 344.329651956132

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', func_tol=1e-05, max_iter=1000)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise(min_algor='simplex', max_iter=10)
        self.interpreter.monte_carlo.error_analysis()

        # Plot the dispersion curves.
        self.interpreter.relax_disp.plot_disp_curves(dir=ds.tmpdir, force=True)

        # Save the results.
        self.interpreter.state.save('state', dir=ds.tmpdir, compress_type=1, force=True)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:9)"))
        print("%-20s %20.15g" % ("R2 (500 MHz)", spin.r2[r20_key1]))
        print("%-20s %20.15g" % ("R2 (600 MHz)", spin.r2[r20_key2]))
        print("%-20s %20.15g" % ("R2 (800 MHz)", spin.r2[r20_key3]))
        print("%-20s %20.15g" % ("pA", spin.pA))
        print("%-20s %20.15g" % ("dw", spin.dw))
        print("%-20s %20.15g" % ("dwH", spin.dwH))
        print("%-20s %20.15g" % ("kex", spin.kex))
        print("%-20s %20.15g\n" % ("chi2", spin.chi2))

        # Checks for residue :9.
        self.assertAlmostEqual(spin.r2[r20_key1], 6.02016436619016, 1)
        self.assertAlmostEqual(spin.r2[r20_key2], 6.65421500772308, 1)
        self.assertAlmostEqual(spin.r2[r20_key3], 8.6729591487622, 1)
        self.assertAlmostEqual(spin.pA, 0.930083249288083, 3)
        self.assertAlmostEqual(spin.dw, 4.33890689462363, 2)
        self.assertAlmostEqual(spin.dwH, -0.274316585638047, 3)
        self.assertAlmostEqual(spin.kex/1000, 344.329651956132/1000, 3)
        self.assertAlmostEqual(spin.chi2, 10.3654315659173, 3)


    def test_korzhnev_2005_15n_sq_data(self):
        """Optimisation of the Korzhnev et al., 2005 15N SQ CPMG data using the 'NS MMQ 2-site' model.

        This uses the data from Dmitry Korzhnev's paper at U{DOI: 10.1021/ja054550e<http://dx.doi.org/10.1021/ja054550e>}.  This is the 1H SQ, 15N SQ, ZQ, DQ, 1H MQ and 15N MQ data for residue Asp 9 of the Fyn SH3 domain mutant.

        Here only the 15N SQ data will be optimised.  The values found by cpmg_fit using just this data are:

            - r2 = {'500': 8.335037972570017, '600': 8.761366016417508, '800': 10.225001019091822},
            - pA = 0.950003458294991,
            - dw = 4.358402855315123,
            - kex = 429.906473361926999,
            - chi2 = 17.393331915567252.
        """

        # Base data setup.
        self.setup_korzhnev_2005_data(data_list=['SQ'])

        # Alias the spin.
        spin = return_spin(":9@N")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=600e6)
        r20_key3 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # Set the initial parameter values.
        spin.r2 = {r20_key1: 8.334232330326190, r20_key2: 8.756773997879968, r20_key3: 10.219320492033058}
        spin.pA = 0.950310172115387
        spin.dw = 4.356737157889636
        spin.kex = 433.176323890829849

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', func_tol=1e-05, max_iter=1000)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise(min_algor='simplex', max_iter=10)
        self.interpreter.monte_carlo.error_analysis()

        # Plot the dispersion curves.
        self.interpreter.relax_disp.plot_disp_curves(dir=ds.tmpdir, force=True)

        # Save the results.
        self.interpreter.state.save('state', dir=ds.tmpdir, compress_type=1, force=True)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:9)"))
        print("%-20s %20.15g" % ("R2 (500 MHz)", spin.r2[r20_key1]))
        print("%-20s %20.15g" % ("R2 (600 MHz)", spin.r2[r20_key2]))
        print("%-20s %20.15g" % ("R2 (800 MHz)", spin.r2[r20_key3]))
        print("%-20s %20.15g" % ("pA", spin.pA))
        print("%-20s %20.15g" % ("dw", spin.dw))
        print("%-20s %20.15g" % ("kex", spin.kex))
        print("%-20s %20.15g\n" % ("chi2", spin.chi2))

        # Checks for residue :9.
        self.assertAlmostEqual(spin.r2[r20_key1], 8.334232330326190, 4)
        self.assertAlmostEqual(spin.r2[r20_key2], 8.756773997879968, 4)
        self.assertAlmostEqual(spin.r2[r20_key3], 10.219320492033058, 4)
        self.assertAlmostEqual(spin.pA, 0.950310172115387, 4)
        self.assertAlmostEqual(spin.dw, 4.356737157889636, 4)
        self.assertAlmostEqual(spin.kex/1000, 433.176323890829849/1000, 4)
        self.assertAlmostEqual(spin.chi2, 17.37460582872912, 1)


    def test_korzhnev_2005_15n_zq_data(self):
        """Optimisation of the Korzhnev et al., 2005 15N ZQ CPMG data using the 'NS MMQ 2-site' model.

        This uses the data from Dmitry Korzhnev's paper at U{DOI: 10.1021/ja054550e<http://dx.doi.org/10.1021/ja054550e>}.  This is the 1H SQ, 15N SQ, ZQ, DQ, 1H MQ and 15N MQ data for residue Asp 9 of the Fyn SH3 domain mutant.

        Here only the 15N ZQ data will be optimised.  The values found by cpmg_fit using just this data are:

            - r2 = {'500': 5.909812628572937, '600': 6.663690132557320, '800': 6.787171647689906},
            - pA = 0.942452612380140,
            - dw = 0.858972784230892,
            - dwH = 0.087155962730608,
            - kex = 373.219151384798920,
            - chi2 = 23.863208106025152.
        """

        # Base data setup.
        self.setup_korzhnev_2005_data(data_list=['ZQ'])

        # Alias the spin.
        spin = return_spin(":9@N")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=600e6)
        r20_key3 = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=800e6)

        # Set the initial parameter values.
        spin.r2 = {r20_key1: 5.91033272691614, r20_key2: 6.66368695342258, r20_key3: 6.78922219135537}
        spin.pA = 0.942457332074014
        spin.dw = 0.850592422908884
        spin.dwH = 0.0881272284455416
        spin.kex = 372.745483351305

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', func_tol=1e-05, max_iter=1000)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise(min_algor='simplex', max_iter=10)
        self.interpreter.monte_carlo.error_analysis()

        # Plot the dispersion curves.
        self.interpreter.relax_disp.plot_disp_curves(dir=ds.tmpdir, force=True)

        # Save the results.
        self.interpreter.state.save('state', dir=ds.tmpdir, compress_type=1, force=True)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:9)"))
        print("%-20s %20.15g" % ("R2 (500 MHz)", spin.r2[r20_key1]))
        print("%-20s %20.15g" % ("R2 (600 MHz)", spin.r2[r20_key2]))
        print("%-20s %20.15g" % ("R2 (800 MHz)", spin.r2[r20_key3]))
        print("%-20s %20.15g" % ("pA", spin.pA))
        print("%-20s %20.15g" % ("dw", spin.dw))
        print("%-20s %20.15g" % ("dwH", spin.dwH))
        print("%-20s %20.15g" % ("kex", spin.kex))
        print("%-20s %20.15g\n" % ("chi2", spin.chi2))

        # Checks for residue :9.
        self.assertAlmostEqual(spin.r2[r20_key1], 5.91033272691614, 2)
        self.assertAlmostEqual(spin.r2[r20_key2], 6.66368695342258, 2)
        self.assertAlmostEqual(spin.r2[r20_key3], 6.78922219135537, 2)
        self.assertAlmostEqual(spin.pA, 0.942457332074014, 4)
        self.assertAlmostEqual(spin.dw, 0.850592422908884, 1)
        self.assertAlmostEqual(spin.dwH, 0.0881272284455416, 3)
        self.assertAlmostEqual(spin.kex/1000, 372.745483351305/1000, 3)
        self.assertAlmostEqual(spin.chi2, 23.8464637019392, 1)


    def test_korzhnev_2005_1h_mq_data(self):
        """Optimisation of the Korzhnev et al., 2005 1H MQ CPMG data using the 'NS MMQ 2-site' model.

        This uses the data from Dmitry Korzhnev's paper at U{DOI: 10.1021/ja054550e<http://dx.doi.org/10.1021/ja054550e>}.  This is the 1H SQ, 15N SQ, ZQ, DQ, 1H MQ and 15N MQ data for residue Asp 9 of the Fyn SH3 domain mutant.

        Here only the 1H MQ data will be optimised.  The values found by cpmg_fit using just this data are:

            - r2 = {'500': -0.000016676911302, '600': 0.036594127620440, '800': 2.131014839635728},
            - pA = 0.936911090448340,
            - dw = 4.325314846914845,
            - dwH = -0.213870168665628,
            - kex = 487.361914835074117,
            - chi2 = 14.870371897291138.
        """

        # Base data setup.
        self.setup_korzhnev_2005_data(data_list=['1H MQ'])

        # Alias the spin.
        spin = return_spin(":9@N")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=600e6)
        r20_key3 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=800e6)

        # Set the initial parameter values.
        spin.r2 = {r20_key1: 0.000022585022901, r20_key2: 0.039223196112941, r20_key3: 2.136576686700357}
        spin.pA = 0.936884348941701
        spin.dw = 4.326454531583964
        spin.dwH = -0.214026093221782
        spin.kex = 487.043592705469223

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', func_tol=1e-05, max_iter=100)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise(min_algor='simplex', max_iter=10)
        self.interpreter.monte_carlo.error_analysis()

        # Plot the dispersion curves.
        self.interpreter.relax_disp.plot_disp_curves(dir=ds.tmpdir, force=True)

        # Save the results.
        self.interpreter.state.save('state', dir=ds.tmpdir, compress_type=1, force=True)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:9)"))
        print("%-20s %20.15g" % ("R2 (500 MHz)", spin.r2[r20_key1]))
        print("%-20s %20.15g" % ("R2 (600 MHz)", spin.r2[r20_key2]))
        print("%-20s %20.15g" % ("R2 (800 MHz)", spin.r2[r20_key3]))
        print("%-20s %20.15g" % ("pA", spin.pA))
        print("%-20s %20.15g" % ("dw", spin.dw))
        print("%-20s %20.15g" % ("dwH", spin.dwH))
        print("%-20s %20.15g" % ("kex", spin.kex))
        print("%-20s %20.15g\n" % ("chi2", spin.chi2))

        # Checks for residue :9.
        self.assertAlmostEqual(spin.r2[r20_key1], 0.000023714274046, 4)
        self.assertAlmostEqual(spin.r2[r20_key2], 0.039223196112941, 2)
        self.assertAlmostEqual(spin.r2[r20_key3], 2.13657668670036, 2)
        self.assertAlmostEqual(spin.pA, 0.936884348941701, 4)
        self.assertAlmostEqual(spin.dw, 4.32645453158396, 2)
        self.assertAlmostEqual(spin.dwH, -0.214026093221782, 2)
        self.assertAlmostEqual(spin.kex/1000, 487.043592705469/1000, 4)
        self.assertAlmostEqual(spin.chi2, 14.8642315375301, 2)


    def test_korzhnev_2005_1h_sq_data(self):
        """Optimisation of the Korzhnev et al., 2005 1H SQ CPMG data using the 'NS MMQ 2-site' model.

        This uses the data from Dmitry Korzhnev's paper at U{DOI: 10.1021/ja054550e<http://dx.doi.org/10.1021/ja054550e>}.  This is the 1H SQ, 15N SQ, ZQ, DQ, 1H MQ and 15N MQ data for residue Asp 9 of the Fyn SH3 domain mutant.

        Here only the 1H SQ data will be optimised.  The values found by cpmg_fit using just this data are:

            - r2 = {'500': 6.691697587650816, '600': 6.998915158708793, '800': 5.519267837559072},
            - pA = 0.946949480545876,
            - dwH = -0.265279672133308,
            - kex = 406.548178869750700,
            - chi2 = 50.400680290545026.
        """

        # Base data setup.
        self.setup_korzhnev_2005_data(data_list=['1H SQ'])

        # Alias the spin.
        spin = return_spin(":9@N")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=600e6)
        r20_key3 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=800e6)

        # Set the initial parameter values.
        spin.r2 = {r20_key1: 6.69107911078939, r20_key2: 6.99888898689085, r20_key3: 5.52012880268077}
        spin.pA = 0.946990967372467
        spin.dwH = -0.265308128403529
        spin.kex = 406.843250675648

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', func_tol=1e-05, max_iter=1000)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise(min_algor='simplex', max_iter=10)
        self.interpreter.monte_carlo.error_analysis()

        # Plot the dispersion curves.
        self.interpreter.relax_disp.plot_disp_curves(dir=ds.tmpdir, force=True)

        # Save the results.
        self.interpreter.state.save('state', dir=ds.tmpdir, compress_type=1, force=True)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:9)"))
        print("%-20s %20.15g" % ("R2 (500 MHz)", spin.r2[r20_key1]))
        print("%-20s %20.15g" % ("R2 (600 MHz)", spin.r2[r20_key2]))
        print("%-20s %20.15g" % ("R2 (800 MHz)", spin.r2[r20_key3]))
        print("%-20s %20.15g" % ("pA", spin.pA))
        print("%-20s %20.15g" % ("dwH", spin.dwH))
        print("%-20s %20.15g" % ("kex", spin.kex))
        print("%-20s %20.15g\n" % ("chi2", spin.chi2))

        # Checks for residue :9.
        self.assertAlmostEqual(spin.r2[r20_key1], 6.69107911078939, 2)
        self.assertAlmostEqual(spin.r2[r20_key2], 6.99888898689085, 2)
        self.assertAlmostEqual(spin.r2[r20_key3], 5.52012880268077, 2)
        self.assertAlmostEqual(spin.pA, 0.946990967372467, 4)
        self.assertAlmostEqual(spin.dwH, -0.265308128403529, 4)
        self.assertAlmostEqual(spin.kex/1000, 406.843250675648/1000, 2)
        self.assertAlmostEqual(spin.chi2, 50.3431330819767, 1)


    def test_korzhnev_2005_all_data(self):
        """Optimisation of all the Korzhnev et al., 2005 CPMG data using the 'NS MMQ 2-site' model.

        This uses the data from Dmitry Korzhnev's paper at U{DOI: 10.1021/ja054550e<http://dx.doi.org/10.1021/ja054550e>}.  This is the 1H SQ, 15N SQ, ZQ, DQ, 1H MQ and 15N MQ data for residue Asp 9 of the Fyn SH3 domain mutant.

        Here all data will be optimised.  The values found by cpmg_fit using just this data are:

            - r2 = {'H-S 500':  6.671649051677150, 'H-S 600':  6.988634195648529, 'H-S 800':  5.527971316790596,
                    'N-S 500':  8.394988400015988, 'N-S 600':  8.891359568401835, 'N-S 800': 10.405356669006709,
                    'NHZ 500':  5.936446687394352, 'NHZ 600':  6.717058062814535, 'NHZ 800':  6.838733853403030,
                    'NHD 500':  8.593136215779710, 'NHD 600': 10.651511259239674, 'NHD 800': 12.567902357560627,
                    'HNM 500':  7.851325614877817, 'HNM 600':  8.408803624020202, 'HNM 800': 11.227489645758979,
                    'NHM 500':  9.189159145380575, 'NHM 600':  9.856814478405868, 'NHM 800': 11.967910041807118},
            - pA = 0.943125351763911,
            - dw = 4.421827493809807,
            - dwH = -0.272637034755752,
            - kex = 360.609744568697238,
            - chi2 = 162.589570340050813.
        """

        # Base data setup.
        self.setup_korzhnev_2005_data(data_list=['SQ', '1H SQ', 'DQ', 'ZQ', 'MQ', '1H MQ'])

        # Alias the spin.
        spin = return_spin(":9@N")

        # The R20 keys.
        r20_key1  = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=500e6)
        r20_key2  = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=600e6)
        r20_key3  = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=800e6)
        r20_key4  = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key5  = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=600e6)
        r20_key6  = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)
        r20_key7  = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=500e6)
        r20_key8  = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=600e6)
        r20_key9  = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=800e6)
        r20_key10 = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=500e6)
        r20_key11 = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=600e6)
        r20_key12 = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=800e6)
        r20_key13 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=500e6)
        r20_key14 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=600e6)
        r20_key15 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=800e6)
        r20_key16 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=500e6)
        r20_key17 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=600e6)
        r20_key18 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=800e6)

        # Set the initial parameter values.
        spin.r2 = {
            r20_key1:   6.67288025927458, r20_key2:   6.98951408255098, r20_key3:   5.52959273852704,
            r20_key4:   8.39471048876782, r20_key5:   8.89290699178799, r20_key6:  10.40770687236930,
            r20_key7:   5.93611174376373, r20_key8:   6.71735669582514, r20_key9:   6.83835225518265,
            r20_key10:  8.59615074668922, r20_key11: 10.65121378892910, r20_key12: 12.57108229191090,
            r20_key13:  7.85956711501608, r20_key14:  8.41891642907918, r20_key15: 11.23620892230380,
            r20_key16:  9.19654863789350, r20_key17:  9.86031627358462, r20_key18: 11.97523755925750
        }
        spin.pA = 0.943129019477673
        spin.dw = 4.42209952545181
        spin.dwH = -0.27258970590969
        spin.kex = 360.516132791038

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', func_tol=1e-05, max_iter=10)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise(min_algor='simplex', max_iter=10)
        self.interpreter.monte_carlo.error_analysis()

        # Plot the dispersion curves.
        self.interpreter.relax_disp.plot_disp_curves(dir=ds.tmpdir, force=True)

        # Save the results.
        self.interpreter.state.save('state', dir=ds.tmpdir, compress_type=1, force=True)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:9)"))
        print("%-20s %20.15g" % ("R2 (1H SQ - 500 MHz)", spin.r2[r20_key1]))
        print("%-20s %20.15g" % ("R2 (1H SQ - 600 MHz)", spin.r2[r20_key2]))
        print("%-20s %20.15g" % ("R2 (1H SQ - 800 MHz)", spin.r2[r20_key3]))
        print("%-20s %20.15g" % ("R2 (SQ - 500 MHz)", spin.r2[r20_key4]))
        print("%-20s %20.15g" % ("R2 (SQ - 600 MHz)", spin.r2[r20_key5]))
        print("%-20s %20.15g" % ("R2 (SQ - 800 MHz)", spin.r2[r20_key6]))
        print("%-20s %20.15g" % ("R2 (ZQ - 500 MHz)", spin.r2[r20_key7]))
        print("%-20s %20.15g" % ("R2 (ZQ - 600 MHz)", spin.r2[r20_key8]))
        print("%-20s %20.15g" % ("R2 (ZQ - 800 MHz)", spin.r2[r20_key9]))
        print("%-20s %20.15g" % ("R2 (DQ - 500 MHz)", spin.r2[r20_key10]))
        print("%-20s %20.15g" % ("R2 (DQ - 600 MHz)", spin.r2[r20_key11]))
        print("%-20s %20.15g" % ("R2 (DQ - 800 MHz)", spin.r2[r20_key12]))
        print("%-20s %20.15g" % ("R2 (1H MQ - 500 MHz)", spin.r2[r20_key13]))
        print("%-20s %20.15g" % ("R2 (1H MQ - 600 MHz)", spin.r2[r20_key14]))
        print("%-20s %20.15g" % ("R2 (1H MQ - 800 MHz)", spin.r2[r20_key15]))
        print("%-20s %20.15g" % ("R2 (MQ - 500 MHz)", spin.r2[r20_key16]))
        print("%-20s %20.15g" % ("R2 (MQ - 600 MHz)", spin.r2[r20_key17]))
        print("%-20s %20.15g" % ("R2 (MQ - 800 MHz)", spin.r2[r20_key18]))
        print("%-20s %20.15g" % ("pA", spin.pA))
        print("%-20s %20.15g" % ("dw", spin.dw))
        print("%-20s %20.15g" % ("dwH", spin.dwH))
        print("%-20s %20.15g" % ("kex", spin.kex))
        print("%-20s %20.15g\n" % ("chi2", spin.chi2))

        # Checks for residue :9.
        self.assertAlmostEqual(spin.r2[r20_key1],  6.67288025927458, 4)
        self.assertAlmostEqual(spin.r2[r20_key2],  6.98951408255098, 4)
        self.assertAlmostEqual(spin.r2[r20_key3],  5.52959273852704, 4)
        self.assertAlmostEqual(spin.r2[r20_key4],  8.39471048876782, 4)
        self.assertAlmostEqual(spin.r2[r20_key5],  8.89290699178799, 4)
        self.assertAlmostEqual(spin.r2[r20_key6],  10.4077068723693, 4)
        self.assertAlmostEqual(spin.r2[r20_key7],  5.93611174376373, 4)
        self.assertAlmostEqual(spin.r2[r20_key8],  6.71735669582514, 4)
        self.assertAlmostEqual(spin.r2[r20_key9],  6.83835225518265, 4)
        self.assertAlmostEqual(spin.r2[r20_key10], 8.59615074668922, 4)
        self.assertAlmostEqual(spin.r2[r20_key11], 10.6512137889291, 4)
        self.assertAlmostEqual(spin.r2[r20_key12], 12.5710822919109, 4)
        self.assertAlmostEqual(spin.r2[r20_key13], 7.85956711501608, 4)
        self.assertAlmostEqual(spin.r2[r20_key14], 8.41891642907918, 4)
        self.assertAlmostEqual(spin.r2[r20_key15], 11.2362089223038, 4)
        self.assertAlmostEqual(spin.r2[r20_key16], 9.1965486378935, 4)
        self.assertAlmostEqual(spin.r2[r20_key17], 9.86031627358462, 4)
        self.assertAlmostEqual(spin.r2[r20_key18], 11.9752375592575, 4)
        self.assertAlmostEqual(spin.pA, 0.943129019477673, 4)
        self.assertAlmostEqual(spin.dw, 4.42209952545181, 4)
        self.assertAlmostEqual(spin.dwH, -0.27258970590969, 4)
        self.assertAlmostEqual(spin.kex/1000, 360.516132791038/1000, 4)
        self.assertAlmostEqual(spin.chi2/1000, 162.511988511609/1000, 3)


    def test_kteilum_fmpoulsen_makke_cpmg_data_048m_guhcl_to_cr72(self):
        """Optimisation of Kaare Teilum, Flemming M Poulsen, Mikael Akke 2006 "acyl-CoA binding protein" CPMG data to the CR72 dispersion model.

        This uses the data from paper at U{http://dx.doi.org/10.1073/pnas.0509100103}.  This is CPMG data with a fixed relaxation time period.  Experiment in 0.48 M GuHCl (guanidine hydrochloride).
        """

        # Base data setup.
        self.setup_kteilum_fmpoulsen_makke_cpmg_data(model='CR72', expfolder="acbp_cpmg_disp_048MGuHCl_40C_041223")

        # Alias the spins.
        res61L = cdp.mol[0].res[0].spin[0]

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=599.89086220e6)

        # Set the initial parameter values.
        res61L.r2 = {r20_key1: 8.0}
        res61L.pA = 0.9
        res61L.dw = 6.0
        res61L.kex = 600.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:61)"))
        print("%-20s %20.15g" % ("R2 (600 MHz)", res61L.r2[r20_key1]))
        print("%-20s %20.15g" % ("pA", res61L.pA))
        print("%-20s %20.15g" % ("dw", res61L.dw))
        print("%-20s %20.15g" % ("kex", res61L.kex))
        print("%-20s %20.15g\n" % ("chi2", res61L.chi2))

        # Checks for residue :61. Calculated for 500 Monte Carlo simulations.
        self.assertAlmostEqual(res61L.r2[r20_key1], 8.69277980194016, 4)
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

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=599.89086220e6)

        # Set the initial parameter values.
        res61L.r2a = {r20_key1: 8.0}
        res61L.r2b = {r20_key1: 105.0}
        res61L.pA = 0.9
        res61L.dw = 6.0
        res61L.kex = 500.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:61)"))
        print("%-20s %20.15g" % ("R2A (600 MHz)", res61L.r2a[r20_key1]))
        print("%-20s %20.15g" % ("R2B (600 MHz)", res61L.r2b[r20_key1]))
        print("%-20s %20.15g" % ("pA", res61L.pA))
        print("%-20s %20.15g" % ("dw", res61L.dw))
        print("%-20s %20.15g" % ("kex", res61L.kex))
        print("%-20s %20.15g\n" % ("chi2", res61L.chi2))

        # Checks for residue :61. Calculated for 500 Monte Carlo simulations.
        self.assertAlmostEqual(res61L.r2a[r20_key1], 8.044428899438309, 0)
        self.assertAlmostEqual(res61L.r2b[r20_key1], 105.11894506392449, -2)
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

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=599.89086220e6)

        # Set the initial parameter values.
        res61L.r2a = {r20_key1: 8.0}
        res61L.dw = 6.5
        res61L.k_AB = 2.5

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:61)"))
        print("%-20s %20.15g" % ("R2A (600 MHz)", res61L.r2a[r20_key1]))
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

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=599.89086270e6)

        # Set the initial parameter values.
        res61L.r2a = {r20_key1: 8.0}
        res61L.dw = 6.5
        res61L.k_AB = 11.0

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s" % ("Parameter", "Value (:61)"))
        print("%-20s %20.15g" % ("R2A (600 MHz)", res61L.r2a[r20_key1]))
        print("%-20s %20.15g" % ("dw", res61L.dw))
        print("%-20s %20.15g" % ("k_AB", res61L.k_AB))
        print("%-20s %20.15g\n" % ("chi2", res61L.chi2))

        # Checks for residue :61. Reference values from paper

        self.assertAlmostEqual(res61L.r2a[r20_key1], 8.4, 0)
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
        keys = ['r1rho_800.00000000_0.000_1000.000', 'r1rho_800.00000000_0.000_1500.000', 'r1rho_800.00000000_0.000_2000.000', 'r1rho_800.00000000_0.000_2500.000', 'r1rho_800.00000000_0.000_3000.000', 'r1rho_800.00000000_0.000_3500.000', 'r1rho_800.00000000_0.000_4000.000', 'r1rho_800.00000000_0.000_4500.000', 'r1rho_800.00000000_0.000_5000.000', 'r1rho_800.00000000_0.000_5500.000', 'r1rho_800.00000000_0.000_6000.000']
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

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=800e6)

        # Switch to the 'M61' model data pipe, then check for each spin.
        self.interpreter.pipe.switch('M61')
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[r20_key1]/10, r1rho_prime[spin_index]/10, 2)
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
        keys = ['r1rho_800.00000000_0.000_1000.000', 'r1rho_800.00000000_0.000_1500.000', 'r1rho_800.00000000_0.000_2000.000', 'r1rho_800.00000000_0.000_2500.000', 'r1rho_800.00000000_0.000_3000.000', 'r1rho_800.00000000_0.000_3500.000', 'r1rho_800.00000000_0.000_4000.000', 'r1rho_800.00000000_0.000_4500.000', 'r1rho_800.00000000_0.000_5000.000', 'r1rho_800.00000000_0.000_5500.000', 'r1rho_800.00000000_0.000_6000.000']
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

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=800e6)

        # Switch to the 'M61' model data pipe, then check for each spin.
        self.interpreter.pipe.switch('M61')
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[r20_key1]/10, r1rho_prime[spin_index]/10, 2)
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

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=800e6)

        # Switch to the 'M61 skew' model data pipe, then check for each spin.
        self.interpreter.pipe.switch(MODEL_M61B)
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[r20_key1]/10, r1rho_prime[spin_index]/10, 2)
            self.assertAlmostEqual(spin.pA, pA, 2)
            self.assertAlmostEqual(spin.dw, dw[spin_index], 2)
            self.assertAlmostEqual(spin.kex/1000.0, kex/1000.0, 2)

            # Increment the spin index.
            spin_index += 1


    def test_ns_mmq_3site(self):
        """Compare the 'NS MMQ 3-site' dispersion model to synthetic data from cpmg_fit."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'ns_mmq_3site.py')

        # Check the chi-squared value.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[1].chi2, 0.0, 3)


    def test_ns_mmq_3site_linear(self):
        """Compare the 'NS MMQ 3-site linear' dispersion model to synthetic data from cpmg_fit."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'ns_mmq_3site_linear.py')

        # Check the chi-squared value.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[1].chi2, 0.0, 3)


    def test_ns_r1rho_3site(self):
        """Compare the 'NS R1rho 3-site' dispersion model to synthetic data from cpmg_fit."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'ns_r1rho_3site.py')

        # Check the chi-squared value.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].chi2, 136.13141468674999, 3)


    def test_ns_r1rho_3site_linear(self):
        """Compare the 'NS R1rho 3-site linear' dispersion model to synthetic data from cpmg_fit."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'ns_r1rho_3site_linear.py')

        # Check the chi-squared value.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].chi2, 0.030959849811015544, 3)


    def test_r1rho_kjaergaard(self):
        """Optimisation of the Kjaergaard et al., 2013 Off-resonance R1rho relaxation dispersion experiments using the 'DPL' model.

        This uses the data from Kjaergaard's paper at U{DOI: 10.1021/bi4001062<http://dx.doi.org/10.1021/bi4001062>}.

        """

        # The path to the data files.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013'

        # Set pipe name, bundle and type.
        pipe_name = 'base pipe'
        pipe_bundle = 'relax_disp'
        pipe_type= 'relax_disp'

        # Create the data pipe.
        self.interpreter.pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type=pipe_type)

        # Read the spins.
        self.interpreter.spectrum.read_spins(file='1_0_46_0_max_standard.ser', dir=data_path+sep+'peak_lists')

        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, None)
        self.assertEqual(len(cdp.mol[0].res), 48)

        # Name the isotope for field strength scaling.
        self.interpreter.spin.isotope(isotope='15N')

        # Set number of experiments to be used.
        NR_exp = -1

        # Load the experiments settings file.
        expfile = open(data_path+sep+'exp_parameters_sort.txt','r')
        expfileslines = expfile.readlines()[:NR_exp]
        expfile.close()

        # In MHz
        yOBS = 81.050
        # In ppm
        yCAR = 118.078
        centerPPM_N15 = yCAR

        ## Read the chemical shift data.
        self.interpreter.chemical_shift.read(file='1_0_46_0_max_standard.ser', dir=data_path+sep+'peak_lists')

        # Test the chemical shift data.
        cs = [122.223, 122.162, 114.250, 125.852, 118.626, 117.449, 119.999, 122.610, 118.602, 118.291, 115.393, 
        121.288, 117.448, 116.378, 116.316, 117.263, 122.211, 118.748, 118.103, 119.421, 119.317, 119.386, 117.279, 
        122.103, 120.038, 116.698, 111.811, 118.639, 118.285, 121.318, 117.770, 119.948, 119.759, 118.314, 118.160, 
        121.442, 118.714, 113.080, 125.706, 119.183, 120.966, 122.361, 126.675, 117.069, 120.875, 109.372, 119.811, 126.048]

        i = 0
        for spin, spin_id in spin_loop(return_id=True):
            print spin.name, spin.num, spin_id, spin.chemical_shift, cs[i]
            # Check the chemical shift.
            self.assertEqual(spin.chemical_shift, cs[i])

            # Increment the index.
            i += 1

        # The lock power to field, has been found in an calibration experiment.
        spin_lock_field_strengths_Hz = {'35': 431.0, '39': 651.2, '41': 800.5, '43': 984.0, '46': 1341.11, '48': 1648.5}

        # Apply spectra settings.
        for i in range(len(expfileslines)):
            line=expfileslines[i]
            if line[0] == "#":
                continue
            else:
                # DIRN I deltadof2 dpwr2slock ncyc trim ss sfrq
                DIRN = line.split()[0]
                I = int(line.split()[1])
                deltadof2 = line.split()[2]
                dpwr2slock = line.split()[3]
                ncyc = int(line.split()[4])
                trim = float(line.split()[5])
                ss = int(line.split()[6])
                set_sfrq = float(line.split()[7])
                apod_rmsd = float(line.split()[8])
                spin_lock_field_strength = spin_lock_field_strengths_Hz[dpwr2slock]

                # Calculate spin_lock time
                time_sl = 2*ncyc*trim

                # Define file name for peak list.
                FNAME = "%s_%s_%s_%s_max_standard.ser"%(I, deltadof2, dpwr2slock, ncyc)
                sp_id = "%s_%s_%s_%s"%(I, deltadof2, dpwr2slock, ncyc)

                # Load the peak intensities.
                self.interpreter.spectrum.read_intensities(file=FNAME, dir=data_path+sep+'peak_lists', spectrum_id=sp_id, int_method='height')

                # Set the peak intensity errors, as defined as the baseplane RMSD.
                self.interpreter.spectrum.baseplane_rmsd(error=apod_rmsd, spectrum_id=sp_id)

                # Set the relaxation dispersion experiment type.
                self.interpreter.relax_disp.exp_type(spectrum_id=sp_id, exp_type='R1rho')

                # Set The spin-lock field strength, nu1, in Hz
                self.interpreter.relax_disp.spin_lock_field(spectrum_id=sp_id, field=spin_lock_field_strength)

                # Calculating the spin-lock offset in ppm, from offsets values provided in Hz.
                frq_N15_Hz = yOBS * 1E6
                offset_ppm_N15 = float(deltadof2) / frq_N15_Hz * 1E6
                omega_rf_ppm = centerPPM_N15 + offset_ppm_N15

                # Set The spin-lock offset, omega_rf, in ppm.
                self.interpreter.relax_disp.spin_lock_offset(spectrum_id=sp_id, offset=omega_rf_ppm)

                # Set the relaxation times (in s).
                self.interpreter.relax_disp.relax_time(spectrum_id=sp_id, time=time_sl)

                # Set the spectrometer frequency.
                self.interpreter.spectrometer.frequency(id=sp_id, frq=set_sfrq, units='MHz')

        # The dispersion models.
        MODELS = ['R2eff', 'No Rex', 'DPL94']

        # The grid search size (the number of increments per dimension).
        GRID_INC = 4

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        MC_NUM = 3

        # Model selection technique.
        MODSEL = 'AIC'

        # Run the analysis.
        #relax_disp.Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=ds.tmpdir, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL)


    def test_r2eff_read(self):
        """Test the operation of the relax_disp.r2eff_read user function."""

        # The path to the data files.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'+sep+'800_MHz'

        # Read the sequence data.
        self.interpreter.sequence.read(file='66.667.in', dir=data_path, res_num_col=1)

        # The ID.
        id = 'test'

        # Set up the metadata.
        self.interpreter.spectrometer.frequency(id=id, frq=800e6)
        self.interpreter.relax_disp.exp_type(spectrum_id=id, exp_type='SQ CPMG')

        # Try reading the file.
        self.interpreter.relax_disp.r2eff_read(id=id, file='66.667.in', dir=data_path, disp_frq=66.667, res_num_col=1, data_col=2, error_col=3)

        # Check the global data.
        data = [
            ['cpmg_frqs', {'test': 66.667}],
            ['cpmg_frqs_list', [66.667]],
            ['dispersion_points', 1],
            ['exp_type', {'test': 'SQ CPMG'}],
            ['exp_type_list', ['SQ CPMG']],
            ['spectrometer_frq', {'test': 800000000.0}],
            ['spectrometer_frq_count', 1],
            ['spectrometer_frq_list', [800000000.0]],
            ['spectrum_ids', ['test']]
        ]
        for name, value in data:
            # Does it exist?
            self.assert_(hasattr(cdp, name))

            # Check the object.
            obj = getattr(cdp, name)
            self.assertEqual(obj, value)

        # Check the spin data.
        data = [
            [1,       2.3035747e+04, 8.5467725e+01],
            [2,       9.9629762e+04, 2.8322033e+02],
            [3,       9.5663137e+04, 2.8632929e+02],
            [4,       1.7089893e+05, 3.1089428e+02],
            [5,       4.7323876e+04, 1.0084269e+02],
            [6,       2.0199122e+04, 1.0135220e+02],
            [7,       1.6655488e+05, 3.1609061e+02],
            [8,       9.0061074e+04, 1.9176585e+02],
            [10,      8.4726204e+04, 2.8898155e+02],
            [11,      1.5050233e+05, 4.3138029e+02],
            [12,      9.2998531e+04, 3.0440191e+02],
            [13,      1.6343507e+05, 3.3144097e+02],
            [14,      1.0137301e+05, 3.7314642e+02],
            [15,      8.3407837e+04, 1.6546473e+02],
            [16,      1.3819126e+05, 3.3388517e+02],
            [17,      1.1010490e+05, 3.5639222e+02],
            [18,      9.4324035e+04, 3.2343585e+02],
            [19,      1.1135179e+05, 3.0706671e+02],
            [20,      7.6339410e+04, 1.7377460e+02],
            [21,      6.2008453e+04, 1.7327150e+02],
            [22,      1.0590404e+05, 2.4814635e+02],
            [23,      1.0630198e+05, 2.3601100e+02],
            [24,      7.2996320e+04, 1.4952465e+02],
            [25,      9.5486742e+04, 2.7080766e+02],
            [26,      5.8067989e+04, 1.6820462e+02],
            [27,     -1.7168510e+04, 2.2519560e+02],
            [28,      1.6891473e+05, 2.3497525e+02],
            [29,      9.4038555e+04, 2.0357593e+02],
            [30,      2.1386951e+04, 2.2153532e+02],
            [31,      9.3982899e+04, 2.0937056e+02],
            [32,      8.6097484e+04, 2.3868467e+02],
            [33,      1.0194337e+05, 2.7370704e+02],
            [34,      8.5683111e+04, 2.0838076e+02],
            [35,      8.6985768e+04, 2.0889310e+02],
            [36,      8.6011237e+04, 1.7498390e+02],
            [37,      1.0984097e+05, 2.7622998e+02],
            [38,      8.7017879e+04, 2.6547994e+02],
            [39,      9.1682649e+04, 5.2777676e+02],
            [40,      7.6370440e+04, 1.9873214e+02],
            [41,      9.1393531e+04, 2.4483824e+02],
            [42,      1.1017111e+05, 2.8020699e+02],
            [43,      9.4552366e+04, 3.4394150e+02],
            [44,      1.2858281e+05, 6.8449252e+02],
            [45,      7.4583525e+04, 1.9544210e+02],
            [46,      9.2087490e+04, 2.0491066e+02],
            [47,      9.7507255e+04, 2.5162839e+02],
            [48,      1.0033842e+05, 2.7566430e+02],
            [49,      1.3048305e+05, 2.6797466e+02],
            [50,      1.0546796e+05, 1.9304384e+02],
            [51,      9.3099697e+04, 2.0773311e+02],
            [52,      4.6863758e+04, 1.3169068e+02],
            [53,      6.1055806e+04, 1.5448477e+02],
            [55,      6.8629994e+04, 1.6868673e+02],
            [56,      1.1005552e+05, 2.1940465e+02],
            [57,      1.0572760e+05, 1.9768486e+02],
            [58,      1.1176950e+05, 3.0009610e+02],
            [59,      9.8758603e+04, 3.3803895e+02],
            [60,      9.9517201e+04, 3.5137994e+02],
            [61,      5.4357946e+04, 2.5896579e+02],
            [62,      1.0899978e+05, 2.8720371e+02],
            [63,      8.4549759e+04, 4.1401837e+02],
            [64,      5.5014550e+04, 2.1135781e+02],
            [65,      8.0569666e+04, 2.3249709e+02],
            [66,      1.2936610e+05, 3.5218725e+02],
            [67,      3.6438010e+04, 8.7924003e+01],
            [70,      3.8763157e+04, 1.3325040e+02],
            [71,      8.5711411e+04, 2.9316183e+02],
            [72,      3.3211541e+04, 1.2182123e+02],
            [73,      3.2070576e+04, 1.2305430e+02]
        ]
        for res_num, value, error in data:
            # Get the spin.
            spin = return_spin(spin_id=":%s"%res_num)

            # Check the values.
            self.assertEqual(spin.r2eff['sq_cpmg_800.00000000_0.000_66.667'], value)
            self.assertEqual(spin.r2eff_err['sq_cpmg_800.00000000_0.000_66.667'], error)


    def test_r2eff_read_spin(self):
        """Test the operation of the relax_disp.r2eff_read_spin user function."""

        # The path to the data files.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Korzhnev_et_al_2005'

        # Generate the sequence.
        self.interpreter.spin.create(res_name='Asp', res_num=9, spin_name='H')
        self.interpreter.spin.create(res_name='Asp', res_num=9, spin_name='N')
        self.interpreter.spin.isotope('1H', spin_id='@H')
        self.interpreter.spin.isotope('15N', spin_id='@N')

        # Build the experiment IDs.
        H_disp_points = [67.0, 133.0, 267.0, 400.0, 533.0, 667.0, 800.0, 933.0, 1067.0, 1600.0, 2133.0, 2667.0]
        N_disp_points = [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0]
        ids = []
        for value in H_disp_points:
            ids.append('1H_CPMG_%s' % value)
        for value in N_disp_points:
            ids.append('15N_CPMG_%s' % value)
        print("\n\nThe experiment IDs are %s." % ids)

        # Set up the metadata for the experiments.
        for id in ids:
            self.interpreter.spectrometer.frequency(id=id, frq=500e6)
            self.interpreter.relax_disp.exp_type(spectrum_id=id, exp_type='SQ CPMG')
        for value in H_disp_points:
            self.interpreter.relax_disp.cpmg_frq(spectrum_id='1H_CPMG_%s' % value, cpmg_frq=value)
        for value in N_disp_points:
            self.interpreter.relax_disp.cpmg_frq(spectrum_id='15N_CPMG_%s' % value, cpmg_frq=value)

        # Loop over the experiments.
        for id, file, spin_id in [['1H_CPMG', 'hs_500.res', ':9@H'], ['15N_CPMG', 'ns_500.res', ':9@N']]:
            # Try reading the file.
            self.interpreter.relax_disp.r2eff_read_spin(id=id, file=file, dir=data_path, spin_id=spin_id, disp_point_col=1, data_col=2, error_col=3)

        # Check the global data.
        data = [
            ['cpmg_frqs', {'1H_CPMG_667.0': 667.0, '1H_CPMG_1067.0': 1067.0, '15N_CPMG_350.0': 350.0, '1H_CPMG_933.0': 933.0, '15N_CPMG_50.0': 50.0, '15N_CPMG_100.0': 100.0, '1H_CPMG_400.0': 400.0, '1H_CPMG_533.0': 533.0, '1H_CPMG_800.0': 800.0, '15N_CPMG_900.0': 900.0, '15N_CPMG_150.0': 150.0, '15N_CPMG_800.0': 800.0, '1H_CPMG_267.0': 267.0, '1H_CPMG_2667.0': 2667.0, '15N_CPMG_300.0': 300.0, '1H_CPMG_133.0': 133.0, '15N_CPMG_700.0': 700.0, '1H_CPMG_67.0': 67.0, '15N_CPMG_400.0': 400.0, '15N_CPMG_250.0': 250.0, '1H_CPMG_2133.0': 2133.0, '1H_CPMG_1600.0': 1600.0, '15N_CPMG_200.0': 200.0, '15N_CPMG_1000.0': 1000.0, '15N_CPMG_500.0': 500.0, '15N_CPMG_600.0': 600.0}],
            ['cpmg_frqs_list', [50.0, 67.0, 100.0, 133.0, 150.0, 200.0, 250.0, 267.0, 300.0, 350.0, 400.0, 500.0, 533.0, 600.0, 667.0, 700.0, 800.0, 900.0, 933.0, 1000.0, 1067.0, 1600.0, 2133.0, 2667.0]],
            ['dispersion_points', 24],
            ['exp_type', {'1H_CPMG_667.0': 'SQ CPMG', '1H_CPMG_1067.0': 'SQ CPMG', '15N_CPMG_350.0': 'SQ CPMG', '1H_CPMG_933.0': 'SQ CPMG', '15N_CPMG_50.0': 'SQ CPMG', '15N_CPMG_100.0': 'SQ CPMG', '1H_CPMG_400.0': 'SQ CPMG', '1H_CPMG_533.0': 'SQ CPMG', '1H_CPMG_800.0': 'SQ CPMG', '15N_CPMG_900.0': 'SQ CPMG', '15N_CPMG_150.0': 'SQ CPMG', '15N_CPMG_800.0': 'SQ CPMG', '1H_CPMG_267.0': 'SQ CPMG', '1H_CPMG_2667.0': 'SQ CPMG', '15N_CPMG_300.0': 'SQ CPMG', '1H_CPMG_133.0': 'SQ CPMG', '15N_CPMG_700.0': 'SQ CPMG', '1H_CPMG_67.0': 'SQ CPMG', '15N_CPMG_400.0': 'SQ CPMG', '15N_CPMG_250.0': 'SQ CPMG', '1H_CPMG_2133.0': 'SQ CPMG', '1H_CPMG_1600.0': 'SQ CPMG', '15N_CPMG_200.0': 'SQ CPMG', '15N_CPMG_1000.0': 'SQ CPMG', '15N_CPMG_500.0': 'SQ CPMG', '15N_CPMG_600.0': 'SQ CPMG'}],
            ['exp_type_list', ['SQ CPMG']],
            ['spectrometer_frq', {'1H_CPMG_667.0': 500000000.0, '1H_CPMG_1067.0': 500000000.0, '15N_CPMG_350.0': 500000000.0, '1H_CPMG_933.0': 500000000.0, '15N_CPMG_50.0': 500000000.0, '15N_CPMG_100.0': 500000000.0, '1H_CPMG_400.0': 500000000.0, '1H_CPMG_533.0': 500000000.0, '1H_CPMG_800.0': 500000000.0, '15N_CPMG_900.0': 500000000.0, '15N_CPMG_150.0': 500000000.0, '15N_CPMG_800.0': 500000000.0, '1H_CPMG_267.0': 500000000.0, '1H_CPMG_2667.0': 500000000.0, '15N_CPMG_300.0': 500000000.0, '1H_CPMG_133.0': 500000000.0, '15N_CPMG_700.0': 500000000.0, '1H_CPMG_67.0': 500000000.0, '15N_CPMG_400.0': 500000000.0, '15N_CPMG_250.0': 500000000.0, '1H_CPMG_2133.0': 500000000.0, '1H_CPMG_1600.0': 500000000.0, '15N_CPMG_200.0': 500000000.0, '15N_CPMG_1000.0': 500000000.0, '15N_CPMG_500.0': 500000000.0, '15N_CPMG_600.0': 500000000.0}],
            ['spectrometer_frq_count', 1],
            ['spectrometer_frq_list', [500000000.0]],
            ['spectrum_ids', ['1H_CPMG_67.0', '1H_CPMG_133.0', '1H_CPMG_267.0', '1H_CPMG_400.0', '1H_CPMG_533.0', '1H_CPMG_667.0', '1H_CPMG_800.0', '1H_CPMG_933.0', '1H_CPMG_1067.0', '1H_CPMG_1600.0', '1H_CPMG_2133.0', '1H_CPMG_2667.0', '15N_CPMG_50.0', '15N_CPMG_100.0', '15N_CPMG_150.0', '15N_CPMG_200.0', '15N_CPMG_250.0', '15N_CPMG_300.0', '15N_CPMG_350.0', '15N_CPMG_400.0', '15N_CPMG_500.0', '15N_CPMG_600.0', '15N_CPMG_700.0', '15N_CPMG_800.0', '15N_CPMG_900.0', '15N_CPMG_1000.0']]
        ]
        for name, value in data:
            # Does it exist?
            self.assert_(hasattr(cdp, name))

            # Check the object.
            obj = getattr(cdp, name)
            if not isinstance(data, dict):
                self.assertEqual(obj, value)

            # Check the global dictionary data.
            else:
                for id in ids:
                    self.assertEqual(obj[id], value[id])

        # Check the spin data.
        h_data = [
            [  67.0,  21.47924,   0.42958],
            [ 133.0,  16.73898,   0.33478],
            [ 267.0,   9.97357,   0.19947],
            [ 400.0,   8.23877,   0.24737],
            [ 533.0,   7.59290,   0.24263],
            [ 667.0,   7.45843,   0.24165],
            [ 800.0,   7.11222,   0.23915],
            [ 933.0,   7.40880,   0.24129],
            [1067.0,   6.55191,   0.16629],
            [1600.0,   6.72177,   0.23637],
            [2133.0,   7.09629,   0.23904],
            [2667.0,   7.14675,   0.23940]
        ]
        for disp_point, value, error in h_data:
            id = 'sq_cpmg_500.00000000_0.000_%.3f' % disp_point
            self.assertEqual(cdp.mol[0].res[0].spin[0].r2eff[id], value)
            self.assertEqual(cdp.mol[0].res[0].spin[0].r2eff_err[id], error)
        n_data = [
            [  50.0,  27.15767,   0.54315],
            [ 100.0,  26.55781,   0.53116],
            [ 150.0,  24.73462,   0.49469],
            [ 200.0,  20.98617,   0.41972],
            [ 250.0,  17.82442,   0.35649],
            [ 300.0,  15.55352,   0.31107],
            [ 350.0,  13.78958,   0.27579],
            [ 400.0,  12.48334,   0.24967],
            [ 500.0,  11.55724,   0.23114],
            [ 600.0,  10.53874,   0.21077],
            [ 700.0,  10.07395,   0.20148],
            [ 800.0,   9.62952,   0.19259],
            [ 900.0,   9.49994,   0.19000],
            [1000.0,   8.71350,   0.17427]
        ]
        for disp_point, value, error in n_data:
            id = 'sq_cpmg_500.00000000_0.000_%.3f' % disp_point
            self.assertEqual(cdp.mol[0].res[0].spin[1].r2eff[id], value)
            self.assertEqual(cdp.mol[0].res[0].spin[1].r2eff_err[id], error)


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


    def test_sprangers_data_to_mmq_cr72(self, model=None):
        """Test the 'MMQ CR72' model fitting against Remco Sprangers' ClpP data.

        This uses the data from Remco Sprangers' paper at http://dx.doi.org/10.1073/pnas.0507370102.  This is MMQ CPMG data with a fixed relaxation time period.
        """

        # Reset.
        self.interpreter.reset()

        # Create the data pipe and load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Sprangers_ClpP'
        self.interpreter.state.load(data_path+sep+'r2eff_values')

        # The model data pipe.
        model = 'MMQ CR72'
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

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=600e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=800e6)

        # Set the cluster specific parameters (only for the first spin).
        spin135S.pA = 0.836591763632
        spin135S.kex = 241.806525261

        # Set the initial parameter values.
        spin135S.r2 = {r20_key1: 28.2493431552, r20_key2: 31.7517334715}
        spin135S.dw = 0.583003118785
        spin135S.dwH = 0.0361441944301

        spin135F.r2 = {r20_key1: 42.7201839991, r20_key2: 57.3178617389}
        spin135F.dw = 0.805849745104
        spin135F.dwH = 0.0215791945715

        spin137S.r2 = {r20_key1: 26.0134115256, r20_key2: 30.575806934}
        spin137S.dw = 0.688107568372
        spin137S.dwH = 0.0344463604043

        spin137F.r2 = {r20_key1: 46.6969397337, r20_key2: 58.602384101}
        spin137F.dw = 0.94978299907
        spin137F.dwH = 1.4818877939e-07

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', func_tol=1e-10, max_iter=1000)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s %-20s %-20s" % ("Parameter", "Value (:135@S)", "Value (:135@F)", "Value (:137@S)", "Value (:137@F)"))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("R2 (500 MHz)", spin135S.r2[r20_key1], spin135F.r2[r20_key1], spin137S.r2[r20_key1], spin137F.r2[r20_key1]))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("R2 (800 MHz)", spin135S.r2[r20_key2], spin135F.r2[r20_key2], spin137S.r2[r20_key2], spin137F.r2[r20_key2]))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("pA", spin135S.pA, spin135F.pA, spin137S.pA, spin137F.pA))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("dw", spin135S.dw, spin135F.dw, spin137S.dw, spin137F.dw))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("dwH", spin135S.dwH, spin135F.dwH, spin137S.dwH, spin137F.dwH))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("kex", spin135S.kex, spin135F.kex, spin137S.kex, spin137F.kex))
        print("%-20s %20.15g %20.15g %20.15g %20.15g\n" % ("chi2", spin135S.chi2, spin135F.chi2, spin137S.chi2, spin137F.chi2))
        print("\n        # Set the cluster specific parameters (only for the first spin).")
        print("        spin135S.pA = %s" % spin135S.pA)
        print("        spin135S.kex = %s" % spin135S.kex)
        print("\n        # Set the initial parameter values.")
        print("        spin135S.r2 = {r20_key1: %s, r20_key2: %s}" % (spin135S.r2[r20_key1], spin135S.r2[r20_key2]))
        print("        spin135S.dw = %s" % spin135S.dw)
        print("        spin135S.dwH = %s" % spin135S.dwH)
        print("\n        spin135F.r2 = {r20_key1: %s, r20_key2: %s}" % (spin135F.r2[r20_key1], spin135F.r2[r20_key2]))
        print("        spin135F.dw = %s" % spin135F.dw)
        print("        spin135F.dwH = %s" % spin135F.dwH)
        print("\n        spin137S.r2 = {r20_key1: %s, r20_key2: %s}" % (spin137S.r2[r20_key1], spin137S.r2[r20_key2]))
        print("        spin137S.dw = %s" % spin137S.dw)
        print("        spin137S.dwH = %s" % spin137S.dwH)
        print("\n        spin137F.r2 = {r20_key1: %s, r20_key2: %s}" % (spin137F.r2[r20_key1], spin137F.r2[r20_key2]))
        print("        spin137F.dw = %s" % spin137F.dw)
        print("        spin137F.dwH = %s" % spin137F.dwH)

        # Checks for residue :135S.
        self.assertAlmostEqual(spin135S.r2[r20_key1], 28.2499549832749, 4)
        self.assertAlmostEqual(spin135S.r2[r20_key2], 31.7529931145939, 4)
        self.assertAlmostEqual(spin135S.pA, 0.836602053942836, 4)
        self.assertAlmostEqual(spin135S.dw, 0.582996164517237, 4)
        self.assertAlmostEqual(spin135S.dwH, 0.0361431023785737, 4)
        self.assertAlmostEqual(spin135S.kex, 241.827943268269, 4)
        self.assertAlmostEqual(spin135S.chi2, 12.4224061774664, 4)

        # Checks for residue :135F.
        self.assertAlmostEqual(spin135F.r2[r20_key1], 42.7201353164699, 4)
        self.assertAlmostEqual(spin135F.r2[r20_key2], 57.3182694767754, 4)
        self.assertAlmostEqual(spin135F.pA, 0.836602053942836, 4)
        self.assertAlmostEqual(spin135F.dw, 0.805844579818815, 4)
        self.assertAlmostEqual(spin135F.dwH, 0.0215772589360951, 4)
        self.assertAlmostEqual(spin135F.kex, 241.827943268269, 4)
        self.assertAlmostEqual(spin135F.chi2, 12.4224061774664, 4)

        # Checks for residue :137S.
        self.assertAlmostEqual(spin137S.r2[r20_key1], 26.0130900829802, 4)
        self.assertAlmostEqual(spin137S.r2[r20_key2], 30.5756150883564, 4)
        self.assertAlmostEqual(spin137S.pA, 0.836602053942836, 4)
        self.assertAlmostEqual(spin137S.dw, 0.688110098029141, 4)
        self.assertAlmostEqual(spin137S.dwH, 0.0344479518787365, 4)
        self.assertAlmostEqual(spin137S.kex, 241.827943268269, 4)
        self.assertAlmostEqual(spin137S.chi2, 12.4224061774664, 4)

        # Checks for residue :137F.
        self.assertAlmostEqual(spin137F.r2[r20_key1], 46.6966999976701, 4)
        self.assertAlmostEqual(spin137F.r2[r20_key2], 58.6021572404496, 4)
        self.assertAlmostEqual(spin137F.pA, 0.836602053942836, 4)
        self.assertAlmostEqual(spin137F.dw, 0.949766944294449, 4)
        self.assertAlmostEqual(spin137F.dwH, 1.60128740101484e-07, 4)
        self.assertAlmostEqual(spin137F.kex, 241.827943268269, 4)
        self.assertAlmostEqual(spin137F.chi2, 12.4224061774664, 4)


    def test_sprangers_data_to_ns_mmq_2site(self, model=None):
        """Test the 'NS MMQ 2-site' model fitting against Remco Sprangers' ClpP data.

        This uses the data from Remco Sprangers' paper at http://dx.doi.org/10.1073/pnas.0507370102.  This is MQ CPMG data with a fixed relaxation time period.
        """

        # Reset.
        self.interpreter.reset()

        # Create the data pipe and load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Sprangers_ClpP'
        self.interpreter.state.load(data_path+sep+'r2eff_values')

        # The model data pipe.
        model = 'NS MMQ 2-site'
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

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=800e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=800e6)

        # Set the cluster specific parameters (only for the first spin).
        spin135S.pA = 0.847378444499757
        spin135S.kex = 264.055604934724329

        # Set the initial parameter values.
        spin135S.r2 = {r20_key1: 30.315119723745390, r20_key2: 37.411874745645299}
        spin135S.dw = 0.585574008745351
        spin135S.dwH = 0.000000000000002

        spin135F.r2 = {r20_key1: 41.440843383778287, r20_key2: 56.989726795397893}
        spin135F.dw = 0.856699277665748
        spin135F.dwH = 0.000000000582587

        spin137S.r2 = {r20_key1: 23.051695938570266, r20_key2: 28.352806483953824}
        spin137S.dw = 0.772904450844973
        spin137S.dwH = 0.183351478512970

        spin137F.r2 = {r20_key1: 44.702032074210429, r20_key2: 56.453146052685319}
        spin137F.dw = 0.984568590342831
        spin137F.dwH = 0.000000001993458

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-5, grad_tol=None, max_iter=100, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s %-20s %-20s" % ("Parameter", "Value (:135@S)", "Value (:135@F)", "Value (:137@S)", "Value (:137@F)"))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("R2 (500 MHz)", spin135S.r2[r20_key1], spin135F.r2[r20_key1], spin137S.r2[r20_key1], spin137F.r2[r20_key1]))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("R2 (800 MHz)", spin135S.r2[r20_key2], spin135F.r2[r20_key2], spin137S.r2[r20_key2], spin137F.r2[r20_key2]))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("pA", spin135S.pA, spin135F.pA, spin137S.pA, spin137F.pA))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("dw", spin135S.dw, spin135F.dw, spin137S.dw, spin137F.dw))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("dwH", spin135S.dwH, spin135F.dwH, spin137S.dwH, spin137F.dwH))
        print("%-20s %20.15g %20.15g %20.15g %20.15g" % ("kex", spin135S.kex, spin135F.kex, spin137S.kex, spin137F.kex))
        print("%-20s %20.15g %20.15g %20.15g %20.15g\n" % ("chi2", spin135S.chi2, spin135F.chi2, spin137S.chi2, spin137F.chi2))

        # FIXME: Remove this temporary return and properly check the results.
        return

        # Checks for residue :135S.
        self.assertAlmostEqual(spin135S.r2[r20_key1], 30.3151197237454, 4)
        self.assertAlmostEqual(spin135S.r2[r20_key2], 37.4118747456453, 4)
        self.assertAlmostEqual(spin135S.pA, 0.847378444499757, 4)
        self.assertAlmostEqual(spin135S.dw, 0.585574008745351, 4)
        self.assertAlmostEqual(spin135S.dwH, 2e-15, 4)
        self.assertAlmostEqual(spin135S.kex, 264.055604934724, 4)
        self.assertAlmostEqual(spin135S.chi2, 13.859423588071, 1)

        # Checks for residue :135F.
        self.assertAlmostEqual(spin135F.r2[r20_key1], 41.4408433837783, 4)
        self.assertAlmostEqual(spin135F.r2[r20_key2], 56.9897267953979, 4)
        self.assertAlmostEqual(spin135F.pA, 0.847378444499757, 4)
        self.assertAlmostEqual(spin135F.dw, 0.856699277665748, 4)
        self.assertAlmostEqual(spin135F.dwH, 5.82587e-10, 4)
        self.assertAlmostEqual(spin135F.kex, 264.055604934724, 4)
        self.assertAlmostEqual(spin135F.chi2, 13.859423588071, 1)

        # Checks for residue :137S.
        self.assertAlmostEqual(spin137S.r2[r20_key1], 23.0516959385703, 4)
        self.assertAlmostEqual(spin137S.r2[r20_key2], 28.3528064839538, 4)
        self.assertAlmostEqual(spin137S.pA, 0.847378444499757, 4)
        self.assertAlmostEqual(spin137S.dw, 0.772904450844973, 4)
        self.assertAlmostEqual(spin137S.dwH, 0.18335147851297, 4)
        self.assertAlmostEqual(spin137S.kex, 264.055604934724, 4)
        self.assertAlmostEqual(spin137S.chi2, 13.859423588071, 1)

        # Checks for residue :137F.
        self.assertAlmostEqual(spin137F.r2[r20_key1], 44.7020320742104, 4)
        self.assertAlmostEqual(spin137F.r2[r20_key2], 56.4531460526853, 4)
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

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=800e6)

        # Set the initial parameter values.
        spin1.r2 = {r20_key1: 9.9963793866185, r20_key2: 15.0056724422684}
        spin1.pA = 0.779782428085762
        spin1.dw = 7.57855284496424
        spin1.kex = 1116.7911285203
        spin2.r2 = {r20_key1: 11.9983346935434, r20_key2: 18.0076097513337}
        spin2.pA = 0.826666229688602
        spin2.dw = 9.5732624231366
        spin2.kex = 1380.46162655657

        # Low precision optimisation.
        self.interpreter.minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:1)", "Value (:2)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin1.r2[r20_key1], spin2.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin1.r2[r20_key2], spin2.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin1.pA, spin2.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin1.dw, spin2.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin1.kex, spin2.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin1.chi2, spin2.chi2))

        # Checks for residue :1.
        self.assertAlmostEqual(spin1.r2[r20_key1], 8.50207717367548, 4)
        self.assertAlmostEqual(spin1.r2[r20_key2], 13.4680429589972, 4)
        self.assertAlmostEqual(spin1.pA, 0.864523128842393, 4)
        self.assertAlmostEqual(spin1.dw, 8.85204828994151, 4)
        self.assertAlmostEqual(spin1.kex/1000, 1199.56359549637/1000, 4)
        self.assertAlmostEqual(spin1.chi2, 2.99182130153514, 4)

        # Checks for residue :2.
        self.assertAlmostEqual(spin2.r2[r20_key1], 10.1334196530849, 4)
        self.assertAlmostEqual(spin2.r2[r20_key2], 16.140167863407, 4)
        self.assertAlmostEqual(spin2.pA, 0.829988381197468, 4)
        self.assertAlmostEqual(spin2.dw, 9.5657894936005, 4)
        self.assertAlmostEqual(spin2.kex/1000, 1404.76852145933/1000, 4)
        self.assertAlmostEqual(spin2.chi2, 0.000150052743893402, 4)


    def test_tp02_data_to_mp05(self):
        """Test the dispersion 'MP05' model fitting against the 'TP02' test data."""

        # Fixed time variable and the models.
        ds.fixed = True
        ds.models = ['R2eff', 'MP05']

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'r1rho_off_res_tp02.py')

        # The original TP02 parameters.
        #r1rho_prime = [[10.0, 15.0], [12.0, 18.0]]
        #pA = 0.7654321
        #kex = 1234.56789
        #delta_omega = [7.0, 9.0]

        # The equivalent MP05 parameters.
        r1rho_prime = [[10.0058087306952, 15.0058071785643], [11.9997883441526, 17.9972824143268]]
        pA = [0.775054986621315, 0.806128964050712]
        kex = [1235.20228577117, 1220.23684410068]
        delta_omega = [7.08193971314044, 9.69856821121164]
        chi2 = [0.0370400968687155, 8.28321387676908e-06]

        # Alias the spins.
        spin1 = cdp.mol[0].res[0].spin[0]
        spin2 = cdp.mol[0].res[1].spin[0]

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=800e6)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:1)", "Value (:2)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin1.r2[r20_key1], spin2.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin1.r2[r20_key2], spin2.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin1.pA, spin2.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin1.dw, spin2.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin1.kex, spin2.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin1.chi2, spin2.chi2))

        # Switch to the 'MP05' model data pipe, then check for each spin.
        self.interpreter.pipe.switch('MP05')
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[r20_key1]/10, r1rho_prime[spin_index][0]/10, 4)
            self.assertAlmostEqual(spin.r2[r20_key2]/10, r1rho_prime[spin_index][1]/10, 4)
            self.assertAlmostEqual(spin.pA, pA[spin_index], 3)
            self.assertAlmostEqual(spin.dw, delta_omega[spin_index], 3)
            self.assertAlmostEqual(spin.kex/1000.0, kex[spin_index]/1000.0, 3)
            self.assertAlmostEqual(spin.chi2, chi2[spin_index], 3)

            # Increment the spin index.
            spin_index += 1


    def test_tp02_data_to_tap03(self):
        """Test the dispersion 'TAP03' model fitting against the 'TP02' test data."""

        # Fixed time variable and the models.
        ds.fixed = True
        ds.models = ['R2eff', 'TAP03']

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'r1rho_off_res_tp02.py')

        # The original TP02 parameters.
        #r1rho_prime = [[10.0, 15.0], [12.0, 18.0]]
        #pA = 0.7654321
        #kex = 1234.56789
        #delta_omega = [7.0, 9.0]

        # The equivalent TAP03 parameters.
        r1rho_prime = [[10.0058156951248, 15.0058184739705], [11.9997721585529, 17.9972521618894]]
        pA = [0.775042773953145, 0.80618481966515]
        kex = [1235.20914100608, 1220.44317542746]
        delta_omega = [7.08176850835834, 9.69883920692148]
        chi2 = [0.0371366837334911, 8.45422574594191e-06]

        # Alias the spins.
        spin1 = cdp.mol[0].res[0].spin[0]
        spin2 = cdp.mol[0].res[1].spin[0]

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=800e6)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:1)", "Value (:2)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin1.r2[r20_key1], spin2.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin1.r2[r20_key2], spin2.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin1.pA, spin2.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin1.dw, spin2.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin1.kex, spin2.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin1.chi2, spin2.chi2))

        # Switch to the 'MP05' model data pipe, then check for each spin.
        self.interpreter.pipe.switch('TAP03')
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[r20_key1]/10, r1rho_prime[spin_index][0]/10, 4)
            self.assertAlmostEqual(spin.r2[r20_key2]/10, r1rho_prime[spin_index][1]/10, 4)
            self.assertAlmostEqual(spin.pA, pA[spin_index], 3)
            self.assertAlmostEqual(spin.dw, delta_omega[spin_index], 3)
            self.assertAlmostEqual(spin.kex/1000.0, kex[spin_index]/1000.0, 3)
            self.assertAlmostEqual(spin.chi2, chi2[spin_index], 3)

            # Increment the spin index.
            spin_index += 1


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

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=800e6)

        # Switch to the 'TP02' model data pipe, then check for each spin.
        self.interpreter.pipe.switch('TP02')
        spin_index = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Printout.
            print("\nSpin %s." % spin_id)

            # Check the fitted parameters.
            self.assertAlmostEqual(spin.r2[r20_key1]/10, r1rho_prime[spin_index][0]/10, 4)
            self.assertAlmostEqual(spin.r2[r20_key2]/10, r1rho_prime[spin_index][1]/10, 4)
            self.assertAlmostEqual(spin.dw, delta_omega[spin_index], 3)
            self.assertAlmostEqual(spin.kex/1000.0, kex/1000.0, 3)

            # Increment the spin index.
            spin_index += 1
