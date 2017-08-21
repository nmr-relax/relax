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

$ ../../../../../relax relax_4_model_sel_trunc.py --tee relax_4_model_sel_trunc.log
"""

import os
from auto_analyses.relax_disp import Relax_disp

# Load the initial state setup
state.load(state='ini_setup_trunc.bz2')
 
# Set settings for run.
results_directory = os.path.join(os.getcwd(), "relax_results_trunc")
pipe_name = 'base pipe'; pipe_bundle = 'relax_disp'
MODELS = ['R2eff', 'No Rex', 'TSMFK01', 'LM63', 'LM63 3-site', 'CR72', 'CR72 full', 'IT99', 'NS CPMG 2-site 3D', 'NS CPMG 2-site expanded', 'NS CPMG 2-site star']
GRID_INC = 11; MC_NUM = 50; MODSEL = 'AIC'
 
# Execute
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=results_directory, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, modsel=MODSEL)
