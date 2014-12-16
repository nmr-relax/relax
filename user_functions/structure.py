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
"""The structure user function definitions."""

# Python module imports.
from numpy import eye
from os import sep
import dep_check
if dep_check.wx_module:
    from wx import FD_OPEN, FD_SAVE
else:
    FD_OPEN = -1
    FD_SAVE = -1

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from pipe_control.pipes import pipe_names
import pipe_control.structure.geometric
import pipe_control.structure.main
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container
from user_functions.wildcards import WILDCARD_STRUCT_GAUSSIAN_ALL, WILDCARD_STRUCT_PDB_ALL, WILDCARD_STRUCT_XYZ_ALL


# Text for the multi-structure paragraph.
paragraph_multi_struct = "Support for multiple structures is provided by the data pipes, model numbers and molecule names arguments.  Each data pipe, model and molecule combination will be treated as a separate structure.  As only atomic coordinates with the same residue name and number and atom name will be assembled, structures with slightly different atomic structures can be compared.  If the list of models is not supplied, then all models of all data pipes will be used.  If the optional molecules list is supplied, each molecule in the list will be considered as a separate structure for comparison between each other."
paragraph_atom_id = "The atom ID string, which uses the same notation as the spin ID, can be used to restrict the coordinates compared to a subset of molecules, residues, or atoms.  For example to only use backbone heavy atoms in a protein, set the atom ID to '@N,C,CA,O', assuming those are the names of the atoms in the 3D structural file."
paragraph_displace_id = "The displacement ID string, which is similar to the atom ID, gives finer control over which atoms are translated and rotated by the algorithm.  When not set this allows, for example, to align structures based on a set of backbone heavy atoms and the backbone protons and side-chains are displaced by default.  Or if set to the same as the atom ID, if a single domain is aligned, then just that domain will be displaced."


# The user function class.
uf_class = uf_info.add_class('structure')
uf_class.title = "Class containing the structural related functions."
uf_class.menu_text = "&structure"
uf_class.gui_icon = "relax.structure"


# The structure.add_atom user function.
uf = uf_info.add_uf('structure.add_atom')
uf.title = "Add an atom."
uf.title_short = "Atom creation."
uf.add_keyarg(
    name = "mol_name",
    py_type = "str",
    desc_short = "molecule name",
    desc = "The name of molecule container to create or add the atom to.",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_name",
    py_type = "str",
    desc_short = "atom name",
    desc = "The atom name."
)
uf.add_keyarg(
    name = "res_name",
    py_type = "str",
    desc_short = "residue name",
    desc = "The residue name."
)
uf.add_keyarg(
    name = "res_num",
    py_type = "int",
    min = -10000,
    max = 10000,
    desc_short = "residue number",
    desc = "The residue number."
)
uf.add_keyarg(
    name = "pos",
    py_type = "float_object",
    desc_short = "atomic position",
    desc = "The atomic coordinates.  For specifying different coordinates for each model of the ensemble, a list of lists can be supplied.",
    list_titles = ['X coordinate', 'Y coordinate', 'Z coordinate']
)
uf.add_keyarg(
    name = "element",
    py_type = "str",
    desc_short = "element",
    desc = "The element name.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["N", "C", "H", "O", "P"],
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_num",
    py_type = "int",
    desc_short = "atom number",
    desc = "The optional atom number.",
    can_be_none = True
)
uf.add_keyarg(
    name = "chain_id",
    py_type = "str",
    desc_short = "optional chain ID",
    desc = "The optional chain ID string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "segment_id",
    py_type = "str",
    desc_short = "optional segment ID",
    desc = "The optional segment ID string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "pdb_record",
    py_type = "str",
    desc_short = "optional PDB record name",
    desc = "The optional PDB record name, e.g. 'ATOM' or 'HETATM'.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows atoms to be added to the internal structural object.  To use the same atomic coordinates for all models, the atomic position can be an array of 3 values.  Alternatively different coordinates can be used for each model if the atomic position is a rank-2 array where the first dimension matches the number of models currently present.")
uf.backend = pipe_control.structure.main.add_atom
uf.menu_text = "&add_atom"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.add_model user function.
uf = uf_info.add_uf('structure.add_model')
uf.title = "Add a new model."
uf.title_short = "Model creation."
uf.add_keyarg(
    name = "model_num",
    py_type = "int",
    desc_short = "model number",
    desc = "The number of the new model."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows new models to be added to the internal structural object.  Note that no structural information is allowed to be present")
uf.backend = pipe_control.structure.main.add_model
uf.menu_text = "&add_model"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_size = (700, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.align user function.
uf = uf_info.add_uf('structure.align')
uf.title = "Align and superimpose different structures."
uf.title_short = "Structural alignment and superimposition."
uf.add_keyarg(
    name = "pipes",
    py_type = "str_list",
    desc_short = "data pipes",
    desc = "The data pipes to use in the alignment and superimposition.",
    wiz_combo_iter = pipe_names,
    wiz_read_only = False,
    can_be_none = True
)
uf.add_keyarg(
    name = "models",
    py_type = "int_list_of_lists",
    desc_short = "model list for each data pipe",
    desc = "The list of models for each data pipe to use in the alignment and superimposition.  The number of elements must match the pipes argument.  If no models are given, then all will be used.",
    can_be_none = True
)
uf.add_keyarg(
    name = "molecules",
    py_type = "str_list_of_lists",
    desc_short = "molecule list for each data pipe",
    desc = "The list of molecules for each data pipe to use in the alignment and superimposition.  This allows differently named molecules in the same or different data pipes to be superimposed.  The number of elements must match the pipes argument.  If no molecules are given, then all will be used.",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom ID string",
    desc = "The atom identification string of the coordinates of interest.",
    can_be_none = True
)
uf.add_keyarg(
    name = "displace_id",
    py_type = "str_or_str_list",
    desc_short = "displacement ID string(s)",
    desc = "The atom identification string for restricting the displacement to a subset of all atoms.  If not set, then all atoms will be translated and rotated.  If supplied as a list of IDs, then the number of items must match the number of structures.",
    can_be_none = True
)
uf.add_keyarg(
    name = "method",
    default = "fit to mean",
    py_type = "str",
    desc_short = "superimposition method",
    desc = "The superimposition method.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["fit to mean", "fit to first"],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "centre_type",
    py_type = "str",
    default = "centroid",
    desc_short = "centre type",
    desc = "The type of centre to user for the superimposition, i.e. either the standard centroid superimposition or a superimposition using the centre of mass (CoM).",
    wiz_element_type = "combo",
    wiz_combo_choices = ["The centroid", "The centre of mass (CoM)"],
    wiz_combo_data = ["centroid", "CoM"]
)
uf.add_keyarg(
    name = "centroid",
    py_type = "float_array",
    desc_short = "centroid position",
    desc = "The alternative position of the centroid.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows a set of related structures to be superimposed to each other.  The current algorithm will only use atoms with the same residue name and number and atom name in the superimposition, hence this is not a true sequence alignment.  Just as with the structure.superimpose user function two methods are currently supported:")
uf.desc[-1].add_item_list_element("'fit to mean'", "All models are fit to the mean structure.  This is the default and most accurate method for an ensemble description.  It is an iterative method which first calculates a mean structure and then fits each model to the mean structure using the Kabsch algorithm.  This is repeated until convergence.")
uf.desc[-1].add_item_list_element("'fit to first'", "This is quicker but is not as accurate for an ensemble description.  The Kabsch algorithm is used to rotate and translate each model to be superimposed onto the first model of the first data pipe.")
uf.desc[-1].add_paragraph(paragraph_multi_struct)
uf.desc[-1].add_paragraph(paragraph_atom_id)
uf.desc[-1].add_paragraph(paragraph_displace_id)
uf.desc[-1].add_paragraph("By supplying the position of the centroid, an alternative position than the standard rigid body centre is used as the focal point of the superimposition.  The allows, for example, the superimposition about a pivot point.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To superimpose all sets of models, exactly as in the structure.superimpose user function, type one of:")
uf.desc[-1].add_prompt("relax> structure.align()")
uf.desc[-1].add_prompt("relax> structure.align(method='fit to mean')")
uf.desc[-1].add_paragraph("To superimpose the models 1, 2, 3, 5 onto model 4, type:")
uf.desc[-1].add_prompt("relax> structure.align(models=[4, 1, 2, 3, 5], method='fit to first')")
uf.desc[-1].add_paragraph("To superimpose an ensemble of protein structures using only the backbone heavy atoms, type one of:")
uf.desc[-1].add_prompt("relax> structure.align(atom_id='@N,C,CA,O')")
uf.desc[-1].add_prompt("relax> structure.align(method='fit to mean', atom_id='@N,C,CA,O')")
uf.desc[-1].add_paragraph("To superimpose the structures in the 'A' data pipe onto the structures of the 'B' data pipe using backbone heavy atoms, type one of:")
uf.desc[-1].add_prompt("relax> structure.align(['B', 'A'], None, 'fit to first', '@N,C,CA,O')")
uf.desc[-1].add_prompt("relax> structure.align(pipes=['B', 'A'], method='fit to first', atom_id='@N,C,CA,O')")
uf.backend = pipe_control.structure.main.align
uf.menu_text = "&align"
uf.wizard_apply_button = False
uf.wizard_height_desc = 400
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.com user function.
uf = uf_info.add_uf('structure.com')
uf.title = "Calculate the centre of mass (CoM) for all structures."
uf.title_short = "Centre of mass calculation."
uf.add_keyarg(
    name = "model",
    py_type = "int",
    desc_short = "model",
    desc = "The optional structural model number to restrict the calculation of the centre of mass to.",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom ID string",
    desc = "The atom identification string to restrict the CoM calculation to.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This user function will calculate the centre of mass (CoM) for all loaded structures, printing out the position and storing it in the current data pipe.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To determine the centre of mass of all structure, simply type:")
uf.desc[-1].add_prompt("relax> structure.com()")
uf.backend = pipe_control.structure.main.com
uf.menu_text = "co&m"
uf.wizard_size = (600, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.connect_atom user function.
uf = uf_info.add_uf('structure.connect_atom')
uf.title = "Connect two atoms."
uf.title_short = "Atom connection."
uf.add_keyarg(
    name = "index1",
    py_type = "int",
    max = 10000,
    desc_short = "index 1",
    desc = "The global index of the first atom."
)
uf.add_keyarg(
    name = "index2",
    py_type = "int",
    max = 10000,
    desc_short = "index 2",
    desc = "The global index of the second atom."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows atoms to be connected in the internal structural object.  The global index is normally equal to the PDB atom number minus 1.")
uf.backend = pipe_control.structure.main.connect_atom
uf.menu_text = "co&nnect_atom"
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.create_diff_tensor_pdb user function.
uf = uf_info.add_uf('structure.create_diff_tensor_pdb')
uf.title = "Create a PDB file to represent the diffusion tensor."
uf.title_short = "Diffusion tensor PDB file creation."
uf.add_keyarg(
    name = "scale",
    default = 1.8e-6,
    py_type = "num",
    desc_short = "scaling factor",
    desc = "Value for scaling the diffusion rates."
)
uf.add_keyarg(
    name = "file",
    default = "tensor.pdb",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file.",
    wiz_filesel_wildcard = WILDCARD_STRUCT_PDB_ALL,
    wiz_filesel_style = FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory to place the file into.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which, if set to True, will overwrite the any pre-existing file."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This creates a PDB file containing an artificial geometric structure to represent the diffusion tensor.  A structure must have previously been read into relax.  The diffusion tensor is represented by an ellipsoidal, spheroidal, or spherical geometric object with its origin located at the centre of mass (of the selected residues).  This diffusion tensor PDB file can subsequently read into any molecular viewer.")
uf.desc[-1].add_paragraph("There are four different types of residue within the PDB.  The centre of mass of the selected residues is represented as a single carbon atom of the residue 'COM'.  The ellipsoidal geometric shape consists of numerous H atoms of the residue 'TNS'.  The axes of the tensor, when defined, are presented as the residue 'AXS' and consist of carbon atoms: one at the centre of mass and one at the end of each eigenvector.  Finally, if Monte Carlo simulations were run and the diffusion tensor parameters were allowed to vary then there will be multiple 'SIM' residues, one for each simulation.  These are essentially the same as the 'AXS' residue, representing the axes of the simulated tensors, and they will appear as a distribution.")
uf.desc[-1].add_paragraph("As the Brownian rotational diffusion tensor is a measure of the rate of rotation about different axes - the larger the geometric object, the faster the diffusion of a molecule.  For example the diffusion tensor of a water molecule is much larger than that of a macromolecule.")
uf.desc[-1].add_paragraph("The effective global correlation time experienced by an XH bond vector, not to be confused with the Lipari and Szabo parameter tau_e, will be approximately proportional to the component of the diffusion tensor parallel to it.  The approximation is not exact due to the multiexponential form of the correlation function of Brownian rotational diffusion.  If an XH bond vector is parallel to the longest axis of the tensor, it will be unaffected by rotations about that axis, which are the fastest rotations of the molecule, and therefore its effective global correlation time will be maximal.")
uf.desc[-1].add_paragraph("To set the size of the diffusion tensor within the PDB frame the unit vectors used to generate the geometric object are first multiplied by the diffusion tensor (which has the units of inverse seconds) then by the scaling factor (which has the units of second Angstroms and has the default value of 1.8e-6 s.Angstrom).  Therefore the rotational diffusion rate per Angstrom is equal the inverse of the scale value (which defaults to 5.56e5 s^-1.Angstrom^-1).  Using the default scaling value for spherical diffusion, the correspondence between global correlation time, Diso diffusion rate, and the radius of the sphere for a number of discrete cases will be:")
table = uf_tables.add_table(label="table: diff tensor PDB scaling", caption="Diffusion tensor PDB representation sizes using the default scaling for different diffusion tensors", caption_short="Diffusion tensor PDB scaling.")
table.add_headings(["tm (ns)", "Diso (s^-1)", "Radius (Angstrom)"])
table.add_row(["1", "1.67e8", "300"])
table.add_row(["3", "5.56e7", "100"])
table.add_row(["10", "1.67e7", "30"])
table.add_row(["30", "5.56e6", "10"])
uf.desc[-1].add_table(table.label)
uf.desc[-1].add_paragraph("The scaling value has been fixed to facilitate comparisons within or between publications, but can be changed to vary the size of the tensor geometric object if necessary.  Reporting the rotational diffusion rate per Angstrom within figure legends would be useful.")
uf.desc[-1].add_paragraph("To create the tensor PDB representation, a number of algorithms are utilised.  Firstly the centre of mass is calculated for the selected residues and is represented in the PDB by a C atom.  Then the axes of the diffusion are calculated, as unit vectors scaled to the appropriate length (multiplied by the eigenvalue Dx, Dy, Dz, Dpar, Dper, or Diso as well as the scale value), and a C atom placed at the position of this vector plus the centre of mass.  Finally a uniform distribution of vectors on a sphere is generated using spherical coordinates.  By incrementing the polar angle using an arccos distribution, a radial array of vectors representing latitude are created while incrementing the azimuthal angle evenly creates the longitudinal vectors.  These unit vectors, which are distributed within the PDB frame and are of 1 Angstrom in length, are first rotated into the diffusion frame using a rotation matrix (the spherical diffusion tensor is not rotated).  Then they are multiplied by the diffusion tensor matrix to extend the vector out to the correct length, and finally multiplied by the scale value so that the vectors reasonably superimpose onto the macromolecular structure.  The last set of algorithms place all this information into a PDB file.  The distribution of vectors are represented by H atoms and are all connected using PDB CONECT records.  Each H atom is connected to its two neighbours on the both the longitude and latitude.  This creates a geometric PDB object with longitudinal and latitudinal lines.")
uf.backend = pipe_control.structure.main.create_diff_tensor_pdb
uf.menu_text = "&create_diff_tensor_pdb"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 450
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + 'create_diff_tensor_pdb.png'


# The structure.create_rotor_pdb user function.
uf = uf_info.add_uf('structure.create_rotor_pdb')
uf.title = "Create a PDB file representation of a rotor."
uf.title_short = "Rotor PDB representation."
uf.add_keyarg(
    name = "file",
    default = "rotor.pdb",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file.",
    wiz_filesel_wildcard = WILDCARD_STRUCT_PDB_ALL,
    wiz_filesel_style = FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory to place the file into.",
    can_be_none = True
)
uf.add_keyarg(
    name = "rotor_angle",
    default = 0.0,
    py_type = "float",
    desc_short = "rotor angle",
    desc = "The angle of the rotor motion in degrees."
)
uf.add_keyarg(
    name = "axis",
    py_type = "float_array",
    dim = 3,
    desc_short = "rotor axis vector",
    desc = "The vector defining the rotor axis."
)
uf.add_keyarg(
    name = "axis_pt",
    py_type = "float_array",
    dim = 3,
    desc_short = "rotor axis point",
    desc = "A point lying anywhere on the rotor axis.  This is used to define the position of the axis in 3D space."
)
uf.add_keyarg(
    name = "centre",
    py_type = "float_array",
    dim = 3,
    desc_short = "central point",
    desc = "The central point of the representation.  If this point is not on the rotor axis, then the closest point on the axis will be used for the centre."
)
uf.add_keyarg(
    name = "span",
    default = 2e-9,
    py_type = "num",
    desc_short = "representation span",
    desc = "The distance from the central point to the rotor blades (meters)."
)
uf.add_keyarg(
    name = "blade_length",
    default = 5e-10,
    py_type = "num",
    desc_short = "blade length",
    desc = "The length of the representative rotor blades."
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will overwrite the file if it already exists."
)
uf.add_keyarg(
    name = "staggered",
    default = False,
    py_type = "bool",
    desc_short = "staggered flag",
    desc = "A flag which if True will cause the rotor blades to be staggered.  This is used to avoid blade overlap."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This creates a PDB file representation of a rotor motional model.  The model axis is defined by a vector and a single point on the axis.  The centre of the representation will be taken as the point on the rotor axis closest to the given centre position.  The size of the representation is defined by the span, which is the distance from the central point to the rotors, and the length of the blades.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following is a synthetic example:")
uf.desc[-1].add_prompt("relax> structure.create_rotor_pdb(file='rotor.pdb', rotor_angle=20.0, axis=[0., 0., 1.], axis_pt=[1., 1., 0.], centre=[0., 0., 2.], span=2e-9, blade_length=1e-9)")
uf.backend = pipe_control.structure.geometric.create_rotor_pdb
uf.menu_text = "create_&rotor_pdb"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 700)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.create_vector_dist user function.
uf = uf_info.add_uf('structure.create_vector_dist')
uf.title = "Create a PDB file representation of the distribution of XH bond vectors."
uf.title_short = "XH vector distribution PDB representation."
uf.add_keyarg(
    name = "length",
    default = 2e-9,
    py_type = "num",
    desc_short = "vector length",
    desc = "The length of the vectors in the PDB representation (meters)."
)
uf.add_keyarg(
    name = "file",
    default = "XH_dist.pdb",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file.",
    wiz_filesel_wildcard = WILDCARD_STRUCT_PDB_ALL,
    wiz_filesel_style = FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory to place the file into.",
    can_be_none = True
)
uf.add_keyarg(
    name = "symmetry",
    default = True,
    py_type = "bool",
    desc_short = "symmetry flag",
    desc = "A flag which if True will create a second chain with reversed XH bond orientations."
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will overwrite the file if it already exists."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This creates a PDB file containing an artificial vectors, the length of which default to 20 Angstrom.  A structure must have previously been read into relax.  The origin of the vector distribution is located at the centre of mass (of the selected residues).  This vector distribution PDB file can subsequently be read into any molecular viewer.")
uf.desc[-1].add_paragraph("Because of the symmetry of the diffusion tensor reversing the orientation of the XH bond vector has no effect.  Therefore by setting the symmetry flag two chains 'A' and 'B' will be added to the PDB file whereby chain 'B' is chain 'A' with the XH bonds reversed.")
uf.backend = pipe_control.structure.geometric.create_vector_dist
uf.menu_text = "cr&eate_vector_dist"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 700)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + 'create_vector_dist.png'


# The structure.get_pos user function.
uf = uf_info.add_uf('structure.get_pos')
uf.title = "Extract the atomic positions from the loaded structures for the given spins."
uf.title_short = "Atomic position extraction."
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identification string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "ave_pos",
    default = True,
    py_type = "bool",
    desc_short = "average position flag",
    desc = "A flag specifying if the position of the atom is to be averaged across models."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the atomic positions of the spins to be extracted from the loaded structures.  This is automatically performed by the structure.load_spins user function, but if the sequence information is generated in other ways, this user function allows the structural information to be obtained.")
uf.desc[-1].add_paragraph("If averaging the atomic positions, then average position of all models will be loaded into the spin container.  Otherwise the positions from all models will be loaded separately.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("For a model-free backbone amide nitrogen analysis whereby the N spins have already been created, to obtain the backbone N positions from the file '1F3Y.pdb' (which is a single protein), type the following two user functions:")
uf.desc[-1].add_prompt("relax> structure.read_pdb('1F3Y.pdb')")
uf.desc[-1].add_prompt("relax> structure.get_pos(spin_id='@N')")
uf.backend = pipe_control.structure.main.get_pos
uf.menu_text = "&get_pos"
uf.wizard_height_desc = 300
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.delete user function.
uf = uf_info.add_uf('structure.delete')
uf.title = "Delete structural information."
uf.title_short = "Structure deletion."
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom ID string",
    desc = "The atom identification string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "model",
    py_type = "int",
    desc_short = "structural model",
    desc = "Individual structural models from a loaded ensemble can be deleted by specifying the model number.",
    can_be_none = True
)
uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "verbosity level",
    desc = "The amount of information to print out.  Set to zero to silence the user function, or one to see all messages."
)
uf.add_keyarg(
    name = "spin_info",
    default = True,
    py_type = "bool",
    desc_short = "spin information flag",
    desc = "A flag which if True will cause all structural information in the spin containers and interatomic data containers to be deleted as well.  If False, then only the 3D structural data will be deleted."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will delete structural information from the current data pipe.  All spin and sequence information loaded from these structures will be preserved - this only affects the structural data.  The atom ID argument can be used to restrict deletion to parts of the loaded molecules, or the model argument can be used to delete individual structural models from an ensemble.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To delete everything, simply type:")
uf.desc[-1].add_prompt("relax> structure.delete()")
uf.desc[-1].add_paragraph("To delete residues 50 to 100 of the molecule called 'Ap4Aase', type one of:")
uf.desc[-1].add_prompt("relax> structure.delete(':50-100')")
uf.desc[-1].add_prompt("relax> structure.delete(atom_id=':50-100')")
uf.backend = pipe_control.structure.main.delete
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_size = (800, 550)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.displacement user function.
uf = uf_info.add_uf('structure.displacement')
uf.title = "Determine the rotational and translational displacement between a set of models or molecules."
uf.title_short = "Rotational and translational displacement."
uf.add_keyarg(
    name = "pipes",
    py_type = "str_list",
    desc_short = "data pipes",
    desc = "The data pipes to determine the displacements for.",
    wiz_combo_iter = pipe_names,
    wiz_read_only = False,
    can_be_none = True
)
uf.add_keyarg(
    name = "models",
    py_type = "int_list_of_lists",
    desc_short = "model list for each data pipe",
    desc = "The list of models for each data pipe to determine the displacements for.  The number of elements must match the pipes argument.  If no models are given, then all will be used.",
    can_be_none = True
)
uf.add_keyarg(
    name = "molecules",
    py_type = "str_list_of_lists",
    desc_short = "molecule list for each data pipe",
    desc = "The list of molecules for each data pipe to determine the displacements for.  This allows differently named molecules in the same or different data pipes to be superimposed.  The number of elements must match the pipes argument.  If no molecules are given, then all will be used.",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom identification string",
    desc = "The atom identification string of the coordinates of interest.",
    can_be_none = True
)
uf.add_keyarg(
    name = "centroid",
    py_type = "float_array",
    desc_short = "centroid position",
    desc = "The alternative position of the centroid.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This user function allows the rotational and translational displacement between different models or molecules to be calculated.  The information will be printed out in various formats and held in the relax data store.  This is directional, so there is a starting and ending position for each displacement.  Therefore the displacements in all directions between all models and molecules will be calculated.")
uf.desc[-1].add_paragraph(paragraph_multi_struct)
uf.desc[-1].add_paragraph(paragraph_atom_id)
uf.desc[-1].add_paragraph("By supplying the position of the centroid, an alternative position than the standard rigid body centre is used as the focal point of the motion.  The allows, for example, a pivot of a rotational domain motion to be specified.  This is not a formally correct algorithm, all translations will be zero, but does give an indication to the amplitude of the pivoting angle.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To determine the rotational and translational displacements between all sets of models, type:")
uf.desc[-1].add_prompt("relax> structure.displacement()")
uf.backend = pipe_control.structure.main.displacement
uf.menu_text = "displace&ment"
uf.wizard_height_desc = 450
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.find_pivot user function.
uf = uf_info.add_uf('structure.find_pivot')
uf.title = "Find the pivot point of the motion of a set of structures."
uf.title_short = "Pivot search."
uf.add_keyarg(
    name = "pipes",
    py_type = "str_list",
    desc_short = "data pipes",
    desc = "The data pipes to use in the motional pivot algorithm.",
    wiz_combo_iter = pipe_names,
    wiz_read_only = False,
    can_be_none = True
)
uf.add_keyarg(
    name = "models",
    py_type = "int_list_of_lists",
    desc_short = "model list for each data pipe",
    desc = "The list of models for each data pipe to use in the motional pivot algorithm.  The number of elements must match the pipes argument.  If no models are given, then all will be used.",
    can_be_none = True
)
uf.add_keyarg(
    name = "molecules",
    py_type = "str_list_of_lists",
    desc_short = "molecule list for each data pipe",
    desc = "The list of molecules for each data pipe to use in the motional pivot algorithm.  This allows differently named molecules in the same or different data pipes to be used.  The number of elements must match the pipes argument.  If no molecules are given, then all will be used.",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom ID string",
    desc = "The atom identification string of the coordinates of interest.",
    can_be_none = True
)
uf.add_keyarg(
    name = "init_pos",
    py_type = "float_array",
    desc_short = "initial pivot position",
    desc = "The initial position of the pivot.",
    can_be_none = True
)
uf.add_keyarg(
    name = "func_tol",
    default = 1e-5,
    py_type = "num",
    desc_short = "function tolerance",
    desc = "The function tolerance.  This is used to terminate minimisation once the function value between iterations is less than the tolerance.  The default value is 1e-5."
)
uf.add_keyarg(
    name = "box_limit",
    default = 200,
    py_type = "int",
    desc_short = "box constraint limit",
    desc = "The pivot point is constrained withing a box of +/- x Angstrom the using the logarithmic barrier function together with simplex optimisation.  This argument is the value of x."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is used to find pivot point of motion between a set of structural models.  If the list of models is not supplied, then all models will be used.")
uf.desc[-1].add_paragraph(paragraph_multi_struct)
uf.desc[-1].add_paragraph(paragraph_atom_id)
uf.desc[-1].add_paragraph("By supplying the position of the centroid, an alternative position than the standard rigid body centre is used as the focal point of the superimposition.  The allows, for example, the superimposition about a pivot point.")
uf.backend = pipe_control.structure.main.find_pivot
uf.menu_text = "&find_pivot"
uf.wizard_height_desc = 450
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.load_spins user function.
uf = uf_info.add_uf('structure.load_spins')
uf.title = "Load spins from the structure into the relax data store."
uf.title_short = "Loading spins from structure."
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "spin ID string",
    desc = "The spin identification string for the selective loading of certain spins into the relax data store.",
    wiz_combo_choices = ["@N", "@C", "@H", "@O", "@P", "@NE1", "@HE1", ":A@C2", ":A@C8", ":G@N1", ":G@C8", ":C@C5", ":C@C5", ":U@N3", ":U@C5", ":U@C6"],
    can_be_none = True
)
uf.add_keyarg(
    name = "from_mols",
    py_type = "str_list",
    desc_short = "molecules to load spins from",
    desc = "The list of similar, but not necessarily identical molecules to load spin information from.",
    wiz_read_only = False,
    can_be_none = True
)
uf.add_keyarg(
    name = "mol_name_target",
    py_type = "str",
    desc_short = "target molecule name",
    desc = "The name of target molecule container, overriding the name of the loaded structures.",
    can_be_none = True
)
uf.add_keyarg(
    name = "ave_pos",
    default = True,
    py_type = "bool",
    desc_short = "average position flag",
    desc = "A flag specifying if the position of the atom is to be averaged across models."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows a sequence to be generated within the relax data store using the atomic information from the structure already associated with this data pipe.  The spin ID string is used to select which molecules, which residues, and which atoms will be recognised as spin systems within relax.  If the spin ID is left unspecified, then all molecules, residues, and atoms will be placed within the data store (and all atoms will be treated as spins).")
uf.desc[-1].add_paragraph("As an alternative to using structural models, by specifying the list of molecules to load spins from similar though not necessarily identical molecules will be combined.  In this case, the target molecule name must be supplied to create a single combined molecule.  And only a single model can be loaded in the current data pipe.  The spin numbering will be dropped to allow for sequential atom numbering in the PDB and other formats.  Therefore only the residue number and name and atom name will be preserved for creating the spin containers.  If the spin is only present in a subset of the structures, then the positional information will only be taken from that subset and hence the number of positions might be different for different spins.")
uf.desc[-1].add_paragraph("If averaging the atomic positions, then average position of all models or molecules will be loaded into the spin container.  Otherwise the positions from all models or molecules will be loaded separately.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("For a model-free backbone amide nitrogen analysis, to load just the backbone N sequence from the file '1F3Y.pdb' (which is a single protein), type the following two user functions:")
uf.desc[-1].add_prompt("relax> structure.read_pdb('1F3Y.pdb')")
uf.desc[-1].add_prompt("relax> structure.load_spins(spin_id='@N')")
uf.desc[-1].add_paragraph("For an RNA analysis of adenine C8 and C2, guanine C8 and N1, cytidine C5 and C6, and uracil N3, C5, and C6, type the following series of commands (assuming that the PDB file with this atom naming has already been read):")
uf.desc[-1].add_prompt("relax> structure.load_spins(spin_id=\":A@C8\")")
uf.desc[-1].add_prompt("relax> structure.load_spins(spin_id=\":A@C2\")")
uf.desc[-1].add_prompt("relax> structure.load_spins(spin_id=\":G@C8\")")
uf.desc[-1].add_prompt("relax> structure.load_spins(spin_id=\":G@N1\")")
uf.desc[-1].add_prompt("relax> structure.load_spins(spin_id=\":C@C5\")")
uf.desc[-1].add_prompt("relax> structure.load_spins(spin_id=\":C@C6\")")
uf.desc[-1].add_prompt("relax> structure.load_spins(spin_id=\":U@N3\")")
uf.desc[-1].add_prompt("relax> structure.load_spins(spin_id=\":U@C5\")")
uf.desc[-1].add_prompt("relax> structure.load_spins(spin_id=\":U@C6\")")
uf.desc[-1].add_paragraph("Alternatively using some Python programming:")
uf.desc[-1].add_prompt("relax> for id in [\":A@C8\", \":A@C2\", \":G@C8\", \":G@N1\", \":C@C5\", \":C@C6\", \":U@N3\", \":U@C5\", \":U@C6\"]:")
uf.desc[-1].add_prompt("relax>     structure.load_spins(spin_id=id)")
uf.backend = pipe_control.structure.main.load_spins
uf.menu_text = "&load_spins"
uf.gui_icon = "relax.spin"
uf.wizard_height_desc = 500
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + 'load_spins.png'


# The structure.mean user function.
uf = uf_info.add_uf('structure.mean')
uf.title = "Calculate the mean structure from all loaded models."
uf.title_short = "Mean structure."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will calculate the mean structure from all loaded models.  The mean structure will replace all the models in the internal structural object.  This is provided as a structural aid, specifically for superimposition purposes.")
uf.backend = pipe_control.structure.main.mean
uf.menu_text = "&mean"
uf.gui_icon = "oxygen.categories.applications-education"
uf.wizard_size = (700, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.read_gaussian user function.
uf = uf_info.add_uf('structure.read_gaussian')
uf.title = "Reading structures from Gaussian log files."
uf.title_short = "Gaussian log structure reading."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the Gaussian log file.",
    wiz_filesel_wildcard = WILDCARD_STRUCT_GAUSSIAN_ALL,
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
    name = "set_mol_name",
    py_type = "str_or_str_list",
    desc_short = "setting of molecule names",
    desc = "Set the names of the read molecules.  If unset, then the molecules will be automatically labelled based on the file name or other information.  This can either be a single name or a list of names.",
    can_be_none = True
)
uf.add_keyarg(
    name = "set_model_num",
    py_type = "int_or_int_list",
    desc_short = "setting of model numbers",
    desc = "Set the model numbers of the loaded molecules.  This can be a single number or list of numbers.",
    can_be_none = True
)
uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "verbosity level",
    desc = "The amount of information to print out.  Set to zero to silence the user function, or one to see all messages."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The atomic positions from a Gaussian log file can be read into relax.  If optimisation has been preformed, the last set of atomic coordinates from the log will be read to obtain the final structure.  The log file can be Gzip or Bzip2 compressed.")
uf.desc[-1].add_paragraph("The setting of molecule names is used to name the molecules within the Gaussian file.  If not set, then the molecules will be named after the file name, with the molecule number appended if more than one exists.  By setting the molecule name or setting the model number, the loaded structure can be stored as a specific model or as a different molecule.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To load all structures from the Gaussian file 'taxol.log' in the directory '~/logs', including all models and all molecules, type one of:")
uf.desc[-1].add_prompt("relax> structure.read_gaussian('taxol.log', '~/logs')")
uf.desc[-1].add_prompt("relax> structure.read_gaussian(file='taxol.log', dir=logs')")
uf.backend = pipe_control.structure.main.read_gaussian
uf.menu_text = "read_&gaussian"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + 'read_xyz.png'


# The structure.read_pdb user function.
uf = uf_info.add_uf('structure.read_pdb')
uf.title = "Reading structures from PDB files."
uf.title_short = "PDB reading."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file.",
    wiz_filesel_wildcard = WILDCARD_STRUCT_PDB_ALL,
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
    name = "read_mol",
    py_type = "int_or_int_list",
    desc_short = "molecule number to read",
    desc = "If set, only the given molecule(s) will be read.  The molecules are numbered consecutively from 1.  If unset, then all molecules will be loaded.  By providing a list of numbers such as [1, 2], multiple molecules will be read.",
    can_be_none = True
)
uf.add_keyarg(
    name = "set_mol_name",
    py_type = "str_or_str_list",
    desc_short = "setting of molecule names",
    desc = "Set the names of the read molecules.  If unset, then the molecules will be automatically labelled based on the file name or other information.  This can either be a single name or a list of names.",
    can_be_none = True
)
uf.add_keyarg(
    name = "read_model",
    py_type = "int_or_int_list",
    desc_short = "model to read",
    desc = "If set, only the given model number(s) from the PDB file will be read.  Otherwise all models will be read.  This can be a single number or list of numbers.",
    can_be_none = True
)
uf.add_keyarg(
    name = "set_model_num",
    py_type = "int_or_int_list",
    desc_short = "setting of model numbers",
    desc = "Set the model numbers of the loaded molecules.  If unset, then the PDB model numbers will be preserved if they exist.  This can be a single number or list of numbers.",
    can_be_none = True
)
uf.add_keyarg(
    name = "alt_loc",
    py_type = "str",
    desc_short = "alternate location indicator",
    desc = "The PDB ATOM record 'Alternate location indicator' field value.",
    can_be_none = True
)
uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "verbosity level",
    desc = "The amount of information to print out.  Set to zero to silence the user function, or one to see all messages."
)
uf.add_keyarg(
    name = "merge",
    default = False,
    py_type = "bool",
    desc_short = "merge structure flag",
    desc = "A flag which if set to True will try to merge the PDB structure into the currently loaded structures."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The reading of PDB files into relax is quite a flexible procedure allowing for both models, defined as an ensemble of the same molecule but with different atomic positions, and different molecules within the same model.  One of more molecules can exist in one or more models.  The flexibility allows PDB models to be converted into different molecules and different PDB files loaded as the same molecule but as different models.")
uf.desc[-1].add_paragraph("In a PDB file, the models are specified by the MODEL PDB record.  All the supported PDB readers in relax recognise this.  The internal reader defines molecules using the TER PDB record.  In both cases, the molecules will be numbered consecutively from 1.")
uf.desc[-1].add_paragraph("Setting the molecule name allows the molecule within the PDB (within one model) to have a custom name.  If not set, then the molecules will be named after the file name, with the molecule number appended if more than one exists.")
uf.desc[-1].add_paragraph("Note that relax will complain if it cannot work out what to do.")
uf.desc[-1].add_paragraph("This is able to handle uncompressed, bzip2 compressed files, or gzip compressed files automatically.  The full file name including extension can be supplied, however, if the file cannot be found, this function will search for the file name with '.bz2' appended followed by the file name with '.gz' appended.")
uf.desc[-1].add_paragraph("If a PDB file contains alternative atomic locations, then the alternate location indicator must be specified to allow one of the multiple coordinate sets to be select.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To load all structures from the PDB file 'test.pdb' in the directory '~/pdb', including all models and all molecules, type one of:")
uf.desc[-1].add_prompt("relax> structure.read_pdb('test.pdb', '~/pdb')")
uf.desc[-1].add_prompt("relax> structure.read_pdb(file='test.pdb', dir='pdb')")
uf.desc[-1].add_paragraph("To load the 10th model from the file 'test.pdb' and naming it 'CaM', use one of:")
uf.desc[-1].add_prompt("relax> structure.read_pdb('test.pdb', read_model=10, set_mol_name='CaM')")
uf.desc[-1].add_prompt("relax> structure.read_pdb(file='test.pdb', read_model=10, set_mol_name='CaM')")
uf.desc[-1].add_paragraph("To load models 1 and 5 from the file 'test.pdb' as two different structures of the same model, type one of:")
uf.desc[-1].add_prompt("relax> structure.read_pdb('test.pdb', read_model=[1, 5], set_model_num=[1, 1])")
uf.desc[-1].add_prompt("relax> structure.read_pdb('test.pdb', set_mol_name=['CaM_1', 'CaM_2'], read_model=[1, 5], set_model_num=[1, 1])")
uf.desc[-1].add_paragraph("To load the files 'lactose_MCMM4_S1_1.pdb', 'lactose_MCMM4_S1_2.pdb', 'lactose_MCMM4_S1_3.pdb' and 'lactose_MCMM4_S1_4.pdb' as models, type the following sequence of commands:")
uf.desc[-1].add_prompt("relax> structure.read_pdb('lactose_MCMM4_S1_1.pdb', set_mol_name='lactose_MCMM4_S1', set_model_num=1)")
uf.desc[-1].add_prompt("relax> structure.read_pdb('lactose_MCMM4_S1_2.pdb', set_mol_name='lactose_MCMM4_S1', set_model_num=2)")
uf.desc[-1].add_prompt("relax> structure.read_pdb('lactose_MCMM4_S1_3.pdb', set_mol_name='lactose_MCMM4_S1', set_model_num=3)")
uf.desc[-1].add_prompt("relax> structure.read_pdb('lactose_MCMM4_S1_4.pdb', set_mol_name='lactose_MCMM4_S1', set_model_num=4)")
uf.backend = pipe_control.structure.main.read_pdb
uf.menu_text = "read_&pdb"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 360
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + 'read_pdb.png'


# The structure.read_xyz user function.
uf = uf_info.add_uf('structure.read_xyz')
uf.title = "Reading structures from XYZ files."
uf.title_short = "XYZ reading."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the XYZ file.",
    wiz_filesel_wildcard = WILDCARD_STRUCT_XYZ_ALL,
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
    name = "read_mol",
    py_type = "int_or_int_list",
    desc_short = "molecule number to read",
    desc = "If set, only the given molecule(s) will be read.  The molecules are numbered consecutively from 1.  If unset, then all molecules will be loaded.  By providing a list of numbers such as [1, 2], multiple molecules will be read.",
    can_be_none = True
)
uf.add_keyarg(
    name = "set_mol_name",
    py_type = "str_or_str_list",
    desc_short = "setting of molecule names",
    desc = "Set the names of the read molecules.  If unset, then the molecules will be automatically labelled based on the file name or other information.  This can either be a single name or a list of names.",
    can_be_none = True
)
uf.add_keyarg(
    name = "read_model",
    py_type = "int_or_int_list",
    desc_short = "model to read",
    desc = "If set, only the given model number(s) from the PDB file will be read.  Otherwise all models will be read.  This can be a single number or list of numbers.",
    can_be_none = True
)
uf.add_keyarg(
    name = "set_model_num",
    py_type = "int_or_int_list",
    desc_short = "setting of model numbers",
    desc = "Set the model numbers of the loaded molecules.  If unset, then the PDB model numbers will be preserved if they exist.  This can be a single number or list of numbers.",
    can_be_none = True
)
uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "verbosity level",
    desc = "The amount of information to print out.  Set to zero to silence the user function, or one to see all messages."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The XYZ files with different models, which defined as an ensemble of the same molecule but with different atomic positions, can be read into relax.  If there are several molecules in one xyz file, please separate them into different files and then load them individually.  Loading different models and different molecules is controlled by specifying the molecule number read, setting the molecule names, specifying which model to read, and setting the model numbers.")
uf.desc[-1].add_paragraph("The setting of molecule names is used to name the molecules within the XYZ (within one model).  If not set, then the molecules will be named after the file name, with the molecule number appended if more than one exists.")
uf.desc[-1].add_paragraph("Note that relax will complain if it cannot work out what to do.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To load all structures from the XYZ file 'test.xyz' in the directory '~/xyz', including all models and all molecules, type one of:")
uf.desc[-1].add_prompt("relax> structure.read_xyz('test.xyz', '~/xyz')")
uf.desc[-1].add_prompt("relax> structure.read_xyz(file='test.xyz', dir='xyz')")
uf.desc[-1].add_paragraph("To load the 10th model from the file 'test.xyz' and naming it 'CaM', use one of:")
uf.desc[-1].add_prompt("relax> structure.read_xyz('test.xyz', read_model=10, set_mol_name='CaM')")
uf.desc[-1].add_prompt("relax> structure.read_xyz(file='test.xyz', read_model=10, set_mol_name='CaM')")
uf.desc[-1].add_paragraph("To load models 1 and 5 from the file 'test.xyz' as two different structures of the same model, type one of:")
uf.desc[-1].add_prompt("relax> structure.read_xyz('test.xyz', read_model=[1, 5], set_model_num=[1, 1])")
uf.desc[-1].add_prompt("relax> structure.read_xyz('test.xyz', set_mol_name=['CaM_1', 'CaM_2'], read_model=[1, 5], set_model_num=[1, 1])")
uf.desc[-1].add_paragraph("To load the files 'test_1.xyz', 'test_2.xyz', 'test_3.xyz' and 'test_4.xyz' as models, type the  following sequence of commands:")
uf.desc[-1].add_prompt("relax> structure.read_xyz('test_1.xyz', set_mol_name='test_1', set_model_num=1)")
uf.desc[-1].add_prompt("relax> structure.read_xyz('test_2.xyz', set_mol_name='test_2', set_model_num=2)")
uf.desc[-1].add_prompt("relax> structure.read_xyz('test_3.xyz', set_mol_name='test_3', set_model_num=3)")
uf.desc[-1].add_prompt("relax> structure.read_xyz('test_4.xyz', set_mol_name='test_4', set_model_num=4)")
uf.backend = pipe_control.structure.main.read_xyz
uf.menu_text = "read_&xyz"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + 'read_xyz.png'


# The structure.rmsd user function.
uf = uf_info.add_uf('structure.rmsd')
uf.title = "Determine the RMSD between structures."
uf.title_short = "Structural RMSD."
uf.add_keyarg(
    name = "pipes",
    py_type = "str_list",
    desc_short = "data pipes",
    desc = "The data pipes to determine the RMSD for.",
    wiz_combo_iter = pipe_names,
    wiz_read_only = False,
    can_be_none = True
)
uf.add_keyarg(
    name = "models",
    py_type = "int_list_of_lists",
    desc_short = "model list for each data pipe",
    desc = "The list of models for each data pipe to determine the RMSD for.  The number of elements must match the pipes argument.  If no models are given, then all will be used.",
    can_be_none = True
)
uf.add_keyarg(
    name = "molecules",
    py_type = "str_list_of_lists",
    desc_short = "molecule list for each data pipe",
    desc = "The list of molecules for each data pipe to determine the RMSD for.  The RMSD will only be calculated for atoms with identical residue name and number and atom name.  The number of elements must match the pipes argument.  If no molecules are given, then all will be used.",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom identification string",
    desc = "The atom identification string of the coordinates of interest.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the root mean squared deviation (RMSD) between all structures to be calculated.  The RMSDs for individual structures to the mean structure will be calculated and reported, and then these values averaged for the global RMSD.  This will be stored in the structural object of the current data pipe.")
uf.desc[-1].add_paragraph(paragraph_multi_struct)
uf.desc[-1].add_paragraph(paragraph_atom_id)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To determine the RMSD of all models in the current data pipe, simply type:")
uf.desc[-1].add_prompt("relax> structure.rmsd()")
uf.backend = pipe_control.structure.main.rmsd
uf.menu_text = "&rmsd"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.rotate user function.
uf = uf_info.add_uf('structure.rotate')
uf.title = "Rotate the internal structural object about the given origin by the rotation matrix."
uf.title_short = "Structure rotation."
uf.add_keyarg(
    name = "R",
    py_type = "float_matrix",
    default = eye(3),
    dim = (3, 3),
    desc_short = "rotation matrix",
    desc = "The rotation matrix in forwards rotation notation."
)
uf.add_keyarg(
    name = "origin",
    py_type = "float_array",
    dim = 3,
    desc_short = "origin of rotation",
    desc = "The origin or pivot of the rotation.",
    can_be_none = True
)
uf.add_keyarg(
    name = "model",
    py_type = "int",
    desc_short = "model",
    desc = "The model to rotate (which if not set will cause all models to be rotated).",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom ID string",
    desc = "The atom identification string.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is used to rotate the internal structural data by the given rotation matrix.  If the origin is supplied, then this will act as the pivot of the rotation.  Otherwise, all structural data will be rotated about the point [0, 0, 0].  The rotation can be restricted to one specific model.")
uf.backend = pipe_control.structure.main.rotate
uf.menu_text = "&rotate"
uf.wizard_height_desc = 300
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.superimpose user function.
uf = uf_info.add_uf('structure.superimpose')
uf.title = "Superimpose a set of models of the same structure."
uf.title_short = "Structural superimposition."
uf.add_keyarg(
    name = "models",
    py_type = "int_list",
    desc_short = "model list",
    desc = "The list of models to superimpose.",
    can_be_none = True
)
uf.add_keyarg(
    name = "method",
    default = "fit to mean",
    py_type = "str",
    desc_short = "superimposition method",
    desc = "The superimposition method.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["fit to mean", "fit to first"],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom ID string",
    desc = "The atom identification string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "displace_id",
    py_type = "str",
    desc_short = "displacement ID string",
    desc = "The atom identification string for restricting the displacement to a subset of all atoms.  If not set, then all atoms will be translated and rotated.",
    can_be_none = True
)
uf.add_keyarg(
    name = "centre_type",
    py_type = "str",
    default = "centroid",
    desc_short = "centre type",
    desc = "The type of centre to user for the superimposition, i.e. either the standard centroid superimposition or a superimposition using the centre of mass (CoM).",
    wiz_element_type = "combo",
    wiz_combo_choices = ["The centroid", "The centre of mass (CoM)"],
    wiz_combo_data = ["centroid", "CoM"]
)
uf.add_keyarg(
    name = "centroid",
    py_type = "float_array",
    desc_short = "centroid position",
    desc = "The alternative position of the centroid.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows a set of models of the same structure to be superimposed to each other.  Two superimposition methods are currently supported:")
uf.desc[-1].add_item_list_element("'fit to mean'", "All models are fit to the mean structure.  This is the default and most accurate method for an ensemble description.  It is an iterative method which first calculates a mean structure and then fits each model to the mean structure using the Kabsch algorithm.  This is repeated until convergence.")
uf.desc[-1].add_item_list_element("'fit to first'", "This is quicker but is not as accurate for an ensemble description.  The Kabsch algorithm is used to rotate and translate each model to be superimposed onto the first model.")
uf.desc[-1].add_paragraph("If the list of models is not supplied, then all models will be superimposed.")
uf.desc[-1].add_paragraph(paragraph_atom_id)
uf.desc[-1].add_paragraph(paragraph_displace_id)
uf.desc[-1].add_paragraph("By supplying the position of the centroid, an alternative position than the standard rigid body centre is used as the focal point of the superimposition.  The allows, for example, the superimposition about a pivot point.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To superimpose all sets of models, type one of:")
uf.desc[-1].add_prompt("relax> structure.superimpose()")
uf.desc[-1].add_prompt("relax> structure.superimpose(method='fit to mean')")
uf.desc[-1].add_paragraph("To superimpose the models 1, 2, 3, 5 onto model 4, type:")
uf.desc[-1].add_prompt("relax> structure.superimpose(models=[4, 1, 2, 3, 5], method='fit to first')")
uf.desc[-1].add_paragraph("To superimpose an ensemble of protein structures using only the backbone heavy atoms, type one of:")
uf.desc[-1].add_prompt("relax> structure.superimpose(atom_id='@N,C,CA,O')")
uf.desc[-1].add_prompt("relax> structure.superimpose(method='fit to mean', atom_id='@N,C,CA,O')")
uf.desc[-1].add_paragraph("To superimpose model 2 onto model 3 using backbone heavy atoms, type one of:")
uf.desc[-1].add_prompt("relax> structure.superimpose([3, 2], 'fit to first', '@N,C,CA,O')")
uf.desc[-1].add_prompt("relax> structure.superimpose(models=[3, 2], method='fit to first', atom_id='@N,C,CA,O')")
uf.backend = pipe_control.structure.main.superimpose
uf.menu_text = "&superimpose"
uf.wizard_apply_button = False
uf.wizard_height_desc = 450
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.translate user function.
uf = uf_info.add_uf('structure.translate')
uf.title = "Laterally displace the internal structural object by the translation vector."
uf.title_short = "Structure translation."
uf.add_keyarg(
    name = "T",
    py_type = "float_array",
    dim = 3,
    desc_short = "translation vector",
    desc = "The translation vector."
)
uf.add_keyarg(
    name = "model",
    py_type = "int",
    desc_short = "model",
    desc = "The model to translate (which if not set will cause all models to be translate).",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom ID string",
    desc = "The atom identification string.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is used to translate the internal structural data by the given translation vector.  The translation can be restricted to one specific model.")
uf.backend = pipe_control.structure.main.translate
uf.menu_text = "&translate"
uf.wizard_size = (750, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.web_of_motion user function.
uf = uf_info.add_uf('structure.web_of_motion')
uf.title = "Create a PDB representation of motion between structures using a web of interconnecting lines."
uf.title_short = "Web of motion between models."
uf.add_keyarg(
    name = "pipes",
    py_type = "str_list",
    desc_short = "data pipes",
    desc = "The data pipes to generate the web between.",
    wiz_combo_iter = pipe_names,
    wiz_read_only = False,
    can_be_none = True
)
uf.add_keyarg(
    name = "models",
    py_type = "int_list_of_lists",
    desc_short = "model list for each data pipe",
    desc = "The list of models for each data pipe to generate the web between.  The number of elements must match the pipes argument.  If no models are given, then all will be used.",
    can_be_none = True
)
uf.add_keyarg(
    name = "molecules",
    py_type = "str_list_of_lists",
    desc_short = "molecule list for each data pipe",
    desc = "The list of molecules for each data pipe to generate the web between.  This allows differently named molecules in the same or different data pipes to be superimposed.  The number of elements must match the pipes argument.  If no molecules are given, then all will be used.",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom identification string",
    desc = "The atom identification string of the coordinates of interest.",
    can_be_none = True
)
uf.add_keyarg(
    name = "file",
    py_type = "str_or_inst",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file.",
    wiz_filesel_wildcard = WILDCARD_STRUCT_PDB_ALL,
    wiz_filesel_style = FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory to save the file to.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause any pre-existing files to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will create a PDB representation of the motion between the atoms of a given set of structures.  Identical atoms of the structures are concatenated into one model, within a temporary internal structural object, linked together using PDB CONECT records, and then written to the PDB file.")
uf.desc[-1].add_paragraph(paragraph_multi_struct)
uf.desc[-1].add_paragraph(paragraph_atom_id)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To create a web of motion for the models 1, 3, and 5, type:")
uf.desc[-1].add_prompt("relax> structure.web_of_motion(models=[[1, 3, 5]], file='web.pdb')")
uf.desc[-1].add_paragraph("To create a web of motion for the molecules 'A', 'B', 'C', and 'D', type:")
uf.desc[-1].add_prompt("relax> structure.web_of_motion(molecules=[['A', 'B', 'C', 'D']], file='web.pdb')")
uf.backend = pipe_control.structure.main.web_of_motion
uf.menu_text = "&web_of_motion"
uf.wizard_height_desc = 450
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.write_pdb user function.
uf = uf_info.add_uf('structure.write_pdb')
uf.title = "Writing structures to a PDB file."
uf.title_short = "PDB writing."
uf.add_keyarg(
    name = "file",
    py_type = "str_or_inst",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file.",
    wiz_filesel_wildcard = WILDCARD_STRUCT_PDB_ALL,
    wiz_filesel_style = FD_SAVE
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
    name = "model_num",
    py_type = "int",
    desc_short = "model number",
    desc = "Restrict the writing of structural data to a single model in the PDB file.",
    can_be_none = True
)
uf.add_keyarg(
    name = "compress_type",
    default = 0,
    py_type = "int",
    desc_short = "compression type",
    desc = "The type of compression to use when creating the file.",
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
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause any pre-existing files to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will write all of the structural data loaded in the current data pipe to be converted to the PDB format and written to file.  Specifying the model number allows single models to be output.")
uf.desc[-1].add_paragraph("The default behaviour of this function is to not compress the file.  The compression can, however, be changed to either bzip2 or gzip compression.  If the '.bz2' or '.gz' extension is not included in the file name, it will be added.  This behaviour is controlled by the compression type which can be set to")
uf.desc[-1].add_item_list_element("0", "No compression (no file extension).")
uf.desc[-1].add_item_list_element("1", "bzip2 compression ('.bz2' file extension).")
uf.desc[-1].add_item_list_element("2", "gzip compression ('.gz' file extension).")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To write all models and molecules to the PDB file 'ensemble.pdb' within the directory '~/pdb', type one of:")
uf.desc[-1].add_prompt("relax> structure.write_pdb('ensemble.pdb', '~/pdb')")
uf.desc[-1].add_prompt("relax> structure.write_pdb(file='ensemble.pdb', dir='pdb')")
uf.desc[-1].add_paragraph("To write model number 3 into the new file 'test.pdb', use one of:")
uf.desc[-1].add_prompt("relax> structure.write_pdb('test.pdb', model_num=3)")
uf.desc[-1].add_prompt("relax> structure.write_pdb(file='test.pdb', model_num=3)")
uf.backend = pipe_control.structure.main.write_pdb
uf.menu_text = "&write_pdb"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 700)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + 'write_pdb.png'
