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
GRID_INC = None

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

# Create the sequence.
spin.create(res_num=70, spin_name='N')
spin.create(res_num=71, spin_name='N')

# Name the spins so they can be matched to the assignments, and the isotope for field strength scaling.
spin.name(name='N')
spin.isotope(isotope='15N')

# The spectral data - experiment ID, R2eff file name, CPMG frequency (Hz), spectrometer frequency in Hertz.
data = [
    ['500_66.67',   '500_66.67.r2eff',     66.6666,  500e6],
    ['500_133.33',  '500_133.33.r2eff',   133.3333,  500e6],
    ['500_200.00',  '500_200.00.r2eff',   200.0000,  500e6],
    ['500_266.67',  '500_266.67.r2eff',   266.6666,  500e6],
    ['500_333.33',  '500_333.33.r2eff',   333.3333,  500e6],
    ['500_400.00',  '500_400.00.r2eff',   400.0000,  500e6],
    ['500_466.67',  '500_466.67.r2eff',   466.6666,  500e6],
    ['500_533.33',  '500_533.33.r2eff',   533.3333,  500e6],
    ['500_600.00',  '500_600.00.r2eff',   600.0000,  500e6],
    ['500_666.67',  '500_666.67.r2eff',   666.6666,  500e6],
    ['500_733.33',  '500_733.33.r2eff',   733.3333,  500e6],
    ['500_800.00',  '500_800.00.r2eff',   800.0000,  500e6],
    ['500_866.67',  '500_866.67.r2eff',   866.6666,  500e6],
    ['500_933.33',  '500_933.33.r2eff',   933.3333,  500e6],
    ['500_1000.00', '500_1000.00.r2eff', 1000.0000,  500e6],
    ['800_66.67',   '800_66.67.r2eff',     66.6666,  800e6],
    ['800_133.33',  '800_133.33.r2eff',   133.3333,  800e6],
    ['800_200.00',  '800_200.00.r2eff',   200.0000,  800e6],
    ['800_266.67',  '800_266.67.r2eff',   266.6666,  800e6],
    ['800_333.33',  '800_333.33.r2eff',   333.3333,  800e6],
    ['800_400.00',  '800_400.00.r2eff',   400.0000,  800e6],
    ['800_466.67',  '800_466.67.r2eff',   466.6666,  800e6],
    ['800_533.33',  '800_533.33.r2eff',   533.3333,  800e6],
    ['800_600.00',  '800_600.00.r2eff',   600.0000,  800e6],
    ['800_666.67',  '800_666.67.r2eff',   666.6666,  800e6],
    ['800_733.33',  '800_733.33.r2eff',   733.3333,  800e6],
    ['800_800.00',  '800_800.00.r2eff',   800.0000,  800e6],
    ['800_866.67',  '800_866.67.r2eff',   866.6666,  800e6],
    ['800_933.33',  '800_933.33.r2eff',   933.3333,  800e6],
    ['800_1000.00', '800_1000.00.r2eff', 1000.0000,  800e6]
]

# Loop over the spectra.
for id, file, cpmg_frq, H_frq in data:
    # Set the relaxation dispersion experiment type.
    relax_disp.exp_type(spectrum_id=id, exp_type='SQ CPMG')

    # Set the NMR field strength of the spectrum.
    spectrometer.frequency(id=id, frq=H_frq)

    # Relaxation dispersion CPMG constant time delay T (in s).
    relax_disp.relax_time(spectrum_id=id, time=0.030)

    # Load the R2eff data.
    relax_disp.r2eff_read(id=id, file=file, dir=data_path+sep+'r2eff_data', disp_frq=cpmg_frq, res_num_col=1, data_col=2, error_col=3)

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
