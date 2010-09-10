###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
"""Module containing all the different cone type classes."""

# Python module imports.
from math import acos, asin, cos, pi, sqrt, sin


class Base:
    """A base class for all the cone objects."""

    def __init__(self, phi_x, phi_y):
        """Set up the cone object.

        @param phi_x:   The maximum cone angle along the x-eigenvector.
        @type phi_x:    float
        @param phi_y:   The maximum cone angle along the y-eigenvector.
        @type phi_y:    float
        """

        # Store the cone limits.
        self._phi_x = phi_x
        self._phi_y = phi_y


    def limit_check(self, phi, theta):
        """Determine if the point is within the cone.

        @param phi:     The polar angle.
        @type phi:      float
        @param theta:   The azimuthal angle.
        @type phi:      float
        @return:        True if the point is within the cone, False otherwise.
        @rtype:         bool
        """

        # Outside.
        if phi > self.phi_max(theta):
            return False

        # Else inside.
        return True



class Cosine(Base):
    """The class for the cosine cone.

    The ellipse is defined by::

        phi_max = cos(theta) * phi_x  +  sin(theta) * phi_y,

    where phi_max is the maximum polar angle for the given azimuthal angle theta, phi_x is the maximum cone angle along the x-eigenvector, and phi_y is that of the y-eigenvector.  The cone axis is assumed to be the z-axis.  The maximum cone opening angle allowed is pi/2.
    """

    def __init__(self, phi_x, phi_y):
        """Set up the cone object.

        @param phi_x:   The maximum cone angle along the x-eigenvector.
        @type phi_x:    float
        @param phi_y:   The maximum cone angle along the y-eigenvector.
        @type phi_y:    float
        """

        # Store the cone limits.
        self._phi_x = phi_x
        self._phi_y = phi_y

        # The scaling factor.
        self._scale = (phi_x - phi_y)/2

        # The shift.
        self._shift = (phi_x + phi_y)/2


    def phi_max(self, theta):
        """Return the maximum polar angle phi for the given azimuthal angle theta.

        @param theta:   The azimuthal angle.
        @type theta:    float
        @return:        The maximum polar angle phi for the value of theta.
        @rtype:         float
        """

        # Determine phi_max.
        phi_max = self._scale * cos(theta*2)  +  self._shift

        # Return the limit.
        return phi_max


    def theta_max(self, phi, theta_min=0.0, theta_max=2*pi):
        """Return the maximum azimuthal angle theta for the given polar angle phi.

        @param phi:         The polar angle.
        @type phi:          float
        @keyword theta_min: The lower limit of the azimuthal angle range for complex distributions.
        @type theta_min:    float
        @keyword theta_max: The upper limit of the azimuthal angle range for complex distributions.
        @type theta_max:    float
        @return:            The maximum azimuthal angle theta for the value of phi.
        @rtype:             float
        """

        # The factor.
        b = (phi - self._shift)/self._scale

        # The 4 quadrants.
        if theta_max < pi/2:
            theta = 0.5*acos(b)
        elif theta_max < pi:
            theta = 0.5*acos(-b) + pi/2
        elif theta_max < 3*pi/2:
            theta = 0.5*acos(b) + pi
        elif theta_max < 2*pi:
            theta = 0.5*acos(-b) + 3*pi/2

        # Return the azimuthal angle.
        return theta



class Elliptic(Base):
    """The class for the elliptic cone.

    The ellipse is defined by::

        1 / sin(phi_max)^2 = cos(theta)^2 / sin(phi_x)^2  +  sin(theta)^2 / sin(phi_y)^2,

    where phi_max is the maximum polar angle for the given azimuthal angle theta, phi_x is the maximum cone angle along the x-eigenvector, and phi_y is that of the y-eigenvector.  The cone axis is assumed to be the z-axis.  The maximum cone opening angle allowed is pi/2.
    """

    def phi_max(self, theta):
        """Return the maximum polar angle phi for the given azimuthal angle theta.

        @param theta:   The azimuthal angle.
        @type theta:    float
        @return:        The maximum polar angle phi for the value of theta.
        @rtype:         float
        """

        # Determine phi_max.
        phi_max = asin(1.0/sqrt((cos(theta) / sin(self._phi_x))**2 + (sin(theta) / sin(self._phi_y))**2))

        # Return the limit.
        return phi_max


    def theta_max(self, phi, theta_min=0.0, theta_max=2*pi):
        """Return the maximum azimuthal angle theta for the given polar angle phi.

        @param phi:         The polar angle.
        @type phi:          float
        @keyword theta_min: The lower limit of the azimuthal angle range for complex distributions.
        @type theta_min:    float
        @keyword theta_max: The upper limit of the azimuthal angle range for complex distributions.
        @type theta_max:    float
        @return:            The maximum azimuthal angle theta for the value of phi.
        @rtype:             float
        """

        # The factor.
        b = sqrt((1.0/sin(phi)**2 - 1.0/sin(self._phi_y)**2)/(1.0/sin(self._phi_x)**2 - 1.0/sin(self._phi_y)**2))

        # The 4 quadrants.
        if theta_max < pi/2:
            theta = acos(b)
        elif theta_max < pi:
            theta = acos(-b)
        elif theta_max < 3*pi/2:
            theta = -acos(-b)
        elif theta_max < 2*pi:
            theta = -acos(b)

        # Return the azimuthal angle.
        return theta



class Iso_cone(Base):
    """The class for the isotropic cone."""

    def __init__(self, angle):
        """Set up the cone object.

        @param angle:   The cone angle.
        @type angle:    float
        """

        # Store the cone angle.
        self._angle = angle


    def phi_max(self, theta):
        """Return the maximum polar angle phi for the given azimuthal angle theta.

        @param theta:   The azimuthal angle.
        @type theta:    float
        @return:        The maximum polar angle phi for the value of theta.
        @rtype:         float
        """

        # The polar angle is fixed!
        return self._angle


    def theta_max(self, phi):
        """Return the maximum azimuthal angle theta for the given polar angle phi.

        @param phi:     The polar angle.
        @type phi:      float
        @return:        The maximum azimuthal angle theta for the value of phi.
        @rtype:         float
        """

        # The polar angle is fixed, so return zero.
        return 0.0



class Pseudo_elliptic(Base):
    """The class for another pseudo-elliptic cone.

    The pseudo-ellipse is defined by::

        1/phi_max^2 = 1/phi_x^2 * cos(theta)^2  +  1/phi_y^2 * sin(theta)^2,

    where phi_max is the maximum polar angle for the given azimuthal angle theta, phi_x is the maximum cone angle along the x-eigenvector, and phi_y is that of the y-eigenvector.  The cone axis is assumed to be the z-axis.
    """

    def phi_max(self, theta):
        """Return the maximum polar angle phi for the given azimuthal angle theta.

        @param theta:   The azimuthal angle.
        @type theta:    float
        @return:        The maximum polar angle phi for the value of theta.
        @rtype:         float
        """

        # Determine phi_max.
        phi_max = 1.0/sqrt(((1.0/self._phi_x) * cos(theta))**2 + ((1.0/self._phi_y) * sin(theta))**2)

        # Return the limit.
        return phi_max


    def theta_max(self, phi, theta_min=0.0, theta_max=2*pi):
        """Return the maximum azimuthal angle theta for the given polar angle phi.

        @param phi:         The polar angle.
        @type phi:          float
        @keyword theta_min: The lower limit of the azimuthal angle range for complex distributions.
        @type theta_min:    float
        @keyword theta_max: The upper limit of the azimuthal angle range for complex distributions.
        @type theta_max:    float
        @return:            The maximum azimuthal angle theta for the value of phi.
        @rtype:             float
        """

        # The factor.
        b = sqrt(((1.0/phi)**2 - (1.0/self._phi_y)**2) / ((1.0/self._phi_x)**2 - (1.0/self._phi_y)**2))

        # The 4 quadrants.
        if theta_max < pi/2:
            phi = acos(b)
        elif theta_max < pi:
            phi = acos(-b)
        elif theta_max < 3*pi/2:
            phi = -acos(-b)
        elif theta_max < 2*pi:
            phi = -acos(b)

        # Return the polar angle.
        return phi



class Pseudo_elliptic2(Base):
    """The class for the pseudo-elliptic cone.

    This is not an elliptic cone!  The pseudo-ellipse is defined by::

        phi_max^2 = phi_x^2 * cos(theta)^2  +  phi_y^2 * sin(theta)^2,

    where phi_max is the maximum polar angle for the given azimuthal angle theta, phi_x is the maximum cone angle along the x-eigenvector, and phi_y is that of the y-eigenvector.  The cone axis is assumed to be the z-axis.
    """

    def phi_max(self, theta):
        """Return the maximum polar angle phi for the given azimuthal angle theta.

        @param theta:   The azimuthal angle.
        @type theta:    float
        @return:        The maximum polar angle phi for the value of theta.
        @rtype:         float
        """

        # Determine phi_max.
        phi_max = sqrt((self._phi_x * cos(theta))**2 + (self._phi_y * sin(theta))**2)

        # Return the limit.
        return phi_max


    def theta_max(self, phi, theta_min=0.0, theta_max=2*pi):
        """Return the maximum azimuthal angle theta for the given polar angle phi.

        @param phi:         The polar angle.
        @type phi:          float
        @keyword theta_min: The lower limit of the azimuthal angle range for complex distributions.
        @type theta_min:    float
        @keyword theta_max: The upper limit of the azimuthal angle range for complex distributions.
        @type theta_max:    float
        @return:            The maximum azimuthal angle theta for the value of phi.
        @rtype:             float
        """

        # The factor.
        b = sqrt((phi**2 - self._phi_y**2)/(self._phi_x**2 - self._phi_y**2))

        # The 4 quadrants.
        if theta_max < pi/2:
            phi = acos(b)
        elif theta_max < pi:
            phi = acos(-b)
        elif theta_max < 3*pi/2:
            phi = -acos(-b)
        elif theta_max < 2*pi:
            phi = -acos(b)

        # Return the polar angle.
        return phi



class Square(Base):
    """The class for the square cone.

    The cone is defined by::

                   / phi_y,     if 0 <= theta < pi/2,
                   |
        phi_max = <  phi_x,     if pi/2 <= theta < 3*pi/3,
                   |
                   \ phi_y,     if 3*pi/2 <= theta < 2*pi,

    where phi_max is the maximum polar angle for the given azimuthal angle theta, phi_x is the maximum cone angle along the x-eigenvector, and phi_y is that of the y-eigenvector.  The cone axis is assumed to be the z-axis.  The maximum cone opening angle allowed is pi/2.
    """

    def phi_max(self, theta):
        """Return the maximum polar angle phi for the given azimuthal angle theta.

        @param theta:   The azimuthal angle.
        @type theta:    float
        @return:        The maximum polar angle phi for the value of theta.
        @rtype:         float
        """

        # The 4 quadrants.
        if theta < pi/2:
            phi_max = self._phi_y
        elif theta < 3*pi/2:
            phi_max = self._phi_x
        elif theta < 2*pi:
            phi_max = self._phi_y

        # Return the limit.
        return phi_max


    def theta_max(self, phi, theta_min=0.0, theta_max=2*pi):
        """Return the maximum azimuthal angle theta for the given polar angle phi.

        @param phi:         The polar angle.
        @type phi:          float
        @keyword theta_min: The lower limit of the azimuthal angle range for complex distributions.
        @type theta_min:    float
        @keyword theta_max: The upper limit of the azimuthal angle range for complex distributions.
        @type theta_max:    float
        @return:            The maximum azimuthal angle theta for the value of phi.
        @rtype:             float
        """

        # The factor.
        return 0
        b = (phi - self._shift)/self._scale

        # The 4 quadrants.
        if theta_max < pi/2:
            theta = pi/4 *(1 - b)
        elif theta_max < pi:
            theta = pi/4 *(3 + b)
        elif theta_max < 3*pi/2:
            theta = pi/4 *(5 - b)
        elif theta_max < 2*pi:
            theta = pi/4 *(7 + b)

        # Return the azimuthal angle.
        return theta



class Zig_zag(Base):
    """The class for the zig-zag cone.

    The cone is defined by::

        phi_max = c * asin(cos(theta*2)) + a,

    where::

        c = (phi_x - phi_y)/2,

        a = (phi_x + phi_y)/2,

    and where phi_max is the maximum polar angle for the given azimuthal angle theta, phi_x is the maximum cone angle along the x-eigenvector, and phi_y is that of the y-eigenvector.  The cone axis is assumed to be the z-axis.  The maximum cone opening angle allowed is pi/2.
    """

    def __init__(self, phi_x, phi_y):
        """Set up the cone object.

        @param phi_x:   The maximum cone angle along the x-eigenvector.
        @type phi_x:    float
        @param phi_y:   The maximum cone angle along the y-eigenvector.
        @type phi_y:    float
        """

        # Store the cone limits.
        self._phi_x = phi_x
        self._phi_y = phi_y

        # The scaling factor.
        self._scale = (phi_x - phi_y)/2

        # The shift.
        self._shift = (phi_x + phi_y)/2


    def phi_max(self, theta):
        """Return the maximum polar angle phi for the given azimuthal angle theta.

        @param theta:   The azimuthal angle.
        @type theta:    float
        @return:        The maximum polar angle phi for the value of theta.
        @rtype:         float
        """

        # The factor.
        b = 4.0 * theta / pi

        # The 4 quadrants.
        if theta < pi/2:
            phi_max = 1 - b
        elif theta < pi:
            phi_max = b - 3
        elif theta < 3*pi/2:
            phi_max = 5 - b
        elif theta < 2*pi:
            phi_max = b - 7

        # Determine phi_max.
        phi_max = self._scale * phi_max  +  self._shift

        # Return the limit.
        return phi_max


    def theta_max(self, phi, theta_min=0.0, theta_max=2*pi):
        """Return the maximum azimuthal angle theta for the given polar angle phi.

        @param phi:         The polar angle.
        @type phi:          float
        @keyword theta_min: The lower limit of the azimuthal angle range for complex distributions.
        @type theta_min:    float
        @keyword theta_max: The upper limit of the azimuthal angle range for complex distributions.
        @type theta_max:    float
        @return:            The maximum azimuthal angle theta for the value of phi.
        @rtype:             float
        """

        # The factor.
        b = (phi - self._shift)/self._scale

        # The 4 quadrants.
        if theta_max < pi/2:
            theta = pi/4 *(1 - b)
        elif theta_max < pi:
            theta = pi/4 *(3 + b)
        elif theta_max < 3*pi/2:
            theta = pi/4 *(5 - b)
        elif theta_max < 2*pi:
            theta = pi/4 *(7 + b)

        # Return the azimuthal angle.
        return theta
