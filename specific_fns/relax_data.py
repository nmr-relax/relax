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

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError

        # Test if relaxation data corresponding to 'ri_label' and 'frq_label' already exists.
        if self.test_labels(run, ri_label, frq_label):
            raise RelaxRiError, (ri_label, frq_label)


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

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError

        # Test if data corresponding to 'ri_label' and 'frq_label' exists.
        if not self.test_labels(run, ri_label, frq_label):
            raise RelaxNoRiError, (ri_label, frq_label)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Find the index corresponding to 'ri_label' and 'frq_label'.
            index = self.find_index(run, i, ri_label, frq_label)

            # Relaxation data and errors.
            self.relax.data.res[run][i].relax_data.pop(index)
            self.relax.data.res[run][i].relax_error.pop(index)

            # Update the number of relaxation data points.
            self.relax.data.res[run][i].num_ri = self.relax.data.res[run][i].num_ri - 1

            # Delete ri_label from the data types.
            self.relax.data.res[run][i].ri_labels.pop(index)

            # Update the remap table.
            self.relax.data.res[run][i].remap_table.pop(index)

            # Find if there is other data corresponding to 'frq_label'
            frq_index = self.relax.data.res[run][i].frq_labels.index(frq_label)
            if not frq_index in self.relax.data.res[run][i].remap_table:
                self.relax.data.res[run][i].num_frq = self.relax.data.res[run][i].num_frq - 1
                self.relax.data.res[run][i].frq_labels.pop(frq_index)
                self.relax.data.res[run][i].frq.pop(frq_index)

            # Update the NOE R1 translation table.
            self.relax.data.res[run][i].noe_r1_table.pop(index)
            for j in xrange(self.relax.data.res[run][i].num_ri):
                if self.relax.data.res[run][i].noe_r1_table[j] > index:
                    self.relax.data.res[run][i].noe_r1_table[j] = self.relax.data.res[run][i].noe_r1_table[j] - 1


    def display(self, run=None, ri_label=None, frq_label=None):
        """Function for displaying relaxation data corresponding to ri_label and frq_label."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError

        # Test if data corresponding to 'ri_label' and 'frq_label' exists.
        if not self.test_labels(run, ri_label, frq_label):
            raise RelaxNoRiError, (ri_label, frq_label)

        # Print the data.
        self.write_data(run, ri_label, frq_label, sys.stdout)


    def find_index(self, run, i, ri_label, frq_label):
        """Function for finding the index corresponding to ri_label and frq_label."""

        index = None
        for j in xrange(self.relax.data.res[run][i].num_ri):
            if ri_label == self.relax.data.res[run][i].ri_labels[j] and frq_label == self.relax.data.res[run][i].frq_labels[self.relax.data.res[run][i].remap_table[j]]:
                index = j

        return index


    def initialise_relax_data(self, data, run):
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

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError

        # Test if relaxation data corresponding to 'ri_label' and 'frq_label' already exists.
        if self.test_labels(run, ri_label, frq_label):
            raise RelaxRiError, (ri_label, frq_label)

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

            # Find the index of self.relax.data.res[run] which corresponds to the relaxation data set i.
            index = None
            for j in xrange(len(self.relax.data.res[run])):
                if self.relax.data.res[run][j].num == res_num and self.relax.data.res[run][j].name == res_name:
                    index = j
                    break
            if index == None:
                raise RelaxNoResError, (res_num, res_name)

            # Initialise the relaxation data structures (if needed).
            self.initialise_relax_data(self.relax.data.res[run][index], run)

            # Relaxation data and errors.
            self.relax.data.res[run][index].relax_data.append(value)
            self.relax.data.res[run][index].relax_error.append(error)

            # Update the number of relaxation data points.
            self.relax.data.res[run][index].num_ri = self.relax.data.res[run][index].num_ri + 1

            # Add ri_label to the data types.
            self.relax.data.res[run][index].ri_labels.append(ri_label)

            # Find if the frequency self.frq has already been loaded.
            remap = len(self.relax.data.res[run][index].frq)
            flag = 0
            for i in xrange(len(self.relax.data.res[run][index].frq)):
                if frq == self.relax.data.res[run][index].frq[i]:
                    remap = i
                    flag = 1

            # Update the remap table.
            self.relax.data.res[run][index].remap_table.append(remap)

            # Update the data structures which have a length equal to the number of field strengths.
            if not flag:
                self.relax.data.res[run][index].num_frq = self.relax.data.res[run][index].num_frq + 1
                self.relax.data.res[run][index].frq_labels.append(frq_label)
                self.relax.data.res[run][index].frq.append(frq)

            # Update the NOE R1 translation table.
            self.relax.data.res[run][index].noe_r1_table.append(None)
            if ri_label == 'NOE':
                # If the data corresponds to 'NOE', try to find if the corresponding 'R1' data has been read.
                for i in xrange(self.relax.data.res[run][index].num_ri):
                    if self.relax.data.res[run][index].ri_labels[i] == 'R1' and frq_label == self.relax.data.res[run][index].frq_labels[self.relax.data.res[run][index].remap_table[i]]:
                        self.relax.data.res[run][index].noe_r1_table[self.relax.data.res[run][index].num_ri - 1] = i
            if ri_label == 'R1':
                # If the data corresponds to 'R1', try to find if the corresponding 'NOE' data has been read.
                for i in xrange(self.relax.data.res[run][index].num_ri):
                    if self.relax.data.res[run][index].ri_labels[i] == 'NOE' and frq_label == self.relax.data.res[run][index].frq_labels[self.relax.data.res[run][index].remap_table[i]]:
                        self.relax.data.res[run][index].noe_r1_table[i] = self.relax.data.res[run][index].num_ri - 1


    def test_labels(self, run, ri_label, frq_label):
        """Function for testing if data corresponding to 'ri_label' and 'frq_label' currently exist."""

        # Initialise.
        exists = 0

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # No ri data.
            if not hasattr(self.relax.data.res[run][i], 'num_ri'):
                continue

            # Loop over the relaxation data.
            for j in xrange(self.relax.data.res[run][i].num_ri):
                # Test if the relaxation data matches 'ri_label' and 'frq_label'.
                if ri_label == self.relax.data.res[run][i].ri_labels[j] and frq_label == self.relax.data.res[run][i].frq_labels[self.relax.data.res[run][i].remap_table[j]]:
                    exists = 1

        return exists


    def write(self, run=None, ri_label=None, frq_label=None, file=None, dir=None, force=0):
        """Function for writing relaxation data."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError

        # Test if data corresponding to 'ri_label' and 'frq_label' exists.
        if not self.test_labels(run, ri_label, frq_label):
            raise RelaxNoRiError, (ri_label, frq_label)

        # Create the file name if none is given.
        if file == None:
            file = ri_label + "." + frq_label + ".out"

        # Open the file for writing.
        relax_file = self.relax.file_ops.open_write_file(file, dir, force)

        # Write the data.
        self.write_data(run, ri_label, frq_label, relax_file)

        # Close the file.
        relax_file.close()


    def write_data(self, run, ri_label, frq_label, file):
        """Function for writing the relaxation data."""

        # Write a header line.
        file.write("%-5s%-6s%-30s%-30s\n" % ('Num', 'Name', 'Value', 'Error'))

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Write the residue number.
            file.write("%-5i" % self.relax.data.res[run][i].num)

            # Write the residue name.
            file.write("%-6s" % self.relax.data.res[run][i].name)

            # Find the index corresponding to 'ri_label' and 'frq_label'.
            index = self.find_index(run, i, ri_label, frq_label)

            # Skip the residue if data does not exist.
            if index == None:
                file.write("\n")
                continue

            # Write the relaxation value.
            file.write("%-30s" % `self.relax.data.res[run][i].relax_data[index]`)

            # Write the relaxation error.
            file.write("%-30s" % `self.relax.data.res[run][i].relax_error[index]`)

            # End of the line.
            file.write("\n")
