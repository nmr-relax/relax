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
        """Class containing functions for the setting up of data structures."""

        # Place relax in the class namespace.
        self.relax = relax

        # Help.
        self.__relax_help__ = help.relax_class_help


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


        The value argument can be a single value, an array of values, or None while the data type
        argument can be a string, array of strings, or None.  The choice of which combination
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
        |       |       | The model parameters are set to the hard wired values.                   |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        |   1   | None  | Invalid combination.                                                     |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        |   n   | None  | This case is used to set the model parameters prior to minimisation.     |
        |       |       | The length of the value array must be equal to the number of model       |
        |       |       | parameters for an individual residue.  The parameters will be set to the |
        |       |       | values of the array.                                                     |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        | None  |   1   | The data type matching the string will be set to the hard wired value.   |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        |   1   |   1   | The data type matching the string will be set to the supplied number.    |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        |   n   |   1   | Invalid combination.                                                     |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        | None  |   n   | Each data type matching the strings will be set to the hard wired        |
        |       |       | values.                                                                  |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        |   1   |   n   | Each data type matching the strings will be set to the supplied number.  |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        |   n   |   n   | Each data type matching the strings will be set to the corresponding     |
        |       |       | number.  Both arrays must be of equal length.                            |
        |_______|_______|__________________________________________________________________________|


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


        Residue number and name argument.

        If the 'res_num' and 'res_name' arguments are left as the defaults of None, then values will
        apply to all residues.  Otherwise the residue number can be set to either an integer for
        selecting a single residue or a python regular expression string for selecting multiple
        residues.  The residue name argument must be a string and can use regular expression as
        well.


        Examples
        ~~~~~~~~

        To set the CSA value of all residues in the model-free run 'm1' to -170 ppm, type:

        relax> value.set('m1', -170 * 1e-6, 'csa')
        relax> value.set('m1', value=-170 * 1e-6, data_type='csa')


        To set the NH bond length of all residues in the model-free run 'm5' to 1.02 Angstroms,
        type:

        relax> value.set('m5', 1.02 * 1e-10, 'bond_length')
        relax> value.set('m5', value=1.02 * 1e-10, data_type='r')


        To set the parameter values of residue 10, which is the model-free run 'm4' and has the
        parameters {S2, te, Rex}, the following can be used.  Note that the Rex term should be the
        chemical exchange value for the first given field strength.

        relax> value.set('m4', [0.97, 2.048*1e-9, 0.149], res_num=10)
        relax> value.set('m4', value=[0.97, 2.048*1e-9, 0.149], res_num=10)


        To set the S2 and te parameter values for model-free run 'm4' which has the parameters
        {S2, te, Rex} to 0.56 and 13e-12, type:

        relax> value.set('m4', [0.56, 13e-12], ['S2', 'te'], 10)
        relax> value.set('m4', value=[0.56, 13e-12], data_type=['S2', 'te'], res_num=10)


        To set the parameter values for the run 'test' to the hard wired values, for all residues,
        type:

        relax> value.set('test')
        """

        # Function intro text.
        if self.relax.interpreter.intro:
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
        if value != None and type(value) != list and type(value) != float and type(value) != int:
            raise RelaxNoneFloatListError, ('value', value)
        if type(value) == list:
            for i in len(value):
                if type(value[i]) != float and type(value[i]) != int:
                    raise RelaxListFloatError, ('value', value)

        # Data type.
        if data_type != None and type(data_type) != str and type(data_type) != list:
            raise RelaxNoneStrListError, ('data type', data_type)
        if type(data_type) == list:
            for i in len(data_type):
                if type(data_type) != str:
                    raise RelaxListStrError, ('data type', data_type)

        # If the value argument is a single value, make sure the data_type argument is set.
        if (type(value) == float or type(value) == int) and data_type == None:
            raise RelaxError, "When the value is a single number, the data_type argument must be supplied."

        # If the value argument is an array, make sure data_type is None or an array of strings.
        if type(value) == list and data_type != None and type(data_type) != list:
            raise RelaxError, "When the value argument is an array, the data_type argument must either be None or an array of strings."

        # If the data_type argument is a single string, make sure the value argument is a single value or None.
        if type(data_type) == str and value != None and type(value) != float and type(value) != str:
            raise RelaxError, "When the data type argument is a single string, the value argument must either be None or a single value."

        # It the data_type argument is None, make sure the value argument is an array of numbers or None.
        if data_type == None and value != None and type(value) != list:
            raise RelaxError, "When the data type argument is None, the value argument must either be None or an array of numbers."

        # Residue number.
        if res_num != None and type(res_num) != int and type(res_num) != str:
            raise RelaxNoneIntStrError, ('residue number', res_num)

        # Residue name.
        if res_name != None and type(res_name) != str:
            raise RelaxNoneStrError, ('residue name', res_name)

        # Execute the functional code.
        self.relax.generic.value.set(run=run, value=value, data_type=data_type, res_num=res_num, res_name=res_name)


    # Modify the docstring of the set method to include the docstring of the model-free specific function get_data_name.
    ####################################################################################################################

    set.__doc__ = set.__doc__ + "\n\n" + Model_free.get_data_name.__doc__ + "\n"
