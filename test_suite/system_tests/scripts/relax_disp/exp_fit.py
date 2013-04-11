# Script for fitting the 'exp_fit' relaxation dispersion model to synthetic R1rho data.

# Python module imports.
from os import sep

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Analysis variables.
#####################

# The dispersion models.
MODELS = ['exp_fit']

# The grid search size (the number of increments per dimension).
GRID_INC = 3

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 3



# Set up the data pipe.
#######################

# The results directory.
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = None

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting_disp'+sep+'exp_fit_data'

# Create the sequence data.
spin.create(res_name='Asp', res_num=1, spin_name='N')
spin.create(res_name='Gly', res_num=2, spin_name='N')
spin.create(res_name='Lys', res_num=3, spin_name='N')

# Set the relaxation dispersion experiment type.
relax_disp.exp_type('r1rho')

# The spectral data - spectrum ID, peak lists, offset frequency (Hz), relaxation time period (s), baseplane RMSD estimate.
data = [
    ["nu_1kHz_relaxT_0.01", "nu_1kHz_relaxT_0.01.list", 1000.0, 0.01,   1000],
    ["nu_1kHz_relaxT_0.02", "nu_1kHz_relaxT_0.02.list", 1000.0, 0.02,   1000],
    ["nu_1kHz_relaxT_0.04", "nu_1kHz_relaxT_0.04.list", 1000.0, 0.04,   1000],
    ["nu_1kHz_relaxT_0.06", "nu_1kHz_relaxT_0.06.list", 1000.0, 0.06,   1000],
    ["nu_1kHz_relaxT_0.08", "nu_1kHz_relaxT_0.08.list", 1000.0, 0.08,   1000],
    ["nu_1kHz_relaxT_0.10", "nu_1kHz_relaxT_0.10.list", 1000.0, 0.10,   1000],
    ["nu_1kHz_relaxT_0.12", "nu_1kHz_relaxT_0.12.list", 1000.0, 0.12,   1000],
    ["nu_2kHz_relaxT_0.01", "nu_2kHz_relaxT_0.01.list", 2000.0, 0.01,   1000],
    ["nu_2kHz_relaxT_0.02", "nu_2kHz_relaxT_0.02.list", 2000.0, 0.02,   1000],
    ["nu_2kHz_relaxT_0.04", "nu_2kHz_relaxT_0.04.list", 2000.0, 0.04,   1000],
    ["nu_2kHz_relaxT_0.06", "nu_2kHz_relaxT_0.06.list", 2000.0, 0.06,   1000],
    ["nu_2kHz_relaxT_0.08", "nu_2kHz_relaxT_0.08.list", 2000.0, 0.08,   1000],
    ["nu_2kHz_relaxT_0.10", "nu_2kHz_relaxT_0.10.list", 2000.0, 0.10,   1000],
    ["nu_2kHz_relaxT_0.12", "nu_2kHz_relaxT_0.12.list", 2000.0, 0.12,   1000],
]

# Loop over the spectral data, loading it and setting the metadata.
for i in range(len(data)):
    # Load the peak intensities and set the errors.
    spectrum.read_intensities(file=data[i][1], dir=data_path, spectrum_id=data[i][0], int_method='height', proton='H')
    spectrum.baseplane_rmsd(spectrum_id=data[i][0], error=data[i][4])

    # Set the relaxation dispersion spin-lock field strength (nu1).
    relax_disp.spin_lock_field(spectrum_id=data[i][0], field=data[i][2])

    # Set the relaxation times.
    relax_disp.relax_time(spectrum_id=data[i][0], time=data[i][3])

# Peak intensity error analysis.
spectrum.error_analysis()

# Clustering.
relax_disp.cluster(cluster_id='test', spin_id=':1')
relax_disp.cluster(cluster_id='cluster', spin_id=':1,3@N')



# Auto-analysis execution.
##########################

# Do not change!
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=ds.tmpdir, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM)

# Save the program state.
state.save('devnull', force=True)
