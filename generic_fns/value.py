###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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
from numpy import ndarray, zeros
from re import compile, match
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import diffusion_tensor
from generic_fns.minimise import reset_min_stats
from generic_fns.mol_res_spin import exists_mol_res_spin_data, spin_loop
from relax_errors import RelaxError, RelaxFileEmptyError, RelaxNoResError, RelaxNoPipeError, RelaxNoSequenceError, RelaxParamSetError, RelaxRegExpError, RelaxUnknownParamError, RelaxValueError
from specific_fns.setup import get_specific_fn


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
    is_spin_param = get_specific_fn('is_spin_param', ds[ds.current_pipe].pipe_type)

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


def set(val=None, param=None, spin_id=None, force=False):
    """Function for setting residue specific data values.

    @param val:     The parameter values.
    @type val:      None, number, or list of numbers
    @param param:   The parameter names.
    @type param:    None, str, or list of str
    @param spin_id: The spin identification string.
    @type spin_id:  str
    @param force:   A flag forcing the overwriting of current values.
    @type force:    bool
    """

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Specific functions.
    return_value = get_specific_fn('return_value', ds[ds.current_pipe].pipe_type)
    set_non_spin_params = get_specific_fn('set_non_spin_params', ds[ds.current_pipe].pipe_type)

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
                # Skip deselected residues.
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
    reset_min_stats()


def set_spin_params(value=None, error=None, param=None, scaling=1.0, spin=None):
    """Function for setting spin specific parameter values.

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
    data_init = get_specific_fn('data_init', ds[ds.current_pipe].pipe_type)
    default_value = get_specific_fn('default_value', ds[ds.current_pipe].pipe_type)
    return_data_name = get_specific_fn('return_data_name', ds[ds.current_pipe].pipe_type)
    set_update = get_specific_fn('set_update', ds[ds.current_pipe].pipe_type)


    # Setting the model parameters prior to minimisation.
    #####################################################

    if param == None:
        # The values are supplied by the user:
        if value:
            # Test if the length of the value array is equal to the length of the parameter array.
            if len(value) != len(spin.params):
                raise RelaxError, "The length of " + `len(value)` + " of the value array must be equal to the length of the parameter array, " + `spin.params` + ", for residue " + `spin.num` + " " + spin.name + "."

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




class Value:
    def __init__(self, relax):
        """Class containing functions for the setting up of data structures."""

        self.relax = relax


    def copy(self, run1=None, run2=None, param=None):
        """Function for copying residue specific data values from run1 to run2."""

        # Arguments.
        self.param = param

        # Test if run1 exists.
        if not run1 in ds.run_names:
            raise RelaxNoPipeError, run1

        # Test if run2 exists.
        if not run2 in ds.run_names:
            raise RelaxNoPipeError, run2

        # Test if the sequence data for run1 is loaded.
        if not ds.res.has_key(run1):
            raise RelaxNoSequenceError, run1

        # Test if the sequence data for run2 is loaded.
        if not ds.res.has_key(run2):
            raise RelaxNoSequenceError, run2

        # Function type.
        self.function_type = ds.run_types[ds.run_names.index(run1)]

        # Specific value and error returning function.
        return_value = self.relax.specific_setup.setup('return_value', self.function_type)

        # Specific set function.
        set = self.relax.specific_setup.setup('set', self.function_type)

        # Test if the data exists for run2.
        for i in xrange(len(ds.res[run2])):
            # Get the value and error for run2.
            value, error = return_value(run2, i, param)

            # Data exists.
            if value != None or error != None:
                raise RelaxValueError, (param, run2)

        # Copy the values.
        for i in xrange(len(ds.res[run1])):
            # Get the value and error for run1.
            value, error = return_value(run1, i, param)

            # Set the values of run2.
            set(run=run2, value=value, error=error, param=param, index=i)

            # Reset the residue specific minimisation statistics.
            self.relax.generic.minimise.reset_min_stats(run2, i)

        # Reset the global minimisation statistics.
        self.relax.generic.minimise.reset_min_stats(run2)


    def display(self, run=None, param=None):
        """Function for displaying residue specific data values."""

        # Arguments.
        self.run = run
        self.param = param

        # Test if the run exists.
        if not self.run in ds.run_names:
            raise RelaxNoPipeError, self.run

        # Test if the sequence data is loaded.
        if not ds.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Print the data.
        self.write_data(sys.stdout)


    def read(self, run=None, param=None, scaling=1.0, file=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
        """Function for reading residue specific data values from a file."""

        # Arguments.
        self.run = run
        self.param = param
        self.scaling = scaling

        # Test if the run exists.
        if not self.run in ds.run_names:
            raise RelaxNoPipeError, self.run

        # Test if sequence data is loaded.
        if not ds.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Function type.
        self.function_type = ds.run_types[ds.run_names.index(self.run)]

        # Minimisation parameter.
        if self.relax.generic.minimise.return_data_name(param):
            # Minimisation statistic flag.
            min_stat = 1

            # Specific value and error returning function.
            return_value = self.relax.generic.minimise.return_value

            # Specific set function.
            set = self.relax.generic.minimise.set

        # Normal parameter.
        else:
            # Minimisation statistic flag.
            min_stat = 0

            # Specific value and error returning function.
            return_value = self.relax.specific_setup.setup('return_value', self.function_type)

            # Specific set function.
            set = self.relax.specific_setup.setup('set', self.function_type)

        # Test data corresponding to param already exists.
        for i in xrange(len(ds.res[self.run])):
            # Skip deselected residues.
            if not ds.res[self.run][i].select:
                continue

            # Get the value and error.
            value, error = return_value(self.run, i, self.param)

            # Data exists.
            if value != None or error != None:
                raise RelaxValueError, (self.param, self.run)

        # Extract the data from the file.
        file_data = self.relax.IO.extract_data(file)

        # Count the number of header lines.
        header_lines = 0
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
        file_data = self.relax.IO.strip(file_data)

        # Do nothing if the file does not exist.
        if not file_data:
            raise RelaxFileEmptyError

        # Test the validity of the data.
        for i in xrange(len(file_data)):
            # Skip missing data.
            if len(file_data[i]) <= data_col or len(file_data[i]) <= error_col:
                continue

            try:
                # Number column.
                int(file_data[i][num_col])

                # Value column.
                if file_data[i][data_col] != 'None':
                    float(file_data[i][data_col])

                # Error column.
                if error_col != None and file_data[i][error_col] != 'None':
                    float(file_data[i][error_col])

            except ValueError:
                if error_col != None:
                    if name_col != None:
                        raise RelaxError, "The data is invalid (num=" + file_data[i][num_col] + ", name=" + file_data[i][name_col] + ", data=" + file_data[i][data_col] + ", error=" + file_data[i][error_col] + ")."
                    else:
                        raise RelaxError, "The data is invalid (num=" + file_data[i][num_col] + ", data=" + file_data[i][data_col] + ", error=" + file_data[i][error_col] + ")."
                else:
                    if name_col != None:
                        raise RelaxError, "The data is invalid (num=" + file_data[i][num_col] + ", name=" + file_data[i][name_col] + ", data=" + file_data[i][data_col] + ")."
                    else:
                        raise RelaxError, "The data is invalid (num=" + file_data[i][num_col] + ", data=" + file_data[i][data_col] + ")."

        # Loop over the data.
        for i in xrange(len(file_data)):
            # Skip missing data.
            if len(file_data[i]) <= data_col or len(file_data[i]) <= error_col:
                continue

            # Residue number.
            spin_num = int(file_data[i][num_col])

            # Residue name.
            if name_col == None:
                spin_name = None
            else:
                spin_name = file_data[i][name_col]

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

            # Find the index of ds.res[self.run] which corresponds to the relaxation data set i.
            index = None
            for j in xrange(len(ds.res[self.run])):
                if ds.res[self.run][j].num == spin_num and (spin_name == None or ds.res[self.run][j].name == spin_name):
                    index = j
                    break
            if index == None:
                raise RelaxNoResError, (spin_num, spin_name)

            # Set the value.
            set(run=run, value=value, error=error, param=self.param, scaling=scaling, index=index)

            # Reset the residue specific minimisation statistics.
            if not min_stat:
                self.relax.generic.minimise.reset_min_stats(self.run, index)

        # Reset the global minimisation statistics.
        if not min_stat:
            self.relax.generic.minimise.reset_min_stats(self.run)


    def write(self, run=None, param=None, file=None, dir=None, force=0, return_value=None):
        """Function for writing data to a file."""

        # Arguments.
        self.run = run
        self.param = param

        # Test if the run exists.
        if not self.run in ds.run_names:
            raise RelaxNoPipeError, self.run

        # Test if the sequence data is loaded.
        if not ds.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Open the file for writing.
        file = self.relax.IO.open_write_file(file, dir, force)

        # Write the data.
        self.write_data(file, return_value)

        # Close the file.
        file.close()


    def write_data(self, run=None, param=None, file=None, return_value=None):
        """Function for writing data."""

        # Get the value and error returning function if required.
        if not return_value:
            # Function type.
            self.function_type = ds.run_types[ds.run_names.index(run)]

            # Specific value and error returning function.
            return_value = self.relax.specific_setup.setup('return_value', self.function_type)

        # Write a header line.
        file.write("%-5s%-6s%-30s%-30s\n" % ('Num', 'Name', 'Value', 'Error'))

        # Loop over the sequence.
        for i in xrange(len(ds.res[run])):
            # Remap the data structure 'ds.res[run][i]'.
            data = ds.res[run][i]

            # Get the value and error.
            value, error = return_value(run, i, param)

            # Write the data.
            file.write("%-5i%-6s%-30s%-30s\n" % (data.num, data.name, `value`, `error`))
