###############################################################################
#                                                                             #
# Copyright (C) 2004-2005, 2008-2009 Edward d'Auvergne                        #
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
from math import acos, asin, atan2, cos, pi, sin, sqrt
from numpy import array, cross, dot, float64, hypot, transpose, zeros
from numpy.linalg import norm
from random import gauss, uniform


def axis_angle_to_euler_xyx(axis, angle):
    """Convert the axis-angle notation to xyx Euler angles.

    This first generates a rotation matrix via axis_angle_to_R() and then used this together with R_to_euler_xyx() to obtain the Euler angles.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @return:        The alpha, beta, and gamma Euler angles in the xyx convention.
    @rtype:         float, float, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    axis_angle_to_R(axis, angle, R)

    # Return the Euler angles.
    return R_to_euler_xyx(R)


def axis_angle_to_euler_xyz(axis, angle):
    """Convert the axis-angle notation to xyz Euler angles.

    This first generates a rotation matrix via axis_angle_to_R() and then used this together with R_to_euler_xyz() to obtain the Euler angles.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @return:        The alpha, beta, and gamma Euler angles in the xyz convention.
    @rtype:         float, float, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    axis_angle_to_R(axis, angle, R)

    # Return the Euler angles.
    return R_to_euler_xyz(R)


def axis_angle_to_euler_xzx(axis, angle):
    """Convert the axis-angle notation to xzx Euler angles.

    This first generates a rotation matrix via axis_angle_to_R() and then used this together with R_to_euler_xzx() to obtain the Euler angles.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @return:        The alpha, beta, and gamma Euler angles in the xzx convention.
    @rtype:         float, float, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    axis_angle_to_R(axis, angle, R)

    # Return the Euler angles.
    return R_to_euler_xzx(R)


def axis_angle_to_euler_xzy(axis, angle):
    """Convert the axis-angle notation to xzy Euler angles.

    This first generates a rotation matrix via axis_angle_to_R() and then used this together with R_to_euler_xzy() to obtain the Euler angles.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @return:        The alpha, beta, and gamma Euler angles in the xzy convention.
    @rtype:         float, float, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    axis_angle_to_R(axis, angle, R)

    # Return the Euler angles.
    return R_to_euler_xzy(R)


def axis_angle_to_euler_yxy(axis, angle):
    """Convert the axis-angle notation to yxy Euler angles.

    This first generates a rotation matrix via axis_angle_to_R() and then used this together with R_to_euler_yxy() to obtain the Euler angles.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @return:        The alpha, beta, and gamma Euler angles in the yxy convention.
    @rtype:         float, float, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    axis_angle_to_R(axis, angle, R)

    # Return the Euler angles.
    return R_to_euler_yxy(R)


def axis_angle_to_euler_yxz(axis, angle):
    """Convert the axis-angle notation to yxz Euler angles.

    This first generates a rotation matrix via axis_angle_to_R() and then used this together with R_to_euler_yxz() to obtain the Euler angles.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @return:        The alpha, beta, and gamma Euler angles in the yxz convention.
    @rtype:         float, float, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    axis_angle_to_R(axis, angle, R)

    # Return the Euler angles.
    return R_to_euler_yxz(R)


def axis_angle_to_euler_yzx(axis, angle):
    """Convert the axis-angle notation to yzx Euler angles.

    This first generates a rotation matrix via axis_angle_to_R() and then used this together with R_to_euler_yzx() to obtain the Euler angles.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @return:        The alpha, beta, and gamma Euler angles in the yzx convention.
    @rtype:         float, float, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    axis_angle_to_R(axis, angle, R)

    # Return the Euler angles.
    return R_to_euler_yzx(R)


def axis_angle_to_euler_yzy(axis, angle):
    """Convert the axis-angle notation to yzy Euler angles.

    This first generates a rotation matrix via axis_angle_to_R() and then used this together with R_to_euler_yzy() to obtain the Euler angles.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @return:        The alpha, beta, and gamma Euler angles in the yzy convention.
    @rtype:         float, float, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    axis_angle_to_R(axis, angle, R)

    # Return the Euler angles.
    return R_to_euler_yzy(R)


def axis_angle_to_euler_zxy(axis, angle):
    """Convert the axis-angle notation to zxy Euler angles.

    This first generates a rotation matrix via axis_angle_to_R() and then used this together with R_to_euler_zxy() to obtain the Euler angles.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @return:        The alpha, beta, and gamma Euler angles in the zxy convention.
    @rtype:         float, float, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    axis_angle_to_R(axis, angle, R)

    # Return the Euler angles.
    return R_to_euler_zxy(R)


def axis_angle_to_euler_zxz(axis, angle):
    """Convert the axis-angle notation to zxz Euler angles.

    This first generates a rotation matrix via axis_angle_to_R() and then used this together with R_to_euler_zxz() to obtain the Euler angles.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @return:        The alpha, beta, and gamma Euler angles in the zxz convention.
    @rtype:         float, float, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    axis_angle_to_R(axis, angle, R)

    # Return the Euler angles.
    return R_to_euler_zxz(R)


def axis_angle_to_euler_zyx(axis, angle):
    """Convert the axis-angle notation to zyx Euler angles.

    This first generates a rotation matrix via axis_angle_to_R() and then used this together with R_to_euler_zyx() to obtain the Euler angles.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @return:        The alpha, beta, and gamma Euler angles in the zyx convention.
    @rtype:         float, float, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    axis_angle_to_R(axis, angle, R)

    # Return the Euler angles.
    return R_to_euler_zyx(R)


def axis_angle_to_euler_zyz(axis, angle):
    """Convert the axis-angle notation to zyz Euler angles.

    This first generates a rotation matrix via axis_angle_to_R() and then used this together with R_to_euler_zyz() to obtain the Euler angles.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @return:        The alpha, beta, and gamma Euler angles in the zyz convention.
    @rtype:         float, float, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    axis_angle_to_R(axis, angle, R)

    # Return the Euler angles.
    return R_to_euler_zyz(R)


def axis_angle_to_R(axis, angle, R):
    """Generate the rotation matrix from the axis-angle notation.

    Conversion equations
    ====================

    From Wikipedia (http://en.wikipedia.org/wiki/Rotation_matrix), the conversion is given by::

        c = cos(angle); s = sin(angle); C = 1-c
        xs = x*s;   ys = y*s;   zs = z*s
        xC = x*C;   yC = y*C;   zC = z*C
        xyC = x*yC; yzC = y*zC; zxC = z*xC
        [ x*xC+c   xyC-zs   zxC+ys ]
        [ xyC+zs   y*yC+c   yzC-xs ]
        [ zxC-ys   yzC+xs   z*zC+c ]


    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    @param angle:   The rotation angle.
    @type angle:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig factors.
    ca = cos(angle)
    sa = sin(angle)
    C = 1 - ca

    # Depack the axis.
    x, y, z = axis

    # Multiplications (to remove duplicate calculations).
    xs = x*sa
    ys = y*sa
    zs = z*sa
    xC = x*C
    yC = y*C
    zC = z*C
    xyC = x*yC
    yzC = y*zC
    zxC = z*xC

    # Update the rotation matrix.
    R[0, 0] = x*xC + ca
    R[0, 1] = xyC - zs
    R[0, 2] = zxC + ys
    R[1, 0] = xyC + zs
    R[1, 1] = y*yC + ca
    R[1, 2] = yzC - xs
    R[2, 0] = zxC - ys
    R[2, 1] = yzC + xs
    R[2, 2] = z*zC + ca


def axis_angle_to_quaternion(axis, angle, quat, norm_flag=True):
    """Generate the quaternion from the axis-angle notation.

    Conversion equations
    ====================

    From Wolfram MathWorld (http://mathworld.wolfram.com/Quaternion.html), the conversion is given by::

        q = (cos(angle/2), n * sin(angle/2)),

    where q is the quaternion and n is the unit vector representing the rotation axis.


    @param axis:        The 3D rotation axis.
    @type axis:         numpy array, len 3
    @param angle:       The rotation angle.
    @type angle:        float
    @param quat:        The quaternion structure.
    @type quat:         numpy 4D, rank-1 array
    @keyword norm_flag: A flag which if True forces the axis to be converted to a unit vector.
    @type norm_flag:    bool
    """

    # Convert to unit vector.
    if norm_flag:
        axis = axis / norm(axis)

    # The scalar component of q.
    quat[0] = cos(angle/2)

    # The vector component.
    quat[1:] = axis * sin(angle/2)


def euler_xyx_to_axis_angle(alpha, beta, gamma):
    """Convert the xyx Euler angles to axis-angle notation.

    This function first generates a rotation matrix via euler_*_to_R() and then uses R_to_axis_angle() to convert to the axis and angle notation.

    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_xyx_to_R(alpha, beta, gamma, R)

    # Return the axis and angle.
    return R_to_axis_angle(R)


def euler_xyx_to_R(alpha, beta, gamma, R):
    """Generate the x-y-x Euler angle convention rotation matrix.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the xyx convention is::

              |  cb                  sa*sb               ca*sb            |
        R  =  |  sa*sb               ca*cg - sa*cb*sg   -sa*cg - ca*cb*sg |,
              | -sb*cg               ca*sg + sa*cb*cg   -sa*sg + ca*cb*cg |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param alpha:   The alpha Euler angle in rad for the x-rotation.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad for the y-rotation.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad for the second x-rotation.
    @type gamma:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig.
    sin_a = sin(alpha)
    cos_a = cos(alpha)
    sin_b = sin(beta)
    cos_b = cos(beta)
    sin_g = sin(gamma)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    R[0, 0] =  cos_b
    R[1, 0] =  sin_a * sin_b
    R[2, 0] = -sin_b * cos_g

    # The unit muy vector component of the rotation matrix.
    R[0, 1] =  sin_a * sin_b
    R[1, 1] =  cos_a * cos_g  -  sin_a * cos_b * sin_g
    R[2, 1] =  cos_a * sin_g  +  sin_a * cos_b * cos_g

    # The unit muz vector component of the rotation matrix.
    R[0, 2] =  cos_a * sin_b
    R[1, 2] = -sin_a * cos_g  -  cos_a * cos_b * sin_g
    R[2, 2] = -sin_a * sin_g  +  cos_a * cos_b * cos_g


def euler_xyz_to_axis_angle(alpha, beta, gamma):
    """Convert the xyz Euler angles to axis-angle notation.

    This function first generates a rotation matrix via euler_*_to_R() and then uses R_to_axis_angle() to convert to the axis and angle notation.

    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_xyz_to_R(alpha, beta, gamma, R)

    # Return the axis and angle.
    return R_to_axis_angle(R)


def euler_xyz_to_R(alpha, beta, gamma, R):
    """Generate the x-y-z Euler angle convention rotation matrix.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the xyz convention is::

              |  cb*cg              -ca*sg + sa*sb*cg    sa*sg + ca*sb*cg |
        R  =  |  cb*sg               ca*cg + sa*sb*sg   -sa*cg + ca*sb*sg |,
              | -sb                  sa*cb               ca*cb            |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param alpha:   The alpha Euler angle in rad for the x-rotation.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad for the y-rotation.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad for the z-rotation.
    @type gamma:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig.
    sin_a = sin(alpha)
    cos_a = cos(alpha)
    sin_b = sin(beta)
    cos_b = cos(beta)
    sin_g = sin(gamma)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    R[0, 0] =  cos_b * cos_g
    R[1, 0] =  cos_b * sin_g
    R[2, 0] = -sin_b

    # The unit muy vector component of the rotation matrix.
    R[0, 1] = -cos_a * sin_g  +  sin_a * sin_b * cos_g
    R[1, 1] =  cos_a * cos_g  +  sin_a * sin_b * sin_g
    R[2, 1] =  sin_a * cos_b

    # The unit muz vector component of the rotation matrix.
    R[0, 2] =  sin_a * sin_g  +  cos_a * sin_b * cos_g
    R[1, 2] = -sin_a * cos_g  +  cos_a * sin_b * sin_g
    R[2, 2] =  cos_a * cos_b


def euler_xzx_to_axis_angle(alpha, beta, gamma):
    """Convert the xzx Euler angles to axis-angle notation.

    This function first generates a rotation matrix via euler_*_to_R() and then uses R_to_axis_angle() to convert to the axis and angle notation.

    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_xzx_to_R(alpha, beta, gamma, R)

    # Return the axis and angle.
    return R_to_axis_angle(R)


def euler_xzx_to_R(alpha, beta, gamma, R):
    """Generate the x-z-x Euler angle convention rotation matrix.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the xzx convention is::

              |  cb                 -ca*sb               sa*sb            |
        R  =  |  sb*cg              -sa*sg + ca*cb*cg   -ca*sg - sa*cb*cg |,
              |  sb*sg               sa*cg + ca*cb*sg    ca*cg - sa*cb*sg |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param alpha:   The alpha Euler angle in rad for the x-rotation.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad for the z-rotation.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad for the second x-rotation.
    @type gamma:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig.
    sin_a = sin(alpha)
    cos_a = cos(alpha)
    sin_b = sin(beta)
    cos_b = cos(beta)
    sin_g = sin(gamma)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    R[0, 0] =  cos_b
    R[1, 0] =  sin_b * cos_g
    R[2, 0] =  sin_b * sin_g

    # The unit muy vector component of the rotation matrix.
    R[0, 1] = -cos_a * sin_b
    R[1, 1] = -sin_a * sin_g  +  cos_a * cos_b * cos_g
    R[2, 1] =  sin_a * cos_g  +  cos_a * cos_b * sin_g

    # The unit muz vector component of the rotation matrix.
    R[0, 2] =  sin_a * sin_b
    R[1, 2] = -cos_a * sin_g  -  sin_a * cos_b * cos_g
    R[2, 2] =  cos_a * cos_g  -  sin_a * cos_b * sin_g


def euler_xzy_to_axis_angle(alpha, beta, gamma):
    """Convert the xzy Euler angles to axis-angle notation.

    This function first generates a rotation matrix via euler_*_to_R() and then uses R_to_axis_angle() to convert to the axis and angle notation.

    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_xzy_to_R(alpha, beta, gamma, R)

    # Return the axis and angle.
    return R_to_axis_angle(R)


def euler_xzy_to_R(alpha, beta, gamma, R):
    """Generate the x-z-y Euler angle convention rotation matrix.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the xzy convention is::

              |  cb*cg               sa*sg - ca*sb*cg    ca*sg + sa*sb*cg |
        R  =  |  sb                  ca*cb              -sa*cb            |,
              | -cb*sg               sa*cg + ca*sb*sg    ca*cg - sa*sb*sg |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param alpha:   The alpha Euler angle in rad for the x-rotation.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad for the z-rotation.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad for the y-rotation.
    @type gamma:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig.
    sin_a = sin(alpha)
    cos_a = cos(alpha)
    sin_b = sin(beta)
    cos_b = cos(beta)
    sin_g = sin(gamma)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    R[0, 0] =  cos_b * cos_g
    R[1, 0] =  sin_b
    R[2, 0] = -cos_b * sin_g

    # The unit muy vector component of the rotation matrix.
    R[0, 1] =  sin_a * sin_g  -  cos_a * sin_b * cos_g
    R[1, 1] =  cos_a * cos_b
    R[2, 1] =  sin_a * cos_g  +  cos_a * sin_b * sin_g

    # The unit muz vector component of the rotation matrix.
    R[0, 2] =  cos_a * sin_g  +  sin_a * sin_b * cos_g
    R[1, 2] = -sin_a * cos_b
    R[2, 2] =  cos_a * cos_g  -  sin_a * sin_b * sin_g


def euler_yxy_to_axis_angle(alpha, beta, gamma):
    """Convert the yxy Euler angles to axis-angle notation.

    This function first generates a rotation matrix via euler_*_to_R() and then uses R_to_axis_angle() to convert to the axis and angle notation.

    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_yxy_to_R(alpha, beta, gamma, R)

    # Return the axis and angle.
    return R_to_axis_angle(R)


def euler_yxy_to_R(alpha, beta, gamma, R):
    """Generate the y-x-y Euler angle convention rotation matrix.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the yxy convention is::

              |  ca*cg - sa*cb*sg    sb*sg               sa*cg + ca*cb*sg |
        R  =  |  sa*sb               cb                 -ca*sb            |,
              | -ca*sg - sa*cb*cg    sb*cg              -sa*sg + ca*cb*cg |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param alpha:   The alpha Euler angle in rad for the y-rotation.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad for the x-rotation.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad for the second y-rotation.
    @type gamma:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig.
    sin_a = sin(alpha)
    cos_a = cos(alpha)
    sin_b = sin(beta)
    cos_b = cos(beta)
    sin_g = sin(gamma)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    R[0, 0] =  cos_a * cos_g  -  sin_a * cos_b * sin_g
    R[1, 0] =  sin_a * sin_b
    R[2, 0] = -cos_a * sin_g  -  sin_a * cos_b * cos_g

    # The unit muy vector component of the rotation matrix.
    R[0, 1] =  sin_b * sin_g
    R[1, 1] =  cos_b
    R[2, 1] =  sin_b * cos_g

    # The unit muz vector component of the rotation matrix.
    R[0, 2] =  sin_a * cos_g  +  cos_a * cos_b * sin_g
    R[1, 2] = -cos_a * sin_b
    R[2, 2] = -sin_a * sin_g  +  cos_a * cos_b * cos_g


def euler_yxz_to_axis_angle(alpha, beta, gamma):
    """Convert the yxz Euler angles to axis-angle notation.

    This function first generates a rotation matrix via euler_*_to_R() and then uses R_to_axis_angle() to convert to the axis and angle notation.

    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_yxz_to_R(alpha, beta, gamma, R)

    # Return the axis and angle.
    return R_to_axis_angle(R)


def euler_yxz_to_R(alpha, beta, gamma, R):
    """Generate the y-x-z Euler angle convention rotation matrix.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the yxz convention is::

              |  ca*cg - sa*sb*sg   -cb*sg               sa*cg + ca*sb*sg |
        R  =  |  ca*sg + sa*sb*cg    cb*cg               sa*sg - ca*sb*cg |,
              | -sa*cb               sb                  ca*cb            |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param alpha:   The alpha Euler angle in rad for the y-rotation.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad for the x-rotation.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad for the z-rotation.
    @type gamma:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig.
    sin_a = sin(alpha)
    cos_a = cos(alpha)
    sin_b = sin(beta)
    cos_b = cos(beta)
    sin_g = sin(gamma)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    R[0, 0] =  cos_a * cos_g  -  sin_a * sin_b * sin_g
    R[1, 0] =  cos_a * sin_g  +  sin_a * sin_b * cos_g
    R[2, 0] = -sin_a * cos_b

    # The unit muy vector component of the rotation matrix.
    R[0, 1] = -cos_b * sin_g
    R[1, 1] =  cos_b * cos_g
    R[2, 1] =  sin_b

    # The unit muz vector component of the rotation matrix.
    R[0, 2] =  sin_a * cos_g  +  cos_a * sin_b * sin_g
    R[1, 2] =  sin_a * sin_g  -  cos_a * sin_b * cos_g
    R[2, 2] =  cos_a * cos_b


def euler_yzx_to_axis_angle(alpha, beta, gamma):
    """Convert the yzx Euler angles to axis-angle notation.

    This function first generates a rotation matrix via euler_*_to_R() and then uses R_to_axis_angle() to convert to the axis and angle notation.

    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_yzx_to_R(alpha, beta, gamma, R)

    # Return the axis and angle.
    return R_to_axis_angle(R)


def euler_yzx_to_R(alpha, beta, gamma, R):
    """Generate the y-z-x Euler angle convention rotation matrix.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the yzx convention is::

              |  ca*cb              -sb                  sa*cb            |
        R  =  |  sa*sg + ca*sb*cg    cb*cg              -ca*sg + sa*sb*cg |,
              | -sa*cg + ca*sb*sg    cb*sg               ca*cg + sa*sb*sg |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param alpha:   The alpha Euler angle in rad for the y-rotation.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad for the z-rotation.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad for the x-rotation.
    @type gamma:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig.
    sin_a = sin(alpha)
    cos_a = cos(alpha)
    sin_b = sin(beta)
    cos_b = cos(beta)
    sin_g = sin(gamma)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    R[0, 0] =  cos_a * cos_b
    R[1, 0] =  sin_a * sin_g  +  cos_a * sin_b * cos_g
    R[2, 0] = -sin_a * cos_g  +  cos_a * sin_b * sin_g

    # The unit muy vector component of the rotation matrix.
    R[0, 1] = -sin_b
    R[1, 1] =  cos_b * cos_g
    R[2, 1] =  cos_b * sin_g

    # The unit muz vector component of the rotation matrix.
    R[0, 2] =  sin_a * cos_b
    R[1, 2] = -cos_a * sin_g  +  sin_a * sin_b * cos_g
    R[2, 2] =  cos_a * cos_g  +  sin_a * sin_b * sin_g


def euler_yzy_to_axis_angle(alpha, beta, gamma):
    """Convert the yzy Euler angles to axis-angle notation.

    This function first generates a rotation matrix via euler_*_to_R() and then uses R_to_axis_angle() to convert to the axis and angle notation.

    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_yzy_to_R(alpha, beta, gamma, R)

    # Return the axis and angle.
    return R_to_axis_angle(R)


def euler_yzy_to_R(alpha, beta, gamma, R):
    """Generate the y-z-y Euler angle convention rotation matrix.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the yzy convention is::

              | -sa*sg + ca*cb*cg   -sb*cg               ca*sg + sa*cb*cg |
        R  =  |  ca*sb               cb                  sa*sb            |,
              | -sa*cg - ca*cb*sg    sb*sg               ca*cg - sa*cb*sg |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param alpha:   The alpha Euler angle in rad for the y-rotation.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad for the z-rotation.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad for the second y-rotation.
    @type gamma:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig.
    sin_a = sin(alpha)
    cos_a = cos(alpha)
    sin_b = sin(beta)
    cos_b = cos(beta)
    sin_g = sin(gamma)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    R[0, 0] = -sin_a * sin_g  +  cos_a * cos_b * cos_g
    R[1, 0] =  cos_a * sin_b
    R[2, 0] = -sin_a * cos_g  -  cos_a * cos_b * sin_g

    # The unit muy vector component of the rotation matrix.
    R[0, 1] = -sin_b * cos_g
    R[1, 1] =  cos_b
    R[2, 1] =  sin_b * sin_g

    # The unit muz vector component of the rotation matrix.
    R[0, 2] =  cos_a * sin_g  +  sin_a * cos_b * cos_g
    R[1, 2] =  sin_a * sin_b
    R[2, 2] =  cos_a * cos_g  -  sin_a * cos_b * sin_g


def euler_zxy_to_axis_angle(alpha, beta, gamma):
    """Convert the zxy Euler angles to axis-angle notation.

    This function first generates a rotation matrix via euler_*_to_R() and then uses R_to_axis_angle() to convert to the axis and angle notation.

    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_zxy_to_R(alpha, beta, gamma, R)

    # Return the axis and angle.
    return R_to_axis_angle(R)


def euler_zxy_to_R(alpha, beta, gamma, R):
    """Generate the z-x-y Euler angle convention rotation matrix.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the zxy convention is::

              |  ca*cg + sa*sb*sg   -sa*cg + ca*sb*sg    cb*sg            |
        R  =  |  sa*cb               ca*cb              -sb               |,
              | -ca*sg + sa*sb*cg    sa*sg + ca*sb*cg    cb*cg            |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param alpha:   The alpha Euler angle in rad for the z-rotation.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad for the x-rotation.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad for the y-rotation.
    @type gamma:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig.
    sin_a = sin(alpha)
    cos_a = cos(alpha)
    sin_b = sin(beta)
    cos_b = cos(beta)
    sin_g = sin(gamma)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    R[0, 0] =  cos_a * cos_g  +  sin_a * sin_b * sin_g
    R[1, 0] =  sin_a * cos_b
    R[2, 0] = -cos_a * sin_g  +  sin_a * sin_b * cos_g

    # The unit muy vector component of the rotation matrix.
    R[0, 1] = -sin_a * cos_g  +  cos_a * sin_b * sin_g
    R[1, 1] =  cos_a * cos_b
    R[2, 1] =  sin_a * sin_g  +  cos_a * sin_b * cos_g

    # The unit muz vector component of the rotation matrix.
    R[0, 2] =  cos_b * sin_g
    R[1, 2] = -sin_b
    R[2, 2] =  cos_b * cos_g


def euler_zxz_to_axis_angle(alpha, beta, gamma):
    """Convert the zxz Euler angles to axis-angle notation.

    This function first generates a rotation matrix via euler_*_to_R() and then uses R_to_axis_angle() to convert to the axis and angle notation.

    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_zxz_to_R(alpha, beta, gamma, R)

    # Return the axis and angle.
    return R_to_axis_angle(R)


def euler_zxz_to_R(alpha, beta, gamma, R):
    """Generate the z-x-z Euler angle convention rotation matrix.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the zxz convention is::

              |  ca*cg - sa*cb*sg   -sa*cg - ca*cb*sg    sb*sg            |
        R  =  |  ca*sg + sa*cb*cg   -sa*sg + ca*cb*cg   -sb*cg            |,
              |  sa*sb               ca*sb               cb               |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param alpha:   The alpha Euler angle in rad for the z-rotation.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad for the y-rotation.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad for the second z-rotation.
    @type gamma:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig.
    sin_a = sin(alpha)
    cos_a = cos(alpha)
    sin_b = sin(beta)
    cos_b = cos(beta)
    sin_g = sin(gamma)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    R[0, 0] =  cos_a * cos_g  -  sin_a * cos_b * sin_g
    R[1, 0] =  cos_a * sin_g  +  sin_a * cos_b * cos_g
    R[2, 0] =  sin_a * sin_b

    # The unit muy vector component of the rotation matrix.
    R[0, 1] = -sin_a * cos_g  -  cos_a * cos_b * sin_g
    R[1, 1] = -sin_a * sin_g  +  cos_a * cos_b * cos_g
    R[2, 1] =  cos_a * sin_b

    # The unit muz vector component of the rotation matrix.
    R[0, 2] =  sin_b * sin_g
    R[1, 2] = -sin_b * cos_g
    R[2, 2] =  cos_b


def euler_zyx_to_axis_angle(alpha, beta, gamma):
    """Convert the zyx Euler angles to axis-angle notation.

    This function first generates a rotation matrix via euler_*_to_R() and then uses R_to_axis_angle() to convert to the axis and angle notation.

    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_zyx_to_R(alpha, beta, gamma, R)

    # Return the axis and angle.
    return R_to_axis_angle(R)


def euler_zyx_to_R(alpha, beta, gamma, R):
    """Generate the z-y-x Euler angle convention rotation matrix.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the zyx convention is::

              |  ca*cb              -sa*cb               sb               |
        R  =  |  sa*cg + ca*sb*sg    ca*cg - sa*sb*sg   -cb*sg            |,
              |  sa*sg - ca*sb*cg    ca*sg + sa*sb*cg    cb*cg            |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param alpha:   The alpha Euler angle in rad for the z-rotation.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad for the y-rotation.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad for the x-rotation.
    @type gamma:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig.
    sin_a = sin(alpha)
    cos_a = cos(alpha)
    sin_b = sin(beta)
    cos_b = cos(beta)
    sin_g = sin(gamma)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    R[0, 0] =  cos_a * cos_b
    R[1, 0] =  sin_a * cos_g  +  cos_a * sin_b * sin_g
    R[2, 0] =  sin_a * sin_g  -  cos_a * sin_b * cos_g

    # The unit muy vector component of the rotation matrix.
    R[0, 1] = -sin_a * cos_b
    R[1, 1] =  cos_a * cos_g  -  sin_a * sin_b * sin_g
    R[2, 1] =  cos_a * sin_g  +  sin_a * sin_b * cos_g

    # The unit muz vector component of the rotation matrix.
    R[0, 2] =  sin_b
    R[1, 2] = -cos_b * sin_g
    R[2, 2] =  cos_b * cos_g


def euler_zyz_to_axis_angle(alpha, beta, gamma):
    """Convert the zyz Euler angles to axis-angle notation.

    This function first generates a rotation matrix via euler_*_to_R() and then uses R_to_axis_angle() to convert to the axis and angle notation.

    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_zyz_to_R(alpha, beta, gamma, R)

    # Return the axis and angle.
    return R_to_axis_angle(R)


def euler_zyz_to_R(alpha, beta, gamma, R):
    """Generate the z-y-z Euler angle convention rotation matrix.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the zyz convention is::

              | -sa*sg + ca*cb*cg   -ca*sg - sa*cb*cg    sb*cg            |
        R  =  |  sa*cg + ca*cb*sg    ca*cg - sa*cb*sg    sb*sg            |,
              | -ca*sb               sa*sb               cb               |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param alpha:   The alpha Euler angle in rad for the z-rotation.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad for the y-rotation.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad for the second z-rotation.
    @type gamma:    float
    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    """

    # Trig.
    sin_a = sin(alpha)
    cos_a = cos(alpha)
    sin_b = sin(beta)
    cos_b = cos(beta)
    sin_g = sin(gamma)
    cos_g = cos(gamma)

    # The unit mux vector component of the rotation matrix.
    R[0, 0] = -sin_a * sin_g  +  cos_a * cos_b * cos_g
    R[1, 0] =  sin_a * cos_g  +  cos_a * cos_b * sin_g
    R[2, 0] = -cos_a * sin_b

    # The unit muy vector component of the rotation matrix.
    R[0, 1] = -cos_a * sin_g  -  sin_a * cos_b * cos_g
    R[1, 1] =  cos_a * cos_g  -  sin_a * cos_b * sin_g
    R[2, 1] =  sin_a * sin_b

    # The unit muz vector component of the rotation matrix.
    R[0, 2] =  sin_b * cos_g
    R[1, 2] =  sin_b * sin_g
    R[2, 2] =  cos_b


def R_to_axis_angle(R):
    """Convert the rotation matrix into the axis-angle notation.

    Conversion equations
    ====================

    From Wikipedia (http://en.wikipedia.org/wiki/Rotation_matrix), the conversion is given by::

        x = Qzy-Qyz
        y = Qxz-Qzx
        z = Qyx-Qxy
        r = hypot(x,hypot(y,z))
        t = Qxx+Qyy+Qzz
        theta = atan2(r,t-1)

    @param R:   The 3x3 rotation matrix to update.
    @type R:    3x3 numpy array
    @return:    The 3D rotation axis and angle.
    @rtype:     numpy 3D rank-1 array, float
    """

    # Axes.
    axis = zeros(3, float64)
    axis[0] = R[2, 1] - R[1, 2]
    axis[1] = R[0, 2] - R[2, 0]
    axis[2] = R[1, 0] - R[0, 1]

    # Angle.
    r = hypot(axis[0], hypot(axis[1], axis[2]))
    t = R[0, 0] + R[1, 1] + R[2, 2]
    theta = atan2(r, t-1)

    # Normalise the axis.
    if r != 0.0:
        axis = axis / r

    # Return the data.
    return axis, theta


def R_to_euler_xyx(R):
    """Convert the rotation matrix to the xyx Euler angles.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the xyx convention is::

              |  cb                  sa*sb               ca*sb            |
        R  =  |  sb*sg               ca*cg - sa*cb*sg   -sa*cg - ca*cb*sg |,
              | -sb*cg               ca*sg + sa*cb*cg   -sa*sg + ca*cb*cg |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).

    If beta is zero degrees (i.e. the Rzz element is one), then the rotation angle is determined from the xy sub-matrix elements.  All of the rotation is assumed to be in alpha, while gamma stays at zero.


    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    @return:        The alpha, beta, and gamma Euler angles in the xyx convention.
    @rtype:         tuple of float
    """

    # The beta Euler angle.
    beta = acos(R[0, 0])

    # Problem case - beta is zero so alpha and gamma are indistinguishable.
    if R[0, 0] == 1.0:
        # Put all the rotation into alpha.
        alpha = atan2(-R[1, 2], R[2, 2])

        # Gamma.
        gamma = 0.0

    # Normal case.
    else:
        # The alpha Euler angle.
        alpha = atan2(R[0, 1], R[0, 2])

        # The gamma Euler angle.
        gamma = atan2(R[1, 0], -R[2, 0])

    # Return the angles.
    return alpha, beta, gamma


def R_to_euler_xyz(R):
    """Convert the rotation matrix to the xyz Euler angles.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the xyz convention is::

              |  cb*cg              -ca*sg + sa*sb*cg    sa*sg + ca*sb*cg |
        R  =  |  cb*sg               ca*cg + sa*sb*sg   -sa*cg + ca*sb*sg |,
              | -sb                  sa*cb               ca*cb            |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).

    If beta is zero degrees (i.e. the Rzz element is one), then the rotation angle is determined from the xy sub-matrix elements.  All of the rotation is assumed to be in alpha, while gamma stays at zero.


    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    @return:        The alpha, beta, and gamma Euler angles in the xyz convention.
    @rtype:         tuple of float
    """

    # The beta Euler angle.
    beta = asin(-R[2, 0])

    # Problem case - beta is zero so alpha and gamma are indistinguishable.
    if -R[2, 0] == 0.0:
        # Put all the rotation into alpha.
        alpha = atan2(-R[1, 2], -R[0, 2])

        # Gamma.
        gamma = 0.0

    # Normal case.
    else:
        # The alpha Euler angle.
        alpha = atan2(R[2, 1], R[2, 2])

        # The gamma Euler angle.
        gamma = atan2(R[1, 0], -R[0, 0])

    # Return the angles.
    return alpha, beta, gamma


def R_to_euler_xzx(R):
    """Convert the rotation matrix to the xzx Euler angles.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the xzx convention is::

              |  cb                 -ca*sb               sa*sb            |
        R  =  |  sb*cg              -sa*sg + ca*cb*cg   -ca*sg - sa*cb*cg |,
              |  sb*sg               sa*cg + ca*cb*sg    ca*cg - sa*cb*sg |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).

    If beta is zero degrees (i.e. the Rxx element is one), then the rotation angle is determined from the yz sub-matrix elements.  All of the rotation is assumed to be in alpha, while gamma stays at zero.


    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    @return:        The alpha, beta, and gamma Euler angles in the xzx convention.
    @rtype:         tuple of float
    """

    # The beta Euler angle.
    beta = acos(R[0, 0])

    # Problem case - beta is zero so alpha and gamma are indistinguishable.
    if R[0, 0] == 1.0:
        # Put all the rotation into alpha.
        alpha = atan2(R[2, 1], R[1, 1])

        # Gamma.
        gamma = 0.0

    # Normal case.
    else:
        # The alpha Euler angle.
        alpha = atan2(R[0, 2], -R[0, 1])

        # The gamma Euler angle.
        gamma = atan2(R[2, 0], R[1, 0])

    # Return the angles.
    return alpha, beta, gamma


def R_to_euler_xzy(R):
    """Convert the rotation matrix to the xzy Euler angles.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the xzy convention is::

              |  cb*cg               sa*sg - ca*sb*cg    ca*sg + sa*sb*cg |
        R  =  |  sb                  ca*cb              -sa*cb            |,
              | -cb*sg               sa*cg + ca*sb*sg    ca*cg - sa*sb*sg |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).

    If beta is zero degrees (i.e. the Ryx element is zero), then the rotation angle is determined from the sub-matrix elements.  All of the rotation is assumed to be in alpha, while gamma stays at zero.


    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    @return:        The alpha, beta, and gamma Euler angles in the xzy convention.
    @rtype:         tuple of float
    """

    # The beta Euler angle.
    beta = asin(R[1, 0])

    # Problem case - beta is zero so alpha and gamma are indistinguishable.
    if R[1, 0] == 0.0:
        # Put all the rotation into alpha.
        alpha = atan2(-R[0, 1], R[2, 2])

        # Gamma.
        gamma = 0.0

    # Normal case.
    else:
        # The alpha Euler angle.
        alpha = atan2(-R[1, 2], R[1, 1])

        # The gamma Euler angle.
        gamma = atan2(-R[2, 0], R[0, 0])

    # Return the angles.
    return alpha, beta, gamma


def R_to_euler_yxy(R):
    """Convert the rotation matrix to the yxy Euler angles.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the yxy convention is::

              |  ca*cg - sa*cb*sg    sb*sg               sa*cg + ca*cb*sg |
        R  =  |  sa*sb               cb                 -ca*sb            |,
              | -ca*sg - sa*cb*cg    sb*cg              -sa*sg + ca*cb*cg |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).

    If beta is zero degrees (i.e. the Rzz element is one), then the rotation angle is determined from the xy sub-matrix elements.  All of the rotation is assumed to be in alpha, while gamma stays at zero.


    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    @return:        The alpha, beta, and gamma Euler angles in the yxy convention.
    @rtype:         tuple of float
    """

    # The beta Euler angle.
    beta = acos(R[1, 1])

    # Problem case - beta is zero so alpha and gamma are indistinguishable.
    if R[1, 1] == 1.0:
        # Put all the rotation into alpha.
        alpha = atan2(R[0, 2], R[2, 2])

        # Gamma.
        gamma = 0.0

    # Normal case.
    else:
        # The alpha Euler angle.
        alpha = atan2(R[1, 0], -R[1, 2])

        # The gamma Euler angle.
        gamma = atan2(R[0, 1], R[2, 1])

    # Return the angles.
    return alpha, beta, gamma


def R_to_euler_yxz(R):
    """Convert the rotation matrix to the yxz Euler angles.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the yxz convention is::

              |  ca*cg - sa*sb*sg   -cb*sg               sa*cg + ca*sb*sg |
        R  =  |  ca*sg + sa*sb*cg    cb*cg               sa*sg - ca*sb*cg |,
              | -sa*cb               sb                  ca*cb            |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).

    If beta is zero degrees (i.e. the Rzz element is one), then the rotation angle is determined from the xy sub-matrix elements.  All of the rotation is assumed to be in alpha, while gamma stays at zero.


    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    @return:        The alpha, beta, and gamma Euler angles in the yxz convention.
    @rtype:         tuple of float
    """

    # The beta Euler angle.
    beta = asin(R[2, 1])

    # Problem case - beta is zero so alpha and gamma are indistinguishable.
    if R[2, 1] == 0.0:
        # Put all the rotation into alpha.
        alpha = atan2(R[0, 2], -R[1, 2])

        # Gamma.
        gamma = 0.0

    # Normal case.
    else:
        # The alpha Euler angle.
        alpha = atan2(-R[2, 0], R[2, 2])

        # The gamma Euler angle.
        gamma = atan2(-R[0, 1], R[1, 1])

    # Return the angles.
    return alpha, beta, gamma


def R_to_euler_yzx(R):
    """Convert the rotation matrix to the yzx Euler angles.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the yzx convention is::

              |  ca*cb              -sb                  sa*cb            |
        R  =  |  sa*sg + ca*sb*cg    cb*cg              -ca*sg + sa*sb*cg |,
              | -sa*cg + ca*sb*sg    cb*sg               ca*cg + sa*sb*sg |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).

    If beta is zero degrees (i.e. the Rzz element is one), then the rotation angle is determined from the xy sub-matrix elements.  All of the rotation is assumed to be in alpha, while gamma stays at zero.


    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    @return:        The alpha, beta, and gamma Euler angles in the yzx convention.
    @rtype:         tuple of float
    """

    # The beta Euler angle.
    beta = asin(-R[0, 1])

    # Problem case - beta is zero so alpha and gamma are indistinguishable.
    if -R[0, 1] == 0.0:
        # Put all the rotation into alpha.
        alpha = atan2(-R[2, 0], -R[1, 0])

        # Gamma.
        gamma = 0.0

    # Normal case.
    else:
        # The alpha Euler angle.
        alpha = atan2(R[0, 2], R[0, 0])

        # The gamma Euler angle.
        gamma = atan2(R[2, 1], R[1, 1])

    # Return the angles.
    return alpha, beta, gamma


def R_to_euler_yzy(R):
    """Convert the rotation matrix to the yzy Euler angles.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the yzy convention is::

              | -sa*sg + ca*cb*cg   -sb*cg               ca*sg + sa*cb*cg |
        R  =  |  ca*sb               cb                  sa*sb            |,
              | -sa*cg - ca*cb*sg    sb*sg               ca*cg - sa*cb*sg |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).

    If beta is zero degrees (i.e. the Rzz element is one), then the rotation angle is determined from the xy sub-matrix elements.  All of the rotation is assumed to be in alpha, while gamma stays at zero.


    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    @return:        The alpha, beta, and gamma Euler angles in the yzy convention.
    @rtype:         tuple of float
    """

    # The beta Euler angle.
    beta = acos(R[1, 1])

    # Problem case - beta is zero so alpha and gamma are indistinguishable.
    if R[1, 1] == 1.0:
        # Put all the rotation into alpha.
        alpha = atan2(-R[2, 0], R[0, 0])

        # Gamma.
        gamma = 0.0

    # Normal case.
    else:
        # The alpha Euler angle.
        alpha = atan2(R[1, 2], R[1, 0])

        # The gamma Euler angle.
        gamma = atan2(R[2, 1], -R[0, 1])

    # Return the angles.
    return alpha, beta, gamma


def R_to_euler_zxy(R):
    """Convert the rotation matrix to the zxy Euler angles.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the zxy convention is::

              |  ca*cg + sa*sb*sg   -sa*cg + ca*sb*sg    cb*sg            |
        R  =  |  sa*cb               ca*cb              -sb               |,
              | -ca*sg + sa*sb*cg    sa*sg + ca*sb*cg    cb*cg            |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).

    If beta is zero degrees (i.e. the Rzz element is one), then the rotation angle is determined from the xy sub-matrix elements.  All of the rotation is assumed to be in alpha, while gamma stays at zero.


    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    @return:        The alpha, beta, and gamma Euler angles in the zxy convention.
    @rtype:         tuple of float
    """

    # The beta Euler angle.
    beta = asin(-R[1, 2])

    # Problem case - beta is zero so alpha and gamma are indistinguishable.
    if -R[1, 2] == 0.0:
        # Put all the rotation into alpha.
        alpha = atan2(-R[0, 1], -R[2, 1])

        # Gamma.
        gamma = 0.0

    # Normal case.
    else:
        # The alpha Euler angle.
        alpha = atan2(R[1, 0], R[1, 1])

        # The gamma Euler angle.
        gamma = atan2(R[0, 2], R[2, 2])

    # Return the angles.
    return alpha, beta, gamma


def R_to_euler_zxz(R):
    """Convert the rotation matrix to the zxz Euler angles.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the zxz convention is::

              |  ca*cg - sa*cb*sg   -sa*cg - ca*cb*sg    sb*sg            |
        R  =  |  ca*sg + sa*cb*cg   -sa*sg + ca*cb*cg   -sb*cg            |,
              |  sa*sb               ca*sb               cb               |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).

    If beta is zero degrees (i.e. the Rzz element is one), then the rotation angle is determined from the xy sub-matrix elements.  All of the rotation is assumed to be in alpha, while gamma stays at zero.


    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    @return:        The alpha, beta, and gamma Euler angles in the zxz convention.
    @rtype:         tuple of float
    """

    # The beta Euler angle.
    beta = acos(R[2, 2])

    # Problem case - beta is zero so alpha and gamma are indistinguishable.
    if R[2, 2] == 1.0:
        # Put all the rotation into alpha.
        alpha = atan2(-R[0, 1], R[1, 1])

        # Gamma.
        gamma = 0.0

    # Normal case.
    else:
        # The alpha Euler angle.
        alpha = atan2(R[2, 0], R[2, 1])

        # The gamma Euler angle.
        gamma = atan2(R[0, 2], -R[1, 2])

    # Return the angles.
    return alpha, beta, gamma


def R_to_euler_zyx(R):
    """Convert the rotation matrix to the zyx Euler angles.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the zyx convention is::

              |  ca*cb              -sa*cb               sb               |
        R  =  |  sa*cg + ca*sb*sg    ca*cg - sa*sb*sg   -cb*sg            |,
              |  sa*sg - ca*sb*cg    ca*sg + sa*sb*cg    cb*cg            |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).


    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    @return:        The alpha, beta, and gamma Euler angles in the zyx convention.
    @rtype:         tuple of float
    """

    # The beta Euler angle.
    beta = asin(R[0, 2])

    # The alpha Euler angle.
    alpha = atan2(-R[0, 1], R[0, 0])

    # The gamma Euler angle.
    gamma = atan2(-R[1, 2], R[2, 2])

    # Return the angles.
    return alpha, beta, gamma


def R_to_euler_zyz(R):
    """Convert the rotation matrix to the zyz Euler angles.

    Rotation matrix
    ===============

    The rotation matrix is defined as the vector of unit vectors::

        R = [mux, muy, muz].

    According to wikipedia (http://en.wikipedia.org/wiki/Euler_angles#Table_of_matrices), the rotation matrix for the zyz convention is::

              | -sa*sg + ca*cb*cg   -ca*sg - sa*cb*cg    sb*cg            |
        R  =  |  sa*cg + ca*cb*sg    ca*cg - sa*cb*sg    sb*sg            |,
              | -ca*sb               sa*sb               cb               |

    where::

        ca = cos(alpha),
        sa = sin(alpha),
        cb = cos(beta),
        sb = sin(beta),
        cg = cos(gamma),
        sg = sin(gamma).

    If beta is zero degrees (i.e. the Rzz element is one), then the rotation angle is determined from the xy sub-matrix elements.  All of the rotation is assumed to be in alpha, while gamma stays at zero.


    @param R:       The 3x3 rotation matrix to update.
    @type R:        3x3 numpy array
    @return:        The alpha, beta, and gamma Euler angles in the zyz convention.
    @rtype:         tuple of float
    """

    # The beta Euler angle.
    beta = acos(R[2, 2])

    # Problem case - beta is zero so alpha and gamma are indistinguishable.
    if R[2, 2] == 1.0:
        # Put all the rotation into alpha.
        alpha = atan2(R[1, 0], R[0, 0])

        # Gamma.
        gamma = 0.0

    # Normal case.
    else:
        # The alpha Euler angle.
        alpha = atan2(R[2, 1], -R[2, 0])

        # The gamma Euler angle.
        gamma = atan2(R[1, 2], R[0, 2])

    # Return the angles.
    return alpha, beta, gamma


def R_random_axis(R, angle=0.0):
    """Generate a random rotation matrix of fixed angle via the axis-angle notation.

    Uniform point sampling on a unit sphere is used to generate a random axis orientation.  This,
    together with the fixed rotation angle, is used to generate the random rotation matrix.

    @param R:       A 3D matrix to convert to the rotation matrix.
    @type R:        numpy 3D, rank-2 array
    @keyword angle: The fixed rotation angle.
    @type angle:    float
    """

    # Random rotation axis.
    rot_axis = zeros(3, float64)
    random_rot_axis(rot_axis)

    # Generate the rotation matrix.
    axis_angle_to_R(rot_axis, angle, R)


def R_random_hypersphere(R):
    """Generate a random rotation matrix using 4D hypersphere point picking.

    A quaternion is generated by creating a 4D vector with each value randomly selected from a
    Gaussian distribution, and then normalising.

    @param R:       A 3D matrix to convert to the rotation matrix.
    @type R:        numpy 3D, rank-2 array
    """

    # The quaternion.
    quat = array([gauss(0, 1), gauss(0, 1), gauss(0, 1), gauss(0, 1)], float64)
    quat = quat / norm(quat)

    # Convert the quaternion to a rotation matrix.
    quaternion_to_R(quat, R)


def R_to_quaternion(R, quat):
    """Convert a rotation matrix into quaternion form.

    This is from Wikipedia (http://en.wikipedia.org/wiki/Rotation_matrix#Quaternion), where::

        w = 0.5*sqrt(1+Qxx+Qyy+Qzz),
        x = copysign(0.5*sqrt(1+Qxx-Qyy-Qzz),Qzy-Qyz),
        y = copysign(0.5*sqrt(1-Qxx+Qyy-Qzz),Qxz-Qzx),
        z = copysign(0.5*sqrt(1-Qxx-Qyy+Qzz),Qyx-Qxy),

    where the quaternion is defined as q = (w, x, y, z), and the copysign function is x with the
    sign of y::

        copysign(x, y) = abs(x) / abs(y) * y


    @param R:       The 3D rotation matrix.
    @type R:        numpy 3D, rank-2 array
    @param quat:    The quaternion.
    @type quat:     numpy 4D, rank-1 array
    """

    # Elements.
    quat[0] = 0.5 * sqrt(1.0 + R[0, 0] + R[1, 1] + R[2, 2])
    quat[1] = R[2, 1] - R[1, 2]
    if quat[1]:
        quat[1] = copysign(0.5*sqrt(1 + R[0, 0] - R[1, 1] - R[2, 2]), quat[1])
    quat[2] = R[0, 2] - R[2, 0]
    if quat[2]:
        quat[2] = copysign(0.5*sqrt(1 - R[0, 0] + R[1, 1] - R[2, 2]), quat[2])
    quat[3] = R[1, 0] - R[0, 1]
    if quat[3]:
        quat[3] = copysign(0.5*sqrt(1 - R[0, 0] - R[1, 1] + R[2, 2]), quat[3])


def copysign(x, y):
    """Return x with the sign of y.

    This is defined as::

        copysign(x, y) = abs(x) / abs(y) * y


    @param x:   The value.
    @type x:    float
    @param y:   The value.
    @type y:    float
    @return:    x with the sign of y.
    @rtype:     float
    """

    # Return the value.
    return abs(x) / abs(y) * y


def random_rot_axis(axis):
    """Generate a random rotation axis.

    Uniform point sampling on a unit sphere is used to generate a random axis orientation.

    @param axis:    The 3D rotation axis.
    @type axis:     numpy array, len 3
    """

    # Random azimuthal angle.
    u = uniform(0, 1)
    theta = 2*pi*u

    # Random polar angle.
    v = uniform(0, 1)
    phi = acos(2.0*v - 1)

    # Random rotation axis.
    axis[0] = cos(theta) * sin(phi)
    axis[1] = sin(theta) * sin(phi)
    axis[2] = cos(phi)


def reverse_euler_xyx(alpha, beta, gamma):
    """Convert the given forward rotation Euler angles into the equivalent reverse rotation Euler angles.
    
    This if for the xyx notation.


    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The alpha, beta, and gamma Euler angles for the reverse rotation.
    @rtype:         tuple of float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_xyx_to_R(alpha, beta, gamma, R)

    # Reverse rotation.
    R = transpose(R)

    # Return the Euler angles.
    return R_to_euler_xyx(R)


def reverse_euler_xyz(alpha, beta, gamma):
    """Convert the given forward rotation Euler angles into the equivalent reverse rotation Euler angles.
    
    This if for the xyz notation.


    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The alpha, beta, and gamma Euler angles for the reverse rotation.
    @rtype:         tuple of float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_xyz_to_R(alpha, beta, gamma, R)

    # Reverse rotation.
    R = transpose(R)

    # Return the Euler angles.
    return R_to_euler_xyz(R)


def reverse_euler_xzx(alpha, beta, gamma):
    """Convert the given forward rotation Euler angles into the equivalent reverse rotation Euler angles.
    
    This if for the xzx notation.


    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The alpha, beta, and gamma Euler angles for the reverse rotation.
    @rtype:         tuple of float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_xzx_to_R(alpha, beta, gamma, R)

    # Reverse rotation.
    R = transpose(R)

    # Return the Euler angles.
    return R_to_euler_xzx(R)


def reverse_euler_xzy(alpha, beta, gamma):
    """Convert the given forward rotation Euler angles into the equivalent reverse rotation Euler angles.
    
    This if for the xzy notation.


    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The alpha, beta, and gamma Euler angles for the reverse rotation.
    @rtype:         tuple of float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_xzy_to_R(alpha, beta, gamma, R)

    # Reverse rotation.
    R = transpose(R)

    # Return the Euler angles.
    return R_to_euler_xzy(R)


def reverse_euler_yxy(alpha, beta, gamma):
    """Convert the given forward rotation Euler angles into the equivalent reverse rotation Euler angles.
    
    This if for the yxy notation.


    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The alpha, beta, and gamma Euler angles for the reverse rotation.
    @rtype:         tuple of float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_yxy_to_R(alpha, beta, gamma, R)

    # Reverse rotation.
    R = transpose(R)

    # Return the Euler angles.
    return R_to_euler_yxy(R)


def reverse_euler_yxz(alpha, beta, gamma):
    """Convert the given forward rotation Euler angles into the equivalent reverse rotation Euler angles.
    
    This if for the yxz notation.


    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The alpha, beta, and gamma Euler angles for the reverse rotation.
    @rtype:         tuple of float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_yxz_to_R(alpha, beta, gamma, R)

    # Reverse rotation.
    R = transpose(R)

    # Return the Euler angles.
    return R_to_euler_yxz(R)


def reverse_euler_yzx(alpha, beta, gamma):
    """Convert the given forward rotation Euler angles into the equivalent reverse rotation Euler angles.
    
    This if for the yzx notation.


    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The alpha, beta, and gamma Euler angles for the reverse rotation.
    @rtype:         tuple of float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_yzx_to_R(alpha, beta, gamma, R)

    # Reverse rotation.
    R = transpose(R)

    # Return the Euler angles.
    return R_to_euler_yzx(R)


def reverse_euler_yzy(alpha, beta, gamma):
    """Convert the given forward rotation Euler angles into the equivalent reverse rotation Euler angles.
    
    This if for the yzy notation.


    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The alpha, beta, and gamma Euler angles for the reverse rotation.
    @rtype:         tuple of float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_yzy_to_R(alpha, beta, gamma, R)

    # Reverse rotation.
    R = transpose(R)

    # Return the Euler angles.
    return R_to_euler_yzy(R)


def reverse_euler_zxy(alpha, beta, gamma):
    """Convert the given forward rotation Euler angles into the equivalent reverse rotation Euler angles.
    
    This if for the zxy notation.


    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The alpha, beta, and gamma Euler angles for the reverse rotation.
    @rtype:         tuple of float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_zxy_to_R(alpha, beta, gamma, R)

    # Reverse rotation.
    R = transpose(R)

    # Return the Euler angles.
    return R_to_euler_zxy(R)


def reverse_euler_zxz(alpha, beta, gamma):
    """Convert the given forward rotation Euler angles into the equivalent reverse rotation Euler angles.
    
    This if for the zxz notation.


    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The alpha, beta, and gamma Euler angles for the reverse rotation.
    @rtype:         tuple of float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_zxz_to_R(alpha, beta, gamma, R)

    # Reverse rotation.
    R = transpose(R)

    # Return the Euler angles.
    return R_to_euler_zxz(R)


def reverse_euler_zyx(alpha, beta, gamma):
    """Convert the given forward rotation Euler angles into the equivalent reverse rotation Euler angles.
    
    This if for the zyx notation.


    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The alpha, beta, and gamma Euler angles for the reverse rotation.
    @rtype:         tuple of float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_zyx_to_R(alpha, beta, gamma, R)

    # Reverse rotation.
    R = transpose(R)

    # Return the Euler angles.
    return R_to_euler_zyx(R)


def reverse_euler_zyz(alpha, beta, gamma):
    """Convert the given forward rotation Euler angles into the equivalent reverse rotation Euler angles.
    
    This if for the zyz notation.


    @param alpha:   The alpha Euler angle in rad.
    @type alpha:    float
    @param beta:    The beta Euler angle in rad.
    @type beta:     float
    @param gamma:   The gamma Euler angle in rad.
    @type gamma:    float
    @return:        The alpha, beta, and gamma Euler angles for the reverse rotation.
    @rtype:         tuple of float
    """

    # Init.
    R = zeros((3, 3), float64)

    # Get the rotation.
    euler_zyz_to_R(alpha, beta, gamma, R)

    # Reverse rotation.
    R = transpose(R)

    # Return the Euler angles.
    return R_to_euler_zyz(R)


def quaternion_to_axis_angle(quat):
    """Convert a quaternion into the axis-angle notation.

    Conversion equations
    ====================

    From Wolfram MathWorld (http://mathworld.wolfram.com/Quaternion.html), the conversion is given by::

        q = (cos(angle/2), n * sin(angle/2)),

    where q is the quaternion and n is the unit vector representing the rotation axis.  Therfore::

        angle = 2*acos(w),

        axis = 2*asin([x, y, z])

    @param quat:    The quaternion.
    @type quat:     numpy 4D, rank-1 array
    @return:        The 3D rotation axis and angle.
    @rtype:         numpy 3D rank-1 array, float
    """

    # The angle.
    angle = 2 * acos(quat[0])

    # The axis.
    if angle:
        axis = quat[1:] / sin(angle/2)
    else:
        axis = quat[1:] * 0.0

    # Return
    return axis, angle


def quaternion_to_R(quat, R):
    """Convert a quaternion into rotation matrix form.

    This is from Wikipedia (http://en.wikipedia.org/wiki/Rotation_matrix#Quaternion), where::

            | 1 - 2y**2 - 2z**2      2xy - 2zw          2xz + 2yw     |
        Q = |     2xy + 2zw      1 - 2x**2 - 2z**2      2yz - 2xw     |,
            |     2xz - 2yw          2yz + 2xw      1 - 2x**2 - 2y**2 |

    and where the quaternion is defined as q = (w, x, y, z).  This has been verified using Simo
    Saerkkae's "Notes on Quaternions" at http://www.lce.hut.fi/~ssarkka/.


    @param quat:    The quaternion.
    @type quat:     numpy 4D, rank-1 array
    @param R:       A 3D matrix to convert to the rotation matrix.
    @type R:        numpy 3D, rank-2 array
    """

    # Alias.
    (w, x, y, z) = quat

    # Repetitive calculations.
    x2 = 2.0 * x**2
    y2 = 2.0 * y**2
    z2 = 2.0 * z**2
    xw = 2.0 * x*w
    xy = 2.0 * x*y
    xz = 2.0 * x*z
    yw = 2.0 * y*w
    yz = 2.0 * y*z
    zw = 2.0 * z*w

    # The diagonal.
    R[0, 0] = 1.0 - y2 - z2
    R[1, 1] = 1.0 - x2 - z2
    R[2, 2] = 1.0 - x2 - y2

    # The off-diagonal.
    R[0, 1] = xy - zw
    R[0, 2] = xz + yw
    R[1, 2] = yz - xw

    R[1, 0] = xy + zw
    R[2, 0] = xz - yw
    R[2, 1] = yz + xw


def two_vect_to_R(vector_orig, vector_fin, R):
    """Calculate the rotation matrix required to rotate from one vector to another.

    For the rotation of one vector to another, there are an infinit series of rotation matrices
    possible.  Due to axially symmetry, the rotation axis can be any vector lying in the symmetry
    plane between the two vectors.  Hence the axis-angle convention will be used to construct the
    matrix with the rotation axis defined as the cross product of the two vectors.  The rotation
    angle is the arccosine of the dot product of the two unit vectors.

    Given a unit vector parallel to the rotation axis, w = [x, y, z] and the rotation angle a,
    the rotation matrix R is::

              |  1 + (1-cos(a))*(x*x-1)   -z*sin(a)+(1-cos(a))*x*y   y*sin(a)+(1-cos(a))*x*z |
        R  =  |  z*sin(a)+(1-cos(a))*x*y   1 + (1-cos(a))*(y*y-1)   -x*sin(a)+(1-cos(a))*y*z |
              | -y*sin(a)+(1-cos(a))*x*z   x*sin(a)+(1-cos(a))*y*z   1 + (1-cos(a))*(z*z-1)  |


    @param vector_orig: The unrotated vector defined in the reference frame.
    @type vector_orig:  numpy array, len 3
    @param vector_fin:  The rotated vector defined in the reference frame.
    @type vector_fin:   numpy array, len 3
    @param R:           The 3x3 rotation matrix to update.
    @type R:            3x3 numpy array
    """

    # Convert the vectors to unit vectors.
    vector_orig = vector_orig / norm(vector_orig)
    vector_fin = vector_fin / norm(vector_fin)

    # The rotation axis (normalised).
    axis = cross(vector_orig, vector_fin)
    axis_len = norm(axis)
    if axis_len != 0.0:
        axis = axis / axis_len

    # Alias the axis coordinates.
    x = axis[0]
    y = axis[1]
    z = axis[2]

    # The rotation angle.
    angle = acos(dot(vector_orig, vector_fin))

    # Trig functions (only need to do this maths once!).
    ca = cos(angle)
    sa = sin(angle)

    # Calculate the rotation matrix elements.
    R[0, 0] = 1.0 + (1.0 - ca)*(x**2 - 1.0)
    R[0, 1] = -z*sa + (1.0 - ca)*x*y
    R[0, 2] = y*sa + (1.0 - ca)*x*z
    R[1, 0] = z*sa+(1.0 - ca)*x*y
    R[1, 1] = 1.0 + (1.0 - ca)*(y**2 - 1.0)
    R[1, 2] = -x*sa+(1.0 - ca)*y*z
    R[2, 0] = -y*sa+(1.0 - ca)*x*z
    R[2, 1] = x*sa+(1.0 - ca)*y*z
    R[2, 2] = 1.0 + (1.0 - ca)*(z**2 - 1.0)
