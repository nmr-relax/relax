###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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

        # Dratio.
        elif param == 'Dratio':
            return 1.0


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

            # Diffusion tensor eigenvalues: Diso, Da, Dr, Dx, Dy, Dz.
            self.relax.data.diff[self.run].Diso = 1.0 / (6.0*tm)
            self.relax.data.diff[self.run].Da = Da
            self.relax.data.diff[self.run].Dr = Dr
            self.relax.data.diff[self.run].Dx = self.relax.data.diff[self.run].Diso - Da*(Dr + 1)
            self.relax.data.diff[self.run].Dy = self.relax.data.diff[self.run].Diso + Da*(Dr - 1)
            self.relax.data.diff[self.run].Dz = self.relax.data.diff[self.run].Diso + 2.0*Da

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = tm

        # (Diso, Da, Dr, alpha, beta, gamma).
        elif self.param_types == 1:
            # Unpack the tuple.
            Diso, Da, Dr, alpha, beta, gamma = self.params

            # Scaling.
            Diso = Diso * self.d_scale
            Da = Da * self.d_scale

            # Diffusion tensor eigenvalues: Diso, Da, Dr, Dx, Dy, Dz.
            self.relax.data.diff[self.run].Diso = Diso
            self.relax.data.diff[self.run].Da = Da
            self.relax.data.diff[self.run].Dr = Dr
            self.relax.data.diff[self.run].Dx = Diso - Da*(Dr + 1)
            self.relax.data.diff[self.run].Dy = Diso + Da*(Dr - 1)
            self.relax.data.diff[self.run].Dz = Diso + 2.0*Da

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0*Diso)

        # (Dx, Dy, Dz, alpha, beta, gamma).
        elif self.param_types == 2:
            # Unpack the tuple.
            Dx, Dy, Dz, alpha, beta, gamma = self.params

            # Scaling.
            Dx = Dx * self.d_scale
            Dy = Dy * self.d_scale
            Dz = Dz * self.d_scale

            # Diffusion tensor eigenvalues: Dx, Dy, Dz.
            self.relax.data.diff[self.run].Dx = Dx
            self.relax.data.diff[self.run].Dy = Dy
            self.relax.data.diff[self.run].Dz = Dz
            self.relax.data.diff[self.run].Diso = (Dx + Dy + Dz) / 3.0
            self.relax.data.diff[self.run].Da = Dz - (Dx + Dy)/2.0
            self.relax.data.diff[self.run].Dr = (Dy - Dx) / (2.0*self.relax.data.diff[self.run].Da)

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0*self.relax.data.diff[self.run].Diso)

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', self.param_types)

        # Convert the angles to radians.
        if self.angle_units == 'deg':
            alpha = (alpha / 360.0) * 2.0 * pi
            beta = (beta / 360.0) * 2.0 * pi
            gamma = (gamma / 360.0) * 2.0 * pi

        # Make sure the angles are within their defined ranges.
        self.relax.data.diff[self.run].alpha = self.relax.generic.angles.wrap_angles(alpha, 0.0, 2.0*pi)
        self.relax.data.diff[self.run].beta = self.relax.generic.angles.wrap_angles(beta, 0.0, pi)
        self.relax.data.diff[self.run].gamma = self.relax.generic.angles.wrap_angles(gamma, 0.0, 2.0*pi)


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


    def return_data_name(self, name):
        """
        Diffusion tensor parameter string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                                                        |              |                  |
        | Data type                                              | Object name  | Patterns         |
        |________________________________________________________|______________|__________________|
        |                                                        |              |                  |
        | Global correlation time - tm                           | 'tm'         | 'tm'             |
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
        if search('tm', name):
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


    def set(self, run=None, params=None, data_type=None):
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

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Diso = 1.0 / (6.0*tm)
            self.relax.data.diff[self.run].Da = Da
            self.relax.data.diff[self.run].Dpar = self.relax.data.diff[self.run].Diso + 2.0/3.0 * Da
            self.relax.data.diff[self.run].Dper = self.relax.data.diff[self.run].Diso - 1.0/3.0 * Da
            self.relax.data.diff[self.run].Dratio = self.relax.data.diff[self.run].Dpar / self.relax.data.diff[self.run].Dper

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = tm

        # (Diso, Da, theta, phi).
        elif self.param_types == 1:
            # Unpack the tuple.
            Diso, Da, theta, phi = self.params

            # Scaling.
            Diso = Diso * self.d_scale
            Da = Da * self.d_scale

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Diso = Diso
            self.relax.data.diff[self.run].Da = Da
            self.relax.data.diff[self.run].Dpar = Diso + 2.0/3.0 * Da
            self.relax.data.diff[self.run].Dper = Diso - 1.0/3.0 * Da
            self.relax.data.diff[self.run].Dratio = self.relax.data.diff[self.run].Dpar / self.relax.data.diff[self.run].Dper

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0 * self.relax.data.diff[self.run].Diso)

        # (tm, Dratio, theta, phi).
        elif self.param_types == 2:
            # Unpack the tuple.
            tm, Dratio, theta, phi = self.params

            # Scaling.
            tm = tm * self.time_scale

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Diso = 1.0 / (6.0 * tm)
            self.relax.data.diff[self.run].Dratio = Dratio
            self.relax.data.diff[self.run].Dpar = 3.0 * self.relax.data.diff[self.run].Diso * Dratio / (Dratio + 2.0)
            self.relax.data.diff[self.run].Dper = 3.0 * self.relax.data.diff[self.run].Diso / (Dratio + 2.0)
            self.relax.data.diff[self.run].Da = self.relax.data.diff[self.run].Dpar - self.relax.data.diff[self.run].Dper

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = tm

        # (Dpar, Dper, theta, phi).
        elif self.param_types == 3:
            # Unpack the tuple.
            Dpar, Dper, theta, phi = self.params

            # Scaling.
            Dpar = Dpar * self.d_scale
            Dper = Dper * self.d_scale

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Dpar = Dpar
            self.relax.data.diff[self.run].Dper = Dper
            self.relax.data.diff[self.run].Diso = (Dpar + 2.0*Dper) / 3.0
            self.relax.data.diff[self.run].Da = Dpar - Dper
            self.relax.data.diff[self.run].Dratio = Dpar / Dper

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0 * self.relax.data.diff[self.run].Diso)

        # (Diso, Dratio, theta, phi).
        elif self.param_types == 4:
            # Unpack the tuple.
            Diso, Dratio, theta, phi = self.params

            # Scaling.
            Diso = Diso * self.d_scale

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Diso = Diso
            self.relax.data.diff[self.run].Dratio = Dratio
            self.relax.data.diff[self.run].Dpar = 3.0 * Diso * Dratio / (Dratio + 2.0)
            self.relax.data.diff[self.run].Dper = 3.0 * Diso / (Dratio + 2.0)
            self.relax.data.diff[self.run].Da = self.relax.data.diff[self.run].Dpar - self.relax.data.diff[self.run].Dper

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0 * Diso)

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', self.param_types)

        # Convert the angles to radians.
        if self.angle_units == 'deg':
            theta = (theta / 360.0) * 2.0 * pi
            phi = (phi / 360.0) * 2.0 * pi

        # Make sure the angles are within their defined ranges.
        self.relax.data.diff[self.run].theta = self.relax.generic.angles.wrap_angles(theta, 0.0, pi)
        self.relax.data.diff[self.run].phi = self.relax.generic.angles.wrap_angles(phi, 0.0, 2.0*pi)

        # Unit symmetry axis vector.
        #x = cos(self.relax.data.diff[self.run].theta) * sin(self.relax.data.diff[self.run].phi)
        #y = sin(self.relax.data.diff[self.run].theta) * sin(self.relax.data.diff[self.run].phi)
        #z = cos(self.relax.data.diff[self.run].phi)
        #self.relax.data.diff[self.run].axis_unit = array([x, y, z], Float64)

        # Full symmetry axis vector.
        #self.relax.data.diff[self.run].axis_vect = self.relax.data.diff[self.run].Dpar * self.relax.data.diff[self.run].axis_unit


    def test_params(self, num_params):
        """Function for testing the validity of the input parameters."""

        # tm.
        if self.relax.data.diff[self.run].tm <= 0.0 or self.relax.data.diff[self.run].tm > 1e-6:
            raise RelaxError, "The tm value of " + `self.relax.data.diff[self.run].tm` + " should be between zero and one microsecond."

        # Spheroid.
        if num_params == 4:
            # Da.
            if self.relax.data.diff[self.run].Da < -1.5*self.relax.data.diff[self.run].Diso or self.relax.data.diff[self.run].Da > 3.0*self.relax.data.diff[self.run].Diso:
                raise RelaxError, "The Da value of " + `self.relax.data.diff[self.run].Da` + " should be between -3/2 * Diso and 3Diso."

        # Ellipsoid.
        if num_params == 6:
            # Da.
            if self.relax.data.diff[self.run].Da < 0.0 or self.relax.data.diff[self.run].Da > 3.0*self.relax.data.diff[self.run].Diso:
                raise RelaxError, "The Da value of " + `self.relax.data.diff[self.run].Da` + " should be between zero and 3Diso."

            # Dr.
            if self.relax.data.diff[self.run].Dr < 0.0 or self.relax.data.diff[self.run].Dr > 1.0:
                raise RelaxError, "The Dr value of " + `self.relax.data.diff[self.run].Dr` + " should be between zero and one."
