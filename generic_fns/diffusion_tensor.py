###############################################################################
#                                                                             #
# Copyright (C) 2003-2007 Edward d'Auvergne                                   #
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
from copy import deepcopy
from math import cos, pi, sin
from Numeric import Float64, array, dot, identity, transpose, zeros
from re import search

# relax module imports.
from relax_errors import RelaxError, RelaxNoRunError, RelaxNoTensorError, RelaxTensorError, RelaxUnknownParamCombError, RelaxUnknownParamError


def calc_Diso(tm):
    """Function for calculating the Diso value.

    The equation for calculating the parameter is

        Diso  =  1 / (6tm).

    @keyword tm:    The global correlation time.
    @type tm:       float
    @return:        The isotropic diffusion rate (Diso).
    @rtype:         float
    """

    # Calculated and return the Diso value.
    return 1.0 / (6.0 * tm)


def calc_Dpar(Diso, Da):
    """Function for calculating the Dpar value.

    The equation for calculating the parameter is

        Dpar  =  Diso + 2/3 Da.

    @keyword Diso:  The isotropic diffusion rate.
    @type Diso:     float
    @keyword Da:    The anisotropic diffusion rate.
    @type Da:       float
    @return:        The diffusion rate parallel to the unique axis of the spheroid.
    @rtype:         float
    """

    # Dpar value.
    return Diso + 2.0/3.0 * Da


def calc_Dpar_unit(theta, phi):
    """Function for calculating the Dpar unit vector.

    The unit vector parallel to the unique axis of the diffusion tensor is

                      | sin(theta) * cos(phi) |
        Dpar_unit  =  | sin(theta) * sin(phi) |.
                      |      cos(theta)       |

    @keyword theta: The azimuthal angle in radians.
    @type theta:    float
    @keyword phi:   The polar angle in radians.
    @type phi:      float
    @return:        The Dpar unit vector.
    @rtype:         Numeric array (Float64)
    """

    # Initilise the vector.
    Dpar_unit = zeros(3, Float64)

    # Calculate the x, y, and z components.
    Dpar_unit[0] = sin(theta) * cos(phi)
    Dpar_unit[1] = sin(theta) * sin(phi)
    Dpar_unit[2] = cos(theta)

    # Return the unit vector.
    return Dpar_unit


def calc_Dper(Diso, Da):
    """Function for calculating the Dper value.

    The equation for calculating the parameter is

        Dper  =  Diso - 1/3 Da.

    @keyword Diso:  The isotropic diffusion rate.
    @type Diso:     float
    @keyword Da:    The anisotropic diffusion rate.
    @type Da:       float
    @return:        The diffusion rate perpendicular to the unique axis of the spheroid.
    @rtype:         float
    """

    # Dper value.
    return Diso - 1.0/3.0 * Da


def calc_Dratio(Dpar, Dper):
    """Function for calculating the Dratio value.

    The equation for calculating the parameter is

        Dratio  =  Dpar / Dper.

    @keyword Dpar:  The diffusion rate parallel to the unique axis of the spheroid.
    @type Dpar:     float
    @keyword Dper:  The diffusion rate perpendicular to the unique axis of the spheroid.
    @type Dper:     float
    @return:        The ratio of the parallel and perpendicular diffusion rates.
    @rtype:         float
    """

    # Dratio value.
    return Dpar / Dper


def calc_Dx(Diso, Da, Dr):
    """Function for calculating the Dx value.

    The equation for calculating the parameter is

        Dx  =  Diso - 1/3 Da(1 + 3Dr).

    @keyword Diso:  The isotropic diffusion rate.
    @type Diso:     float
    @keyword Da:    The anisotropic diffusion rate.
    @type Da:       float
    @keyword Dr:    The rhombic component of the diffusion tensor.
    @type Dr:       float
    @return:        The diffusion rate parallel to the x-axis of the ellipsoid.
    @rtype:         float
    """

    # Dx value.
    return Diso - 1.0/3.0 * Da * (1.0 + 3.0*Dr)


def calc_Dx_unit(alpha, beta, gamma):
    """Function for calculating the Dx unit vector.

    The unit Dx vector is

                    | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
        Dx_unit  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |.
                    |                    cos(alpha) * sin(beta)                      |

    @keyword alpha: The Euler angle alpha in radians using the z-y-z convention.
    @type alpha:    float
    @keyword beta:  The Euler angle beta in radians using the z-y-z convention.
    @type beta:     float
    @keyword gamma: The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:    float
    @return:        The Dx unit vector.
    @rtype:         Numeric array (Float64)
    """

    # Initilise the vector.
    Dx_unit = zeros(3, Float64)

    # Calculate the x, y, and z components.
    Dx_unit[0] = -sin(alpha) * sin(gamma)  +  cos(alpha) * cos(beta) * cos(gamma)
    Dx_unit[1] = -sin(alpha) * cos(gamma)  -  cos(alpha) * cos(beta) * sin(gamma)
    Dx_unit[2] = cos(alpha) * sin(beta)

    # Return the unit vector.
    return Dx_unit


def calc_Dy(Diso, Da, Dr):
    """Function for calculating the Dy value.

    The equation for calculating the parameter is

        Dy  =  Diso - 1/3 Da(1 - 3Dr),

    @keyword Diso:  The isotropic diffusion rate.
    @type Diso:     float
    @keyword Da:    The anisotropic diffusion rate.
    @type Da:       float
    @keyword Dr:    The rhombic component of the diffusion tensor.
    @type Dr:       float
    @return:        The Dy value.
    @rtype:         float
    """

    # Dy value.
    return Diso - 1.0/3.0 * Da * (1.0 - 3.0*Dr)


def calc_Dy_unit(alpha, beta, gamma):
    """Function for calculating the Dy unit vector.

    The unit Dy vector is

                    | cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
        Dy_unit  =  | cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |.
                    |                   sin(alpha) * sin(beta)                      |

    @keyword alpha: The Euler angle alpha in radians using the z-y-z convention.
    @type alpha:    float
    @keyword beta:  The Euler angle beta in radians using the z-y-z convention.
    @type beta:     float
    @keyword gamma: The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:    float
    @return:        The Dy unit vector.
    @rtype:         Numeric array (Float64)
    """

    # Initilise the vector.
    Dy_unit = zeros(3, Float64)

    # Calculate the x, y, and z components.
    Dy_unit[0] = cos(alpha) * sin(gamma)  +  sin(alpha) * cos(beta) * cos(gamma)
    Dy_unit[1] = cos(alpha) * cos(gamma)  -  sin(alpha) * cos(beta) * sin(gamma)
    Dy_unit[2] = sin(alpha) * sin(beta)

    # Return the unit vector.
    return Dy_unit


def calc_Dz(Diso, Da):
    """Function for calculating the Dz value.

    The equation for calculating the parameter is

        Dz  =  Diso + 2/3 Da.

    @keyword Diso:  The isotropic diffusion rate.
    @type Diso:     float
    @keyword Da:    The anisotropic diffusion rate.
    @type Da:       float
    @return:        The Dz value.
    @rtype:         float
    """

    # Dz value.
    return Diso + 2.0/3.0 * Da


def calc_Dz_unit(beta, gamma):
    """Function for calculating the Dz unit vector.

    The unit Dz vector is

                    | -sin(beta) * cos(gamma) |
        Dz_unit  =  |  sin(beta) * sin(gamma) |.
                    |        cos(beta)        |

    @keyword beta:  The Euler angle beta in radians using the z-y-z convention.
    @type beta:     float
    @keyword gamma: The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:    float
    @return:        The Dz unit vector.
    @rtype:         Numeric array (Float64)
    """

    # Initilise the vector.
    Dz_unit = zeros(3, Float64)

    # Calculate the x, y, and z components.
    Dz_unit[0] = -sin(beta) * cos(gamma)
    Dz_unit[1] = sin(beta) * sin(gamma)
    Dz_unit[2] = cos(beta)

    # Return the unit vector.
    return Dz_unit


def calc_rotation(diff_type, *args):
    """Function for calculating the rotation matrix.

    Spherical diffusion
    ===================

    As the orientation of the diffusion tensor within the structural frame is undefined when the
    molecule diffuses as a sphere, the rotation matrix is simply the identity matrix

              | 1  0  0 |
        R  =  | 0  1  0 |.
              | 0  0  1 |


    Spheroidal diffusion
    ====================

    The rotation matrix required to shift from the diffusion tensor frame to the structural
    frame is equal to

              |  cos(theta) * cos(phi)  -sin(phi)   sin(theta) * cos(phi) |
        R  =  |  cos(theta) * sin(phi)   cos(phi)   sin(theta) * sin(phi) |.
              | -sin(theta)              0          cos(theta)            |


    Ellipsoidal diffusion
    =====================

    The rotation matrix required to shift from the diffusion tensor frame to the structural
    frame is equal to

        R  =  | Dx_unit  Dy_unit  Dz_unit |,

              | Dx_unit[0]  Dy_unit[0]  Dz_unit[0] |
           =  | Dx_unit[1]  Dy_unit[1]  Dz_unit[1] |.
              | Dx_unit[2]  Dy_unit[2]  Dz_unit[2] |

    @param *args:       All the function arguments.
    @type *args:        tuple
    @param theta:       The azimuthal angle in radians.
    @type theta:        float
    @param phi:         The polar angle in radians.
    @type phi:          float
    @param Dpar_unit:   The Dpar unit vector.
    @type Dpar_unit:    Numeric array (Float64)
    @param Dx_unit:     The Dx unit vector.
    @type Dx_unit:      Numeric array (Float64)
    @param Dy_unit:     The Dy unit vector.
    @type Dy_unit:      Numeric array (Float64)
    @param Dz_unit:     The Dz unit vector.
    @type Dz_unit:      Numeric array (Float64)
    @return:            The rotation matrix.
    @rtype:             Numeric array ((3, 3), Float64)
    """

    # The rotation matrix for the sphere.
    if diff_type == 'sphere':
        return identity(3, Float64)

    # The rotation matrix for the spheroid.
    elif diff_type == 'spheroid':
        # Unpack the arguments.
        theta, phi, Dpar_unit = args

        # Initialise the rotation matrix.
        rotation = identity(3, Float64)

        # First row of the rotation matrix.
        rotation[0, 0] = cos(theta) * cos(phi)
        rotation[1, 0] = cos(theta) * sin(phi)
        rotation[2, 0] = -sin(theta)

        # Second row of the rotation matrix.
        rotation[0, 1] = -sin(phi)
        rotation[1, 1] = cos(phi)

        # Replace the last row of the rotation matrix with the Dpar unit vector.
        rotation[:, 2] = Dpar_unit

        # Return the tensor.
        return rotation

    # The rotation matrix for the ellipsoid.
    elif diff_type == 'ellipsoid':
        # Unpack the arguments.
        Dx_unit, Dy_unit, Dz_unit = args

        # Initialise the rotation matrix.
        rotation = identity(3, Float64)

        # First column of the rotation matrix.
        rotation[:, 0] = Dx_unit

        # Second column of the rotation matrix.
        rotation[:, 1] = Dy_unit

        # Third column of the rotation matrix.
        rotation[:, 2] = Dz_unit

        # Return the tensor.
        return rotation

    # Raise an error.
    else:
        raise RelaxError, 'The diffusion tensor has not been specified'


def calc_tensor(rotation, tensor_diag):
    """Function for calculating the diffusion tensor (in the structural frame).

    The diffusion tensor is calculated using the diagonalised tensor and the rotation matrix
    through the equation

        R . tensor_diag . R^T.

    @keyword rotation:      The rotation matrix.
    @type rotation:         Numeric array ((3, 3), Float64)
    @keyword tensor_diag:   The diagonalised diffusion tensor.
    @type tensor_diag:      Numeric array ((3, 3), Float64)
    @return:                The diffusion tensor (within the structural frame).
    @rtype:                 Numeric array ((3, 3), Float64)
    """

    # Rotation (R . tensor_diag . R^T).
    return dot(rotation, dot(tensor_diag, transpose(rotation)))


def calc_tensor_diag(diff_type, *args):
    """Function for calculating the diagonalised diffusion tensor.

    The diagonalised spherical diffusion tensor is defined as

                   | Diso     0     0 |
        tensor  =  |    0  Diso     0 |.
                   |    0     0  Diso |

    The diagonalised spheroidal tensor is defined as

                   | Dper     0     0 |
        tensor  =  |    0  Dper     0 |.
                   |    0     0  Dpar |

    The diagonalised ellipsoidal diffusion tensor is defined as

                   | Dx   0   0 |
        tensor  =  |  0  Dy   0 |.
                   |  0   0  Dz |

    @param *args:   All the arguments.
    @type *args:    tuple
    @param Diso:    The Diso parameter of the sphere.
    @type Diso:     float
    @param Dpar:    The Dpar parameter of the spheroid.
    @type Dpar:     float
    @param Dper:    The Dper parameter of the spheroid.
    @type Dper:     float
    @param Dx:      The Dx parameter of the ellipsoid.
    @type Dx:       float
    @param Dy:      The Dy parameter of the ellipsoid.
    @type Dy:       float
    @param Dz:      The Dz parameter of the ellipsoid.
    @type Dz:       float
    @return:        The diagonalised diffusion tensor.
    @rtype:         Numeric array ((3, 3), Float64)
    """

    # Spherical diffusion tensor.
    if diff_type == 'sphere':
        # Unpack the arguments.
        Diso, = args

        # Initialise the tensor.
        tensor = zeros((3, 3), Float64)

        # Populate the diagonal elements.
        tensor[0, 0] = Diso
        tensor[1, 1] = Diso
        tensor[2, 2] = Diso

        # Return the tensor.
        return tensor

    # Spheroidal diffusion tensor.
    elif diff_type == 'spheroid':
        # Unpack the arguments.
        Dpar, Dper = args

        # Initialise the tensor.
        tensor = zeros((3, 3), Float64)

        # Populate the diagonal elements.
        tensor[0, 0] = Dper
        tensor[1, 1] = Dper
        tensor[2, 2] = Dpar

        # Return the tensor.
        return tensor

    # Ellipsoidal diffusion tensor.
    elif diff_type == 'ellipsoid':
        # Unpack the arguments.
        Dx, Dy, Dz = args

        # Initialise the tensor.
        tensor = zeros((3, 3), Float64)

        # Populate the diagonal elements.
        tensor[0, 0] = Dx
        tensor[1, 1] = Dy
        tensor[2, 2] = Dz

        # Return the tensor.
        return tensor


class Diffusion_tensor:
    def __init__(self, relax):
        """Class containing the function for setting up the diffusion tensor."""

        self.relax = relax

        # relax data store module import.  This import statement has to be here to prevent circular import issues.
        from data import Data

        # The relax data storage object.
        global relax_data_store
        relax_data_store = Data()




    def copy(self, run1=None, run2=None):
        """Function for copying diffusion tensor data from run1 to run2."""

        # Test if run1 exists.
        if not run1 in relax_data_store.run_names:
            raise RelaxNoRunError, run1

        # Test if run2 exists.
        if not run2 in relax_data_store.run_names:
            raise RelaxNoRunError, run2

        # Test if run1 contains diffusion tensor data.
        if not relax_data_store.diff.has_key(run1):
            raise RelaxNoTensorError, run1

        # Test if run2 contains diffusion tensor data.
        if relax_data_store.diff.has_key(run2):
            raise RelaxTensorError, run2

        # Copy the data.
        relax_data_store.diff[run2] = deepcopy(relax_data_store.diff[run1])


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
        if not run in relax_data_store.run_names:
            raise RelaxNoRunError, run

        # Test if diffusion tensor data for the run exists.
        if not relax_data_store.diff.has_key(run):
            raise RelaxNoTensorError, run

        # Delete the diffusion data.
        del(relax_data_store.diff[run])

        # Clean up the runs.
        self.relax.generic.runs.eliminate_unused_runs()


    def display(self, run=None):
        """Function for displaying the diffusion tensor."""

        # Test if the run exists.
        if not run in relax_data_store.run_names:
            raise RelaxNoRunError, run

        # Test if diffusion tensor data for the run exists.
        if not relax_data_store.diff.has_key(run):
            raise RelaxNoTensorError, run

        # Spherical diffusion.
        if relax_data_store.diff[run].type == 'sphere':
            # Tensor type.
            print "Type:  Spherical diffusion"

            # Parameters.
            print "\nParameters {tm}."
            print "tm (s):  " + `relax_data_store.diff[run].tm`

            # Alternate parameters.
            print "\nAlternate parameters {Diso}."
            print "Diso (1/s):  " + `relax_data_store.diff[run].Diso`

            # Fixed flag.
            print "\nFixed:  " + `relax_data_store.diff[run].fixed`

        # Spheroidal diffusion.
        elif relax_data_store.diff[run].type == 'spheroid':
            # Tensor type.
            print "Type:  Spheroidal diffusion"

            # Parameters.
            print "\nParameters {tm, Da, theta, phi}."
            print "tm (s):  " + `relax_data_store.diff[run].tm`
            print "Da (1/s):  " + `relax_data_store.diff[run].Da`
            print "theta (rad):  " + `relax_data_store.diff[run].theta`
            print "phi (rad):  " + `relax_data_store.diff[run].phi`

            # Alternate parameters.
            print "\nAlternate parameters {Diso, Da, theta, phi}."
            print "Diso (1/s):  " + `relax_data_store.diff[run].Diso`
            print "Da (1/s):  " + `relax_data_store.diff[run].Da`
            print "theta (rad):  " + `relax_data_store.diff[run].theta`
            print "phi (rad):  " + `relax_data_store.diff[run].phi`

            # Alternate parameters.
            print "\nAlternate parameters {Dpar, Dper, theta, phi}."
            print "Dpar (1/s):  " + `relax_data_store.diff[run].Dpar`
            print "Dper (1/s):  " + `relax_data_store.diff[run].Dper`
            print "theta (rad):  " + `relax_data_store.diff[run].theta`
            print "phi (rad):  " + `relax_data_store.diff[run].phi`

            # Alternate parameters.
            print "\nAlternate parameters {tm, Dratio, theta, phi}."
            print "tm (s):  " + `relax_data_store.diff[run].tm`
            print "Dratio:  " + `relax_data_store.diff[run].Dratio`
            print "theta (rad):  " + `relax_data_store.diff[run].theta`
            print "phi (rad):  " + `relax_data_store.diff[run].phi`

            # Fixed flag.
            print "\nFixed:  " + `relax_data_store.diff[run].fixed`

        # Ellipsoidal diffusion.
        elif relax_data_store.diff[run].type == 'ellipsoid':
            # Tensor type.
            print "Type:  Ellipsoidal diffusion"

            # Parameters.
            print "\nParameters {tm, Da, Dr, alpha, beta, gamma}."
            print "tm (s):  " + `relax_data_store.diff[run].tm`
            print "Da (1/s):  " + `relax_data_store.diff[run].Da`
            print "Dr:  " + `relax_data_store.diff[run].Dr`
            print "alpha (rad):  " + `relax_data_store.diff[run].alpha`
            print "beta (rad):  " + `relax_data_store.diff[run].beta`
            print "gamma (rad):  " + `relax_data_store.diff[run].gamma`

            # Alternate parameters.
            print "\nAlternate parameters {Diso, Da, Dr, alpha, beta, gamma}."
            print "Diso (1/s):  " + `relax_data_store.diff[run].Diso`
            print "Da (1/s):  " + `relax_data_store.diff[run].Da`
            print "Dr:  " + `relax_data_store.diff[run].Dr`
            print "alpha (rad):  " + `relax_data_store.diff[run].alpha`
            print "beta (rad):  " + `relax_data_store.diff[run].beta`
            print "gamma (rad):  " + `relax_data_store.diff[run].gamma`

            # Alternate parameters.
            print "\nAlternate parameters {Dx, Dy, Dz, alpha, beta, gamma}."
            print "Dx (1/s):  " + `relax_data_store.diff[run].Dx`
            print "Dy (1/s):  " + `relax_data_store.diff[run].Dy`
            print "Dz (1/s):  " + `relax_data_store.diff[run].Dz`
            print "alpha (rad):  " + `relax_data_store.diff[run].alpha`
            print "beta (rad):  " + `relax_data_store.diff[run].beta`
            print "gamma (rad):  " + `relax_data_store.diff[run].gamma`

            # Fixed flag.
            print "\nFixed:  " + `relax_data_store.diff[run].fixed`


    def ellipsoid(self):
        """Function for setting up ellipsoidal diffusion."""

        # The diffusion type.
        relax_data_store.diff[self.run].type = 'ellipsoid'

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
        if relax_data_store.diff[self.run].type == 'spheroid':
            # Get the current angles.
            theta = relax_data_store.diff[self.run].theta
            phi = relax_data_store.diff[self.run].phi

            # Simulated values.
            if sim_index != None:
                theta_sim = relax_data_store.diff[self.run].theta_sim[sim_index]
                phi_sim   = relax_data_store.diff[self.run].phi_sim[sim_index]

            # Normal value.
            if sim_index == None:
                relax_data_store.diff[self.run].theta = self.relax.generic.angles.wrap_angles(theta, 0.0, pi)
                relax_data_store.diff[self.run].phi = self.relax.generic.angles.wrap_angles(phi, 0.0, 2.0*pi)

            # Simulated theta and phi values.
            else:
                relax_data_store.diff[self.run].theta_sim[sim_index] = self.relax.generic.angles.wrap_angles(theta_sim, theta - pi/2.0, theta + pi/2.0)
                relax_data_store.diff[self.run].phi_sim[sim_index]   = self.relax.generic.angles.wrap_angles(phi_sim, phi - pi, phi + pi)

        # Ellipsoid.
        elif relax_data_store.diff[self.run].type == 'ellipsoid':
            # Get the current angles.
            alpha = relax_data_store.diff[self.run].alpha
            beta  = relax_data_store.diff[self.run].beta
            gamma = relax_data_store.diff[self.run].gamma

            # Simulated values.
            if sim_index != None:
                alpha_sim = relax_data_store.diff[self.run].alpha_sim[sim_index]
                beta_sim  = relax_data_store.diff[self.run].beta_sim[sim_index]
                gamma_sim = relax_data_store.diff[self.run].gamma_sim[sim_index]

            # Normal value.
            if sim_index == None:
                relax_data_store.diff[self.run].alpha = self.relax.generic.angles.wrap_angles(alpha, 0.0, 2.0*pi)
                relax_data_store.diff[self.run].beta  = self.relax.generic.angles.wrap_angles(beta, 0.0, 2.0*pi)
                relax_data_store.diff[self.run].gamma = self.relax.generic.angles.wrap_angles(gamma, 0.0, 2.0*pi)

            # Simulated alpha, beta, and gamma values.
            else:
                relax_data_store.diff[self.run].alpha_sim[sim_index] = self.relax.generic.angles.wrap_angles(alpha_sim, alpha - pi, alpha + pi)
                relax_data_store.diff[self.run].beta_sim[sim_index]  = self.relax.generic.angles.wrap_angles(beta_sim, beta - pi, beta + pi)
                relax_data_store.diff[self.run].gamma_sim[sim_index] = self.relax.generic.angles.wrap_angles(gamma_sim, gamma - pi, gamma + pi)


        # Remove the glide reflection and translational symmetries.
        ###########################################################

        # Spheroid.
        if relax_data_store.diff[self.run].type == 'spheroid':
            # Normal value.
            if sim_index == None:
                # Fold phi inside 0 and pi.
                if relax_data_store.diff[self.run].phi >= pi:
                    relax_data_store.diff[self.run].theta = pi - relax_data_store.diff[self.run].theta
                    relax_data_store.diff[self.run].phi = relax_data_store.diff[self.run].phi - pi

            # Simulated theta and phi values.
            else:
                # Fold phi_sim inside phi-pi/2 and phi+pi/2.
                if relax_data_store.diff[self.run].phi_sim[sim_index] >= relax_data_store.diff[self.run].phi + pi/2.0:
                    relax_data_store.diff[self.run].theta_sim[sim_index] = pi - relax_data_store.diff[self.run].theta_sim[sim_index]
                    relax_data_store.diff[self.run].phi_sim[sim_index]   = relax_data_store.diff[self.run].phi_sim[sim_index] - pi
                elif relax_data_store.diff[self.run].phi_sim[sim_index] <= relax_data_store.diff[self.run].phi - pi/2.0:
                    relax_data_store.diff[self.run].theta_sim[sim_index] = pi - relax_data_store.diff[self.run].theta_sim[sim_index]
                    relax_data_store.diff[self.run].phi_sim[sim_index]   = relax_data_store.diff[self.run].phi_sim[sim_index] + pi

        # Ellipsoid.
        elif relax_data_store.diff[self.run].type == 'ellipsoid':
            # Normal value.
            if sim_index == None:
                # Fold alpha inside 0 and pi.
                if relax_data_store.diff[self.run].alpha >= pi:
                    relax_data_store.diff[self.run].alpha = relax_data_store.diff[self.run].alpha - pi

                # Fold beta inside 0 and pi.
                if relax_data_store.diff[self.run].beta >= pi:
                    relax_data_store.diff[self.run].alpha = pi - relax_data_store.diff[self.run].alpha
                    relax_data_store.diff[self.run].beta = relax_data_store.diff[self.run].beta - pi

                # Fold gamma inside 0 and pi.
                if relax_data_store.diff[self.run].gamma >= pi:
                    relax_data_store.diff[self.run].alpha = pi - relax_data_store.diff[self.run].alpha
                    relax_data_store.diff[self.run].beta = pi - relax_data_store.diff[self.run].beta
                    relax_data_store.diff[self.run].gamma = relax_data_store.diff[self.run].gamma - pi

            # Simulated theta and phi values.
            else:
                # Fold alpha_sim inside alpha-pi/2 and alpha+pi/2.
                if relax_data_store.diff[self.run].alpha_sim[sim_index] >= relax_data_store.diff[self.run].alpha + pi/2.0:
                    relax_data_store.diff[self.run].alpha_sim[sim_index] = relax_data_store.diff[self.run].alpha_sim[sim_index] - pi
                elif relax_data_store.diff[self.run].alpha_sim[sim_index] <= relax_data_store.diff[self.run].alpha - pi/2.0:
                    relax_data_store.diff[self.run].alpha_sim[sim_index] = relax_data_store.diff[self.run].alpha_sim[sim_index] + pi

                # Fold beta_sim inside beta-pi/2 and beta+pi/2.
                if relax_data_store.diff[self.run].beta_sim[sim_index] >= relax_data_store.diff[self.run].beta + pi/2.0:
                    relax_data_store.diff[self.run].alpha_sim[sim_index] = pi - relax_data_store.diff[self.run].alpha_sim[sim_index]
                    relax_data_store.diff[self.run].beta_sim[sim_index] = relax_data_store.diff[self.run].beta_sim[sim_index] - pi
                elif relax_data_store.diff[self.run].beta_sim[sim_index] <= relax_data_store.diff[self.run].beta - pi/2.0:
                    relax_data_store.diff[self.run].alpha_sim[sim_index] = pi - relax_data_store.diff[self.run].alpha_sim[sim_index]
                    relax_data_store.diff[self.run].beta_sim[sim_index] = relax_data_store.diff[self.run].beta_sim[sim_index] + pi

                # Fold gamma_sim inside gamma-pi/2 and gamma+pi/2.
                if relax_data_store.diff[self.run].gamma_sim[sim_index] >= relax_data_store.diff[self.run].gamma + pi/2.0:
                    relax_data_store.diff[self.run].alpha_sim[sim_index] = pi - relax_data_store.diff[self.run].alpha_sim[sim_index]
                    relax_data_store.diff[self.run].beta_sim[sim_index] = pi - relax_data_store.diff[self.run].beta_sim[sim_index]
                    relax_data_store.diff[self.run].gamma_sim[sim_index] = relax_data_store.diff[self.run].gamma_sim[sim_index] - pi
                elif relax_data_store.diff[self.run].gamma_sim[sim_index] <= relax_data_store.diff[self.run].gamma - pi/2.0:
                    relax_data_store.diff[self.run].alpha_sim[sim_index] = pi - relax_data_store.diff[self.run].alpha_sim[sim_index]
                    relax_data_store.diff[self.run].beta_sim[sim_index] = pi - relax_data_store.diff[self.run].beta_sim[sim_index]
                    relax_data_store.diff[self.run].gamma_sim[sim_index] = relax_data_store.diff[self.run].gamma_sim[sim_index] + pi


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
        if not self.run in relax_data_store.run_names:
            raise RelaxNoRunError, self.run

        # Test if diffusion tensor data corresponding to the run already exists.
        if relax_data_store.diff.has_key(self.run):
            raise RelaxTensorError, self.run

        # Check the validity of the angle_units argument.
        valid_types = ['deg', 'rad']
        if not angle_units in valid_types:
            raise RelaxError, "The diffusion tensor 'angle_units' argument " + `angle_units` + " should be either 'deg' or 'rad'."

        # Add the run to the diffusion tensor data structure.
        relax_data_store.diff.add_item(self.run)

        # Set the fixed flag.
        relax_data_store.diff[self.run].fixed = fixed

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
        data = relax_data_store.diff[self.run]

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
                value[i] = self.default_value(object_names[i])

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

        if relax_data_store.diff[self.run].type == 'sphere':
            # Geometric parameters.
            #######################

            # A single geometric parameter.
            if len(geo_params) == 1:
                # The single parameter tm.
                if geo_params[0] == 'tm':
                    relax_data_store.diff[self.run].tm = geo_values[0]

                # The single parameter Diso.
                elif geo_params[0] == 'Diso':
                    relax_data_store.diff[self.run].tm = 1.0 / (6.0 * geo_values[0])

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

        elif relax_data_store.diff[self.run].type == 'spheroid':
            # Geometric parameters.
            #######################

            # A single geometric parameter.
            if len(geo_params) == 1:
                # The single parameter tm.
                if geo_params[0] == 'tm':
                    relax_data_store.diff[self.run].tm = geo_values[0]

                # The single parameter Diso.
                elif geo_params[0] == 'Diso':
                    relax_data_store.diff[self.run].tm = 1.0 / (6.0 * geo_values[0])

                # The single parameter Da.
                elif geo_params[0] == 'Da':
                    relax_data_store.diff[self.run].Da = geo_values[0]

                # The single parameter Dratio.
                elif geo_params[0] == 'Dratio':
                    Dratio = geo_values[0]
                    relax_data_store.diff[self.run].Da = (Dratio - 1.0) / (2.0 * relax_data_store.diff[self.run].tm * (Dratio + 2.0))

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
                    relax_data_store.diff[self.run].tm = tm
                    relax_data_store.diff[self.run].Da = Da

                # The geometric parameter set {Diso, Da}.
                elif geo_params.count('Diso') == 1 and geo_params.count('Da') == 1:
                    # The parameters.
                    Diso = geo_values[geo_params.index('Diso')]
                    Da = geo_values[geo_params.index('Da')]

                    # Set the internal parameter values.
                    relax_data_store.diff[self.run].tm = 1.0 / (6.0 * Diso)
                    relax_data_store.diff[self.run].Da = Da

                # The geometric parameter set {tm, Dratio}.
                elif geo_params.count('tm') == 1 and geo_params.count('Dratio') == 1:
                    # The parameters.
                    tm = geo_values[geo_params.index('tm')]
                    Dratio = geo_values[geo_params.index('Dratio')]

                    # Set the internal parameter values.
                    relax_data_store.diff[self.run].tm = tm
                    relax_data_store.diff[self.run].Da = (Dratio - 1.0) / (2.0 * tm * (Dratio + 2.0))

                # The geometric parameter set {Dpar, Dper}.
                elif geo_params.count('Dpar') == 1 and geo_params.count('Dpar') == 1:
                    # The parameters.
                    Dpar = geo_values[geo_params.index('Dpar')]
                    Dper = geo_values[geo_params.index('Dper')]

                    # Set the internal parameter values.
                    relax_data_store.diff[self.run].tm = 1.0 / (2.0 * (Dpar + 2.0*Dper))
                    relax_data_store.diff[self.run].Da = Dpar - Dper

                # The geometric parameter set {Diso, Dratio}.
                elif geo_params.count('Diso') == 1 and geo_params.count('Dratio') == 1:
                    # The parameters.
                    Diso = geo_values[geo_params.index('Diso')]
                    Dratio = geo_values[geo_params.index('Dratio')]

                    # Set the internal parameter values.
                    relax_data_store.diff[self.run].tm = 1.0 / (6.0 * Diso)
                    relax_data_store.diff[self.run].Da = 3.0 * Diso * (Dratio - 1.0) / (Dratio + 2.0)

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
                    relax_data_store.diff[self.run].theta = orient_values[orient_params.index('theta')]

                # The single parameter phi.
                elif orient_params[0] == 'phi':
                    relax_data_store.diff[self.run].phi = orient_values[orient_params.index('phi')]

            # Two orientational parameters.
            elif len(orient_params) == 2:
                # The orientational parameter set {theta, phi}.
                if orient_params.count('theta') == 1 and orient_params.count('phi') == 1:
                    relax_data_store.diff[self.run].theta = orient_values[orient_params.index('theta')]
                    relax_data_store.diff[self.run].phi = orient_values[orient_params.index('phi')]

                # Unknown parameter combination.
                else:
                    raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)

            # More than two orientational parameters.
            elif len(orient_params) > 2:
                raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)


        # Ellipsoidal diffusion.
        ########################

        elif relax_data_store.diff[self.run].type == 'ellipsoid':
            # Geometric parameters.
            #######################

            # A single geometric parameter.
            if len(geo_params) == 1:
                # The single parameter tm.
                if geo_params[0] == 'tm':
                    relax_data_store.diff[self.run].tm = geo_values[0]

                # The single parameter Diso.
                elif geo_params[0] == 'Diso':
                    relax_data_store.diff[self.run].tm = 1.0 / (6.0 * geo_values[0])

                # The single parameter Da.
                elif geo_params[0] == 'Da':
                    relax_data_store.diff[self.run].Da = geo_values[0]

                # The single parameter Dr.
                elif geo_params[0] == 'Dr':
                    relax_data_store.diff[self.run].Dr = geo_values[0]

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
                    relax_data_store.diff[self.run].tm = tm
                    relax_data_store.diff[self.run].Da = Da

                # The geometric parameter set {tm, Dr}.
                elif geo_params.count('tm') == 1 and geo_params.count('Dr') == 1:
                    # The parameters.
                    tm = geo_values[geo_params.index('tm')]
                    Dr = geo_values[geo_params.index('Dr')]

                    # Set the internal parameter values.
                    relax_data_store.diff[self.run].tm = tm
                    relax_data_store.diff[self.run].Dr = Dr

                # The geometric parameter set {Diso, Da}.
                elif geo_params.count('Diso') == 1 and geo_params.count('Da') == 1:
                    # The parameters.
                    Diso = geo_values[geo_params.index('Diso')]
                    Da = geo_values[geo_params.index('Da')]

                    # Set the internal parameter values.
                    relax_data_store.diff[self.run].tm = 1.0 / (6.0 * Diso)
                    relax_data_store.diff[self.run].Da = Da

                # The geometric parameter set {Diso, Dr}.
                elif geo_params.count('Diso') == 1 and geo_params.count('Dr') == 1:
                    # The parameters.
                    Diso = geo_values[geo_params.index('Diso')]
                    Dr = geo_values[geo_params.index('Dr')]

                    # Set the internal parameter values.
                    relax_data_store.diff[self.run].tm = 1.0 / (6.0 * Diso)
                    relax_data_store.diff[self.run].Dr = Dr

                # The geometric parameter set {Da, Dr}.
                elif geo_params.count('Da') == 1 and geo_params.count('Dr') == 1:
                    # The parameters.
                    Da = geo_values[geo_params.index('Da')]
                    Dr = geo_values[geo_params.index('Dr')]

                    # Set the internal parameter values.
                    relax_data_store.diff[self.run].Da = Da
                    relax_data_store.diff[self.run].Da = Dr

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
                    relax_data_store.diff[self.run].tm = tm
                    relax_data_store.diff[self.run].Da = Da
                    relax_data_store.diff[self.run].Dr = Dr

                # The geometric parameter set {Diso, Da, Dr}.
                elif geo_params.count('Diso') == 1 and geo_params.count('Da') == 1 and geo_params.count('Dr') == 1:
                    # The parameters.
                    Diso = geo_values[geo_params.index('Diso')]
                    Da = geo_values[geo_params.index('Da')]
                    Dr = geo_values[geo_params.index('Dr')]

                    # Set the internal parameter values.
                    relax_data_store.diff[self.run].tm = 1.0 / (6.0 * Diso)
                    relax_data_store.diff[self.run].Da = Da
                    relax_data_store.diff[self.run].Dr = Dr

                # The geometric parameter set {Dx, Dy, Dz}.
                elif geo_params.count('Dx') == 1 and geo_params.count('Dy') == 1 and geo_params.count('Dz') == 1:
                    # The parameters.
                    Dx = geo_values[geo_params.index('Dx')]
                    Dy = geo_values[geo_params.index('Dy')]
                    Dz = geo_values[geo_params.index('Dz')]

                    # Set the internal tm value.
                    if Dx + Dy + Dz == 0.0:
                        relax_data_store.diff[self.run].tm = 1e99
                    else:
                        relax_data_store.diff[self.run].tm = 0.5 / (Dx + Dy + Dz)

                    # Set the internal Da value.
                    relax_data_store.diff[self.run].Da = Dz - 0.5*(Dx + Dy)

                    # Set the internal Dr value.
                    if relax_data_store.diff[self.run].Da == 0.0:
                        relax_data_store.diff[self.run].Dr = (Dy - Dx) * 1e99
                    else:
                        relax_data_store.diff[self.run].Dr = (Dy - Dx) / (2.0*relax_data_store.diff[self.run].Da)

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
                    relax_data_store.diff[self.run].alpha = orient_values[orient_params.index('alpha')]

                # The single parameter beta.
                elif orient_params[0] == 'beta':
                    relax_data_store.diff[self.run].beta = orient_values[orient_params.index('beta')]

                # The single parameter gamma.
                elif orient_params[0] == 'gamma':
                    relax_data_store.diff[self.run].gamma = orient_values[orient_params.index('gamma')]

            # Two orientational parameters.
            elif len(orient_params) == 2:
                # The orientational parameter set {alpha, beta}.
                if orient_params.count('alpha') == 1 and orient_params.count('beta') == 1:
                    relax_data_store.diff[self.run].alpha = orient_values[orient_params.index('alpha')]
                    relax_data_store.diff[self.run].beta = orient_values[orient_params.index('beta')]

                # The orientational parameter set {alpha, gamma}.
                if orient_params.count('alpha') == 1 and orient_params.count('gamma') == 1:
                    relax_data_store.diff[self.run].alpha = orient_values[orient_params.index('alpha')]
                    relax_data_store.diff[self.run].gamma = orient_values[orient_params.index('gamma')]

                # The orientational parameter set {beta, gamma}.
                if orient_params.count('beta') == 1 and orient_params.count('gamma') == 1:
                    relax_data_store.diff[self.run].beta = orient_values[orient_params.index('beta')]
                    relax_data_store.diff[self.run].gamma = orient_values[orient_params.index('gamma')]

                # Unknown parameter combination.
                else:
                    raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)

            # Three orientational parameters.
            elif len(orient_params) == 3:
                # The orientational parameter set {alpha, beta, gamma}.
                if orient_params.count('alpha') == 1 and orient_params.count('beta') == 1:
                    relax_data_store.diff[self.run].alpha = orient_values[orient_params.index('alpha')]
                    relax_data_store.diff[self.run].beta = orient_values[orient_params.index('beta')]
                    relax_data_store.diff[self.run].gamma = orient_values[orient_params.index('gamma')]

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
        relax_data_store.diff[self.run].type = 'sphere'

        # tm.
        if self.param_types == 0:
            # Scaling.
            tm = self.params * self.time_scale

            # Set the parameters.
            self.set(run=self.run, value=[tm], param=['tm'])

        # Diso
        elif self.param_types == 1:
            # Scaling.
            Diso = self.params * self.d_scale

            # Set the parameters.
            self.set(run=self.run, value=[Diso], param=['Diso'])

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', self.param_types)


    def spheroid(self):
        """Function for setting up spheroidal diffusion."""

        # The diffusion type.
        relax_data_store.diff[self.run].type = 'spheroid'

        # Spheroid diffusion type.
        allowed_types = [None, 'oblate', 'prolate']
        if self.spheroid_type not in allowed_types:
            raise RelaxError, "The 'spheroid_type' argument " + `self.spheroid_type` + " should be 'oblate', 'prolate', or None."
        relax_data_store.diff[self.run].spheroid_type = self.spheroid_type

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
        tm = relax_data_store.diff[self.run].tm
        if tm <= 0.0 or tm > 1e-6:
            raise RelaxError, "The tm value of " + `tm` + " should be between zero and one microsecond."

        # Spheroid.
        if num_params == 4:
            # Parameters.
            Diso = 1.0 / (6.0 * relax_data_store.diff[self.run].tm)
            Da = relax_data_store.diff[self.run].Da

            # Da.
            if Da < (-1.5*Diso - error*Diso) or Da > (3.0*Diso + error*Diso):
                raise RelaxError, "The Da value of " + `Da` + " should be between -3/2 * Diso and 3Diso."

        # Ellipsoid.
        if num_params == 6:
            # Parameters.
            Diso = 1.0 / (6.0 * relax_data_store.diff[self.run].tm)
            Da = relax_data_store.diff[self.run].Da
            Dr = relax_data_store.diff[self.run].Dr

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
        if relax_data_store.diff[self.run].type == 'spheroid':
            # Initialise.
            Dpar = zeros(3, Float64)

            # Trig.
            sin_theta = sin(relax_data_store.diff[self.run].theta)
            cos_theta = cos(relax_data_store.diff[self.run].theta)
            sin_phi = sin(relax_data_store.diff[self.run].phi)
            cos_phi = cos(relax_data_store.diff[self.run].phi)

            # Unit Dpar axis.
            Dpar[0] = sin_theta * cos_phi
            Dpar[1] = sin_theta * sin_phi
            Dpar[2] = cos_theta

            # Return the vector.
            return Dpar

        # Ellipsoid.
        if relax_data_store.diff[self.run].type == 'ellipsoid':
            # Initialise.
            Dx = zeros(3, Float64)
            Dy = zeros(3, Float64)
            Dz = zeros(3, Float64)

            # Trig.
            sin_alpha = sin(relax_data_store.diff[self.run].alpha)
            cos_alpha = cos(relax_data_store.diff[self.run].alpha)
            sin_beta = sin(relax_data_store.diff[self.run].beta)
            cos_beta = cos(relax_data_store.diff[self.run].beta)
            sin_gamma = sin(relax_data_store.diff[self.run].gamma)
            cos_gamma = cos(relax_data_store.diff[self.run].gamma)

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
