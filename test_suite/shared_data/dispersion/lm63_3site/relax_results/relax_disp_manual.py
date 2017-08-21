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

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Load the saved state.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'lm63_3site'
state.load(data_path+sep+'r2eff_values')

# A new data pipe.
pipe.copy(pipe_from='base pipe', pipe_to='LM63 3-site', bundle_to='relax_disp')
pipe.switch(pipe_name='LM63 3-site')

# Set up the model data.
relax_disp.select_model(model='LM63 3-site')
value.copy(pipe_from='R2eff', pipe_to='LM63 3-site', param='r2eff')
spin.isotope('15N')

# Manually set the parameter values.
cdp.mol[0].res[0].spin[0].r2 = [12.0, 12.0]
cdp.mol[0].res[0].spin[0].phi_ex_B = 0.1
cdp.mol[0].res[0].spin[0].phi_ex_C = 0.5
cdp.mol[0].res[0].spin[0].kB = 1500.0
cdp.mol[0].res[0].spin[0].kC = 2500.0
cdp.mol[0].res[1].spin[0].r2 = [15.0, 15.0]
cdp.mol[0].res[1].spin[0].phi_ex_B = 0.1
cdp.mol[0].res[1].spin[0].phi_ex_C = 0.5
cdp.mol[0].res[1].spin[0].kB = 1500.0
cdp.mol[0].res[1].spin[0].kC = 2500.0

# Optimisation.
minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-25, grad_tol=None, max_iter=10000000, constraints=True, scaling=True, verbosity=1)

# Monte Carlo simulations.
monte_carlo.setup(number=3)
monte_carlo.create_data(method='back_calc')
monte_carlo.initial_values()
minimise.execute(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-25, grad_tol=None, max_iter=10000000, constraints=True, scaling=True, verbosity=1)
monte_carlo.error_analysis()

results.write(file='results', compress_type=1, force=True)
