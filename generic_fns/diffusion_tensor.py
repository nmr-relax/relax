###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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

from copy import deepcopy
from math import cos, pi, sin
from Numeric import Float64, array


class Diffusion_tensor:
    def __init__(self, relax):
        """Class containing the function for setting up the diffusion tensor."""

        self.relax = relax


    def copy(self, run1=None, run2=None):
        """Function for copying diffusion tensor data from run1 to run2."""

        # Test if run1 exists.
        if not run1 in self.relax.data.run_names:
            raise RelaxNoRunError, run1

        # Test if run2 exists.
        if not run2 in self.relax.data.run_names:
            raise RelaxNoRunError, run2

        # Test if run1 contains diffusion tensor data.
        if not self.relax.data.diff.has_key(run1):
            raise RelaxNoTensorError, run1

        # Test if run2 contains diffusion tensor data.
        if self.relax.data.diff.has_key(run2):
            raise RelaxTensorError, run2

        # Copy the data.
        self.relax.data.diff[run2] = deepcopy(self.relax.data.diff[run1])


    def data_names(self):
        """Function for returning a list of names of data structures associated with the sequence."""

        names = [ 'diff_type',
                  'diff_params' ]

        return names


    def delete(self, run=None):
        """Function for deleting diffusion tensor data."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if diffusion tensor data for the run exists.
        if not self.relax.data.diff.has_key(run):
            raise RelaxNoTensorError, run

        # Delete the diffusion data.
        del(self.relax.data.diff[run])

        # Clean up the runs.
        self.relax.generic.delete.clean_runs()


    def display(self, run=None):
        """Function for displaying the diffusion tensor."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if diffusion tensor data for the run exists.
        if not self.relax.data.diff.has_key(run):
            raise RelaxNoTensorError, run

        # Isotropic diffusion.
        if self.relax.data.diff[run].type == 'iso':
            # Tensor type.
            print "Type:  Isotropic diffusion"

            # Parameters.
            print "\nParameters {tm}."
            print "tm (s):  " + `self.relax.data.diff[run].tm`

            # Alternate parameters.
            print "\nAlternate parameters {Diso}."
            print "Diso (1/s):  " + `self.relax.data.diff[run].Diso`

            # Fixed flag.
            print "\nFixed:  " + `self.relax.data.diff[run].fixed`

        # Anisotropic diffusion.
        elif self.relax.data.diff[run].type == 'axial':
            # Tensor type.
            print "Type:  Axially symmetric anisotropic diffusion"

            # Parameters.
            print "\nParameters {Dpar, Dper, theta, phi}."
            print "Dpar (1/s):  " + `self.relax.data.diff[run].Dpar`
            print "Dper (1/s):  " + `self.relax.data.diff[run].Dper`
            print "theta (rad):  " + `self.relax.data.diff[run].theta`
            print "phi (rad):  " + `self.relax.data.diff[run].phi`

            # Alternate parameters.
            print "\nAlternate parameters {tm, Dratio, theta, phi}."
            print "tm (s):  " + `self.relax.data.diff[run].tm`
            print "Dratio:  " + `self.relax.data.diff[run].Dratio`
            print "theta (rad):  " + `self.relax.data.diff[run].theta`
            print "phi (rad):  " + `self.relax.data.diff[run].phi`

            # Fixed flag.
            print "\nFixed:  " + `self.relax.data.diff[run].fixed`

        # Anisotropic diffusion.
        elif self.relax.data.diff[run].type == 'aniso':
            # Tensor type.
            print "Type:  Anisotropic diffusion"

            # Parameters.
            print "\nParameters {Dx, Dy, Dz, alpha, beta, gamma}."
            print "Dx (1/s):  " + `self.relax.data.diff[run].Dx`
            print "Dy (1/s):  " + `self.relax.data.diff[run].Dy`
            print "Dz (1/s):  " + `self.relax.data.diff[run].Dz`
            print "alpha (rad):  " + `self.relax.data.diff[run].alpha`
            print "beta (rad):  " + `self.relax.data.diff[run].beta`
            print "gamma (rad):  " + `self.relax.data.diff[run].gamma`

            # Fixed flag.
            print "\nFixed:  " + `self.relax.data.diff[run].fixed`


    def set(self, run=None, params=None, time_scale=1.0, d_scale=1.0, angle_units='deg', param_types=0, axial_type=None, fixed=1, scaling=1):
        """Function for setting up the diffusion tensor."""

        # Arguments.
        self.run = run
        self.params = params
        self.time_scale = time_scale
        self.d_scale = d_scale
        self.angle_units = angle_units
        self.param_types = param_types
        self.axial_type = axial_type

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if diffusion tensor data corresponding to the run already exists.
        if self.relax.data.diff.has_key(self.run):
            raise RelaxTensorError, self.run

        # Check the validity of the angle_units argument.
        valid_types = ['deg', 'rad']
        if not angle_units in valid_types:
            raise RelaxError, "The diffusion tensor 'angle_units' argument " + `angle_units` + " should be either 'deg' or 'rad'."

        # Add the run to the diffusion tensor data structure.
        self.relax.data.diff.add_item(self.run)

        # Set the fixed flag.
        self.relax.data.diff[self.run].fixed = fixed

        # Set the scaling flag.
        self.relax.data.diff[self.run].scaling = scaling

        # Isotropic diffusion.
        if type(params) == float:
            self.isotropic()

        # Axially symmetric anisotropic diffusion.
        elif len(params) == 4:
            self.axial()

        # Fully anisotropic diffusion.
        elif len(params) == 6:
            self.anisotropic()

        # Unknown.
        else:
            raise RelaxError, "The diffusion tensor parameters " + `params` + " are of an unknown type."

        # Test tm.
        if self.relax.data.diff[self.run].tm <= 0.0 or self.relax.data.diff[self.run].tm > 1e-6:
            raise RelaxError, "The tm value of " + `self.relax.data.diff[self.run].tm` + " should be between zero and 1 microsecond."


    def anisotropic(self):
        """Function for setting up fully anisotropic diffusion."""

        # The diffusion type.
        self.relax.data.diff[self.run].type = 'aniso'

        # (Dx, Dy, Dz, alpha, beta, gamma).
        if self.param_types == 0:
            # Unpack the tuple.
            Dx, Dy, Dz, alpha, beta, gamma = self.params

            # Diffusion tensor eigenvalues: Dx, Dy, Dz.
            self.relax.data.diff[self.run].Dx = Dx * self.d_scale
            self.relax.data.diff[self.run].Dy = Dy * self.d_scale
            self.relax.data.diff[self.run].Dz = Dz * self.d_scale

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', self.param_types)

        # Angles in radians.
        if self.angle_units == 'deg':
            self.relax.data.diff[self.run].alpha = (alpha / 360.0) * 2.0 * pi
            self.relax.data.diff[self.run].beta = (beta / 360.0) * 2.0 * pi
            self.relax.data.diff[self.run].gamma = (gamma / 360.0) * 2.0 * pi
        else:
            self.relax.data.diff[self.run].alpha = alpha
            self.relax.data.diff[self.run].beta = beta
            self.relax.data.diff[self.run].gamma = gamma


    def axial(self):
        """Function for setting up axially symmetric diffusion."""

        # The diffusion type.
        self.relax.data.diff[self.run].type = 'axial'

        # Axial diffusion type.
        allowed_types = [None, 'oblate', 'prolate']
        if self.axial_type not in allowed_types:
            raise RelaxError, "The 'axial_type' argument " + `self.axial_type` + " should be 'oblate', 'prolate', or None."
        self.relax.data.diff[self.run].axial_type = self.axial_type

        # (Dpar, Dper, theta, phi).
        print self.param_types
        if self.param_types == 0:
            # Unpack the tuple.
            tm, Dratio, theta, phi = self.params

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Diso = 1.0 / (6.0 * tm * self.time_scale)
            self.relax.data.diff[self.run].Dratio = Dratio * self.d_scale
            self.relax.data.diff[self.run].Dpar = 3.0 * self.relax.data.diff[self.run].Diso * self.relax.data.diff[self.run].Dratio / (2.0 + self.relax.data.diff[self.run].Dratio)
            self.relax.data.diff[self.run].Dper = 3.0 * self.relax.data.diff[self.run].Diso / (2.0 + self.relax.data.diff[self.run].Dratio)

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = tm * self.time_scale

        # (tm, Dratio, theta, phi).
        elif self.param_types == 1:
            # Unpack the tuple.
            Dpar, Dper, theta, phi = self.params

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Dpar = Dpar * self.d_scale
            self.relax.data.diff[self.run].Dper = Dper * self.d_scale
            self.relax.data.diff[self.run].Diso = (Dpar + 2.0 * Dper) * self.d_scale / 3.0
            self.relax.data.diff[self.run].Dratio = Dpar / Dper

            # Correlation times:  tm, t1, t2, t3.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0 * self.relax.data.diff[self.run].Diso)


        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', self.param_types)

        # Correlation times:  t1, t2, t3.
        self.relax.data.diff[self.run].t1 = 1.0 / (6.0 * self.relax.data.diff[self.run].Dper)
        self.relax.data.diff[self.run].t2 = 1.0 / (5.0 * self.relax.data.diff[self.run].Dper + self.relax.data.diff[self.run].Dpar)
        self.relax.data.diff[self.run].t3 = 1.0 / (2.0 * self.relax.data.diff[self.run].Dper + 4.0 * self.relax.data.diff[self.run].Dpar)

        # Convert the angles to radians.
        if self.angle_units == 'deg':
            theta = (theta / 360.0) * 2.0 * pi
            phi = (phi / 360.0) * 2.0 * pi

        # Make sure the angles are between 0 and 2pi.
        self.relax.data.diff[self.run].theta = self.wrap_angles(theta, 0.0, pi)
        self.relax.data.diff[self.run].phi = self.wrap_angles(phi, 0.0, 2.0 * pi)

        # Unit symmetry axis vector.
        x = cos(self.relax.data.diff[self.run].theta) * sin(self.relax.data.diff[self.run].phi)
        y = sin(self.relax.data.diff[self.run].theta) * sin(self.relax.data.diff[self.run].phi)
        z = cos(self.relax.data.diff[self.run].phi)
        self.relax.data.diff[self.run].axis_unit = array([x, y, z], Float64)

        # Full symmetry axis vector.
        self.relax.data.diff[self.run].axis_vect = self.relax.data.diff[self.run].Dpar * self.relax.data.diff[self.run].axis_unit


    def isotropic(self):
        """Function for setting up isotropic diffusion."""

        # The diffusion type.
        self.relax.data.diff[self.run].type = 'iso'

        # tm.
        if self.param_types == 0:
            # Correlation times.
            self.relax.data.diff[self.run].tm = self.params * self.time_scale

            # Diffusion tensor eigenvalues.
            self.relax.data.diff[self.run].Diso = 6.0 / self.relax.data.diff[self.run].tm

        # Diso
        elif self.param_types == 1:
            # Diffusion tensor eigenvalues.
            self.relax.data.diff[self.run].Diso = self.params * self.d_scale

            # Correlation times.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0 * self.relax.data.diff[self.run].Diso)

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', self.param_types)


    def wrap_angles(self, angle, lower, upper):
        """Convert the given angle to be between the lower and upper values."""

        while 1:
            if angle > upper:
                angle = angle - upper
            elif angle < lower:
                angle = angle + upper
            else:
                break

        return angle
