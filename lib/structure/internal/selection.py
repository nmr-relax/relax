###############################################################################
#                                                                             #
# Copyright (C) 2014-2015 Edward d'Auvergne                                   #
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
"""Module containing the fast structural selection object."""


class Internal_selection:
    """The fast structural selection object."""

    def __init__(self):
        """Set up the object."""

        # The molecule index list.
        self._mol_indices = []

        # The atom index list of lists.
        self._atom_indices = []


    def add_atom(self, mol_index=None, atom_index=None):
        """Add an atom index to the object.

        @keyword mol_index:     The index of the molecule.
        @type mol_index:        int
        @keyword atom_index:    The index of the atom.
        @type atom_index:       int
        """

        # Find the molecule index.
        index = self._mol_indices.index(mol_index)

        # Store the index.
        self._atom_indices[index].append(atom_index)


    def add_mol(self, mol_index=None):
        """Add a molecule index to the object.

        @keyword mol_index:     The index of the molecule.
        @type mol_index:        int
        """

        # Store the index.
        self._mol_indices.append(mol_index)

        # Add a new atom list.
        self._atom_indices.append([])


    def count_atoms(self):
        """Return the number of atoms in the selection."""

        # No data.
        if self._atom_indices == []:
            return 0

        # Sum the atoms of all molecules.
        sum = 0
        for i in range(len(self._atom_indices)):
            sum += len(self._atom_indices[i])

        # Return the sum.
        return sum


    def loop(self):
        """Fast loop over all molecule and atom indices.

        @return:    The molecule and atom index pairs for all atoms.
        @rtype:     int, int
        """

        # Molecule loop.
        for mol_index in self._mol_indices:
            # Find the molecule index.
            index = self._mol_indices.index(mol_index)

            # Atom loop.
            for atom_index in self._atom_indices[index]:
                yield mol_index, atom_index


    def mol_loop(self):
        """Fast loop over all molecule indices.

        @return:    The molecule index.
        @rtype:     int
        """

        # Molecule loop.
        for mol_index in self._mol_indices:
            yield mol_index
