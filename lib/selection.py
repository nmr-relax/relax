from __future__ import absolute_import
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
"""Module for the molecule, residue and atom selections."""

# Python module imports.
from warnings import warn

# relax module imports.
from lib import regex
from lib.check_types import is_unicode
from lib.errors import RelaxError
from lib.warnings import RelaxWarning


def parse_token(token, verbosity=False):
    """Parse the token string and return a list of identifying numbers and names.

    Firstly the token is split by the ',' character into its individual elements and all whitespace stripped from the elements.  Numbers are converted to integers, names are left as strings, and ranges are converted into the full list of integers.


    @param token:       The identification string, the elements of which are separated by commas. Each element can be either a single number, a range of numbers (two numbers separated by '-'), or a name.
    @type token:        str
    @keyword verbosity: A flag which if True will cause a number of printouts to be activated.
    @type verbosity:    bool
    @return:            A list of identifying numbers and names.
    @rtype:             list of int and str
    """

    # No token.
    if token == None:
        return []

    # Convert to a list.
    if not isinstance(token, list):
        tokens = [token]
    else:
        tokens = token

    # Loop over the tokens.
    id_list = []
    for token in tokens:
        # Split by the ',' character.
        elements = token.split(',')

        # Loop over the elements.
        for element in elements:
            # Strip all leading and trailing whitespace.
            element = element.strip()

            # Find all '-' characters (ignoring the first character, i.e. a negative number).
            indices= []
            for i in range(1, len(element)):
                if element[i] == '-':
                    indices.append(i)

            # Range.
            valid_range = True
            if indices:
                # Invalid range element, only one range char '-' and one negative sign is allowed.
                if len(indices) > 2:
                    if verbosity:
                        print("The range element " + repr(element) + " is invalid.  Assuming the '-' character does not specify a range.")
                    valid_range = False

                # Convert the two numbers to integers.
                try:
                    start = int(element[:indices[0]])
                    end = int(element[indices[0]+1:])
                except ValueError:
                    if verbosity:
                        print("The range element " + repr(element) + " is invalid as either the start or end of the range are not integers.  Assuming the '-' character does not specify a range.")
                    valid_range = False

                # Test that the starting number is less than the end.
                if valid_range and start >= end:
                    if verbosity:
                        print("The starting number of the range element " + repr(element) + " needs to be less than the end number.  Assuming the '-' character does not specify a range.")
                    valid_range = False

                # Create the range and append it to the list.
                if valid_range:
                    for i in range(start, end+1):
                        id_list.append(i)

                # Just append the string (even though it might be junk).
                else:
                    id_list.append(element)

            # Number or name.
            else:
                # Try converting the element into an integer.
                try:
                    element = int(element)
                except ValueError:
                    pass

                # Append the element.
                id_list.append(element)

    # Return the identifying list.
    return id_list


def tokenise(selection):
    """Split the input selection string returning the mol_token, res_token, and spin_token strings.

    The mol_token is identified as the text from the '#' to either the ':' or '@' characters or the end of the string.

    The res_token is identified as the text from the ':' to either the '@' character or the end of the string.

    The spin_token is identified as the text from the '@' to the end of the string.


    @param selection:   The selection identifier.
    @type selection:    str
    @return:            The mol_token, res_token, and spin_token.
    @rtype:             3-tuple of str or None
    """

    # No selection.
    if selection == None:
        return None, None, None


    # Walk along the ID string, separating the molecule, residue, and spin data.
    mol_info = ''
    res_info = ''
    spin_info = ''
    pos = 'mol'
    for i in range(len(selection)):
        # Find forbidden boolean operators.
        if selection[i] == '|':
            raise RelaxError("The boolean operator '|' is not supported for individual spin selections.")

        # Hit the residue position.
        if selection[i] == ':':
            if pos == 'spin':
                raise RelaxError("Invalid selection string '%s'." % selection)
            pos = 'res'

        # Hit the spin position.
        if selection[i] == '@':
            pos = 'spin'

        # Append the data.
        if pos == 'mol':
            mol_info = mol_info + selection[i]
        if pos == 'res':
            res_info = res_info + selection[i]
        if pos == 'spin':
            spin_info = spin_info + selection[i]


    # Molecules.
    ############

    # Molecule identifier.
    if mol_info:
        # Find boolean operators.
        if '&' in mol_info:
            raise RelaxError("The boolean operator '&' is not supported for the molecule component of individual spin IDs.")

        # Checks:
        #   No residue identification characters are allowed.
        #   No spin identification characters are allowed.
        #   First character must be '#'.
        #   Only 1 '#' allowed.
        if ':' in mol_info or '@' in mol_info or mol_info[0] != '#' or mol_info.count('#') != 1:
            raise RelaxError("Invalid molecule selection '%s'." % mol_info)

        # ID.
        mol_token = mol_info[1:]

    # No molecule identifier.
    else:
        mol_token = None


    # Residues.
    ###########

    # Residue identifier.
    if res_info:
        # Only max 1 '&' allowed.
        if res_info.count('&') > 1:
            raise RelaxError("Only one '&' boolean operator is supported for the residue component of individual spin IDs.")

        # Split by '&'.
        res_token = res_info.split('&')

        # Check and remove the ':' character.
        for i in range(len(res_token)):
            # Checks:
            #   No molecule identification characters are allowed.
            #   No spin identification characters are allowed.
            #   First character must be ':'.
            #   Only 1 ':' allowed.
            if '#' in res_token[i] or '@' in res_token[i] or res_token[i][0] != ':' or res_token[i].count(':') != 1:
                raise RelaxError("Invalid residue selection '%s'." % res_info)

            # Strip.
            res_token[i] = res_token[i][1:]

        # Convert to a string if only a single item.
        if len(res_token) == 1:
            res_token = res_token[0]

    # No residue identifier.
    else:
        res_token = None


    # Spins.
    ########

    # Spin identifier.
    if spin_info:
        # Only max 1 '&' allowed.
        if spin_info.count('&') > 1:
            raise RelaxError("Only one '&' boolean operator is supported for the spin component of individual spin IDs.")

        # Split by '&'.
        spin_token = spin_info.split('&')

        # Check and remove the ':' character.
        for i in range(len(spin_token)):
            # Checks:
            #   No molecule identification characters are allowed.
            #   No residue identification characters are allowed.
            #   First character must be '@'.
            #   Only 1 '@' allowed.
            if '#' in spin_token[i] or ':' in spin_token[i] or spin_token[i][0] != '@' or spin_token[i].count('@') != 1:
                raise RelaxError("Invalid spin selection '%s'." % spin_info)

            # Strip.
            spin_token[i] = spin_token[i][1:]

        # Convert to a string if only a single item.
        if len(spin_token) == 1:
            spin_token = spin_token[0]

    # No spin identifier.
    else:
        spin_token = None


    # End.
    ######

    # Improper selection string.
    if mol_token == None and res_token == None and spin_token == None:
        raise RelaxError("The selection string '%s' is invalid." % selection)

    # Return the three tokens.
    return mol_token, res_token, spin_token



class Selection(object):
    """An object containing mol-res-spin selections.

    A Selection object represents either a set of selected molecules, residues and spins, or the union or intersection of two other Selection objects.
    """

    def __init__(self, select_string):
        """Initialise a Selection object.

        @param select_string:   A mol-res-spin selection string.
        @type select_string:    string
        """

        # Handle Unicode.
        if is_unicode(select_string):
            select_string = str(select_string)

        self._union = None
        self._intersect = None

        self.molecules = []
        self.residues = []
        self.spins = []

        if not select_string:
            return

        # Read boolean symbols from right to left:
        and_index = select_string.rfind('&')
        or_index = select_string.rfind('|')

        if and_index > or_index:
            sel0 = Selection(select_string[:and_index].strip())
            sel1 = Selection(select_string[and_index+1:].strip())
            self.intersection(sel0, sel1)

        elif or_index > and_index:
            sel0 = Selection(select_string[:or_index].strip())
            sel1 = Selection(select_string[or_index+1:].strip())
            self.union(sel0, sel1)

        # No booleans, so parse as simple selection:
        else:
            mol_token, res_token, spin_token = tokenise(select_string)
            self.molecules = parse_token(mol_token)
            self.residues = parse_token(res_token)
            self.spins = parse_token(spin_token)


    def contains_mol(self, mol=None):
        """Determine if the molecule name, in string form, is contained in this selection object.

        @keyword mol:   The name of the molecule.
        @type mol:      str or None
        @return:        The answer of whether the molecule is contained withing the selection object.
        @rtype:         bool
        """

        # The selection object is a union.
        if self._union:
            return self._union[0].contains_mol(mol) or self._union[1].contains_mol(mol)

        # The selection object is an intersection.
        elif self._intersect:
            return self._intersect[0].contains_mol(mol) and self._intersect[1].contains_mol(mol)

        # The check.
        if regex.search(self.molecules, mol):
            return True

        # Nothingness.
        if not self.molecules:
            return True

        # No match.
        return False


    def contains_res(self, res_num=None, res_name=None, mol=None):
        """Determine if the residue name, in string form, is contained in this selection object.

        @keyword res_num:   The residue number.
        @type res_num:      int or None
        @keyword res_name:  The residue name.
        @type res_name:     str or None
        @keyword mol:       The molecule name.
        @type mol:          str or None
        @return:            The answer of whether the molecule is contained withing the selection object.
        @rtype:             bool
        """

        # The selection object is a union.
        if self._union:
            return self._union[0].contains_res(res_num, res_name, mol) or self._union[1].contains_res(res_num, res_name, mol)

        # The selection object is an intersection.
        elif self._intersect:
            return self._intersect[0].contains_res(res_num, res_name, mol) and self._intersect[1].contains_res(res_num, res_name, mol)

        # Does it contain the molecule.
        select_mol = self.contains_mol(mol)

        # Residue selection flag.
        select_res = False

        # The residue checks.
        if res_num in self.residues or regex.search(self.residues, res_name):
            select_res = True

        # Nothingness.
        if not self.residues:
            select_res = True

        # Return the result.
        return select_res and select_mol


    def contains_spin(self, spin_num=None, spin_name=None, res_num=None, res_name=None, mol=None):
        """Determine if the spin is contained in this selection object.

        @keyword spin_num:  The spin number.
        @type spin_num:     int or None
        @keyword spin_name: The spin name.
        @type spin_name:    str or None
        @keyword res_num:   The residue number.
        @type res_num:      int or None
        @keyword res_name:  The residue name.
        @type res_name:     str or None
        @keyword mol:       The molecule name.
        @type mol:          str or None
        @return:            The answer of whether the spin is contained withing the selection object.
        @rtype:             bool
        """

        # The selection object is a union.
        if self._union:
            return self._union[0].contains_spin(spin_num, spin_name, res_num, res_name, mol) or self._union[1].contains_spin(spin_num, spin_name, res_num, res_name, mol)

        # The selection object is an intersection.
        elif self._intersect:
            return self._intersect[0].contains_spin(spin_num, spin_name, res_num, res_name, mol) and self._intersect[1].contains_spin(spin_num, spin_name, res_num, res_name, mol)

        # Does it contain the molecule.
        select_mol = self.contains_mol(mol)

        # Does it contain the residue.
        select_res = self.contains_res(res_num, res_name, mol)

        # Spin selection flag.
        select_spin = False

        # The spin checks.
        if spin_num in self.spins or regex.search(self.spins, spin_name):
            select_spin = True

        # Nothingness.
        if not self.spins:
            select_spin = True

        # Return the result.
        return select_spin and select_res and select_mol


    def has_molecules(self):
        """Determine if the selection object contains molecules.

        @return:            The answer of whether the selection contains molecules.
        @rtype:             bool
        """

        # The selection object is a union.
        if self._union:
            return self._union[0].has_molecules() or self._union[1].has_molecules()

        # The selection object is an intersection.
        elif self._intersect:
            return self._intersect[0].has_molecules() and self._intersect[1].has_molecules()

        # Molecules are present.
        if self.molecules:
            return True


    def has_residues(self):
        """Determine if the selection object contains residues.

        @return:            The answer of whether the selection contains residues.
        @rtype:             bool
        """

        # The selection object is a union.
        if self._union:
            return self._union[0].has_residues() or self._union[1].has_residues()

        # The selection object is an intersection.
        elif self._intersect:
            return self._intersect[0].has_residues() and self._intersect[1].has_residues()

        # Residues are present.
        if self.residues:
            return True


    def has_spins(self):
        """Determine if the selection object contains spins.

        @return:            The answer of whether the selection contains spins.
        @rtype:             bool
        """

        # The selection object is a union.
        if self._union:
            return self._union[0].has_spins() or self._union[1].has_spins()

        # The selection object is an intersection.
        elif self._intersect:
            return self._intersect[0].has_spins() and self._intersect[1].has_spins()

        # Spins are present.
        if self.spins:
            return True


    def intersection(self, select_obj0, select_obj1):
        """Make this Selection object the intersection of two other Selection objects.

        @param select_obj0: First Selection object in intersection.
        @type select_obj0:  Selection instance.
        @param select_obj1: First Selection object in intersection.
        @type select_obj1:  Selection instance.
        """

        # Check that nothing is set.
        if self._union or self._intersect or self.molecules or self.residues or self.spins:
            raise RelaxError("Cannot define multiple Boolean relationships between Selection objects")

        # Create the intersection.
        self._intersect = (select_obj0, select_obj1)


    def union(self, select_obj0, select_obj1):
        """Make this Selection object the union of two other Selection objects.

        @param select_obj0: First Selection object in intersection.
        @type select_obj0:  Selection instance.
        @param select_obj1: First Selection object in intersection.
        @type select_obj1:  Selection instance.
        """

        # Check that nothing is set.
        if self._union or self._intersect or self.molecules or self.residues or self.spins:
            raise RelaxError("Cannot define multiple Boolean relationships between Selection objects")

        # Create the union.
        self._union = (select_obj0, select_obj1)
