# Script for CPMG relaxation dispersion curve fitting using Dr. Flemming Hansen's data from http://dx.doi.org/10.1021/jp074793o.

# Python module imports.
from os import sep

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


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



# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'

# Load the saved base pipe containing R2eff data.
results.read(data_path+sep+'r2eff_pipe')
deselect.spin(":4")

# Set the nuclear isotope data.
spin.isotope('15N')



# Auto-analysis execution.
##########################

# Run fast.
Relax_disp.opt_func_tol = 1e-5
Relax_disp.opt_max_iterations = 10000

# Do not change!
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=ds.tmpdir, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, numeric_only=ds.numeric_only)
