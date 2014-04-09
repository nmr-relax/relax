###############################################################################
#                                                                             #
# Copyright (C) 2007-2014 Edward d'Auvergne                                   #
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
"""The module for the Lipari-Szabo model-free parameter list object."""

# relax module imports.
from lib.physical_constants import N15_CSA
from pipe_control import diffusion_tensor, relax_data
from specific_analyses.parameter_object import Param_list
from specific_analyses.model_free.parameters import conv_factor_rex, units_rex


class Model_free_params(Param_list):
    """The Lipari-Szabo model-free parameter list singleton."""

    # Class variable for storing the class instance (for the singleton design pattern).
    _instance = None

    def __init__(self):
        """Define all the parameters of the analysis."""

        # Execute the base class __init__ method.
        Param_list.__init__(self)

        # Add the base data for the models.
        self.add('ri_data', scope='spin', desc=relax_data.return_data_desc('ri_data'), py_type=dict, err=False, sim=True)
        self.add('ri_data_err', scope='spin', desc=relax_data.return_data_desc('ri_data_err'), py_type=dict, err=False, sim=False)

        # Add the model variables.
        self.add_model_info(equation_flag=True)

        # Add up the global model parameters.
        self.add('tm', scope='global', default=diffusion_tensor.default_value('tm'), conv_factor=1e-9, grace_string='\\xt\\f{}\\sm', units='ns', py_type=float, set='params', err=True, sim=True)
        self.add('Diso', scope='global', default=diffusion_tensor.default_value('Diso'), py_type=float, set='params', err=True, sim=True)
        self.add('Dx', scope='global', default=diffusion_tensor.default_value('Dx'), py_type=float, set='params', err=True, sim=True)
        self.add('Dy', scope='global', default=diffusion_tensor.default_value('Dy'), py_type=float, set='params', err=True, sim=True)
        self.add('Dz', scope='global', default=diffusion_tensor.default_value('Dz'), py_type=float, set='params', err=True, sim=True)
        self.add('Dpar', scope='global', default=diffusion_tensor.default_value('Dpar'), py_type=float, set='params', err=True, sim=True)
        self.add('Dper', scope='global', default=diffusion_tensor.default_value('Dper'), py_type=float, set='params', err=True, sim=True)
        self.add('Da', scope='global', default=diffusion_tensor.default_value('Da'), py_type=float, set='params', err=True, sim=True)
        self.add('Dratio', scope='global', default=diffusion_tensor.default_value('Dratio'), py_type=float, set='params', err=True, sim=True)
        self.add('Dr', scope='global', default=diffusion_tensor.default_value('Dr'), py_type=float, set='params', err=True, sim=True)
        self.add('alpha', scope='global', default=diffusion_tensor.default_value('alpha'), py_type=float, set='params', err=True, sim=True)
        self.add('beta', scope='global', default=diffusion_tensor.default_value('beta'), py_type=float, set='params', err=True, sim=True)
        self.add('gamma', scope='global', default=diffusion_tensor.default_value('gamma'), py_type=float, set='params', err=True, sim=True)
        self.add('theta', scope='global', default=diffusion_tensor.default_value('theta'), py_type=float, set='params', err=True, sim=True)
        self.add('phi', scope='global', default=diffusion_tensor.default_value('phi'), py_type=float, set='params', err=True, sim=True)

        # Add up the spin model parameters.
        self.add('s2', scope='spin', default=0.8, desc='S2, the model-free generalised order parameter (S2 = S2f.S2s)', py_type=float, set='params', grace_string='\\qS\\v{0.4}\\z{0.71}2\\Q', err=True, sim=True)
        self.add('s2f', scope='spin', default=0.8, desc='S2f, the faster motion model-free generalised order parameter', py_type=float, set='params', grace_string='\\qS\\sf\\N\\h{-0.2}\\v{0.4}\\z{0.71}2\\Q', err=True, sim=True)
        self.add('s2s', scope='spin', default=0.8, desc='S2s, the slower motion model-free generalised order parameter', py_type=float, set='params', grace_string='\\qS\\ss\\N\\h{-0.2}\\v{0.4}\\z{0.71}2\\Q', err=True, sim=True)
        self.add('local_tm', scope='spin', default=10.0 * 1e-9, desc='The spin specific global correlation time (seconds)', py_type=float, set='params', grace_string='\\xt\\f{}\\sm', units='ns', err=True, sim=True)
        self.add('te', scope='spin', default=100.0 * 1e-12, desc='Single motion effective internal correlation time (seconds)', py_type=float, set='params', conv_factor=1e-12, grace_string='\\xt\\f{}\\se', units='ps', err=True, sim=True)
        self.add('tf', scope='spin', default=10.0 * 1e-12, desc='Faster motion effective internal correlation time (seconds)', py_type=float, set='params', conv_factor=1e-12, grace_string='\\xt\\f{}\\sf', units='ps', err=True, sim=True)
        self.add('ts', scope='spin', default=1000.0 * 1e-12, desc='Slower motion effective internal correlation time (seconds)', py_type=float, set='params', conv_factor=1e-12, grace_string='\\xt\\f{}\\ss', units='ps', err=True, sim=True)
        self.add('rex', scope='spin', default=0.0, desc='Chemical exchange relaxation (sigma_ex = Rex / omega**2)', py_type=float, set='params', conv_factor=conv_factor_rex, units=units_rex, grace_string='\\qR\\sex\\Q', err=True, sim=True)
        self.add_csa(default=N15_CSA, set='params', err=True, sim=True)

        # Add the minimisation data.
        self.add_min_data(min_stats_global=True, min_stats_spin=True)
