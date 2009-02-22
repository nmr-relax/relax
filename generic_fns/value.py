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
"""Module for the manipulation of parameter and constant values."""

# Python module imports.
from numpy import ndarray
import sys

# relax module imports.
from generic_fns import minimise, pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data, generate_spin_id_data_array, return_spin, spin_loop
from generic_fns.sequence import write_header, write_line
from relax_errors import RelaxError, RelaxFileEmptyError, RelaxNoSequenceError, RelaxNoSpinError, RelaxParamSetError, RelaxValueError
from relax_io import extract_data, open_write_file, strip
import specific_fns


def copy(pipe_from=None, pipe_to=None, param=None):
    """Copy spin specific data values from pipe_from to pipe_to.

    @param pipe_from:   The data pipe to copy the value from.  This defaults to the current data
                        pipe.
    @type pipe_from:    str
    @param pipe_to:     The data pipe to copy the value to.  This defaults to the current data pipe.
    @type pipe_to:      str
    @param param:       The name of the parameter to copy the values of.
    @type param:        str
    """

    # The current data pipe.
    if pipe_from == None:
        pipe_from = pipes.cdp_name()
    if pipe_to == None:
        pipe_to = pipes.cdp_name()

    # The second pipe does not exist.
    pipes.test(pipe_to)

    # Test if the sequence data for pipe_from is loaded.
    if not exists_mol_res_spin_data(pipe_from):
        raise RelaxNoSequenceError, pipe_from

    # Test if the sequence data for pipe_to is loaded.
    if not exists_mol_res_spin_data(pipe_to):
        raise RelaxNoSequenceError, pipe_to

    # Specific value and error returning function.
    return_value = specific_fns.setup.get_specific_fn('return_value', pipes.get_type(pipe_from))

    # Test if the data exists for pipe_to.
    for spin in spin_loop(pipe_to):
        # Get the value and error for pipe_to.
        value, error = return_value(spin, param)

        # Data exists.
        if value != None or error != None:
            raise RelaxValueError, (param, pipe_to)

    # Copy the values.
    for spin, spin_id in spin_loop(pipe_from, return_id=True):
        # Get the value and error from pipe_from.
        value, error = return_value(spin, param)

        # Get the equivalent spin in pipe_to.
        spin_to = return_spin(spin_id, pipe_to)

        # Set the values of pipe_to.
        set_spin_params(spin_to, value=value, error=error, param=param)

    # Reset all minimisation statistics.
    minimise.reset_min_stats(pipe_to)


def display(param=None):
    """Display spin specific data values.

    @param param:       The name of the parameter to display.
    @type param:        str
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Print the data.
    write_data(param, sys.stdout)


def partition_params(val, param):
    """Function for sorting and partitioning the parameters and their values.

    The two major partitions are the tensor parameters and the spin specific parameters.

    @param val:     The parameter values.
    @type val:      None, number, or list of numbers
    @param param:   The parameter names.
    @type param:    None, str, or list of str
    @return:        A tuple, of length 4, of lists.  The first and second elements are the lists of
                    spin specific parameters and values respectively.  The third and forth elements
                    are the lists of all other parameters and their values.
    @rtype:         tuple of 4 lists
    """

    # Specific functions.
    is_spin_param = specific_fns.setup.get_specific_fn('is_spin_param', pipes.get_type())

    # Initialise.
    spin_params = []
    spin_values = []
    other_params = []
    other_values = []

    # Single parameter.
    if type(param) == str:
        # Spin specific parameter.
        if is_spin_param(param):
            params = spin_params
            values = spin_values

        # Other parameters.
        else:
            params = other_params
            values = other_values

        # List of values.
        if type(val) == list or isinstance(val, ndarray):
            # Parameter name.
            for i in xrange(len(val)):
                params.append(param)

            # Parameter value.
            values = val

        # Single value.
        else:
            # Parameter name.
            params.append(param)

            # Parameter value.
            values.append(val)

    # Multiple parameters.
    elif type(param) == list:
        # Loop over all parameters.
        for i in xrange(len(param)):
            # Spin specific parameter.
            if is_spin_param(param[i]):
                params = spin_params
                values = spin_values

            # Other parameters.
            else:
                params = other_params
                values = other_values

            # Parameter name.
            params.append(param[i])

            # Parameter value.
            if type(val) == list or isinstance(val, ndarray):
                values.append(val[i])
            else:
                values.append(val)


    # Return the partitioned parameters and values.
    return spin_params, spin_values, other_params, other_values


def read(param=None, scaling=1.0, file=None, dir=None, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, data_col=2, error_col=3, sep=None):
    """Read spin specific data values from a file.

    @keyword param:         The name of the parameter to read.
    @type param:            str
    @keyword scaling:       A scaling factor by which all read values are multiplied by.
    @type scaling:          float
    @keyword file:          The name of the file to open.
    @type file:             str
    @keyword dir:           The directory containing the file (defaults to the current directory if
                            None).
    @type dir:              str or None
    @keyword mol_name_col:  The column containing the molecule name information.
    @type mol_name_col:     int or None
    @keyword res_name_col:  The column containing the residue name information.
    @type res_name_col:     int or None
    @keyword res_num_col:   The column containing the residue number information.
    @type res_num_col:      int or None
    @keyword spin_name_col  The column containing the spin name information.
    @type spin_name_col:    int or None
    @keyword spin_num_col:  The column containing the spin number information.
    @type spin_num_col:     int or None
    @keyword data_col:      The column containing the values.
    @type data_col:         int
    @keyword error_col:     The column containing the errors.
    @type error_col:        int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Minimisation parameter.
    if minimise.return_data_name(param):
        # Minimisation statistic flag.
        min_stat = True

        # Specific value and error returning function.
        return_value = minimise.return_value

        # Specific set function.
        set = minimise.set

    # Normal parameter.
    else:
        # Minimisation statistic flag.
        min_stat = False

        # Specific v
        return_value = specific_fns.setup.get_specific_fn('return_value', pipes.get_type())

        # Specific set function.
        set = set_spin_params

    # Test data corresponding to param already exists.
    for spin in spin_loop():
        # Skip deselected spins.
        if not spin.select:
            continue

        # Get the value and error.
        value, error = return_value(spin, param)

        # Data exists.
        if value != None or error != None:
            raise RelaxValueError, param

    # Extract the data from the file.
    file_data = extract_data(file, dir=dir, sep=sep)

    # Count the number of header lines.
    header_lines = 0
    num_col = max(res_num_col, spin_num_col)
    for i in xrange(len(file_data)):
        try:
            int(file_data[i][num_col])
        except:
            header_lines = header_lines + 1
        else:
            break

    # Remove the header.
    file_data = file_data[header_lines:]

    # Strip the data.
    file_data = strip(file_data)

    # Do nothing if the file does not exist.
    if not file_data:
        raise RelaxFileEmptyError

    # Minimum number of columns.
    min_col_num = max(mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, error_col)

    # Test the validity of the data.
    for i in xrange(len(file_data)):
        # Skip missing data.
        if len(file_data[i]) <= min_col_num:
            continue

        try:
            # Value column.
            if file_data[i][data_col] != 'None':
                float(file_data[i][data_col])

            # Error column.
            if error_col != None and file_data[i][error_col] != 'None':
                float(file_data[i][error_col])

        except ValueError:
            if error_col != None:
                raise RelaxError, "The data is invalid (data=" + file_data[i][data_col] + ", error=" + file_data[i][error_col] + ")."
            else:
                raise RelaxError, "The data is invalid (data=" + file_data[i][data_col] + ")."

    # Loop over the data.
    for i in xrange(len(file_data)):
        # Skip missing data.
        if len(file_data[i]) <= min_col_num:
            continue

        # Generate the spin identification string.
        id = generate_spin_id_data_array(data=file_data[i], mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col)

        # Value.
        if file_data[i][data_col] != 'None':
            value = float(file_data[i][data_col])
        else:
            value = None

        # Error.
        if error_col != None and file_data[i][error_col] != 'None':
            error = float(file_data[i][error_col])
        else:
            error = None

        # Get the corresponding spin container.
        spin = return_spin(id)
        if spin == None:
            raise RelaxNoSpinError, id

        # Set the value.
        set(value=value, error=error, param=param, scaling=scaling, spin=spin)

    # Reset the minimisation statistics.
    if not min_stat:
        minimise.reset_min_stats()


def set(val=None, param=None, spin_id=None, force=True, reset=True):
    """Set global or spin specific data values.

    @keyword val:       The parameter values.
    @type val:          None, number, or list of numbers
    @keyword param:     The parameter names.
    @type param:        None, str, or list of str
    @keyword spin_id:   The spin identification string.
    @type spin_id:      str
    @keyword force:     A flag forcing the overwriting of current values.
    @type force:        bool
    @keyword reset:     A flag which if True will cause all minimisation statistics to be reset.
    @type reset:        bool
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Specific functions.
    return_value = specific_fns.setup.get_specific_fn('return_value', pipes.get_type())
    set_non_spin_params = specific_fns.setup.get_specific_fn('set_non_spin_params', pipes.get_type())

    # The parameters have been specified.
    if param:
        # Partition the parameters into those which are spin specific and those which are not.
        spin_params, spin_values, other_params, other_values = partition_params(val, param)

        # Spin specific parameters.
        if spin_params:
            # Test if the sequence data is loaded.
            if not exists_mol_res_spin_data():
                raise RelaxNoSequenceError

            # First test if parameter value already exists, prior to setting any params.
            if not force:
                # Loop over the spins.
                for spin in spin_loop(spin_id):
                    # Skip deselected spins.
                    if not spin.select:
                        continue

                    # Loop over the parameters.
                    for param in spin_params:
                        # Get the value and error.
                        temp_value, temp_error = return_value(spin, param)

                        # Data exists.
                        if temp_value != None or temp_error != None:
                            raise RelaxValueError, (param)

            # Loop over the spins.
            for spin in spin_loop(spin_id):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Set the individual parameter values.
                for j in xrange(len(spin_params)):
                    set_spin_params(value=spin_values[j], error=None, spin=spin, param=spin_params[j])


        # All other parameters.
        if other_params:
            set_non_spin_params(value=other_values, param=other_params)


    # All model parameters (i.e. no parameters have been supplied).
    else:
        # Convert val to a list if necessary.
        if type(val) != list or not isinstance(val, ndarray):
            val = [val]

        # Spin specific models.
        if exists_mol_res_spin_data():
            # Loop over the spins.
            for spin in spin_loop(spin_id):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Set the individual parameter values.
                for j in xrange(len(val)):
                    set_spin_params(value=val[j], error=None, spin=spin, param=None)

        # Set the non-spin specific parameters.
        set_non_spin_params(value=val, param=param)

    # Reset all minimisation statistics.
    if reset:
        minimise.reset_min_stats()


def set_spin_params(value=None, error=None, param=None, scaling=1.0, spin=None):
    """Set spin specific parameter values.

    @param value:   The value to change the parameter to.
    @type value:    float or str
    @param error:   The error value associated with the parameter, also to be set.
    @type error:    float or str
    @param param:   The name of the parameter to change.
    @type param:    str
    @param scaling: The scaling factor for the value or error parameters.
    @type scaling:  float
    @param spin:    The SpinContainer object.
    @type spin:     SpinContainer
    """

    # Specific functions.
    data_init = specific_fns.setup.get_specific_fn('data_init', pipes.get_type())
    default_value = specific_fns.setup.get_specific_fn('default_value', pipes.get_type())
    return_data_name = specific_fns.setup.get_specific_fn('return_data_name', pipes.get_type())
    set_update = specific_fns.setup.get_specific_fn('set_update', pipes.get_type())


    # Setting the model parameters prior to minimisation.
    #####################################################

    if param == None:
        # The values are supplied by the user:
        if value:
            # Test if the length of the value array is equal to the length of the parameter array.
            if len(value) != len(spin.params):
                raise RelaxError, "The length of " + `len(value)` + " of the value array must be equal to the length of the parameter array, " + `spin.params` + ", for spin " + `spin.num` + " " + spin.name + "."

        # Default values.
        else:
            # Set 'value' to an empty array.
            value = []

            # Loop over the parameters.
            for i in xrange(len(spin.params)):
                value.append(default_value(spin.params[i]))

        # Loop over the parameters.
        for i in xrange(len(spin.params)):
            # Get the object.
            object_name = return_data_name(spin.params[i])
            if not object_name:
                raise RelaxError, "The data type " + `spin.params[i]` + " does not exist."

            # Initialise all data if it doesn't exist.
            if not hasattr(spin, object_name):
                data_init(spin)

            # Set the value.
            if value[i] == None:
                setattr(spin, object_name, None)
            else:
                # Catch parameters with string values.
                try:
                    value[i] = float(value[i]) * scaling
                except ValueError:
                    pass

                # Set the attribute.
                setattr(spin, object_name, value[i])


    # Individual data type.
    #######################

    else:
        # Get the object.
        object_name = return_data_name(param)
        if not object_name:
            raise RelaxError, "The data type " + `param` + " does not exist."

        # Initialise all data if it doesn't exist.
        if not hasattr(spin, object_name):
            data_init(spin)

        # Default value.
        if value == None:
            value = default_value(object_name)

        # No default value, hence the parameter cannot be set.
        if value == None:
            raise RelaxParamSetError, param

        # Set the value.
        if value == None:
            setattr(spin, object_name, None)
        else:
            # Catch parameters with string values.
            try:
                value = float(value) * scaling
            except ValueError:
                pass

            # Set the attribute.
            setattr(spin, object_name, value)

        # Set the error.
        if error != None:
            # Catch parameters with string values.
            try:
                error = float(error) * scaling
            except ValueError:
                pass

            # Set the attribute.
            setattr(spin, object_name+'_err', error)

        # Update the other parameters if necessary.
        set_update(param=param, spin=spin)


def write(param=None, file=None, dir=None, force=False, return_value=None):
    """Write data to a file.

    @keyword param:         The name of the parameter to write to file.
    @type param:            str
    @keyword file:          The file to write the data to.
    @type file:             str
    @keyword dir:           The name of the directory to place the file into (defaults to the
                            current directory).
    @type dir:              str
    @keyword force:         A flag which if True will cause any pre-existing file to be overwritten.
    @type force:            bool
    @keyword return_value:  An optional function which if supplied will override the default value
                            returning function.
    @type return_value:     None or func
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Write the data.
    write_data(param, file, return_value)

    # Close the file.
    file.close()


def write_data(param=None, file=None, return_value=None):
    """The function which actually writes the data.

    @keyword file:          The file to write the data to.
    @type file:             str
    @keyword dir:           The name of the directory to place the file into (defaults to the
                            current directory).
    @type dir:              str
    @keyword return_value:  An optional function which if supplied will override the default value
                            returning function.
    @type return_value:     None or func
    """

    # Get the value and error returning function if required.
    if not return_value:
        return_value = specific_fns.setup.get_specific_fn('return_value', pipes.get_type())

    # Format string.
    format = "%-30s%-30s"

    # Write a header line.
    write_header(file, extra_format=format, extra_values=('Value', 'Error'), mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True)

    # Loop over the sequence.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # Get the value and error.
        value, error = return_value(spin, param)

        # Write the data.
        write_line(file, mol_name, res_num, res_name, spin.num, spin.name, extra_format=format, extra_values=(`value`, `error`), mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True)
