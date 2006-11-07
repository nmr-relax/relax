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


from LinearAlgebra import inverse
from math import cos, pi, sin
from Numeric import Float64, dot, identity, transpose, zeros
from re import match
from types import DictType, ListType


# Global data.
##############

class Data:
    def __init__(self):
        """Class containing all the program data."""

        # Fundamental constants.
        #self.h = 6.6260755e-34    # Old low precision value.
        self.h = 6.62606876e-34
        self.h_bar = self.h / ( 2.0*pi )
        self.mu0 = 4.0 * pi * 1e-7

        # PDB data.
        self.pdb = SpecificData()

        # Diffusion data.
        self.diff = DiffTensorData()

        # The residue specific data.
        self.res = Residue()

        # The name of the runs.
        self.run_names = []

        # The type of the runs.
        self.run_types = []

        # Hybrid models.
        self.hybrid_runs = {}

        # Global minimisation statistics.
        self.chi2 = {}
        self.iter = {}
        self.f_count = {}
        self.g_count = {}
        self.h_count = {}
        self.warning = {}


    def __repr__(self):
        text = "The data class containing all permanent program data.\n"
        text = text + "The class contains the following objects:\n"
        for name in dir(self):
            if match("^_", name):
                continue
            text = text + "  " + name + ", " + `type(getattr(self, name))` + "\n"
        return text



# Empty data container.
#######################

class Element:
    def __init__(self):
        """Empty data container."""


    def __repr__(self):
        # Header.
        text = "%-25s%-100s\n\n" % ("Data structure", "Value")

        # Data structures.
        for name in dir(self):
            if match("^_", name):
                continue
            text = text + "%-25s%-100s\n" % (name, `getattr(self, name)`)

        # Return the lot.
        return text


# Specific data class.
######################

class SpecificData(DictType):
    def __init__(self):
        """Dictionary type class for specific data."""


    def __repr__(self):
        text = "Data:\n"
        if len(self) == 0:
            text = text + "  {}\n"
        else:
            i = 0
            for key in self.keys():
                if i == 0:
                    text = text + "  { "
                else:
                    text = text + "  , "
                text = text + "Key " + `key` + ":\n"
                for name in dir(self[key]):
                    if match("^_", name):
                        continue
                    text = text + "    " + name + ", " + `type(getattr(self[key], name))` + "\n"
                i = i + 1
            text = text + "  }\n"

        return text


    def add_item(self, key):
        """Function for adding an empty container to the dictionary."""

        self[key] = Element()



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

        # Automatically generated objects for all tensor types.
        #######################################################

        # The diagonalised diffusion tensor (within the diffusion frame).
        self.tensor_diag = DiffAutoNumericObject(self._auto_object_tensor_diag)

        # The diffusion tensor (within the structural frame).
        self.tensor = DiffAutoNumericObject(self._auto_object_tensor)

        # The rotation matrix (diffusion frame to structural frame).
        self.rotation = DiffAutoNumericObject(self._auto_object_rotation)

        # The isotropic diffusion rate.
        #self.Diso = DiffAutoFloat(self._auto_object_tensor)
        self.Diso_sim = DiffAutoSimArrayObject(self._auto_object_Diso, self)


        # Automatically generated objects for spherical diffusion.
        ##########################################################

        # Eigenvalue parallel to the unique axis.
        self.Dpar_sim = DiffAutoSimArrayObject(self._auto_object_Dpar, self)

        # Eigenvalue perpendicular to the unique axis.
        self.Dper_sim = DiffAutoSimArrayObject(self._auto_object_Dper, self)

        # Unit vector parallel to the axis.
        self.Dpar_unit = DiffAutoNumericObject(self._auto_object_Dpar_unit)
        self.Dpar_unit_sim = DiffAutoSimArrayObject(self._auto_object_Dpar_unit, self)


        # Automatically generated objects for ellipsoidal diffusion.
        ############################################################

        # Eigenvalues Dx, Dy, and Dz.
        self.Dx_sim = DiffAutoSimArrayObject(self._auto_object_Dx, self)
        self.Dy_sim = DiffAutoSimArrayObject(self._auto_object_Dy, self)
        self.Dz_sim = DiffAutoSimArrayObject(self._auto_object_Dz, self)

        # Unit vectors parallel to the axes.
        self.Dx_unit = DiffAutoNumericObject(self._auto_object_Dx_unit)
        self.Dy_unit = DiffAutoNumericObject(self._auto_object_Dy_unit)
        self.Dz_unit = DiffAutoNumericObject(self._auto_object_Dz_unit)
        self.Dx_unit_sim = DiffAutoSimArrayObject(self._auto_object_Dx_unit, self)
        self.Dy_unit_sim = DiffAutoSimArrayObject(self._auto_object_Dy_unit, self)
        self.Dz_unit_sim = DiffAutoSimArrayObject(self._auto_object_Dz_unit, self)


    def __getattr__(self, name):
        """Function for calculating the parameters, unit vectors, and tensors on the fly.

        All tensor types
        ================

        The equation for calculating Diso is

            Diso  =  1 / (6tm).


        Spheroidal diffusion
        ====================

        The equations for the parameters Dper, Dpar, and Dratio are

            Dper  =  Diso - 1/3 Da,

            Dpar  =  Diso + 2/3 Da,

            Dratio  =  Dpar / Dper.


        Ellipsoidal diffusion
        =====================

        The equations for the parameters Dx, Dy, and Dz are

            Dx  =  Diso - 1/3 Da(1 + 3Dr),

            Dy  =  Diso - 1/3 Da(1 - 3Dr),

            Dz  =  Diso + 2/3 Da.


        """

        # All tensor types.
        ###################

        # Diso.
        if name == 'Diso':
            return 1.0 / (6.0 * self.tm)


        # Spheroidal diffusion.
        #######################

        # Dper.
        if name == 'Dper' and self.type == 'spheroid':
            return self.Diso - 1.0/3.0 * self.Da

        # Dpar.
        if name == 'Dpar' and self.type == 'spheroid':
            return self.Diso + 2.0/3.0 * self.Da

        # Dratio.
        if name == 'Dratio' and self.type == 'spheroid':
            return self.Dpar / self.Dper


        # Ellipsoidal diffusion.
        ########################

        # Dx.
        if name == 'Dx' and self.type == 'ellipsoid':
            return self.Diso - 1.0/3.0 * self.Da * (1.0 + 3.0*self.Dr)

        # Dy.
        if name == 'Dy' and self.type == 'ellipsoid':
            return self.Diso - 1.0/3.0 * self.Da * (1.0 - 3.0*self.Dr)

        # Dz.
        if name == 'Dz' and self.type == 'ellipsoid':
            return self.Diso + 2.0/3.0 * self.Da

        # The attribute asked for does not exist.
        raise AttributeError, name


    def _auto_object_Diso(self, i=None):
        """Function for automatically calculating the Diso value for simulation i.

        @return:    The Diso value for Monte Carlo simulation i.
        @rtype:     float
        """

        # Diso value for simulation i.
        return 1.0 / (6.0 * self.tm_sim[i])


    def _auto_object_Dpar(self, i=None):
        """Function for automatically calculating the Dpar value.

        @return:    The Dpar value for Monte Carlo simulation i.
        @rtype:     float
        """

        # Dpar value for simulation i (only generate the object if the diffusion is spheroidal).
        if self.type == 'spheroid':
            return self.Diso_sim[i] + 2.0/3.0 * self.Da_sim[i]


    def _auto_object_Dpar_unit(self, i=None):
        """Function for automatically calculating the Dpar unit vector.

        The unit vector parallel to the unique axis of the diffusion tensor is

                          | sin(theta) * cos(phi) |
            Dpar_unit  =  | sin(theta) * sin(phi) |.
                          |      cos(theta)       |

        If the argument 'i' is supplied, then the Dpar unit vector for Monte Carlo simulation i is
        returned instead.

        @return:    The Dpar unit vector.
        @rtype:     array (Float64)
        """

        # Only calculate the array if diffusion is spheroidal.
        if self.type == 'spheroid':
            # Determine which angles to use.
            if i == None:
                theta = self.theta
                phi = self.phi
            else:
                theta = self.theta_sim[i]
                phi = self.phi_sim[i]

            # Initilise the vector.
            Dpar_unit = zeros(3, Float64)

            # Calculate the x, y, and z components.
            Dpar_unit[0] = sin(theta) * cos(phi)
            Dpar_unit[1] = sin(theta) * sin(phi)
            Dpar_unit[2] = cos(theta)

            # Return the unit vector.
            return Dpar_unit


    def _auto_object_Dper(self, i=None):
        """Function for automatically calculating the Dper value.

        @return:    The Dper value for Monte Carlo simulation i.
        @rtype:     float
        """

        # Dper value for simulation i (only generate the object if the diffusion is spheroidal).
        if self.type == 'spheroid':
            return self.Diso_sim[i] - 1.0/3.0 * self.Da_sim[i]


    def _auto_object_Dx(self, i=None):
        """Function for automatically calculating the Dx value.

        @return:    The Dx value for Monte Carlo simulation i.
        @rtype:     float
        """

        # Dx value for simulation i (only generate the object if the diffusion is ellipsoidal).
        if self.type == 'ellipsoid':
            return self.Diso_sim[i] - 1.0/3.0 * self.Da_sim[i] * (1.0 + 3.0*self.Dr_sim[i])


    def _auto_object_Dx_unit(self, i=None):
        """Function for automatically calculating the Dx unit vector.

        The unit Dx vector is

                        | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
            Dx_unit  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |.
                        |                    cos(alpha) * sin(beta)                      |

        If the argument 'i' is supplied, then the Dx unit vector for Monte Carlo simulation i is
        returned instead.

        @return:    The Dx unit vector.
        @rtype:     array (Float64)
        """

        # Only calculate the array if diffusion is ellipsoidal.
        if self.type == 'ellipsoid':
            # Determine which angles to use.
            if i == None:
                alpha = self.alpha
                beta = self.beta
                gamma = self.gamma
            else:
                alpha = self.alpha_sim[i]
                beta = self.beta_sim[i]
                gamma = self.gamma_sim[i]

            # Initilise the vector.
            Dx_unit = zeros(3, Float64)

            # Calculate the x, y, and z components.
            Dx_unit[0] = -sin(alpha) * sin(gamma)  +  cos(alpha) * cos(beta) * cos(gamma)
            Dx_unit[1] = -sin(alpha) * cos(gamma)  -  cos(alpha) * cos(beta) * sin(gamma)
            Dx_unit[2] = cos(alpha) * sin(beta)

            # Return the unit vector.
            return Dx_unit


    def _auto_object_Dy(self, i=None):
        """Function for automatically calculating the Dy value.

        @return:    The Dy value for Monte Carlo simulation i.
        @rtype:     float
        """

        # Dy value for simulation i (only generate the object if the diffusion is ellipsoidal).
        if self.type == 'ellipsoid':
            return self.Diso_sim[i] - 1.0/3.0 * self.Da_sim[i] * (1.0 - 3.0*self.Dr_sim[i])


    def _auto_object_Dy_unit(self, i=None):
        """Function for automatically calculating the Dy unit vector.

        The unit Dy vector is

                        | cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
            Dy_unit  =  | cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |.
                        |                   sin(alpha) * sin(beta)                      |

        If the argument 'i' is supplied, then the Dy unit vector for Monte Carlo simulation i is
        returned instead.

        @return:    The Dy unit vector.
        @rtype:     array (Float64)
        """

        # Only calculate the array if diffusion is ellipsoidal.
        if self.type == 'ellipsoid':
            # Determine which angles to use.
            if i == None:
                alpha = self.alpha
                beta = self.beta
                gamma = self.gamma
            else:
                alpha = self.alpha_sim[i]
                beta = self.beta_sim[i]
                gamma = self.gamma_sim[i]

            # Initilise the vector.
            Dy_unit = zeros(3, Float64)

            # Calculate the x, y, and z components.
            Dy_unit[0] = cos(alpha) * sin(gamma)  +  sin(alpha) * cos(beta) * cos(gamma)
            Dy_unit[1] = cos(alpha) * cos(gamma)  -  sin(alpha) * cos(beta) * sin(gamma)
            Dy_unit[2] = sin(alpha) * sin(beta)

            # Return the unit vector.
            return Dy_unit


    def _auto_object_Dz(self, i=None):
        """Function for automatically calculating the Dz value.

        @return:    The Dz value for Monte Carlo simulation i.
        @rtype:     float
        """

        # Dz value for simulation i (only generate the object if the diffusion is ellipsoidal).
        if self.type == 'ellipsoid':
            return self.Diso_sim[i] - 1.0/3.0 * self.Da_sim[i] * (1.0 - 3.0*self.Dr_sim[i])


    def _auto_object_Dz_unit(self, i=None):
        """Function for automatically calculating the Dz unit vector.

        The unit Dz vector is

                        | -sin(beta) * cos(gamma) |
            Dz_unit  =  |  sin(beta) * sin(gamma) |.
                        |        cos(beta)        |

        If the argument 'i' is supplied, then the Dz unit vector for Monte Carlo simulation i is
        returned instead.

        @return:    The Dz unit vector.
        @rtype:     array (Float64)
        """

        # Only calculate the array if diffusion is ellipsoidal.
        if self.type == 'ellipsoid':
            # Determine which angles to use.
            if i == None:
                alpha = self.alpha
                beta = self.beta
                gamma = self.gamma
            else:
                alpha = self.alpha_sim[i]
                beta = self.beta_sim[i]
                gamma = self.gamma_sim[i]

            # Initilise the vector.
            Dz_unit = zeros(3, Float64)

            # Calculate the x, y, and z components.
            Dz_unit[0] = -sin(beta) * cos(gamma)
            Dz_unit[1] = sin(beta) * sin(gamma)
            Dz_unit[2] = cos(beta)

            # Return the unit vector.
            return Dz_unit


    def _auto_object_rotation(self, i=None):
        """Function for automatically calculating the rotation matrix.

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

        @return:    The rotation matrix.
        @rtype:     matrix (Float64)
        """

        # The rotation matrix for the sphere.
        if self.type == 'sphere':
            return identity(3, Float64)

        # The rotation matrix for the spheroid.
        elif self.type == 'spheroid':
            # Initialise the rotation matrix.
            rotation = identity(3, Float64)

            # First row of the rotation matrix.
            rotation[0, 0] = cos(self.theta) * cos(self.phi)
            rotation[1, 0] = cos(self.theta) * sin(self.phi)
            rotation[2, 0] = -sin(self.theta)

            # Second row of the rotation matrix.
            rotation[0, 1] = -sin(self.phi)
            rotation[1, 1] = cos(self.phi)

            # Replace the last row of the rotation matrix with the Dpar unit vector.
            rotation[:, 2] = self.Dpar_unit

            # Return the tensor.
            return rotation

        # The rotation matrix for the ellipsoid.
        elif self.type == 'ellipsoid':
            # Initialise the rotation matrix.
            rotation = identity(3, Float64)

            # First column of the rotation matrix.
            rotation[:, 0] = self.Dx_unit

            # Second column of the rotation matrix.
            rotation[:, 1] = self.Dy_unit

            # Third column of the rotation matrix.
            rotation[:, 2] = self.Dz_unit

            # Return the tensor.
            return rotation



    def _auto_object_tensor(self, i=None):
        """Function for automatically calculating the diffusion tensor (in the structural frame).

        The diffusion tensor is calculated using the diagonalised tensor and the rotation matrix
        through the equation

            R . tensor_diag . R^T.

        @return:    The diffusion tensor (within the structural frame).
        @rtype:     matrix (Float64)
        """

        # Alias the rotation matrix.
        R = self.rotation

        # Rotation (R . tensor_diag . R^T).
        return dot(R, dot(self.tensor_diag, transpose(R)))


    def _auto_object_tensor_diag(self, i=None):
        """Function for automatically calculating the diagonalised diffusion tensor.

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

        @return:    The diagonalised diffusion tensor.
        @rtype:     matrix (Float64)
        """

        # Spherical diffusion tensor.
        if self.type == 'sphere':
            # Initialise the tensor.
            tensor = zeros((3, 3), Float64)

            # Populate the diagonal elements.
            tensor[0, 0] = self.Diso
            tensor[1, 1] = self.Diso
            tensor[2, 2] = self.Diso

            # Return the tensor.
            return tensor

        # Spheroidal diffusion tensor.
        elif self.type == 'spheroid':
            # Initialise the tensor.
            tensor = zeros((3, 3), Float64)

            # Populate the diagonal elements.
            tensor[0, 0] = self.Dper
            tensor[1, 1] = self.Dper
            tensor[2, 2] = self.Dpar

            # Return the tensor.
            return tensor

        # Ellipsoidal diffusion tensor.
        elif self.type == 'ellipsoid':
            # Initialise the tensor.
            tensor = zeros((3, 3), Float64)

            # Populate the diagonal elements.
            tensor[0, 0] = self.Dx
            tensor[1, 1] = self.Dy
            tensor[2, 2] = self.Dz

            # Return the tensor.
            return tensor


# Automatic Numeric-like objects.
class DiffAutoNumericObject(ListType):
    def __init__(self, object):
        """Class for implementing an automatically generated Numeric-like object."""

        # Function which returns the Numeric data structure (to be called at run-time).
        self.object = object


    def __add__(self, x):
        """Function for the implementation of addition.

        @return:    The array plus x.
        @rtype:     array
        """

        return self.object() + x


    def __getitem__(self, i):
        """Function for selecting individual elements of the array.

        @return:    Element i of the array.
        @rtype:     float
        """

        return self.object()[i]


    def __iter__(self):
        """Function for looping over the array.

        @return:    An iterator object for looping over the array.
        @rtype:     iterator object
        """

        return iter(self.object())


    def __len__(self):
        """Function to calculate the length of the array.

        @return:    The length of the array.
        @rtype:     int
        """

        return len(self.object())


    def __mul__(self, x):
        """Function for the implementation of multiplication.

        @return:    The array multiplied by x.
        @rtype:     array
        """

        return self.object() * x


    def __repr__(self):
        """Function for computing the 'official' string representation of the array.

        @return:    The string representation of the array.
        @rtype:     string
        """

        return `self.object()`


    def __setitem__(self, key, value):
        """Disallow modifications to the array.

        @raise:     RelaxError.
        """

        raise RelaxError, "This object cannot be modified!"



# Automatic array-like objects for the Monte Carlo simulations.
class DiffAutoSimArrayObject(ListType):
    def __init__(self, object, diff_data):
        """Class for implementing an automatically generated array-like object for the MC sims."""

        # Function which returns the Numeric data structure (to be called at run-time).
        self.object = object

        # The local scope of the diffusion tensor data structure.
        self.diff_data = diff_data


    def __add__(self, x):
        """Disallow addition.

        @raise:     RelaxError.
        """

        raise RelaxError, "Addition is not allowed."


    def __getitem__(self, i):
        """Function for selecting individual elements of the array.

        @return:    Element i of the array.
        @rtype:     float
        """

        return self.object(i)


    def __iter__(self):
        """Function for looping over the array.

        @return:    An iterator object for looping over the array.
        @rtype:     iterator object
        """

        return iter(self.create_array())


    def __len__(self):
        """Function to calculate the length of the array.

        @return:    The length of the array.
        @rtype:     int
        """

        return len(self.diff_data.tm_sim)


    def __mul__(self, x):
        """Disallow multiplication.

        @raise:     RelaxError.
        """

        raise RelaxError, "Multiplication is not allowed."


    def __repr__(self):
        """Function for computing the 'official' string representation of the array.

        @return:    The string representation of the array.
        @rtype:     string
        """

        return `self.create_array()`


    def __setitem__(self, key, value):
        """Disallow modifications to the array.

        @raise:     RelaxError.
        """

        raise RelaxError, "This object cannot be modified!"


    def create_array(self):
        """Generate the array.

        @return:    The array of objects.
        @rtype:     list
        """

        # Initialise the array.
        array = []

        # Loop over the elements, appending the structure to the array.
        for i in xrange(len(self.diff_data.tm_sim)):
            array.append(self.object(i))

        # Return the array.
        return array




# Residue specific data.
########################

class Residue(DictType):
    def __init__(self):
        """Class containing all the residue specific data."""


    def __repr__(self):
        text = "Class containing all the residue specific data.\n\n"

        # Empty.
        if not len(self):
            text = text + "The class contains no data.\n"

        # Not empty.
        else:
            text = text + "The residue container contains the following keys:\n"
            for key in self:
                text = text + "    " + `key` + "\n"
            text = text + "\nThese can be accessed by typing 'self.relax.data.res[key]'.\n"

        return text


    def add_list(self, key):
        """Function for adding an empty container to the dictionary."""

        self[key] = ResidueList()


class ResidueList(ListType):
    def __init__(self):
        """Empty data container for residue specific data."""


    def __repr__(self):
        text = "Sequence data.\n\n"
        text = text + "%-8s%-8s%-8s%-10s" % ("Index", "Number", "Name", "Selected") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8i%-8s%-10i" % (i, self[i].num, self[i].name, self[i].select) + "\n"
        text = text + "\nThese can be accessed by typing 'self.relax.data.res[key][index]'.\n"
        return text


    def add_item(self):
        """Function for appending an empty container to the list."""

        self.append(Element())
