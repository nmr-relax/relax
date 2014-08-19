###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Troels E. Linnet                                    #
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

# Python module imports.
from os import getcwd, sep
import re

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from specific_analyses.relax_disp.variables import MODEL_R2EFF


#########################################
#### Setup
# The data path
if not hasattr(ds, 'data_path'):
    ds.data_path = getcwd()

# The models to analyse.
if not hasattr(ds, 'models'):
    ds.models = [MODEL_R2EFF]

# The number of increments per parameter, to split up the search interval in grid search.
if not hasattr(ds, 'grid_inc'):
    ds.grid_inc = 21

# The number of Monte-Carlo simulations, for the error analysis in the 'R2eff' model when exponential curves are fitted.
# For estimating the error of the fitted R2eff values,
# a high number should be provided. Later the high quality R2eff values will be read for subsequent model analyses.
if not hasattr(ds, 'exp_mc_sim_num'):
    ds.exp_mc_sim_num = 10

# The result directory.
if not hasattr(ds, 'results_dir'):
    ds.results_dir = getcwd() + sep + 'results_R2eff'

## The optimisation function tolerance.
## This is set to the standard value, and should not be changed.
#if not hasattr(ds, 'opt_func_tol'):
#    ds.opt_func_tol = 1e-25
#Relax_disp.opt_func_tol = ds.opt_func_tol

#if not hasattr(ds, 'opt_max_iterations'):
#    ds.opt_max_iterations = int(1e7)
#Relax_disp.opt_max_iterations = ds.opt_max_iteration


#########################################
### Run script with setup.
script(file='1_setup_r1rho.py', dir=ds.data_path)

# To speed up the analysis, only select a few spins.
deselect.all()

# Load the experiments settings file.
residues = open(ds.data_path+sep+'global_fit_residues.txt', 'r')
residueslines = residues.readlines()
residues.close()

# Split the line string into number and text.
r = re.compile("([a-zA-Z]+)([0-9]+)([a-zA-Z]+)(-)([a-zA-Z]+)")

for i, line in enumerate(residueslines):
    if line[0] == "#":
        continue
    else:
        re_split = r.match(line)
        #print re_split.groups()
        resn = re_split.group(1)
        resi = int(re_split.group(2))
        isotope = re_split.group(3)

        select.spin(spin_id=':%i@%s'%(resi, isotope), change_all=False)

# Run the analysis.
Relax_disp(pipe_name=ds.pipe_name, pipe_bundle=ds.pipe_bundle, results_dir=ds.results_dir, models=ds.models, grid_inc=ds.grid_inc, exp_mc_sim_num=ds.exp_mc_sim_num)