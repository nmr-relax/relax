###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2007 Edward d'Auvergne                        #
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
from os import F_OK, access
from re import compile, match, split
from string import strip

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxNoRunError, RelaxNoSequenceError, RelaxRegExpError, RelaxResSelectDisallowError, RelaxSpinSelectDisallowError



def desel_all(self, run=None):
    """Function for deselecting all residues."""

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not len(relax_data_store.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence and set the selection flag to 0.
        for i in xrange(len(relax_data_store.res[self.run])):
            relax_data_store.res[self.run][i].select = 0


def desel_read(self, run=None, file=None, dir=None, change_all=None, column=None):
    """Function for deselecting the residues contained in a file."""

    # Extract the data from the file.
    file_data = self.relax.IO.extract_data(file, dir)

    # Count the number of header lines.
    header_lines = 0
    for i in xrange(len(file_data)):
        try:
            int(file_data[i][column])
        except:
            header_lines = header_lines + 1
        else:
            break

    # Remove the header.
    file_data = file_data[header_lines:]

    # Strip the data.
    file_data = self.relax.IO.strip(file_data)

    # Create the list of residues to deselect.
    deselect = []
    for i in xrange(len(file_data)):
        try:
            deselect.append(int(file_data[i][column]))
        except:
            raise RelaxError, "Improperly formatted file."

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    no_match = 1
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not len(relax_data_store.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Remap the data structure 'relax_data_store.res[self.run][i]'.
            data = relax_data_store.res[self.run][i]

            # Select all residues.
            if change_all:
                data.select = 1

            # Unselect the residue if it is in the list deselect.
            if data.num in deselect:
                data.select = 0

            # Match flag.
            no_match = 0

    # No residue matched.
    if no_match:
        print "No residues match."


def desel_res(self, run=None, num=None, name=None, change_all=None):
    """Function for deselecting specific residues."""

    # Test if the residue number is a valid regular expression.
    if type(num) == str:
        try:
            compile(num)
        except:
            raise RelaxRegExpError, ('residue number', num)

    # Test if the residue name is a valid regular expression.
    if name:
        try:
            compile(name)
        except:
            raise RelaxRegExpError, ('residue name', name)

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    no_match = 1
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not len(relax_data_store.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Remap the data structure 'relax_data_store.res[self.run][i]'.
            data = relax_data_store.res[self.run][i]

            # Select all residues.
            if change_all:
                data.select = 1

            # Skip the residue if there is no match to 'num'.
            if type(num) == int:
                if not data.num == num:
                    continue
            if type(num) == str:
                if not match(num, `data.num`):
                    continue

            # Skip the residue if there is no match to 'name'.
            if name != None:
                if not match(name, data.name):
                    continue

            # Unselect the residue.
            data.select = 0

            # Match flag.
            no_match = 0

    # No residue matched.
    if no_match:
        print "No residues match."


def molecule_loop(selection=None):
    """Generator function for looping over all the molecules of the given selection.

    @param selection:   The molecule selection identifier.
    @type selection:    str
    @return:            The molecule specific data container.
    @rtype:             instance of the MoleculeContainer class.
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(selection)

    # Disallowed selections.
    if res_token:
        raise RelaxResSelectDisallowError
    if spin_token:
        raise RelaxSpinSelectDisallowError

    # Parse the token.
    molecules = parse_token(mol_token)

    # Loop over the molecules.
    for mol in relax_data_store[relax_data_store.current_pipe].mol:
        # Skip the molecule if there is no match to the selection.
        if mol_token and mol.name not in molecules:
            continue

        # Yield the molecule data container.
        yield mol


def parse_token(token):
    """Parse the token string and return a list of identifying numbers and names.

    Firstly the token is split by the ',' character into its individual elements and all whitespace
    stripped from the elements.  Numbers are converted to integers, names are left as strings, and
    ranges are converted into the full list of integers.

    @param token:   The identification string, the elements of which are separated by commas.  Each
        element can be either a single number, a range of numbers (two numbers separated by '-'), or
        a name.
    @type token:    str
    @return:        A list of identifying numbers and names.
    @rtype:         list of int and str
    """

    # No token.
    if token == None:
        return None

    # Split by the ',' character.
    elements = split(',', token)

    # Loop over the elements.
    list = []
    for element in elements:
        # Strip all leading and trailing whitespace.
        element = strip(element)

        # Find all '-' characters (ignoring the first character, i.e. a negative number).
        indecies= []
        for i in xrange(1,len(element)):
            if element[i] == '-':
                indecies.append(i)

        # Range.
        if indecies:
            # Invalid range element, only one range char '-' and one negative sign is allowed.
            if len(indecies) > 2:
                raise RelaxError, "The range element " + `element` + " is invalid."

            # Convert the two numbers to integers.
            try:
                start = int(element[:indecies[0]])
                end = int(element[indecies[0]+1:])
            except ValueError:
                raise RelaxError, "The range element " + `element` + " is invalid as either the start or end of the range are not integers."

            # Test that the starting number is less than the end.
            if start >= end:
                raise RelaxError, "The starting number of the range element " + `element` + " needs to be less than the end number."

            # Create the range and append it to the list.
            for i in range(start, end+1):
                list.append(i)

        # Number or name.
        else:
            # Try converting the element into an integer.
            try:
                element = int(element)
            except ValueError:
                pass

            # Append the element.
            list.append(element)

    # Sort the list.
    list.sort()

    # Return the identifying list.
    return list


def residue_loop(selection=None):
    """Generator function for looping over all the residues of the given selection.

    @param selection:   The residue selection identifier.
    @type selection:    str
    @return:            The residue specific data container.
    @rtype:             instance of the MoleculeContainer class.
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(selection)

    # Disallowed selections.
    if spin_token:
        raise RelaxSpinSelectDisallowError

    # Parse the tokens.
    molecules = parse_token(mol_token)
    residues = parse_token(res_token)

    # Loop over the molecules.
    for mol in relax_data_store[relax_data_store.current_pipe].mol:
        # Skip the molecule if there is no match to the selection.
        if mol_token and mol.name not in molecules:
            continue

        # Loop over the residues.
        for res in mol.res:
            # Skip the residue if there is no match to the selection.
            if res_token and res.name not in residues:
                continue

            # Yield the residue data container.
            yield res


def reverse(selection=None):
    """Function for the reversal of the spin system selection."""

    # Loop over the spin systems and reverse the selection flag.
    for spin in spin_loop(selection):
        # Reverse the selection.
        if spin.select:
            spin.select = 0
        else:
            spin.select = 1


def sel_all(self, run=None):
    """Function for selecting all residues."""

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not len(relax_data_store.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence and set the selection flag to 1.
        for i in xrange(len(relax_data_store.res[self.run])):
            relax_data_store.res[self.run][i].select = 1


def sel_read(self, run=None, file=None, dir=None, boolean='OR', change_all=0, column=None):
    """Select the residues contained in the given file.

    @param run:         The run name.
    @type run:          str
    @param file:        The name of the file.
    @type file:         str
    @param dir:         The directory containing the file.
    @type dir:          str
    @param boolean:     The boolean operator used to select the spin systems with.  It can be
        one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'.
    @type boolean:      str
    @param change_all:  A flag which if set will set the selection to solely those of the file.
    @type change_all:   int
    @param column:      The whitespace separated column in which the residue numbers are
        located.
    @type column:       int
    """

    # Extract the data from the file.
    file_data = self.relax.IO.extract_data(file, dir)

    # Count the number of header lines.
    header_lines = 0
    for i in xrange(len(file_data)):
        try:
            int(file_data[i][column])
        except:
            header_lines = header_lines + 1
        else:
            break

    # Remove the header.
    file_data = file_data[header_lines:]

    # Strip the data.
    file_data = self.relax.IO.strip(file_data)

    # Create the list of residues to select.
    select = []
    for i in xrange(len(file_data)):
        try:
            select.append(int(file_data[i][column]))
        except:
            raise RelaxError, "Improperly formatted file."

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not len(relax_data_store.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Remap the data structure 'relax_data_store.res[self.run][i]'.
            data = relax_data_store.res[self.run][i]

            # The spin system is in the new selection list.
            if data.num in select:
                new_select = 1
            else:
                new_select = 0

            # Select just the residues in the file.
            if change_all:
                data.select = new_select

            # Boolean selections.
            if boolean == 'OR':
                data.select = data.select or new_select
            elif boolean == 'NOR':
                data.select = not (data.select or new_select)
            elif boolean == 'AND':
                data.select = data.select and new_select
            elif boolean == 'NAND':
                data.select = not (data.select and new_select)
            elif boolean == 'XOR':
                data.select = not (data.select and new_select) and (data.select or new_select)
            elif boolean == 'XNOR':
                data.select = (data.select and new_select) or not (data.select or new_select)
            else:
                raise RelaxError, "Unknown boolean operator " + `boolean`


def sel_res(self, run=None, num=None, name=None, boolean='OR', change_all=0):
    """Select specific residues.

    @param run:         The run name.
    @type run:          str
    @param num:         The residue number.
    @type num:          int or regular expression str
    @param name:        The residue name.
    @type name:         regular expression str
    @param boolean:     The boolean operator used to select the spin systems with.  It can be
        one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'.
    @type boolean:      str
    @param change_all:  A flag which if set will set the selection to solely those residues
        specified.
    @type change_all:   int
    """

    # Test if the residue number is a valid regular expression.
    if type(num) == str:
        try:
            compile(num)
        except:
            raise RelaxRegExpError, ('residue number', num)

    # Test if the residue name is a valid regular expression.
    if name:
        try:
            compile(name)
        except:
            raise RelaxRegExpError, ('residue name', name)

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    no_match = 1
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not len(relax_data_store.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Remap the data structure 'relax_data_store.res[self.run][i]'.
            data = relax_data_store.res[self.run][i]

            # Initialise the new selection flag.
            new_select = 0

            # Set the new selection flag if the residue matches 'num'.
            if type(num) == int:
                if data.num == num:
                    new_select = 1
            elif type(num) == str:
                if match(num, `data.num`):
                    new_select = 1

            # Set the new selection flag if the residue matches 'name'.
            if name != None:
                if match(name, data.name):
                    new_select = 1

            # Select just the specified residues.
            if change_all:
                data.select = new_select

            # Boolean selections.
            if boolean == 'OR':
                data.select = data.select or new_select
            elif boolean == 'NOR':
                data.select = not (data.select or new_select)
            elif boolean == 'AND':
                data.select = data.select and new_select
            elif boolean == 'NAND':
                data.select = not (data.select and new_select)
            elif boolean == 'XOR':
                data.select = not (data.select and new_select) and (data.select or new_select)
            elif boolean == 'XNOR':
                data.select = (data.select and new_select) or not (data.select or new_select)
            else:
                raise RelaxError, "Unknown boolean operator " + `boolean`

            # Match flag.
            if new_select:
                no_match = 0

    # No residue matched.
    if no_match:
        print "No residues match."


def spin_loop(selection=None):
    """Generator function for looping over all the spin systems of the given selection.

    @param selection:   The spin system selection identifier.
    @type selection:    str
    @return:            The spin system specific data container.
    @rtype:             instance of the SpinContainer class.
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(selection)

    # Parse the tokens.
    molecules = parse_token(mol_token)
    residues = parse_token(res_token)
    spins = parse_token(spin_token)

    # Loop over the molecules.
    for mol in relax_data_store[relax_data_store.current_pipe].mol:
        # Skip the molecule if there is no match to the selection.
        if mol_token and mol.name not in molecules:
            continue

        # Loop over the residues.
        for res in mol.res:
            # Skip the residue if there is no match to the selection.
            if res_token and res.name not in residues:
                continue

            # Loop over the spins.
            for spin in res.spin:
                # Skip the spin if there is no match to the selection.
                if spin_token and spin.name not in spins:
                    continue

                # Yield the spin system data container.
                yield spin


def tokenise(selection):
    """Split the input selection string returning the mol_token, res_token, and spin_token strings.

    The mol_token is identified as the text from the '#' to either the ':' or '@' characters or the
    end of the string.

    The res_token is identified as the text from the ':' to either the '@' character or the end of
    the string.

    The spin_token is identified as the text from the '@' to the end of the string.

    @param selection:   The selection identifier.
    @type selection:    str
    @return:            The mol_token, res_token, and spin_token.
    @rtype:             3-tuple of str or None
    """

    # No selection.
    if selection == None:
        return None, None, None


    # Atoms.
    ########

    # Split by '@'.
    atom_split = split('@', selection)

    # Test that only one '@' character was supplied.
    if len(atom_split) > 2:
        raise RelaxError, "Only one '@' character is allowed within the selection identifier string."

    # No atom identifier.
    if len(atom_split) == 1:
        spin_token = None
    else:
        # Test for out of order identifiers.
        if ':' in atom_split[1]:
            raise RelaxError, "The atom identifier '@' must come after the residue identifier ':'."
        elif '#' in atom_split[1]:
            raise RelaxError, "The atom identifier '@' must come after the molecule identifier '#'."

        # The token.
        spin_token = atom_split[1]


    # Residues.
    ###########

    # Split by ':'.
    res_split = split(':', atom_split[0])

    # Test that only one ':' character was supplied.
    if len(res_split) > 2:
        raise RelaxError, "Only one ':' character is allowed within the selection identifier string."

    # No residue identifier.
    if len(res_split) == 1:
        res_token = None
    else:
        # Test for out of order identifiers.
        if '#' in res_split[1]:
            raise RelaxError, "The residue identifier ':' must come after the molecule identifier '#'."

        # The token.
        res_token = res_split[1]



    # Molecules.
    ############

    # Split by '#'.
    mol_split = split('#', res_split[0])

    # Test that only one '#' character was supplied.
    if len(mol_split) > 2:
        raise RelaxError, "Only one '#' character is allowed within the selection identifier string."

    # No molecule identifier.
    if len(mol_split) == 1:
        mol_token = None
    else:
        mol_token = mol_split[1]


    # Improper selection string.
    if mol_token == None and res_token == None and spin_token == None:
        raise RelaxError, "The selection string " + `selection` + " is invalid."

    # Return the three tokens.
    return mol_token, res_token, spin_token
