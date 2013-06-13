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
"""The interatom user function definitions."""

# Python module imports.
import dep_check
from os import sep
if dep_check.wx_module:
    from wx import FD_OPEN
else:
    FD_OPEN = -1

# relax module imports.
from pipe_control.mol_res_spin import get_spin_ids
from pipe_control import pipes, interatomic
from graphics import WIZARD_IMAGE_PATH
from lib.physical_constants import NH_BOND_LENGTH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('interatom')
uf_class.title = "Class for manipulating magnetic dipole-dipole interactions."
uf_class.menu_text = "&interatom"
uf_class.gui_icon = "relax.dipole_pair"


# The interatom.copy user function.
uf = uf_info.add_uf('interatom.copy')
uf.title = "Copy all data associated with a interatomic data container."
uf.title_short = "Spin copying."
uf.display = True
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "source data pipe",
    desc = "The data pipe containing the interatomic data container from which the data will be copied.  This defaults to the current data pipe.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "pipe_to",
    py_type = "str",
    desc_short = "destination data pipe",
    desc = "The data pipe to copy the interatomic data container to.  This defaults to the current data pipe.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id1",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "first spin ID",
    desc = "The spin ID of the first spin.",
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id2",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "second spin ID",
    desc = "The spin ID of the first spin.",
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will copy all the data associated with the identified interatomic data container to a different data pipe.  The new interatomic data container must not already exist.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To copy the interatomic data container between ':2@C' and ':2@H', from the 'orig' data pipe to the current data pipe, type one of:")
uf.desc[-1].add_prompt("relax> interatom.copy('orig', spin_id1=':2@C', spin_id2=':2@H')")
uf.desc[-1].add_prompt("relax> interatom.copy(pipe_from='orig', spin_id1=':2@C', spin_id2=':2@H')")
uf.backend = interatomic.copy
uf.menu_text = "&copy"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_size = (700, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'dipole_pair' + sep + 'NH_dipole_pair.png'


# The interatom.create user function.
uf = uf_info.add_uf('interatom.create')
uf.title = "Create a new spin."
uf.title_short = "Spin creation."
uf.display = True
uf.add_keyarg(
    name = "spin_id1",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "first spin ID",
    desc = "The spin ID of the first spin.",
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id2",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "second spin ID",
    desc = "The spin ID of the first spin.",
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
uf.add_keyarg(
    name = "pipe",
    py_type = "str",
    desc_short = "alternative data pipe",
    desc = "The data pipe to create the interatomic data container for.  This defaults to the current data pipe if not supplied.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will add a new interatomic data container connecting two existing spins to the relax data storage object.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To connect the spins ':1@N' to ':1@H', type one of:")
uf.desc[-1].add_prompt("relax> interatom.create(':1@N', ':1@H')")
uf.desc[-1].add_prompt("relax> interatom.create(spin_id1=':1@N', spin_id2=':1@H')")
uf.backend = interatomic.create_interatom
uf.menu_text = "c&reate"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'dipole_pair' + sep + 'NH_dipole_pair.png'


# The interatom.define user function.
uf = uf_info.add_uf('interatom.define')
uf.title = "Define interatomic interactions between pairs of spins."
uf.title_short = "Interatomic interaction setup."
uf.add_keyarg(
    name = "spin_id1",
    default = "@N",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "first spin ID string",
    desc = "The spin identification string for the first spin of the dipole pair."
)
uf.add_keyarg(
    name = "spin_id2",
    default = "@H",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "second spin ID string",
    desc = "The spin identification string for the second spin of the dipole pair."
)
uf.add_keyarg(
    name = "direct_bond",
    default = True,
    py_type = "bool",
    desc_short = "directly bonded atoms flag",
    desc = "This is a flag which if True means that the two spins are directly bonded.  This flag is useful to simply the set up of the main heteronuclear relaxation mechanism or one-bond residual dipolar couplings."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("To analyse relaxation or residual dipolar coupling (RDC) data, for example, pairs of spins which are coupled via the magnetic dipole-dipole interaction need to be defined.  This function will create an interatomic data object which will be used to store all all information about the interactomic interaction.")
uf.desc[-1].add_paragraph("For analyses which use relaxation data, simply defining the interatomic interaction will indicate that there is a dipolar relaxation mechanism operating between the two spins.  Note that for model-free analyses or reduced spectral density mapping, only a single relaxation mechanism can be handled.  For RDC dependent analyses, this indicates that dipolar coupling is expected between the two spins.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To define the protein 15N heteronuclear relaxation mechanism for a model-free analysis, type one of the following:")
uf.desc[-1].add_prompt("relax> interatom.define('@N', '@H', True)")
uf.desc[-1].add_prompt("relax> interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)")
uf.backend = interatomic.define
uf.menu_text = "&define"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 350
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'dipole_pair' + sep + 'NH_dipole_pair.png'


# The interatom.read_dist user function.
uf = uf_info.add_uf('interatom.read_dist')
uf.title = "Load the inter-spin distances for the interatomic interactions from a file."
uf.title_short = "Interatomic distance loading."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file containing the averaged distance data.",
    wiz_filesel_style = FD_OPEN
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the file is located.",
    can_be_none = True
)
uf.add_keyarg(
    name = "unit",
    default = "meter",
    py_type = "str",
    desc_short = "distance unit",
    desc = "The unit of distance.  The default is 'meter', but 'Angstrom' can also be specified.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["meter", "Angstrom"],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "spin_id1_col",
    default = 1,
    py_type = "int",
    min = 1,
    desc_short = "first spin ID column",
    desc = "The spin ID string column for the first spin."
)
uf.add_keyarg(
    name = "spin_id2_col",
    default = 2,
    py_type = "int",
    min = 1,
    desc_short = "second spin ID column",
    desc = "The spin ID string column for the second spin."
)
uf.add_keyarg(
    name = "data_col",
    default = 3,
    py_type = "int",
    min = 1,
    desc_short = "data column",
    desc = "The distance data column."
)
uf.add_keyarg(
    name = "sep",
    py_type = "str",
    desc_short = "column separator",
    desc = "The column separator (the default is white space).",
    wiz_element_type = "combo",
    wiz_combo_choices = ["white space", ",", ";", ":"],
    wiz_combo_data = [None, ",", ";", ":"],
    wiz_read_only = False,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows interatomic distances to be read from a file.  This is useful in the case when the distances vary, avoiding having to tediously use the interatom.set_dist user function for each spin-pair separately.  The format of the file should be columnar, with the two spin ID strings in two separate columns and the distances in any other.  The default measurement unit is 'meter' but this can be changed to 'Angstrom'.")
uf.desc[-1].add_paragraph("For RDC and relaxation based anylses, as the magnetic dipole-dipole interaction is averaged in NMR over the interatomic distance to the inverse third power, the interatomic distances within a 3D structural file are of no use for defining the interaction.  Therefore these r^-3 average distances must be explicitly defined.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To load the distances in meters from the fifth column of the 'distances' file, and where the spin IDs are in the first and second columns, type one of the following:")
uf.desc[-1].add_prompt("relax> interatom.read_dist('distances', 1, 2, 5)")
uf.desc[-1].add_prompt("relax> interatom.read_dist(file='distances', unit='meter', spin_id1_col=1, spin_id2_col=2, data_col=5)")
uf.backend = interatomic.read_dist
uf.menu_text = "&read_dist"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 350
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'dipole_pair' + sep + 'NH_dipole_pair.png'


# The interatom.set_dist user function.
uf = uf_info.add_uf('interatom.set_dist')
uf.title = "Set the inter-spin distances for the interatomic interactions."
uf.title_short = "Magnetic dipole-dipole distance setup."
uf.add_keyarg(
    name = "spin_id1",
    default = "@N",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "first spin ID string",
    desc = "The spin identification string for the first spin of the dipole pair."
)
uf.add_keyarg(
    name = "spin_id2",
    default = "@H",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "second spin ID string",
    desc = "The spin identification string for the second spin of the dipole pair."
)
uf.add_keyarg(
    name = "ave_dist",
    default = NH_BOND_LENGTH,
    py_type = "float",
    desc_short = "averaged interatomic distance",
    desc = "The r^-3 averaged distance between the two spins to be used in the magnetic dipole constant, defaulting to meters."
)
uf.add_keyarg(
    name = "unit",
    default = "meter",
    py_type = "str",
    desc_short = "distance unit",
    desc = "The unit of distance (the default is 'meter').",
    wiz_element_type = "combo",
    wiz_combo_choices = ["meter", "Angstrom"],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("As the magnetic dipole-dipole interaction is averaged in NMR over the interatomic distance to the inverse third power, the interatomic distances within a 3D structural file are of no use for defining the interaction.  Therefore these average distances must be explicitly supplied.  This user function allows these distances to be set up.  The default measurement unit is 'meter' but this can be changed to 'Angstrom'.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set the N-H distance for protein the 15N heteronuclear relaxation mechanism to 1.02 Angstrom, type one of the following:")
uf.desc[-1].add_prompt("relax> interatom.set_dist('@N', '@H', 1.02 * 1e-10)")
uf.desc[-1].add_prompt("relax> interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10, unit='meter')")
uf.desc[-1].add_prompt("relax> interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02, unit='Angstrom')")
uf.backend = interatomic.set_dist
uf.menu_text = "&set_dist"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_height_desc = 350
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'dipole_pair' + sep + 'NH_dipole_pair.png'


# The interatom.unit_vectors user function.
uf = uf_info.add_uf('interatom.unit_vectors')
uf.title = "Calculate the unit vectors for all interatomic interactions."
uf.title_short = "Interatomic unit vector calculation."
uf.add_keyarg(
    name = "ave",
    default = True,
    py_type = "bool",
    desc_short = "average vector flag",
    desc = "A flag which if True will cause the bond vectors from all models to be averaged.  If vectors from only one model is extracted, this will have no effect."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("For an orientational dependent analysis, such as model-free analysis with the spheroidal and ellipsoidal global diffusion tensors or any analysis using RDCs, the unit vectors between the two dipoles must be calculated prior to starting the analysis.  For the unit vector extraction, the two interacting spins should already possess positional information and the dipole-dipole interaction should already be defined via the interatom.define user function.  This information will be used to calculate unit vectors between the two spins.  Without positional information, no vectors can be calculated and an orientational dependent analysis will not be possible.")
uf.desc[-1].add_paragraph("The number of unit vectors per interaction will be defined by the number of positions each spin possesses together with the averaging flag.  If both spins have N and M positions loaded, the number of positions for both must match (N=M).  In this case, as well as when one spin has N positions and the other a single position, then N unit vectors will be calculated.  This is unless the averaging flag is set in which case an averaged vector of unit length will be calculated.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To calculate the unit vectors prior to a model-free analysis, type one of the following:")
uf.desc[-1].add_prompt("relax> interatom.unit_vectors(True)")
uf.desc[-1].add_prompt("relax> interatom.unit_vectors(ave=True)")
uf.backend = interatomic.unit_vectors
uf.menu_text = "&unit_vectors"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'dipole_pair' + sep + 'NH_dipole_pair.png'
