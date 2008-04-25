###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2006 Edward d'Auvergne                            #
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
import sys

# relax module imports.
import help
from relax_errors import RelaxBinError, RelaxError, RelaxIntError, RelaxListStrError, RelaxNoneIntStrError, RelaxNoneStrError, RelaxNoneStrListError, RelaxStrError
from generic_fns.selection import reverse


class Select:
    __boolean_doc = """
        Boolean operators
        ~~~~~~~~~~~~~~~~~

        The 'boolean' keyword argument can be used to change how spin systems are selected.  The
        allowed values are: 'OR', 'NOR', 'AND', 'NAND', 'XOR', 'XNOR'.  The following table details
        how the selections will occur for the different boolean operators.
        __________________________________________________________
        |                    |   |   |   |   |   |   |   |   |   |
        | Spin system        | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
        |____________________|___|___|___|___|___|___|___|___|___|
        |                    |   |   |   |   |   |   |   |   |   |
        | Original selection | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | 1 |
        |                    |   |   |   |   |   |   |   |   |   |
        | New selection      | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
        |____________________|___|___|___|___|___|___|___|___|___|
        |                    |   |   |   |   |   |   |   |   |   |
        | OR                 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 |
        |                    |   |   |   |   |   |   |   |   |   |
        | NOR                | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
        |                    |   |   |   |   |   |   |   |   |   |
        | AND                | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
        |                    |   |   |   |   |   |   |   |   |   |
        | NAND               | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 |
        |                    |   |   |   |   |   |   |   |   |   |
        | XOR                | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 1 |
        |                    |   |   |   |   |   |   |   |   |   |
        | XNOR               | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 1 | 0 |
        |____________________|___|___|___|___|___|___|___|___|___|
    """


    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for selecting residues."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def all(self, run=None):
        """Function for selecting all residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run(s).  By supplying a single string, array of strings, or None, a
        single run, multiple runs, or all runs will be selected respectively.


        Examples
        ~~~~~~~~

        To select all residues for all runs type:

        relax> select.all()


        To select all residues for the run 'srls_m1', type:

        relax> select.all('srls_m1')
        relax> select.all(run='srls_m1')
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "select.all("
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
        self.__relax__.generic.selection.sel_all(run=run)


    def read(self, run=None, file=None, dir=None, boolean='OR', change_all=0, column=0):
        """Function for selecting the residues contained in a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run(s).  By supplying a single string, array of strings, or None, a
        single run, multiple runs, or all runs will be selected respectively.

        file:  The name of the file containing the list of residues to select.

        dir:  The directory where the file is located.

        boolean:  The boolean operator specifying how residues should be selected.

        change_all:  A flag specifying if all other residues should be changed.

        column:  The column containing the residue numbers (defaulting to 0, the first column).


        Description
        ~~~~~~~~~~~

        Empty lines and lines beginning with a hash are ignored.

        The 'change_all' flag argument default is zero meaning that all residues currently either
        selected or deselected will remain that way.  Setting the argument to 1 will cause all
        residues not specified in the file to be deselected.


        Examples
        ~~~~~~~~

        To select all residues in the file 'isolated_peaks', type one of:

        relax> select.read('noe', 'isolated_peaks')
        relax> select.read(run='noe', file='isolated_peaks')

        To select the residues in the second column of the relaxation data file 'r1.600' while
        deselecting all other residues, type one of:

        relax> select.read('test', 'r1.600', change_all=1, column=1)
        relax> select.read(run='test', file='r1.600', change_all=1, column=1)
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "select.read("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", boolean=" + `boolean`
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

        # Boolean operator.
        if type(boolean) != str:
            raise RelaxStrError, ('boolean operator', boolean)

        # Change all flag.
        if type(change_all) != int or (change_all != 0 and change_all != 1):
            raise RelaxBinError, ('change_all', change_all)

        # The residue column.
        if type(column) != int:
            raise RelaxIntError, ('residue number column', column)

        # Execute the functional code.
        self.__relax__.generic.selection.sel_read(run=run, file=file, dir=dir, boolean=boolean, change_all=change_all, column=column)


    def res(self, run=None, num=None, name=None, boolean='OR', change_all=0):
        """Function for selecting specific residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run(s).  By supplying a single string, array of strings, or None, a
        single run, multiple runs, or all runs will be selected respectively.

        num:  The residue number.

        name:  The residue name.

        boolean:  The boolean operator specifying how residues should be selected.

        change_all:  A flag specifying if all other residues should be changed.


        Description
        ~~~~~~~~~~~

        The residue number can be either an integer for selecting a single residue or a python
        regular expression, in string form, for selecting multiple residues.  For details about
        using regular expression, see the python documentation for the module 're'.

        The residue name argument must be a string.  Regular expression is also allowed.

        The 'change_all' flag argument default is zero meaning that all residues currently either
        selected or deselected will remain that way.  Setting the argument to 1 will cause all
        residues not specified by 'num' or 'name' to become deselected.


        Examples
        ~~~~~~~~

        To select only glycines and alanines for the run 'm3', assuming they have been loaded with
        the names GLY and ALA, type:

        relax> select.res(run='m3', name='GLY|ALA', change_all=1)
        relax> select.res(run='m3', name='[GA]L[YA]', change_all=1)

        To select residue 5 CYS in addition to the currently selected residues, type:

        relax> select.res('m3', 5)
        relax> select.res('m3', 5, 'CYS')
        relax> select.res('m3', '5')
        relax> select.res('m3', '5', 'CYS')
        relax> select.res(run='m3', num='5', name='CYS')
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "select.res("
            text = text + "run=" + `run`
            text = text + ", num=" + `num`
            text = text + ", name=" + `name`
            text = text + ", boolean=" + `boolean`
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

        # Boolean operator.
        if type(boolean) != str:
            raise RelaxStrError, ('boolean operator', boolean)

        # Change all flag.
        if type(change_all) != int or (change_all != 0 and change_all != 1):
            raise RelaxBinError, ('change_all', change_all)

        # Execute the functional code.
        self.__relax__.generic.selection.sel_res(run=run, num=num, name=name, boolean=boolean, change_all=change_all)


    def reverse(self, selection=None):
        """Function for the reversal of the spin system selection for the given spins.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        selection:  The selection string identifying the molecules, residues, and spins to reverse
        the selection of.


        Description
        ~~~~~~~~~~~

        If the selection argument is left on the default of None, then the selection status of all
        spin systems of the current data pipe will be reversed.


        Examples
        ~~~~~~~~

        To deselect all currently selected residues and select those which are deselected type:

        relax> select.reverse()
        """

        # Function intro test.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "select.reverse("
            text = text + "selection=" + `selection` + ")"
            print text

        # The selection argument.
        if selection != None and type(selection) != str:
            raise RelaxNoneStrError, ('selection', selection)

        # Execute the functional code.
        reverse(selection=selection)



    # Docstring modification.
    #########################

    # Read function.
    read.__doc__ = read.__doc__ + "\n\n" + __boolean_doc + "\n"
