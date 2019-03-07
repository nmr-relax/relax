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

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
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
from pipe_control import mol_res_spin
from specific_analyses.relax_disp.api import Relax_disp
from specific_analyses.relax_disp.parameters import loop_parameters
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_api(UnitTestCase):
    """Unit tests for the functions of the specific_analyses.relax_disp.api module."""

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


    def test_sim_init_values(self):
        """Test the specific_analyses.relax_disp.api.sim_init_values() function for a cluster of 2 spins."""

        # Test parameter values.
        fixed_values = {
            'r1': 2.2,
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
            cdp.sim_number = 2

            # Set up the spin systems.
            cdp.mol.add_item(mol_name="sim test")
            cdp.mol[0].res[0].num = 1
            cdp.mol[0].res.add_item(res_num=2)
            mol_res_spin.metadata_update()
            spins = [cdp.mol[0].res[0].spin[0], cdp.mol[0].res[1].spin[0]]
            for spin in spins:
                spin.model = model
                if model == MODEL_R2EFF:
                    spin.params = ['r2eff']
                else:
                    spin.params = deepcopy(MODEL_PARAMS[model])
                spin.chi2 = 1000.0
                spin.iter = 20
                spin.f_count = 300
                spin.g_count = 200
                spin.h_count = 100
                spin.warning = None
                spin.isotope = '15N'

            # Set the ordinary parameter values, as these are copied into the simulation structures.
            for name, param_index, spin_index, R20_key in loop_parameters(spins):
                # R1/R2 parameters.
                if name in ['r1', 'r2', 'r2a', 'r2b']:
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

            # MC simulation setup.
            api = Relax_disp()
            api.sim_init_values()

            # Checks.
            for i in range(cdp.sim_number):
                print("        Simulation %i." % i)

                # Check the probabilities.
                if 'pB' in MODEL_PARAMS[model]:
                    print("        Checking parameter pC.")
                    self.assertAlmostEqual(spins[0].pC_sim[i], 0.05)
                    self.assertAlmostEqual(spins[1].pC_sim[i], 0.05)
                elif 'pA' in MODEL_PARAMS[model]:
                    print("        Checking parameter pB.")
                    self.assertAlmostEqual(spins[0].pB_sim[i], 0.20)
                    self.assertAlmostEqual(spins[1].pB_sim[i], 0.20)

                # Check the kex-tex pair.
                if 'kex' in MODEL_PARAMS[model]:
                    print("        Checking parameter tex.")
                    self.assertAlmostEqual(spins[0].tex_sim[i], 100.0)
                    self.assertAlmostEqual(spins[1].tex_sim[i], 100.0)
                elif 'tex' in MODEL_PARAMS[model]:
                    print("        Checking parameter kex.")
                    self.assertAlmostEqual(spins[0].kex_sim[i], 0.02)
                    self.assertAlmostEqual(spins[1].kex_sim[i], 0.02)

                # Check the rates.
                if 'kex' in MODEL_PARAMS[model] and 'pA' in MODEL_PARAMS[model]:
                    print("        Checking parameter k_AB.")
                    self.assertAlmostEqual(spins[0].k_AB_sim[i], 0.002)
                    self.assertAlmostEqual(spins[1].k_AB_sim[i], 0.002)
                    print("        Checking parameter k_BA.")
                    self.assertAlmostEqual(spins[0].k_BA_sim[i], 0.008)
                    self.assertAlmostEqual(spins[1].k_BA_sim[i], 0.008)
