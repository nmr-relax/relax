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

from re import compile, match


class Selection:
    def __init__(self, relax):
        """Base class containing functions for the manipulation of residue selection."""

        self.relax = relax


    def reverse(self):
        """Function for the reversal of residue selection."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Loop over the sequence and reverse the selection flag.
        for i in xrange(len(self.relax.data.res)):
            if self.relax.data.res[i].select:
                self.relax.data.res[i].select = 0
            else:
                self.relax.data.res[i].select = 1


    def sel_all(self):
        """Function for selecting all residues."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Loop over the sequence and set the selection flag to 1.
        for i in xrange(len(self.relax.data.res)):
            self.relax.data.res[i].select = 1


    def sel_res(self, num=None, name=None, change_all=None):
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

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Unselect all residues.
            if change_all:
                self.relax.data.res[i].select = 0

            # Skip the residue if there is no match to 'num'.
            if type(num) == int:
                if not self.relax.data.res[i].num == num:
                    continue
            elif type(num) == str:
                if not match(num, `self.relax.data.res[i].num`):
                    continue

            # Skip the residue if there is no match to 'name'.
            if name != None:
                if not match(name, self.relax.data.res[i].name):
                    continue

            # Select the residue.
            self.relax.data.res[i].select = 1


    def unsel_all(self):
        """Function for unselecting all residues."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Loop over the sequence and set the selection flag to 0.
        for i in xrange(len(self.relax.data.res)):
            self.relax.data.res[i].select = 0


    def unsel_res(self, num=None, name=None, change_all=None):
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

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Select all residues.
            if change_all:
                self.relax.data.res[i].select = 1

            # Skip the residue if there is no match to 'num'.
            if type(num) == int:
                if not self.relax.data.res[i].num == num:
                    continue
            if type(num) == str:
                if not match(num, `self.relax.data.res[i].num`):
                    continue

            # Skip the residue if there is no match to 'name'.
            if name != None:
                if not match(name, self.relax.data.res[i].name):
                    continue

            # Unselect the residue.
            self.relax.data.res[i].select = 0
