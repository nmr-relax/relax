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
            if match("^__", name):
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
            if match("^__", name):
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
                    if match("^__", name):
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


    def __getattr__(self, name):
        """Function for calculating the parameters, unit vectors, and tensors on the fly.

        All tensor types
        ================

        The equation for calculating Diso is

            Diso  =  1 / (6tm).


        Spherical diffusion
        ===================

        The diagonalised spherical diffusion tensor is defined as

                       | Diso     0     0 |
            tensor  =  |    0  Diso     0 |.
                       |    0     0  Diso |

        The rotation matrix required to shift from the diffusion tensor frame to the PDB frame is

                  | 1  0  0 |
            R  =  | 0  1  0 |.
                  | 0  0  1 |


        Spheroidal diffusion
        ====================

        The equations for the parameters Dper, Dpar, and Dratio are

            Dper  =  Diso - 1/3 Da,

            Dpar  =  Diso + 2/3 Da,

            Dratio  =  Dpar / Dper.

        The unit vector parallel to the unique axis of the diffusion tensor is

                          | sin(theta) * cos(phi) |
            Dpar_unit  =  | sin(theta) * sin(phi) |.
                          |      cos(theta)       |

        The diagonalised spheroidal diffusion tensor is defined as

                       | Dper     0     0 |
            tensor  =  |    0  Dper     0 |.
                       |    0     0  Dpar |

        The rotation matrix required to shift from the diffusion tensor frame to the PDB frame is
        equal to

                  |  cos(theta) * cos(phi)  -sin(phi)   sin(theta) * cos(phi) |
            R  =  |  cos(theta) * sin(phi)   cos(phi)   sin(theta) * sin(phi) |.
                  | -sin(theta)              0          cos(theta)            |


        Ellipsoidal diffusion
        =====================

        The equations for the parameters Dx, Dy, and Dz are

            Dx  =  Diso - 1/3 Da(1 + 3Dr),

            Dy  =  Diso - 1/3 Da(1 - 3Dr),

            Dz  =  Diso + 2/3 Da.

        The unit Dx vector is

                        | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
            Dx_unit  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |,
                        |                    cos(alpha) * sin(beta)                      |

        the unit Dy vector is

                        | cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
            Dy_unit  =  | cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |,
                        |                   sin(alpha) * sin(beta)                      |

        and the unit Dz vector is

                        | -sin(beta) * cos(gamma) |
            Dz_unit  =  |  sin(beta) * sin(gamma) |.
                        |        cos(beta)        |

        The diagonalised ellipsoidal diffusion tensor is defined as

                       | Dx   0   0 |
            tensor  =  |  0  Dy   0 |.
                       |  0   0  Dz |

        The rotation matrix required to shift from the diffusion tensor frame to the PDB frame is
        equal to

            R  =  | Dx_unit  Dy_unit  Dz_unit |,

                  | Dx_unit[0]  Dy_unit[0]  Dz_unit[0] |
               =  | Dx_unit[1]  Dy_unit[1]  Dz_unit[1] |.
                  | Dx_unit[2]  Dy_unit[2]  Dz_unit[2] |
        """

        # All tensor types.
        ###################

        # Diso.
        if name == 'Diso':
            return 1.0 / (6.0 * self.tm)


        # Spherical diffusion.
        ######################

        # The diffusion tensor.
        if (name == 'tensor_diag' or name == 'tensor') and self.type == 'sphere':
            # Initialise the tensor.
            tensor = zeros((3, 3), Float64)

            # Populate the diagonal elements.
            tensor[0, 0] = self.Diso
            tensor[1, 1] = self.Diso
            tensor[2, 2] = self.Diso

            # Return the tensor.
            return tensor

        # The rotation matrix.
        if name == 'rotation' and self.type == 'sphere':
            return identity(3, Float64)


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

        # Dpar unit vector.
        if name == 'Dpar_unit' and self.type == 'spheroid':
            # Initilise the vector.
            Dpar_unit = zeros(3, Float64)

            # Calculate the x, y, and z components.
            Dpar_unit[0] = sin(self.theta) * cos(self.phi)
            Dpar_unit[1] = sin(self.theta) * sin(self.phi)
            Dpar_unit[2] = cos(self.theta)

            # Return the unit vector.
            return Dpar_unit

        # The diffusion tensor (diagonalised).
        if name == 'tensor_diag' and self.type == 'spheroid':
            # Initialise the tensor.
            tensor = zeros((3, 3), Float64)

            # Populate the diagonal elements.
            tensor[0, 0] = self.Dper
            tensor[1, 1] = self.Dper
            tensor[2, 2] = self.Dpar

            # Return the tensor.
            return tensor

        # The diffusion tensor (within the structural frame).
        if name == 'tensor' and self.type == 'spheroid':
            # Rotation (R . tensor . R^T).
            R = self.rotation
            return dot(R, dot(self.tensor_diag, transpose(R)))

        # The rotation matrix.
        if name == 'rotation' and self.type == 'spheroid':
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

        # Dx unit vector.
        if name == 'Dx_unit' and self.type == 'ellipsoid':
            # Initilise the vector.
            Dx_unit = zeros(3, Float64)

            # Calculate the x, y, and z components.
            Dx_unit[0] = -sin(self.alpha) * sin(self.gamma)  +  cos(self.alpha) * cos(self.beta) * cos(self.gamma)
            Dx_unit[1] = -sin(self.alpha) * cos(self.gamma)  -  cos(self.alpha) * cos(self.beta) * sin(self.gamma)
            Dx_unit[2] = cos(self.alpha) * sin(self.beta)

            # Return the unit vector.
            return Dx_unit

        # Dy unit vector.
        if name == 'Dy_unit' and self.type == 'ellipsoid':
            # Initilise the vector.
            Dy_unit = zeros(3, Float64)

            # Calculate the x, y, and z components.
            Dy_unit[0] = cos(self.alpha) * sin(self.gamma)  +  sin(self.alpha) * cos(self.beta) * cos(self.gamma)
            Dy_unit[1] = cos(self.alpha) * cos(self.gamma)  -  sin(self.alpha) * cos(self.beta) * sin(self.gamma)
            Dy_unit[2] = sin(self.alpha) * sin(self.beta)

            # Return the unit vector.
            return Dy_unit

        # Dz unit vector.
        if name == 'Dz_unit' and self.type == 'ellipsoid':
            # Initilise the vector.
            Dz_unit = zeros(3, Float64)

            # Calculate the x, y, and z components.
            Dz_unit[0] = -sin(self.beta) * cos(self.gamma)
            Dz_unit[1] = sin(self.beta) * sin(self.gamma)
            Dz_unit[2] = cos(self.beta)

            # Return the unit vector.
            return Dz_unit


        # The diffusion tensor (diagonalised).
        if name == 'tensor_diag' and self.type == 'ellipsoid':
            # Initialise the tensor.
            tensor = zeros((3, 3), Float64)

            # Populate the diagonal elements.
            tensor[0, 0] = self.Dx
            tensor[1, 1] = self.Dy
            tensor[2, 2] = self.Dz

            # Return the tensor.
            return tensor

        # The diffusion tensor (within the structural frame).
        if name == 'tensor' and self.type == 'ellipsoid':
            # Rotation (R . tensor . R^T).
            R = self.rotation
            return dot(R, dot(self.tensor_diag, transpose(R)))

        # The rotation matrix.
        if name == 'rotation' and self.type == 'ellipsoid':
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

        # The attribute asked for does not exist.
        raise AttributeError, name



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
