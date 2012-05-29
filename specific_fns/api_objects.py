###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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

# Module docstring.
"""A module of special objects used within the specific function API."""

# Python module imports.
from re import search
from types import FunctionType, MethodType

# relax module imports.
from relax_errors import RelaxError


class Param_list:
    """A special object for handling global and spin parameters."""

    def __init__(self, spin_data=True):
        """Set up the class.

        @keyword spin_data:         A flag which if True indicates that the specific analysis operates with spins.
        @type spin_data:            bool
        """

        # Store the flags.
        self.spin_data = spin_data

        # Initialise the lists and dictionaries for the parameter info.
        self._names = []
        self._scope = {}
        self._string = {}
        self._defaults = {}
        self._units = {}
        self._desc = {}
        self._py_types = {}
        self._conv_factor = {}
        self._grace_string = {}
        self._set = {}
        self._err = {}
        self._sim = {}

        # Add some spin specific objects.
        if self.spin_data:
            self.add('select', scope='spin', desc='The spin selection flag', py_type=bool)
            self.add('fixed', scope='spin', desc='The fixed flag', py_type=bool)


    def add(self, name, scope=None, string=None, default=None, units=None, desc=None, py_type=None, set='generic', conv_factor=None, grace_string=None, err=False, sim=False):
        """Add a parameter to the list.

        @param name:            The name of the parameter.  This will be used as the variable name.
        @type name:             str
        @keyword scope:         The parameter scope.  This can be set to 'global' for parameters located within the global scope of the current data pipe.  Or set to 'spin' for spin specific parameters.  Alternatively the value 'both' indicates that there are both global and specific versions of this parameter.
        @type scope:            str
        @keyword string:        The string representation of the parameter.
        @type string:           None or str
        @keyword default:       The default value of the parameter.
        @type default:          anything
        @keyword units:         A string representing the parameters units.
        @type units:            None or str
        @keyword desc:          The text description of the parameter.
        @type desc:             None or str
        @keyword py_type:       The Python type that this parameter should be.
        @type py_type:          Python type object
        @keyword set:           The set of object names.  This can be set to 'all' for all names, to 'generic' for generic object names, 'params' for analysis specific parameter names, or to 'min' for minimisation specific object names.
        @type set:              str
        @keyword conv_factor:   The factor of conversion between different parameter units.
        @type conv_factor:      None, float or func
        @keyword grace_string:  The string used for the axes in Grace plots of the data.
        @type grace_string:     None or str
        @keyword err:           A flag which if True indicates that the parameter name + '_err' error data structure can exist.
        @type err:              bool
        @keyword sim:           A flag which if True indicates that the parameter name + '_sim' Monte Carlo simulation data structure can exist.
        @type sim:              bool
        """

        # Checks.
        if scope == None:
            raise RelaxError("The parameter scope must be set.")
        if py_type == None:
            raise RelaxError("The parameter type must be set.")
        allowed_sets = ['all', 'generic', 'params', 'min']
        if set not in allowed_sets:
            raise RelaxError("The parameter set '%s' must be one of %s." % (set, allowed_sets))

        # Add the values.
        self._names.append(name)
        self._scope[name] = scope
        self._defaults[name] = default
        self._units[name] = units
        self._desc[name] = desc
        self._py_types[name] = py_type
        self._set[name] = set
        self._conv_factor[name] = conv_factor
        self._err[name] = err
        self._sim[name] = sim

        # The parameter string.
        if string:
            self._string[name] = string
        else:
            self._string[name] = name

        # The Grace string.
        if grace_string:
            self._grace_string[name] = grace_string
        else:
            self._grace_string[name] = name


    def add_min_data(self, min_stats_global=False, min_stats_spin=False):
        """Add minimisation specific objects.

        @keyword min_stats_global:  A flag which if True will include the parameters 'chi2', 'iter', 'f_count', 'g_count', 'h_count', 'warning' in the list of global parameters.
        @type min_stats_global:     bool
        @keyword min_stats_spin:    A flag which if True will include the parameters 'chi2', 'iter', 'f_count', 'g_count', 'h_count', 'warning' in the list of spin parameters.
        @type min_stats_spin:       bool
        """

        # Store the flags.
        self.min_stats_global = min_stats_global
        self.min_stats_spin = min_stats_spin

        # Global minimisation data.
        if self.min_stats_global or self.min_stats_spin:
            # The scope.
            if self.min_stats_global and self.min_stats_spin:
                scope = 'both'
            elif self.min_stats_global:
                scope = 'global'
            else:
                scope = 'spin'

            # The minimisation parameters.
            self.add('chi2', scope=scope, desc='Chi-squared value', py_type=float, set='min', err=False, sim=True)
            self.add('iter', scope=scope, desc='Optimisation iterations', py_type=int, set='min', err=False, sim=True)
            self.add('f_count', scope=scope, desc='Number of function calls', py_type=int, set='min', err=False, sim=True)
            self.add('g_count', scope=scope, desc='Number of gradient calls', py_type=int, set='min', err=False, sim=True)
            self.add('h_count', scope=scope, desc='Number of Hessian calls', py_type=int, set='min', err=False, sim=True)
            self.add('warning', scope=scope, desc='Optimisation warning', py_type=str, set='min', err=False, sim=True)


    def base_loop(self, set=None):
        """An iterator method for looping over all the base parameters.

        @keyword set:   The set of object names to return.  This can be set to 'all' for all names, to 'generic' for generic object names, 'params' for analysis specific parameter names, or to 'min' for minimisation specific object names.
        @type set:      str
        @returns:       The parameter names.
        @rtype:         str
        """

        # Loop over the parameters.
        for name in self._names:
            # Skip the parameter if the set does not match.
            if set == 'generic' and self._set[name] != 'generic':
                continue
            elif set == 'params' and self._set[name] != 'params':
                continue
            elif set == 'min' and self._set[name] != 'min':
                continue

            # Yield the parameter name.
            yield name


    def check_param(self, name):
        """Check if the parameter exists.

        @param name:        The name of the parameter to search for.
        @type name:         str
        @raises RelaxError: If the parameter does not exist.
        """

        # Check.
        if name not in self._names:
            raise RelaxError("The parameter '%s' does not exist." % name)


    def contains(self, name):
        """Determine if the given name is within the parameter list.

        @param name:    The name of the parameter to search for.
        @type name:     str
        @return:        True if the parameter is within the list, False otherwise.
        @rtype:         bool
        """

        # Check.
        if name in self._names:
            return True

        # No match.
        return False


    def get_conv_factor(self, name):
        """Return the conversion factor.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The conversion factor.
        @rtype:         float
        """

        # Parameter check.
        self.check_param(name)

        # No factor.
        if self._conv_factor[name] == None:
            return 1.0

        # Function.
        if isinstance(self._conv_factor[name], FunctionType) or isinstance(self._conv_factor[name], MethodType):
            return self._conv_factor[name]()

        # Value.
        return self._conv_factor[name]


    def get_default(self, name):
        """Return the default value of the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The default value.
        @rtype:         None or str
        """

        # Parameter check.
        self.check_param(name)

        # Return the default value.
        return self._defaults[name]


    def get_desc(self, name):
        """Return the description of the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The description.
        @rtype:         None or str
        """

        # Skip error and simulation structures.
        if search('_err$', name) or search('_sim$', name):
            return None

        # Parameter check.
        self.check_param(name)

        # Return the description.
        return self._desc[name]


    def get_err(self, name):
        """Return the error flag for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The error flag for the parameter.
        @rtype:         bool
        """

        # Parameter check.
        self.check_param(name)

        # Return the type.
        return self._err[name]


    def get_grace_string(self, name):
        """Return the Grace string for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The Grace string.
        @rtype:         str
        """

        # Parameter check.
        self.check_param(name)

        # Return the value.
        return self._grace_string[name]


    def get_set(self, name):
        """Return the parameter set that the parameter belongs to.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The parameter set.
        @rtype:         str
        """

        # Parameter check.
        self.check_param(name)

        # Return the type.
        return self._set[name]


    def get_sim(self, name):
        """Return the Monte Carlo simulation flag for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The Monte Carlo simulation flag for the parameter.
        @rtype:         bool
        """

        # Parameter check.
        self.check_param(name)

        # Return the type.
        return self._sim[name]


    def get_type(self, name):
        """Return the Python type for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The Python type.
        @rtype:         Python type object
        """

        # Parameter check.
        self.check_param(name)

        # Return the Python type.
        return self._py_types[name]


    def get_units(self, name):
        """Return the units string for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The units string.
        @rtype:         str
        """

        # Parameter check.
        self.check_param(name)

        # Function.
        if isinstance(self._conv_factor[name], FunctionType) or isinstance(self._conv_factor[name], MethodType):
            return self._units[name]()

        # Return the value.
        return self._units[name]


    def loop(self, set=None, error_names=False, sim_names=False):
        """An iterator method for looping over all the parameters.

        @keyword set:           The set of object names to return.  This can be set to 'all' for all names, to 'generic' for generic object names, 'params' for analysis specific parameter names, or to 'min' for minimisation specific object names.
        @type set:              str
        @keyword error_names:   A flag which if True will add the error object names as well.
        @type error_names:      bool
        @keyword sim_names:     A flag which if True will add the Monte Carlo simulation object names as well.
        @type sim_names:        bool
        @returns:               The parameter names.
        @rtype:                 str
        """

        # Loop over and yield the parameters.
        for name in self.base_loop(set=set):
            yield name

        # Error names.
        if error_names:
            for name in self.base_loop(set=set):
                if self.get_err(name):
                    yield name + '_err'

        # Sim names.
        if sim_names:
            for name in self.base_loop(set=set):
                if self.get_sim(name):
                    yield name + '_sim'
