###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# relax module imports.
from specific_analyses.relax_disp.model import nesting_model, sort_models
from specific_analyses.relax_disp.variables import MODEL_B14, MODEL_B14_FULL, MODEL_CR72, MODEL_CR72_FULL, MODEL_DPL94_FIT_R1, MODEL_IT99, MODEL_MMQ_CR72, MODEL_LM63, MODEL_LM63_3SITE, MODEL_MP05_FIT_R1, MODEL_NOREX, MODEL_NOREX_R1RHO_FIT_R1, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_2SITE_FIT_R1, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR, MODEL_R2EFF, MODEL_TAP03_FIT_R1, MODEL_TP02_FIT_R1, MODEL_TSMFK01
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_model(UnitTestCase):
    """Unit tests for the functions of the specific_analyses.relax_disp.variables module."""


    def test_nesting_model_cpmg_1(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG experiments."""

        ## Test numerical model return.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_TSMFK01, MODEL_B14, MODEL_B14_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL]

        # Define which current model is selected
        model = MODEL_NS_CPMG_2SITE_STAR
        model_nest = MODEL_NS_CPMG_2SITE_3D

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_cpmg_2(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG experiments."""

        ## Test numerical full model return.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_TSMFK01, MODEL_B14, MODEL_B14_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL]

        # Define which current model is selected
        model = MODEL_NS_CPMG_2SITE_STAR_FULL
        model_nest = MODEL_NS_CPMG_2SITE_3D_FULL

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_cpmg_3(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG experiments."""

        ## Test silico simple return from a full model request.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_B14_FULL]

        # Define which current model is selected
        model = MODEL_B14_FULL
        model_nest = MODEL_NS_CPMG_2SITE_EXPANDED

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_cpmg_4(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG experiments."""

        ## Test LM63 model request.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_LM63, MODEL_LM63_3SITE]

        # Define which current model is selected
        model = MODEL_LM63_3SITE
        model_nest = MODEL_LM63

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_cpmg_5(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG experiments."""

        ## Test MODEL_CR72_FULL model request.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_CR72, MODEL_CR72_FULL, MODEL_B14, MODEL_B14_FULL]

        # Define which current model is selected
        model = MODEL_CR72_FULL
        model_nest = MODEL_CR72

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_cpmg_6(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG experiments."""

        ## Test MODEL_CR72_FULL model request, when models are ordered different.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_B14, MODEL_B14_FULL, MODEL_CR72, MODEL_CR72_FULL]

        # Define which current model is selected
        model = MODEL_CR72_FULL
        model_nest = MODEL_B14_FULL

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_cpmg_7(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG experiments."""

        ## Test MODEL_CR72 model request, when models are LM63.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_LM63, MODEL_CR72]

        # Define which current model is selected
        model = MODEL_CR72
        model_nest = MODEL_LM63

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_cpmg_8(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG experiments."""

        ## Test MODEL_IT99 model request, when models are CR72.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_CR72, MODEL_IT99]

        # Define which current model is selected
        model = MODEL_IT99
        model_nest = MODEL_CR72

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_cpmg_9(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG experiments."""

        ## Test MODEL_CR72 model request, when models are MODEL_IT99.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_IT99, MODEL_CR72]

        # Define which current model is selected
        model = MODEL_CR72
        model_nest = MODEL_IT99

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_cpmg_mmq_1(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG MMQ experiments."""

        ## Test MODEL_MMQ_CR72 model request, when models are MODEL_CR72.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_CR72, MODEL_MMQ_CR72]

        # Define which current model is selected
        model = MODEL_MMQ_CR72
        model_nest = MODEL_CR72

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_cpmg_mmq_2(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG MMQ experiments."""

        ## Test MODEL_NS_MMQ_3SITE_LINEAR model request, when models are MODEL_NS_MMQ_2SITE.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE_LINEAR]

        # Define which current model is selected
        model = MODEL_NS_MMQ_3SITE_LINEAR
        model_nest = MODEL_NS_MMQ_2SITE

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_cpmg_mmq_3(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG MMQ experiments."""

        ## Test MODEL_NS_MMQ_3SITE model request, when models are MODEL_NS_MMQ_3SITE_LINEAR.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_NS_MMQ_3SITE_LINEAR, MODEL_NS_MMQ_3SITE]

        # Define which current model is selected
        model = MODEL_NS_MMQ_3SITE
        model_nest = MODEL_NS_MMQ_3SITE_LINEAR

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_cpmg_mmq_4(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for CPMG MMQ experiments."""

        ## Test MODEL_NS_MMQ_3SITE model request, when models are MODEL_NS_MMQ_2SITE.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE]

        # Define which current model is selected
        model = MODEL_NS_MMQ_3SITE
        model_nest = MODEL_NS_MMQ_2SITE

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_r1rho_ns_1(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for numerical R1rho experiments."""

        ## Test MODEL_NS_R1RHO_3SITE_LINEAR model request, when models are MODEL_NS_R1RHO_2SITE.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE_LINEAR]

        # Define which current model is selected
        model = MODEL_NS_R1RHO_3SITE_LINEAR
        model_nest = MODEL_NS_R1RHO_2SITE

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_r1rho_ns_2(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for numerical R1rho experiments."""

        ## Test MODEL_NS_R1RHO_3SITE model request, when models are MODEL_NS_R1RHO_3SITE_LINEAR.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_NS_R1RHO_3SITE_LINEAR, MODEL_NS_R1RHO_3SITE]

        # Define which current model is selected
        model = MODEL_NS_R1RHO_3SITE
        model_nest = MODEL_NS_R1RHO_3SITE_LINEAR

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_r1rho_ns_3(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for numerical R1rho experiments."""

        ## Test MODEL_NS_R1RHO_3SITE model request, when models are MODEL_NS_R1RHO_2SITE.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE]

        # Define which current model is selected
        model = MODEL_NS_R1RHO_3SITE
        model_nest = MODEL_NS_R1RHO_2SITE

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_r1rho_1(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for R1rho experiments."""

        ## Test MODEL_MP05_FIT_R1 model request, when models are all R1rho models with fitted R1.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX_R1RHO_FIT_R1, MODEL_DPL94_FIT_R1, MODEL_TP02_FIT_R1, MODEL_TAP03_FIT_R1, MODEL_MP05_FIT_R1, MODEL_NS_R1RHO_2SITE_FIT_R1]

        # Define which current model is selected
        model = MODEL_MP05_FIT_R1
        model_nest = MODEL_TAP03_FIT_R1

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_r1rho_2(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for R1rho experiments."""

        ## Test MODEL_TP02_FIT_R1 model request, when models are all R1rho models with fitted R1, and MODEL_NS_R1RHO_2SITE_FIT_R1 was fitted first.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX_R1RHO_FIT_R1, MODEL_R2EFF, MODEL_NOREX_R1RHO_FIT_R1, MODEL_NS_R1RHO_2SITE_FIT_R1, MODEL_TP02_FIT_R1]

        # Define which current model is selected
        model = MODEL_TP02_FIT_R1
        model_nest = MODEL_NS_R1RHO_2SITE_FIT_R1

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_r1rho_3(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for R1rho experiments."""

        ## Test MODEL_DPL94_FIT_R1 model request, when models are all R1rho models with fitted R1, and MODEL_NS_R1RHO_2SITE_FIT_R1 was fitted first.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX_R1RHO_FIT_R1, MODEL_NS_R1RHO_2SITE_FIT_R1, MODEL_DPL94_FIT_R1]

        # Define which current model is selected
        model = MODEL_DPL94_FIT_R1
        model_nest = MODEL_NS_R1RHO_2SITE_FIT_R1

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_nesting_model_r1rho_4(self):
        """Unit test of function nesting_model, which determine which model to nest from, testing for R1rho experiments."""

        ## Test MODEL_TP02_FIT_R1 model request, when model are all R1rho models with fitted R1, and MODEL_DPL94_FIT_R1 was fitted first.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX_R1RHO_FIT_R1, MODEL_DPL94_FIT_R1, MODEL_TP02_FIT_R1]

        # Define which current model is selected
        model = MODEL_TP02_FIT_R1
        model_nest = MODEL_DPL94_FIT_R1

        print("self.models is:", self_models)
        print("Current model to analyse is:", model)
        print("Expected nest model is:", model_nest)

        # Test the return.
        self.assertEqual(nesting_model(self_models=self_models, model=model)[1].model, model_nest)


    def test_sort_models(self):
        """Unit test of function sort_models, which determine how to sort models for auto analyses."""

        ## Test sort of models, when models are all R1rho models with fitted R1.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX_R1RHO_FIT_R1, MODEL_DPL94_FIT_R1, MODEL_TP02_FIT_R1, MODEL_TAP03_FIT_R1, MODEL_MP05_FIT_R1, MODEL_NS_R1RHO_2SITE_FIT_R1]
        expected_result = [MODEL_R2EFF, MODEL_NOREX_R1RHO_FIT_R1, MODEL_MP05_FIT_R1, MODEL_TAP03_FIT_R1, MODEL_TP02_FIT_R1, MODEL_DPL94_FIT_R1, MODEL_NS_R1RHO_2SITE_FIT_R1]

        # Test the return.
        self.assertEqual(sort_models(models=self_models), expected_result)

        ## Test sort of models, when models are all CPMG models.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_TSMFK01, MODEL_B14, MODEL_B14_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL]
        expected_result = [MODEL_R2EFF, MODEL_NOREX, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_B14, MODEL_B14_FULL, MODEL_TSMFK01, MODEL_IT99, MODEL_CR72, MODEL_CR72_FULL, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR_FULL]

        # Test the return.
        self.assertEqual(sort_models(models=self_models), expected_result)

        ## Test sort of models, when models are all CPMG MMQ models.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_2SITE, MODEL_MMQ_CR72, MODEL_NS_MMQ_3SITE_LINEAR]
        expected_result = [MODEL_R2EFF, MODEL_NOREX, MODEL_MMQ_CR72, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE_LINEAR, MODEL_NS_MMQ_3SITE]

        # Test the return.
        self.assertEqual(sort_models(models=self_models), expected_result)

        ## Test sort of models, when models are mix of CPMG and CPMG MMQ models.
        # Define all the models tested in the analysis.
        self_models = [MODEL_R2EFF, MODEL_NOREX, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_2SITE, MODEL_MMQ_CR72, MODEL_CR72, MODEL_B14, MODEL_NS_MMQ_3SITE_LINEAR]
        expected_result = [MODEL_R2EFF, MODEL_NOREX, MODEL_B14, MODEL_CR72, MODEL_MMQ_CR72, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE_LINEAR, MODEL_NS_MMQ_3SITE]

        ## Test the return.
        self.assertEqual(sort_models(models=self_models), expected_result)

