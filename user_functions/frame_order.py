###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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
"""The frame_order user function definitions."""

# Python module imports.
import dep_check
if dep_check.wx_module:
    from wx import FD_SAVE
else:
    FD_SAVE = -1

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from specific_analyses.frame_order.uf import num_int_pts, pdb_model, pivot, ref_domain, select_model
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container
from user_functions.wildcards import WILDCARD_STRUCT_PDB_ALL


# The user function class.
uf_class = uf_info.add_class('frame_order')
uf_class.title = "Class containing the user functions of the Frame Order theories."
uf_class.menu_text = "&frame_order"
uf_class.gui_icon = "relax.frame_order"


# The frame_order.pdb_model user function.
uf = uf_info.add_uf('frame_order.pdb_model')
uf.title = "Create a PDB file representation of the frame order dynamics."
uf.title_short = "Frame order dynamics PDB representation."
uf.add_keyarg(
    name = "ave_pos",
    default = "ave_pos",
    py_type = "str",
    arg_type = "str",
    desc_short = "average structure file root",
    desc = "The file root of the 3D structure PDB file for the molecular structure with the moving domains shifted to the average position.",
    can_be_none = True
)
uf.add_keyarg(
    name = "rep",
    default = "frame_order",
    py_type = "str",
    arg_type = "str",
    desc_short = "PDB representation file root",
    desc = "The file root of the PDB file for the geometric object representation of the frame order dynamics.",
    can_be_none = True
)
uf.add_keyarg(
    name = "dist",
    default = "domain_distribution",
    py_type = "str",
    arg_type = "str",
    desc_short = "distribution file root",
    desc = "The file root of the file which will contain multiple models spanning the full dynamics distribution of the frame order model.",
    can_be_none = True
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the files are to be located.",
    can_be_none = True
)
uf.add_keyarg(
    name = "compress_type",
    default = 0,
    py_type = "int",
    desc_short = "file compression",
    desc = "The type of compression to use when creating the files.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "No compression",
        "bzip2 compression",
        "gzip compression"
    ],
    wiz_combo_data = [
        0,
        1,
        2
    ],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "size",
    default = 30.0,
    py_type = "num",
    desc_short = "geometric object size",
    desc = "The size of the geometric object in Angstroms."
)
uf.add_keyarg(
    name = "inc",
    default = 36,
    py_type = "int",
    desc_short = "increment number",
    desc = "The number of increments used to create the geometric object.",
    wiz_element_type = "spin"
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which, if set to True, will overwrite the any pre-existing files."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This function creates a set of PDB files for representing the frame order cone models.  This includes a file for the average position of the molecule, a file containing a geometric representation of the frame order motions, and a file containing a distribution of structures which sample the motional modes.")
uf.desc[-1].add_paragraph("The three files are specified via the file root whereby the extensions '.pdb', '.pdb.gz', etc. should not be provided.  This is important for the geometric representation whereby different files are created for the positive and negative representations (due to symmetry in the NMR data, these cannot be differentiated), and for the Monte Carlo simulations.  For example if the file root is 'frame_order', the positive and negative representations will be placed in the 'frame_order_pos.pdb.gz' and 'frame_order_neg.pdb.gz' files and the Monte Carlo simulations in the 'frame_order_sim_pos.pdb.gz' and 'frame_order_sim_neg.pdb.gz' files.  For models where there is no difference in representation between the positive and negative directions, the files 'frame_order.pdb.gz' and 'frame_order_sim.pdb.gz' will be produced.")
uf.desc[-1].add_paragraph("There are four different types of residue within the PDB.  The pivot point is represented as as a single carbon atom of the residue 'PIV'.  The cone consists of numerous H atoms of the residue 'CON'.  The cone axis vector is presented as the residue 'AXE' with one carbon atom positioned at the pivot and the other x Angstroms away on the cone axis (set by the geometric object size).  Finally, if Monte Carlo have been performed, there will be multiple 'MCC' residues representing the cone for each simulation, and multiple 'MCA' residues representing the multiple cone axes.")
uf.desc[-1].add_paragraph("To create the diffusion in a cone PDB representation, a uniform distribution of vectors on a sphere is generated using spherical coordinates with the polar angle defined by the cone axis.  By incrementing the polar angle using an arccos distribution, a radial array of vectors representing latitude are created while incrementing the azimuthal angle evenly creates the longitudinal vectors.  These are all placed into the PDB file as H atoms and are all connected using PDB CONECT records.  Each H atom is connected to its two neighbours on the both the longitude and latitude.  This creates a geometric PDB object with longitudinal and latitudinal lines representing the filled cone.")
uf.backend = pdb_model
uf.menu_text = "pdb_&model"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_height_desc = 400
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'frame_order.png'


# The frame_order.pivot user function.
uf = uf_info.add_uf('frame_order.pivot')
uf.title = "Set the pivot points for the two body motion in the structural coordinate system."
uf.title_short = "Pivot point setting."
uf.add_keyarg(
    name = "pivot",
    py_type = "num_list",
    dim = 3,
    desc_short = "pivot point",
    desc = "The pivot point for the motion (e.g. the position between the 2 domains in PDB coordinates).",
    can_be_none = True
)
uf.add_keyarg(
    name = "order",
    default = 1,
    min = 1,
    max = 100,
    py_type = "int",
    desc_short = "pivot point number",
    desc = "The ordinal number of the pivot point.  The value of 1 is for the first pivot point, the value of 2 for the second pivot point, and so on.",
    wiz_element_type = "spin"
)
uf.add_keyarg(
    name = "fix",
    py_type = "bool",
    default = False,
    desc_short = "fixed flag",
    desc = "A flag specifying if the pivot point should be fixed during optimisation."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will set the pivot points for the two domain system within the PDB coordinate system.  This is required for interpreting PCS data as well as for the generation of cone or other PDB representations of the domain motions.")
uf.desc[-1].add_paragraph("This user function can also be used to change the optimisation status of an already set pivot point.  By simply providing the fixed flag and not the pivot point values, the pivot can be changed to be either fixed during optimisation or that it will be optimised.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set the pivot point, type one of:")
uf.desc[-1].add_prompt("relax> frame_order.pivot([12.067, 14.313, -3.2675])")
uf.desc[-1].add_prompt("relax> frame_order.pivot(pivot=[12.067, 14.313, -3.2675])")
uf.desc[-1].add_paragraph("To change an already set and fixed pivot point so that it can now be optimised, type:")
uf.desc[-1].add_prompt("relax> frame_order.pivot(fix=False)")
uf.backend = pivot
uf.menu_text = "&pivot"
uf.wizard_size = (900, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'frame_order.png'


# The frame_order.num_int_pts user function.
uf = uf_info.add_uf('frame_order.num_int_pts')
uf.title = "Set the number of integration points used in the quasi-random Sobol' sequence during optimisation."
uf.title_short = "Number of integration points."
uf.add_keyarg(
    name = "num",
    default = 200000,
    min = 3,
    max = 10000000,
    py_type = "int",
    desc_short = "number of points",
    desc = "The number of integration points to use in the Sobol' sequence during optimisation.",
    wiz_element_type = "spin"
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the number of integration points used during the Frame Order target function optimisation to be changed from the default.  This is used in the quasi-random Sobol' sequence for the numerical integration.")
uf.backend = num_int_pts
uf.menu_text = "&num_int_pts"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_size = (900, 500)
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
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Prior to optimisation of the '2-domain' Frame Order theories, which of the two domains will act as the frame of reference must be specified.  This is important for the attachment of cones to domains, etc.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set up the isotropic cone frame order model with 'centre' domain being the frame of reference, type:")
uf.desc[-1].add_prompt("relax> frame_order.ref_domain(ref='centre')")
uf.backend = ref_domain
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
        "Free rotor isotropic cone",
        "Torsionless isotropic cone",
        "Isotropic cone",
        "Free rotor pseudo-ellipse",
        "Torsionless pseudo-ellipse",
        "Pseudo-ellipse",
        "Double rotor"
    ],
    wiz_combo_data = [
        "free rotor",
        "rigid",
        "rotor",
        "iso cone, free rotor",
        "iso cone, torsionless",
        "iso cone",
        "pseudo-ellipse, free rotor",
        "pseudo-ellipse, torsionless",
        "pseudo-ellipse",
        "double rotor"
    ],
    wiz_read_only = True,
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Prior to optimisation, the Frame Order model should be selected.  These models consist of three parameter categories:")
uf.desc[-1].add_list_element("The average domain position.  This includes the parameters ave_pos_alpha, ave_pos_beta, and ave_pos_gamma.  These Euler angles rotate the tensors from the arbitrary PDB frame of the moving domain to the average domain position.")
uf.desc[-1].add_list_element("The frame order eigenframe.  This includes the parameters eigen_alpha, eigen_beta, and eigen_gamma.  These Euler angles define the major modes of motion.  The cone central axis is defined as the z-axis.  The pseudo-elliptic cone x and y-axes are defined as the x and y-axes of the eigenframe.")
uf.desc[-1].add_list_element("The cone parameters.  These are defined as the tilt-torsion angles cone_theta_x, cone_theta_y, and cone_sigma_max.  The cone_theta_x and cone_theta_y parameters define the two cone opening angles of the pseudo-ellipse.  The amount of domain torsion is defined as the average domain position, plus and minus cone_sigma_max.  The isotropic cones are defined by setting cone_theta_x = cone_theta_y and converting the single parameter into a 2nd rank order parameter.")
uf.desc[-1].add_paragraph("The list of available models are:")
uf.desc[-1].add_item_list_element("'pseudo-ellipse'", "The pseudo-elliptic cone model.  This is the full model consisting of the parameters ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, and cone_sigma_max.")
uf.desc[-1].add_item_list_element("'pseudo-ellipse, torsionless'", "The pseudo-elliptic cone with the torsion angle cone_sigma_max set to zero.")
uf.desc[-1].add_item_list_element("'pseudo-ellipse, free rotor'", "The pseudo-elliptic cone with no torsion angle restriction.")
uf.desc[-1].add_item_list_element("'iso cone'", "The isotropic cone model.  The cone is defined by a single order parameter s1 which is related to the single cone opening angle cone_theta_x = cone_theta_y.  Due to rotational symmetry about the cone axis, the average position alpha Euler angle ave_pos_alpha is dropped from the model.  The symmetry also collapses the eigenframe to a single z-axis defined by the parameters axis_theta and axis_phi.")
uf.desc[-1].add_item_list_element("'iso cone, torsionless'", "The isotropic cone model with the torsion angle cone_sigma_max set to zero.")
uf.desc[-1].add_item_list_element("'iso cone, free rotor'", "The isotropic cone model with no torsion angle restriction.")
uf.desc[-1].add_item_list_element("'rotor'", "The only motion is a rotation about the cone axis restricted by the torsion angle cone_sigma_max.")
uf.desc[-1].add_item_list_element("'rigid'", "No domain motions.")
uf.desc[-1].add_item_list_element("'free rotor'", "The only motion is free rotation about the cone axis.")
uf.desc[-1].add_item_list_element("'double rotor'", "Restricted motions about two independent rotor axes.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To select the isotropic cone model, type:")
uf.desc[-1].add_prompt("relax> frame_order.select_model(model='iso cone')")
uf.backend = select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 560
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'frame_order.png'
