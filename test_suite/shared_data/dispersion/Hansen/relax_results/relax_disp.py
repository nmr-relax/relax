"""Script for CPMG relaxation dispersion curve fitting using Dr. Flemming Hansen's data from http://dx.doi.org/10.1021/jp074793o.

To run:

$ ../../../../../relax relax_disp.py
"""


# Python module imports.
from os import sep

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# The dispersion models.
MODELS = ['LM63', 'CR72']

# The grid search size (the number of increments per dimension).
GRID_INC = 11

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 50



# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'

# Load the saved base pipe
results.read(data_path+sep+'base_pipe')

# Create the R2eff data pipe and load the results.
pipe.create(pipe_name='R2eff', bundle=pipe_bundle, pipe_type='relax_disp')
pipe.switch(pipe_name='R2eff')
results.read(data_path+sep+'r2eff_pipe')


# Auto-analysis execution.
##########################

# Do not change!
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM)
