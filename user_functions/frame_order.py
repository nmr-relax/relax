###############################################################################
#                                                                             #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
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
"""Module containing the user function data of the Frame Order theories."""

# relax module imports.
from specific_fns.setup import frame_order_obj
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('frame_order')
uf_class.title = "Class containing the user functions of the Frame Order theories."
uf_class.menu_text = "&frame_order"
uf_class.gui_icon = "relax.frame_order"


# The frame_order.cone_pdb user function.
uf = uf_info.add_uf('frame_order.cone_pdb')
uf.title = "Create a PDB file representing the Frame Order cone models."
uf.title_short = "Cone model PDB creation."
uf.add_keyarg(
    name = "size",
    default = 30.0,
    py_type = "num",
    desc_short = "geometric object size",
    desc = "The size of the geometric object in Angstroms."
)
uf.add_keyarg(
    name = "inc",
    default = 40,
    py_type = "int",
    desc_short = "increment number",
    desc = "The number of increments used to create the geometric object.",
    wiz_element_type = "spin"
)
uf.add_keyarg(
    name = "file",
    default = "cone.pdb",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file to create."
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the file is to be located.",
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
This function creates a PDB file containing an artificial geometric structure representing the Frame Order cone models.

There are four different types of residue within the PDB.  The pivot point is represented as as a single carbon atom of the residue 'PIV'.  The cone consists of numerous H atoms of the residue 'CON'.  The cone axis vector is presented as the residue 'AXE' with one carbon atom positioned at the pivot and the other x Angstroms away on the cone axis (set by the size argument).  Finally, if Monte Carlo have been performed, there will be multiple 'MCC' residues representing the cone for each simulation, and multiple 'MCA' residues representing the multiple cone axes.

To create the diffusion in a cone PDB representation, a uniform distribution of vectors on a sphere is generated using spherical coordinates with the polar angle defined by the cone axis.  By incrementing the polar angle using an arccos distribution, a radial array of vectors representing latitude are created while incrementing the azimuthal angle evenly creates the longitudinal vectors.  These are all placed into the PDB file as H atoms and are all connected using PDB CONECT records.  Each H atom is connected to its two neighbours on the both the longitude and latitude.  This creates a geometric PDB object with longitudinal and latitudinal lines representing the filled cone.
"""
uf.backend = frame_order_obj._cone_pdb
uf.menu_text = "&cone_pdb"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_height_desc = 400
uf.wizard_size = (1000, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'frame_order.png'


# The frame_order.domain_to_pdb user function.
uf = uf_info.add_uf('frame_order.domain_to_pdb')
uf.title = "Match the domains to PDB files."
uf.title_short = "Domains to PDB matching."
uf.add_keyarg(
    name = "domain",
    py_type = "str",
    desc_short = "domain",
    desc = "The domain to associate the PDB file to."
)
uf.add_keyarg(
    name = "pdb",
    py_type = "str",
    desc_short = "PDB file",
    desc = "The PDB file to associate the domain to."
)
uf.desc = """
To display the frame order cone models within Pymol, the two domains need to be associated with PDB files.  Then the reference domain will be fixed in the PDB frame, and the moving domain will be rotated to its average position.
"""
uf.prompt_examples = """
To set the 'N' domain to the PDB file 'bax_N_1J7O_1st.pdb', type one of:

relax> frame_order.domain_to_pdb('N', 'bax_N_1J7O_1st.pdb')
relax> frame_order.domain_to_pdb(domain='N', pdb='bax_N_1J7O_1st.pdb')
"""
uf.backend = frame_order_obj._domain_to_pdb
uf.menu_text = "&domain_to_pdb"
uf.wizard_image = WIZARD_IMAGE_PATH + 'frame_order.png'


# The frame_order.pivot user function.
uf = uf_info.add_uf('frame_order.pivot')
uf.title = "Set the pivot point for the two body motion in the structural coordinate system."
uf.title_short = "Pivot point setting."
uf.add_keyarg(
    name = "pivot",
    py_type = "num_list",
    size = 3,
    desc_short = "pivot point",
    desc = "The pivot point for the motion (e.g. the position between the 2 domains in PDB coordinates)."
)
uf.desc = """
This will set the pivot point for the two domain system within the PDB coordinate system.  This is required for interpreting PCS data as well as for the generation of cone or other PDB representations of the domain motions.
"""
uf.prompt_examples = """
To set the pivot point, type one of:

relax> frame_order.pivot([12.067, 14.313, -3.2675])
relax> frame_order.pivot(pivot=[12.067, 14.313, -3.2675])
"""
uf.backend = frame_order_obj._pivot
uf.menu_text = "&pivot"
uf.wizard_image = WIZARD_IMAGE_PATH + 'frame_order.png'


# The frame_order.ref_domain user function.
uf = uf_info.add_uf('frame_order.ref_domain')
uf.title = "Set the reference domain for the '2-domain' Frame Order theories."
uf.title_short = "Reference domain setting."
uf.add_keyarg(
    name = "ref",
    py_type = "str",
    desc_short = "reference frame",
    desc = "The domain which will act as the frame of reference.  This is only valid for the '2-domain' Frame Order theories."
)
uf.desc = """
Prior to optimisation of the '2-domain' Frame Order theories, which of the two domains will act as the frame of reference must be specified.  This is important for the attachment of cones to domains, etc.
"""
uf.prompt_examples = """
To set up the isotropic cone frame order model with 'centre' domain being the frame of reference, type:

relax> frame_order.ref_domain(ref='centre')
"""
uf.backend = frame_order_obj._ref_domain
uf.menu_text = "&ref_domain"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_image = WIZARD_IMAGE_PATH + 'frame_order.png'


# The frame_order.select_model user function.
uf = uf_info.add_uf('frame_order.select_model')
uf.title = "Select and set up the Frame Order model."
uf.title_short = "Model choice."
uf.add_keyarg(
    name = "model",
    py_type = "str",
    desc_short = "Frame Order model",
    desc = "The name of the preset Frame Order model.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "Free rotor model",
        "Rigid model",
        "Rotor model",
        "Free rotor line model",
        "Torsionless line model",
        "Line model",
        "Free rotor isotropic cone",
        "Torsionless isotropic cone",
        "Isotropic cone",
        "Free rotor pseudo-ellipse",
        "Torsionless pseudo-ellipse",
        "Pseudo-ellipse"
    ],
    wiz_combo_data = [
        "free rotor",
        "rigid",
        "rotor",
        "line, free rotor",
        "line, torsionless",
        "line",
        "iso cone, free rotor",
        "iso cone, torsionless",
        "iso cone",
        "pseudo-ellipse, free rotor",
        "pseudo-ellipse, torsionless",
        "pseudo-ellipse"
    ],
    wiz_read_only = True,
)
uf.desc = """
Prior to optimisation, the Frame Order model should be selected.  These models consist of three parameter categories:

    - The average domain position.  This includes the parameters ave_pos_alpha, ave_pos_beta, and ave_pos_gamma.  These Euler angles rotate the tensors from the arbitrary PDB frame of the moving domain to the average domain position.

    - The frame order eigenframe.  This includes the parameters eigen_alpha, eigen_beta, and eigen_gamma.  These Euler angles define the major modes of motion.  The cone central axis is defined as the z-axis.  The pseudo-elliptic cone x and y-axes are defined as the x and y-axes of the eigenframe.

    - The cone parameters.  These are defined as the tilt-torsion angles cone_theta_x, cone_theta_y, and cone_sigma_max.  The cone_theta_x and cone_theta_y parameters define the two cone opening angles of the pseudo-ellipse.  The amount of domain torsion is defined as the average domain position, plus and minus cone_sigma_max.  The isotropic cones are defined by setting cone_theta_x = cone_theta_y and converting the single parameter into a 2nd rank order parameter.

The list of available models are:

    'pseudo-ellipse' - The pseudo-elliptic cone model.  This is the full model consisting of the parameters ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, and cone_sigma_max.

    'pseudo-ellipse, torsionless' - The pseudo-elliptic cone with the torsion angle cone_sigma_max set to zero.

    'pseudo-ellipse, free rotor' - The pseudo-elliptic cone with no torsion angle restriction.

    'iso cone' - The isotropic cone model.  The cone is defined by a single order parameter s1 which is related to the single cone opening angle cone_theta_x = cone_theta_y.  Due to rotational symmetry about the cone axis, the average position alpha Euler angle ave_pos_alpha is dropped from the model.  The symmetry also collapses the eigenframe to a single z-axis defined by the parameters axis_theta and axis_phi.

    'iso cone, torsionless' - The isotropic cone model with the torsion angle cone_sigma_max set to zero.

    'iso cone, free rotor' - The isotropic cone model with no torsion angle restriction.

    'line' - The line cone model.  This is the pseudo-elliptic cone with one of the cone angles, cone_theta_y, assumed to be statistically negligible.  I.e. the cone angle is so small that it cannot be distinguished from noise.

    'line, torsionless' - The line cone model with the torsion angle cone_sigma_max set to zero.

    'line, free rotor' - The line cone model with no torsion angle restriction.

    'rotor' - The only motion is a rotation about the cone axis restricted by the torsion angle cone_sigma_max.

    'rigid' - No domain motions.

    'free rotor' - The only motion is free rotation about the cone axis.
"""
uf.prompt_examples = """
To select the isotropic cone model, type:

relax> frame_order.select_model(model='iso cone')
"""
uf.backend = frame_order_obj._select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 600
uf.wizard_size = (1000, 800)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'frame_order.png'
