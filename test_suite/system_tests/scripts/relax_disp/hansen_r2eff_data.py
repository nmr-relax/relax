# Script for CPMG relaxation dispersion curve fitting using Dr. Flemming Hansen's data from http://dx.doi.org/10.1021/jp074793o.

# Python module imports.
from os import sep

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Analysis variables.
#####################

# The dispersion models.
MODELS = ['LM63']
if hasattr(ds, 'models'):
    MODELS = ds.models

# The temporary directory, if needed.
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp'

# The numeric flag.
if not hasattr(ds, 'numeric_only'):
    ds.numeric_only = False

# The grid search size (the number of increments per dimension).
GRID_INC = 5

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 3



# Set up the data pipe.
#######################

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'

# Load the sequence.
sequence.read('fake_sequence.in', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen', res_num_col=1, res_name_col=2)

# Name the spins so they can be matched to the assignments, and the isotope for field strength scaling.
spin.name(name='N')
spin.isotope(isotope='15N')

# The spectral data - peak list file name, CPMG frequency (Hz), spectrometer frequency in Hertz.
data = [
    ['500_MHz'+sep+'reference.in',           None,  500e6],
    ['500_MHz'+sep+'66.667.in',           66.6666,  500e6],
    ['500_MHz'+sep+'133.33.in',          133.3333,  500e6],
    ['500_MHz'+sep+'133.33.in.bis',      133.3333,  500e6],
    ['500_MHz'+sep+'200.in',             200.0000,  500e6],
    ['500_MHz'+sep+'266.67.in',          266.6666,  500e6],
    ['500_MHz'+sep+'333.33.in',          333.3333,  500e6],
    ['500_MHz'+sep+'400.in',             400.0000,  500e6],
    ['500_MHz'+sep+'466.67.in',          466.6666,  500e6],
    ['500_MHz'+sep+'533.33.in',          533.3333,  500e6],
    ['500_MHz'+sep+'533.33.in.bis',      533.3333,  500e6],
    ['500_MHz'+sep+'600.in',             600.0000,  500e6],
    ['500_MHz'+sep+'666.67.in',          666.6666,  500e6],
    ['500_MHz'+sep+'733.33.in',          733.3333,  500e6],
    ['500_MHz'+sep+'800.in',             800.0000,  500e6],
    ['500_MHz'+sep+'866.67.in',          866.6666,  500e6],
    ['500_MHz'+sep+'933.33.in',          933.3333,  500e6],
    ['500_MHz'+sep+'933.33.in.bis',      933.3333,  500e6],
    ['500_MHz'+sep+'1000.in',           1000.0000,  500e6],
    ['800_MHz'+sep+'reference.in',           None,  800e6],
    ['800_MHz'+sep+'66.667.in',           66.6666,  800e6],
    ['800_MHz'+sep+'133.33.in',          133.3333,  800e6],
    ['800_MHz'+sep+'133.33.in.bis',      133.3333,  800e6],
    ['800_MHz'+sep+'200.in',             200.0000,  800e6],
    ['800_MHz'+sep+'266.67.in',          266.6666,  800e6],
    ['800_MHz'+sep+'333.33.in',          333.3333,  800e6],
    ['800_MHz'+sep+'400.in',             400.0000,  800e6],
    ['800_MHz'+sep+'466.67.in',          466.6666,  800e6],
    ['800_MHz'+sep+'533.33.in',          533.3333,  800e6],
    ['800_MHz'+sep+'533.33.in.bis',      533.3333,  800e6],
    ['800_MHz'+sep+'600.in',             600.0000,  800e6],
    ['800_MHz'+sep+'666.67.in',          666.6666,  800e6],
    ['800_MHz'+sep+'733.33.in',          733.3333,  800e6],
    ['800_MHz'+sep+'800.in',             800.0000,  800e6],
    ['800_MHz'+sep+'866.67.in',          866.6666,  800e6],
    ['800_MHz'+sep+'933.33.in',          933.3333,  800e6],
    ['800_MHz'+sep+'933.33.in.bis',      933.3333,  800e6],
    ['800_MHz'+sep+'1000.in',           1000.0000,  800e6]
]

# Loop over the spectra.
for file, cpmg_frq, H_frq in data:
    relax_disp.r2eff_read(file=file, dir=data_path, exp_type='CPMG', frq=H_frq, disp_frq=cpmg_frq, res_num_col=1, data_col=2, error_col=3)

# Deselect unresolved spins.
deselect.read(file='unresolved', dir=data_path+sep+'500_MHz', res_num_col=1)
deselect.read(file='unresolved', dir=data_path+sep+'800_MHz', res_num_col=1)



# Auto-analysis execution.
##########################

# Run fast.
Relax_disp.opt_func_tol = 1e-5
Relax_disp.opt_max_iterations = 10000

# Do not change!
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=ds.tmpdir, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, numeric_only=ds.numeric_only)
