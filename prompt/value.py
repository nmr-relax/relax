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
from specific_fns.model_free import Model_free


class Value:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for setting data values."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def display(self, run=None, data_type=None):
        """Function for displaying residue specific data values.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        data_type:  The data type.


        Description
        ~~~~~~~~~~~

        This function will display the residue specific data values for the given run.  The
        data type argument can only be a single string.


        Examples
        ~~~~~~~~

        To show all CSA values for the run 'm1', type:

        relax> value.display('m1', 'CSA')

        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.display("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Data type.
        if type(data_type) != str:
            raise RelaxStrError, ('data type', data_type)

        # Execute the functional code.
        self.__relax__.generic.value.display(run=run, data_type=data_type)


    def set(self, run=None, value=None, data_type=None, res_num=None, res_name=None):
        """Function for setting residue specific data values.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the values to.

        value:  The value(s).

        data_type:  The data type(s).

        res_num:  The residue number.

        res_name:  The residue name.


        Description
        ~~~~~~~~~~~

        If this function is used to change values of previously minimised runs, then the
        minimisation statistics (chi-squared value, iteration count, function count, gradient count,
        and Hessian count) will be reset to None.


        The value argument can be None, a single value, or an array of values while the data type
        argument can be None, a string, or array of strings.  The choice of which combination
        determines the behaviour of this function.  The following table describes what occurs in
        each instance.  The Value column refers to the 'value' argument while the Type column refers
        to the 'data_type' argument.  In these columns, 'None' corresponds to None, '1' corresponds
        to either a single value or single string, and 'n' corresponds to either an array of values
        or an array of strings.

        ____________________________________________________________________________________________
        |       |       |                                                                          |
        | Value | Type  | Description                                                              |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        | None  | None  | This case is used to set the model parameters prior to minimisation.     |
        |       |       | The model parameters are set to the default values.                      |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        |   1   | None  | Invalid combination.                                                     |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        |   n   | None  | This case is used to set the model parameters prior to minimisation.     |
        |       |       | The length of the value array must be equal to the number of model       |
        |       |       | parameters for an individual residue.  The parameters will be set to the |
        |       |       | corresponding number.                                                    |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        | None  |   1   | The data type matching the string will be set to the default value.      |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        |   1   |   1   | The data type matching the string will be set to the supplied number.    |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        |   n   |   1   | Invalid combination.                                                     |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        | None  |   n   | Each data type matching the strings will be set to the default values.   |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        |   1   |   n   | Each data type matching the strings will be set to the supplied number.  |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        |   n   |   n   | Each data type matching the strings will be set to the corresponding     |
        |       |       | number.  Both arrays must be of equal length.                            |
        |_______|_______|__________________________________________________________________________|


        Residue number and name argument.

        If the 'res_num' and 'res_name' arguments are left as the defaults of None, then the
        function will be applied to all residues.  Otherwise the residue number can be set to either
        an integer for selecting a single residue or a python regular expression string for
        selecting multiple residues.  The residue name argument must be a string and can use regular
        expression as well.


        Examples
        ~~~~~~~~

        To set the parameter values for the run 'test' to the default values, for all residues,
        type:

        relax> value.set('test')


        To set the parameter values of residue 10, which is the model-free run 'm4' and has the
        parameters {S2, te, Rex}, the following can be used.  Rex term is the value for the first
        given field strength.

        relax> value.set('m4', [0.97, 2.048*1e-9, 0.149], res_num=10)
        relax> value.set('m4', value=[0.97, 2.048*1e-9, 0.149], res_num=10)


        To set the CSA value for the model-free run 'tm3' to the default value, type:

        relax> value.set('tm3', data_type='csa')


        To set the CSA value of all residues in the model-free run 'm1' to -170 ppm, type:

        relax> value.set('m1', -170 * 1e-6, 'csa')
        relax> value.set('m1', value=-170 * 1e-6, data_type='csa')


        To set the NH bond length of all residues in the model-free run 'm5' to 1.02 Angstroms,
        type:

        relax> value.set('m5', 1.02 * 1e-10, 'bond_length')
        relax> value.set('m5', value=1.02 * 1e-10, data_type='r')


        To set both the bond length and the CSA value for the model-free run 'tm3' to the default
        values, type:

        relax> value.set('tm3', data_type=['bond length', 'csa'])


        To set both tf and ts in the model-free run 'm6' to 100 ps, type:

        relax> value.set('m6', 100e-12, ['tf', 'ts'])
        relax> value.set('m6', value=100e-12, data_type=['tf', 'ts'])


        To set the S2 and te parameter values for model-free run 'm4' which has the parameters
        {S2, te, Rex} to 0.56 and 13 ps, type:

        relax> value.set('m4', [0.56, 13e-12], ['S2', 'te'], 10)
        relax> value.set('m4', value=[0.56, 13e-12], data_type=['S2', 'te'], res_num=10)
        relax> value.set(run='m4', value=[0.56, 13e-12], data_type=['S2', 'te'], res_num=10)

        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.set("
            text = text + "run=" + `run`
            text = text + ", value=" + `value`
            text = text + ", data_type=" + `data_type`
            text = text + ", res_num=" + `res_num`
            text = text + ", res_name=" + `res_name` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Value.
        if value != None and type(value) != float and type(value) != int and type(value) != list:
            raise RelaxNoneFloatListError, ('value', value)
        if type(value) == list:
            for i in range(len(value)):
                if type(value[i]) != float and type(value[i]) != int:
                    raise RelaxListFloatError, ('value', value)

        # Data type.
        if data_type != None and type(data_type) != str and type(data_type) != list:
            raise RelaxNoneStrListError, ('data type', data_type)
        if type(data_type) == list:
            for i in range(len(data_type)):
                if type(data_type[i]) != str:
                    raise RelaxListStrError, ('data type', data_type)

        # The invalid combination of a single value and no data_type argument.
        if (type(value) == float or type(value) == int) and data_type == None:
            raise RelaxError, "Invalid value and data type argument combination, for details by type 'help(value.set)'"

        # The invalid combination of an array of values and a single data_type string.
        if type(value) == list and type(data_type) == str:
            raise RelaxError, "Invalid value and data type argument combination, for details by type 'help(value.set)'"

        # Value array and data type array of equal length.
        if type(value) == list and type(data_type) == list and len(value) != len(data_type):
            raise RelaxError, "Both the value array and data type array must be of equal length."

        # Residue number.
        if res_num != None and type(res_num) != int and type(res_num) != str:
            raise RelaxNoneIntStrError, ('residue number', res_num)

        # Residue name.
        if res_name != None and type(res_name) != str:
            raise RelaxNoneStrError, ('residue name', res_name)

        # Execute the functional code.
        self.__relax__.generic.value.set(run=run, value=value, data_type=data_type, res_num=res_num, res_name=res_name)


    def write(self, run=None, data_type=None, file=None, dir=None, force=0):
        """Function for writing residue specific data values to a file.

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
        The data type argument can only be a single string.


        Examples
        ~~~~~~~~

        To write the CSA values for the run 'm1' to the file 'csa.txt', type:

        relax> value.write('m1', 'CSA', 'csa.txt')
        relax> value.write(run='m1', data_type='CSA', file='csa.txt')

        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.write("
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
        self.__relax__.generic.value.write(run=run, data_type=data_type, file=file, dir=dir, force=force)


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

    # Display function.
    display.__doc__ = display.__doc__ + "\n\n" + __re_doc__ + "\n"
    display.__doc__ = display.__doc__ + Model_free.get_data_name.__doc__ + "\n"

    # Set function.
    set.__doc__ = set.__doc__ + "\n\n" + __re_doc__ + "\n"
    set.__doc__ = set.__doc__ + Model_free.get_data_name.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Model_free.set.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Model_free.default_value.__doc__ + "\n"

    # Write function.
    write.__doc__ = write.__doc__ + "\n\n" + __re_doc__ + "\n"
    write.__doc__ = write.__doc__ + Model_free.get_data_name.__doc__ + "\n"
