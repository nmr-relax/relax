###############################################################################
#                                                                             #
# Copyright (C) 2003-2009 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module containing the 'value' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
from doc_string import docs
import help
from generic_fns import diffusion_tensor
from generic_fns import value
from num_types import int_list, float_list
from relax_errors import RelaxError, RelaxFloatError, RelaxIntError, RelaxListFloatStrError, RelaxListStrError, RelaxNoneFloatStrListError, RelaxNoneIntError, RelaxNoneStrError, RelaxNoneStrListError, RelaxStrError
from specific_fns.jw_mapping import Jw_mapping
from specific_fns.model_free import Model_free
from specific_fns.relax_fit import Relax_fit
from specific_fns.n_state_model import N_state_model
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


    def copy(self, pipe_from=None, pipe_to=None, param=None):
        """Copy spin specific data values from one data pipe to another.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The name of the pipe to copy from.

        pipe_to:  The name of the pipe to copy to.

        param:  The parameter to copy.


        Description
        ~~~~~~~~~~~

        Only one parameter may be selected, therefore the 'param' argument should be a string.

        If this function is used to change values of previously minimised parameters, then the
        minimisation statistics (chi-squared value, iteration count, function count, gradient count,
        and Hessian count) will be reset.


        Examples
        ~~~~~~~~

        To copy the CSA values from the data pipe 'm1' to 'm2', type:

        relax> value.copy('m1', 'm2', 'CSA')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.copy("
            text = text + "pipe_from=" + `pipe_from`
            text = text + ", pipe_to=" + `pipe_to`
            text = text + ", param=" + `param` + ")"
            print text

        # The pipe_from argument.
        if type(pipe_from) != str:
            raise RelaxStrError, ('pipe_from', pipe_from)

        # The pipe_to argument.
        if type(pipe_to) != str:
            raise RelaxStrError, ('pipe_to', pipe_to)

        # The parameter.
        if type(param) != str:
            raise RelaxStrError, ('parameter', param)

        # Execute the functional code.
        self.__relax__.generic.value.copy(pipe_from=pipe_from, pipe_to=pipe_to, param=param)


    def display(self, param=None):
        """Display spin specific data values.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        param:  The parameter to display.


        Description
        ~~~~~~~~~~~

        Only one parameter may be selected, therefore the 'param' argument should be a string.


        Examples
        ~~~~~~~~

        To show all CSA values, type:

        relax> value.display('CSA')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.display("
            text = text + "param=" + `param` + ")"
            print text

        # The parameter.
        if type(param) != str:
            raise RelaxStrError, ('parameter', param)

        # Execute the functional code.
        self.__relax__.generic.value.display(param=param)


    def read(self, param=None, scaling=1.0, file=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
        """Read spin specific data values from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

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

        If this function is used to change values of previously minimised parameters, then the
        minimisation statistics (chi-squared value, iteration count, function count, gradient count,
        and Hessian count) will be reset to None.


        Examples
        ~~~~~~~~

        To load CSA values from the file 'csa_values' in the directory 'data', type one of the
        following:

        relax> value.read('CSA', 'data/csa_value')
        relax> value.read('CSA', 'data/csa_value', 0, 1, 2, 3, None, 1)
        relax> value.read(param='CSA', file='data/csa_value', num_col=0, name_col=1,
                          data_col=2, error_col=3, sep=None)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.read("
            text = text + "param=" + `param`
            text = text + ", scaling=" + `scaling`
            text = text + ", file=" + `file`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", data_col=" + `data_col`
            text = text + ", error_col=" + `error_col`
            text = text + ", sep=" + `sep` + ")"
            print text

        # The parameter.
        if type(param) != str:
            raise RelaxStrError, ('parameter', param)

        # The scaling factor.
        if type(scaling) not in float_list:
            raise RelaxFloatError, ('scaling', scaling)

        # The file name.
        if type(file) != str:
            raise RelaxStrError, ('file', file)

        # The number column.
        if type(num_col) not in int_list:
            raise RelaxIntError, ('residue number column', num_col)

        # The name column.
        if name_col != None and type(name_col) not in int_list:
            raise RelaxNoneIntError, ('residue name column', name_col)

        # The data column.
        if type(data_col) not in int_list:
            raise RelaxIntError, ('data column', data_col)

        # The error column.
        if error_col != None and type(error_col) not in int_list:
            raise RelaxNoneIntError, ('error column', error_col)

        # Column separator.
        if sep != None and type(sep) != str:
            raise RelaxNoneStrError, ('column separator', sep)

        # Execute the functional code.
        self.__relax__.generic.value.read(param=param, scaling=scaling, file=file, num_col=num_col, name_col=name_col, data_col=data_col, error_col=error_col, sep=sep)


    def set(self, val=None, param=None, spin_id=None):
        """Set spin specific data values.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        val:  The value(s).

        param:  The parameter(s).

        spin_id:  The spin identifier.


        Description
        ~~~~~~~~~~~

        If this function is used to change values of previously minimised results, then the
        minimisation statistics (chi-squared value, iteration count, function count, gradient count,
        and Hessian count) will be reset to None.


        The val argument can be None, a single value, or an array of values while the parameter
        argument can be None, a string, or array of strings.  The choice of which combination
        determines the behaviour of this function.  The following table describes what occurs in
        each instance.  The Value column refers to the 'val' argument while the Param column refers
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
        |       |       | calculation.  The length of the val array must be equal to the number    |
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


        Spin identification
        ~~~~~~~~~~~~~~~~~~~

        If the 'spin_id' argument is left as the default of None, then the function will be applied
        to all spins.  If the data is global non-residue specific data, such as diffusion tensor
        parameters, supplying the spin identifier will terminate the program with an error.


        Examples
        ~~~~~~~~

        To set the parameter values for the current data pipe to the default values, for all spins,
        type:

        relax> value.set()


        To set the parameter values of residue 10, which is in the current model-free data pipe 'm4'
        and has the parameters {S2, te, Rex}, the following can be used.  Rex term is the value for
        the first given field strength.

        relax> value.set([0.97, 2.048*1e-9, 0.149], spin_id=':10')
        relax> value.set(val=[0.97, 2.048*1e-9, 0.149], spin_id=':10')


        To set the CSA value of all spins to the default value, type:

        relax> value.set(param='csa')


        To set the CSA value of all spins to -172 ppm, type:

        relax> value.set(-172 * 1e-6, 'csa')
        relax> value.set(val=-172 * 1e-6, param='csa')


        To set the NH bond length of all spins to 1.02 Angstroms, type:

        relax> value.set(1.02 * 1e-10, 'bond_length')
        relax> value.set(val=1.02 * 1e-10, param='r')


        To set both the bond length and the CSA value to the default values, type:

        relax> value.set(param=['bond length', 'csa'])


        To set both tf and ts to 100 ps, type:

        relax> value.set(100e-12, ['tf', 'ts'])
        relax> value.set(val=100e-12, param=['tf', 'ts'])


        To set the S2 and te parameter values of residue 126, Ca spins to 0.56 and 13 ps, type:

        relax> value.set([0.56, 13e-12], ['S2', 'te'], ':126@Ca')
        relax> value.set(val=[0.56, 13e-12], param=['S2', 'te'], spin_id=':126@Ca')
        relax> value.set(val=[0.56, 13e-12], param=['S2', 'te'], spin_id=':126@Ca')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.set("
            text = text + "val=" + `val`
            text = text + ", param=" + `param`
            text = text + ", spin_id=" + `spin_id` + ")"
            print text

        # The value.
        if val != None and type(val) not in float_list and type(val) not in int_list and type(val) != str and type(val) != list:
            raise RelaxNoneFloatStrListError, ('value', val)
        if type(val) == list:
            # Empty list.
            if val == []:
                raise RelaxListFloatStrError, ('value', val)

            # Check for values.
            for i in xrange(len(val)):
                if type(val[i]) not in float_list and type(val[i]) not in int_list:
                    print type(val[i])
                    raise RelaxListFloatStrError, ('value', val)

        # The parameter.
        if param != None and type(param) != str and type(param) != list:
            raise RelaxNoneStrListError, ('parameter', param)
        if type(param) == list:
            # Empty list.
            if param == []:
                raise RelaxListStrError, ('parameter', param)

            # Check for strings.
            for i in xrange(len(param)):
                if type(param[i]) != str:
                    raise RelaxListStrError, ('parameter', param)

        # The invalid combination of a single value and no param argument.
        if (type(val) == float or type(val) == int) and param == None:
            raise RelaxError, "Invalid value and parameter argument combination, for details by type 'help(value.set)'"

        # The invalid combination of an array of values and a single param string.
        if type(val) == list and type(param) == str:
            raise RelaxError, "Invalid value and parameter argument combination, for details by type 'help(value.set)'"

        # Value array and parameter array of equal length.
        if type(val) == list and type(param) == list and len(val) != len(param):
            raise RelaxError, "Both the value array and parameter array must be of equal length."

        # Spin identifier.
        if spin_id != None and type(spin_id) != str:
            raise RelaxNoneStrError, ('spin identifier', spin_id)

        # Execute the functional code.
        value.set(val=val, param=param, spin_id=spin_id)


    def write(self, param=None, file=None, dir=None, force=False):
        """Write spin specific data values to a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        param:  The parameter.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which, if set to True, will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the file will be placed in the current working directory.

        The parameter argument should be a string.


        Examples
        ~~~~~~~~

        To write the CSA values to the file 'csa.txt', type one of:

        relax> value.write('CSA', 'csa.txt')
        relax> value.write(param='CSA', file='csa.txt')


        To write the NOE values to the file 'noe', type one of:

        relax> value.write('noe', 'noe.out')
        relax> value.write(param='noe', file='noe.out')
        relax> value.write(param='noe', file='noe.out')
        relax> value.write(param='noe', file='noe.out', force=True)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "value.write("
            text = text + "param=" + `param`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

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
        if type(force) != bool:
            raise RelaxBoolError, ('force flag', force)

        # Execute the functional code.
        value.write(param=param, file=file, dir=dir, force=force)


    # Docstring modification.
    #########################

    # Copy function.
    copy.__doc__ = copy.__doc__ + "\n\n" + docs.regexp.doc + "\n"
    copy.__doc__ = copy.__doc__ + Model_free.set_doc + "\n\n"
    copy.__doc__ = copy.__doc__ + Model_free.return_data_name_doc + "\n"
    copy.__doc__ = copy.__doc__ + Jw_mapping.set_doc + "\n"
    copy.__doc__ = copy.__doc__ + Jw_mapping.return_data_name_doc + "\n"
    copy.__doc__ = copy.__doc__ + Relax_fit.set_doc + "\n"
    copy.__doc__ = copy.__doc__ + Relax_fit.return_data_name_doc + "\n"
    copy.__doc__ = copy.__doc__ + N_state_model.set_doc + "\n"
    copy.__doc__ = copy.__doc__ + N_state_model.return_data_name_doc + "\n"

    # Display function.
    display.__doc__ = display.__doc__ + "\n\n" + docs.regexp.doc + "\n"
    display.__doc__ = display.__doc__ + Model_free.return_data_name_doc + "\n\n"
    display.__doc__ = display.__doc__ + Jw_mapping.return_data_name_doc + "\n"
    display.__doc__ = display.__doc__ + Relax_fit.return_data_name_doc + "\n"
    display.__doc__ = display.__doc__ + N_state_model.return_data_name_doc + "\n"

    # Read function.
    read.__doc__ = read.__doc__ + "\n\n" + docs.regexp.doc + "\n"
    read.__doc__ = read.__doc__ + Model_free.set_doc + "\n\n"
    read.__doc__ = read.__doc__ + Model_free.return_data_name_doc + "\n"
    read.__doc__ = read.__doc__ + Jw_mapping.set_doc + "\n"
    read.__doc__ = read.__doc__ + Jw_mapping.return_data_name_doc + "\n"
    read.__doc__ = read.__doc__ + Relax_fit.set_doc + "\n"
    read.__doc__ = read.__doc__ + Relax_fit.return_data_name_doc + "\n"
    read.__doc__ = read.__doc__ + N_state_model.set_doc + "\n"
    read.__doc__ = read.__doc__ + N_state_model.return_data_name_doc + "\n"

    # Set function.
    set.__doc__ = set.__doc__ + "\n\n" + docs.regexp.doc + "\n"
    set.__doc__ = set.__doc__ + Model_free.set_doc + "\n"
    set.__doc__ = set.__doc__ + Model_free.return_data_name_doc + "\n"
    set.__doc__ = set.__doc__ + Model_free.default_value_doc + "\n\n"
    set.__doc__ = set.__doc__ + Jw_mapping.set_doc + "\n"
    set.__doc__ = set.__doc__ + Jw_mapping.return_data_name_doc + "\n"
    set.__doc__ = set.__doc__ + Jw_mapping.default_value_doc + "\n"
    set.__doc__ = set.__doc__ + diffusion_tensor.__set_prompt_doc__ + "\n"
    set.__doc__ = set.__doc__ + diffusion_tensor.__return_data_name_prompt_doc__ + "\n"
    set.__doc__ = set.__doc__ + diffusion_tensor.__default_value_prompt_doc__ + "\n\n"
    set.__doc__ = set.__doc__ + Relax_fit.set_doc + "\n"
    set.__doc__ = set.__doc__ + Relax_fit.return_data_name_doc + "\n"
    set.__doc__ = set.__doc__ + Relax_fit.default_value_doc + "\n\n"
    set.__doc__ = set.__doc__ + N_state_model.set_doc + "\n"
    set.__doc__ = set.__doc__ + N_state_model.return_data_name_doc + "\n"
    set.__doc__ = set.__doc__ + N_state_model.default_value_doc + "\n\n"

    # Write function.
    write.__doc__ = write.__doc__ + "\n\n" + docs.regexp.doc + "\n"
    write.__doc__ = write.__doc__ + Model_free.return_data_name_doc + "\n\n"
    write.__doc__ = write.__doc__ + Jw_mapping.return_data_name_doc + "\n\n"
    write.__doc__ = write.__doc__ + Noe.return_data_name_doc + "\n"
    write.__doc__ = write.__doc__ + Relax_fit.return_data_name_doc + "\n"
    write.__doc__ = write.__doc__ + N_state_model.return_data_name_doc + "\n"
