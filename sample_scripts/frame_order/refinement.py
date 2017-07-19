###############################################################################
#                                                                             #
# Copyright (C) 2015 Edward d'Auvergne                                        #
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

"""Script for black-box Frame Order analysis.

This is for the CaM-IQ data.

The free rotor pseudo-elliptic cone model is not used in this script as the cone X and Y opening angles cannot be differentiated with simply RDC and PCS data, hence this model is perfectly approximated by the free rotor isotropic cone.
"""

# Python module imports.
from time import asctime, localtime

# relax module imports.
from auto_analyses.frame_order import Frame_order_analysis, Optimisation_settings


# Analysis variables.
#####################

# The frame order models to use.
MODELS = [
    'rigid',
    'rotor',
    'iso cone',
    'pseudo-ellipse',
    'iso cone, torsionless',
    'pseudo-ellipse, torsionless',
    'double rotor'
]

# The number of Monte Carlo simulations to be used for error analysis at the end of the protocol.
MC_NUM = 10

# Full data set optimisation setup.
OPT_FULL = Optimisation_settings()
OPT_FULL.add_min(min_algor='simplex', func_tol=1e-4, quad_int=True)

# Monte Carlo simulation optimisation setup.
OPT_MC = Optimisation_settings()
OPT_MC.add_min(min_algor='simplex', func_tol=1e-3, quad_int=True)


# Set up the base data pipes.
#############################

# The data pipe bundle to group all data pipes.
PIPE_BUNDLE = "Frame Order (%s)" % asctime(localtime())


# Execution.
############

# Do not change!
Frame_order_analysis(pipe_bundle=PIPE_BUNDLE, results_dir='refinement', pre_run_dir='.', opt_full=OPT_FULL, opt_mc=OPT_MC, mc_sim_num=MC_NUM, models=MODELS)
