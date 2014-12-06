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
from math import pi
from re import search
from types import FunctionType, MethodType

# relax module imports.
from lib.errors import RelaxError
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container


def da_lower(incs=None, model_info=None):
    """Determine the lower grid bound for the Da diffusion parameter.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The model information from model_loop().
    @type model_info:       unknown
    @return:                The lower grid search bound for the Da diffusion parameter.
    @rtype:                 float
    """

    # Return the lower bound.
    if (cdp.diff_tensor.type == 'spheroid' and cdp.diff_tensor.spheroid_type == 'prolate') or cdp.diff_tensor.type == 'ellipsoid':
        return 0.0
    else:
        return -1e7


def da_upper(incs=None, model_info=None):
    """Determine the upper grid bound for the Da diffusion parameter.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The model information from model_loop().
    @type model_info:       unknown
    @return:                The upper grid search bound for the Da diffusion parameter.
    @rtype:                 float
    """

    # Return the upper bound.
    if cdp.diff_tensor.type == 'spheroid' and cdp.diff_tensor.spheroid_type == 'oblate':
        return 0.0
    else:
        return 1e7



class Param_list(object):
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
        self._grid_lower = {}
        self._grid_upper = {}
        self._set = {}
        self._err = {}
        self._scaling = {}
        self._sim = {}

        # Add some spin specific objects.
        if self.spin_data:
            self._add(
                'select',
                scope = 'spin',
                desc = 'The spin selection flag',
                py_type = bool,
                sim = True
            )
            self._add(
                'fixed',
                scope = 'spin',
                desc = 'The fixed flag',
                py_type = bool
            )

        # Default user function documentation.
        self._uf_title = "Parameters"
        self._uf_table_caption = "Parameters"
        self._uf_docs = {}

        # Set the initialised flag.
        self._initialised = True


    def __new__(cls, *args, **kargs):
        """Replacement function for implementing the singleton design pattern."""

        # First initialisation.
        if cls._instance is None:
            # Create a new instance.
            cls._instance = object.__new__(cls, *args, **kargs)

            # Add an initialisation flag.
            cls._instance._initialised = False

        # Already initialised, so return the instance.
        return cls._instance


    def _add(self, name, scope=None, string=None, default=None, units=None, desc=None, py_type=None, set='all', conv_factor=None, scaling=1.0, grid_lower=None, grid_upper=None, grace_string=None, err=False, sim=False):
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
        @keyword set:           The set of object names.  This can be set to 'all' for all names, to 'fixed' for parameter of the model which are permanently fixed, to 'params' for parameter of the model which are optimised or calculated, or to 'min' for minimisation specific object names.
        @type set:              str
        @keyword conv_factor:   The factor of conversion between different parameter units.
        @type conv_factor:      None, float or func
        @keyword scaling:       The diagonal scaling factor for optimisation.
        @type scaling:          float or function
        @keyword grid_lower:    The lower bound for the grid search.
        @type grid_lower:       int or function
        @keyword grid_upper:    The upper bound for the grid search.
        @type grid_upper:       int or function
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
        allowed_sets = ['all', 'fixed', 'params', 'min']
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
        self._grid_lower[name] = grid_lower
        self._grid_upper[name] = grid_upper
        self._scaling[name] = scaling

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


    def _add_align_data(self):
        """Add the PCS and RDC data."""

        # Add the data.
        self._add(
            'pcs',
            scope = 'spin',
            grace_string = 'Pseudo-contact shift',
            units = 'ppm',
            desc = 'The pseudo-contact shift (PCS)',
            py_type = float
        )
        self._add(
            'rdc',
            scope = 'spin',
            grace_string = 'Residual dipolar coupling',
            units = 'Hz',
            desc = 'The residual dipolar coupling (RDC)',
            py_type = float
        )


    def _add_align_tensor(self):
        """Add the alignment tensor parameters."""

        # Add the parameters.
        self._add(
            'Axx',
            scope = 'global',
            desc = 'The Axx component of the alignment tensor',
            py_type = float,
            set = 'params',
            grid_lower = -1e-3,
            grid_upper = 1e-3,
            grace_string = '\\qA\\sxx\\N',
            err = True,
            sim = True
        )
        self._add(
            'Ayy',
            scope = 'global',
            desc = 'The Ayy component of the alignment tensor',
            py_type = float,
            set = 'params',
            grid_lower = -1e-3,
            grid_upper = 1e-3,
            grace_string = '\\qA\\syy\\N',
            err = True,
            sim = True
        )
        self._add(
            'Axy',
            scope = 'global',
            desc = 'The Axy component of the alignment tensor',
            py_type = float,
            set = 'params',
            grid_lower = -1e-3,
            grid_upper = 1e-3,
            grace_string = '\\qA\\sxy\\N',
            err = True,
            sim = True
        )
        self._add(
            'Axz',
            scope = 'global',
            desc = 'The Axz component of the alignment tensor',
            py_type = float,
            set = 'params',
            grid_lower = -1e-3,
            grid_upper = 1e-3,
            grace_string = '\\qA\\sxz\\N',
            err = True,
            sim = True
        )
        self._add(
            'Ayz',
            scope = 'global',
            desc = 'The Ayz component of the alignment tensor',
            py_type = float,
            set = 'params',
            grid_lower = -1e-3,
            grid_upper = 1e-3,
            grace_string = '\\qA\\syz\\N',
            err = True,
            sim = True
        )


    def _add_csa(self, default=None, set='fixed', err=False, sim=False):
        """Add the CSA parameter 'csa'.

        @keyword default:       The default CSA value.
        @type default:          float
        @keyword set:           The set of object names.  This can be set to 'all' for all names, to 'fixed' for parameter of the model which are permanently fixed, to 'params' for parameter of the model which are optimised or calculated, or to 'min' for minimisation specific object names.
        @type set:              str
        @keyword err:           A flag which if True indicates that the 'csa_err' error data structure can exist.
        @type err:              bool
        @keyword sim:           A flag which if True indicates that the 'csa_sim' Monte Carlo simulation data structure can exist.
        @type sim:              bool
        """

        # Add the CSA structure.
        self._add(
            'csa',
            scope = 'spin',
            default = default,
            units = 'ppm',
            desc = 'Chemical shift anisotropy (unitless)',
            py_type = float,
            set = set,
            scaling = 1e-4,
            grid_lower = -120 * 1e-6,
            grid_upper = -200 * 1e-6,
            conv_factor = 1e-6,
            grace_string = '\\qCSA\\Q',
            err = err,
            sim = sim
        )


    def _add_diffusion_params(self):
        """Add the Brownian rotational diffusion parameters to the list."""

        # Add the CSA structure.
        self._add(
            'tm',
            scope = 'global',
            default = 10.0 * 1e-9,
            grace_string = '\\xt\\f{}\\sm',
            units = 'ns',
            desc = 'Global correlation time',
            py_type = float,
            set = 'params',
            scaling = 1e-12,
            grid_lower = 1.0 * 1e-9,
            grid_upper = 12.0 * 1e-9,
            conv_factor = 1e-9,
            err = True,
            sim = True
        )
        self._add(
            'Diso',
            scope = 'global',
            default = 1.666 * 1e7,
            units = '1e6 1/s',
            desc = 'Isotropic component of the diffusion tensor',
            py_type = float,
            set = 'params',
            conv_factor = 1e6,
            err = True,
            sim = True
        )
        self._add(
            'Dx',
            scope = 'global',
            default = 1.666 * 1e7,
            units = '1e6 1/s',
            desc = 'Eigenvalue associated with the x-axis of the diffusion tensor',
            py_type = float,
            set = 'params',
            conv_factor = 1e6,
            err = True,
            sim = True
        )
        self._add(
            'Dy',
            scope = 'global',
            default = 1.666 * 1e7,
            units = '1e6 1/s',
            desc = 'Eigenvalue associated with the y-axis of the diffusion tensor',
            py_type = float,
            set = 'params',
            conv_factor = 1e6,
            err = True,
            sim = True
        )
        self._add(
            'Dz',
            scope = 'global',
            default = 1.666 * 1e7,
            units = '1e6 1/s',
            desc = 'Eigenvalue associated with the z-axis of the diffusion tensor',
            py_type = float,
            set = 'params',
            conv_factor = 1e6,
            err = True,
            sim = True
        )
        self._add(
            'Dpar',
            scope = 'global',
            default = 1.666 * 1e7,
            units = '1e6 1/s',
            desc = 'Diffusion coefficient parallel to the major axis of the spheroid diffusion tensor',
            py_type = float,
            set = 'params',
            conv_factor = 1e6,
            err = True,
            sim = True
        )
        self._add(
            'Dper',
            scope = 'global',
            default = 1.666 * 1e7,
            units = '1e6 1/s',
            desc = 'Diffusion coefficient perpendicular to the major axis of the spheroid diffusion tensor',
            py_type = float,
            set = 'params',
            conv_factor = 1e6,
            err = True,
            sim = True
        )
        self._add(
            'Da',
            scope = 'global',
            default = 0.0,
            units = '1e6 1/s',
            desc = 'Anisotropic component of the diffusion tensor',
            py_type = float,
            set = 'params',
            scaling = 1e7,
            grid_lower = da_lower,
            grid_upper = da_upper,
            conv_factor = 1e6,
            err = True,
            sim = True
        )
        self._add(
            'Dr',
            scope = 'global',
            default = 0.0,
            desc = 'Rhombic component of the diffusion tensor',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = 1.0,
            err = True,
            sim = True
        )
        self._add(
            'Dratio',
            scope = 'global',
            default = 1.0,
            desc = 'Ratio of the parallel and perpendicular components of the spheroid diffusion tensor',
            py_type = float,
            set = 'params',
            err = True,
            sim = True
        )
        self._add(
            'alpha',
            scope = 'global',
            default = 0.0,
            units = 'deg',
            desc = 'The first Euler angle of the ellipsoid diffusion tensor',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = pi,
            conv_factor = (2.0*pi) / 360.0,
            err = True,
            sim = True
        )
        self._add(
            'beta',
            scope = 'global',
            default = 0.0,
            units = 'deg',
            desc = 'The second Euler angle of the ellipsoid diffusion tensor',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = pi,
            conv_factor = (2.0*pi) / 360.0,
            err = True,
            sim = True
        )
        self._add(
            'gamma',
            scope = 'global',
            default = 0.0,
            units = 'deg',
            desc = 'The third Euler angle of the ellipsoid diffusion tensor',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = pi,
            conv_factor = (2.0*pi) / 360.0,
            err = True,
            sim = True
        )
        self._add(
            'theta',
            scope = 'global',
            default = 0.0,
            units = 'deg',
            desc = 'The polar angle defining the major axis of the spheroid diffusion tensor',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = pi,
            conv_factor = (2.0*pi) / 360.0,
            err = True,
            sim = True
        )
        self._add(
            'phi',
            scope = 'global',
            default = 0.0,
            units = 'deg',
            desc = 'The azimuthal angle defining the major axis of the spheroid diffusion tensor',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = pi,
            conv_factor = (2.0*pi) / 360.0,
            err = True,
            sim = True
        )


    def _add_min_data(self, min_stats_global=False, min_stats_spin=False):
        """Add minimisation specific objects.

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
            self._add(
                'chi2',
                scope = scope,
                desc = 'Chi-squared value',
                py_type = float,
                set = 'min',
                grace_string = '\\xc\\S2',
                err = False,
                sim = True
            )
            self._add(
                'iter',
                scope = scope,
                desc = 'Optimisation iterations',
                py_type = int,
                set = 'min',
                grace_string = 'Iteration count',
                err = False,
                sim = True
            )
            self._add(
                'f_count',
                scope = scope,
                desc = 'Number of function calls',
                py_type = int,
                set = 'min',
                grace_string = 'Function call count',
                err = False,
                sim = True
            )
            self._add(
                'g_count',
                scope = scope,
                desc = 'Number of gradient calls',
                py_type = int,
                set = 'min',
                grace_string = 'Gradient call count',
                err = False,
                sim = True
            )
            self._add(
                'h_count',
                scope = scope,
                desc = 'Number of Hessian calls',
                py_type = int,
                set = 'min',
                grace_string = 'Hessian call count',
                err = False,
                sim = True
            )
            self._add(
                'warning',
                scope = scope,
                desc = 'Optimisation warning',
                py_type = str,
                set = 'min',
                err = False,
                sim = True
            )


    def _add_model_info(self, scope='spin', model_flag=True, equation_flag=False):
        """Add model specific objects 'model' and 'params'.

        @keyword scope:         The parameter scope.  This can be set to 'global' for parameters located within the global scope of the current data pipe.  Or set to 'spin' for spin specific parameters.  Alternatively the value 'both' indicates that there are both global and specific versions of this parameter.
        @type scope:            str
        @keyword model_flag:    A flag which if True will cause the 'model' structure to be added.
        @type model_flag:       bool
        """

        # Add the model structure.
        if model_flag:
            self._add(
                'model',
                scope = scope,
                desc = 'The model name',
                py_type = str
            )

        # The equation information.
        if equation_flag:
            self._add(
                'equation',
                scope = scope,
                desc = 'The model equation',
                py_type = str
            )

        # Add the parameter name list structure.
        self._add(
            'params',
            scope = scope,
            desc = 'The parameters of the model',
            py_type = list
        )


    def _add_peak_intensity(self):
        """Add the peak intensity structure 'peak_intensity'."""

        # Add the peak intensity structure.
        self._add(
            'peak_intensity',
            scope = 'spin',
            desc = 'The peak intensities',
            py_type = dict,
            grace_string = '\\qPeak intensities\\Q'
        )


    def _add_sn_ratio(self):
        """Add the signal to noise ratio structure 'sn_ratio'."""

        # Add the peak intensity structure.
        self._add(
            'sn_ratio',
            scope = 'spin',
            desc = 'The signal to noise ratios',
            py_type = dict,
            grace_string = '\\qS/N ratio\\Q'
        )


    def _set_uf_title(self, title):
        """Set the title for the user function documentation.

        @param title:   The title to use in the user function docstrings.
        @type title:    str
        """

        # Store the text.
        self._uf_title = title


    def _uf_param_table(self, label=None, caption=None, scope='spin', sets=['params', 'fixed'], default=False, units=False, type=False):
        """"Create the parameter documentation for the user function docstrings.

        @keyword label:     The label of the table.  This is used to identify replicated tables, and is also used in the table referencing in the LaTeX compilation of the user manual.  If this label is already used, the corresponding pre-constructed documentation object will be returned.
        @type label:        str
        @keyword caption:   The caption for the table.
        @type caption:      str
        @keyword scope:     The parameter scope to restrict the table to, defaulting to 'spin'.
        @type scope:        str or None
        @keyword sets:      The parameter sets to restrict the table to.  If not given, then all parameters of the 'params' and 'fixed' sets will be added.  This can be set to 'all' for all names, to 'fixed' for parameter of the model which are permanently fixed, to 'params' for parameter of the model which are optimised or calculated, or to 'min' for minimisation specific object names.
        @type sets:         list of str
        @keyword default:   A flag which if True will cause the default parameter value to be included in the table.
        @type default:      bool
        @keyword units:     A flag which if True will cause the units to be included in the table.
        @type units:        bool
        @keyword type:      A flag which if True will cause the parameter type to be included in the table.
        @type type:         bool
        @return:            The parameter documentation.
        @rtype:             Desc_container instance
        """

        # Sanity checks.
        if label == None:
            raise RelaxError("The table identifying label must be supplied.")
        if label in self._uf_docs:
            raise RelaxError("The table identifying label '%s' already exists." % label)

        # Initialise the documentation object.
        self._uf_docs[label] = Desc_container(self._uf_title)

        # The parameter table.
        table = uf_tables.add_table(label=label, caption=caption)

        # Add the headings.
        headings = ["Name", "Description"]
        if default:
            headings.append("Default")
        if units:
            headings.append("Units")
        if type:
            headings.append("Type")
        table.add_headings(headings)

        # Add each parameter, first of the parameter set, then the 'generic' set.
        for set in sets:
            for param in self.loop(set=set):
                # Limit the scope.
                if scope and self.scope(param) != scope:
                    continue

                row = []
                row.append(param)
                row.append(self.description(param))
                if default:
                    row.append("%s" % self.default_value(param))
                if units:
                    row.append("%s" % self.units(param))
                if type:
                    row.append("%s" % self.type_string(param))
                table.add_row(row)

        # Add the table to the documentation object.
        self._uf_docs[label].add_table(table.label)

        # Return the documentation object so that additional text can be added after the table.
        return self._uf_docs[label]


    def _uf_doc_loop(self, tables=None):
        """Generator method for looping over and yielding the user function parameter documentation.

        @keyword tables:    The list of tables to loop over.  If None, then all tables will be yielded.
        @type tables:       list of str or None
        @return:            The user function documentation for each table.
        @rtype:             Desc_container instance
        """

        # No tables supplied.
        if tables == None:
            tables = sorted(self._uf_docs.keys())

        # Loop over the tables, yielding the documentation objects.
        for table in tables:
            yield self._uf_docs[table]


    def base_loop(self, set=None, scope=None):
        """An iterator method for looping over all the base parameters.

        @keyword set:   The set of object names.  This can be set to 'all' for all names, to 'fixed' for parameter of the model which are permanently fixed, to 'params' for parameter of the model which are optimised or calculated, or to 'min' for minimisation specific object names.
        @type set:      str
        @keyword scope: The scope of the parameter to return.  If not set, then all will be returned.  If set to 'global' or 'spin', then only the parameters within that scope will be returned.
        @type scope:    str or None
        @returns:       The parameter names.
        @rtype:         str
        """

        # Loop over the parameters.
        for name in self._names:
            # Skip the parameter if the set does not match.
            if set == 'fixed' and self._set[name] != 'fixed':
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

        @keyword set:           The set of object names.  This can be set to 'all' for all names, to 'fixed' for parameter of the model which are permanently fixed, to 'params' for parameter of the model which are optimised or calculated, or to 'min' for minimisation specific object names.
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


    def grid_lower(self, name, incs=None, model_info=None):
        """Return the default lower grid bound for the parameter.

        @param name:            The name of the parameter.
        @type name:             str
        @keyword incs:          The number of grid search increments.  This is used by some of the bound determining functions.
        @type incs:             int
        @keyword model_info:    The model information from the model_loop() specific API method.  If the lower bound is a function, this information is sent into it.
        @type model_info:       int
        @return:                The lower bound for the grid search.
        @rtype:                 int
        """

        # Parameter check.
        self.check_param(name)

        # Call any function or method.
        if isinstance(self._grid_lower[name], FunctionType) or isinstance(self._grid_lower[name], MethodType):
            return self._grid_lower[name](incs=incs, model_info=model_info)

        # Return the value.
        return self._grid_lower[name]


    def grid_upper(self, name, incs=None, model_info=None):
        """Return the default upper grid bound for the parameter.

        @param name:            The name of the parameter.
        @type name:             str
        @keyword incs:          The number of grid search increments.  This is used by some of the bound determining functions.
        @type incs:             int
        @keyword model_info:    The model information from the model_loop() specific API method.  If the upper bound is a function, this information is sent into it.
        @type model_info:       int
        @return:                The upper bound for the grid search.
        @rtype:                 int
        """

        # Parameter check.
        self.check_param(name)

        # Call any function or method.
        if isinstance(self._grid_upper[name], FunctionType) or isinstance(self._grid_upper[name], MethodType):
            return self._grid_upper[name](incs=incs, model_info=model_info)

        # Return the value.
        return self._grid_upper[name]


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


    def is_spin_param(self, name):
        """Determine whether the given parameter is spin specific.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        True if the parameter is spin specific, False otherwise.
        @rtype:         bool
        """

        # Use the scope.
        if self.scope(name) == 'spin':
            return True
        else:
            return False


    def loop(self, set=None, scope=None, error_names=False, sim_names=False):
        """An iterator method for looping over all the parameters.

        @keyword set:           The set of object names.  This can be set to 'all' for all names, to 'fixed' for parameter of the model which are permanently fixed, to 'params' for parameter of the model which are optimised or calculated, or to 'min' for minimisation specific object names.
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


    def scaling(self, name, model_info=None):
        """Return the scaling factor for the parameter.

        @param model_info:  The model information from the model_loop() specific API method.  If the scaling factor is a function, this information is sent into it.
        @type model_info:   int
        @param name:        The name of the parameter.
        @type name:         str
        @return:            The scaling factor for optimisation.
        @rtype:             int
        """

        # Parameter check.
        self.check_param(name)

        # Call any function or method.
        if isinstance(self._scaling[name], FunctionType) or isinstance(self._scaling[name], MethodType):
            return self._scaling[name](model_info)

        # Return the scaling factor.
        return self._scaling[name]


    def scope(self, name):
        """Return the parameter scope.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The scope.  This is 'global' for parameters located within the global scope of the current data pipe.  Or 'spin' for spin specific parameters.  Alternatively the value 'both' indicates that there are both global and specific versions of this parameter.
        @rtype:         str
        """

        # Parameter check.
        self.check_param(name)

        # Return the Python type.
        return self._scope[name]


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


    def type_string(self, name):
        """Return the Python type for the parameter as a string representation.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The Python type.
        @rtype:         Python type object
        """

        # Parameter check.
        self.check_param(name)

        # The text representation.
        text = repr(self._py_types[name])

        # Return only the part in quotes.
        return text.split("'")[1]


    def uf_doc(self, label=None, caption=None, scope='spin', default=False, units=False, type=False):
        """"Create the parameter documentation for the user function docstrings.

        @keyword label:     The label of the table to return.
        @type label:        str
        @return:            The parameter documentation.
        @rtype:             Desc_container instance
        """

        # Sanity check.
        if label == None:
            raise RelaxError("The table identifying label must be supplied.")
        if label not in self._uf_docs:
            raise RelaxError("The table identifying label '%s' does not exist." % label)

        # Return the documentation.
        return self._uf_docs[label]


    def units(self, name):
        """Return the units string for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The units string.  If no unit is present, the empty string will be returned.
        @rtype:         str
        """

        # Parameter check.
        self.check_param(name)

        # Function.
        if isinstance(self._units[name], FunctionType) or isinstance(self._units[name], MethodType):
            unit = self._units[name]()

        # The value.
        else:
            unit = self._units[name]

        # Convert None to an empty string.
        if unit == None:
            unit = ''

        # Return the units.
        return unit
