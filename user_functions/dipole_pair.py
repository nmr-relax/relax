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
"""The dipole_pair user function definitions."""

# Python module imports.
from os import sep
import wx

# relax module imports.
from generic_fns import pipes, dipole_pair
from graphics import WIZARD_IMAGE_PATH
from physical_constants import NH_BOND_LENGTH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('dipole_pair')
uf_class.title = "Class for manipulating magnetic dipole-dipole interactions."
uf_class.menu_text = "&dipole_pair"
uf_class.gui_icon = "relax.dipole_pair"


# The dipole_pair.define user function.
uf = uf_info.add_uf('dipole_pair.define')
uf.title = "Define the pairs of spins involved in magnetic dipole-dipole interactions."
uf.title_short = "Magnetic dipole-dipole interaction setup."
uf.add_keyarg(
    name = "spin_id1",
    default = "@N",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "first spin ID string",
    desc = "The spin identification string for the first spin of the dipolar pair."
)
uf.add_keyarg(
    name = "spin_id2",
    default = "@H",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "second spin ID string",
    desc = "The spin identification string for the second spin of the dipolar pair."
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
uf.desc[-1].add_paragraph("To analyse relaxation or residual dipolar coupling (RDC) data, pairs of spins which are coupled via the magnetic dipole-dipole interaction need to be specified.  This must proceed the use of the other user functions in this class.  An interatomic data object will be created, if it is not already present, and this will be used to store all subsequently loaded dipole-dipole data.")
uf.desc[-1].add_paragraph("For analyses which use relaxation data, specifying the dipole-dipole interaction will indicate that there is a dipolar relaxation mechanism operating between the two spins.  For RDC dependent analyses, this indicates that a residual dipolar coupling is expected between the two spins.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To define the protein 15N heteronuclear relaxation mechanism, type on of the following:")
uf.desc[-1].add_prompt("relax> dipole_pair.define('@N', '@H', True)")
uf.desc[-1].add_prompt("relax> dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)")
uf.backend = dipole_pair.define
uf.menu_text = "&define"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 350
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'dipole_pair' + sep + 'NH_dipole_pair.png'


# The dipole_pair.set_dist user function.
uf = uf_info.add_uf('dipole_pair.set_dist')
uf.title = "Define the pairs of spins involved in magnetic dipole-dipole relaxation interactions."
uf.title_short = "Magnetic dipole-dipole interaction setup."
uf.add_keyarg(
    name = "spin_id1",
    default = "@N",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "first spin ID string",
    desc = "The spin identification string for the first spin of the dipolar relaxation pair."
)
uf.add_keyarg(
    name = "spin_id2",
    default = "@H",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "second spin ID string",
    desc = "The spin identification string for the second spin of the dipolar relaxation pair."
)
uf.add_keyarg(
    name = "ave_dist",
    default = NH_BOND_LENGTH,
    py_type = "float",
    desc_short = "averaged interatomic distance (meters)",
    desc = "The r^-3 averaged distance between the two spins to be used in the magnetic dipole constant."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("To analyse relaxation data, the relaxation mechanism and related parameters needs to be defined.  This user function allows pairs of spins which are coupled via the magnetic dipole-dipole interaction to be defined.  Hence the dipolar relaxation mechanism between the two spins is to be considered active.")
uf.desc[-1].add_paragraph("For an orientational dependent analysis, such as model-free analysis with the spheroidal and ellipsoidal global diffusion tensors, the two spins should already possess positional information.  This information will be used by this user function to calculate unit vectors between the two spins.  Without positional information, no vectors can be calculated and an orientational dependent analysis will not be possible.")
uf.desc[-1].add_paragraph("As the magnetic dipole-dipole interaction is averaged in NMR over the interatomic distance to the inverse third power, the interatomic distances within a 3D structural file are of no use for defining the interaction.  Therefore these average distances must be explicitly defined.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set the N-H distance for protein the 15N heteronuclear relaxation mechanism, type on of the following:")
uf.desc[-1].add_prompt("relax> dipole_pair.set_dist('@N', '@H', 1.02 * 1e-10)")
uf.desc[-1].add_prompt("relax> dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)")
uf.backend = dipole_pair.set_dist
uf.menu_text = "&set_dist"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_height_desc = 350
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'dipole_pair' + sep + 'NH_dipole_pair.png'
