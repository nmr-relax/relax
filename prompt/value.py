###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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

from doc_string import regexp_doc
import help
from generic_fns.diffusion_tensor import Diffusion_tensor
from specific_fns.consistency_tests import Consistency_tests
from specific_fns.model_free import Model_free
from specific_fns.jw_mapping import Jw_mapping
from specific_fns.relax_fit import Relax_fit
from specific_fns.noe import Noe


class Value:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for setting data values."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def copy(self, run1=None, run2=None, param=None):
        """Function for copying residue specific data values from run1 to run2.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run1:  The name of the run to copy from.

        run2:  The name of the run to copy to.

        param:  The parameter to copy.


        Description
        ~~~~~~~~~~~

        Only one parameter may be selected, therefore the 'param' argument should be a string.

        If this function is used to change values of previously minimised runs, then the
        minimisation statistics (chi-squared value, iteration count, function count, gradient count,
        and Hessian count) will be reset to None.


        Examples
        ~~~~~~~~

        To copy the CSA values from the run 'm1' to 'm2', type:

        relax> value.copy('m1', 'm2', 'CSA')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.copy("
            text = text + "run1=" + `run1`
            text = text + ", run2=" + `run2`
            text = text + ", param=" + `param` + ")"
            print text

        # The run1 argument.
        if type(run1) != str:
            raise RelaxStrError, ('run1', run1)

        # The run2 argument.
        if type(run2) != str:
            raise RelaxStrError, ('run2', run2)

        # The parameter.
        if type(param) != str:
            raise RelaxStrError, ('parameter', param)

        # Execute the functional code.
        self.__relax__.generic.value.copy(run1=run1, run2=run2, param=param)


    def display(self, run=None, param=None):
        """Function for displaying residue specific data values.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        param:  The parameter to display.


        Description
        ~~~~~~~~~~~

        Only one parameter may be selected, therefore the 'param' argument should be a string.


        Examples
        ~~~~~~~~

        To show all CSA values for the run 'm1', type:

        relax> value.display('m1', 'CSA')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.display("
            text = text + "run=" + `run`
            text = text + ", param=" + `param` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The parameter.
        if type(param) != str:
            raise RelaxStrError, ('parameter', param)

        # Execute the functional code.
        self.__relax__.generic.value.display(run=run, param=param)


    def read(self, run=None, param=None, scaling=1.0, file=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
        """Function for reading residue specific data values from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        param:  The parameter.

        scaling:  The factor to scale parameters by.

        file:  The name of the file containing the relaxation data.

        num_col:  The residue number column (the default is 0, ie the first column).

        name_col:  The residue name column (the default is 1).

        data_col:  The relaxation data column (the default is 2).

        error_col:  The experimental error column (the default is 3).

        sep:  The column separator (the default is white space).


        Description
        ~~~~~~~~~~~

        Only one parameter may be selected, therefore the 'param' argument should be a string.  If
        the file only contains values and no errors, set the error column argument to None.

        If this function is used to change values of previously minimised runs, then the
        minimisation statistics (chi-squared value, iteration count, function count, gradient count,
        and Hessian count) will be reset to None.


        Examples
        ~~~~~~~~

        To load CSA values for the run 'm1' from the file 'csa_values' in the directory 'data', type
        any of the following:

        relax> value.read('m1', 'CSA', 'data/csa_value')
        relax> value.read('m1', 'CSA', 'data/csa_value', 0, 1, 2, 3, None, 1)
        relax> value.read(run='m1', param='CSA', file='data/csa_value', num_col=0, name_col=1,
                          data_col=2, error_col=3, sep=None)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.read("
            text = text + "run=" + `run`
            text = text + ", param=" + `param`
            text = text + ", scaling=" + `scaling`
            text = text + ", file=" + `file`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", data_col=" + `data_col`
            text = text + ", error_col=" + `error_col`
            text = text + ", sep=" + `sep` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The parameter.
        if type(param) != str:
            raise RelaxStrError, ('parameter', param)

        # The scaling factor.
        if type(scaling) != float:
            raise RelaxFloatError, ('scaling', scaling)

        # The file name.
        if type(file) != str:
            raise RelaxStrError, ('file', file)

        # The number column.
        if type(num_col) != int:
            raise RelaxIntError, ('residue number column', num_col)

        # The name column.
        if name_col != None and type(name_col) != int:
            raise RelaxNoneIntError, ('residue name column', name_col)

        # The data column.
        if type(data_col) != int:
            raise RelaxIntError, ('data column', data_col)

        # The error column.
        if error_col != None and type(error_col) != int:
            raise RelaxNoneIntError, ('error column', error_col)

        # Column separator.
        if sep != None and type(sep) != str:
            raise RelaxNoneStrError, ('column separator', sep)

        # Execute the functional code.
        self.__relax__.generic.value.read(run=run, param=param, scaling=scaling, file=file, num_col=num_col, name_col=name_col, data_col=data_col, error_col=error_col, sep=sep)


    def set(self, run=None, value=None, param=None, res_num=None, res_name=None):
        """Function for setting residue specific data values.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the values to.

        value:  The value(s).

        param:  The parameter(s).

        res_num:  The residue number.

        res_name:  The residue name.


        Description
        ~~~~~~~~~~~

        If this function is used to change values of previously minimised runs, then the
        minimisation statistics (chi-squared value, iteration count, function count, gradient count,
        and Hessian count) will be reset to None.


        The value argument can be None, a single value, or an array of values while the parameter
        argument can be None, a string, or array of strings.  The choice of which combination
        determines the behaviour of this function.  The following table describes what occurs in
        each instance.  The Value column refers to the 'value' argument while the Param column refers
        to the 'param' argument.  In these columns, 'None' corresponds to None, '1' corresponds
        to either a single value or single string, and 'n' corresponds to either an array of values
        or an array of strings.

        ____________________________________________________________________________________________
        |       |       |                                                                          |
        | Value | Param | Description                                                              |
        |_______|_______|__________________________________________________________________________|
        |       |       |                                                                          |
        | None  | None  | This case is used to set the model parameters prior to minimisation or   |
        |       |       | calculation.  The model parameters are set to the default values.        |
        |       |       |                                                                          |
        |   1   | None  | Invalid combination.                                                     |
        |       |       |                                                                          |
        |   n   | None  | This case is used to set the model parameters prior to minimisation or   |
        |       |       | calculation.  The length of the value array must be equal to the number  |
        |       |       | of model parameters for an individual residue.  The parameters will be   |
        |       |       | set to the corresponding number.                                         |
        |       |       |                                                                          |
        | None  |   1   | The parameter matching the string will be set to the default value.      |
        |       |       |                                                                          |
        |   1   |   1   | The parameter matching the string will be set to the supplied number.    |
        |       |       |                                                                          |
        |   n   |   1   | Invalid combination.                                                     |
        |       |       |                                                                          |
        | None  |   n   | Each parameter matching the strings will be set to the default values.   |
        |       |       |                                                                          |
        |   1   |   n   | Each parameter matching the strings will be set to the supplied number.  |
        |       |       |                                                                          |
        |   n   |   n   | Each parameter matching the strings will be set to the corresponding     |
        |       |       | number.  Both arrays must be of equal length.                            |
        |_______|_______|__________________________________________________________________________|


        Residue number and name argument
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        If the 'res_num' and 'res_name' arguments are left as the defaults of None, then the
        function will be applied to all residues.  Otherwise the residue number can be set to either
        an integer for selecting a single residue or a python regular expression string for
        selecting multiple residues.  The residue name argument must be a string and can use regular
        expression as well.  If the data is global non-residue specific data, such as diffusion
        tensor parameters, supplying the residue number and name will terminate the program with an
        error.


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

        relax> value.set('tm3', param='csa')


        To set the CSA value of all residues in the reduced spectral density mapping run '600MHz' to
        -172 ppm, type:

        relax> value.set('600MHz', -172 * 1e-6, 'csa')
        relax> value.set('600MHz', value=-172 * 1e-6, param='csa')


        To set the NH bond length of all residues in the model-free run 'm5' to 1.02 Angstroms,
        type:

        relax> value.set('m5', 1.02 * 1e-10, 'bond_length')
        relax> value.set('m5', value=1.02 * 1e-10, param='r')


        To set both the bond length and the CSA value for the run 'new' to the default values, type:

        relax> value.set('new', param=['bond length', 'csa'])


        To set both tf and ts in the model-free run 'm6' to 100 ps, type:

        relax> value.set('m6', 100e-12, ['tf', 'ts'])
        relax> value.set('m6', value=100e-12, param=['tf', 'ts'])


        To set the S2 and te parameter values for model-free run 'm4' which has the parameters
        {S2, te, Rex} to 0.56 and 13 ps, type:

        relax> value.set('m4', [0.56, 13e-12], ['S2', 'te'], 10)
        relax> value.set('m4', value=[0.56, 13e-12], param=['S2', 'te'], res_num=10)
        relax> value.set(run='m4', value=[0.56, 13e-12], param=['S2', 'te'], res_num=10)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.set("
            text = text + "run=" + `run`
            text = text + ", value=" + `value`
            text = text + ", param=" + `param`
            text = text + ", res_num=" + `res_num`
            text = text + ", res_name=" + `res_name` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The value.
        if value != None and type(value) != float and type(value) != int and type(value) != list:
            raise RelaxNoneFloatListError, ('value', value)
        if type(value) == list:
            for i in xrange(len(value)):
                if type(value[i]) != float and type(value[i]) != int:
                    raise RelaxListFloatError, ('value', value)

        # The parameter.
        if param != None and type(param) != str and type(param) != list:
            raise RelaxNoneStrListError, ('parameter', param)
        if type(param) == list:
            for i in xrange(len(param)):
                if type(param[i]) != str:
                    raise RelaxListStrError, ('parameter', param)

        # The invalid combination of a single value and no param argument.
        if (type(value) == float or type(value) == int) and param == None:
            raise RelaxError, "Invalid value and parameter argument combination, for details by type 'help(value.set)'"

        # The invalid combination of an array of values and a single param string.
        if type(value) == list and type(param) == str:
            raise RelaxError, "Invalid value and parameter argument combination, for details by type 'help(value.set)'"

        # Value array and parameter array of equal length.
        if type(value) == list and type(param) == list and len(value) != len(param):
            raise RelaxError, "Both the value array and parameter array must be of equal length."

        # Residue number.
        if res_num != None and type(res_num) != int and type(res_num) != str:
            raise RelaxNoneIntStrError, ('residue number', res_num)

        # Residue name.
        if res_name != None and type(res_name) != str:
            raise RelaxNoneStrError, ('residue name', res_name)

        # Execute the functional code.
        self.__relax__.generic.value.set(run=run, value=value, param=param, res_num=res_num, res_name=res_name)


    def write(self, run=None, param=None, file=None, dir=None, force=0):
        """Function for writing residue specific data values to a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        param:  The parameter.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which, if set to 1, will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the file will be placed in the current working directory.

        The parameter argument should be a string.


        Examples
        ~~~~~~~~

        To write the CSA values for the run 'm1' to the file 'csa.txt', type:

        relax> value.write('m1', 'CSA', 'csa.txt')
        relax> value.write(run='m1', param='CSA', file='csa.txt')


        To write the NOE values from the run 'noe' to the file 'noe', type:

        relax> value.write('noe', 'noe', 'noe.out')
        relax> value.write('noe', param='noe', file='noe.out')
        relax> value.write(run='noe', param='noe', file='noe.out')
        relax> value.write(run='noe', param='noe', file='noe.out', force=1)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.write("
            text = text + "run=" + `run`
            text = text + ", param=" + `param`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The parameter.
        if type(param) != str:
            raise RelaxStrError, ('parameter', param)

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
        self.__relax__.generic.value.write(run=run, param=param, file=file, dir=dir, force=force)


    # Docstring modification.
    #########################

    # Copy function.
    copy.__doc__ = copy.__doc__ + "\n\n" + regexp_doc() + "\n"
    copy.__doc__ = copy.__doc__ + Consistency_tests.set.__doc__ + "\n"
    copy.__doc__ = copy.__doc__ + Consistency_tests.return_data_name.__doc__ + "\n"
    copy.__doc__ = copy.__doc__ + Model_free.set_doc.__doc__ + "\n\n"
    copy.__doc__ = copy.__doc__ + Model_free.return_data_name.__doc__ + "\n"
    copy.__doc__ = copy.__doc__ + Jw_mapping.set.__doc__ + "\n"
    copy.__doc__ = copy.__doc__ + Jw_mapping.return_data_name.__doc__ + "\n"
    copy.__doc__ = copy.__doc__ + Relax_fit.set_doc.__doc__ + "\n"
    copy.__doc__ = copy.__doc__ + Relax_fit.return_data_name.__doc__ + "\n"

    # Display function.
    display.__doc__ = display.__doc__ + "\n\n" + regexp_doc() + "\n"
    display.__doc__ = display.__doc__ + Consistency_tests.return_data_name.__doc__ + "\n"
    display.__doc__ = display.__doc__ + Model_free.return_data_name.__doc__ + "\n\n"
    display.__doc__ = display.__doc__ + Jw_mapping.return_data_name.__doc__ + "\n"
    display.__doc__ = display.__doc__ + Relax_fit.return_data_name.__doc__ + "\n"

    # Read function.
    read.__doc__ = read.__doc__ + "\n\n" + regexp_doc() + "\n"
    read.__doc__ = read.__doc__ + Consistency_tests.set.__doc__ + "\n"
    read.__doc__ = read.__doc__ + Consistency_tests.return_data_name.__doc__ + "\n"
    read.__doc__ = read.__doc__ + Model_free.set_doc.__doc__ + "\n\n"
    read.__doc__ = read.__doc__ + Model_free.return_data_name.__doc__ + "\n"
    read.__doc__ = read.__doc__ + Jw_mapping.set.__doc__ + "\n"
    read.__doc__ = read.__doc__ + Jw_mapping.return_data_name.__doc__ + "\n"
    read.__doc__ = read.__doc__ + Relax_fit.set_doc.__doc__ + "\n"
    read.__doc__ = read.__doc__ + Relax_fit.return_data_name.__doc__ + "\n"

    # Set function.
    set.__doc__ = set.__doc__ + "\n\n" + regexp_doc() + "\n"
    set.__doc__ = set.__doc__ + Consistency_tests.set.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Consistency_tests.return_data_name.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Consistency_tests.default_value.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Model_free.set_doc.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Model_free.return_data_name.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Model_free.default_value.__doc__ + "\n\n"
    set.__doc__ = set.__doc__ + Jw_mapping.set.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Jw_mapping.return_data_name.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Jw_mapping.default_value.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Diffusion_tensor.set.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Diffusion_tensor.return_data_name.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Diffusion_tensor.default_value.__doc__ + "\n\n"
    set.__doc__ = set.__doc__ + Relax_fit.set_doc.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Relax_fit.return_data_name.__doc__ + "\n"
    set.__doc__ = set.__doc__ + Relax_fit.default_value.__doc__ + "\n\n"

    # Write function.
    write.__doc__ = write.__doc__ + "\n\n" + regexp_doc() + "\n"
    write.__doc__ = write.__doc__ + Consistency_tests.return_data_name.__doc__ + "\n\n"
    write.__doc__ = write.__doc__ + Model_free.return_data_name.__doc__ + "\n\n"
    write.__doc__ = write.__doc__ + Jw_mapping.return_data_name.__doc__ + "\n\n"
    write.__doc__ = write.__doc__ + Noe.return_data_name.__doc__ + "\n"
    write.__doc__ = write.__doc__ + Relax_fit.return_data_name.__doc__ + "\n"
