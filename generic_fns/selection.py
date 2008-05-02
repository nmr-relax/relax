###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2008 Edward d'Auvergne                        #
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
from re import compile, match, search, split
from string import replace, strip
from textwrap import fill
from warnings import warn

# relax module imports.
from data import Data as relax_data_store
from data.mol_res_spin import MoleculeContainer, ResidueContainer, SpinContainer
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoSequenceError, RelaxRegExpError, RelaxResSelectDisallowError, RelaxSpinSelectDisallowError
from relax_warnings import RelaxWarning


def desel_all(self, run=None):
    """Function for deselecting all residues."""

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

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
            raise RelaxNoPipeError, self.run

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

            # Deselect the residue if it is in the list deselect.
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
            raise RelaxNoPipeError, self.run

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

            # Deselect the residue.
            data.select = 0

            # Match flag.
            no_match = 0

    # No residue matched.
    if no_match:
        print "No residues match."


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
            raise RelaxNoPipeError, self.run

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
            raise RelaxNoPipeError, self.run

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
            raise RelaxNoPipeError, self.run

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
