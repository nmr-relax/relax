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

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from specific_analyses.frame_order.optimisation import count_sobol_points
from specific_analyses.frame_order.uf import sobol_setup, pdb_model, permute_axes, pivot, ref_domain, select_model
from specific_analyses.frame_order.variables import MODEL_DOUBLE_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_RIGID, MODEL_ROTOR
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('frame_order')
uf_class.title = "Class containing the user functions of the Frame Order theories."
uf_class.menu_text = "&frame_order"
uf_class.gui_icon = "relax.frame_order"


# The frame_order.count_sobol_points user function.
uf = uf_info.add_uf('frame_order.count_sobol_points')
uf.title = "Count the number of Sobol' points used for the current parameter values."
uf.title_short = "Used Sobol' point count."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the number of Sobol' integration points used during the Frame Order target function optimisation to be counted.  This uses the current parameter values to determine how many are used for the PCS calculation compared to the total number.")
uf.backend = count_sobol_points
uf.menu_text = "&count_sobol_points"
uf.gui_icon = "oxygen.categories.applications-education"
uf.wizard_size = (800, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'frame_order.png'


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
    name = "model",
    default = 1,
    min = 1,
    py_type = "int",
    desc_short = "structural model",
    desc = "Only one model from an analysed ensemble can be used for the PDB representation of the Monte Carlo simulations of the average domain position, as these consists of one model per simulation, and also for the distribution of structures.",
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
uf.desc[-1].add_paragraph("The PDB representation of the Monte Carlo simulations consists of one model per simulation.  And the distribution of structures consists of one model per motional simulation step.  Therefore if an ensemble of structures has been analysed ,only one model from the ensemble can be used for either representation.  This defaults to model number 1, but this can be changed.")
uf.backend = pdb_model
uf.menu_text = "pdb_&model"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_height_desc = 370
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'frame_order.png'


# The frame_order.permute_axes user function.
uf = uf_info.add_uf('frame_order.permute_axes')
uf.title = "Permute the axes of the motional eigenframe to switch between local minima."
uf.title_short = "Eigenframe axis permutation."
uf.add_keyarg(
    name = "permutation",
    default = "A",
    py_type = "str",
    desc_short = "permutation",
    desc = "Which of the two permutations 'A' or 'B' to create.  Three permutations are possible, and 'A' and 'B' select those which are not the starting combination.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "A",
        "B"
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The pseudo-elliptic frame order models consist of multiple solutions as the optimisation space contains multiple local minima.  Because of the constraint cone_theta_x <= cone_theta_y, there are exactly three local minima (out of 6 possible permutations).  These correspond to permutations of the motional system - the eigenframe x, y and z-axes as well as the cone opening angles cone_theta_x, cone_theta_y, and cone_sigma_max associated with these axes.  But as the mechanics of the cone angles is not identical to that of the torsion angle, only one of the three local minima is the global minimum.")
uf.desc[-1].add_paragraph("When optimising the pseudo-elliptic models, specifically the '%s' and '%s' model, any of the three local minima can be found.  Convergence to the global minimum is not guaranteed.  Therefore this user function can be used to permute the motional system to jump from one local minimum to the other.  Optimisation will be required as the permuted parameters will not be exactly at the minimum." % (MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_TORSIONLESS))
table = uf_tables.add_table(label="table: frame_order.permute_axes combinations", caption="The motional eigenframe permutations for the frame_order.permute_axes user function.", caption_short="The permutations for the frame_order.permute_axes user function.")
table.add_headings(["Permutation ",  "Axis inversion", "If x < y < z", "If x < z < y", "If z < x < y"])
table.add_row([     "[x', y', z']", "      z        ", "    Self    ", "    Self    ", "    Self    "])
table.add_row([     "[x', z', y']", "     -z        ", "     A      ", "     A      ", "     x      "])
table.add_row([     "[y', x', z']", "     -z        ", "     x      ", "     x      ", "     x      "])
table.add_row([     "[y', z', x']", "      z        ", "     B      ", "     x      ", "     x      "])
table.add_row([     "[z', x', y']", "      z        ", "     x      ", "     x      ", "     A      "])
table.add_row([     "[z', y', x']", "     -z        ", "     x      ", "     B      ", "     B      "])
uf.desc[-1].add_table(table.label)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("For combination 'A', simply type:")
uf.desc[-1].add_prompt("relax> frame_order.permute_axes('A')")
uf.backend = permute_axes
uf.menu_text = "per&mute_axes"
uf.wizard_height_desc = 550
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
        "Rigid model",
        "Rotor model",
        "Free rotor model",
        "Torsionless isotropic cone",
        "Isotropic cone",
        "Free rotor isotropic cone",
        "Torsionless pseudo-ellipse",
        "Pseudo-ellipse",
        "Free rotor pseudo-ellipse",
        "Double rotor"
    ],
    wiz_combo_data = [
        MODEL_RIGID,
        MODEL_ROTOR,
        MODEL_FREE_ROTOR,
        MODEL_ISO_CONE_TORSIONLESS,
        MODEL_ISO_CONE,
        MODEL_ISO_CONE_FREE_ROTOR,
        MODEL_PSEUDO_ELLIPSE_TORSIONLESS,
        MODEL_PSEUDO_ELLIPSE,
        MODEL_PSEUDO_ELLIPSE_FREE_ROTOR,
        MODEL_DOUBLE_ROTOR
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
uf.desc[-1].add_item_list_element(repr(MODEL_PSEUDO_ELLIPSE), "The pseudo-elliptic cone model.  This is the full model consisting of the parameters ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, and cone_sigma_max.")
uf.desc[-1].add_item_list_element(repr(MODEL_PSEUDO_ELLIPSE_TORSIONLESS), "The pseudo-elliptic cone with the torsion angle cone_sigma_max set to zero.")
uf.desc[-1].add_item_list_element(repr(MODEL_PSEUDO_ELLIPSE_FREE_ROTOR), "The pseudo-elliptic cone with no torsion angle restriction.")
uf.desc[-1].add_item_list_element(repr(MODEL_ISO_CONE), "The isotropic cone model.  The cone is defined by a single order parameter s1 which is related to the single cone opening angle cone_theta_x = cone_theta_y.  Due to rotational symmetry about the cone axis, the average position alpha Euler angle ave_pos_alpha is dropped from the model.  The symmetry also collapses the eigenframe to a single z-axis defined by the parameters axis_theta and axis_phi.")
uf.desc[-1].add_item_list_element(repr(MODEL_ISO_CONE_TORSIONLESS), "The isotropic cone model with the torsion angle cone_sigma_max set to zero.")
uf.desc[-1].add_item_list_element(repr(MODEL_ISO_CONE_FREE_ROTOR), "The isotropic cone model with no torsion angle restriction.")
uf.desc[-1].add_item_list_element(repr(MODEL_ROTOR), "The only motion is a rotation about the cone axis restricted by the torsion angle cone_sigma_max.")
uf.desc[-1].add_item_list_element(repr(MODEL_RIGID), "No domain motions.")
uf.desc[-1].add_item_list_element(repr(MODEL_FREE_ROTOR), "The only motion is free rotation about the cone axis.")
uf.desc[-1].add_item_list_element(repr(MODEL_DOUBLE_ROTOR), "Restricted motions about two independent rotor axes.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To select the isotropic cone model, type:")
uf.desc[-1].add_prompt("relax> frame_order.select_model(model='%s')" % MODEL_ISO_CONE)
uf.backend = select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 560
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'frame_order.png'


# The frame_order.sobol_setup user function.
uf = uf_info.add_uf('frame_order.sobol_setup')
uf.title = "Set up the quasi-random Sobol' sequence points for numerical PCS integration."
uf.title_short = "Set up the quasi-random Sobol' sequence."
uf.add_keyarg(
    name = "max_num",
    default = 200,
    min = 3,
    max = 10000000,
    py_type = "int",
    desc_short = "maximum number of Sobol' points",
    desc = "The maximum number of integration points to use in the Sobol' sequence during optimisation.  This can be considered as the number of molecular structures in an ensemble used form a uniform distribution of the dynamics.",
    wiz_element_type = "spin"
)
uf.add_keyarg(
    name = "oversample",
    default = 1,
    min = 1,
    max = 100000,
    py_type = "int",
    desc_short = "oversampling factor",
    desc = "The generation of the Sobol' sequence oversamples as N * Ov * 10**M, where N is the maximum number of points, Ov is the oversamling value, and M is the number of dimensions or torsion-tilt angles used in the system.",
    wiz_element_type = "spin"
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the maximum number of integration points N used during the Frame Order target function optimisation to be specified.  This is used in the quasi-random Sobol' sequence for the numerical integration of the PCS.  The symbols used to describe the algorithm are:")
uf.desc[-1].add_list_element("N, the maximum number of Sobol' integration points.")
uf.desc[-1].add_list_element("Ov, the oversampling factor.")
uf.desc[-1].add_list_element("M, the number of dimensions or torsion-tilt angles used in the system.")
uf.desc[-1].add_paragraph("The algorithm used for uniformly sampling the motional space is:")
uf.desc[-1].add_list_element("Generate the Sobol' sequence.  The number of points is oversampled as N * Ov * 10**M.")
uf.desc[-1].add_list_element("Convert all points to the torsion-tilt angle system.")
uf.desc[-1].add_list_element("Skip all Sobol' points with angles greater than the current parameter values.")
uf.desc[-1].add_list_element("Terminate the loop over the Sobol' points for calculating the PCS once the maximum number of points has been reached.")
uf.desc[-1].add_paragraph("The aim of the oversampling is to try to reach the maximum number of points.  However if the system is not very dynamic, the maximum number of points may not be reached.  In this case, simply increase the oversampling factor.")
uf.backend = sobol_setup
uf.menu_text = "&sobol_setup"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'frame_order.png'
