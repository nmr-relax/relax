###############################################################################
#                                                                             #
# Copyright (C) 2012-2014 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""The parameter list object base class for the specific analyses.

This provides a uniform interface for defining and handling parameters - either optimised or fixed - of the specific analyses.
"""

# Python module imports.
from re import search
from types import FunctionType, MethodType

# relax module imports.
from lib.errors import RelaxError


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
            self.add('select', scope='spin', desc='The spin selection flag', py_type=bool, sim=True)
            self.add('fixed', scope='spin', desc='The fixed flag', py_type=bool)


    def __new__(self, *args, **kargs):
        """Replacement function for implementing the singleton design pattern."""

        # First initialisation.
        if self.instance is None:
            # Create a new instance.
            self.instance = object.__new__(self, *args, **kargs)

        # Already initialised, so return the instance.
        return self.instance


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


    def add_align_data(self):
        """Add the PCS and RDC data.

        This is the equivalent of calling:

            add('pcs', scope='spin', grace_string='Pseudo-contact shift', units='ppm', desc='The pseudo-contact shift (PCS)', py_type=float)
            add('rdc', scope='spin', grace_string='Residual dipolar coupling', units='Hz', desc='The residual dipolar coupling (RDC)', py_type=float)
        """

        # Add the data.
        self.add('pcs', scope='spin', grace_string='Pseudo-contact shift', units='ppm', desc='The pseudo-contact shift (PCS)', py_type=float)
        self.add('rdc', scope='spin', grace_string='Residual dipolar coupling', units='Hz', desc='The residual dipolar coupling (RDC)', py_type=float)


    def add_csa(self, default=None, set='generic', err=False, sim=False):
        """Add the CSA parameter 'csa'.

        This is the equivalent of calling:

            add('csa', scope='spin', default=default, units='ppm', desc='Chemical shift anisotropy value (unitless)', py_type=float, set=set, conv_factor=1e-6, grace_string='\\qCSA\\Q', err=err, sim=sim)


        @keyword default:       The default CSA value.
        @type default:          float
        @keyword set:           The set of object names.  This can be set to 'all' for all names, to 'generic' for generic object names, 'params' for analysis specific parameter names, or to 'min' for minimisation specific object names.
        @type set:              str
        @keyword err:           A flag which if True indicates that the 'csa_err' error data structure can exist.
        @type err:              bool
        @keyword sim:           A flag which if True indicates that the 'csa_sim' Monte Carlo simulation data structure can exist.
        @type sim:              bool
        """

        # Add the CSA structure.
        self.add('csa', scope='spin', default=default, units='ppm', desc='Chemical shift anisotropy (unitless)', py_type=float, set=set, conv_factor=1e-6, grace_string='\\qCSA\\Q', err=err, sim=sim)


    def add_min_data(self, min_stats_global=False, min_stats_spin=False):
        """Add minimisation specific objects.

        This is the equivalent of calling the add() method as:

            add('chi2', desc='Chi-squared value', py_type=float, set='min', err=False, sim=True)
            add('iter', desc='Optimisation iterations', py_type=int, set='min', err=False, sim=True)
            add('f_count', desc='Number of function calls', py_type=int, set='min', err=False, sim=True)
            add('g_count', desc='Number of gradient calls', py_type=int, set='min', err=False, sim=True)
            add('h_count', desc='Number of Hessian calls', py_type=int, set='min', err=False, sim=True)
            add('warning', desc='Optimisation warning', py_type=str, set='min', err=False, sim=True)

        The parameter scope is defined by the keyword arguments.


        @keyword min_stats_global:  A flag which if True will cause the parameters to be global.
        @type min_stats_global:     bool
        @keyword min_stats_spin:    A flag which if True will cause the parameters to be spin specific.
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


    def add_model_info(self, scope='spin', model_flag=True, equation_flag=False):
        """Add model specific objects 'model' and 'params'.

        This is the equivalent of calling:

            add('params', scope=scope, desc='The parameters of the model', py_type=list)
            add('model', scope=scope, desc='The model', py_type=str)


        @keyword scope:         The parameter scope.  This can be set to 'global' for parameters located within the global scope of the current data pipe.  Or set to 'spin' for spin specific parameters.  Alternatively the value 'both' indicates that there are both global and specific versions of this parameter.
        @type scope:            str
        @keyword model_flag:    A flag which if True will cause the 'model' structure to be added.
        @type model_flag:       bool
        """

        # Add the model structure.
        if model_flag:
            self.add('model', scope=scope, desc='The model name', py_type=str)

        # The equation information.
        if equation_flag:
            self.add('equation', scope=scope, desc='The model equation', py_type=str)

        # Add the parameter name list structure.
        self.add('params', scope=scope, desc='The parameters of the model', py_type=list)


    def add_peak_intensity(self):
        """Add the peak intensity structure 'peak_intensity'.

        This is the equivalent of calling:

            add('peak_intensity', scope='spin', desc='The peak intensities', py_type=dict, grace_string='\\qPeak intensities\\Q')
        """

        # Add the peak intensity structure.
        self.add('peak_intensity', scope='spin', desc='The peak intensities', py_type=dict, grace_string='\\qPeak intensities\\Q')


    def base_loop(self, set=None, scope=None):
        """An iterator method for looping over all the base parameters.

        @keyword set:   The set of object names to return.  This can be set to 'all' for all names, to 'generic' for generic object names, 'params' for analysis specific parameter names, or to 'min' for minimisation specific object names.
        @type set:      str
        @keyword scope: The scope of the parameter to return.  If not set, then all will be returned.  If set to 'global' or 'spin', then only the parameters within that scope will be returned.
        @type scope:    str or None
        @returns:       The parameter names.
        @rtype:         str
        """

        # Loop over the parameters.
        for name in self._names:
            # Skip the parameter if the set does not match.
            if set == 'generic' and self._set[name] != 'generic':
                continue
            if set == 'params' and self._set[name] != 'params':
                continue
            if set == 'min' and self._set[name] != 'min':
                continue

            # Skip the parameter is outside of the scope.
            if scope == 'global' and self._scope[name] == 'spin':
                continue
            if scope == 'spin' and self._scope[name] == 'global':
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


    def conversion_factor(self, name):
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


    def data_names(self, set='all', scope=None, error_names=False, sim_names=False):
        """Return a list of names of data structures.

        @keyword set:           The set of object names to return.  This can be set to 'all' for all names, to 'generic' for generic object names, 'params' for analysis specific parameter names, or to 'min' for minimisation specific object names.
        @type set:              str
        @keyword scope:         The scope of the parameter to return.  If not set, then all will be returned.  If set to 'global' or 'spin', then only the parameters within that scope will be returned.
        @type scope:            str or None
        @keyword error_names:   A flag which if True will add the error object names as well.
        @type error_names:      bool
        @keyword sim_names:     A flag which if True will add the Monte Carlo simulation object names as well.
        @type sim_names:        bool
        @return:                The list of object names.
        @rtype:                 list of str
        """

        # Initialise.
        names = []

        # Loop over the parameters.
        for name in self.loop(set=set, scope=scope, error_names=error_names, sim_names=sim_names):
            names.append(name)

        # Return the names.
        return names


    def default_value(self, name):
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


    def description(self, name):
        """Return the description of the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The description.
        @rtype:         None or str
        """

        # Skip error and simulation structures.
        if name not in ['ri_data_err'] and (search('_err$', name) or search('_sim$', name)):
            return None

        # Parameter check.
        self.check_param(name)

        # Return the description.
        return self._desc[name]


    def error_flag(self, name):
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


    def grace_string(self, name):
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


    def loop(self, set=None, scope=None, error_names=False, sim_names=False):
        """An iterator method for looping over all the parameters.

        @keyword set:           The set of object names to return.  This can be set to 'all' for all names, to 'generic' for generic object names, 'params' for analysis specific parameter names, or to 'min' for minimisation specific object names.
        @type set:              str
        @keyword scope:         The scope of the parameter to return.  If not set, then all will be returned.  If set to 'global' or 'spin', then only the parameters within that scope will be returned.
        @type scope:            str or None
        @keyword error_names:   A flag which if True will add the error object names as well.
        @type error_names:      bool
        @keyword sim_names:     A flag which if True will add the Monte Carlo simulation object names as well.
        @type sim_names:        bool
        @returns:               The parameter names.
        @rtype:                 str
        """

        # Loop over and yield the parameters.
        for name in self.base_loop(set=set, scope=scope):
            yield name

        # Error names.
        if error_names:
            for name in self.base_loop(set=set):
                if self.error_flag(name):
                    yield name + '_err'

        # Sim names.
        if sim_names:
            for name in self.base_loop(set=set):
                if self.simulation_flag(name):
                    yield name + '_sim'


    def set(self, name):
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


    def simulation_flag(self, name):
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


    def type(self, name):
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


    def units(self, name):
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
