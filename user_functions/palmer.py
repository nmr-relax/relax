###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""The palmer user function definitions for controlling the Modelfree4 software."""

# relax module imports.
from pipe_control import palmer
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('palmer')
uf_class.title = "Class for interfacing with Art Palmer's Modelfree 4."
uf_class.menu_text = "&palmer"
uf_class.gui_icon = "relax.modelfree4"


# The palmer.create user function.
uf = uf_info.add_uf('palmer.create')
uf.title = "Create the Modelfree4 input files."
uf.title_short = "Modelfree4 input file creation."
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory to place the files.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause the results file to be overwritten if it already exists."
)
uf.add_keyarg(
    name = "binary",
    default = "modelfree4",
    py_type = "str",
    desc_short = "Modelfree executable file",
    desc = "The name of the executable Modelfree program file."
)
uf.add_keyarg(
    name = "diff_search",
    default = "none",
    py_type = "str",
    desc_short = "diffusion search",
    desc = "See the Modelfree4 manual for 'diffusion_search'."
)
uf.add_keyarg(
    name = "sims",
    default = 0,
    py_type = "int",
    desc_short = "Monte Carlo simulation number",
    desc = "The number of Monte Carlo simulations."
)
uf.add_keyarg(
    name = "sim_type",
    default = "pred",
    py_type = "str",
    desc_short = "simulation type",
    desc = "See the Modelfree4 manual."
)
uf.add_keyarg(
    name = "trim",
    default = 0,
    py_type = "num",
    desc_short = "trimming",
    desc = "See the Modelfree4 manual."
)
uf.add_keyarg(
    name = "steps",
    default = 20,
    py_type = "int",
    desc_short = "grid search steps",
    desc = "See the Modelfree4 manual."
)
uf.add_keyarg(
    name = "constraints",
    default = True,
    py_type = "bool",
    desc_short = "constraints flag",
    desc = "A flag specifying whether the parameters should be constrained.  The default is to turn constraints on (constraints=True)."
)
uf.add_keyarg(
    name = "heteronuc_type",
    default = "15N",
    py_type = "str",
    desc_short = "heteronucleus",
    desc = "A three letter string describing the heteronucleus type, ie '15N', '13C', etc."
)
uf.add_keyarg(
    name = "atom1",
    default = "N",
    py_type = "str",
    desc_short = "atom1",
    desc = "The symbol of the X heteronucleus in the PDB file."
)
uf.add_keyarg(
    name = "atom2",
    default = "H",
    py_type = "str",
    desc_short = "atom2",
    desc = "The symbol of the H nucleus in the PDB file."
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
uf.desc[-1].add_paragraph("The following files are created")
uf.desc[-1].add_list_element("'dir/mfin'")
uf.desc[-1].add_list_element("'dir/mfdata'")
uf.desc[-1].add_list_element("'dir/mfpar'")
uf.desc[-1].add_list_element("'dir/mfmodel'")
uf.desc[-1].add_list_element("'dir/run.sh'")
uf.desc[-1].add_paragraph("The file 'dir/run.sh' contains the single command,")
uf.desc[-1].add_item_list_element(None, "'modelfree4 -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out',")
uf.desc[-1].add_paragraph("which can be used to execute modelfree4.")
uf.desc[-1].add_paragraph("If you would like to use a different Modelfree executable file, change the binary name to the appropriate file name.  If the file is not located within the environment's path, include the full path in front of the binary file name.")
uf.backend = palmer.create
uf.menu_text = "&create"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 230
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'modelfree4.png'


# The palmer.execute user function.
uf = uf_info.add_uf('palmer.execute')
uf.title = "Perform a model-free optimisation using Modelfree4."
uf.title_short = "Modelfree4 execution."
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory to place the files.",
    can_be_none = True
)

uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause the results file to be overwritten if it already exists."
)

uf.add_keyarg(
    name = "binary",
    default = "modelfree4",
    py_type = "str",
    desc_short = "Modelfree4 executable file",
    desc = "The name of the executable Modelfree program file."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Modelfree 4 will be executed as")
uf.desc[-1].add_prompt("$ modelfree4 -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out")
uf.desc[-1].add_paragraph("If a PDB file is loaded and non-isotropic diffusion is selected, then the file name will be placed on the command line as '-s pdb_file_name'.")
uf.desc[-1].add_paragraph("If you would like to use a different Modelfree executable file, change the binary name to the appropriate file name.  If the file is not located within the environment's path, include the full path in front of the binary file name.")
uf.backend = palmer.execute
uf.gui_icon = "oxygen.categories.applications-education"
uf.menu_text = "&execute"
uf.wizard_size = (800, 600)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'modelfree4.png'


# The palmer.extract user function.
uf = uf_info.add_uf('palmer.extract')
uf.title = "Extract data from the Modelfree4 'mfout' star formatted file."
uf.title_short = "Modelfree4 data extraction."
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory where the file 'mfout' is found.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The model-free results will be extracted from the Modelfree4 results file 'mfout' located in the given directory.")
uf.backend = palmer.extract
uf.menu_text = "ex&tract"
uf.gui_icon = "oxygen.actions.archive-extract"
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'modelfree4.png'
