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
from relax_errors import RelaxError, RelaxFileEmptyError, RelaxNoPdbChainError, RelaxNoPipeError, RelaxNoSequenceError, RelaxSequenceError, RelaxSpinSelectDisallowError
from selection import molecule_loop, parse_token, residue_loop, return_molecule, return_residue, return_single_residue_info, tokenise


def copy(pipe_from=None, res_from=None, pipe_to=None, res_to=None):
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
    if res_to_cont:
        raise RelaxError, "The residue " + `res_to` + " already exists in the " + `pipe_from` + " data pipe."

    # Get the single residue data container.
    res_from_cont = return_residue(res_from, pipe_from)

    # No residue to copy data from.
    if res_from_cont == None:
        raise RelaxError, "The residue " + `res_from` + " does not exist in the " + `pipe_from` + " data pipe."

    # Get the single molecule data container to copy the residue to.
    mol_to_container = return_molecule(res_to, pipe_to)

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


def create(res_num=None, res_name=None):
    """Function for adding a residue into the relax data store."""

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if the residue number already exists.
    for i in xrange(len(cdp.mol[0].res)):
        if cdp.mol[0].res[i].num == res_num:
            raise RelaxError, "The residue number '" + `res_num` + "' already exists in the sequence."

    # If no residue data exists, replace the empty first residue with this residue.
    if cdp.mol[0].res[0].num == None and cdp.mol[0].res[0].name == None and len(cdp.mol[0].res) == 1:
        cdp.mol[0].res[0].num = res_num
        cdp.mol[0].res[0].name = res_name

    # Append the residue.
    else:
        cdp.mol[0].res.add_item(res_num=res_num, res_name=res_name)


def delete(res_id=None):
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


def display(res_id=None):
    """Function for displaying the information associated with the residue.

    @param res_id:  The molecule and residue identifier string.
    @type res_id:   str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # The molecule selection string.
    if mol_token:
        mol_sel = '#' + mol_token
    else:
        mol_sel = None

    # Molecule loop.
    for mol in molecule_loop(mol_sel):
        # Print a header.
        print "\n\nMolecule: " + `mol.name`
        print "%-8s%-8s%-10s" % ("Number", "Name", "Number of spins")

        # The residue identifier for this molecule.
        res_sel = '#' + mol.name
        if res_token:
            res_sel = res_sel + ':' + res_token

        # Loop over the residues of this molecule.
        for res in residue_loop(res_sel):
            # Print the residue data.
            print "%-8i%-8s%-10i" % (res.num, res.name, len(res.spin))


def rename(res_id, new_name=None):
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

    # Molecule loop.
    for mol in molecule_loop(mol_token):
        # Loop over the residues of the molecule.
        for i in xrange(len(mol.res)):
            # Rename the residue is there is a match.
            if mol.res[i].num in residues or mol.res[i].name in residues:
                mol.res[i].name = new_name


def renumber(res_id, new_number=None):
    """Function for renumbering residues.

    @param res_id:      The identifier string for the residue to renumber.
    @type res_id:       str
    @param new_number:  The new residue number.
    @type new_number:   str
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
    for mol in molecule_loop(mol_token):
        # Loop over the residues of the molecule.
        for i in xrange(len(mol.res)):
            # Rename the residue is there is a match.
            if mol.res[i].num in residues or mol.res[i].name in residues:
                number = number + 1

    # Fail if multiple residues are numbered.
    if number > 1:
        raise RelaxError, "The renumbering of multiple residues is disallowed."

    # Molecule loop.
    for mol in molecule_loop(mol_token):
        # Loop over the residues of the molecule.
        for i in xrange(len(mol.res)):
            # Rename the residue is there is a match.
            if mol.res[i].num in residues or mol.res[i].name in residues:
                mol.res[i].num = new_number
