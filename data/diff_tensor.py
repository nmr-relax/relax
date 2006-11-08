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


from types import ListType

from data_classes import Element, SpecificData
from diff_tensor_auto_objects import *



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
        self.tensor_diag = DiffAutoNumericObject(auto_object_tensor_diag, self)

        # The diffusion tensor (within the structural frame).
        self.tensor = DiffAutoNumericObject(auto_object_tensor, self)

        # The rotation matrix (diffusion frame to structural frame).
        self.rotation = DiffAutoNumericObject(auto_object_rotation, self)

        # The isotropic diffusion rate.
        #self.Diso = DiffAutoFloat(auto_object_tensor)
        self.Diso_sim = DiffAutoSimArrayObject(auto_object_Diso, self)


        # Automatically generated objects for spherical diffusion.
        ##########################################################

        # Eigenvalue parallel to the unique axis.
        self.Dpar_sim = DiffAutoSimArrayObject(auto_object_Dpar, self)

        # Eigenvalue perpendicular to the unique axis.
        self.Dper_sim = DiffAutoSimArrayObject(auto_object_Dper, self)

        # Unit vector parallel to the axis.
        self.Dpar_unit = DiffAutoNumericObject(auto_object_Dpar_unit, self)
        self.Dpar_unit_sim = DiffAutoSimArrayObject(auto_object_Dpar_unit, self)


        # Automatically generated objects for ellipsoidal diffusion.
        ############################################################

        # Eigenvalues Dx, Dy, and Dz.
        self.Dx_sim = DiffAutoSimArrayObject(auto_object_Dx, self)
        self.Dy_sim = DiffAutoSimArrayObject(auto_object_Dy, self)
        self.Dz_sim = DiffAutoSimArrayObject(auto_object_Dz, self)

        # Unit vectors parallel to the axes.
        self.Dx_unit = DiffAutoNumericObject(auto_object_Dx_unit, self)
        self.Dy_unit = DiffAutoNumericObject(auto_object_Dy_unit, self)
        self.Dz_unit = DiffAutoNumericObject(auto_object_Dz_unit, self)
        self.Dx_unit_sim = DiffAutoSimArrayObject(auto_object_Dx_unit, self)
        self.Dy_unit_sim = DiffAutoSimArrayObject(auto_object_Dy_unit, self)
        self.Dz_unit_sim = DiffAutoSimArrayObject(auto_object_Dz_unit, self)


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


# Automatic Numeric-like objects.
class DiffAutoNumericObject(ListType):
    def __init__(self, object, diff_data):
        """Class for implementing an automatically generated Numeric-like object."""

        # Function which returns the Numeric data structure (to be called at run-time).
        self.object = object

        # The local scope of the diffusion tensor data structure.
        self.diff_data = diff_data


    def __add__(self, x):
        """Function for the implementation of addition.

        @return:    The array plus x.
        @rtype:     array
        """

        return self.object(self.diff_data) + x


    def __getitem__(self, i):
        """Function for selecting individual elements of the array.

        @return:    Element i of the array.
        @rtype:     float
        """

        return self.object(self.diff_data)[i]


    def __iter__(self):
        """Function for looping over the array.

        @return:    An iterator object for looping over the array.
        @rtype:     iterator object
        """

        # Get the object.
        object = self.object(self.diff_data)

        # Return the iterator.
        if object != None:
            return iter(object)
        else:
            return iter([])


    def __len__(self):
        """Function to calculate the length of the array.

        @return:    The length of the array.
        @rtype:     int
        """

        return len(self.object(self.diff_data))


    def __mul__(self, x):
        """Function for the implementation of multiplication.

        @return:    The array multiplied by x.
        @rtype:     array
        """

        return self.object(self.diff_data) * x


    def __repr__(self):
        """Function for computing the 'official' string representation of the array.

        @return:    The string representation of the array.
        @rtype:     string
        """

        return `self.object(self.diff_data)`


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

        return self.object(self.diff_data, i)


    def __iter__(self):
        """Function for looping over the array.

        @return:    An iterator object for looping over the array.
        @rtype:     iterator object
        """

        # Get the object.
        object = self.create_array()

        # Return the iterator.
        if object != None:
            return iter(self.create_array())
        else:
            return iter([])


    def __len__(self):
        """Function to calculate the length of the array.

        @return:    The length of the array.
        @rtype:     int
        """

        if hasattr(self.diff_data, 'tm_sim'):
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

        # No simulations.
        if not hasattr(self.diff_data, 'tm_sim'):
            return

        # Initialise the array.
        array = []

        # Loop over the elements, appending the structure to the array.
        for i in xrange(len(self.diff_data.tm_sim)):
            array.append(self.object(self.diff_data, i))

        # Return the array.
        return array
