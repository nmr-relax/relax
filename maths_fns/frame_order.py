###############################################################################
#                                                                             #
# Copyright (C) 2009-2010 Edward d'Auvergne                                   #
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
from numpy import array, dot, float64, ones, transpose, zeros

# relax module imports.
from generic_fns.frame_order import print_frame_order_2nd_degree
from maths_fns.alignment_tensor import to_5D, to_tensor
from maths_fns.chi2 import chi2
from maths_fns.frame_order_matrix_ops import compile_2nd_matrix_iso_cone, compile_2nd_matrix_pseudo_ellipse, reduce_alignment_tensor
from maths_fns.rotation_matrix import euler_to_R_zyz as euler_to_R
from relax_errors import RelaxError


class Frame_order:
    """Class containing the target function of the optimisation of Frame Order matrix components."""

    def __init__(self, model=None, init_params=None, full_tensors=None, red_tensors=None, red_errors=None, full_in_ref_frame=None, frame_order_2nd=None):
        """Set up the target functions for the Frame Order theories.
        
        @keyword model:             The name of the Frame Order model.
        @type model:                str
        @keyword init_params:       The initial parameter values.
        @type init_params:          numpy float64 array
        @keyword full_tensors:      An array of the {Sxx, Syy, Sxy, Sxz, Syz} values for all full alignment tensors.  The format is [Sxx1, Syy1, Sxy1, Sxz1, Syz1, Sxx2, Syy2, Sxy2, Sxz2, Syz2, ..., Sxxn, Syyn, Sxyn, Sxzn, Syzn].
        @type full_tensors:         numpy nx5D, rank-1 float64 array
        @keyword red_tensors:       An array of the {Sxx, Syy, Sxy, Sxz, Syz} values for all reduced tensors.  The array format is the same as for full_tensors.
        @type red_tensors:          numpy nx5D, rank-1 float64 array
        @keyword red_errors:        An array of the {Sxx, Syy, Sxy, Sxz, Syz} errors for all reduced tensors.  The array format is the same as for full_tensors.
        @type red_errors:           numpy nx5D, rank-1 float64 array
        @keyword full_in_ref_frame: An array of flags specifying if the tensor in the reference frame is the full or reduced tensor.
        @type full_in_ref_frame:    numpy rank-1 array
        @keyword frame_order_2nd:   The numerical values of the 2nd degree Frame Order matrix.  If supplied, the target functions will optimise directly to these values.
        @type frame_order_2nd:      None or numpy 9D, rank-2 array
        """

        # Model test.
        if not model:
            raise RelaxError("The type of Frame Order model must be specified.")

        # Store the initial parameter (as a copy).
        self.params = deepcopy(init_params)

        # Store the agrs.
        self.model = model
        self.full_tensors = full_tensors
        self.red_tensors = red_tensors
        self.red_errors = red_errors
        self.full_in_ref_frame = full_in_ref_frame

        # Mix up.
        if full_tensors != None and frame_order_2nd != None:
            raise RelaxError("Tensors and Frame Order matrices cannot be supplied together.")
        if full_tensors == None and frame_order_2nd == None:
            raise RelaxError("The arguments have been incorrectly supplied, cannot determine the optimisation mode.")

        # Tensor setup.
        if full_tensors != None:
            self.__init_tensors()

        # The rigid model.
        if model == 'rigid':
            # Alias the target function.
            self.func = self.func_rigid

        # Isotropic cone model.
        if model == 'iso cone':
            # Optimisation to the 2nd degree Frame Order matrix components directly.
            if frame_order_2nd != None:
                self.__init_iso_cone_elements(frame_order_2nd)

            # The cone axis storage and molecular frame z-axis.
            self.cone_axis = zeros(3, float64)
            self.z_axis = array([0, 0, 1], float64)

            # Alias the target function.
            self.func = self.func_iso_cone

        # Pseudo-ellipse cone model.
        elif model == 'pseudo-ellipse':
            # Alias the target function.
            self.func = self.func_pseudo_ellipse


    def __init_tensors(self):
        """Set up isotropic cone optimisation against the alignment tensor data."""

        # Some checks.
        if self.full_tensors == None or not len(self.full_tensors):
            raise RelaxError("The full_tensors argument " + repr(self.full_tensors) + " must be supplied.")
        if self.red_tensors == None or not len(self.red_tensors):
            raise RelaxError("The red_tensors argument " + repr(self.red_tensors) + " must be supplied.")
        if self.red_errors == None or not len(self.red_errors):
            raise RelaxError("The red_errors argument " + repr(self.red_errors) + " must be supplied.")
        if self.full_in_ref_frame == None or not len(self.full_in_ref_frame):
            raise RelaxError("The full_in_ref_frame argument " + repr(self.full_in_ref_frame) + " must be supplied.")

        # Tensor set up.
        self.num_tensors = len(self.full_tensors) / 5
        self.red_tensors_bc = zeros(self.num_tensors*5, float64)

        # The rotation to the Frame Order eigenframe.
        self.rot = zeros((3, 3), float64)
        self.tensor_3D = zeros((3, 3), float64)

        # Initialise the Frame Order matrices.
        self.frame_order_2nd = zeros((9, 9), float64)


    def __init_iso_cone_elements(self, frame_order_2nd):
        """Set up isotropic cone optimisation against the 2nd degree Frame Order matrix elements.
        
        @keyword frame_order_2nd:   The numerical values of the 2nd degree Frame Order matrix.  If supplied, the target functions will optimise directly to these values.
        @type frame_order_2nd:      numpy 9D, rank-2 array
        """

        # Store the real matrix components.
        self.data = frame_order_2nd

        # The errors.
        self.errors = ones((9, 9), float64)

        # The cone axis storage and molecular frame z-axis.
        self.cone_axis = zeros(3, float64)
        self.z_axis = array([0, 0, 1], float64)

        # The rotation.
        self.rot = zeros((3, 3), float64)

        # Initialise the Frame Order matrices.
        self.frame_order_2nd = zeros((9, 9), float64)

        # Alias the target function.
        self.func = self.func_iso_cone_elements


    def func_rigid(self, params):
        """Target function for rigid model optimisation using the alignment tensors.

        This function optimises against alignment tensors.  The Euler angles for the tensor rotation are the 3 parameters optimised in this model.

        @param params:  The vector of parameter values.  These are the tensor rotation angles {alpha, beta, gamma}.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Unpack the parameters.
        alpha, beta, gamma = params

        # Alignment tensor rotation.
        euler_to_R(alpha, beta, gamma, self.rot)

        # Back calculate the rotated tensors.
        for i in range(self.num_tensors):
            # Tensor indices.
            index1 = i*5
            index2 = i*5+5

            # Convert the original tensor to 3D, rank-2 form.
            to_tensor(self.tensor_3D, self.full_tensors[index1:index2])

            # Rotate the tensor (normal R.X.RT rotation).
            if self.full_in_ref_frame[i]:
                tensor_3D = dot(self.rot, dot(self.tensor_3D, transpose(self.rot)))

            # Rotate the tensor (inverse RT.X.R rotation).
            else:
                tensor_3D = dot(transpose(self.rot), dot(self.tensor_3D, self.rot))

            # Convert the tensor back to 5D, rank-1 form, as the back-calculated reduced tensor.
            to_5D(self.red_tensors_bc[index1:index2], tensor_3D)

        # Return the chi-squared value.
        return chi2(self.red_tensors, self.red_tensors_bc, self.red_errors)


    def func_iso_cone(self, params):
        """Target function for isotropic cone model optimisation using the alignment tensors.

        This function optimises against alignment tensors.

        @param params:  The vector of parameter values {beta, gamma, theta, phi, s1} where the first 2 are the tensor rotation Euler angles, the next two are the polar and azimuthal angles of the cone axis, and s1 is the isotropic cone order parameter.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Unpack the parameters.
        beta, gamma, theta, phi, s1 = params

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_iso_cone(self.frame_order_2nd, self.rot, self.z_axis, self.cone_axis, theta, phi, s1)

        # Reduced alignment tensor rotation.
        euler_to_R(0.0, beta, gamma, self.rot)

        # Back calculate the reduced tensors.
        for i in range(self.num_tensors):
            # Tensor indices.
            index1 = i*5
            index2 = i*5+5

            # Reduce the tensor.
            reduce_alignment_tensor(frame_order_2nd, self.full_tensors[index1:index2], self.red_tensors_bc[index1:index2])

            # Convert the tensor to 3D, rank-2 form.
            to_tensor(self.tensor_3D, self.red_tensors_bc[index1:index2])

            # Rotate the tensor (normal R.X.RT rotation).
            if self.full_in_ref_frame[i]:
                tensor_3D = dot(self.rot, dot(self.tensor_3D, transpose(self.rot)))

            # Rotate the tensor (inverse RT.X.R rotation).
            else:
                tensor_3D = dot(transpose(self.rot), dot(saelf.tensor_3D, self.rot))

            # Convert the tensor back to 5D, rank-1 form.
            to_5D(self.red_tensors_bc[index1:index2], tensor_3D)

        # Return the chi-squared value.
        return chi2(self.red_tensors, self.red_tensors_bc, self.red_errors)


    def func_iso_cone_elements(self, params):
        """Target function for isotropic cone model optimisation using the Frame Order matrix.

        This function optimises by directly matching the elements of the 2nd degree Frame Order
        super matrix.  The cone axis spherical angles theta and phi and the cone angle theta are the
        3 parameters optimised in this model.

        @param params:  The vector of parameter values {theta, phi, theta_cone} where the first two are the polar and azimuthal angles of the cone axis theta_cone is the isotropic cone angle.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Break up the parameters.
        theta, phi, theta_cone = params

        # Generate the 2nd degree Frame Order super matrix.
        self.frame_order_2nd = compile_2nd_matrix_iso_cone(self.frame_order_2nd, self.rot, self.z_axis, self.cone_axis, theta, phi, theta_cone)

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


    def func_pseudo_ellipse(self, params):
        """Target function for pseudo-elliptic cone model optimisation using alignment tensors.

        @param params:  The vector of parameter values {alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max} where the first 3 are the average position rotation Euler angles, the next 3 are the Euler angles defining the eigenframe, and the last 3 are the pseudo-elliptic cone geometric parameters.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Unpack the parameters.
        alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = params

        # Generate the 2nd degree Frame Order super matrix.
        frame_order_2nd = compile_2nd_matrix_pseudo_ellipse(self.frame_order_2nd, self.rot, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max)

        # Average position rotation.
        euler_to_R(alpha, beta, gamma, self.rot)

        # Back calculate the reduced tensors.
        for i in range(self.num_tensors):
            # Tensor indices.
            index1 = i*5
            index2 = i*5+5

            # Reduce the tensor.
            reduce_alignment_tensor(frame_order_2nd, self.full_tensors[index1:index2], self.red_tensors_bc[index1:index2])

            # Convert the tensor to 3D, rank-2 form.
            to_tensor(self.tensor_3D, self.red_tensors_bc[index1:index2])

            # Rotate the tensor (normal R.X.RT rotation).
            if self.full_in_ref_frame[i]:
                tensor_3D = dot(self.rot, dot(self.tensor_3D, transpose(self.rot)))

            # Rotate the tensor (inverse RT.X.R rotation).
            else:
                tensor_3D = dot(transpose(self.rot), dot(self.tensor_3D, self.rot))

            # Convert the tensor back to 5D, rank-1 form.
            to_5D(self.red_tensors_bc[index1:index2], tensor_3D)

        # Return the chi-squared value.
        return chi2(self.red_tensors, self.red_tensors_bc, self.red_errors)
