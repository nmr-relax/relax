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
import string


class CSAx_data:
    def __init__(self, relax):
        """Class containing functions for csa data."""

        self.relax = relax
        # Global data flag (default to residue specific data).
        self.global_flag = 0


    def add_residue(self, run=None, res_index=None, csa_labels=None, values_ax=None, values_by=None, values_cz=None, sim=0):
        """Function for adding all csa data for a single residue."""

        # Arguments.
        self.run = run
        self.csa_labels = csa_labels

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
        self.relax.data.csa_labels[self.run] = deepcopy(csa_labels)
        self.relax.data.num_csa[self.run] = len(csa_labels)


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
            data.csa_data_ax = values_ax
            data.csa_data_by = values_by
            data.csa_data_cz = values_cz

            # Associated data structures.
            data.csa_labels = csa_labels

            # Remove any data with the ax value None.
            for index,Csa in enumerate(data.csa_data_ax):
                if Csa == None:
                    data.csa_data_ax.pop(index)
                    data.csa_data_by.pop(index)
                    data.csa_data_cz.pop(index)
                    data.csa_labels.pop(index)

#            # Remove any data with the by value of None.
#            for index,by in enumerate(data.csa_data_by):
#                if by == None:
#                    data.csa_data_ax.pop(index)
#                    data.csa_data_by.pop(index)
#                    data.csa_data_cz.pop(index)
#                    data.csa_labels.pop(index)
# 
#            # Remove any data with the cz value of None.
#            for index,cz in enumerate(data.csa_data_cz):
#                if cz == None:
#                    data.csa_data_ax.pop(index)
#                    data.csa_data_by.pop(index)
#                    data.csa_data_cz.pop(index)
#                    data.csa_labels.pop(index)

            # Associated data structures.
            data.num_csa = len(csa_labels)


#        # Simulation data.
#        else:
#            # Create the data structure if necessary.
#            if not hasattr(data, 'relax_sim_data') or type(data.relax_sim_data) != list:
#                data.relax_sim_data = []
#
#            # Append the simulation's relaxation data.
#            data.relax_sim_data.append(values)


    def back_calc(self, run=None, csa_label=None, frq_label=None, frq=None):
        """Function for back calculating relaxation data."""
# 
#        # Arguments.
        self.run = run
        self.csa_label = csa_label
        self.frq_label = frq_label
        self.frq = frq
# 
#        # Test if the run exists.
#        if not self.run in self.relax.data.run_names:
#            raise RelaxNoRunError, self.run
# 
#        # Test if sequence data is loaded.
#        if not self.relax.data.res.has_key(self.run):
#            raise RelaxNoSequenceError, self.run
# 
#        # Test if relaxation data corresponding to 'self.csa_label' and 'self.frq_label' already exists.
#        if self.test_labels(run):
#            raise RelaxRiError, (self.csa_label, self.frq_label)
# 
# 
#        # Global (non-residue specific) data.
#        #####################################
# 
#        # Global data flag.
#        self.global_flag = 1
# 
#        # Initialise the global data if necessary.
#        self.data_init(self.relax.data)
# 
#        # Update the global data.
#        self.update_global_data_structures()
# 
# 
#        # Residue specific data.
#        ########################
# 
#        # Global data flag.
#        self.global_flag = 0
# 
#        # Function type.
#        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]
# 
#        # Specific back-calculate function setup.
#        back_calculate = self.relax.specific_setup.setup('back_calc', function_type)
# 
#        # Loop over the sequence.
#        for i in xrange(len(self.relax.data.res[self.run])):
#            # Remap the data structure 'self.relax.data.res[self.run][i]'.
#            data = self.relax.data.res[self.run][i]
# 
#            # Skip unselected residues.
#            if not data.select:
#                continue
# 
#            # Store a copy of all the data in 'self.relax.data.res[self.run][i]' for backing up if the back_calculation function fails.
#            back_up = deepcopy(data)
# 
#            # Initialise all data structures.
#            self.update_data_structures(data)
# 
#            # Back-calculate the relaxation value.
#            try:
#                value = back_calculate(run=self.run, index=i, csa_label=self.csa_label, frq_label=frq_label, frq=self.frq)
#            except:
#                # Restore the data.
#                self.relax.data.res[self.run][i] = deepcopy(back_up)
#                del back_up
#                raise
# 
#            # Update all data structures.
#            self.update_data_structures(data, value)
# 
# 
    def copy(self, run1=None, run2=None, csa_label=None):
        """Function for copying csa data from run1 to run2."""

        # Arguments.
        self.csa_label = csa_label

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
        if csa_label == None:
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
            # Test if relaxation data corresponding to 'self.csa_label' exists for run1.
            if not self.test_labels(run1):
                raise RelaxNoRiError, (self.csa_label, )

            # Test if relaxation data corresponding to 'self.csa_label' exists for run2.
            if self.test_labels(run2):
                raise RelaxRiError, (self.csa_label, )

            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[run1])):
                # Remap the data structure 'self.relax.data.res[run1][i]'.
                data1 = self.relax.data.res[run1][i]
                data2 = self.relax.data.res[run2][i]

                # Find the index corresponding to 'self.csa_label'.
                index = self.find_index(data1)

                # Catch any problems.
                if index == None:
                    continue

                # Get the value and error from run1.
                value_ax = data1.csa_data_ax[index]
                value_by = data1.csa_data_by[index]
                value_cz = data1.csa_data_cz[index]

                # Update all data structures for run2.
                self.update_data_structures(data2, value_ax, value_by, value_cz)


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
            list_data = [ 'csa_data_ax',
                          'csa_data_by',
                          'csa_data_cz',
			  'cst',
			  'csea',
                          'csa_labels']
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
            zero_data = [ 'num_csa' ]
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

        num_csa:  Number of data points, eg 6.

        num_frq:  Number of field strengths, eg 2.

        csa_labels:  Labels corresponding to the data type, eg ['NOE', 'R1', 'R2', 'NOE', 'R1',
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
            names = [ 'num_csa',
                      'csa_labels' ]

        # Residue specific data names.
        else:
            names = [ 'csa_data_ax',
                      'csa_data_by',
                      'csa_data_cz',
		      'cst',
		      'csea',
                      'num_csa',
                      'csa_labels' ]

        return names


    def delete(self, run=None, csa_label=None, frq_label=None):
        """Function for deleting relaxation data corresponding to csa_label."""

        # Arguments.
        self.run = run
        self.csa_label = csa_label

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if data corresponding to 'self.csa_label' exists.
        if not self.test_labels(run):
            raise RelaxNoRiError, (self.csa_label, )

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Global data flag.
            self.global_flag = 0

            # Find the index corresponding to 'self.csa_label'.
            index = self.find_index(data)

            # Catch any problems.
            if index == None:
                continue

            # Relaxation data and errors.
            data.csa_data_ax.pop(index)
            data.csa_data_by.pop(index)
            data.csa_data_cz.pop(index)

            # Update the number of relaxation data points.
            data.num_csa = data.num_csa - 1

            # Delete csa_label from the data types.
            data.csa_labels.pop(index)

        # Clean up the runs.
        self.relax.generic.runs.eliminate_unused_runs()


    def display(self, run=None, csa_label=None):
        """Function for displaying csa data corresponding to csa_label."""

        # Arguments.
        self.run = run
        self.csa_label = csa_label

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if data corresponding to 'self.csa_label' and exists.
        if not self.test_labels(run):
            raise RelaxNoRiError, (self.csa_label, )

        # Print the data.
        self.relax.generic.value.write_data(self.run, (self.csa_label, ), sys.stdout, return_value=self.return_value)


    def find_index(self, data):
        """Function for finding the index corresponding to self.csa_label."""

        # No data.num_csa data structure.
        if self.global_flag == 1:
            if not data.num_csa.has_key(self.relax):
                return None
        else:
            if not hasattr(data, 'num_csa'):
                return None

        # Initialise.
        index = None

        # Find the index.
        if self.global_flag == 1:
            for j in xrange(data.num_csa[self.run]):
                if self.csa_label == data.csa_labels[self.run][j]:
                    index = j
        else:
            for j in xrange(data.num_csa):
                if self.csa_label == data.csa_labels[j]:
                    index = j

        # Return the index.
        return index


    def read(self, run=None, csa_label=None, file=None, dir=None, file_data=None, num_col=0, name_col=1, data_ax_col=2, data_by_col=3, data_cz_col=4, sep=None):
        """Function for reading CST or CSEA relaxation data."""

        # Arguments.
        self.run = run
        self.csa_label = csa_label

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if relaxation data corresponding to 'self.csa_label' already exists.
        if self.test_labels(run):
            raise RelaxRiError, (self.csa_label, )

        # Minimum number of columns.
        min_col_num = max(num_col, name_col, data_ax_col, data_by_col, data_cz_col)

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

                # Test that the data are numbers.
                try:
                    int(file_data[i][num_col])
                    float(file_data[i][data_ax_col])
                    float(file_data[i][data_by_col])
                    float(file_data[i][data_cz_col])
                except ValueError:
                    raise RelaxError, "The relaxation data is invalid (num=" + file_data[i][num_col] + ", name=" + file_data[i][name_col] + ", data_ax=" + file_data[i][data_ax_col] + ", data_by=" + file_data[i][data_by_col] + ", data_cz=" + file_data[i][data_cz_col] + ")."


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
            value_ax = eval(file_data[i][data_ax_col])
            value_by = eval(file_data[i][data_by_col])
            value_cz = eval(file_data[i][data_cz_col])

            # Skip all rows where the value or error is None.
            if value_ax == None or value_by == None or value_cz == None:
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
            self.update_data_structures(data, value_ax, value_by, value_cz)

            # Add the index to the list.
            index_list.append(index)


    def return_value(self, run, i, data_type):
        """Function for returning the value and error corresponding to 'data_type'."""

        # Arguments.
        self.run = run

        # Unpack the data_type tuple.
        self.csa_label, = data_type

        # Initialise.
        value_ax = None
        value_by = None
        value_cz = None

        # Find the index corresponding to 'self.csa_label' and 'self.frq_label'.
        index = self.find_index(self.relax.data.res[self.run][i])

        # Get the data.
        if index != None:
            value_ax = self.relax.data.res[self.run][i].csa_data_ax[index]
            value_by = self.relax.data.res[self.run][i].csa_data_by[index]
            value_cz = self.relax.data.res[self.run][i].csa_data_cz[index]

        # Return the data.
        return value_ax, value_by, value_cz


    def test_labels(self, run):
        """Test if data corresponding to 'self.csa_label' currently exists."""

        # Initialise.
        exists = 0

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Remap the data structure 'self.relax.data.res[run][i]'.
            data = self.relax.data.res[run][i]

            # No ri data.
            if not hasattr(data, 'num_csa'):
                continue

            # Loop over the relaxation data.
            for j in xrange(data.num_csa):
                # Test if the relaxation data matches 'self.csa_label'.
                if self.csa_label == data.csa_labels[j]:
                    exists = 1

        return exists


    def update_data_structures(self, data=None, value_ax=None, value_by=None, value_cz=None):
        """Function for updating all csa data structures."""

        # Initialise the relaxation data structures (if needed).
        self.data_init(data)

        # Find the index corresponding to 'self.csa_label'.
        index = self.find_index(data)

	# Creating CST or CSEA data
	setattr(data, string.lower(self.csa_label), [value_ax, value_by, value_cz])
	
        # Append empty data.
        if index == None:
            data.csa_data_ax.append(None)
            data.csa_data_by.append(None)
            data.csa_data_cz.append(None)
            data.csa_labels.append(None)

        # Set the index value.
        if index == None:
            i = len(data.csa_data_ax) - 1
        else:
            i = index

        # Relaxation data and errors.
        data.csa_data_ax[i] = value_ax
        data.csa_data_by[i] = value_by
        data.csa_data_cz[i] = value_cz

        # Update the number of relaxation data points.
        if index == None:
            data.num_csa = data.num_csa + 1

        # Add csa_label to the data types.
        data.csa_labels[i] = self.csa_label

    def update_global_data_structures(self):
        """Function for updating all csa data structures."""

        # Initialise the relaxation data structures (if needed).
        self.data_init(self.relax.data)

        # The index.
        i = len(self.relax.data.csa_labels[self.run]) - 1

        # Update the number of relaxation data points.
        self.relax.data.num_csa[self.run] = self.relax.data.num_csa[self.run] + 1

        # Add csa_label to the data types.
        self.relax.data.csa_labels[self.run].append(self.csa_label,)


    def write(self, run=None, csa_label=None, file=None, dir=None, force=0):
        """Function for writing csa data."""

        # Arguments.
        self.run = run
        self.csa_label = csa_label

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if data corresponding to 'self.csa_label'.
        if not self.test_labels(run):
            raise RelaxNoRiError, (self.csa_label, )

        # Create the file name if none is given.
        if file == None:
            file = self.csa_label + ".out"

        # Write the data.
        self.relax.generic.value.write(run=self.run, param=(self.csa_label, ), file=file, dir=dir, force=force, return_value=self.return_value)
