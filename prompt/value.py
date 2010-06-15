###############################################################################
#                                                                             #
# Copyright (C) 2003-2010 Edward d'Auvergne                                   #
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

# relax module imports.
from doc_string import docs
from base_class import User_fn_class
import arg_check
from generic_fns import diffusion_tensor
from generic_fns import value
from relax_errors import RelaxError
from specific_fns.jw_mapping import Jw_mapping
from specific_fns.model_free import Model_free
from specific_fns.relax_fit import Relax_fit
from specific_fns.n_state_model import N_state_model
from specific_fns.noe import Noe


class Value(User_fn_class):
    """Class for setting data values."""

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
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "value.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", pipe_to=" + repr(pipe_to)
            text = text + ", param=" + repr(param) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(pipe_from, 'pipe from')
        arg_check.is_str(pipe_to, 'pipe to')
        arg_check.is_str(param, 'parameter')

        # Execute the functional code.
        value.copy(pipe_from=pipe_from, pipe_to=pipe_to, param=param)


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
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "value.display("
            text = text + "param=" + repr(param) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(param, 'parameter')

        # Execute the functional code.
        value.display(param=param)


    def read(self, param=None, scaling=1.0, file=None, dir=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None, spin_id=None):
        """Read spin specific data values from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        param:  The parameter.

        scaling:  The factor to scale parameters by.

        file:  The name of the file containing the values.

        dir:  The directory where the file is located.

        spin_id_col:  The spin ID string column (an alternative to the mol, res, and spin name and
            number columns).

        mol_name_col:  The molecule name column (alternative to the spin_id_col).

        res_num_col:  The residue number column (alternative to the spin_id_col).

        res_name_col:  The residue name column (alternative to the spin_id_col).

        spin_num_col:  The spin number column (alternative to the spin_id_col).

        spin_name_col:  The spin name column (alternative to the spin_id_col).

        data_col:  The RDC data column.

        error_col:  The experimental error column.

        sep:  The column separator (the default is white space).

        spin_id:  The spin ID string to restrict the loading of data to certain spin subsets.


        Description
        ~~~~~~~~~~~

        The spin system can be identified in the file using two different formats.  The first is the
        spin ID string column which can include the molecule name, the residue name and number, and
        the spin name and number.  Alternatively the mol_name_col, res_num_col, res_name_col,
        spin_num_col, and/or spin_name_col arguments can be supplied allowing this information to be
        in separate columns.  Note that the numbering of columns starts at one.  The spin_id
        argument can be used to restrict the reading to certain spin types, for example only 15N
        spins when only residue information is in the file.

        Only one parameter may be selected, therefore the 'param' argument should be a string.

        If this function is used to change values of previously minimised parameters, then the
        minimisation statistics (chi-squared value, iteration count, function count, gradient count,
        and Hessian count) will be reset.


        Examples
        ~~~~~~~~

        To load 15N CSA values from the file 'csa_values' in the directory 'data', where spins are
        only identified by residue name and number, type one of the following:

        relax> value.read('CSA', 'data/csa_value', spin_id='@N')
        relax> value.read('CSA', 'csa_value', dir='data', spin_id='@N')
        relax> value.read(param='CSA', file='csa_value', dir='data', res_num_col=1, res_name_col=2,
                          data_col=3, error_col=4, spin_id='@N')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "value.read("
            text = text + "param=" + repr(param)
            text = text + ", scaling=" + repr(scaling)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", spin_id_col=" + repr(spin_id_col)
            text = text + ", mol_name_col=" + repr(mol_name_col)
            text = text + ", res_num_col=" + repr(res_num_col)
            text = text + ", res_name_col=" + repr(res_name_col)
            text = text + ", spin_num_col=" + repr(spin_num_col)
            text = text + ", spin_name_col=" + repr(spin_name_col)
            text = text + ", data_col=" + repr(data_col)
            text = text + ", error_col=" + repr(error_col)
            text = text + ", sep=" + repr(sep)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(param, 'parameter')
        arg_check.is_float(scaling, 'scaling')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_int(spin_id_col, 'spin ID string column', can_be_none=True)
        arg_check.is_int(mol_name_col, 'molecule name column', can_be_none=True)
        arg_check.is_int(res_num_col, 'residue number column', can_be_none=True)
        arg_check.is_int(res_name_col, 'residue name column', can_be_none=True)
        arg_check.is_int(spin_num_col, 'spin number column', can_be_none=True)
        arg_check.is_int(spin_name_col, 'spin name column', can_be_none=True)
        arg_check.is_int(data_col, 'data column', can_be_none=True)
        arg_check.is_int(error_col, 'error column', can_be_none=True)
        arg_check.is_str(sep, 'column separator', can_be_none=True)
        arg_check.is_str(spin_id, 'spin ID string', can_be_none=True)

        # Execute the functional code.
        value.read(param=param, scaling=scaling, file=file, dir=dir, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep, spin_id=spin_id)


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
        |       |       | of model parameters.  The parameters will be set to the corresponding    |
        |       |       | number.                                                                  |
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
        to all spins.  If the data is global non-spin specific data, such as diffusion tensor
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
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "value.set("
            text = text + "val=" + repr(val)
            text = text + ", param=" + repr(param)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str_or_num_or_str_num_list(val, 'value', can_be_none=True)
        arg_check.is_str_or_str_list(param, 'parameter', can_be_none=True)
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)

        # The invalid combination of a single value and no param argument.
        if (isinstance(val, float) or isinstance(val, int)) and param == None:
            raise RelaxError("Invalid value and parameter argument combination, for details by type 'help(value.set)'")

        # The invalid combination of an array of values and a single param string.
        if isinstance(val, list) and isinstance(param, str):
            raise RelaxError("Invalid value and parameter argument combination, for details by type 'help(value.set)'")

        # Value array and parameter array of equal length.
        if isinstance(val, list) and isinstance(param, list) and len(val) != len(param):
            raise RelaxError("Both the value array and parameter array must be of equal length.")

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
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "value.write("
            text = text + "param=" + repr(param)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(param, 'parameter')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')

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
