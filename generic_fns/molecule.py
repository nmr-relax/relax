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
from relax_errors import RelaxError, RelaxNoPipeError, RelaxResSelectDisallowError, RelaxSpinSelectDisallowError
from selection import molecule_loop, parse_token, return_molecule, return_single_molecule_info, tokenise


# Module doc.
"""Functions for manipulating the molecule information content in the relax data storage singleton.

This touches part of the molecule-residue-spin data structure.
"""


def copy_molecule(pipe_from=None, mol_from=None, pipe_to=None, mol_to=None):
    """Copy the contents of a molecule container to a new molecule.

    For copying to be successful, the mol_from identification string must match an existent molecule.

    @param pipe_from:   The data pipe to copy the molecule data from.  This defaults to the current
                        data pipe.
    @type pipe_from:    str
    @param mol_from:    The molecule identification string for the structure to copy the data from.
    @type mol_from:     str
    @param pipe_to:     The data pipe to copy the molecule data to.  This defaults to the current
                        data pipe.
    @type pipe_to:      str
    @param mol_to:      The molecule identification string for the structure to copy the data to.
    @type mol_to:       str
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
        raise RelaxError, "The molecule " + `mol_to` + " already exists in the " + `pipe_to` + " data pipe."

    # Get the single molecule data container.
    mol_from_cont = return_molecule(mol_from, pipe_from)

    # No molecule to copy data from.
    if mol_from_cont == None:
        raise RelaxError, "The molecule " + `mol_from` + " does not exist in the " + `pipe_from` + " data pipe."

    # Copy the data.
    if relax_data_store[pipe_to].mol[0].name == None and len(relax_data_store[pipe_to].mol) == 1:
        relax_data_store[pipe_to].mol[0] = mol_from_cont.__clone__()
    else:
        relax_data_store[pipe_to].mol.append(mol_from_cont.__clone__())

    # Change the new molecule name.
    if mol_name_to != None:
        relax_data_store[pipe_to].mol[-1].name = mol_name_to


def create_molecule(mol_name=None):
    """Function for adding a molecule into the relax data store."""

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if the molecule name already exists.
    for i in xrange(len(cdp.mol)):
        if cdp.mol[i].name == mol_name:
            raise RelaxError, "The molecule '" + `mol_name` + "' already exists in the relax data store."


    # Append the molecule.
    cdp.mol.add_item(mol_name=mol_name)


def delete_molecule(mol_id=None):
    """Function for deleting molecules from the current data pipe.

    @param mol_id:  The molecule identifier string.
    @type mol_id:   str
    """

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

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # List of indecies to delete.
    indecies = []

    # Loop over the molecules.
    for i in xrange(len(cdp.mol)):
        # Remove the residue is there is a match.
        if cdp.mol[i].name in molecules:
            indecies.append(i)

    # Reverse the indecies.
    indecies.reverse()

    # Delete the molecules.
    for index in indecies:
        cdp.mol.pop(index)

    # Create an empty residue container if no residues remain.
    if len(cdp.mol) == 0:
        cdp.mol.add_item()


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
    print "\n\n%-15s %-15s" % ("Molecule", "Number of residues")

    # Molecule loop.
    for mol in molecule_loop(mol_sel):
        # Print the molecule data.
        print "%-15s %-15s" % (mol.name, `len(mol.res)`)


def rename_molecule(mol_id, new_name=None):
    """Function for renaming molecules.

    @param mol_id:      The identifier string for the molecule to rename.
    @type mol_id:       str
    @param new_name:    The new molecule name.
    @type new_name:     str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(mol_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Disallow residue selections.
    if res_token != None:
        raise RelaxResSelectDisallowError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Parse the tokens.
    molecules = parse_token(mol_token)

    # Get the single molecule data container.
    mol = return_molecule(mol_id)

    # Rename the molecule is there is a match.
    if mol:
        mol.name = new_name
