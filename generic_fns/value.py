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


from re import compile, match
import sys


class Value:
    def __init__(self, relax):
        """Class containing functions for the setting up of data structures."""

        self.relax = relax


    def copy(self, run1=None, run2=None, data_type=None):
        """Function for copying residue specific data values from run1 to run2."""

        # Arguments.
        self.data_type = data_type

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
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run1)]

        # Specific value and error returning function.
        return_value = self.relax.specific_setup.setup('return_value', function_type)

        # Specific set function.
        set = self.relax.specific_setup.setup('set', function_type)

        # Test if the data exists for run2.
        for i in xrange(len(self.relax.data.res[run2])):
            # Get the value and error for run2.
            value, error = return_value(run2, i, data_type)

            # Data exists.
            if value != None or error != None:
                raise RelaxValueError, (data_type, run2)

        # Copy the values.
        for i in xrange(len(self.relax.data.res[run1])):
            # Get the value and error for run1.
            value, error = return_value(run1, i, data_type)

            # Set the values of run2.
            set(run=run2, value=value, error=error, data_type=data_type, index=i)

            # Reset the minimisation statistics.
            self.reset_min_stats(run2, i)


    def display(self, run=None, data_type=None):
        """Function for displaying residue specific data values."""

        # Arguments.
        self.run = run
        self.data_type = data_type

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Print the data.
        self.write_data(run, data_type, sys.stdout)


    def read(self, run=None, data_type=None, file=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None, header_lines=None):
        """Function for reading residue specific data values from a file."""

        # Arguments.
        self.run = run
        self.data_type = data_type

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]

        # Specific value and error returning function.
        return_value = self.relax.specific_setup.setup('return_value', function_type)

        # Specific set function.
        set = self.relax.specific_setup.setup('set', function_type)

        # Test data corresponding to data_type already exists.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Get the value and error.
            value, error = return_value(self.run, i, data_type)

            # Data exists.
            if value != None or error != None:
                raise RelaxValueError, (data_type, self.run)

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(file)

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip the data.
        file_data = self.relax.file_ops.strip(file_data)

        # Test the validity of the data.
        for i in xrange(len(file_data)):
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
                    raise RelaxError, "The data is invalid (num=" + file_data[i][num_col] + ", name=" + file_data[i][name_col] + ", data=" + file_data[i][data_col] + ", error=" + file_data[i][error_col] + ")."
                else:
                    raise RelaxError, "The data is invalid (num=" + file_data[i][num_col] + ", name=" + file_data[i][name_col] + ", data=" + file_data[i][data_col] + ")."

        # Loop over the data.
        for i in xrange(len(file_data)):
            # Residue number.
            res_num = int(file_data[i][num_col])

            # Residue name.
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
                if self.relax.data.res[self.run][j].num == res_num and self.relax.data.res[self.run][j].name == res_name:
                    index = j
                    break
            if index == None:
                raise RelaxNoResError, (res_num, res_name)

            # Set the values of run2.
            set(run=run, value=value, error=error, data_type=data_type, index=i)

            # Reset the minimisation statistics.
            self.reset_min_stats(self.run, i)


    def set(self, run=None, value=None, data_type=None, res_num=None, res_name=None, force=0):
        """Function for setting residue specific data values."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Test if the residue number is a valid regular expression.
        if type(res_num) == str:
            try:
                compile(res_num)
            except:
                raise RelaxRegExpError, ('residue number', res_num)

        # Test if the residue name is a valid regular expression.
        if res_name:
            try:
                compile(res_name)
            except:
                raise RelaxRegExpError, ('residue name', res_name)

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific value and error returning function.
        return_value = self.relax.specific_setup.setup('return_value', function_type)

        # Specific set function.
        set = self.relax.specific_setup.setup('set', function_type)

        # Test data corresponding to data_type already exists.
        if data_type and not force:
            # Create an array with all data types.
            if type(data_type) == str:
                data_type_array = [data_type]
            else:
                data_type_array = data_type

            # Test if the values already exist.
            for i in xrange(len(self.relax.data.res[run])):
                # Skip unselected residues.
                if not self.relax.data.res[run][i].select:
                    continue

                # If 'res_num' is not None, skip the residue if there is no match.
                if type(res_num) == int and not self.relax.data.res[run][i].num == res_num:
                    continue
                elif type(res_num) == str and not match(res_num, `self.relax.data.res[run][i].num`):
                    continue

                # If 'res_name' is not None, skip the residue if there is no match.
                if res_name != None and not match(res_name, self.relax.data.res[run][i].name):
                    continue

                # Loop over the data types.
                for name in data_type_array:
                    # Get the value and error.
                    temp_value, temp_error = return_value(run, i, name)

                    # Data exists.
                    if temp_value != None or temp_error != None:
                        raise RelaxValueError, (name, run)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Residue skipping.
            ###################

            # Skip unselected residues.
            if not self.relax.data.res[run][i].select:
                continue

            # If 'res_num' is not None, skip the residue if there is no match.
            if type(res_num) == int and not self.relax.data.res[run][i].num == res_num:
                continue
            elif type(res_num) == str and not match(res_num, `self.relax.data.res[run][i].num`):
                continue

            # If 'res_name' is not None, skip the residue if there is no match.
            if res_name != None and not match(res_name, self.relax.data.res[run][i].name):
                continue


            # Go to the specific code.
            ##########################

            # Setting the model parameters prior to minimisation.
            if data_type == None:
                set(run=run, value=value, error=None, data_type=data_type, index=i)

            # Single data type.
            if type(data_type) == str:
                set(run=run, value=value, error=None, data_type=data_type, index=i)

            # Multiple data type.
            if type(data_type) == list:
                for j in xrange(len(data_type)):
                    # Get the value of the data type 'j'.
                    if type(value) == None:
                        val = None
                    elif type(value) == list:
                        val = value[j]
                    else:
                        val = value

                    # Set the value of data type 'j' to 'val'.
                    set(run=run, value=val, error=None, data_type=data_type[j], index=i)

            # Reset the minimisation statistics.
            self.reset_min_stats(run, i)


    def reset_min_stats(self, run, i):
        """Reset the minimisation statistics."""

        # Chi-squared.
        if hasattr(self.relax.data.res[run][i], 'chi2'):
            self.relax.data.res[run][i].chi2 = None

        # Iteration count.
        if hasattr(self.relax.data.res[run][i], 'iter'):
            self.relax.data.res[run][i].iter = None

        # Function count.
        if hasattr(self.relax.data.res[run][i], 'f_count'):
            self.relax.data.res[run][i].f_count = None

        # Gradient count.
        if hasattr(self.relax.data.res[run][i], 'g_count'):
            self.relax.data.res[run][i].g_count = None

        # Hessian count.
        if hasattr(self.relax.data.res[run][i], 'h_count'):
            self.relax.data.res[run][i].h_count = None

        # Warning.
        if hasattr(self.relax.data.res[run][i], 'warning'):
            self.relax.data.res[run][i].warning = None


    def write(self, run=None, data_type=None, file=None, dir=None, force=0):
        """Function for writing data to a file."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Open the file for writing.
        relax_file = self.relax.file_ops.open_write_file(file, dir, force)

        # Write the data.
        self.write_data(run, data_type, relax_file)

        # Close the file.
        relax_file.close()


    def write_data(self, run, data_type, file, return_value=None):
        """Function for writing data."""

        # Get the value and error returning function if required.
        if not return_value:
            # Function type.
            function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

            # Specific value and error returning function.
            return_value = self.relax.specific_setup.setup('return_value', function_type)

        # Test if the data exists.
        for i in xrange(len(self.relax.data.res[run])):
            value, error = return_value(run, i, data_type)

        # Write a header line.
        file.write("%-5s%-6s%-30s%-30s\n" % ('Num', 'Name', 'Value', 'Error'))

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Remap the data structure 'self.relax.data.res[run][i]'.
            data = self.relax.data.res[run][i]

            # Get the value and error.
            value, error = return_value(run, i, data_type)

            # Write the data.
            file.write("%-5i%-6s%-30s%-30s\n" % (data.num, data.name, `value`, `error`))
