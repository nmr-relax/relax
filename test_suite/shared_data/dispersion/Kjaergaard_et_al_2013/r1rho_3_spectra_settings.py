# Set settings for experiment
import os, math

NR_exp = -1

# The lock power to field, has been found in an calibration experiment.
# lock_powers = [35.0, 39.0, 41.0, 43.0, 46.0, 48.0]
spin_lock_field_strengths_Hz = {'35': 431.0, '39': 651.2, '41': 800.5, '43': 984.0, '46': 1341.11, '48': 1648.5}
ncycs = [0, 4, 10, 14, 20, 40]

# Load the experiments settings file.
expfile = open('exp_parameters_sort.txt','r')
expfileslines = expfile.readlines()[:NR_exp]
expfile.close()

# In MHz
yOBS = 81.050
# In ppm
yCAR = 118.078
centerPPM_N15 = yCAR

#gyro1H = 26.7522212E7
#gyro15N = 2.7126E7

writefile = open('omega_rf_ppm.txt','w')

## Read the chemical shift data.
chemical_shift.read(file='peaks_corr_final.list', dir=None)

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
        spin_lock_field_strength = spin_lock_field_strengths_Hz[dpwr2slock]

        # Calculate spin_lock time
        time_sl = 2*ncyc*trim

        # Load the R1 data.
        rxlabel = "%s_%s"%(deltadof2, dpwr2slock)
        rx_dir = os.path.join('rx', rxlabel)
        #relax_data.read(ri_id=rxlabel, ri_type='R1', frq=set_sfrq*1e6, file='rx.out', dir=rx_dir, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

        # Define file name for peak list.
        FNAME = "%s_%s_%s_%s_max_standard.ser"%(I, deltadof2, dpwr2slock, ncyc)
        sp_id = "%s_%s_%s_%s"%(I, deltadof2, dpwr2slock, ncyc)

        # Load the peak intensities.
        spectrum.read_intensities(file=FNAME, dir=os.path.join(os.getcwd(),"peak_lists"), spectrum_id=sp_id, int_method='height')

        # Set the peak intensity errors, as defined as the baseplane RMSD.
        spectrum.baseplane_rmsd(error=1.33e+03, spectrum_id=sp_id)

        # Set the relaxation dispersion experiment type.
        relax_disp.exp_type(spectrum_id=sp_id, exp_type='R1rho')

        # Set The spin-lock field strength, nu1, in Hz
        relax_disp.spin_lock_field(spectrum_id=sp_id, field=spin_lock_field_strength)

        # Calculating the spin-lock offset in ppm, from offsets values provided in Hz.
        #frq_N15_Hz = set_sfrq * 1E6 * gyro15N / gyro1H
        frq_N15_Hz = yOBS * 1E6
        offset_ppm_N15 = float(deltadof2) / frq_N15_Hz * 1E6
        omega_rf_ppm = centerPPM_N15 + offset_ppm_N15
        writefile.write("%s %s %s %s\n"%(frq_N15_Hz, centerPPM_N15, offset_ppm_N15, omega_rf_ppm))

        # Set The spin-lock offset, omega_rf, in ppm.
        relax_disp.spin_lock_offset(spectrum_id=sp_id, offset=omega_rf_ppm)

        # Set the relaxation times (in s).
        relax_fit.relax_time(time=time_sl, spectrum_id=sp_id)

        # Set the spectrometer frequency.
        spectrometer.frequency(id=sp_id, frq=set_sfrq, units='MHz')

writefile.close()
