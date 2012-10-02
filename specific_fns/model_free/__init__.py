###############################################################################
#                                                                             #
# Copyright (C) 2007-2012 Edward d'Auvergne                                   #
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
"""The model-free specific code."""


# The available modules.
__all__ = [ 'bmrb',
            'macro_base',
            'main',
            'mf_minimise',
            'molmol',
            'multi_processor_commands',
            'pymol',
            'results'
]

# relax module imports.
from generic_fns import diffusion_tensor, relax_data
from physical_constants import N15_CSA, NH_BOND_LENGTH
from specific_fns.api_base import API_base
from specific_fns.api_common import API_common
from specific_fns.model_free.bmrb import Bmrb
from specific_fns.model_free.main import Model_free_main
from specific_fns.model_free.mf_minimise import Mf_minimise
from specific_fns.model_free.molmol import Molmol
from specific_fns.model_free.pymol import Pymol
from specific_fns.model_free.results import Results


class Model_free(Model_free_main, Mf_minimise, Results, Bmrb, API_base, API_common):
    """Parent class containing all the model-free specific functions."""

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Execute the base class __init__ method.
        super(Model_free, self).__init__()

        # Place methods into the API.
        self.base_data_loop = self._base_data_loop_spin
        self.return_error = self._return_error_relax_data
        self.return_value = self._return_value_general
        self.sim_pack_data = self._sim_pack_relax_data
        self.test_grid_ops = self._test_grid_ops_general

        # Initialise the macro classes.
        self._molmol_macros = Molmol()
        self._pymol_macros = Pymol()

        # Alias the macro creation methods.
        self.pymol_macro = self._pymol_macros.create_macro
        self.molmol_macro = self._molmol_macros.create_macro

        # Set up the global parameters.
        self.PARAMS.add('tm', scope='global', default=diffusion_tensor.default_value('tm'), conv_factor=1e-9, grace_string='\\xt\\f{}\\sm', units='ns', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Diso', scope='global', default=diffusion_tensor.default_value('Diso'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dx', scope='global', default=diffusion_tensor.default_value('Dx'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dy', scope='global', default=diffusion_tensor.default_value('Dy'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dz', scope='global', default=diffusion_tensor.default_value('Dz'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dpar', scope='global', default=diffusion_tensor.default_value('Dpar'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dper', scope='global', default=diffusion_tensor.default_value('Dper'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Da', scope='global', default=diffusion_tensor.default_value('Da'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dratio', scope='global', default=diffusion_tensor.default_value('Dratio'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dr', scope='global', default=diffusion_tensor.default_value('Dr'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('alpha', scope='global', default=diffusion_tensor.default_value('alpha'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('beta', scope='global', default=diffusion_tensor.default_value('beta'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('gamma', scope='global', default=diffusion_tensor.default_value('gamma'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('theta', scope='global', default=diffusion_tensor.default_value('theta'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('phi', scope='global', default=diffusion_tensor.default_value('phi'), py_type=float, set='params', err=True, sim=True)

        # Set up the spin parameters.
        self.PARAMS.add('model', scope='spin', desc='The model', py_type=str)
        self.PARAMS.add('equation', scope='spin', desc='The model equation', py_type=str)
        self.PARAMS.add('params', scope='spin', desc='The model parameters', py_type=list)
        self.PARAMS.add('s2', scope='spin', default=0.8, desc='S2, the model-free generalised order parameter (S2 = S2f.S2s)', py_type=float, set='params', grace_string='\\qS\\v{0.4}\\z{0.71}2\\Q', err=True, sim=True)
        self.PARAMS.add('s2f', scope='spin', default=0.8, desc='S2f, the faster motion model-free generalised order parameter', py_type=float, set='params', grace_string='\\qS\\sf\\N\\h{-0.2}\\v{0.4}\\z{0.71}2\\Q', err=True, sim=True)
        self.PARAMS.add('s2s', scope='spin', default=0.8, desc='S2s, the slower motion model-free generalised order parameter', py_type=float, set='params', grace_string='\\qS\\ss\\N\\h{-0.2}\\v{0.4}\\z{0.71}2\\Q', err=True, sim=True)
        self.PARAMS.add('local_tm', scope='spin', default=10.0 * 1e-9, desc='The spin specific global correlation time (seconds)', py_type=float, set='params', grace_string='\\xt\\f{}\\sm', units='ns', err=True, sim=True)
        self.PARAMS.add('te', scope='spin', default=100.0 * 1e-12, desc='Single motion effective internal correlation time (seconds)', py_type=float, set='params', conv_factor=1e-12, grace_string='\\xt\\f{}\\se', units='ps', err=True, sim=True)
        self.PARAMS.add('tf', scope='spin', default=10.0 * 1e-12, desc='Faster motion effective internal correlation time (seconds)', py_type=float, set='params', conv_factor=1e-12, grace_string='\\xt\\f{}\\sf', units='ps', err=True, sim=True)
        self.PARAMS.add('ts', scope='spin', default=1000.0 * 1e-12, desc='Slower motion effective internal correlation time (seconds)', py_type=float, set='params', conv_factor=1e-12, grace_string='\\xt\\f{}\\ss', units='ps', err=True, sim=True)
        self.PARAMS.add('rex', scope='spin', default=0.0, desc='Chemical exchange relaxation (sigma_ex = Rex / omega**2)', py_type=float, set='params', conv_factor=self._conv_factor_rex, units=self._units_rex, grace_string='\\qR\\sex\\Q', err=True, sim=True)
        self.PARAMS.add('csa', scope='spin', default=N15_CSA, units='ppm', desc='Chemical shift anisotropy (unitless)', py_type=float, set='params', conv_factor=1e-6, grace_string='\\qCSA\\Q', err=True, sim=True)

        # Add the minimisation data.
        self.PARAMS.add_min_data(min_stats_global=True, min_stats_spin=True)

        # Add the relaxation data parameters.
        self.PARAMS.add('ri_data', scope='spin', desc=relax_data.return_data_desc('ri_data'), py_type=dict, err=False, sim=True)
        self.PARAMS.add('ri_data_err', scope='spin', desc=relax_data.return_data_desc('ri_data_err'), py_type=dict, err=False, sim=False)
