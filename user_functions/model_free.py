###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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
"""The model_free user function definitions for model-free analysis."""

# Python module imports.
from os import sep

# relax module imports.
from graphics import ANALYSIS_IMAGE_PATH
from lib.text.gui import csa, local_tm, r, rex, s2, s2f, te, tf, ts
from specific_analyses.model_free.uf import create_model, delete, remove_tm, select_model
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('model_free')
uf_class.title = "Class for model-free analysis."
uf_class.menu_text = "&model_free"
uf_class.gui_icon = "relax.model-free"


# The model_free.create_model user function.
uf = uf_info.add_uf('model_free.create_model')
uf.title = "Create a model-free model."
uf.title_short = "Model-free model creation."
uf.display = True
uf.add_keyarg(
    name = "model",
    py_type = "str",
    desc_short = "model name",
    desc = "The new name of the model-free model."
)
uf.add_keyarg(
    name = "equation",
    py_type = "str",
    desc_short = "model-free equation",
    desc = "The model-free equation.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "Original model-free equation {S2, te}",
        "Extended model-free equation {S2f, tf, S2, ts}",
        "Extended model-free equation {S2f, tf, S2s, ts}"
    ],
    wiz_combo_data = [
        "mf_orig",
        "mf_ext",
        "mf_ext2"
    ],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "params",
    py_type = "str_list",
    desc_short = "model-free parameters",
    desc = "The array of parameter names of the model.",
    wiz_element_type = "combo_list",
    wiz_combo_choices = [
        "S2 - generalised order parameter (single motion)",
        "te - effective correlation time (single motion)",
        "S2f - generalised order parameter (faster motion)",
        "S2s - generalised order parameter (slower motion)",
        "tf - effective correlation time (faster motion)",
        "ts - effective correlation time (slower motion)",
        "Rex - chemical exchange relaxation",
        "r - average bond length <r>",
        "CSA - chemical shift anisotropy"
    ],
    wiz_combo_data = [
        "s2",
        "te",
        "s2f",
        "s2s",
        "tf",
        "ts",
        "rex",
        "r",
        "csa"
    ],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin identification string",
    desc = "The spin identification string.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This user function should almost never be used.  It is provided for academic reasons for the study of old analyses and published results.  If you are looking for a normal model-free model, use the model_free.select_model user function instead.")
# Model-free equation.
uf.desc.append(Desc_container("Model-free equation"))
uf.desc[-1].add_paragraph("The model-free equation can be one of the following:")
uf.desc[-1].add_list_element("'mf_orig' selects the original model-free equations with parameters {S2, te}.")
uf.desc[-1].add_list_element("'mf_ext' selects the extended model-free equations with parameters {S2f, tf, S2, ts}.")
uf.desc[-1].add_list_element("'mf_ext2' selects the extended model-free equations with parameters {S2f, tf, S2s, ts}.")
# Model-free parameters.
uf.desc.append(Desc_container("Model-free parameters"))
uf.desc[-1].add_paragraph("The following parameters are accepted for the original model-free equation:")
uf.desc[-1].add_item_list_element("'s2'", " The square of the generalised order parameter.")
uf.desc[-1].add_item_list_element("'te'", " The effective correlation time.")
uf.desc[-1].add_paragraph("The following parameters are accepted for the extended model-free equation:")
uf.desc[-1].add_item_list_element("'s2f'", "The square of the generalised order parameter of the faster motion.")
uf.desc[-1].add_item_list_element("'tf'", " The effective correlation time of the faster motion.")
uf.desc[-1].add_item_list_element("'s2'", " The square of the generalised order parameter S2 = S2f * S2s.")
uf.desc[-1].add_item_list_element("'ts'", " The effective correlation time of the slower motion.")
uf.desc[-1].add_paragraph("The following parameters are accepted for the extended 2 model-free equation:")
uf.desc[-1].add_item_list_element("'s2f'", "The square of the generalised order parameter of the faster motion.")
uf.desc[-1].add_item_list_element("'tf'", " The effective correlation time of the faster motion.")
uf.desc[-1].add_item_list_element("'s2s'", "The square of the generalised order parameter of the slower motion.")
uf.desc[-1].add_item_list_element("'ts'", " The effective correlation time of the slower motion.")
uf.desc[-1].add_paragraph("The following parameters are accepted for all equations:")
uf.desc[-1].add_item_list_element("'rex'", "The chemical exchange relaxation.")
uf.desc[-1].add_item_list_element("'r'", "  The average bond length <r>.")
uf.desc[-1].add_item_list_element("'csa'", "The chemical shift anisotropy.")
# Spin identification string.
uf.desc.append(Desc_container("Spin identification string"))
uf.desc[-1].add_paragraph("If 'spin_id' is supplied then the model will only be created for the corresponding spins.  Otherwise the model will be created for all spins.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following commands will create the model-free model 'm1' which is based on the original model-free equation and contains the single parameter 's2'.")
uf.desc[-1].add_prompt("relax> model_free.create_model('m1', 'mf_orig', ['s2'])")
uf.desc[-1].add_prompt("relax> model_free.create_model(model='m1', params=['s2'], equation='mf_orig')")
uf.desc[-1].add_paragraph("The following commands will create the model-free model 'large_model' which is based on the extended model-free equation and contains the seven parameters 's2f', 'tf', 's2', 'ts', 'rex', 'csa', 'r'.")
uf.desc[-1].add_prompt("relax> model_free.create_model('large_model', 'mf_ext', ['s2f', 'tf', 's2', 'ts', 'rex', 'csa', 'r'])")
uf.desc[-1].add_prompt("relax> model_free.create_model(model='large_model', params=['s2f', 'tf', 's2', 'ts', 'rex', 'csa', 'r'], equation='mf_ext')")
uf.backend = create_model
uf.menu_text = "&create_model"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 450
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'model_free' + sep + 'model_free_200x200.png'


# The model_free.delete user function.
uf = uf_info.add_uf('model_free.delete')
uf.title = "Delete all model-free data from the current data pipe."
uf.title_short = "Model-free data deletion."
uf.display = True
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will delete all of the model-free data - parameters, model, etc. - from the current data pipe.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To delete all model-free data, type:")
uf.desc[-1].add_prompt("relax> model_free.delete()")
uf.backend = delete
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_size = (600, 300)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'model_free' + sep + 'model_free_200x200.png'


# The model_free.remove_tm user function.
uf = uf_info.add_uf('model_free.remove_tm')
uf.title = "Remove the local tm parameter from a model."
uf.title_short = "Local tm parameter removal."
uf.display = True
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identification string.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This function will remove the local tm parameter from the model-free parameter set.  If there is no local tm parameter within the set nothing will happen.")
uf.desc[-1].add_paragraph("If no spin identification string is given, then the function will apply to all spins.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following command will remove the parameter 'tm':")
uf.desc[-1].add_prompt("relax> model_free.remove_tm()")
uf.backend = remove_tm
uf.menu_text = "&remove_tm"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_height_desc = 300
uf.wizard_size = (700, 400)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'model_free' + sep + 'model_free_200x200.png'


# The model_free.select_model user function.
uf = uf_info.add_uf('model_free.select_model')
uf.title = "Select a preset model-free model."
uf.title_short = "Model-free model choice."
uf.display = True
uf.add_keyarg(
    name = "model",
    py_type = "str",
    desc_short = "preset model name",
    desc = "The name of the preset model.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "m0:  {}",
        "m1:  {%s}" % s2,
        "m2:  {%s, %s}" % (s2, te),
        "m3:  {%s, %s}" % (s2, rex),
        "m4:  {%s, %s, %s}" % (s2, te, rex),
        "m5:  {%s, %s, %s}" % (s2, s2f, ts),
        "m6:  {%s, %s, %s, %s}" % (s2, tf, s2f, ts),
        "m7:  {%s, %s, %s, %s}" % (s2, s2f, ts, rex),
        "m8:  {%s, %s, %s, %s, %s}" % (s2, tf, s2f, ts, rex),
        "m9:  {%s}" % rex,
        "",
        "tm0:  {%s}" % local_tm,
        "tm1:  {%s, %s}" % (local_tm, s2),
        "tm2:  {%s, %s, %s}" % (local_tm, s2, te),
        "tm3:  {%s, %s, %s}" % (local_tm, s2, rex),
        "tm4:  {%s, %s, %s, %s}" % (local_tm, s2, te, rex),
        "tm5:  {%s, %s, %s, %s}" % (local_tm, s2, s2f, ts),
        "tm6:  {%s, %s, %s, %s, %s}" % (local_tm, s2, tf, s2f, ts),
        "tm7:  {%s, %s, %s, %s, %s}" % (local_tm, s2, s2f, ts, rex),
        "tm8:  {%s, %s, %s, %s, %s, %s}" % (local_tm, s2, tf, s2f, ts, rex),
        "tm9:  {%s, %s}" % (local_tm, rex),
        "",
        "m10:  {%s}" % csa,
        "m11:  {%s, %s}" % (csa, s2),
        "m12:  {%s, %s, %s}" % (csa, s2, te),
        "m13:  {%s, %s, %s}" % (csa, s2, rex),
        "m14:  {%s, %s, %s, %s}" % (csa, s2, te, rex),
        "m15:  {%s, %s, %s, %s}" % (csa, s2, s2f, ts),
        "m16:  {%s, %s, %s, %s, %s}" % (csa, s2, tf, s2f, ts),
        "m17:  {%s, %s, %s, %s, %s}" % (csa, s2, s2f, ts, rex),
        "m18:  {%s, %s, %s, %s, %s, %s}" % (csa, s2, tf, s2f, ts, rex),
        "m19:  {%s, %s}" % (csa, rex),
        "",
        "tm10:  {%s, %s}" % (local_tm, csa),
        "tm11:  {%s, %s, %s}" % (local_tm, csa, s2),
        "tm12:  {%s, %s, %s, %s}" % (local_tm, csa, s2, te),
        "tm13:  {%s, %s, %s, %s}" % (local_tm, csa, s2, rex),
        "tm14:  {%s, %s, %s, %s, %s}" % (local_tm, csa, s2, te, rex),
        "tm15:  {%s, %s, %s, %s, %s}" % (local_tm, csa, s2, s2f, ts),
        "tm16:  {%s, %s, %s, %s, %s, %s}" % (local_tm, csa, s2, tf, s2f, ts),
        "tm17:  {%s, %s, %s, %s, %s, %s}" % (local_tm, csa, s2, s2f, ts, rex),
        "tm18:  {%s, %s, %s, %s, %s, %s, %s}" % (local_tm, csa, s2, tf, s2f, ts, rex),
        "tm19:  {%s, %s, %s}" % (local_tm, csa, rex),
        "",
        "m20:  {%s}" % r,
        "m21:  {%s, %s}" % (r, s2),
        "m22:  {%s, %s, %s}" % (r, s2, te),
        "m23:  {%s, %s, %s}" % (r, s2, rex),
        "m24:  {%s, %s, %s, %s}" % (r, s2, te, rex),
        "m25:  {%s, %s, %s, %s}" % (r, s2, s2f, ts),
        "m26:  {%s, %s, %s, %s, %s}" % (r, s2, tf, s2f, ts),
        "m27:  {%s, %s, %s, %s, %s}" % (r, s2, s2f, ts, rex),
        "m28:  {%s, %s, %s, %s, %s, %s}" % (r, s2, tf, s2f, ts, rex),
        "m29:  {%s, %s}" % (r, rex),
        "",
        "tm20:  {%s, %s}" % (local_tm, r),
        "tm21:  {%s, %s, %s}" % (local_tm, r, s2),
        "tm22:  {%s, %s, %s, %s}" % (local_tm, r, s2, te),
        "tm23:  {%s, %s, %s, %s}" % (local_tm, r, s2, rex),
        "tm24:  {%s, %s, %s, %s, %s}" % (local_tm, r, s2, te, rex),
        "tm25:  {%s, %s, %s, %s, %s}" % (local_tm, r, s2, s2f, ts),
        "tm26:  {%s, %s, %s, %s, %s, %s}" % (local_tm, r, s2, tf, s2f, ts),
        "tm27:  {%s, %s, %s, %s, %s, %s}" % (local_tm, r, s2, s2f, ts, rex),
        "tm28:  {%s, %s, %s, %s, %s, %s, %s}" % (local_tm, r, s2, tf, s2f, ts, rex),
        "tm29:  {%s, %s, %s}" % (local_tm, r, rex),
        "",
        "m30:  {%s, %s}" % (r, csa),
        "m31:  {%s, %s, %s}" % (r, csa, s2),
        "m32:  {%s, %s, %s, %s}" % (r, csa, s2, te),
        "m33:  {%s, %s, %s, %s}" % (r, csa, s2, rex),
        "m34:  {%s, %s, %s, %s, %s}" % (r, csa, s2, te, rex),
        "m35:  {%s, %s, %s, %s, %s}" % (r, csa, s2, s2f, ts),
        "m36:  {%s, %s, %s, %s, %s, %s}" % (r, csa, s2, tf, s2f, ts),
        "m37:  {%s, %s, %s, %s, %s, %s}" % (r, csa, s2, s2f, ts, rex),
        "m38:  {%s, %s, %s, %s, %s, %s, %s}" % (r, csa, s2, tf, s2f, ts, rex),
        "m39:  {%s, %s, %s}" % (r, csa, rex),
        "",
        "tm30:  {%s, %s, %s}" % (local_tm, r, csa),
        "tm31:  {%s, %s, %s, %s}" % (local_tm, r, csa, s2),
        "tm32:  {%s, %s, %s, %s, %s}" % (local_tm, r, csa, s2, te),
        "tm33:  {%s, %s, %s, %s, %s}" % (local_tm, r, csa, s2, rex),
        "tm34:  {%s, %s, %s, %s, %s, %s}" % (local_tm, r, csa, s2, te, rex),
        "tm35:  {%s, %s, %s, %s, %s, %s}" % (local_tm, r, csa, s2, s2f, ts),
        "tm36:  {%s, %s, %s, %s, %s, %s, %s}" % (local_tm, r, csa, s2, tf, s2f, ts),
        "tm37:  {%s, %s, %s, %s, %s, %s, %s}" % (local_tm, r, csa, s2, s2f, ts, rex),
        "tm38:  {%s, %s, %s, %s, %s, %s, %s, %s}" % (local_tm, r, csa, s2, tf, s2f, ts, rex),
        "tm39:  {%s, %s, %s, %s}" % (local_tm, r, csa, rex)
    ],
    wiz_combo_data = [
        "m0",
        "m1",
        "m2",
        "m3",
        "m4",
        "m5",
        "m6",
        "m7",
        "m8",
        "m9",
        None,
        "tm0",
        "tm1",
        "tm2",
        "tm3",
        "tm4",
        "tm5",
        "tm6",
        "tm7",
        "tm8",
        "tm9",
        None,
        "m10",
        "m11",
        "m12",
        "m13",
        "m14",
        "m15",
        "m16",
        "m17",
        "m18",
        "m19",
        None,
        "tm10",
        "tm11",
        "tm12",
        "tm13",
        "tm14",
        "tm15",
        "tm16",
        "tm17",
        "tm18",
        "tm19",
        None,
        "m20",
        "m21",
        "m22",
        "m23",
        "m24",
        "m25",
        "m26",
        "m27",
        "m28",
        "m29",
        None,
        "tm20",
        "tm21",
        "tm22",
        "tm23",
        "tm24",
        "tm25",
        "tm26",
        "tm27",
        "tm28",
        "tm29",
        None,
        "m30",
        "m31",
        "m32",
        "m33",
        "m34",
        "m35",
        "m36",
        "m37",
        "m38",
        "m39",
        None,
        "tm30",
        "tm31",
        "tm32",
        "tm33",
        "tm34",
        "tm35",
        "tm36",
        "tm37",
        "tm38",
        "tm39"
    ],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identification string.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows a standard model-free model to be selected from a long list of models.")
# The preset models.
uf.desc.append(Desc_container("The preset models"))
uf.desc[-1].add_paragraph("The standard preset model-free models are")
uf.desc[-1].add_item_list_element("'m0'", "{},")
uf.desc[-1].add_item_list_element("'m1'", "{S2},")
uf.desc[-1].add_item_list_element("'m2'", "{S2, te},")
uf.desc[-1].add_item_list_element("'m3'", "{S2, Rex},")
uf.desc[-1].add_item_list_element("'m4'", "{S2, te, Rex},")
uf.desc[-1].add_item_list_element("'m5'", "{S2f, S2, ts},")
uf.desc[-1].add_item_list_element("'m6'", "{S2f, tf, S2, ts},")
uf.desc[-1].add_item_list_element("'m7'", "{S2f, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'m8'", "{S2f, tf, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'m9'", "{Rex}.")
uf.desc[-1].add_paragraph("The preset model-free models with optimisation of the CSA value are")
uf.desc[-1].add_item_list_element("'m10'", "{CSA},")
uf.desc[-1].add_item_list_element("'m11'", "{CSA, S2},")
uf.desc[-1].add_item_list_element("'m12'", "{CSA, S2, te},")
uf.desc[-1].add_item_list_element("'m13'", "{CSA, S2, Rex},")
uf.desc[-1].add_item_list_element("'m14'", "{CSA, S2, te, Rex},")
uf.desc[-1].add_item_list_element("'m15'", "{CSA, S2f, S2, ts},")
uf.desc[-1].add_item_list_element("'m16'", "{CSA, S2f, tf, S2, ts},")
uf.desc[-1].add_item_list_element("'m17'", "{CSA, S2f, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'m18'", "{CSA, S2f, tf, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'m19'", "{CSA, Rex}.")
uf.desc[-1].add_paragraph("The preset model-free models with optimisation of the bond length are")
uf.desc[-1].add_item_list_element("'m20'", "{r},")
uf.desc[-1].add_item_list_element("'m21'", "{r, S2},")
uf.desc[-1].add_item_list_element("'m22'", "{r, S2, te},")
uf.desc[-1].add_item_list_element("'m23'", "{r, S2, Rex},")
uf.desc[-1].add_item_list_element("'m24'", "{r, S2, te, Rex},")
uf.desc[-1].add_item_list_element("'m25'", "{r, S2f, S2, ts},")
uf.desc[-1].add_item_list_element("'m26'", "{r, S2f, tf, S2, ts},")
uf.desc[-1].add_item_list_element("'m27'", "{r, S2f, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'m28'", "{r, S2f, tf, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'m29'", "{r, CSA, Rex}.")
uf.desc[-1].add_paragraph("The preset model-free models with both optimisation of the bond length and CSA are")
uf.desc[-1].add_item_list_element("'m30'", "{r, CSA},")
uf.desc[-1].add_item_list_element("'m31'", "{r, CSA, S2},")
uf.desc[-1].add_item_list_element("'m32'", "{r, CSA, S2, te},")
uf.desc[-1].add_item_list_element("'m33'", "{r, CSA, S2, Rex},")
uf.desc[-1].add_item_list_element("'m34'", "{r, CSA, S2, te, Rex},")
uf.desc[-1].add_item_list_element("'m35'", "{r, CSA, S2f, S2, ts},")
uf.desc[-1].add_item_list_element("'m36'", "{r, CSA, S2f, tf, S2, ts},")
uf.desc[-1].add_item_list_element("'m37'", "{r, CSA, S2f, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'m38'", "{r, CSA, S2f, tf, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'m39'", "{r, CSA, Rex}.")
uf.desc[-1].add_paragraph("Warning:  The models in the thirties range fail when using standard R1, R2, and NOE relaxation data.  This is due to the extreme flexibly of these models where a change in the parameter 'r' is compensated by a corresponding change in the parameter 'csa' and vice versa.")
uf.desc.append(Desc_container("The preset local tm models"))
uf.desc[-1].add_paragraph("Additional preset model-free models, which are simply extensions of the above models with the addition of a local tm parameter are:")
uf.desc[-1].add_item_list_element("'tm0'", "{tm},")
uf.desc[-1].add_item_list_element("'tm1'", "{tm, S2},")
uf.desc[-1].add_item_list_element("'tm2'", "{tm, S2, te},")
uf.desc[-1].add_item_list_element("'tm3'", "{tm, S2, Rex},")
uf.desc[-1].add_item_list_element("'tm4'", "{tm, S2, te, Rex},")
uf.desc[-1].add_item_list_element("'tm5'", "{tm, S2f, S2, ts},")
uf.desc[-1].add_item_list_element("'tm6'", "{tm, S2f, tf, S2, ts},")
uf.desc[-1].add_item_list_element("'tm7'", "{tm, S2f, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'tm8'", "{tm, S2f, tf, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'tm9'", "{tm, Rex}.")
uf.desc[-1].add_paragraph("The preset model-free models with optimisation of the CSA value are")
uf.desc[-1].add_item_list_element("'tm10'", "{tm, CSA},")
uf.desc[-1].add_item_list_element("'tm11'", "{tm, CSA, S2},")
uf.desc[-1].add_item_list_element("'tm12'", "{tm, CSA, S2, te},")
uf.desc[-1].add_item_list_element("'tm13'", "{tm, CSA, S2, Rex},")
uf.desc[-1].add_item_list_element("'tm14'", "{tm, CSA, S2, te, Rex},")
uf.desc[-1].add_item_list_element("'tm15'", "{tm, CSA, S2f, S2, ts},")
uf.desc[-1].add_item_list_element("'tm16'", "{tm, CSA, S2f, tf, S2, ts},")
uf.desc[-1].add_item_list_element("'tm17'", "{tm, CSA, S2f, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'tm18'", "{tm, CSA, S2f, tf, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'tm19'", "{tm, CSA, Rex}.")
uf.desc[-1].add_paragraph("The preset model-free models with optimisation of the bond length are")
uf.desc[-1].add_item_list_element("'tm20'", "{tm, r},")
uf.desc[-1].add_item_list_element("'tm21'", "{tm, r, S2},")
uf.desc[-1].add_item_list_element("'tm22'", "{tm, r, S2, te},")
uf.desc[-1].add_item_list_element("'tm23'", "{tm, r, S2, Rex},")
uf.desc[-1].add_item_list_element("'tm24'", "{tm, r, S2, te, Rex},")
uf.desc[-1].add_item_list_element("'tm25'", "{tm, r, S2f, S2, ts},")
uf.desc[-1].add_item_list_element("'tm26'", "{tm, r, S2f, tf, S2, ts},")
uf.desc[-1].add_item_list_element("'tm27'", "{tm, r, S2f, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'tm28'", "{tm, r, S2f, tf, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'tm29'", "{tm, r, CSA, Rex}.")
uf.desc[-1].add_paragraph("The preset model-free models with both optimisation of the bond length and CSA are")
uf.desc[-1].add_item_list_element("'tm30'", "{tm, r, CSA},")
uf.desc[-1].add_item_list_element("'tm31'", "{tm, r, CSA, S2},")
uf.desc[-1].add_item_list_element("'tm32'", "{tm, r, CSA, S2, te},")
uf.desc[-1].add_item_list_element("'tm33'", "{tm, r, CSA, S2, Rex},")
uf.desc[-1].add_item_list_element("'tm34'", "{tm, r, CSA, S2, te, Rex},")
uf.desc[-1].add_item_list_element("'tm35'", "{tm, r, CSA, S2f, S2, ts},")
uf.desc[-1].add_item_list_element("'tm36'", "{tm, r, CSA, S2f, tf, S2, ts},")
uf.desc[-1].add_item_list_element("'tm37'", "{tm, r, CSA, S2f, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'tm38'", "{tm, r, CSA, S2f, tf, S2, ts, Rex},")
uf.desc[-1].add_item_list_element("'tm39'", "{tm, r, CSA, Rex}.")
# Spin identification string.
uf.desc.append(Desc_container("Spin identification string"))
uf.desc[-1].add_paragraph("If 'spin_id' is supplied then the model will only be selected for the corresponding spins.  Otherwise the model will be selected for all spins.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To pick model 'm1' for all selected spins, type:")
uf.desc[-1].add_prompt("relax> model_free.select_model('m1')")
uf.desc[-1].add_prompt("relax> model_free.select_model(model='m1')")
uf.backend = select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 450
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'model_free' + sep + 'model_free_200x200.png'
