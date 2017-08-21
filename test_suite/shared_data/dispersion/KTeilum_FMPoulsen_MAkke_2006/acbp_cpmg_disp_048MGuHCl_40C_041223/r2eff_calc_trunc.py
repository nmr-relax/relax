###############################################################################
#                                                                             #
# Copyright (C) 2013 Troels E. Linnet                                         #
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
"""Taken from the relax disp manual, section 10.6.1 Dispersion script mode - the sample script.

To run the script, simply type:

$ ../../../../../relax r2eff_calc_trunc.py --tee r2eff_calc_trunc.log
"""

import shutil
from auto_analyses.relax_disp import Relax_disp

# Load the initial state setup
state.load(state='ini_setup_trunc.bz2')

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
state.save('r2eff_pipe_trunc', force=True)

# Delete data result directory
shutil.rmtree(results_directory)
