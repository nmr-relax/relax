###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
from random import uniform


# Create a data pipe.
pipe.create('random tensors', 'N-state')

# Generate a number of tensors
for i in range(4):
    align_tensor.init(tensor='tensor %i'%i, params=(uniform(-1e-3, 1e-3), uniform(-1e-3, 1e-3), uniform(-1e-3, 1e-3), uniform(-1e-3, 1e-3), uniform(-1e-3, 1e-3)))

# Display the tensor info.
align_tensor.display()

# Save the results.
results.write('random_tensors', dir=None, force=True)
