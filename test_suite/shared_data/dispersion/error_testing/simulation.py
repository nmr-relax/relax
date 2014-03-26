# Optimise the R1rho on-resonance synthetic data using the M61 model.


# Python module imports.
from math import sqrt
from numpy import float64, zeros
from os import sep
from random import gauss

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from lib.statistics import std
from status import Status; status = Status()


# Simulation number.
SIM_NUM = 10000

# Intensity error.
ERR = 2e6

# Create the data pipe.
pipe.create(pipe_name='base', pipe_type='relax_disp')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'r1rho_on_res_m61'

# Create the sequence data.
spin.create(res_name='Trp', res_num=1, spin_name='N')
spin.create(res_name='Trp', res_num=1, spin_name='NE1')

# Set the isotope information.
spin.isotope(isotope='15N')

# The spectral data - spectrum ID, peak lists, offset frequency (Hz), relaxation time period (s), baseplane RMSD estimate.
data = []
times = [0.1]
ncyc = [7]
spin_lock = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000]
for spin_lock_index in range(len(spin_lock)):
    for time_index in range(len(times)):
        data.append(["nu_%s_ncyc%s" % (spin_lock[spin_lock_index], ncyc[time_index]), "nu_%s_ncyc%s.list" % (spin_lock[spin_lock_index], ncyc[time_index]), spin_lock[spin_lock_index], times[time_index], ERR])

# Load the peak intensities and set the errors.
spectrum.read_intensities(file="nu_%s_ncyc1.list" % spin_lock[0], dir=data_path, spectrum_id='ref', int_method='height', heteronuc='N', proton='HN')
spectrum.read_intensities(file="nu_%s_ncyc1.list" % spin_lock[0], dir=data_path, spectrum_id='ref', int_method='height', heteronuc='NE1', proton='HE1')
spectrum.baseplane_rmsd(spectrum_id='ref', error=data[0][4])

# Set as the reference.
relax_disp.spin_lock_field(spectrum_id='ref', field=None)

# Set the spectrometer frequency.
spectrometer.frequency(id='ref', frq=800, units='MHz')

# Loop over the spectral data, loading it and setting the metadata.
for i in range(len(data)):
    # Load the peak intensities and set the errors.
    spectrum.read_intensities(file=data[i][1], dir=data_path, spectrum_id=data[i][0], int_method='height', heteronuc='N', proton='HN')
    spectrum.read_intensities(file=data[i][1], dir=data_path, spectrum_id=data[i][0], int_method='height', heteronuc='NE1', proton='HE1')
    spectrum.baseplane_rmsd(spectrum_id=data[i][0], error=data[i][4])

    # Set the experiment type.
    relax_disp.exp_type(spectrum_id=id, exp_type='R1rho')

    # Set the relaxation dispersion spin-lock field strength (nu1).
    relax_disp.spin_lock_field(spectrum_id=data[i][0], field=data[i][2])

    # Set the relaxation times.
    relax_disp.relax_time(spectrum_id=data[i][0], time=data[i][3])

    # Set the spectrometer frequency.
    spectrometer.frequency(id=data[i][0], frq=800, units='MHz')

# The model.
relax_disp.select_model('R2eff')

# Set up all the errors.
spectrum.error_analysis()

# The error data structures.
r2eff_indiv = zeros((len(spin_lock), SIM_NUM), float64)
r2eff_group = zeros((len(spin_lock), SIM_NUM), float64)
sigma_r2eff_indiv = zeros(len(spin_lock), float64)
sigma_r2eff_group = zeros(len(spin_lock), float64)

# Calculate the theoretical errors.
sigma_r2eff_full = []
sigma_r2eff_red = []
int = cdp.mol[0].res[0].spin[0].peak_intensity
for i in range(len(spin_lock)):
    sigma_r2eff_full.append(1.0/0.1 * sqrt((ERR/int['ref'])**2 + (ERR/int['nu_%s_ncyc7'%spin_lock[i]])**2))
    sigma_r2eff_red.append(1.0/0.1 * ERR/int['nu_%s_ncyc7'%spin_lock[i]])

# Loop over the simulations.
for i in range(SIM_NUM):
    # Duplicate the data pipe for the simulations.
    pipe.copy(pipe_from='base', pipe_to='sim_%i'%i)
    pipe.switch('sim_%i'%i)

    # Alias the spin and intensities.
    spin = cdp.mol[0].res[0].spin[0]
    int = spin.peak_intensity
    i0 = int['ref']

    # Individual dispersion point pair test.
    for j in range(len(spin_lock)):
        # Randomise both points.
        int['ref'] = gauss(i0, ERR)
        int['nu_%s_ncyc7'%spin_lock[j]] = gauss(int['nu_%s_ncyc7'%spin_lock[j]], ERR)

        # Calculate R2eff and store it.
        calc()
        r2eff_indiv[j, i] = spin.r2eff['800.0_%.1f' % spin_lock[j]]

    # Randomise I0 once.
    int['ref'] = gauss(i0, ERR)

    # Calculate all R2eff and store them.
    calc()
    for j in range(len(spin_lock)):
        r2eff_group[j, i] = spin.r2eff['800.0_%.1f' % spin_lock[j]]

# The errors.
for j in range(len(spin_lock)):
    sigma_r2eff_indiv[j] = std(r2eff_indiv[j])
    sigma_r2eff_group[j] = std(r2eff_group[j])

# Plot the data.
file = open('error_plot.agr', 'w')

# Header.
file.write("@with g0\n")
file.write("@    s0 legend  \"Full error formula\"\n")
file.write("@    s1 legend  \"Reduced error formula\"\n")
file.write("@    s2 legend  \"Bootstrap individual dispersion points\"\n")
file.write("@    s3 legend  \"Bootstrap group\"\n")

# The full error formula.
file.write("@target G0.S0\n@type xy\n")
for i in range(len(spin_lock)):
    file.write("%s %s\n" % (spin_lock[i], sigma_r2eff_full[i]))
file.write("&\n")

# The reduced error formula.
file.write("@target G0.S1\n@type xy\n")
for i in range(len(spin_lock)):
    file.write("%s %s\n" % (spin_lock[i], sigma_r2eff_red[i]))
file.write("&\n")

# The Bootstrapped individual errors.
file.write("@target G0.S2\n@type xy\n")
for i in range(len(spin_lock)):
    file.write("%s %s\n" % (spin_lock[i], sigma_r2eff_indiv[i]))
file.write("&\n")

# The Bootstrapped group errors.
file.write("@target G0.S2\n@type xy\n")
for i in range(len(spin_lock)):
    file.write("%s %s\n" % (spin_lock[i], sigma_r2eff_group[i]))
file.write("&\n")

# Save the program state.
state.save('state_individual', force=True)
