###############################################################################
#                                                                             #
# Copyright (C) 2003-2009,2011-2016,2019,2024 Edward d'Auvergne               #
# Copyright (C) 2006 Chris MacRaild                                           #
# Copyright (C) 2008 Sebastien Morin                                          #
# Copyright (C) 2011 Han Sun                                                  #
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

# Python module imports.
from minfx.generic import generic_minimise
from numpy import array, average, concatenate, dot, float64, mean, ones, std, zeros
from numpy.linalg import norm
from os import F_OK, access, getcwd
from re import search
import sys
from warnings import warn

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from data_store.seq_align import Sequence_alignments
from lib.check_types import is_float
from lib.errors import RelaxError, RelaxFileError
from lib.geometry.vectors import vector_angle_atan2
from lib.io import get_file_path, open_write_file, write_data
from lib.plotting.api import correlation_matrix, write_xy_data, write_xy_header
from lib.selection import tokenise
from lib.sequence import write_spin_data
from lib.sequence_alignment.msa import msa_general, msa_residue_numbers, msa_residue_skipping
from lib.structure.internal.coordinates import assemble_atomic_coordinates, assemble_coord_array, loop_coord_structures
from lib.structure.internal.displacements import Displacements
from lib.structure.internal.object import Internal
from lib.structure.pca import pca_analysis
from lib.structure.represent.diffusion_tensor import diffusion_tensor
from lib.structure.statistics import atomic_rmsd, per_atom_rmsd
from lib.structure.superimpose import fit_to_first, fit_to_mean
from lib.warnings import RelaxWarning, RelaxNoPDBFileWarning, RelaxZeroVectorWarning
from pipe_control import molmol, pipes
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import check_mol_res_spin_data, create_spin, generate_spin_id_unique, linear_ave, return_spin, spin_loop
from pipe_control.pipes import cdp_name, check_pipe, get_pipe
from pipe_control.structure.checks import check_structure
from pipe_control.structure.mass import pipe_centre_of_mass
from status import Status; status = Status()
from target_functions.ens_pivot_finder import Pivot_finder


def add_atom(mol_name=None, atom_name=None, res_name=None, res_num=None, pos=[None, None, None], element=None, atom_num=None, chain_id=None, segment_id=None, pdb_record=None):
    """Add a new atom to the structural data object.

    @keyword mol_name:      The name of the molecule.
    @type mol_name:         str
    @keyword atom_name:     The atom name, e.g. 'H1'.
    @type atom_name:        str or None
    @keyword res_name:      The residue name.
    @type res_name:         str or None
    @keyword res_num:       The residue number.
    @type res_num:          int or None
    @keyword pos:           The position vector of coordinates.  If a rank-2 array is supplied, the length of the first dimension must match the number of models.
    @type pos:              rank-1 or rank-2 array or list of float
    @keyword element:       The element symbol.
    @type element:          str or None
    @keyword atom_num:      The atom number.
    @type atom_num:         int or None
    @keyword chain_id:      The chain identifier.
    @type chain_id:         str or None
    @keyword segment_id:    The segment identifier.
    @type segment_id:       str or None
    @keyword pdb_record:    The optional PDB record name, e.g. 'ATOM' or 'HETATM'.
    @type pdb_record:       str or None
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Place the structural object into the relax data store if needed.
    if not hasattr(cdp, 'structure'):
        cdp.structure = Internal()

    # Add the atoms.
    cdp.structure.add_atom(mol_name=mol_name, atom_name=atom_name, res_name=res_name, res_num=res_num, pos=pos, element=element, atom_num=atom_num, chain_id=chain_id, segment_id=segment_id, pdb_record=pdb_record, sort=True)


def add_helix(start=None, end=None, mol_name=None):
    """Define alpha helical secondary structure for the structural data object.

    @keyword start:     The residue number for the start of the helix.
    @type start:        int
    @keyword end:       The residue number for the end of the helix.
    @type end:          int
    @keyword mol_name:  Define the secondary structure for a specific molecule.
    @type mol_name:     str or None
    """

    # Checks.
    check_pipe()
    check_structure()

    # Add the atoms.
    cdp.structure.add_helix(res_start=start, res_end=end, mol_name=mol_name)


def add_model(model_num=None):
    """Add a new model to the empty structural data object."""

    # Test if the current data pipe exists.
    check_pipe()

    # Place the structural object into the relax data store if needed.
    if not hasattr(cdp, 'structure'):
        cdp.structure = Internal()

    # Check the structural object is empty.
    if cdp.structure.num_molecules() != 0:
        raise RelaxError("The internal structural object is not empty.")

    # Add a model.
    cdp.structure.structural_data.add_item(model_num=model_num)
    print("Created the empty model number %s." % model_num)


def add_sheet(strand=1, sheet_id='A', strand_count=2, strand_sense=0, start=None, end=None, mol_name=None, current_atom=None, prev_atom=None):
    """Define beta sheet secondary structure for the structural data object.

    @keyword strand:        Strand number which starts at 1 for each strand within a sheet and increases by one.
    @type strand:           int
    @keyword sheet_id:      The sheet identifier.  To match the PDB standard, sheet IDs should range from 'A' to 'Z'.
    @type sheet_id:         str
    @keyword strand_count:  The number of strands in the sheet.
    @type strand_count:     int
    @keyword strand_sense:  Sense of strand with respect to previous strand in the sheet. 0 if first strand, 1 if parallel, -1 if anti-parallel.
    @type strand_sense:     int
    @keyword start:         The residue number for the start of the sheet.
    @type start:            int
    @keyword end:           The residue number for the end of the sheet.
    @type end:              int
    @keyword mol_name:      Define the secondary structure for a specific molecule.
    @type mol_name:         str or None
    @keyword current_atom:  The name of the first atom in the current strand, to link the current back to the previous strand.
    @type current_atom:     str or None
    @keyword prev_atom:     The name of the last atom in the previous strand, to link the current back to the previous strand.
    @type prev_atom:        str or None
    """

    # Checks.
    check_pipe()
    check_structure()

    # Add the atoms.
    cdp.structure.add_sheet(strand=strand, sheet_id=sheet_id, strand_count=strand_count, strand_sense=strand_sense, res_start=start, res_end=end, mol_name=mol_name, current_atom=current_atom, prev_atom=prev_atom)


def assemble_structural_coordinates(pipes=None, models=None, molecules=None, atom_id=None, lists=False):
    """Assemble the common atomic coordinates taking sequence alignments into account.
 
    @keyword pipes:     The data pipes to assemble the coordinates from.
    @type pipes:        None or list of str
    @keyword models:    The list of models for each data pipe.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:       None or list of lists of int
    @keyword molecules: The list of molecules for each data pipe.  The number of elements must match the pipes argument.
    @type molecules:    None or list of lists of str
    @keyword atom_id:   The molecule, residue, and atom identifier string.  This matches the spin ID string format.
    @type atom_id:      str or None
    @keyword lists:     A flag which if true will cause the object ID list per molecule, the model number list per molecule, and the molecule name list per molecule to also be returned.
    @type lists:        bool
    @return:            The array of atomic coordinates (first dimension is the model and/or molecule, the second are the atoms, and the third are the coordinates); a list of unique IDs for each structural object, model, and molecule; the common list of molecule names; the common list of residue names; the common list of residue numbers; the common list of atom names; the common list of element names.
    @rtype:             numpy rank-3 float64 array, list of str, list of str, list of str, list of int, list of str, list of str
    """

    # Assemble the structural objects.
    objects, object_names, pipes = assemble_structural_objects(pipes=pipes, models=models, molecules=molecules)

    # Assemble the atomic coordinates of all molecules.
    ids, object_id_list, model_list, molecule_list, atom_pos, mol_names, res_names, res_nums, atom_names, elements, one_letter_codes, num_mols = assemble_atomic_coordinates(objects=objects, object_names=object_names, molecules=molecules, models=models, atom_id=atom_id)

    # No data.
    if mol_names == []:
        if atom_id != None:
            raise RelaxError("No structural data matching the atom ID string '%s' can be found." % atom_id)
        else:
            raise RelaxError("No structural data can be found.")

    # Are all molecules the same?
    same_mol = True
    for mol in molecule_list:
        if mol != molecule_list[0]:
            same_mol = False

    # Handle sequence alignments - retrieve the alignment.
    align = None
    if hasattr(ds, 'sequence_alignments'):
        align = ds.sequence_alignments.find_alignment(object_ids=object_id_list, models=model_list, molecules=molecule_list, sequences=one_letter_codes)
    if align != None:
        # Printout.
        print("\nSequence alignment found - common atoms will be determined based on this MSA:")
        for i in range(len(align.object_ids)):
            print(align.strings[i])

        # Alias the required data structures.
        strings = align.strings
        gaps = align.gaps

    # Handle sequence alignments - no alignment required.
    elif len(objects) == 1 and same_mol:
        # Printout.
        print("\nSequence alignment disabled as only models with identical molecule, residue and atomic sequences are being superimposed.")

        # Set the one letter codes to be the alignment strings.
        strings = one_letter_codes

        # Create an empty gap data structure.
        gaps = []
        for mol_index in range(num_mols):
            gaps.append([])
            for i in range(len(one_letter_codes[mol_index])):
                gaps[mol_index].append(0)

    # Handle sequence alignments - fall back alignment based on residue numbering.
    else:
        # Printout.
        print("\nSequence alignment cannot be found - falling back to a residue number based alignment.")

        # Convert the residue number data structure.
        res_num_list = []
        for mol_index in range(num_mols):
            res_num_list.append([])
            for i in range(len(one_letter_codes[mol_index])):
                key = list(res_nums[mol_index][i].keys())[0]
                res_num_list[mol_index].append(res_nums[mol_index][i][key])

        # Sequence alignment.
        strings, gaps = msa_residue_numbers(one_letter_codes, residue_numbers=res_num_list)

    # Create the residue skipping data structure. 
    skip = msa_residue_skipping(strings=strings, gaps=gaps)

    # Assemble and return the atomic coordinates and common atom information.
    coord, mol_name_common, res_name_common, res_num_common, atom_name_common, element_common = assemble_coord_array(atom_pos=atom_pos, mol_names=mol_names, res_names=res_names, res_nums=res_nums, atom_names=atom_names, elements=elements, sequences=one_letter_codes, skip=skip)
    if lists:
        return coord, ids, object_id_list, model_list, molecule_list, mol_name_common, res_name_common, res_num_common, atom_name_common, element_common
    else:
        return coord, ids, mol_name_common, res_name_common, res_num_common, atom_name_common, element_common


def assemble_structural_objects(pipes=None, models=None, molecules=None):
    """Assemble the atomic coordinates.
 
    @keyword pipes:                     The data pipes to assemble the coordinates from.
    @type pipes:                        None or list of str
    @keyword models:                    The list of models for each data pipe.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:                       None or list of lists of int
    @keyword molecules:                 The list of molecules for each data pipe.  The number of elements must match the pipes argument.
    @type molecules:                    None or list of lists of str
    @return:                            The structural objects, structural object names, and data pipes list.
    @rtype:                             list of lib.structure.internal.object.Internal instances, list of str, list of str
    """

    # The data pipes to use.
    if pipes == None:
        pipes = [cdp_name()]
    num_pipes = len(pipes)

    # Checks.
    for pipe in pipes:
        check_pipe(pipe)

    # Check the models and molecules arguments.
    if models != None:
        if len(models) != num_pipes:
            raise RelaxError("The %i elements of the models argument does not match the %i data pipes." % (len(models), num_pipes))
    if molecules != None:
        if len(molecules) != num_pipes:
            raise RelaxError("The %i elements of the molecules argument does not match the %i data pipes." % (len(molecules), num_pipes))

    # Assemble the structural objects.
    objects = []
    object_names = []
    for pipe_index in range(len(pipes)):
        dp = get_pipe(pipes[pipe_index])
        objects.append(dp.structure)
        object_names.append(pipes[pipe_index])

    # Return the structural objects, object names, and the new pipes list.
    return objects, object_names, pipes


def atomic_fluctuations(pipes=None, models=None, molecules=None, atom_id=None, measure='distance', file=None, format='text', dir=None, force=False):
    """Write out a correlation matrix of pairwise interatomic distance fluctuations between different structures.

    @keyword pipes:     The data pipes to generate the interatomic distance fluctuation correlation matrix for.
    @type pipes:        None or list of str
    @keyword models:    The list of models to generate the interatomic distance fluctuation correlation matrix for.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:       None or list of lists of int
    @keyword molecules: The list of molecules to generate the interatomic distance fluctuation correlation matrix for.  The number of elements must match the pipes argument.
    @type molecules:    None or list of lists of str
    @keyword atom_id:   The atom identification string of the coordinates of interest.  This matches the spin ID string format.
    @type atom_id:      str or None
    @keyword measure:   The type of fluctuation to measure.  This can be either 'distance' or 'angle'.
    @type measure:      str
    @keyword file:      The name of the file to write.
    @type file:         str
    @keyword format:    The output format.  This can be set to "text" for text file output, or "gnuplot" for creating a gnuplot script.
    @type format:       str
    @keyword dir:       The directory where the file will be placed.  If set to None, then the file will be placed in the current directory.
    @type dir:          str or None
    @keyword force:     The force flag which if True will cause the file to be overwritten.
    @type force:        bool
    """

    # Checks.
    check_pipe()
    check_structure()
    allowed_measures = ['distance', 'angle', 'parallax shift']
    if measure not in allowed_measures:
        raise RelaxError("The measure '%s' must be one of %s." % (measure, allowed_measures))

    # Assemble the structural coordinates.
    coord, ids, mol_names, res_names, res_nums, atom_names, elements = assemble_structural_coordinates(pipes=pipes, models=models, molecules=molecules, atom_id=atom_id)

    # The number of dimensions.
    n = len(atom_names)
    m = len(coord)

    # Check that more than one structure is present.
    if not m > 1:
        raise RelaxError("Two or more structures are required.")

    # The labels as spin ID strings.
    labels = []
    for i in range(n):
        labels.append(generate_spin_id_unique(mol_name=mol_names[i], res_num=res_nums[i], res_name=res_names[i], spin_name=atom_names[i]))

    # Initialise the SD matrix and other structures.
    matrix = zeros((n, n), float64)
    dist = zeros(m, float64)
    vectors = zeros((m, 3), float64)
    parallax_vectors = zeros((m, 3), float64)
    angles = zeros(m, float64)

    # Generate the pairwise distance SD matrix.
    if measure == 'distance':
        for i in range(n):
            for j in range(n):
                # Only calculate the upper triangle to avoid duplicate calculations.
                if j > i:
                    continue

                # The interatomic distances between each structure.
                for k in range(m):
                    dist[k] = norm(coord[k, i] - coord[k, j])

                # Calculate and store the corrected sample standard deviation.
                matrix[i, j] = matrix[j, i] = std(dist, ddof=1)

    # Generate the pairwise angle SD matrix.
    elif measure == 'angle':
        # Loop over the atom pairs.
        for i in range(n):
            for j in range(n):
                # Only calculate the upper triangle to avoid duplicate calculations.
                if j > i:
                    continue

                # The interatomic vectors between each structure.
                for k in range(m):
                    vectors[k] = coord[k, i] - coord[k, j]

                # The average vector.
                ave_vect = average(vectors, axis=0)

                # The intervector angles.
                for k in range(m):
                    angles[k] = vector_angle_atan2(ave_vect, vectors[k])

                # Calculate and store the corrected sample standard deviation.
                matrix[i, j] = matrix[j, i] = std(angles, ddof=1)

    # Generate the pairwise parallax shift SD matrix.
    elif measure == 'parallax shift':
        # Loop over the atom pairs.
        for i in range(n):
            for j in range(n):
                # Only calculate the upper triangle to avoid duplicate calculations.
                if j > i:
                    continue

                # The interatomic vectors between each structure.
                for k in range(m):
                    vectors[k] = coord[k, i] - coord[k, j]

                # The average vector.
                ave_vect = average(vectors, axis=0)

                # Catch the zero vector.
                length = norm(ave_vect)
                if length == 0.0:
                    matrix[i, j] = matrix[j, i] = 0.0
                    continue

                # The unit average vector.
                unit = ave_vect / length

                # The parallax shift.
                for k in range(m):
                    # The projection onto the average vector.
                    proj = dot(vectors[k], unit) * unit

                    # The distance shift.
                    dist[k] = norm(vectors[k] - proj)

                # Calculate and store the corrected sample standard deviation.
                matrix[i, j] = matrix[j, i] = std(dist, ddof=1)

    # Call the plotting API.
    correlation_matrix(format=format, matrix=matrix, labels=labels, file=file, dir=dir, force=force)


def average_structure(pipes=None, models=None, molecules=None, atom_id=None, set_mol_name=None, set_model_num=None):
    """Calculate a mean structure.

    @keyword pipes:         The data pipes containing structures to average.
    @type pipes:            None or list of str
    @keyword models:        The list of models for each data pipe.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:           None or list of lists of int
    @keyword molecules:     The list of molecules for each data pipe.  The number of elements must match the pipes argument.
    @type molecules:        None or list of lists of str
    @keyword atom_id:       The molecule, residue, and atom identifier string.  This matches the spin ID string format.
    @type atom_id:          str or None
    @keyword set_mol_name:  The molecule name for the averaged molecule.
    @type set_mol_name:     None or str
    @keyword set_model_num: The model number for the averaged molecule.
    @type set_model_num:    None or int
    """

    # Checks.
    check_pipe()

    # Assemble the structural coordinates.
    coord, ids, mol_names, res_names, res_nums, atom_names, elements = assemble_structural_coordinates(pipes=pipes, models=models, molecules=molecules, atom_id=atom_id)

    # Calculate the mean structure.
    struct = mean(coord, axis=0)

    # Place the structural object into the relax data store if needed.
    if not hasattr(cdp, 'structure'):
        cdp.structure = Internal()

    # Store the data.
    cdp.structure.add_coordinates(coord=struct, mol_names=mol_names, res_names=res_names, res_nums=res_nums, atom_names=atom_names, elements=elements, set_mol_name=set_mol_name, set_model_num=set_model_num)


def connect_atom(index1=None, index2=None):
    """Connect two atoms.

    @keyword index1:    The global index of the first atom.
    @type index1:       str
    @keyword index2:    The global index of the first atom.
    @type index2:       str
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Place the structural object into the relax data store if needed.
    if not hasattr(cdp, 'structure'):
        cdp.structure = Internal()

    # Add the atoms.
    cdp.structure.connect_atom(index1=index1, index2=index2)


def com(model=None, atom_id=None):
    """Calculate the centre of mass (CoM) of all structures.

    The value will be stored in the current data pipe 'com' variable.


    @keyword model:     Only use a specific model.
    @type model:        int or None
    @keyword atom_id:   The molecule, residue, and atom identifier string.  This matches the spin ID string format.  If not given, then all structural data will be used for calculating the CoM.
    @type atom_id:      str or None
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Calculate and store the centre of mass.
    cdp.com = pipe_centre_of_mass(model=model, atom_id=atom_id)


def create_diff_tensor_pdb(scale=1.8e-6, file=None, dir=None, force=False):
    """Create the PDB representation of the diffusion tensor.

    @keyword scale: The scaling factor for the diffusion tensor.
    @type scale:    float
    @keyword file:  The name of the PDB file to create.
    @type file:     str
    @keyword dir:   The name of the directory to place the PDB file into.
    @type dir:      str
    @keyword force: Flag which if set to True will overwrite any pre-existing file.
    @type force:    bool
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Calculate the centre of mass.
    if hasattr(cdp, 'structure') and not cdp.structure.empty():
        com = pipe_centre_of_mass()
    else:
        com = zeros(3, float64)

    # Create the structural object.
    structure = Internal()

    # Create an array of data pipes to loop over (hybrid support).
    if cdp.pipe_type == 'hybrid':
        pipe_list = cdp.hybrid_pipes
    else:
        pipe_list = [pipes.cdp_name()]

    # The molecule names.
    if cdp.pipe_type == 'hybrid':
        mol_names = []
        for pipe in pipe_list:
            mol_names.append('diff_tensor_' % pipe)
    else:
        mol_names = ['diff_tensor']

    # Loop over the pipes.
    for pipe_index in range(len(pipe_list)):
        # Get the pipe container.
        pipe = pipes.get_pipe(pipe_list[pipe_index])

        # Test if the diffusion tensor data is loaded.
        if not hasattr(pipe, 'diff_tensor'):
            raise RelaxNoTensorError('diffusion')

        # Add a new structure.
        structure.add_molecule(name=mol_names[pipe_index])

        # Alias the single molecule from the single model.
        mol = structure.get_molecule(mol_names[pipe_index])

        # The diffusion tensor type.
        diff_type = pipe.diff_tensor.type
        if diff_type == 'spheroid':
            diff_type = pipe.diff_tensor.spheroid_type

        # Simulation info.
        sim_num = None
        if hasattr(pipe.diff_tensor, 'tm_sim'):
            # The number.
            sim_num = len(pipe.diff_tensor.tm_sim)

        # Tensor axes.
        axes = []
        sim_axes = []
        if diff_type in ['oblate', 'prolate']:
            axes.append(pipe.diff_tensor.Dpar * pipe.diff_tensor.Dpar_unit)
            sim_axes.append([])
            if sim_num != None:
                for i in range(sim_num):
                    sim_axes[0].append(pipe.diff_tensor.Dpar_sim[i] * pipe.diff_tensor.Dpar_unit_sim[i])

        if diff_type == 'ellipsoid':
            axes.append(pipe.diff_tensor.Dx * pipe.diff_tensor.Dx_unit)
            axes.append(pipe.diff_tensor.Dy * pipe.diff_tensor.Dy_unit)
            axes.append(pipe.diff_tensor.Dz * pipe.diff_tensor.Dz_unit)
            sim_axes.append([])
            sim_axes.append([])
            sim_axes.append([])
            if sim_num != None:
                for i in range(sim_num):
                    sim_axes[0].append(pipe.diff_tensor.Dx_sim[i] * pipe.diff_tensor.Dx_unit_sim[i])
                    sim_axes[1].append(pipe.diff_tensor.Dy_sim[i] * pipe.diff_tensor.Dy_unit_sim[i])
                    sim_axes[2].append(pipe.diff_tensor.Dz_sim[i] * pipe.diff_tensor.Dz_unit_sim[i])

        # Create the object.
        diffusion_tensor(mol=mol, tensor=pipe.diff_tensor.tensor, tensor_diag=pipe.diff_tensor.tensor_diag, diff_type=diff_type, rotation=pipe.diff_tensor.rotation, axes=axes, sim_axes=sim_axes, com=com, scale=scale)


    # Create the PDB file.
    ######################

    # Print out.
    print("\nGenerating the PDB file.")

    # Create the PDB file.
    tensor_pdb_file = open_write_file(file, dir, force=force)
    structure.write_pdb(tensor_pdb_file)
    tensor_pdb_file.close()

    # Add the file to the results file list.
    if not hasattr(cdp, 'result_files'):
        cdp.result_files = []
    if dir == None:
        dir = getcwd()
    cdp.result_files.append(['diff_tensor_pdb', 'Diffusion tensor PDB', get_file_path(file, dir)])
    status.observers.result_file.notify()


def delete(atom_id=None, model=None, verbosity=1, spin_info=True):
    """Delete structural data.
    
    @keyword atom_id:   The molecule, residue, and atom identifier string.  This matches the spin ID string format.  If not given, then all structural data will be deleted.
    @type atom_id:      str or None
    @keyword model:     Individual structural models from a loaded ensemble can be deleted by specifying the model number.
    @type model:        None or int
    @keyword verbosity: The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1.
    @type verbosity:    int
    @keyword spin_info: A flag which if True will cause all structural information in the spin containers and interatomic data containers to be deleted as well.  If False, then only the 3D structural data will be deleted.
    @type spin_info:    bool
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Run the object method.
    if hasattr(cdp, 'structure'):
        if verbosity:
            print("Deleting structural data from the current pipe.")
        selection = None
        if atom_id != None:
            selection = cdp.structure.selection(atom_id=atom_id)
        cdp.structure.delete(model=model, selection=selection, verbosity=verbosity)
    elif verbosity:
        print("No structures are present.")

    # Skip the rest.
    if not spin_info:
        return

    # Then remove any spin specific structural info.
    if verbosity:
        print("Deleting all spin specific structural info.")
    for spin in spin_loop(selection=atom_id):
        # Delete positional information.
        if hasattr(spin, 'pos'):
            del spin.pos

    # Then remove any interatomic vector structural info.
    if verbosity:
        print("Deleting all interatomic vectors.")
    for interatom in interatomic_loop(selection1=atom_id):
        # Delete bond vectors.
        if hasattr(interatom, 'vector'):
            del interatom.vector


def delete_ss(verbosity=1):
    """Delete all secondary structure information.

    @keyword verbosity: The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1.
    @type verbosity:    int
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Run the object method.
    if hasattr(cdp, 'structure'):
        if verbosity:
            print("Deleting secondary structure information from the current pipe.")
        cdp.structure.delete_ss(verbosity=verbosity)
    elif verbosity:
        print("No structures are present.")



def displacement(pipes=None, models=None, molecules=None, atom_id=None, centroid=None):
    """Calculate the rotational and translational displacement between structures or models.

    All results will be placed into the current data pipe cdp.structure.displacements data structure.


    @keyword pipes:     The data pipes to determine the displacements for.
    @type pipes:        None or list of str
    @keyword models:    The list of models to determine the displacements for.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:       None or list of lists of int
    @keyword molecules: The list of molecules to determine the displacements for.  The number of elements must match the pipes argument.
    @type molecules:    None or list of lists of str
    @keyword atom_id:   The atom identification string of the coordinates of interest.  This matches the spin ID string format.
    @type atom_id:      str or None
    @keyword centroid:  An alternative position of the centroid, used for studying pivoted systems.
    @type centroid:     list of float or numpy rank-1, 3D array
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Assemble the structural coordinates.
    coord, ids, mol_names, res_names, res_nums, atom_names, elements = assemble_structural_coordinates(pipes=pipes, models=models, molecules=molecules, atom_id=atom_id)

    # Initialise the data structure.
    if not hasattr(cdp.structure, 'displacments'):
        cdp.structure.displacements = Displacements()

    # Double loop over all structures, sending the data to the base container for the calculations.
    for i in range(len(ids)):
        for j in range(len(ids)):
            cdp.structure.displacements._calculate(id_from=ids[i], id_to=ids[j], coord_from=coord[i], coord_to=coord[j], centroid=centroid)


def find_pivot(pipes=None, models=None, molecules=None, atom_id=None, init_pos=None, func_tol=1e-5, box_limit=200):
    """Find the pivoted motion of a set of structural models or structures.

    The pivot will be placed into the current data pipe cdp.structure.pivot data structure.


    @keyword pipes:     The data pipes to use in the motional pivot algorithm.
    @type pipes:        None or list of str
    @keyword models:    The list of models to use.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:       None or list of lists of int
    @keyword molecules: The list of molecules to find the pivoted motion for.  The number of elements must match the pipes argument.
    @type molecules:    None or list of lists of str
    @keyword atom_id:   The molecule, residue, and atom identifier string.  This matches the spin ID string format.
    @type atom_id:      str or None
    @keyword init_pos:  The starting pivot position for the pivot point optimisation.
    @type init_pos:     list of float or numpy rank-1, 3D array
    @keyword func_tol:  The function tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
    @type func_tol:     None or float
    @keyword box_limit: The simplex optimisation used in this function is constrained withing a box of +/- x Angstrom containing the pivot point using the logarithmic barrier function.  This argument is the value of x.
    @type box_limit:    int
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Initialised the starting position if needed.
    if init_pos == None:
        init_pos = zeros(3, float64)
    init_pos = array(init_pos)

    # Assemble the structural coordinates.
    coord, ids, mol_names, res_names, res_nums, atom_names, elements = assemble_structural_coordinates(pipes=pipes, models=models, molecules=molecules, atom_id=atom_id)

    # Linear constraints for the pivot position (between -1000 and 1000 Angstrom).
    A = zeros((6, 3), float64)
    b = zeros(6, float64)
    for i in range(3):
        A[2*i, i] = 1
        A[2*i+1, i] = -1
        b[2*i] = -box_limit
        b[2*i+1] = -box_limit

    # The target function.
    finder = Pivot_finder(list(range(len(coord))), coord)
    results = generic_minimise(func=finder.func, x0=init_pos, min_algor='Log barrier', min_options=('simplex',), A=A, b=b, func_tol=func_tol, print_flag=1)

    # No result.
    if results is None:
        return

    # Store the data.
    cdp.structure.pivot = results

    # Print out.
    print("Motional pivot found at:  %s" % results)


def get_pos(spin_id=None, str_id=None, ave_pos=False):
    """Load the spins from the structural object into the relax data store.

    @keyword spin_id:           The molecule, residue, and spin identifier string.
    @type spin_id:              str
    @keyword str_id:            The structure identifier.  This can be the file name, model number, or structure number.
    @type str_id:               int or str
    @keyword ave_pos:           A flag specifying if the average atom position or the atom position from all loaded structures is loaded into the SpinContainer.
    @type ave_pos:              bool
    """

    # Checks.
    check_pipe()
    check_structure()

    # The selection object.
    selection = cdp.structure.selection(atom_id=spin_id)

    # Loop over all atoms of the spin_id selection.
    data = []
    for mol_name, res_num, res_name, atom_num, atom_name, element, pos in cdp.structure.atom_loop(selection=selection, str_id=str_id, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True, ave=ave_pos):
        # Remove the '+' regular expression character from the mol, res, and spin names!
        if mol_name and search(r'\+', mol_name):
            mol_name = mol_name.replace('+', '')
        if res_name and search(r'\+', res_name):
            res_name = res_name.replace('+', '')
        if atom_name and search(r'\+', atom_name):
            atom_name = atom_name.replace('+', '')

        # The spin identification string.
        id = generate_spin_id_unique(res_num=res_num, res_name=None, spin_num=atom_num, spin_name=atom_name)

        # Get the spin container.
        spin_cont = return_spin(spin_id=id)

        # Skip the spin if it doesn't exist.
        if spin_cont == None:
            continue

        # Add the position vector to the spin container.
        spin_cont.pos = pos

        # Store the data for a printout at the end.
        data.append([id, repr(pos)])

    # No positions found.
    if not len(data):
        raise RelaxError("No positional information matching the spin ID '%s' could be found." % spin_id)

    # Update pseudo-atoms.
    for spin in spin_loop():
        if hasattr(spin, 'members'):
            # Get the spin positions.
            positions = []
            for atom in spin.members:
                # Get the spin container.
                subspin = return_spin(spin_id=atom)

                # Test that the spin exists.
                if subspin == None:
                    raise RelaxNoSpinError(atom)

                # Test the position.
                if not hasattr(subspin, 'pos') or subspin.pos is None or not len(subspin.pos):
                    raise RelaxError("Positional information is not available for the atom '%s'." % atom)

                # Alias the position.
                pos = subspin.pos

                # Convert to a list of lists if not already.
                multi_model = True
                if type(pos[0]) in [float, float64]:
                    multi_model = False
                    pos = [pos]

                # Store the position.
                positions.append([])
                for i in range(len(pos)):
                    positions[-1].append(pos[i].tolist())

            # The averaging.
            if spin.averaging == 'linear':
                # Average pos.
                ave = linear_ave(positions)

                # Convert to the correct structure.
                if multi_model:
                    spin.pos = ave
                else:
                    spin.pos = ave[0]

    # Print out.
    write_data(out=sys.stdout, headings=["Spin_ID", "Position"], data=data)


def load_spins(spin_id=None, str_id=None, from_mols=None, mol_name_target=None, ave_pos=False, spin_num=True):
    """Load the spins from the structural object into the relax data store.

    @keyword spin_id:           The molecule, residue, and spin identifier string.
    @type spin_id:              str
    @keyword str_id:            The structure identifier.  This can be the file name, model number, or structure number.
    @type str_id:               int or str
    @keyword from_mols:         The list of similar, but not necessarily identical molecules to load spin information from.
    @type from_mols:            list of str or None
    @keyword mol_name_target:   The name of target molecule container, overriding the name of the loaded structures
    @type mol_name_target:      str or None
    @keyword ave_pos:           A flag specifying if the average atom position or the atom position from all loaded structures is loaded into the SpinContainer.
    @type ave_pos:              bool
    @keyword spin_num:          A flag specifying if the spin number should be loaded.
    @type spin_num:             bool
    """

    # The multi-molecule case.
    if from_mols != None:
        load_spins_multi_mol(spin_id=spin_id, str_id=str_id, from_mols=from_mols, mol_name_target=mol_name_target, ave_pos=ave_pos, spin_num=spin_num)
        return

    # Checks.
    check_pipe()
    check_structure()

    # Print out.
    print("Adding the following spins to the relax data store.\n")

    # Init the data for printing out.
    mol_names = []
    res_nums = []
    res_names = []
    spin_nums = []
    spin_names = []

    # Loop over all atoms of the spin_id selection.
    selection = cdp.structure.selection(atom_id=spin_id)
    for mol_name, res_num, res_name, atom_num, atom_name, element, pos in cdp.structure.atom_loop(selection=selection, str_id=str_id, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True, ave=ave_pos):
        # Override the molecule name.
        if mol_name_target:
            mol_name = mol_name_target

        # No spin number.
        if not spin_num:
            atom_num = None

        # Remove the '+' regular expression character from the mol, res, and spin names!
        if mol_name and search(r'\+', mol_name):
            mol_name = mol_name.replace('+', '')
        if res_name and search(r'\+', res_name):
            res_name = res_name.replace('+', '')
        if atom_name and search(r'\+', atom_name):
            atom_name = atom_name.replace('+', '')

        # Generate a spin ID for the current atom.
        id = generate_spin_id_unique(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=atom_num, spin_name=atom_name)

        # Create the spin.
        try:
            spin_cont = create_spin(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=atom_num, spin_name=atom_name)[0]

        # Otherwise, get the spin container.
        except RelaxError:
            spin_cont = return_spin(spin_id=id)

        # Append all the spin ID info for printing later.
        if mol_name_target:
            mol_names.append(mol_name_target)
        else:
            mol_names.append(mol_name)
        res_nums.append(res_num)
        res_names.append(res_name)
        spin_nums.append(atom_num)
        spin_names.append(atom_name)

        # Position vector.
        if hasattr(spin_cont, 'pos') and spin_cont.pos is not None and (spin_cont.pos.shape != pos.shape or (spin_cont.pos != pos).any()):
            warn(RelaxWarning("Positional information already exists for the spin %s, appending the new positions." % id))
            spin_cont.pos = concatenate((spin_cont.pos, pos))
        else:
            spin_cont.pos = pos

        # Add the element.
        spin_cont.element = element

    # Catch no data.
    if len(mol_names) == 0:
        warn(RelaxWarning("No spins matching the '%s' ID string could be found." % spin_id))
        return

    # Print out.
    write_spin_data(file=sys.stdout, mol_names=mol_names, res_nums=res_nums, res_names=res_names, spin_nums=spin_nums, spin_names=spin_names)

    # Set the number of states for use in the specific analyses.
    cdp.N = cdp.structure.num_models()


def load_spins_multi_mol(spin_id=None, str_id=None, from_mols=None, mol_name_target=None, ave_pos=False, spin_num=True):
    """Load the spins from the structural object into the relax data store.

    @keyword spin_id:           The molecule, residue, and spin identifier string.
    @type spin_id:              str
    @keyword str_id:            The structure identifier.  This can be the file name, model number, or structure number.
    @type str_id:               int or str
    @keyword from_mols:         The list of similar, but not necessarily identical molecules to load spin information from.
    @type from_mols:            list of str or None
    @keyword mol_name_target:   The name of target molecule container, overriding the name of the loaded structures
    @type mol_name_target:      str or None
    @keyword ave_pos:           A flag specifying if the average atom position or the atom position from all loaded structures is loaded into the SpinContainer.
    @type ave_pos:              bool
    @keyword spin_num:          A flag specifying if the spin number should be loaded.
    @type spin_num:             bool
    """

    # Checks.
    check_pipe()
    check_structure()

    # The target molecule name must be supplied.
    if mol_name_target == None:
        raise RelaxError("The target molecule name must be supplied when specifying multiple molecules to load spins from.")

    # Disallow multiple structural models.
    if cdp.structure.num_models() != 1:
        raise RelaxError("Only a single structural model is allowed when specifying multiple molecules to load spins from.")

    # Split up the selection string.
    if spin_id:
        mol_token, res_token, spin_token = tokenise(spin_id)
        if mol_token != None:
            raise RelaxError("The spin ID string cannot contain molecular information when specifying multiple molecules to load spins from.")

    # Print out.
    print("Adding the following spins to the relax data store.\n")

    # Initialise the data structures.
    ids = []
    res_nums = {}
    res_names = {}
    spin_names = {}
    positions = {}
    elements = {}

    # Loop over all target molecules.
    for mol_name in from_mols:
        # Add the molecule name as a key for the positions structure, and initialise as a dictionary for the spin IDs.
        positions[mol_name] = {}

        # Create a new spin ID with the molecule name.
        new_id = '#' + mol_name
        if spin_id != None:
            new_id += spin_id

        # Loop over all atoms of the new spin ID selection.
        selection = cdp.structure.selection(atom_id=new_id)
        for res_num, res_name, atom_num, atom_name, element, pos in cdp.structure.atom_loop(selection=selection, str_id=str_id, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True, ave=ave_pos):
            # Remove the '+' regular expression character from the res and atom names.
            if res_name and search(r'\+', res_name):
                res_name = res_name.replace('+', '')
            if atom_name and search(r'\+', atom_name):
                atom_name = atom_name.replace('+', '')

            # No spin number.
            if not spin_num:
                atom_num = None

            # Generate a spin ID for the current atom.
            id = generate_spin_id_unique(mol_name=mol_name_target, res_num=res_num, res_name=res_name, spin_name=atom_name)

            # Store the position info in all cases, collapsing list of lists into single lists when needed.
            if is_float(pos[0]):
                positions[mol_name][id] = pos
            else:
                positions[mol_name][id] = pos[0]

            # Not a new ID.
            if id in ids:
                continue

            # Store the ID, residue, spin, element and position info.
            ids.append(id)
            res_nums[id] = res_num
            res_names[id] = res_name
            spin_names[id] = atom_name
            elements[id] = element

    # Catch no data.
    if len(ids) == 0:
        warn(RelaxWarning("No spins matching the '%s' ID string could be found." % spin_id))
        return

    # Create the spin containers.
    mol_names2 = []
    res_nums2 = []
    res_names2 = []
    spin_names2 = []
    for id in ids:
        # Fetch the spin.
        spin_cont = return_spin(spin_id=id)

        # Create the spin if it does not exist.
        if spin_cont == None:
            spin_cont = create_spin(mol_name=mol_name_target, res_num=res_nums[id], res_name=res_names[id], spin_name=spin_names[id])[0]

        # Position vector.
        spin_cont.pos = []
        for mol_name in from_mols:
            if id in positions[mol_name]:
                spin_cont.pos.append(positions[mol_name][id])
            else:
                spin_cont.pos.append(None)

        # Add the element.
        spin_cont.element = elements[id]

        # Update the structures for the printout.
        mol_names2.append(mol_name_target)
        res_nums2.append(res_nums[id])
        res_names2.append(res_names[id])
        spin_names2.append(spin_names[id])

    # Print out.
    write_spin_data(file=sys.stdout, mol_names=mol_names2, res_nums=res_nums2, res_names=res_names2, spin_names=spin_names2)

    # Set the number of states for use in the specific analyses.
    cdp.N = len(from_mols)


def pca(pipes=None, models=None, molecules=None, obs_pipes=None, obs_models=None, obs_molecules=None, atom_id=None, algorithm=None, num_modes=4, format='grace', dir=None):
    """PC analysis of the motions between all the loaded models.

    @keyword pipes:         The data pipes to perform the PC analysis on.
    @type pipes:            None or list of str
    @keyword models:        The list of models to perform the PC analysis on.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:           None or list of lists of int
    @keyword molecules:     The list of molecules to perform the PC analysis on.  The number of elements must match the pipes argument.
    @type molecules:        None or list of lists of str
    @keyword obs_pipes:     The data pipes in the PC analysis which will have zero weight.  These structures are for comparison.
    @type obs_pipes:        None or list of str
    @keyword obs_models:    The list of models in the PC analysis which will have zero weight.  These structures are for comparison.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type obs_models:       None or list of lists of int
    @keyword obs_molecules: The list of molecules in the PC analysis which will have zero weight.  These structures are for comparison.  The number of elements must match the pipes argument.
    @type obs_molecules:    None or list of lists of str
    @keyword atom_id:       The atom identification string of the coordinates of interest.  This matches the spin ID string format.
    @type atom_id:          str or None
    @keyword algorithm:     The PCA algorithm to use (either 'eigen' or 'svd').
    @type algorithm:        str
    @keyword num_modes:     The number of PCA modes to calculate.
    @type num_modes:        int
    @keyword format:        The graph format to use.
    @type format:           str
    @keyword dir:           The optional directory to place the graphs into.
    @type dir:              str
    """

    # Checks.
    check_pipe()

    # Assemble the structural coordinates.
    coord, ids, object_id_list, model_list, molecule_list, mol_names, res_names, res_nums, atom_names, elements = assemble_structural_coordinates(pipes=pipes, models=models, molecules=molecules, atom_id=atom_id, lists=True)

    # Determine the structure weights.
    M = len(coord)
    if obs_pipes == None:
        obs_pipes = []
    weights = ones(M, float64)
    for struct in range(M):
        # Is the structure in the 'observing' lists?
        for i in range(len(obs_pipes)):
            # Matching data pipe.
            if object_id_list[struct] == obs_pipes[i]:
                # Matching molecules.
                if obs_molecules == None or molecule_list[struct] == obs_molecules[i]:
                    # Matching models.
                    if obs_models == None or model_list[struct] == obs_models[i]:
                        weights[struct] = 0.0

    # Perform the PC analysis.
    print("\n\nStarting the PCA analysis.\n")
    values, vectors, proj = pca_analysis(coord=coord, weights=weights, algorithm=algorithm, num_modes=num_modes)

    # Store the values.
    cdp.structure.pca_values = values
    cdp.structure.pca_vectors = vectors
    cdp.structure.pca_proj = proj

    # Generate the graphs.
    for mode in range(num_modes - 1):
        # Assemble the data.
        data = [[[]]]
        current = None
        labels = []
        for struct in range(M):
            # Create a unique ID for pipe and molecule name.
            id = "%s - %s" % (object_id_list[struct], molecule_list[struct])
            if current == None:
                current = id
                labels.append(current)

            # Start a new set.
            if current != id:
                data[-1].append([])
                current = id
                labels.append(current)

            # Add the projection.
            data[-1][-1].append([proj[mode, struct], proj[mode+1, struct]])

        # The number of graph sets.
        sets = len(labels)

        # Open the file for writing.
        file = open_write_file("graph_pc%s_pc%s.agr" % (mode+1, mode+2), dir=dir, force=True)

        # The header.
        write_xy_header(format=format, file=file, title="Principle component projections", sets=[sets], set_names=[labels], axis_labels=[[r'PC mode %i (\cE\C)' % (mode+1), r'PC mode %i (\cE\C)' % (mode+2)]], linestyle=[[0]*sets])

        # The data.
        write_xy_data(format=format, data=data, file=file, graph_type='xy')

        # Close the file.
        file.close()


def read_gaussian(file=None, dir=None, set_mol_name=None, set_model_num=None, verbosity=1, fail=True):
    """Read structures from a Gaussian log file.


    @keyword file:          The name of the Gaussian log file to read.
    @type file:             str
    @keyword dir:           The directory where the Gaussian log file is located.  If set to None, then the file will be searched for in the current directory.
    @type dir:              str or None
    @keyword set_mol_name:  Set the names of the molecules which are loaded.  If set to None, then the molecules will be automatically labelled based on the file name or other information.
    @type set_mol_name:     None, str, or list of str
    @keyword set_model_num: Set the model number of the loaded molecule.
    @type set_model_num:    None, int, or list of int
    @keyword fail:          A flag which, if True, will cause a RelaxError to be raised if the Gaussian log  file does not exist.  If False, then a RelaxWarning will be trown instead.
    @type fail:             bool
    @keyword verbosity:     The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1.
    @type verbosity:        int
    @raise RelaxFileError:  If the fail flag is set, then a RelaxError is raised if the Gaussian log file does not exist.
    """

    # Test if the current data pipe exists.
    check_pipe()

    # The file path.
    file_path = get_file_path(file, dir)

    # Try adding '.log' to the end of the file path, if the file can't be found.
    if not access(file_path, F_OK):
        file_path_orig = file_path
        file_path = file_path + '.log'

    # Test if the file exists.
    if not access(file_path, F_OK):
        if fail:
            raise RelaxFileError('Gaussian log', file_path_orig)
        else:
            warn(RelaxNoPDBFileWarning(file_path))
            return

    # Place the  structural object into the relax data store.
    if not hasattr(cdp, 'structure'):
        cdp.structure = Internal()

    # Load the structures.
    cdp.structure.load_gaussian(file_path, set_mol_name=set_mol_name, set_model_num=set_model_num, verbosity=verbosity)


def read_pdb(file=None, dir=None, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None, alt_loc=None, verbosity=1, merge=False, fail=True):
    """The PDB loading function.

    @keyword file:          The name of the PDB file to read.
    @type file:             str
    @keyword dir:           The directory where the PDB file is located.  If set to None, then the file will be searched for in the current directory.
    @type dir:              str or None
    @keyword read_mol:      The molecule(s) to read from the file, independent of model.  The molecules are numbered consecutively from 1.  If set to None, then all molecules will be loaded.
    @type read_mol:         None, int, or list of int
    @keyword set_mol_name:  Set the names of the molecules which are loaded.  If set to None, then the molecules will be automatically labelled based on the file name or other information.
    @type set_mol_name:     None, str, or list of str
    @keyword read_model:    The PDB model to extract from the file.  If set to None, then all models will be loaded.
    @type read_model:       None, int, or list of int
    @keyword set_model_num: Set the model number of the loaded molecule.  If set to None, then the PDB model numbers will be preserved, if they exist.
    @type set_model_num:    None, int, or list of int
    @keyword alt_loc:       The PDB ATOM record 'Alternate location indicator' field value to select which coordinates to use.
    @type alt_loc:          str or None
    @keyword verbosity:     The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1.
    @type verbosity:        int
    @keyword merge:         A flag which if set to True will try to merge the PDB structure into the currently loaded structures.
    @type merge:            bool
    @keyword fail:          A flag which, if True, will cause a RelaxError to be raised if the PDB file does not exist.  If False, then a RelaxWarning will be trown instead.
    @type fail:             bool
    @raise RelaxFileError:  If the fail flag is set, then a RelaxError is raised if the PDB file does not exist.
    """

    # Test if the current data pipe exists.
    check_pipe()

    # The file path.
    file_path = get_file_path(file, dir)

    # Try adding file extensions to the end of the file path, if the file can't be found.
    file_path_orig = file_path
    if not access(file_path, F_OK):
        # List of possible extensions.
        for ext in ['.pdb', '.gz', '.pdb.gz', '.bz2', '.pdb.bz2']:
            # Add the extension if the file can be found.
            if access(file_path+ext, F_OK):
                file_path = file_path + ext

    # Test if the file exists.
    if not access(file_path, F_OK):
        if fail:
            raise RelaxFileError('PDB', file_path_orig)
        else:
            warn(RelaxNoPDBFileWarning(file_path))
            return

    # Place the internal structural object into the relax data store.
    if not hasattr(cdp, 'structure'):
        cdp.structure = Internal()

    # Load the structures.
    cdp.structure.load_pdb(file_path, read_mol=read_mol, set_mol_name=set_mol_name, read_model=read_model, set_model_num=set_model_num, alt_loc=alt_loc, verbosity=verbosity, merge=merge)

    # Load into Molmol (if running).
    molmol.molmol_obj.open_pdb()


def read_xyz(file=None, dir=None, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None, verbosity=1, fail=True):
    """The XYZ loading function.


    @keyword file:          The name of the XYZ file to read.
    @type file:             str
    @keyword dir:           The directory where the XYZ file is located.  If set to None, then the
                            file will be searched for in the current directory.
    @type dir:              str or None
    @keyword read_mol:      The molecule(s) to read from the file, independent of model.
                            If set to None, then all molecules will be loaded.
    @type read_mol:         None, int, or list of int
    @keyword set_mol_name:  Set the names of the molecules which are loaded.  If set to None, then
                            the molecules will be automatically labelled based on the file name or
                            other information.
    @type set_mol_name:     None, str, or list of str
    @keyword read_model:    The XYZ model to extract from the file.  If set to None, then all models
                            will be loaded.
    @type read_model:       None, int, or list of int
    @keyword set_model_num: Set the model number of the loaded molecule.  If set to None, then the
                            XYZ model numbers will be preserved, if they exist.
    @type set_model_num:    None, int, or list of int
    @keyword fail:          A flag which, if True, will cause a RelaxError to be raised if the XYZ 
                            file does not exist.  If False, then a RelaxWarning will be trown
                            instead.
    @type fail:             bool
    @keyword verbosity:     The amount of information to print to screen.  Zero corresponds to
                            minimal output while higher values increase the amount of output.  The
                            default value is 1.
    @type verbosity:        int
    @raise RelaxFileError:  If the fail flag is set, then a RelaxError is raised if the XYZ file
                            does not exist.
    """

    # Test if the current data pipe exists.
    check_pipe()

    # The file path.
    file_path = get_file_path(file, dir)

    # Try adding '.xyz' to the end of the file path, if the file can't be found.
    if not access(file_path, F_OK):
        file_path_orig = file_path
        file_path = file_path + '.xyz'

    # Test if the file exists.
    if not access(file_path, F_OK):
        if fail:
            raise RelaxFileError('XYZ', file_path_orig)
        else:
            warn(RelaxNoPDBFileWarning(file_path))
            return

    # Place the  structural object into the relax data store.
    if not hasattr(cdp, 'structure'):
        cdp.structure = Internal()

    # Load the structures.
    cdp.structure.load_xyz(file_path, read_mol=read_mol, set_mol_name=set_mol_name, read_model=read_model, set_model_num=set_model_num, verbosity=verbosity)


def rmsd(pipes=None, models=None, molecules=None, atom_id=None, atomic=False):
    """Calculate the RMSD between the loaded models.

    The RMSD value will be placed into the current data pipe cdp.structure.rmsd data structure.


    @keyword pipes:     The data pipes to determine the RMSD for.
    @type pipes:        None or list of str
    @keyword models:    The list of models to determine the RMSD for.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:       None or list of lists of int
    @keyword molecules: The list of molecules to determine the RMSD for.  The number of elements must match the pipes argument.
    @type molecules:    None or list of lists of str
    @keyword atom_id:   The atom identification string of the coordinates of interest.  This matches the spin ID string format.
    @type atom_id:      str or None
    @keyword atomic:    A flag which if True will allow for per-atom RMSDs to be additionally calculated.
    @type atomic:       bool
    @return:            The RMSD value.
    @rtype:             float
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Assemble the structural coordinates.
    coord, ids, mol_names, res_names, res_nums, atom_names, elements = assemble_structural_coordinates(pipes=pipes, models=models, molecules=molecules, atom_id=atom_id)

    # Per-atom RMSDs.
    if atomic:
        # Printout.
        print("\nCalculating the atomic-level RMSDs.")

        # Calculate the per-atom RMSDs.
        rmsd = per_atom_rmsd(coord, verbosity=0)

        # Loop over the atoms.
        for i in range(len(res_nums)):
            # The spin identification string.
            id = generate_spin_id_unique(mol_name=mol_names[i], res_num=res_nums[i], res_name=res_names[i], spin_num=i, spin_name=atom_names[i])

            # Get the spin container.
            spin_cont = return_spin(spin_id=id)

            # Skip the spin if it doesn't exist.
            if spin_cont == None:
                continue

            # Store the value.
            spin_cont.pos_rmsd = rmsd[i]

    # Calculate the RMSD.
    print("\nCalculating the global RMSD.")
    cdp.structure.rmsd = atomic_rmsd(coord, verbosity=1)

    # Return the global RMSD.
    return cdp.structure.rmsd


def rotate(R=None, origin=None, model=None, atom_id=None, pipe_name=None):
    """Rotate the structural data about the origin by the specified forwards rotation.

    @keyword R:         The forwards rotation matrix.
    @type R:            numpy 3D, rank-2 array or a 3x3 list of floats
    @keyword origin:    The origin of the rotation.  If not supplied, the origin will be set to [0, 0, 0].
    @type origin:       numpy 3D, rank-1 array or list of len 3 or None
    @keyword model:     The model to rotate.  If None, all models will be rotated.
    @type model:        int
    @keyword atom_id:   The molecule, residue, and atom identifier string.  Only atoms matching this selection will be used.
    @type atom_id:      str or None
    @keyword pipe_name: The name of the data pipe containing the structures to translate.  This defaults to the current data pipe.
    @type pipe_name:    None or str
    """

    # Defaults.
    if pipe_name == None:
        pipe_name = cdp_name()

    # Checks.
    check_pipe(pipe_name)
    check_structure(pipe_name)

    # Get the data pipe.
    dp = get_pipe(pipe_name)

    # Set the origin if not supplied.
    if origin is None:
        origin = [0, 0, 0]

    # Convert the args to numpy float data structures.
    R = array(R, float64)
    origin = array(origin, float64)

    # Call the specific code.
    selection = dp.structure.selection(atom_id=atom_id)
    dp.structure.rotate(R=R, origin=origin, model=model, selection=selection)

    # Final printout.
    if model != None:
        print("Rotated %i atoms of model %i." % (selection.count_atoms(), model))
    else:
        print("Rotated %i atoms." % selection.count_atoms())


def sequence_alignment(pipes=None, models=None, molecules=None, msa_algorithm='Central Star', pairwise_algorithm='NW70', matrix='BLOSUM62', gap_open_penalty=1.0, gap_extend_penalty=1.0, end_gap_open_penalty=0.0, end_gap_extend_penalty=0.0):
    """Superimpose a set of related, but not identical structures.

    @keyword pipes:                     The data pipes to include in the alignment and superimposition.
    @type pipes:                        None or list of str
    @keyword models:                    The list of models to for each data pipe superimpose.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:                       list of lists of int or None
    @keyword molecules:                 The molecule names to include in the alignment and superimposition.  The number of elements must match the pipes argument.
    @type molecules:                    None or list of str
    @keyword msa_algorithm:             The multiple sequence alignment (MSA) algorithm to use.
    @type msa_algorithm:                str
    @keyword pairwise_algorithm:        The pairwise sequence alignment algorithm to use.
    @type pairwise_algorithm:           str
    @keyword matrix:                    The substitution matrix to use.
    @type matrix:                       str
    @keyword gap_open_penalty:          The penalty for introducing gaps, as a positive number.
    @type gap_open_penalty:             float
    @keyword gap_extend_penalty:        The penalty for extending a gap, as a positive number.
    @type gap_extend_penalty:           float
    @keyword end_gap_open_penalty:      The optional penalty for opening a gap at the end of a sequence.
    @type end_gap_open_penalty:         float
    @keyword end_gap_extend_penalty:    The optional penalty for extending a gap at the end of a sequence.
    @type end_gap_extend_penalty:       float
    """

    # Assemble the structural objects.
    objects, object_names, pipes = assemble_structural_objects(pipes=pipes, models=models, molecules=molecules)

    # Assemble the atomic coordinates of all molecules.
    ids, object_id_list, model_list, molecule_list, atom_pos, mol_names, res_names, res_nums, atom_names, elements, one_letter_codes, num_mols = assemble_atomic_coordinates(objects=objects, object_names=object_names, molecules=molecules, models=models)

    # Convert the residue number data structure.
    res_num_list = []
    for mol_index in range(num_mols):
        res_num_list.append([])
        for i in range(len(one_letter_codes[mol_index])):
            key = list(res_nums[mol_index][i].keys())[0]
            res_num_list[mol_index].append(res_nums[mol_index][i][key])

    # MSA.
    strings, gaps = msa_general(one_letter_codes, residue_numbers=res_num_list, msa_algorithm=msa_algorithm, pairwise_algorithm=pairwise_algorithm, matrix=matrix, gap_open_penalty=gap_open_penalty, gap_extend_penalty=gap_extend_penalty, end_gap_open_penalty=end_gap_open_penalty, end_gap_extend_penalty=end_gap_extend_penalty)

    # Set up the data store object.
    if not hasattr(ds, 'sequence_alignments'):
        ds.sequence_alignments = Sequence_alignments()

    # Set some unused arguments to None for storage.
    if msa_algorithm == 'residue number':
        pairwise_algorithm = None
        matrix = None
        gap_open_penalty = None
        gap_extend_penalty = None
        end_gap_open_penalty = None
        end_gap_extend_penalty = None

    # Store the alignment.
    ds.sequence_alignments.add(object_ids=object_id_list, models=model_list, molecules=molecule_list, sequences=one_letter_codes, strings=strings, gaps=gaps, msa_algorithm=msa_algorithm, pairwise_algorithm=pairwise_algorithm, matrix=matrix, gap_open_penalty=gap_open_penalty, gap_extend_penalty=gap_extend_penalty, end_gap_open_penalty=end_gap_open_penalty, end_gap_extend_penalty=end_gap_extend_penalty)


def set_vector(spin=None, xh_vect=None):
    """Place the XH unit vector into the spin container object.

    @keyword spin:      The spin container object.
    @type spin:         SpinContainer instance
    @keyword xh_vect:   The unit vector parallel to the XH bond.
    @type xh_vect:      array of len 3
    """

    # Place the XH unit vector into the container.
    spin.xh_vect = xh_vect


def structure_loop(pipes=None, molecules=None, models=None, atom_id=None):
    """Generator function for looping over all internal structural objects, models and molecules.
 
    @keyword pipes:         The data pipes to loop over.
    @type pipes:            None or list of str
    @keyword models:        The list of models for each data pipe.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:           None or list of lists of int
    @keyword molecules:     The list of molecules for each data pipe.  The number of elements must match the pipes argument.
    @type molecules:        None or list of lists of str
    @keyword atom_id:       The molecule, residue, and atom identifier string of the coordinates of interest.  This matches the spin ID string format.
    @type atom_id:          None or str
    @return:                The data pipe index, model number, and molecule name.
    @rtype:                 int, int or None, str
    """

    # The data pipes to use.
    if pipes == None:
        pipes = [cdp_name()]
    num_pipes = len(pipes)

    # Checks.
    for pipe in pipes:
        check_pipe(pipe)

    # Check the models and molecules arguments.
    if models != None:
        if len(models) != num_pipes:
            raise RelaxError("The %i elements of the models argument does not match the %i data pipes." % (len(models), num_pipes))
    if molecules != None:
        if len(molecules) != num_pipes:
            raise RelaxError("The %i elements of the molecules argument does not match the %i data pipes." % (len(molecules), num_pipes))

    # Assemble the structural objects.
    objects = []
    for pipe_index in range(len(pipes)):
        dp = get_pipe(pipes[pipe_index])
        objects.append(dp.structure)

    # Call the library method to do all of the work.
    for pipe_index, model_num, mol_name in loop_coord_structures(objects=objects, models=models, molecules=molecules, atom_id=atom_id):
        yield pipe_index, model_num, mol_name


def superimpose(pipes=None, models=None, molecules=None, atom_id=None, displace_id=None, method='fit to mean', centre_type="centroid", centroid=None):
    """Superimpose a set of structures.

    @keyword pipes:         The data pipes to include in the alignment and superimposition.
    @type pipes:            None or list of str
    @keyword models:        The list of models to for each data pipe superimpose.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:           list of lists of int or None
    @keyword molecules:     The molecule names to include in the alignment and superimposition.  The number of elements must match the pipes argument.
    @type molecules:        None or list of str
    @keyword atom_id:       The molecule, residue, and atom identifier string.  This matches the spin ID string format.
    @type atom_id:          str or None
    @keyword displace_id:   The atom ID string for restricting the displacement to a subset of all atoms.  If not set, then all atoms will be translated and rotated.  This can be a list of atom IDs with each element corresponding to one of the structures.
    @type displace_id:      None, str, or list of str
    @keyword method:        The superimposition method.  It must be one of 'fit to mean' or 'fit to first'.
    @type method:           str
    @keyword centre_type:   The type of centre to superimpose over.  This can either be the standard centroid superimposition or the CoM could be used instead.
    @type centre_type:      str
    @keyword centroid:      An alternative position of the centroid to allow for different superpositions, for example of pivot point motions.
    @type centroid:         list of float or numpy rank-1, 3D array
    """

    # Check the method.
    allowed = ['fit to mean', 'fit to first']
    if method not in allowed:
        raise RelaxError("The superimposition method '%s' is unknown.  It must be one of %s." % (method, allowed))

    # Check the type.
    allowed = ['centroid', 'CoM']
    if centre_type not in allowed:
        raise RelaxError("The superimposition centre type '%s' is unknown.  It must be one of %s." % (centre_type, allowed))

    # The data pipes to use.
    if pipes == None:
        pipes = [cdp_name()]

    # Assemble the structural coordinates.
    coord, ids, mol_names, res_names, res_nums, atom_names, elements = assemble_structural_coordinates(pipes=pipes, models=models, molecules=molecules, atom_id=atom_id)

    # Catch missing data.
    if len(coord[0]) == 0:
        raise RelaxError("No common atoms could be found between the structures.")

    # The different algorithms.
    if method == 'fit to mean':
        T, R, pivot = fit_to_mean(models=list(range(len(ids))), coord=coord, centre_type=centre_type, elements=elements, centroid=centroid)
    elif method == 'fit to first':
        T, R, pivot = fit_to_first(models=list(range(len(ids))), coord=coord, centre_type=centre_type, elements=elements, centroid=centroid)

    # Loop over all pipes, models, and molecules.
    i = 0
    for pipe_index, model_num, mol_name in structure_loop(pipes=pipes, models=models, molecules=molecules, atom_id=atom_id):
        # Skip the first structure if not moved.
        if i == 0 and method == 'fit to first':
            i += 1
            continue

        # The current displacement ID.
        curr_displace_id = None
        if isinstance(displace_id, str):
            curr_displace_id = displace_id
        elif isinstance(displace_id, list):
            if len(displace_id) <= i:
                raise RelaxError("Not enough displacement ID strings have been provided.")
            curr_displace_id = displace_id[i]

        # Add the molecule name to the displacement ID if required.
        id = curr_displace_id
        if id == None or (mol_name and not search('#', id)):
            if curr_displace_id == None:
                id = '#%s' % mol_name
            elif search('#', curr_displace_id):
                id = curr_displace_id
            else:
                id = '#%s%s' % (mol_name, curr_displace_id)

        # Translate the molecule first (the rotational pivot is defined in the first model).
        translate(T=T[i], model=model_num, pipe_name=pipes[pipe_index], atom_id=id)

        # Rotate the molecule.
        rotate(R=R[i], origin=pivot[i], model=model_num, pipe_name=pipes[pipe_index], atom_id=id)

        # Increment the index.
        i += 1


def translate(T=None, model=None, atom_id=None, pipe_name=None):
    """Shift the structural data by the specified translation vector.

    @keyword T:         The translation vector.
    @type T:            numpy rank-1, 3D array or list of float
    @keyword model:     The model to translate.  If None, all models will be rotated.
    @type model:        int or None
    @keyword atom_id:   The molecule, residue, and atom identifier string.  Only atoms matching this selection will be used.
    @type atom_id:      str or None
    @keyword pipe_name: The name of the data pipe containing the structures to translate.  This defaults to the current data pipe.
    @type pipe_name:    None or str
    """

    # Defaults.
    if pipe_name == None:
        pipe_name = cdp_name()

    # Checks.
    check_pipe(pipe_name)
    check_structure(pipe_name)

    # Get the data pipe.
    dp = get_pipe(pipe_name)

    # Convert the args to numpy float data structures.
    T = array(T, float64)

    # Call the specific code.
    selection = dp.structure.selection(atom_id=atom_id)
    dp.structure.translate(T=T, model=model, selection=selection)

    # Final printout.
    if model != None:
        print("Translated %i atoms of model %i." % (selection.count_atoms(), model))
    else:
        print("Translated %i atoms." % selection.count_atoms())


def vectors(spin_id1=None, spin_id2=None, model=None, verbosity=1, ave=True, unit=True):
    """Extract the bond vectors from the loaded structures and store them in the spin container.

    @keyword spin_id1:      The spin identifier string of the first spin of the pair.
    @type spin_id1:         str
    @keyword spin_id2:      The spin identifier string of the second spin of the pair.
    @type spin_id2:         str
    @keyword model:         The model to extract the vector from.  If None, all vectors will be extracted.
    @type model:            str
    @keyword verbosity:     The higher the value, the more information is printed to screen.
    @type verbosity:        int
    @keyword ave:           A flag which if True will cause the average of all vectors to be extracted.
    @type ave:              bool
    @keyword unit:          A flag which if True will cause the function to calculate the unit vectors.
    @type unit:             bool
    """

    # Checks.
    check_pipe()
    check_structure()
    check_mol_res_spin_data()

    # Print out.
    if verbosity:
        # Number of models.
        num_models = cdp.structure.num_models()

        # Multiple models loaded.
        if num_models > 1:
            if model:
                print("Extracting vectors for model '%s'." % model)
            else:
                print("Extracting vectors for all %s models." % num_models)
                if ave:
                    print("Averaging all vectors.")

        # Single model loaded.
        else:
            print("Extracting vectors from the single model.")

        # Unit vectors.
        if unit:
            print("Calculating the unit vectors.")

    # Loop over the spins.
    no_vectors = True
    for spin, mol_name, res_num, res_name in spin_loop(selection=spin_id, full_info=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # The spin identification string.  The residue name and spin num is not included to allow molecules with point mutations to be used as different models.
        id = generate_spin_id_unique(res_num=res_num, res_name=None, spin_name=spin.name, spin_num=spin.num)

        # Test that the spin number or name are set (one or both are essential for the identification of the atom).
        if spin.num == None and spin.name == None:
            warn(RelaxWarning("Either the spin number or name must be set for the spin " + repr(id) + " to identify the corresponding atom in the molecule."))
            continue

        # The bond vector already exists.
        if hasattr(spin, 'vector'):
            obj = getattr(spin, 'vector')
            if obj != None:
                warn(RelaxWarning("The bond vector for the spin " + repr(id) + " already exists."))
                continue

        # Get the bond info.
        bond_vectors, attached_name, warnings = cdp.structure.bond_vectors(attached_atom=attached, model_num=model, res_num=res_num, spin_name=spin.name, spin_num=spin.num, return_name=True, return_warnings=True)
        id2 = generate_spin_id_unique(res_num=res_num, res_name=None, spin_name=spin.name)

        # No attached atom.
        if not bond_vectors:
            # Warning messages.
            if warnings:
                warn(RelaxWarning(warnings + " (atom ID " + repr(id) + ")."))

            # Skip the spin.
            continue

        # Set the attached atom name.
        if not hasattr(spin, 'attached_atom'):
            spin.attached_atom = attached_name
        elif spin.attached_atom != attached_name:
            raise RelaxError("The " + repr(spin.attached_atom) + " atom already attached to the spin does not match the attached atom " + repr(attached_name) + ".")

        # Initialise the average vector.
        if ave:
            ave_vector = zeros(3, float64)

        # Loop over the individual vectors.
        for i in range(len(bond_vectors)):
            # Unit vector.
            if unit:
                # Normalisation factor.
                norm_factor = norm(bond_vectors[i])

                # Test for zero length.
                if norm_factor == 0.0:
                    warn(RelaxZeroVectorWarning(spin_id1=id, spin_id2=id2))

                # Calculate the normalised vector.
                else:
                    bond_vectors[i] = bond_vectors[i] / norm_factor

            # Sum the vectors.
            if ave:
                ave_vector = ave_vector + bond_vectors[i]

        # Average.
        if ave:
            vector = ave_vector / float(len(bond_vectors))
        else:
            vector = bond_vectors

        # Convert to a single vector if needed.
        if len(vector) == 1:
            vector = vector[0]

        # Set the vector.
        setattr(spin, 'vector', vector)

        # We have a vector!
        no_vectors = False

        # Print out of modified spins.
        if verbosity:
            # The number of vectors.
            num = len(bond_vectors)
            plural = 's'
            if num == 1:
                plural = ''

            if spin.name:
                print("Extracted %s %s-%s vector%s for the spin '%s'." % (num, spin.name, attached_name, plural, id))
            else:
                print("Extracted %s %s-%s vector%s for the spin '%s'." % (num, spin.num, attached_name, plural, id))

    # Right, catch the problem of missing vectors to prevent massive user confusion!
    if no_vectors:
        raise RelaxError("No vectors could be extracted.")


def web_of_motion(pipes=None, models=None, molecules=None, atom_id=None, file=None, dir=None, force=False):
    """Create a PDB representation of the motion between a set of models.

    This will create a PDB file containing the atoms of all models, with identical atoms links using CONECT records.  This function only supports the internal structural object.


    @keyword pipes:     The data pipes to generate the web between.
    @type pipes:        None or list of str
    @keyword models:    The list of models to generate the web between.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:       None or list of lists of int
    @keyword molecules: The list of molecules to generate the web between.  The number of elements must match the pipes argument.
    @type molecules:    None or list of lists of str
    @keyword atom_id:   The atom identification string of the coordinates of interest.  This matches the spin ID string format.
    @type atom_id:      str or None
    @keyword file:      The name of the PDB file to write.
    @type file:         str
    @keyword dir:       The directory where the PDB file will be placed.  If set to None, then the file will be placed in the current directory.
    @type dir:          str or None
    @keyword force:     The force flag which if True will cause the file to be overwritten.
    @type force:        bool
    """

    # Checks.
    check_pipe()
    check_structure()

    # Assemble the structural coordinates.
    coord, ids, mol_names, res_names, res_nums, atom_names, elements = assemble_structural_coordinates(pipes=pipes, models=models, molecules=molecules, atom_id=atom_id)

    # Check that more than one structure is present.
    if not len(coord) > 1:
        raise RelaxError("Two or more structures are required.")

    # Initialise the structural object.
    web = Internal()

    # Loop over the atoms.
    for atom_index in range(len(atom_names)):
        # Loop over the structures.
        for struct_index in range(len(ids)):
            # Add the atom.
            web.add_atom(mol_name=mol_names[atom_index], atom_name=atom_names[atom_index], res_name=res_names[atom_index], res_num=res_nums[atom_index], pos=coord[struct_index, atom_index], element=elements[atom_index], sort=False)

        # Loop over the structures again, this time twice.
        for k in range(len(ids)):
            for l in range(len(ids)):
                # Skip identical atoms.
                if k == l:
                    continue

                # The atom index.
                index1 = atom_index*len(ids) + k
                index2 = atom_index*len(ids) + l

                # Connect to the previous atoms.
                web.connect_atom(mol_name=mol_names[atom_index], index1=index1, index2=index2)

    # Append the PDB extension if needed.
    if isinstance(file, str):
        # The file path.
        file = get_file_path(file, dir)

        # Add '.pdb' to the end of the file path if it isn't there yet.
        if not search(".pdb$", file):
            file += '.pdb'

    # Open the file for writing.
    file = open_write_file(file, force=force)

    # Write the structure.
    web.write_pdb(file)


def write_pdb(file=None, dir=None, model_num=None, compress_type=0, force=False):
    """The PDB writing function.

    @keyword file:          The name of the PDB file to write.  This can also be a file instance.
    @type file:             str or file instance
    @keyword dir:           The directory where the PDB file will be placed.  If set to None, then the file will be placed in the current directory.
    @type dir:              str or None
    @keyword model_num:     The model to place into the PDB file.  If not supplied, then all models will be placed into the file.
    @type model_num:        None or int
    @keyword compress_type: The compression type.  The integer values correspond to the compression type: 0, no compression; 1, Bzip2 compression; 2, Gzip compression.
    @type compress_type:    int
    @keyword force:         The force flag which if True will cause the file to be overwritten.
    @type force:            bool
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Check if the structural object exists.
    if not hasattr(cdp, 'structure'):
        raise RelaxError("No structural data is present in the current data pipe.")

    # Path handling.
    if isinstance(file, str):
        # The file path.
        file = get_file_path(file, dir)

        # Add '.pdb' to the end of the file path if it isn't there yet.
        if not search(".pdb$", file):
            file = file + '.pdb'

    # Open the file for writing.
    file = open_write_file(file, compress_type=compress_type, force=force)

    # Write the structures.
    cdp.structure.write_pdb(file, model_num=model_num)
