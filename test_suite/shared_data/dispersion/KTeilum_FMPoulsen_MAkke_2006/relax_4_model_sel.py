# Taken from the relax disp manual, section 10.6.1 Dispersion script mode - the sample script
import os
from auto_analyses.relax_disp import Relax_disp

# Load the initial state setup
state.load(state='ini_setup.bz2')
 
# Set settings for run.
results_directory = os.path.join(os.getcwd(),"model_sel_analyt")
pipe_name = 'base pipe'; pipe_bundle = 'relax_disp'
MODELS = ['R2eff', 'No Rex', 'TSMFK01', 'LM63', 'CR72', 'CR72 full', 'IT99']
GRID_INC = 21; MC_NUM = 10; MODSEL = 'AIC'
 
# Execute
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=results_directory, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL)
