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

import sys


class Rx_data:
    def __init__(self, relax):
        """Class containing functions for relaxation data."""

        self.relax = relax


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
            raise RelaxNoSequenceError

        # Test if relaxation data corresponding to 'self.ri_label' and 'self.frq_label' already exists.
        if self.test_labels():
            raise RelaxRiError, (self.ri_label, self.frq_label)

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]

        # Specific back-calculate function setup.
        back_calculate = self.relax.specific_setup.setup('back_calc', function_type)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Back-calculate the relaxation value.
            value = back_calculate(run=self.run, index=i, ri_label=self.ri_label, frq_label=frq_label, frq=self.frq)

            # Update all data structures.
            self.update_data_structures(data, value)


    def data_init(self, name):
        """Function for returning an initial data structure corresponding to 'name'."""

        # Empty arrays.
        list_data = [ 'relax_data',
                      'relax_error',
                      'ri_labels',
                      'remap_table',
                      'noe_r1_table',
                      'frq_labels',
                      'frq' ]
        if name in list_data:
            return []

        # Zero.
        zero_data = [ 'num_ri', 'num_frq' ]
        if name in zero_data:
            return 0


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
            raise RelaxNoSequenceError

        # Test if data corresponding to 'self.ri_label' and 'self.frq_label' exists.
        if not self.test_labels():
            raise RelaxNoRiError, (self.ri_label, self.frq_label)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Find the index corresponding to 'self.ri_label' and 'self.frq_label'.
            index = self.find_index(data)

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
            raise RelaxNoSequenceError

        # Test if data corresponding to 'self.ri_label' and 'self.frq_label' exists.
        if not self.test_labels():
            raise RelaxNoRiError, (self.ri_label, self.frq_label)

        # Print the data.
        self.write_data(sys.stdout)


    def find_index(self, data):
        """Function for finding the index corresponding to self.ri_label and self.frq_label."""

        # Find the index.
        index = None
        for j in xrange(data.num_ri):
            if self.ri_label == data.ri_labels[j] and self.frq_label == data.frq_labels[data.remap_table[j]]:
                index = j

        # Return the index.
        return index


    def initialise_relax_data(self, data):
        """Function for initialisation of relaxation data structures.

        Only data structures which do not exist are created.
        """

        # Get the data names.
        data_names = self.data_names()

        # Loop over the names.
        for name in data_names:
            # If the name is not in 'data', add it.
            if not hasattr(data, name):
                setattr(data, name, self.data_init(name))


    def read(self, run=None, ri_label=None, frq_label=None, frq=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None, header_lines=None):
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
            raise RelaxNoSequenceError

        # Test if relaxation data corresponding to 'self.ri_label' and 'self.frq_label' already exists.
        if self.test_labels():
            raise RelaxRiError, (self.ri_label, self.frq_label)

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(file_name)

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip the data.
        file_data = self.relax.file_ops.strip(file_data)

        # Test the validity of the relaxation data.
        for i in xrange(len(file_data)):
            try:
                int(file_data[i][num_col])
                float(file_data[i][data_col])
                float(file_data[i][error_col])
            except ValueError:
                raise RelaxError, "The relaxation data is invalid (num=" + file_data[i][num_col] + ", name=" + file_data[i][name_col] + ", data=" + file_data[i][data_col] + ", error=" + file_data[i][error_col] + ")."

        # Loop over the relaxation data.
        for i in xrange(len(file_data)):
            # Get the data.
            res_num = int(file_data[i][num_col])
            res_name = file_data[i][name_col]
            value = float(file_data[i][data_col])
            error = float(file_data[i][error_col])

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


    def test_labels(self):
        """Test if data corresponding to 'self.ri_label' and 'self.frq_label' currently exists."""

        # Initialise.
        exists = 0

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

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
        self.initialise_relax_data(data)

        # Relaxation data and errors.
        data.relax_data.append(value)
        data.relax_error.append(error)

        # Update the number of relaxation data points.
        data.num_ri = data.num_ri + 1

        # Add ri_label to the data types.
        data.ri_labels.append(self.ri_label)

        # Find if the frequency self.frq has already been loaded.
        remap = len(data.frq)
        flag = 0
        for i in xrange(len(data.frq)):
            if self.frq == data.frq[i]:
                remap = i
                flag = 1

        # Update the remap table.
        data.remap_table.append(remap)

        # Update the data structures which have a length equal to the number of field strengths.
        if not flag:
            # Update the number of frequencies.
            data.num_frq = data.num_frq + 1

            # Update the frequency labels.
            data.frq_labels.append(self.frq_label)

            # Update the frequency array.
            data.frq.append(self.frq)

        # Update the NOE R1 translation table.
        data.noe_r1_table.append(None)

        # If the data corresponds to 'NOE', try to find if the corresponding R1 data.
        if self.ri_label == 'NOE':
            for i in xrange(data.num_ri):
                if data.ri_labels[i] == 'R1' and self.frq_label == data.frq_labels[data.remap_table[i]]:
                    data.noe_r1_table[data.num_ri - 1] = i

        # If the data corresponds to 'R1', try to find if the corresponding NOE data.
        if self.ri_label == 'R1':
            for i in xrange(data.num_ri):
                if data.ri_labels[i] == 'NOE' and self.frq_label == data.frq_labels[data.remap_table[i]]:
                    data.noe_r1_table[i] = data.num_ri - 1


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
            raise RelaxNoSequenceError

        # Test if data corresponding to 'self.ri_label' and 'self.frq_label' exists.
        if not self.test_labels():
            raise RelaxNoRiError, (self.ri_label, self.frq_label)

        # Create the file name if none is given.
        if file == None:
            file = self.ri_label + "." + self.frq_label + ".out"

        # Open the file for writing.
        relax_file = self.relax.file_ops.open_write_file(file, dir, force)

        # Write the data.
        self.write_data(relax_file)

        # Close the file.
        relax_file.close()


    def write_data(self, file):
        """Function for writing the relaxation data."""

        # Write a header line.
        file.write("%-5s%-6s%-30s%-30s\n" % ('Num', 'Name', 'Value', 'Error'))

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Write the residue number.
            file.write("%-5i" % data.num)

            # Write the residue name.
            file.write("%-6s" % data.name)

            # Find the index corresponding to 'self.ri_label' and 'self.frq_label'.
            index = self.find_index(data)

            # Skip the residue if data does not exist.
            if index == None:
                file.write("\n")
                continue

            # Write the relaxation value.
            file.write("%-30s" % `data.relax_data[index]`)

            # Write the relaxation error.
            file.write("%-30s" % `data.relax_error[index]`)

            # End of the line.
            file.write("\n")
