###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2006-2007 Edward d'Auvergne                       #
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


from re import search
from types import ListType

from data_classes import Element, SpecificData
from generic_fns.diffusion_tensor import calc_Diso, calc_Dpar, calc_Dpar_unit, calc_Dper, calc_Dratio, calc_Dx, calc_Dx_unit, calc_Dy, calc_Dy_unit, calc_Dz, calc_Dz_unit, calc_rotation, calc_tensor, calc_tensor_diag



def dependency_generator(diff_type):
    """Generator for the automatic updating the diffusion tensor data structures.

    The order of the yield statements is important!

    @param diff_type:   The type of Brownian rotational diffusion.
    @type diff_type:    str
    @return:            This generator successively yields three objects, the target object to
                        update, the list of parameters which if modified cause the target to be
                        updated, and the list of parameters that the target depends upon.
    """

    # Spherical diffusion.
    if diff_type == 'sphere':
        yield ('Diso',          ['tm'], ['tm'])
        yield ('tensor_diag',   ['tm'], ['type', 'Diso'])
        yield ('rotation',      ['tm'], ['type'])
        yield ('tensor',        ['tm'], ['rotation', 'tensor_diag'])

    # Spheroidal diffusion.
    elif diff_type == 'spheroid':
        yield ('Diso',          ['tm'],                         ['tm'])
        yield ('Dpar',          ['tm', 'Da'],                   ['Diso', 'Da'])
        yield ('Dper',          ['tm', 'Da'],                   ['Diso', 'Da'])
        yield ('Dratio',        ['tm', 'Da'],                   ['Dpar', 'Dper'])
        yield ('Dpar_unit',     ['theta', 'phi'],               ['theta', 'phi'])
        yield ('tensor_diag',   ['tm', 'Da'],                   ['type', 'Dpar', 'Dper'])
        yield ('rotation',      ['theta', 'phi'],               ['type', 'theta', 'phi', 'Dpar_unit'])
        yield ('tensor',        ['tm', 'Da', 'theta', 'phi'],   ['rotation', 'tensor_diag'])

    # Ellipsoidal diffusion.
    elif diff_type == 'ellipsoid':
        yield ('Diso',          ['tm'],                                         ['tm'])
        yield ('Dx',            ['tm', 'Da', 'Dr'],                             ['Diso', 'Da', 'Dr'])
        yield ('Dy',            ['tm', 'Da', 'Dr'],                             ['Diso', 'Da', 'Dr'])
        yield ('Dz',            ['tm', 'Da'],                                   ['Diso', 'Da'])
        yield ('Dx_unit',       ['alpha', 'beta', 'gamma'],                     ['alpha', 'beta', 'gamma'])
        yield ('Dy_unit',       ['alpha', 'beta', 'gamma'],                     ['alpha', 'beta', 'gamma'])
        yield ('Dz_unit',       ['alpha', 'beta'],                              ['alpha', 'beta'])
        yield ('tensor_diag',   ['tm', 'Da', 'Dr'],                             ['type', 'Dx', 'Dy', 'Dz'])
        yield ('rotation',      ['alpha', 'beta', 'gamma'],                     ['type', 'Dx_unit', 'Dy_unit', 'Dz_unit'])
        yield ('tensor',        ['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma'],   ['rotation', 'tensor_diag'])



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
        if not param_name in mod_attr:
            raise RelaxError, "The object " + `name` + " is not modifiable."

        # Set the attribute normally.
        self.__dict__[name] = value

        # Skip the updating process for certain objects.
        if name in ['type', 'fixed', 'spheroid_type']:
            return

        # Update the data structures.
        for target, update_if_set, depends in dependency_generator(self.type):
            self._update_object(param_name, target, update_if_set, depends, category)


    def _update_object(self, param_name, target, update_if_set, depends, category):
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
        @param depends:         An array of names objects that the target is dependant upon.
        @type depends:          array of str
        @param category:        The category of the object to update (one of 'val', 'err', or
            'sim').
        @type category:         str
        @return:                None
        """

        # Only update if the parameter name is within the 'update_if_set' list.
        if not param_name in update_if_set:
            return

        # Debugging.
        if Debug:
            print "\n\n"
            print "Param name: " + `param_name`
            print "Target: " + `target`
            print "update_if_set: " + `update_if_set`
            print "Depends: " + `depends`
            print "Category: " + `category`

        # Get the function for calculating the value.
        fn = globals()['calc_'+target]


        # The value.
        ############

        if category == 'val':
            # Get all the dependancies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Test if the object exists.
                if not hasattr(self, dep_name):
                    # Debugging.
                    if Debug:
                        print "Missing dep: " + `dep_name`

                    missing_dep = 1
                    break

                # Get the object and place it into the 'deps' tuple.
                deps = deps+(getattr(self, dep_name),)

            # Debugging.
            if Debug:
                print "Deps: " + `deps`

            # Only update the object if its dependancies exist.
            if not missing_dep:
                # Calculate the value.
                value = fn(*deps)

                # Debugging.
                if Debug:
                    print "Value: " + `value`

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
                sim_values = DiffTensorSimList(self)

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



class DiffTensorSimList(ListType):
    """Empty data container for Monte Carlo simulation diffusion tensor data."""

    def __init__(self, diff_element):
        """Make the parent object accessible to this list object."""

        self.__diff_element = diff_element


    def __setitem__(self, index, value):
        """Set the value."""

        ListType.__setitem__(self, index, value)


    def append(self, value):
        """Replacement function for the normal self.append() method."""

        # Append the value to the list.
        self[len(self):len(self)] = [value]
