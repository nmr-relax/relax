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
        """Class for unselecting residues."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def all(self, run=None):
        """Function for unselecting all residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run(s).  By supplying a single string, array of strings, or None, a
        single run, multiple runs, or all runs will be selected respectively.


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
        if run != None and type(run) != str and type(run) != list:
            raise RelaxNoneStrListError, ('run', run)
        if type(run) == list:
            for i in xrange(len(run)):
                if type(run[i]) != str:
                    raise RelaxListStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.selection.unsel_all(run=run)


    def read(self, run=None, file=None, dir=None, change_all=0, column=0):
        """Function for unselecting the residues contained in a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run(s).  By supplying a single string, array of strings, or None, a
        single run, multiple runs, or all runs will be selected respectively.

        file:  The name of the file containing the list of residues to unselect.

        dir:  The directory where the file is located.

        change_all:  A flag specifying if all other residues should be changed.

        column:  The column containing the residue numbers (defaulting to 0, the first column).


        Description
        ~~~~~~~~~~~

        Empty lines and lines beginning with a hash are ignored.

        The 'change_all' flag argument default is zero meaning that all residues currently either
        selected or unselected will remain that way.  Setting the argument to 1 will cause all
        residues not specified in the file to be selected.


        Examples
        ~~~~~~~~

        To unselect all overlapped residues in the file 'unresolved', type:

        relax> unselect.read('noe', 'unresolved')
        relax> unselect.read(run='noe', file='unresolved')

        To unselect the residues in the second column of the relaxation data file 'r1.600' while
        selecting all other residues, type one of: 

        relax> unselect.read('test', 'r1.600', change_all=1, column=1)
        relax> unselect.read(run='test', file='r1.600', change_all=1, column=1)
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "unselect.read("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", change_all=" + `change_all`
            text = text + ", column=" + `column` + ")"
            print text

        # The run argument.
        if run != None and type(run) != str and type(run) != list:
            raise RelaxNoneStrListError, ('run', run)
        if type(run) == list:
            for i in xrange(len(run)):
                if type(run[i]) != str:
                    raise RelaxListStrError, ('run', run)

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Change all flag.
        if type(change_all) != int or (change_all != 0 and change_all != 1):
            raise RelaxBinError, ('change_all', change_all)

        # The residue column.
        if type(column) != int:
            raise RelaxIntError, ('residue number column', column)

        # Execute the functional code.
        self.__relax__.generic.selection.unsel_read(run=run, file=file, dir=dir, change_all=change_all, column=column)


    def res(self, run=None, num=None, name=None, change_all=0):
        """Function for unselecting specific residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run(s).  By supplying a single string, array of strings, or None, a
        single run, multiple runs, or all runs will be selected respectively.

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
        if run != None and type(run) != str and type(run) != list:
            raise RelaxNoneStrListError, ('run', run)
        if type(run) == list:
            for i in xrange(len(run)):
                if type(run[i]) != str:
                    raise RelaxListStrError, ('run', run)

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

        run:  The name of the run(s).  By supplying a single string, array of strings, or None, a
        single run, multiple runs, or all runs will be selected respectively.


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
        if run != None and type(run) != str and type(run) != list:
            raise RelaxNoneStrListError, ('run', run)
        if type(run) == list:
            for i in xrange(len(run)):
                if type(run[i]) != str:
                    raise RelaxListStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.selection.reverse(run=run)
