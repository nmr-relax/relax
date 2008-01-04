###############################################################################
#                                                                             #
# Copyright (C) 2003-2006 Edward d'Auvergne                                   #
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
from Numeric import Float64, array, zeros
from re import search


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


    def default_value(self, param):
        """
        Diffusion tensor parameter default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ________________________________________________________________________
        |                        |                    |                        |
        | Data type              | Object name        | Value                  |
        |________________________|____________________|________________________|
        |                        |                    |                        |
        | tm                     | 'tm'               | 10 * 1e-9              |
        |                        |                    |                        |
        | Diso                   | 'Diso'             | 1.666 * 1e7            |
        |                        |                    |                        |
        | Da                     | 'Da'               | 0.0                    |
        |                        |                    |                        |
        | Dr                     | 'Dr'               | 0.0                    |
        |                        |                    |                        |
        | Dx                     | 'Dx'               | 1.666 * 1e7            |
        |                        |                    |                        |
        | Dy                     | 'Dy'               | 1.666 * 1e7            |
        |                        |                    |                        |
        | Dz                     | 'Dz'               | 1.666 * 1e7            |
        |                        |                    |                        |
        | Dpar                   | 'Dpar'             | 1.666 * 1e7            |
        |                        |                    |                        |
        | Dper                   | 'Dper'             | 1.666 * 1e7            |
        |                        |                    |                        |
        | Dratio                 | 'Dratio'           | 1.0                    |
        |                        |                    |                        |
        | alpha                  | 'alpha'            | 0.0                    |
        |                        |                    |                        |
        | beta                   | 'beta'             | 0.0                    |
        |                        |                    |                        |
        | gamma                  | 'gamma'            | 0.0                    |
        |                        |                    |                        |
        | theta                  | 'theta'            | 0.0                    |
        |                        |                    |                        |
        | phi                    | 'phi'              | 0.0                    |
        |________________________|____________________|________________________|

        """

        # tm.
        if param == 'tm':
            return 10.0 * 1e-9

        # Diso, Dx, Dy, Dz, Dpar, Dper.
        elif param == 'Diso' or param == 'Dx' or param == 'Dy' or param == 'Dz' or param == 'Dpar' or param == 'Dper':
            return 1.666 * 1e7

        # Da, Dr.
        elif param == 'Da' or param == 'Dr':
            return 0.0

        # Dratio.
        elif param == 'Dratio':
            return 1.0

        # All angles.
        elif param == 'alpha' or param == 'beta' or param == 'gamma' or param == 'theta' or param == 'phi':
            return 0.0


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
        self.relax.generic.runs.eliminate_unused_runs()


    def display(self, run=None):
        """Function for displaying the diffusion tensor."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if diffusion tensor data for the run exists.
        if not self.relax.data.diff.has_key(run):
            raise RelaxNoTensorError, run

        # Spherical diffusion.
        if self.relax.data.diff[run].type == 'sphere':
            # Tensor type.
            print "Type:  Spherical diffusion"

            # Parameters.
            print "\nParameters {tm}."
            print "tm (s):  " + `self.relax.data.diff[run].tm`

            # Alternate parameters.
            print "\nAlternate parameters {Diso}."
            print "Diso (1/s):  " + `self.relax.data.diff[run].Diso`

            # Fixed flag.
            print "\nFixed:  " + `self.relax.data.diff[run].fixed`

        # Spheroidal diffusion.
        elif self.relax.data.diff[run].type == 'spheroid':
            # Tensor type.
            print "Type:  Spheroidal diffusion"

            # Parameters.
            print "\nParameters {tm, Da, theta, phi}."
            print "tm (s):  " + `self.relax.data.diff[run].tm`
            print "Da (1/s):  " + `self.relax.data.diff[run].Da`
            print "theta (rad):  " + `self.relax.data.diff[run].theta`
            print "phi (rad):  " + `self.relax.data.diff[run].phi`

            # Alternate parameters.
            print "\nAlternate parameters {Diso, Da, theta, phi}."
            print "Diso (1/s):  " + `self.relax.data.diff[run].Diso`
            print "Da (1/s):  " + `self.relax.data.diff[run].Da`
            print "theta (rad):  " + `self.relax.data.diff[run].theta`
            print "phi (rad):  " + `self.relax.data.diff[run].phi`

            # Alternate parameters.
            print "\nAlternate parameters {Dpar, Dper, theta, phi}."
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

        # Ellipsoidal diffusion.
        elif self.relax.data.diff[run].type == 'ellipsoid':
            # Tensor type.
            print "Type:  Ellipsoidal diffusion"

            # Parameters.
            print "\nParameters {tm, Da, Dr, alpha, beta, gamma}."
            print "tm (s):  " + `self.relax.data.diff[run].tm`
            print "Da (1/s):  " + `self.relax.data.diff[run].Da`
            print "Dr:  " + `self.relax.data.diff[run].Dr`
            print "alpha (rad):  " + `self.relax.data.diff[run].alpha`
            print "beta (rad):  " + `self.relax.data.diff[run].beta`
            print "gamma (rad):  " + `self.relax.data.diff[run].gamma`

            # Alternate parameters.
            print "\nAlternate parameters {Diso, Da, Dr, alpha, beta, gamma}."
            print "Diso (1/s):  " + `self.relax.data.diff[run].Diso`
            print "Da (1/s):  " + `self.relax.data.diff[run].Da`
            print "Dr:  " + `self.relax.data.diff[run].Dr`
            print "alpha (rad):  " + `self.relax.data.diff[run].alpha`
            print "beta (rad):  " + `self.relax.data.diff[run].beta`
            print "gamma (rad):  " + `self.relax.data.diff[run].gamma`

            # Alternate parameters.
            print "\nAlternate parameters {Dx, Dy, Dz, alpha, beta, gamma}."
            print "Dx (1/s):  " + `self.relax.data.diff[run].Dx`
            print "Dy (1/s):  " + `self.relax.data.diff[run].Dy`
            print "Dz (1/s):  " + `self.relax.data.diff[run].Dz`
            print "alpha (rad):  " + `self.relax.data.diff[run].alpha`
            print "beta (rad):  " + `self.relax.data.diff[run].beta`
            print "gamma (rad):  " + `self.relax.data.diff[run].gamma`

            # Fixed flag.
            print "\nFixed:  " + `self.relax.data.diff[run].fixed`


    def ellipsoid(self):
        """Function for setting up ellipsoidal diffusion."""

        # The diffusion type.
        self.relax.data.diff[self.run].type = 'ellipsoid'

        # (tm, Da, Dr, alpha, beta, gamma).
        if self.param_types == 0:
            # Unpack the tuple.
            tm, Da, Dr, alpha, beta, gamma = self.params

            # Scaling.
            tm = tm * self.time_scale
            Da = Da * self.d_scale

            # Set the parameters.
            self.set(run=self.run, value=[tm, Da, Dr], param=['tm', 'Da', 'Dr'])

        # (Diso, Da, Dr, alpha, beta, gamma).
        elif self.param_types == 1:
            # Unpack the tuple.
            Diso, Da, Dr, alpha, beta, gamma = self.params

            # Scaling.
            Diso = Diso * self.d_scale
            Da = Da * self.d_scale

            # Set the parameters.
            self.set(run=self.run, value=[Diso, Da, Dr], param=['Diso', 'Da', 'Dr'])

        # (Dx, Dy, Dz, alpha, beta, gamma).
        elif self.param_types == 2:
            # Unpack the tuple.
            Dx, Dy, Dz, alpha, beta, gamma = self.params

            # Scaling.
            Dx = Dx * self.d_scale
            Dy = Dy * self.d_scale
            Dz = Dz * self.d_scale

            # Set the parameters.
            self.set(run=self.run, value=[Dx, Dy, Dz], param=['Dx', 'Dy', 'Dz'])

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', self.param_types)

        # Convert the angles to radians.
        if self.angle_units == 'deg':
            alpha = (alpha / 360.0) * 2.0 * pi
            beta = (beta / 360.0) * 2.0 * pi
            gamma = (gamma / 360.0) * 2.0 * pi

        # Set the orientational parameters.
        self.set(run=self.run, value=[alpha, beta, gamma], param=['alpha', 'beta', 'gamma'])


    def fold_angles(self, run=None, sim_index=None):
        """Wrap the Euler or spherical angles and remove the glide reflection and translational symmetries.

        Wrap the angles such that

            0 <= theta <= pi,
            0 <= phi <= 2pi,

        and

            0 <= alpha <= 2pi,
            0 <= beta <= pi,
            0 <= gamma <= 2pi.


        For the simulated values, the angles are wrapped as

            theta - pi/2 <= theta_sim <= theta + pi/2
            phi - pi <= phi_sim <= phi + pi

        and

            alpha - pi <= alpha_sim <= alpha + pi
            beta - pi/2 <= beta_sim <= beta + pi/2
            gamma - pi <= gamma_sim <= gamma + pi
        """

        # Arguments.
        self.run = run


        # Wrap the angles.
        ##################

        # Spheroid.
        if self.relax.data.diff[self.run].type == 'spheroid':
            # Get the current angles.
            theta = self.relax.data.diff[self.run].theta
            phi = self.relax.data.diff[self.run].phi

            # Simulated values.
            if sim_index != None:
                theta_sim = self.relax.data.diff[self.run].theta_sim[sim_index]
                phi_sim   = self.relax.data.diff[self.run].phi_sim[sim_index]

            # Normal value.
            if sim_index == None:
                self.relax.data.diff[self.run].theta = self.relax.generic.angles.wrap_angles(theta, 0.0, pi)
                self.relax.data.diff[self.run].phi = self.relax.generic.angles.wrap_angles(phi, 0.0, 2.0*pi)

            # Simulated theta and phi values.
            else:
                self.relax.data.diff[self.run].theta_sim[sim_index] = self.relax.generic.angles.wrap_angles(theta_sim, theta - pi/2.0, theta + pi/2.0)
                self.relax.data.diff[self.run].phi_sim[sim_index]   = self.relax.generic.angles.wrap_angles(phi_sim, phi - pi, phi + pi)

        # Ellipsoid.
        elif self.relax.data.diff[self.run].type == 'ellipsoid':
            # Get the current angles.
            alpha = self.relax.data.diff[self.run].alpha
            beta  = self.relax.data.diff[self.run].beta
            gamma = self.relax.data.diff[self.run].gamma

            # Simulated values.
            if sim_index != None:
                alpha_sim = self.relax.data.diff[self.run].alpha_sim[sim_index]
                beta_sim  = self.relax.data.diff[self.run].beta_sim[sim_index]
                gamma_sim = self.relax.data.diff[self.run].gamma_sim[sim_index]

            # Normal value.
            if sim_index == None:
                self.relax.data.diff[self.run].alpha = self.relax.generic.angles.wrap_angles(alpha, 0.0, 2.0*pi)
                self.relax.data.diff[self.run].beta  = self.relax.generic.angles.wrap_angles(beta, 0.0, 2.0*pi)
                self.relax.data.diff[self.run].gamma = self.relax.generic.angles.wrap_angles(gamma, 0.0, 2.0*pi)

            # Simulated alpha, beta, and gamma values.
            else:
                self.relax.data.diff[self.run].alpha_sim[sim_index] = self.relax.generic.angles.wrap_angles(alpha_sim, alpha - pi, alpha + pi)
                self.relax.data.diff[self.run].beta_sim[sim_index]  = self.relax.generic.angles.wrap_angles(beta_sim, beta - pi, beta + pi)
                self.relax.data.diff[self.run].gamma_sim[sim_index] = self.relax.generic.angles.wrap_angles(gamma_sim, gamma - pi, gamma + pi)


        # Remove the glide reflection and translational symmetries.
        ###########################################################

        # Spheroid.
        if self.relax.data.diff[self.run].type == 'spheroid':
            # Normal value.
            if sim_index == None:
                # Fold phi inside 0 and pi.
                if self.relax.data.diff[self.run].phi >= pi:
                    self.relax.data.diff[self.run].theta = pi - self.relax.data.diff[self.run].theta
                    self.relax.data.diff[self.run].phi = self.relax.data.diff[self.run].phi - pi

            # Simulated theta and phi values.
            else:
                # Fold phi_sim inside phi-pi/2 and phi+pi/2.
                if self.relax.data.diff[self.run].phi_sim[sim_index] >= self.relax.data.diff[self.run].phi + pi/2.0:
                    self.relax.data.diff[self.run].theta_sim[sim_index] = pi - self.relax.data.diff[self.run].theta_sim[sim_index]
                    self.relax.data.diff[self.run].phi_sim[sim_index]   = self.relax.data.diff[self.run].phi_sim[sim_index] - pi
                elif self.relax.data.diff[self.run].phi_sim[sim_index] <= self.relax.data.diff[self.run].phi - pi/2.0:
                    self.relax.data.diff[self.run].theta_sim[sim_index] = pi - self.relax.data.diff[self.run].theta_sim[sim_index]
                    self.relax.data.diff[self.run].phi_sim[sim_index]   = self.relax.data.diff[self.run].phi_sim[sim_index] + pi

        # Ellipsoid.
        elif self.relax.data.diff[self.run].type == 'ellipsoid':
            # Normal value.
            if sim_index == None:
                # Fold alpha inside 0 and pi.
                if self.relax.data.diff[self.run].alpha >= pi:
                    self.relax.data.diff[self.run].alpha = self.relax.data.diff[self.run].alpha - pi

                # Fold beta inside 0 and pi.
                if self.relax.data.diff[self.run].beta >= pi:
                    self.relax.data.diff[self.run].alpha = pi - self.relax.data.diff[self.run].alpha
                    self.relax.data.diff[self.run].beta = self.relax.data.diff[self.run].beta - pi

                # Fold gamma inside 0 and pi.
                if self.relax.data.diff[self.run].gamma >= pi:
                    self.relax.data.diff[self.run].alpha = pi - self.relax.data.diff[self.run].alpha
                    self.relax.data.diff[self.run].beta = pi - self.relax.data.diff[self.run].beta
                    self.relax.data.diff[self.run].gamma = self.relax.data.diff[self.run].gamma - pi

            # Simulated theta and phi values.
            else:
                # Fold alpha_sim inside alpha-pi/2 and alpha+pi/2.
                if self.relax.data.diff[self.run].alpha_sim[sim_index] >= self.relax.data.diff[self.run].alpha + pi/2.0:
                    self.relax.data.diff[self.run].alpha_sim[sim_index] = self.relax.data.diff[self.run].alpha_sim[sim_index] - pi
                elif self.relax.data.diff[self.run].alpha_sim[sim_index] <= self.relax.data.diff[self.run].alpha - pi/2.0:
                    self.relax.data.diff[self.run].alpha_sim[sim_index] = self.relax.data.diff[self.run].alpha_sim[sim_index] + pi

                # Fold beta_sim inside beta-pi/2 and beta+pi/2.
                if self.relax.data.diff[self.run].beta_sim[sim_index] >= self.relax.data.diff[self.run].beta + pi/2.0:
                    self.relax.data.diff[self.run].alpha_sim[sim_index] = pi - self.relax.data.diff[self.run].alpha_sim[sim_index]
                    self.relax.data.diff[self.run].beta_sim[sim_index] = self.relax.data.diff[self.run].beta_sim[sim_index] - pi
                elif self.relax.data.diff[self.run].beta_sim[sim_index] <= self.relax.data.diff[self.run].beta - pi/2.0:
                    self.relax.data.diff[self.run].alpha_sim[sim_index] = pi - self.relax.data.diff[self.run].alpha_sim[sim_index]
                    self.relax.data.diff[self.run].beta_sim[sim_index] = self.relax.data.diff[self.run].beta_sim[sim_index] + pi

                # Fold gamma_sim inside gamma-pi/2 and gamma+pi/2.
                if self.relax.data.diff[self.run].gamma_sim[sim_index] >= self.relax.data.diff[self.run].gamma + pi/2.0:
                    self.relax.data.diff[self.run].alpha_sim[sim_index] = pi - self.relax.data.diff[self.run].alpha_sim[sim_index]
                    self.relax.data.diff[self.run].beta_sim[sim_index] = pi - self.relax.data.diff[self.run].beta_sim[sim_index]
                    self.relax.data.diff[self.run].gamma_sim[sim_index] = self.relax.data.diff[self.run].gamma_sim[sim_index] - pi
                elif self.relax.data.diff[self.run].gamma_sim[sim_index] <= self.relax.data.diff[self.run].gamma - pi/2.0:
                    self.relax.data.diff[self.run].alpha_sim[sim_index] = pi - self.relax.data.diff[self.run].alpha_sim[sim_index]
                    self.relax.data.diff[self.run].beta_sim[sim_index] = pi - self.relax.data.diff[self.run].beta_sim[sim_index]
                    self.relax.data.diff[self.run].gamma_sim[sim_index] = self.relax.data.diff[self.run].gamma_sim[sim_index] + pi


    def init(self, run=None, params=None, time_scale=1.0, d_scale=1.0, angle_units='deg', param_types=0, spheroid_type=None, fixed=1):
        """Function for initialising the diffusion tensor."""

        # Arguments.
        self.run = run
        self.params = params
        self.time_scale = time_scale
        self.d_scale = d_scale
        self.angle_units = angle_units
        self.param_types = param_types
        self.spheroid_type = spheroid_type

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

        # Spherical diffusion.
        if type(params) == float:
            num_params = 1
            self.sphere()

        # Spheroidal diffusion.
        elif (type(params) == tuple or type(params) == list) and len(params) == 4:
            num_params = 4
            self.spheroid()

        # Ellipsoidal diffusion.
        elif (type(params) == tuple or type(params) == list) and len(params) == 6:
            num_params = 6
            self.ellipsoid()

        # Unknown.
        else:
            raise RelaxError, "The diffusion tensor parameters " + `params` + " are of an unknown type."

        # Test the validity of the parameters.
        self.test_params(num_params)


    def map_bounds(self, run, param):
        """The function for creating bounds for the mapping function."""

        # Initialise.
        self.run = run

        # tm.
        if param == 'tm':
            return [0, 10.0 * 1e-9]

        # {Diso, Dx, Dy, Dz, Dpar, Dper}.
        if param == 'Diso' or param == 'Dx' or param == 'Dy' or param == 'Dz' or param == 'Dpar' or param == 'Dper':
            return [1e6, 1e7]

        # Da.
        if param == 'Da':
            return [-3.0/2.0 * 1e7, 3.0 * 1e7]

        # Dr.
        elif param == 'Dr':
            return [0, 1]

        # Dratio.
        elif param == 'Dratio':
            return [1.0/3.0, 3.0]

        # theta.
        elif param == 'theta':
            return [0, pi]

        # phi.
        elif param == 'phi':
            return [0, 2*pi]

        # alpha.
        elif param == 'alpha':
            return [0, 2*pi]

        # beta.
        elif param == 'beta':
            return [0, pi]

        # gamma.
        elif param == 'gamma':
            return [0, 2*pi]


    def map_labels(self, run, index, params, bounds, swap, inc):
        """Function for creating labels, tick locations, and tick values for an OpenDX map."""

        # Initialise.
        labels = "{"
        tick_locations = []
        tick_values = []
        n = len(params)
        axis_incs = 5
        loc_inc = inc / axis_incs

        # Increment over the model parameters.
        for i in xrange(n):
            # Parameter conversion factors.
            factor = self.return_conversion_factor(params[swap[i]])

            # Parameter units.
            units = self.return_units(params[swap[i]])

            # Labels.
            if units:
                labels = labels + "\"" + params[swap[i]] + " (" + units + ")\""
            else:
                labels = labels + "\"" + params[swap[i]] + "\""

            # Tick values.
            vals = bounds[swap[i], 0] / factor
            val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / (axis_incs * factor)

            if i < n - 1:
                labels = labels + " "
            else:
                labels = labels + "}"

            # Tick locations.
            string = "{"
            val = 0.0
            for j in xrange(axis_incs + 1):
                string = string + " " + `val`
                val = val + loc_inc
            string = string + " }"
            tick_locations.append(string)

            # Tick values.
            string = "{"
            for j in xrange(axis_incs + 1):
                string = string + "\"" + "%.2f" % vals + "\" "
                vals = vals + val_inc
            string = string + "}"
            tick_values.append(string)

        return labels, tick_locations, tick_values


    def return_conversion_factor(self, param):
        """Function for returning the factor of conversion between different parameter units.

        For example, the internal representation of tm is in seconds, whereas the external
        representation is in nanoseconds, therefore this function will return 1e-9 for tm.
        """

        # Get the object name.
        object_name = self.return_data_name(param)

        # tm (nanoseconds).
        if object_name == 'tm':
            return 1e-9

        # Diso, Da, Dx, Dy, Dz, Dpar, Dper.
        elif object_name in ['Diso', 'Da', 'Dx', 'Dy', 'Dz', 'Dpar', 'Dper']:
            return 1e6

        # Angles.
        elif object_name in ['theta', 'phi', 'alpha', 'beta', 'gamma']:
            return (2.0*pi) / 360.0

        # No conversion factor.
        else:
            return 1.0


    def return_data_name(self, name):
        """
        Diffusion tensor parameter string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                                                        |              |                  |
        | Data type                                              | Object name  | Patterns         |
        |________________________________________________________|______________|__________________|
        |                                                        |              |                  |
        | Global correlation time - tm                           | 'tm'         | '^tm$'           |
        |                                                        |              |                  |
        | Isotropic component of the diffusion tensor - Diso     | 'Diso'       | '[Dd]iso'        |
        |                                                        |              |                  |
        | Anisotropic component of the diffusion tensor - Da     | 'Da'         | '[Dd]a'          |
        |                                                        |              |                  |
        | Rhombic component of the diffusion tensor - Dr         | 'Dr'         | '[Dd]r$'         |
        |                                                        |              |                  |
        | Eigenvalue associated with the x-axis of the diffusion | 'Dx'         | '[Dd]x'          |
        | diffusion tensor - Dx                                  |              |                  |
        |                                                        |              |                  |
        | Eigenvalue associated with the y-axis of the diffusion | 'Dy'         | '[Dd]y'          |
        | diffusion tensor - Dy                                  |              |                  |
        |                                                        |              |                  |
        | Eigenvalue associated with the z-axis of the diffusion | 'Dz'         | '[Dd]z'          |
        | diffusion tensor - Dz                                  |              |                  |
        |                                                        |              |                  |
        | Diffusion coefficient parallel to the major axis of    | 'Dpar'       | '[Dd]par'        |
        | the spheroid diffusion tensor - Dpar                   |              |                  |
        |                                                        |              |                  |
        | Diffusion coefficient perpendicular to the major axis  | 'Dper'       | '[Dd]per'        |
        | of the spheroid diffusion tensor - Dper                |              |                  |
        |                                                        |              |                  |
        | Ratio of the parallel and perpendicular components of  | 'Dratio'     | '[Dd]ratio'      |
        | the spheroid diffusion tensor - Dratio                 |              |                  |
        |                                                        |              |                  |
        | The first Euler angle of the ellipsoid diffusion       | 'alpha'      | '^a$' or 'alpha' |
        | tensor - alpha                                         |              |                  |
        |                                                        |              |                  |
        | The second Euler angle of the ellipsoid diffusion      | 'beta'       | '^b$' or 'beta'  |
        | tensor - beta                                          |              |                  |
        |                                                        |              |                  |
        | The third Euler angle of the ellipsoid diffusion       | 'gamma'      | '^g$' or 'gamma' |
        | tensor - gamma                                         |              |                  |
        |                                                        |              |                  |
        | The polar angle defining the major axis of the         | 'theta'      | 'theta'          |
        | spheroid diffusion tensor - theta                      |              |                  |
        |                                                        |              |                  |
        | The azimuthal angle defining the major axis of the     | 'phi'        | 'phi'            |
        | spheroid diffusion tensor - phi                        |              |                  |
        |________________________________________________________|______________|__________________|
        """

        # Local tm.
        if search('^tm$', name):
            return 'tm'

        # Diso.
        if search('[Dd]iso', name):
            return 'Diso'

        # Da.
        if search('[Dd]a', name):
            return 'Da'

        # Dr.
        if search('[Dd]r$', name):
            return 'Dr'

        # Dx.
        if search('[Dd]x', name):
            return 'Dx'

        # Dy.
        if search('[Dd]y', name):
            return 'Dy'

        # Dz.
        if search('[Dd]z', name):
            return 'Dz'

        # Dpar.
        if search('[Dd]par', name):
            return 'Dpar'

        # Dper.
        if search('[Dd]per', name):
            return 'Dper'

        # Dratio.
        if search('[Dd]ratio', name):
            return 'Dratio'

        # alpha.
        if search('^a$', name) or search('alpha', name):
            return 'alpha'

        # beta.
        if search('^b$', name) or search('beta', name):
            return 'beta'

        # gamma.
        if search('^g$', name) or search('gamma', name):
            return 'gamma'

        # theta.
        if search('theta', name):
            return 'theta'

        # phi.
        if search('phi', name):
            return 'phi'


    def return_eigenvalues(self, run=None):
        """Function for returning Dx, Dy, and Dz."""

        # Argument.
        if run:
            self.run = run

        # Reassign the data.
        data = self.relax.data.diff[self.run]

        # Diso.
        Diso = 1.0 / (6.0 * data.tm)

        # Dx.
        Dx = Diso - 1.0/3.0 * data.Da * (1.0  +  3.0 * data.Dr)

        # Dy.
        Dy = Diso - 1.0/3.0 * data.Da * (1.0  -  3.0 * data.Dr)

        # Dz.
        Dz = Diso + 2.0/3.0 * data.Da

        # Return the eigenvalues.
        return Dx, Dy, Dz


    def return_units(self, param):
        """Function for returning a string representing the parameters units.

        For example, the internal representation of tm is in seconds, whereas the external
        representation is in nanoseconds, therefore this function will return the string
        'nanoseconds' for tm.
        """

        # Get the object name.
        object_name = self.return_data_name(param)

        # tm (nanoseconds).
        if object_name == 'tm':
            return 'ns'

        # Diso, Da, Dx, Dy, Dz, Dpar, Dper.
        elif object_name in ['Diso', 'Da', 'Dx', 'Dy', 'Dz', 'Dpar', 'Dper']:
            return '1e6 1/s'

        # Angles.
        elif object_name in ['theta', 'phi', 'alpha', 'beta', 'gamma']:
            return 'deg'


    def set(self, run=None, value=None, param=None):
        """
        Diffusion tensor set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        If the diffusion tensor has not been setup, use the more powerful function
        'diffusion_tensor.init' to initialise the tensor parameters.

        The diffusion tensor parameters can only be set when the run corresponds to model-free
        analysis.  The units of the parameters are:

            Inverse seconds for tm.
            Seconds for Diso, Da, Dx, Dy, Dz, Dpar, Dper.
            Unitless for Dratio and Dr.
            Radians for all angles (alpha, beta, gamma, theta, phi).


        When setting a diffusion tensor parameter, the residue number has no effect.  As the
        internal parameters of spherical diffusion are {tm}, spheroidal diffusion are {tm, Da,
        theta, phi}, and ellipsoidal diffusion are {tm, Da, Dr, alpha, beta, gamma}, supplying
        geometric parameters must be done in the following way.  If a single geometric parameter is
        supplied, it must be one of tm, Diso, Da, Dr, or Dratio.  For the parameters Dpar, Dper, Dx,
        Dy, and Dx, it is not possible to determine how to use the currently set values together
        with the supplied value to calculate the new internal parameters.  For spheroidal diffusion,
        when supplying multiple geometric parameters, the set must belong to one of

            {tm, Da},
            {Diso, Da},
            {tm, Dratio},
            {Dpar, Dper},
            {Diso, Dratio},

        where either theta, phi, or both orientational parameters can be additionally supplied.  For
        ellipsoidal diffusion, again when supplying multiple geometric parameters, the set must
        belong to one of

            {tm, Da, Dr},
            {Diso, Da, Dr},
            {Dx, Dy, Dz},

        where any number of the orientational parameters, alpha, beta, or gamma can be additionally
        supplied.
        """

        # Initialise.
        geo_params = []
        geo_values = []
        orient_params = []
        orient_values = []

        # Loop over the parameters.
        for i in xrange(len(param)):
            # Get the object name.
            param[i] = self.return_data_name(param[i])

            # Unknown parameter.
            if not param[i]:
                raise RelaxUnknownParamError, ("diffusion tensor", param[i])

            # Default value.
            if value[i] == None:
                value[i] = self.default_value(param[i])

            # Geometric parameter.
            if param[i] in ['tm', 'Diso', 'Da', 'Dratio', 'Dper', 'Dpar', 'Dr', 'Dx', 'Dy', 'Dz']:
                geo_params.append(param[i])
                geo_values.append(value[i])

            # Orientational parameter.
            if param[i] in ['theta', 'phi', 'alpha', 'beta', 'gamma']:
                orient_params.append(param[i])
                orient_values.append(value[i])


        # Spherical diffusion.
        ######################

        if self.relax.data.diff[self.run].type == 'sphere':
            # Geometric parameters.
            #######################

            # A single geometric parameter.
            if len(geo_params) == 1:
                # The single parameter tm.
                if geo_params[0] == 'tm':
                    self.relax.data.diff[self.run].tm = geo_values[0]

                # The single parameter Diso.
                elif geo_params[0] == 'Diso':
                    self.relax.data.diff[self.run].tm = 1.0 / (6.0 * geo_values[0])

                # Cannot set the single parameter.
                else:
                    raise RelaxError, "The geometric diffusion parameter " + `geo_params[0]` + " cannot be set."

            # More than one geometric parameters.
            elif len(geo_params) > 1:
                raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)


            # Orientational parameters.
            ###########################

            # ???
            if len(orient_params):
                raise RelaxError, "For spherical diffusion, the orientation parameters " + `orient_params` + " should not exist."


        # Spheroidal diffusion.
        #######################

        elif self.relax.data.diff[self.run].type == 'spheroid':
            # Geometric parameters.
            #######################

            # A single geometric parameter.
            if len(geo_params) == 1:
                # The single parameter tm.
                if geo_params[0] == 'tm':
                    self.relax.data.diff[self.run].tm = geo_values[0]

                # The single parameter Diso.
                elif geo_params[0] == 'Diso':
                    self.relax.data.diff[self.run].tm = 1.0 / (6.0 * geo_values[0])

                # The single parameter Da.
                elif geo_params[0] == 'Da':
                    self.relax.data.diff[self.run].Da = geo_values[0]

                # The single parameter Dratio.
                elif geo_params[0] == 'Dratio':
                    Dratio = geo_values[0]
                    self.relax.data.diff[self.run].Da = (Dratio - 1.0) / (2.0 * self.relax.data.diff[self.run].tm * (Dratio + 2.0))

                # Cannot set the single parameter.
                else:
                    raise RelaxError, "The geometric diffusion parameter " + `geo_params[0]` + " cannot be set."

            # Two geometric parameters.
            elif len(geo_params) == 2:
                # The geometric parameter set {tm, Da}.
                if geo_params.count('tm') == 1 and geo_params.count('Da') == 1:
                    # The parameters.
                    tm = geo_values[geo_params.index('tm')]
                    Da = geo_values[geo_params.index('Da')]

                    # Set the internal parameter values.
                    self.relax.data.diff[self.run].tm = tm
                    self.relax.data.diff[self.run].Da = Da

                # The geometric parameter set {Diso, Da}.
                elif geo_params.count('Diso') == 1 and geo_params.count('Da') == 1:
                    # The parameters.
                    Diso = geo_values[geo_params.index('Diso')]
                    Da = geo_values[geo_params.index('Da')]

                    # Set the internal parameter values.
                    self.relax.data.diff[self.run].tm = 1.0 / (6.0 * Diso)
                    self.relax.data.diff[self.run].Da = Da

                # The geometric parameter set {tm, Dratio}.
                elif geo_params.count('tm') == 1 and geo_params.count('Dratio') == 1:
                    # The parameters.
                    tm = geo_values[geo_params.index('tm')]
                    Dratio = geo_values[geo_params.index('Dratio')]

                    # Set the internal parameter values.
                    self.relax.data.diff[self.run].tm = tm
                    self.relax.data.diff[self.run].Da = (Dratio - 1.0) / (2.0 * tm * (Dratio + 2.0))

                # The geometric parameter set {Dpar, Dper}.
                elif geo_params.count('Dpar') == 1 and geo_params.count('Dper') == 1:
                    # The parameters.
                    Dpar = geo_values[geo_params.index('Dpar')]
                    Dper = geo_values[geo_params.index('Dper')]

                    # Set the internal parameter values.
                    self.relax.data.diff[self.run].tm = 1.0 / (2.0 * (Dpar + 2.0*Dper))
                    self.relax.data.diff[self.run].Da = Dpar - Dper

                # The geometric parameter set {Diso, Dratio}.
                elif geo_params.count('Diso') == 1 and geo_params.count('Dratio') == 1:
                    # The parameters.
                    Diso = geo_values[geo_params.index('Diso')]
                    Dratio = geo_values[geo_params.index('Dratio')]

                    # Set the internal parameter values.
                    self.relax.data.diff[self.run].tm = 1.0 / (6.0 * Diso)
                    self.relax.data.diff[self.run].Da = 3.0 * Diso * (Dratio - 1.0) / (Dratio + 2.0)

                # Unknown parameter combination.
                else:
                    raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)

            # More than two geometric parameters.
            elif len(geo_params) > 2:
                raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)


            # Orientational parameters.
            ###########################

            # A single orientational parameter.
            if len(orient_params) == 1:
                # The single parameter theta.
                if orient_params[0] == 'theta':
                    self.relax.data.diff[self.run].theta = orient_values[orient_params.index('theta')]

                # The single parameter phi.
                elif orient_params[0] == 'phi':
                    self.relax.data.diff[self.run].phi = orient_values[orient_params.index('phi')]

            # Two orientational parameters.
            elif len(orient_params) == 2:
                # The orientational parameter set {theta, phi}.
                if orient_params.count('theta') == 1 and orient_params.count('phi') == 1:
                    self.relax.data.diff[self.run].theta = orient_values[orient_params.index('theta')]
                    self.relax.data.diff[self.run].phi = orient_values[orient_params.index('phi')]

                # Unknown parameter combination.
                else:
                    raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)

            # More than two orientational parameters.
            elif len(orient_params) > 2:
                raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)


        # Ellipsoidal diffusion.
        ########################

        elif self.relax.data.diff[self.run].type == 'ellipsoid':
            # Geometric parameters.
            #######################

            # A single geometric parameter.
            if len(geo_params) == 1:
                # The single parameter tm.
                if geo_params[0] == 'tm':
                    self.relax.data.diff[self.run].tm = geo_values[0]

                # The single parameter Diso.
                elif geo_params[0] == 'Diso':
                    self.relax.data.diff[self.run].tm = 1.0 / (6.0 * geo_values[0])

                # The single parameter Da.
                elif geo_params[0] == 'Da':
                    self.relax.data.diff[self.run].Da = geo_values[0]

                # The single parameter Dr.
                elif geo_params[0] == 'Dr':
                    self.relax.data.diff[self.run].Dr = geo_values[0]

                # Cannot set the single parameter.
                else:
                    raise RelaxError, "The geometric diffusion parameter " + `geo_params[0]` + " cannot be set."

            # Two geometric parameters.
            elif len(geo_params) == 2:
                # The geometric parameter set {tm, Da}.
                if geo_params.count('tm') == 1 and geo_params.count('Da') == 1:
                    # The parameters.
                    tm = geo_values[geo_params.index('tm')]
                    Da = geo_values[geo_params.index('Da')]

                    # Set the internal parameter values.
                    self.relax.data.diff[self.run].tm = tm
                    self.relax.data.diff[self.run].Da = Da

                # The geometric parameter set {tm, Dr}.
                elif geo_params.count('tm') == 1 and geo_params.count('Dr') == 1:
                    # The parameters.
                    tm = geo_values[geo_params.index('tm')]
                    Dr = geo_values[geo_params.index('Dr')]

                    # Set the internal parameter values.
                    self.relax.data.diff[self.run].tm = tm
                    self.relax.data.diff[self.run].Dr = Dr

                # The geometric parameter set {Diso, Da}.
                elif geo_params.count('Diso') == 1 and geo_params.count('Da') == 1:
                    # The parameters.
                    Diso = geo_values[geo_params.index('Diso')]
                    Da = geo_values[geo_params.index('Da')]

                    # Set the internal parameter values.
                    self.relax.data.diff[self.run].tm = 1.0 / (6.0 * Diso)
                    self.relax.data.diff[self.run].Da = Da

                # The geometric parameter set {Diso, Dr}.
                elif geo_params.count('Diso') == 1 and geo_params.count('Dr') == 1:
                    # The parameters.
                    Diso = geo_values[geo_params.index('Diso')]
                    Dr = geo_values[geo_params.index('Dr')]

                    # Set the internal parameter values.
                    self.relax.data.diff[self.run].tm = 1.0 / (6.0 * Diso)
                    self.relax.data.diff[self.run].Dr = Dr

                # The geometric parameter set {Da, Dr}.
                elif geo_params.count('Da') == 1 and geo_params.count('Dr') == 1:
                    # The parameters.
                    Da = geo_values[geo_params.index('Da')]
                    Dr = geo_values[geo_params.index('Dr')]

                    # Set the internal parameter values.
                    self.relax.data.diff[self.run].Da = Da
                    self.relax.data.diff[self.run].Da = Dr

                # Unknown parameter combination.
                else:
                    raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)

            # Three geometric parameters.
            elif len(geo_params) == 3:
                # The geometric parameter set {tm, Da, Dr}.
                if geo_params.count('tm') == 1 and geo_params.count('Da') == 1 and geo_params.count('Dr') == 1:
                    # The parameters.
                    tm = geo_values[geo_params.index('tm')]
                    Da = geo_values[geo_params.index('Da')]
                    Dr = geo_values[geo_params.index('Dr')]

                    # Set the internal parameter values.
                    self.relax.data.diff[self.run].tm = tm
                    self.relax.data.diff[self.run].Da = Da
                    self.relax.data.diff[self.run].Dr = Dr

                # The geometric parameter set {Diso, Da, Dr}.
                elif geo_params.count('Diso') == 1 and geo_params.count('Da') == 1 and geo_params.count('Dr') == 1:
                    # The parameters.
                    Diso = geo_values[geo_params.index('Diso')]
                    Da = geo_values[geo_params.index('Da')]
                    Dr = geo_values[geo_params.index('Dr')]

                    # Set the internal parameter values.
                    self.relax.data.diff[self.run].tm = 1.0 / (6.0 * Diso)
                    self.relax.data.diff[self.run].Da = Da
                    self.relax.data.diff[self.run].Dr = Dr

                # The geometric parameter set {Dx, Dy, Dz}.
                elif geo_params.count('Dx') == 1 and geo_params.count('Dy') == 1 and geo_params.count('Dz') == 1:
                    # The parameters.
                    Dx = geo_values[geo_params.index('Dx')]
                    Dy = geo_values[geo_params.index('Dy')]
                    Dz = geo_values[geo_params.index('Dz')]

                    # Set the internal tm value.
                    if Dx + Dy + Dz == 0.0:
                        self.relax.data.diff[self.run].tm = 1e99
                    else:
                        self.relax.data.diff[self.run].tm = 0.5 / (Dx + Dy + Dz)

                    # Set the internal Da value.
                    self.relax.data.diff[self.run].Da = Dz - 0.5*(Dx + Dy)

                    # Set the internal Dr value.
                    if self.relax.data.diff[self.run].Da == 0.0:
                        self.relax.data.diff[self.run].Dr = (Dy - Dx) * 1e99
                    else:
                        self.relax.data.diff[self.run].Dr = (Dy - Dx) / (2.0*self.relax.data.diff[self.run].Da)

                # Unknown parameter combination.
                else:
                    raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)


            # More than three geometric parameters.
            elif len(geo_params) > 3:
                raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)


            # Orientational parameters.
            ###########################

            # A single orientational parameter.
            if len(orient_params) == 1:
                # The single parameter alpha.
                if orient_params[0] == 'alpha':
                    self.relax.data.diff[self.run].alpha = orient_values[orient_params.index('alpha')]

                # The single parameter beta.
                elif orient_params[0] == 'beta':
                    self.relax.data.diff[self.run].beta = orient_values[orient_params.index('beta')]

                # The single parameter gamma.
                elif orient_params[0] == 'gamma':
                    self.relax.data.diff[self.run].gamma = orient_values[orient_params.index('gamma')]

            # Two orientational parameters.
            elif len(orient_params) == 2:
                # The orientational parameter set {alpha, beta}.
                if orient_params.count('alpha') == 1 and orient_params.count('beta') == 1:
                    self.relax.data.diff[self.run].alpha = orient_values[orient_params.index('alpha')]
                    self.relax.data.diff[self.run].beta = orient_values[orient_params.index('beta')]

                # The orientational parameter set {alpha, gamma}.
                if orient_params.count('alpha') == 1 and orient_params.count('gamma') == 1:
                    self.relax.data.diff[self.run].alpha = orient_values[orient_params.index('alpha')]
                    self.relax.data.diff[self.run].gamma = orient_values[orient_params.index('gamma')]

                # The orientational parameter set {beta, gamma}.
                if orient_params.count('beta') == 1 and orient_params.count('gamma') == 1:
                    self.relax.data.diff[self.run].beta = orient_values[orient_params.index('beta')]
                    self.relax.data.diff[self.run].gamma = orient_values[orient_params.index('gamma')]

                # Unknown parameter combination.
                else:
                    raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)

            # Three orientational parameters.
            elif len(orient_params) == 3:
                # The orientational parameter set {alpha, beta, gamma}.
                if orient_params.count('alpha') == 1 and orient_params.count('beta') == 1:
                    self.relax.data.diff[self.run].alpha = orient_values[orient_params.index('alpha')]
                    self.relax.data.diff[self.run].beta = orient_values[orient_params.index('beta')]
                    self.relax.data.diff[self.run].gamma = orient_values[orient_params.index('gamma')]

                # Unknown parameter combination.
                else:
                    raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)

            # More than three orientational parameters.
            elif len(orient_params) > 3:
                raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)


        # Fold the angles in.
        #####################

        if orient_params:
            self.fold_angles(self.run)


    def sphere(self):
        """Function for setting up spherical diffusion."""

        # The diffusion type.
        self.relax.data.diff[self.run].type = 'sphere'

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


    def spheroid(self):
        """Function for setting up spheroidal diffusion."""

        # The diffusion type.
        self.relax.data.diff[self.run].type = 'spheroid'

        # Spheroid diffusion type.
        allowed_types = [None, 'oblate', 'prolate']
        if self.spheroid_type not in allowed_types:
            raise RelaxError, "The 'spheroid_type' argument " + `self.spheroid_type` + " should be 'oblate', 'prolate', or None."
        self.relax.data.diff[self.run].spheroid_type = self.spheroid_type

        # (tm, Da, theta, phi).
        if self.param_types == 0:
            # Unpack the tuple.
            tm, Da, theta, phi = self.params

            # Scaling.
            tm = tm * self.time_scale
            Da = Da * self.d_scale

            # Set the parameters.
            self.set(run=self.run, value=[tm, Da], param=['tm', 'Da'])

        # (Diso, Da, theta, phi).
        elif self.param_types == 1:
            # Unpack the tuple.
            Diso, Da, theta, phi = self.params

            # Scaling.
            Diso = Diso * self.d_scale
            Da = Da * self.d_scale

            # Set the parameters.
            self.set(run=self.run, value=[Diso, Da], param=['Diso', 'Da'])

        # (tm, Dratio, theta, phi).
        elif self.param_types == 2:
            # Unpack the tuple.
            tm, Dratio, theta, phi = self.params

            # Scaling.
            tm = tm * self.time_scale

            # Set the parameters.
            self.set(run=self.run, value=[tm, Dratio], param=['tm', 'Dratio'])

        # (Dpar, Dper, theta, phi).
        elif self.param_types == 3:
            # Unpack the tuple.
            Dpar, Dper, theta, phi = self.params

            # Scaling.
            Dpar = Dpar * self.d_scale
            Dper = Dper * self.d_scale

            # Set the parameters.
            self.set(run=self.run, value=[Dpar, Dper], param=['Dpar', 'Dper'])

        # (Diso, Dratio, theta, phi).
        elif self.param_types == 4:
            # Unpack the tuple.
            Diso, Dratio, theta, phi = self.params

            # Scaling.
            Diso = Diso * self.d_scale

            # Set the parameters.
            self.set(run=self.run, value=[Diso, Dratio], param=['Diso', 'Dratio'])

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', self.param_types)

        # Convert the angles to radians.
        if self.angle_units == 'deg':
            theta = (theta / 360.0) * 2.0 * pi
            phi = (phi / 360.0) * 2.0 * pi

        # Set the orientational parameters.
        self.set(run=self.run, value=[theta, phi], param=['theta', 'phi'])


    def test_params(self, num_params):
        """Function for testing the validity of the input parameters."""

        # An allowable error to account for machine precision, optimisation quality, etc.
        error = 1e-4

        # tm.
        tm = self.relax.data.diff[self.run].tm
        if tm <= 0.0 or tm > 1e-6:
            raise RelaxError, "The tm value of " + `tm` + " should be between zero and one microsecond."

        # Spheroid.
        if num_params == 4:
            # Parameters.
            Diso = 1.0 / (6.0 * self.relax.data.diff[self.run].tm)
            Da = self.relax.data.diff[self.run].Da

            # Da.
            if Da < (-1.5*Diso - error*Diso) or Da > (3.0*Diso + error*Diso):
                raise RelaxError, "The Da value of " + `Da` + " should be between -3/2 * Diso and 3Diso."

        # Ellipsoid.
        if num_params == 6:
            # Parameters.
            Diso = 1.0 / (6.0 * self.relax.data.diff[self.run].tm)
            Da = self.relax.data.diff[self.run].Da
            Dr = self.relax.data.diff[self.run].Dr

            # Da.
            if Da < (0.0 - error*Diso) or Da > (3.0*Diso + error*Diso):
                raise RelaxError, "The Da value of " + `Da` + " should be between zero and 3Diso."

            # Dr.
            if Dr < (0.0 - error) or Dr > (1.0 + error):
                raise RelaxError, "The Dr value of " + `Dr` + " should be between zero and one."


    def unit_axes(self):
        """Function for calculating the unit axes of the diffusion tensor.

        Spheroid
        ~~~~~~~~

        The unit Dpar vector is

                     | sin(theta) * cos(phi) |
            Dpar  =  | sin(theta) * sin(phi) |
                     |      cos(theta)       |


        Ellipsoid
        ~~~~~~~~~

        The unit Dx vector is

                   | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
            Dx  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |
                   |                    cos(alpha) * sin(beta)                      |

        The unit Dy vector is

                   | cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
            Dy  =  | cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |
                   |                   sin(alpha) * sin(beta)                      |

        The unit Dz vector is

                   | -sin(beta) * cos(gamma) |
            Dz  =  |  sin(beta) * sin(gamma) |
                   |        cos(beta)        |

        """

        # Spheroid.
        if self.relax.data.diff[self.run].type == 'spheroid':
            # Initialise.
            Dpar = zeros(3, Float64)

            # Trig.
            sin_theta = sin(self.relax.data.diff[self.run].theta)
            cos_theta = cos(self.relax.data.diff[self.run].theta)
            sin_phi = sin(self.relax.data.diff[self.run].phi)
            cos_phi = cos(self.relax.data.diff[self.run].phi)

            # Unit Dpar axis.
            Dpar[0] = sin_theta * cos_phi
            Dpar[1] = sin_theta * sin_phi
            Dpar[2] = cos_theta

            # Return the vector.
            return Dpar

        # Ellipsoid.
        if self.relax.data.diff[self.run].type == 'ellipsoid':
            # Initialise.
            Dx = zeros(3, Float64)
            Dy = zeros(3, Float64)
            Dz = zeros(3, Float64)

            # Trig.
            sin_alpha = sin(self.relax.data.diff[self.run].alpha)
            cos_alpha = cos(self.relax.data.diff[self.run].alpha)
            sin_beta = sin(self.relax.data.diff[self.run].beta)
            cos_beta = cos(self.relax.data.diff[self.run].beta)
            sin_gamma = sin(self.relax.data.diff[self.run].gamma)
            cos_gamma = cos(self.relax.data.diff[self.run].gamma)

            # Unit Dx axis.
            Dx[0] = -sin_alpha * sin_gamma  +  cos_alpha * cos_beta * cos_gamma
            Dx[1] = -sin_alpha * cos_gamma  -  cos_alpha * cos_beta * sin_gamma
            Dx[2] =  cos_alpha * sin_beta

            # Unit Dy axis.
            Dx[0] = cos_alpha * sin_gamma  +  sin_alpha * cos_beta * cos_gamma
            Dx[1] = cos_alpha * cos_gamma  -  sin_alpha * cos_beta * sin_gamma
            Dx[2] = sin_alpha * sin_beta

            # Unit Dz axis.
            Dx[0] = -sin_beta * cos_gamma
            Dx[1] =  sin_beta * sin_gamma
            Dx[2] =  cos_beta

            # Return the vectors.
            return Dx, Dy, Dz
