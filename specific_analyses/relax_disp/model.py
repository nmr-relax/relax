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

# Module docstring.
"""Functions for sorting and nesting the models in relaxation dispersion specific analysis."""

# Python module imports.
from datetime import date
from functools import partial
from operator import attrgetter, ne

# relax module imports.
from specific_analyses.relax_disp.variables import EQ_ANALYTIC, EQ_NUMERIC, EQ_SILICO, EXP_TYPE_CPMG_MMQ, EXP_TYPE_R1RHO, EXP_TYPE_CPMG_SQ, EXP_TYPE_NOREX, EXP_TYPE_NOREX_R1RHO, EXP_TYPE_R2EFF, MODEL_DESC, MODEL_EQ, MODEL_EXP_TYPE, MODEL_LIST_ANALYTIC_CPMG, MODEL_LIST_NUMERIC_CPMG, MODEL_LIST_R1RHO_FIT_R1_ONLY, MODEL_LIST_R1RHO_W_R1_ONLY, MODEL_CR72, MODEL_DPL94, MODEL_DPL94_FIT_R1, MODEL_IT99, MODEL_LM63, MODEL_LM63_3SITE, MODEL_MMQ_CR72, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR, MODEL_PARAMS, MODEL_SITES, MODEL_YEAR, PARAMS_R20


# Define class for describing the model.
# This class is defined to be able to make better sorting of the models.
class model_class:
    def __init__(self, model=None, desc=None, exp_type=None, eq=None, sites=None, year=None, params=None, params_nr=None):
        """Class for storing model information.

        @keyword model:     Current model
        @type model:        str
        @keyword desc:      Model description.
        @type desc:         str
        @keyword exp_type:  Model experiment type.
        @type exp_type:     str
        @keyword eq:        Model equation type.
        @type eq:           str
        @keyword sites:     Number of chemical sites in model.
        @type site:         int
        @keyword year:      Which year model was described or published.
        @type year:         int
        @keyword params:    Parameters belonging to model.
        @type params:       list of str
        @keyword params_nr: Nr of parameters belonging to model.
        @type params_nr:    int
        """

        # Save the info to variables.
        self.model = model
        self.desc = desc
        self.exp_type = exp_type
        self.eq = eq
        self.sites = sites
        self.year = year
        self.params = params
        self.params_nr = params_nr

        # Define the order of how exp type ranks.
        order_exp_type = [EXP_TYPE_R2EFF, EXP_TYPE_NOREX, EXP_TYPE_NOREX_R1RHO, EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_MMQ, EXP_TYPE_R1RHO]

        # Save the index of current model to order of equation type.
        self.exp_type_i = order_exp_type.index(self.exp_type)

        # Define the order of how equation type ranks.
        order_eq = [EQ_NUMERIC, EQ_SILICO, EQ_ANALYTIC]

        # Save the index of current model to order of equation type.
        self.eq_i = order_eq.index(self.eq)

        # Define the order of how equation type ranks, when sorting before auto analyses.
        order_s = [EQ_ANALYTIC, EQ_SILICO, EQ_NUMERIC]

        # Save the index of current model to order of equation type.
        self.eq_s = order_s.index(self.eq)

        # Save the difference in year from now, to implemented model.
        self.year_diff = date.today().year - self.year

    # Make a readable presentation of the class object. Here a tuple.
    def __repr__(self):
        return repr((self.model, self.desc, self.exp_type, self.eq, self.sites, self.year, self.params, self.params_nr))


# Define function, to return model info.
def models_info(models=None):
    """Get model info for list of models.

    @keyword model:   The list of all models analysed.
    @type model:      list of str
    @return:          List of tuples, where each tuple contains model info.
    @rtype:           List of tuples with str.
    """

    # Define list of return.
    models_info = []

    # Loop over models.
    for model in models:
        # model description.
        model_DESC = MODEL_DESC[model]

        # model equation type: analytic, silico or numeric.
        model_EQ = MODEL_EQ[model]

        # The model experiment type.
        model_EXP_TYPE = MODEL_EXP_TYPE[model]

        # model parameters.
        model_PARAMS = MODEL_PARAMS[model]

        # model number of parameters.
        model_PARAMS_NR = len(model_PARAMS)

        # The number of chemical sites.
        model_SITES = MODEL_SITES[model]

        # year where model was developed or published.
        model_YEAR = MODEL_YEAR[model]

        # Append to the list, the class instance of model info.
        models_info.append(model_class(model=model, desc=model_DESC, exp_type=model_EXP_TYPE, eq=model_EQ, sites=model_SITES, year=model_YEAR, params=model_PARAMS, params_nr=model_PARAMS_NR))

    # Return the list of model info.
    return models_info


# Define function, to determine which model to nest from.
def nesting_model(self_models=None, model=None):
    """Determine if the current model can use nested results from any of the previous analysed models.

    @keyword self_models:   The list of all models analysed.
    @type self_models:      list of str
    @keyword model:         The current model to analyse.
    @type model:            str
    @return:                The current model info, the possible nest model info.
    @rtype:                 class, class
    """


    # Get the list index for the current model in all models.
    model_index = self_models.index(model)

    # Define the list of models which can be tested. This is the number of models which have already been tested.
    completed_models = self_models[:model_index]

    # Get the current models information.
    model_info = models_info([model])[0]

    # Get the info of the completed models.
    completed_models_info = models_info(completed_models)

    # Sort the models according to: exp_type, equation type, chemical sites, year for model, number of parameters.
    completed_models_info = sorted(completed_models_info, key=attrgetter('exp_type_i', 'eq_i', 'sites', 'year_diff', 'params_nr'))

    # Define list of comparable models
    compa_models = []

    # Loop over the list of model info.
    for compl_model_info in completed_models_info:
        # If the exp_type is the same, add to list of comparable models.
        if compl_model_info.exp_type == model_info.exp_type:
            compa_models.append(compl_model_info)

    # Now determine how to report the nested models, if there exist comparable models.
    if len(compa_models) >= 1:
        # Loop over the list of comparable models, if the parameters are the same, return that as nested model.
        for compa_model in compa_models:
            if compa_model.params == model_info.params:
                return model_info, compa_model

        # Loop over the list of comparable models, if the parameters (other than R20 params) are the same, return that as nested model.
        for compa_model in compa_models:
            # Remove R20 params.
            part_compa_model_params = compa_model.params
            part_model_params = model_info.params
            for r20 in PARAMS_R20:
                part_compa_model_params = filter(partial(ne, r20), part_compa_model_params)
                part_model_params = filter(partial(ne, r20), part_model_params)

            # If the partial params are the same, then return that model.
            if part_compa_model_params == part_model_params:
                return model_info, compa_model

        # Loop over the list of comparable models, if the parameters are part of the more complex model, return that as nested model.
        for compa_model in compa_models:
            # If the params list are within the parameter list, then return that model.
            param_in = False

            # Loop over the parameters.
            for param in compa_model.params:
                if param in model_info.params:
                    param_in = True

                # Special situation, where 'kex' can still be nested from DPL94 model.
                elif param == 'phi_ex' and compa_model.model in MODEL_LIST_R1RHO_W_R1_ONLY + MODEL_LIST_R1RHO_FIT_R1_ONLY and model in MODEL_LIST_R1RHO_W_R1_ONLY + MODEL_LIST_R1RHO_FIT_R1_ONLY:
                    continue

                # Special situation, where 'kex' can still be nested from LM63 model.
                elif param == 'phi_ex' and compa_model.model in MODEL_LIST_ANALYTIC_CPMG + MODEL_LIST_NUMERIC_CPMG and model in MODEL_LIST_ANALYTIC_CPMG + MODEL_LIST_NUMERIC_CPMG:
                    continue

                # Special situation, where 'kex'=1/tex can still be nested from IT99 model.
                elif param == 'tex' and compa_model.model in MODEL_LIST_ANALYTIC_CPMG + MODEL_LIST_NUMERIC_CPMG and model in MODEL_LIST_ANALYTIC_CPMG + MODEL_LIST_NUMERIC_CPMG:
                    continue

                # Else break out of the loop.
                else:
                    # Break the for loop, if not found.
                    param_in = False
                    break

            # If all parameters are found in the more complex model.
            if param_in:
                return model_info, compa_model

        # Special case for LM63
        if model == MODEL_LM63_3SITE:
            # Loop over the models.
            for compa_model in compa_models:
                # If one of the comparable models is MODEL_LM63, return this.
                if compa_model.model == MODEL_LM63:
                    return model_info, compa_model

        # Special case for MODEL_NS_MMQ_3SITE or MODEL_NS_MMQ_3SITE_LINEAR, getting parameters from MODEL_NS_MMQ_2SITE.
        elif model in [MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]:
            # Loop over the models.
            for compa_model in compa_models:
                # If one of the comparable models is MODEL_NS_MMQ_2SITE, return this.
                if compa_model.model == MODEL_NS_MMQ_2SITE:
                    return model_info, compa_model

        # Special case for MODEL_NS_R1RHO_3SITE or MODEL_NS_R1RHO_3SITE_LINEAR, getting parameters from MODEL_NS_R1RHO_2SITE.
        elif model in [MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR]:
            # Loop over the models.
            for compa_model in compa_models:
                # If one of the comparable models is MODEL_NS_MMQ_2SITE, return this.
                if compa_model.model == MODEL_NS_R1RHO_2SITE:
                    return model_info, compa_model

        # Special case for DPL94.
        elif model in [MODEL_DPL94, MODEL_DPL94_FIT_R1]:
            # Loop over the models.
            for compa_model in compa_models:
                # If one of the comparable models is in list with R1rho R1, return this.
                if compa_model.model in MODEL_LIST_R1RHO_W_R1_ONLY + MODEL_LIST_R1RHO_FIT_R1_ONLY:
                    return model_info, compa_model

        # Special case for IT99.
        elif model in [MODEL_IT99]:
            # Loop over the models.
            for compa_model in compa_models:
                # If one of the comparable models is in list with R1rho R1, return this.
                if compa_model.model in MODEL_LIST_ANALYTIC_CPMG + MODEL_LIST_NUMERIC_CPMG:
                    return model_info, compa_model

        # If all fails.
        return model_info, None

    # If there is no comparable models according to EXP_TYPE, check if some models can be nested anyway.
    else:
        # Define list of comparable models, to be all completed models.
        compa_models = completed_models_info

        # Special case for MODEL_MMQ_CR72.
        if model == MODEL_MMQ_CR72:
            # Loop over the models.
            for compa_model in compa_models:
                # If one of the comparable models is MODEL_CR72, return this.
                if compa_model.model == MODEL_CR72:
                    return model_info, compa_model

        else:
            return model_info, None


# Define function, to sort models.
def sort_models(models=None):
    """Determine how to order the models for analyses.

    @keyword models:   The list of all models to be analysed.
    @type models:      list of str
    @return:           The ordered list how models should be analysed.
    @rtype:            list of str
    """

    # Get the info of the models selected for analysis.
    all_models_info = models_info(models)

    # Sort the models according to: exp_type, equation type, chemical sites, year for model, number of parameters.
    all_models_info_sorted = sorted(all_models_info, key=attrgetter('exp_type_i', 'eq_s', 'sites', 'year', 'params_nr'))

    # Define list of sorted models.
    sorted_models = []

    # Loop over the models info, and extract model.
    for model_info in all_models_info_sorted:
        sorted_models.append(model_info.model)

    # Return sorted list of models.
    return sorted_models

