###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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
from specific_fns.model_free import Model_free
from specific_fns.jw_mapping import Jw_mapping
from specific_fns.noe import Noe


class Grace:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for interfacing with Grace."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def view(self, run=None, data_type=None, file=None, dir='grace', grace_exe='xmgrace', force=0):
        """Function for running Grace.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        data_type:  The data type.

        file:  The name of the file.

        dir:  The directory name.

        grace_exe:  The Grace executable file.

        force:  A flag which, if set to 1, will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        This function can be used either to execute grace, opening the specified file, or to create
        the grace '.agr' file and the execute grace.  If the run and data_type arguments are
        supplied, the second of these two options is pursued.  To simply execute grace, leave the
        run and data_type arguments as None.

        If the directory name is set to None, the file will be placed in the current working
        directory.

        The force flag will only have an effect if the run argument is not None.


        Examples
        ~~~~~~~~

        To view the file 's2.agr' in the directory 'grace', type:

        relax> grace.view(file='s2.agr')
        relax> grace.view(file='s2.agr', dir='grace')


        To write the NOE values from the run 'noe' to the grace file 'noe.agr' and then view the
        file, type:

        relax> grace.view('noe', 'noe', 'noe.agr')
        relax> grace.view('noe', data_type='noe', file='noe.agr')
        relax> grace.view(run='noe', data_type='noe', file='noe.agr', dir='grace')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "grace.view("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", grace_exe=" + `grace_exe` + ")"
            print text

        # The run name.
        if run != None and type(run) != str:
            raise RelaxNoneStrError, ('run', run)

        # Data type.
        if data_type != None and type(data_type) != str:
            raise RelaxNoneStrError, ('data type', data_type)

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Grace executable file.
        if type(grace_exe) != str:
            raise RelaxStrError, ('Grace executable file', grace_exe)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # Execute the functional code.
        self.__relax__.generic.grace.view(run=run, data_type=data_type, file=file, dir=dir, grace_exe=grace_exe, force=force)


    def write(self, run=None, data_type=None, file=None, dir='grace', force=0):
        """Function for creating a grace '.agr' file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        data_type:  The data type.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which, if set to 1, will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the file will be placed in the current working directory.

        The data type argument should be a string.


        Examples
        ~~~~~~~~

        To write the NOE values from the run 'noe' to the grace file 'noe.agr', type:

        relax> grace.write('noe', 'noe', 'noe.agr')
        relax> grace.write('noe', data_type='noe', file='noe.agr')
        relax> grace.write(run='noe', data_type='noe', file='noe.agr', dir='grace')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "grace.write("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Data type.
        if type(data_type) != str:
            raise RelaxStrError, ('data type', data_type)

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # Execute the functional code.
        self.__relax__.generic.grace.write(run=run, data_type=data_type, file=file, dir=dir, force=force)


    # Docstring modification.
    #########################

    __re_doc__ = """

        Regular expression
        ~~~~~~~~~~~~~~~~~~

        The python function 'match', which uses regular expression, is used to determine which data
        type to set values to, therefore various data_type strings can be used to select the same
        data type.  Patterns used for matching for specific data types are listed below.  Regular
        expression is also used in residue name and number selections, except this time the user
        supplies the regular expression string.

        This is a short description of python regular expression, for more information, see the
        regular expression syntax section of the Python Library Reference.  Some of the regular
        expression syntax used in this function is:

            [] - A sequence or set of characters to match to a single character.  For example,
            '[Ss]2' will match both 'S2' and 's2'.

            ^ - Match the start of the string.

            $ - Match the end of the string.  For example, '^[Ss]2$' will match 's2' but not 'S2f'
            or 's2s'.

    """

    # View function.
    view.__doc__ = view.__doc__ + "\n\n" + __re_doc__ + "\n"
    view.__doc__ = view.__doc__ + Model_free.get_data_name.__doc__ + "\n\n"
    view.__doc__ = view.__doc__ + Jw_mapping.get_data_name.__doc__ + "\n\n"
    view.__doc__ = view.__doc__ + Noe.get_data_name.__doc__ + "\n"

    # Write function.
    write.__doc__ = write.__doc__ + "\n\n" + __re_doc__ + "\n"
    write.__doc__ = write.__doc__ + Model_free.get_data_name.__doc__ + "\n\n"
    write.__doc__ = write.__doc__ + Jw_mapping.get_data_name.__doc__ + "\n\n"
    write.__doc__ = write.__doc__ + Noe.get_data_name.__doc__ + "\n"
