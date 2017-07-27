###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Script for catching bug #20464, the failure due to missing relaxation data (https://gna.org/bugs/?20464)."""

# Python module imports.
from os import sep
from tempfile import mkdtemp

# relax module imports.
from auto_analyses.dauvergne_protocol import dAuvergne_protocol
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Analysis variables.
#####################

# The diffusion model.
DIFF_MODEL = 'final'

# The model-free models.  Do not change these unless absolutely necessary, the protocol is likely to fail if these are changed.
MF_MODELS = ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm9']
LOCAL_TM_MODELS = ['tm0', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm9']

# The grid search size (the number of increments per dimension).
GRID_INC = 4

# The optimisation technique.
MIN_ALGOR = 'newton'

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 3

# Automatic looping over all rounds until convergence (must be a boolean value of True or False).
CONV_LOOP = True



# Load the state.
data_path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'bug_20613_auto_mf_diff_tensor_pdb'
state.load('state', dir=data_path)

# The results dir.
ds.tmpdir = mkdtemp()

# The pipe and bundle names from the state file.
pipe_bundle = 'mf (Fri Mar  8 07:43:00 2013)'
name = 'origin - mf (Fri Mar  8 07:43:00 2013)'


# Execution.
############

dAuvergne_protocol.opt_func_tol = 1e-5
dAuvergne_protocol.opt_max_iterations = 2000

# Do not change!
dAuvergne_protocol(pipe_name=name, pipe_bundle=pipe_bundle, results_dir=data_path, write_results_dir=ds.tmpdir, diff_model=DIFF_MODEL, mf_models=MF_MODELS, local_tm_models=LOCAL_TM_MODELS, grid_inc=GRID_INC, min_algor=MIN_ALGOR, mc_sim_num=MC_NUM, max_iter=2, conv_loop=CONV_LOOP)
