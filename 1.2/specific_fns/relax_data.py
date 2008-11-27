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

from copy import deepcopy
import sys


class Rx_data:
    def __init__(self, relax):
        """Class containing functions for relaxation data."""

        self.relax = relax

        # Global data flag (default to residue specific data).
        self.global_flag = 0


    def add_residue(self, run=None, res_index=None, ri_labels=None, remap_table=None, frq_labels=None, frq=None, values=None, errors=None, sim=0):
        """Function for adding all relaxation data for a single residue."""

        # Arguments.
        self.run = run
        self.ri_labels = ri_labels
        self.remap_table = remap_table
        self.frq_labels = frq_labels
        self.frq = frq

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run


        # Global (non-residue specific) data.
        #####################################

        # Global data flag.
        self.global_flag = 1

        # Initialise the global data if necessary.
        self.data_init(self.relax.data)

        # Add the data structures.
        self.relax.data.ri_labels[self.run] = deepcopy(ri_labels)
        self.relax.data.remap_table[self.run] = deepcopy(remap_table)
        self.relax.data.frq_labels[self.run] = deepcopy(frq_labels)
        self.relax.data.frq[self.run] = deepcopy(frq)
        self.relax.data.num_ri[self.run] = len(ri_labels)
        self.relax.data.num_frq[self.run] = len(frq)


        # Residue specific data.
        ########################

        # Global data flag.
        self.global_flag = 0

        # Remap the data structure 'self.relax.data.res[self.run][res_index]'.
        data = self.relax.data.res[self.run][res_index]

        # Relaxation data.
        if not sim:
            # Initialise the relaxation data structures (if needed).
            self.data_init(data)

            # Relaxation data and errors.
            data.relax_data = values
            data.relax_error = errors

            # Associated data structures.
            data.ri_labels = ri_labels
            data.remap_table = remap_table

            # Remove any data with the value None.
            for index,Ri in enumerate(data.relax_data):
                if Ri == None:
                    data.relax_data.pop(index)
                    data.relax_error.pop(index)
                    data.ri_labels.pop(index)
                    data.remap_table.pop(index)

            # Remove any data with error of None.
            for index,error in enumerate(data.relax_error):
                if error == None:
                    data.relax_data.pop(index)
                    data.relax_error.pop(index)
                    data.ri_labels.pop(index)
                    data.remap_table.pop(index)

            # Associated data structures.
            data.frq_labels = frq_labels
            data.frq = frq
            data.num_ri = len(ri_labels)
            data.num_frq = len(frq)

            # Create an array of None for the NOE R1 translation table.
            for i in xrange(data.num_ri):
                data.noe_r1_table.append(None)

            # Update the NOE R1 translation table.
            for i in xrange(data.num_ri):
                # If the data corresponds to 'NOE', try to find if the corresponding R1 data.
                if data.ri_labels[i] == 'NOE':
                    for j in xrange(data.num_ri):
                        if data.ri_labels[j] == 'R1' and data.frq_labels[data.remap_table[i]] == data.frq_labels[data.remap_table[j]]:
                            data.noe_r1_table[i] = j

                # If the data corresponds to 'R1', try to find if the corresponding NOE data.
                if data.ri_labels[i] == 'R1':
                    for j in xrange(data.num_ri):
                        if data.ri_labels[j] == 'NOE' and data.frq_labels[data.remap_table[i]] == data.frq_labels[data.remap_table[j]]:
                            data.noe_r1_table[j] = i


        # Simulation data.
        else:
            # Create the data structure if necessary.
            if not hasattr(data, 'relax_sim_data') or type(data.relax_sim_data) != list:
                data.relax_sim_data = []

            # Append the simulation's relaxation data.
            data.relax_sim_data.append(values)


    def back_calc(self, run=None, ri_label=None, frq_label=None, frq=None):
        """Function for back calculating relaxation data."""

        # Arguments.
        self.run = run
        self.ri_label = ri_label
        self.frq_label = frq_label
        self.frq = frq

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if relaxation data corresponding to 'self.ri_label' and 'self.frq_label' already exists.
        if self.test_labels(run):
            raise RelaxRiError, (self.ri_label, self.frq_label)


        # Global (non-residue specific) data.
        #####################################

        # Global data flag.
        self.global_flag = 1

        # Initialise the global data if necessary.
        self.data_init(self.relax.data)

        # Update the global data.
        self.update_global_data_structures()


        # Residue specific data.
        ########################

        # Global data flag.
        self.global_flag = 0

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]

        # Specific back-calculate function setup.
        back_calculate = self.relax.specific_setup.setup('back_calc', function_type)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # Store a copy of all the data in 'self.relax.data.res[self.run][i]' for backing up if the back_calculation function fails.
            back_up = deepcopy(data)

            # Initialise all data structures.
            self.update_data_structures(data)

            # Back-calculate the relaxation value.
            try:
                value = back_calculate(run=self.run, index=i, ri_label=self.ri_label, frq_label=frq_label, frq=self.frq)
            except:
                # Restore the data.
                self.relax.data.res[self.run][i] = deepcopy(back_up)
                del back_up
                raise

            # Update all data structures.
            self.update_data_structures(data, value)


    def copy(self, run1=None, run2=None, ri_label=None, frq_label=None):
        """Function for copying relaxation data from run1 to run2."""

        # Arguments.
        self.ri_label = ri_label
        self.frq_label = frq_label

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

        # Copy all data.
        if ri_label == None and frq_label == None:
            # Get all data structure names.
            names = self.data_names()

            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[run1])):
                # Remap the data structure 'self.relax.data.res[run1][i]'.
                data1 = self.relax.data.res[run1][i]
                data2 = self.relax.data.res[run2][i]

                # Loop through the data structure names.
                for name in names:
                    # Skip the data structure if it does not exist.
                    if not hasattr(data1, name):
                        continue

                    # Copy the data structure.
                    setattr(data2, name, deepcopy(getattr(data1, name)))

        # Copy a specific data set.
        else:
            # Test if relaxation data corresponding to 'self.ri_label' and 'self.frq_label' exists for run1.
            if not self.test_labels(run1):
                raise RelaxNoRiError, (self.ri_label, self.frq_label)

            # Test if relaxation data corresponding to 'self.ri_label' and 'self.frq_label' exists for run2.
            if self.test_labels(run2):
                raise RelaxRiError, (self.ri_label, self.frq_label)

            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[run1])):
                # Remap the data structure 'self.relax.data.res[run1][i]'.
                data1 = self.relax.data.res[run1][i]
                data2 = self.relax.data.res[run2][i]

                # Find the index corresponding to 'self.ri_label' and 'self.frq_label'.
                index = self.find_index(data1)

                # Catch any problems.
                if index == None:
                    continue

                # Get the value and error from run1.
                value = data1.relax_data[index]
                error = data1.relax_error[index]

                # Update all data structures for run2.
                self.update_data_structures(data2, value, error)


    def data_init(self, data):
        """Function for initialising the data structures."""

        # Get the data names.
        data_names = self.data_names()

        # Loop over the data structure names.
        for name in data_names:
            # Global data.
            if self.global_flag == 1:
                # Add the global data structure if it does not exist.
                if not hasattr(data, name):
                    setattr(data, name, {})

            # Data structures which are initially empty arrays.
            list_data = [ 'relax_data',
                          'relax_error',
                          'ri_labels',
                          'remap_table',
                          'noe_r1_table',
                          'frq_labels',
                          'frq' ]
            if name in list_data:
                # Global data.
                if self.global_flag == 1:
                    # Get the object.
                    object = getattr(data, name)

                    # Add the data if the key is missing.
                    if not object.has_key(self.run):
                        object[self.run] = []

                # Residue specific data.
                else:
                    # If the name is not in 'data', add it.
                    if not hasattr(data, name):
                        setattr(data, name, [])

            # Data structures which are initially zero.
            zero_data = [ 'num_ri', 'num_frq' ]
            if name in zero_data:
                # Global data.
                if self.global_flag == 1:
                    # Get the object.
                    object = getattr(data, name)

                    # Add the data if the key is missing.
                    if not object.has_key(self.run):
                        object[self.run] = 0

                # Residue specific data.
                else:
                    # If the name is not in 'data', add it.
                    if not hasattr(data, name):
                        setattr(data, name, 0)


    def data_names(self):
        """Function for returning a list of names of data structures associated with relax_data.

        Description
        ~~~~~~~~~~~

        The names are as follows:

        relax_data:  Relaxation data.

        relax_error:  Relaxation error.

        num_ri:  Number of data points, eg 6.

        num_frq:  Number of field strengths, eg 2.

        ri_labels:  Labels corresponding to the data type, eg ['NOE', 'R1', 'R2', 'NOE', 'R1',
        'R2'].

        remap_table:  A translation table to map relaxation data points to their frequencies, eg [0,
        0, 0, 1, 1, 1].

        noe_r1_table:  A translation table to direct the NOE data points to the R1 data points.
        This is used to speed up calculations by avoiding the recalculation of R1 values.  eg [None,
        None, 0, None, None, 3]

        frq_labels:  NMR frequency labels, eg ['600', '500']

        frq:  NMR frequencies in Hz, eg [600.0 * 1e6, 500.0 * 1e6]
        """

        # Global data names.
        if self.global_flag == 1:
            names = [ 'num_ri',
                      'num_frq',
                      'ri_labels',
                      'remap_table',
                      'noe_r1_table',
                      'frq_labels',
                      'frq' ]

        # Residue specific data names.
        else:
            names = [ 'relax_data',
                      'relax_error',
                      'num_ri',
                      'num_frq',
                      'ri_labels',
                      'remap_table',
                      'noe_r1_table',
                      'frq_labels',
                      'frq' ]

        return names


    def delete(self, run=None, ri_label=None, frq_label=None):
        """Function for deleting relaxation data corresponding to ri_label and frq_label."""

        # Arguments.
        self.run = run
        self.ri_label = ri_label
        self.frq_label = frq_label

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if data corresponding to 'self.ri_label' and 'self.frq_label' exists.
        if not self.test_labels(run):
            raise RelaxNoRiError, (self.ri_label, self.frq_label)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Global data flag.
            self.global_flag = 0

            # Find the index corresponding to 'self.ri_label' and 'self.frq_label'.
            index = self.find_index(data)

            # Catch any problems.
            if index == None:
                continue

            # Relaxation data and errors.
            data.relax_data.pop(index)
            data.relax_error.pop(index)

            # Update the number of relaxation data points.
            data.num_ri = data.num_ri - 1

            # Delete ri_label from the data types.
            data.ri_labels.pop(index)

            # Update the remap table.
            data.remap_table.pop(index)

            # Find if there is other data corresponding to 'self.frq_label'
            frq_index = data.frq_labels.index(self.frq_label)
            if not frq_index in data.remap_table:
                # Update the number of frequencies.
                data.num_frq = data.num_frq - 1

                # Update the frequency labels.
                data.frq_labels.pop(frq_index)

                # Update the frequency array.
                data.frq.pop(frq_index)

            # Update the NOE R1 translation table.
            data.noe_r1_table.pop(index)
            for j in xrange(data.num_ri):
                if data.noe_r1_table[j] > index:
                    data.noe_r1_table[j] = data.noe_r1_table[j] - 1

        # Clean up the runs.
        self.relax.generic.runs.eliminate_unused_runs()


    def display(self, run=None, ri_label=None, frq_label=None):
        """Function for displaying relaxation data corresponding to ri_label and frq_label."""

        # Arguments.
        self.run = run
        self.ri_label = ri_label
        self.frq_label = frq_label

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if data corresponding to 'self.ri_label' and 'self.frq_label' exists.
        if not self.test_labels(run):
            raise RelaxNoRiError, (self.ri_label, self.frq_label)

        # Print the data.
        self.relax.generic.value.write_data(run=self.run, param=(self.ri_label, self.frq_label), file=sys.stdout, return_value=self.return_value)


    def find_index(self, data):
        """Function for finding the index corresponding to self.ri_label and self.frq_label."""

        # No data.num_ri data structure.
        if self.global_flag == 1:
            if not data.num_ri.has_key(self.relax):
                return None
        else:
            if not hasattr(data, 'num_ri'):
                return None

        # Initialise.
        index = None

        # Find the index.
        if self.global_flag == 1:
            for j in xrange(data.num_ri[self.run]):
                if self.ri_label == data.ri_labels[self.run][j] and self.frq_label == data.frq_labels[self.run][data.remap_table[self.run][j]]:
                    index = j
        else:
            for j in xrange(data.num_ri):
                if self.ri_label == data.ri_labels[j] and self.frq_label == data.frq_labels[data.remap_table[j]]:
                    index = j

        # Return the index.
        return index


    def read(self, run=None, ri_label=None, frq_label=None, frq=None, file=None, dir=None, file_data=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
        """Function for reading R1, R2, or NOE relaxation data."""

        # Arguments.
        self.run = run
        self.ri_label = ri_label
        self.frq_label = frq_label
        self.frq = frq

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if relaxation data corresponding to 'self.ri_label' and 'self.frq_label' already exists.
        if self.test_labels(run):
            raise RelaxRiError, (self.ri_label, self.frq_label)

        # Minimum number of columns.
        min_col_num = max(num_col, name_col, data_col, error_col)

        # Extract the data from the file.
        if not file_data:
            # Extract.
            file_data = self.relax.IO.extract_data(file, dir)

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

            # Test the validity of the relaxation data.
            for i in xrange(len(file_data)):
                # Skip missing data.
                if len(file_data[i]) <= min_col_num:
                    continue
                elif file_data[i][data_col] == 'None' or file_data[i][error_col] == 'None':
                    continue

                # Test that the data are numbers.
                try:
                    int(file_data[i][num_col])
                    float(file_data[i][data_col])
                    float(file_data[i][error_col])
                except ValueError:
                    raise RelaxError, "The relaxation data is invalid (num=" + file_data[i][num_col] + ", name=" + file_data[i][name_col] + ", data=" + file_data[i][data_col] + ", error=" + file_data[i][error_col] + ")."


        # Global (non-residue specific) data.
        #####################################

        # Global data flag.
        self.global_flag = 1

        # Initialise the global data if necessary.
        self.data_init(self.relax.data)

        # Update the global data.
        self.update_global_data_structures()


        # Residue specific data.
        ########################

        # Global data flag.
        self.global_flag = 0

        # Store the indecies for which relaxation data has been added.
        index_list = []

        # Loop over the relaxation data.
        for i in xrange(len(file_data)):
            # Skip missing data.
            if len(file_data[i]) <= min_col_num:
                continue

            # Convert the data.
            res_num = int(file_data[i][num_col])
            res_name = file_data[i][name_col]
            value = eval(file_data[i][data_col])
            error = eval(file_data[i][error_col])

            # Skip all rows where the value or error is None.
            if value == None or error == None:
                continue

            # Find the index of self.relax.data.res[self.run] which corresponds to the relaxation data set i.
            index = None
            for j in xrange(len(self.relax.data.res[self.run])):
                if self.relax.data.res[self.run][j].num == res_num and self.relax.data.res[self.run][j].name == res_name:
                    index = j
                    break
            if index == None:
                raise RelaxNoResError, (res_num, res_name)

            # Remap the data structure 'self.relax.data.res[self.run][index]'.
            data = self.relax.data.res[self.run][index]

            # Update all data structures.
            self.update_data_structures(data, value, error)

            # Add the index to the list.
            index_list.append(index)


    def return_value(self, run, i, data_type):
        """Function for returning the value and error corresponding to 'data_type'."""

        # Arguments.
        self.run = run

        # Unpack the data_type tuple.
        self.ri_label, self.frq_label = data_type

        # Initialise.
        value = None
        error = None

        # Find the index corresponding to 'self.ri_label' and 'self.frq_label'.
        index = self.find_index(self.relax.data.res[self.run][i])

        # Get the data.
        if index != None:
            value = self.relax.data.res[self.run][i].relax_data[index]
            error = self.relax.data.res[self.run][i].relax_error[index]

        # Return the data.
        return value, error


    def test_labels(self, run):
        """Test if data corresponding to 'self.ri_label' and 'self.frq_label' currently exists."""

        # Initialise.
        exists = 0

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Remap the data structure 'self.relax.data.res[run][i]'.
            data = self.relax.data.res[run][i]

            # No ri data.
            if not hasattr(data, 'num_ri'):
                continue

            # Loop over the relaxation data.
            for j in xrange(data.num_ri):
                # Test if the relaxation data matches 'self.ri_label' and 'self.frq_label'.
                if self.ri_label == data.ri_labels[j] and self.frq_label == data.frq_labels[data.remap_table[j]]:
                    exists = 1

        return exists


    def update_data_structures(self, data=None, value=None, error=None):
        """Function for updating all relaxation data structures."""

        # Initialise the relaxation data structures (if needed).
        self.data_init(data)

        # Find the index corresponding to 'self.ri_label' and 'self.frq_label'.
        index = self.find_index(data)

        # Append empty data.
        if index == None:
            data.relax_data.append(None)
            data.relax_error.append(None)
            data.ri_labels.append(None)
            data.remap_table.append(None)
            data.noe_r1_table.append(None)

        # Set the index value.
        if index == None:
            i = len(data.relax_data) - 1
        else:
            i = index

        # Relaxation data and errors.
        data.relax_data[i] = value
        data.relax_error[i] = error

        # Update the number of relaxation data points.
        if index == None:
            data.num_ri = data.num_ri + 1

        # Add ri_label to the data types.
        data.ri_labels[i] = self.ri_label

        # Find if the frequency self.frq has already been loaded.
        remap = len(data.frq)
        flag = 0
        for j in xrange(len(data.frq)):
            if self.frq == data.frq[j]:
                remap = j
                flag = 1

        # Update the remap table.
        data.remap_table[i] = remap

        # Update the data structures which have a length equal to the number of field strengths.
        if not flag:
            # Update the number of frequencies.
            if index == None:
                data.num_frq = data.num_frq + 1

            # Update the frequency labels.
            data.frq_labels.append(self.frq_label)

            # Update the frequency array.
            data.frq.append(self.frq)

        # Update the NOE R1 translation table.
        # If the data corresponds to 'NOE', try to find if the corresponding R1 data.
        if self.ri_label == 'NOE':
            for j in xrange(data.num_ri):
                if data.ri_labels[j] == 'R1' and self.frq_label == data.frq_labels[data.remap_table[j]]:
                    data.noe_r1_table[data.num_ri - 1] = j

        # Update the NOE R1 translation table.
        # If the data corresponds to 'R1', try to find if the corresponding NOE data.
        if self.ri_label == 'R1':
            for j in xrange(data.num_ri):
                if data.ri_labels[j] == 'NOE' and self.frq_label == data.frq_labels[data.remap_table[j]]:
                    data.noe_r1_table[j] = data.num_ri - 1


    def update_global_data_structures(self):
        """Function for updating all relaxation data structures."""

        # Initialise the relaxation data structures (if needed).
        self.data_init(self.relax.data)

        # The index.
        i = len(self.relax.data.ri_labels[self.run]) - 1

        # Update the number of relaxation data points.
        self.relax.data.num_ri[self.run] = self.relax.data.num_ri[self.run] + 1

        # Add ri_label to the data types.
        self.relax.data.ri_labels[self.run].append(self.ri_label)

        # Find if the frequency self.frq has already been loaded.
        remap = len(self.relax.data.frq[self.run])
        flag = 0
        for j in xrange(len(self.relax.data.frq[self.run])):
            if self.frq == self.relax.data.frq[self.run][j]:
                remap = j
                flag = 1

        # Update the remap table.
        self.relax.data.remap_table[self.run].append(remap)

        # Update the data structures which have a length equal to the number of field strengths.
        if not flag:
            # Update the number of frequencies.
            self.relax.data.num_frq[self.run] = self.relax.data.num_frq[self.run] + 1

            # Update the frequency labels.
            self.relax.data.frq_labels[self.run].append(self.frq_label)

            # Update the frequency array.
            self.relax.data.frq[self.run].append(self.frq)

        # Update the NOE R1 translation table.
        self.relax.data.noe_r1_table[self.run].append(None)

        # If the data corresponds to 'NOE', try to find if the corresponding R1 data.
        if self.ri_label == 'NOE':
            for j in xrange(self.relax.data.num_ri[self.run]):
                if self.relax.data.ri_labels[self.run][j] == 'R1' and self.frq_label == self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][j]]:
                    self.relax.data.noe_r1_table[self.run][self.relax.data.num_ri[self.run] - 1] = j

        # Update the NOE R1 translation table.
        # If the data corresponds to 'R1', try to find if the corresponding NOE data.
        if self.ri_label == 'R1':
            for j in xrange(self.relax.data.num_ri[self.run]):
                if self.relax.data.ri_labels[self.run][j] == 'NOE' and self.frq_label == self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][j]]:
                    self.relax.data.noe_r1_table[self.run][j] = self.relax.data.num_ri[self.run] - 1


    def write(self, run=None, ri_label=None, frq_label=None, file=None, dir=None, force=0):
        """Function for writing relaxation data."""

        # Arguments.
        self.run = run
        self.ri_label = ri_label
        self.frq_label = frq_label

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if data corresponding to 'self.ri_label' and 'self.frq_label' exists.
        if not self.test_labels(run):
            raise RelaxNoRiError, (self.ri_label, self.frq_label)

        # Create the file name if none is given.
        if file == None:
            file = self.ri_label + "." + self.frq_label + ".out"

        # Write the data.
        self.relax.generic.value.write(run=self.run, param=(self.ri_label, self.frq_label), file=file, dir=dir, force=force, return_value=self.return_value)
