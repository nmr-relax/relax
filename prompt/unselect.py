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
        # Help.
        self.__relax_help__ = \
        """Class containing functions for unselecting residues."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def all(self, run=None):
        """Function for unselecting all residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.


        Description
        ~~~~~~~~~~~

        If the run argument is set to the default of None, then all runs will be affected, otherwise
        only the supplied run will be affected.


        Examples
        ~~~~~~~~

        To unselect all residues type:

        relax> unselect.all()


        To unselect all residues for the run 'srls_m1', type:

        relax> select.all('srls_m1')
        relax> select.all(run='srls_m1')
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "unselect.all("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.selection.unsel_all(run=run)


    def res(self, run=None, num=None, name=None, change_all=0):
        """Function for unselecting specific residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        num:  The residue number.

        name:  The residue name.

        change_all:  A flag specifying if all other residues should be changed.


        Description
        ~~~~~~~~~~~

        If the run argument is set to the default of None, then all runs will be affected, otherwise
        only the supplied run will be affected.

        The residue number can be either an integer for unselecting a single residue or a python
        regular expression, in string form, for unselecting multiple residues.  For details about
        using regular expression, see the python documentation for the module 're'.

        The residue name argument must be a string.  Regular expression is also allowed.

        The 'change_all' flag argument default is zero meaning that all residues currently either
        selected or unselected will remain that way.  Setting the argument to 1 will cause all
        residues not specified by 'num' or 'name' to become selected.


        Examples
        ~~~~~~~~

        To unselect all glycines for the run 'm5', type:

        relax> unselect.res(run='m5', name='GLY|ALA')
        relax> unselect.res(run='m5', name='[GA]L[YA]')

        To unselect residue 12 MET type:

        relax> unselect.res('m5', 12)
        relax> unselect.res('m5', 12, 'MET')
        relax> unselect.res('m5', '12')
        relax> unselect.res('m5', '12', 'MET')
        relax> unselect.res(run='m5', num='12', name='MET')
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "unselect.res("
            text = text + "run=" + `run`
            text = text + ", num=" + `num`
            text = text + ", name=" + `name`
            text = text + ", change_all=" + `change_all` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

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

        # Execute the functional code.
        self.__relax__.generic.selection.unsel_res(run=run, num=num, name=name, change_all=change_all)


    def reverse(self, run=None):
        """Function for the reversal of the residue selection.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.


        Description
        ~~~~~~~~~~~

        If the run argument is set to the default of None, then all runs will be affected, otherwise
        only the supplied run will be affected.


        Examples
        ~~~~~~~~

        To unselect all currently selected residues and select those which are unselected type:

        relax> unselect.reverse()
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "unselect.reverse("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.selection.reverse(run=run)
