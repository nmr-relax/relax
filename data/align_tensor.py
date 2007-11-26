###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2007 Edward d'Auvergne                        #
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
from re import search
from math import cos, sin
from Numeric import Float64, dot, identity, transpose, zeros
from types import ListType

# relax module imports.
from data_classes import Element
from relax_errors import RelaxError



def calc_Axxyy(Axx, Ayy):
    """Function for calculating the Axx-yy value.

    The equation for calculating the parameter is

        Axx-yy  =  Axx - Ayy.

    @param Axx:     The Axx component of the tensor.
    @type Axx:      float
    @param Ayy:     The Ayy component of the tensor.
    @type Ayy:      float
    @return:        The Axx-yy component of the tensor.
    @rtype:         float
    """

    # Calculate and return the Axx-yy value.
    return Axx - Ayy


def calc_Azz(Axx, Ayy):
    """Function for calculating the Azz value.

    The equation for calculating the parameter is

        Azz  =  1 - Axx - Ayy.

    @param Axx:     The Axx component of the tensor.
    @type Axx:      float
    @param Ayy:     The Ayy component of the tensor.
    @type Ayy:      float
    @return:        The Azz component of the tensor.
    @rtype:         float
    """

    # Calculate and return the Azz value.
    return 1.0 - Axx - Ayy


def calc_Axx_unit(alpha, beta, gamma):
    """Function for calculating the Axx unit vector.

    The unit Axx vector is

                     | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
        Axx_unit  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |.
                     |                    cos(alpha) * sin(beta)                      |

    @param alpha:   The Euler angle alpha in radians using the z-y-z convention.
    @type alpha:    float
    @param beta:    The Euler angle beta in radians using the z-y-z convention.
    @type beta:     float
    @param gamma:   The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:    float
    @return:        The Axx unit vector.
    @rtype:         Numeric array (Float64)
    """

    # Initilise the vector.
    Axx_unit = zeros(3, Float64)

    # Calculate the x, y, and z components.
    Axx_unit[0] = -sin(alpha) * sin(gamma)  +  cos(alpha) * cos(beta) * cos(gamma)
    Axx_unit[1] = -sin(alpha) * cos(gamma)  -  cos(alpha) * cos(beta) * sin(gamma)
    Axx_unit[2] = cos(alpha) * sin(beta)

    # Return the unit vector.
    return Axx_unit


def calc_Ayy_unit(alpha, beta, gamma):
    """Function for calculating the Ayy unit vector.

    The unit Ayy vector is

                     | cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
        Ayy_unit  =  | cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |.
                     |                   sin(alpha) * sin(beta)                      |

    @param alpha:   The Euler angle alpha in radians using the z-y-z convention.
    @type alpha:    float
    @param beta:    The Euler angle beta in radians using the z-y-z convention.
    @type beta:     float
    @param gamma:   The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:    float
    @return:        The Ayy unit vector.
    @rtype:         Numeric array (Float64)
    """

    # Initilise the vector.
    Ayy_unit = zeros(3, Float64)

    # Calculate the x, y, and z components.
    Ayy_unit[0] = cos(alpha) * sin(gamma)  +  sin(alpha) * cos(beta) * cos(gamma)
    Ayy_unit[1] = cos(alpha) * cos(gamma)  -  sin(alpha) * cos(beta) * sin(gamma)
    Ayy_unit[2] = sin(alpha) * sin(beta)

    # Return the unit vector.
    return Ayy_unit


def calc_Azz_unit(beta, gamma):
    """Function for calculating the Azz unit vector.

    The unit Azz vector is

                     | -sin(beta) * cos(gamma) |
        Azz_unit  =  |  sin(beta) * sin(gamma) |.
                     |        cos(beta)        |

    @param beta:    The Euler angle beta in radians using the z-y-z convention.
    @type beta:     float
    @param gamma:   The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:    float
    @return:        The Azz unit vector.
    @rtype:         Numeric array (Float64)
    """

    # Initilise the vector.
    Azz_unit = zeros(3, Float64)

    # Calculate the x, y, and z components.
    Azz_unit[0] = -sin(beta) * cos(gamma)
    Azz_unit[1] = sin(beta) * sin(gamma)
    Azz_unit[2] = cos(beta)

    # Return the unit vector.
    return Azz_unit


def calc_rotation(Axx_unit, Ayy_unit, Azz_unit):
    """Function for calculating the rotation matrix.

    The rotation matrix required to shift from the align tensor frame to the structural
    frame is equal to

        R  =  | Axx_unit  Ayy_unit  Azz_unit |,

              | Axx_unit[0]  Ayy_unit[0]  Azz_unit[0] |
           =  | Axx_unit[1]  Ayy_unit[1]  Azz_unit[1] |.
              | Axx_unit[2]  Ayy_unit[2]  Azz_unit[2] |

    @param Axx_unit:    The Axx unit vector.
    @type Axx_unit:     Numeric array (Float64)
    @param Ayy_unit:    The Ayy unit vector.
    @type Ayy_unit:     Numeric array (Float64)
    @param Azz_unit:    The Azz unit vector.
    @type Azz_unit:     Numeric array (Float64)
    @return:            The rotation matrix.
    @rtype:             Numeric array ((3, 3), Float64)
    """

    # Initialise the rotation matrix.
    rotation = identity(3, Float64)

    # First column of the rotation matrix.
    rotation[:, 0] = Axx_unit

    # Second column of the rotation matrix.
    rotation[:, 1] = Ayy_unit

    # Third column of the rotation matrix.
    rotation[:, 2] = Azz_unit

    # Return the tensor.
    return rotation


def calc_tensor(rotation, tensor_diag):
    """Function for calculating the alignment tensor (in the structural frame).

    The alignment tensor is calculated using the diagonalised tensor and the rotation matrix
    through the equation

        R . tensor_diag . R^T.

    @param rotation:        The rotation matrix.
    @type rotation:         Numeric array ((3, 3), Float64)
    @param tensor_diag:     The diagonalised alignment tensor.
    @type tensor_diag:      Numeric array ((3, 3), Float64)
    @return:                The alignment tensor (within the structural frame).
    @rtype:                 Numeric array ((3, 3), Float64)
    """

    # Rotation (R . tensor_diag . R^T).
    return dot(rotation, dot(tensor_diag, transpose(rotation)))


def calc_tensor_diag(Axx, Ayy, Azz):
    """Function for calculating the diagonalised alignment tensor.

    The diagonalised alignment tensor is defined as

                   | Axx   0    0  |
        tensor  =  |  0   Ayy   0  |.
                   |  0    0   Azz |

    @param Axx:     The Axx parameter of the ellipsoid.
    @type Axx:      float
    @param Ayy:     The Ayy parameter of the ellipsoid.
    @type Ayy:      float
    @param Azz:     The Azz parameter of the ellipsoid.
    @type Azz:      float
    @return:        The diagonalised alignment tensor.
    @rtype:         Numeric array ((3, 3), Float64)
    """

    # Initialise the tensor.
    tensor = zeros((3, 3), Float64)

    # Populate the diagonal elements.
    tensor[0, 0] = Axx
    tensor[1, 1] = Ayy
    tensor[2, 2] = Azz

    # Return the tensor.
    return tensor


def dependency_generator():
    """Generator for the automatic updating the alignment tensor data structures.

    The order of the yield statements is important!

    @return:            This generator successively yields three objects, the target object to
                        update, the list of parameters which if modified cause the target to be
                        updated, and the list of parameters that the target depends upon.
    """

    yield ('Azz',           ['Axx', 'Ayy'],                                 ['Axx', 'Ayy'])
    yield ('Axxyy',         ['Axx', 'Ayy'],                                 ['Axx', 'Ayy'])
    yield ('Axx_unit',      ['alpha', 'beta', 'gamma'],                     ['alpha', 'beta', 'gamma'])
    yield ('Ayy_unit',      ['alpha', 'beta', 'gamma'],                     ['alpha', 'beta', 'gamma'])
    yield ('Azz_unit',      ['alpha', 'beta'],                              ['alpha', 'beta'])
    yield ('tensor_diag',   ['tm', 'Da', 'Dr'],                             ['type', 'Axx', 'Ayy', 'Azz'])
    yield ('rotation',      ['alpha', 'beta', 'gamma'],                     ['type', 'Axx_unit', 'Ayy_unit', 'Azz_unit'])
    yield ('tensor',        ['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma'],   ['rotation', 'tensor_diag'])



# Alignment tensor specific data.
#################################

class AlignTensorData(Element):
    def __init__(self):
        """An empty data container for the alignment tensor elements."""


    def __setattr__(self, name, value):
        """Function for calculating the parameters, unit vectors, and tensors on the fly.

        @param name:    The name of the object to set.
        @type name:     str
        @param value:   The value to set the object corresponding to the name argument to.
        @type value:    Any Python object type
        """

        # Get the base parameter name and determine the object category ('val', 'err', or 'sim').
        if search('_err$', name):
            category = 'err'
            param_name = name[:-4]
        elif search('_sim$', name):
            category = 'sim'
            param_name = name[:-4]
        else:
            category = 'val'
            param_name = name

        # List of modifiable attributes.
        mod_attr = ['Axx',
                    'Ayy',
                    'Axy',
                    'Axz',
                    'Ayz',
                    'alpha',
                    'beta',
                    'gamma']

        # Test if the attribute that is trying to be set is modifiable.
        if not param_name in mod_attr:
            raise RelaxError, "The object " + `name` + " is not modifiable."

        # Set the attribute normally.
        self.__dict__[name] = value

        # Update the data structures.
        for target, update_if_set, depends in dependency_generator():
            self.__update_object(param_name, target, update_if_set, depends, category)


    def __update_sim_append(self, param_name, index):
        """Update the Monte Carlo simulation data lists when a simulation value is appended.

        @param param_name:  The MC sim parameter name which is being appended to.
        @type param_name:   str
        @param index:       The index of the Monte Carlo simulation which was set.
        @type index:        int
        """

        # Loop over the targets.
        for target, update_if_set, depends in dependency_generator(self.type):
            # Only update if the parameter name is within the 'update_if_set' list.
            if not param_name in update_if_set:
                continue

            # Get the function for calculating the value.
            fn = globals()['calc_'+target]

            # Get all the dependencies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Modify the dependency name.
                if dep_name != 'type':
                    dep_name = dep_name+'_sim'

                # Test if the MC sim object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

                # Get the MC dependency.
                dep_obj = getattr(self, dep_name)

                # The alignment tensor type.
                if dep_name == 'type':
                    deps = deps+(dep_obj,)
                    continue

                # Test if the MC sim dependency is long enough.
                if len(dep_obj) <= index:
                    missing_dep = 1
                    break

                # Place the value corresponding to the index into the 'deps' array.
                deps = deps+(dep_obj[index],)

            # Only update the MC simulation object if its dependencies exist.
            if not missing_dep:
                # Get the target object.
                target_obj = getattr(self, target+'_sim')

                # Calculate and set the value.
                target_obj.append_untouchable_item(fn(*deps))


    def __update_sim_set(self, param_name, index):
        """Update the Monte Carlo simulation data lists when a simulation value is set.

        @param param_name:  The MC sim parameter name which is being set.
        @type param_name:   str
        @param index:       The index of the Monte Carlo simulation which was set.
        @type index:        int
        """

        # Loop over the targets.
        for target, update_if_set, depends in dependency_generator(self.type):
            # Only update if the parameter name is within the 'update_if_set' list.
            if not param_name in update_if_set:
                continue

            # Get the function for calculating the value.
            fn = globals()['calc_'+target]

            # Get all the dependencies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Modify the dependency name.
                if dep_name != 'type':
                    dep_name = dep_name+'_sim'

                # Test if the MC sim object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

                # Get the MC dependency.
                dep_obj = getattr(self, dep_name)

                # The alignment tensor type.
                if dep_name == 'type':
                    deps = deps+(dep_obj,)
                    continue

                # Test if the MC sim dependency is long enough.
                if len(dep_obj) <= index:
                    missing_dep = 1
                    break

                # Place the value corresponding to the index into the 'deps' array.
                deps = deps+(dep_obj[index],)

            # Only update the MC simulation object if its dependencies exist.
            if not missing_dep:
                # Get the target object.
                target_obj = getattr(self, target+'_sim')

                # Calculate and set the value.
                target_obj.set_untouchable_item(index, fn(*deps))


    def __update_object(self, param_name, target, update_if_set, depends, category):
        """Function for updating the target object, its error, and the MC simulations.

        If the base name of the object is not within the 'update_if_set' list, this function returns
        without doing anything (to avoid wasting time).  Dependant upon the category the object
        (target), its error (target+'_err'), or all Monte Carlo simulations (target+'_sim') are
        updated.

        @param param_name:      The parameter name which is being set in the __setattr__() function.
        @type param_name:       str
        @param target:          The name of the object to update.
        @type target:           str
        @param update_if_set:   If the parameter being set by the __setattr__() function is not
            within this list of parameters, don't waste time updating the
            target.
        @param depends:         An array of names objects that the target is dependent upon.
        @type depends:          array of str
        @param category:        The category of the object to update (one of 'val', 'err', or
            'sim').
        @type category:         str
        @return:                None
        """

        # Only update if the parameter name is within the 'update_if_set' list.
        if not param_name in update_if_set:
            return

        # Get the function for calculating the value.
        fn = globals()['calc_'+target]


        # The value.
        ############

        if category == 'val':
            # Get all the dependencies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Test if the object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

                # Get the object and place it into the 'deps' tuple.
                deps = deps+(getattr(self, dep_name),)

            # Only update the object if its dependencies exist.
            if not missing_dep:
                # Calculate the value.
                value = fn(*deps)

                # Set the attribute.
                self.__dict__[target] = value


        # The error.
        ############

        if category == 'err':
            # Get all the dependencies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Test if the error object exists.
                if not hasattr(self, dep_name+'_err'):
                    missing_dep = 1
                    break

                # Get the object and place it into the 'deps' tuple.
                deps = deps+(getattr(self, dep_name+'_err'),)

            # Only update the error object if its dependencies exist.
            if not missing_dep:
                # Calculate the value.
                value = fn(*deps)

                # Set the attribute.
                self.__dict__[target+'_err'] = value


        # The Monte Carlo simulations.
        ##############################

        if category == 'sim':
            # Get all the dependencies if possible.
            missing_dep = 0
            deps = []
            for dep_name in depends:
                # Modify the dependency name.
                if dep_name != 'type':
                    dep_name = dep_name+'_sim'

                # Test if the MC sim object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

            # Only create the MC simulation object if its dependencies exist.
            if not missing_dep:
                # Initialise an empty array to store the MC simulation object elements (if it doesn't already exist).
                if not target+'_sim' in self.__dict__:
                    self.__dict__[target+'_sim'] = AlignTensorSimList(target, self)



class AlignTensorSimList(ListType):
    """Empty data container for Monte Carlo simulation alignment tensor data."""

    def __init__(self, param_name, align_element):
        """Initialise the Monte Carlo simulation parameter list.

        This function makes the parameter name and parent object accessible to the functions of this
        list object.
        """

        self.param_name = param_name
        self.align_element = align_element


    def __setitem__(self, index, value):
        """Set the value."""

        # Set the value.
        ListType.__setitem__(self, index, value)

        # Then update the other lists.
        self.align_element._AlignTensorData__update_sim_set(self.param_name, index)


    def append(self, value):
        """Replacement function for the normal self.append() method."""

        # Append the value to the list.
        self[len(self):len(self)] = [value]

        # Update the other MC lists.
        self.align_element._AlignTensorData__update_sim_append(self.param_name, len(self)-1)


    def append_untouchable_item(self, value):
        """Append the value for an untouchable MC data structure."""

        # Append the value to the list.
        self[len(self):len(self)] = [value]


    def set_untouchable_item(self, index, value):
        """Set the value for an untouchable MC data structure."""

        # Set the value.
        ListType.__setitem__(self, index, value)
