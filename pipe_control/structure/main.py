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

# Python module imports.
from minfx.generic import generic_minimise
from numpy import array, float64, zeros
from numpy.linalg import norm
from os import F_OK, access, getcwd
from re import search
import sys
from warnings import warn

# relax module imports.
from lib.check_types import is_float
from lib.errors import RelaxError, RelaxFileError
from lib.io import get_file_path, open_write_file, write_data
from lib.selection import tokenise
from lib.sequence import write_spin_data
from lib.structure.internal.displacements import Displacements
from lib.structure.internal.object import Internal
from lib.structure.represent.diffusion_tensor import diffusion_tensor
from lib.structure.statistics import atomic_rmsd
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
    cdp.structure.add_atom(mol_name=mol_name, atom_name=atom_name, res_name=res_name, res_num=res_num, pos=pos, element=element, atom_num=atom_num, chain_id=chain_id, segment_id=segment_id, pdb_record=pdb_record)


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


def align(pipes=None, molecules=None, models=None, method='fit to mean', atom_id=None, centre_type="centroid", centroid=None):
    """Superimpose a set of related, but not identical structures.

    @keyword pipes:         The data pipes to include in the alignment and superimposition.
    @type pipes:            None or list of str
    @keyword molecules:     The molecule names to include in the alignment and superimposition.
    @type molecules:        None or list of str
    @keyword models:        The list of models to for each data pipe superimpose.  The number of elements must match the pipes argument.  If set to None, then all models will be used.
    @type models:           list of lists of int or None
    @keyword method:        The superimposition method.  It must be one of 'fit to mean' or 'fit to first'.
    @type method:           str
    @keyword atom_id:       The molecule, residue, and atom identifier string.  This matches the spin ID string format.
    @type atom_id:          str or None
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

    # Assemble the atomic coordinates of all structures.
    print("Assembling all atomic coordinates:")
    atom_ids = []
    atom_pos = []
    atom_elem = []
    for pipe_index in range(len(pipes)):
        # Printout.
        print("    Data pipe: %s" % pipes[pipe_index])

        # The data pipe object.
        dp = get_pipe(pipes[pipe_index])

        # Validate the models.
        dp.structure.validate_models(verbosity=0)

        # The selection object.
        selection = dp.structure.selection(atom_id=atom_id)

        # Loop over the models.
        for model in dp.structure.model_loop():
            # No model match.
            if models != None and model.num not in models[pipe_index]:
                continue

            # Printout.
            print("        Model: %s" % model.num)

            # Extend the lists.
            if molecules == None:
                atom_ids.append([])
                atom_pos.append({})
                atom_elem.append({})

            # Add all coordinates and elements.
            current_mol = ''
            for mol_name, res_num, res_name, atom_name, elem, pos in dp.structure.atom_loop(selection=selection, model_num=model.num, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_name_flag=True, pos_flag=True, element_flag=True):
                # No molecule match, so skip.
                if molecules != None and mol_name not in molecules[pipe_index]:
                    continue

                # A new molecule.
                if mol_name != current_mol:
                    # Printout.
                    print("            Molecule: %s" % mol_name)

                    # Change the current molecule name.
                    current_mol = mol_name

                    # Extend the lists.
                    if molecules != None:
                        atom_ids.append([])
                        atom_pos.append({})
                        atom_elem.append({})

                # A unique identifier.
                if molecules != None:
                    id = ":%s&%s@%s" % (res_num, res_name, atom_name)
                else:
                    id = "#%s:%s&%s@%s" % (mol_name, res_num, res_name, atom_name)

                atom_ids[-1].append(id)
                atom_pos[-1][id] = pos[0]
                atom_elem[-1][id] = elem

    # Set up the structures for the superimposition algorithm.
    num = len(atom_ids)
    coord = []
    elements = []
    for i in range(num):
        coord.append([])
        elements.append([])

    # Find the common atoms and create the coordinate data structure.
    for id in atom_ids[0]:
        # Is the atom ID present in all other structures?
        present = True
        for i in range(num):
            if id not in atom_ids[i]:
                present = False
                break

        # Not present, so skip the atom.
        if not present:
            continue

        # Add the atomic position to the coordinate list and the element to the element list.
        for i in range(num):
            coord[i].append(atom_pos[i][id])
            elements[i].append(atom_elem[i][id])

    # Convert to a numpy array.
    coord = array(coord, float64)

    # The different algorithms.
    if method == 'fit to mean':
        T, R, pivot = fit_to_mean(models=list(range(num)), coord=coord, centre_type=centre_type, elements=elements, centroid=centroid)
    elif method == 'fit to first':
        T, R, pivot = fit_to_first(models=list(range(num)), coord=coord, centre_type=centre_type, elements=elements, centroid=centroid)

    # Update to the new coordinates.
    i = 0
    for pipe_index in range(len(pipes)):
        # The data pipe object.
        dp = get_pipe(pipes[pipe_index])

        print("    Data pipe: %s" % pipes[pipe_index])

        # The selection object.
        selection = dp.structure.selection(atom_id=atom_id)

        # Loop over the models.
        for model in dp.structure.model_loop():
            # No model match.
            if models != None and model.num not in models[pipe_index]:
                continue

            print("        Model: %s" % model.num)

            # Loop over the molecules.
            current_mol = ''
            for mol_name in dp.structure.atom_loop(selection=selection, model_num=model.num, mol_name_flag=True):
                # No molecule match, so skip.
                if molecules != None and mol_name not in molecules[pipe_index]:
                    continue

                # A new molecule.
                if mol_name != current_mol:

                    print("            Molecule: %s" % mol_name)

                    # Change the current molecule name.
                    current_mol = mol_name

                    # The atom ID from the molecule name.
                    id = '#%s' % mol_name

                    # Translate the molecule first (the rotational pivot is defined in the first model).
                    translate(T=T[i], model=model.num, pipe_name=pipes[pipe_index], atom_id=id)

                    # Rotate the molecule.
                    rotate(R=R[i], origin=pivot[i], model=model.num, pipe_name=pipes[pipe_index], atom_id=id)

                    # Increment the index.
                    i += 1


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


def displacement(model_from=None, model_to=None, atom_id=None, centroid=None):
    """Calculate the rotational and translational displacement between two structural models.

    @keyword model_from:        The optional model number for the starting position of the displacement.
    @type model_from:           int or None
    @keyword model_to:          The optional model number for the ending position of the displacement.
    @type model_to:             int or None
    @keyword atom_id:           The molecule, residue, and atom identifier string.  This matches the spin ID string format.
    @type atom_id:              str or None
    @keyword centroid:          An alternative position of the centroid, used for studying pivoted systems.
    @type centroid:             list of float or numpy rank-1, 3D array
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Convert the model_from and model_to args to lists, is supplied.
    if model_from != None:
        model_from = [model_from]
    if model_to != None:
        model_to = [model_to]

    # Create a list of all models.
    models = []
    for model in cdp.structure.model_loop():
        models.append(model.num)

    # Set model_from or model_to to all models if None.
    if model_from == None:
        model_from = models
    if model_to == None:
        model_to = models

    # Initialise the data structure.
    if not hasattr(cdp.structure, 'displacements'):
        cdp.structure.displacements = Displacements()

    # The selection object.
    selection = cdp.structure.selection(atom_id=atom_id)

    # Loop over the starting models.
    for i in range(len(model_from)):
        # Assemble the atomic coordinates.
        coord_from = []
        for pos in cdp.structure.atom_loop(selection=selection, model_num=model_from[i], pos_flag=True):
            coord_from.append(pos[0])

        # Loop over the ending models.
        for j in range(len(model_to)):
            # Assemble the atomic coordinates.
            coord_to = []
            for pos in cdp.structure.atom_loop(selection=selection, model_num=model_to[j], pos_flag=True):
                coord_to.append(pos[0])

            # Send to the base container for the calculations.
            cdp.structure.displacements._calculate(model_from=model_from[i], model_to=model_to[j], coord_from=array(coord_from), coord_to=array(coord_to), centroid=centroid)


def find_pivot(models=None, atom_id=None, init_pos=None, func_tol=1e-5, box_limit=200):
    """Superimpose a set of structural models.

    @keyword models:    The list of models to use.  If set to None, then all models will be used.
    @type models:       list of int or None
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

    # Validate the models.
    cdp.structure.validate_models()

    # Create a list of all models.
    if models == None:
        models = []
        for model in cdp.structure.model_loop():
            models.append(model.num)

    # The selection object.
    selection = cdp.structure.selection(atom_id=atom_id)

    # Assemble the atomic coordinates of all models.
    coord = []
    for model in models:
        coord.append([])
        for pos in cdp.structure.atom_loop(selection=selection, model_num=model, pos_flag=True):
            coord[-1].append(pos[0])
        coord[-1] = array(coord[-1])
    coord = array(coord)

    # Linear constraints for the pivot position (between -1000 and 1000 Angstrom).
    A = zeros((6, 3), float64)
    b = zeros(6, float64)
    for i in range(3):
        A[2*i, i] = 1
        A[2*i+1, i] = -1
        b[2*i] = -box_limit
        b[2*i+1] = -box_limit

    # The target function.
    finder = Pivot_finder(models, coord)
    results = generic_minimise(func=finder.func, x0=init_pos, min_algor='Log barrier', min_options=('simplex',), A=A, b=b, func_tol=func_tol, print_flag=1)

    # No result.
    if results == None:
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
        if mol_name and search('\+', mol_name):
            mol_name = mol_name.replace('+', '')
        if res_name and search('\+', res_name):
            res_name = res_name.replace('+', '')
        if atom_name and search('\+', atom_name):
            atom_name = atom_name.replace('+', '')

        # The spin identification string.
        id = generate_spin_id_unique(res_num=res_num, res_name=None, spin_num=atom_num, spin_name=atom_name)

        # Get the spin container.
        spin_cont = return_spin(id)

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
                subspin = return_spin(atom)

                # Test that the spin exists.
                if subspin == None:
                    raise RelaxNoSpinError(atom)

                # Test the position.
                if not hasattr(subspin, 'pos') or subspin.pos == None or not len(subspin.pos):
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


def load_spins(spin_id=None, str_id=None, from_mols=None, mol_name_target=None, ave_pos=False):
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
    """

    # The multi-molecule case.
    if from_mols != None:
        load_spins_multi_mol(spin_id=spin_id, str_id=str_id, from_mols=from_mols, mol_name_target=mol_name_target, ave_pos=ave_pos)
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

        # Remove the '+' regular expression character from the mol, res, and spin names!
        if mol_name and search('\+', mol_name):
            mol_name = mol_name.replace('+', '')
        if res_name and search('\+', res_name):
            res_name = res_name.replace('+', '')
        if atom_name and search('\+', atom_name):
            atom_name = atom_name.replace('+', '')

        # Generate a spin ID for the current atom.
        id = generate_spin_id_unique(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=atom_num, spin_name=atom_name)

        # Create the spin.
        try:
            spin_cont = create_spin(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=atom_num, spin_name=atom_name)

        # Otherwise, get the spin container.
        except RelaxError:
            spin_cont = return_spin(id)

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


def load_spins_multi_mol(spin_id=None, str_id=None, from_mols=None, mol_name_target=None, ave_pos=False):
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
            if res_name and search('\+', res_name):
                res_name = res_name.replace('+', '')
            if atom_name and search('\+', atom_name):
                atom_name = atom_name.replace('+', '')

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
        spin_cont = return_spin(id)

        # Create the spin if it does not exist.
        if spin_cont == None:
            spin_cont = create_spin(mol_name=mol_name_target, res_num=res_nums[id], res_name=res_names[id], spin_name=spin_names[id])

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


def mean():
    """Calculate the mean structure from all models in the structural data object."""

    # Checks.
    check_pipe()
    check_structure()

    # Call the specific code.
    cdp.structure.mean()


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


def rmsd(atom_id=None, models=None, molecules=None):
    """Calculate the RMSD between the loaded models.

    @keyword atom_id:   The molecule, residue, and atom identifier string.  Only atoms matching this selection will be used.
    @type atom_id:      str or None
    @keyword models:    The list of models to calculate the RMSD of.  If set to None, then all models will be used.
    @type models:       list of int or None
    @keyword molecules: The list of molecules to calculate the RMSD between.  This overrides the models.
    @type molecules:    None or list of str
    @return:            The RMSD value.
    @rtype:             float
    """

    # Test if the current data pipe exists.
    check_pipe()

    # The selection object.
    selection = cdp.structure.selection(atom_id=atom_id)

    # RMSD between models.
    if molecules == None:
        # Create a list of all models.
        if models == None:
            models = []
            for model in cdp.structure.model_loop():
                models.append(model.num)

        # Assemble the atomic coordinates of all models.
        coord = []
        for model in models:
            coord.append([])
            for pos in cdp.structure.atom_loop(selection=selection, model_num=model, pos_flag=True):
                coord[-1].append(pos[0])
            coord[-1] = array(coord[-1])

    # RMSD between structures.
    else:
        # No models allowed.
        if cdp.structure.num_models() > 1:
            raise RelaxError("When calculating the RMSD between different molecules, no models are allowed to be present.")

        # Assemble the atomic coordinates of all molecules.
        coord = []
        current_mol = ''
        for mol_name, pos in cdp.structure.atom_loop(selection=selection, mol_name_flag=True, pos_flag=True):
            # No molecule match, so skip.
            if mol_name not in molecules:
                continue

            # A new molecule.
            if mol_name != current_mol:
                # Change the current molecule name.
                current_mol = mol_name

                # Extend the coordinates.
                coord.append([])

            # Append the coordinate.
            coord[-1].append(pos[0])

        # Numpy conversion.
        for i in range(len(coord)):
            coord[i] = array(coord[i])

    # Calculate the RMSD.
    cdp.structure.rmsd = atomic_rmsd(coord, verbosity=1)

    # Return the RMSD.
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
    if origin == None:
        origin = [0, 0, 0]

    # Convert the args to numpy float data structures.
    R = array(R, float64)
    origin = array(origin, float64)

    # Call the specific code.
    selection = dp.structure.selection(atom_id=atom_id)
    dp.structure.rotate(R=R, origin=origin, model=model, selection=selection)


def set_vector(spin=None, xh_vect=None):
    """Place the XH unit vector into the spin container object.

    @keyword spin:      The spin container object.
    @type spin:         SpinContainer instance
    @keyword xh_vect:   The unit vector parallel to the XH bond.
    @type xh_vect:      array of len 3
    """

    # Place the XH unit vector into the container.
    spin.xh_vect = xh_vect


def superimpose(models=None, method='fit to mean', atom_id=None, centre_type="centroid", centroid=None):
    """Superimpose a set of structural models.

    @keyword models:        The list of models to superimpose.  If set to None, then all models will be used.
    @type models:           list of int or None
    @keyword method:        The superimposition method.  It must be one of 'fit to mean' or 'fit to first'.
    @type method:           str
    @keyword atom_id:       The molecule, residue, and atom identifier string.  This matches the spin ID string format.
    @type atom_id:          str or None
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

    # Test if the current data pipe exists.
    check_pipe()

    # Validate the models.
    cdp.structure.validate_models()

    # Create a list of all models.
    if models == None:
        models = []
        for model in cdp.structure.model_loop():
            models.append(model.num)

    # The selection object.
    selection = cdp.structure.selection(atom_id=atom_id)

    # Assemble the atomic coordinates of all models.
    coord = []
    for model in models:
        coord.append([])
        for pos in cdp.structure.atom_loop(selection=selection, model_num=model, pos_flag=True):
            coord[-1].append(pos[0])
        coord[-1] = array(coord[-1])

    # Assemble the element types.
    elements = []
    for elem in cdp.structure.atom_loop(selection=selection, model_num=model, element_flag=True):
        elements.append(elem)

    # The different algorithms.
    if method == 'fit to mean':
        T, R, pivot = fit_to_mean(models=models, coord=coord, centre_type=centre_type, elements=elements, centroid=centroid)
    elif method == 'fit to first':
        T, R, pivot = fit_to_first(models=models, coord=coord, centre_type=centre_type, elements=elements, centroid=centroid)

    # Update to the new coordinates.
    for i in range(len(models)):
        # Translate the molecule first (the rotational pivot is defined in the first model).
        translate(T=T[i], model=models[i])

        # Rotate the molecule.
        rotate(R=R[i], origin=pivot[i], model=models[i])


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


def web_of_motion(file=None, dir=None, models=None, force=False):
    """Create a PDB representation of the motion between a set of models.

    This will create a PDB file containing the atoms of all models, with identical atoms links using CONECT records.  This function only supports the internal structural object.

    @keyword file:          The name of the PDB file to write.
    @type file:             str
    @keyword dir:           The directory where the PDB file will be placed.  If set to None, then the file will be placed in the current directory.
    @type dir:              str or None
    @keyword models:        The optional list of models to restrict this to.
    @type models:           list of int or None
    @keyword force:         The force flag which if True will cause the file to be overwritten.
    @type force:            bool
    """

    # Checks.
    check_pipe()
    check_structure()

    # Validate the models.
    cdp.structure.validate_models()

    # Initialise the structural object.
    web = Internal()

    # The model list.
    if models == None:
        models = []
        for k in range(len(cdp.structure.structural_data)):
            models.append(cdp.structure.structural_data[k].num)

    # Loop over the molecules.
    for i in range(len(cdp.structure.structural_data[0].mol)):
        # Alias the molecule of the first model.
        mol1 = cdp.structure.structural_data[0].mol[i]

        # Loop over the atoms.
        for j in range(len(mol1.atom_name)):
            # Loop over the models.
            for k in range(len(cdp.structure.structural_data)):
                # Skip the model.
                if cdp.structure.structural_data[k].num not in models:
                    continue

                # Alias.
                mol = cdp.structure.structural_data[k].mol[i]

                # Add the atom.
                web.add_atom(mol_name=mol1.mol_name, atom_name=mol.atom_name[j], res_name=mol.res_name[j], res_num=mol.res_num[j], pos=[mol.x[j], mol.y[j], mol.z[j]], element=mol.element[j], chain_id=mol.chain_id[j], segment_id=mol.seg_id[j], pdb_record=mol.pdb_record[j])

            # Loop over the models again, this time twice.
            for k in range(len(models)):
                for l in range(len(models)):
                    # Skip identical atoms.
                    if k == l:
                        continue

                    # The atom index.
                    index1 = j*len(models) + k
                    index2 = j*len(models) + l

                    # Connect to the previous atoms.
                    web.connect_atom(mol_name=mol1.mol_name, index1=index1, index2=index2)

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
