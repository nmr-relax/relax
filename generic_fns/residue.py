###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007 Edward d'Auvergne                             #
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

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxNoPipeError, RelaxSpinSelectDisallowError
from selection import molecule_loop, parse_token, residue_loop, return_molecule, return_residue, return_single_residue_info, tokenise


# Module doc.
"""Functions for manipulating the residue information content in the relax data storage singleton.

This touches part of the molecule-residue-spin data structure.
"""


def copy_residue(pipe_from=None, res_from=None, pipe_to=None, res_to=None):
    """Copy the contents of the residue structure from one residue to a new residue.

    For copying to be successful, the res_from identification string must match an existent residue.
    The new residue number must be unique.

    @param pipe_from:   The data pipe to copy the residue from.  This defaults to the current data
                        pipe.
    @type pipe_from:    str
    @param res_from:    The residue identification string for the structure to copy the data from.
    @type res_from:     str
    @param pipe_to:     The data pipe to copy the residue to.  This defaults to the current data
                        pipe.
    @type pipe_to:      str
    @param res_to:      The residue identification string for the structure to copy the data to.
    @type res_to:       str
    """

    # The current data pipe.
    if pipe_from == None:
        pipe_from = relax_data_store.current_pipe
    if pipe_to == None:
        pipe_to = relax_data_store.current_pipe

    # The second pipe does not exist.
    if pipe_to not in relax_data_store.keys():
        raise RelaxNoPipeError, pipe_to

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
        raise RelaxError, "The residue " + `res_to` + " already exists in the " + `pipe_to` + " data pipe."

    # Get the single residue data container.
    res_from_cont = return_residue(res_from, pipe_from)

    # No residue to copy data from.
    if res_from_cont == None:
        raise RelaxError, "The residue " + `res_from` + " does not exist in the " + `pipe_from` + " data pipe."

    # Get the single molecule data container to copy the residue to (default to the first molecule).
    mol_to_container = return_molecule(res_to, pipe_to)
    if mol_to_container == None:
        mol_to_container = relax_data_store[pipe_to].mol[0]

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


def create_residue(res_num=None, res_name=None, mol_id=None):
    """Function for adding a residue into the relax data store.

    @param res_num:     The identification number of the new residue.
    @type res_num:      int
    @param res_name:    The name of the new residue.
    @type res_name:     str
    @param mol_id:      The molecule identification string.
    @type mol_id:       str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(mol_id)

    # Disallowed selections.
    if res_token != None:
        raise RelaxResSelectDisallowError
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Get the molecule container to add the residue to.
    if mol_id:
        mol_to_cont = return_molecule(mol_id)
        if mol_to_cont == None:
            raise RelaxError, "The molecule in " + `mol_id` + " does not exist in the current data pipe."
    else:
        mol_to_cont = relax_data_store[relax_data_store.current_pipe].mol[0]

    # Add the residue.
    mol_to_cont.res.add_item(res_num=res_num, res_name=res_name)


def delete_residue(res_id=None):
    """Function for deleting residues from the current data pipe.

    @param res_id:  The molecule and residue identifier string.
    @type res_id:   str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Parse the tokens.
    residues = parse_token(res_token)

    # Molecule loop.
    for mol in molecule_loop(mol_token):
        # List of indecies to delete.
        indecies = []

        # Loop over the residues of the molecule.
        for i in xrange(len(mol.res)):
            # Remove the residue is there is a match.
            if mol.res[i].num in residues or mol.res[i].name in residues:
                indecies.append(i)

        # Reverse the indecies.
        indecies.reverse()

        # Delete the residues.
        for index in indecies:
            mol.res.pop(index)

        # Create an empty residue container if no residues remain.
        if len(mol.res) == 0:
            mol.res.add_item()


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
    print "\n\n%-15s %-15s %-15s %-15s" % ("Molecule", "Res number", "Res name", "Number of spins")

    # Residue loop.
    for res, mol_name in residue_loop(res_id, full_info=True):
        print "%-15s %-15s %-15s %-15s" % (mol_name, `res.num`, res.name, `len(res.spin)`)


def rename_residue(res_id, new_name=None):
    """Function for renaming residues.

    @param res_id:      The identifier string for the residue(s) to rename.
    @type res_id:       str
    @param new_name:    The new residue name.
    @type new_name:     str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Parse the tokens.
    residues = parse_token(res_token)

    # Residue loop.
    for res in residue_loop(res_id):
        # Rename the residue is there is a match.
        if res.num in residues or res.name in residues:
            res.name = new_name


def renumber_residue(res_id, new_number=None):
    """Function for renumbering residues.

    @param res_id:      The identifier string for the residue to renumber.
    @type res_id:       str
    @param new_number:  The new residue number.
    @type new_number:   int
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Parse the tokens.
    residues = parse_token(res_token)

    # Catch multiple renumberings!
    number = 0
    for res in residue_loop(res_id):
        if res.num in residues or res.name in residues:
            number = number + 1

    # Fail if multiple residues are numbered.
    if number > 1:
        raise RelaxError, "The renumbering of multiple residues is disallowed."

    # Residue loop.
    for res in residue_loop(res_id):
        # Rename the residue is there is a match.
        if res.num in residues or res.name in residues:
            res.num = new_number
