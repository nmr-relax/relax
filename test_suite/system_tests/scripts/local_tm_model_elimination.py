###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""Script for eliminating model tm4 with parameters {local_tm, S2, te, Rex} when tm > 50 ns."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Read the sequence.
sequence.read(file='Ap4Aase.Noe.600', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'relaxation_data'+sep, res_num_col=1, res_name_col=2)

# Select the model.
model_free.select_model(model='tm4')

# Set a local tm value
value.set(51 * 1e-9, 'local_tm', spin_id=":15")

# Model elimination.
eliminate()
