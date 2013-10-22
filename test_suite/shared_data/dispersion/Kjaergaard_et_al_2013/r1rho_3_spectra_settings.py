# Set settings for experiment
import os, math

NR_exp = -1

# The lock power to field, has been found in an calibration experiment.
# lock_powers = [35.0, 39.0, 41.0, 43.0, 46.0, 48.0]
spin_lock_field_strengths_Hz = {'35': 321.1, '39': 509., '41': 640.8, '43': 806.7, '46': 1139.6, '48': 1434.7}
ncycs = [0, 4, 10, 14, 20, 40]

# dw(ppm) = dw(rad.s^-1) * 10^6 * 1/(2*pi) * (gyro1H/(gyro15N*spectrometer_freq)) = 2.45E3 * 1E6 / (2 * math.pi) * (26.7522212E7/(-2.7126E7 * 599.8908622E6)) = -6.41 ppm.
gyro1H = 26.7522212E7
gyro15N = 2.7126E7

# Load the experiments settings file.
expfile = open('exp_parameters_sort.txt','r')
expfileslines = expfile.readlines()[:NR_exp]
expfile.close()

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
        #offset_ppm = 

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

        omega_rf_ppm_direct = float(deltadof2) * 1E6 * 1/(2 * math.pi) * (1 / ( set_sfrq*1E6 ) )
        omega_rf_ppm_indirect = float(deltadof2) * 1E6 * 1/(2 * math.pi) * (gyro1H / (gyro15N * set_sfrq*1E6 ) )
        writefile.write("%s %s \n"%(omega_rf_ppm_direct, omega_rf_ppm_indirect))

        # Set The spin-lock offset, omega_rf, in ppm.
        relax_disp.spin_lock_offset(spectrum_id=sp_id, offset=omega_rf_ppm_indirect)

        # Set the relaxation times.
        relax_fit.relax_time(time=time_sl, spectrum_id=sp_id)

        # Set the spectrometer frequency.
        spectrometer.frequency(id=sp_id, frq=set_sfrq, units='MHz')


writefile.close()
