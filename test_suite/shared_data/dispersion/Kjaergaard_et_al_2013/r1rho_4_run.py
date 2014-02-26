"""Taken from the relax disp manual, section 10.6.1 Dispersion script mode - the sample script.
# Copyright (C) 2013 Troels E. Linnet

To run the script, simply type:

$ ../../../../../relax r1rho_4_run.py --tee log_r1rho_4_run.log
"""

import os
from auto_analyses.relax_disp import Relax_disp

# Setting variables for pipe names.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'

# The dispersion models.
MODELS = ['R2eff', 'No Rex', 'DPL94']
# The grid search size (the number of increments per dimension).
GRID_INC = 4
# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 3
# Model selection technique.
MODSEL = 'AIC'

# Load the initial state setup
state.load(state='ini_setup_r1rho.bz2')

# Run faster.
Relax_disp.opt_func_tol = 1e-10
Relax_disp.opt_max_iterations = 10000

results_directory = os.path.join("r1rho", "test")

Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=results_directory, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL)
