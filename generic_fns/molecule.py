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
