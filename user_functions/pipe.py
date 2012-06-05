###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
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
"""The pipe user function definitions."""

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from generic_fns import pipes
from specific_fns.setup import hybrid_obj
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('pipe')
uf_class.title = "Class holding the user functions for manipulating data pipes."
uf_class.menu_text = "&pipe"
uf_class.gui_icon = "relax.pipe"


# The pipe.bundle user function.
uf = uf_info.add_uf('pipe.bundle')
uf.title = "The grouping of data pipes into a bundle."
uf.title_short = "Data pipe bundling."
uf.add_keyarg(
    name = "bundle",
    py_type = "str",
    desc_short = "pipe bundle",
    desc = "The pipe bundle is a special grouping or clustering of data pipes.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.bundle_names,
    wiz_read_only = False
)
uf.add_keyarg(
    name = "pipe",
    py_type = "str",
    desc_short = "data pipe",
    desc = "The name of the data pipe to add to the bundle.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Data pipes can be grouped or clustered together through special structures known as pipe bundles.  If the specified data pipe bundle does not currently exist, it will be created.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To add the data pipes 'test 1', 'test 2', and 'test 3' to the bundle 'first analysis', type the following:")
uf.desc[-1].add_prompt("relax> pipe.bundle('first analysis 1', 'test 1')")
uf.desc[-1].add_prompt("relax> pipe.bundle('first analysis 1', 'test 2')")
uf.desc[-1].add_prompt("relax> pipe.bundle('first analysis 1', 'test 3')")
uf.backend = pipes.bundle
uf.menu_text = "&bundle"
uf.gui_icon = "relax.pipe_bundle"
uf.wizard_image = WIZARD_IMAGE_PATH + 'pipe_bundle.png'

        
# The pipe.copy user function.
uf = uf_info.add_uf('pipe.copy')
uf.title = "Copy a data pipe."
uf.title_short = "Data pipe copying."
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "source data pipe",
    desc = "The name of the source data pipe to copy the data from.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "pipe_to",
    py_type = "str",
    desc_short = "destination data pipe",
    desc = "The name of the target data pipe to copy the data to.",
    can_be_none = True
)
uf.add_keyarg(
    name = "bundle_to",
    py_type = "str",
    desc_short = "destination pipe bundle",
    desc = "If given, the new data pipe will be grouped into this bundle.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.bundle_names,
    wiz_read_only = False,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the contents of a data pipe to be copied.  If the source data pipe is not set, the current data pipe will be assumed.  The target data pipe must not yet exist.")
uf.desc[-1].add_paragraph("The optional bundling allows the newly created data pipe to be placed into either a new or existing data pipe bundle.  If not specified, then the copied data pipe will not be associated with a bundle.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To copy the contents of the 'm1' data pipe to the 'm2' data pipe, type:")
uf.desc[-1].add_prompt("relax> pipe.copy('m1', 'm2')")
uf.desc[-1].add_prompt("relax> pipe.copy(pipe_from='m1', pipe_to='m2')")
uf.desc[-1].add_paragraph("If the current data pipe is 'm1', then the following command can be used:")
uf.desc[-1].add_prompt("relax> pipe.copy(pipe_to='m2')")
uf.backend = pipes.copy
uf.menu_text = "&copy"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_size = (800, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'pipe.png'


# The pipe.create user function.
uf = uf_info.add_uf('pipe.create')
uf.title = "Add a new data pipe to the relax data store."
uf.title_short = "Data pipe creation."
uf.add_keyarg(
    name = "pipe_name",
    py_type = "str",
    desc_short = "data pipe name",
    desc = "The name of the data pipe.",
)
uf.add_keyarg(
    name = "pipe_type",
    py_type = "str",
    desc_short = "type of data pipe",
    desc = "The type of data pipe.",
    wiz_element_type = 'combo',
    wiz_combo_choices = pipes.PIPE_DESC_LIST,
    wiz_combo_data = pipes.VALID_TYPES,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "bundle",
    py_type = "str",
    desc_short = "pipe bundle",
    desc = "The optional pipe bundle is a special grouping or clustering of data pipes.  If this is specified, the newly created data pipe will be added to this bundle.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.bundle_names,
    wiz_read_only = False,
    can_be_none = True
)
uf.backend = pipes.create
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The data pipe name can be any string however the data pipe type can only be one of the following:")
uf.desc[-1].add_item_list_element("'ct'", "Consistency testing,")
uf.desc[-1].add_item_list_element("'frame order'", "The Frame Order theories,")
uf.desc[-1].add_item_list_element("'jw'", "Reduced spectral density mapping,")
uf.desc[-1].add_item_list_element("'hybrid'", "A special hybrid pipe,")
uf.desc[-1].add_item_list_element("'mf'", "Model-free analysis,")
uf.desc[-1].add_item_list_element("'N-state'", "N-state model of domain motions,")
uf.desc[-1].add_item_list_element("'noe'", "Steady state NOE calculation,")
uf.desc[-1].add_item_list_element("'relax_fit'", "Relaxation curve fitting,")
uf.desc[-1].add_paragraph("The pipe bundling concept is simply a way of grouping data pipes together.  This is useful for a number of purposes:")
uf.desc[-1].add_list_element("The grouping or categorisation of data pipes, for example when multiple related analyses are performed.")
uf.desc[-1].add_list_element("In the auto-analyses, as all the data pipes that they spawn are bound together within the original bundle.")
uf.desc[-1].add_list_element("In the graphical user interface mode as analysis tabs are linked to specific pipe bundles.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set up a model-free analysis data pipe with the name 'm5', type:")
uf.desc[-1].add_prompt("relax> pipe.create('m5', 'mf')")
uf.menu_text = "crea&te"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'pipe.png'


# The pipe.current user function.
uf = uf_info.add_uf('pipe.current')
uf.title = "Print the name of the current data pipe."
uf.title_short = "Current data pipe printing."
uf.display = True
uf.backend = pipes.current
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To run the user function, type:")
uf.desc[-1].add_prompt("relax> pipe.current()")
uf.menu_text = "c&urrent"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_image = WIZARD_IMAGE_PATH + 'pipe.png'


# The pipe.delete user function.
uf = uf_info.add_uf('pipe.delete')
uf.title = "Delete a data pipe from the relax data store."
uf.title_short = "Data pipe deletion."
uf.add_keyarg(
    name = "pipe_name",
    py_type = "str",
    desc_short = "data pipe",
    desc = "The name of the data pipe to delete.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will permanently remove the data pipe and all of its contents from the relax data store.  If the pipe name is not given, then all data pipes will be deleted.")
uf.backend = pipes.delete
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_image = WIZARD_IMAGE_PATH + 'pipe.png'


# The pipe.display user function.
uf = uf_info.add_uf('pipe.display')
uf.title = "Print a list of all the data pipes."
uf.title_short = "Data pipe listing."
uf.display = True
uf.backend = pipes.display
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To run the user function, type:")
uf.desc[-1].add_prompt("relax> pipe.display()")
uf.menu_text = "di&splay"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_image = WIZARD_IMAGE_PATH + 'pipe.png'


# The pipe.hybridise user function.
uf = uf_info.add_uf('pipe.hybridise')
uf.title = "Create a hybrid data pipe by fusing a number of other data pipes."
uf.title_short = "Hybrid data pipe creation."
uf.add_keyarg(
    name = "hybrid",
    py_type = "str",
    desc_short = "hybrid pipe name",
    desc = "The name of the hybrid data pipe to create."
)
uf.add_keyarg(
    name = "pipes",
    py_type = "str_list",
    desc_short = "data pipes to hybridise",
    desc = "An array containing the names of all data pipes to hybridise.",
    wiz_element_type = 'combo_list',
    wiz_combo_iter = pipes.pipe_names,
    wiz_combo_list_min = 2
)
uf.backend = hybrid_obj._hybridise
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This user function can be used to construct hybrid models.  An example of the use of a hybrid model could be if the protein consists of two independent domains.  These two domains could be analysed separately, each having their own optimised diffusion tensors.  The N-terminal domain data pipe could be called 'N_sphere' while the C-terminal domain could be called 'C_ellipsoid'.  These two data pipes could then be hybridised into a single data pipe.  This hybrid data pipe can then be compared via model selection to a data pipe whereby the entire protein is assumed to have a single diffusion tensor.")
uf.desc[-1].add_paragraph("The requirements for data pipes to be hybridised is that the molecules, sequences, and spin systems for all the data pipes is the same, and that no spin system is allowed to be selected in two or more data pipes.  The selections must not overlap to allow for rigorous statistical comparisons.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The two data pipes 'N_sphere' and 'C_ellipsoid' could be hybridised into a single data pipe called 'mixed model' by typing:")
uf.desc[-1].add_prompt("relax> pipe.hybridise('mixed model', ['N_sphere', 'C_ellipsoid'])")
uf.desc[-1].add_prompt("relax> pipe.hybridise(hybrid='mixed model', pipes=['N_sphere', 'C_ellipsoid'])")
uf.menu_text = "&hybridise"
uf.gui_icon = "relax.pipe_hybrid"
uf.wizard_size = (800, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'pipe_hybrid.png'


# The pipe.switch user function.
uf = uf_info.add_uf('pipe.switch')
uf.title = "Switch between the data pipes of the relax data store."
uf.title_short = "Data pipe switching."
uf.add_keyarg(
    name = "pipe_name",
    py_type = "str",
    desc_short = "data pipe",
    desc = "The name of the data pipe.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names
)
uf.backend = pipes.switch
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will switch between the various data pipes within the relax data store.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To switch to the 'ellipsoid' data pipe, type:")
uf.desc[-1].add_prompt("relax> pipe.switch('ellipsoid')")
uf.desc[-1].add_prompt("relax> pipe.switch(pipe_name='ellipsoid')")
uf.menu_text = "&switch"
uf.gui_icon = "oxygen.actions.system-switch-user"
uf.wizard_size = (650, 450)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'pipe_switch.png'
