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

import sys

import message


class Shell:
    def __init__(self, relax):
        """The class accessible to the interpreter.

        The purpose of this class is to hide the variables and functions found within the namespace
        of the main class, found below, except for those required for interactive use.  This is an
        abstraction layer designed to avoid user confusion as none of the main class data structures
        are accessible.  For more flexibility use the main class directly.
        """

        # Load the main class into the namespace of this __init__ function.
        x = Main(relax)

        # Place references to the interactive functions within the namespace of this class.
        self.all = x.all
        self.none = x.none
        self.res = x.res
        self.reverse = x.reverse

        # __repr__.
        self.__repr__ = message.main_class


class Main:
    def __init__(self, relax):
        """Class containing the functions for selecting and unselecting residues."""

        self.relax = relax


    def all(self):
        """Function for selection all residues.

        Examples
        ~~~~~~~~

        To select all residues type:

        relax> selection.all()
        """

        # Function intro test.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "selection.all()"
            print text

        # Execture the functional code.
        self.relax.generic.selection.all()


    def none(self):
        """Function for unselecting all residues.

        Examples
        ~~~~~~~~

        To have no residues selected type:

        relax> selection.none()
        """

        # Function intro test.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "selection.none()"
            print text

        # Execture the functional code.
        self.relax.generic.selection.none()


    def res(self, num=None, name=None, unselect=1):
        """Function for the selection of specific residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        num:  The residue number.

        name:  The residue name.

        unselect:  A flag specifying if all other residues should be unselected.

        Description
        ~~~~~~~~~~~

        The residue number can be either an integer for selecting a single residue or a python
        regular expression in string form for selecting integers.  For details about using regular
        expression, see the python documentation for the module 're'.

        The residue name argument must be a string.  Regular expression is also allowed.

        If the unselect argument is 0, then the current selection is unmodified and the residues
        matched using the number and name arguments will be selected.  If on the other hand unselect
        is 1, then all residues not selected using the number and name arguments will be unselected.


        Examples
        ~~~~~~~~

        To select only glycines and alanines, assuming they have been loaded with the names GLY and
        ALA, type:

        relax> selection.res(name='GLY|ALA', unselect=1)
        relax> selection.res(name='[GA]L[YA]', unselect=1)

        To select residue 5 CYS in addition to the currently selected residues, type:

        relax> selection.res(5)
        relax> selection.res(5, 'CYS')
        relax> selection.res('5')
        relax> selection.res('5', 'CYS')
        relax> selection.res(num='5', name='CYS')
        """

        # Function intro test.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "selection.res("
            text = text + "num=" + `num`
            text = text + ", name=" + `name`
            text = text + ", unselect=" + `unselect` + ")"
            print text

        # Residue number.
        if num != None and type(num) != int and type(num) != str:
            raise RelaxNoneIntStrError, ('residue number', num)

        # Residue name.
        if name != None and type(name) != str:
            raise RelaxNoneStrError, ('residue name', name)

        # Neither are given.
        if num == None and name == None:
            raise RelaxError, "At least one of the number or name arguments is required."

        # Unselect flag.
        if type(unselect) != int or (unselect != 0 and unselect != 1):
            raise RelaxBinError, ('unselect', unselect)

        # Execture the functional code.
        self.relax.generic.selection.res(num=num, name=name, unselect=unselect)


    def reverse(self):
        """Function for the reversal of the residue selection.

        Examples
        ~~~~~~~~

        To unselect all currently selected residues and select those which are unselected type:

        relax> selection.reverse()
        """

        # Function intro test.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "selection.reverse()"
            print text

        # Execture the functional code.
        self.relax.generic.selection.reverse()
