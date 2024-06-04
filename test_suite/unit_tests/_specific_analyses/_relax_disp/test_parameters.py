###############################################################################
#                                                                             #
# Copyright (C) 2019 Edward d'Auvergne                                        #
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

# Python module imports.
from copy import deepcopy
from numpy import array, array_equal, diag, float64

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from data_store.mol_res_spin import SpinContainer
from lib.dispersion.variables import MODEL_LIST_FULL, \
    MODEL_PARAMS, \
    MODEL_R2EFF, \
    MODEL_NOREX, \
    MODEL_LM63, \
    MODEL_LM63_3SITE, \
    MODEL_CR72, \
    MODEL_CR72_FULL, \
    MODEL_IT99, \
    MODEL_TSMFK01, \
    MODEL_B14, \
    MODEL_B14_FULL, \
    MODEL_M61, \
    MODEL_M61B, \
    MODEL_DPL94, \
    MODEL_TP02, \
    MODEL_TAP03, \
    MODEL_MP05, \
    MODEL_NS_CPMG_2SITE_3D, \
    MODEL_NS_CPMG_2SITE_3D_FULL, \
    MODEL_NS_CPMG_2SITE_STAR, \
    MODEL_NS_CPMG_2SITE_STAR_FULL, \
    MODEL_NS_CPMG_2SITE_EXPANDED, \
    MODEL_NS_R1RHO_2SITE, \
    MODEL_NS_R1RHO_3SITE, \
    MODEL_NS_R1RHO_3SITE_LINEAR, \
    MODEL_MMQ_CR72, \
    MODEL_NS_MMQ_2SITE, \
    MODEL_NS_MMQ_3SITE, \
    MODEL_NS_MMQ_3SITE_LINEAR, \
    MODEL_EXP_TYPE_R2EFF, \
    MODEL_EXP_TYPE_NOREX, \
    MODEL_EXP_TYPE_LM63, \
    MODEL_EXP_TYPE_LM63_3SITE, \
    MODEL_EXP_TYPE_CR72, \
    MODEL_EXP_TYPE_CR72_FULL, \
    MODEL_EXP_TYPE_TSMFK01, \
    MODEL_EXP_TYPE_TSMFK01, \
    MODEL_EXP_TYPE_B14, \
    MODEL_EXP_TYPE_B14_FULL, \
    MODEL_EXP_TYPE_M61, \
    MODEL_EXP_TYPE_M61B, \
    MODEL_EXP_TYPE_DPL94, \
    MODEL_EXP_TYPE_TP02, \
    MODEL_EXP_TYPE_TAP03, \
    MODEL_EXP_TYPE_MP05, \
    MODEL_EXP_TYPE_NS_CPMG_2SITE_3D, \
    MODEL_EXP_TYPE_NS_CPMG_2SITE_3D_FULL, \
    MODEL_EXP_TYPE_NS_CPMG_2SITE_STAR, \
    MODEL_EXP_TYPE_NS_CPMG_2SITE_STAR_FULL, \
    MODEL_EXP_TYPE_NS_CPMG_2SITE_EXPANDED, \
    MODEL_EXP_TYPE_NS_R1RHO_2SITE, \
    MODEL_EXP_TYPE_NS_R1RHO_3SITE, \
    MODEL_EXP_TYPE_NS_R1RHO_3SITE_LINEAR, \
    MODEL_EXP_TYPE_MMQ_CR72, \
    MODEL_EXP_TYPE_NS_MMQ_2SITE, \
    MODEL_EXP_TYPE_NS_MMQ_3SITE, \
    MODEL_EXP_TYPE_NS_MMQ_3SITE_LINEAR
from specific_analyses.relax_disp.parameters import linear_constraints, loop_parameters, param_conversion, param_num
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_parameters(UnitTestCase):
    """Unit tests for the functions of the specific_analyses.relax_disp.parameters module."""

    def setUp(self):
        """Setup some structures for the unit tests."""

        # Create a dispersion data pipe.
        ds.add(pipe_name='testing', pipe_type='relax_disp')

        # The experiment types for all models.
        self.exp_type = {
            MODEL_R2EFF: MODEL_EXP_TYPE_R2EFF,
            MODEL_NOREX: MODEL_EXP_TYPE_NOREX,
            MODEL_LM63: MODEL_EXP_TYPE_LM63,
            MODEL_LM63_3SITE: MODEL_EXP_TYPE_LM63_3SITE,
            MODEL_CR72: MODEL_EXP_TYPE_CR72,
            MODEL_CR72_FULL: MODEL_EXP_TYPE_CR72_FULL,
            MODEL_IT99: MODEL_EXP_TYPE_TSMFK01,
            MODEL_TSMFK01: MODEL_EXP_TYPE_TSMFK01,
            MODEL_B14: MODEL_EXP_TYPE_B14,
            MODEL_B14_FULL: MODEL_EXP_TYPE_B14_FULL,
            MODEL_M61: MODEL_EXP_TYPE_M61,
            MODEL_M61B: MODEL_EXP_TYPE_M61B,
            MODEL_DPL94: MODEL_EXP_TYPE_DPL94,
            MODEL_TP02: MODEL_EXP_TYPE_TP02,
            MODEL_TAP03: MODEL_EXP_TYPE_TAP03,
            MODEL_MP05: MODEL_EXP_TYPE_MP05,
            MODEL_NS_CPMG_2SITE_3D: MODEL_EXP_TYPE_NS_CPMG_2SITE_3D,
            MODEL_NS_CPMG_2SITE_3D_FULL: MODEL_EXP_TYPE_NS_CPMG_2SITE_3D_FULL,
            MODEL_NS_CPMG_2SITE_STAR: MODEL_EXP_TYPE_NS_CPMG_2SITE_STAR,
            MODEL_NS_CPMG_2SITE_STAR_FULL: MODEL_EXP_TYPE_NS_CPMG_2SITE_STAR_FULL,
            MODEL_NS_CPMG_2SITE_EXPANDED: MODEL_EXP_TYPE_NS_CPMG_2SITE_EXPANDED,
            MODEL_NS_R1RHO_2SITE: MODEL_EXP_TYPE_NS_R1RHO_2SITE,
            MODEL_NS_R1RHO_3SITE: MODEL_EXP_TYPE_NS_R1RHO_3SITE,
            MODEL_NS_R1RHO_3SITE_LINEAR: MODEL_EXP_TYPE_NS_R1RHO_3SITE_LINEAR,
            MODEL_MMQ_CR72: MODEL_EXP_TYPE_MMQ_CR72,
            MODEL_NS_MMQ_2SITE: MODEL_EXP_TYPE_NS_MMQ_2SITE,
            MODEL_NS_MMQ_3SITE: MODEL_EXP_TYPE_NS_MMQ_3SITE,
            MODEL_NS_MMQ_3SITE_LINEAR: MODEL_EXP_TYPE_NS_MMQ_3SITE_LINEAR
        }


    def test_linear_constraints_clustered_spins(self):
        """Test the specific_analyses.relax_disp.parameters.linear_constraints() function for a cluster of 2 spins."""

        # The expected parameter information.
        expected = {
            MODEL_R2EFF: {
                'scaling_matrix': diag(array([1, 1], float64)),
                'A': array(
                    [[ 1,  0],
                     [-1,  0],
                     [ 0,  1],
                     [ 0, -1]],
                float64),
                'b': array([0, -200, 0, -200], float64)
            },
            MODEL_NOREX: {
                'scaling_matrix': diag(array([10, 10], float64)),
                'A': array(
                    [[ 1,  0],
                     [-1,  0],
                     [ 0,  1],
                     [ 0, -1]],
                float64),
                'b': array([0, -20, 0, -20], float64)
            },
            MODEL_LM63: { # ['r2', 'phi_ex', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0],
                     [-1,  0, 0, 0,  0],
                     [ 0,  1, 0, 0,  0],
                     [ 0, -1, 0, 0,  0],
                     [ 0,  0, 1, 0,  0],
                     [ 0,  0, 0, 1,  0],
                     [ 0,  0, 0, 0,  1],
                     [ 0,  0, 0, 0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, 0, -200], float64)
            },
            MODEL_LM63_3SITE: { # ['r2', 'phi_ex_B', 'phi_ex_C', 'kB', 'kC']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 1, 10000, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0, 0, 0,  0,  0],
                     [-1,  0, 0, 0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0, 0, 0,  0,  0],
                     [ 0, -1, 0, 0, 0, 0,  0,  0],
                     [ 0,  0, 1, 0, 0, 0,  0,  0],
                     [ 0,  0, 0, 1, 0, 0,  0,  0],
                     [ 0,  0, 0, 0, 1, 0,  0,  0],
                     [ 0,  0, 0, 0, 0, 1,  0,  0],
                     [ 0,  0, 0, 0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, 0, 0, 0, -200, 0, -200], float64)
            },
            MODEL_CR72: { # ['r2', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0,  0],
                     [-1,  0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0,  0,  0],
                     [ 0, -1, 0, 0,  0,  0],
                     [ 0,  0, 1, 0,  0,  0],
                     [ 0,  0, 0, 1,  0,  0],
                     [ 0,  0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_CR72_FULL: { # ['r2a', 'r2b', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0,  0,  0, 0,  0,  0,  0],
                     [-1,  0,  0,  0, 0,  0,  0,  0],
                     [ 0,  1,  0,  0, 0,  0,  0,  0],
                     [ 0, -1,  0,  0, 0,  0,  0,  0],
                     [ 0,  0,  1,  0, 0,  0,  0,  0],
                     [ 0,  0, -1,  0, 0,  0,  0,  0],
                     [ 0,  0,  0,  1, 0,  0,  0,  0],
                     [ 0,  0,  0, -1, 0,  0,  0,  0],
                     [ 0,  0,  0,  0, 1,  0,  0,  0],
                     [ 0,  0,  0,  0, 0,  1,  0,  0],
                     [ 0,  0,  0,  0, 0,  0, -1,  0],
                     [ 0,  0,  0,  0, 0,  0,  1,  0],
                     [ 0,  0,  0,  0, 0,  0,  0,  1],
                     [ 0,  0,  0,  0, 0,  0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_IT99: { # ['r2', 'dw', 'pA', 'tex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 1e-4], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0, 0],
                     [-1,  0, 0, 0,  0, 0],
                     [ 0,  1, 0, 0,  0, 0],
                     [ 0, -1, 0, 0,  0, 0],
                     [ 0,  0, 1, 0,  0, 0],
                     [ 0,  0, 0, 1,  0, 0],
                     [ 0,  0, 0, 0, -1, 0],
                     [ 0,  0, 0, 0,  1, 0],
                     [ 0,  0, 0, 0,  0, 1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, -1, 0.5, 0], float64)
            },
            MODEL_TSMFK01: { # ['r2a', 'dw', 'k_AB']
                'scaling_matrix': diag(array([10, 10, 1, 1, 20], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0],
                     [-1,  0, 0, 0,  0],
                     [ 0,  1, 0, 0,  0],
                     [ 0, -1, 0, 0,  0],
                     [ 0,  0, 1, 0,  0],
                     [ 0,  0, 0, 1,  0],
                     [ 0,  0, 0, 0,  1],
                     [ 0,  0, 0, 0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, 0, -5], float64)
            },
            MODEL_B14: { # ['r2', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0,  0],
                     [-1,  0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0,  0,  0],
                     [ 0, -1, 0, 0,  0,  0],
                     [ 0,  0, 1, 0,  0,  0],
                     [ 0,  0, 0, 1,  0,  0],
                     [ 0,  0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_B14_FULL: { # ['r2a', 'r2b', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0,  0,  0, 0, 0,  0,  0],
                     [-1,  0,  0,  0, 0, 0,  0,  0],
                     [ 0,  1,  0,  0, 0, 0,  0,  0],
                     [ 0, -1,  0,  0, 0, 0,  0,  0],
                     [ 0,  0,  1,  0, 0, 0,  0,  0],
                     [ 0,  0, -1,  0, 0, 0,  0,  0],
                     [ 0,  0,  0,  1, 0, 0,  0,  0],
                     [ 0,  0,  0, -1, 0, 0,  0,  0],
                     [ 0,  0,  0,  0, 1, 0,  0,  0],
                     [ 0,  0,  0,  0, 0, 1,  0,  0],
                     [ 0,  0,  0,  0, 0, 0, -1,  0],
                     [ 0,  0,  0,  0, 0, 0,  1,  0],
                     [ 0,  0,  0,  0, 0, 0,  0,  1],
                     [ 0,  0,  0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_M61: { # ['r2', 'phi_ex', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0],
                     [-1,  0, 0, 0,  0],
                     [ 0,  1, 0, 0,  0],
                     [ 0, -1, 0, 0,  0],
                     [ 0,  0, 1, 0,  0],
                     [ 0,  0, 0, 1,  0],
                     [ 0,  0, 0, 0,  1],
                     [ 0,  0, 0, 0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, 0, -200], float64)
            },
            MODEL_M61B: { # ['r2', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0,  0],
                     [-1,  0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0,  0,  0],
                     [ 0, -1, 0, 0,  0,  0],
                     [ 0,  0, 1, 0,  0,  0],
                     [ 0,  0, 0, 1,  0,  0],
                     [ 0,  0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, -1, 0.85, 0, -200], float64)
            },
            MODEL_DPL94: { # ['r2', 'phi_ex', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0],
                     [-1,  0, 0, 0,  0],
                     [ 0,  1, 0, 0,  0],
                     [ 0, -1, 0, 0,  0],
                     [ 0,  0, 1, 0,  0],
                     [ 0,  0, 0, 1,  0],
                     [ 0,  0, 0, 0,  1],
                     [ 0,  0, 0, 0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, 0, -200], float64)
            },
            MODEL_TP02: { # ['r2', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0,  0],
                     [-1,  0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0,  0,  0],
                     [ 0, -1, 0, 0,  0,  0],
                     [ 0,  0, 1, 0,  0,  0],
                     [ 0,  0, 0, 1,  0,  0],
                     [ 0,  0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_TAP03: { # ['r2', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0,  0],
                     [-1,  0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0,  0,  0],
                     [ 0, -1, 0, 0,  0,  0],
                     [ 0,  0, 1, 0,  0,  0],
                     [ 0,  0, 0, 1,  0,  0],
                     [ 0,  0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_MP05: { # ['r2', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0,  0],
                     [-1,  0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0,  0,  0],
                     [ 0, -1, 0, 0,  0,  0],
                     [ 0,  0, 1, 0,  0,  0],
                     [ 0,  0, 0, 1,  0,  0],
                     [ 0,  0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_CPMG_2SITE_3D: { # ['r2', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0,  0],
                     [-1,  0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0,  0,  0],
                     [ 0, -1, 0, 0,  0,  0],
                     [ 0,  0, 1, 0,  0,  0],
                     [ 0,  0, 0, 1,  0,  0],
                     [ 0,  0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_CPMG_2SITE_3D_FULL: { # ['r2a', 'r2b', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0,  0,  0, 0, 0,  0,  0],
                     [-1,  0,  0,  0, 0, 0,  0,  0],
                     [ 0,  1,  0,  0, 0, 0,  0,  0],
                     [ 0, -1,  0,  0, 0, 0,  0,  0],
                     [ 0,  0,  1,  0, 0, 0,  0,  0],
                     [ 0,  0, -1,  0, 0, 0,  0,  0],
                     [ 0,  0,  0,  1, 0, 0,  0,  0],
                     [ 0,  0,  0, -1, 0, 0,  0,  0],
                     [ 0,  0,  0,  0, 1, 0,  0,  0],
                     [ 0,  0,  0,  0, 0, 1,  0,  0],
                     [ 0,  0,  0,  0, 0, 0, -1,  0],
                     [ 0,  0,  0,  0, 0, 0,  1,  0],
                     [ 0,  0,  0,  0, 0, 0,  0,  1],
                     [ 0,  0,  0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_CPMG_2SITE_STAR: { # ['r2', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0,  0],
                     [-1,  0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0,  0,  0],
                     [ 0, -1, 0, 0,  0,  0],
                     [ 0,  0, 1, 0,  0,  0],
                     [ 0,  0, 0, 1,  0,  0],
                     [ 0,  0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_CPMG_2SITE_STAR_FULL: { # ['r2a', 'r2b', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0,  0,  0, 0, 0,  0,  0],
                     [-1,  0,  0,  0, 0, 0,  0,  0],
                     [ 0,  1,  0,  0, 0, 0,  0,  0],
                     [ 0, -1,  0,  0, 0, 0,  0,  0],
                     [ 0,  0,  1,  0, 0, 0,  0,  0],
                     [ 0,  0, -1,  0, 0, 0,  0,  0],
                     [ 0,  0,  0,  1, 0, 0,  0,  0],
                     [ 0,  0,  0, -1, 0, 0,  0,  0],
                     [ 0,  0,  0,  0, 1, 0,  0,  0],
                     [ 0,  0,  0,  0, 0, 1,  0,  0],
                     [ 0,  0,  0,  0, 0, 0, -1,  0],
                     [ 0,  0,  0,  0, 0, 0,  1,  0],
                     [ 0,  0,  0,  0, 0, 0,  0,  1],
                     [ 0,  0,  0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_CPMG_2SITE_EXPANDED: { # ['r2', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0,  0],
                     [-1,  0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0,  0,  0],
                     [ 0, -1, 0, 0,  0,  0],
                     [ 0,  0, 1, 0,  0,  0],
                     [ 0,  0, 0, 1,  0,  0],
                     [ 0,  0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_R1RHO_2SITE: { # ['r2', 'dw', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0,  0,  0],
                     [-1,  0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0,  0,  0],
                     [ 0, -1, 0, 0,  0,  0],
                     [ 0,  0, 1, 0,  0,  0],
                     [ 0,  0, 0, 1,  0,  0],
                     [ 0,  0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_R1RHO_3SITE: { # ['r2', 'dw_AB', 'dw_BC', 'pA', 'kex_AB', 'pB', 'kex_BC', 'kex_AC']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 1, 1, 10000, 1, 10000, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0, 0, 0,  0,  0,  0,  0,  0],
                     [-1,  0, 0, 0, 0, 0,  0,  0,  0,  0,  0],
                     [ 0,  1, 0, 0, 0, 0,  0,  0,  0,  0,  0],
                     [ 0, -1, 0, 0, 0, 0,  0,  0,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, -1,  0,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0,  1,  0,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0,  0,  1,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0,  0, -1,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, -1,  0, -1,  0,  0],
                     [ 0,  0, 0, 0, 0, 0,  1,  0, -1,  0,  0],
                     [ 0,  0, 0, 0, 0, 0,  0,  0,  0,  1,  0],
                     [ 0,  0, 0, 0, 0, 0,  0,  0,  0, -1,  0],
                     [ 0,  0, 0, 0, 0, 0,  0,  0,  0,  0,  1],
                     [ 0,  0, 0, 0, 0, 0,  0,  0,  0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, -1, 0.5, 0, -200, -1, 0, 0, -200, 0, -200], float64)
            },
            MODEL_NS_R1RHO_3SITE_LINEAR: { # ['r2', 'dw_AB', 'dw_BC', 'pA', 'kex_AB', 'pB', 'kex_BC']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 1, 1, 10000, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0, 0, 0,  0,  0,  0,  0],
                     [-1,  0, 0, 0, 0, 0,  0,  0,  0,  0],
                     [ 0,  1, 0, 0, 0, 0,  0,  0,  0,  0],
                     [ 0, -1, 0, 0, 0, 0,  0,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, -1,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0,  1,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0,  0,  1,  0,  0],
                     [ 0,  0, 0, 0, 0, 0,  0, -1,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, -1,  0, -1,  0],
                     [ 0,  0, 0, 0, 0, 0,  1,  0, -1,  0],
                     [ 0,  0, 0, 0, 0, 0,  0,  0,  0,  1],
                     [ 0,  0, 0, 0, 0, 0,  0,  0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, -1, 0.5, 0, -200, -1, 0, 0, -200], float64)
            },
            MODEL_MMQ_CR72: { # ['r2', 'dw', 'dwH', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0, 0, 0,  0,  0],
                     [-1,  0, 0, 0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0, 0, 0,  0,  0],
                     [ 0, -1, 0, 0, 0, 0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_MMQ_2SITE: { # ['r2', 'dw', 'dwH', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0, 0, 0,  0,  0],
                     [-1,  0, 0, 0, 0, 0,  0,  0],
                     [ 0,  1, 0, 0, 0, 0,  0,  0],
                     [ 0, -1, 0, 0, 0, 0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, -1,  0],
                     [ 0,  0, 0, 0, 0, 0,  1,  0],
                     [ 0,  0, 0, 0, 0, 0,  0,  1],
                     [ 0,  0, 0, 0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_MMQ_3SITE: { # ['r2', 'dw_AB', 'dw_BC', 'dwH_AB', 'dwH_BC', 'pA', 'kex_AB', 'pB', 'kex_BC', 'kex_AC']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10000, 1, 10000, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0],
                     [-1,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0],
                     [ 0,  1, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0],
                     [ 0, -1, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, -1,  0,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  1,  0,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  1,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0, -1,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, -1,  0, -1,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  1,  0, -1,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  1,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0, -1,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0,  1],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, -1, 0.5, 0, -200, -1, 0, 0, -200, 0, -200], float64)
            },
            MODEL_NS_MMQ_3SITE_LINEAR: { # ['r2', 'dw_AB', 'dw_BC', 'dwH_AB', 'dwH_BC', 'pA', 'kex_AB', 'pB', 'kex_BC']
                'scaling_matrix': diag(array([10, 10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10000, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0],
                     [-1,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0],
                     [ 0,  1, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0],
                     [ 0, -1, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, -1,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  1,  0,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  1,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0, -1,  0,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, -1,  0, -1,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  1,  0, -1,  0],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0,  1],
                     [ 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, -1, 0.5, 0, -200, -1, 0, 0, -200], float64)
            },
        }

        # Loop over all models.
        print("Checking the linear constraints for a cluster of 2 spins.")
        for model in MODEL_LIST_FULL:
            # Sanity check.
            if model not in expected:
                raise RelaxError("The model '%s' is not being checked." % model)

            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            cdp.spectrometer_frq_list = [1e6]
            spins = [SpinContainer(), SpinContainer()]
            for spin in spins:
                spin.model = model
                spin.params = deepcopy(MODEL_PARAMS[model])

            # Build the linear constraints.
            A, b = linear_constraints(spins=spins, scaling_matrix=expected[model]['scaling_matrix'])

            # Array checks.
            self.assertTrue(array_equal(A, expected[model]['A']))
            self.assertTrue(array_equal(b, expected[model]['b']))


    def test_linear_constraints_single_spin(self):
        """Test the specific_analyses.relax_disp.parameters.linear_constraints() function for a single spin."""

        # The expected parameter information.
        expected = {
            MODEL_R2EFF: {
                'scaling_matrix': diag(array([1], float64)),
                'A': array([[1], [-1]], float64),
                'b': array([0, -200], float64)
            },
            MODEL_NOREX: {
                'scaling_matrix': diag(array([10], float64)),
                'A': array([[1], [-1]], float64),
                'b': array([0, -20], float64)
            },
            MODEL_LM63: {
                'scaling_matrix': diag(array([10, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0],
                     [-1, 0,  0],
                     [ 0, 1,  0],
                     [ 0, 0,  1],
                     [ 0, 0, -1]],
                float64),
                'b': array([0, -20, 0, 0, -200], float64)
            },
            MODEL_LM63_3SITE: {
                'scaling_matrix': diag(array([10, 1, 1, 10000, 10000], float64)),
                'A': array(
                    [[ 1, 0, 0,  0,  0],
                     [-1, 0, 0,  0,  0],
                     [ 0, 1, 0,  0,  0],
                     [ 0, 0, 1,  0,  0],
                     [ 0, 0, 0,  1,  0],
                     [ 0, 0, 0, -1,  0],
                     [ 0, 0, 0,  0,  1],
                     [ 0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, 0, 0, -200, 0, -200], float64)
            },
            MODEL_CR72: {
                'scaling_matrix': diag(array([10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0,  0],
                     [-1, 0,  0,  0],
                     [ 0, 1,  0,  0],
                     [ 0, 0, -1,  0],
                     [ 0, 0,  1,  0],
                     [ 0, 0,  0,  1],
                     [ 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_CR72_FULL: {
                'scaling_matrix': diag(array([10, 10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0,  0,  0],
                     [-1,  0, 0,  0,  0],
                     [ 0,  1, 0,  0,  0],
                     [ 0, -1, 0,  0,  0],
                     [ 0,  0, 1,  0,  0],
                     [ 0,  0, 0, -1,  0],
                     [ 0,  0, 0,  1,  0],
                     [ 0,  0, 0,  0,  1],
                     [ 0,  0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_IT99: {
                'scaling_matrix': diag(array([10, 1, 1, 1e-4], float64)),
                'A': array(
                    [[ 1, 0,  0, 0],
                     [-1, 0,  0, 0],
                     [ 0, 1,  0, 0],
                     [ 0, 0, -1, 0],
                     [ 0, 0,  1, 0],
                     [ 0, 0,  0, 1]],
                float64),
                'b': array([0, -20, 0, -1, 0.5, 0], float64)
            },
            MODEL_TSMFK01: {
                'scaling_matrix': diag(array([10, 1, 20], float64)),
                'A': array(
                    [[ 1, 0,  0],
                     [-1, 0,  0],
                     [ 0, 1,  0],
                     [ 0, 0,  1],
                     [ 0, 0, -1]],
                float64),
                'b': array([0, -20, 0, 0, -5], float64)
            },
            MODEL_B14: {
                'scaling_matrix': diag(array([10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0,  0],
                     [-1, 0,  0,  0],
                     [ 0, 1,  0,  0],
                     [ 0, 0, -1,  0],
                     [ 0, 0,  1,  0],
                     [ 0, 0,  0,  1],
                     [ 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_B14_FULL: {
                'scaling_matrix': diag(array([10, 10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0,  0,  0],
                     [-1,  0, 0,  0,  0],
                     [ 0,  1, 0,  0,  0],
                     [ 0, -1, 0,  0,  0],
                     [ 0,  0, 1,  0,  0],
                     [ 0,  0, 0, -1,  0],
                     [ 0,  0, 0,  1,  0],
                     [ 0,  0, 0,  0,  1],
                     [ 0,  0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_M61: {
                'scaling_matrix': diag(array([10, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0],
                     [-1, 0,  0],
                     [ 0, 1,  0],
                     [ 0, 0,  1],
                     [ 0, 0, -1]],
                float64),
                'b': array([0, -20, 0, 0, -200], float64)
            },
            MODEL_M61B: {
                'scaling_matrix': diag(array([10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0,  0],
                     [-1, 0,  0,  0],
                     [ 0, 1,  0,  0],
                     [ 0, 0, -1,  0],
                     [ 0, 0,  1,  0],
                     [ 0, 0,  0,  1],
                     [ 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -1, 0.85, 0, -200], float64)
            },
            MODEL_DPL94: {
                'scaling_matrix': diag(array([10, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0],
                     [-1, 0,  0],
                     [ 0, 1,  0],
                     [ 0, 0,  1],
                     [ 0, 0, -1]],
                float64),
                'b': array([0, -20, 0, 0, -200], float64)
            },
            MODEL_TP02: {
                'scaling_matrix': diag(array([10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0,  0],
                     [-1, 0,  0,  0],
                     [ 0, 1,  0,  0],
                     [ 0, 0, -1,  0],
                     [ 0, 0,  1,  0],
                     [ 0, 0,  0,  1],
                     [ 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_TAP03: {
                'scaling_matrix': diag(array([10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0,  0],
                     [-1, 0,  0,  0],
                     [ 0, 1,  0,  0],
                     [ 0, 0, -1,  0],
                     [ 0, 0,  1,  0],
                     [ 0, 0,  0,  1],
                     [ 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_MP05: {
                'scaling_matrix': diag(array([10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0,  0],
                     [-1, 0,  0,  0],
                     [ 0, 1,  0,  0],
                     [ 0, 0, -1,  0],
                     [ 0, 0,  1,  0],
                     [ 0, 0,  0,  1],
                     [ 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_CPMG_2SITE_3D: {
                'scaling_matrix': diag(array([10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0,  0],
                     [-1, 0,  0,  0],
                     [ 0, 1,  0,  0],
                     [ 0, 0, -1,  0],
                     [ 0, 0,  1,  0],
                     [ 0, 0,  0,  1],
                     [ 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_CPMG_2SITE_3D_FULL: {
                'scaling_matrix': diag(array([10, 10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0,  0,  0],
                     [-1,  0, 0,  0,  0],
                     [ 0,  1, 0,  0,  0],
                     [ 0, -1, 0,  0,  0],
                     [ 0,  0, 1,  0,  0],
                     [ 0,  0, 0, -1,  0],
                     [ 0,  0, 0,  1,  0],
                     [ 0,  0, 0,  0,  1],
                     [ 0,  0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_CPMG_2SITE_STAR: {
                'scaling_matrix': diag(array([10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0,  0],
                     [-1, 0,  0,  0],
                     [ 0, 1,  0,  0],
                     [ 0, 0, -1,  0],
                     [ 0, 0,  1,  0],
                     [ 0, 0,  0,  1],
                     [ 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_CPMG_2SITE_STAR_FULL: {
                'scaling_matrix': diag(array([10, 10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1,  0, 0,  0,  0],
                     [-1,  0, 0,  0,  0],
                     [ 0,  1, 0,  0,  0],
                     [ 0, -1, 0,  0,  0],
                     [ 0,  0, 1,  0,  0],
                     [ 0,  0, 0, -1,  0],
                     [ 0,  0, 0,  1,  0],
                     [ 0,  0, 0,  0,  1],
                     [ 0,  0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_CPMG_2SITE_EXPANDED: {
                'scaling_matrix': diag(array([10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0,  0],
                     [-1, 0,  0,  0],
                     [ 0, 1,  0,  0],
                     [ 0, 0, -1,  0],
                     [ 0, 0,  1,  0],
                     [ 0, 0,  0,  1],
                     [ 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_R1RHO_2SITE: {
                'scaling_matrix': diag(array([10, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0,  0,  0],
                     [-1, 0,  0,  0],
                     [ 0, 1,  0,  0],
                     [ 0, 0, -1,  0],
                     [ 0, 0,  1,  0],
                     [ 0, 0,  0,  1],
                     [ 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, 0, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_R1RHO_3SITE: { # ['r2', 'dw_AB', 'dw_BC', 'pA', 'kex_AB', 'pB', 'kex_BC', 'kex_AC']
                'scaling_matrix': diag(array([10, 1, 1, 1, 10000, 1, 10000, 10000], float64)),
                'A': array(
                    [[ 1, 0, 0,  0,  0,  0,  0,  0],
                     [-1, 0, 0,  0,  0,  0,  0,  0],
                     [ 0, 0, 0, -1,  0,  0,  0,  0],
                     [ 0, 0, 0,  1,  0,  0,  0,  0],
                     [ 0, 0, 0,  0,  1,  0,  0,  0],
                     [ 0, 0, 0,  0, -1,  0,  0,  0],
                     [ 0, 0, 0, -1,  0, -1,  0,  0],
                     [ 0, 0, 0,  1,  0, -1,  0,  0],
                     [ 0, 0, 0,  0,  0,  0,  1,  0],
                     [ 0, 0, 0,  0,  0,  0, -1,  0],
                     [ 0, 0, 0,  0,  0,  0,  0,  1],
                     [ 0, 0, 0,  0,  0,  0,  0, -1]],
                float64),
                'b': array([0, -20, -1, 0.5, 0, -200, -1, 0, 0, -200, 0, -200], float64)
            },
            MODEL_NS_R1RHO_3SITE_LINEAR: { # ['r2', 'dw_AB', 'dw_BC', 'pA', 'kex_AB', 'pB', 'kex_BC']
                'scaling_matrix': diag(array([10, 1, 1, 1, 10000, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0, 0,  0,  0,  0,  0],
                     [-1, 0, 0,  0,  0,  0,  0],
                     [ 0, 0, 0, -1,  0,  0,  0],
                     [ 0, 0, 0,  1,  0,  0,  0],
                     [ 0, 0, 0,  0,  1,  0,  0],
                     [ 0, 0, 0,  0, -1,  0,  0],
                     [ 0, 0, 0, -1,  0, -1,  0],
                     [ 0, 0, 0,  1,  0, -1,  0],
                     [ 0, 0, 0,  0,  0,  0,  1],
                     [ 0, 0, 0,  0,  0,  0, -1]],
                float64),
                'b': array([0, -20, -1, 0.5, 0, -200, -1, 0, 0, -200], float64)
            },
            MODEL_MMQ_CR72: { # ['r2', 'dw', 'dwH', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0, 0,  0,  0],
                     [-1, 0, 0,  0,  0],
                     [ 0, 0, 0, -1,  0],
                     [ 0, 0, 0,  1,  0],
                     [ 0, 0, 0,  0,  1],
                     [ 0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_MMQ_2SITE: { # ['r2', 'dw', 'dwH', 'pA', 'kex']
                'scaling_matrix': diag(array([10, 1, 1, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0, 0,  0,  0],
                     [-1, 0, 0,  0,  0],
                     [ 0, 0, 0, -1,  0],
                     [ 0, 0, 0,  1,  0],
                     [ 0, 0, 0,  0,  1],
                     [ 0, 0, 0,  0, -1]],
                float64),
                'b': array([0, -20, -1, 0.5, 0, -200], float64)
            },
            MODEL_NS_MMQ_3SITE: { # ['r2', 'dw_AB', 'dw_BC', 'dwH_AB', 'dwH_BC', 'pA', 'kex_AB', 'pB', 'kex_BC', 'kex_AC']
                'scaling_matrix': diag(array([10, 1, 1, 1, 1, 1, 10000, 1, 10000, 10000], float64)),
                'A': array(
                    [[ 1, 0, 0, 0, 0,  0,  0,  0,  0,  0],
                     [-1, 0, 0, 0, 0,  0,  0,  0,  0,  0],
                     [ 0, 0, 0, 0, 0, -1,  0,  0,  0,  0],
                     [ 0, 0, 0, 0, 0,  1,  0,  0,  0,  0],
                     [ 0, 0, 0, 0, 0,  0,  1,  0,  0,  0],
                     [ 0, 0, 0, 0, 0,  0, -1,  0,  0,  0],
                     [ 0, 0, 0, 0, 0, -1,  0, -1,  0,  0],
                     [ 0, 0, 0, 0, 0,  1,  0, -1,  0,  0],
                     [ 0, 0, 0, 0, 0,  0,  0,  0,  1,  0],
                     [ 0, 0, 0, 0, 0,  0,  0,  0, -1,  0],
                     [ 0, 0, 0, 0, 0,  0,  0,  0,  0,  1],
                     [ 0, 0, 0, 0, 0,  0,  0,  0,  0, -1]],
                float64),
                'b': array([0, -20, -1, 0.5, 0, -200, -1, 0, 0, -200, 0, -200], float64)
            },
            MODEL_NS_MMQ_3SITE_LINEAR: { # ['r2', 'dw_AB', 'dw_BC', 'dwH_AB', 'dwH_BC', 'pA', 'kex_AB', 'pB', 'kex_BC']
                'scaling_matrix': diag(array([10, 1, 1, 1, 1, 1, 10000, 1, 10000], float64)),
                'A': array(
                    [[ 1, 0, 0, 0, 0,  0,  0,  0,  0],
                     [-1, 0, 0, 0, 0,  0,  0,  0,  0],
                     [ 0, 0, 0, 0, 0, -1,  0,  0,  0],
                     [ 0, 0, 0, 0, 0,  1,  0,  0,  0],
                     [ 0, 0, 0, 0, 0,  0,  1,  0,  0],
                     [ 0, 0, 0, 0, 0,  0, -1,  0,  0],
                     [ 0, 0, 0, 0, 0, -1,  0, -1,  0],
                     [ 0, 0, 0, 0, 0,  1,  0, -1,  0],
                     [ 0, 0, 0, 0, 0,  0,  0,  0,  1],
                     [ 0, 0, 0, 0, 0,  0,  0,  0, -1]],
                float64),
                'b': array([0, -20, -1, 0.5, 0, -200, -1, 0, 0, -200], float64)
            },
        }

        # Loop over all models.
        print("Checking the linear constraints for a single spin.")
        for model in MODEL_LIST_FULL:
            # Sanity check.
            if model not in expected:
                raise RelaxError("The model '%s' is not being checked." % model)

            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            cdp.spectrometer_frq_list = [1e6]
            spin = SpinContainer()
            spin.model = model
            spin.params = deepcopy(MODEL_PARAMS[model])

            # Build the linear constraints.
            A, b = linear_constraints(spins=[spin], scaling_matrix=expected[model]['scaling_matrix'])

            # Array checks.
            self.assertTrue(array_equal(A, expected[model]['A']))
            self.assertTrue(array_equal(b, expected[model]['b']))


    def test_loop_parameters_clustered_spins(self):
        """Test the specific_analyses.relax_disp.parameters.loop_parameters() function for a cluster of 2 spins."""

        # The expected parameter information.
        expected = {
            MODEL_R2EFF: [
                ['r2eff', 0, None],
                ['r2eff', 1, None],
            ],
            MODEL_NOREX: [
                ['r2', 0, 'No Rex - 1.00000000 MHz'],
                ['r2', 1, 'No Rex - 1.00000000 MHz'],
            ],
            MODEL_LM63: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['phi_ex', 0, None],
                ['phi_ex', 1, None],
                ['kex', None, None],
            ],
            MODEL_LM63_3SITE: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['phi_ex_B', 0, None],
                ['phi_ex_C', 0, None],
                ['phi_ex_B', 1, None],
                ['phi_ex_C', 1, None],
                ['kB', None, None],
                ['kC', None, None],
            ],
            MODEL_CR72: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_CR72_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2a', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_IT99: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['tex', None, None],
            ],
            MODEL_TSMFK01: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2a', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['k_AB', None, None],
            ],
            MODEL_B14: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_B14_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2a', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_M61: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['phi_ex', 0, None],
                ['phi_ex', 1, None],
                ['kex', None, None],
            ],
            MODEL_M61B: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_DPL94: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['phi_ex', 0, None],
                ['phi_ex', 1, None],
                ['kex', None, None],
            ],
            MODEL_TP02: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_TAP03: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_MP05: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_3D: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_3D_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2a', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_STAR: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_STAR_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2a', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_EXPANDED: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_R1RHO_2SITE: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_R1RHO_3SITE: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['dw_AB', 1, None],
                ['dw_BC', 1, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
                ['kex_AC', None, None],
            ],
            MODEL_NS_R1RHO_3SITE_LINEAR: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['dw_AB', 1, None],
                ['dw_BC', 1, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
            ],
            MODEL_MMQ_CR72: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['r2', 1, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['dwH', 0, None],
                ['dwH', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_MMQ_2SITE: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['r2', 1, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['dwH', 0, None],
                ['dwH', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_MMQ_3SITE: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['r2', 1, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['dw_AB', 1, None],
                ['dw_BC', 1, None],
                ['dwH_AB', 0, None],
                ['dwH_BC', 0, None],
                ['dwH_AB', 1, None],
                ['dwH_BC', 1, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
                ['kex_AC', None, None],
            ],
            MODEL_NS_MMQ_3SITE_LINEAR: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['r2', 1, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['dw_AB', 1, None],
                ['dw_BC', 1, None],
                ['dwH_AB', 0, None],
                ['dwH_BC', 0, None],
                ['dwH_AB', 1, None],
                ['dwH_BC', 1, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
            ],
        }

        # Loop over all models.
        print("Checking the parameter looping for a cluster of 2 spins.")
        for model in MODEL_LIST_FULL:
            # Sanity check.
            if model not in expected:
                raise RelaxError("The model '%s' is not being checked." % model)

            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            cdp.spectrometer_frq_list = [1e6]
            spins = [SpinContainer(), SpinContainer()]
            for spin in spins:
                spin.model = model
                spin.params = deepcopy(MODEL_PARAMS[model])

            # Check the parameter loop.
            i = 0
            for name, param_index, spin_index, R20_key in loop_parameters(spins):
                print("        Parameter '%s', %s, %s, %s." % (name, param_index, spin_index, repr(R20_key)))
                self.assertEqual(name, expected[model][i][0])
                self.assertEqual(spin_index, expected[model][i][1])
                self.assertEqual(R20_key, expected[model][i][2])
                i += 1

            # Parameter count check.
            self.assertEqual(i, len(expected[model]))


    def test_loop_parameters_single_spin(self):
        """Test the specific_analyses.relax_disp.parameters.loop_parameters() function for a single spin."""

        # The expected parameter information.
        expected = {
            MODEL_R2EFF: [
                ['r2eff', 0, None],
            ],
            MODEL_NOREX: [
                ['r2', 0, 'No Rex - 1.00000000 MHz'],
            ],
            MODEL_LM63: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['phi_ex', 0, None],
                ['kex', None, None],
            ],
            MODEL_LM63_3SITE: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['phi_ex_B', 0, None],
                ['phi_ex_C', 0, None],
                ['kB', None, None],
                ['kC', None, None],
            ],
            MODEL_CR72: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_CR72_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_IT99: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['tex', None, None],
            ],
            MODEL_TSMFK01: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['k_AB', None, None],
            ],
            MODEL_B14: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_B14_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_M61: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['phi_ex', 0, None],
                ['kex', None, None],
            ],
            MODEL_M61B: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_DPL94: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['phi_ex', 0, None],
                ['kex', None, None],
            ],
            MODEL_TP02: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_TAP03: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_MP05: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_3D: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_3D_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_STAR: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_STAR_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_EXPANDED: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_R1RHO_2SITE: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_R1RHO_3SITE: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
                ['kex_AC', None, None],
            ],
            MODEL_NS_R1RHO_3SITE_LINEAR: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
            ],
            MODEL_MMQ_CR72: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dwH', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_MMQ_2SITE: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dwH', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_MMQ_3SITE: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['dwH_AB', 0, None],
                ['dwH_BC', 0, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
                ['kex_AC', None, None],
            ],
            MODEL_NS_MMQ_3SITE_LINEAR: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['dwH_AB', 0, None],
                ['dwH_BC', 0, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
            ],
        }

        # Loop over all models.
        print("Checking the parameter looping for a single spin.")
        for model in MODEL_LIST_FULL:
            # Sanity check.
            if model not in expected:
                raise RelaxError("The model '%s' is not being checked." % model)

            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            cdp.spectrometer_frq_list = [1e6]
            spin = SpinContainer()
            spin.model = model
            spin.params = deepcopy(MODEL_PARAMS[model])

            # Check the parameter loop.
            i = 0
            for name, param_index, spin_index, R20_key in loop_parameters([spin]):
                print("        Parameter '%s', %s, %s, %s." % (name, param_index, spin_index, repr(R20_key)))
                self.assertEqual(name, expected[model][i][0])
                self.assertEqual(spin_index, expected[model][i][1])
                self.assertEqual(R20_key, expected[model][i][2])
                i += 1

            # Parameter count check.
            self.assertEqual(i, len(expected[model]))


    def test_param_conversion_clustered_spins(self):
        """Test the specific_analyses.relax_disp.parameters.param_conversion() function for a cluster of 2 spins."""

        # Test parameter values.
        fixed_values = {
            'r2eff': 10.0,
            'r2': 15.0,
            'r2a': 12.0,
            'r2b': 18.0,
            'pA': 0.80,
            'pB': 0.15,
            'k_AB': 0.001,
            'k_BA': 0.003,
            'kex': 0.01,
            'kex_AB': 0.015,
            'kex_BC': 0.017,
            'kex_AC': 0.016,
            'kB': 0.005,
            'kC': 0.004,
            'tex': 50.0,
            'dw': 1.0,
            'dw_AB': 1.02,
            'dw_BC': 1.03,
            'dwH': 0.1,
            'dwH_AB': 0.12,
            'dwH_BC': 0.13,
            'phi_ex': 0.5,
            'phi_ex_B': 0.4,
            'phi_ex_C': 0.3,
        }

        # Loop over all models.
        print("Checking the parameter conversion and setting for a cluster of 2 spins.")
        for model in MODEL_LIST_FULL:
            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            cdp.spectrometer_frq_list = [1e6]
            spins = [SpinContainer(), SpinContainer()]
            for spin in spins:
                spin.model = model
                spin.params = deepcopy(MODEL_PARAMS[model])

            # First set the parameter values.
            for name, param_index, spin_index, R20_key in loop_parameters(spins):
                # R2 parameters.
                if name in ['r2', 'r2a', 'r2b']:
                    key = "%s - %.8f MHz" % (cdp.exp_type_list[0], cdp.spectrometer_frq_list[0]/1e6)
                    print("        Setting spin %i parameter %s['%s'] to %s." % (spin_index, name, key, fixed_values[name]))
                    setattr(spins[spin_index], name, {key: fixed_values[name]})

                # Global parameters.
                elif spin_index == None:
                    print("        Setting global parameter %s to %s." % (name, fixed_values[name]))
                    setattr(spins[0], name, fixed_values[name])
                    setattr(spins[1], name, fixed_values[name])

                # Spin parameters.
                else:
                    print("        Setting spin %i parameter %s to %s." % (spin_index, name, fixed_values[name]))
                    setattr(spins[spin_index], name, fixed_values[name])

            # Then perform the conversion.
            param_conversion(key=None, spins=spins, sim_index=None)

            # Check the probabilities.
            if 'pB' in MODEL_PARAMS[model]:
                print("        Checking parameter pC.")
                self.assertAlmostEqual(spins[0].pC, 0.05)
                self.assertAlmostEqual(spins[1].pC, 0.05)
            elif 'pA' in MODEL_PARAMS[model]:
                print("        Checking parameter pB.")
                self.assertAlmostEqual(spins[0].pB, 0.20)
                self.assertAlmostEqual(spins[1].pB, 0.20)

            # Check the kex-tex pair.
            if 'kex' in MODEL_PARAMS[model]:
                print("        Checking parameter tex.")
                self.assertAlmostEqual(spins[0].tex, 100.0)
                self.assertAlmostEqual(spins[1].tex, 100.0)
            elif 'tex' in MODEL_PARAMS[model]:
                print("        Checking parameter kex.")
                self.assertAlmostEqual(spins[0].kex, 0.02)
                self.assertAlmostEqual(spins[1].kex, 0.02)

            # Check the rates.
            if 'kex' in MODEL_PARAMS[model] and 'pA' in MODEL_PARAMS[model]:
                print("        Checking parameter k_AB.")
                self.assertAlmostEqual(spins[0].k_AB, 0.002)
                self.assertAlmostEqual(spins[1].k_AB, 0.002)
                print("        Checking parameter k_BA.")
                self.assertAlmostEqual(spins[0].k_BA, 0.008)
                self.assertAlmostEqual(spins[1].k_BA, 0.008)


    def test_param_conversion_clustered_spins_sim(self):
        """Test the specific_analyses.relax_disp.parameters.param_conversion() function for a cluster of 2 spins for Monte Carlo simulations."""

        # Test parameter values.
        fixed_values = {
            'r2eff': 10.0,
            'r2': 15.0,
            'r2a': 12.0,
            'r2b': 18.0,
            'pA': 0.80,
            'pB': 0.15,
            'k_AB': 0.001,
            'k_BA': 0.003,
            'kex': 0.01,
            'kex_AB': 0.015,
            'kex_BC': 0.017,
            'kex_AC': 0.016,
            'kB': 0.005,
            'kC': 0.004,
            'tex': 50.0,
            'dw': 1.0,
            'dw_AB': 1.02,
            'dw_BC': 1.03,
            'dwH': 0.1,
            'dwH_AB': 0.12,
            'dwH_BC': 0.13,
            'phi_ex': 0.5,
            'phi_ex_B': 0.4,
            'phi_ex_C': 0.3,
        }

        # Loop over all models.
        print("Checking the parameter conversion and setting for a cluster of 2 spins.")
        for model in MODEL_LIST_FULL:
            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            cdp.spectrometer_frq_list = [1e6]
            spins = [SpinContainer(), SpinContainer()]
            for spin in spins:
                spin.model = model
                spin.params = deepcopy(MODEL_PARAMS[model])

            # First set the parameter values.
            for name, param_index, spin_index, R20_key in loop_parameters(spins):
                # The MC simulation parameter name.
                sim_name = "%s_sim" % name

                # R2 parameters.
                if name in ['r2', 'r2a', 'r2b']:
                    key = "%s - %.8f MHz" % (cdp.exp_type_list[0], cdp.spectrometer_frq_list[0]/1e6)
                    print("        Setting spin %i parameter %s[0]['%s'] to %s." % (spin_index, sim_name, key, fixed_values[name]))
                    setattr(spins[spin_index], sim_name, [{key: fixed_values[name]}])

                # Global parameters.
                elif spin_index == None:
                    print("        Setting global parameter %s[0] to %s." % (sim_name, fixed_values[name]))
                    setattr(spins[0], sim_name, [fixed_values[name]])
                    setattr(spins[1], sim_name, [fixed_values[name]])

                # Spin parameters.
                else:
                    print("        Setting spin %i parameter %s[0] to %s." % (spin_index, sim_name, fixed_values[name]))
                    setattr(spins[spin_index], sim_name, [fixed_values[name]])

            # Set up the conversion structures.
            for spin in spins:
                if 'pB' in MODEL_PARAMS[model]:
                    spin.pC_sim = [None]
                elif 'pA' in MODEL_PARAMS[model]:
                    spin.pB_sim = [None]
                if 'kex' in MODEL_PARAMS[model]:
                    spin.tex_sim = [None]
                elif 'tex' in MODEL_PARAMS[model]:
                    spin.kex_sim = [None]
                if 'kex' in MODEL_PARAMS[model] and 'pA' in MODEL_PARAMS[model]:
                    spin.k_AB_sim = [None]
                    spin.k_BA_sim = [None]

            # Then perform the conversion.
            param_conversion(key=None, spins=spins, sim_index=0)

            # Check the probabilities.
            if 'pB' in MODEL_PARAMS[model]:
                print("        Checking parameter pC.")
                self.assertAlmostEqual(spins[0].pC_sim[0], 0.05)
                self.assertAlmostEqual(spins[1].pC_sim[0], 0.05)
            elif 'pA' in MODEL_PARAMS[model]:
                print("        Checking parameter pB.")
                self.assertAlmostEqual(spins[0].pB_sim[0], 0.20)
                self.assertAlmostEqual(spins[1].pB_sim[0], 0.20)

            # Check the kex-tex pair.
            if 'kex' in MODEL_PARAMS[model]:
                print("        Checking parameter tex.")
                self.assertAlmostEqual(spins[0].tex_sim[0], 100.0)
                self.assertAlmostEqual(spins[1].tex_sim[0], 100.0)
            elif 'tex' in MODEL_PARAMS[model]:
                print("        Checking parameter kex.")
                self.assertAlmostEqual(spins[0].kex_sim[0], 0.02)
                self.assertAlmostEqual(spins[1].kex_sim[0], 0.02)

            # Check the rates.
            if 'kex' in MODEL_PARAMS[model] and 'pA' in MODEL_PARAMS[model]:
                print("        Checking parameter k_AB.")
                self.assertAlmostEqual(spins[0].k_AB_sim[0], 0.002)
                self.assertAlmostEqual(spins[1].k_AB_sim[0], 0.002)
                print("        Checking parameter k_BA.")
                self.assertAlmostEqual(spins[0].k_BA_sim[0], 0.008)
                self.assertAlmostEqual(spins[1].k_BA_sim[0], 0.008)


    def test_param_conversion_single_spin(self):
        """Test the specific_analyses.relax_disp.parameters.param_conversion() function for a single spin."""

        # Test parameter values.
        fixed_values = {
            'r2eff': 10.0,
            'r2': 15.0,
            'r2a': 12.0,
            'r2b': 18.0,
            'pA': 0.80,
            'pB': 0.15,
            'k_AB': 0.001,
            'k_BA': 0.003,
            'kex': 0.01,
            'kex_AB': 0.015,
            'kex_BC': 0.017,
            'kex_AC': 0.016,
            'kB': 0.005,
            'kC': 0.004,
            'tex': 50.0,
            'dw': 1.0,
            'dw_AB': 1.02,
            'dw_BC': 1.03,
            'dwH': 0.1,
            'dwH_AB': 0.12,
            'dwH_BC': 0.13,
            'phi_ex': 0.5,
            'phi_ex_B': 0.4,
            'phi_ex_C': 0.3,
        }

        # Loop over all models.
        print("Checking the parameter conversion and setting for a single spin.")
        for model in MODEL_LIST_FULL:
            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            cdp.spectrometer_frq_list = [1e6]
            spin = SpinContainer()
            spin.model = model
            spin.params = deepcopy(MODEL_PARAMS[model])

            # First set the parameter values.
            for name, param_index, spin_index, R20_key in loop_parameters([spin]):
                # R2 parameters.
                if name in ['r2', 'r2a', 'r2b']:
                    key = "%s - %.8f MHz" % (cdp.exp_type_list[0], cdp.spectrometer_frq_list[0]/1e6)
                    print("        Setting spin %i parameter %s['%s'] to %s." % (spin_index, name, key, fixed_values[name]))
                    setattr(spin, name, {key: fixed_values[name]})

                # Global parameters.
                elif spin_index == None:
                    print("        Setting global parameter %s to %s." % (name, fixed_values[name]))
                    setattr(spin, name, fixed_values[name])

                # Spin parameters.
                else:
                    print("        Setting spin %i parameter %s to %s." % (spin_index, name, fixed_values[name]))
                    setattr(spin, name, fixed_values[name])

            # Then perform the conversion.
            param_conversion(key=None, spins=[spin], sim_index=None)

            # Check the probabilities.
            if 'pB' in MODEL_PARAMS[model]:
                print("        Checking parameter pC.")
                self.assertAlmostEqual(spin.pC, 0.05)
            elif 'pA' in MODEL_PARAMS[model]:
                print("        Checking parameter pB.")
                self.assertAlmostEqual(spin.pB, 0.20)

            # Check the kex-tex pair.
            if 'kex' in MODEL_PARAMS[model]:
                print("        Checking parameter tex.")
                self.assertAlmostEqual(spin.tex, 100.0)
            elif 'tex' in MODEL_PARAMS[model]:
                print("        Checking parameter kex.")
                self.assertAlmostEqual(spin.kex, 0.02)

            # Check the rates.
            if 'kex' in MODEL_PARAMS[model] and 'pA' in MODEL_PARAMS[model]:
                print("        Checking parameter k_AB.")
                self.assertAlmostEqual(spin.k_AB, 0.002)
                print("        Checking parameter k_BA.")
                self.assertAlmostEqual(spin.k_BA, 0.008)


    def test_param_num_clustered_spins(self):
        """Test the specific_analyses.relax_disp.parameters.param_num() function for a cluster of 2 spins."""

        # The expected number of parameters for the single spin.
        expected = {
            MODEL_R2EFF: 2,
            MODEL_NOREX: 2,
            MODEL_LM63: 5,
            MODEL_LM63_3SITE: 8,
            MODEL_CR72: 6,
            MODEL_CR72_FULL: 8,
            MODEL_IT99: 6,
            MODEL_TSMFK01: 5,
            MODEL_B14: 6,
            MODEL_B14_FULL: 8,
            MODEL_M61: 5,
            MODEL_M61B: 6,
            MODEL_DPL94: 5,
            MODEL_TP02: 6,
            MODEL_TAP03: 6,
            MODEL_MP05: 6,
            MODEL_NS_CPMG_2SITE_3D: 6,
            MODEL_NS_CPMG_2SITE_3D_FULL: 8,
            MODEL_NS_CPMG_2SITE_STAR: 6,
            MODEL_NS_CPMG_2SITE_STAR_FULL: 8,
            MODEL_NS_CPMG_2SITE_EXPANDED: 6,
            MODEL_NS_R1RHO_2SITE: 6,
            MODEL_NS_R1RHO_3SITE: 11,
            MODEL_NS_R1RHO_3SITE_LINEAR: 10,
            MODEL_MMQ_CR72: 8,
            MODEL_NS_MMQ_2SITE: 8,
            MODEL_NS_MMQ_3SITE: 15,
            MODEL_NS_MMQ_3SITE_LINEAR: 14
        }

        # Loop over all models.
        print("Checking the parameter number counts for a cluster of 2 spins.")
        for model in MODEL_LIST_FULL:
            # Sanity check.
            if model not in expected:
                raise RelaxError("The model '%s' is not being checked." % model)

            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            spins = [SpinContainer(), SpinContainer()]
            for spin in spins:
                spin.model = model
                spin.params = deepcopy(MODEL_PARAMS[model])

            # Check the parameter number.
            self.assertEqual(param_num(spins), expected[model])


    def test_param_num_single_spin(self):
        """Test the specific_analyses.relax_disp.parameters.param_num() function for a single spin."""

        # The expected number of parameters for the single spin.
        expected = {
            MODEL_R2EFF: 1,
            MODEL_NOREX: 1,
            MODEL_LM63: 3,
            MODEL_LM63_3SITE: 5,
            MODEL_CR72: 4,
            MODEL_CR72_FULL: 5,
            MODEL_IT99: 4,
            MODEL_TSMFK01: 3,
            MODEL_B14: 4,
            MODEL_B14_FULL: 5,
            MODEL_M61: 3,
            MODEL_M61B: 4,
            MODEL_DPL94: 3,
            MODEL_TP02: 4,
            MODEL_TAP03: 4,
            MODEL_MP05: 4,
            MODEL_NS_CPMG_2SITE_3D: 4,
            MODEL_NS_CPMG_2SITE_3D_FULL: 5,
            MODEL_NS_CPMG_2SITE_STAR: 4,
            MODEL_NS_CPMG_2SITE_STAR_FULL: 5,
            MODEL_NS_CPMG_2SITE_EXPANDED: 4,
            MODEL_NS_R1RHO_2SITE: 4,
            MODEL_NS_R1RHO_3SITE: 8,
            MODEL_NS_R1RHO_3SITE_LINEAR: 7,
            MODEL_MMQ_CR72: 5,
            MODEL_NS_MMQ_2SITE: 5,
            MODEL_NS_MMQ_3SITE: 10,
            MODEL_NS_MMQ_3SITE_LINEAR: 9
        }

        # Loop over all models.
        print("Checking the parameter number counts for a single spin.")
        for model in MODEL_LIST_FULL:
            # Sanity check.
            if model not in expected:
                raise RelaxError("The model '%s' is not being checked." % model)

            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            spin = SpinContainer()
            spin.model = model
            spin.params = deepcopy(MODEL_PARAMS[model])

            # Check the parameter number.
            self.assertEqual(param_num([spin]), expected[model])
