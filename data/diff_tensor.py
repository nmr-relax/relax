###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2006 Edward d'Auvergne                            #
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


from math import cos, sin
from Numeric import Float64, dot, identity, transpose, zeros
from re import search
from types import ListType

from data_classes import Element, SpecificData



# Diffusion tensor specific data.
#################################

class DiffTensorData(SpecificData):
    def __init__(self):
        """Dictionary type class for the diffusion tensor data.

        The non-default diffusion parameters are calculated on the fly.
        """


    def add_item(self, key):
        """Function for adding an empty container to the dictionary.

        This overwrites the function from the parent class SpecificData.
        """

        self[key] = DiffTensorElement()



class DiffTensorElement(Element):
    def __init__(self):
        """An empty data container for the diffusion tensor elements."""

        # Set the initial diffusion type to None.
        self.type = None


    def __setattr__(self, name, value):
        """Function for calculating the parameters, unit vectors, and tensors on the fly.

        The equations for the parameters Dper, Dpar, and Dratio are

            Dratio  =  Dpar / Dper.
        """

        ######################
        # Set the attribute. #
        ######################

        # Get the base parameter name and determine the object category ('val', 'err', or 'sim').
        if search('_err$', name):
            category = 'err'
            base_name = name[:-4]
        elif search('_sim$', name):
            category = 'sim'
            base_name = name[:-4]
        else:
            category = 'val'
            base_name = name

        # List of modifiable attributes.
        mod_attr = ['type',
                    'fixed',
                    'spheroid_type',
                    'tm',
                    'Da',
                    'Dr',
                    'theta',
                    'phi',
                    'alpha',
                    'beta',
                    'gamma']

        # Test if the attribute that is trying to be set is modifiable.
        if not base_name in mod_attr:
            raise RelaxError, "The object " + `name` + " is not modifiable."

        # Set the attribute normally.
        self.__dict__[name] = value

        # Skip the updating process for certain objects.
        if name in ['type', 'fixed', 'spheroid_type']:
            return


        ###############################
        # Update the data structures. #
        ###############################


        # Objects for all tensor types.
        ###############################

        # The isotropic diffusion rate Diso.
        self._update_object(base_name, target='Diso', update_if_set=['tm'], depends=['tm'], category=category)


        # Spherical diffusion.
        ######################

        if self.type == 'sphere':
            # Update the diagonalised diffusion tensor (within the diffusion frame).
            self._update_object(base_name, target='tensor_diag', update_if_set=['tm'], depends=['Diso'], category=category)

            # The rotation matrix (diffusion frame to structural frame).
            self._update_object(base_name, target='rotation', update_if_set=['tm'], depends=[], category=category)

            # The diffusion tensor (within the structural frame).
            self._update_object(base_name, target='tensor', update_if_set=['tm'], depends=['rotation', 'tensor_diag'], category=category)


        # Spheroidal diffusion.
        #######################

        elif self.type == 'spheroid':
            # Update Dpar, Dper, and Dratio.
            self._update_object(base_name, target='Dpar', update_if_set=['tm', 'Da'], depends=['Diso', 'Da'], category=category)
            self._update_object(base_name, target='Dper', update_if_set=['tm', 'Da'], depends=['Diso', 'Da'], category=category)
            self._update_object(base_name, target='Dratio', update_if_set=['tm', 'Da'], depends=['Dpar', 'Dper'], category=category)

            # Update the unit vector parallel to the axis.
            self._update_object(base_name, target='Dpar_unit', update_if_set=['theta', 'phi'], depends=['theta', 'phi'], category=category)

            # Update the diagonalised diffusion tensor (within the diffusion frame).
            self._update_object(base_name, target='tensor_diag', update_if_set=['tm', 'Da'], depends=['Dpar', 'Dper'], category=category)

            # The rotation matrix (diffusion frame to structural frame).
            self._update_object(base_name, target='rotation', update_if_set=['theta', 'phi'], depends=['theta', 'phi', 'Dpar_unit'], category=category)

            # The diffusion tensor (within the structural frame).
            self._update_object(base_name, target='tensor', update_if_set=['tm', 'Da', 'theta', 'phi'], depends=['rotation', 'tensor_diag'], category=category)


        # Ellipsoidal diffusion.
        ########################

        elif self.type == 'ellipsoid':
            # Update Dx, Dy, and Dz.
            self._update_object(base_name, target='Dx', update_if_set=['tm', 'Da', 'Dr'], depends=['Diso', 'Da', 'Dr'], category=category)
            self._update_object(base_name, target='Dy', update_if_set=['tm', 'Da', 'Dr'], depends=['Diso', 'Da', 'Dr'], category=category)
            self._update_object(base_name, target='Dz', update_if_set=['tm', 'Da'], depends=['Diso', 'Da'], category=category)

            # Update the unit vectors parallel to the axes.
            self._update_object(base_name, target='Dx_unit', update_if_set=['alpha', 'beta', 'gamma'], depends=['alpha', 'beta', 'gamma'], category=category)
            self._update_object(base_name, target='Dy_unit', update_if_set=['alpha', 'beta', 'gamma'], depends=['alpha', 'beta', 'gamma'], category=category)
            self._update_object(base_name, target='Dz_unit', update_if_set=['beta', 'gamma'], depends=['beta', 'gamma'], category=category)

            # Update the diagonalised diffusion tensor (within the diffusion frame).
            self._update_object(base_name, target='tensor_diag', update_if_set=['tm', 'Da', 'Dr'], depends=['Dx', 'Dy', 'Dz'], category=category)

            # The rotation matrix (diffusion frame to structural frame).
            self._update_object(base_name, target='rotation', update_if_set=['alpha', 'beta', 'gamma'], depends=['Dx_unit', 'Dy_unit', 'Dz_unit'], category=category)

            # The diffusion tensor (within the structural frame).
            self._update_object(base_name, target='tensor', update_if_set=['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma'], depends=['rotation', 'tensor_diag'], category=category)


    def _calc_Diso(self, tm=None):
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


    def _calc_Dpar(self, Diso=None, Da=None):
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


    def _calc_Dpar_unit(self, theta=None, phi=None):
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


    def _calc_Dper(self, Diso=None, Da=None):
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


    def _calc_Dratio(self, Dpar=None, Dper=None):
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


    def _calc_Dx(self, Diso=None, Da=None, Dr=None):
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


    def _calc_Dx_unit(self, alpha=None, beta=None, gamma=None):
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


    def _calc_Dy(self, Diso=None, Da=None, Dr=None):
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


    def _calc_Dy_unit(self, alpha=None, beta=None, gamma=None):
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


    def _calc_Dz(self, Diso=None, Da=None):
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


    def _calc_Dz_unit(self, beta=None, gamma=None):
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


    def _calc_rotation(self, *args):
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
        if self.type == 'sphere':
            return identity(3, Float64)

        # The rotation matrix for the spheroid.
        elif self.type == 'spheroid':
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
        elif self.type == 'ellipsoid':
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


    def _calc_tensor(self, rotation=None, tensor_diag=None):
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


    def _calc_tensor_diag(self, *args):
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
        if self.type == 'sphere':
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
        elif self.type == 'spheroid':
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
        elif self.type == 'ellipsoid':
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


    def _update_object(self, base_name, target, update_if_set, depends, category):
        """Function for updating the target object, its error, and the MC simulations.

        If the base name of the object is not within the 'update_if_set' list, this function returns
        without doing anything (to avoid wasting time).  Dependant upon the category the object
        (target), its error (target+'_err'), or all Monte Carlo simulations (target+'_sim') are
        updated.

        @param base_name:       The parameter name which is being set in the __setattr__() function.
        @type base_name:        str
        @param target:          The name of the object to update.
        @type target:           str
        @param update_if_set:   If the parameter being set by the __setattr__() function is not
            within this list of parameters, don't waste time updating the
            target.
        @param depends:         An array of names objects that the target is dependant upon.
        @type depends:          array of str
        @param category:        The category of the object to update (one of 'val', 'err', or
            'sim').
        @type category:         str
        @return:                None
        """

        # Only update if the parameter name is within the 'update_if_set' list.
        if not base_name in update_if_set:
            return

        # Get the function for calculating the value.
        fn = getattr(self, '_calc_'+target)


        # The value.
        ############

        if category == 'val':
            # Get all the dependancies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Test if the object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

                # Get the object and place it into the 'deps' tuple.
                deps = deps+(getattr(self, dep_name),)

            # Only update the object if its dependancies exist.
            if not missing_dep:
                # Calculate the value.
                value = fn(*deps)

                # Set the attribute.
                self.__dict__[target] = value


        # The error.
        ############

        if category == 'err':
            # Get all the dependancies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Test if the error object exists.
                if not hasattr(self, dep_name+'_err'):
                    missing_dep = 1
                    break

                # Get the object and place it into the 'deps' tuple.
                deps = deps+(getattr(self, dep_name+'_err'),)

            # Only update the error object if its dependancies exist.
            if not missing_dep:
                # Calculate the value.
                value = fn(*deps)

                # Set the attribute.
                self.__dict__[target+'_err'] = value


        # The Monte Carlo simulations.
        ##############################

        if category == 'sim':
            # Get all the dependancies if possible.
            missing_dep = 0
            deps = []
            for dep_name in depends:
                # Test if the error object exists.
                if not hasattr(self, dep_name+'_sim'):
                    missing_dep = 1
                    break

                # Get the object and place it into the 'deps' array.
                deps.append(getattr(self, dep_name+'_sim'))

            # The number of simulations.
            if deps:
                num_sim = len(deps[0])
            else:
                num_sim = len(getattr(self, update_if_set[0]+'_sim'))

            # Only update the MC simulation object if its dependancies exist.
            if not missing_dep:
                # Initialise an empty array to store the MC simulation object elements.
                sim_values = []

                # Loop over the simulations.
                for i in xrange(num_sim):
                    # Create a tuple of the dependancies.
                    deps_tuple = ()
                    for dep in deps:
                        deps_tuple = deps_tuple+(dep[i],)

                    # Calculate the value.
                    sim_values.append(fn(*deps_tuple))

                # Set the attribute.
                self.__dict__[target+'_sim'] = sim_values
