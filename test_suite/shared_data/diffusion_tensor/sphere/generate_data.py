###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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

"""relax script for creating a PDB file and relaxation data.

The PDB file consists of uniformly distributed bond vectors.  The relaxation data is that of a NH bond vector with an ellipsoidal diffusion tensor and no internal motion.
"""

# Python module imports.
from numpy import array, float64

# relax module imports.
from test_suite.shared_data.diffusion_tensor import generate_data


# The tensor values.
Dx = 2e7
Dy = 2e7
Dz = 2e7
alpha = 1.0
beta = 2.0
gamma = 0.5

# Other data.
frq = array([500, 600, 700, 800], float64)
wH = frq * 1e6 * 2*pi
csa = -172e-6

# The tensor.
R, R_rev, D_prime, D = generate_data.tensor_setup(Dx, Dy, Dz, alpha, beta, gamma)

# The bond vector distribution.
vectors = generate_data.pdb(file_name='uniform.pdb', inc=6)

# The relaxation data.
for i in range(len(frq)):
    generate_data.ri_data(Dx=Dx, Dy=Dy, Dz=Dz, R=R, vectors=vectors, frq_label=str(int(frq[i])), wH=wH[i], csa=csa)
