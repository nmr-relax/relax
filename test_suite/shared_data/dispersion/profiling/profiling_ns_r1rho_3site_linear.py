#!/usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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

# relax module imports.
from base import cluster, main, NUM_SPINS_CLUSTER, NUM_SPINS_SINGLE, single, Profile
from specific_analyses.relax_disp.variables import EXP_TYPE_R1RHO, MODEL_NS_R1RHO_3SITE_LINEAR


# Setup.
SINGLE = Profile(exp_type=[EXP_TYPE_R1RHO], num_spins=NUM_SPINS_SINGLE, model=MODEL_NS_R1RHO_3SITE_LINEAR, r2=5.0, dw_AB=1.0, dw_BC=2.0, pA=0.8, kex_AB=5000.0, pB=0.1, kex_BC=3000.0, spins_params=['r2', 'dw_AB', 'dw_BC', 'pA', 'kex_AB', 'pB', 'kex_BC'])
CLUSTER = Profile(exp_type=[EXP_TYPE_R1RHO], num_spins=NUM_SPINS_CLUSTER, model=MODEL_NS_R1RHO_3SITE_LINEAR, r2=5.0, dw_AB=1.0, dw_BC=2.0, pA=0.8, kex_AB=5000.0, pB=0.1, kex_BC=3000.0, spins_params=['r2', 'dw_AB', 'dw_BC', 'pA', 'kex_AB', 'pB', 'kex_BC'])

# Execute main function.
if __name__ == "__main__":
    main()
