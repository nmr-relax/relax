###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Python module imports.
from math import sqrt
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store


class N_state_model(TestCase):
    """Class for testing various aspects specific to the N-state model."""

    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()



    def test_5_conf_xz(self):
        """A 5-state model in the xz-plane (no pivotting of alpha).

        The 5 states correspond to the Euler angles (z-y-z notation):
            State 1:    {0, pi/4, 0}
            State 2:    {0, pi/8, 0}
            State 3:    {0, 0, 0}
            State 4:    {0, -pi/8, 0}
            State 5:    {0, -pi/4, 0}
        """

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('C domain', 'N-state')

        # Load the C-terminal alignment tensors..
        self.relax.interpreter._Align_tensor.init(tensor='chi1', params=(-1/2., -1/2.,  0.,   0.,     0.))
        self.relax.interpreter._Align_tensor.init(tensor='chi2', params=(-1/8., -7/8.,  0.,   0.,     0.))
        self.relax.interpreter._Align_tensor.init(tensor='chi3', params=(-1/8.,  1/16., 0.,   0.,    -15/16.))
        self.relax.interpreter._Align_tensor.init(tensor='chi4', params=(7/16., -7/8.,  0.,   9/16.,  0.))
        self.relax.interpreter._Align_tensor.init(tensor='chi5', params=(-1/2., -1/2.,  3/8., 0.,     0.))

        # Calculate the singular values.
        self.relax.interpreter._Align_tensor.svd(basis_set=0)
        self.relax.interpreter._Align_tensor.svd(basis_set=1)

        # Calculate the angles between the matrices.
        self.relax.interpreter._Align_tensor.matrix_angles(basis_set=0)
        self.relax.interpreter._Align_tensor.matrix_angles(basis_set=1)


        # Create the data pipe.
        self.relax.interpreter._Pipe.create('N domain', 'N-state')

        # Load the N-terminal alignment tensors.
        self.relax.interpreter._Align_tensor.init(tensor='chi1', params=(1/4.,   -1/2.,   0.,              3/4.,   0.))
        self.relax.interpreter._Align_tensor.init(tensor='chi2', params=(7/16.,  -7/8.,   0.,              9/16.,  0.))
        self.relax.interpreter._Align_tensor.init(tensor='chi3', params=(-1/32.,  1/16., -15/(16*sqrt(2)), 3/32., -15/(16*sqrt(2))))
        self.relax.interpreter._Align_tensor.init(tensor='chi4', params=(1.,     -7/8.,   0.,              0.,     0.))
        self.relax.interpreter._Align_tensor.init(tensor='chi5', params=(1/4.,   -1/2.,   3/(8*sqrt(2)),   3/4.,  -3/(8*sqrt(2))))

        # Calculate the singular values.
        self.relax.interpreter._Align_tensor.svd(basis_set=0)
        self.relax.interpreter._Align_tensor.svd(basis_set=1)

        # Calculate the angles between the matrices.
        self.relax.interpreter._Align_tensor.matrix_angles(basis_set=0)
        self.relax.interpreter._Align_tensor.matrix_angles(basis_set=1)

        # Grid search.
        self.relax.interpreter._Minimisation.grid_search(inc=11)

        # Minimise.
        self.relax.interpreter._Minimisation.minimise('simplex')

        # Finish.
        #self.relax.interpreter._Results.write(file='devnull', force=1)
