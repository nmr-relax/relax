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

# Python module imports.
from math import sqrt
from minfx.generic import generic_minimise
from numpy import array, dot, float64, ndarray, zeros
from numpy.linalg import norm
from os import F_OK, access
from re import search
import sys
from warnings import warn

# relax module imports.
from generic_fns import molmol, relax_re
from generic_fns.interatomic import interatomic_loop
from generic_fns.mol_res_spin import create_spin, exists_mol_res_spin_data, generate_spin_id_unique, linear_ave, return_molecule, return_residue, return_spin, spin_loop
from generic_fns import pipes
from generic_fns.structure.api_base import Displacements
from generic_fns.structure.internal import Internal
from generic_fns.structure.scientific import Scientific_data
from generic_fns.structure.statistics import atomic_rmsd
from generic_fns.structure.superimpose import fit_to_first, fit_to_mean
from target_functions.ens_pivot_finder import Pivot_finder
from lib.errors import RelaxError, RelaxFileError, RelaxNoPdbError, RelaxNoSequenceError
from lib.io import get_file_path, open_write_file, write_data, write_spin_data
from lib.warnings import RelaxWarning, RelaxNoPDBFileWarning, RelaxZeroVectorWarning


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
    pipes.test()

    # Place the structural object into the relax data store if needed.
    if not hasattr(cdp, 'structure'):
        cdp.structure = Internal()

    # Add the atoms.
    cdp.structure.add_atom(mol_name=mol_name, atom_name=atom_name, res_name=res_name, res_num=res_num, pos=pos, element=element, atom_num=atom_num, chain_id=chain_id, segment_id=segment_id, pdb_record=pdb_record)


def add_model(model_num=None):
    """Add a new model to the empty structural data object."""

    # Test if the current data pipe exists.
    pipes.test()

    # Place the structural object into the relax data store if needed.
    if not hasattr(cdp, 'structure'):
        cdp.structure = Internal()

    # The structural object can only be the internal object.
    if cdp.structure.id != 'internal':
        raise RelaxError("Models can only be added to the internal structural object.")

    # Check the structural object is empty.
    if cdp.structure.num_molecules() != 0:
        raise RelaxError("The internal structural object is not empty.")

    # Add a model.
    cdp.structure.structural_data.add_item(model_num=model_num)
    print("Created the empty model number %s." % model_num)


def connect_atom(index1=None, index2=None):
    """Connect two atoms.

    @keyword index1:    The global index of the first atom.
    @type index1:       str
    @keyword index2:    The global index of the first atom.
    @type index2:       str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Place the structural object into the relax data store if needed.
    if not hasattr(cdp, 'structure'):
        cdp.structure = Internal()

    # Add the atoms.
    cdp.structure.connect_atom(index1=index1, index2=index2)


def delete(atom_id=None):
    """Delete structural data.
    
    @keyword atom_id:   The molecule, residue, and atom identifier string.  This matches the spin ID string format.  If not given, then all structural data will be deleted.
    @type atom_id:      str or None
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Run the object method.
    if hasattr(cdp, 'structure'):
        print("Deleting structural data from the current pipe.")
        cdp.structure.delete(atom_id=atom_id)
    else:
        print("No structures are present.")

    # Then remove any spin specific structural info.
    print("Deleting all spin specific structural info.")
    for spin in spin_loop(selection=atom_id):
        # Delete positional information.
        if hasattr(spin, 'pos'):
            del spin.pos

    # Then remove any interatomic vector structural info.
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
    pipes.test()

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

    # Loop over the starting models.
    for i in range(len(model_from)):
        # Assemble the atomic coordinates.
        coord_from = []
        for pos in cdp.structure.atom_loop(atom_id=atom_id, model_num=model_from[i], pos_flag=True):
            coord_from.append(pos[0])

        # Loop over the ending models.
        for j in range(len(model_to)):
            # Assemble the atomic coordinates.
            coord_to = []
            for pos in cdp.structure.atom_loop(atom_id=atom_id, model_num=model_to[j], pos_flag=True):
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
    pipes.test()

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

    # Assemble the atomic coordinates of all models.
    coord = []
    for model in models:
        coord.append([])
        for pos in cdp.structure.atom_loop(atom_id=atom_id, model_num=model, pos_flag=True):
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

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the structure exists.
    if not hasattr(cdp, 'structure') or not cdp.structure.num_models() or not cdp.structure.num_molecules():
        raise RelaxNoPdbError

    # Loop over all atoms of the spin_id selection.
    data = []
    for mol_name, res_num, res_name, atom_num, atom_name, element, pos in cdp.structure.atom_loop(atom_id=spin_id, str_id=str_id, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True, ave=ave_pos):
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


def load_spins(spin_id=None, str_id=None, mol_name_target=None, ave_pos=False):
    """Load the spins from the structural object into the relax data store.

    @keyword spin_id:           The molecule, residue, and spin identifier string.
    @type spin_id:              str
    @keyword str_id:            The structure identifier.  This can be the file name, model number, or structure number.
    @type str_id:               int or str
    @keyword mol_name:          The name of target molecule container, overriding the name of the loaded structures
    @type mol_name:             str or None
    @keyword ave_pos:           A flag specifying if the average atom position or the atom position from all loaded structures is loaded into the SpinContainer.
    @type ave_pos:              bool
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the structure exists.
    if not hasattr(cdp, 'structure') or not cdp.structure.num_models() or not cdp.structure.num_molecules():
        raise RelaxNoPdbError

    # Print out.
    print("Adding the following spins to the relax data store.\n")

    # Init the data for printing out.
    mol_names = []
    res_nums = []
    res_names = []
    spin_nums = []
    spin_names = []

    # Loop over all atoms of the spin_id selection.
    for mol_name, res_num, res_name, atom_num, atom_name, element, pos in cdp.structure.atom_loop(atom_id=spin_id, str_id=str_id, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True, ave=ave_pos):
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


def read_pdb(file=None, dir=None, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None, parser='internal', alt_loc=None, verbosity=1, merge=False, fail=True):
    """The PDB loading function.

    Parsers
    =======

    A number of parsers are available for reading PDB files.  These include:

        - 'scientific', the Scientific Python PDB parser.
        - 'internal', a low quality yet fast PDB parser built into relax.


    @keyword file:          The name of the PDB file to read.
    @type file:             str
    @keyword dir:           The directory where the PDB file is located.  If set to None, then the file will be searched for in the current directory.
    @type dir:              str or None
    @keyword read_mol:      The molecule(s) to read from the file, independent of model.  The molecules are determined differently by the different parsers, but are numbered consecutively from 1.  If set to None, then all molecules will be loaded.
    @type read_mol:         None, int, or list of int
    @keyword set_mol_name:  Set the names of the molecules which are loaded.  If set to None, then the molecules will be automatically labelled based on the file name or other information.
    @type set_mol_name:     None, str, or list of str
    @keyword read_model:    The PDB model to extract from the file.  If set to None, then all models will be loaded.
    @type read_model:       None, int, or list of int
    @keyword set_model_num: Set the model number of the loaded molecule.  If set to None, then the PDB model numbers will be preserved, if they exist.
    @type set_model_num:    None, int, or list of int
    @keyword parser:        The parser to be used to read the PDB file.
    @type parser:           str
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
    pipes.test()

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

    # Check that the parser is the same as the currently loaded PDB files.
    if hasattr(cdp, 'structure') and cdp.structure.id != parser:
        raise RelaxError("The " + repr(parser) + " parser does not match the " + repr(cdp.structure.id) + " parser of the PDB loaded into the current pipe.")

    # Place the parser specific structural object into the relax data store.
    if not hasattr(cdp, 'structure'):
        if parser == 'scientific':
            cdp.structure = Scientific_data()
        elif parser == 'internal':
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
    pipes.test()

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


def rmsd(atom_id=None, models=None):
    """Calculate the RMSD between the loaded models.

    @keyword atom_id:   The molecule, residue, and atom identifier string.  Only atoms matching this selection will be used.
    @type atom_id:      str or None
    @keyword models:    The list of models to calculate the RMDS of.  If set to None, then all models will be used.
    @type models:       list of int or None
    @return:            The RMSD value.
    @rtype:             float
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Create a list of all models.
    if models == None:
        models = []
        for model in cdp.structure.model_loop():
            models.append(model.num)

    # Assemble the atomic coordinates of all models.
    coord = []
    for model in models:
        coord.append([])
        for pos in cdp.structure.atom_loop(atom_id=atom_id, model_num=model, pos_flag=True):
            coord[-1].append(pos[0])
        coord[-1] = array(coord[-1])

    # Calculate the RMSD.
    cdp.structure.rmsd = atomic_rmsd(coord, verbosity=1)

    # Return the RMSD.
    return cdp.structure.rmsd


def rotate(R=None, origin=None, model=None, atom_id=None):
    """Rotate the structural data about the origin by the specified forwards rotation.

    @keyword R:         The forwards rotation matrix.
    @type R:            numpy 3D, rank-2 array or a 3x3 list of floats
    @keyword origin:    The origin of the rotation.  If not supplied, the origin will be set to [0, 0, 0].
    @type origin:       numpy 3D, rank-1 array or list of len 3 or None
    @keyword model:     The model to rotate.  If None, all models will be rotated.
    @type model:        int
    @keyword atom_id:   The molecule, residue, and atom identifier string.  Only atoms matching this selection will be used.
    @type atom_id:      str or None
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the structure exists.
    if not hasattr(cdp, 'structure') or not cdp.structure.num_models() or not cdp.structure.num_molecules():
        raise RelaxNoPdbError

    # Set the origin if not supplied.
    if origin == None:
        origin = [0, 0, 0]

    # Convert the args to numpy float data structures.
    R = array(R, float64)
    origin = array(origin, float64)

    # Call the specific code.
    cdp.structure.rotate(R=R, origin=origin, model=model, atom_id=atom_id)


def set_vector(spin=None, xh_vect=None):
    """Place the XH unit vector into the spin container object.

    @keyword spin:      The spin container object.
    @type spin:         SpinContainer instance
    @keyword xh_vect:   The unit vector parallel to the XH bond.
    @type xh_vect:      array of len 3
    """

    # Place the XH unit vector into the container.
    spin.xh_vect = xh_vect


def superimpose(models=None, method='fit to mean', atom_id=None, centroid=None):
    """Superimpose a set of structural models.

    @keyword models:    The list of models to superimpose.  If set to None, then all models will be used.
    @type models:       list of int or None
    @keyword method:    The superimposition method.  It must be one of 'fit to mean' or 'fit to first'.
    @type method:       str
    @keyword atom_id:   The molecule, residue, and atom identifier string.  This matches the spin ID string format.
    @type atom_id:      str or None
    @keyword centroid:  An alternative position of the centroid to allow for different superpositions, for example of pivot point motions.
    @type centroid:     list of float or numpy rank-1, 3D array
    """

    # Check the method.
    allowed = ['fit to mean', 'fit to first']
    if method not in allowed:
        raise RelaxError("The superimposition method '%s' is unknown.  It must be one of %s." % (method, allowed))

    # Test if the current data pipe exists.
    pipes.test()

    # Validate the models.
    cdp.structure.validate_models()

    # Create a list of all models.
    if models == None:
        models = []
        for model in cdp.structure.model_loop():
            models.append(model.num)

    # Assemble the atomic coordinates of all models.
    coord = []
    for model in models:
        coord.append([])
        for pos in cdp.structure.atom_loop(atom_id=atom_id, model_num=model, pos_flag=True):
            coord[-1].append(pos[0])
        coord[-1] = array(coord[-1])

    # The different algorithms.
    if method == 'fit to mean':
        T, R, pivot = fit_to_mean(models=models, coord=coord, centroid=centroid)
    elif method == 'fit to first':
        T, R, pivot = fit_to_first(models=models, coord=coord, centroid=centroid)


    # Update to the new coordinates.
    for i in range(len(models)):
        # Translate the molecule first (the rotational pivot is defined in the first model).
        translate(T=T[i], model=models[i])

        # Rotate the molecule.
        rotate(R=R[i], origin=pivot[i], model=models[i])


def translate(T=None, model=None, atom_id=None):
    """Shift the structural data by the specified translation vector.

    @keyword T:         The translation vector.
    @type T:            numpy rank-1, 3D array or list of float
    @keyword model:     The model to translate.  If None, all models will be rotated.
    @type model:        int or None
    @keyword atom_id:   The molecule, residue, and atom identifier string.  Only atoms matching this selection will be used.
    @type atom_id:      str or None
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the structure exists.
    if not hasattr(cdp, 'structure') or not cdp.structure.num_models() or not cdp.structure.num_molecules():
        raise RelaxNoPdbError

    # Convert the args to numpy float data structures.
    T = array(T, float64)

    # Call the specific code.
    cdp.structure.translate(T=T, model=model, atom_id=atom_id)


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

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the PDB file has been loaded.
    if not hasattr(cdp, 'structure'):
        raise RelaxNoPdbError

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

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
                    warn(RelaxZeroVectorWarning(id))

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

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the structure exists.
    if not hasattr(cdp, 'structure') or not cdp.structure.num_models() or not cdp.structure.num_molecules():
        raise RelaxNoPdbError

    # Validate the models.
    cdp.structure.validate_models()

    # Check the structural object type.
    if cdp.structure.id != 'internal':
        raise RelaxError("The %s structure type is not supported." % cdp.structure.id)

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

    @keyword file:          The name of the PDB file to write.
    @type file:             str
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
    pipes.test()

    # Check if the structural object exists.
    if not hasattr(cdp, 'structure'):
        raise RelaxError("No structural data is present in the current data pipe.")

    # Check if the structural object is writable.
    if cdp.structure.id in ['scientific']:
        raise RelaxError("The structures from the " + cdp.structure.id + " parser are not writable.")

    # The file path.
    file_path = get_file_path(file, dir)

    # Add '.pdb' to the end of the file path if it isn't there yet.
    if not search(".pdb$", file_path):
        file_path = file_path + '.pdb'

    # Open the file for writing.
    file = open_write_file(file_path, compress_type=compress_type, force=force)

    # Write the structures.
    cdp.structure.write_pdb(file, model_num=model_num)
