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

import help


class Unselect:
    def __init__(self, relax):
        """Class containing the functions for unselecting residues."""

        # Place relax in the class namespace.
        self.relax = relax

        # Help.
        self.__relax_help__ = help.relax_class_help


    def all(self):
        """Function for unselecting all residues.

        Examples
        ~~~~~~~~

        To unselect all residues type:

        relax> unselect.all()
        """

        # Function intro test.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "unselect.all()"
            print text

        # Execture the functional code.
        self.relax.generic.selection.unsel_all()


    def res(self, num=None, name=None, change_all=0):
        """Function for unselecting specific residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        num:  The residue number.

        name:  The residue name.

        change_all:  A flag specifying if all other residues should be changed.


        Description
        ~~~~~~~~~~~

        The residue number can be either an integer for unselecting a single residue or a python
        regular expression, in string form, for unselecting multiple residues.  For details about
        using regular expression, see the python documentation for the module 're'.

        The residue name argument must be a string.  Regular expression is also allowed.

        The 'change_all' flag argument default is zero meaning that all residues currently either
        selected or unselected will remain that way.  Setting the argument to 1 will cause all
        residues not specified by 'num' or 'name' to become selected.


        Examples
        ~~~~~~~~

        To unselect all glycines type:

        relax> unselect.res(name='GLY|ALA')
        relax> unselect.res(name='[GA]L[YA]')

        To unselect residue 12 MET type:

        relax> unselect.res(12)
        relax> unselect.res(12, 'MET')
        relax> unselect.res('12')
        relax> unselect.res('12', 'MET')
        relax> unselect.res(num='12', name='MET')
        """

        # Function intro test.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "unselect.res("
            text = text + "num=" + `num`
            text = text + ", name=" + `name`
            text = text + ", change_all=" + `change_all` + ")"
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

        # Change all flag.
        if type(change_all) != int or (change_all != 0 and change_all != 1):
            raise RelaxBinError, ('change_all', change_all)

        # Execture the functional code.
        self.relax.generic.selection.unsel_res(num=num, name=name, change_all=change_all)


    def reverse(self):
        """Function for the reversal of the residue selection.

        Examples
        ~~~~~~~~

        To unselect all currently selected residues and select those which are unselected type:

        relax> unselect.reverse()
        """

        # Function intro test.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "unselect.reverse()"
            print text

        # Execture the functional code.
        self.relax.generic.selection.reverse()
