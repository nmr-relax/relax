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

# Module docstring.
"""Module for the manipulation of the molecule-residue-spin data structures in the relax data store.

The functionality of this module is diverse:
    - Documentation for the spin identification string.
    - Functions for parsing or generating spin identification strings.
    - The mol-res-spin selection object (derived from the Selection class).
    - Generator functions for looping over molecules, residues, or spins.
    - Functions for returning MoleculeContainer, ResidueContainer, and SpinContainer objects or information about these.
    - Functions for copying, creating, deleting, displaying, naming, and numbering MoleculeContainer, ResidueContainer, and SpinContainer objects in the relax data store.
    - Functions for counting spins or testing their existence.
"""

# Python module imports.
from numpy import array, float64
from re import split
import sys
from warnings import warn

# relax module imports.
from pipe_control import exp_info, pipes
from lib.check_types import is_unicode
from lib.errors import RelaxError, RelaxNoSpinError, RelaxMultiMolIDError, RelaxMultiResIDError, RelaxMultiSpinIDError, RelaxResSelectDisallowError, RelaxSpinSelectDisallowError
from lib.selection import Selection, parse_token, tokenise
from lib.warnings import RelaxWarning
from status import Status; status = Status()
from user_functions.objects import Desc_container


ALLOWED_MOL_TYPES = ['protein',
                     'DNA',
                     'RNA',
                     'organic molecule',
                     'inorganic molecule'
]
"""The list of allowable molecule types."""

id_string_doc = Desc_container("Spin ID string documentation")
id_string_doc.add_paragraph("The identification string is composed of three components: the molecule ID token beginning with the '#' character, the residue ID token beginning with the ':' character, and the atom or spin system ID token beginning with the '@' character.  Each token can be composed of multiple elements - one per spin - separated by the ',' character and each individual element can either be a number (which must be an integer, in string format), a name, or a range of numbers separated by the '-' character.  Negative numbers are supported.  The full ID string specification is '#<mol_name> :<res_id>[, <res_id>[, <res_id>, ...]] @<atom_id>[, <atom_id>[, <atom_id>, ...]]', where the token elements are '<mol_name>', the name of the molecule, '<res_id>', the residue identifier which can be a number, name, or range of numbers, '<atom_id>', the atom or spin system identifier which can be a number, name, or range of numbers.")
id_string_doc.add_paragraph("If one of the tokens is left out then all elements will be assumed to match.  For example if the string does not contain the '#' character then all molecules will match the string.  If only the molecule ID component is specified, then all spins of the molecule will match.")
id_string_doc.add_paragraph("Regular expression can be used to select spins.  For example the string '@H*' will select the protons 'H', 'H2', 'H98'.")


def are_spins_named(spin_id=None):
    """Determine if any spins have been named.

    @keyword spin_id:   The spin ID string.
    @type spin_id:      None or str
    @return:            True if a spin has been named or False if no spins have been named.
    @rtype:             bool
    """

    # Loop over the spins.
    for spin in spin_loop(spin_id):
        # The spin is named.
        if spin.name != None:
            return True

    # No spins have been named.
    return False


def bmrb_read(star):
    """Generate the molecule and residue spin containers from the entity saveframe records.

    @param star:    The NMR-STAR dictionary object.
    @type star:     NMR_STAR instance
    """

    # Get the entities.
    for data in star.entity.loop():
        # Remove nasty characters from the molecule name.
        mol_name = data['mol_name']
        if mol_name:
            # Round brackets.
            mol_name = mol_name.replace('(', '')
            mol_name = mol_name.replace(')', '')

            # Square brackets.
            mol_name = mol_name.replace('[', '')
            mol_name = mol_name.replace(']', '')

            # Commas.
            mol_name = mol_name.replace(',', ' ')

        # The molecule type.
        mol_type = data['mol_type']
        polymer_type = data['polymer_type']

        # Translate from the BMRB notation to relax'.
        if mol_type == 'polymer':
            map = {
                'DNA/RNA hybrid': 'DNA',
                'polydeoxyribonucleotide': 'DNA',
                'polypeptide(D)': 'protein',
                'polypeptide(L)': 'protein',
                'polyribonucleotide': 'RNA',
                'polysaccharide(D)': 'organic molecule',
                'polysaccharide(L)': 'organic molecule'
            }
            mol_type = map[polymer_type]

        # Create the molecule.
        create_molecule(mol_name=mol_name, mol_type=mol_type)

        # The thiol state.
        exp_info.thiol_state(data['thiol_state'])

        # Add the residues.
        for i in range(len(data['res_nums'])):
            create_residue(data['res_nums'][i], data['res_names'][i], mol_name=mol_name)


def bmrb_write_entity(star, version=None):
    """Generate the entity saveframe records for the NMR-STAR dictionary object.

    @param star:        The NMR-STAR dictionary object.
    @type star:         NMR_STAR instance
    @keyword version:   The BMRB NMR-STAR dictionary format to output to.
    @type version:      str
    """

    # Loop over the molecules.
    for mol in molecule_loop():
        # Test that the molecule has a name!
        if not mol.name:
            raise RelaxError("All molecules must be named.")

        # Test that the molecule has a type!
        if not hasattr(mol, 'type') or not mol.type:
            raise RelaxError("The molecule type for the '%s' molecule must be specified, please use the appropriate molecule user function to set this." % mol.name)

        # Test that the molecule thiol state has been set.
        if not hasattr(cdp, 'exp_info') or not hasattr(cdp.exp_info, 'thiol_state'):
            raise RelaxError("The thiol state of the molecule '%s' must be specified, please use the appropriate BMRB user function to set this." % mol.name)

        # Get the residue names and numbers.
        res_names = get_residue_names("#" + mol.name)
        res_nums = get_residue_nums("#" + mol.name)

        # Get the one letter codes.
        polymer_seq_code = one_letter_code(res_names)

        # Find the molecule type.
        if mol.type in ['organic molecule', 'other']:
            mol_type = 'non-polymer'
        else:
            mol_type = 'polymer'

        # Translate the names.
        polymer_type = mol.type
        if polymer_type == 'protein':
            polymer_type = 'polypeptide(L)'
        if polymer_type == 'DNA':
            polymer_type = 'polydeoxyribonucleotide'
        if polymer_type == 'RNA':
            polymer_type = 'polyribonucleotide'
        if polymer_type == 'inorganic molecule':
            polymer_type = 'other'

        # Add the entity.
        star.entity.add(mol_name=mol.name, mol_type=mol_type, polymer_type=polymer_type, polymer_seq_code=polymer_seq_code, thiol_state=cdp.exp_info.thiol_state, res_nums=res_nums, res_names=res_names)


def copy_molecule(pipe_from=None, mol_from=None, pipe_to=None, mol_to=None):
    """Copy the contents of a molecule container to a new molecule.

    For copying to be successful, the mol_from identification string must match an existent molecule.


    @param pipe_from:   The data pipe to copy the molecule data from.  This defaults to the current data pipe.
    @type pipe_from:    str
    @param mol_from:    The molecule identification string for the structure to copy the data from.
    @type mol_from:     str
    @param pipe_to:     The data pipe to copy the molecule data to.  This defaults to the current data pipe.
    @type pipe_to:      str
    @param mol_to:      The molecule identification string for the structure to copy the data to.
    @type mol_to:       str
    """

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # The current data pipe.
        if pipe_from == None:
            pipe_from = pipes.cdp_name()
        if pipe_to == None:
            pipe_to = pipes.cdp_name()

        # The second pipe does not exist.
        pipes.test(pipe_to)

        # Split up the selection string.
        mol_from_token, res_from_token, spin_from_token = tokenise(mol_from)
        mol_to_token, res_to_token, spin_to_token = tokenise(mol_to)

        # Disallow spin selections.
        if spin_from_token != None or spin_to_token != None:
            raise RelaxSpinSelectDisallowError

        # Disallow residue selections.
        if res_from_token != None or res_to_token != None:
            raise RelaxResSelectDisallowError

        # Parse the molecule token for renaming.
        mol_name_to = return_single_molecule_info(mol_to_token)

        # Test if the molecule name already exists.
        mol_to_cont = return_molecule(mol_to, pipe_to)
        if mol_to_cont and not mol_to_cont.is_empty():
            raise RelaxError("The molecule " + repr(mol_to) + " already exists in the " + repr(pipe_to) + " data pipe.")

        # Get the single molecule data container.
        mol_from_cont = return_molecule(mol_from, pipe_from)

        # No molecule to copy data from.
        if mol_from_cont == None:
            raise RelaxError("The molecule " + repr(mol_from) + " does not exist in the " + repr(pipe_from) + " data pipe.")

        # Get the target pipe.
        pipe = pipes.get_pipe(pipe_to)

        # Copy the data.
        if pipe.mol[0].name == None and len(pipe.mol) == 1:
            pipe.mol[0] = mol_from_cont.__clone__()
        else:
            pipe.mol.append(mol_from_cont.__clone__())

        # Change the new molecule name.
        if mol_name_to != None:
            pipe.mol[-1].name = mol_name_to

        # Update the private metadata.
        metadata_update(pipe=pipe_to)

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)


def copy_residue(pipe_from=None, res_from=None, pipe_to=None, res_to=None):
    """Copy the contents of the residue structure from one residue to a new residue.

    For copying to be successful, the res_from identification string must match an existent residue. The new residue number must be unique.

    @param pipe_from:   The data pipe to copy the residue from.  This defaults to the current data pipe.
    @type pipe_from:    str
    @param res_from:    The residue identification string for the structure to copy the data from.
    @type res_from:     str
    @param pipe_to:     The data pipe to copy the residue to.  This defaults to the current data pipe.
    @type pipe_to:      str
    @param res_to:      The residue identification string for the structure to copy the data to.
    @type res_to:       str
    """

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # The current data pipe.
        if pipe_from == None:
            pipe_from = pipes.cdp_name()
        if pipe_to == None:
            pipe_to = pipes.cdp_name()

        # The second pipe does not exist.
        pipes.test(pipe_to)

        # Get the target pipe.
        pipe = pipes.get_pipe(pipe_to)

        # Split up the selection string.
        mol_from_token, res_from_token, spin_from_token = tokenise(res_from)
        mol_to_token, res_to_token, spin_to_token = tokenise(res_to)

        # Disallow spin selections.
        if spin_from_token != None or spin_to_token != None:
            raise RelaxSpinSelectDisallowError

        # Parse the residue token for renaming and renumbering.
        res_num_to, res_name_to = return_single_residue_info(res_to_token)

        # Test if the residue number already exists.
        res_to_cont = return_residue(res_to, pipe_to)
        if res_to_cont and not res_to_cont.is_empty():
            raise RelaxError("The residue " + repr(res_to) + " already exists in the " + repr(pipe_to) + " data pipe.")

        # Get the single residue data container.
        res_from_cont = return_residue(res_from, pipe_from)

        # No residue to copy data from.
        if res_from_cont == None:
            raise RelaxError("The residue " + repr(res_from) + " does not exist in the " + repr(pipe_from) + " data pipe.")

        # Get the single molecule data container to copy the residue to (default to the first molecule).
        mol_to_container = return_molecule(res_to, pipe_to)
        if mol_to_container == None:
            mol_to_container = pipe.mol[0]

        # Copy the data.
        if mol_to_container.res[0].num == None and mol_to_container.res[0].name == None and len(mol_to_container.res) == 1:
            mol_to_container.res[0] = res_from_cont.__clone__()
        else:
            mol_to_container.res.append(res_from_cont.__clone__())

        # Change the new residue number and name.
        if res_num_to != None:
            mol_to_container.res[-1].num = res_num_to
        if res_name_to != None:
            mol_to_container.res[-1].name = res_name_to

        # Update the private metadata.
        metadata_update(pipe=pipe_to)

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)


def copy_spin(pipe_from=None, spin_from=None, pipe_to=None, spin_to=None):
    """Copy the contents of the spin structure from one spin to a new spin.

    For copying to be successful, the spin_from identification string must match an existent spin. The new spin number must be unique.


    @param pipe_from:   The data pipe to copy the spin from.  This defaults to the current data pipe.
    @type pipe_from:    str
    @param spin_from:   The spin identification string for the structure to copy the data from.
    @type spin_from:    str
    @param pipe_to:     The data pipe to copy the spin to.  This defaults to the current data pipe.
    @type pipe_to:      str
    @param spin_to:     The spin identification string for the structure to copy the data to.
    @type spin_to:      str
    """

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # The current data pipe.
        if pipe_from == None:
            pipe_from = pipes.cdp_name()
        if pipe_to == None:
            pipe_to = pipes.cdp_name()

        # The second pipe does not exist.
        pipes.test(pipe_to)

        # Get the target pipe.
        pipe = pipes.get_pipe(pipe_to)

        # Split up the selection string.
        mol_to_token, res_to_token, spin_to_token = tokenise(spin_to)

        # Test if the spin number already exists.
        if spin_to_token:
            spin_to_cont = return_spin(spin_to, pipe_to)
            if spin_to_cont and not spin_to_cont.is_empty():
                raise RelaxError("The spin " + repr(spin_to) + " already exists in the " + repr(pipe_from) + " data pipe.")

        # No residue to copy data from.
        if not return_residue(spin_from, pipe_from):
            raise RelaxError("The residue in " + repr(spin_from) + " does not exist in the " + repr(pipe_from) + " data pipe.")

        # No spin to copy data from.
        spin_from_cont = return_spin(spin_from, pipe_from)
        if spin_from_cont == None:
            raise RelaxError("The spin " + repr(spin_from) + " does not exist in the " + repr(pipe_from) + " data pipe.")

        # Get the single residue data container to copy the spin to (default to the first molecule, first residue).
        res_to_cont = return_residue(spin_to, pipe_to)
        if res_to_cont == None and spin_to:
            # No residue to copy data to.
            raise RelaxError("The residue in " + repr(spin_to) + " does not exist in the " + repr(pipe_from) + " data pipe.")
        if res_to_cont == None:
            res_to_cont = pipe.mol[0].res[0]

        # Copy the data.
        if len(res_to_cont.spin) == 1 and res_to_cont.spin[0].is_empty():
            res_to_cont.spin[0] = spin_from_cont.__clone__()
        else:
            res_to_cont.spin.append(spin_from_cont.__clone__())

        # Parse the spin token for renaming and renumbering.
        spin_num_to, spin_name_to = return_single_spin_info(spin_to_token)

        # Change the new spin number and name.
        if spin_num_to != None:
            res_to_cont.spin[-1].num = spin_num_to
        if spin_name_to != None:
            res_to_cont.spin[-1].name = spin_name_to

        # Update the private metadata.
        metadata_update(pipe=pipe_to)

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)


def count_max_spins_per_residue(pipe=None, skip_desel=True):
    """Determine the maximum number of spins present per residue.

    @keyword pipe:          The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:             str
    @keyword skip_desel:    A flag which if true will cause deselected spins to be skipped in the count.
    @type skip_desel:       bool
    @return:                The number of non-empty spins.
    @rtype:                 int
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # No data, hence no spins.
    if not exists_mol_res_spin_data(pipe=pipe):
        return 0

    # Init.
    max_num = 0

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Loop over the molecules.
    for mol in dp.mol:
        # Loop over the residues.
        for res in mol.res:
            # Initialise the counter.
            spin_num = 0

            # Loop over the spins.
            for spin in res.spin:
                # Skip deselected spins.
                if skip_desel and not spin.select:
                    continue

                # Increment the spin number.
                spin_num = spin_num + 1

            # The maximum number.
            max_num = max(max_num, spin_num)

    # Return the maximum number of spins.
    return spin_num


def count_molecules(selection=None, pipe=None):
    """Count the number of molecules for which there is data.

    @keyword selection: The selection string.
    @type selection:    str
    @keyword pipe:      The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:         str
    @return:            The number of non-empty molecules.
    @rtype:             int
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # No data, hence no molecules.
    if not exists_mol_res_spin_data(pipe=pipe):
        return 0

    # Init.
    mol_num = 0

    # Spin loop.
    for mol in molecule_loop(selection, pipe=pipe):
        mol_num = mol_num + 1

    # Return the number of molecules.
    return mol_num


def count_residues(selection=None, pipe=None):
    """Count the number of residues for which there is data.

    @keyword selection: The selection string.
    @type selection:    str
    @keyword pipe:      The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:         str
    @return:            The number of non-empty residues.
    @rtype:             int
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # No data, hence no residues.
    if not exists_mol_res_spin_data(pipe=pipe):
        return 0

    # Init.
    res_num = 0

    # Spin loop.
    for res in residue_loop(selection, pipe=pipe):
        res_num = res_num + 1

    # Return the number of residues.
    return res_num


def count_spins(selection=None, pipe=None, skip_desel=True):
    """Function for counting the number of spins for which there is data.

    @keyword selection:     The selection string.
    @type selection:        str
    @keyword pipe:          The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:             str
    @keyword skip_desel:    A flag which if true will cause deselected spins to be skipped in the count.
    @type skip_desel:       bool
    @return:                The number of non-empty spins.
    @rtype:                 int
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # No data, hence no spins.
    if not exists_mol_res_spin_data(pipe=pipe):
        return 0

    # Init.
    spin_num = 0

    # Spin loop.
    for spin in spin_loop(selection, pipe=pipe):
        # Skip deselected spins.
        if skip_desel and not spin.select:
            continue

        spin_num = spin_num + 1

    # Return the number of spins.
    return spin_num


def create_molecule(mol_name=None, mol_type=None, pipe=None):
    """Add a molecule into the relax data store.

    @keyword mol_name:  The name of the molecule.
    @type mol_name:     str
    @keyword pipe:      The data pipe to add the molecule to.  Defaults to the current data pipe.
    @type pipe:         str or None
    @keyword mol_type:  The type of molecule.
    @type mol_type:     str
    @return:            The newly created molecule.
    @rtype:             MoleculeContainer instance
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # Test the molecule type.
        if mol_type and mol_type not in ALLOWED_MOL_TYPES:
            raise RelaxError("The molecule type '%s' must be one of %s" % (mol_type, ALLOWED_MOL_TYPES))

        # Test if the molecule name already exists.
        for i in range(len(dp.mol)):
            if dp.mol[i].name == mol_name:
                raise RelaxError("The molecule '" + repr(mol_name) + "' already exists in the relax data store.")

        # Append the molecule.
        dp.mol.add_item(mol_name=mol_name, mol_type=mol_type)

        # Alias the molecule.
        mol = dp.mol[-1]

        # Update the private metadata.
        if len(dp.mol) == 2:
            metadata_cleanup(pipe=pipe)
        else:
            metadata_cleanup(mol_index=len(dp.mol)-1, pipe=pipe)
        metadata_update(mol_index=len(dp.mol)-1, pipe=pipe)

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)

    # Return the molecule.
    return mol


def create_residue(res_num=None, res_name=None, mol_name=None, pipe=None):
    """Add a residue into the relax data store (and molecule if necessary).

    @keyword res_num:   The number of the new residue.
    @type res_num:      int
    @keyword res_name:  The name of the new residue.
    @type res_name:     str
    @keyword mol_name:  The name of the molecule to add the residue to.
    @type mol_name:     str
    @keyword pipe:      The data pipe to add the residue to.  Defaults to the current data pipe.
    @type pipe:         str or None
    @return:            The newly created residue.
    @rtype:             ResidueContainer instance
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # Create the molecule if it does not exist.
        mol_cont = return_molecule(generate_spin_id(pipe_name=pipe, mol_name=mol_name), pipe=pipe)
        if mol_cont == None:
            mol_cont = create_molecule(mol_name=mol_name, pipe=pipe)

        # Add the residue.
        mol_cont.res.add_item(res_num=res_num, res_name=res_name)

        # Alias the residue.
        res = mol_cont.res[-1]

        # Update the private metadata.
        if len(mol_cont.res) == 2:
            metadata_cleanup(mol_index=mol_cont._mol_index, pipe=pipe)
        else:
            metadata_cleanup(mol_index=mol_cont._mol_index, res_index=len(mol_cont.res)-1, pipe=pipe)
        metadata_update(mol_index=mol_cont._mol_index, res_index=len(mol_cont.res)-1, pipe=pipe)

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)

    # Return the residue.
    return res


def create_pseudo_spin(spin_name=None, spin_num=None, res_id=None, members=None, averaging=None, pipe=None):
    """Add a pseudo-atom spin container into the relax data store.

    @param spin_name:   The name of the new pseudo-spin.
    @type spin_name:    str
    @param spin_num:    The identification number of the new spin.
    @type spin_num:     int
    @param res_id:      The molecule and residue identification string.
    @type res_id:       str
    @keyword pipe:      The data pipe to add the spin to.  Defaults to the current data pipe.
    @type pipe:         str or None
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test if the current data pipe exists.
    pipes.test()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # Split up the selection string.
        mol_token, res_token, spin_token = tokenise(res_id)

        # Disallow spin selections.
        if spin_token != None:
            raise RelaxSpinSelectDisallowError

        # Get the residue container to add the spin to.
        if res_id:
            res_to_cont, mol_index, res_index = return_residue(res_id, pipe=pipe, indices=True)
            if res_to_cont == None:
                raise RelaxError("The residue in " + repr(res_id) + " does not exist in the current data pipe.")
        else:
            res_to_cont = dp.mol[0].res[0]
            mol_index = 0
            res_index = 0

        # Check the averaging technique.
        if averaging not in ['linear']:
            raise RelaxError("The '%s' averaging technique is unknown." % averaging)

        # Get the spin positions.
        positions = []
        for atom in members:
            # Get the spin container.
            spin = return_spin(atom, pipe=pipe)

            # Test that the spin exists.
            if spin == None:
                raise RelaxNoSpinError(atom)

            # Test the position.
            if not hasattr(spin, 'pos') or spin.pos == None:
                raise RelaxError("Positional information is not available for the atom '%s'." % atom)

            # Alias the position.
            pos = spin.pos

            # Convert to a list of lists if not already.
            multi_model = True
            if type(pos[0]) in [float, float64]:
                multi_model = False
                pos = [pos]

            # Store the position.
            positions.append([])
            for i in range(len(pos)):
                positions[-1].append(pos[i].tolist())

        # Now add the pseudo-spin name to the spins belonging to it (after the tests).
        for atom in members:
            # Get the spin container.
            spin = return_spin(atom, pipe=pipe)

            # Add the pseudo-spin number and name.
            if res_id:
                spin.pseudo_name = res_id + '@' + spin_name
            else:
                spin.pseudo_name = '@' + spin_name
            spin.pseudo_num = spin_num

        # Add the spin.
        res_to_cont.spin.add_item(spin_num=spin_num, spin_name=spin_name)
        spin = res_to_cont.spin[-1]
        spin_index = len(res_to_cont.spin) - 1

        # Set the pseudo-atom spin container attributes.
        spin.averaging = averaging
        spin.members = members
        if averaging == 'linear':
            # Average pos.
            ave = linear_ave(positions)

            # Convert to the correct structure.
            if multi_model:
                spin.pos = ave
            else:
                spin.pos = ave[0]

        # Update the private metadata.
        metadata_cleanup(mol_index=mol_index, res_index=res_index, pipe=pipe)
        metadata_update(mol_index=mol_index, res_index=res_index, pipe=pipe)

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)


def create_spin(spin_num=None, spin_name=None, res_num=None, res_name=None, mol_name=None, pipe=None):
    """Add a spin into the relax data store (and molecule and residue if necessary).

    @keyword spin_num:  The number of the new spin.
    @type spin_num:     int
    @keyword spin_name: The name of the new spin.
    @type spin_name:    str
    @keyword res_num:   The number of the residue to add the spin to.
    @type res_num:      int
    @keyword res_name:  The name of the residue to add the spin to.
    @type res_name:     str
    @keyword mol_name:  The name of the molecule to add the spin to.
    @type mol_name:     str
    @keyword pipe:      The data pipe to add the spin to.  Defaults to the current data pipe.
    @type pipe:         str or None
    @return:            The newly created spin.
    @rtype:             SpinContainer instance
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test if the current data pipe exists.
    pipes.test()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # Create the molecule if it does not exist.
        mol_index = index_molecule(mol_name, pipe=pipe)
        if mol_index == None:
            create_molecule(mol_name=mol_name, pipe=pipe)
            mol_index = len(dp.mol) - 1

        # Create the residue if it does not exist.
        res_index = index_residue(res_num=res_num, res_name=res_name, mol_index=mol_index, pipe=pipe)
        if res_index == None:
            create_residue(mol_name=mol_name, res_num=res_num, res_name=res_name, pipe=pipe)
            res_index = len(dp.mol[mol_index].res) - 1

        # Alias the residue.
        res_cont = dp.mol[mol_index].res[res_index]

        # Rename the spin, if only a single one exists and it is empty.
        if len(res_cont.spin) == 1 and res_cont.spin[0].is_empty():
            spin_cont = res_cont.spin[0]
            spin_cont.name = spin_name
            spin_cont.num = spin_num

        # Otherwise add the spin.
        else:
            res_cont.spin.add_item(spin_num=spin_num, spin_name=spin_name)
            spin_cont = res_cont.spin[-1]

        # The spin index and id.
        spin_index = len(res_cont.spin) - 1
        spin_id = generate_spin_id(pipe_cont=dp, mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name)

        # Update the private metadata.
        if len(res_cont.spin) == 2:
            metadata_cleanup(mol_index=mol_index, res_index=res_index, pipe=pipe)
        else:
            metadata_cleanup(mol_index=mol_index, res_index=res_index, spin_index=spin_index, pipe=pipe)
        metadata_update(mol_index=mol_index, res_index=res_index, spin_index=spin_index, pipe=pipe)

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)

    # Return the spin.
    return spin_cont


def convert_from_global_index(global_index=None, pipe=None):
    """Convert the global index into the molecule, residue, and spin indices.

    @param global_index:        The global spin index, spanning the molecule and residue containers.
    @type global_index:         int
    @param pipe:                The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:                 str
    @return:                    The corresponding molecule, residue, and spin indices.
    @rtype:                     tuple of int
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Loop over the spins.
    spin_num = 0
    for mol_index, res_index, spin_index in spin_index_loop(pipe=pipe):
        # Match to the global index.
        if spin_num == global_index:
            return mol_index, res_index, spin_index

        # Increment the spin number.
        spin_num = spin_num + 1


def delete_molecule(mol_id=None):
    """Function for deleting molecules from the current data pipe.

    @param mol_id:  The molecule identifier string.
    @type mol_id:   str
    """

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # Split up the selection string.
        mol_token, res_token, spin_token = tokenise(mol_id)

        # Disallow spin selections.
        if spin_token != None:
            raise RelaxSpinSelectDisallowError

        # Disallow residue selections.
        if res_token != None:
            raise RelaxResSelectDisallowError

        # Parse the token.
        molecules = parse_token(mol_token)

        # List of indices to delete.
        indices = []

        # Loop over the molecules.
        for i in range(len(cdp.mol)):
            # Remove the residue is there is a match.
            if cdp.mol[i].name in molecules:
                indices.append(i)

        # Reverse the indices.
        indices.reverse()

        # First prune the metadata.
        for index in indices:
            metadata_prune(mol_index=index)

        # Delete the molecules.
        for index in indices:
            cdp.mol.pop(index)

        # Create an empty residue container if no residues remain.
        if len(cdp.mol) == 0:
            cdp.mol.add_item()

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)


def delete_residue(res_id=None):
    """Function for deleting residues from the current data pipe.

    @param res_id:  The molecule and residue identifier string.
    @type res_id:   str
    """

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # Split up the selection string.
        mol_token, res_token, spin_token = tokenise(res_id)

        # Disallow spin selections.
        if spin_token != None:
            raise RelaxSpinSelectDisallowError

        # Parse the tokens.
        residues = parse_token(res_token)

        # Molecule loop.
        for mol in molecule_loop(res_id):
            # List of indices to delete.
            indices = []

            # Loop over the residues of the molecule.
            for i in range(len(mol.res)):
                # Remove the residue is there is a match.
                if mol.res[i].num in residues or mol.res[i].name in residues:
                    indices.append(i)

            # Reverse the indices.
            indices.reverse()

            # First prune the metadata.
            for index in indices:
                metadata_prune(mol_index=mol._mol_index, res_index=index)

            # Delete the residues.
            for index in indices:
                mol.res.pop(index)

            # Create an empty residue container if no residues remain.
            if len(mol.res) == 0:
                mol.res.add_item()

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)


def delete_spin(spin_id=None):
    """Function for deleting spins from the current data pipe.

    @param spin_id: The molecule, residue, and spin identifier string.
    @type spin_id:  str
    """

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:

        # Split up the selection string.
        mol_token, res_token, spin_token = tokenise(spin_id)

        # Parse the tokens.
        spins = parse_token(spin_token)

        # Residue loop.
        for res in residue_loop(spin_id):
            # List of indices to delete.
            indices = []

            # Loop over the spins of the residue.
            for i in range(len(res.spin)):
                # Store the spin indices for deletion.
                if res.spin[i].num in spins or res.spin[i].name in spins:
                    indices.append(i)

            # Reverse the indices.
            indices.reverse()

            # First prune the metadata.
            for index in indices:
                metadata_prune(mol_index=res._mol_index, res_index=res._res_index, spin_index=index)

            # Delete the spins.
            for index in indices:
                res.spin.pop(index)

            # Create an empty spin container if no spins remain.
            if len(res.spin) == 0:
                res.spin.add_item()

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)


def display_molecule(mol_id=None):
    """Function for displaying the information associated with the molecule.

    @param mol_id:  The molecule identifier string.
    @type mol_id:   str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(mol_id)

    # Disallowed selections.
    if res_token != None:
        raise RelaxResSelectDisallowError
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # The molecule selection string.
    if mol_token:
        mol_sel = '#' + mol_token
    else:
        mol_sel = None

    # Print a header.
    print("\n\n%-15s %-15s" % ("Molecule", "Number of residues"))

    # Molecule loop.
    for mol in molecule_loop(mol_sel):
        # Print the molecule data.
        print("%-15s %-15s" % (mol.name, repr(len(mol.res))))


def display_residue(res_id=None):
    """Function for displaying the information associated with the residue.

    @param res_id:  The molecule and residue identifier string.
    @type res_id:   str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Print a header.
    print("\n\n%-15s %-15s %-15s %-15s" % ("Molecule", "Res number", "Res name", "Number of spins"))

    # Residue loop.
    for res, mol_name in residue_loop(res_id, full_info=True):
        print("%-15s %-15s %-15s %-15s" % (mol_name, repr(res.num), res.name, repr(len(res.spin))))


def display_spin(spin_id=None):
    """Function for displaying the information associated with the spin.

    @param spin_id: The molecule and residue identifier string.
    @type spin_id:  str
    """

    # Print a header.
    print("\n\n%-15s %-15s %-15s %-15s %-15s" % ("Molecule", "Res number", "Res name", "Spin number", "Spin name"))

    # Spin loop.
    for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
        # Print the residue data.
        print("%-15s %-15s %-15s %-15s %-15s" % (mol_name, repr(res_num), res_name, repr(spin.num), spin.name))


def exists_mol_res_spin_data(pipe=None):
    """Function for determining if any molecule-residue-spin data exists.

    @keyword pipe:      The data pipe in which the molecule-residue-spin data will be checked for.
    @type pipe:         str
    @return:            The answer to the question about the existence of data.
    @rtype:             bool
    """

    # The current data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # The molecule, residue, spin object stack is empty.
    if dp.mol.is_empty():
        return False

    # Otherwise.
    return True


def find_index(selection=None, pipe=None, global_index=True):
    """Find and return the spin index or indices for the selection string.

    @keyword selection:     The spin selection identifier.
    @type selection:        str
    @keyword pipe:          The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:             str
    @keyword global_index:  A flag which if True will cause the global index to be returned.  If False, then the molecule, residue, and spin indices will be returned.
    @type global_index:     bool
    @return:                The global spin index or the molecule, residue, and spin indices.
    @rtype:                 int or tuple of 3 int
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Parse the selection string.
    select_obj = Selection(selection)

    # Init the mol and global index.
    global_i = -1
    mol_index = -1

    # Loop over the molecules.
    for mol in dp.mol:
        # Increment the molecule index.
        mol_index = mol_index + 1

        # Init the residue index.
        res_index = -1

        # Loop over the residues.
        for res in mol.res:
            # Increment the residue index.
            res_index = res_index + 1

            # Init the residue index.
            spin_index = -1

            # Loop over the spins.
            for spin in res.spin:
                # Increment the spin and global index.
                spin_index = spin_index + 1
                global_i = global_i + 1

                # Stop if the spin matches the selection.
                if select_obj.contains_spin(spin_num=spin.num, spin_name=spin.name, res_num=res.num, res_name=res.name, mol=mol.name):
                    # Return the indices.
                    if global_index:
                        return global_i
                    else:
                        return mol_index, res_index, spin_index


def first_residue_num(selection=None):
    """Determine the first residue number.

    @return:    The number of the first residue.
    @rtype:     int
    """

    # Get the molecule.
    mol = return_molecule(selection)

    # The first residue number.
    return mol.res[0].num


def generate_spin_id(pipe_cont=None, pipe_name=None, mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None):
    """Generate the spin selection string.

    @keyword pipe_cont: The data pipe object.
    @type pipe_cont:    PipeContainer instance
    @keyword pipe_name: The data pipe name.
    @type pipe_name:    str
    @keyword mol_name:  The molecule name.
    @type mol_name:     str or None
    @keyword res_num:   The residue number.
    @type res_num:      int or None
    @keyword res_name:  The residue name.
    @type res_name:     str or None
    @keyword spin_num:  The spin number.
    @type spin_num:     int or None
    @keyword spin_name: The spin name.
    @type spin_name:    str or None
    @return:            The spin identification string.
    @rtype:             str
    """

    # The data pipe.
    if pipe_cont == None:
        pipe_cont = pipes.get_pipe(pipe_name)

    # Init.
    id = ""

    # Molecule name and container.
    if mol_name != None:
        id = id + "#" + mol_name

    # Residue data.
    res_num_id = ''
    res_name_id = ''
    if res_num != None:
        res_num_id = id + ":" + str(res_num)
        res_num_exists = res_num_id in pipe_cont.mol._spin_id_lookup
    if res_name != None:
        res_name_id = id + ":" + res_name
        res_name_exists = res_name_id in pipe_cont.mol._spin_id_lookup

    # Select between the name and number, defaulting to the residue number if needed.
    if res_name != None and res_num != None:
        if res_num_exists and res_name_exists:
            id = res_num_id
        elif not res_num_exists or not res_name_exists:
            id = res_num_id
        elif res_num_exists:
            id = res_num_id
        elif res_name_exists:
            id = res_name_id
        elif res_num != None:
            id = res_num_id
        elif res_name != None:
            id = res_name_id
    elif res_num != None:
        id = res_num_id
    elif res_name != None:
        id = res_name_id

    # Spin data.
    spin_num_id = ''
    spin_name_id = ''
    spin_num_exists = False
    spin_name_exists = False
    if spin_num != None:
        spin_num_id = id + "@" + str(spin_num)
        spin_num_exists = spin_num_id in pipe_cont.mol._spin_id_lookup
    if spin_name != None:
        spin_name_id = id + "@" + spin_name
        spin_name_exists = spin_name_id in pipe_cont.mol._spin_id_lookup

    # Select between the name and number, defaulting to the spin name if needed.
    if spin_name != None and spin_num != None:
        if spin_num_exists and spin_name_exists:
            id = spin_name_id
        elif not spin_num_exists or not spin_name_exists:
            id = spin_name_id
        elif spin_name_exists:
            id = spin_name_id
        elif spin_num_exists:
            id = spin_num_id
        elif spin_name != None:
            id = spin_name_id
        elif spin_num != None:
            id = spin_num_id
    elif spin_name != None:
        id = spin_name_id
    elif spin_num != None:
        id = spin_num_id

    # Return the full spin ID string.
    return id


def generate_spin_id_data_array(data=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None):
    """Generate the spin selection string from the given data array.

    @param data:            An array containing the molecule, residue, and/or spin data.
    @type data:             list of str
    @param mol_name_col:    The column containing the molecule name information.
    @type mol_name_col:     int or None
    @param res_name_col:    The column containing the residue name information.
    @type res_name_col:     int or None
    @param res_num_col:     The column containing the residue number information.
    @type res_num_col:      int or None
    @param spin_name_col:   The column containing the spin name information.
    @type spin_name_col:    int or None
    @param spin_num_col:    The column containing the spin number information.
    @type spin_num_col:     int or None
    @return:                The spin identification string.
    @rtype:                 str
    """

    # Init.
    id = ""

    # Molecule data.
    if mol_name_col and data[mol_name_col-1] not in [None, 'None']:
        id = id + "#" + data[mol_name_col-1]

    # Residue data.
    if res_num_col and data[res_num_col-1] not in [None, 'None']:
        id = id + ":" + str(data[res_num_col-1])
    elif res_name_col and data[res_name_col-1] not in [None, 'None']:
        id = id + ":" + data[res_name_col-1]

    # Spin data.
    if spin_num_col and data[spin_num_col-1] not in [None, 'None']:
        id = id + "@" + str(data[spin_num_col-1])
    elif spin_name_col and data[spin_name_col-1] not in [None, 'None']:
        id = id + "@" + data[spin_name_col-1]

    # Return the spin id string.
    return id


def generate_spin_id_unique(pipe_cont=None, pipe_name=None, mol=None, res=None, spin=None, mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None):
    """Generate a list of spin ID variants for the given set of molecule, residue and spin indices.

    @keyword pipe_cont: The data pipe object.
    @type pipe_cont:    PipeContainer instance
    @keyword pipe_name: The data pipe name.
    @type pipe_name:    str
    @keyword mol:       The molecule container.
    @type mol:          MoleculeContainer instance
    @keyword res:       The residue container.
    @type res:          ResidueContainer instance
    @keyword spin:      The spin container.
    @type spin:         SpinContainer instance
    @keyword mol_name:  The molecule name (an alternative to the molecule container).
    @type mol_name:     str or None
    @keyword res_num:   The residue number (an alternative to the residue container).
    @type res_num:      int or None
    @keyword res_name:  The residue name (an alternative to the residue container).
    @type res_name:     str or None
    @keyword spin_num:  The spin number (an alternative to the spin container).
    @type spin_num:     int or None
    @keyword spin_name: The spin name (an alternative to the spin container).
    @type spin_name:    str or None
    @return:            The unique spin ID.
    @rtype:             str
    """

    # The data pipe.
    if pipe_cont == None:
        pipe_cont = pipes.get_pipe(pipe_name)

    # Get the containers if needed.
    if mol == None:
        mol = return_molecule_by_name(pipe_cont=pipe_cont, mol_name=mol_name)
    if mol != None and res == None:
        if res_name != None or res_num != None:
            res = return_residue_by_info(mol=mol, res_name=res_name, res_num=res_num)
        elif len(mol.res) == 1:
            res = mol.res[0]
    if res != None and spin == None:
        if spin_name != None or spin_num != None:
            spin = return_spin_by_info(res=res, spin_name=spin_name, spin_num=spin_num)
        elif len(res.spin) == 1:
            spin = res.spin[0]

    # The info.
    if mol:
        mol_name = mol.name
    if res:
        res_name = res.name
        res_num = res.num
    if spin:
        spin_name = spin.name
        spin_num = spin.num

    # Unique info.
    unique_res_name = True
    if res and res.name != None and mol._res_name_count[res.name] > 1:
        unique_res_name = False
    unique_res_num = True
    if res and res.num != None and mol._res_num_count[res.num] > 1:
        unique_res_num = False
    unique_spin_name = True
    if spin and spin.name != None and res._spin_name_count[spin.name] > 1:
        unique_spin_name = False
    unique_spin_num = True
    if spin and spin.num != None and res._spin_num_count[spin.num] > 1:
        unique_spin_num = False

    # The unique ID.
    if unique_res_num and unique_spin_name:
        return generate_spin_id(pipe_cont=pipe_cont, mol_name=mol_name, res_num=res_num, spin_name=spin_name)
    if unique_res_num and unique_spin_num:
        return generate_spin_id(pipe_cont=pipe_cont, mol_name=mol_name, res_num=res_num, spin_num=spin_num)
    if unique_res_name and unique_spin_num:
        return generate_spin_id(pipe_cont=pipe_cont, mol_name=mol_name, res_name=res_name, spin_num=spin_num)
    if unique_res_name and unique_spin_name:
        return generate_spin_id(pipe_cont=pipe_cont, mol_name=mol_name, res_name=res_name, spin_name=spin_name)


def get_molecule_ids(selection=None):
    """Return a list of the molecule ID strings.

    @param selection:   The molecule selection identifier.
    @type selection:    str
    @return:            The molecule ID strings.
    @rtype:             list of str
    """

    # No data pipes, so return an empty list without throwing an error.
    if not pipes.cdp_name():
        return []

    # Loop over the molecules, append the ID of each within the selection.
    mol_ids = []
    for mol, mol_id in molecule_loop(selection, return_id=True):
        mol_ids.append(mol_id)

    # Return the IDs.
    return mol_ids


def get_molecule_names(selection=None):
    """Return a list of the molecule names.

    @param selection:   The molecule selection identifier.
    @type selection:    str
    @return:            The molecule names.
    @rtype:             list of str
    """

    # No data pipes, so return an empty list without throwing an error.
    if not pipes.cdp_name():
        return []

    # Loop over the molecules, append the name of each within the selection.
    mol_names = []
    for mol in molecule_loop(selection):
        mol_names.append(mol.name)

    # Return the names.
    return mol_names


def get_residue_ids(selection=None):
    """Return a list of the residue ID strings.

    @param selection:   The molecule and residue selection identifier.
    @type selection:    str
    @return:            The residue ID strings.
    @rtype:             list of str
    """

    # No data pipes, so return an empty list without throwing an error.
    if not pipes.cdp_name():
        return []

    # Loop over the residues, appending the ID of each within the selection.
    res_ids = []
    for res, res_id in residue_loop(selection, return_id=True):
        res_ids.append(res_id)

    # Return the IDs.
    return res_ids


def get_residue_names(selection=None):
    """Return a list of the residue names.

    @param selection:   The molecule and residue selection identifier.
    @type selection:    str
    @return:            The residue names.
    @rtype:             list of str
    """

    # No data pipes, so return an empty list without throwing an error.
    if not pipes.cdp_name():
        return []

    # Loop over the residues, appending the name of each within the selection.
    res_names = []
    for res in residue_loop(selection):
        res_names.append(res.name)

    # Return the names.
    return res_names


def get_residue_nums(selection=None):
    """Return a list of the residue numbers.

    @param selection:   The molecule and residue selection identifier.
    @type selection:    str
    @return:            The residue numbers.
    @rtype:             list of str
    """

    # No data pipes, so return an empty list without throwing an error.
    if not pipes.cdp_name():
        return []

    # Loop over the residues, appending the number of each within the selection.
    res_nums = []
    for res in residue_loop(selection):
        res_nums.append(res.num)

    # Return the numbers.
    return res_nums


def get_spin_ids(selection=None):
    """Return a list of the spin ID strings.

    @param selection:   The molecule and spin selection identifier.
    @type selection:    str
    @return:            The spin ID strings.
    @rtype:             list of str
    """

    # No data pipes, so return an empty list without throwing an error.
    if not pipes.cdp_name():
        return []

    # Loop over the spins, appending the ID of each within the selection.
    spin_ids = []
    for spin, spin_id in spin_loop(selection, return_id=True):
        spin_ids.append(spin_id)

    # Return the IDs.
    return spin_ids


def index_molecule(mol_name=None, pipe=None):
    """Return the index of the molecule of the given name.

    @keyword mol_name:  The name of the molecule.
    @type mol_name:     str or None
    @keyword pipe:      The data pipe, defaulting to the current data pipe.
    @type pipe:         str or None
    @return:            The index of the molecule, if it exists.
    @rtype:             int or None
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Single molecule and no name given.
    if mol_name == None and len(dp.mol) == 1:
        return 0

    # Loop over the molecules.
    i = 0
    for mol in dp.mol:
        # A match.
        if mol.name == mol_name:
            return i

        # Increment the index.
        i += 1

    # Nothing found.
    return None


def index_residue(res_num=None, res_name=None, mol_index=None, pipe=None):
    """Return the index of the residue.

    @keyword res_num:   The number of the residue.
    @type res_num:      int
    @keyword res_name:  The name of the residue.
    @type res_name:     str
    @keyword mol_index: The index of the molecule.
    @type mol_index:    str
    @keyword pipe:      The data pipe, defaulting to the current data pipe.
    @type pipe:         str or None
    @return:            The index of the residue, if it exists.
    @rtype:             int or None
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Single unnamed residue.
    if len(dp.mol[mol_index].res) == 1 and res_num == dp.mol[mol_index].res[0].num and res_name == dp.mol[mol_index].res[0].name:
        return 0

    # Loop over the residues.
    i = 0
    for res in dp.mol[mol_index].res:
        # A unique number match.
        if res_num != None and res.num == res_num:
            return i

        # Match names, if no number is given.
        if res_num == None and res_name != None and res.name == res_name:
            return i

        # Increment the index.
        i += 1

    # Nothing found.
    return None


def last_residue_num(selection=None):
    """Determine the last residue number.

    @param selection:   The molecule selection identifier.
    @type selection:    str
    @return:            The number of the last residue.
    @rtype:             int
    """

    # Get the molecule.
    mol = return_molecule(selection)

    # The last residue number.
    return mol.res[-1].num


def linear_ave(positions):
    """Perform linear averaging of the atomic positions.

    @param positions:   The atomic positions.  The first index is that of the positions to be averaged over.  The second index is over the different models.  The last index is over the x, y, and z coordinates.
    @type positions:    list of lists of numpy float arrays
    @return:            The averaged positions as a list of vectors.
    @rtype:             list of numpy float arrays
    """

    # Loop over the multiple models.
    ave = []
    for model_index in range(len(positions[0])):
        # Append an empty vector.
        ave.append(array([0.0, 0.0, 0.0]))

        # Loop over the x, y, and z coordinates.
        for coord_index in range(3):
            # Loop over the atomic positions.
            for atom_index in range(len(positions)):
                ave[model_index][coord_index] = ave[model_index][coord_index] + positions[atom_index][model_index][coord_index]

            # Average.
            ave[model_index][coord_index] = ave[model_index][coord_index] / len(positions)

    # Return the averaged positions.
    return ave


def metadata_cleanup(mol_index=None, res_index=None, spin_index=None, pipe=None):
    """Prune all of the metadata matching the given indices.

    @keyword mol_index:     The index of the molecule to prune.  If not supplied, all molecules will be pruned.
    @type mol_index:        int or None
    @keyword res_index:     The index of the residue to prune.  If not supplied, all residues of the matching molecules will be pruned.
    @type res_index:        int or None
    @keyword spin_index:    The index of the spin to prune.  If not supplied, all spins of the matching residues will be pruned.
    @type spin_index:       int or None
    @keyword pipe:          The data pipe to update, defaulting to the current data pipe.
    @type pipe:             str or None
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Update the metadata info counts.
    metadata_counts(pipe_cont=dp)

    # Loop over the molecules.
    to_remove = []
    for i in range(len(dp.mol)):
        # Molecule skipping.
        if mol_index != None and mol_index != i:
            continue

        # Alias.
        mol = dp.mol[i]

        # Loop over the residues.
        for j in range(len(mol.res)):
            # Residue skipping.
            if res_index != None and res_index != j:
                continue

            # Alias.
            res = mol.res[j]

            # Loop over the spins.
            for k in range(len(res.spin)):
                # Spin skipping.
                if spin_index != None and spin_index != k:
                    continue

                # Alias.
                spin = res.spin[k]

                # The list of IDs to remove.
                to_remove = spin_id_variants_cleanup(dp=dp, mol_index=i, res_index=j, spin_index=k)

                # ID removal.
                for spin_id in to_remove:
                    # Blank IDs.
                    if spin_id == '':
                        continue

                    # Remove from the list in the spin container itself.
                    if spin_id in spin._spin_ids:
                        spin._spin_ids.pop(spin._spin_ids.index(spin_id))

                    # Remove the IDs from the look up table.
                    if spin_id in dp.mol._spin_id_lookup:
                        dp.mol._spin_id_lookup.pop(spin_id)


def metadata_counts(pipe_cont=None):
    """Update the molecule, residue, and spin name and number count metadata.

    @keyword pipe_cont: The data pipe object.
    @type pipe_cont:    PipeContainer instance
    """

    # The top level counts.
    pipe_cont.mol._res_name_count = {}
    pipe_cont.mol._res_num_count = {}
    pipe_cont.mol._spin_name_count = {}
    pipe_cont.mol._spin_num_count = {}

    # Pre-parse:  Update the metadata for determining if names and numbers already exist.
    for i in range(len(pipe_cont.mol)):
        # Alias.
        mol = pipe_cont.mol[i]

        # The molecule level counts.
        mol._res_name_count = {}
        mol._res_num_count = {}
        mol._spin_name_count = {}
        mol._spin_num_count = {}

        # Loop over the residues.
        for j in range(len(mol.res)):
            # Alias.
            res = mol.res[j]

            # Count the residue names.
            if res.name != None:
                # Top level.
                if res.name not in pipe_cont.mol._res_name_count:
                    pipe_cont.mol._res_name_count[res.name] = 1
                else:
                    pipe_cont.mol._res_name_count[res.name] += 1

                # Molecule level.
                if res.name not in mol._res_name_count:
                    mol._res_name_count[res.name] = 1
                else:
                    mol._res_name_count[res.name] += 1

            # Count the residue numbers.
            if res.num != None:
                # Top level.
                if res.num not in pipe_cont.mol._res_num_count:
                    pipe_cont.mol._res_num_count[res.num] = 1
                else:
                    pipe_cont.mol._res_num_count[res.num] += 1

                # Molecule level.
                if res.num not in mol._res_num_count:
                    mol._res_num_count[res.num] = 1
                else:
                    mol._res_num_count[res.num] += 1

            # The residue level counts.
            res._spin_name_count = {}
            res._spin_num_count = {}

            # Loop over the spins.
            for k in range(len(res.spin)):
                # Alias.
                spin = res.spin[k]

                # Count the spin names.
                if spin.name != None:
                    # Top level.
                    if spin.name not in pipe_cont.mol._spin_name_count:
                        pipe_cont.mol._spin_name_count[spin.name] = 1
                    else:
                        pipe_cont.mol._spin_name_count[spin.name] += 1

                    # Molecule level.
                    if spin.name not in mol._spin_name_count:
                        mol._spin_name_count[spin.name] = 1
                    else:
                        mol._spin_name_count[spin.name] += 1

                    # Residue level.
                    if spin.name not in res._spin_name_count:
                        res._spin_name_count[spin.name] = 1
                    else:
                        res._spin_name_count[spin.name] += 1

                # Count the spin numbers.
                if spin.num != None:
                    # Top level.
                    if spin.num not in pipe_cont.mol._spin_num_count:
                        pipe_cont.mol._spin_num_count[spin.num] = 1
                    else:
                        pipe_cont.mol._spin_num_count[spin.num] += 1

                    # Molecule level.
                    if spin.num not in mol._spin_num_count:
                        mol._spin_num_count[spin.num] = 1
                    else:
                        mol._spin_num_count[spin.num] += 1

                    # Residue level.
                    if spin.num not in res._spin_num_count:
                        res._spin_num_count[spin.num] = 1
                    else:
                        res._spin_num_count[spin.num] += 1


def metadata_prune(mol_index=None, res_index=None, spin_index=None, pipe=None):
    """Prune all of the metadata matching the given indices.

    @keyword mol_index:     The index of the molecule to prune.  If not supplied, all molecules will be pruned.
    @type mol_index:        int or None
    @keyword res_index:     The index of the residue to prune.  If not supplied, all residues of the matching molecules will be pruned.
    @type res_index:        int or None
    @keyword spin_index:    The index of the spin to prune.  If not supplied, all spins of the matching residues will be pruned.
    @type spin_index:       int or None
    @keyword pipe:          The data pipe to update, defaulting to the current data pipe.
    @type pipe:             str or None
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Update the metadata info counts.
    metadata_counts(pipe_cont=dp)

    # Loop over the molecules.
    to_remove = []
    for i in range(len(dp.mol)):
        # Molecule skipping.
        if mol_index != None and mol_index != i:
            continue

        # Alias.
        mol = dp.mol[i]

        # Loop over the residues.
        for j in range(len(mol.res)):
            # Residue skipping.
            if res_index != None and res_index != j:
                continue

            # Alias.
            res = mol.res[j]

            # Loop over the spins.
            for k in range(len(res.spin)):
                # Spin skipping.
                if spin_index != None and spin_index != k:
                    continue

                # Alias.
                spin = res.spin[k]

                # The list of IDs to remove.
                to_remove = spin_id_variants_prune(dp=dp, mol_index=i, res_index=j, spin_index=k)

                # ID removal.
                for spin_id in to_remove:
                    # Blank IDs.
                    if spin_id == '':
                        continue

                    # Remove from the list in the spin container itself.
                    if spin_id in spin._spin_ids:
                        spin._spin_ids.pop(spin._spin_ids.index(spin_id))

                    # Remove the IDs from the look up table.
                    if spin_id in dp.mol._spin_id_lookup:
                        dp.mol._spin_id_lookup.pop(spin_id)


def metadata_update(mol_index=None, res_index=None, spin_index=None, pipe=None):
    """Update all of the private look up metadata for the given containers.

    @keyword mol_index:     The index of the molecule to update.  If not supplied, all molecules will be updated.
    @type mol_index:        int or None
    @keyword res_index:     The index of the residue to update.  If not supplied, all residues will be updated.
    @type res_index:        int or None
    @keyword spin_index:    The index of the spin to update.  If not supplied, all spins will be updated.
    @type spin_index:       int or None
    @keyword pipe:          The data pipe to update, defaulting to the current data pipe.
    @type pipe:             str or None
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Update the metadata info counts.
    metadata_counts(pipe_cont=dp)

    # Loop over the molecules.
    for i in range(len(dp.mol)):
        # Molecule skipping.
        if mol_index != None and mol_index != i:
            continue

        # Alias.
        mol = dp.mol[i]

        # Update the molecule metadata.
        mol._mol_index = i

        # Loop over the residues.
        for j in range(len(mol.res)):
            # Residue skipping.
            if res_index != None and res_index != j:
                continue

            # Alias.
            res = mol.res[j]

            # Update the residue metadata.
            res._mol_name = mol.name
            res._mol_index = i
            res._res_index = j

            # Loop over the spins.
            for k in range(len(res.spin)):
                # Spin skipping.
                if spin_index != None and spin_index != k:
                    continue

                # Alias.
                spin = res.spin[k]

                # Update the spin metadata.
                spin._mol_name = mol.name
                spin._mol_index = i
                spin._res_name = res.name
                spin._res_num = res.num
                spin._res_index = j
                spin._spin_index = k

                # The list of IDs to store.
                spin_ids = spin_id_variants(dp=dp, mol_index=i, res_index=j, spin_index=k)

                # ID storage.
                spin._spin_ids = []
                for spin_id in spin_ids:
                    # Blank IDs.
                    if spin_id == '':
                        continue

                    # Store the list in the spin container itself.
                    spin._spin_ids.append(spin_id)

                    # Update the look up table.
                    dp.mol._spin_id_lookup[spin_id] = [i, j, k]


def molecule_loop(selection=None, pipe=None, return_id=False):
    """Generator function for looping over all the molecules of the given selection.

    @param selection:   The molecule selection identifier.
    @type selection:    str
    @param pipe:        The data pipe containing the molecule.  Defaults to the current data pipe.
    @type pipe:         str
    @keyword return_id: A flag which if True will cause the molecule identification string of the molecule spin to be returned in addition to the spin container.
    @type return_id:    bool
    @return:            The molecule specific data container.
    @rtype:             instance of the MoleculeContainer class.
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Test for the presence of data, and end the execution of this function if there is none.
    if not exists_mol_res_spin_data(pipe=pipe):
        return

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    for mol in dp.mol:
        # Skip the molecule if there is no match to the selection.
        if not select_obj.contains_mol(mol.name):
            continue

        # Generate the spin id.
        if return_id:
            mol_id = generate_spin_id(pipe_cont=dp, mol_name=mol.name)

        # Yield the molecule data container.
        if return_id:
            yield mol, mol_id
        else:
            yield mol


def name_molecule(mol_id, name=None, force=False):
    """Name the molecules.

    @param mol_id:      The molecule identification string.
    @type mol_id:       str
    @param name:        The new molecule name.
    @type name:         str
    @keyword force:     A flag which if True will cause the named molecule to be renamed.
    @type force:        bool
    """

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:

        # Get the single molecule data container.
        mol = return_molecule(mol_id)

        # Disallow residue and spin selections.
        select_obj = Selection(mol_id)
        if select_obj.has_residues():
            raise RelaxResSelectDisallowError
        if select_obj.has_spins():
            raise RelaxSpinSelectDisallowError

        # Name the molecule is there is a single match.
        if mol:
            if mol.name and not force:
                warn(RelaxWarning("The molecule '%s' is already named.  Set the force flag to rename." % mol_id))
            else:
                mol.name = name

            # Update the private metadata.
            metadata_cleanup(mol_index=mol._mol_index)
            metadata_update(mol_index=mol._mol_index)

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)


def name_residue(res_id, name=None, force=False):
    """Name the residues.

    @param res_id:      The residue identification string.
    @type res_id:       str
    @param name:        The new residue name.
    @type name:         str
    @keyword force:     A flag which if True will cause the named residue to be renamed.
    @type force:        bool
    """

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # Disallow spin selections.
        select_obj = Selection(res_id)
        if select_obj.has_spins():
            raise RelaxSpinSelectDisallowError

        # Rename the matching residues.
        for res, mol_name in residue_loop(res_id, full_info=True):
            if res.name and not force:
                warn(RelaxWarning("The residue '%s' is already named.  Set the force flag to rename." % generate_spin_id(mol_name=mol_name, res_num=res.num, res_name=res.name)))
            else:
                res.name = name

                # Update the private metadata.
                metadata_cleanup(mol_index=res._mol_index, res_index=res._res_index)
                metadata_update(mol_index=res._mol_index, res_index=res._res_index)

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)


def name_spin(spin_id=None, name=None, pipe=None, force=False):
    """Name the spins.

    @keyword spin_id:   The spin identification string.
    @type spin_id:      str
    @keyword name:      The new spin name.
    @type name:         str
    @param pipe:        The data pipe to operate on.  Defaults to the current data pipe.
    @type pipe:         str
    @keyword force:     A flag which if True will cause the named spin to be renamed.  If None, then the warning messages will not mention the need to change this flag to rename.
    @type force:        bool or None
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # Rename the matching spins.
        for spin, id in spin_loop(spin_id, pipe=pipe, return_id=True):
            if spin.name and force != True:
                if force == False:
                    warn(RelaxWarning("The spin '%s' is already named.  Set the force flag to rename." % id))
                else:
                    warn(RelaxWarning("The spin '%s' is already named." % id))
            else:
                spin.name = name

                # Update the private metadata.
                metadata_cleanup(mol_index=spin._mol_index, res_index=spin._res_index, spin_index=spin._spin_index)
                metadata_update(mol_index=spin._mol_index, res_index=spin._res_index, spin_index=spin._spin_index)

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)


def number_residue(res_id, number=None, force=False):
    """Number the residues.

    @param res_id:      The residue identification string.
    @type res_id:       str
    @param number:      The new residue number.
    @type number:       int
    @keyword force:     A flag which if True will cause the numbered residue to be renumbered.
    @type force:        bool
    """

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # Catch multiple numberings!
        i = 0
        for res in residue_loop(res_id):
            i = i + 1

        # Fail if multiple residues are numbered.
        if i > 1:
            raise RelaxError("The numbering of multiple residues is disallowed, each residue requires a unique number.")

        # Disallow spin selections.
        select_obj = Selection(res_id)
        if select_obj.has_spins():
            raise RelaxSpinSelectDisallowError

        # Rename the residue.
        for res, mol_name in residue_loop(res_id, full_info=True):
            if res.num and not force:
                warn(RelaxWarning("The residue '%s' is already numbered.  Set the force flag to renumber." % generate_spin_id(mol_name=mol_name, res_num=res.num, res_name=res.name)))
            else:
                res.num = number

                # Update the private metadata.
                metadata_cleanup(mol_index=res._mol_index, res_index=res._res_index)
                metadata_update(mol_index=res._mol_index, res_index=res._res_index)

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)


def number_spin(spin_id=None, number=None, force=False):
    """Number the spins.

    @param spin_id:     The spin identification string.
    @type spin_id:      str
    @param number:      The new spin number.
    @type number:       int
    @keyword force:     A flag which if True will cause the numbered spin to be renumbered.
    @type force:        bool
    """

    # Acquire the spin lock (data modifying function), and make sure it is finally released.
    status.spin_lock.acquire(sys._getframe().f_code.co_name)
    try:
        # Catch multiple renumberings!
        i = 0
        for spin in spin_loop(spin_id):
            i = i + 1

        # Fail if multiple spins are numbered.
        if number != None and i > 1:
            raise RelaxError("The numbering of multiple spins is disallowed, as each spin requires a unique number.")

        # Rename the spin.
        for spin, id in spin_loop(spin_id, return_id=True):
            if spin.num and not force:
                warn(RelaxWarning("The spin '%s' is already numbered.  Set the force flag to renumber." % id))
            else:
                spin.num = number

                # Update the private metadata.
                metadata_cleanup(mol_index=spin._mol_index, res_index=spin._res_index, spin_index=spin._spin_index)
                metadata_update(mol_index=spin._mol_index, res_index=spin._res_index, spin_index=spin._spin_index)

    # Release the lock.
    finally:
        status.spin_lock.release(sys._getframe().f_code.co_name)


def one_letter_code(res_names):
    """Convert the list of residue names into a string of one letter residue codes.

    Standard amino acids are converted to the one letter code.  Unknown residues are labelled as 'X'.


    @param res_names:   A list of residue names.
    @type res_names:    list or str
    @return:            The one letter codes for the residues.
    @rtype:             str
    """

    # The amino acid translation table.
    aa_table = [
                ['Alanine',         'ALA', 'A'],
                ['Arginine',        'ARG', 'R'],
                ['Asparagine',      'ASN', 'N'],
                ['Aspartic acid',   'ASP', 'D'],
                ['Cysteine',        'CYS', 'C'],
                ['Glutamic acid',   'GLU', 'E'],
                ['Glutamine',       'GLN', 'Q'],
                ['Glycine',         'GLY', 'G'],
                ['Histidine',       'HIS', 'H'],
                ['Isoleucine',      'ILE', 'I'],
                ['Leucine',         'LEU', 'L'],
                ['Lysine',          'LYS', 'K'],
                ['Methionine',      'MET', 'M'],
                ['Phenylalanine',   'PHE', 'F'],
                ['Proline',         'PRO', 'P'],
                ['Serine',          'SER', 'S'],
                ['Threonine',       'THR', 'T'],
                ['Tryptophan',      'TRP', 'W'],
                ['Tyrosine',        'TYR', 'Y'],
                ['Valine',          'VAL', 'V']
    ]

    # Translate.
    seq = ''
    for res in res_names:
        # Aa match.
        match = False
        for i in range(len(aa_table)):
            if res.upper() == aa_table[i][1]:
                seq = seq + aa_table[i][2]
                match = True
                break

        # No match.
        if not match:
            seq = seq + 'X'

    # Return the sequence.
    return seq


def residue_loop(selection=None, pipe=None, full_info=False, return_id=False):
    """Generator function for looping over all the residues of the given selection.

    @param selection:   The residue selection identifier.
    @type selection:    str
    @param pipe:        The data pipe containing the residue.  Defaults to the current data pipe.
    @type pipe:         str
    @param full_info:   A flag specifying if the amount of information to be returned.  If false, only the data container is returned.  If true, the molecule name, residue number, and residue name is additionally returned.
    @type full_info:    boolean
    @keyword return_id: A flag which if True will cause the molecule identification string of the molecule spin to be returned in addition to the spin container.
    @type return_id:    bool
    @return:            The residue specific data container and, if full_info=True, the molecule name.
    @rtype:             instance of the ResidueContainer class.  If full_info=True, the type is the tuple (ResidueContainer, str).
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Test for the presence of data, and end the execution of this function if there is none.
    if not exists_mol_res_spin_data(pipe=pipe):
        return

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    for mol in dp.mol:
        # Loop over the residues.
        for res in mol.res:
            # Skip the residue if there is no match to the selection.
            if not select_obj.contains_res(res_num=res.num, res_name=res.name, mol=mol.name):
                continue

            # Generate the spin id.
            if return_id:
                res_id = generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_num=res.num, res_name=res.name)

            # Yield the residue data container.
            if full_info and return_id:
                yield res, mol.name, res_id
            elif full_info:
                yield res, mol.name
            elif return_id:
                yield res, res_id
            else:
                yield res


def return_molecule(selection=None, pipe=None):
    """Function for returning the molecule data container of the given selection.

    @param selection:   The molecule selection identifier.
    @type selection:    str
    @param pipe:        The data pipe containing the molecule.  Defaults to the current data pipe.
    @type pipe:         str
    @return:            The molecule specific data container.
    @rtype:             instance of the MoleculeContainer class.
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    mol_num = 0
    mol_container = None
    for mol in dp.mol:
        # Skip the molecule if there is no match to the selection.
        if not select_obj.contains_mol(mol=mol.name):
            continue

        # Skip named molecules if the selection is None.
        if selection == None and mol.name != None:
            continue

        # Store the molecule container.
        mol_container = mol

        # Increment the molecule number counter.
        mol_num = mol_num + 1

    # No unique identifier.
    if mol_num > 1:
        raise RelaxMultiMolIDError(selection)

    # Return the molecule container.
    return mol_container


def return_molecule_by_name(pipe_cont=None, pipe_name=None, mol_name=None):
    """Return the molecule container matching the given name.

    @keyword pipe_cont: The data pipe object.
    @type pipe_cont:    PipeContainer instance
    @keyword pipe_name: The data pipe name.
    @type pipe_name:    str
    @keyword mol_name:  The molecule name.  If not supplied and only a single molecule container exists, then that container will be returned.
    @type mol_name:     str
    @return:            The molecule container object.
    @rtype:             MoleculeContainer instance
    """

    # The data pipe.
    if pipe_cont == None:
        pipe_cont = pipes.get_pipe(pipe)

    # No molecule name specified, so assume a single molecule.
    if mol_name == None:
        # More than one molecule.
        if len(pipe_cont.mol) > 1:
            raise RelaxError("Cannot return the molecule with no name as more than one molecule exists.")

        # Return the molecule.
        return pipe_cont.mol[0]

    # Loop over the molecules.
    for mol in pipe_cont.mol:
        # Return the matching molecule.
        if mol.name == mol_name:
            return mol


def return_residue(selection=None, pipe=None, indices=False):
    """Function for returning the residue data container of the given selection.

    @param selection:   The residue selection identifier.
    @type selection:    str
    @param pipe:        The data pipe containing the residue.  Defaults to the current data pipe.
    @type pipe:         str
    @return:            The residue specific data container, and the molecule and residue indices if asked.
    @rtype:             instance of the ResidueContainer class.
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    res = None
    res_num = 0
    res_container = None
    for i in range(len(dp.mol)):
        # Skip the molecule if there is no match to the selection.
        if not select_obj.contains_mol(mol=dp.mol[i].name):
            continue

        # Store the molecule index.
        mol_index = i

        # Loop over the residues.
        for j in range(len(dp.mol[i].res)):
            # Skip the residue if there is no match to the selection.
            if not select_obj.contains_res(res_num=dp.mol[i].res[j].num, res_name=dp.mol[i].res[j].name, mol=dp.mol[i].name):
                continue

            # Store the residue container and index.
            res_container = dp.mol[i].res[j]
            res_index = j

            # Increment the residue number counter.
            res_num = res_num + 1

    # No unique identifier.
    if res_num > 1:
        raise RelaxMultiResIDError(selection)

    # Return the residue container.
    if indices:
        return res_container, mol_index, res_index
    else:
        return res_container


def return_residue_by_info(mol=None, res_name=None, res_num=None):
    """Return the residue container matching the given name.

    @keyword mol:       The molecule container.
    @type mol:          MoleculeContainer instance
    @keyword res_name:  The residue name.  If not supplied and only a single residue container exists, then that container will be returned.
    @type res_name:     str
    @keyword res_num:   The residue number.  If not supplied and only a single residue container exists, then that container will be returned.
    @type res_num:      str
    @return:            The residue container object.
    @rtype:             ResidueContainer instance
    """

    # No residue name or number specified, so assume a single residue.
    if res_name == None and res_num == None:
        # More than one residue.
        if len(mol.res) > 1:
            raise RelaxError("Cannot return the residue with no name or number as more than one residue exists.")

        # Return the residue.
        return mol.res[0]

    # Loop over the residues.
    for res in mol.res:
        # Return the matching residue.
        if res_name != None and res_num != None:
            if res.name == res_name and res.num == res_num:
               return res
        elif res_name != None:
            if res.name == res_name:
                return res
        elif res_num != None:
            if res.num == res_num:
                return res


def return_spin(spin_id=None, pipe=None, full_info=False, multi=False):
    """Return the spin data container corresponding to the given spin ID string.

    @keyword spin_id:   The unique spin ID string.
    @type spin_id:      str
    @keyword pipe:      The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:         str
    @keyword full_info: A flag specifying if the amount of information to be returned.  If false, only the data container is returned.  If true, the molecule name, residue number, and residue name is additionally returned.
    @type full_info:    bool
    @keyword multi:     A flag which if True will allow multiple spins to be returned.
    @type multi:        bool
    @return:            The spin system specific data container and, if full_info=True, the molecule name, residue number, and residue name.
    @rtype:             SpinContainer instance of list of instances or tuple of (str, int, str, SpinContainer instance or list of instances)
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # No spin ID, so assume there is no spin.
    if spin_id not in dp.mol._spin_id_lookup:
        return None

    # The indices from the look up table.
    else:
        mol_index, res_index, spin_index = dp.mol._spin_id_lookup[spin_id]

    # Return the data.
    if full_info and multi:
        return [dp.mol[mol_index].name], [dp.mol[mol_index].res[res_index].num], [dp.mol[mol_index].res[res_index].name], [dp.mol[mol_index].res[res_index].spin[spin_index]]
    elif full_info:
        return dp.mol[mol_index].name, dp.mol[mol_index].res[res_index].num, dp.mol[mol_index].res[res_index].name, dp.mol[mol_index].res[res_index].spin[spin_index]
    elif multi:
        return [dp.mol[mol_index].res[res_index].spin[spin_index]]
    else:
        return dp.mol[mol_index].res[res_index].spin[spin_index]


def return_spin_by_info(res=None, spin_name=None, spin_num=None):
    """Return the spin container matching the given name.

    @keyword res:       The residue container.
    @type res:          ResidueContainer instance
    @keyword spin_name: The spin name.  If not supplied and only a single spin container exists, then that container will be returned.
    @type spin_name:    str
    @keyword spin_num:  The spin number.  If not supplied and only a single spin container exists, then that container will be returned.
    @type spin_num:     str
    @return:            The spin container object.
    @rtype:             SpinContainer instance
    """

    # No spin name or number specified, so assume a single spin.
    if spin_name == None and spin_num == None:
        # More than one spin.
        if len(res.spin) > 1:
            raise RelaxError("Cannot return the spin with no name or number as more than one spin exists.")

        # Return the spin.
        return res.spin[0]

    # Loop over the spins.
    for spin in res.spin:
        # Return the matching spin.
        if spin_name != None and spin_num != None:
            if spin.name == spin_name and spin.num == spin_num:
               return spin
        elif spin_name != None:
            if spin.name == spin_name:
                return spin
        elif spin_num != None:
            if spin.num == spin_num:
                return spin


def return_spin_from_selection(selection=None, pipe=None, full_info=False, multi=False):
    """Function for returning the spin data container of the given selection.

    If more than one selection is given, then the boolean AND operation will be used to pull out the spin.


    @keyword selection: The spin selection identifier.
    @type selection:    str
    @keyword pipe:      The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:         str
    @keyword full_info: A flag specifying if the amount of information to be returned.  If false, only the data container is returned.  If true, the molecule name, residue number, and residue name is additionally returned.
    @type full_info:    bool
    @keyword multi:     A flag which if True will allow multiple spins to be returned.
    @type multi:        bool
    @return:            The spin system specific data container and, if full_info=True, the molecule name, residue number, and residue name.
    @rtype:             SpinContainer instance of list of instances or tuple of (str, int, str, SpinContainer instance or list of instances)
    """

    # Handle Unicode.
    if is_unicode(selection):
        selection = str(selection)

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    spin_num = 0
    spins = []
    mol_names = []
    res_nums = []
    res_names = []
    spin_ids = []
    for mol in dp.mol:
        # Skip the molecule if there is no match to the selection.
        if not select_obj.contains_mol(mol=mol.name):
            continue

        # Loop over the residues.
        for res in mol.res:
            # Skip the residue if there is no match to the selection.
            if not select_obj.contains_res(res_num=res.num, res_name=res.name, mol=mol.name):
                continue

            # Loop over the spins.
            for spin in res.spin:
                # Skip the spin if there is no match to the selection.
                if not select_obj.contains_spin(spin_num=spin.num, spin_name=spin.name, res_num=res.num, res_name=res.name, mol=mol.name):
                    continue

                # Store all data.
                mol_names.append(mol.name)
                res_nums.append(res.num)
                res_names.append(res.name)
                spins.append(spin)

                # Increment the spin number counter.
                spin_num = spin_num + 1

                # Generate as store the spin ID.
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_num=res.num, res_name=res.name, spin_num=spin.num, spin_name=spin.name))

    # No unique identifier.
    if not multi and spin_num > 1:
        raise RelaxMultiSpinIDError(selection, spin_ids)

    # Return the spin container.
    if full_info and multi:
        return mol_names, res_nums, res_names, spins
    elif full_info:
        return mol_names[0], res_nums[0], res_names[0], spins[0]
    elif multi:
        return spins
    elif len(spins):
        return spins[0]
    else:
        return None


def return_spin_from_index(global_index=None, pipe=None, return_spin_id=False):
    """Function for returning the spin data container corresponding to the global index.

    @param global_index:        The global spin index, spanning the molecule and residue containers.
    @type global_index:         int
    @param pipe:                The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:                 str
    @keyword return_spin_id:    A flag which if True will cause both the spin container and spin identification string to be returned.
    @type return_spin_id:       bool
    @return:                    The spin specific data container (additionally the spin identification string if return_spin_id is set).
    @rtype:                     instance of the SpinContainer class (or tuple of SpinContainer and str)
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Loop over the spins.
    spin_num = 0
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True, pipe=pipe):
        # Match to the global index.
        if spin_num == global_index:
            # Return the spin and the spin_id string.
            if return_spin_id:
                # The spin identification string.
                spin_id = generate_spin_id(pipe_name=pipe, mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin.num, spin_name=spin.name)

                # Return both objects.
                return spin, spin_id

            # Return the spin by itself.
            else:
                return spin

        # Increment the spin number.
        spin_num = spin_num + 1


def return_spin_indices(spin_id=None, pipe=None):
    """Return the molecule, residue and spin indices corresponding to the given spin ID string.

    @keyword spin_id:   The unique spin ID string.
    @type spin_id:      str
    @param pipe:        The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:         str
    @return:            The molecule, residue and spin indices.
    @rtype:             list of int
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # No spin ID, so switch to selection matching.
    if spin_id not in dp.mol._spin_id_lookup:
        # Parse the selection string.
        select_obj = Selection(spin_id)

        # Loop over the molecules.
        for i in range(len(dp.mol)):
            # Skip the molecule if there is no match to the selection.
            if not select_obj.contains_mol(mol=dp.mol[i].name):
                continue

            # The molecule index.
            mol_index = i

            # Loop over the residues.
            for j in range(len(dp.mol[i].res)):
                # Skip the residue if there is no match to the selection.
                if not select_obj.contains_res(res_num=dp.mol[i].res[j].num, res_name=dp.mol[i].res[j].name, mol=dp.mol[i].name):
                    continue

                # The residue index.
                res_index = j

                # Loop over the spins.
                for k in range(len(dp.mol[i].res[j].spin)):
                    # Skip the spin if there is no match to the selection.
                    if not select_obj.contains_spin(spin_num=dp.mol[i].res[j].spin[k].num, spin_name=dp.mol[i].res[j].spin[k].name, res_num=dp.mol[i].res[j].num, res_name=dp.mol[i].res[j].name, mol=dp.mol[i].name):
                        continue

                    # The spin index.
                    spin_index = k

                    # Found the spin, so terminate.
                    break

    # The indices from the look up table.
    else:
        mol_index, res_index, spin_index = dp.mol._spin_id_lookup[spin_id]

    # Return the data.
    return mol_index, res_index, spin_index


def return_single_molecule_info(molecule_token):
    """Return the single molecule name corresponding to the molecule token.

    @param molecule_token:  The molecule identification string.
    @type molecule_token:   str
    @return:                The molecule name.
    @rtype:                 str
    """

    # Parse the molecule token for renaming and renumbering.
    molecule_info = parse_token(molecule_token)

    # Determine the molecule name.
    mol_name = None
    for info in molecule_info:
        # A molecule name identifier.
        if mol_name == None:
            mol_name = info
        else:
            raise RelaxError("The molecule identifier " + repr(molecule_token) + " does not correspond to a single molecule.")

    # Convert to a string if needed.
    if mol_name != None and not isinstance(mol_name, str):
        mol_name = str(mol_name)

    # Return the molecule name.
    return mol_name


def return_single_residue_info(residue_token):
    """Return the single residue number and name corresponding to the residue token.

    @param residue_token:   The residue identification string.
    @type residue_token:    str
    @return:                A tuple containing the residue number and the residue name.
    @rtype:                 (int, str)
    """

    # Parse the residue token for renaming and renumbering.
    residue_info = parse_token(residue_token)

    # Determine the residue number and name.
    res_num = None
    res_name = None
    for info in residue_info:
        # A residue name identifier.
        if isinstance(info, str):
            if res_name == None:
                res_name = info
            else:
                raise RelaxError("The residue identifier " + repr(residue_token) + " does not correspond to a single residue.")

        # A residue number identifier.
        if isinstance(info, int):
            if res_num == None:
                res_num = info
            else:
                raise RelaxError("The residue identifier " + repr(residue_token) + " does not correspond to a single residue.")

    # Return the residue number and name.
    return res_num, res_name


def return_single_spin_info(spin_token):
    """Return the single spin number and name corresponding to the spin token.

    @param spin_token:  The spin identification string.
    @type spin_token:   str
    @return:            A tuple containing the spin number and the spin name.
    @rtype:             (int, str)
    """

    # Parse the spin token for renaming and renumbering.
    spin_info = parse_token(spin_token)

    # Determine the spin number and name.
    spin_num = None
    spin_name = None
    for info in spin_info:
        # A spin name identifier.
        if isinstance(info, str):
            if spin_name == None:
                spin_name = info
            else:
                raise RelaxError("The spin identifier " + repr(spin_token) + " does not correspond to a single spin.")

        # A spin number identifier.
        if isinstance(info, int):
            if spin_num == None:
                spin_num = info
            else:
                raise RelaxError("The spin identifier " + repr(spin_token) + " does not correspond to a single spin.")

    # Return the spin number and name.
    return spin_num, spin_name


def same_sequence(pipe1, pipe2):
    """Test if the sequence data in both pipes are the same.

    @param pipe1:       The first data pipe.
    @type pipe1:        str
    @param pipe2:       The second data pipe.
    @type pipe2:        str
    @return:            True if the sequence data matches, False otherwise.
    @rtype:             bool
    """

    # Test the data pipes.
    pipes.test(pipe1)
    pipes.test(pipe2)

    # Get the data pipes.
    pipe1 = pipes.get_pipe(pipe1)
    pipe2 = pipes.get_pipe(pipe2)

    # Different number of molecules.
    if len(pipe1.mol) != len(pipe2.mol):
        return False

    # Loop over the molecules.
    for i in range(len(pipe1.mol)):
        # Different number of residues.
        if len(pipe1.mol[i].res) != len(pipe2.mol[i].res):
            return False

        # Loop over the residues.
        for j in range(len(pipe1.mol[i].res)):
            # Different number of spins.
            if len(pipe1.mol[i].res[j].spin) != len(pipe2.mol[i].res[j].spin):
                return False

            # Loop over the spins.
            for k in range(len(pipe1.mol[i].res[j].spin)):
                # Different spin numbers.
                if pipe1.mol[i].res[j].spin[k].num != pipe2.mol[i].res[j].spin[k].num:
                    return False

                # Different spin names.
                if pipe1.mol[i].res[j].spin[k].name != pipe2.mol[i].res[j].spin[k].name:
                    return False

    # The sequence is the same.
    return True


def set_spin_element(spin_id=None, element=None, pipe=None, force=False):
    """Set the element type of the spins.

    @keyword spin_id:   The spin identification string.
    @type spin_id:      str
    @keyword element:   The IUPAC element name.
    @type element:      str
    @param pipe:        The data pipe to operate on.  Defaults to the current data pipe.
    @type pipe:         str
    @keyword force:     A flag which if True will cause the element to be changed.
    @type force:        bool
    """

    # Valid names (for NMR active spins).
    valid_names = ['H',
             'C',
             'N',
             'O',
             'F',
             'Na',
             'P',
             'Cd'
    ]

    # Check.
    if element not in valid_names:
        raise RelaxError("The element name '%s' is not valid and should be one of the IUPAC names %s." % (element, valid_names)) 

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Set the element name for the matching spins.
    for spin, id in spin_loop(spin_id, pipe=pipe, return_id=True):
        if hasattr(spin, 'element') and spin.element and not force:
            warn(RelaxWarning("The element type of the spin '%s' is already set.  Set the force flag to True to rename." % id))
        else:
            spin.element = element


def set_spin_isotope(spin_id=None, isotope=None, pipe=None, force=False):
    """Set the nuclear isotope type of the spins.

    @keyword spin_id:   The spin identification string.
    @type spin_id:      str
    @keyword isotope:   The nuclear isotope type.
    @type isotope:      str
    @param pipe:        The data pipe to operate on.  Defaults to the current data pipe.
    @type pipe:         str
    @keyword force:     A flag which if True will cause the isotope type to be changed.  If None, then the warning messages will not mention the need to change this flag to rename.
    @type force:        bool or None
    """

    # Types currently supported in relax.
    supported_types = [
        '1H',
        '2H',
        '13C',
        '14N',
        '15N',
        '17O',
        '19F',
        '23Na',
        '31P',
        '113Cd'
    ]

    # Check.
    if isotope not in supported_types:
        raise RelaxError("The nuclear isotope type '%s' is currently not supported." % isotope) 

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Set the isotope type for the matching spins.
    for spin, id in spin_loop(spin_id, pipe=pipe, return_id=True):
        if hasattr(spin, 'isotope') and spin.isotope and force != True:
            if force == False:
                warn(RelaxWarning("The nuclear isotope type of the spin '%s' is already set.  Change the force flag to True to reset." % id))
            else:
                warn(RelaxWarning("The nuclear isotope type of the spin '%s' is already set." % id))
        else:
            spin.isotope = isotope


def spin_id_to_data_list(id):
    """Convert the single spin ID string into a list of the mol, res, and spin names and numbers.

    @param id:  The spin ID string.
    @type id:   str
    @return:    The molecule name, the residue number and name, and the spin number and name.
    @rtype:     str, int, str, int, str
    """

    # Split up the spin ID.
    mol_token, res_token, spin_token = tokenise(id)
    mol_info = parse_token(mol_token)
    res_info = parse_token(res_token)
    spin_info = parse_token(spin_token)

    # Molecule name.
    mol_name = None
    if len(mol_info) > 1:
        raise RelaxError("The single spin ID '%s' should only belong to one molecule, not %s." % (id, mol_info))
    if len(mol_info) == 1:
        mol_name = mol_info[0]

    # Residue info.
    res_names = []
    res_nums = []
    for i in range(len(res_info)):
        try:
            res_nums.append(int(res_info[i]))
        except ValueError:
            res_names.append(res_info[i])

    # Residue number.
    res_num = None
    if len(res_nums) > 1:
        raise RelaxError("The single spin ID '%s' should only belong to one residue number, not %s." % (id, res_info))
    elif len(res_nums) == 1:
        res_num = res_nums[0]

    # Residue name.
    res_name = None
    if len(res_names) > 1:
        raise RelaxError("The single spin ID '%s' should only belong to one residue name, not %s." % (id, res_info))
    elif len(res_names) == 1:
        res_name = res_names[0]

    # Spin info.
    spin_names = []
    spin_nums = []
    for i in range(len(spin_info)):
        try:
            spin_nums.append(int(spin_info[i]))
        except ValueError:
            spin_names.append(spin_info[i])

    # Spin number.
    spin_num = None
    if len(spin_nums) > 1:
        raise RelaxError("The single spin ID '%s' should only belong to one spin number, not %s." % (id, spin_info))
    elif len(spin_nums) == 1:
        spin_num = spin_nums[0]

    # Spin name.
    spin_name = None
    if len(spin_names) > 1:
        raise RelaxError("The single spin ID '%s' should only belong to one spin name, not %s." % (id, spin_info))
    elif len(spin_names) == 1:
        spin_name = spin_names[0]

    # Return the data.
    return mol_name, res_num, res_name, spin_num, spin_name


def spin_id_variants(dp=None, mol_index=None, res_index=None, spin_index=None):
    """Generate a list of spin ID variants for the given set of molecule, residue and spin indices.

    @keyword dp:            The data pipe to work on.
    @type dp:               PipeContainer instance
    @keyword mol_index:     The molecule index.
    @type mol_index:        int
    @keyword res_index:     The residue index.
    @type res_index:        int
    @keyword spin_index:    The spin index.
    @type spin_index:       int
    @return:                The list of all spin IDs matching the spin.
    @rtype:                 list of str
    """

    # Initialise.
    spin_ids = []
    mol = dp.mol[mol_index]
    res = dp.mol[mol_index].res[res_index]
    spin = dp.mol[mol_index].res[res_index].spin[spin_index]
    mol_count = len(dp.mol)
    res_count = len(mol.res)
    spin_count = len(res.spin)

    # Unique top level info.
    unique_top_level_res_name = True
    unique_top_level_res_num = True
    unique_top_level_spin_name = True
    unique_top_level_spin_num = True
    if res.name != None and dp.mol._res_name_count[res.name] > 1:
        unique_top_level_res_name = False
    if res.num != None and dp.mol._res_num_count[res.num] > 1:
        unique_top_level_res_num = False
    if spin.name != None and dp.mol._spin_name_count[spin.name] > 1:
        unique_top_level_spin_name = False
    if spin.num != None and dp.mol._spin_num_count[spin.num] > 1:
        unique_top_level_spin_num = False

    # Unique molecule level info.
    unique_mol_level_res_name = True
    unique_mol_level_res_num = True
    unique_mol_level_spin_name = True
    unique_mol_level_spin_num = True
    if res.name != None and mol._res_name_count[res.name] > 1:
        unique_mol_level_res_name = False
    if res.num != None and mol._res_num_count[res.num] > 1:
        unique_mol_level_res_num = False
    if spin.name != None and mol._spin_name_count[spin.name] > 1:
        unique_mol_level_spin_name = False
    if spin.num != None and mol._spin_num_count[spin.num] > 1:
        unique_mol_level_spin_num = False

    # Unique residue level info.
    unique_res_level_spin_name = True
    unique_res_level_spin_num = True
    if spin.name != None and res._spin_name_count[spin.name] > 1:
        unique_res_level_spin_name = False
    if spin.num != None and res._spin_num_count[spin.num] > 1:
        unique_res_level_spin_num = False

    # IDs with the molecule name.
    if mol.name != None:
        # IDs with the residue name.
        if res.name != None:
            # The molecule name, residue name and spin name.
            if spin.name != None and unique_mol_level_res_name and unique_res_level_spin_name:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_name=res.name, spin_name=spin.name))

            # The molecule name, residue name and spin number.
            if spin.num != None and unique_mol_level_res_name and unique_res_level_spin_num:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_name=res.name, spin_num=spin.num))

            # The molecule name and residue name.
            if spin_count == 1 and unique_mol_level_res_name:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_name=res.name))

        # IDs with the residue number.
        if res.num != None:
            # The molecule name, residue number and spin name.
            if spin.name != None and unique_mol_level_res_num and unique_res_level_spin_name:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_num=res.num, spin_name=spin.name))

            # The molecule name, residue number and spin number.
            if spin.num != None and unique_mol_level_res_num and unique_res_level_spin_num:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_num=res.num, spin_num=spin.num))

            # The molecule name and residue number.
            if spin_count == 1 and unique_mol_level_res_num:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_num=res.num))

        # The molecule name and spin name.
        if spin.name != None and unique_mol_level_spin_name:
            spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, spin_name=spin.name))

        # The molecule name and spin number.
        if spin.num != None and unique_mol_level_spin_num:
            spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, spin_num=spin.num))

        # The molecule name.
        if spin_count == 1 and res_count == 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name))

    # IDs with the residue name.
    if res.name != None:
        # The residue name and spin name.
        if spin.name != None and unique_top_level_res_name and unique_res_level_spin_name:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_name=res.name, spin_name=spin.name))

        # The residue name and spin number.
        if spin.num != None and unique_top_level_res_name and unique_res_level_spin_num:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_name=res.name, spin_num=spin.num))

        # The residue name.
        if spin_count == 1 and unique_top_level_res_name:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_name=res.name))

    # IDs with the residue number.
    if res.num != None:
        # The residue number and spin name.
        if spin.name != None and unique_top_level_res_num and unique_res_level_spin_name:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_num=res.num, spin_name=spin.name))

        # The residue number and spin number.
        if spin.num != None and unique_top_level_res_num and unique_res_level_spin_num:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_num=res.num, spin_num=spin.num))

        # The residue number.
        if spin_count == 1 and unique_top_level_res_num:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_num=res.num))

    # The spin name.
    if spin.name != None and unique_top_level_spin_name:
        spin_ids.append(generate_spin_id(pipe_cont=dp, spin_name=spin.name))

    # The spin number.
    if spin.num != None and unique_top_level_spin_num:
        spin_ids.append(generate_spin_id(pipe_cont=dp, spin_num=spin.num))

    # Return the IDs.
    return spin_ids


def spin_id_variants_cleanup(dp=None, mol_index=None, res_index=None, spin_index=None):
    """Generate a list of spin ID variants to eliminate for the given set of molecule, residue and spin indices.

    @keyword dp:            The data pipe to work on.
    @type dp:               PipeContainer instance
    @keyword mol_index:     The molecule index.
    @type mol_index:        int
    @keyword res_index:     The residue index.
    @type res_index:        int
    @keyword spin_index:    The spin index.
    @type spin_index:       int
    @return:                The list of all spin IDs matching the spin.
    @rtype:                 list of str
    """

    # Initialise.
    spin_ids = []
    mol = dp.mol[mol_index]
    res = dp.mol[mol_index].res[res_index]
    spin = dp.mol[mol_index].res[res_index].spin[spin_index]
    mol_count = len(dp.mol)
    res_count = len(mol.res)
    spin_count = len(res.spin)

    # Unique top level info.
    unique_top_level_res_name = True
    unique_top_level_res_num = True
    unique_top_level_spin_name = True
    unique_top_level_spin_num = True
    if res.name != None and dp.mol._res_name_count[res.name] > 1:
        unique_top_level_res_name = False
    if res.num != None and dp.mol._res_num_count[res.num] > 1:
        unique_top_level_res_num = False
    if spin.name != None and dp.mol._spin_name_count[spin.name] > 1:
        unique_top_level_spin_name = False
    if spin.num != None and dp.mol._spin_num_count[spin.num] > 1:
        unique_top_level_spin_num = False

    # Unique molecule level info.
    unique_mol_level_res_name = True
    unique_mol_level_res_num = True
    unique_mol_level_spin_name = True
    unique_mol_level_spin_num = True
    if res.name != None and mol._res_name_count[res.name] > 1:
        unique_mol_level_res_name = False
    if res.num != None and mol._res_num_count[res.num] > 1:
        unique_mol_level_res_num = False
    if spin.name != None and mol._spin_name_count[spin.name] > 1:
        unique_mol_level_spin_name = False
    if spin.num != None and mol._spin_num_count[spin.num] > 1:
        unique_mol_level_spin_num = False

    # Unique residue level info.
    unique_res_level_spin_name = True
    unique_res_level_spin_num = True
    if spin.name != None and res._spin_name_count[spin.name] > 1:
        unique_res_level_spin_name = False
    if spin.num != None and res._spin_num_count[spin.num] > 1:
        unique_res_level_spin_num = False

    # IDs with the molecule name.
    if mol.name != None:
        # IDs with the residue name.
        if res.name != None:
            # The molecule name, residue name and spin name.
            if spin.name != None and (not unique_mol_level_res_name or not unique_res_level_spin_name):
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_name=res.name, spin_name=spin.name))

            # The molecule name, residue name and spin number.
            if spin.num != None and (not unique_mol_level_res_name or not unique_res_level_spin_num):
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_name=res.name, spin_num=spin.num))

            # The molecule name and residue name.
            if not unique_mol_level_res_name or spin_count > 1:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_name=res.name))

        # IDs with the residue number.
        if res.num != None:
            # The molecule name, residue number and spin name.
            if spin.name != None and (not unique_mol_level_res_num or not unique_res_level_spin_name):
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_num=res.num, spin_name=spin.name))

            # The molecule name, residue number and spin number.
            if spin.num != None and (not unique_mol_level_res_num or not unique_res_level_spin_num):
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_num=res.num, spin_num=spin.num))

            # The molecule name and residue number.
            if not unique_mol_level_res_num or spin_count > 1:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_num=res.num))

        # The molecule name and spin name.
        if spin.name != None and not unique_mol_level_spin_name:
            spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, spin_name=spin.name))

        # The molecule name and spin number.
        if spin.num != None and not unique_mol_level_spin_num:
            spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, spin_num=spin.num))

        # The molecule name.
        if res_count > 1 or spin_count > 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name))

    # IDs with the residue name.
    if res.name != None:
        # The residue name and spin name.
        if spin.name != None and (not unique_top_level_res_name and not unique_top_level_spin_name):
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_name=res.name, spin_name=spin.name))

        # The residue name and spin number.
        if spin.num != None and (not unique_top_level_res_name and not unique_top_level_spin_num):
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_name=res.name, spin_num=spin.num))

        # The residue name.
        if not unique_top_level_res_name or spin_count > 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_name=res.name))

    # IDs with the residue number.
    if res.num != None:
        # The residue number and spin name.
        if spin.name != None and (not unique_top_level_res_num and not unique_top_level_spin_name):
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_num=res.num, spin_name=spin.name))

        # The residue number and spin number.
        if spin.num != None and (not unique_top_level_res_num and not unique_top_level_spin_num):
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_num=res.num, spin_num=spin.num))

        # The residue number.
        if not unique_top_level_res_num or spin_count > 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_num=res.num))

    # The spin name.
    if spin.name != None and not unique_top_level_spin_name:
        spin_ids.append(generate_spin_id(pipe_cont=dp, spin_name=spin.name))

    # The spin number.
    if spin.num != None and not unique_top_level_spin_num:
        spin_ids.append(generate_spin_id(pipe_cont=dp, spin_num=spin.num))

    # Return the IDs.
    return spin_ids


def spin_id_variants_prune(dp=None, mol_index=None, res_index=None, spin_index=None):
    """Generate a list of spin ID variants to eliminate for the given set of molecule, residue and spin indices.

    @keyword dp:            The data pipe to work on.
    @type dp:               PipeContainer instance
    @keyword mol_index:     The molecule index.
    @type mol_index:        int
    @keyword res_index:     The residue index.
    @type res_index:        int
    @keyword spin_index:    The spin index.
    @type spin_index:       int
    @return:                The list of all spin IDs matching the spin.
    @rtype:                 list of str
    """

    # Initialise.
    spin_ids = []
    mol = dp.mol[mol_index]
    res = dp.mol[mol_index].res[res_index]
    spin = dp.mol[mol_index].res[res_index].spin[spin_index]
    mol_count = len(dp.mol)
    res_count = len(mol.res)
    spin_count = len(res.spin)

    # IDs with the molecule name.
    if mol.name != None:
        # IDs with the residue name.
        if res.name != None:
            # The molecule name, residue name and spin name.
            if spin.name != None:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_name=res.name, spin_name=spin.name))

            # The molecule name, residue name and spin number.
            if spin.num != None:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_name=res.name, spin_num=spin.num))

            # The molecule name and residue name.
            if spin_count == 1:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_name=res.name))

        # IDs with the residue number.
        if res.num != None:
            # The molecule name, residue number and spin name.
            if spin.name != None:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_num=res.num, spin_name=spin.name))

            # The molecule name, residue number and spin number.
            if spin.num != None:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_num=res.num, spin_num=spin.num))

            # The molecule name and residue number.
            if spin_count == 1:
                spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, res_num=res.num))

        # The molecule name and spin name.
        if spin.name != None and res_count == 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, spin_name=spin.name))

        # The molecule name and spin number.
        if spin.num != None and res_count == 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name, spin_num=spin.num))

        # The molecule name.
        if res_count == 1 and spin_count == 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, mol_name=mol.name))

    # IDs with the residue name.
    if res.name != None:
        # The residue name and spin name.
        if spin.name != None and mol_count == 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_name=res.name, spin_name=spin.name))

        # The residue name and spin number.
        if spin.num != None and mol_count == 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_name=res.name, spin_num=spin.num))

        # The residue name.
        if mol_count == 1 and spin_count == 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_name=res.name))

    # IDs with the residue number.
    if res.num != None:
        # The residue number and spin name.
        if spin.name != None and mol_count == 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_num=res.num, spin_name=spin.name))

        # The residue number and spin number.
        if spin.num != None and mol_count == 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_num=res.num, spin_num=spin.num))

        # The residue number.
        if mol_count == 1 and spin_count == 1:
            spin_ids.append(generate_spin_id(pipe_cont=dp, res_num=res.num))

    # The spin name.
    if spin.name != None and mol_count == 1 and res_count == 1:
        spin_ids.append(generate_spin_id(pipe_cont=dp, spin_name=spin.name))

    # The spin number.
    if spin.num != None and mol_count == 1 and res_count == 1:
        spin_ids.append(generate_spin_id(pipe_cont=dp, spin_num=spin.num))

    # Return the IDs.
    return spin_ids


def spin_index_loop(selection=None, pipe=None):
    """Generator function for looping over all selected spins, returning the mol-res-spin indices.

    @param selection:   The spin system selection identifier.
    @type selection:    str
    @param pipe:        The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:         str
    @return:            The molecule, residue, and spin index.
    @rtype:             tuple of 3 int
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Test for the presence of data, and end the execution of this function if there is none.
    if not exists_mol_res_spin_data(pipe=pipe):
        return

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    for mol_index in range(len(dp.mol)):
        # Alias the molecule container.
        mol = dp.mol[mol_index]

        # Loop over the residues.
        for res_index in range(len(dp.mol[mol_index].res)):
            # Alias the residue container.
            res = dp.mol[mol_index].res[res_index]

            # Loop over the spins.
            for spin_index in range(len(dp.mol[mol_index].res[res_index].spin)):
                # Alias the spin container.
                spin = dp.mol[mol_index].res[res_index].spin[spin_index]

                # Skip the spin if there is no match to the selection.
                if not select_obj.contains_spin(spin_num=spin.num, spin_name=spin.name, res_num=res.num, res_name=res.name, mol=mol.name):
                    continue

                # Yield the spin system specific indices.
                yield mol_index, res_index, spin_index


def spin_loop(selection=None, pipe=None, full_info=False, return_id=False, skip_desel=False):
    """Generator function for looping over all the spin systems of the given selection.

    @keyword selection:     The spin system selection identifier.
    @type selection:        str
    @keyword pipe:          The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:             str
    @keyword full_info:     A flag which if True will cause the the molecule name, residue number, and residue name to be returned in addition to the spin container.
    @type full_info:        bool
    @keyword return_id:     A flag which if True will cause the spin identification string of the current spin to be returned in addition to the spin container.
    @type return_id:        bool
    @keyword skip_desel:    A flag which if True will cause deselected spins to be skipped.
    @type skip_desel:       bool
    @return:                The spin system specific data container.  If full_info is True, a tuple of the spin container, the molecule name, residue number, and residue name.  If return_id is True, a tuple of the spin container and spin id.  If both flags are True, then a tuple of the spin container, the molecule name, residue number, residue name, and spin id.
    @rtype:                 If full_info and return_id are False, SpinContainer instance.  If full_info is True and return_id is false, a tuple of (SpinContainer instance, str, int, str).  If full_info is False and return_id is True, a tuple of (SpinContainer instance, str).  If full_info and return_id are False, a tuple of (SpinContainer instance, str, int, str, str)
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Test for the presence of data, and end the execution of this function if there is none.
    if not exists_mol_res_spin_data(pipe=pipe):
        return

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    for mol in dp.mol:
        # Loop over the residues.
        for res in mol.res:
            # Loop over the spins.
            for spin in res.spin:
                # Skip the spin if there is no match to the selection.
                if not select_obj.contains_spin(spin_num=spin.num, spin_name=spin.name, res_num=res.num, res_name=res.name, mol=mol.name):
                    continue

                # Skip deselected spins.
                if not spin.select:
                    continue

                # Generate the spin id.
                if return_id:
                    spin_id = generate_spin_id_unique(pipe_cont=dp, mol=mol, res=res, spin=spin)

                # Yield the data.
                if full_info and return_id:
                    yield spin, mol.name, res.num, res.name, spin_id
                elif full_info:
                    yield spin, mol.name, res.num, res.name
                elif return_id:
                    yield spin, spin_id
                else:
                    yield spin


def type_molecule(mol_id, type=None, force=False):
    """Set the molecule type.

    @param mol_id:      The molecule identification string.
    @type mol_id:       str
    @param type:        The molecule type.
    @type type:         str
    @keyword force:     A flag which if True will cause the molecule type to be overwritten.
    @type force:        bool
    """

    # Check the type.
    if type not in ALLOWED_MOL_TYPES:
        raise RelaxError("The molecule type '%s' must be one of %s." % (type, ALLOWED_MOL_TYPES))

    # Disallow residue and spin selections.
    select_obj = Selection(mol_id)
    if select_obj.has_residues():
        raise RelaxResSelectDisallowError
    if select_obj.has_spins():
        raise RelaxSpinSelectDisallowError

    # Change the molecule types.
    for mol in molecule_loop(mol_id):
        if hasattr(mol, 'type') and mol.type and not force:
            warn(RelaxWarning("The molecule '%s' already has its type set.  Set the force flag to change." % mol_id))
        else:
            mol.type = type
