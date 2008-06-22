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
from numpy import dot, float64, identity, transpose, zeros
from types import ListType

# relax module imports.
from data_classes import Element
from relax_errors import RelaxError
from relax_xml import fill_object_contents



def calc_Axx(Sxx):
    """Function for calculating the Axx value.

    The equation for calculating the parameter is

        Axx  =  2/3 Sxx.

    @param Sxx:     The Sxx component of the Saupe order matrix.
    @type Sxx:      float
    @rtype:         float
    """

    # Calculate and return the Axx value.
    return 2.0/3.0 * Sxx


def calc_Ayy(Syy):
    """Function for calculating the Ayy value.

    The equation for calculating the parameter is

        Ayy  =  2/3 Syy.

    @param Syy:     The Syy component of the Saupe order matrix.
    @type Syy:      float
    @rtype:         float
    """

    # Calculate and return the Ayy value.
    return 2.0/3.0 * Syy


def calc_Axy(Sxy):
    """Function for calculating the Axy value.

    The equation for calculating the parameter is

        Axy  =  2/3 Sxy.

    @param Sxy:     The Sxy component of the Saupe order matrix.
    @type Sxy:      float
    @rtype:         float
    """

    # Calculate and return the Axy value.
    return 2.0/3.0 * Sxy


def calc_Axz(Sxz):
    """Function for calculating the Axz value.

    The equation for calculating the parameter is

        Axz  =  2/3 Sxz.

    @param Sxz:     The Sxz component of the Saupe order matrix.
    @type Sxz:      float
    @rtype:         float
    """

    # Calculate and return the Axz value.
    return 2.0/3.0 * Sxz


def calc_Ayz(Syz):
    """Function for calculating the Ayz value.

    The equation for calculating the parameter is

        Ayz  =  2/3 Syz.

    @param Syz:     The Syz component of the Saupe order matrix.
    @type Syz:      float
    @rtype:         float
    """

    # Calculate and return the Ayz value.
    return 2.0/3.0 * Syz


def calc_Axxyy(Axx, Ayy):
    """Function for calculating the Axx-yy value.

    The equation for calculating the parameter is

        Axx-yy  =  Axx - Ayy.

    @param Axx:     The Axx component of the alignment tensor.
    @type Axx:      float
    @param Ayy:     The Ayy component of the alignment tensor.
    @type Ayy:      float
    @return:        The Axx-yy component of the alignment tensor.
    @rtype:         float
    """

    # Calculate and return the Axx-yy value.
    return Axx - Ayy


def calc_Azz(Axx, Ayy):
    """Function for calculating the Azz value.

    The equation for calculating the parameter is

        Azz  =  - Axx - Ayy.

    @param Axx:     The Axx component of the alignment tensor.
    @type Axx:      float
    @param Ayy:     The Ayy component of the alignment tensor.
    @type Ayy:      float
    @return:        The Azz component of the alignment tensor.
    @rtype:         float
    """

    # Calculate and return the Azz value.
    return - Axx - Ayy


def calc_Pxx(Sxx):
    """Function for calculating the Pxx value.

    The equation for calculating the parameter is

        Pxx  =  2/3 Sxx + 1/3.

    @param Sxx:     The Sxx component of the Saupe order matrix.
    @type Sxx:      float
    @rtype:         float
    """

    # Calculate and return the Pxx value.
    return 2.0/3.0 * Sxx + 1.0/3.0


def calc_Pyy(Syy):
    """Function for calculating the Pyy value.

    The equation for calculating the parameter is

        Pyy  =  2/3 Syy + 1/3.

    @param Syy:     The Syy component of the Saupe order matrix.
    @type Syy:      float
    @rtype:         float
    """

    # Calculate and return the Pyy value.
    return 2.0/3.0 * Syy + 1.0/3.0


def calc_Pxy(Sxy):
    """Function for calculating the Pxy value.

    The equation for calculating the parameter is

        Pxy  =  2/3 Sxy.

    @param Sxy:     The Sxy component of the Saupe order matrix.
    @type Sxy:      float
    @rtype:         float
    """

    # Calculate and return the Pxy value.
    return 2.0/3.0 * Sxy


def calc_Pxz(Sxz):
    """Function for calculating the Pxz value.

    The equation for calculating the parameter is

        Pxz  =  2/3 Sxz.

    @param Sxz:     The Sxz component of the Saupe order matrix.
    @type Sxz:      float
    @rtype:         float
    """

    # Calculate and return the Pxz value.
    return 2.0/3.0 * Sxz


def calc_Pyz(Syz):
    """Function for calculating the Pyz value.

    The equation for calculating the parameter is

        Pyz  =  2/3 Syz.

    @param Syz:     The Syz component of the Saupe order matrix.
    @type Syz:      float
    @rtype:         float
    """

    # Calculate and return the Pyz value.
    return 2.0/3.0 * Syz


def calc_Pxxyy(Pxx, Pyy):
    """Function for calculating the Pxx-yy value.

    The equation for calculating the parameter is

        Pxx-yy  =  Pxx - Pyy.

    @param Pxx:     The Pxx component of the alignment tensor.
    @type Pxx:      float
    @param Pyy:     The Pyy component of the alignment tensor.
    @type Pyy:      float
    @return:        The Pxx-yy component of the alignment tensor.
    @rtype:         float
    """

    # Calculate and return the Pxx-yy value.
    return Pxx - Pyy


def calc_Pzz(Pxx, Pyy):
    """Function for calculating the Pzz value.

    The equation for calculating the parameter is

        Pzz  =  1 - Pxx - Pyy.

    @param Pxx:     The Pxx component of the alignment tensor.
    @type Pxx:      float
    @param Pyy:     The Pyy component of the alignment tensor.
    @type Pyy:      float
    @return:        The Pzz component of the alignment tensor.
    @rtype:         float
    """

    # Calculate and return the Pzz value.
    return 1.0 - Pxx - Pyy


def calc_Sxx_unit(alpha, beta, gamma):
    """Function for calculating the Sxx unit vector.

    The unit Sxx vector is

                     | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
        Sxx_unit  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |.
                     |                    cos(alpha) * sin(beta)                      |

    @param alpha:   The Euler angle alpha in radians using the z-y-z convention.
    @type alpha:    float
    @param beta:    The Euler angle beta in radians using the z-y-z convention.
    @type beta:     float
    @param gamma:   The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:    float
    @return:        The Sxx unit vector.
    @rtype:         numpy array (float64)
    """

    # Initilise the vector.
    Sxx_unit = zeros(3, float64)

    # Calculate the x, y, and z components.
    Sxx_unit[0] = -sin(alpha) * sin(gamma)  +  cos(alpha) * cos(beta) * cos(gamma)
    Sxx_unit[1] = -sin(alpha) * cos(gamma)  -  cos(alpha) * cos(beta) * sin(gamma)
    Sxx_unit[2] = cos(alpha) * sin(beta)

    # Return the unit vector.
    return Sxx_unit


def calc_Syy_unit(alpha, beta, gamma):
    """Function for calculating the Syy unit vector.

    The unit Syy vector is

                     | cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
        Syy_unit  =  | cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |.
                     |                   sin(alpha) * sin(beta)                      |

    @param alpha:   The Euler angle alpha in radians using the z-y-z convention.
    @type alpha:    float
    @param beta:    The Euler angle beta in radians using the z-y-z convention.
    @type beta:     float
    @param gamma:   The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:    float
    @return:        The Syy unit vector.
    @rtype:         numpy array (float64)
    """

    # Initilise the vector.
    Syy_unit = zeros(3, float64)

    # Calculate the x, y, and z components.
    Syy_unit[0] = cos(alpha) * sin(gamma)  +  sin(alpha) * cos(beta) * cos(gamma)
    Syy_unit[1] = cos(alpha) * cos(gamma)  -  sin(alpha) * cos(beta) * sin(gamma)
    Syy_unit[2] = sin(alpha) * sin(beta)

    # Return the unit vector.
    return Syy_unit


def calc_Szz_unit(beta, gamma):
    """Function for calculating the Szz unit vector.

    The unit Szz vector is

                     | -sin(beta) * cos(gamma) |
        Szz_unit  =  |  sin(beta) * sin(gamma) |.
                     |        cos(beta)        |

    @param beta:    The Euler angle beta in radians using the z-y-z convention.
    @type beta:     float
    @param gamma:   The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:    float
    @return:        The Szz unit vector.
    @rtype:         numpy array (float64)
    """

    # Initilise the vector.
    Szz_unit = zeros(3, float64)

    # Calculate the x, y, and z components.
    Szz_unit[0] = -sin(beta) * cos(gamma)
    Szz_unit[1] = sin(beta) * sin(gamma)
    Szz_unit[2] = cos(beta)

    # Return the unit vector.
    return Szz_unit


def calc_Sxxyy(Sxx, Syy):
    """Function for calculating the Sxx-yy value.

    The equation for calculating the parameter is

        Sxx-yy  =  Sxx - Syy.

    @param Sxx:     The Sxx component of the Saupe order matrix.
    @type Sxx:      float
    @param Syy:     The Syy component of the Saupe order matrix.
    @type Syy:      float
    @return:        The Sxx-yy component of the Saupe order matrix.
    @rtype:         float
    """

    # Calculate and return the Sxx-yy value.
    return Sxx - Syy


def calc_Szz(Sxx, Syy):
    """Function for calculating the Szz value.

    The equation for calculating the parameter is

        Szz  =  - Sxx - Syy.

    @param Sxx:     The Sxx component of the Saupe order matrix.
    @type Sxx:      float
    @param Syy:     The Syy component of the Saupe order matrix.
    @type Syy:      float
    @return:        The Szz component of the Saupe order matrix.
    @rtype:         float
    """

    # Calculate and return the Szz value.
    return - Sxx - Syy


def calc_rotation(Sxx_unit, Syy_unit, Szz_unit):
    """Function for calculating the rotation matrix.

    The rotation matrix required to shift from the align tensor frame to the structural
    frame is equal to

        R  =  | Sxx_unit  Syy_unit  Szz_unit |,

              | Sxx_unit[0]  Syy_unit[0]  Szz_unit[0] |
           =  | Sxx_unit[1]  Syy_unit[1]  Szz_unit[1] |.
              | Sxx_unit[2]  Syy_unit[2]  Szz_unit[2] |

    @param Sxx_unit:    The Sxx unit vector.
    @type Sxx_unit:     numpy array (float64)
    @param Syy_unit:    The Syy unit vector.
    @type Syy_unit:     numpy array (float64)
    @param Szz_unit:    The Szz unit vector.
    @type Szz_unit:     numpy array (float64)
    @return:            The rotation matrix.
    @rtype:             numpy array ((3, 3), float64)
    """

    # Initialise the rotation matrix.
    rotation = identity(3, float64)

    # First column of the rotation matrix.
    rotation[:, 0] = Sxx_unit

    # Second column of the rotation matrix.
    rotation[:, 1] = Syy_unit

    # Third column of the rotation matrix.
    rotation[:, 2] = Szz_unit

    # Return the tensor.
    return rotation


def calc_tensor(Sxx, Syy, Szz, Sxy, Sxz, Syz):
    """Function for calculating the alignment tensor (in the structural frame).

    @param Sxx:     The Sxx tensor element.
    @type Sxx:      float
    @param Syy:     The Syy tensor element.
    @type Syy:      float
    @param Szz:     The Szz tensor element.
    @type Szz:      float
    @param Sxy:     The Sxy tensor element.
    @type Sxy:      float
    @param Sxz:     The Sxz tensor element.
    @type Sxz:      float
    @param Syz:     The Syz tensor element.
    @type Syz:      float
    @return:        The alignment tensor (within the structural frame).
    @rtype:         3x3 numpy float64 array
    """

    # Initialise the tensor.
    tensor = zeros((3, 3), float64)

    # Populate the diagonal elements.
    tensor[0, 0] = Sxx
    tensor[1, 1] = Syy
    tensor[2, 2] = Szz

    # Populate the off diagonal elements.
    tensor[0, 1] = tensor[1, 0] = Sxy
    tensor[0, 2] = tensor[2, 0] = Sxz
    tensor[1, 2] = tensor[2, 1] = Syz

    # Return the tensor.
    return tensor


def calc_tensor_diag(rotation, tensor):
    """Function for calculating the diagonalised alignment tensor.

    The diagonalised alignment tensor is defined as

                   | Sxx'  0    0  |
        tensor  =  |  0   Syy'  0  |.
                   |  0    0   Szz'|

    The diagonalised alignment tensor is calculated using the tensor and the rotation matrix
    through the equation

        R^T . tensor_diag . R.

    @param rotation:    The rotation matrix.
    @type rotation:     numpy array ((3, 3), float64)
    @param tensor:      The full alignment tensor.
    @type tensor:       numpy array ((3, 3), float64)
    @return:        The diagonalised alignment tensor.
    @rtype:         numpy array ((3, 3), float64)
    """

    # Rotation (R^T . tensor_diag . R).
    return dot(transpose(rotation), dot(tensor_diag, rotation))


def dependency_generator():
    """Generator for the automatic updating the alignment tensor data structures.

    The order of the yield statements is important!

    @return:            This generator successively yields three objects, the target object to
                        update, the list of parameters which if modified cause the target to be
                        updated, and the list of parameters that the target depends upon.
    """

    yield ('Axx',           ['Sxx'],                                        ['Sxx'])
    yield ('Ayy',           ['Syy'],                                        ['Syy'])
    yield ('Axy',           ['Sxy'],                                        ['Sxy'])
    yield ('Axz',           ['Sxz'],                                        ['Sxz'])
    yield ('Ayz',           ['Syz'],                                        ['Syz'])
    yield ('Azz',           ['Sxx', 'Syy'],                                 ['Axx', 'Ayy'])
    yield ('Axxyy',         ['Sxx', 'Syy'],                                 ['Axx', 'Ayy'])
    yield ('Pxx',           ['Sxx'],                                        ['Sxx'])
    yield ('Pyy',           ['Syy'],                                        ['Syy'])
    yield ('Pxy',           ['Sxy'],                                        ['Sxy'])
    yield ('Pxz',           ['Sxz'],                                        ['Sxz'])
    yield ('Pyz',           ['Syz'],                                        ['Syz'])
    yield ('Pzz',           ['Sxx', 'Syy'],                                 ['Pxx', 'Pyy'])
    yield ('Pxxyy',         ['Sxx', 'Syy'],                                 ['Pxx', 'Pyy'])
    yield ('Szz',           ['Sxx', 'Syy'],                                 ['Sxx', 'Syy'])
    yield ('Sxxyy',         ['Sxx', 'Syy'],                                 ['Sxx', 'Syy'])
    yield ('Sxx_unit',      ['alpha', 'beta', 'gamma'],                     ['alpha', 'beta', 'gamma'])
    yield ('Syy_unit',      ['alpha', 'beta', 'gamma'],                     ['alpha', 'beta', 'gamma'])
    yield ('Szz_unit',      ['alpha', 'beta'],                              ['alpha', 'beta'])
    yield ('tensor_diag',   ['Sxx', 'Syy', 'Sxy', 'Sxz', 'Syz'],            ['tensor', 'rotation'])
    yield ('rotation',      ['alpha', 'beta', 'gamma'],                     ['Sxx_unit', 'Syy_unit', 'Szz_unit'])
    yield ('tensor',        ['Sxx', 'Syy', 'Sxy', 'Sxz', 'Syz'],            ['Sxx', 'Syy', 'Szz', 'Sxy', 'Sxz', 'Syz'])



# Alignment tensor specific data.
#################################

class AlignTensorList(ListType):
    """List type data container for holding all the alignment tensors.

    The elements of the list should be AlignTensorData instances.
    """

    def __repr__(self):
        """Replacement function for displaying an instance of this class."""

        text = "Alignment tensors.\n\n"
        text = text + "%-8s%-20s\n" % ("Index", "Name")
        for i in xrange(len(self)):
            text = text + "%-8i%-20s\n" % (i, self[i].name)
        text = text + "\nThese can be accessed by typing 'ds.align_tensor[index]'.\n"
        return text


    def add_item(self, name):
        """Function for appending a new AlignTensorData instance to the list."""

        self.append(AlignTensorData(name))


    def xml_create_element(self, doc, element):
        """Create an XML element for the alignment tensors.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the alignment tensors XML element to.
        @type element:  XML element object
        """

        # Create the alignment tensors element and add it to the higher level element.
        tensor_list_element = doc.createElement('align_tensors')
        element.appendChild(tensor_list_element)

        # Set the alignment tensor attributes.
        tensor_list_element.setAttribute('desc', 'Alignment tensor list')

        # Loop over the tensors.
        for i in xrange(len(self)):
            # Create an XML element for a single tensor.
            tensor_element = doc.createElement('align_tensor')
            tensor_list_element.appendChild(tensor_element)
            tensor_element.setAttribute('index', `i`)
            tensor_element.setAttribute('desc', 'Alignment tensor')

            # Add all simple python objects within the PipeContainer to the pipe element.
            fill_object_contents(doc, tensor_element, object=self[i], blacklist=self[i].__class__.__dict__.keys())


class AlignTensorData(Element):
    """An empty data container for the alignment tensor elements."""

    # List of modifiable attributes.
    __mod_attr__ = ['name',
                    'Sxx',
                    'Syy',
                    'Sxy',
                    'Sxz',
                    'Syz',
                    'domain',
                    'red']

    def __init__(self, name):
        """Function for placing the tensor name in the class namespace."""

        self.name = name


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

        # Test if the attribute that is trying to be set is modifiable.
        if not param_name in self.__mod_attr__:
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
        for target, update_if_set, depends in dependency_generator():
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
        for target, update_if_set, depends in dependency_generator():
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
