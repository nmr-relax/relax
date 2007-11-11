###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
from selection import molecule_loop, parse_token, residue_loop, return_molecule, return_residue, return_spin, return_single_residue_info, return_single_spin_info, spin_loop, tokenise


# Module doc.
"""Functions for manipulating the spin information content in the relax data storage singleton.

This touches part of the molecule-residue-spin data structure.
"""


def copy(pipe_from=None, spin_from=None, pipe_to=None, spin_to=None):
    """Copy the contents of the spin structure from one spin to a new spin.

    For copying to be successful, the spin_from identification string must match an existent spin.
    The new spin number must be unique.

    @param pipe_from:   The data pipe to copy the spin from.  This defaults to the current data
                        pipe.
    @type pipe_from:    str
    @param spin_from:   The spin identification string for the structure to copy the data from.
    @type spin_from:    str
    @param pipe_to:     The data pipe to copy the spin to.  This defaults to the current data
                        pipe.
    @type pipe_to:      str
    @param spin_to:     The spin identification string for the structure to copy the data to.
    @type spin_to:      str
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
    mol_from_token, res_from_token, spin_from_token = tokenise(spin_from)
    mol_to_token, res_to_token, spin_to_token = tokenise(spin_to)

    # Parse the spin token for renaming and renumbering.
    spin_num_to, spin_name_to = return_single_spin_info(spin_to_token)

    # Test if the spin number already exists.
    spin_to_cont = return_spin(spin_to, pipe_to)
    if spin_to_cont:
        raise RelaxError, "The spin " + `spin_to` + " already exists in the " + `pipe_from` + " data pipe."

    # No residue to copy data from.
    res_from_cont = return_residue(spin_from, pipe_from)
    if res_from_cont == None:
        raise RelaxError, "The residue in " + `spin_from` + " does not exist in the " + `pipe_from` + " data pipe."

    # No residue to copy data to.
    res_to_cont = return_residue(spin_to, pipe_from)
    if res_to_cont == None and spin_to:
        raise RelaxError, "The residue in " + `spin_to` + " does not exist in the " + `pipe_from` + " data pipe."

    # No spin to copy data from.
    spin_from_cont = return_spin(spin_from, pipe_from)
    if spin_from_cont == None:
        raise RelaxError, "The spin " + `spin_from` + " does not exist in the " + `pipe_from` + " data pipe."

    # Get the single residue data container to copy the spin to (default to the first molecule, first residue).
    res_to_container = return_residue(spin_to, pipe_to)
    if res_to_container == None:
        res_to_container = relax_data_store[pipe_to].mol[0].res[0]

    # Copy the data.
    if res_to_container.spin[0].num == None and res_to_container.spin[0].name == None and len(res_to_container.spin) == 1:
        res_to_container.spin[0] = spin_from_cont.__clone__()
    else:
        res_to_container.spin.append(spin_from_cont.__clone__())

    # Change the new spin number and name.
    if spin_num_to != None:
        res_to_container.spin[-1].num = spin_num_to
    if spin_name_to != None:
        res_to_container.spin[-1].name = spin_name_to


def create(spin_num=None, spin_name=None, res_id=None):
    """Function for adding a spin into the relax data store.
    
    @param spin_num:    The identification number of the new spin.
    @type spin_num:     int
    @param spin_name:   The name of the new spin.
    @type spin_name:    str
    @param res_id:      The molecule and residue identification string.
    @type res_id:       str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # No residue to add the spin to.
    res_to_cont = return_residue(res_id)
    if res_to_cont == None and res_id:
        raise RelaxError, "The residue in " + `res_id` + " does not exist in the current data pipe."
    elif res_to_cont == None:
        res_to_cont = cdp.mol[0].res[0]

    # Test if the spin number already exists.
    for i in xrange(len(res_to_cont.spin)):
        if res_to_cont.spin[i].num == spin_num:
            raise RelaxError, "The spin number '" + `spin_num` + "' already exists."

    # If no spin data exists, replace the empty first spin with this spin.
    if res_to_cont.spin[0].num == None and res_to_cont.spin[0].name == None and len(res_to_cont.spin) == 1:
        res_to_cont.spin[0].num = spin_num
        res_to_cont.spin[0].name = spin_name

    # Append the residue.
    else:
        res_to_cont.spin.add_item(spin_num=spin_num, spin_name=spin_name)


def delete(spin_id=None):
    """Function for deleting spins from the current data pipe.

    @param spin_id: The molecule, residue, and spin identifier string.
    @type spin_id:  str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(spin_id)

    # Parse the tokens.
    spins = parse_token(spin_token)

    # Residue loop.
    for res in residue_loop(spin_id):
        # List of indecies to delete.
        indecies = []

        # Loop over the spins of the residue.
        for i in xrange(len(res.spin)):
            # Remove the spin is there is a match.
            if res.spin[i].num in spins or res.spin[i].name in spins:
                indecies.append(i)

        # Reverse the indecies.
        indecies.reverse()

        # Delete the residues.
        for index in indecies:
            res.spin.pop(index)

        # Create an empty residue container if no residues remain.
        if len(res.spin) == 0:
            res.spin.add_item()


def display(spin_id=None):
    """Function for displaying the information associated with the spin.

    @param spin_id: The molecule and residue identifier string.
    @type spin_id:  str
    """

    # Print a header.
    print "\n\n%-15s %-15s %-15s %-15s %-15s" % ("Molecule", "Res number", "Res name", "Spin number", "Spin name")

    # Spin loop.
    for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
        # Print the residue data.
        print "%-15s %-15s %-15s %-15s %-15s" % (mol_name, `res_num`, res_name, `spin.num`, spin.name)


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
