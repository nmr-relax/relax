###############################################################################
#                                                                             #
# Copyright (C) 2006-2014 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2013-2014 Troels E. Linnet                                    #
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
from os import F_OK, access, getcwd, path, sep
from numpy import array, exp, median, log, save, sum, zeros
import re, math
from tempfile import mkdtemp

# relax module imports.
from auto_analyses import relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from lib.errors import RelaxError
from lib.io import get_file_path
from pipe_control.mol_res_spin import generate_spin_string, return_spin, spin_loop
from specific_analyses.relax_disp.checks import check_missing_r1
from specific_analyses.relax_disp.estimate_r2eff import estimate_r2eff
from specific_analyses.relax_disp.data import average_intensity, check_intensity_errors, generate_r20_key, get_curve_type, has_exponential_exp_type, has_r1rho_exp_type, loop_exp_frq, loop_exp_frq_offset_point, loop_exp_frq_offset_point_time, loop_time, return_grace_file_name_ini, return_param_key_from_data
from specific_analyses.relax_disp.data import INTERPOLATE_DISP, INTERPOLATE_OFFSET, X_AXIS_DISP, X_AXIS_W_EFF, X_AXIS_THETA, Y_AXIS_R2_R1RHO, Y_AXIS_R2_EFF
from specific_analyses.relax_disp.model import models_info, nesting_param
from specific_analyses.relax_disp.variables import EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_PROTON_MQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_ZQ, EXP_TYPE_LIST, EXP_TYPE_R1RHO, MODEL_B14_FULL, MODEL_CR72, MODEL_CR72_FULL, MODEL_DPL94, MODEL_IT99, MODEL_LIST_ANALYTIC_CPMG, MODEL_LIST_FULL, MODEL_LIST_NUMERIC_CPMG, MODEL_LM63, MODEL_M61, MODEL_M61B, MODEL_MP05, MODEL_NOREX, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR, MODEL_PARAMS, MODEL_R2EFF, MODEL_TP02, MODEL_TAP03
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
                "test_bug_21344_sparse_time_spinlock_acquired_r1rho_fail_relax_disp",
                "test_estimate_r2eff_err",
                "test_estimate_r2eff_err_methods"
                "test_exp_fit",
                "test_m61_exp_data_to_m61",
                "test_r1rho_kjaergaard_auto",
                "test_r1rho_kjaergaard_man",
                "test_r1rho_kjaergaard_missing_r1",
                "test_value_write_calc_rotating_frame_params_auto_analysis"
            ]

            # Store in the status object.
            if methodName in to_skip:
                status.skipped_tests.append([methodName, 'Relax curve-fitting C module', self._skip_type])

        # If not scipy.optimize.leastsq.
        if not dep_check.scipy_module:
            # The list of tests to skip.
            to_skip = [
                "test_estimate_r2eff_err_methods"
            ]

            # Store in the status object.
            if methodName in to_skip:
                status.skipped_tests.append([methodName, 'scipy.optimize.leastsq module', self._skip_type])


    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('relax_disp', 'relax_disp')

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()
        self.tmpdir = ds.tmpdir


    def setup_bug_22146_unpacking_r2a_r2b_cluster(self, folder=None, model_analyse=None, places = 7):
        """Setup data for the catch of U{bug #22146<https://gna.org/bugs/?22146>}, the failure of unpacking R2A and R2B, when performing a clustered full dispersion models.

        @keyword folder:            The name of the folder for the test data.
        @type folder:               str
        @keyword model_analyse:     The name of the model which will be tested.
        @type model_analyse:        str
        """

        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'

        # Data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_22146_unpacking_r2a_r2b_cluster'+sep+folder

        ## Experiments
        # Exp 1
        sfrq_1 = 500.0*1E6
        r20_key_1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_1)
        time_T2_1 = 0.05
        ncycs_1 = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 40, 50]
        # Here you define the direct R2eff errors (rad/s), as being added or subtracted for the created R2eff point in the corresponding ncyc cpmg frequence.
        #r2eff_errs_1 = [0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05]
        r2eff_errs_1 = [0.0] * len(ncycs_1)
        exp_1 = [sfrq_1, time_T2_1, ncycs_1, r2eff_errs_1]

        sfrq_2 = 600.0*1E6
        r20_key_2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_2)
        time_T2_2 = 0.06
        ncycs_2 = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 40, 60]
        # Here you define the direct R2eff errors (rad/s), as being added or subtracted for the created R2eff point in the corresponding ncyc cpmg frequence.
        #r2eff_errs_2 = [0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05]
        r2eff_errs_2 = [0.0] * len(ncycs_2)
        exp_2 = [sfrq_2, time_T2_2, ncycs_2, r2eff_errs_2]

        sfrq_3 = 700.0*1E6
        r20_key_3 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_3)
        time_T2_3 = 0.07
        ncycs_3 = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 50, 70]
        # Here you define the direct R2eff errors (rad/s), as being added or subtracted for the created R2eff point in the corresponding ncyc cpmg frequence.
        #r2eff_errs_2 = [0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05]
        r2eff_errs_3 = [0.0] * len(ncycs_3)
        exp_3 = [sfrq_3, time_T2_3, ncycs_3, r2eff_errs_3]

        # Collect all exps
        exps = [exp_1, exp_2, exp_3]

        R20 = [5.1, 5.2, 5.3, 10.1, 10.2, 10.3, 6.1, 6.2, 6.3, 11.1, 11.2, 11.3, 7.1, 7.2, 7.3, 12.1, 12.2, 12.3, 8.1, 8.2, 8.3, 13.1, 13.2, 13.3]
        dw_arr = [1.0, 2.0, 3.0, 4.0]
        pA_arr = [0.9]
        kex_arr = [1000.]

        spins = [
                ['Ala', 1, 'N', {'r2a': {r20_key_1: R20[0], r20_key_2: R20[1], r20_key_3: R20[2]}, 'r2b': {r20_key_1: R20[3], r20_key_2: R20[4], r20_key_3: R20[5]}, 'kex': kex_arr[0], 'pA': pA_arr[0], 'dw': dw_arr[0]}],
                ['Ala', 2, 'N', {'r2a': {r20_key_1: R20[6], r20_key_2: R20[7], r20_key_3: R20[8]}, 'r2b': {r20_key_1: R20[9], r20_key_2: R20[10], r20_key_3: R20[11]}, 'kex': kex_arr[0], 'pA': pA_arr[0], 'dw': dw_arr[1]}],
                ['Ala', 3, 'N', {'r2a': {r20_key_1: R20[12], r20_key_2: R20[13], r20_key_3: R20[14]}, 'r2b': {r20_key_1: R20[15], r20_key_2: R20[16], r20_key_3: R20[17]}, 'kex': kex_arr[0], 'pA': pA_arr[0], 'dw': dw_arr[2]}],
                ['Ala', 4, 'N', {'r2a': {r20_key_1: R20[18], r20_key_2: R20[19], r20_key_3: R20[20]}, 'r2b': {r20_key_1: R20[21], r20_key_2: R20[22], r20_key_3: R20[23]}, 'kex': kex_arr[0], 'pA': pA_arr[0], 'dw': dw_arr[3]}],
                ]

        # Create the data pipe.
        pipe_name = 'base pipe'
        pipe_type = 'relax_disp'
        pipe_bundle = 'relax_disp'
        self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type=pipe_type, bundle = pipe_bundle)

        # Generate the sequence.
        for res_name, res_num, spin_name, params in spins:
            self.interpreter.spin.create(res_name=res_name, res_num=res_num, spin_name=spin_name)

        # Set isotope
        self.interpreter.spin.isotope('15N', spin_id='@N')

        # Now loop over the experiments, to set the variables in relax.
        exp_ids = []
        for exp_i in exps:
            sfrq, time_T2, ncycs, r2eff_errs = exp_i
            exp_id = 'CPMG_%3.1f' % (sfrq/1E6)
            exp_ids.append(exp_id)

            ids = []
            for ncyc in ncycs:
                nu_cpmg = ncyc / time_T2
                cur_id = '%s_%.1f' % (exp_id, nu_cpmg)
                ids.append(cur_id)

                # Set the spectrometer frequency.
                self.interpreter.spectrometer.frequency(id=cur_id, frq=sfrq)

                # Set the experiment type.
                self.interpreter.relax_disp.exp_type(spectrum_id=cur_id, exp_type=EXP_TYPE_CPMG_SQ)

                # Set the relaxation dispersion CPMG constant time delay T (in s).
                self.interpreter.relax_disp.relax_time(spectrum_id=cur_id, time=time_T2)

                # Set the relaxation dispersion CPMG frequencies.
                self.interpreter.relax_disp.cpmg_setup(spectrum_id=cur_id, cpmg_frq=nu_cpmg)

        print("\n\nThe experiment IDs are %s." % cdp.spectrum_ids)

        ### Now do fitting.
        # Change pipe.

        pipe_name_MODEL = "%s_%s"%(pipe_name, model_analyse)
        self.interpreter.pipe.copy(pipe_from=pipe_name, pipe_to=pipe_name_MODEL, bundle_to = pipe_bundle)
        self.interpreter.pipe.switch(pipe_name=pipe_name_MODEL)

        # Now read data in.
        for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):
            exp_id = exp_ids[mi]
            exp_i = exps[mi]
            sfrq, time_T2, ncycs, r2eff_errs = exp_i

            # Then loop over the spins.
            for res_name, res_num, spin_name, params in spins:
                cur_spin_id = ":%i@%s"%(res_num, spin_name)

                # Define file name
                file_name = "%s%s.txt" % (exp_id, cur_spin_id .replace('#', '_').replace(':', '_').replace('@', '_'))

                # Read in the R2eff file to put into spin structure.
                self.interpreter.relax_disp.r2eff_read_spin(id=exp_id, spin_id=cur_spin_id, file=file_name, dir=data_path, disp_point_col=1, data_col=2, error_col=3)

        # Then select model.
        self.interpreter.relax_disp.select_model(model=model_analyse)

        # Then cluster
        self.interpreter.relax_disp.cluster('model_cluster', ":1-100")

        # Grid search
        low_arr = R20 + dw_arr + pA_arr + kex_arr
        self.interpreter.minimise.grid_search(lower=low_arr, upper=low_arr, inc=1, constraints=True, verbosity=1)

        # Then loop over the defined spins and read the parameters.
        for i in range(len(spins)):
            res_name, res_num, spin_name, params = spins[i]
            cur_spin_id = ":%i@%s"%(res_num, spin_name)
            cur_spin = return_spin(cur_spin_id)

            for mo_param in cur_spin.params:
                print(mo_param)
                # The R2 is a dictionary, depending on spectrometer frequency.
                if isinstance(getattr(cur_spin, mo_param), dict):
                    for key, val in getattr(cur_spin, mo_param).items():
                        should_be = params[mo_param][key]
                        print(cur_spin.model, res_name, cur_spin_id, mo_param, key, float(val), should_be)
                        self.assertAlmostEqual(val, should_be)
                else:
                    should_be = float(params[mo_param])
                    val = getattr(cur_spin, mo_param)
                    print(cur_spin.model, res_name, cur_spin_id, mo_param, val, should_be)
                    self.assertAlmostEqual(val, should_be)

            # Test chi2.
            # At this point the chi-squared value at the solution should be zero, as the relaxation data was created with the same parameter values.
            self.assertAlmostEqual(cur_spin.chi2, 0.0, places = places)


    def setup_r1rho_kjaergaard(self, cluster_ids=[], read_R1=True):
        """Set up the data for the test_r1rho_kjaergaard_*() system tests."""

        # The path to the data files.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013'

        # Set pipe name, bundle and type.
        ds.pipe_name = 'base pipe'
        ds.pipe_bundle = 'relax_disp'
        ds.pipe_type = 'relax_disp'

        # Create the data pipe.
        self.interpreter.pipe.create(pipe_name=ds.pipe_name, bundle=ds.pipe_bundle, pipe_type=ds.pipe_type)

        # Read the spins.
        self.interpreter.spectrum.read_spins(file='1_0_46_0_max_standard.ser', dir=data_path+sep+'peak_lists')

        # Name the isotope for field strength scaling.
        self.interpreter.spin.isotope(isotope='15N')

        # Set number of experiments to be used.
        NR_exp = 70

        # Load the experiments settings file.
        expfile = open(data_path+sep+'exp_parameters_sort.txt', 'r')
        expfileslines = expfile.readlines()[:NR_exp]
        expfile.close()

        # In MHz
        yOBS = 81.050
        # In ppm
        yCAR = 118.078
        centerPPM_N15 = yCAR

        ## Read the chemical shift data.
        self.interpreter.chemical_shift.read(file='1_0_46_0_max_standard.ser', dir=data_path+sep+'peak_lists')

        # The lock power to field, has been found in an calibration experiment.
        spin_lock_field_strengths_Hz = {'35': 431.0, '39': 651.2, '41': 800.5, '43': 984.0, '46': 1341.11, '48': 1648.5}

        # Apply spectra settings.
        # Count settings
        j = 0
        for i in range(len(expfileslines)):
            line = expfileslines[i]
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

                # Add to counter
                j += 1


        print("Testing the number of settings")
        print("Number of settings iterations is: %s. Number of cdp.exp_type.keys() is: %s"%(i, len(cdp.exp_type.keys() ) ) )
        self.assertEqual(70, len(expfileslines))
        self.assertEqual(69, j)
        self.assertEqual(69, len(cdp.exp_type.keys()) )

        # Cluster spins
        for curspin in cluster_ids:
            print("Adding spin %s to cluster"%curspin)
            self.interpreter.relax_disp.cluster('model_cluster', curspin)

        # De-select for analysis those spins who have not been clustered
        for free_spin in cdp.clustering['free spins']:
            print("Deselecting free spin %s"%free_spin)
            self.interpreter.deselect.spin(spin_id=free_spin, change_all=False)


        #Paper         reference values
        #              Resi   Resn         R1_rad_s   R1err_rad_s   R2_rad_s   R2err_rad_s   kEX_rad_s      kEXerr_rad_s  phi_rad2_s2     phierr_rad2_s2    phi_ppm2         phierr_ppm2
        # Scaling rad2_s2 to ppm2: scaling_rad2_s2 = frequency_to_ppm(frq=1/(2*pi), B0=cdp.spectrometer_frq_list[0], isotope='15N')**2 = 3.85167990165e-06
        ds.ref = dict()
        ds.ref[':13@N'] = [13,   'L13N-HN',   1.32394,   0.14687,      8.16007,   1.01237,      13193.82986,   2307.09152,   58703.06446,    22413.09854,      0.2261054135,    0.0863280812]
        ds.ref[':15@N'] = [15,   'R15N-HN',   1.34428,   0.14056,      7.83256,   0.67559,      13193.82986,   2307.09152,   28688.33492,    13480.72253,      0.110498283,     0.051923428]
        ds.ref[':16@N'] = [16,   'T16N-HN',   1.71514,   0.13651,      17.44216,  0.98583,      13193.82986,   2307.09152,   57356.77617,    21892.44205,      0.220919942,     0.084322679]
        ds.ref[':25@N'] = [25,   'Q25N-HN',   1.82412,   0.15809,      9.09447,   2.09215,      13193.82986,   2307.09152,   143111.13431,   49535.80302,      0.5512182797,    0.1907960569]
        ds.ref[':26@N'] = [26,   'Q26N-HN',   1.45746,   0.14127,      10.22801,  0.67116,      13193.82986,   2307.09152,   28187.06876,    13359.01615,      0.1085675662,    0.051454654]
        ds.ref[':28@N'] = [28,   'Q28N-HN',   1.48095,   0.14231,      10.33552,  0.691,        13193.82986,   2307.09152,   30088.0686,     13920.25654,      0.1158896091,    0.0536163723]
        ds.ref[':39@N'] = [39,   'L39N-HN',   1.46094,   0.14514,      8.02194,   0.84649,      13193.82986,   2307.09152,   44130.18538,    18104.55064,      0.1699753481,    0.0697329338]
        ds.ref[':40@N'] = [40,   'M40N-HN',   1.21381,   0.14035,      12.19112,  0.81418,      13193.82986,   2307.09152,   41834.90493,    17319.92156,      0.1611346625,    0.0667107938]
        ds.ref[':41@N'] = [41,   'A41N-HN',   1.29296,   0.14286,      9.29941,   0.66246,      13193.82986,   2307.09152,   26694.8921,     13080.66782,      0.1028201794,    0.0503825453]
        ds.ref[':43@N'] = [43,   'F43N-HN',   1.33626,   0.14352,      12.73816,  1.17386,      13193.82986,   2307.09152,   70347.63797,    26648.30524,      0.2709565833,    0.1026407417]
        ds.ref[':44@N'] = [44,   'I44N-HN',   1.28487,   0.1462,       12.70158,  1.52079,      13193.82986,   2307.09152,   95616.20461,    35307.79817,      0.3682830136,    0.1359943366]
        ds.ref[':45@N'] = [45,   'K45N-HN',   1.59227,   0.14591,      9.54457,   0.95596,      13193.82986,   2307.09152,   53849.7826,     21009.89973,      0.2074121253,    0.0809234085]
        ds.ref[':49@N'] = [49,   'A49N-HN',   1.38521,   0.14148,      4.44842,   0.88647,      13193.82986,   2307.09152,   40686.65286,    18501.20774,      0.1567119631,    0.07126073]
        ds.ref[':52@N'] = [52,   'V52N-HN',   1.57531,   0.15042,      6.51945,   1.43418,      13193.82986,   2307.09152,   93499.92172,    33233.23039,      0.3601317693,    0.1280037656]
        ds.ref[':53@N'] = [53,   'A53N-HN',   1.27214,   0.13823,      4.0705,    0.85485,      13193.82986,   2307.09152,   34856.18636,    17505.02393,      0.1342548725,    0.0674237488]

        ds.guess = dict()
        ds.guess[':13@N'] = [13,   'L13N-HN',   1.32394,   0.14687,      8.16007,   1.01237,      13193.82986,   2307.09152,   58703.06446,    22413.09854,      0.2261054135,    0.0863280812]
        ds.guess[':15@N'] = [15,   'R15N-HN',   1.34428,   0.14056,      7.83256,   0.67559,      13193.82986,   2307.09152,   28688.33492,    13480.72253,      0.110498283,     0.051923428]
        ds.guess[':16@N'] = [16,   'T16N-HN',   1.71514,   0.13651,      17.44216,  0.98583,      13193.82986,   2307.09152,   57356.77617,    21892.44205,      0.220919942,     0.084322679]
        ds.guess[':25@N'] = [25,   'Q25N-HN',   1.82412,   0.15809,      9.09447,   2.09215,      13193.82986,   2307.09152,   143111.13431,   49535.80302,      0.5512182797,    0.1907960569]
        ds.guess[':26@N'] = [26,   'Q26N-HN',   1.45746,   0.14127,      10.22801,  0.67116,      13193.82986,   2307.09152,   28187.06876,    13359.01615,      0.1085675662,    0.051454654]
        ds.guess[':28@N'] = [28,   'Q28N-HN',   1.48095,   0.14231,      10.33552,  0.691,        13193.82986,   2307.09152,   30088.0686,     13920.25654,      0.1158896091,    0.0536163723]
        ds.guess[':39@N'] = [39,   'L39N-HN',   1.46094,   0.14514,      8.02194,   0.84649,      13193.82986,   2307.09152,   44130.18538,    18104.55064,      0.1699753481,    0.0697329338]
        ds.guess[':40@N'] = [40,   'M40N-HN',   1.21381,   0.14035,      12.19112,  0.81418,      13193.82986,   2307.09152,   41834.90493,    17319.92156,      0.1611346625,    0.0667107938]
        ds.guess[':41@N'] = [41,   'A41N-HN',   1.29296,   0.14286,      9.29941,   0.66246,      13193.82986,   2307.09152,   26694.8921,     13080.66782,      0.1028201794,    0.0503825453]
        ds.guess[':43@N'] = [43,   'F43N-HN',   1.33626,   0.14352,      12.73816,  1.17386,      13193.82986,   2307.09152,   70347.63797,    26648.30524,      0.2709565833,    0.1026407417]
        ds.guess[':44@N'] = [44,   'I44N-HN',   1.28487,   0.1462,       12.70158,  1.52079,      13193.82986,   2307.09152,   95616.20461,    35307.79817,      0.3682830136,    0.1359943366]
        ds.guess[':45@N'] = [45,   'K45N-HN',   1.59227,   0.14591,      9.54457,   0.95596,      13193.82986,   2307.09152,   53849.7826,     21009.89973,      0.2074121253,    0.0809234085]
        ds.guess[':49@N'] = [49,   'A49N-HN',   1.38521,   0.14148,      4.44842,   0.88647,      13193.82986,   2307.09152,   40686.65286,    18501.20774,      0.1567119631,    0.07126073]
        ds.guess[':52@N'] = [52,   'V52N-HN',   1.57531,   0.15042,      6.51945,   1.43418,      13193.82986,   2307.09152,   93499.92172,    33233.23039,      0.3601317693,    0.1280037656]
        ds.guess[':53@N'] = [53,   'A53N-HN',   1.27214,   0.13823,      4.0705,    0.85485,      13193.82986,   2307.09152,   34856.18636,    17505.02393,      0.1342548725,    0.0674237488]

        # Assign guess values.
        for spin, spin_id in spin_loop(return_id=True):
            if spin_id in cluster_ids:
                print("spin_id %s in cluster ids"%(spin_id))
                spin.kex = ds.guess[spin_id][6]
                spin.phi_ex = ds.guess[spin_id][10]
            else:
                print("spin_id %s NOT in cluster ids"%(spin_id))

        if read_R1:
            # Read the R1 data
            self.interpreter.relax_data.read(ri_id='R1', ri_type='R1', frq=cdp.spectrometer_frq_list[0], file='R1_fitted_values.txt', dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)


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
        self.interpreter.pipe.create(pipe_name='R2eff - relax_disp', pipe_type='relax_disp')
        self.interpreter.pipe.switch(pipe_name='R2eff - relax_disp')
        self.interpreter.results.read(data_path+sep+'r2eff_pipe')
        self.interpreter.deselect.spin(':4')

        # The model data pipe.
        pipe_name = "%s - relax_disp" % model
        self.interpreter.pipe.copy(pipe_from='base pipe', pipe_to=pipe_name, bundle_to='relax_disp')
        self.interpreter.pipe.switch(pipe_name=pipe_name)

        # Set the model.
        self.interpreter.relax_disp.select_model(model=model)

        # Copy the data.
        self.interpreter.value.copy(pipe_from='R2eff - relax_disp', pipe_to=pipe_name, param='r2eff')


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
        pipe_name = "%s - relax_disp" % model
        self.interpreter.pipe.copy(pipe_from='base pipe', pipe_to=pipe_name, bundle_to='relax_disp')
        self.interpreter.pipe.switch(pipe_name=pipe_name)

        # Set the model.
        self.interpreter.relax_disp.select_model(model=model)

        # Copy the data.
        self.interpreter.value.copy(pipe_from='R2eff', pipe_to=pipe_name, param='r2eff')


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
                self.interpreter.relax_disp.cpmg_setup(spectrum_id=new_id, cpmg_frq=cpmg_frq)

            # Read the R2eff data.
            self.interpreter.relax_disp.r2eff_read_spin(id=id, file=file, dir=data_path, spin_id=spin_id, disp_point_col=1, data_col=2, error_col=3)

        # Change the model.
        self.interpreter.relax_disp.select_model('NS MMQ 2-site')


    def setup_sod1wt_t25(self, pipe_name, pipe_type, pipe_name_r2eff, select_spin_index):
        """Setup of data SOD1-WT CPMG. From paper at U{http://dx.doi.org/10.1073/pnas.0907387106}.

        Optimisation of Kaare Teilum, Melanie H. Smith, Eike Schulz, Lea C. Christensen, Gleb Solomentseva, Mikael Oliveberg, and Mikael Akkea 2009
        'SOD1-WT' CPMG data to the CR72 dispersion model.

        This uses the data from paper at U{http://dx.doi.org/10.1073/pnas.0907387106}.  This is CPMG data with a fixed relaxation time period recorded at fields of 500 and 600MHz.
        Data is for experiment at 25 degree Celcius.
        """

        # Create the data pipe and load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'sod1wt_t25'

        # Set experiment settings. sfrq, time_T2, ncyc
        Exps = [
        ["600MHz", "Z_A", 599.8908617*1E6, 0.06, [28, 0, 4, 32, 60, 2, 10, 16, 8, 20, 50, 18, 40, 6, 12, 0, 24], ["Z_A1", "Z_A15"] ],
        ["500MHz", "Z_B", 499.862139*1E6, 0.04, [20, 0, 16, 10, 36, 2, 12, 4, 22, 18, 40, 14, 26, 8, 32, 24, 6, 28, 0], ["Z_B1", "Z_B18"] ] ]

        # Create base pipe
        self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type=pipe_type)

        # Loop throug experiments
        id_lists = []
        for folder, key, sfrq, time_T2, ncycs, rep_ncyss in Exps:
            # Read spins
            self.interpreter.spectrum.read_spins(file="128_FT.ser", dir=data_path+sep+folder)
            self.interpreter.spectrum.read_spins(file="128_FT.ser", dir=data_path+sep+folder)

            # Make spectrum id list
            id_list = list(key+str(i) for i in range(len(ncycs)))
            id_lists.append(id_list)

            # Read intensities
            self.interpreter.spectrum.read_intensities(file="128_FT.ser", dir=data_path+sep+folder, int_method='height', spectrum_id=id_list, int_col=list(range(len(id_list))) )

            # Loop over experiments
            for i in range(len(ncycs)):
                ncyc = ncycs[i]
                vcpmg = ncyc/time_T2

                # Test if spectrum is a reference
                if float(vcpmg) == 0.0:
                    vcpmg = None
                else:
                    vcpmg = round(float(vcpmg), 3)

                # Set current id
                current_id = id_list[i]

                # Set the current experiment type.
                self.interpreter.relax_disp.exp_type(spectrum_id=current_id, exp_type='SQ CPMG')

                # Set the NMR field strength of the spectrum.
                self.interpreter.spectrometer.frequency(id=current_id, frq=sfrq, units='Hz')

                # Relaxation dispersion CPMG constant time delay T (in s).
                self.interpreter.relax_disp.relax_time(spectrum_id=current_id, time=time_T2)

                # Set the relaxation dispersion CPMG frequencies.
                self.interpreter.relax_disp.cpmg_setup(spectrum_id=current_id, cpmg_frq=vcpmg)

        # Define replicated
        self.interpreter.spectrum.replicated(spectrum_ids=Exps[0][5])
        self.interpreter.spectrum.replicated(spectrum_ids=Exps[1][5])

        # Perform error analysis
        self.interpreter.spectrum.error_analysis(subset=id_lists[0])
        self.interpreter.spectrum.error_analysis(subset=id_lists[1])

        # Define isotope
        self.interpreter.spin.isotope(isotope='15N')

        #############

        # Define the 64 residues which was used for Global fitting
        glob_assn = ["G10N-H", "D11N-H", "Q15N-H", "G16N-H", "G37N-H", "G41N-H", "L42N-H", "H43N-H", "H46N-H", "V47N-H", "E49N-H",
        "E50N-H", "E51N-H", "N53N-H", "T54N-H", "G56N-H", "C57N-H", "T58N-H", "G61N-H", "H63aN-H", "F64aN-H", "N65aN-H",
        "L67N-H", "S68N-H", "K70N-H", "G72N-H", "G73N-H", "K75N-H", "E78N-H", "R79N-H", "H80N-H", "V81N-H", "G82N-H",
        "G85N-H", "N86N-H", "V87N-H", "S102N-H", "V103N-H", "I104N-H", "S105N-H", "A111N-H", "I112N-H", "R115N-H",
        "V118N-H", "E121N-H", "A123N-H", "L126N-H", "G127N-H", "K128N-H", "G129N-H", "G130N-H", "N131N-H", "E133N-H",
        "S134N-H", "T135N-H", "T137N-H", "G138N-H", "N139N-H", "A140N-H", "G141N-H", "S142N-H", "R143N-H", "C146N-H", "G147N-H"]

        # Test number of global
        self.assertEqual(64, len(glob_assn ))

        ## Turn assignments into relax spin ids.
        # Define regular expression search
        r = re.compile("([a-zA-Z]+)([0-9]+)([a-zA-Z]+)")

        # Create list to hold regular expression search
        relax_glob_ids = []

        # Loop over assignments
        for assn in glob_assn:
            # Make match for the regular search
            m = r.match(assn)
            # Convert to relax spin string
            relax_string = ":%s@%s"%(m.group(2), m.group(3))

            # Save the relax spin string and the regular search
            relax_glob_ids.append([m.group(0), m.group(1), m.group(2), m.group(3), relax_string])

        ############# Deselect all spins, and select few spins

        ## Deselect all spins, and select a few for analysis
        self.interpreter.deselect.all()

        # Select few spins
        for i in select_spin_index:
            self.interpreter.select.spin(spin_id=relax_glob_ids[i][4], change_all=False)

        ##############

        # Prepare for R2eff calculation
        self.interpreter.pipe.copy(pipe_from=pipe_name, pipe_to=pipe_name_r2eff)
        self.interpreter.pipe.switch(pipe_name=pipe_name_r2eff)

        # Select model for points calculation
        MODEL = "R2eff"
        self.interpreter.relax_disp.select_model(model=MODEL)
        # Calculate R2eff values
        self.interpreter.minimise.calculate(verbosity=1)


    def setup_missing_r1_spins(self):
        """Function for setting up a few spins for the given pipe."""

        # Path to file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013'

        # File with spins.
        file = open(data_path+sep+'R1_fitted_values.txt')
        lines = file.readlines()
        file.close()

        for i, line in enumerate(lines):
            # Make the string test
            line_split = line.split()

            if line_split[0] == "#":
                continue

            mol_name = line_split[0]
            mol_name = None
            res_num = int(line_split[1])
            res_name = line_split[2]
            spin_num = line_split[3]
            spin_num = None
            spin_name = line_split[4]

            # Create the spin.
            self.interpreter.spin.create(spin_name=spin_name, spin_num=spin_num, res_name=res_name, res_num=res_num, mol_name=mol_name)


    def setup_tp02_data_to_ns_r1rho_2site(self, clustering=False):
        """Setup data for the test of relaxation dispersion 'NS R1rho 2-site' model fitting against the 'TP02' test data."""

        # Reset.
        self.interpreter.reset()

        # Create the data pipe and load the base data.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'r1rho_off_res_tp02'
        self.interpreter.state.load(data_path+sep+'r2eff_values')

        # The model data pipe.
        model = 'NS R1rho 2-site'
        pipe_name = "%s - relax_disp" % model
        self.interpreter.pipe.copy(pipe_from='base pipe', pipe_to=pipe_name, bundle_to='relax_disp')
        self.interpreter.pipe.switch(pipe_name=pipe_name)

        # Set the model.
        self.interpreter.relax_disp.select_model(model=model)

        # Copy the data.
        self.interpreter.value.copy(pipe_from='R2eff', pipe_to=pipe_name, param='r2eff')

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

        # Test the values when clustering.
        if clustering:
            self.interpreter.relax_disp.cluster(cluster_id='all', spin_id=":1-100")

        # Low precision optimisation.
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:1)", "Value (:2)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin1.r2[r20_key1], spin2.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin1.r2[r20_key2], spin2.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("pA", spin1.pA, spin2.pA))
        print("%-20s %20.15g %20.15g" % ("dw", spin1.dw, spin2.dw))
        print("%-20s %20.15g %20.15g" % ("kex", spin1.kex, spin2.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin1.chi2, spin2.chi2))


    def test_baldwin_synthetic(self):
        """Test synthetic data of Andrew J. Baldwin B14 model  whereby the simplification R20A = R20B is assumed.

        Support requst sr #3154 U{https://gna.org/support/index.php?3154}.

        This uses the synthetic data from paper U{DOI: 10.1016/j.jmr.2014.02.023 <http://dx.doi.org/10.1016/j.jmr.2014.02.023>} with R20A, R20B = 2. rad/s.
        """

        # The path to the data files.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Baldwin_2014'

        # Create pipe
        pipe_name = 'base pipe'
        pipe_type = 'relax_disp'
        pipe_name_r2eff = "%s_R2eff"%(pipe_name)

        # Create base pipe
        self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type=pipe_type)

        # Generate the sequence.
        self.interpreter.spin.create(res_name='Ala', res_num=1, spin_name='H')

        # Define the isotope.
        self.interpreter.spin.isotope('1H', spin_id='@H')

        # Build the experiment IDs.
        # Number of cpmg cycles (1 cycle = delay/180/delay/delay/180/delay)
        ncycs = [2, 4, 8, 10, 20, 40, 500]
        ids = []
        for ncyc in ncycs:
            ids.append('CPMG_%s' % ncyc)

        print("\n\nThe experiment IDs are %s." % ids)

        # Set up the metadata for the experiments.
        # This value is used in Baldwin.py. It is the 1H Larmor frequency.
        sfrq = 200. * 1E6

        # Total time of CPMG block.
        Trelax = 0.04

        # First set the
        for i in range(len(ids)):
            id = ids[i]
            # Set the spectrometer frequency.
            self.interpreter.spectrometer.frequency(id=id, frq=sfrq)

            # Set the experiment type.
            self.interpreter.relax_disp.exp_type(spectrum_id=id, exp_type='SQ CPMG')

            # Set the relaxation dispersion CPMG constant time delay T (in s).
            self.interpreter.relax_disp.relax_time(spectrum_id=id, time=Trelax)

            # Set the relaxation dispersion CPMG frequencies.
            ncyc = ncycs[i]
            nu_cpmg = ncyc / Trelax
            self.interpreter.relax_disp.cpmg_setup(spectrum_id=id, cpmg_frq=nu_cpmg)

        # Prepare for R2eff reading.
        self.interpreter.pipe.copy(pipe_from=pipe_name, pipe_to=pipe_name_r2eff)
        self.interpreter.pipe.switch(pipe_name=pipe_name_r2eff)

        # Try reading the R2eff file.
        self.interpreter.relax_disp.r2eff_read_spin(id="CPMG", file="test_r2a_eq_r2b_w_error.out", dir=data_path, spin_id=':1@H', disp_point_col=1, data_col=2, error_col=3)

        # Check the global data.
        data = [
            ['cpmg_frqs', {'CPMG_20': 500.0, 'CPMG_10': 250.0, 'CPMG_40': 1000.0, 'CPMG_4': 100.0, 'CPMG_2': 50.0, 'CPMG_500': 12500.0, 'CPMG_8': 200.0}],
            ['cpmg_frqs_list', list(array(ncycs)/Trelax) ],
            ['dispersion_points', len(ncycs)],
            ['exp_type', {'CPMG_20': 'SQ CPMG', 'CPMG_10': 'SQ CPMG', 'CPMG_40': 'SQ CPMG', 'CPMG_4': 'SQ CPMG', 'CPMG_2': 'SQ CPMG', 'CPMG_500': 'SQ CPMG', 'CPMG_8': 'SQ CPMG'}],
            ['exp_type_list', ['SQ CPMG']],
            ['spectrometer_frq', {'CPMG_20': 200000000.0, 'CPMG_10': 200000000.0, 'CPMG_40': 200000000.0, 'CPMG_4': 200000000.0, 'CPMG_2': 200000000.0, 'CPMG_500': 200000000.0, 'CPMG_8': 200000000.0}],
            ['spectrometer_frq_count', 1],
            ['spectrometer_frq_list', [sfrq]],
            ['spectrum_ids', ['CPMG_2', 'CPMG_4', 'CPMG_8', 'CPMG_10', 'CPMG_20', 'CPMG_40', 'CPMG_500']]
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
        n_data = [
            [ 50.000000, 10.367900, 0.1],
            [ 100.000000, 10.146849, 0.1],
            [ 200.000000, 9.765987, 0.1],
            [ 250.000000, 9.409789, 0.1],
            [ 500.000000, 5.829819, 0.1],
            [ 1000.000000, 3.191928, 0.1],
            [ 12500.000000, 2.008231, 0.1]
        ]
        for disp_point, value, error in n_data:
            id = 'sq_cpmg_200.00000000_0.000_%.3f' % disp_point
            self.assertEqual(cdp.mol[0].res[0].spin[0].r2eff[id], value)
            self.assertEqual(cdp.mol[0].res[0].spin[0].r2eff_err[id], error)

        # Generate r20 key.
        r20_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq)

        ## Now prepare for MODEL calculation.
        MODEL = "B14"

        # Change pipe.
        pipe_name_MODEL = "%s_%s"%(pipe_name, MODEL)
        self.interpreter.pipe.copy(pipe_from=pipe_name_r2eff, pipe_to=pipe_name_MODEL)
        self.interpreter.pipe.switch(pipe_name=pipe_name_MODEL)

        # Then select model.
        self.interpreter.relax_disp.select_model(model=MODEL)

        # Store grid and minimisations results.
        grid_results = []
        mini_results = []

        # The grid search size (the number of increments per dimension).
        # If None, use the default values.
        #GRID = None
        GRID = 13
        # Perform Grid Search.
        if GRID:
            # Set the R20 parameters in the default grid search using the minimum R2eff value.
            # This speeds it up considerably.
            self.interpreter.relax_disp.r20_from_min_r2eff(force=False)

            # Then do grid search.
            self.interpreter.minimise.grid_search(lower=None, upper=None, inc=GRID, constraints=True, verbosity=1)

            # If no Grid search, set the default values.
        else:
            for param in MODEL_PARAMS[MODEL]:
                self.interpreter.value.set(param=param, index=None)
                # Do a grid search, which will store the chi2 value.
            self.interpreter.minimise.grid_search(lower=None, upper=None, inc=1, constraints=True, verbosity=1)

        # Store result.
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            grid_results.append([spin.r2[r20_key], spin.dw, spin.pA, spin.kex, spin.chi2, spin_id, resi, resn])

        ## Now do minimisation.
        # Standard parameters are: func_tol = 1e-25, grad_tol = None, max_iter = 10000000,
        set_func_tol = 1e-10
        set_max_iter = 1000
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=set_func_tol, max_iter=set_max_iter, constraints=True, scaling=True, verbosity=1)

        # Store result.
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            mini_results.append([spin.r2[r20_key], spin.dw, spin.pA, spin.kex, spin.chi2, spin_id, resi, resn])

        # Print results.
        for i in range(len(grid_results)):
            g_r2, g_dw, g_pA, g_kex, g_chi2, g_spin_id, g_resi, g_resn = grid_results[i]
            m_r2, m_dw, m_pA, m_kex, m_chi2, m_spin_id, m_resi, m_resn = mini_results[i]
            print("GRID %s r2=%2.4f dw=%1.4f pA=%1.4f kex=%3.4f chi2=%3.4f spin_id=%s resi=%i resn=%s"%(g_spin_id, g_r2, g_dw, g_pA, g_kex, g_chi2, g_spin_id, g_resi, g_resn))
            print("MIN  %s r2=%2.4f dw=%1.4f pA=%1.4f kex=%3.4f chi2=%3.4f spin_id=%s resi=%i resn=%s"%(m_spin_id, m_r2, m_dw, m_pA, m_kex, m_chi2, m_spin_id, m_resi, m_resn))

        # Reference values from Baldwin.py.
        # Exchange rate = k+ + k- (s-1)
        kex = 1000.
        # Fractional population of excited state k+/kex
        pb = 0.01
        # deltaOmega in ppm
        dw_ppm = 2.
        #relaxation rate of ground (s-1)
        R2g = 2.
        #relaxation rate of excited (s-1)
        R2e = 2.

        # Test the parameters which created the data.
        # This is for the 1H spin.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].r2[r20_key], R2g, 6)

        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].dw, dw_ppm, 6)
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].pA, 1-pb, 8)
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].kex, kex, 3)


    def test_baldwin_synthetic_full(self):
        """Test synthetic data of Andrew J. Baldwin B14 model. Support requst sr #3154 U{https://gna.org/support/index.php?3154}.

        This uses the synthetic data from paper U{DOI: 10.1016/j.jmr.2014.02.023 <http://dx.doi.org/10.1016/j.jmr.2014.02.023>}.
        """

        # The path to the data files.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Baldwin_2014'

        # Create pipe
        pipe_name = 'base pipe'
        pipe_type = 'relax_disp'
        pipe_name_r2eff = "%s_R2eff"%(pipe_name)

        # Create base pipe
        self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type=pipe_type)

        # Generate the sequence.
        # Generate both a 1H spin, and 15N spin.
        self.interpreter.spin.create(res_name='Ala', res_num=1, spin_name='H')

        # Define the isotope.
        self.interpreter.spin.isotope('1H', spin_id='@H')

        # Build the experiment IDs.
        # Number of cpmg cycles (1 cycle = delay/180/delay/delay/180/delay)
        ncycs = [2, 4, 8, 10, 20, 40, 500]
        ids = []
        for ncyc in ncycs:
            ids.append('CPMG_%s' % ncyc)

        print("\n\nThe experiment IDs are %s." % ids)

        # Set up the metadata for the experiments.
        # This value is used in Baldwin.py. It is the 1H Larmor frequency.
        sfrq = 200. * 1E6

        # Total time of CPMG block.
        Trelax = 0.04

        # First set the
        for i in range(len(ids)):
            id = ids[i]
            # Set the spectrometer frequency.
            self.interpreter.spectrometer.frequency(id=id, frq=sfrq)

            # Set the experiment type.
            self.interpreter.relax_disp.exp_type(spectrum_id=id, exp_type='SQ CPMG')

            # Set the relaxation dispersion CPMG constant time delay T (in s).
            self.interpreter.relax_disp.relax_time(spectrum_id=id, time=Trelax)

            # Set the relaxation dispersion CPMG frequencies.
            ncyc = ncycs[i]
            nu_cpmg = ncyc / Trelax
            self.interpreter.relax_disp.cpmg_setup(spectrum_id=id, cpmg_frq=nu_cpmg)

        # Prepare for R2eff reading.
        self.interpreter.pipe.copy(pipe_from=pipe_name, pipe_to=pipe_name_r2eff)
        self.interpreter.pipe.switch(pipe_name=pipe_name_r2eff)

        # Try reading the R2eff file.
        self.interpreter.relax_disp.r2eff_read_spin(id="CPMG", file="test_w_error.out", dir=data_path, spin_id=':1@H', disp_point_col=1, data_col=2, error_col=3)

        # Check the global data.
        data = [
            ['cpmg_frqs', {'CPMG_20': 500.0, 'CPMG_10': 250.0, 'CPMG_40': 1000.0, 'CPMG_4': 100.0, 'CPMG_2': 50.0, 'CPMG_500': 12500.0, 'CPMG_8': 200.0}],
            ['cpmg_frqs_list', list(array(ncycs)/Trelax) ],
            ['dispersion_points', len(ncycs)],
            ['exp_type', {'CPMG_20': 'SQ CPMG', 'CPMG_10': 'SQ CPMG', 'CPMG_40': 'SQ CPMG', 'CPMG_4': 'SQ CPMG', 'CPMG_2': 'SQ CPMG', 'CPMG_500': 'SQ CPMG', 'CPMG_8': 'SQ CPMG'}],
            ['exp_type_list', ['SQ CPMG']],
            ['spectrometer_frq', {'CPMG_20': 200000000.0, 'CPMG_10': 200000000.0, 'CPMG_40': 200000000.0, 'CPMG_4': 200000000.0, 'CPMG_2': 200000000.0, 'CPMG_500': 200000000.0, 'CPMG_8': 200000000.0}],
            ['spectrometer_frq_count', 1],
            ['spectrometer_frq_list', [sfrq]],
            ['spectrum_ids', ['CPMG_2', 'CPMG_4', 'CPMG_8', 'CPMG_10', 'CPMG_20', 'CPMG_40', 'CPMG_500']]
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
        n_data = [
            [ 50.000000, 10.286255, 0.1],
            [ 100.000000, 10.073083, 0.1],
            [ 200.000000, 9.692746, 0.1],
            [ 250.000000, 9.382441, 0.1],
            [ 500.000000, 6.312396, 0.1],
            [ 1000.000000, 3.957029, 0.1],
            [ 12500.000000, 2.880420, 0.1]
        ]
        for disp_point, value, error in n_data:
            id = 'sq_cpmg_200.00000000_0.000_%.3f' % disp_point
            self.assertEqual(cdp.mol[0].res[0].spin[0].r2eff[id], value)
            self.assertEqual(cdp.mol[0].res[0].spin[0].r2eff_err[id], error)

        # Generate r20 key.
        r20_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq)

        ## Now prepare for MODEL calculation.
        MODEL = "B14 full"

        # Change pipe.
        pipe_name_MODEL = "%s_%s"%(pipe_name, MODEL)
        self.interpreter.pipe.copy(pipe_from=pipe_name_r2eff, pipe_to=pipe_name_MODEL)
        self.interpreter.pipe.switch(pipe_name=pipe_name_MODEL)

        # Then select model.
        self.interpreter.relax_disp.select_model(model=MODEL)

        # Store grid and minimisations results.
        grid_results = []
        mini_results = []
        clust_results = []

        # The grid search size (the number of increments per dimension).
        # If None, use the default values.
        #GRID = None
        GRID = 13
        # Perform Grid Search.
        if GRID:
            # Set the R20 parameters in the default grid search using the minimum R2eff value.
            # This speeds it up considerably.
            self.interpreter.relax_disp.r20_from_min_r2eff(force=False)

            # Then do grid search.
            self.interpreter.minimise.grid_search(lower=None, upper=None, inc=GRID, constraints=True, verbosity=1)

            # If no Grid search, set the default values.
        else:
            for param in MODEL_PARAMS[MODEL]:
                self.interpreter.value.set(param=param, index=None)
                # Do a grid search, which will store the chi2 value.
            self.interpreter.minimise.grid_search(lower=None, upper=None, inc=1, constraints=True, verbosity=1)

        # Store result.
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            grid_results.append([spin.r2a[r20_key], spin.r2b[r20_key], spin.dw, spin.pA, spin.kex, spin.chi2, spin_id, resi, resn])

        ## Now do minimisation.
        # Standard parameters are: func_tol = 1e-25, grad_tol = None, max_iter = 10000000,
        set_func_tol = 1e-11
        set_max_iter = 10000
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=set_func_tol, max_iter=set_max_iter, constraints=True, scaling=True, verbosity=1)

        # Store result.
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            mini_results.append([spin.r2a[r20_key], spin.r2b[r20_key], spin.dw, spin.pA, spin.kex, spin.chi2, spin_id, resi, resn])

        print("\n# Now print before and after minimisation-\n")

        # Print results.
        for i in range(len(grid_results)):
            g_r2a, g_r2b, g_dw, g_pA, g_kex, g_chi2, g_spin_id, g_resi, g_resn = grid_results[i]
            m_r2a, m_r2b, m_dw, m_pA, m_kex, m_chi2, m_spin_id, m_resi, m_resn = mini_results[i]
            print("GRID %s r2a=%2.4f r2b=%2.4f dw=%1.4f pA=%1.4f kex=%3.4f chi2=%3.4f spin_id=%s resi=%i resn=%s"%(g_spin_id, g_r2a, g_r2b, g_dw, g_pA, g_kex, g_chi2, g_spin_id, g_resi, g_resn))
            print("MIN  %s r2b=%2.4f r2b=%2.4f dw=%1.4f pA=%1.4f kex=%3.4f chi2=%3.4f spin_id=%s resi=%i resn=%s"%(m_spin_id, m_r2a, m_r2b, m_dw, m_pA, m_kex, m_chi2, m_spin_id, m_resi, m_resn))

        # Reference values from Baldwin.py.
        # Exchange rate = k+ + k- (s-1)
        kex = 1000.
        # Fractional population of excited state k+/kex
        pb = 0.01
        # deltaOmega in ppm
        dw_ppm = 2.
        #relaxation rate of ground (s-1)
        R2g = 2.
        #relaxation rate of excited (s-1)
        R2e = 100.

        # Test the parameters which created the data.
        # This is for the 1H spin.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].r2a[r20_key], R2g, 4)
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].r2b[r20_key], R2e, 2)

        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].dw, dw_ppm, 6)
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].pA, 1-pb, 6)
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].kex, kex, 2)


    def test_bug_21081_disp_cluster_fail(self):
        """U{Bug #21081<https://gna.org/bugs/?21081>} catch, the failure of a cluster analysis when spins are deselected."""

        # Clear the data store.
        self.interpreter.reset()

        # Load the state.
        state = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'saved_states'+sep+'bug_21081_disp_cluster_fail.bz2'
        self.interpreter.state.load(state, force=True)

        # Model selection - to catch the failure.
        self.interpreter.model_selection(method='AIC', modsel_pipe='final', bundle='relax_disp', pipes=['No Rex', 'CR72'])


    def test_bug_21460_disp_cluster_fail(self):
        """U{Bug #21460<https://gna.org/bugs/?21460>} catch, the failure due to a spectrometer frequency having no relaxation data."""

        # Clear the data store.
        self.interpreter.reset()

        # Load the state.
        state = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'saved_states'+sep+'bug_21460_bad_fields.bz2'
        self.interpreter.state.load(state, force=True)

        # Execute the auto-analysis (fast).
        relax_disp.Relax_disp.opt_func_tol = 1e-5
        relax_disp.Relax_disp.opt_max_iterations = 1000
        relax_disp.Relax_disp(pipe_name="origin - relax_disp (Thu Jan  2 13:46:44 2014)", pipe_bundle="relax_disp (Thu Jan  2 13:46:44 2014)", results_dir=self.tmpdir, models=['R2eff', 'No Rex', 'CR72', 'NS CPMG 2-site expanded'], grid_inc=3, mc_sim_num=5, modsel='AIC', pre_run_dir=None, insignificance=1.0, numeric_only=False, mc_sim_all_models=False, eliminate=True)


    def test_bug_21344_sparse_time_spinlock_acquired_r1rho_fail_relax_disp(self):
        """U{Bug #21665<https://gna.org/bugs/?21344>} catch, the failure of an analysis of a sparse acquired R1rho dataset with missing combinations of time and spin-lock field strengths using auto_analysis."""

        # Clear the data store.
        self.interpreter.reset()

        # Load the state.
        state = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21344_trunc.bz2'
        self.interpreter.state.load(state, force=True)

        # Execute the auto-analysis (fast).
        relax_disp.Relax_disp.opt_func_tol = 1e-5
        relax_disp.Relax_disp.opt_max_iterations = 1000
        relax_disp.Relax_disp(pipe_name='base pipe', pipe_bundle='relax_disp', results_dir=self.tmpdir, models=['R2eff'], grid_inc=3, mc_sim_num=5, modsel='AIC', pre_run_dir=None, insignificance=1.0, numeric_only=False, mc_sim_all_models=False, eliminate=True)


    def test_bug_21665_cpmg_two_fields_two_delaytimes_fail_calc(self):
        """U{Bug #21665<https://gna.org/bugs/?21665>} catch, the failure due to a a CPMG analysis recorded at two fields at two delay times, using minimise.calculate()."""

        # Clear the data store.
        self.interpreter.reset()

        # Load the state.
        state = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        self.interpreter.state.load(state, force=True)

        # Run the calculation.
        self.interpreter.minimise.calculate(verbosity=1)


    def test_bug_21665_cpmg_two_fields_two_delaytimes_fail_relax_disp(self):
        """U{Bug #21665<https://gna.org/bugs/?21665>} catch, the failure due to a a CPMG analysis recorded at two fields at two delay times using auto_analysis."""

        # Clear the data store.
        self.interpreter.reset()

        # Load the state.
        state = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        self.interpreter.state.load(state, force=True)

        # Execute the auto-analysis (fast).
        relax_disp.Relax_disp.opt_func_tol = 1e-5
        relax_disp.Relax_disp.opt_max_iterations = 1000
        relax_disp.Relax_disp(pipe_name="compare_128_FT_R2eff", pipe_bundle="cpmg_disp_sod1d90a", results_dir=self.tmpdir, models=['R2eff'], grid_inc=3, mc_sim_num=5, modsel='AIC', pre_run_dir=None, insignificance=1.0, numeric_only=False, mc_sim_all_models=False, eliminate=True)


    def test_bug_21715_clustered_indexerror(self):
        """Catch U{bug #21715<https://gna.org/bugs/?21715>}, the failure of a clustered auto-analysis due to an IndexError."""

        # Clear the data store.
        self.interpreter.reset()

        # Load the state.
        state = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21715_clustered_indexerror'+sep+'state.bz2'
        self.interpreter.state.load(state, force=True)

        # Execute the auto-analysis (fast).
        pre_run_dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21715_clustered_indexerror'+sep+'non_clustered'
        relax_disp.Relax_disp.opt_func_tol = 1e-5
        relax_disp.Relax_disp.opt_max_iterations = 1000
        relax_disp.Relax_disp(pipe_name='origin - relax_disp (Sun Feb 23 19:36:51 2014)', pipe_bundle='relax_disp (Sun Feb 23 19:36:51 2014)', results_dir=self.tmpdir, models=['R2eff', 'No Rex'], grid_inc=11, mc_sim_num=2, modsel='AIC', pre_run_dir=pre_run_dir, insignificance=1.0, numeric_only=True, mc_sim_all_models=False, eliminate=True)


    def test_bug_22146_unpacking_r2a_r2b_cluster_B14(self):
        """Catch U{bug #22146<https://gna.org/bugs/?22146>}, the failure of unpacking R2A and R2B, when performing a clustered B14 full analysis."""

        # Base data setup.
        self.setup_bug_22146_unpacking_r2a_r2b_cluster(folder='B14_full', model_analyse = MODEL_B14_FULL)


    def test_bug_22146_unpacking_r2a_r2b_cluster_CR72(self):
        """Catch U{bug #22146<https://gna.org/bugs/?22146>}, the failure of unpacking R2A and R2B, when performing a clustered CR72 full analysis."""

        # Base data setup.
        self.setup_bug_22146_unpacking_r2a_r2b_cluster(folder='CR72_full', model_analyse = MODEL_CR72_FULL)


    def test_bug_22146_unpacking_r2a_r2b_cluster_NS_3D(self):
        """Catch U{bug #22146<https://gna.org/bugs/?22146>}, the failure of unpacking R2A and R2B, when performing a clustered NS CPMG 2SITE 3D full analysis."""

        # Base data setup.
        self.setup_bug_22146_unpacking_r2a_r2b_cluster(folder='ns_cpmg_2site_3d_full', model_analyse = MODEL_NS_CPMG_2SITE_3D_FULL)


    def test_bug_22146_unpacking_r2a_r2b_cluster_NS_STAR(self):
        """Catch U{bug #22146<https://gna.org/bugs/?22146>}, the failure of unpacking R2A and R2B, when performing a clustered NS CPMG 2SITE STAR full analysis."""

        # Base data setup.
        self.setup_bug_22146_unpacking_r2a_r2b_cluster(folder='ns_cpmg_2site_star_full', model_analyse = MODEL_NS_CPMG_2SITE_STAR_FULL, places = 4)


    def test_bug_22477_grace_write_k_AB_mixed_analysis(self):
        """Catch U{bug #22146<https://gna.org/bugs/?22477>}, the failure of issuing: grace.write(x_data_type='res_num', y_data_type=param) for a mixed CPMG analysis."""

        # Clear the data store.
        self.interpreter.reset()

        # Load the state.
        state = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_22477_grace_write_k_AB_mixed_analysis'+sep+'bug_22477_results.bz2'
        self.interpreter.state.load(state, force=True)

        param = 'k_AB'

        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            print(spin_id, spin.params)
            if param in spin.params:
                print(spin_id, spin.k_AB, spin.k_AB_err)

        # Perform write.
        self.interpreter.grace.write(x_data_type='res_num', y_data_type=param, file='%s.agr'%param, dir=self.tmpdir, force=True)


        # Test the header of the value.write  parameter r2.
        param = 'r2'
        self.interpreter.value.write(param=param, file='%s.out'%param, dir=self.tmpdir, force=True)

        file = open(self.tmpdir+sep+'%s.out'%param)
        lines = file.readlines()
        file.close()

        for i, line in enumerate(lines):
            # Make the string test
            line_split = line.split()
            print(line_split)

            if len(line_split) > 1:
                # Break at parameter header.
                if line_split[0] == "#" and line_split[1] == 'mol_name':
                    nr_split_header = len(line_split)
                    nr_split_header_i = i
                    break

        # Call the line after.
        line_split_val = lines[nr_split_header_i + 1].split()
        print(line_split_val)

        # Assert that the number of columns is equal, plus 1 for "#".
        self.assertEqual(nr_split_header, len(line_split_val) + 1)

        # Test the header of the value.write for parameter r2eff.
        param = 'r2eff'
        self.interpreter.value.write(param=param, file='%s.out'%param, dir=self.tmpdir, force=True)

        file = open(self.tmpdir+sep+'%s.out'%param)
        lines = file.readlines()
        file.close()

        for i, line in enumerate(lines):
            # Make the string test
            line_split = line.split()
            print(line_split)

            if len(line_split) > 1:
                # Break at parameter header.
                if line_split[0] == "#" and line_split[1] == 'mol_name':
                    nr_split_header = len(line_split)
                    nr_split_header_i = i
                    break

        # Call the line after.
        line_split_val = lines[nr_split_header_i + 1].split()
        print(line_split_val)

        # Assert that the number of columns is equal, plus 1 for "#".
        self.assertEqual(nr_split_header, len(line_split_val) + 1)


    def test_bug_9999_slow_r1rho_r2eff_error_with_mc(self):
        """Catch U{bug #9999<https://gna.org/bugs/?9999>}, The slow optimisation of R1rho R2eff error estimation with Monte Carlo simulations."""

        # Define path to data 
        prev_data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013' +sep+ "check_graphs" +sep+ "mc_2000"  +sep+ "R2eff"

        # Read data.
        self.interpreter.results.read(prev_data_path + sep + 'results')        

        # Now count number
        graph_nr = 1
        for exp_type, frq, offset, point in loop_exp_frq_offset_point(return_indices=False):
            print("\nGraph nr %i" % graph_nr)
            for time in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point):
                print(exp_type, frq, offset, point, time)
            graph_nr += 1

        ## Possibly do an error analysis.

        # Check if intensity errors have already been calculated by the user.
        precalc = True
        for spin in spin_loop(skip_desel=True):
            # No structure.
            if not hasattr(spin, 'peak_intensity_err'):
                precalc = False
                break

            # Determine if a spectrum ID is missing from the list.
            for id in cdp.spectrum_ids:
                if id not in spin.peak_intensity_err:
                    precalc = False
                    break

        # Skip.
        if precalc:
            print("Skipping the error analysis as it has already been performed.")

        else:
            # Loop over the spectrometer frequencies.
            for frq in loop_frq():
                # Generate a list of spectrum IDs matching the frequency.
                ids = []
                for id in cdp.spectrum_ids:
                    # Check that the spectrometer frequency matches.
                    match_frq = True
                    if frq != None and cdp.spectrometer_frq[id] != frq:
                        match_frq = False

                    # Add the ID.
                    if match_frq:
                        ids.append(id)

                # Run the error analysis on the subset.
                self.interpreter.spectrum.error_analysis(subset=ids)

        print("has_exponential_exp_type:", has_exponential_exp_type())

        model = 'R2eff'
        self.interpreter.relax_disp.select_model(model)

        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            #delattr(spin, 'r2eff')
            #delattr(spin, 'r2eff_err')
            #delattr(spin, 'i0')
            #delattr(spin, 'i0_err')
            setattr(spin, 'r2eff', {})
            setattr(spin, 'r2eff_err', {})
            setattr(spin, 'i0', {})
            setattr(spin, 'i0_err', {})

        # Do Grid Search
        self.interpreter.minimise.grid_search(lower=None, upper=None, inc=21, constraints=True, verbosity=1)

        # Start dic.
        my_dic = {}

        # Define counter for maximum elements in the numpy array list
        NE = 0
        NS = 1
        NM = 0
        NO = 0
        ND = 0
        NT = 0

        for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
            # Save to counter.
            if ei > NE:
                NE = ei
            if mi > NM:
                NM = mi
            if oi > NO:
                NO = oi
            if di > ND:
               ND = di

            for time, ti in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point, return_indices=True):
                # Save to counter.
                if ti > NT:
                    NT = ti

        # Add 1 to counter, since index start from 0.
        NE = NE + 1
        NM = NM + 1 
        NO = NO + 1
        ND = ND + 1
        NT = NT + 1

        # Make data array.
        values_arr = zeros([NE, NS, NM, NO, ND, NT])
        errors_arr = zeros([NE, NS, NM, NO, ND, NT])
        times_arr = zeros([NE, NS, NM, NO, ND, NT])
        struct_arr = zeros([NE, NS, NM, NO, ND, NT])
        param_key_list = []


        # Loop over each spectrometer frequency and dispersion point.
        for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            # Add key to dic.
            my_dic[spin_id] = {}

            # Generate spin string.
            spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

            # Loop over the parameters.
            #print("Grid optimised parameters for spin: %s" % (spin_string))

            for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
                # Generate the param_key.
                param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

                # Append key.
                param_key_list.append(param_key)

                # Add key to dic.
                my_dic[spin_id][param_key] = {}

                # Get the value.
                R2eff_value = getattr(cur_spin, 'r2eff')[param_key]
                i0_value = getattr(cur_spin, 'i0')[param_key]

                # Save to dic.
                my_dic[spin_id][param_key]['R2eff_value_grid'] = R2eff_value
                my_dic[spin_id][param_key]['i0_value_grid'] = i0_value

                ## Now try do a line of best fit by least squares.
                # The peak intensities, errors and times.
                values = []
                errors = []
                times = []
                for time, ti in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point, return_indices=True):
                    value = average_intensity(spin=cur_spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time, sim_index=None)
                    values.append(value)

                    error = average_intensity(spin=cur_spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time, error=True)
                    errors.append(error)
                    times.append(time)

                    # Save to numpy arrays.
                    values_arr[ei, 0, mi, oi, di, ti] = value
                    errors_arr[ei, 0, mi, oi, di, ti] = error
                    times_arr[ei, 0, mi, oi, di, ti] = time
                    struct_arr[ei, 0, mi, oi, di, ti] = 1.0

                # y= A exp(x * k)
                # w[i] = ln(y[i])
                # int[i] = i0 * exp( - times[i] * r2eff);
                w = log(array(values))
                x = - array(times)
                n = len(times)

                b = (sum(x*w) - 1./n * sum(x) * sum(w) ) / ( sum(x**2) - 1./n * (sum(x))**2 )
                a = 1./n * sum(w) - b * 1./n * sum(x)
                R2eff_est = b
                i0_est = exp(a)

                my_dic[spin_id][param_key]['R2eff_est'] = R2eff_est
                my_dic[spin_id][param_key]['i0_est'] = i0_est

                # Print value.
                #print("%-10s %-6s %-6s %3.1f : %3.1f" % ("Parameter:", 'R2eff', "Value : Estimated:", R2eff_value, R2eff_est))
                #print("%-10s %-6s %-6s %3.1f : %3.1f" % ("Parameter:", 'i0', "Value: Estimated:", i0_value, i0_est))


        # Do minimisation.
        set_func_tol = 1e-25
        set_max_iter = int(1e7)
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=set_func_tol, max_iter=set_max_iter, constraints=True, scaling=True, verbosity=1)

        # Loop over each spectrometer frequency and dispersion point.
        for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            # Generate spin string.
            spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

            # Loop over the parameters.
            print("Optimised parameters for spin: %s" % (spin_string))

            for exp_type, frq, offset, point in loop_exp_frq_offset_point():
                # Generate the param_key.
                param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

                # Get the value.
                R2eff_value = getattr(cur_spin, 'r2eff')[param_key]
                i0_value = getattr(cur_spin, 'i0')[param_key]

                # Extract from dic.
                R2eff_value_grid = my_dic[spin_id][param_key]['R2eff_value_grid']
                i0_value_grid = my_dic[spin_id][param_key]['i0_value_grid']
                R2eff_est = my_dic[spin_id][param_key]['R2eff_est']
                i0_est = my_dic[spin_id][param_key]['i0_est']

                # Print value.
                #print("%-10s %-6s %-6s %3.1f : %3.1f" % ("Parameter:", 'R2eff', "Value : Estimated:", R2eff_value, R2eff_est))
                #print("%-10s %-6s %-6s %3.1f : %3.1f" % ("Parameter:", 'i0', "Value: Estimated:", i0_value, i0_est))

                print("%-10s %-6s %-6s %3.1f : %3.1f: %3.1f" % ("Parameter:", 'R2eff', "Grid : Min : Estimated:", R2eff_value_grid, R2eff_value, R2eff_est))
                print("%-10s %-6s %-6s %3.1f : %3.1f: %3.1f" % ("Parameter:", 'i0', "Grid : Min : Estimated:", i0_value_grid, i0_value, i0_est))

        print(NE, NS, NM, NO, ND, NT)
        for param_key in param_key_list:
            print("        '%s'," % param_key)
        print(values_arr.shape)

        # Save arrays to profiling.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting'+sep+'profiling'+sep
        #save(data_path + "values_arr", values_arr)
        #save(data_path + "errors_arr", errors_arr)
        #save(data_path + "times_arr", times_arr)
        #save(data_path + "struct_arr", struct_arr)


    def test_check_missing_r1(self):
        """Test of the check_missing_r1() function."""

        # Set up some spins.
        self.setup_missing_r1_spins()

        # Set variables.
        exp_type = 'R1rho'
        frq = 800.1 * 1E6

        spectrum_id='test'

        # Set an experiment type to the pipe.
        self.interpreter.relax_disp.exp_type(spectrum_id=spectrum_id, exp_type=exp_type)

        # Set a frequency to loop through.
        self.interpreter.spectrometer.frequency(id=spectrum_id, frq=frq, units='Hz')

        # Check R1 for DPL94.
        check_missing_r1_return = check_missing_r1(model=MODEL_DPL94)
        self.assertEqual(check_missing_r1_return, True)

        # Check R1 for R2eff.
        check_missing_r1_return = check_missing_r1(model=MODEL_R2EFF)
        self.assertEqual(check_missing_r1_return, False)

        # The path to the data files.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013'

        # Now load some R1 data.
        self.interpreter.relax_data.read(ri_id='R1', ri_type='R1', frq=cdp.spectrometer_frq_list[0], file='R1_fitted_values.txt', dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

        # Check R1.
        check_missing_r1_return = check_missing_r1(model=MODEL_DPL94)
        self.assertEqual(check_missing_r1_return, False)


    def test_cpmg_synthetic_b14_to_ns3d_cluster(self):
        """Test synthetic cpmg data.  Created with B14, analysed with NS CPMG 2site 3D, for clustered analysis.

        This is part of: U{Task #7807 <https://gna.org/task/index.php?7807>}: Speed-up of dispersion models for Clustered analysis.

        This script will produce synthetic CPMG R2eff values according to the selected model, and the fit the selected model.
        """

        # Reset.
        #self.interpreter.reset()

        ## Set Experiments.
        model_create = 'B14'
        #model_create = 'NS CPMG 2-site expanded'
        model_analyse = 'NS CPMG 2-site 3D'

        # Exp 1
        sfrq_1 = 599.8908617*1E6
        r20_key_1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_1)
        time_T2_1 = 0.06
        ncycs_1 = [2, 4, 8, 10, 20, 30, 40, 60]
        #r2eff_errs_1 = [0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05]
        r2eff_errs_1 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        exp_1 = [sfrq_1, time_T2_1, ncycs_1, r2eff_errs_1]

        sfrq_2 = 499.8908617*1E6
        r20_key_2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_2)
        time_T2_2 = 0.05
        ncycs_2 = [2, 4, 8, 10, 30, 35, 40, 50]
        #r2eff_errs_2 = [0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05]
        r2eff_errs_2 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        exp_2 = [sfrq_2, time_T2_2, ncycs_2, r2eff_errs_2]

        # Collect all exps
        exps = [exp_1, exp_2]

        spins = [
            ['Ala', 1, 'N', {'r2': {r20_key_1:10., r20_key_2:11.5}, 'r2a': {r20_key_1:10., r20_key_2:11.5}, 'r2b': {r20_key_1:10., r20_key_2:11.5}, 'kex': 1000., 'pA': 0.95, 'dw': 2.} ],
            ['Ala', 2, 'N', {'r2': {r20_key_1:13., r20_key_2:14.5}, 'r2a': {r20_key_1:13., r20_key_2:14.5}, 'r2b': {r20_key_1:13., r20_key_2:14.5}, 'kex': 1000., 'pA': 0.95, 'dw': 1.} ]
            ]

        # Collect the data to be used.
        ds.data = [model_create, model_analyse, spins, exps]

        # The tmp directory. None is the local directory.
        ds.tmpdir = ds.tmpdir

        # The results directory. None is the local directory.
        #ds.resdir = None
        ds.resdir = ds.tmpdir

        # Do r20_from_min_r2eff ?.
        ds.r20_from_min_r2eff = True

        # Remove insignificant level.
        ds.insignificance = 0.0

        # The grid search size (the number of increments per dimension).
        ds.GRID_INC = None

        # The do clustering.
        ds.do_cluster = True

        # The function tolerance.  This is used to terminate minimisation once the function value between iterations is less than the tolerance.
        # The default value is 1e-25.
        ds.set_func_tol = 1e-1

        # The maximum number of iterations.
        # The default value is 1e7.
        ds.set_max_iter = 1000

        # The verbosity level.
        ds.verbosity = 1

        # The rel_change WARNING level.
        ds.rel_change = 0.05

        # The plot_curves.
        ds.plot_curves = False

        # The conversion for ShereKhan at http://sherekhan.bionmr.org/.
        ds.sherekhan_input = False

        # Make a dx map to be opened om OpenDX. To map the hypersurface of chi2, when altering kex, dw and pA.
        ds.opendx = False

        # The set r2eff err.
        ds.r2eff_err = 0.1

        # The print result info.
        ds.print_res = True

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'cpmg_synthetic.py')

        cur_spins = ds.data[2]
        # Compare results.
        for i in range(len(cur_spins)):
            res_name, res_num, spin_name, params = cur_spins[i]
            cur_spin_id = ":%i@%s"%(res_num, spin_name)
            cur_spin = return_spin(cur_spin_id)

            grid_params = ds.grid_results[i][3]

            # Extract the clust results.
            min_params = ds.clust_results[i][3]
            # Now read the parameters.
            print("For spin: '%s'"%cur_spin_id)
            for mo_param in cur_spin.params:
                # The R2 is a dictionary, depending on spectrometer frequency.
                if isinstance(getattr(cur_spin, mo_param), dict):
                    grid_r2 = grid_params[mo_param]
                    min_r2 = min_params[mo_param]
                    set_r2 = params[mo_param]
                    for key, val in set_r2.items():
                        grid_r2_frq = grid_r2[key]
                        min_r2_frq = min_r2[key]
                        set_r2_frq = set_r2[key]
                        frq = float(key.split(EXP_TYPE_CPMG_SQ+' - ')[-1].split('MHz')[0])
                        rel_change = math.sqrt( (min_r2_frq - set_r2_frq)**2/(min_r2_frq)**2 )
                        print("%s %s %s %s %.1f GRID=%.3f MIN=%.3f SET=%.3f RELC=%.3f"%(cur_spin.model, res_name, cur_spin_id, mo_param, frq, grid_r2_frq, min_r2_frq, set_r2_frq, rel_change) )
                        if rel_change > ds.rel_change:
                            print("WARNING: rel change level is above %.2f, and is %.4f."%(ds.rel_change, rel_change))
                            print("###################################")

                        ## Make test on R2.
                        self.assertAlmostEqual(set_r2_frq, min_r2_frq, 1)
                else:
                    grid_val = grid_params[mo_param]
                    min_val = min_params[mo_param]
                    set_val = params[mo_param]
                    rel_change = math.sqrt( (min_val - set_val)**2/(min_val)**2 )
                    print("%s %s %s %s GRID=%.3f MIN=%.3f SET=%.3f RELC=%.3f"%(cur_spin.model, res_name, cur_spin_id, mo_param, grid_val, min_val, set_val, rel_change) )
                    if rel_change > ds.rel_change:
                        print("WARNING: rel change level is above %.2f, and is %.4f."%(ds.rel_change, rel_change))
                        print("###################################")

                    ## Make test on parameters.
                    if mo_param == 'dw':
                        self.assertAlmostEqual(set_val/10, min_val/10, 1)
                    elif mo_param == 'kex':
                        self.assertAlmostEqual(set_val/1000, min_val/1000, 1)
                    elif mo_param == 'pA':
                        self.assertAlmostEqual(set_val, min_val, 2)


    def test_cpmg_synthetic_b14_to_ns_star_cluster(self):
        """Test synthetic cpmg data.  Created with B14, analysed with NS CPMG 2site STAR, for clustered analysis.

        This is part of: U{Task #7807 <https://gna.org/task/index.php?7807>}: Speed-up of dispersion models for Clustered analysis.

        This script will produce synthetic CPMG R2eff values according to the selected model, and the fit the selected model.
        """

        # Reset.
        #self.interpreter.reset()

        ## Set Experiments.
        model_create = 'B14'
        #model_create = 'NS CPMG 2-site expanded'
        model_analyse = 'NS CPMG 2-site star'

        # Exp 1
        sfrq_1 = 599.8908617*1E6
        r20_key_1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_1)
        time_T2_1 = 0.06
        ncycs_1 = [2, 4, 8, 10, 20, 30, 40, 60]
        #r2eff_errs_1 = [0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05]
        r2eff_errs_1 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        exp_1 = [sfrq_1, time_T2_1, ncycs_1, r2eff_errs_1]

        sfrq_2 = 499.8908617*1E6
        r20_key_2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_2)
        time_T2_2 = 0.05
        ncycs_2 = [2, 4, 8, 10, 30, 35, 40, 50]
        #r2eff_errs_2 = [0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05]
        r2eff_errs_2 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        exp_2 = [sfrq_2, time_T2_2, ncycs_2, r2eff_errs_2]

        # Collect all exps
        exps = [exp_1, exp_2]

        spins = [
            ['Ala', 1, 'N', {'r2': {r20_key_1:10., r20_key_2:11.5}, 'r2a': {r20_key_1:10., r20_key_2:11.5}, 'r2b': {r20_key_1:10., r20_key_2:11.5}, 'kex': 1000., 'pA': 0.95, 'dw': 2.} ],
            ['Ala', 2, 'N', {'r2': {r20_key_1:13., r20_key_2:14.5}, 'r2a': {r20_key_1:13., r20_key_2:14.5}, 'r2b': {r20_key_1:13., r20_key_2:14.5}, 'kex': 1000., 'pA': 0.95, 'dw': 1.} ]
            ]

        # Collect the data to be used.
        ds.data = [model_create, model_analyse, spins, exps]

        # The tmp directory. None is the local directory.
        ds.tmpdir = ds.tmpdir

        # The results directory. None is the local directory.
        #ds.resdir = None
        ds.resdir = ds.tmpdir

        # Do r20_from_min_r2eff ?.
        ds.r20_from_min_r2eff = True

        # Remove insignificant level.
        ds.insignificance = 0.0

        # The grid search size (the number of increments per dimension).
        ds.GRID_INC = None

        # The do clustering.
        ds.do_cluster = True

        # The function tolerance.  This is used to terminate minimisation once the function value between iterations is less than the tolerance.
        # The default value is 1e-25.
        ds.set_func_tol = 1e-1

        # The maximum number of iterations.
        # The default value is 1e7.
        ds.set_max_iter = 1000

        # The verbosity level.
        ds.verbosity = 1

        # The rel_change WARNING level.
        ds.rel_change = 0.05

        # The plot_curves.
        ds.plot_curves = False

        # The conversion for ShereKhan at http://sherekhan.bionmr.org/.
        ds.sherekhan_input = False

        # Make a dx map to be opened om OpenDX. To map the hypersurface of chi2, when altering kex, dw and pA.
        ds.opendx = False

        # The set r2eff err.
        ds.r2eff_err = 0.1

        # The print result info.
        ds.print_res = True

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'cpmg_synthetic.py')

        cur_spins = ds.data[2]
        # Compare results.
        for i in range(len(cur_spins)):
            res_name, res_num, spin_name, params = cur_spins[i]
            cur_spin_id = ":%i@%s"%(res_num, spin_name)
            cur_spin = return_spin(cur_spin_id)

            grid_params = ds.grid_results[i][3]

            # Extract the clust results.
            min_params = ds.clust_results[i][3]
            # Now read the parameters.
            print("For spin: '%s'"%cur_spin_id)
            for mo_param in cur_spin.params:
                # The R2 is a dictionary, depending on spectrometer frequency.
                if isinstance(getattr(cur_spin, mo_param), dict):
                    grid_r2 = grid_params[mo_param]
                    min_r2 = min_params[mo_param]
                    set_r2 = params[mo_param]
                    for key, val in set_r2.items():
                        grid_r2_frq = grid_r2[key]
                        min_r2_frq = min_r2[key]
                        set_r2_frq = set_r2[key]
                        frq = float(key.split(EXP_TYPE_CPMG_SQ+' - ')[-1].split('MHz')[0])
                        rel_change = math.sqrt( (min_r2_frq - set_r2_frq)**2/(min_r2_frq)**2 )
                        print("%s %s %s %s %.1f GRID=%.3f MIN=%.3f SET=%.3f RELC=%.3f"%(cur_spin.model, res_name, cur_spin_id, mo_param, frq, grid_r2_frq, min_r2_frq, set_r2_frq, rel_change) )
                        if rel_change > ds.rel_change:
                            print("WARNING: rel change level is above %.2f, and is %.4f."%(ds.rel_change, rel_change))
                            print("###################################")

                        ## Make test on R2.
                        self.assertAlmostEqual(set_r2_frq, min_r2_frq, 1)
                else:
                    grid_val = grid_params[mo_param]
                    min_val = min_params[mo_param]
                    set_val = params[mo_param]
                    rel_change = math.sqrt( (min_val - set_val)**2/(min_val)**2 )
                    print("%s %s %s %s GRID=%.3f MIN=%.3f SET=%.3f RELC=%.3f"%(cur_spin.model, res_name, cur_spin_id, mo_param, grid_val, min_val, set_val, rel_change) )
                    if rel_change > ds.rel_change:
                        print("WARNING: rel change level is above %.2f, and is %.4f."%(ds.rel_change, rel_change))
                        print("###################################")

                    ## Make test on parameters.
                    if mo_param == 'dw':
                        self.assertAlmostEqual(set_val/10, min_val/10, 1)
                    elif mo_param == 'kex':
                        self.assertAlmostEqual(set_val/1000, min_val/1000, 1)
                    elif mo_param == 'pA':
                        self.assertAlmostEqual(set_val, min_val, 2)


    def test_cpmg_synthetic_ns3d_to_cr72(self):
        """Test synthetic cpmg data.

        This script will produce synthetic CPMG R2eff values according to the NS CPMG 2-site 3D model, and the fit the data with CR72.
        """

        # Reset.
        #self.interpreter.reset()

        ## Set Experiments.
        model_create = 'NS CPMG 2-site 3D'
        #model_create = 'NS CPMG 2-site expanded'
        model_analyse = 'CR72'
        # Exp 1
        sfrq_1 = 599.8908617*1E6
        r20_key_1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_1)
        time_T2_1 = 0.06
        ncycs_1 = [2, 4, 8, 10, 20, 30, 40, 60]
        r2eff_err_1 = [0, 0, 0, 0, 0, 0, 0, 0]
        exp_1 = [sfrq_1, time_T2_1, ncycs_1, r2eff_err_1]

        sfrq_2 = 499.8908617*1E6
        r20_key_2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_2)
        time_T2_2 = 0.05
        ncycs_2 = [2, 4, 8, 10, 30, 35, 40, 50]
        r2eff_err_2 = [0, 0, 0, 0, 0, 0, 0, 0]
        exp_2 = [sfrq_2, time_T2_2, ncycs_2, r2eff_err_2]

        # Collect all exps
        exps = [exp_1, exp_2]

        spins = [
            ['Ala', 1, 'N', {'r2': {r20_key_1:10., r20_key_2:10.}, 'r2a': {r20_key_1:10., r20_key_2:10.}, 'r2b': {r20_key_1:10., r20_key_2:10.}, 'kex': 1000., 'pA': 0.99, 'dw': 2.} ]
            ]

        # Collect the data to be used.
        ds.data = [model_create, model_analyse, spins, exps]

        # The tmp directory. None is the local directory.
        ds.tmpdir = ds.tmpdir

        # The results directory. None is the local directory.
        #ds.resdir = None
        ds.resdir = ds.tmpdir

        # Do r20_from_min_r2eff ?.
        ds.r20_from_min_r2eff = True

        # Remove insignificant level.
        ds.insignificance = 0.0

        # The grid search size (the number of increments per dimension).
        ds.GRID_INC = 8

        # The do clustering.
        ds.do_cluster = False

        # The function tolerance.  This is used to terminate minimisation once the function value between iterations is less than the tolerance.
        # The default value is 1e-25.
        ds.set_func_tol = 1e-9

        # The maximum number of iterations.
        # The default value is 1e7.
        ds.set_max_iter = 1000

        # The verbosity level.
        ds.verbosity = 1

        # The rel_change WARNING level.
        ds.rel_change = 0.05

        # The plot_curves.
        ds.plot_curves = False

        # The conversion for ShereKhan at http://sherekhan.bionmr.org/.
        ds.sherekhan_input = False

        # Make a dx map to be opened om OpenDX. To map the hypersurface of chi2, when altering kex, dw and pA.
        ds.opendx = False

        # The set r2eff err.
        ds.r2eff_err = 0.1

        # The print result info.
        ds.print_res = False

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'cpmg_synthetic.py')

        cur_spins = ds.data[2]
        # Compare results.
        for i in range(len(cur_spins)):
            res_name, res_num, spin_name, params = cur_spins[i]
            cur_spin_id = ":%i@%s"%(res_num, spin_name)
            cur_spin = return_spin(cur_spin_id)

            grid_params = ds.grid_results[i][3]
            min_params = ds.min_results[i][3]
            # Now read the parameters.
            print("For spin: '%s'"%cur_spin_id)
            for mo_param in cur_spin.params:
                # The R2 is a dictionary, depending on spectrometer frequency.
                if isinstance(getattr(cur_spin, mo_param), dict):
                    grid_r2 = grid_params[mo_param]
                    min_r2 = min_params[mo_param]
                    set_r2 = params[mo_param]
                    for key, val in set_r2.items():
                        grid_r2_frq = grid_r2[key]
                        min_r2_frq = min_r2[key]
                        set_r2_frq = set_r2[key]
                        frq = float(key.split(EXP_TYPE_CPMG_SQ+' - ')[-1].split('MHz')[0])
                        rel_change = math.sqrt( (min_r2_frq - set_r2_frq)**2/(min_r2_frq)**2 )
                        print("%s %s %s %s %.1f GRID=%.3f MIN=%.3f SET=%.3f RELC=%.3f"%(cur_spin.model, res_name, cur_spin_id, mo_param, frq, grid_r2_frq, min_r2_frq, set_r2_frq, rel_change) )
                        if rel_change > ds.rel_change:
                            print("WARNING: rel change level is above %.2f, and is %.4f."%(ds.rel_change, rel_change))
                            print("###################################")

                        ## Make test on R2.
                        self.assertAlmostEqual(set_r2_frq, min_r2_frq, 2)
                else:
                    grid_val = grid_params[mo_param]
                    min_val = min_params[mo_param]
                    set_val = params[mo_param]
                    rel_change = math.sqrt( (min_val - set_val)**2/(min_val)**2 )
                    print("%s %s %s %s GRID=%.3f MIN=%.3f SET=%.3f RELC=%.3f"%(cur_spin.model, res_name, cur_spin_id, mo_param, grid_val, min_val, set_val, rel_change) )
                    if rel_change > ds.rel_change:
                        print("WARNING: rel change level is above %.2f, and is %.4f."%(ds.rel_change, rel_change))
                        print("###################################")

                    ## Make test on parameters.
                    if mo_param == 'dw':
                        self.assertAlmostEqual(set_val/10, min_val/10, 1)
                    elif mo_param == 'kex':
                        self.assertAlmostEqual(set_val/1000, min_val/1000, 1)
                    elif mo_param == 'pA':
                        self.assertAlmostEqual(set_val, min_val, 3)


    def test_cpmg_synthetic_ns3d_to_b14(self):
        """Test synthetic cpmg data.

        This script will produce synthetic CPMG R2eff values according to the NS CPMG 2-site 3D model, and the fit the data with B14.
        Try to catch bug #22021 U{https://gna.org/bugs/index.php?22021}: Model B14 shows bad fitting to data.
        """

        # Reset.
        #self.interpreter.reset()

        ## Set Experiments.
        model_create = 'NS CPMG 2-site 3D'
        #model_create = 'NS CPMG 2-site expanded'
        model_analyse = 'B14'
        # Exp 1
        sfrq_1 = 599.8908617*1E6
        r20_key_1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_1)
        time_T2_1 = 0.06
        ncycs_1 = [2, 4, 8, 10, 20, 30, 40, 60]
        r2eff_err_1 = [0, 0, 0, 0, 0, 0, 0, 0]
        exp_1 = [sfrq_1, time_T2_1, ncycs_1, r2eff_err_1]

        sfrq_2 = 499.8908617*1E6
        r20_key_2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_2)
        time_T2_2 = 0.05
        ncycs_2 = [2, 4, 8, 10, 30, 35, 40, 50]
        r2eff_err_2 = [0, 0, 0, 0, 0, 0, 0, 0]
        exp_2 = [sfrq_2, time_T2_2, ncycs_2, r2eff_err_2]

        # Collect all exps
        exps = [exp_1, exp_2]

        spins = [
            ['Ala', 1, 'N', {'r2': {r20_key_1:10., r20_key_2:10.}, 'r2a': {r20_key_1:10., r20_key_2:10.}, 'r2b': {r20_key_1:10., r20_key_2:10.}, 'kex': 1000., 'pA': 0.99, 'dw': 2.} ]
            ]

        # Collect the data to be used.
        ds.data = [model_create, model_analyse, spins, exps]

        # The tmp directory. None is the local directory.
        ds.tmpdir = ds.tmpdir

        # The results directory. None is the local directory.
        #ds.resdir = None
        ds.resdir = ds.tmpdir

        # Do r20_from_min_r2eff ?.
        ds.r20_from_min_r2eff = True

        # Remove insignificant level.
        ds.insignificance = 0.0

        # The grid search size (the number of increments per dimension).
        ds.GRID_INC = 8

        # The do clustering.
        ds.do_cluster = False

        # The function tolerance.  This is used to terminate minimisation once the function value between iterations is less than the tolerance.
        # The default value is 1e-25.
        ds.set_func_tol = 1e-9

        # The maximum number of iterations.
        # The default value is 1e7.
        ds.set_max_iter = 1000

        # The verbosity level.
        ds.verbosity = 1

        # The rel_change WARNING level.
        ds.rel_change = 0.05

        # The plot_curves.
        ds.plot_curves = False

        # The conversion for ShereKhan at http://sherekhan.bionmr.org/.
        ds.sherekhan_input = False

        # Make a dx map to be opened om OpenDX. To map the hypersurface of chi2, when altering kex, dw and pA.
        ds.opendx = False

        # The set r2eff err.
        ds.r2eff_err = 0.1

        # The print result info.
        ds.print_res = False

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'cpmg_synthetic.py')

        cur_spins = ds.data[2]
        # Compare results.
        for i in range(len(cur_spins)):
            res_name, res_num, spin_name, params = cur_spins[i]
            cur_spin_id = ":%i@%s"%(res_num, spin_name)
            cur_spin = return_spin(cur_spin_id)

            grid_params = ds.grid_results[i][3]
            min_params = ds.min_results[i][3]
            # Now read the parameters.
            print("For spin: '%s'"%cur_spin_id)
            for mo_param in cur_spin.params:
                # The R2 is a dictionary, depending on spectrometer frequency.
                if isinstance(getattr(cur_spin, mo_param), dict):
                    grid_r2 = grid_params[mo_param]
                    min_r2 = min_params[mo_param]
                    set_r2 = params[mo_param]
                    for key, val in set_r2.items():
                        grid_r2_frq = grid_r2[key]
                        min_r2_frq = min_r2[key]
                        set_r2_frq = set_r2[key]
                        frq = float(key.split(EXP_TYPE_CPMG_SQ+' - ')[-1].split('MHz')[0])
                        rel_change = math.sqrt( (min_r2_frq - set_r2_frq)**2/(min_r2_frq)**2 )
                        print("%s %s %s %s %.1f GRID=%.3f MIN=%.3f SET=%.3f RELC=%.3f"%(cur_spin.model, res_name, cur_spin_id, mo_param, frq, grid_r2_frq, min_r2_frq, set_r2_frq, rel_change) )
                        if rel_change > ds.rel_change:
                            print("WARNING: rel change level is above %.2f, and is %.4f."%(ds.rel_change, rel_change))
                            print("###################################")

                        ## Make test on R2.
                        self.assertAlmostEqual(set_r2_frq, min_r2_frq, 2)
                else:
                    grid_val = grid_params[mo_param]
                    min_val = min_params[mo_param]
                    set_val = params[mo_param]
                    rel_change = math.sqrt( (min_val - set_val)**2/(min_val)**2 )
                    print("%s %s %s %s GRID=%.3f MIN=%.3f SET=%.3f RELC=%.3f"%(cur_spin.model, res_name, cur_spin_id, mo_param, grid_val, min_val, set_val, rel_change) )
                    if rel_change > ds.rel_change:
                        print("WARNING: rel change level is above %.2f, and is %.4f."%(ds.rel_change, rel_change))
                        print("###################################")

                    ## Make test on parameters.
                    if mo_param == 'dw':
                        self.assertAlmostEqual(set_val/10, min_val/10, 5)
                    elif mo_param == 'kex':
                        self.assertAlmostEqual(set_val/1000, min_val/1000, 5)
                    elif mo_param == 'pA':
                        self.assertAlmostEqual(set_val, min_val, 6)


    def test_cpmg_synthetic_ns3d_to_cr72_noise_cluster(self):
        """Test synthetic cpmg data. For CR72 with small noise and cluster.

        This script will produce synthetic CPMG R2eff values according to the selected model, and the fit the selected model.
        """

        # Reset.
        #self.interpreter.reset()

        ## Set Experiments.
        model_create = 'NS CPMG 2-site 3D'
        #model_create = 'NS CPMG 2-site expanded'
        model_analyse = 'CR72'

        # Exp 1
        sfrq_1 = 599.8908617*1E6
        r20_key_1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_1)
        time_T2_1 = 0.06
        ncycs_1 = [2, 4, 8, 10, 20, 30, 40, 60]
        r2eff_errs_1 = [0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05]
        #r2eff_errs_1 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        exp_1 = [sfrq_1, time_T2_1, ncycs_1, r2eff_errs_1]

        sfrq_2 = 499.8908617*1E6
        r20_key_2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_2)
        time_T2_2 = 0.05
        ncycs_2 = [2, 4, 8, 10, 30, 35, 40, 50]
        r2eff_errs_2 = [0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05]
        #r2eff_errs_2 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        exp_2 = [sfrq_2, time_T2_2, ncycs_2, r2eff_errs_2]

        # Collect all exps
        exps = [exp_1, exp_2]

        spins = [
            ['Ala', 1, 'N', {'r2': {r20_key_1:10., r20_key_2:11.5}, 'r2a': {r20_key_1:10., r20_key_2:11.5}, 'r2b': {r20_key_1:10., r20_key_2:11.5}, 'kex': 1000., 'pA': 0.99, 'dw': 2.} ],
            ['Ala', 2, 'N', {'r2': {r20_key_1:13., r20_key_2:14.5}, 'r2a': {r20_key_1:13., r20_key_2:14.5}, 'r2b': {r20_key_1:13., r20_key_2:14.5}, 'kex': 1000., 'pA': 0.99, 'dw': 1.} ]
            ]

        # Collect the data to be used.
        ds.data = [model_create, model_analyse, spins, exps]

        # The tmp directory. None is the local directory.
        ds.tmpdir = ds.tmpdir

        # The results directory. None is the local directory.
        #ds.resdir = None
        ds.resdir = ds.tmpdir

        # Do r20_from_min_r2eff ?.
        ds.r20_from_min_r2eff = True

        # Remove insignificant level.
        ds.insignificance = 0.0

        # The grid search size (the number of increments per dimension).
        ds.GRID_INC = 13

        # The do clustering.
        ds.do_cluster = True

        # The function tolerance.  This is used to terminate minimisation once the function value between iterations is less than the tolerance.
        # The default value is 1e-25.
        ds.set_func_tol = 1e-8

        # The maximum number of iterations.
        # The default value is 1e7.
        ds.set_max_iter = 10000

        # The verbosity level.
        ds.verbosity = 1

        # The rel_change WARNING level.
        ds.rel_change = 0.05

        # The plot_curves.
        ds.plot_curves = False

        # The conversion for ShereKhan at http://sherekhan.bionmr.org/.
        ds.sherekhan_input = False

        # Make a dx map to be opened om OpenDX. To map the hypersurface of chi2, when altering kex, dw and pA.
        ds.opendx = False

        # The set r2eff err.
        ds.r2eff_err = 0.1

        # The print result info.
        ds.print_res = False

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'cpmg_synthetic.py')

        cur_spins = ds.data[2]
        # Compare results.
        for i in range(len(cur_spins)):
            res_name, res_num, spin_name, params = cur_spins[i]
            cur_spin_id = ":%i@%s"%(res_num, spin_name)
            cur_spin = return_spin(cur_spin_id)

            grid_params = ds.grid_results[i][3]

            # Extract the clust results.
            min_params = ds.clust_results[i][3]
            # Now read the parameters.
            print("For spin: '%s'"%cur_spin_id)
            for mo_param in cur_spin.params:
                # The R2 is a dictionary, depending on spectrometer frequency.
                if isinstance(getattr(cur_spin, mo_param), dict):
                    grid_r2 = grid_params[mo_param]
                    min_r2 = min_params[mo_param]
                    set_r2 = params[mo_param]
                    for key, val in set_r2.items():
                        grid_r2_frq = grid_r2[key]
                        min_r2_frq = min_r2[key]
                        set_r2_frq = set_r2[key]
                        frq = float(key.split(EXP_TYPE_CPMG_SQ+' - ')[-1].split('MHz')[0])
                        rel_change = math.sqrt( (min_r2_frq - set_r2_frq)**2/(min_r2_frq)**2 )
                        print("%s %s %s %s %.1f GRID=%.3f MIN=%.3f SET=%.3f RELC=%.3f"%(cur_spin.model, res_name, cur_spin_id, mo_param, frq, grid_r2_frq, min_r2_frq, set_r2_frq, rel_change) )
                        if rel_change > ds.rel_change:
                            print("WARNING: rel change level is above %.2f, and is %.4f."%(ds.rel_change, rel_change))
                            print("###################################")

                        ## Make test on R2.
                        self.assertAlmostEqual(set_r2_frq, min_r2_frq, 1)
                else:
                    grid_val = grid_params[mo_param]
                    min_val = min_params[mo_param]
                    set_val = params[mo_param]
                    rel_change = math.sqrt( (min_val - set_val)**2/(min_val)**2 )
                    print("%s %s %s %s GRID=%.3f MIN=%.3f SET=%.3f RELC=%.3f"%(cur_spin.model, res_name, cur_spin_id, mo_param, grid_val, min_val, set_val, rel_change) )
                    if rel_change > ds.rel_change:
                        print("WARNING: rel change level is above %.2f, and is %.4f."%(ds.rel_change, rel_change))
                        print("###################################")

                    ## Make test on parameters.
                    if mo_param == 'dw':
                        self.assertAlmostEqual(set_val/10, min_val/10, 1)
                    elif mo_param == 'kex':
                        self.assertAlmostEqual(set_val/1000, min_val/1000, 1)
                    elif mo_param == 'pA':
                        self.assertAlmostEqual(set_val, min_val, 2)


    def test_cpmg_synthetic_dx_map_points(self):
        """Test synthetic cpmg data, calling the dx.map function with one or two points.

        This script will produce synthetic CPMG R2eff values according to the selected model, and the fit the selected model.
        """

        # Reset.
        #self.interpreter.reset()

        ## Set Experiments.
        model_create = MODEL_NS_CPMG_2SITE_EXPANDED
        model_analyse = 'CR72'
        # Exp 1
        sfrq_1 = 599.8908617*1E6
        r20_key_1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_1)
        time_T2_1 = 0.06
        ncycs_1 = [2, 4, 8, 10, 20, 30, 40, 60]
        r2eff_err_1 = [0, 0, 0, 0, 0, 0, 0, 0]
        exp_1 = [sfrq_1, time_T2_1, ncycs_1, r2eff_err_1]

        sfrq_2 = 499.8908617*1E6
        r20_key_2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_2)
        time_T2_2 = 0.05
        ncycs_2 = [2, 4, 8, 10, 30, 35, 40, 50]
        r2eff_err_2 = [0, 0, 0, 0, 0, 0, 0, 0]
        exp_2 = [sfrq_2, time_T2_2, ncycs_2, r2eff_err_2]

        # Collect all exps
        exps = [exp_1, exp_2]

        spins = [
            ['Ala', 1, 'N', {'r2': {r20_key_1:2, r20_key_2:2}, 'r2a': {r20_key_1:2, r20_key_2:2}, 'r2b': {r20_key_1:2, r20_key_2:2}, 'kex': 1000, 'pA': 0.99, 'dw': 2} ]
            ]

        # Collect the data to be used.
        ds.data = [model_create, model_analyse, spins, exps]

        # The tmp directory. None is the local directory.
        ds.tmpdir = ds.tmpdir

        # The results directory. None is the local directory.
        #ds.resdir = None
        ds.resdir = ds.tmpdir

        # Do r20_from_min_r2eff ?.
        ds.r20_from_min_r2eff = True

        # Remove insignificant level.
        ds.insignificance = 0.0

        # The grid search size (the number of increments per dimension).
        ds.GRID_INC = None

        # The do clustering.
        ds.do_cluster = False

        # The function tolerance.  This is used to terminate minimisation once the function value between iterations is less than the tolerance.
        # The default value is 1e-25.
        ds.set_func_tol = 1e-9

        # The maximum number of iterations.
        # The default value is 1e7.
        ds.set_max_iter = 1000

        # The verbosity level.
        ds.verbosity = 1

        # The rel_change WARNING level.
        ds.rel_change = 0.05

        # The plot_curves.
        ds.plot_curves = False

        # The conversion for ShereKhan at http://sherekhan.bionmr.org/.
        ds.sherekhan_input = False

        # Make a dx map to be opened om OpenDX. To map the hypersurface of chi2, when altering kex, dw and pA.
        ds.opendx = False

        # The set r2eff err.
        ds.r2eff_err = 0.1

        # The print result info.
        ds.print_res = False

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'cpmg_synthetic.py')

        # Get the spins.
        cur_spins = ds.data[2]

        # First switch pipe, since dx.map will go through parameters and end up a "bad" place. :-)
        ds.pipe_name_MODEL_MAP = "%s_%s_map"%(ds.pipe_name, model_analyse)
        self.interpreter.pipe.copy(pipe_from=ds.pipe_name, pipe_to=ds.pipe_name_MODEL_MAP, bundle_to = ds.pipe_bundle)
        self.interpreter.pipe.switch(pipe_name=ds.pipe_name_MODEL_MAP)

        # Copy R2eff, but not the original parameters
        self.interpreter.value.copy(pipe_from=ds.pipe_name_r2eff, pipe_to=ds.pipe_name_MODEL_MAP, param='r2eff')

        # Then select model.
        self.interpreter.relax_disp.select_model(model=model_analyse)

        # Define dx.map settings.
        ds.dx_inc = 4
        ds.dx_params = ['dw', 'pA', 'kex']

        res_name, res_num, spin_name, params = cur_spins[0]
        cur_spin_id = ":%i@%s"%(res_num, spin_name)
        cur_spin = return_spin(cur_spin_id)

        print("Params for dx map is")
        print(ds.dx_params)
        print("Point param for dx map is")
        print(ds.dx_set_val)
        cur_model = model_analyse.replace(' ', '_')
        file_name_map = "%s_map%s" % (cur_model, cur_spin_id.replace('#', '_').replace(':', '_').replace('@', '_'))
        file_name_point = "%s_point%s" % (cur_model, cur_spin_id .replace('#', '_').replace(':', '_').replace('@', '_'))
        self.interpreter.dx.map(params=ds.dx_params, map_type='Iso3D', spin_id=cur_spin_id, inc=ds.dx_inc, lower=None, upper=None, axis_incs=10, file_prefix=file_name_map, dir=ds.resdir, point=[ds.dx_set_val, ds.dx_clust_val], point_file=file_name_point)

        ## Check for file creation
        # Set filepaths.
        map_cfg = ds.tmpdir+sep+file_name_map+".cfg"
        map_net = ds.tmpdir+sep+file_name_map+".net"
        map_general = ds.tmpdir+sep+file_name_map+".general"

        point_general = ds.tmpdir+sep+file_name_point+".general"
        point_point = ds.tmpdir+sep+file_name_point

        # Test the files exists.
        self.assert_(access(map_cfg, F_OK))
        self.assert_(access(map_net, F_OK))
        self.assert_(access(map_general, F_OK))
        self.assert_(access(point_general, F_OK))
        self.assert_(access(point_point, F_OK))

        # Open the files for testing.
        # Check the cfg file.
        print("\nChecking the dx map .cfg file.")
        res_file = [
            '//'+"\n",
            '//'+"\n",
            '// time: Thu May  8 18:55:31 2014'+"\n",
            '//'+"\n",
            '// version: 3.2.0 (format), 4.3.2 (DX)'+"\n",
            '//'+"\n",
            '//'+"\n",
            '// panel[0]: position = (0.0164,0.0000), size = 0.2521x0.1933, startup = 1, devstyle = 1'+"\n",
            '// title: value = Control Panel'+"\n",
            '//'+"\n",
            '// workspace: width = 251, height = 142'+"\n",
            '// layout: snap = 0, width = 50, height = 50, align = NN'+"\n",
            '//'+"\n",
            '// interactor Selector[1]: num_components = 1, value = 1 '+"\n",
            '// selections: maximum = 2, current = 0 '+"\n",
            '// option[0]: name = "Colour", value = 1'+"\n",
            '// option[1]: name = "Grey", value = 2'+"\n",
            '// instance: panel = 0, x = 81, y = 6, style = Scrolled List, vertical = 1, size = 170x136'+"\n",
            '// label: value = Colour Selector'+"\n",
            '//'+"\n",
            '// node Image[3]:'+"\n",
            '// title: value = Surface'+"\n",
            '// depth: value = 24'+"\n",
            '// window: position = (0.0000,0.0400), size = 0.9929x0.9276'+"\n",
        ]
        file = open(map_cfg, 'r')
        lines = file.readlines()
        file.close()
        for i in range(len(res_file)):
            # Skip time point
            if i == 2:
                continue
            self.assertEqual(res_file[i], lines[i])

        print("\nChecking the dx map .general file.")
        res_file = [
            'file = CR72_map_1_N'+"\n",
            'grid = 5 x 5 x 5'+"\n",
            'format = ascii'+"\n",
            'interleaving = field'+"\n",
            'majority = row'+"\n",
            'field = data'+"\n",
            'structure = scalar'+"\n",
            'type = float'+"\n",
            'dependency = positions'+"\n",
            'positions = regular, regular, regular, 0, 1, 0, 1, 0, 1'+"\n",
            ''+"\n",
            'end'+"\n",
        ]
        file = open(map_general, 'r')
        lines = file.readlines()
        file.close()
        for i in range(len(res_file)):
            # Skip time point
            #if i == 2:
            #    continue
            self.assertEqual(res_file[i], lines[i])

        print("\nChecking the dx point .general file.")
        res_file = [
            'file = CR72_point_1_N'+"\n",
            'points = 2'+"\n",
            'format = ascii'+"\n",
            'interleaving = field'+"\n",
            'field = locations, field0'+"\n",
            'structure = 3-vector, scalar'+"\n",
            'type = float, float'+"\n",
            ''+"\n",
            'end'+"\n",
        ]
        file = open(point_general, 'r')
        lines = file.readlines()
        file.close()
        for i in range(len(res_file)):
            # Skip time point
            #if i == 2:
            #    continue
            self.assertEqual(res_file[i], lines[i])

        print("\nChecking the dx point point file.")
        res_file = [
            '0.8            3.92           0.39964        1'+"\n",
            '0.76981        3.9169         0.41353        1'+"\n",
        ]
        file = open(point_point, 'r')
        lines = file.readlines()
        file.close()
        for i in range(len(res_file)):
            # Skip time point
            #if i == 2:
            #    continue
            self.assertEqual(res_file[i], lines[i])


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
        self.interpreter.pipe.switch('DPL94 - relax_disp')
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


    def test_estimate_r2eff_err(self):
        """Test the user function for estimating R2eff errors from exponential curve fitting.

        This follows Task 7822.
        U{task #7822<https://gna.org/task/index.php?7822>}: Implement user function to estimate R2eff and associated errors for exponential curve fitting.

        This uses the data from Kjaergaard's paper at U{DOI: 10.1021/bi4001062<http://dx.doi.org/10.1021/bi4001062>}.
        Optimisation of the Kjaergaard et al., 2013 Off-resonance R1rho relaxation dispersion experiments using the 'DPL' model.
        """

        # Cluster residues
        cluster_ids = [
        ":13@N",
        ":15@N",
        ":16@N",
        ":25@N",
        ":26@N",
        ":28@N",
        ":39@N",
        ":40@N",
        ":41@N",
        ":43@N",
        ":44@N",
        ":45@N",
        ":49@N",
        ":52@N",
        ":53@N"]

        # Load the data.
        self.setup_r1rho_kjaergaard(cluster_ids=cluster_ids, read_R1=False)

        # The dispersion models.
        MODELS = [MODEL_NOREX, MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MP05, MODEL_NS_R1RHO_2SITE]

        # The grid search size (the number of increments per dimension).
        GRID_INC = None

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        MC_NUM = 3

        # Model selection technique.
        MODSEL = 'AIC'

        # Execute the auto-analysis (fast).
        # Standard parameters are: func_tol = 1e-25, grad_tol = None, max_iter = 10000000,
        OPT_FUNC_TOL = 1e-25
        relax_disp.Relax_disp.opt_func_tol = OPT_FUNC_TOL
        OPT_MAX_ITERATIONS = 10000000
        relax_disp.Relax_disp.opt_max_iterations = OPT_MAX_ITERATIONS

        result_dir_name = ds.tmpdir

        # Make all spins free
        for curspin in cluster_ids:
            self.interpreter.relax_disp.cluster('free spins', curspin)
            # Shut them down
            self.interpreter.deselect.spin(spin_id=curspin, change_all=False)

        # Select only a subset of spins for global fitting
        #self.interpreter.select.spin(spin_id=':41@N', change_all=False)
        #self.interpreter.relax_disp.cluster('model_cluster', ':41@N')

        #self.interpreter.select.spin(spin_id=':40@N', change_all=False)
        #self.interpreter.relax_disp.cluster('model_cluster', ':40@N')

        self.interpreter.select.spin(spin_id=':52@N', change_all=False)
        #self.interpreter.relax_disp.cluster('model_cluster', ':52@N')

        # Set the model.
        self.interpreter.relax_disp.select_model(MODEL_R2EFF)

        # Check if intensity errors have already been calculated.
        check_intensity_errors()

        # Do a grid search.
        self.interpreter.minimise.grid_search(lower=None, upper=None, inc=11, constraints=True, verbosity=1)

        # Minimise.
        self.interpreter.minimise.execute(min_algor='Newton', constraints=False, verbosity=1)

        # Estimate R2eff errors.
        self.interpreter.relax_disp.r2eff_err_estimate()

        # Run the analysis.
        relax_disp.Relax_disp(pipe_name=ds.pipe_name, pipe_bundle=ds.pipe_bundle, results_dir=result_dir_name, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL)

        # Verify the data.
        self.verify_r1rho_kjaergaard_missing_r1(models=MODELS, result_dir_name=result_dir_name, do_assert=False)


    def test_estimate_r2eff_err_methods(self):
        """Test the user function for estimating R2eff and associated errors for exponential curve fitting with different methods.
        This is compared with a run where erros are estimated by 2000 Monte Carlo simulations.

        This follows Task 7822.
        U{task #7822<https://gna.org/task/index.php?7822>}: Implement user function to estimate R2eff and associated errors for exponential curve fitting.

        This uses the data from Kjaergaard's paper at U{DOI: 10.1021/bi4001062<http://dx.doi.org/10.1021/bi4001062>}.
        Optimisation of the Kjaergaard et al., 2013 Off-resonance R1rho relaxation dispersion experiments using the 'DPL' model.
        """

        # Define data path.
        prev_data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013' +sep+ "check_graphs" +sep+ "mc_2000"  +sep+ "R2eff"

        # Create pipe.
        self.interpreter.pipe.create('MC_2000', 'relax_disp')

        # Read results for 2000 MC simulations.
        self.interpreter.results.read(prev_data_path + sep + 'results')

        # Start dic.
        my_dic = {}
        param_key_list = []

        for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            # Add key to dic.
            my_dic[spin_id] = {}

            # Generate spin string.
            spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

            for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
                # Generate the param_key.
                param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

                # Append key.
                param_key_list.append(param_key)

                # Add key to dic.
                my_dic[spin_id][param_key] = {}

                # Get the value.
                r2eff = getattr(cur_spin, 'r2eff')[param_key]
                r2eff_err = getattr(cur_spin, 'r2eff_err')[param_key]
                i0 = getattr(cur_spin, 'i0')[param_key]
                i0_err = getattr(cur_spin, 'i0_err')[param_key]

                # Save to dic.
                my_dic[spin_id][param_key]['r2eff'] = r2eff
                my_dic[spin_id][param_key]['r2eff_err'] = r2eff_err
                my_dic[spin_id][param_key]['i0'] = i0
                my_dic[spin_id][param_key]['i0_err'] = i0_err

        # A new data pipe.
        self.interpreter.pipe.copy(pipe_from='MC_2000', pipe_to='r2eff_est')
        self.interpreter.pipe.switch(pipe_name='r2eff_est')

        # Delete old errors.
        for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            delattr(cur_spin, 'r2eff_err')
            delattr(cur_spin, 'i0_err')

        # Set the model.
        self.interpreter.relax_disp.select_model(MODEL_R2EFF)

        # Estimate R2eff and errors.
        self.interpreter.relax_disp.r2eff_err_estimate(verbosity=0)

        for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            # Generate spin string.
            spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

            for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
                # Generate the param_key.
                param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

                # Get the value.
                r2eff_est = getattr(cur_spin, 'r2eff')[param_key]
                r2eff_err_est = getattr(cur_spin, 'r2eff_err')[param_key]
                i0_est = getattr(cur_spin, 'i0')[param_key]
                i0_err_est = getattr(cur_spin, 'i0_err')[param_key]

                # Get from dic.
                r2eff = my_dic[spin_id][param_key]['r2eff']
                r2eff_err = my_dic[spin_id][param_key]['r2eff_err']
                i0 = my_dic[spin_id][param_key]['i0']
                i0_err = my_dic[spin_id][param_key]['i0_err']

                print("%s at %3.1f MHz, for offset=%3.3f ppm and dispersion point %-5.1f." % (exp_type, frq/1E6, offset, point) )
                print("r2eff=%3.3f/%3.3f r2eff_err=%3.4f/%3.4f" % (r2eff, r2eff_est, r2eff_err, r2eff_err_est) ),
                print("i0=%3.3f/%3.3f i0_err=%3.4f/%3.4f\n" % (i0, i0_est, i0_err, i0_err_est) )


        # Now do it manually.
        estimate_r2eff(method='scipy.optimize.leastsq')
        estimate_r2eff(method='minfx', min_algor='simplex', c_code=True, constraints=False)
        estimate_r2eff(method='minfx', min_algor='simplex', c_code=False, constraints=False)
        estimate_r2eff(method='minfx', min_algor='BFGS', c_code=True, constraints=False)
        estimate_r2eff(method='minfx', min_algor='BFGS', c_code=False, constraints=False)
        estimate_r2eff(method='minfx', min_algor='Newton', c_code=True, constraints=False)


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
        self.interpreter.pipe.switch(pipe_name='No Rex - relax_disp')
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
        self.interpreter.pipe.switch(pipe_name='LM63 - relax_disp')
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("phi_ex", spin70.phi_ex, spin71.phi_ex))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.74326615264889, 2)
        self.assertAlmostEqual(spin70.r2[r20_key2], 6.57331164382438, 2)
        self.assertAlmostEqual(spin70.phi_ex, 0.312767653822936, 3)
        self.assertAlmostEqual(spin70.kex/10000, 4723.44390412119/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 363.534049046805, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.00778024769786, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.83343630016037, 3)
        self.assertAlmostEqual(spin71.phi_ex, 0.0553791362097596, 3)
        self.assertAlmostEqual(spin71.kex/10000, 2781.67925957068/10000, 3)
        self.assertAlmostEqual(spin71.chi2, 17.0776426190574, 3)

        # The 'CR72' model checks.
        self.interpreter.pipe.switch(pipe_name='CR72 - relax_disp')
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
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.409506394526, 2)
        self.assertAlmostEqual(spin70.pA, 0.989856804525044, 3)
        self.assertAlmostEqual(spin70.dw, 5.60889078920945, 3)
        self.assertAlmostEqual(spin70.kex/10000, 1753.01607073019/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 53.8382158551706, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.003171547206, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.90210797727492, 3)
        self.assertAlmostEqual(spin71.pA, 0.985922406455826, 3)
        self.assertAlmostEqual(spin71.dw, 2.00500965892672, 2)
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
        self.interpreter.pipe.switch(pipe_name='No Rex - relax_disp')
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
        self.interpreter.pipe.switch(pipe_name='CR72 - relax_disp')
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
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.409506394526, 2)
        self.assertAlmostEqual(spin70.pA, 0.989856804525044, 3)
        self.assertAlmostEqual(spin70.dw, 5.60889078920945, 3)
        self.assertAlmostEqual(spin70.kex/10000, 1753.01607073019/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 53.8382158551706, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.003171547206, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.90210797727492, 3)
        self.assertAlmostEqual(spin71.pA, 0.985922406455826, 3)
        self.assertAlmostEqual(spin71.dw, 2.00500965892672, 2)
        self.assertAlmostEqual(spin71.kex/10000, 2481.10839579617/10000, 3)
        self.assertAlmostEqual(spin71.chi2, 15.6595374286822, 3)

        # The 'NS CPMG 2-site expanded' model checks.
        self.interpreter.pipe.switch(pipe_name='NS CPMG 2-site expanded - relax_disp')
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
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.95815351460902, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.39649535771294, 3)
        self.assertAlmostEqual(spin70.pA, 0.989701014493195, 3)
        self.assertAlmostEqual(spin70.dw, 5.67314464776128, 3)
        self.assertAlmostEqual(spin70.kex/10000, 1713.65380495429/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 52.5106880917473, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 4.99889337382435, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.89822887466673, 3)
        self.assertAlmostEqual(spin71.pA, 0.986709050819695, 3)
        self.assertAlmostEqual(spin71.dw, 2.09238266766502, 2)
        self.assertAlmostEqual(spin71.kex/10000, 2438.27019901422/10000, 3)
        self.assertAlmostEqual(spin71.chi2, 15.1644906963987, 3)

        # The final data pipe checks.
        self.interpreter.pipe.switch(pipe_name='final - relax_disp')
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
        self.interpreter.pipe.switch(pipe_name='No Rex - relax_disp')
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
        self.interpreter.pipe.switch(pipe_name='LM63 - relax_disp')
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("phi_ex", spin70.phi_ex, spin71.phi_ex))
        print("%-20s %20.15g %20.15g" % ("kex", spin70.kex, spin71.kex))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.74326615264889, 2)
        self.assertAlmostEqual(spin70.r2[r20_key2], 6.57331164382438, 2)
        self.assertAlmostEqual(spin70.phi_ex, 0.312767653822936, 3)
        self.assertAlmostEqual(spin70.kex/10000, 4723.44390412119/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 363.534049046805, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.00778024769786, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.83343630016037, 3)
        self.assertAlmostEqual(spin71.phi_ex, 0.0553791362097596, 3)
        self.assertAlmostEqual(spin71.kex/10000, 2781.67925957068/10000, 3)
        self.assertAlmostEqual(spin71.chi2, 17.0776426190574, 3)

        # The 'CR72' model checks.
        self.interpreter.pipe.switch(pipe_name='CR72 - relax_disp')
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
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.409506394526, 2)
        self.assertAlmostEqual(spin70.pA, 0.989856804525044, 3)
        self.assertAlmostEqual(spin70.dw, 5.60889078920945, 3)
        self.assertAlmostEqual(spin70.kex/10000, 1753.01607073019/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 53.8382158551706, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.00317154730225, 3)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.90210797713541, 3)
        self.assertAlmostEqual(spin71.pA, 0.985922406429147, 3)
        self.assertAlmostEqual(spin71.dw, 2.00500965887772, 2)
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
        self.interpreter.pipe.switch(pipe_name='No Rex - relax_disp')
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
        self.assertAlmostEqual(spin4.chi2, 26.7356700694891, 3)
        self.assertAlmostEqual(spin70.r2[r20_key1], 10.534285641325, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 16.1112794857068, 3)
        self.assertAlmostEqual(spin70.chi2, 8973.84809774722, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.83136858890037, 3)
        self.assertAlmostEqual(spin71.chi2, 182.60081909193, 3)

        # The 'CR72' model checks.
        self.interpreter.pipe.switch(pipe_name='CR72 - relax_disp')
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
        self.assertAlmostEqual(spin4.r2[r20_key1], 1.60463650370664, 2)
        self.assertAlmostEqual(spin4.r2[r20_key2], 1.63221675941434, 3)
        #self.assertAlmostEqual(spin4.pA, 0.818979078699935, 3)    # As dw (and kex) is zero, this parameter is not stable.
        self.assertAlmostEqual(spin4.dw, 0.0, 5)
        self.assertAlmostEqual(spin4.kex/10000, 0.0, 3)
        self.assertAlmostEqual(spin4.chi2/100, 26.7356711142038/100, 3)
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.97268077496405, 3)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.41028133407727, 3)
        self.assertAlmostEqual(spin70.pA, 0.989856641885939, 3)
        self.assertAlmostEqual(spin70.dw, 5.60889911049405, 3)
        self.assertAlmostEqual(spin70.kex/10000, 1752.62025618632/10000, 3)
        self.assertAlmostEqual(spin70.chi2, 53.8382196964083, 3)
        self.assertAlmostEqual(spin71.r2[r20_key1], 4.98123328466942, 3)
        self.assertAlmostEqual(spin71.pA, 0.996607425484157, 3)
        self.assertAlmostEqual(spin71.dw, 4.34346257383825, 3)
        self.assertAlmostEqual(spin71.kex/10000, 1936.73197158804/10000, 3)
        self.assertAlmostEqual(spin71.chi2, 5.51703791653689, 3)


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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

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
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.9724581325007, 4)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.40968331038162, 2)
        self.assertAlmostEqual(spin70.pA, 0.989856656702431, 4)
        self.assertAlmostEqual(spin70.dw, 5.60885879594746, 3)
        self.assertAlmostEqual(spin70.kex/1000, 1752.91052702273/1000, 3)
        self.assertAlmostEqual(spin70.chi2, 53.8382133597495, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.0030740940524, 4)
        self.assertAlmostEqual(spin71.pA, 0.985941082507823, 4)
        self.assertAlmostEqual(spin71.dw, 2.00640384113696, 4)
        self.assertAlmostEqual(spin71.kex/1000, 2480.79614442041/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 15.6595388312451, 4)

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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

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
        self.assertAlmostEqual(spin70.r2a[r20_key1], 6.87485258365614, 4)
        self.assertAlmostEqual(spin70.r2b[r20_key1], 1.26075839074614, 4)
        self.assertAlmostEqual(spin70.r2a[r20_key2], 8.79580446260797, 4)
        self.assertAlmostEqual(spin70.r2b[r20_key2], 51.188411562843, 4)
        self.assertAlmostEqual(spin70.pA, 0.989384178573802, 4)
        self.assertAlmostEqual(spin70.dw, 5.54738203723682, 4)
        self.assertAlmostEqual(spin70.kex/1000, 1831.4566463179/1000, 4)
        self.assertAlmostEqual(spin70.chi2, 50.450410782403, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2a[r20_key1], 5.04185695754972, 4)
        self.assertAlmostEqual(spin71.r2b[r20_key1], 1.62857899941921, 4)
        self.assertAlmostEqual(spin71.pA, 0.988832866751676, 4)
        self.assertAlmostEqual(spin71.dw, 2.24905251856265, 4)
        self.assertAlmostEqual(spin71.kex/1000, 2397.64122642946/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 15.8586492923672, 4)

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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-10, grad_tol=None, max_iter=10000, constraints=True, scaling=True, verbosity=1)

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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-25, grad_tol=None, max_iter=10000000, constraints=True, scaling=True, verbosity=1)

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
        self.assertAlmostEqual(spin70.r2[r20_key2], 6.57406797067481, 6)
        self.assertAlmostEqual(spin70.phi_ex, 0.312733013751449)
        self.assertAlmostEqual(spin70.kex/1000, 4723.09897146338/1000, 6)
        self.assertAlmostEqual(spin70.chi2, 363.534044873483)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[r20_key1], 5.00776657729728, 5)
        self.assertAlmostEqual(spin71.phi_ex, 0.0553787825650613, 5)
        self.assertAlmostEqual(spin71.kex/1000, 2781.72292994154/1000, 5)
        self.assertAlmostEqual(spin71.chi2, 17.0776399916287, 5)


    def test_hansen_cpmg_data_to_lm63_3site(self):
        """Optimisation of Dr. Flemming Hansen's CPMG data to the LM63 dispersion model.

        This uses the data from Dr. Flemming Hansen's paper at http://dx.doi.org/10.1021/jp074793o.  This is CPMG data with a fixed relaxation time period.
        """

        # Base data setup.
        self.setup_hansen_cpmg_data(model='LM63 3-site')

        # Alias the spins.
        spin70 = return_spin(":70")
        spin71 = return_spin(":71")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        ## Set the initial parameter values.
        spin70.r2 = {r20_key1: 7.570370921220954, r20_key2: 8.694446951909107}
        spin70.phi_ex_B = 0.14872003058250227
        spin70.phi_ex_C = 0.1319419923472704
        spin70.kB = 4103.672910444741
        spin70.kC = 7029.001690726248
        spin71.r2 = {r20_key1: 5.1347793381636, r20_key2: 7.156573986051575}
        spin71.phi_ex_B = 0.04013553485505605
        spin71.phi_ex_C = 0.020050748406928887
        spin71.kB = 4045.3007136121364
        spin71.kC = 3586.38798270774

        #self.interpreter.relax_disp.r20_from_min_r2eff(force=False)
        #self.interpreter.minimise.grid_search(lower=None, upper=None, inc=41, constraints=True, verbosity=1)

        # Low precision optimisation.
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-25, grad_tol=None, max_iter=10000000, constraints=True, scaling=True, verbosity=1)

        # Printout.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:70)", "Value (:71)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin70.r2[r20_key1], spin71.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin70.r2[r20_key2], spin71.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("phi_ex_B", spin70.phi_ex_B, spin71.phi_ex_B))
        print("%-20s %20.15g %20.15g" % ("phi_ex_C", spin70.phi_ex_C, spin71.phi_ex_C))
        print("%-20s %20.15g %20.15g" % ("kB", spin70.kB, spin71.kB))
        print("%-20s %20.15g %20.15g" % ("kC", spin70.kC, spin71.kC))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin70.chi2, spin71.chi2))

        # Checks for residue :70.
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.7436230253685, 5)
        self.assertAlmostEqual(spin70.r2[r20_key2], 6.57406813008828, 6)
        self.assertAlmostEqual(spin70.phi_ex_B, 0.206304023079778, 5)
        self.assertAlmostEqual(spin70.phi_ex_C, 0.106428983339627, 5)
        self.assertAlmostEqual(spin70.kB/1000, 4723.09897652589/1000, 6)
        self.assertAlmostEqual(spin70.kC/1000, 4723.09876196409/1000, 6)
        self.assertAlmostEqual(spin70.chi2, 363.534044873483, 5)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[r20_key1], 4.96612095596752, 5)
        self.assertAlmostEqual(spin71.phi_ex_B, 0.00398262266512895, 5)
        self.assertAlmostEqual(spin71.phi_ex_C, 0.0555791581291262, 5)
        self.assertAlmostEqual(spin71.kB/1000, 1323.33195689832/1000, 5)
        self.assertAlmostEqual(spin71.kC/1000, 3149.58971568059/1000, 5)
        self.assertAlmostEqual(spin71.chi2, 16.2620934464368)


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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=False, scaling=True, verbosity=1)

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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=False, scaling=True, verbosity=1)

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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

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
        self.assertAlmostEqual(spin70.r2[r20_key1], 6.95813330991529, 4)
        self.assertAlmostEqual(spin70.r2[r20_key2], 9.39663480561524, 4)
        self.assertAlmostEqual(spin70.pA, 0.989700843879574, 4)
        self.assertAlmostEqual(spin70.dw, 5.67315878825691, 4)
        self.assertAlmostEqual(spin70.kex/1000, 1713.56110716632/1000, 4)
        self.assertAlmostEqual(spin70.chi2, 52.5106879242812, 4)

        # Checks for residue :71.
        self.assertAlmostEqual(spin71.r2[r20_key1], 4.99881666793312, 4)
        self.assertAlmostEqual(spin71.r2[r20_key2], 6.89817482453042, 4)
        self.assertAlmostEqual(spin71.pA, 0.986712911453639, 4)
        self.assertAlmostEqual(spin71.dw, 2.09273069372236, 4)
        self.assertAlmostEqual(spin71.kex/1000, 2438.20525930405/1000, 4)
        self.assertAlmostEqual(spin71.chi2, 15.1644913030633, 4)

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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=False, scaling=True, verbosity=1)

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
        self.assertAlmostEqual(spin71.pA, 0.986716058519642, 2)
        self.assertAlmostEqual(spin71.dw/100, 2.09292495350993/100, 2)
        self.assertAlmostEqual(spin71.kex/100000, 2438.04423541463/100000, 2)
        self.assertAlmostEqual(spin71.chi2/100, 15.1644902423334/100, 1)

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
        self.interpreter.minimise.calculate()

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
        for i in range(len(spin1)):
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
        for i in range(len(spin2)):
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
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=1e-05, max_iter=1000)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise.execute(min_algor='simplex', max_iter=10)
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
        self.assertAlmostEqual(spin.r2[r20_key2], 11.7135951595536, 2)
        self.assertAlmostEqual(spin.r2[r20_key3], 13.6153887849344, 2)
        self.assertAlmostEqual(spin.pA, 0.965638501551899, 4)
        self.assertAlmostEqual(spin.dw, 2.8537583461577, 1)
        self.assertAlmostEqual(spin.dwH, -0.387633062766635, 2)
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
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=1e-05, max_iter=1000)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise.execute(min_algor='simplex', max_iter=10)
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
        self.assertAlmostEqual(spin.chi2, 10.3654315659173, 2)


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
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=1e-05, max_iter=1000)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise.execute(min_algor='simplex', max_iter=10)
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
        self.assertAlmostEqual(spin.r2[r20_key1], 8.334232330326190, 2)
        self.assertAlmostEqual(spin.r2[r20_key2], 8.756773997879968, 2)
        self.assertAlmostEqual(spin.r2[r20_key3], 10.219320492033058, 1)
        self.assertAlmostEqual(spin.pA, 0.950310172115387, 3)
        self.assertAlmostEqual(spin.dw, 4.356737157889636, 2)
        self.assertAlmostEqual(spin.kex/1000, 433.176323890829849/1000, 2)
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
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=1e-05, max_iter=1000)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise.execute(min_algor='simplex', max_iter=10)
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
        self.assertAlmostEqual(spin.dwH, 0.0881272284455416, 2)
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
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=1e-05, max_iter=100)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise.execute(min_algor='simplex', max_iter=10)
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
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=1e-05, max_iter=1000)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise.execute(min_algor='simplex', max_iter=10)
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
        self.assertAlmostEqual(spin.dwH, -0.265308128403529, 3)
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
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=1e-05, max_iter=10)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=2)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise.execute(min_algor='simplex', max_iter=10)
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


    def test_korzhnev_2005_all_data_disp_speed_bug(self):
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

        # Calc the chi2 values at these parameters.
        self.interpreter.minimise.calculate(verbosity=1)

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
        self.assertAlmostEqual(spin.chi2/1000, 162.511988511609/1000, 3)


    def test_kteilum_fmpoulsen_makke_check_graphs(self):
        """Check of all possible dispersion graphs from optimisation of Kaare Teilum, Flemming M Poulsen, Mikael Akke 2006 "acyl-CoA binding protein" CPMG data to the CR72 dispersion model.

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
        model = 'TSMFK01'
        expfolder = "acbp_cpmg_disp_048MGuHCl_40C_041223"
        self.setup_kteilum_fmpoulsen_makke_cpmg_data(model=model, expfolder=expfolder)

        # Alias the spins.
        res61L = cdp.mol[0].res[0].spin[0]

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=599.89086220e6)

        # Set the initial parameter values.
        res61L.r2a = {r20_key1: 8.0}
        res61L.dw = 6.5
        res61L.k_AB = 2.5

        # Low precision optimisation.
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Start testing all possible combinations of graphs.
        y_axis_types = [Y_AXIS_R2_EFF, Y_AXIS_R2_R1RHO]
        x_axis_types = [X_AXIS_DISP, X_AXIS_THETA, X_AXIS_W_EFF]
        interpolate_types = [INTERPOLATE_DISP]

        # Write to temp folder.
        result_dir_name = ds.tmpdir
        result_folders = [model]
        spin_id = ":61@N"

        # Loop through all possible combinations of y_axis, x_axis and interpolation.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'KTeilum_FMPoulsen_MAkke_2006'+sep+expfolder+sep+'check_graphs'

        for result_folder in result_folders:
            for y_axis in y_axis_types:
                for x_axis in x_axis_types:
                    for interpolate in interpolate_types:
                        # Determine file name:
                        file_name_ini = return_grace_file_name_ini(y_axis=y_axis, x_axis=x_axis, interpolate=interpolate)

                        # Make the file name.
                        file_name = "%s%s.agr" % (file_name_ini, spin_id.replace('#', '_').replace(':', '_').replace('@', '_'))

                        # Write the curves.
                        dir = result_dir_name+sep+result_folder
                        print("Plotting combination of %s, %s, %s"%(y_axis, x_axis, interpolate))
                        self.interpreter.relax_disp.plot_disp_curves(dir=dir, y_axis=y_axis, x_axis=x_axis, interpolate=interpolate, force=True)

                        # Get the file path.
                        file_path = get_file_path(file_name, dir)

                        # Test the plot file exists.
                        print("Testing file access to graph: %s"%file_path)
                        self.assert_(access(file_path, F_OK))

                        # Now open, and compare content, line by line.
                        file_prod = open(file_path)
                        lines_prod = file_prod.readlines()
                        file_prod.close()

                        # Define file to compare against.
                        dir_comp = data_path+sep+result_folder
                        file_path_comp = get_file_path(file_name, dir_comp)
                        file_comp = open(file_path_comp)
                        lines_comp = file_comp.readlines()
                        file_comp.close()

                        ## Assert number of lines is equal.
                        self.assertEqual(len(lines_prod), len(lines_comp))
                        for j in range(len(lines_prod)):
                            # Make the string test
                            first_char = lines_prod[j][0]
                            if first_char in ["@", "&"]:
                                self.assertEqual(lines_prod[j], lines_comp[j])
                            else:
                                # Split string in x, y, error.
                                # The error would change per run.
                                x_prod, y_prod, y_prod_err = lines_prod[j].split()
                                x_comp, y_comp, y_comp_err = lines_comp[j].split()
                                self.assertAlmostEqual(float(x_prod), float(x_comp))
                                self.assertAlmostEqual(float(y_prod), float(y_comp))
                                self.assertAlmostEqual(float(y_prod_err), float(y_comp_err))


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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

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


    def test_lm63_3site_synthetic(self):
        """Test the 'LM63 3-site' dispersion model using the pure noise-free synthetic data."""

        # The path to the data files.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'lm63_3site'

        # Load the state file.
        self.interpreter.reset()
        self.interpreter.state.load(data_path+sep+'r2eff_values')

        # A new data pipe.
        self.interpreter.pipe.copy(pipe_from='base pipe', pipe_to='LM63 3-site', bundle_to='relax_disp')
        self.interpreter.pipe.switch(pipe_name='LM63 3-site')

        # Set up the model data.
        self.interpreter.relax_disp.select_model(model='LM63 3-site')
        self.interpreter.value.copy(pipe_from='R2eff - relax_disp', pipe_to='LM63 3-site', param='r2eff')
        self.interpreter.spin.isotope('15N')

        # Alias the spins.
        spin1 = return_spin(":1")
        spin2 = return_spin(":2")

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

        # Manually set the parameter values.
        spin1.r2 = {r20_key1: 12.0, r20_key2: 12.0}
        spin1.phi_ex_B = 0.1
        spin1.phi_ex_C = 0.5
        spin1.kB = 1500.0
        spin1.kC = 2500.0
        spin2.r2 = {r20_key1: 15.0, r20_key2: 15.0}
        spin2.phi_ex_B = 0.1
        spin2.phi_ex_C = 0.5
        spin2.kB = 1500.0
        spin2.kC = 2500.0

        # Low precision optimisation.
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-05, grad_tol=None, max_iter=1000, constraints=True, scaling=True, verbosity=1)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=3)
        self.interpreter.monte_carlo.create_data(method='back_calc')
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-2, grad_tol=None, max_iter=10, constraints=True, scaling=True, verbosity=1)
        self.interpreter.monte_carlo.error_analysis()

        # Save the results.
        self.interpreter.results.write(file='devnull', compress_type=1, force=True)

        # The model checks.
        print("\n\nOptimised parameters:\n")
        print("%-20s %-20s %-20s" % ("Parameter", "Value (:1)", "Value (:2)"))
        print("%-20s %20.15g %20.15g" % ("R2 (500 MHz)", spin1.r2[r20_key1], spin2.r2[r20_key1]))
        print("%-20s %20.15g %20.15g" % ("R2 (800 MHz)", spin1.r2[r20_key2], spin2.r2[r20_key2]))
        print("%-20s %20.15g %20.15g" % ("phi_ex_B", spin1.phi_ex_B, spin2.phi_ex_B))
        print("%-20s %20.15g %20.15g" % ("phi_ex_C", spin1.phi_ex_C, spin2.phi_ex_C))
        print("%-20s %20.15g %20.15g" % ("kB", spin1.kB, spin2.kB))
        print("%-20s %20.15g %20.15g" % ("kC", spin1.kC, spin2.kC))
        print("%-20s %20.15g %20.15g\n" % ("chi2", spin1.chi2, spin2.chi2))
        self.assertAlmostEqual(spin1.r2[r20_key1], 12.0, 2)
        self.assertAlmostEqual(spin1.r2[r20_key2], 12.0, 2)
        self.assertAlmostEqual(spin1.phi_ex_B, 0.1, 3)
        self.assertAlmostEqual(spin1.phi_ex_C, 0.5, 3)
        self.assertAlmostEqual(spin1.kB/1000, 1500.0/1000, 3)
        self.assertAlmostEqual(spin1.kC/1000, 2500.0/1000, 3)
        self.assertAlmostEqual(spin1.chi2, 0.0, 3)
        self.assertAlmostEqual(spin2.r2[r20_key1], 15.0, 3)
        self.assertAlmostEqual(spin2.r2[r20_key2], 15.0, 3)
        self.assertAlmostEqual(spin1.phi_ex_B, 0.1, 3)
        self.assertAlmostEqual(spin1.phi_ex_C, 0.5, 3)
        self.assertAlmostEqual(spin1.kB/1000, 1500.0/1000, 3)
        self.assertAlmostEqual(spin1.kC/1000, 2500.0/1000, 3)
        self.assertAlmostEqual(spin2.chi2, 0.0, 3)


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
        self.interpreter.pipe.switch('R2eff - relax_disp')
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
        self.interpreter.pipe.switch('M61 - relax_disp')
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

        # Single spin optimisation.
        ds.single = True

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
        self.interpreter.pipe.switch('R2eff - relax_disp')
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
        self.interpreter.pipe.switch('M61 - relax_disp')
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
        self.interpreter.pipe.switch("%s - relax_disp" % MODEL_M61B)
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


    def test_model_nesting_and_param(self):
        """Test that all models which can nest, have all their parameters converted."""

        # Set the experiment type.
        cdp.exp_type_list = EXP_TYPE_LIST

        # Get info for all models.
        all_models_info = models_info(models=MODEL_LIST_FULL)

        # Loop over all models.
        print("Printing the listed of nested models for each model.")
        print("#########################################")
        for model_info in all_models_info:
            print("%s"%model_info.model),
            print("<-"),
            nest_list = model_info.nest_list
            if nest_list == None:
                nest_list = ["None"]
            print(', '.join(map(str, nest_list)))

            # Skip if there is no model to nest from.
            if nest_list == ["None"]:
                continue

            # Assign params to variable.
            model_params = model_info.params

            # Now loop over the nested models.
            for nested_model in nest_list:
                # Get the params for the nested model.
                nested_model_params = MODEL_PARAMS[nested_model]

                # Get the dictionary of parameter conversion.
                par_dic = nesting_param(model_params=model_params, nested_model_params=nested_model_params)

                # Test the number of elements in the dictionary.
                self.assertEqual(len(par_dic), len(model_params))

                # Loop over dictionary.
                for param, param_conv in par_dic.iteritems():
                        if param != param_conv:
                            print("Model:'%s', Nested model:'%s', Copying '%s' to '%s'." % (model_info.model, nested_model, param_conv, param))
                        self.assertNotEqual(param_conv, None)


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


    def test_r1rho_kjaergaard_auto(self):
        """Optimisation of the Kjaergaard et al., 2013 Off-resonance R1rho relaxation dispersion experiments using the 'DPL' model.

        This uses the data from Kjaergaard's paper at U{DOI: 10.1021/bi4001062<http://dx.doi.org/10.1021/bi4001062>}.

        This uses the automatic analysis.

        """

        # Cluster residues
        cluster_ids = [
        ":13@N",
        ":15@N",
        ":16@N",
        ":25@N",
        ":26@N",
        ":28@N",
        ":39@N",
        ":40@N",
        ":41@N",
        ":43@N",
        ":44@N",
        ":45@N",
        ":49@N",
        ":52@N",
        ":53@N"]

        # Load the data.
        self.setup_r1rho_kjaergaard(cluster_ids=cluster_ids)

        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, None)
        self.assertEqual(len(cdp.mol[0].res), 48)

        # Test the chemical shift data.
        cs = [122.223, 122.162, 114.250, 125.852, 118.626, 117.449, 119.999, 122.610, 118.602, 118.291, 115.393,
        121.288, 117.448, 116.378, 116.316, 117.263, 122.211, 118.748, 118.103, 119.421, 119.317, 119.386, 117.279,
        122.103, 120.038, 116.698, 111.811, 118.639, 118.285, 121.318, 117.770, 119.948, 119.759, 118.314, 118.160,
        121.442, 118.714, 113.080, 125.706, 119.183, 120.966, 122.361, 126.675, 117.069, 120.875, 109.372, 119.811, 126.048]

        i = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Check the chemical shift.
            self.assertEqual(spin.chemical_shift, cs[i])

            # Increment the index.
            i += 1

        # Initialize counter
        i = 0
        j = 0
        # Count instances of select/deselect
        for curspin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=False):
            if curspin.select == True:
                i += 1
            if curspin.select == False:
                j += 1

        # Test number of selected/deselected spins.
        self.assertEqual(i, len(cluster_ids))
        self.assertEqual(j, 48-len(cluster_ids))

        # Check the initial setup.
        self.assertEqual(cdp.mol[0].res[7].num, 13)
        self.assertEqual(cdp.mol[0].res[7].spin[0].kex, ds.guess[':13@N'][6])
        self.assertEqual(cdp.mol[0].res[7].spin[0].ri_data['R1'], ds.ref[':13@N'][2])

        self.assertEqual(cdp.mol[0].res[9].num, 15)
        self.assertEqual(cdp.mol[0].res[9].spin[0].kex, ds.guess[':15@N'][6])
        self.assertEqual(cdp.mol[0].res[9].spin[0].ri_data['R1'], ds.ref[':15@N'][2])

        self.assertEqual(cdp.mol[0].res[10].num, 16)
        self.assertEqual(cdp.mol[0].res[10].spin[0].kex, ds.guess[':16@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[10].spin[0], 'ri_data'))

        self.assertEqual(cdp.mol[0].res[16].num, 25)
        self.assertEqual(cdp.mol[0].res[16].spin[0].kex, ds.guess[':25@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[16].spin[0], 'ri_data'))

        self.assertEqual(cdp.mol[0].res[17].num, 26)
        self.assertEqual(cdp.mol[0].res[17].spin[0].kex, ds.guess[':26@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[17].spin[0], 'ri_data'))

        self.assertEqual(cdp.mol[0].res[19].num, 28)
        self.assertEqual(cdp.mol[0].res[19].spin[0].kex, ds.guess[':28@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[19].spin[0], 'ri_data'))

        self.assertEqual(cdp.mol[0].res[29].num, 39)
        self.assertEqual(cdp.mol[0].res[29].spin[0].kex, ds.guess[':39@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[29].spin[0], 'ri_data'))

        self.assertEqual(cdp.mol[0].res[30].num, 40)
        self.assertEqual(cdp.mol[0].res[30].spin[0].kex, ds.guess[':40@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[30].spin[0], 'ri_data'))

        self.assertEqual(cdp.mol[0].res[31].num, 41)
        self.assertEqual(cdp.mol[0].res[31].spin[0].kex, ds.guess[':41@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[31].spin[0], 'ri_data'))

        self.assertEqual(cdp.mol[0].res[33].num, 43)
        self.assertEqual(cdp.mol[0].res[33].spin[0].kex, ds.guess[':43@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[33].spin[0], 'ri_data'))

        self.assertEqual(cdp.mol[0].res[34].num, 44)
        self.assertEqual(cdp.mol[0].res[34].spin[0].kex, ds.guess[':44@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[34].spin[0], 'ri_data'))

        self.assertEqual(cdp.mol[0].res[35].num, 45)
        self.assertEqual(cdp.mol[0].res[35].spin[0].kex, ds.guess[':45@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[35].spin[0], 'ri_data'))

        self.assertEqual(cdp.mol[0].res[38].num, 49)
        self.assertEqual(cdp.mol[0].res[38].spin[0].kex, ds.guess[':49@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[38].spin[0], 'ri_data'))

        self.assertEqual(cdp.mol[0].res[41].num, 52)
        self.assertEqual(cdp.mol[0].res[41].spin[0].kex, ds.guess[':52@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[41].spin[0], 'ri_data'))

        self.assertEqual(cdp.mol[0].res[42].num, 53)
        self.assertEqual(cdp.mol[0].res[42].spin[0].kex, ds.guess[':53@N'][6])
        self.assert_(hasattr(cdp.mol[0].res[42].spin[0], 'ri_data'))

        # The dispersion models.
        MODELS = [MODEL_R2EFF, MODEL_NOREX, MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MP05, MODEL_NS_R1RHO_2SITE]

        # The grid search size (the number of increments per dimension).
        GRID_INC = 4

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        MC_NUM = 3

        # Model selection technique.
        MODSEL = 'AIC'

        # Execute the auto-analysis (fast).
        # Standard parameters are: func_tol = 1e-25, grad_tol = None, max_iter = 10000000,
        OPT_FUNC_TOL = 1e-1
        relax_disp.Relax_disp.opt_func_tol = OPT_FUNC_TOL
        OPT_MAX_ITERATIONS = 1000
        relax_disp.Relax_disp.opt_max_iterations = OPT_MAX_ITERATIONS

        result_dir_name = ds.tmpdir

        # Make all spins free
        for curspin in cluster_ids:
            self.interpreter.relax_disp.cluster('free spins', curspin)
            # Shut them down
            self.interpreter.deselect.spin(spin_id=curspin, change_all=False)

        # Select only a subset of spins for global fitting
        #self.interpreter.select.spin(spin_id=':41@N', change_all=False)
        #self.interpreter.relax_disp.cluster('model_cluster', ':41@N')

        #self.interpreter.select.spin(spin_id=':40@N', change_all=False)
        #self.interpreter.relax_disp.cluster('model_cluster', ':40@N')

        self.interpreter.select.spin(spin_id=':52@N', change_all=False)
        #self.interpreter.relax_disp.cluster('model_cluster', ':52@N')

        # Run the analysis.
        relax_disp.Relax_disp(pipe_name=ds.pipe_name, pipe_bundle=ds.pipe_bundle, results_dir=result_dir_name, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL)

        # Check the kex value of residue 52
        #self.assertAlmostEqual(cdp.mol[0].res[41].spin[0].kex, ds.ref[':52@N'][6])

        # Print results for each model.
        print("\n\n################")
        print("Printing results")
        print("################\n")
        for model in MODELS:
            # Skip R2eff model.
            if model == MODEL_R2EFF:
                continue

            # Switch to pipe.
            self.interpreter.pipe.switch(pipe_name='%s - relax_disp' % (model))
            print("\nModel: %s" % (model))

            # Loop over the spins.
            for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
                # Generate spin string.
                spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

                # Loop over the parameters.
                print("Optimised parameters for spin: %s" % (spin_string))
                for param in cur_spin.params + ['chi2']:
                    # Get the value.
                    if param in ['r1', 'r2']:
                        for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):
                            # Generate the R20 key.
                            r20_key = generate_r20_key(exp_type=exp_type, frq=frq)

                            # Get the value.
                            value = getattr(cur_spin, param)[r20_key]

                            # Print value.
                            print("%-10s %-6s %-6s %3.3f" % ("Parameter:", param, "Value:", value))

                    # For all other parameters.
                    else:
                        # Get the value.
                        value = getattr(cur_spin, param)

                        # Print value.
                        print("%-10s %-6s %-6s %3.3f" % ("Parameter:", param, "Value:", value))

        # Print the final pipe.
        self.interpreter.pipe.switch(pipe_name='%s - relax_disp' % ('final'))
        print("\nFinal pipe")


    def test_r1rho_kjaergaard_auto_check_graphs(self):
        """Check of plot_disp_curves() function, after optimisation of the Kjaergaard et al., 2013 Off-resonance R1rho relaxation dispersion experiments using the 'R2eff' model.

        This uses the data from Kjaergaard's paper at U{DOI: 10.1021/bi4001062<http://dx.doi.org/10.1021/bi4001062>}.

        This uses the automatic analysis.

        """

        # Cluster residues
        cluster_ids = [
        ":52@N"]

        # Load the data.
        self.setup_r1rho_kjaergaard(cluster_ids=cluster_ids)

        # The dispersion models.
        MODELS = [MODEL_R2EFF]

        # The grid search size (the number of increments per dimension).
        GRID_INC = 4

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        MC_NUM = 3

        # Model selection technique.
        MODSEL = 'AIC'

        # Execute the auto-analysis (fast).
        # Standard parameters are: func_tol = 1e-25, grad_tol = None, max_iter = 10000000,
        OPT_FUNC_TOL = 1e-1
        relax_disp.Relax_disp.opt_func_tol = OPT_FUNC_TOL
        OPT_MAX_ITERATIONS = 1000
        relax_disp.Relax_disp.opt_max_iterations = OPT_MAX_ITERATIONS

        result_dir_name = ds.tmpdir

        # Make all spins free
        for curspin in cluster_ids:
            self.interpreter.relax_disp.cluster('free spins', curspin)
            # Shut them down
            self.interpreter.deselect.spin(spin_id=curspin, change_all=False)

        self.interpreter.select.spin(spin_id=':52@N', change_all=False)

        # Run the analysis.
        relax_disp.Relax_disp(pipe_name=ds.pipe_name, pipe_bundle=ds.pipe_bundle, results_dir=result_dir_name, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL)

        # Check the graphs produced.
        graph_comb = [
        [Y_AXIS_R2_EFF, X_AXIS_DISP, INTERPOLATE_DISP],
        [Y_AXIS_R2_EFF, X_AXIS_THETA, INTERPOLATE_DISP],
        [Y_AXIS_R2_R1RHO, X_AXIS_W_EFF, INTERPOLATE_DISP],
        [Y_AXIS_R2_EFF, X_AXIS_THETA, INTERPOLATE_OFFSET]
        ]

        # Define expected folder names.
        result_folders = MODELS

        # Assign spin_id.
        spin_id = ':52@N'

        # Loop over result folders.
        for result_folder in result_folders:
            # Skip the model R2eff, which does not produce graphs.
            if result_folder == MODEL_R2EFF:
                continue

            # Loop over graphs.
            for y_axis, x_axis, interpolate in graph_comb:
                # Determine file name:
                file_name_ini = return_grace_file_name_ini(y_axis=y_axis, x_axis=x_axis, interpolate=interpolate)

                # Make the file name.
                file_name = "%s%s.agr" % (file_name_ini, spin_id.replace('#', '_').replace(':', '_').replace('@', '_'))

                # Get the file path.
                file_path = get_file_path(file_name, result_dir_name+sep+result_folder)

                print("Testing file access to graph: %s"%file_path)
                self.assert_(access(file_path, F_OK))

        # Start testing all possible combinations of graphs.
        y_axis_types = [Y_AXIS_R2_EFF, Y_AXIS_R2_R1RHO]
        x_axis_types = [X_AXIS_DISP, X_AXIS_THETA, X_AXIS_W_EFF]
        interpolate_types = [INTERPOLATE_DISP, INTERPOLATE_OFFSET]

        result_dir_name = ds.tmpdir

        # Loop through all possible combinations of y_axis, x_axis and interpolation.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013'+sep+'check_graphs'

        for result_folder in result_folders:
            # Skip the model R2eff, which does not produce graphs.
            if result_folder == MODEL_R2EFF:
                continue

            for y_axis in y_axis_types:
                for x_axis in x_axis_types:
                    for interpolate in interpolate_types:
                        # Determine file name:
                        file_name_ini = return_grace_file_name_ini(y_axis=y_axis, x_axis=x_axis, interpolate=interpolate)

                        # Make the file name.
                        file_name = "%s%s.agr" % (file_name_ini, spin_id.replace('#', '_').replace(':', '_').replace('@', '_'))

                        # Write the curves.
                        dir = result_dir_name+sep+result_folder
                        print("Plotting combination of %s, %s, %s"%(y_axis, x_axis, interpolate))
                        self.interpreter.relax_disp.plot_disp_curves(dir=dir, y_axis=y_axis, x_axis=x_axis, interpolate=interpolate, force=True)

                        # Get the file path.
                        file_path = get_file_path(file_name, dir)

                        # Test the plot file exists.
                        print("Testing file access to graph: %s"%file_path)
                        self.assert_(access(file_path, F_OK))

                        # Now open, and compare content, line by line.
                        file_prod = open(file_path)
                        lines_prod = file_prod.readlines()
                        file_prod.close()

                        # Define file to compare against.
                        dir_comp = data_path+sep+result_folder
                        file_path_comp = get_file_path(file_name, dir_comp)
                        file_comp = open(file_path_comp)
                        lines_comp = file_comp.readlines()
                        file_comp.close()

                        # Assert number of lines is equal.
                        self.assertEqual(len(lines_prod), len(lines_comp))
                        for j in range(len(lines_prod)):
                            # Make the string test
                            first_char = lines_prod[j][0]
                            if first_char in ["@", "&"]:
                                self.assertEqual(lines_prod[j], lines_comp[j])
                            else:
                                # Split string in x, y, error.
                                # The error would change per run.
                                x_prod, y_prod, y_prod_err = lines_prod[j].split()
                                x_comp, y_comp, y_comp_err = lines_comp[j].split()
                                self.assertAlmostEqual(float(x_prod), float(x_comp))
                                self.assertAlmostEqual(float(y_prod), float(y_comp))


    def test_r1rho_kjaergaard_missing_r1(self):
        """Optimisation of the Kjaergaard et al., 2013 Off-resonance R1rho relaxation dispersion experiments using the 'DPL' model.

        This uses the data from Kjaergaard's paper at U{DOI: 10.1021/bi4001062<http://dx.doi.org/10.1021/bi4001062>}.

        This uses the automatic analysis, with missing loading R1.

        """

        # Cluster residues
        cluster_ids = [
        ":13@N",
        ":15@N",
        ":16@N",
        ":25@N",
        ":26@N",
        ":28@N",
        ":39@N",
        ":40@N",
        ":41@N",
        ":43@N",
        ":44@N",
        ":45@N",
        ":49@N",
        ":52@N",
        ":53@N"]

        # Load the data.
        self.setup_r1rho_kjaergaard(cluster_ids=cluster_ids, read_R1=False)

        # The dispersion models.
        MODELS = [MODEL_R2EFF, MODEL_NOREX, MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MP05, MODEL_NS_R1RHO_2SITE]

        # The grid search size (the number of increments per dimension).
        GRID_INC = None

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        MC_NUM = 3

        # Model selection technique.
        MODSEL = 'AIC'

        # Execute the auto-analysis (fast).
        # Standard parameters are: func_tol = 1e-25, grad_tol = None, max_iter = 10000000,
        OPT_FUNC_TOL = 1e-25
        relax_disp.Relax_disp.opt_func_tol = OPT_FUNC_TOL
        OPT_MAX_ITERATIONS = 10000000
        relax_disp.Relax_disp.opt_max_iterations = OPT_MAX_ITERATIONS

        result_dir_name = ds.tmpdir

        # Make all spins free
        for curspin in cluster_ids:
            self.interpreter.relax_disp.cluster('free spins', curspin)
            # Shut them down
            self.interpreter.deselect.spin(spin_id=curspin, change_all=False)

        # Select only a subset of spins for global fitting
        #self.interpreter.select.spin(spin_id=':41@N', change_all=False)
        #self.interpreter.relax_disp.cluster('model_cluster', ':41@N')

        #self.interpreter.select.spin(spin_id=':40@N', change_all=False)
        #self.interpreter.relax_disp.cluster('model_cluster', ':40@N')

        self.interpreter.select.spin(spin_id=':52@N', change_all=False)
        #self.interpreter.relax_disp.cluster('model_cluster', ':52@N')

        # Point to directory with R2eff values, with 2000 MC simulations.
        prev_data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013' +sep+ "check_graphs" +sep+ "mc_2000"

        # Run the analysis.
        relax_disp.Relax_disp(pipe_name=ds.pipe_name, pipe_bundle=ds.pipe_bundle, results_dir=result_dir_name, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL, pre_run_dir=prev_data_path)

        # Verify the data.
        self.verify_r1rho_kjaergaard_missing_r1(models=MODELS, result_dir_name=result_dir_name)


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
            self.interpreter.relax_disp.cpmg_setup(spectrum_id='1H_CPMG_%s' % value, cpmg_frq=value)
        for value in N_disp_points:
            self.interpreter.relax_disp.cpmg_setup(spectrum_id='15N_CPMG_%s' % value, cpmg_frq=value)

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


    def test_r20_from_min_r2eff_cpmg(self):
        """Test speeding up grid search. Support requst sr #3151 U{https://gna.org/support/index.php?3151}.

        User function to set the R20 parameters in the default grid search using the minimum R2eff value.

        Optimisation of Kaare Teilum, Melanie H. Smith, Eike Schulz, Lea C. Christensen, Gleb Solomentseva, Mikael Oliveberg, and Mikael Akkea 2009
        'SOD1-WT' CPMG data to the CR72 dispersion model.

        This uses the data from paper at U{http://dx.doi.org/10.1073/pnas.0907387106}.  This is CPMG data with a fixed relaxation time period recorded at fields of 500 and 600MHz.
        Data is for experiment at 25 degree Celcius.
        """

        # Base data setup.
        pipe_name = 'base pipe'
        pipe_type = 'relax_disp'
        pipe_name_r2eff = "%s_R2eff"%(pipe_name)
        select_spin_index = list(range(0, 1))
        self.setup_sod1wt_t25(pipe_name=pipe_name, pipe_type=pipe_type, pipe_name_r2eff=pipe_name_r2eff, select_spin_index=select_spin_index)

        # Generate r20 key.
        r20_key_600 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=599.8908617*1E6)
        r20_key_500 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=499.862139*1E6)

        ## Now prepare for MODEL calculation.
        MODEL = "CR72"

        # Change pipe.
        pipe_name_MODEL = "%s_%s"%(pipe_name, MODEL)
        self.interpreter.pipe.copy(pipe_from=pipe_name_r2eff, pipe_to=pipe_name_MODEL)
        self.interpreter.pipe.switch(pipe_name=pipe_name_MODEL)

        # Then select model.
        self.interpreter.relax_disp.select_model(model=MODEL)

        # Set the R20 parameters in the default grid search using the minimum R2eff value.
        self.interpreter.relax_disp.r20_from_min_r2eff(force=False)

        # Test result, for normal run.
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            # Get the spin_params.
            spin_params = spin.params

            # Defined fixed values for testing.
            if spin_id == ":10@N":
                self.assertEqual(spin.r2[r20_key_600], 20.282732526087106)
                self.assertEqual(spin.r2[r20_key_500], 18.475299724356649)

            # Print out.
            print("r2_600=%2.2f r2_500=%2.2f spin_id=%s resi=%i resn=%s"%(spin.r2[r20_key_600], spin.r2[r20_key_500], spin_id, resi, resn))

            # Testing the r2 values for the different fields are not the same.
            self.assert_(spin.r2[r20_key_600] != spin.r2[r20_key_500])

            # Test values are larger than 0.
            self.assert_(spin.r2[r20_key_600] > 0.0)
            self.assert_(spin.r2[r20_key_500] > 0.0)

            # Loop over the experiment settings.
            r2eff_600 = []
            r2eff_500 = []
            for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
                # Create the data key.
                data_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

                # Extract the r2 eff data.
                r2eff = spin.r2eff[data_key]
                if frq == 599.8908617*1E6:
                    r2eff_600.append(r2eff)
                elif frq == 499.862139*1E6:
                    r2eff_500.append(r2eff)

            # Sort values.
            r2eff_600.sort()
            r2eff_500.sort()

            # Test values again.
            print("For r20 600MHz min r2eff=%3.3f."%(min(r2eff_600)))
            print(r2eff_600)
            self.assertEqual(spin.r2[r20_key_600], min(r2eff_600))
            print("")

            print("For r20 500MHz min r2eff=%3.3f."%(min(r2eff_500)))
            print(r2eff_500)
            self.assertEqual(spin.r2[r20_key_500], min(r2eff_500))
            print("")

        print("###########################################")
        print("Trying GRID SEARCH for minimum R2eff values")

        ### Test just the Grid search.
        GRID_INC = 5

        self.interpreter.minimise.grid_search(lower=None, upper=None, inc=GRID_INC, constraints=True, verbosity=1)

        ### Then test the value.set function.
        # Change pipe.
        pipe_name_MODEL = "%s_%s_2"%(pipe_name, MODEL)
        self.interpreter.pipe.copy(pipe_from=pipe_name_r2eff, pipe_to=pipe_name_MODEL)
        self.interpreter.pipe.switch(pipe_name=pipe_name_MODEL)

        # Then select model.
        self.interpreter.relax_disp.select_model(model=MODEL)

        # Then set the standard parameter values.
        for param in spin_params:
            print("Setting standard parameter for param: %s"%param)
            self.interpreter.value.set(param=param, index=None)

        # Test result, for normal run.
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            # Print out.
            print("r2_600=%2.2f r2_500=%2.2f pA=%2.2f, dw=%2.2f, kex=%2.2f, spin_id=%s resi=%i resn=%s"%(spin.r2[r20_key_600], spin.r2[r20_key_500], spin.pA, spin.dw, spin.kex, spin_id, resi, resn))

            # Testing the r2 values.
            self.assertEqual(spin.r2[r20_key_600], 10.00)
            self.assertEqual(spin.r2[r20_key_500], 10.00)
            self.assertEqual(spin.pA, 0.9)
            self.assertEqual(spin.dw, 1.0)
            self.assertEqual(spin.kex, 1000.0)

        print("###########################################")
        print("Trying GRID SEARCH for standard R2eff values")

        ### Test just the Grid search.
        GRID_INC = 5

        self.interpreter.minimise.grid_search(lower=None, upper=None, inc=GRID_INC, constraints=True, verbosity=1)

        ### Run auto_analysis.
        # The grid search size (the number of increments per dimension).
        GRID_INC = 5

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        MC_NUM = 3

        # Model selection technique.
        MODSEL = 'AIC'

        # Execute the auto-analysis (fast).
        # Standard parameters are: func_tol = 1e-25, grad_tol = None, max_iter = 10000000,
        OPT_FUNC_TOL = 1e-1
        relax_disp.Relax_disp.opt_func_tol = OPT_FUNC_TOL
        OPT_MAX_ITERATIONS = 1000
        relax_disp.Relax_disp.opt_max_iterations = OPT_MAX_ITERATIONS

        # Run the analysis.
        relax_disp.Relax_disp(pipe_name=pipe_name_r2eff, results_dir=ds.tmpdir, models=[MODEL], grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL, set_grid_r20=True)


    def test_sod1wt_t25_bug_21954_order_error_analysis(self):
        """Error analysis of SOD1-WT CPMG. From paper at U{http://dx.doi.org/10.1073/pnas.0907387106}.

        Optimisation of Kaare Teilum, Melanie H. Smith, Eike Schulz, Lea C. Christensen, Gleb Solomentseva, Mikael Oliveberg, and Mikael Akkea 2009
        'SOD1-WT' CPMG data to the CR72 dispersion model.

        This uses the data from paper at U{http://dx.doi.org/10.1073/pnas.0907387106}.  This is CPMG data with a fixed relaxation time period recorded at fields of 500 and 600MHz.
        Data is for experiment at 25 degree Celcius.

        bug #21954 U{https://gna.org/bugs/index.php?21954}: Order of spectrum.error_analysis is important.
        """

        # Base data setup.
        pipe_name = 'base pipe'
        pipe_type = 'relax_disp'
        pipe_name_r2eff = "%s_R2eff"%(pipe_name)
        select_spin_index = list(range(0, 1))
        self.setup_sod1wt_t25(pipe_name=pipe_name, pipe_type=pipe_type, pipe_name_r2eff=pipe_name_r2eff, select_spin_index=select_spin_index)

        # Define replicated
        repl_A = ['Z_A1', 'Z_A15']
        repl_B = ['Z_B1', 'Z_B18']

        # Loop over spectrum ID, and sort them
        spectrum_ids_A = []
        spectrum_ids_B = []
        for spectrum_id in cdp.spectrum_ids:
            if "A" in spectrum_id:
                spectrum_ids_A.append(spectrum_id)
            elif "B" in spectrum_id:
                spectrum_ids_B.append(spectrum_id)

        # To clean up old error analysis, delete attributes
        delattr(cdp, "var_I")
        delattr(cdp, "sigma_I")

        # Perform error analysis
        self.interpreter.spectrum.error_analysis(subset=spectrum_ids_A)
        self.interpreter.spectrum.error_analysis(subset=spectrum_ids_B)

        # Loop over spins, save errors to list
        Errors_A_B = []
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            A_err = spin.peak_intensity_err[spectrum_ids_A[0]]
            B_err = spin.peak_intensity_err[spectrum_ids_B[0]]
            Errors_A_B.append([A_err, B_err])

        # To clean up old error analysis, delete attributes
        delattr(cdp, "var_I")
        delattr(cdp, "sigma_I")

        # Perform error analysis. Order is important
        self.interpreter.spectrum.error_analysis(subset=spectrum_ids_B)
        self.interpreter.spectrum.error_analysis(subset=spectrum_ids_A)

        # Loop over spins, save errors to list
        Errors_B_A = []
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            A_err = spin.peak_intensity_err[spectrum_ids_A[0]]
            B_err = spin.peak_intensity_err[spectrum_ids_B[0]]
            Errors_B_A.append([A_err, B_err])

        # Make test for order of error
        for i in range(len(Errors_A_B)):
            Error_A_B = Errors_A_B[i]
            Error_B_A = Errors_B_A[i]
            self.assertAlmostEqual(Error_A_B[0], Error_B_A[0], 4)
            self.assertAlmostEqual(Error_A_B[1], Error_B_A[1], 4)

        # Make further tests for fixed values
        std_A = math.sqrt((cdp.var_I[repl_A[0]] + cdp.var_I[repl_A[1]])/2)
        std_A_fix = 2785.7263335738567

        for id_A in spectrum_ids_A:
            self.assertEqual(cdp.sigma_I[id_A], std_A)
            self.assertAlmostEqual(cdp.sigma_I[id_A], std_A_fix, 7)

        std_B = math.sqrt((cdp.var_I[repl_B[0]] + cdp.var_I[repl_B[1]])/2)
        std_B_fix = 4967.3772030667988

        for id_B in spectrum_ids_B:
            self.assertEqual(cdp.sigma_I[id_B], std_B)
            self.assertAlmostEqual(cdp.sigma_I[id_B], std_B_fix, 7)


    def test_sod1wt_t25_to_cr72(self):
        """Optimisation of SOD1-WT CPMG. From paper at U{http://dx.doi.org/10.1073/pnas.0907387106}.

        Optimisation of Kaare Teilum, Melanie H. Smith, Eike Schulz, Lea C. Christensen, Gleb Solomentseva, Mikael Oliveberg, and Mikael Akkea 2009
        'SOD1-WT' CPMG data to the CR72 dispersion model.

        This uses the data from paper at U{http://dx.doi.org/10.1073/pnas.0907387106}.  This is CPMG data with a fixed relaxation time period recorded at fields of 500 and 600MHz.
        Data is for experiment at 25 degree Celcius.
        """

        # Base data setup.
        pipe_name = 'base pipe'
        pipe_type = 'relax_disp'
        pipe_name_r2eff = "%s_R2eff"%(pipe_name)
        select_spin_index = list(range(0, 2))
        self.setup_sod1wt_t25(pipe_name=pipe_name, pipe_type=pipe_type, pipe_name_r2eff=pipe_name_r2eff, select_spin_index=select_spin_index)

        # Generate r20 key.
        r20_key_600 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=599.8908617*1E6)
        r20_key_500 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=499.862139*1E6)

        ## Now prepare for MODEL calculation.
        MODEL = "CR72"

        # Change pipe.
        pipe_name_MODEL = "%s_%s"%(pipe_name, MODEL)
        self.interpreter.pipe.copy(pipe_from=pipe_name_r2eff, pipe_to=pipe_name_MODEL)
        self.interpreter.pipe.switch(pipe_name=pipe_name_MODEL)

        # Then select model.
        self.interpreter.relax_disp.select_model(model=MODEL)

        # GRID inc of 7 was found to be appropriate not to find pA = 0.5.
        GRID_INC = 7

        # Store grid and minimisations results.
        grid_results = []
        mini_results = []
        clust_results = []

        # Set the R20 parameters in the default grid search using the minimum R2eff value.
        self.interpreter.relax_disp.r20_from_min_r2eff(force=False)

        # Deselect insignificant spins.
        self.interpreter.relax_disp.insignificance(level=1.0)

        # Perform Grid Search.
        self.interpreter.minimise.grid_search(lower=None, upper=None, inc=GRID_INC, constraints=True, verbosity=1)

        # Store result.
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            # Store grid results.
            grid_results.append([spin.r2[r20_key_600], spin.r2[r20_key_500], spin.dw, spin.pA, spin.kex, spin.chi2, spin_id, resi, resn])

        ## Now do minimisation.
        # Standard parameters are: func_tol = 1e-25, grad_tol = None, max_iter = 10000000,
        set_func_tol = 1e-9
        set_max_iter = 100000
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=set_func_tol, max_iter=set_max_iter, constraints=True, scaling=True, verbosity=1)

        # Store result.
        pA_values = []
        kex_values = []
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            # Store minimisation results.
            mini_results.append([spin.r2[r20_key_600], spin.r2[r20_key_500], spin.dw, spin.pA, spin.kex, spin.chi2, spin_id, resi, resn])

            # Store pA values.
            pA_values.append(spin.pA)

            # Store kex values.
            kex_values.append(spin.kex)

        print("\n# Now print before and after minimisation.\n")

        # Print results.
        for i in range(len(grid_results)):
            # Get values.
            g_r2_600, g_r2_500, g_dw, g_pA, g_kex, g_chi2, g_spin_id, g_resi, g_resn = grid_results[i]
            m_r2_600, m_r2_500, m_dw, m_pA, m_kex, m_chi2, m_spin_id, m_resi, m_resn = mini_results[i]

            print("GRID r2600=%2.2f r2500=%2.2f dw=%1.1f pA=%1.3f kex=%3.2f chi2=%3.2f spin_id=%s resi=%i resn=%s"%(g_r2_600, g_r2_500, g_dw, g_pA, g_kex, g_chi2, g_spin_id, g_resi, g_resn))
            print("MIN  r2600=%2.2f r2500=%2.2f dw=%1.1f pA=%1.3f kex=%3.2f chi2=%3.2f spin_id=%s resi=%i resn=%s"%(m_r2_600, m_r2_500, m_dw, m_pA, m_kex, m_chi2, m_spin_id, m_resi, m_resn))

        ## Prepare for clustering
        # Change pipe.
        pipe_name_MODEL_CLUSTER = "%s_%s_Cluster"%(pipe_name, MODEL)
        self.interpreter.pipe.copy(pipe_from=pipe_name_r2eff, pipe_to=pipe_name_MODEL_CLUSTER)
        self.interpreter.pipe.switch(pipe_name=pipe_name_MODEL_CLUSTER)

        # Then select model.
        self.interpreter.relax_disp.select_model(model=MODEL)

        # Define cluster id.
        cluster_id = 'clust'

        # Loop over spins to cluster them.
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            self.interpreter.relax_disp.cluster(cluster_id, spin_id)

        # Copy over values.
        self.interpreter.relax_disp.parameter_copy(pipe_from=pipe_name_MODEL, pipe_to=pipe_name_MODEL_CLUSTER)

        # Test the median values is correct
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            print(pA_values)
            # The the median pA value returned.
            self.assertEqual(median(pA_values), spin.pA)

            # The the median kex value returned.
            self.assertEqual(median(kex_values), spin.kex)

        ## Now do minimisation.
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=set_func_tol, max_iter=set_max_iter, constraints=True, scaling=True, verbosity=1)

        # Store result.
        for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            # Store clust results.
            clust_results.append([spin.r2[r20_key_600], spin.r2[r20_key_500], spin.dw, spin.pA, spin.kex, spin.chi2, spin_id, resi, resn])

            # Store the outcome of the clustering minimisation.
            clust_pA = spin.pA
            clust_kex = spin.kex

        print("\n# Now testing.\n")

        # Define results
        test_res = {}
        test_res[':10@N'] = {}
        test_res[':10@N']['r2600'] = 18.429755324773360
        test_res[':10@N']['r2500'] = 16.981349161968630
        test_res[':10@N']['dw'] = 2.700755859433969
        test_res[':10@N']['pA'] = 0.971531659288657
        test_res[':10@N']['kex'] = 3831.766337047963134
        test_res[':11@N'] = {}
        test_res[':11@N']['r2600'] = 18.193409421115213
        test_res[':11@N']['r2500'] = 17.308838135567765
        test_res[':11@N']['dw'] = 2.706650302761793
        test_res[':11@N']['pA'] = 0.971531659288657
        test_res[':11@N']['kex'] = 3831.766337047963134

        # Then make tests.
        for i in range(len(grid_results)):
            # Get values.
            g_r2_600, g_r2_500, g_dw, g_pA, g_kex, g_chi2, g_spin_id, g_resi, g_resn = grid_results[i]
            m_r2_600, m_r2_500, m_dw, m_pA, m_kex, m_chi2, m_spin_id, m_resi, m_resn = mini_results[i]
            c_r2_600, c_r2_500, c_dw, c_pA, c_kex, c_chi2, c_spin_id, c_resi, c_resn = clust_results[i]

            print("%s GRID   r2600=%2.2f r2500=%2.2f dw=%1.1f pA=%1.3f kex=%3.2f chi2=%3.2f spin_id=%s resi=%i resn=%s"%(g_spin_id, g_r2_600, g_r2_500, g_dw, g_pA, g_kex, g_chi2, g_spin_id, g_resi, g_resn))
            print("%s MIN    r2600=%2.2f r2500=%2.2f dw=%1.1f pA=%1.3f kex=%3.2f chi2=%3.2f spin_id=%s resi=%i resn=%s"%(m_spin_id, m_r2_600, m_r2_500, m_dw, m_pA, m_kex, m_chi2, m_spin_id, m_resi, m_resn))
            print("%s Clust  r2600=%2.2f r2500=%2.2f dw=%1.1f pA=%1.3f kex=%3.2f chi2=%3.2f spin_id=%s resi=%i resn=%s"%(m_spin_id, c_r2_600, c_r2_500, c_dw, c_pA, c_kex, c_chi2, c_spin_id, c_resi, c_resn))

            # Make tests.
            self.assertEqual(clust_pA, c_pA)
            self.assertEqual(clust_kex, c_kex)

            # Test values.
            if c_spin_id in test_res:
                self.assertAlmostEqual(c_r2_600, test_res[c_spin_id]['r2600'], 4)
                self.assertAlmostEqual(c_r2_500, test_res[c_spin_id]['r2500'], 4)
                self.assertAlmostEqual(c_dw, test_res[c_spin_id]['dw'], 3)
                self.assertAlmostEqual(c_pA, test_res[c_spin_id]['pA'], 5)
                self.assertAlmostEqual(c_kex, test_res[c_spin_id]['kex'], 1)

        # Save disp graph to temp.
        #self.interpreter.relax_disp.plot_disp_curves(dir="~"+sep+"test", num_points=1000, extend=500.0, force=True).


    def test_sod1wt_t25_to_sherekhan_input(self):
        """Conversion of SOD1-WT CPMG R2eff values into input files for sherekhan.

        Optimisation of Kaare Teilum, Melanie H. Smith, Eike Schulz, Lea C. Christensen, Gleb Solomentseva, Mikael Oliveberg, and Mikael Akkea 2009
        'SOD1-WT' CPMG data to the CR72 dispersion model.

        This uses the data from paper at U{http://dx.doi.org/10.1073/pnas.0907387106}.  This is CPMG data with a fixed relaxation time period recorded at fields of 500 and 600MHz.
        Data is for experiment at 25 degree Celcius.
        """

        # Base data setup.
        pipe_name = 'base pipe'
        pipe_type = 'relax_disp'
        pipe_name_r2eff = "%s_R2eff"%(pipe_name)
        select_spin_index = list(range(0, 2))
        self.setup_sod1wt_t25(pipe_name=pipe_name, pipe_type=pipe_type, pipe_name_r2eff=pipe_name_r2eff, select_spin_index=select_spin_index)

        # Generate r20 key.
        r20_key_600 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=599.8908617*1E6)
        r20_key_500 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=499.862139*1E6)

        # Cluster everything, to analyse together.
        self.interpreter.relax_disp.cluster(cluster_id='all', spin_id=":1-1000")

        # Write input
        self.interpreter.relax_disp.sherekhan_input(force=True, spin_id=None, dir=ds.tmpdir)

        # Check the r2eff set files.
        print("\nChecking the R2eff input set files.")
        files = [[ds.tmpdir + sep + 'cluster1', 'sherekhan_frq1.in'], [ ds.tmpdir + sep + 'cluster1', 'sherekhan_frq2.in']]

        # First check file exists
        for dir, file in files:
            print(dir+sep+file)
            self.assert_(access(dir+sep+file, F_OK))

        # Define how files should look like
        data_set_600 = [
             "60.8272464287\n",
             "0.06\n",
             "# nu_cpmg (Hz)       R2eff (rad/s)        Error               \n",
             "# G10\n",
             "              33.333       26.53556078711      0.5236104771163\n",
             "              66.667       25.29735243318        0.48766574122\n",
             "                 100       25.09470361403      0.4820438864671\n",
             "             133.333       25.15603274331      0.4837377286085\n",
             "             166.667       24.27213341753      0.4599457904395\n",
             "                 200       24.00364120328      0.4529773198905\n",
             "             266.667       24.03511395168      0.4537880662536\n",
             "                 300       23.04761040024      0.4291039120557\n",
             "             333.333       22.95530300787      0.4268745963972\n",
             "                 400       23.06158810662      0.4294426293624\n",
             "             466.667       22.26799054092      0.4106809618644\n",
             "             533.333       21.99851418823      0.4045232104735\n",
             "             666.667       21.19651570955      0.3868136173831\n",
             "             833.333       20.30938498379      0.3682604887899\n",
             "                1000       20.28273252609       0.367719392568\n",
             "# D11\n",
             "              33.333       24.76520269878      0.5026475808706\n",
             "              66.667        24.8773107448      0.5058752916906\n",
             "                 100       24.90357815239      0.5066348551479\n",
             "             133.333        23.7782506151      0.4751950583865\n",
             "             166.667       23.68548762076      0.4727017128631\n",
             "                 200       23.58629651618      0.4700517377679\n",
             "             266.667       23.47734671187      0.4671601744044\n",
             "                 300       24.08647493772      0.4835855560598\n",
             "             333.333       22.98314371029      0.4542918950801\n",
             "                 400       22.80339361568      0.4497107885587\n",
             "             466.667       22.91634335366      0.4525833037874\n",
             "             533.333       22.59774140046      0.4445334311324\n",
             "             666.667        20.9177750759      0.4046955726046\n",
             "             833.333       20.71792550566      0.4002363835007\n",
             "                1000       19.54080006349      0.3751112751853\n",
        ]

        # Check data_set_600
        file = open(files[0][0]+sep+files[0][1])
        lines = file.readlines()
        file.close()
        self.assertEqual(len(data_set_600), len(lines))
        for i in range(len(data_set_600)):
            # Make the string test
            self.assertEqual(data_set_600[i], lines[i])

        # Define how files should look like
        data_set_500 = [
             "50.6846152368\n",
             "0.04\n",
             "# nu_cpmg (Hz)       R2eff (rad/s)        Error               \n",
             "# G10\n",
             "                  50       22.28084307393      0.2944966344183\n",
             "                 100       21.93494977761      0.2910362768307\n",
             "                 150       21.09850032232       0.282892238351\n",
             "                 200       20.86493960397      0.2806737853646\n",
             "                 250       20.75287269752      0.2796178205016\n",
             "                 300       20.25597152406      0.2750013546989\n",
             "                 350       19.92172163467      0.2719555756504\n",
             "                 400       19.97712052922       0.272457105051\n",
             "                 450       19.46807010415      0.2678972122793\n",
             "                 500       19.76875460947      0.2705774849203\n",
             "                 550       19.39161367402      0.2672216964327\n",
             "                 600       19.03949517697      0.2641417899694\n",
             "                 650       19.12218812132      0.2648605059901\n",
             "                 700       19.01037461457      0.2638893584683\n",
             "                 800       18.83395162904      0.2623674321143\n",
             "                 900       18.47529972436      0.2593123604687\n",
             "                1000        18.5252023121      0.2597343394038\n",
             "# D11\n",
             "                  50       22.15403890237      0.3285588379827\n",
             "                 100       21.80946781746      0.3247185598713\n",
             "                 150       21.77715415505       0.324361526682\n",
             "                 200       21.41647464235      0.3204122024881\n",
             "                 250       21.17099940822      0.3177616325958\n",
             "                 300       21.03740030577      0.3163316496664\n",
             "                 350       20.95393648281      0.3154427665172\n",
             "                 400       20.93311399332       0.315221543436\n",
             "                 450       20.18219905222      0.3073848655291\n",
             "                 500       19.93599065085      0.3048744697057\n",
             "                 550       19.68475725452      0.3023424499113\n",
             "                 600       19.33575433934      0.2988741928798\n",
             "                 650       19.53915692194      0.3008886196853\n",
             "                 700        19.2018754351      0.2975587767134\n",
             "                 800       18.82360965368      0.2938866923878\n",
             "                 900       18.71861761238      0.2928790380131\n",
             "                1000       17.95878049287      0.2857341721151\n",
        ]

        # Check data_set_500
        file = open(files[1][0]+sep+files[1][1])
        lines = file.readlines()
        file.close()
        self.assertEqual(len(data_set_500), len(lines))
        for i in range(len(data_set_500)):
            # Make the string test
            self.assertEqual(data_set_500[i], lines[i])

        # Test local dir tests. This will be turned off in system test.
        turn_on_local_dir_test = False

        if turn_on_local_dir_test:
            ## Now check to local folder with None argument.
            # Write input
            self.interpreter.relax_disp.sherekhan_input(force=True, spin_id=None)

            # Check the r2eff set files.
            print("\nChecking the R2eff input set files.")
            files = [[path.join(getcwd(), 'cluster1'), 'sherekhan_frq1.in'], [path.join(getcwd(), 'cluster1'), 'sherekhan_frq2.in']]

            # First check file exists
            for dir, file in files:
                print(dir+sep+file)
                self.assert_(access(dir+sep+file, F_OK))

            ## Now check to local folder with dir argument.
            # Write input
            set_dir = "Test_ShereKhan"
            self.interpreter.relax_disp.sherekhan_input(force=True, spin_id=None, dir=set_dir)

            # Check the r2eff set files.
            print("\nChecking the R2eff input set files.")
            files = [[path.join(getcwd(), set_dir, 'cluster1'), 'sherekhan_frq1.in'], [path.join(getcwd(), set_dir, 'cluster1'), 'sherekhan_frq2.in']]

            # First check file exists
            for dir, file in files:
                print(dir+sep+file)
                self.assert_(access(dir+sep+file, F_OK))


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
        pipe_name = "%s - relax_disp" % model
        self.interpreter.pipe.copy(pipe_from='base pipe', pipe_to=pipe_name, bundle_to='relax_disp')
        self.interpreter.pipe.switch(pipe_name=pipe_name)

        # Set the model.
        self.interpreter.relax_disp.select_model(model=model)

        # Cluster everything.
        self.interpreter.relax_disp.cluster(cluster_id='all', spin_id=":135-137")

        # Copy the data.
        self.interpreter.value.copy(pipe_from='R2eff', pipe_to=pipe_name, param='r2eff')

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
        self.interpreter.minimise.execute(min_algor='simplex', func_tol=1e-10, max_iter=1000)

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
        self.assertAlmostEqual(spin135S.r2[r20_key1], 28.2493445347425, 4)
        self.assertAlmostEqual(spin135S.r2[r20_key2], 31.7517352342937, 4)
        self.assertAlmostEqual(spin135S.pA, 0.836591714049569, 4)
        self.assertAlmostEqual(spin135S.dw, 0.583003004605869, 4)
        self.assertAlmostEqual(spin135S.dwH, 0.0361441894065963, 4)
        self.assertAlmostEqual(spin135S.kex/100, 241.806464344233/100, 4)
        self.assertAlmostEqual(spin135S.chi2, 12.4224060116473, 4)

        # Checks for residue :135F.
        self.assertAlmostEqual(spin135F.r2[r20_key1], 42.7201844426839, 4)
        self.assertAlmostEqual(spin135F.r2[r20_key2], 57.3178718548898, 4)
        self.assertAlmostEqual(spin135F.pA, 0.836591714049569, 4)
        self.assertAlmostEqual(spin135F.dw, 0.805849748711916, 4)
        self.assertAlmostEqual(spin135F.dwH, 0.0215791669142752, 4)
        self.assertAlmostEqual(spin135F.kex/100, 241.806464344233/100, 4)
        self.assertAlmostEqual(spin135F.chi2, 12.4224060116473, 4)

        # Checks for residue :137S.
        self.assertAlmostEqual(spin137S.r2[r20_key1], 26.013412509919, 4)
        self.assertAlmostEqual(spin137S.r2[r20_key2], 30.5758092335097, 4)
        self.assertAlmostEqual(spin137S.pA, 0.836591714049569, 4)
        self.assertAlmostEqual(spin137S.dw, 0.688107406812537, 4)
        self.assertAlmostEqual(spin137S.dwH, 0.034446357344577, 4)
        self.assertAlmostEqual(spin137S.kex/100, 241.806464344233/100, 4)
        self.assertAlmostEqual(spin137S.chi2, 12.4224060116473, 4)

        # Checks for residue :137F.
        self.assertAlmostEqual(spin137F.r2[r20_key1], 46.696935090697, 4)
        self.assertAlmostEqual(spin137F.r2[r20_key2], 58.6023842513446, 4)
        self.assertAlmostEqual(spin137F.pA, 0.836591714049569, 4)
        self.assertAlmostEqual(spin137F.dw, 0.94978325541294, 4)
        self.assertAlmostEqual(spin137F.dwH, 1.5189362257653e-07, 4)
        self.assertAlmostEqual(spin137F.kex/100, 241.806464344233/100, 4)
        self.assertAlmostEqual(spin137F.chi2, 12.4224060116473, 4)


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
        pipe_name = "%s - relax_disp" % model
        self.interpreter.pipe.copy(pipe_from='base pipe', pipe_to=pipe_name, bundle_to='relax_disp')
        self.interpreter.pipe.switch(pipe_name=pipe_name)

        # Set the model.
        self.interpreter.relax_disp.select_model(model=model)

        # Cluster everything.
        self.interpreter.relax_disp.cluster(cluster_id='all', spin_id=":135-137")

        # Copy the data.
        self.interpreter.value.copy(pipe_from='R2eff', pipe_to=pipe_name, param='r2eff')

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
        self.interpreter.minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-5, grad_tol=None, max_iter=100, constraints=True, scaling=True, verbosity=1)

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

        # Setup the data.
        self.setup_tp02_data_to_ns_r1rho_2site()

        # Alias the spins.
        spin1 = cdp.mol[0].res[0].spin[0]
        spin2 = cdp.mol[0].res[1].spin[0]

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=800e6)

        # Checks for residue :1.
        self.assertAlmostEqual(spin1.r2[r20_key1], 8.50207717367548, 4)
        self.assertAlmostEqual(spin1.r2[r20_key2], 13.4680429589972, 4)
        self.assertAlmostEqual(spin1.pA, 0.864523128842393, 4)
        self.assertAlmostEqual(spin1.dw, 8.85204828994151, 4)
        self.assertAlmostEqual(spin1.kex/1000, 1199.56359549637/1000, 4)
        self.assertAlmostEqual(spin1.chi2, 2.99182130153514, 4)

        # Checks for residue :2.
        self.assertAlmostEqual(spin2.r2[r20_key1], 10.2099357790203, 4)
        self.assertAlmostEqual(spin2.r2[r20_key2], 16.2137648697873, 4)
        self.assertAlmostEqual(spin2.pA, 0.836488681031685, 4)
        self.assertAlmostEqual(spin2.dw, 9.5505714779503, 4)
        self.assertAlmostEqual(spin2.kex/1000, 1454.45726998929/1000, 4)
        self.assertAlmostEqual(spin2.chi2, 0.000402231563481261, 4)


    def test_tp02_data_to_ns_r1rho_2site_cluster(self, model=None):
        """Test the relaxation dispersion 'NS R1rho 2-site' model fitting against the 'TP02' test data, when performing clustering."""

        # Setup the data.
        self.setup_tp02_data_to_ns_r1rho_2site(clustering=True)

        # Alias the spins.
        spin1 = cdp.mol[0].res[0].spin[0]
        spin2 = cdp.mol[0].res[1].spin[0]

        # The R20 keys.
        r20_key1 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=500e6)
        r20_key2 = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=800e6)

        # Checks for residue :1.
        self.assertAlmostEqual(spin1.r2[r20_key1], 8.48607207881462, 4)
        self.assertAlmostEqual(spin1.r2[r20_key2], 13.4527609061722, 4)
        self.assertAlmostEqual(spin1.pA, 0.863093838784425, 4)
        self.assertAlmostEqual(spin1.dw, 8.86218096536618, 4)
        self.assertAlmostEqual(spin1.kex/1000, 1186.22749648299/1000, 4)
        self.assertAlmostEqual(spin1.chi2, 3.09500996065247, 4)

        # Checks for residue :2.
        self.assertAlmostEqual(spin2.r2[r20_key1], 10.4577906018883, 4)
        self.assertAlmostEqual(spin2.r2[r20_key2], 16.4455550953792, 4)
        self.assertAlmostEqual(spin2.pA, 0.863093838784425, 4)
        self.assertAlmostEqual(spin2.dw, 11.5841168862587, 4)
        self.assertAlmostEqual(spin2.kex/1000, 1186.22749648299/1000, 4)
        self.assertAlmostEqual(spin2.chi2, 3.09500996065247, 4)


    def test_tp02_data_to_mp05(self):
        """Test the dispersion 'MP05' model fitting against the 'TP02' test data."""

        # Fixed time variable and the models.
        ds.fixed = True
        ds.models = ['R2eff', 'MP05']

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_disp'+sep+'r1rho_off_res_tp02.py')

        # Switch back to the data pipe for the optimisation.
        self.interpreter.pipe.switch('MP05 - relax_disp')

        # The equivalent MP05 parameters.
        r1rho_prime = [[10.0058086343329, 15.005806870124], [12.0766320470785, 18.0767503536277]]
        pA = [0.775055484521586, 0.500000000036595]
        kex = [1235.20361276079, 2378.31403454691]
        delta_omega = [7.08194146569694, 5.4083562844306]
        chi2 = [0.0370400968727768, 0.182141732163934]

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

        # Check each spin.
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

        # Switch back to the data pipe for the optimisation.
        self.interpreter.pipe.switch('TAP03 - relax_disp')

        # The equivalent TAP03 parameters.
        r1rho_prime = [[10.0058156589442, 15.005818505006], [12.0766046472748, 18.076648462452]]
        pA = [0.775042569092891, 0.500000000229685]
        kex = [1235.20852748765, 2379.47085580169]
        delta_omega = [7.08176806468445, 5.40708372863538]
        chi2 = [0.0371366837083293, 0.182212857256044]

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
        self.interpreter.pipe.switch('TAP03 - relax_disp')
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
        self.interpreter.pipe.switch('TP02 - relax_disp')
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


    def test_value_write_calc_rotating_frame_params_int(self):
        """System test of the value.write function to write intensities for an R1rho setup.
        This system test is to make sure, that modifying the API for special parameters theta and w_eff does not alter the functionality value.write.

        This uses the data of the saved state attached to U{bug #21344<https://gna.org/bugs/?21344>}.
        """

        # Load the state.
        statefile = status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21344_trunc.bz2'
        self.interpreter.state.load(statefile, force=True)

        # Set filepaths.
        int_filepath = ds.tmpdir+sep+'int.out'

        # Write out the intensity parameter file.
        # The writing out of intensity file is to make sure the API function retains its function after modification for special parameters.
        self.interpreter.value.write(param='peak_intensity', file='int.out', dir=ds.tmpdir, scaling=1.0, force=True)

        # Test the file exists.
        self.assert_(access(int_filepath, F_OK))

        # Open the files for testing.
        int_file = open(int_filepath, 'r')

        # Loop over the intensity file to test values.
        for line in int_file:
            # Skip lines starting with #.
            if line[0] == "#":
                continue

            # Split the line
            linesplit = line.split()

            # Assume values
            if linesplit[0] == "None" and linesplit[1] == "5" and linesplit[2] == "I":
                self.assertEqual(linesplit[5], "115571.4")
            elif linesplit[0] == "None" and linesplit[1] == "6" and linesplit[2] == "S":
                self.assertEqual(linesplit[5], "68377.52")
            elif linesplit[0] == "None" and linesplit[1] == "8" and linesplit[2] == "S":
                self.assertEqual(linesplit[5], "9141.689")
            elif linesplit[0] == "None" and linesplit[1] == "9" and linesplit[2] == "A":
                self.assertEqual(linesplit[5], "29123.77")
            elif linesplit[0] == "None" and linesplit[1] == "10" and linesplit[2] == "L":
                self.assertEqual(linesplit[5], "58914.94")

        # Close files
        int_file.close()


    def test_value_write_calc_rotating_frame_params_theta(self):
        """System test of the value.write function to write return values of theta from calc_rotating_frame_params() function for an R1rho setup.

        This uses the data of the saved state attached to U{bug #21344<https://gna.org/bugs/?21344>}.
        """

        # Load the state.
        statefile = status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21344_trunc.bz2'
        self.interpreter.state.load(statefile, force=True)

        # Set filepaths.
        theta_filepath = ds.tmpdir+sep+'theta.out'

        # Write out the theta parameter file.
        self.interpreter.value.write(param='theta', file='theta.out', dir=ds.tmpdir, scaling=1.0, force=True)

        # Test the file exists.
        self.assert_(access(theta_filepath, F_OK))

        # Open the files for testing.
        theta_file = open(theta_filepath, 'r')

        # Loop over the theta file to test values.
        for line in theta_file:
            # Skip lines starting with #.
            if line[0] == "#":
                continue
            # Print lines, not including newline character.
            print(line[:-1])

            # Split the line
            linesplit = line.split()

            # Assume values
            if linesplit[0] == "None" and linesplit[1] == "5" and linesplit[2] == "I":
                self.assertNotEqual(linesplit[5], "None")
            elif linesplit[0] == "None" and linesplit[1] == "6" and linesplit[2] == "S":
                self.assertNotEqual(linesplit[5], "None")
            elif linesplit[0] == "None" and linesplit[1] == "8" and linesplit[2] == "S":
                self.assertNotEqual(linesplit[5], "None")
            elif linesplit[0] == "None" and linesplit[1] == "9" and linesplit[2] == "A":
                self.assertNotEqual(linesplit[5], "None")
            elif linesplit[0] == "None" and linesplit[1] == "10" and linesplit[2] == "L":
                self.assertNotEqual(linesplit[5], "None")

        # Close files
        theta_file.close()


    def test_value_write_calc_rotating_frame_params_w_eff(self):
        """System test of the value.write function to write return values of w_eff from calc_rotating_frame_params() function for an R1rho setup.

        This uses the data of the saved state attached to U{bug #21344<https://gna.org/bugs/?21344>}.
        """

        # Load the state.
        statefile = status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21344_trunc.bz2'
        self.interpreter.state.load(statefile, force=True)

        # Set filepaths.
        w_eff_filepath = ds.tmpdir+sep+'w_eff.out'

        # Write out the w_eff parameter file.
        self.interpreter.value.write(param='w_eff', file='w_eff.out', dir=ds.tmpdir, scaling=1.0, force=True)

        # Test the file exists.
        self.assert_(access(w_eff_filepath, F_OK))

        # Open the files for testing.
        w_eff_file = open(w_eff_filepath, 'r')

        # Loop over the w_eff file to test values.
        for line in w_eff_file:
            # Skip lines starting with #.
            if line[0] == "#":
                continue
            # Print lines, not including newline character.
            print(line[:-1])

            # Split the line
            linesplit = line.split()

            # Assume values
            if linesplit[0] == "None" and linesplit[1] == "5" and linesplit[2] == "I":
                self.assertNotEqual(linesplit[5], "None")
            elif linesplit[0] == "None" and linesplit[1] == "6" and linesplit[2] == "S":
                self.assertNotEqual(linesplit[5], "None")
            elif linesplit[0] == "None" and linesplit[1] == "8" and linesplit[2] == "S":
                self.assertNotEqual(linesplit[5], "None")
            elif linesplit[0] == "None" and linesplit[1] == "9" and linesplit[2] == "A":
                self.assertNotEqual(linesplit[5], "None")
            elif linesplit[0] == "None" and linesplit[1] == "10" and linesplit[2] == "L":
                self.assertNotEqual(linesplit[5], "None")

        # Close files
        w_eff_file.close()


    def test_value_write_calc_rotating_frame_params_auto_analysis(self):
        """System test of the auto_analysis value.write function to write theta and w_eff values for an R1rho setup.

        This uses the data of the saved state attached to U{bug #21344<https://gna.org/bugs/?21344>}.
        """

        # Load the state.
        statefile = status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21344.bz2'
        self.interpreter.state.load(statefile, force=True)

        # Set pipe name, bundle and type.
        pipe_name = 'base pipe'
        pipe_bundle = 'relax_disp'
        pipe_type = 'relax_disp'

        # The path to the data files.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013'

        # Deselect all spins
        self.interpreter.deselect.all()

        # Specify spins to be selected.
        select_spin_ids = [
        ":13@N",
        ":15@N",
        ":16@N",
        ":25@N",
        ":26@N",
        ":28@N",
        ":39@N",
        ":40@N",
        ":41@N",
        ":43@N",
        ":44@N",
        ":45@N",
        ":49@N",
        ":52@N",
        ":53@N"]

        # Reverse the selection for the spins.
        for curspin in select_spin_ids:
            print("Selecting spin %s"%curspin)
            self.interpreter.deselect.reverse(spin_id=curspin)

        # Read the R1 data
        self.interpreter.relax_data.read(ri_id='R1', ri_type='R1', frq=cdp.spectrometer_frq_list[0], file='R1_fitted_values.txt', dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

        # The dispersion models.
        MODELS = ['R2eff']

        # The grid search size (the number of increments per dimension).
        GRID_INC = 4

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        MC_NUM = 3

        # Model selection technique.
        MODSEL = 'AIC'

        # Execute the auto-analysis (fast).
        # Standard parameters are: func_tol = 1e-25, grad_tol = None, max_iter = 10000000,
        OPT_FUNC_TOL = 1e-1
        relax_disp.Relax_disp.opt_func_tol = OPT_FUNC_TOL
        OPT_MAX_ITERATIONS = 1000
        relax_disp.Relax_disp.opt_max_iterations = OPT_MAX_ITERATIONS

        # Run the analysis.
        relax_disp.Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=ds.tmpdir, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL)

        ## Check for file creation
        # Set filepaths.
        theta_filepath = ds.tmpdir+sep+MODELS[0]+sep+'theta.out'
        w_eff_filepath = ds.tmpdir+sep+MODELS[0]+sep+'w_eff.out'

        # Test the files exists.
        self.assert_(access(theta_filepath, F_OK))
        self.assert_(access(w_eff_filepath, F_OK))

        # Open the files for testing.
        theta_file = open(theta_filepath, 'r')
        theta_result = [
            "# Parameter description:  Rotating frame tilt angle : ( theta = arctan(w_1 / Omega) ) (rad).\n",
            "#\n",
            "# mol_name    res_num    res_name    spin_num    spin_name    r1rho_799.77739910_118.078_1341.110    sd(r1rho_799.77739910_118.078_1341.110)    r1rho_799.77739910_118.078_1648.500    sd(r1rho_799.77739910_118.078_1648.500)    r1rho_799.77739910_118.078_431.000    sd(r1rho_799.77739910_118.078_431.000)    r1rho_799.77739910_118.078_651.200    sd(r1rho_799.77739910_118.078_651.200)    r1rho_799.77739910_118.078_800.500    sd(r1rho_799.77739910_118.078_800.500)    r1rho_799.77739910_118.078_984.000    sd(r1rho_799.77739910_118.078_984.000)    r1rho_799.77739910_124.247_1341.110    sd(r1rho_799.77739910_124.247_1341.110)    r1rho_799.77739910_130.416_1341.110    sd(r1rho_799.77739910_130.416_1341.110)    r1rho_799.77739910_130.416_1648.500    sd(r1rho_799.77739910_130.416_1648.500)    r1rho_799.77739910_130.416_800.500    sd(r1rho_799.77739910_130.416_800.500)    r1rho_799.77739910_142.754_1341.110    sd(r1rho_799.77739910_142.754_1341.110)    r1rho_799.77739910_142.754_800.500    sd(r1rho_799.77739910_142.754_800.500)    r1rho_799.77739910_179.768_1341.110    sd(r1rho_799.77739910_179.768_1341.110)    r1rho_799.77739910_241.459_1341.110    sd(r1rho_799.77739910_241.459_1341.110)    \n",
            "None          5          I           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          6          S           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          8          S           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          9          A           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          10         L           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          11         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          12         D           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          13         L           None        N                1.83827367612531                   None                                           1.79015307643158                   None                                            2.2768687598681                  None                                          2.08461171779445                  None                                          2.00120623474388                  None                                          1.92825070277699                  None                                          1.47212860033516                   None                                           1.12978017906854                   None                                           1.20415336139956                   None                                          0.901691390796334                  None                                         0.687390207543568                   None                                          0.455635480573046                  None                                         0.281637123971289                   None                                          0.138259661766539                   None                                       \n",
            "None          14         L           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          15         R           None        N                1.58367544790673                   None                                           1.58127411936947                   None                                           1.61085209029811                  None                                          1.59731540507347                  None                                          1.59237108385522                  None                                          1.58834866344307                  None                                           1.2251048782537                   None                                          0.938142786712004                   None                                           1.03297495592991                   None                                          0.683284686224254                  None                                         0.594447788256641                   None                                          0.383528609383686                  None                                         0.262780814059893                   None                                          0.133469839450564                   None                                       \n",
            "None          16         T           None        N                1.40984232256624                   None                                           1.43947245672073                   None                                           1.10299856647417                  None                                          1.24811470332083                  None                                          1.30521602599932                  None                                          1.35302443831853                  None                                          1.07923777467974                   None                                          0.833345927788896                   None                                          0.934350308974616                   None                                          0.581325254389991                  None                                         0.543659670184793                   None                                          0.346238480454282                  None                                         0.251454336191817                   None                                          0.130436714663781                   None                                       \n",
            "None          17         L           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          18         K           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          19         S           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          21         S           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          24         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          25         Q           None        N                1.81569700258844                   None                                           1.77137827615015                   None                                           2.23175875585624                  None                                          2.04612705363098                  None                                           1.9673155780155                  None                                          1.89908711012298                  None                                          1.44829660124856                   None                                           1.11023386429581                   None                                           1.18716091371256                   None                                          0.877306975624962                  None                                         0.677790118853413                   None                                          0.447932002242236                  None                                         0.279785379050945                   None                                          0.137802891887767                   None                                       \n",
            "None          26         Q           None        N                1.61128821168674                   None                                           1.60374392042003                   None                                           1.69619923953765                  None                                          1.65403989292986                  None                                          1.63856717205868                  None                                          1.62595755714564                  None                                          1.24977859227795                   None                                          0.956353494917591                   None                                           1.04972090035774                   None                                          0.702164059520172                  None                                         0.603227813742091                   None                                          0.390116910781037                  None                                         0.264658552037535                   None                                          0.133960994297096                   None                                       \n",
            "None          27         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          28         Q           None        N                1.65182797011356                   None                                           1.63676707684161                   None                                           1.81830827892972                  None                                           1.7365089711986                  None                                          1.70601955220877                  None                                          1.68102938663686                  None                                          1.28685736157369                   None                                          0.984047498595701                   None                                            1.0749792109454                   None                                          0.731585685663053                  None                                         0.616577997665602                   None                                          0.400219205533665                  None                                         0.267471993812649                   None                                          0.134690869499646                   None                                       \n",
            "None          29         V           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          30         L           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          31         N           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          32         I           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          33         L           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          34         K           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          35         S           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          36         N           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          38         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          39         L           None        N                1.76426439181176                   None                                           1.72885318885161                   None                                           2.11826300085737                  None                                          1.95430201082222                  None                                          1.88794717058464                  None                                          1.83172922971397                  None                                          1.39549951193417                   None                                           1.06783946148624                   None                                           1.14997013232702                   None                                          0.826128785942585                  None                                         0.657105386950171                   None                                          0.431542911580536                  None                                         0.275725736430539                   None                                          0.136791385554619                   None                                       \n",
            "None          40         M           None        N                 1.5521741199158                   None                                           1.55564594516135                   None                                           1.51290906497298                  None                                          1.53245929150759                  None                                          1.53960430408466                  None                                          1.54541832596591                  None                                          1.19750223001929                   None                                          0.917959090226757                   None                                           1.01428385962747                   None                                          0.662779584695967                  None                                         0.584708929219264                   None                                          0.376271266885303                  None                                         0.260671619214194                   None                                          0.132914250767089                   None                                       \n",
            "None          41         A           None        N                1.68339451828261                   None                                           1.66252964414082                   None                                           1.90911961276946                  None                                          1.79959323497326                  None                                          1.75801925517113                  None                                          1.72370710837265                  None                                          1.31646868936419                   None                                           1.00647189763597                   None                                           1.09525348649914                   None                                           0.75605702767542                  None                                         0.627395557358039                   None                                          0.408481831044309                  None                                         0.269716174238842                   None                                          0.135267948387412                   None                                       \n",
            "None          42         A           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          43         F           None        N                1.58506597154432                   None                                           1.58240542750303                   None                                           1.61517196062351                  None                                          1.60017740004898                  None                                          1.59469990835425                  None                                          1.59024353162528                  None                                          1.22633651794829                   None                                          0.939047922181951                   None                                           1.03380990731605                   None                                          0.684214484755514                  None                                         0.594884298549546                   None                                          0.383855128702894                  None                                         0.262874695048502                   None                                           0.13349447283116                   None                                       \n",
            "None          44         I           None        N                1.57575471961837                   None                                           1.57483015671791                   None                                           1.58622388390755                  None                                          1.58100758841935                  None                                          1.57910319967536                  None                                          1.57755415552211                  None                                          1.21811077066835                   None                                          0.933010299763027                   None                                           1.02823520295828                   None                                           0.67802911457195                  None                                         0.591972285081647                   None                                          0.381678892926696                  None                                         0.262247347241724                   None                                          0.133329708422379                   None                                       \n",
            "None          45         K           None        N                1.77147501495754                   None                                           1.73479633022489                   None                                           2.13509660780385                  None                                          1.96751045408372                  None                                          1.89924480319914                  None                                          1.84124387452692                  None                                          1.40277881643715                   None                                           1.07361367582571                   None                                           1.15506365550891                   None                                          0.832963505534767                  None                                         0.659913187081268                   None                                          0.433751178249555                  None                                         0.276282572106685                   None                                           0.13693095791902                   None                                       \n",
            "None          46         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          48         T           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          49         A           None        N                2.00297059962685                   None                                           1.92978318052058                   None                                           2.53305709323468                  None                                          2.33052197276846                  None                                          2.22870514722639                  None                                          2.13201782446864                  None                                           1.6587904412969                   None                                           1.29333162369472                   None                                           1.34311052758116                   None                                           1.12559033900783                  None                                         0.770195063841652                   None                                          0.524846264860003                  None                                         0.296857751274362                   None                                          0.141908833673671                   None                                       \n",
            "None          50         K           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          51         Y           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          52         V           None        N                1.82421571143794                   None                                           1.77845404105203                   None                                           2.24910726268822                  None                                          2.06078232916932                  None                                          1.98017451806059                  None                                          1.91012195713554                  None                                          1.45724107606646                   None                                           1.11753869321304                   None                                           1.19352234944057                   None                                          0.886361068343012                  None                                         0.681372607920812                   None                                          0.450799407357501                  None                                         0.280478735779163                   None                                          0.137974257665877                   None                                       \n",
            "None          53         A           None        N                2.05019708195234                   None                                           1.97089957318506                   None                                           2.58789168363698                  None                                          2.39027806684801                  None                                          2.28731354878582                  None                                           2.1872118539319                  None                                           1.7165709935896                   None                                           1.34832362477229                   None                                           1.38879751095815                   None                                            1.2085314357749                  None                                         0.799450059125864                   None                                          0.550583841461621                  None                                          0.30195492609136                   None                                          0.143090604877102                   None                                       \n",
            "None          54         N           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          55         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          57         G           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          58         M           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          59         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n"
        ]
        # Check the created theta file.
        lines = theta_file.readlines()
        for i in range(len(lines)):
            # Test lines starting with #
            if theta_result[i][0] == "#":
                self.assertEqual(theta_result[i], lines[i])
            # If the line is equal each other, make a line comparison. This should catch lines with None values.
            if theta_result[i] == lines[i]:
                self.assertEqual(theta_result[i], lines[i])
            # If the line is not equal each other, make a slower comparison of values.
            else:
                # Print lines if they don't match. To help find differences.
                print(theta_result[i])
                print(lines[i])

                # First test first 62 characters containing spin information
                self.assertEqual(theta_result[i][:62], lines[i][:62])

                # Make a string split after 62 characters. Select each second element, so None values are skipped.
                theta_result_s = theta_result[i][62:].split()[::2]
                print(theta_result_s )
                lines_s = lines[i][62:].split()[::2]
                print(lines_s)
                # Loop over the value elements
                for j in range(len(lines_s)):
                    print(theta_result_s[j], lines_s[j])
                    # Assume a precision to digits.
                    self.assertAlmostEqual(float(theta_result_s[j]), float(lines_s[j]), 14)

        # Close file
        theta_file.close()

        w_eff_file = open(w_eff_filepath, 'r')
        w_eff_result = [
            "# Parameter description:  Effective field in rotating frame : ( w_eff = sqrt(Omega^2 + w_1^2) ) (rad.s^-1).\n",
            "#\n",
            "# mol_name    res_num    res_name    spin_num    spin_name    r1rho_799.77739910_118.078_1341.110    sd(r1rho_799.77739910_118.078_1341.110)    r1rho_799.77739910_118.078_1648.500    sd(r1rho_799.77739910_118.078_1648.500)    r1rho_799.77739910_118.078_431.000    sd(r1rho_799.77739910_118.078_431.000)    r1rho_799.77739910_118.078_651.200    sd(r1rho_799.77739910_118.078_651.200)    r1rho_799.77739910_118.078_800.500    sd(r1rho_799.77739910_118.078_800.500)    r1rho_799.77739910_118.078_984.000    sd(r1rho_799.77739910_118.078_984.000)    r1rho_799.77739910_124.247_1341.110    sd(r1rho_799.77739910_124.247_1341.110)    r1rho_799.77739910_130.416_1341.110    sd(r1rho_799.77739910_130.416_1341.110)    r1rho_799.77739910_130.416_1648.500    sd(r1rho_799.77739910_130.416_1648.500)    r1rho_799.77739910_130.416_800.500    sd(r1rho_799.77739910_130.416_800.500)    r1rho_799.77739910_142.754_1341.110    sd(r1rho_799.77739910_142.754_1341.110)    r1rho_799.77739910_142.754_800.500    sd(r1rho_799.77739910_142.754_800.500)    r1rho_799.77739910_179.768_1341.110    sd(r1rho_799.77739910_179.768_1341.110)    r1rho_799.77739910_241.459_1341.110    sd(r1rho_799.77739910_241.459_1341.110)    \n",
            "None          5          I           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          6          S           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          8          S           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          9          A           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          10         L           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          11         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          12         D           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          13         L           None        N                8737.12883908829                   None                                           10612.1226552258                   None                                           3558.93734069587                  None                                          4698.27194621826                  None                                          5534.46153956037                  None                                          6599.82570817753                  None                                          8467.62674839481                   None                                           9318.00441649087                   None                                           11095.2662520767                   None                                           6412.33580591254                  None                                          13279.9803044242                   None                                            11430.254637056                  None                                          30318.7268264644                   None                                           61141.1080046448                   None                                       \n",
            "None          14         L           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          15         R           None        N                8427.14155005377                   None                                           10358.3995676635                   None                                           2710.22680763322                  None                                          4093.04942975722                  None                                          5030.86065069262                  None                                          6183.60685459024                  None                                          8956.28403254202                   None                                           10448.6627754369                   None                                           12060.4428066937                   None                                           7966.64282975241                  None                                          15045.8392092364                   None                                           13441.3586252373                  None                                          32438.4764809909                   None                                           63321.5201471181                   None                                       \n",
            "None          16         T           None        N                 8536.7818857229                   None                                            10447.792678989                   None                                           3034.01707453628                  None                                           4314.2767521567                  None                                          5212.43600885913                  None                                          6332.21319855067                  None                                          9558.14311447582                   None                                           11384.2336494604                   None                                           12879.4604966293                   None                                           9159.34604475399                  None                                          16290.1746838959                   None                                           14821.0200530829                  None                                          33866.5933527757                   None                                           64785.3205696403                   None                                       \n",
            "None          17         L           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          18         K           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          19         S           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          21         S           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          24         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          25         Q           None        N                8685.60895531182                   None                                           10569.7459677762                   None                                           3430.51272680396                  None                                          4601.75421490393                  None                                          5452.76508815826                  None                                          6531.46859076009                  None                                          8490.06475886501                   None                                           9406.58372902508                   None                                           11169.7602637607                   None                                           6540.38696356753                  None                                          13437.7348017798                   None                                           11613.1632549021                  None                                          30514.0741594726                   None                                           61342.4792156782                   None                                       \n",
            "None          26         Q           None        N                8433.35533683544                   None                                           10363.4554631194                   None                                           2729.48656005151                  None                                          4105.82770792005                  None                                          5041.26238350827                  None                                          6192.07245313098                  None                                          8880.08366342131                   None                                           10312.6868786802                   None                                           11942.8320576165                   None                                           7787.44854491812                  None                                          14853.4987024375                   None                                           13225.7048162038                  None                                          32213.6690023282                   None                                           63090.7407990801                   None                                       \n",
            "None          27         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          28         Q           None        N                8454.18308422202                   None                                           10380.4112885894                   None                                           2793.17494362899                  None                                          4148.43953208179                  None                                          5076.02756135055                  None                                          6220.40920270029                  None                                          8777.91538040813                   None                                           10118.8737706315                   None                                           11775.8792998529                   None                                           7528.90766101027                  None                                          14572.4015102398                   None                                            12909.211050939                  None                                          31882.8171856889                   None                                           62750.9120842199                   None                                       \n",
            "None          29         V           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          30         L           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          31         N           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          32         I           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          33         L           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          34         K           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          35         S           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          36         N           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          38         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          39         L           None        N                 8586.6405431352                   None                                           10488.5710521378                   None                                           3171.59430904777                  None                                          4412.11227722123                  None                                          5293.69814015286                  None                                          6399.27143075725                  None                                          8557.58926327909                   None                                           9617.45773774313                   None                                           11347.9169998729                   None                                           6840.20010813426                  None                                          13795.1250622375                   None                                           12024.9041436853                  None                                           30951.651485352                   None                                           61793.2130509111                   None                                       \n",
            "None          40         M           None        N                8427.90394711227                   None                                           10359.0198301036                   None                                           2712.59646573568                  None                                          4094.61889210019                  None                                          5032.13762965554                  None                                           6184.6458240746                  None                                          9049.68452800053                   None                                           10607.7913029633                   None                                           12198.5639821231                   None                                           8174.23271685285                  None                                          15266.4924700447                   None                                           13687.9010998756                  None                                          32694.9043143038                   None                                           63584.6371927381                   None                                       \n",
            "None          41         A           None        N                8480.14299737436                   None                                           10401.5648897003                   None                                           2870.79081440785                  None                                          4201.09083283266                  None                                          5119.14733505123                  None                                          6255.64579267482                  None                                          8706.50768957471                   None                                           9972.71017314947                   None                                           11650.5225246067                   None                                           7331.28858930568                  None                                          14354.1616183112                   None                                           12662.3378547029                  None                                          31623.9195264738                   None                                           62484.8290612112                   None                                       \n",
            "None          42         A           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          43         F           None        N                8427.30062786474                   None                                           10358.5289868368                   None                                            2710.7214015056                  None                                          4093.37694357637                  None                                          5031.12711571215                  None                                          6183.82364721878                  None                                          8952.31975962078                   None                                           10441.7375680915                   None                                           12054.4435931163                   None                                           7957.55789315654                  None                                          15036.1316712316                   None                                           13430.4914212645                  None                                          32427.1596037519                   None                                           63309.9050677925                   None                                       \n",
            "None          44         I           None        N                8426.54623319716                   None                                           10357.9152496503                   None                                            2708.3751705368                  None                                          4091.82359712664                  None                                          5029.86337809029                  None                                          6182.79552045043                  None                                          8979.12144335458                   None                                           10488.2688526334                   None                                           12094.7720286018                   None                                           8018.51779989075                  None                                          15101.1843990883                   None                                           13503.2816173444                  None                                          32502.9389163062                   None                                           63387.6763306952                   None                                       \n",
            "None          45         K           None        N                8599.01176345321                   None                                           10498.7013581079                   None                                           3204.93649737055                  None                                          4436.14046641897                  None                                          5313.74138343704                  None                                          6415.86177652694                  None                                          8546.79665373249                   None                                           9587.16245449134                   None                                           11322.2529042385                   None                                           6797.53838612575                  None                                          13745.1536613763                   None                                           11967.5433300612                  None                                          30890.8603419261                   None                                           61730.6213936947                   None                                       \n",
            "None          46         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          48         T           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          49         A           None        N                9279.63849130869                   None                                           11063.0654625247                   None                                           4737.11992391463                  None                                          5643.40583860235                  None                                          6356.45614406507                  None                                          7302.87406141381                  None                                          8459.17105047661                   None                                           8761.54554569995                   None                                           10632.2343488142                   None                                           5572.92782399155                  None                                          12102.1714908775                   None                                           10037.6988885228                  None                                          28806.6916858172                   None                                           59579.0348769179                   None                                       \n",
            "None          50         K           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          51         Y           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          52         V           None        N                8704.45610117774                   None                                           10585.2389163429                   None                                            3477.9549539207                  None                                          4637.22923167743                  None                                          5482.73656118686                  None                                           6556.5108895527                  None                                          8481.06470969555                   None                                           9372.86414918436                   None                                           11141.3782476763                   None                                           6491.79686536093                  None                                          13378.2843939736                   None                                           11544.3205736882                  None                                            30440.62308788                   None                                           61266.7742546508                   None                                       \n",
            "None          53         A           None        N                9497.02860450276                   None                                           11246.0339326126                   None                                           5149.96766581255                  None                                          5994.15475647208                  None                                          6669.81232845336                  None                                          7577.19152075731                  None                                          8516.77431951689                   None                                           8639.36099840319                   None                                           10531.7750336522                   None                                           5378.79193153767                  None                                          11752.8060152439                   None                                           9613.59939949642                  None                                          28334.9153747994                   None                                           59090.2988815445                   None                                       \n",
            "None          54         N           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          55         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          57         G           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          58         M           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n",
            "None          59         Q           None        N            None                                   None                                       None                                   None                                       None                                  None                                      None                                  None                                      None                                  None                                      None                                  None                                      None                                   None                                       None                                   None                                       None                                   None                                       None                                  None                                      None                                   None                                       None                                  None                                      None                                   None                                       None                                   None                                       \n"
        ]
        # Check the created w_eff file.
        lines = w_eff_file.readlines()
        for i in range(len(lines)):
            # Test lines starting with #
            if w_eff_result[i][0] == "#":
                self.assertEqual(w_eff_result[i], lines[i])
            # If the line is equal each other, make a line comparison. This should catch lines with None values.
            if w_eff_result[i] == lines[i]:
                self.assertEqual(w_eff_result[i], lines[i])
            # If the line is not equal each other, make a slower comparison of values.
            else:
                # Print lines if they don't match. To help find differences.
                print(w_eff_result[i])
                print(lines[i])

                # First test first 62 characters containing spin information
                self.assertEqual(w_eff_result[i][:62], lines[i][:62])

                # Make a string split after 62 characters. Select each second element, so None values are skipped.
                w_eff_result_s = w_eff_result[i][62:].split()[::2]
                print(w_eff_result_s )
                lines_s = lines[i][62:].split()[::2]
                print(lines_s)
                # Loop over the value elements
                for j in range(len(lines_s)):
                    print(w_eff_result_s[j], lines_s[j])
                    # Assume a precision to digits.
                    self.assertAlmostEqual(float(w_eff_result_s[j]), float(lines_s[j]), 14)

        # Close file
        w_eff_file.close()


    def verify_r1rho_kjaergaard_missing_r1(self, models=None, result_dir_name=None, do_assert=True):
        """Verification of test_r1rho_kjaergaard_missing_r1."""

        # Check the kex value of residue 52
        #self.assertAlmostEqual(cdp.mol[0].res[41].spin[0].kex, ds.ref[':52@N'][6])

        # Print results for each model.
        print("\n\n################")
        print("Printing results")
        print("################\n")
        for model in models:
            # Skip R2eff model.
            if model == MODEL_R2EFF:
                continue

            # Switch to pipe.
            self.interpreter.pipe.switch(pipe_name='%s - relax_disp' % (model))
            print("\nModel: %s" % (model))

            # Loop over the spins.
            for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
                # Generate spin string.
                spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

                # Loop over the parameters.
                print("Optimised parameters for spin: %s" % (spin_string))
                for param in cur_spin.params + ['chi2']:
                    # Get the value.
                    if param in ['r1', 'r2']:
                        for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):
                            # Generate the R20 key.
                            r20_key = generate_r20_key(exp_type=exp_type, frq=frq)

                            # Get the value.
                            value = getattr(cur_spin, param)[r20_key]

                            # Print value.
                            print("%-10s %-6s %-6s %3.8f" % ("Parameter:", param, "Value:", value))

                            if do_assert:
                                # Compare values.
                                if spin_id == ':52@N':
                                    if param == 'r1':
                                        if model == MODEL_NOREX:
                                            self.assertAlmostEqual(value, 1.46328102)
                                        elif model == MODEL_DPL94:
                                            self.assertAlmostEqual(value, 1.45019848)
                                        elif model == MODEL_TP02:
                                            self.assertAlmostEqual(value, 1.54352369)
                                        elif model == MODEL_TAP03:
                                            self.assertAlmostEqual(value, 1.54354367)
                                        elif model == MODEL_MP05:
                                            self.assertAlmostEqual(value, 1.54354372)
                                        elif model == MODEL_NS_R1RHO_2SITE:
                                            self.assertAlmostEqual(value, 1.41321968, 5)

                                    elif param == 'r2':
                                        if model == MODEL_NOREX:
                                            self.assertAlmostEqual(value, 11.48040934)
                                        elif model == MODEL_DPL94:
                                            self.assertAlmostEqual(value, 10.16304887, 6)
                                        elif model == MODEL_TP02:
                                            self.assertAlmostEqual(value, 9.72772726, 6)
                                        elif model == MODEL_TAP03:
                                            self.assertAlmostEqual(value, 9.72759374, 6)
                                        elif model == MODEL_MP05:
                                            self.assertAlmostEqual(value, 9.72759220, 6)
                                        elif model == MODEL_NS_R1RHO_2SITE:
                                            self.assertAlmostEqual(value, 9.34602793, 5)

                    # For all other parameters.
                    else:
                        # Get the value.
                        value = getattr(cur_spin, param)

                        # Print value.
                        print("%-10s %-6s %-6s %3.8f" % ("Parameter:", param, "Value:", value))

                        if do_assert:
                            # Compare values.
                            if spin_id == ':52@N':
                                if param == 'phi_ex':
                                    if model == MODEL_DPL94:
                                        self.assertAlmostEqual(value, 0.07561937)

                                elif param == 'pA':
                                    if model == MODEL_TP02:
                                        self.assertAlmostEqual(value, 0.88807487)
                                    elif model == MODEL_TAP03:
                                        self.assertAlmostEqual(value, 0.88809318)
                                    elif model == MODEL_MP05:
                                        self.assertAlmostEqual(value, 0.88809321)
                                    elif model == MODEL_NS_R1RHO_2SITE:
                                        self.assertAlmostEqual(value, 0.94496541, 6)

                                elif param == 'dw':
                                    if model == MODEL_TP02:
                                        self.assertAlmostEqual(value, 1.08765638, 6)
                                    elif model == MODEL_TAP03:
                                        self.assertAlmostEqual(value, 1.08726698, 6)
                                    elif model == MODEL_MP05:
                                        self.assertAlmostEqual(value, 1.08726706, 6)
                                    elif model == MODEL_NS_R1RHO_2SITE:
                                        self.assertAlmostEqual(value, 1.55833321, 5)

                                elif param == 'kex':
                                    if model == MODEL_DPL94:
                                        self.assertAlmostEqual(value, 4419.03917195, 2)
                                    elif model == MODEL_TP02:
                                        self.assertAlmostEqual(value, 4904.70144883, 3)
                                    elif model == MODEL_TAP03:
                                        self.assertAlmostEqual(value, 4909.86877150, 3)
                                    elif model == MODEL_MP05:
                                        self.assertAlmostEqual(value, 4909.88110195, 3)
                                    elif model == MODEL_NS_R1RHO_2SITE:
                                        self.assertAlmostEqual(value, 5610.20221435, 2)

                                elif param == 'chi2':
                                    if model == MODEL_NOREX:
                                        self.assertAlmostEqual(value, 3363.95829122)
                                    elif model == MODEL_DPL94:
                                        self.assertAlmostEqual(value, 710.24767560)
                                    elif model == MODEL_TP02:
                                        self.assertAlmostEqual(value, 114.47142772)
                                    elif model == MODEL_TAP03:
                                        self.assertAlmostEqual(value, 114.27987534)
                                    elif model == MODEL_MP05:
                                        self.assertAlmostEqual(value, 114.28002272)
                                    elif model == MODEL_NS_R1RHO_2SITE:
                                        self.assertAlmostEqual(value, 134.14368365)


        # Print the final pipe.
        model = 'final'
        self.interpreter.pipe.switch(pipe_name='%s - relax_disp' % (model))
        print("\nFinal pipe")

        # Loop over the spins.
        for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
            # Generate spin string.
            spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

            # Loop over the parameters.
            print("Optimised model for spin: %s" % (spin_string))
            param = 'model'

            # Get the value.
            value = getattr(cur_spin, param)
            print("%-10s %-6s %-6s %6s" % ("Parameter:", param, "Value:", value))


        ### Now check some of the written out files.
        file_names = ['r1rho_prime', 'r1']

        for file_name_i in file_names:

            # Make the file name.
            file_name = "%s.out" % file_name_i

            # Get the file path.
            file_path = get_file_path(file_name, result_dir_name + sep + model)

            # Test the file exists.
            print("Testing file access to: %s"%file_path)
            self.assert_(access(file_path, F_OK))

            # Now open, and compare content, line by line.
            file_prod = open(file_path)
            lines_prod = file_prod.readlines()
            file_prod.close()

            # Loop over the lines.
            for i, line in enumerate(lines_prod):
                # Make the string test
                line_split = line.split()

                # Continue for comment lines.
                if line_split[0] == "#":
                    print(line),
                    continue

                # Assign the split of the line.
                mol_name, res_num, res_name, spin_num, spin_name, val, sd_error = line_split
                print(mol_name, res_num, res_name, spin_num, spin_name, val, sd_error)

                if res_num == '52':
                    # Assert that the value is not None.
                    self.assertNotEqual(val, 'None')
