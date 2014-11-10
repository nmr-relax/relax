###############################################################################
#                                                                             #
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
from os import getcwd, sep

# relax module imports.
from status import Status; status = Status()

#data_path = getcwd()
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013'

# Read the spins.
spectrum.read_spins(file='1_0_46_0_max_standard.ser', dir=data_path+sep+'peak_lists')

# Name the isotope for field strength scaling.
spin.isotope(isotope='15N')

# Load the experiments settings file.
expfile = open(data_path+sep+'exp_parameters_sort.txt', 'r')
expfileslines = expfile.readlines()
expfile.close()

# In MHz
yOBS = 81.050
# In ppm
yCAR = 118.078
centerPPM_N15 = yCAR

## Read the chemical shift data.
chemical_shift.read(file='1_0_46_0_max_standard.ser', dir=data_path+sep+'peak_lists')

## The lock power to field, has been found in an calibration experiment.
spin_lock_field_strengths_Hz = {'35': 431.0, '39': 651.2, '41': 800.5, '43': 984.0, '46': 1341.11, '48': 1648.5}

## Apply spectra settings.
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
        spectrum.read_intensities(file=FNAME, dir=data_path+sep+'peak_lists', spectrum_id=sp_id, int_method='height')

        # Set the peak intensity errors, as defined as the baseplane RMSD.
        spectrum.baseplane_rmsd(error=apod_rmsd, spectrum_id=sp_id)

        # Set the relaxation dispersion experiment type.
        relax_disp.exp_type(spectrum_id=sp_id, exp_type='R1rho')

        # Set The spin-lock field strength, nu1, in Hz
        relax_disp.spin_lock_field(spectrum_id=sp_id, field=spin_lock_field_strength)

        # Calculating the spin-lock offset in ppm, from offsets values provided in Hz.
        frq_N15_Hz = yOBS * 1E6
        offset_ppm_N15 = float(deltadof2) / frq_N15_Hz * 1E6
        omega_rf_ppm = centerPPM_N15 + offset_ppm_N15

        # Set The spin-lock offset, omega_rf, in ppm.
        relax_disp.spin_lock_offset(spectrum_id=sp_id, offset=omega_rf_ppm)

        # Set the relaxation times (in s).
        relax_disp.relax_time(spectrum_id=sp_id, time=time_sl)

        # Set the spectrometer frequency.
        spectrometer.frequency(id=sp_id, frq=set_sfrq, units='MHz')


# Read the R1 data
# relax_data.read(ri_id='R1', ri_type='R1', frq=cdp.spectrometer_frq_list[0], file='R1_fitted_values.txt', dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
