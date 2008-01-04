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
from Numeric import ArrayType, zeros
from re import compile, match
import sys

# relax module imports.
from data import Data as relax_data_store
from generic_fns import diffusion_tensor
from generic_fns.minimise import reset_min_stats
from generic_fns.selection import exists_mol_res_spin_data, spin_loop
from relax_errors import RelaxError, RelaxFileEmptyError, RelaxNoResError, RelaxNoPipeError, RelaxNoSequenceError, RelaxRegExpError, RelaxUnknownParamError, RelaxValueError
from specific_fns import get_specific_fn


def partition_params(val, param, return_data_name):
    """Function for sorting and partitioning the parameters and their values.

    The two major partitions are the tensor parameters and the spin specific parameters.

    @return:        A tuple, of length 4, of arrays.
    @return type:   tuple of arrays
    """

    # Initialise.
    tensor_params = []
    tensor_values = []
    spin_params = []
    spin_values = []

    # Separate the residue specific parameters from the diffusion tensor parameters.
    if param:
        # Single parameter.
        if type(param) == str:
            # Get the diffusion tensor parameter name.
            tensor_name = diffusion_tensor.return_data_name(param)

            # The parameter is a diffusion parameter.
            if tensor_name:
                # List of values.
                if type(val) == list or type(val) == ArrayType:
                    # Parameter name.
                    for i in xrange(len(val)):
                        tensor_params.append(tensor_name)

                    # Parameter value.
                    tensor_values = val

                # Single value.
                else:
                    # Parameter name.
                    tensor_params.append(param)

                    # Parameter value.
                    tensor_values.append(val)

            # The parameter is not a diffusion parameter.
            elif return_data_name(param):
                # List of values.
                if type(val) == list or type(val) == ArrayType:
                    # Parameter name.
                    for i in xrange(len(val)):
                        spin_params.append(param)

                    # Parameter value.
                    spin_values = val

                # Single value.
                else:
                    # Parameter name.
                    spin_params.append(param)

                    # Parameter value.
                    spin_values.append(val)

            # Unknown parameter
            else:
                raise RelaxUnknownParamError, param

        # Multiple parameters.
        elif type(param) == list:
            # Loop over all parameters.
            for i in xrange(len(param)):
                # Get the diffusion tensor parameter name.
                try:
                    tensor_name = diffusion_tensor.return_data_name(param[i])
                except RelaxUnknownParamError:
                    tensor_name = None

                # The parameter is a diffusion parameter.
                if tensor_name:
                    # Parameter name.
                    tensor_params.append(tensor_name)

                    # Parameter value.
                    if type(val) == list or type(val) == ArrayType:
                        tensor_values.append(val[i])
                    else:
                        tensor_values.append(val)

                # The parameter is not a diffusion parameter.
                elif return_data_name(param[i]):
                    # Parameter name.
                    spin_params.append(param[i])

                    # Parameter value.
                    if type(val) == list or type(val) == ArrayType:
                        spin_values.append(val[i])
                    else:
                        spin_values.append(val)

                # Unknown parameter
                else:
                    raise RelaxUnknownParamError, param[i]


    # All other parameters.
    else:
        # No parameter or a single parameter.
        if param == None or type(param) == str:
            # List of values.
            if type(val) == list or type(val) == ArrayType:
                # Parameter name.
                for i in xrange(len(val)):
                    spin_params.append(param)

                # Parameter value.
                spin_values = val

            # Single value.
            else:
                # Parameter name.
                spin_params.append(param)

                # Parameter value.
                spin_values.append(val)

        # Multiple parameters.
        elif type(param) == list:
            # Loop over all parameters.
            for i in xrange(len(param)):
                # Parameter name.
                spin_params.append(param[i])

                # Parameter value.
                if type(val) == list or type(val) == ArrayType:
                    spin_values.append(val[i])
                else:
                    spin_values.append(val)

    # Debugging.
    if len(tensor_params) != len(tensor_values) or len(spin_params) != len(spin_values):
        print "Diff params: " + `tensor_params`
        print "Diff values: " + `tensor_values`
        print "Res params: " + `spin_params`
        print "Res values: " + `spin_values`
        raise RelaxError, "Bug in the code."

    # Return the partitioned parameters and values.
    return tensor_params, tensor_values, spin_params, spin_values


def set(val=None, param=None, spin_id=None, force=False):
    """Function for setting residue specific data values.

    @param val:     The parameter values.
    @type val:      None, number, or list of numbers
    @param param:   The parameter names.
    @type val:      None, str, or list of str
    @param spin_id: The spin identification string.
    @type spin_id:  str
    @param force:   A flag forcing the overwriting of current values.
    @type force:    bool
    """

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Specific functions.
    return_data_name = get_specific_fn('return_data_name', cdp.pipe_type)
    return_value = get_specific_fn('return_value', cdp.pipe_type)
    set = get_specific_fn('set', cdp.pipe_type)

    # Sort the parameters and their values.
    tensor_params, tensor_values, spin_params, spin_values = partition_params(val, param, return_data_name)


    # Diffusion tensor parameters.
    ##############################

    if tensor_params:
        # Set the diffusion parameters.
        diffusion_tensor.set(value=tensor_values, param=tensor_params)


    # Residue specific parameters.
    ##############################

    if spin_params:
        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # First test if parameter value already exists, prior to setting any params.
        if not force:
            # Loop over the spins.
            for spin in spin_loop(spin_id):
                # Skip unselected spins.
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
            # Skip unselected residues.
            if not spin.select:
                continue

            # Go to the specific code.
            for j in xrange(len(spin_params)):
                set(value=spin_values[j], error=None, spin=spin, param=spin_params[j])

    # Reset all minimisation statistics.
    reset_min_stats()



class Value:
    def __init__(self, relax):
        """Class containing functions for the setting up of data structures."""

        self.relax = relax


    def copy(self, run1=None, run2=None, param=None):
        """Function for copying residue specific data values from run1 to run2."""

        # Arguments.
        self.param = param

        # Test if run1 exists.
        if not run1 in relax_data_store.run_names:
            raise RelaxNoPipeError, run1

        # Test if run2 exists.
        if not run2 in relax_data_store.run_names:
            raise RelaxNoPipeError, run2

        # Test if the sequence data for run1 is loaded.
        if not relax_data_store.res.has_key(run1):
            raise RelaxNoSequenceError, run1

        # Test if the sequence data for run2 is loaded.
        if not relax_data_store.res.has_key(run2):
            raise RelaxNoSequenceError, run2

        # Function type.
        self.function_type = relax_data_store.run_types[relax_data_store.run_names.index(run1)]

        # Specific value and error returning function.
        return_value = self.relax.specific_setup.setup('return_value', self.function_type)

        # Specific set function.
        set = self.relax.specific_setup.setup('set', self.function_type)

        # Test if the data exists for run2.
        for i in xrange(len(relax_data_store.res[run2])):
            # Get the value and error for run2.
            value, error = return_value(run2, i, param)

            # Data exists.
            if value != None or error != None:
                raise RelaxValueError, (param, run2)

        # Copy the values.
        for i in xrange(len(relax_data_store.res[run1])):
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
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if the sequence data is loaded.
        if not relax_data_store.res.has_key(self.run):
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
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if sequence data is loaded.
        if not relax_data_store.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Function type.
        self.function_type = relax_data_store.run_types[relax_data_store.run_names.index(self.run)]

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
        for i in xrange(len(relax_data_store.res[self.run])):
            # Skip unselected residues.
            if not relax_data_store.res[self.run][i].select:
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

            # Find the index of relax_data_store.res[self.run] which corresponds to the relaxation data set i.
            index = None
            for j in xrange(len(relax_data_store.res[self.run])):
                if relax_data_store.res[self.run][j].num == spin_num and (spin_name == None or relax_data_store.res[self.run][j].name == spin_name):
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
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if the sequence data is loaded.
        if not relax_data_store.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Open the file for writing.
        file = self.relax.IO.open_write_file(file, dir, force)

        # Write the data.
        self.write_data(file, return_value)

        # Close the file.
        file.close()


    def write_data(self, file, return_value=None):
        """Function for writing data."""

        # Get the value and error returning function if required.
        if not return_value:
            # Function type.
            self.function_type = relax_data_store.run_types[relax_data_store.run_names.index(self.run)]

            # Specific value and error returning function.
            return_value = self.relax.specific_setup.setup('return_value', self.function_type)

        # Write a header line.
        file.write("%-5s%-6s%-30s%-30s\n" % ('Num', 'Name', 'Value', 'Error'))

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Remap the data structure 'relax_data_store.res[self.run][i]'.
            data = relax_data_store.res[self.run][i]

            # Get the value and error.
            value, error = return_value(self.run, i, self.param)

            # Write the data.
            file.write("%-5i%-6s%-30s%-30s\n" % (data.num, data.name, `value`, `error`))
