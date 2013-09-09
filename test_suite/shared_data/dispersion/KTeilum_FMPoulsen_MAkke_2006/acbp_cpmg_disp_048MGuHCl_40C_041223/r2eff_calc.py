# Taken from the relax disp manual, section 10.6.1 Dispersion script mode - the sample script
import os
import shutil
from auto_analyses.relax_disp import Relax_disp

# Load the initial state setup
state.load(state='ini_setup.bz2')

# Set settings for run.
results_directory = 'temp'
pipe_name = 'base pipe'; pipe_bundle = 'relax_disp'
MODELS = ['R2eff']
GRID_INC = 5; MC_NUM = 3; MODSEL = 'AIC'

# Execute
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=results_directory, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL)

# Delete the "base pipe"
pipe.delete(pipe_name='base pipe')

# Save the program state.
state.save('r2eff_pipe', force=True)

# Delete data result directory
shutil.rmtree(results_directory)
