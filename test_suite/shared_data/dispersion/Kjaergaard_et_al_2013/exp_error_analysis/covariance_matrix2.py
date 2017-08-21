###############################################################################
#                                                                             #
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

# Module docstring.
"""Check the R2eff and I0 errors using the covariance technique."""

# Python module imports.
from os import chdir, getcwd, pardir


# Setup.
cwd = getcwd()
chdir(pardir)
script('1_setup_r1rho.py')
chdir(cwd)

# Peak intensity error analysis.
spectrum.error_analysis()

# Only select a few spins for speed.
deselect.all()
select.spin(":5-10")

# The model.
relax_disp.select_model('R2eff')

# Optimisation.
minimise.grid_search(inc=11)
minimise.execute('newton', constraints=False)

# Error analysis.
relax_disp.r2eff_err_estimate(chi2_jacobian=False)

# Write out the values.
value.write(param='r2eff', file='r2eff_covar2.txt', force=True)
value.write(param='i0', file='i0_covar2.txt', force=True)

# Save the state.
state.save('covar2_errors', force=True)

