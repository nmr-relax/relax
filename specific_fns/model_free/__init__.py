###############################################################################
#                                                                             #
# Copyright (C) 2007-2012 Edward d'Auvergne                                   #
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
from bmrb import Bmrb
from generic_fns import diffusion_tensor
from main import Model_free_main
from mf_minimise import Mf_minimise
from molmol import Molmol
from physical_constants import N15_CSA, NH_BOND_LENGTH
from pymol import Pymol
from results import Results
from specific_fns.api_base import API_base
from specific_fns.api_common import API_common


class Model_free(Model_free_main, Mf_minimise, Results, Bmrb, API_base, API_common):
    """Parent class containing all the model-free specific functions."""

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Place methods into the API.
        self.base_data_loop = self._base_data_loop_spin
        self.return_error = self._return_error_relax_data
        self.return_conversion_factor = self._return_conversion_factor_spin
        self.return_grace_string = self._return_grace_string_spin
        self.return_units = self._return_units_spin
        self.return_value = self._return_value_general
        self.sim_pack_data = self._sim_pack_relax_data
        self.test_grid_ops = self._test_grid_ops_general

        # Initialise the macro classes.
        self._molmol_macros = Molmol()
        self._pymol_macros = Pymol()

        # Alias the macro creation methods.
        self.pymol_macro = self._pymol_macros.create_macro
        self.molmol_macro = self._molmol_macros.create_macro

        # Set up the spin parameters.
        self.SPIN_PARAMS.add('tm', default=diffusion_tensor.default_value('tm'), conv_factor=1e-9, grace_string='\\xt\\f{}\\sm', units='ns')
        self.SPIN_PARAMS.add('Diso', default=diffusion_tensor.default_value('Diso'))
        self.SPIN_PARAMS.add('Dx', default=diffusion_tensor.default_value('Dx'))
        self.SPIN_PARAMS.add('Dy', default=diffusion_tensor.default_value('Dy'))
        self.SPIN_PARAMS.add('Dz', default=diffusion_tensor.default_value('Dz'))
        self.SPIN_PARAMS.add('Dpar', default=diffusion_tensor.default_value('Dpar'))
        self.SPIN_PARAMS.add('Dper', default=diffusion_tensor.default_value('Dper'))
        self.SPIN_PARAMS.add('Da', default=diffusion_tensor.default_value('Da'))
        self.SPIN_PARAMS.add('Dratio', default=diffusion_tensor.default_value('Dratio'))
        self.SPIN_PARAMS.add('alpha', default=diffusion_tensor.default_value('alpha'))
        self.SPIN_PARAMS.add('beta', default=diffusion_tensor.default_value('beta'))
        self.SPIN_PARAMS.add('gamma', default=diffusion_tensor.default_value('gamma'))
        self.SPIN_PARAMS.add('theta', default=diffusion_tensor.default_value('theta'))
        self.SPIN_PARAMS.add('phi', default=diffusion_tensor.default_value('phi'))
        self.SPIN_PARAMS.add('local_tm', default=10.0 * 1e-9, desc='The spin specific global correlation time (seconds)', grace_string='\\xt\\f{}\\sm', units='ns')
        self.SPIN_PARAMS.add('s2', default=0.8, desc='S2, the model-free generalised order parameter (S2 = S2f.S2s)', grace_string='\\qS\\v{0.4}\\z{0.71}2\\Q')
        self.SPIN_PARAMS.add('s2f', default=0.8, desc='S2f, the faster motion model-free generalised order parameter', grace_string='\\qS\\sf\\N\\h{-0.2}\\v{0.4}\\z{0.71}2\\Q')
        self.SPIN_PARAMS.add('s2s', default=0.8, desc='S2s, the slower motion model-free generalised order parameter', grace_string='\\qS\\ss\\N\\h{-0.2}\\v{0.4}\\z{0.71}2\\Q')
        self.SPIN_PARAMS.add('te', default=100.0 * 1e-12, desc='Single motion effective internal correlation time (seconds)', conv_factor=1e-12, grace_string='\\xt\\f{}\\se', units='ps')
        self.SPIN_PARAMS.add('tf', default=10.0 * 1e-12, desc='Faster motion effective internal correlation time (seconds)', conv_factor=1e-12, grace_string='\\xt\\f{}\\sf', units='ps')
        self.SPIN_PARAMS.add('ts', default=1000.0 * 1e-12, desc='Slower motion effective internal correlation time (seconds)', conv_factor=1e-12, grace_string='\\xt\\f{}\\ss', units='ps')
        self.SPIN_PARAMS.add('rex', default=0.0, desc='Chemical exchange relaxation (sigma_ex = Rex / omega**2)', conv_factor=self._conv_factor_rex, units=self._units_rex, grace_string='\\qR\\sex\\Q')
        self.SPIN_PARAMS.add('r', default=NH_BOND_LENGTH, units='Angstrom', desc='Bond length (meters)', conv_factor=1e-10, grace_string='Bond length')
        self.SPIN_PARAMS.add('csa', default=N15_CSA, units='ppm', desc='Chemical shift anisotropy (unitless)', conv_factor=1e-6, grace_string='\\qCSA\\Q')
        self.SPIN_PARAMS.add('heteronuc_type', default='15N', desc='The heteronucleus spin type')
        self.SPIN_PARAMS.add('proton_type', default='1H', desc='The proton spin type')
        self.SPIN_PARAMS.add('model', desc='The model')
        self.SPIN_PARAMS.add('equation', desc='The model equation')
        self.SPIN_PARAMS.add('params', desc='The model parameters')
        self.SPIN_PARAMS.add('xh_vect', desc='XH bond vector')
