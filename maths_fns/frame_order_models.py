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
from copy import deepcopy
from numpy import float64, ones, zeros

# relax module imports.
from maths_fns.chi2 import chi2
from maths_fns.frame_order_matrix_ops import compile_2nd_matrix_iso_cone
from relax_errors import RelaxError


class Frame_order:
    """Class containing the target function of the optimisation of Frame Order matrix components."""

    def __init__(self, model=None, init_params=None, full_tensors=None, red_tensors=None, red_errors=None, frame_order_2nd=None):
        """Set up the target functions for the Frame Order theories.
        
        @keyword model:             The name of the Frame Order model.
        @type model:                str
        @keyword init_params:       The initial parameter values.
        @type init_params:          numpy float64 array
        @keyword full_tensors:      A list of the full alignment tensors in 5D, rank-1 form of {Sxx,
                                    Syy, Sxy, Sxz, Syz} values.
        @type full_tensors:         list of 5D, rank-1 arrays
        @keyword red_tensors:       An array of the {Sxx, Syy, Sxy, Sxz, Syz} values for all reduced
                                    tensors.  The format is [Sxx1, Syy1, Sxy1, Sxz1, Syz1, Sxx2,
                                    Syy2, Sxy2, Sxz2, Syz2, ..., Sxxn, Syyn, Sxyn, Sxzn, Syzn]
        @type red_tensors:          numpy nx5D, rank-1 float64 array
        @keyword red_errors:        An array of the {Sxx, Syy, Sxy, Sxz, Syz} errors for all reduced
                                    tensors.  The array format is the same as for red_tensors.
        @type red_errors:           numpy nx5D, rank-1 float64 array
        @keyword frame_order_2nd:   The numerical values of the 2nd degree Frame Order matrix.  If
                                    supplied, the target functions will optimise directly to these
                                    values.
        @type frame_order_2nd:      None or numpy 9D, rank-2 array
        """

        # Model test.
        if not model:
            raise RelaxError, "The type of Frame Order model must be specified."

        # Store the initial parameter (as a copy).
        self.params = deepcopy(init_params)

        # Isotropic cone model.
        if model == 'iso cone':
            # Mix up.
            if full_tensors != None and frame_order_2nd != None:
                raise RelaxError, "Tensors and Frame Order matrices cannot be supplied together."

            # Tensor optimisation.
            if full_tensors != None:
                self.__init_iso_cone_elements(full_tensors, red_tensors, red_errors)

            # Optimisation to the 2nd degree Frame Order matrix components directly.
            if frame_order_2nd != None:
                self.__init_iso_cone_elements(frame_order_2nd)


    def __init_iso_cone(self, full_tensors, red_tensors, red_errors):
        """Set up isotropic cone optimisation against the alignment tensor data.

        @keyword full_tensors:      A list of the full alignment tensors in 5D, rank-1 form of {Sxx,
                                    Syy, Sxy, Sxz, Syz} values.
        @type full_tensors:         list of 5D, rank-1 arrays
        @keyword red_tensors:       An array of the {Sxx, Syy, Sxy, Sxz, Syz} values for all reduced
                                    tensors.  The format is [Sxx1, Syy1, Sxy1, Sxz1, Syz1, Sxx2,
                                    Syy2, Sxy2, Sxz2, Syz2, ..., Sxxn, Syyn, Sxyn, Sxzn, Syzn]
        @type red_tensors:          numpy nx5D, rank-1 float64 array
        @keyword red_errors:        An array of the {Sxx, Syy, Sxy, Sxz, Syz} errors for all reduced
                                    tensors.  The array format is the same as for red_tensors.
        @type red_errors:           numpy nx5D, rank-1 float64 array
        """

        # Checks.
        if red_tensors != None:
            raise RelaxError, "The reduced tensors have not been supplied."

        # Tensor set up.
        self.full_tensors = array(full_tensors, float64)
        self.num_tensors = len(self.full_tensors)
        self.red_tensors = red_tensors
        self.red_errors = red_errors

        # The rotation to the Frame Order eigenframe.
        self.rot = zeros((3, 3), float64)

        # Initialise the Frame Order matrices.
        self.frame_order_2nd = zeros((9, 9), float64)

        # Alias the target function.
        self.func = self.func_iso_cone


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


    def func_iso_cone(self, params):
        """Target function for isotropic cone model optimisation using the alignment tensors.

        This function optimises against alignment tensors.  The Frame Order eigenframe via the
        alpha, beta, and gamma Euler angles, and the cone angle theta are the 4 parameters optimised
        in this model.

        @param params:  The vector of parameter values {alpha, beta, gamma, theta} where the first
                        three are the Euler angles for the Frame Order eigenframe and theta is the
                        isotropic cone angle.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Break up the parameters.
        alpha, beta, gamma, theta = params

        # Generate the 2nd degree Frame Order super matrix.
        compile_2nd_matrix_iso_cone(self.frame_order_2nd, self.rot, alpha, beta, gamma, theta)

        # Get the chi-squared value.
        val = chi2(self.data, self.frame_order_2nd, self.errors)

        # Return the chi2 value.
        return val


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

        # Generate the 2nd degree Frame Order super matrix.
        compile_2nd_matrix_iso_cone(self.frame_order_2nd, self.rot, alpha, beta, gamma, theta)

        # Make the Frame Order matrix contiguous.
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
