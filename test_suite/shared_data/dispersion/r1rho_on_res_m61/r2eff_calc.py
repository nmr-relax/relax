# Script for generating a save file of the R2eff fitted model.

# Python module imports.
from os import sep

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Analysis variables.
#####################

# The dispersion models.
MODELS = ['R2eff']

# The grid search size (the number of increments per dimension).
GRID_INC = 10

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 500


# Set up the data pipe.
#######################

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'r1rho_on_res_m61'

# Create the sequence data.
spin.create(res_name='Trp', res_num=1, spin_name='N')
spin.create(res_name='Trp', res_num=2, spin_name='N')

# Set the isotope information.
spin.isotope(isotope='15N')

# The spectral data - spectrum ID, peak lists, offset frequency (Hz), relaxation time period (s), baseplane RMSD estimate.
data = []
times = [0.00, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.15]
ncyc = [1, 2, 3, 4, 5, 6, 7, 8, 9]
spin_lock = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000]
for spin_lock_index in range(len(spin_lock)):
    for time_index in range(len(times)):
        data.append(["nu_%s_ncyc%s" % (spin_lock[spin_lock_index], ncyc[time_index]), "nu_%s_ncyc%s.list" % (spin_lock[spin_lock_index], ncyc[time_index]), spin_lock[spin_lock_index], times[time_index], 200000.0])


# Loop over the spectral data, loading it and setting the metadata.
for i in range(len(data)):
    # Load the peak intensities and set the errors.
    spectrum.read_intensities(file=data[i][1], dir=data_path, spectrum_id=data[i][0], int_method='height')
    spectrum.baseplane_rmsd(spectrum_id=data[i][0], error=data[i][4])

    # Set the relaxation dispersion experiment type.
    relax_disp.exp_type(spectrum_id=data[i][0], exp_type='R1rho')

    # Set the relaxation dispersion spin-lock field strength (nu1).
    relax_disp.spin_lock_field(spectrum_id=data[i][0], field=data[i][2])

    # Set the spin-lock offset.
    relax_disp.spin_lock_offset(spectrum_id=data[i][0], offset=115.0)

    # Set the relaxation times.
    relax_disp.relax_time(spectrum_id=data[i][0], time=data[i][3])

    # Set the spectrometer frequency.
    spectrometer.frequency(id=data[i][0], frq=800, units='MHz')

# Read the chemical shift data.
chemical_shift.read(file="nu_%s_ncyc1.list" % spin_lock[0], dir=data_path)



# Auto-analysis execution.
##########################

# Do not change!
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir='.', models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM)

# Save the program state.
state.save('r2eff_values', force=True)
