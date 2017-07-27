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
"""This system test catches the local tm global model selection bug.

The bug is:
    - Bug #21079 (U{bug #21079<https://gna.org/bugs/?21079>}).
"""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Path of the files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'bug_21079_local_tm_global_selection'

# Load the state files.
pipes = ['local_tm', 'sphere']
files = ['local_tm_trunc', 'sphere_trunc']
for i in range(len(pipes)):
    pipe.create(pipes[i], 'mf')
    results.read(file=files[i], dir=path)

# Model selection.
model_selection(method='AIC', modsel_pipe='final', pipes=['local_tm', 'sphere'])

# Display the sequence data for a sanity check.
sequence.display()

# Monte Carlo simulations.
monte_carlo.setup(number=5)
monte_carlo.create_data(method='back_calc')
monte_carlo.initial_values()
minimise.execute()
monte_carlo.error_analysis()
