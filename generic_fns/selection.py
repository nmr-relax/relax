###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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

from os import F_OK, access
from re import compile, match


class Selection:
    def __init__(self, relax):
        """Base class containing functions for the manipulation of residue selection."""

        self.relax = relax


    def reverse(self, run=None):
        """Function for the reversal of residue selection."""

        # Create the list of runs.
        self.runs = self.relax.generic.runs.list_of_runs(run)

        # Loop over the runs.
        for self.run in self.runs:
            # Test if the run exists.
            if not self.run in self.relax.data.run_names:
                raise RelaxNoRunError, self.run

            # Test if sequence data is loaded.
            if not len(self.relax.data.res[self.run]):
                raise RelaxNoSequenceError, self.run

            # Loop over the sequence and reverse the selection flag.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Remap the data structure 'self.relax.data.res[self.run][i]'.
                data = self.relax.data.res[self.run][i]

                # Reverse the selection.
                if data.user_select:
                    data.user_select = 0
                else:
                    data.user_select = 1


    def sel_all(self, run=None):
        """Function for selecting all residues."""

        # Create the list of runs.
        self.runs = self.relax.generic.runs.list_of_runs(run)

        # Loop over the runs.
        for self.run in self.runs:
            # Test if the run exists.
            if not self.run in self.relax.data.run_names:
                raise RelaxNoRunError, self.run

            # Test if sequence data is loaded.
            if not len(self.relax.data.res[self.run]):
                raise RelaxNoSequenceError, self.run

            # Loop over the sequence and set the selection flag to 1.
            for i in xrange(len(self.relax.data.res[self.run])):
                self.relax.data.res[self.run][i].user_select = 1


    def sel_read(self, run=None, file=None, dir=None, change_all=None):
        """Function for selecting the residues contained in a file."""

        # Extract the data from the file.
        file_data = self.relax.IO.extract_data(file, dir)

        # Strip the data.
        file_data = self.relax.IO.strip(file_data)

        # Create the list of residues to select.
        select = []
        for i in xrange(len(file_data)):
            try:
                select.append(int(file_data[i][0]))
            except:
                raise RelaxError, "Improperly formatted file."

        # Create the list of runs.
        self.runs = self.relax.generic.runs.list_of_runs(run)

        # Loop over the runs.
        no_match = 1
        for self.run in self.runs:
            # Test if the run exists.
            if not self.run in self.relax.data.run_names:
                raise RelaxNoRunError, self.run

            # Test if sequence data is loaded.
            if not len(self.relax.data.res[self.run]):
                raise RelaxNoSequenceError, self.run

            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Remap the data structure 'self.relax.data.res[self.run][i]'.
                data = self.relax.data.res[self.run][i]

                # Unselect all residues.
                if change_all:
                    data.user_select = 0

                # Select the residue if it is in the list select.
                if data.num in select:
                    data.user_select = 1

                # Match flag.
                no_match = 0

        # No residue matched.
        if no_match:
            print "No residues match."


    def sel_res(self, run=None, num=None, name=None, change_all=None):
        """Function for selecting specific residues."""

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
            if not self.run in self.relax.data.run_names:
                raise RelaxNoRunError, self.run

            # Test if sequence data is loaded.
            if not len(self.relax.data.res[self.run]):
                raise RelaxNoSequenceError, self.run

            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Remap the data structure 'self.relax.data.res[self.run][i]'.
                data = self.relax.data.res[self.run][i]

                # Unselect all residues.
                if change_all:
                    data.user_select = 0

                # Skip the residue if there is no match to 'num'.
                if type(num) == int:
                    if not data.num == num:
                        continue
                elif type(num) == str:
                    if not match(num, `data.num`):
                        continue

                # Skip the residue if there is no match to 'name'.
                if name != None:
                    if not match(name, data.name):
                        continue

                # Select the residue.
                data.user_select = 1

                # Match flag.
                no_match = 0

        # No residue matched.
        if no_match:
            print "No residues match."


    def unsel_all(self, run=None):
        """Function for unselecting all residues."""

        # Create the list of runs.
        self.runs = self.relax.generic.runs.list_of_runs(run)

        # Loop over the runs.
        for self.run in self.runs:
            # Test if the run exists.
            if not self.run in self.relax.data.run_names:
                raise RelaxNoRunError, self.run

            # Test if sequence data is loaded.
            if not len(self.relax.data.res[self.run]):
                raise RelaxNoSequenceError, self.run

            # Loop over the sequence and set the selection flag to 0.
            for i in xrange(len(self.relax.data.res[self.run])):
                self.relax.data.res[self.run][i].user_select = 0


    def unsel_read(self, run=None, file=None, dir=None, change_all=None):
        """Function for unselecting the residues contained in a file."""

        # Extract the data from the file.
        file_data = self.relax.IO.extract_data(file, dir)

        # Strip the data.
        file_data = self.relax.IO.strip(file_data)

        # Create the list of residues to unselect.
        unselect = []
        for i in xrange(len(file_data)):
            try:
                unselect.append(int(file_data[i][0]))
            except:
                raise RelaxError, "Improperly formatted file."

        # Create the list of runs.
        self.runs = self.relax.generic.runs.list_of_runs(run)

        # Loop over the runs.
        no_match = 1
        for self.run in self.runs:
            # Test if the run exists.
            if not self.run in self.relax.data.run_names:
                raise RelaxNoRunError, self.run

            # Test if sequence data is loaded.
            if not len(self.relax.data.res[self.run]):
                raise RelaxNoSequenceError, self.run

            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Remap the data structure 'self.relax.data.res[self.run][i]'.
                data = self.relax.data.res[self.run][i]

                # Select all residues.
                if change_all:
                    data.user_select = 1

                # Unselect the residue if it is in the list unselect.
                if data.num in unselect:
                    data.user_select = 0

                # Match flag.
                no_match = 0

        # No residue matched.
        if no_match:
            print "No residues match."


    def unsel_res(self, run=None, num=None, name=None, change_all=None):
        """Function for unselecting specific residues."""

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
            if not self.run in self.relax.data.run_names:
                raise RelaxNoRunError, self.run

            # Test if sequence data is loaded.
            if not len(self.relax.data.res[self.run]):
                raise RelaxNoSequenceError, self.run

            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Remap the data structure 'self.relax.data.res[self.run][i]'.
                data = self.relax.data.res[self.run][i]

                # Select all residues.
                if change_all:
                    data.user_select = 1

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
                data.user_select = 0

                # Match flag.
                no_match = 0

        # No residue matched.
        if no_match:
            print "No residues match."
