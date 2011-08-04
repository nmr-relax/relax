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

# Python module imports.
from math import sqrt
from numpy import array, dot, float64, ndarray, zeros
from numpy.linalg import norm
from os import F_OK, access
from re import search
from string import replace
import sys
from warnings import warn

# relax module imports.
from generic_fns import molmol, relax_re
from generic_fns.mol_res_spin import create_spin, exists_mol_res_spin_data, generate_spin_id, linear_ave, return_molecule, return_residue, return_spin, spin_loop
from generic_fns import pipes
from generic_fns.structure.internal import Internal
from generic_fns.structure.scientific import Scientific_data
from relax_errors import RelaxError, RelaxFileError, RelaxNoPdbError, RelaxNoSequenceError
from relax_io import get_file_path, open_write_file, write_spin_data
from relax_warnings import RelaxWarning, RelaxNoPDBFileWarning, RelaxZeroVectorWarning



def delete():
    """Simple function for deleting all structural data."""

    # Run the object method.
    cdp.structure.delete()

    # Then remove any spin specific structural info.
    for spin in spin_loop():
        # Delete positional information.
        if hasattr(spin, 'pos'):
            del spin.pos

        # Delete bond vectors.
        if hasattr(spin, 'bond_vect'):
            del spin.bond_vect
        if hasattr(spin, 'xh_vect'):
            del spin.xh_vect


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
    model_index = -1
    last_model = None
    for model_num, mol_name, res_num, res_name, atom_num, atom_name, element, pos in cdp.structure.atom_loop(atom_id=spin_id, str_id=str_id, model_num_flag=True, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True, ave=ave_pos):
        # Update the model info.
        if last_model != model_num:
            model_index = model_index + 1
            last_model = model_num

        # Remove the '+' regular expression character from the mol, res, and spin names!
        if mol_name and search('\+', mol_name):
            mol_name = replace(mol_name, '+', '')
        if res_name and search('\+', res_name):
            res_name = replace(res_name, '+', '')
        if atom_name and search('\+', atom_name):
            atom_name = replace(atom_name, '+', '')

        # The spin identification string.  The residue name and spin num is not included to allow molecules with point mutations to be used as different models.
        id = generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=None, spin_name=atom_name)

        # Get the spin container.
        spin_cont = return_spin(id)

        # Skip the spin if it doesn't exist.
        if spin_cont == None:
            continue

        # Add the position vector to the spin container.
        if ave_pos:
            spin_cont.pos = pos
        else:
            if not hasattr(spin_cont, 'pos'):
                spin_cont.pos = []
            spin_cont.pos.append(pos)

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
                if not hasattr(subspin, 'pos') or not subspin.pos:
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


def load_spins(spin_id=None, str_id=None, ave_pos=False):
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

    # Print out.
    print("Adding the following spins to the relax data store.\n")

    # Init the data for printing out.
    mol_names = []
    res_nums = []
    res_names = []
    spin_nums = []
    spin_names = []

    # Initialise data for the atom loop.
    model_index = -1
    last_model = 1000000

    # Loop over all atoms of the spin_id selection.
    for model_num, mol_name, res_num, res_name, atom_num, atom_name, element, pos in cdp.structure.atom_loop(atom_id=spin_id, str_id=str_id, model_num_flag=True, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True, ave=ave_pos):
        # Update the model info.
        if last_model != model_num:
            model_index = model_index + 1
            last_model = model_num

        # Remove the '+' regular expression character from the mol, res, and spin names!
        if mol_name and search('\+', mol_name):
            mol_name = replace(mol_name, '+', '')
        if res_name and search('\+', res_name):
            res_name = replace(res_name, '+', '')
        if atom_name and search('\+', atom_name):
            atom_name = replace(atom_name, '+', '')

        # Generate a spin ID for the current atom.
        id = generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=atom_num, spin_name=atom_name)

        # Create the spin.
        try:
            spin_cont = create_spin(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=atom_num, spin_name=atom_name)
        except RelaxError:
            # Throw a warning if still on the first model.
            if not model_index:
                warn(RelaxWarning("The spin '%s' already exists." % id))
                continue

            # Otherwise, get the spin container.
            spin_cont = return_spin(id)

        # Append all the spin ID info for the first model for printing later.
        if model_index == 0:
            mol_names.append(mol_name)
            res_nums.append(res_num)
            res_names.append(res_name)
            spin_nums.append(atom_num)
            spin_names.append(atom_name)

        # Convert the position vector to a numpy array.
        pos = array(pos, float64)

        # Average position vector (already averaged across models in the atom_loop).
        if ave_pos:
            spin_cont.pos = pos

        # All positions.
        else:
            # Initialise.
            if not hasattr(spin_cont, 'pos'):
                spin_cont.pos = []

            # Add the current model's position.
            spin_cont.pos.append(pos)

        # Add the element.
        if not model_index:
            spin_cont.element = element

    # Catch no data.
    if len(mol_names) == 0:
        warn(RelaxWarning("No spins matching the '%s' ID string could be found." % spin_id))
        return

    # Print out.
    write_spin_data(file=sys.stdout, mol_names=mol_names, res_nums=res_nums, res_names=res_names, spin_nums=spin_nums, spin_names=spin_names)


def read_pdb(file=None, dir=None, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None, parser='internal', verbosity=1, fail=True):
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
    @keyword fail:          A flag which, if True, will cause a RelaxError to be raised if the PDB file does not exist.  If False, then a RelaxWarning will be trown instead.
    @type fail:             bool
    @keyword verbosity:     The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1.
    @type verbosity:        int
    @raise RelaxFileError:  If the fail flag is set, then a RelaxError is raised if the PDB file does not exist.
    """

    # Test if the current data pipe exists.
    pipes.test()

    # The file path.
    file_path = get_file_path(file, dir)

    # Try adding '.pdb' to the end of the file path, if the file can't be found.
    if not access(file_path, F_OK):
        file_path_orig = file_path
        file_path = file_path + '.pdb'

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
    cdp.structure.load_pdb(file_path, read_mol=read_mol, set_mol_name=set_mol_name, read_model=read_model, set_model_num=set_model_num, verbosity=verbosity)

    # Load into Molmol (if running).
    molmol.open_pdb()


def set_vector(spin=None, xh_vect=None):
    """Place the XH unit vector into the spin container object.

    @keyword spin:      The spin container object.
    @type spin:         SpinContainer instance
    @keyword xh_vect:   The unit vector parallel to the XH bond.
    @type xh_vect:      array of len 3
    """

    # Place the XH unit vector into the container.
    spin.xh_vect = xh_vect


def vectors(attached=None, spin_id=None, model=None, verbosity=1, ave=True, unit=True):
    """Extract the bond vectors from the loaded structures and store them in the spin container.

    @keyword attached:      The name of the atom attached to the spin, as given in the structural file.  Regular expression can be used, for example 'H*'.  This uses relax rather than Python regular expression (i.e. shell like syntax).
    @type attached:         str
    @keyword spin_id:       The spin identifier string.
    @type spin_id:          str
    @keyword model:         The model to extract the vector from.  If None, all vectors will be extracted.
    @type model:            str
    @keyword verbosity:     The higher the value, the more information is printed to screen.
    @type verbosity:        int
    @keyword ave:           A flag which if True will cause the average of all vectors to be extracted.
    @type ave:              bool
    @keyword unit:          A flag which if True will cause the function to calculate the unit vectors.
    @type unit:             bool
    """

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
                print(("Extracting vectors for model '%s'." % model))
            else:
                print(("Extracting vectors for all %s models." % num_models))
                if ave:
                    print("Averaging all vectors.")

        # Single model loaded.
        else:
            print("Extracting vectors from the single model.")

        # Unit vectors.
        if unit:
            print("Calculating the unit vectors.")

    # Determine if the attached atom is a proton.
    proton = False
    if relax_re.search('.*H.*', attached) or relax_re.search(attached, 'H'):
        proton = True
    if verbosity:
        if proton:
            print("The attached atom is a proton.")
        else:
            print("The attached atom is not a proton.")
        print('')

    # Set the variable name in which the vectors will be stored.
    if proton:
        object_name = 'xh_vect'
    else:
        object_name = 'bond_vect'

    # Loop over the spins.
    no_vectors = True
    for spin, mol_name, res_num, res_name in spin_loop(selection=spin_id, full_info=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # The spin identification string.  The residue name and spin num is not included to allow molecules with point mutations to be used as different models.
        id = generate_spin_id(res_num=res_num, res_name=None, spin_name=spin.name)

        # Test that the spin number or name are set (one or both are essential for the identification of the atom).
        if spin.num == None and spin.name == None:
            warn(RelaxWarning("Either the spin number or name must be set for the spin " + repr(id) + " to identify the corresponding atom in the molecule."))
            continue

        # The bond vector already exists.
        if hasattr(spin, object_name):
            obj = getattr(spin, object_name)
            if obj:
                warn(RelaxWarning("The bond vector for the spin " + repr(id) + " already exists."))
                continue

        # Get the bond info.
        bond_vectors, attached_name, warnings = cdp.structure.bond_vectors(attached_atom=attached, model_num=model, res_num=res_num, spin_name=spin.name, return_name=True, return_warnings=True)

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
        for i in xrange(len(bond_vectors)):
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

        # Set the vector.
        setattr(spin, object_name, vector)

        # We have a vector!
        no_vectors = False

        # Print out of modified spins.
        if verbosity:
            print(("Extracted " + spin.name + "-" + attached_name + " vectors for " + repr(id) + '.'))

    # Right, catch the problem of missing vectors to prevent massive user confusion!
    if no_vectors:
        raise RelaxError("No vectors could be extracted.")


def write_pdb(file=None, dir=None, model_num=None, force=False):
    """The PDB writing function.

    @keyword file:          The name of the PDB file to write.
    @type file:             str
    @keyword dir:           The directory where the PDB file will be placed.  If set to None, then the file will be placed in the current directory.
    @type dir:              str or None
    @keyword model_num:     The model to place into the PDB file.  If not supplied, then all models will be placed into the file.
    @type model_num:        None or int
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
    file = open_write_file(file_path, force=force)

    # Write the structures.
    cdp.structure.write_pdb(file, model_num=model_num)
