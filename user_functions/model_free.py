###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""Module containing the model-free analysis 'model_free' user function data."""

# Python module imports.
from os import sep

# relax module imports.
from graphics import ANALYSIS_IMAGE_PATH
from specific_fns.setup import model_free_obj
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('model_free')
uf_class.title = "Class for model-free analysis."
uf_class.menu_text = "&model_free"


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
uf.desc = """
This user function should almost never be used.  It is provided for academic reasons for the study of old analyses and published results.  If you are looking for a normal model-free model, use the model_free.select_model user function instead.
"""
uf.additional = [["Model-free equation", """
The model-free equation can be one of the following:

    - 'mf_orig' selects the original model-free equations with parameters {S2, te}.
    - 'mf_ext' selects the extended model-free equations with parameters {S2f, tf, S2, ts}.
    - 'mf_ext2' selects the extended model-free equations with parameters {S2f, tf, S2s, ts}.
"""],
["Model-free parameters", """
The following parameters are accepted for the original model-free equation:

    's2':   The square of the generalised order parameter.
    'te':   The effective correlation time.

The following parameters are accepted for the extended model-free equation:

    's2f':  The square of the generalised order parameter of the faster motion.
    'tf':   The effective correlation time of the faster motion.
    's2':   The square of the generalised order parameter S2 = S2f * S2s.
    'ts':   The effective correlation time of the slower motion.

The following parameters are accepted for the extended 2 model-free equation:

    's2f':  The square of the generalised order parameter of the faster motion.
    'tf':   The effective correlation time of the faster motion.
    's2s':  The square of the generalised order parameter of the slower motion.
    'ts':   The effective correlation time of the slower motion.

The following parameters are accepted for all equations:

    'rex':  The chemical exchange relaxation.
    'r':    The average bond length <r>.
    'csa':  The chemical shift anisotropy.
"""],
["Spin identification string", """
If 'spin_id' is supplied then the model will only be created for the corresponding spins.  Otherwise the model will be created for all spins.
"""]
]
uf.prompt_examples = """
The following commands will create the model-free model 'm1' which is based on the original
model-free equation and contains the single parameter 's2'.

relax> model_free.create_model('m1', 'mf_orig', ['s2'])
relax> model_free.create_model(model='m1', params=['s2'], equation='mf_orig')


The following commands will create the model-free model 'large_model' which is based on the
extended model-free equation and contains the seven parameters 's2f', 'tf', 's2', 'ts',
'rex', 'csa', 'r'.

relax> model_free.create_model('large_model', 'mf_ext', ['s2f', 'tf', 's2', 'ts', 'rex',
                               'csa', 'r'])
relax> model_free.create_model(model='large_model', params=['s2f', 'tf', 's2', 'ts', 'rex',
                               'csa', 'r'], equation='mf_ext')
"""
uf.backend = model_free_obj._create_model
uf.menu_text = "&create_model"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 350
uf.wizard_size = (1000, 800)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'model_free' + sep + 'model_free_200x200.png'


# The model_free.delete user function.
uf = uf_info.add_uf('model_free.delete')
uf.title = "Delete all model-free data from the current data pipe."
uf.title_short = "Model-free data deletion."
uf.display = True
uf.desc = """
This will delete all of the model-free data - parameters, model, etc. - from the current data pipe.
"""
uf.prompt_examples = """
To delete all model-free data, type:

relax> model_free.delete()
"""
uf.backend = model_free_obj._delete
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
uf.desc = """
This function will remove the local tm parameter from the model-free parameter set.  If there is no local tm parameter within the set nothing will happen.

If no spin identification string is given, then the function will apply to all spins.
"""
uf.prompt_examples = """
The following command will remove the parameter 'tm':

relax> model_free.remove_tm()
"""
uf.backend = model_free_obj._remove_tm
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
        "m1:  {S2}",
        "m2:  {S2, te}",
        "m3:  {S2, Rex}",
        "m4:  {S2, te, Rex}",
        "m5:  {S2f, S2, ts}",
        "m6:  {S2f, tf, S2, ts}",
        "m7:  {S2f, S2, ts, Rex}",
        "m8:  {S2f, tf, S2, ts, Rex}",
        "m9:  {Rex}",
        "",
        "tm0:  {tm}",
        "tm1:  {tm, S2}",
        "tm2:  {tm, S2, te}",
        "tm3:  {tm, S2, Rex}",
        "tm4:  {tm, S2, te, Rex}",
        "tm5:  {tm, S2f, S2, ts}",
        "tm6:  {tm, S2f, tf, S2, ts}",
        "tm7:  {tm, S2f, S2, ts, Rex}",
        "tm8:  {tm, S2f, tf, S2, ts, Rex}",
        "tm9:  {tm, Rex}",
        "",
        "m10:  {CSA}",
        "m11:  {CSA, S2}",
        "m12:  {CSA, S2, te}",
        "m13:  {CSA, S2, Rex}",
        "m14:  {CSA, S2, te, Rex}",
        "m15:  {CSA, S2f, S2, ts}",
        "m16:  {CSA, S2f, tf, S2, ts}",
        "m17:  {CSA, S2f, S2, ts, Rex}",
        "m18:  {CSA, S2f, tf, S2, ts, Rex}",
        "m19:  {CSA, Rex}",
        "",
        "tm10:  {tm, CSA}",
        "tm11:  {tm, CSA, S2}",
        "tm12:  {tm, CSA, S2, te}",
        "tm13:  {tm, CSA, S2, Rex}",
        "tm14:  {tm, CSA, S2, te, Rex}",
        "tm15:  {tm, CSA, S2f, S2, ts}",
        "tm16:  {tm, CSA, S2f, tf, S2, ts}",
        "tm17:  {tm, CSA, S2f, S2, ts, Rex}",
        "tm18:  {tm, CSA, S2f, tf, S2, ts, Rex}",
        "tm19:  {tm, CSA, Rex}",
        "",
        "m20:  {r}",
        "m21:  {r, S2}",
        "m22:  {r, S2, te}",
        "m23:  {r, S2, Rex}",
        "m24:  {r, S2, te, Rex}",
        "m25:  {r, S2f, S2, ts}",
        "m26:  {r, S2f, tf, S2, ts}",
        "m27:  {r, S2f, S2, ts, Rex}",
        "m28:  {r, S2f, tf, S2, ts, Rex}",
        "m29:  {r, CSA, Rex}",
        "",
        "tm20:  {tm, r}",
        "tm21:  {tm, r, S2}",
        "tm22:  {tm, r, S2, te}",
        "tm23:  {tm, r, S2, Rex}",
        "tm24:  {tm, r, S2, te, Rex}",
        "tm25:  {tm, r, S2f, S2, ts}",
        "tm26:  {tm, r, S2f, tf, S2, ts}",
        "tm27:  {tm, r, S2f, S2, ts, Rex}",
        "tm28:  {tm, r, S2f, tf, S2, ts, Rex}",
        "tm29:  {tm, r, CSA, Rex}",
        "",
        "m30:  {r, CSA}",
        "m31:  {r, CSA, S2}",
        "m32:  {r, CSA, S2, te}",
        "m33:  {r, CSA, S2, Rex}",
        "m34:  {r, CSA, S2, te, Rex}",
        "m35:  {r, CSA, S2f, S2, ts}",
        "m36:  {r, CSA, S2f, tf, S2, ts}",
        "m37:  {r, CSA, S2f, S2, ts, Rex}",
        "m38:  {r, CSA, S2f, tf, S2, ts, Rex}",
        "m39:  {r, CSA, Rex}",
        "",
        "tm30:  {tm, r, CSA}",
        "tm31:  {tm, r, CSA, S2}",
        "tm32:  {tm, r, CSA, S2, te}",
        "tm33:  {tm, r, CSA, S2, Rex}",
        "tm34:  {tm, r, CSA, S2, te, Rex}",
        "tm35:  {tm, r, CSA, S2f, S2, ts}",
        "tm36:  {tm, r, CSA, S2f, tf, S2, ts}",
        "tm37:  {tm, r, CSA, S2f, S2, ts, Rex}",
        "tm38:  {tm, r, CSA, S2f, tf, S2, ts, Rex}",
        "tm39:  {tm, r, CSA, Rex}"
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
uf.desc = """
This allows a standard model-free model to be selected from a long list of models.
"""
uf.additional = [["The preset models", """
The standard preset model-free models are
    'm0' = {},
    'm1' = {S2},
    'm2' = {S2, te},
    'm3' = {S2, Rex},
    'm4' = {S2, te, Rex},
    'm5' = {S2f, S2, ts},
    'm6' = {S2f, tf, S2, ts},
    'm7' = {S2f, S2, ts, Rex},
    'm8' = {S2f, tf, S2, ts, Rex},
    'm9' = {Rex}.

The preset model-free models with optimisation of the CSA value are
    'm10' = {CSA},
    'm11' = {CSA, S2},
    'm12' = {CSA, S2, te},
    'm13' = {CSA, S2, Rex},
    'm14' = {CSA, S2, te, Rex},
    'm15' = {CSA, S2f, S2, ts},
    'm16' = {CSA, S2f, tf, S2, ts},
    'm17' = {CSA, S2f, S2, ts, Rex},
    'm18' = {CSA, S2f, tf, S2, ts, Rex},
    'm19' = {CSA, Rex}.

The preset model-free models with optimisation of the bond length are
    'm20' = {r},
    'm21' = {r, S2},
    'm22' = {r, S2, te},
    'm23' = {r, S2, Rex},
    'm24' = {r, S2, te, Rex},
    'm25' = {r, S2f, S2, ts},
    'm26' = {r, S2f, tf, S2, ts},
    'm27' = {r, S2f, S2, ts, Rex},
    'm28' = {r, S2f, tf, S2, ts, Rex},
    'm29' = {r, CSA, Rex}.

The preset model-free models with both optimisation of the bond length and CSA are
    'm30' = {r, CSA},
    'm31' = {r, CSA, S2},
    'm32' = {r, CSA, S2, te},
    'm33' = {r, CSA, S2, Rex},
    'm34' = {r, CSA, S2, te, Rex},
    'm35' = {r, CSA, S2f, S2, ts},
    'm36' = {r, CSA, S2f, tf, S2, ts},
    'm37' = {r, CSA, S2f, S2, ts, Rex},
    'm38' = {r, CSA, S2f, tf, S2, ts, Rex},
    'm39' = {r, CSA, Rex}.

Warning:  The models in the thirties range fail when using standard R1, R2, and NOE
relaxation data.  This is due to the extreme flexibly of these models where a change in the
parameter 'r' is compensated by a corresponding change in the parameter 'csa' and
vice versa.


Additional preset model-free models, which are simply extensions of the above models with
the addition of a local tm parameter are:
    'tm0' = {tm},
    'tm1' = {tm, S2},
    'tm2' = {tm, S2, te},
    'tm3' = {tm, S2, Rex},
    'tm4' = {tm, S2, te, Rex},
    'tm5' = {tm, S2f, S2, ts},
    'tm6' = {tm, S2f, tf, S2, ts},
    'tm7' = {tm, S2f, S2, ts, Rex},
    'tm8' = {tm, S2f, tf, S2, ts, Rex},
    'tm9' = {tm, Rex}.

The preset model-free models with optimisation of the CSA value are
    'tm10' = {tm, CSA},
    'tm11' = {tm, CSA, S2},
    'tm12' = {tm, CSA, S2, te},
    'tm13' = {tm, CSA, S2, Rex},
    'tm14' = {tm, CSA, S2, te, Rex},
    'tm15' = {tm, CSA, S2f, S2, ts},
    'tm16' = {tm, CSA, S2f, tf, S2, ts},
    'tm17' = {tm, CSA, S2f, S2, ts, Rex},
    'tm18' = {tm, CSA, S2f, tf, S2, ts, Rex},
    'tm19' = {tm, CSA, Rex}.

The preset model-free models with optimisation of the bond length are
    'tm20' = {tm, r},
    'tm21' = {tm, r, S2},
    'tm22' = {tm, r, S2, te},
    'tm23' = {tm, r, S2, Rex},
    'tm24' = {tm, r, S2, te, Rex},
    'tm25' = {tm, r, S2f, S2, ts},
    'tm26' = {tm, r, S2f, tf, S2, ts},
    'tm27' = {tm, r, S2f, S2, ts, Rex},
    'tm28' = {tm, r, S2f, tf, S2, ts, Rex},
    'tm29' = {tm, r, CSA, Rex}.

The preset model-free models with both optimisation of the bond length and CSA are
    'tm30' = {tm, r, CSA},
    'tm31' = {tm, r, CSA, S2},
    'tm32' = {tm, r, CSA, S2, te},
    'tm33' = {tm, r, CSA, S2, Rex},
    'tm34' = {tm, r, CSA, S2, te, Rex},
    'tm35' = {tm, r, CSA, S2f, S2, ts},
    'tm36' = {tm, r, CSA, S2f, tf, S2, ts},
    'tm37' = {tm, r, CSA, S2f, S2, ts, Rex},
    'tm38' = {tm, r, CSA, S2f, tf, S2, ts, Rex},
    'tm39' = {tm, r, CSA, Rex}.
"""],
["Spin identification string", """
If 'spin_id' is supplied then the model will only be selected for the corresponding spins.  Otherwise the model will be selected for all spins.
"""]
]
uf.prompt_examples = """
To pick model 'm1' for all selected spins, type:

relax> model_free.select_model('m1')
relax> model_free.select_model(model='m1')
"""
uf.backend = model_free_obj._select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 450
uf.wizard_size = (1000, 800)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'model_free' + sep + 'model_free_200x200.png'
