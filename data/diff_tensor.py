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


        ###############################
        # Update the data structures. #
        ###############################


        # Objects for all tensor types.
        ###############################

        # The isotropic diffusion rate Diso.
        self._update_object(param_name, target='Diso', update_if_set=['tm'], depends=['tm'], category=category)


        # Spherical diffusion.
        ######################

        if self.type == 'sphere':
            # Update the diagonalised diffusion tensor (within the diffusion frame).
            self._update_object(param_name, target='tensor_diag', update_if_set=['tm'], depends=['type', 'Diso'], category=category)

            # The rotation matrix (diffusion frame to structural frame).
            self._update_object(param_name, target='rotation', update_if_set=['tm'], depends=['type'], category=category)

            # The diffusion tensor (within the structural frame).
            self._update_object(param_name, target='tensor', update_if_set=['tm'], depends=['rotation', 'tensor_diag'], category=category)


        # Spheroidal diffusion.
        #######################

        elif self.type == 'spheroid':
            # Update Dpar, Dper, and Dratio.
            self._update_object(param_name, target='Dpar', update_if_set=['tm', 'Da'], depends=['Diso', 'Da'], category=category)
            self._update_object(param_name, target='Dper', update_if_set=['tm', 'Da'], depends=['Diso', 'Da'], category=category)
            self._update_object(param_name, target='Dratio', update_if_set=['tm', 'Da'], depends=['Dpar', 'Dper'], category=category)

            # Update the unit vector parallel to the axis.
            self._update_object(param_name, target='Dpar_unit', update_if_set=['theta', 'phi'], depends=['theta', 'phi'], category=category)

            # Update the diagonalised diffusion tensor (within the diffusion frame).
            self._update_object(param_name, target='tensor_diag', update_if_set=['tm', 'Da'], depends=['type', 'Dpar', 'Dper'], category=category)

            # The rotation matrix (diffusion frame to structural frame).
            self._update_object(param_name, target='rotation', update_if_set=['theta', 'phi'], depends=['type', 'theta', 'phi', 'Dpar_unit'], category=category)

            # The diffusion tensor (within the structural frame).
            self._update_object(param_name, target='tensor', update_if_set=['tm', 'Da', 'theta', 'phi'], depends=['rotation', 'tensor_diag'], category=category)


        # Ellipsoidal diffusion.
        ########################

        elif self.type == 'ellipsoid':
            # Update Dx, Dy, and Dz.
            self._update_object(param_name, target='Dx', update_if_set=['tm', 'Da', 'Dr'], depends=['Diso', 'Da', 'Dr'], category=category)
            self._update_object(param_name, target='Dy', update_if_set=['tm', 'Da', 'Dr'], depends=['Diso', 'Da', 'Dr'], category=category)
            self._update_object(param_name, target='Dz', update_if_set=['tm', 'Da'], depends=['Diso', 'Da'], category=category)

            # Update the unit vectors parallel to the axes.
            self._update_object(param_name, target='Dx_unit', update_if_set=['alpha', 'beta', 'gamma'], depends=['alpha', 'beta', 'gamma'], category=category)
            self._update_object(param_name, target='Dy_unit', update_if_set=['alpha', 'beta', 'gamma'], depends=['alpha', 'beta', 'gamma'], category=category)
            self._update_object(param_name, target='Dz_unit', update_if_set=['beta', 'gamma'], depends=['beta', 'gamma'], category=category)

            # Update the diagonalised diffusion tensor (within the diffusion frame).
            self._update_object(param_name, target='tensor_diag', update_if_set=['tm', 'Da', 'Dr'], depends=['type', 'Dx', 'Dy', 'Dz'], category=category)

            # The rotation matrix (diffusion frame to structural frame).
            self._update_object(param_name, target='rotation', update_if_set=['alpha', 'beta', 'gamma'], depends=['type', 'Dx_unit', 'Dy_unit', 'Dz_unit'], category=category)

            # The diffusion tensor (within the structural frame).
            self._update_object(param_name, target='tensor', update_if_set=['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma'], depends=['rotation', 'tensor_diag'], category=category)


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
                sim_values = DiffTensorSimList()

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
    def __init__(self):
        """Empty data container for Monte Carlo simulation diffusion tensor data."""

    def __setitem__(self):
        """Set the value."""
        print "Setitem"

    def append(self, value):
        print "append: " + `value`
