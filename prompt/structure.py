###############################################################################
#                                                                             #
# Copyright (C) 2003-2011 Edward d'Auvergne                                   #
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
"""Module containing the 'structure' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
import generic_fns.structure.geometric
import generic_fns.structure.main


class Structure(User_fn_class):
    """Class containing the structural related functions."""

    def add_atom(self, atom_name=None, res_name=None, res_num=None, pos=[None, None, None], element=None, atom_num=None, chain_id=None, segment_id=None, pdb_record=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.add_atom("
            text = text + "atom_name=" + repr(atom_name)
            text = text + ", res_name=" + repr(res_name)
            text = text + ", res_num=" + repr(res_num)
            text = text + ", pos=" + repr(pos)
            text = text + ", element=" + repr(element)
            text = text + ", atom_num=" + repr(atom_num)
            text = text + ", chain_id=" + repr(chain_id)
            text = text + ", segment_id=" + repr(segment_id)
            text = text + ", pdb_record=" + repr(pdb_record) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(atom_name, 'atom name')
        arg_check.is_str(res_name, 'residue name')
        arg_check.is_int(res_num, 'residue number')
        arg_check.is_float_array(pos, 'atomic position', size=3)
        arg_check.is_str(element, 'element', can_be_none=True)
        arg_check.is_int(atom_num, 'atom number', can_be_none=True)
        arg_check.is_str(chain_id, 'chain ID', can_be_none=True)
        arg_check.is_str(segment_id, 'segment_id', can_be_none=True)
        arg_check.is_str(pdb_record, 'pdb_record', can_be_none=True)

        # Execute the functional code.
        generic_fns.structure.main.add_atom(atom_name=atom_name, res_name=res_name, res_num=res_num, pos=pos, element=element, atom_num=atom_num, chain_id=chain_id, segment_id=segment_id, pdb_record=pdb_record)

    # The function doc info.
    add_atom._doc_title = "Add an atom."
    add_atom._doc_title_short = "Atom creation."
    add_atom._doc_args = [
        ["atom_name", "The atom name."],
        ["res_name", "The residue name."],
        ["res_num", "The residue number."],
        ["pos", "The atomic coordinates."],
        ["element", "The element name."],
        ["atom_num", "The optional atom number."],
        ["chain_id", "The optional chain ID string."],
        ["segment_id", "The optional segment ID string."],
        ["pdb_record", "The optional PDB record name, e.g. 'ATOM' or 'HETATM'."]
    ]
    add_atom._doc_desc = """
        This allows atoms to be added to the internal structural object.
        """
    _build_doc(add_atom)


    def connect_atom(self, index1=None, index2=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.connect_atom("
            text = text + "index1=" + repr(index1)
            text = text + ", index2=" + repr(index2) + ")"
            print(text)

        # The argument checks.
        arg_check.is_int(index1, 'index 1')
        arg_check.is_int(index2, 'index 2')

        # Execute the functional code.
        generic_fns.structure.main.connect_atom(index1=index1, index2=index2)

    # The function doc info.
    connect_atom._doc_title = "Connect two atoms."
    connect_atom._doc_title_short = "Atom connection."
    connect_atom._doc_args = [
        ["index1", "The global index of the first atom."],
        ["index2", "The global index of the second atom."]
    ]
    connect_atom._doc_desc = """
        This allows atoms to be connected in the internal structural object.  The global index is normally equal to the PDB atom number minus 1.
        """
    _build_doc(connect_atom)


    def create_diff_tensor_pdb(self, scale=1.8e-6, file='tensor.pdb', dir=None, force=False):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.create_diff_tensor_pdb("
            text = text + "scale=" + repr(scale)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num(scale, 'scaling factor')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        generic_fns.structure.geometric.create_diff_tensor_pdb(scale=scale, file=file, dir=dir, force=force)

    # The function doc info.
    create_diff_tensor_pdb._doc_title = "Create a PDB file to represent the diffusion tensor."
    create_diff_tensor_pdb._doc_title_short = "Diffusion tensor PDB file creation."
    create_diff_tensor_pdb._doc_args = [
        ["scale", "Value for scaling the diffusion rates."],
        ["file", "The name of the PDB file."],
        ["dir", "The directory where the file is located."],
        ["force", "A flag which, if set to True, will overwrite the any pre-existing file."]
    ]
    create_diff_tensor_pdb._doc_desc = """
        This creates a PDB file containing an artificial geometric structure to represent the diffusion tensor.  A structure must have previously been read into relax.  The diffusion tensor is represented by an ellipsoidal, spheroidal, or spherical geometric object with its origin located at the centre of mass (of the selected residues).  This diffusion tensor PDB file can subsequently read into any molecular viewer.

        There are four different types of residue within the PDB.  The centre of mass of the selected residues is represented as a single carbon atom of the residue 'COM'.  The ellipsoidal geometric shape consists of numerous H atoms of the residue 'TNS'.  The axes of the tensor, when defined, are presented as the residue 'AXS' and consist of carbon atoms: one at the centre of mass and one at the end of each eigenvector.  Finally, if Monte Carlo simulations were run and the diffusion tensor parameters were allowed to vary then there will be multiple 'SIM' residues, one for each simulation.  These are essentially the same as the 'AXS' residue, representing the axes of the simulated tensors, and they will appear as a distribution.

        As the Brownian rotational diffusion tensor is a measure of the rate of rotation about different axes - the larger the geometric object, the faster the diffusion of a molecule. For example the diffusion tensor of a water molecule is much larger than that of a macromolecule.

        The effective global correlation time experienced by an XH bond vector, not to be confused with the Lipari and Szabo parameter tau_e, will be approximately proportional to the component of the diffusion tensor parallel to it.  The approximation is not exact due to the multiexponential form of the correlation function of Brownian rotational diffusion.  If an XH bond vector is parallel to the longest axis of the tensor, it will be unaffected by rotations about that axis, which are the fastest rotations of the molecule, and therefore its effective global correlation time will be maximal.

        To set the size of the diffusion tensor within the PDB frame the unit vectors used to generate the geometric object are first multiplied by the diffusion tensor (which has the units of inverse seconds) then by the scaling factor (which has the units of second Angstroms and has the default value of 1.8e-6 s.Angstrom).  Therefore the rotational diffusion rate per Angstrom is equal the inverse of the scale value (which defaults to 5.56e5 s^-1.Angstrom^-1).  Using the default scaling value for spherical diffusion, the correspondence between global correlation time, Diso diffusion rate, and the radius of the sphere for a number of discrete cases will be:

        _________________________________________________
        |           |               |                   |
        | tm (ns)   | Diso (s^-1)   | Radius (Angstrom) |
        |___________|_______________|___________________|
        |           |               |                   |
        | 1         | 1.67e8        | 300               |
        |           |               |                   |
        | 3         | 5.56e7        | 100               |
        |           |               |                   |
        | 10        | 1.67e7        | 30                |
        |           |               |                   |
        | 30        | 5.56e6        | 10                |
        |___________|_______________|___________________|


        The scaling value has been fixed to facilitate comparisons within or between publications, but can be changed to vary the size of the tensor geometric object if necessary.  Reporting the rotational diffusion rate per Angstrom within figure legends would be useful.

        To create the tensor PDB representation, a number of algorithms are utilised.  Firstly the centre of mass is calculated for the selected residues and is represented in the PDB by a C atom.  Then the axes of the diffusion are calculated, as unit vectors scaled to the appropriate length (multiplied by the eigenvalue Dx, Dy, Dz, Dpar, Dper, or Diso as well as the scale value), and a C atom placed at the position of this vector plus the centre of mass.  Finally a uniform distribution of vectors on a sphere is generated using spherical coordinates.  By incrementing the polar angle using an arccos distribution, a radial array of vectors representing latitude are created while incrementing the azimuthal angle evenly creates the longitudinal vectors.  These unit vectors, which are distributed within the PDB frame and are of 1 Angstrom in length, are first rotated into the diffusion frame using a rotation matrix (the spherical diffusion tensor is not rotated).  Then they are multiplied by the diffusion tensor matrix to extend the vector out to the correct length, and finally multiplied by the scale value so that the vectors reasonably superimpose onto the macromolecular structure.  The last set of algorithms place all this information into a PDB file.  The distribution of vectors are represented by H atoms and are all connected using PDB CONECT records.  Each H atom is connected to its two neighbours on the both the longitude and latitude.  This creates a geometric PDB object with longitudinal and latitudinal lines.
        """
    _build_doc(create_diff_tensor_pdb)


    def create_vector_dist(self, length=2e-9, file='XH_dist.pdb', dir=None, symmetry=True, force=False):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.create_vector_dist("
            text = text + "length=" + repr(length)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", symmetry=" + repr(symmetry)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num(length, 'vector length')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(symmetry, 'symmetry flag')
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        generic_fns.structure.geometric.create_vector_dist(length=length, symmetry=symmetry, file=file, dir=dir, force=force)

    # The function doc info.
    create_vector_dist._doc_title = "Create a PDB file representation of the distribution of XH bond vectors."
    create_vector_dist._doc_title_short = "XH vector distribution PDB representation."
    create_vector_dist._doc_args = [
        ["length", "The length of the vectors in the PDB representation (meters)."],
        ["file", "The name of the PDB file."],
        ["dir", "The directory to place the file into."],
        ["symmetry", "A flag which if True will create a second chain with reversed XH bond orientations."],
        ["force", "A flag which if True will overwrite the file if it already exists."]
    ]
    create_vector_dist._doc_desc = """
        This creates a PDB file containing an artificial vectors, the length of which default to the length argument of 20 Angstrom.  A structure must have previously been read into relax.  The origin of the vector distribution is located at the centre of mass (of the selected residues).  This vector distribution PDB file can subsequently be read into any molecular viewer.

        Because of the symmetry of the diffusion tensor reversing the orientation of the XH bond vector has no effect.  Therefore by setting the symmetry flag two chains 'A' and 'B' will be added to the PDB file whereby chain 'B' is chain 'A' with the XH bonds reversed.
        """
    _build_doc(create_vector_dist)


    def get_pos(self, spin_id=None, ave_pos=True):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.get_pos("
            text = text + "spin_id=" + repr(spin_id)
            text = text + ", ave_pos=" + repr(ave_pos) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)
        arg_check.is_bool(ave_pos, 'average position flag')

        # Execute the functional code.
        generic_fns.structure.main.get_pos(spin_id=spin_id, ave_pos=ave_pos)

    # The function doc info.
    get_pos._doc_title = "Extract the atomic positions from the loaded structures for the given spins."
    get_pos._doc_title_short = "Atomic position extraction."
    get_pos._doc_args = [
        ["spin_id", "The spin identification string."],
        ["ave_pos", "A flag specifying if the position of the atom is to be averaged across models."]
    ]
    get_pos._doc_desc = """
        This allows the atomic positions of the spins to be extracted from the loaded structures.  This is automatically performed by the structure.load_spins() user function, but if the sequence information is generated in other ways, this user function allows the structural information to be obtained.

        If averaging the atomic positions, then average position of all models will be loaded into the spin container.  Otherwise the positions from all models will be loaded separately.
        """
    get_pos._doc_examples = """
        For a model-free backbone amide nitrogen analysis whereby the N spins have already been
        created, to obtain the backbone N positions from the file '1F3Y.pdb' (which is a single
        protein), type the following two user functions:

        relax> structure.read_pdb('1F3Y.pdb')
        relax> structure.get_pos(spin_id='@N')
        """
    _build_doc(get_pos)


    def delete(self):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.delete()"
            print(text)

        # Execute the functional code.
        generic_fns.structure.main.delete()

    # The function doc info.
    delete._doc_title = "Delete all structural information."
    delete._doc_title_short = "Structure deletion."
    delete._doc_desc = """
        This will delete all the structural information from the current data pipe.  All spin and sequence information loaded from these structures will be preserved - this only affects the structural data.
        """
    delete._doc_examples = """
        Simply type:

        relax> structure.delete()
        """
    _build_doc(delete)


    def displacement(self, model_from=None, model_to=None, atom_id=None, centroid=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.displacement("
            text = text + "model_from=" + repr(model_from)
            text = text + ", model_to=" + repr(model_to)
            text = text + ", atom_id=" + repr(atom_id)
            text = text + ", centroid=" + repr(centroid) + ")"
            print(text)

        # The argument checks.
        arg_check.is_int(model_from, 'model from', can_be_none=True)
        arg_check.is_int(model_to, 'model to', can_be_none=True)
        arg_check.is_str(atom_id, 'atom identification string', can_be_none=True)
        arg_check.is_float_array(centroid, 'centroid position', can_be_none=True)

        # Execute the functional code.
        generic_fns.structure.main.displacement(model_from=model_from, model_to=model_to, atom_id=atom_id, centroid=centroid)

    # The function doc info.
    displacement._doc_title = "Determine the rotational and translational displacement between a set of models."
    displacement._doc_title_short = "Rotational and translational displacement."
    displacement._doc_args = [
        ["model_from", "The optional model number for the starting position of the displacement."],
        ["model_to", "The optional model number for the ending position of the displacement."],
        ["atom_id", "The atom identification string."],
        ["centroid", "The alternative position of the centroid."]
    ]
    displacement._doc_desc = """
        This user function allows the rotational and translational displacement between two models of the same structure to be calculated.  The information will be printed out in various formats and held in the relax data store.  This is directional, so there is a starting and ending position for each displacement.  If the starting and ending models are not specified, then the displacements in all directions between all models will be calculated.

        The atom ID, which uses the same notation as the spin ID strings, can be used to restrict the displacement calculation to certain molecules, residues, or atoms.  This is useful if studying domain motions, secondary structure rearrangements, amino acid side chain rotations, etc.

        By supplying the position of the centroid, an alternative position than the standard rigid body centre is used as the focal point of the motion.  The allows, for example, a pivot of a rotational domain motion to be specified.  This is not a formally correct algorithm, all translations will be zero, but does give an indication to the amplitude of the pivoting angle.
        """
    displacement._doc_examples = """
        To determine the rotational and translational displacements between all sets of models, type:

        relax> structure.displacement()


        To determine the displacement from model 5 to all other models, type:

        relax> structure.displacement(model_from=5)


        To determine the displacement of all models to model 5, type:

        relax> structure.displacement(model_to=5)



        To determine the displacement of model 2 to model 3, type one of:

        relax> structure.displacement(2, 3)
        relax> structure.displacement(model_from=2, model_to=3)
         """
    _build_doc(displacement)


    def find_pivot(self, models=None, atom_id=None, init_pos=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.find_pivot("
            text = text + "models=" + repr(models)
            text = text + ", atom_id=" + repr(atom_id)
            text = text + ", init_pos=" + repr(init_pos) + ")"
            print(text)

        # The argument checks.
        arg_check.is_int_list(models, 'model list', can_be_none=True)
        arg_check.is_str(atom_id, 'atom identification string', can_be_none=True)
        arg_check.is_float_array(init_pos, 'initial pivot position', can_be_none=True)

        # Execute the functional code.
        generic_fns.structure.main.find_pivot(models=models, atom_id=atom_id, init_pos=init_pos)

    # The function doc info.
    find_pivot._doc_title = "Find the pivot point of the motion of a set of structures."
    find_pivot._doc_title_short = "Pivot search."
    find_pivot._doc_args = [
        ["models", "The list of models to use."],
        ["atom_id", "The atom identification string."],
        ["init_pos", "The initial position of the pivot."]
    ]
    find_pivot._doc_desc = """
        This is used to find pivot point of motion between a set of structural models.  If the list of models is not supplied, then all models will be used.

        The atom ID, which uses the same notation as the spin ID strings, can be used to restrict the search to certain molecules, residues, or atoms.  For example to only use backbone heavy atoms in a protein, use the atom ID of '@N,C,CA,O', assuming those are the names of the atoms from the structural file.

        By supplying the position of the centroid, an alternative position than the standard rigid body centre is used as the focal point of the superimposition.  The allows, for example, the superimposition about a pivot point.
        """
    _build_doc(find_pivot)


    def load_spins(self, spin_id=None, ave_pos=True):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.load_spins("
            text = text + "spin_id=" + repr(spin_id)
            text = text + ", ave_pos=" + repr(ave_pos) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)
        arg_check.is_bool(ave_pos, 'average position flag')

        # Execute the functional code.
        generic_fns.structure.main.load_spins(spin_id=spin_id, ave_pos=ave_pos)

    # The function doc info.
    load_spins._doc_title = "Load spins from the structure into the relax data store."
    load_spins._doc_title_short = "Loading spins from structure."
    load_spins._doc_args = [
        ["spin_id", "The spin identification string."],
        ["ave_pos", "A flag specifying if the position of the atom is to be averaged across models."]]
    load_spins._doc_desc = """
        This allows a sequence to be generated within the relax data store using the atomic information from the structure already associated with this data pipe.  The spin ID string is used to select which molecules, which residues, and which atoms will be recognised as spin systems within relax.  If the spin ID is left unspecified, then all molecules, residues, and atoms will be placed within the data store (and all atoms will be treated as spins).

        If averaging the atomic positions, then average position of all models will be loaded into the spin container.  Otherwise the positions from all models will be loaded separately.
        """
    load_spins._doc_examples = """
        For a model-free backbone amide nitrogen analysis, to load just the backbone N sequence from
        the file '1F3Y.pdb' (which is a single protein), type the following two user functions:

        relax> structure.read_pdb('1F3Y.pdb')
        relax> structure.load_spins(spin_id='@N')


        For an RNA analysis of adenine C8 and C2, guanine C8 and N1, cytidine C5 and C6, and uracil
        N3, C5, and C6, type the following series of commands (assuming that the PDB file with this
        atom naming has already been read):

        relax> structure.load_spins(spin_id=":A@C8")
        relax> structure.load_spins(spin_id=":A@C2")
        relax> structure.load_spins(spin_id=":G@C8")
        relax> structure.load_spins(spin_id=":G@N1")
        relax> structure.load_spins(spin_id=":C@C5")
        relax> structure.load_spins(spin_id=":C@C6")
        relax> structure.load_spins(spin_id=":U@N3")
        relax> structure.load_spins(spin_id=":U@C5")
        relax> structure.load_spins(spin_id=":U@C6")

        Alternatively using some Python programming:

        relax> for id in [":A@C8", ":A@C2", ":G@C8", ":G@N1", ":C@C5", ":C@C6", ":U@N3", ":U@C5", ":U@C6"]:
        relax>     structure.load_spins(spin_id=id)
        """
    _build_doc(load_spins)


    def read_pdb(self, file=None, dir=None, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None, parser='internal'):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.read_pdb("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", read_mol=" + repr(read_mol)
            text = text + ", set_mol_name=" + repr(set_mol_name)
            text = text + ", read_model=" + repr(read_model)
            text = text + ", set_model_num=" + repr(set_model_num)
            text = text + ", parser=" + repr(parser) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_int_or_int_list(read_mol, 'read molecule number', can_be_none=True)
        arg_check.is_int_or_int_list(read_model, 'read model', can_be_none=True)
        arg_check.is_int_or_int_list(set_model_num, 'set model numbers', can_be_none=True)
        arg_check.is_str_or_str_list(set_mol_name, 'set molecule names', can_be_none=True)
        arg_check.is_str(parser, 'PDB parser')

        # Execute the functional code.
        generic_fns.structure.main.read_pdb(file=file, dir=dir, read_mol=read_mol, set_mol_name=set_mol_name, read_model=read_model, set_model_num=set_model_num, parser=parser)

    # The function doc info.
    read_pdb._doc_title = "Reading structures from PDB files."
    read_pdb._doc_title_short = "PDB reading."
    read_pdb._doc_args = [
        ["file", "The name of the PDB file."],
        ["dir", "The directory where the file is located."],
        ["read_mol", "If set, only the given molecule(s) will be read.  The molecules are determined differently by the different parsers, but are numbered consecutively from 1.  If unset, then all molecules will be loaded.  By providing a list of numbers such as [1, 2], multiple molecules will be read."],
        ["set_mol_name", "Set the names of the read molecules.  If unset, then the molecules will be automatically labelled based on the file name or other information.  This can either be a single name or a list of names."],
        ["read_model", "If set, only the given model number(s) from the PDB file will be read.  This can be a single number or list of numbers."],
        ["set_model_num", "Set the model numbers of the loaded molecules.  If unset, then the PDB model numbers will be preserved if they exist.  This can be a single number or list of numbers."],
        ["parser", "The PDB parser used to read the file."]]
    read_pdb._doc_desc = """
        The reading of PDB files into relax is quite a flexible procedure allowing for both models, defined as an ensemble of the same molecule but with different atomic positions, and different molecules within the same model.  One of more molecules can exist in one or more models.  The flexibility allows PDB models to be converted into different molecules and different PDB files loaded as the same molecule but as different models.

        A few different PDB parsers can be used to read the structural data.  The choice of which to use depends on whether your PDB file is supported by that reader.  These are selected by setting the 'parser' argument to one of:

            'internal' - a fast PDB parser built into relax.
            'scientific' - the Scientific Python PDB parser.

        In a PDB file, the models are specified by the MODEL PDB record.  All the supported PDB readers in relax recognise this.  The molecule level is quite different between the Scientific Python and internal readers.  For how Scientific Python defines molecules, please see its documentation.  The internal reader is far simpler as it defines molecules using the TER PDB record.  In both cases, the molecules will be numbered consecutively from 1.

        Setting the molecule name allows the molecule within the PDB (within one model) to have a custom name.  If not set, then the molecules will be named after the file name, with the molecule number appended if more than one exists.

        Note that relax will complain if it cannot work out what to do.

        This is able to handle uncompressed, bzip2 compressed files, or gzip compressed files automatically.  The full file name including extension can be supplied, however, if the file cannot be found, this function will search for the file name with '.bz2' appended followed by the file name with '.gz' appended.
        """
    read_pdb._doc_examples = """
        To load all structures from the PDB file 'test.pdb' in the directory '~/pdb', including all
        models and all molecules, type one of:

        relax> structure.read_pdb('test.pdb', '~/pdb')
        relax> structure.read_pdb(file='test.pdb', dir='pdb')


        To load the 10th model from the file 'test.pdb' using the Scientific Python PDB parser and
        naming it 'CaM', use one of:

        relax> structure.read_pdb('test.pdb', read_model=10, set_mol_name='CaM',
                                  parser='scientific')
        relax> structure.read_pdb(file='test.pdb', read_model=10, set_mol_name='CaM',
                                  parser='scientific')


        To load models 1 and 5 from the file 'test.pdb' as two different structures of the same
        model, type one of:

        relax> structure.read_pdb('test.pdb', read_model=[1, 5], set_model_num=[1, 1])
        relax> structure.read_pdb('test.pdb', set_mol_name=['CaM_1', 'CaM_2'], read_model=[1, 5],
                                  set_model_num=[1, 1])

        To load the files 'lactose_MCMM4_S1_1.pdb', 'lactose_MCMM4_S1_2.pdb',
        'lactose_MCMM4_S1_3.pdb' and 'lactose_MCMM4_S1_4.pdb' as models, type the following sequence
        of commands:

        relax> structure.read_pdb('lactose_MCMM4_S1_1.pdb', set_mol_name='lactose_MCMM4_S1',
                                  set_model_num=1)
        relax> structure.read_pdb('lactose_MCMM4_S1_2.pdb', set_mol_name='lactose_MCMM4_S1',
                                  set_model_num=2)
        relax> structure.read_pdb('lactose_MCMM4_S1_3.pdb', set_mol_name='lactose_MCMM4_S1',
                                  set_model_num=3)
        relax> structure.read_pdb('lactose_MCMM4_S1_4.pdb', set_mol_name='lactose_MCMM4_S1',
                                  set_model_num=4)
        """
    _build_doc(read_pdb)


    def read_xyz(self, file=None, dir=None, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None):
        """The XYZ loading function.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the XYZ file.

        dir:  The directory where the file is located.

        read_mol:  If set, only the given molecule(s) will be read.

        set_mol_name:  Set the names of the read molecules.

        read_model:  If set, only the given model number(s) from the XYZ file will be read.

        set_model_num:  Set the model numbers of the read molecules.


        Description
        ~~~~~~~~~~~

        The XYZ files with different models, which defined as an ensemble of the same molecule but with 
        different atomic positions, can be read into relax. If there are several molecules in one xyz file, 
        please seperate them into different files and then load them individually. Loading different models
        and different molecules is controlled by the four keyword arguments 'read_mol', 'set_mol_name', 
        'read_model', and 'set_model_num'.


        The 'set_mol_name' argument is used to name the molecules within the XYZ (within one
        model).  If not set, then the molecules will be named after the file name, with the molecule
        number appended if more than one exists.

        Note that relax will complain if it cannot work out what to do.


        Examples
        ~~~~~~~~

        To load all structures from the XYZ file 'test.xyz' in the directory '~/xyz', including all
        models and all molecules, type one of:

        relax> structure.read_xyz('test.xyz', '~/xyz')
        relax> structure.read_xyz(file='test.xyz', dir='xyz')


        To load the 10th model from the file 'test.xyz' and
        naming it 'CaM', use one of:

        relax> structure.read_xyz('test.xyz', read_model=10, set_mol_name='CaM')
        relax> structure.read_xyz(file='test.xyz', read_model=10, set_mol_name='CaM')


        To load models 1 and 5 from the file 'test.xyz' as two different structures of the same
        model, type one of:

        relax> structure.read_xyz('test.xyz', read_model=[1, 5], set_model_num=[1, 1])
        relax> structure.read_xyz('test.xyz', set_mol_name=['CaM_1', 'CaM_2'], read_model=[1, 5],
                                  set_model_num=[1, 1])

        To load the files 'test_1.xyz', 'test_2.xyz', 'test_3.xyz' and 'test_4.xyz' as models, type the 
        following sequence of commands:

        relax> structure.read_xyz('test_1.xyz', set_mol_name='test_1',
                                  set_model_num=1)
        relax> structure.read_xyz('test_2.xyz', set_mol_name='test_2',
                                  set_model_num=2)
        relax> structure.read_xyz('test_3.xyz', set_mol_name='test_3',
                                  set_model_num=3)
        relax> structure.read_xyz('test_4.xyz', set_mol_name='test_4',
                                  set_model_num=4)
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.read_xyz("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", read_mol=" + repr(read_mol)
            text = text + ", set_mol_name=" + repr(set_mol_name)
            text = text + ", read_model=" + repr(read_model)
            text = text + ", set_model_num=" + repr(set_model_num)
            text = text +  ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_int_or_int_list(read_mol, 'read molecule number', can_be_none=True)
        arg_check.is_int_or_int_list(read_model, 'read model', can_be_none=True)
        arg_check.is_int_or_int_list(set_model_num, 'set model numbers', can_be_none=True)
        arg_check.is_str_or_str_list(set_mol_name, 'set molecule names', can_be_none=True)

        # Execute the functional code.
        generic_fns.structure.main.read_xyz(file=file, dir=dir, read_mol=read_mol, set_mol_name=set_mol_name, read_model=read_model, set_model_num=set_model_num)


    def rotate(self, R=None, origin=None, model=None, atom_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.rotate("
            text = text + "R=" + repr(R)
            text = text + ", origin=" + repr(origin)
            text = text + ", model=" + repr(model)
            text = text + ", atom_id=" + repr(atom_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_float_matrix(R, 'rotation matrix', dim=(3,3))
        arg_check.is_float_array(origin, 'origin of rotation', size=3, can_be_none=True)
        arg_check.is_int(model, 'model', can_be_none=True)
        arg_check.is_str(atom_id, 'atom identification string', can_be_none=True)

        # Execute the functional code.
        generic_fns.structure.main.rotate(R=R, origin=origin, model=model, atom_id=atom_id)

    # The function doc info.
    rotate._doc_title = "Rotate the internal structural object about the given origin by the rotation matrix."
    rotate._doc_title_short = "Structure rotation."
    rotate._doc_args = [
        ["R", "The rotation matrix in forwards rotation notation."],
        ["origin", "The origin or pivot of the rotation."],
        ["model", "The model to rotate (which if not set will cause all models to be rotated)."]
    ]
    rotate._doc_desc = """
        This is used to rotate the internal structural data by the given rotation matrix.  If the origin is supplied, then this will act as the pivot of the rotation.  Otherwise, all structural data will be rotated about the point [0, 0, 0].  The model argument can be used to rotate specific models.
        """
    _build_doc(rotate)


    def superimpose(self, models=None, method='fit to mean', atom_id=None, centroid=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.superimpose("
            text = text + "models=" + repr(models)
            text = text + ", method=" + repr(method)
            text = text + ", atom_id=" + repr(atom_id)
            text = text + ", centroid=" + repr(centroid) + ")"
            print(text)

        # The argument checks.
        arg_check.is_int_list(models, 'model list', can_be_none=True)
        arg_check.is_str(method, 'superimposition method')
        arg_check.is_str(atom_id, 'atom identification string', can_be_none=True)
        arg_check.is_float_array(centroid, 'centroid position', can_be_none=True)

        # Execute the functional code.
        generic_fns.structure.main.superimpose(models=models, method=method, atom_id=atom_id, centroid=centroid)

    # The function doc info.
    superimpose._doc_title = "Superimpose a set of models of the same structure."
    superimpose._doc_title_short = "Structural superimposition."
    superimpose._doc_args = [
        ["models", "The list of models to superimpose."],
        ["method", "The superimposition method."],
        ["atom_id", "The atom identification string."],
        ["centroid", "The alternative position of the centroid."]
    ]
    superimpose._doc_desc = """
        This allows a set of models of the same structure to be superimposed to each other.  Two superimposition methods are currently supported:

            'fit to mean':  All models are fit to the mean structure.  This is the default and most accurate method for an ensemble description.  It is an iterative method which first calculates a mean structure and then fits each model to the mean structure using the Kabsch algorithm.  This is repeated until convergence.
            'fit to first':  This is quicker but is not as accurate for an ensemble description.  The Kabsch algorithm is used to rotate and translate each model to be superimposed onto the first model.

        If the list of models is not supplied, then all models will be superimposed.

        The atom ID, which uses the same notation as the spin ID strings, can be used to restrict the superimpose calculation to certain molecules, residues, or atoms.  For example to only superimpose backbone heavy atoms in a protein, use the atom ID of '@N,C,CA,O', assuming those are the names of the atoms from the structural file.

        By supplying the position of the centroid, an alternative position than the standard rigid body centre is used as the focal point of the superimposition.  The allows, for example, the superimposition about a pivot point.
        """
    superimpose._doc_examples = """
        To superimpose all sets of models, type one of:

        relax> structure.superimpose()
        relax> structure.superimpose(method='fit to mean')


        To superimpose the models 1, 2, 3, 5 onto model 4, type:

        relax> structure.superimpose(models=[4, 1, 2, 3, 5], method='fit to first')


        To superimpose an ensemble of protein structures using only the backbone heavy atoms, type
        one of:

        relax> structure.superimpose(atom_id='@N,C,CA,O')
        relax> structure.superimpose(method='fit to mean', atom_id='@N,C,CA,O')


        To superimpose model 2 onto model 3 using backbone heavy atoms, type one of:

        relax> structure.superimpose([3, 2], 'fit to first', '@N,C,CA,O')
        relax> structure.superimpose(models=[3, 2], method='fit to first', atom_id='@N,C,CA,O')
         """
    _build_doc(superimpose)


    def translate(self, T=None, model=None, atom_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.translate("
            text = text + "T=" + repr(T)
            text = text + ", model=" + repr(model)
            text = text + ", atom_id=" + repr(atom_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_float_array(T, 'translation vector', size=3)
        arg_check.is_int(model, 'model', can_be_none=True)
        arg_check.is_str(atom_id, 'atom identification string', can_be_none=True)

        # Execute the functional code.
        generic_fns.structure.main.translate(T=T, model=model, atom_id=atom_id)

    # The function doc info.
    translate._doc_title = "Laterally displace the internal structural object by the translation vector."
    translate._doc_title_short = "Structure translation."
    translate._doc_args = [
        ["T", "The translation vector."],
        ["model", "The model to translate (which if not set will cause all models to be translate)."],
        ["atom_id", "The atom identification string."]
    ]
    translate._doc_desc = """
        This is used to translate the internal structural data by the given translation vector.  The model argument can be used to translate specific models.
        """
    _build_doc(translate)


    def vectors(self, attached='H', spin_id=None, model=None, verbosity=1, ave=True, unit=True):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.vectors("
            text = text + "attached=" + repr(attached)
            text = text + ", spin_id=" + repr(spin_id)
            text = text + ", model=" + repr(model)
            text = text + ", verbosity=" + repr(verbosity)
            text = text + ", ave=" + repr(ave)
            text = text + ", unit=" + repr(unit) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(attached, 'attached atom')
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)
        arg_check.is_int(model, 'model', can_be_none=True)
        arg_check.is_int(verbosity, 'verbosity level')
        arg_check.is_bool(ave, 'average vector flag')
        arg_check.is_bool(unit, 'unit vector flag')

        # Execute the functional code.
        generic_fns.structure.main.vectors(attached=attached, spin_id=spin_id, model=model, verbosity=verbosity, ave=ave, unit=unit)

    # The function doc info.
    vectors._doc_title = "Extract and store the bond vectors from the loaded structures in the spin container."
    vectors._doc_title_short = "Bond vector extraction."
    vectors._doc_args = [
        ["attached", "The name of the second atom which attached to the spin of interest.  Regular expression is allowed, for example 'H*'."],
        ["spin_id", "The spin identification string."],
        ["model", "The model to extract bond vectors from (which if not set will cause the vectors of all models to be extracted)."],
        ["verbosity", "The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1."],
        ["ave", "A flag which if True will cause the bond vectors from all models to be averaged.  If vectors from only one model is extracted, this argument will have no effect."],
        ["unit", "A flag which if True will cause the unit vector to calculated rather than the full length bond vector."]
    ]
    vectors._doc_desc = """
        For a number of types of analysis, bond vectors or unit bond vectors are required for the calculations.  This user function allows these vectors to be extracted from the loaded structures.  The bond vector will be that from the atom associated with the spin system loaded in relax to the bonded atom specified by the 'attached' argument.  For example if the attached atom is set to 'H' and the protein backbone amide spins 'N' are loaded, the all 'N-H' vectors will be extracted.  But if set to 'CA', all atoms named 'CA' in the structures will be searched for and all 'N-Ca' bond vectors will be extracted.

        The extraction of vectors can occur in a number of ways.  For example if an NMR structure with N models is loaded or if multiple molecules, from any source, of the same compound are loaded as different models, there are three options for extracting the bond vector.  Firstly the bond vector of a single model can be extracted by setting the model number. Secondly the bond vectors from all models can be extracted if the model number is not set and the average vector flag is not set.  Thirdly, if the model number is not set and the average vector flag is set, then a single vector which is the average for all models will be calculated.
        """
    vectors._doc_examples = """
        To extract the XH vectors of the backbone amide nitrogens where in the PDB file the backbone
        nitrogen is called 'N' and the attached atom is called 'H', assuming multiple types of
        spin have already been loaded, type one of:

        relax> structure.vectors(spin_id='@N')
        relax> structure.vectors('H', spin_id='@N')
        relax> structure.vectors(attached='H', spin_id='@N')

        If the attached atom is called 'HN', type:

        relax> structure.vectors(attached='HN', spin_id='@N')

        For the 'CA' spin bonded to the 'HA' proton, type:

        relax> structure.vectors(attached='HA', spin_id='@CA')


        If you are working with RNA, you can use the residue name identifier to calculate the
        vectors for each residue separately.  For example to calculate the vectors for all possible
        spins in the bases, type:

        relax> structure.vectors('H2', spin_id=':A')
        relax> structure.vectors('H8', spin_id=':A')
        relax> structure.vectors('H1', spin_id=':G')
        relax> structure.vectors('H8', spin_id=':G')
        relax> structure.vectors('H5', spin_id=':C')
        relax> structure.vectors('H6', spin_id=':C')
        relax> structure.vectors('H3', spin_id=':U')
        relax> structure.vectors('H5', spin_id=':U')
        relax> structure.vectors('H6', spin_id=':U')

        Alternatively, assuming the desired spins have been loaded, regular expression can be used:

        relax> structure.vectors('H*')
        """
    _build_doc(vectors)


    def write_pdb(self, file=None, dir=None, model_num=None, compress_type=0, force=False):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "structure.write_pdb("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", model_num=" + repr(model_num)
            text = text + ", compress_type=" + repr(compress_type)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_int(model_num, 'model number', can_be_none=True)
        arg_check.is_int(compress_type, 'compression type')
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        generic_fns.structure.main.write_pdb(file=file, dir=dir, model_num=model_num, compress_type=compress_type, force=force)

    # The function doc info.
    write_pdb._doc_title = "Writing structures to a PDB file."
    write_pdb._doc_title_short = "PDB writing."
    write_pdb._doc_args = [["file", "The name of the PDB file."],
                           ["dir", "The directory where the file is located."],
                           ["model_num", "Restrict the writing of structural data to a single model in the PDB file."],
                           ["compress_type", "The type of compression to use when creating the file."],
                           ["force", "A flag which if set to True will cause any pre-existing files to be overwritten."]]
    write_pdb._doc_desc = """
        This will write all of the structural data loaded in the current data pipe to be converted to the PDB format and written to file.  Specifying the model number allows single models to be output.

        The default behaviour of this function is to not compress the file.  The compression can, however, be changed to either bzip2 or gzip compression.  If the '.bz2' or '.gz' extension is not included in the file name, it will be added.  This behaviour is controlled by the compress_type argument which can be set to

            0:  No compression (no file extension).
            1:  bzip2 compression ('.bz2' file extension).
            2:  gzip compression ('.gz' file extension).
        """
    write_pdb._doc_examples = """
        To write all models and molecules to the PDB file 'ensemble.pdb' within the directory '~/pdb', type
        one of:

        relax> structure.write_pdb('ensemble.pdb', '~/pdb')
        relax> structure.write_pdb(file='ensemble.pdb', dir='pdb')


        To write model number 3 into the new file 'test.pdb', use one of:

        relax> structure.write_pdb('test.pdb', model_num=3)
        relax> structure.write_pdb(file='test.pdb', model_num=3)
        """
    _build_doc(write_pdb)
