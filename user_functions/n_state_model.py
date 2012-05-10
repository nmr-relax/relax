###############################################################################
#                                                                             #
# Copyright (C) 2008-2012 Edward d'Auvergne                                   #
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
"""Module containing the 'n_state_model' user function data."""

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from specific_fns.setup import n_state_model_obj
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('n_state_model')
uf_class.title = "Class for the N-state models."
uf_class.menu_text = "&n_state_model"
uf_class.gui_icon = "relax.n_state_model"


# The n_state_model.CoM user function.
uf = uf_info.add_uf('n_state_model.CoM')
uf.title = "The defunct centre of mass (CoM) analysis."
uf.title_short = "CoM analysis."
uf.add_keyarg(
    name = "pivot_point",
    default = [0.0, 0.0, 0.0],
    py_type = "num_list",
    size = 3,
    desc_short = "pivot point",
    desc = "The pivot point of the motions between the two domains."
)
uf.add_keyarg(
    name = "centre",
    py_type = "num_list",
    size = 3,
    desc_short = "centre of mass",
    desc = "The optional argument for manually specifying the CoM of the initial position prior to the N rotations to the positions of the N states.",
    can_be_none = True
)
uf.desc = """
WARNING:  This analysis is now defunct!

This is used for analysing the domain motion information content of the N states from the N-state model.  The states do not correspond to physical states, hence nothing can be extracted from the individual states.  This analysis involves the calculation of the pivot to centre of mass (pivot-CoM) order parameter and subsequent cone of motions.

For the analysis, both the pivot point and centre of mass must be specified.  The supplied pivot point must be a vector of floating point numbers of length 3.  If the centre keyword argument is supplied, it must also be a vector of floating point numbers (of length 3).  If the centre argument is not supplied, then the CoM will be calculated from the selected parts of a previously loaded structure.
"""
uf.prompt_examples = """
To perform an analysis where the pivot is at the origin and the CoM is set to the N-terminal
domain of a previously loaded PDB file (the C-terminal domain has been deselected), type:

relax> n_state_model.CoM()


To perform an analysis where the pivot is at the origin (because the real pivot has been
shifted to this position) and the CoM is at the position [0, 0, 1], type one of:

relax> n_state_model.CoM(centre=[0, 0, 1])
relax> n_state_model.CoM(centre=[0.0, 0.0, 1.0])
relax> n_state_model.CoM(pivot_point=[0.0, 0.0, 0.0], centre=[0.0, 0.0, 1.0])
"""
uf.backend = n_state_model_obj._CoM
uf.menu_text = "&CoM"
uf.wizard_height_desc = 350
uf.wizard_size = (800, 600)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'n_state_model.png'


# The n_state_model.cone_pdb user function.
uf = uf_info.add_uf('n_state_model.cone_pdb')
uf.title = "Create a PDB file representing the cone models from the centre of mass (CoM) analysis."
uf.title_short = "Cone PDB creation."
uf.add_keyarg(
    name = "cone_type",
    py_type = "str",
    desc_short = "cone type",
    desc = "The type of cone model to represent.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        'diff in cone',
        'diff on cone'
    ],
    wiz_read_only = True
)

uf.add_keyarg(
    name = "scale",
    default = 1.0,
    py_type = "num",
    desc_short = "scaling factor",
    desc = "Value for scaling the pivot-CoM distance which the size of the cone defaults to."
)

uf.add_keyarg(
    name = "file",
    default = "cone.pdb",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file."
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
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which, if set to True, will overwrite the any pre-existing file."
)
uf.desc = """
WARNING:  This analysis is now defunct!

This creates a PDB file containing an artificial geometric structure to represent the various cone models.  These models include:

    'diff in cone'
    'diff on cone'

The model can be selected by setting the cone_type argument to one of these strings.  The cone is represented as an isotropic cone with its axis parallel to the average pivot-CoM vector, the vertex placed at the pivot point of the domain motions, and the length of the edge of the cone equal to the pivot-CoM distance multipled by the scaling argument.  The resultant PDB file can subsequently read into any molecular viewer.

There are four different types of residue within the PDB.  The pivot point is represented as as a single carbon atom of the residue 'PIV'.  The cone consists of numerous H atoms of the residue 'CON'.  The average pivot-CoM vector is presented as the residue 'AVE' with one carbon atom positioned at the pivot and the other at the head of the vector (after scaling by the scale argument).  Finally, if Monte Carlo have been performed, there will be multiple 'MCC' residues representing the cone for each simulation, and multiple 'MCA' residues representing the varying average pivot-CoM vector for each simulation.

To create the diffusion in a cone PDB representation, a uniform distribution of vectors on a sphere is generated using spherical coordinates with the polar angle defined from the average pivot-CoM vector.  By incrementing the polar angle using an arccos distribution, a radial array of vectors representing latitude are created while incrementing the azimuthal angle evenly creates the longitudinal vectors.  These are all placed into the PDB file as H atoms and are all connected using PDB CONECT records.  Each H atom is connected to its two neighbours on the both the longitude and latitude.  This creates a geometric PDB object with longitudinal and latitudinal lines representing the filled cone.
"""
uf.backend = n_state_model_obj._cone_pdb
uf.menu_text = "&cone_pdb"
uf.wizard_size = (800, 600)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'n_state_model.png'


# The n_state_model.elim_no_prob user function.
uf = uf_info.add_uf('n_state_model.elim_no_prob')
uf.title = "Eliminate the structures or states with no probability."
uf.title_short = "Insignificant state elimination."
uf.desc = """
This will simply remove the structures from the N-state analysis which have an optimised probability of zero.
"""
uf.prompt_examples = """
Simply type:

relax> n_state_model.elim_no_prob(N=8)
"""
uf.backend = n_state_model_obj._elim_no_prob
uf.menu_text = "&elim_no_prob"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_size = (600, 300)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'n_state_model.png'


# The n_state_model.number_of_states user function.
uf = uf_info.add_uf('n_state_model.number_of_states')
uf.title = "Set the number of states in the N-state model."
uf.title_short = "Number of states."
uf.add_keyarg(
    name = "N",
    py_type = "int",
    desc_short = "number of states N",
    desc = "The number of states.",
    can_be_none = True
)
uf.desc = """
Prior to optimisation, the number of states in the N-state model can be specified.  If the number of states is not set, then this parameter will be equal to the number of loaded structures - the ensemble size.
"""
uf.prompt_examples = """
To set up an 8-state model, type:

relax> n_state_model.number_of_states(N=8)
"""
uf.backend = n_state_model_obj._number_of_states
uf.menu_text = "&number_of_states"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'n_state_model.png'


# The n_state_model.ref_domain user function.
uf = uf_info.add_uf('n_state_model.ref_domain')
uf.title = "Set the reference domain for the '2-domain' N-state model."
uf.title_short = "Reference domain identification."
uf.add_keyarg(
    name = "ref",
    py_type = "str",
    desc_short = "reference frame",
    desc = "The domain which will act as the frame of reference.  This is only valid for the '2-domain' N-state model."
)
uf.desc = """
Prior to optimisation of the '2-domain' N-state model, which of the two domains will act as the frame of reference must be specified.  The N-states will be rotations of the other domain, so to switch the frame of reference to the other domain simply transpose the rotation matrices.
"""
uf.prompt_examples = """
To set up a 5-state model with 'C' domain being the frame of reference, type:

relax> n_state_model.ref_domain(ref='C')
"""
uf.backend = n_state_model_obj._ref_domain
uf.menu_text = "&ref_domain"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_image = WIZARD_IMAGE_PATH + 'n_state_model.png'


# The n_state_model.select_model user function.
uf = uf_info.add_uf('n_state_model.select_model')
uf.title = "Select the N-state model type and set up the model."
uf.title_short = "N-state model choice."
uf.add_keyarg(
    name = "model",
    default = "population",
    py_type = "str",
    desc_short = "model",
    desc = "The name of the preset N-state model.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["population", "fixed", "2-domain"],
    wiz_read_only = True
)
uf.desc = """
Prior to optimisation, the N-state model type should be selected.  The preset models are:

    'population' - The N-state model whereby only populations are optimised.  The structures loaded into relax are assumed to be fixed, i.e. the orientations are not optimised, or if two domains are present the Euler angles for each state are fixed.  The parameters of the model include the weight or probability for each state and the alignment tensors - {p0, p1, ..., pN, Axx, Ayy, Axy, Axz, Ayz, ...}.

    'fixed' - The N-state model whereby all motions are fixed and all populations are fixed to the set probabilities.  The parameters of the model are simply the parameters of each alignment tensor {Axx, Ayy, Axy, Axz, Ayz, ...}.

    '2-domain' - The N-state model for a system of two domains, where one domain experiences a reduced tensor.
"""
uf.prompt_examples = """
To analyse populations of states, type:

relax> n_state_model.select_model(model='populations')
"""
uf.backend = n_state_model_obj._select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 400
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'n_state_model.png'
