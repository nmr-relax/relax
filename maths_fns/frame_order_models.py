###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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

# Module docstring.
"""Module containing the target functions of the Frame Order theories."""

# Python module imports.
from numpy import dot, float64, ones, transpose, zeros

# relax module imports.
from maths_fns.chi2 import chi2
from maths_fns.frame_order_matrix_ops import populate_2nd_eigenframe_iso_cone
from maths_fns.kronecker_product import kron_prod, transpose_14
from maths_fns.rotation_matrix import R_euler_zyz
from relax_errors import RelaxError


class Frame_order:
    """Class containing the target function of the optimisation of Frame Order matrix components."""

    def __init__(self, model=None, frame_order_2nd=None):
        """Set up the target functions for the Frame Order theories.
        
        @keyword model:             The name of the Frame Order model.
        @type model:                str
        @keyword frame_order_2nd:   The numerical values of the 2nd degree Frame Order matrix.  If
                                    supplied, the target functions will optimise directly to these
                                    values.
        @type frame_order_2nd:      None or numpy 9D, rank-2 array
        """

        # Model test.
        if not model:
            raise RelaxError, "The type of Frame Order model must be specified."

        # Isotropic cone model.
        if model == 'iso cone':
            # Optimisation to the 2nd degree Frame Order matrix components directly.
            if frame_order_2nd != None:
                self.__init_iso_cone_elements(frame_order_2nd)


    def __init_iso_cone_elements(self, frame_order_2nd):
        """Set up isotropic cone optimisation against the 2nd degree Frame Order matrix elements.
        
        @keyword frame_order_2nd:   The numerical values of the 2nd degree Frame Order matrix.  If
                                    supplied, the target functions will optimise directly to these
                                    values.
        @type frame_order_2nd:      numpy 9D, rank-2 array
        """

        # Store the real matrix components.
        self.data = frame_order_2nd

        # The errors.
        self.errors = ones((9, 9), float64)

        # The rotation.
        self.rot = zeros((3, 3), float64)

        # Initialise the Frame Order matrices.
        self.frame_order_2nd = zeros((9, 9), float64)

        # Alias the target function.
        self.func = self.func_iso_cone_elements


    def func_iso_cone_elements(self, params):
        """Target function for isotropic cone model optimisation using the Frame Order matrix.

        This function optimises by directly matching the elements of the 2nd degree Frame Order
        super matrix.  The Frame Order eigenframe via the alpha, beta, and gamma Euler angles, and
        the cone angle theta are the 4 parameters optimised in this model.

        @param params:  The vector of parameter values {alpha, beta, gamma, theta} where the first
                        three are the Euler angles for the Frame Order eigenframe and theta is the
                        isotropic cone angle.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Break up the parameters.
        alpha, beta, gamma, theta = params

        # Populate the Frame Order matrix in the eigenframe.
        populate_2nd_eigenframe_iso_cone(self.frame_order_2nd, theta)

        # Generate the rotation matrix.
        R_euler_zyz(self.rot, alpha, beta, gamma)

        # The outer product of R.
        R_kron = kron_prod(self.rot, self.rot)

        # Perform the T14 transpose to obtain the Kronecker product matrix!
        self.frame_order_2nd = transpose_14(self.frame_order_2nd)

        # Rotate.
        self.frame_order_2nd = dot(R_kron, dot(self.frame_order_2nd, transpose(R_kron)))

        # Perform T14 again to return back.
        self.frame_order_2nd = transpose_14(self.frame_order_2nd)

        # Make the Frame Order contiguous.
        self.frame_order_2nd = self.frame_order_2nd.copy()

        # Reshape the numpy arrays for use in the chi2() function.
        self.data.shape = (81,)
        self.frame_order_2nd.shape = (81,)
        self.errors.shape = (81,)

        # Get the chi-squared value.
        val = chi2(self.data, self.frame_order_2nd, self.errors)

        # Reshape the arrays back to normal.
        self.data.shape = (9, 9)
        self.frame_order_2nd.shape = (9, 9)
        self.errors.shape = (9, 9)

        # Return the chi2 value.
        return val
