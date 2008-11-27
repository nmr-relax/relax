###############################################################################
#                                                                             #
# Copyright (C) 2003-2006 Edward d'Auvergne                                   #
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


from Numeric import ArrayType, zeros
from re import compile, match
import sys


class Value:
    def __init__(self, relax):
        """Class containing functions for the setting up of data structures."""

        self.relax = relax


    def copy(self, run1=None, run2=None, param=None):
        """Function for copying residue specific data values from run1 to run2."""

        # Arguments.
        self.param = param

        # Test if run1 exists.
        if not run1 in self.relax.data.run_names:
            raise RelaxNoRunError, run1

        # Test if run2 exists.
        if not run2 in self.relax.data.run_names:
            raise RelaxNoRunError, run2

        # Test if the sequence data for run1 is loaded.
        if not self.relax.data.res.has_key(run1):
            raise RelaxNoSequenceError, run1

        # Test if the sequence data for run2 is loaded.
        if not self.relax.data.res.has_key(run2):
            raise RelaxNoSequenceError, run2

        # Function type.
        self.function_type = self.relax.data.run_types[self.relax.data.run_names.index(run1)]

        # Specific value and error returning function.
        return_value = self.relax.specific_setup.setup('return_value', self.function_type)

        # Specific set function.
        set = self.relax.specific_setup.setup('set', self.function_type)

        # Test if the data exists for run2.
        for i in xrange(len(self.relax.data.res[run2])):
            # Get the value and error for run2.
            value, error = return_value(run2, i, param)

            # Data exists.
            if value != None or error != None:
                raise RelaxValueError, (param, run2)

        # Copy the values.
        for i in xrange(len(self.relax.data.res[run1])):
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
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Print the data.
        self.write_data(run=run, param=param, file=sys.stdout)


    def read(self, run=None, param=None, scaling=1.0, file=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
        """Function for reading residue specific data values from a file."""

        # Arguments.
        self.run = run
        self.param = param
        self.scaling = scaling

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Function type.
        self.function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]

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
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
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
            res_num = int(file_data[i][num_col])

            # Residue name.
            if name_col == None:
                res_name = None
            else:
                res_name = file_data[i][name_col]

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

            # Find the index of self.relax.data.res[self.run] which corresponds to the relaxation data set i.
            index = None
            for j in xrange(len(self.relax.data.res[self.run])):
                if self.relax.data.res[self.run][j].num == res_num and (res_name == None or self.relax.data.res[self.run][j].name == res_name):
                    index = j
                    break
            if index == None:
                raise RelaxNoResError, (res_num, res_name)

            # Set the value.
            set(run=run, value=value, error=error, param=self.param, scaling=scaling, index=index)

            # Reset the residue specific minimisation statistics.
            if not min_stat:
                self.relax.generic.minimise.reset_min_stats(self.run, index)

        # Reset the global minimisation statistics.
        if not min_stat:
            self.relax.generic.minimise.reset_min_stats(self.run)


    def set(self, run=None, value=None, param=None, res_num=None, res_name=None, force=0):
        """Function for setting residue specific data values."""

        # Arguments
        self.run = run
        self.value = value
        self.param = param
        self.res_num = res_num
        self.res_name = res_name
        self.force = force

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Function type.
        self.function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]

        # Specific functions.
        self.return_data_name = self.relax.specific_setup.setup('return_data_name', self.function_type)
        return_value = self.relax.specific_setup.setup('return_value', self.function_type)
        set = self.relax.specific_setup.setup('set', self.function_type)

        # Sort the parameters and their values.
        self.sort_params()


        # Diffusion tensor parameters.
        ##############################

        if self.diff_params:
            # Set the diffusion parameters.
            self.relax.generic.diffusion_tensor.set(run=self.run, value=self.diff_values, param=self.diff_params)


        # Residue specific parameters.
        ##############################

        if self.res_params:
            # Test if the sequence data is loaded.
            if not self.relax.data.res.has_key(self.run):
                raise RelaxNoSequenceError, self.run

            # Test if the residue number is a valid regular expression.
            if type(self.res_num) == str:
                try:
                    compile(self.res_num)
                except:
                    raise RelaxRegExpError, ('residue number', self.res_num)

            # Test if the residue name is a valid regular expression.
            if self.res_name:
                try:
                    compile(self.res_name)
                except:
                    raise RelaxRegExpError, ('residue name', self.res_name)

            # Test if parameter value already exists.
            if not self.force:
                # Loop over the residues.
                for i in xrange(len(self.relax.data.res[self.run])):
                    # Skip unselected residues.
                    if not self.relax.data.res[self.run][i].select:
                        continue

                    # If 'res_num' is not None, skip the residue if there is no match.
                    if type(self.res_num) == int and not self.relax.data.res[self.run][i].num == self.res_num:
                        continue
                    elif type(self.res_num) == str and not match(self.res_num, `self.relax.data.res[self.run][i].num`):
                        continue

                    # If 'res_name' is not None, skip the residue if there is no match.
                    if self.res_name != None and not match(self.res_name, self.relax.data.res[self.run][i].name):
                        continue

                    # Loop over the parameters.
                    for param in self.res_params:
                        if param:
                            # Get the value and error.
                            temp_value, temp_error = return_value(self.run, i, param)

                            # Data exists.
                            if temp_value != None or temp_error != None:
                                raise RelaxValueError, (param, self.run)

            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # If 'res_num' is not None, skip the residue if there is no match.
                if type(self.res_num) == int and not self.relax.data.res[self.run][i].num == self.res_num:
                    continue
                elif type(self.res_num) == str and not match(self.res_num, `self.relax.data.res[self.run][i].num`):
                    continue

                # If 'res_name' is not None, skip the residue if there is no match.
                if self.res_name != None and not match(self.res_name, self.relax.data.res[self.run][i].name):
                    continue

                # Go to the specific code.
                for j in xrange(len(self.res_params)):
                    set(run=self.run, value=self.res_values[j], error=None, param=self.res_params[j], index=i)


        # Reset the minimisation statistics.
        ####################################

        # Reset the global minimisation statistics.
        self.relax.generic.minimise.reset_min_stats(self.run)

        # Reset the sequence specific minimisation statistics.
        if self.relax.data.res.has_key(self.run):
            for i in xrange(len(self.relax.data.res[self.run])):
                self.relax.generic.minimise.reset_min_stats(self.run, i)


    def sort_params(self):
        """Function for sorting the parameters and their values."""

        # Initialise.
        self.diff_params = []
        self.diff_values = []
        self.res_params = []
        self.res_values = []

        # Separate the residue specific parameters from the diffusion tensor parameters.
        if self.param:
            # Single parameter.
            if type(self.param) == str:
                # Get the diffusion tensor parameter name.
                diff_name = self.relax.generic.diffusion_tensor.return_data_name(self.param)

                # The parameter is a diffusion parameter.
                if diff_name:
                    # List of values.
                    if type(self.value) == list or type(self.value) == ArrayType:
                        # Parameter name.
                        for i in xrange(len(self.value)):
                            self.diff_params.append(diff_name)

                        # Parameter value.
                        self.diff_values = self.value

                    # Single value.
                    else:
                        # Parameter name.
                        self.diff_params.append(self.param)

                        # Parameter value.
                        self.diff_values.append(self.value)

                # The parameter is not a diffusion parameter.
                elif self.return_data_name(self.param):
                    # List of values.
                    if type(self.value) == list or type(self.value) == ArrayType:
                        # Parameter name.
                        for i in xrange(len(self.value)):
                            self.res_params.append(self.param)

                        # Parameter value.
                        self.res_values = self.value

                    # Single value.
                    else:
                        # Parameter name.
                        self.res_params.append(self.param)

                        # Parameter value.
                        self.res_values.append(self.value)

                # Unknown parameter
                else:
                    raise RelaxUnknownParamError, self.param

            # Multiple parameters.
            elif type(self.param) == list:
                # Loop over all parameters.
                for i in xrange(len(self.param)):
                    # Get the diffusion tensor parameter name.
                    diff_name = self.relax.generic.diffusion_tensor.return_data_name(self.param[i])

                    # The parameter is a diffusion parameter.
                    if diff_name:
                        # Parameter name.
                        self.diff_params.append(diff_name)

                        # Parameter value.
                        if type(self.value) == list or type(self.value) == ArrayType:
                            self.diff_values.append(self.value[i])
                        else:
                            self.diff_values.append(self.value)

                    # The parameter is not a diffusion parameter.
                    elif self.return_data_name(self.param[i]):
                        # Parameter name.
                        self.res_params.append(self.param[i])

                        # Parameter value.
                        if type(self.value) == list or type(self.value) == ArrayType:
                            self.res_values.append(self.value[i])
                        else:
                            self.res_values.append(self.value)

                    # Unknown parameter
                    else:
                        raise RelaxUnknownParamError, self.param[i]


        # All other parameters.
        else:
            # No parameter or a single parameter.
            if self.param == None or type(self.param) == str:
                # List of values.
                if type(self.value) == list or type(self.value) == ArrayType:
                    # Parameter name.
                    for i in xrange(len(self.value)):
                        self.res_params.append(self.param)

                    # Parameter value.
                    self.res_values = self.value

                # Single value.
                else:
                    # Parameter name.
                    self.res_params.append(self.param)

                    # Parameter value.
                    self.res_values.append(self.value)

            # Multiple parameters.
            elif type(self.param) == list:
                # Loop over all parameters.
                for i in xrange(len(self.param)):
                    # Parameter name.
                    self.res_params.append(self.param[i])

                    # Parameter value.
                    if type(self.value) == list or type(self.value) == ArrayType:
                        self.res_values.append(self.value[i])
                    else:
                        self.res_values.append(self.value)

        # Debugging.
        if len(self.diff_params) != len(self.diff_values) or len(self.res_params) != len(self.res_values):
            print "Diff params: " + `self.diff_params`
            print "Diff values: " + `self.diff_values`
            print "Res params: " + `self.res_params`
            print "Res values: " + `self.res_values`
            raise RelaxError, "Bug in the code."


    def write(self, run=None, param=None, file=None, dir=None, force=0, return_value=None):
        """Function for writing data to a file."""

        # Arguments.
        self.run = run
        self.param = param

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Open the file for writing.
        file = self.relax.IO.open_write_file(file, dir, force)

        # Write the data.
        self.write_data(run=run, param=param, file=file, return_value=return_value)

        # Close the file.
        file.close()


    def write_data(self, run=None, param=None, file=None, return_value=None):
        """Function for writing data."""

        # Get the value and error returning function if required.
        if not return_value:
            # Function type.
            self.function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

            # Specific value and error returning function.
            return_value = self.relax.specific_setup.setup('return_value', self.function_type)

        # Write a header line.
        file.write("%-5s%-6s%-30s%-30s\n" % ('Num', 'Name', 'Value', 'Error'))

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Remap the data structure 'self.relax.data.res[run][i]'.
            data = self.relax.data.res[run][i]

            # Get the value and error.
            value, error = return_value(run, i, param)

            # Write the data.
            file.write("%-5i%-6s%-30s%-30s\n" % (data.num, data.name, `value`, `error`))
