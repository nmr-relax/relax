###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


from generic_functions import Generic_functions


class Load(Generic_functions):
    def __init__(self, relax):
        """Class containing functions for loading data."""

        self.relax = relax


    def relax_data(self, ri_label=None, frq_label=None, frq=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None, header_lines=None):
        """Function for loading R1, R2, or NOE relaxation data."""

        # Arguments
        self.ri_label = ri_label
        self.frq_label = frq_label
        self.frq = frq
        self.file_name = file_name
        self.num_col = num_col
        self.name_col = name_col
        self.data_col = data_col
        self.error_col = error_col
        self.sep = sep

        # Test if sequence data is loaded.
        if not len(self.relax.data.seq):
            print "Sequence data has to be loaded first."
            return

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(self.file_name)

        # Do nothing if the file does not exist.
        if not file_data:
            print "No relaxation data loaded."
            return

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip data.
        file_data = self.relax.file_ops.strip(file_data)

        # Test if relaxation data corresponding to 'ri_label' and 'frq_label' already exists, and if so, do not load or update the data.
        try:
            for i in range(self.relax.data.num_ri):
                if self.ri_label == self.relax.data.ri_labels[i] and self.frq_label == self.relax.data.frq_labels[self.relax.data.remap_table[i]]:
                    print "The relaxation data corresponding to " + `ri_label` + " and " + `frq_label` + " has already been loaded."
                    print "To load the data, either delete the original or use different labels."
                    return
        except AttributeError:
            pass

        # Update the data.
        self.update_data()

        # Add the relaxation data to self.relax.data.relax_data
        data = []
        for i in range(len(file_data)):
            data.append([int(file_data[i][self.num_col]), file_data[i][self.name_col], float(file_data[i][self.data_col]), float(file_data[i][self.error_col])])
        self.relax.data.relax_data.append(self.create_data(data))


    def sequence(self, file_name=None, num_col=0, name_col=1, sep=None, header_lines=None):
        """Function for loading sequence data."""

        # Test if the sequence data has already been loaded.
        try:
            self.relax.data.seq
        except AttributeError:
            pass
        else:
            print "The sequence data has already been loaded."
            print "To reload, delete the original sequence data (self.relax.data.seq)."
            return

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(file_name)

        # Do nothing if the file does not exist.
        if not file_data:
            print "No sequence data loaded."
            return

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip data.
        file_data = self.relax.file_ops.strip(file_data)

        # Place the data in self.relax.data.seq
        seq = []
        for i in range(len(file_data)):
            label = file_data[i][num_col] + '_' + file_data[i][name_col]
            try:
                seq.append([int(file_data[i][num_col]), file_data[i][name_col], label])
            except ValueError:
                print "Sequence data is invalid."
                return
        self.relax.data.seq = seq


    def update_data(self):
        """Update the relaxation data structures."""

        # Data initialisation.
        ######################

        # The number of data points, eg 6.
        try:
            self.relax.data.num_ri
        except AttributeError:
            self.relax.data.num_ri = 0

        # The number of field strengths, eg 2.
        try:
            self.relax.data.num_frq
        except AttributeError:
            self.relax.data.num_frq = 0

        # Labels corresponding to the data type, eg ['NOE', 'R1', 'R2', 'NOE', 'R1', 'R2']
        try:
            self.relax.data.ri_labels
        except AttributeError:
            self.relax.data.ri_labels = []

        # A translation table to map relaxation data points to their frequencies, eg [0, 0, 0, 1, 1, 1]
        try:
            self.relax.data.remap_table
        except AttributeError:
            self.relax.data.remap_table = []

        # A translation table to direct the NOE data points to the R1 data points.  Used to speed up
        # calculations by avoiding the recalculation of R1 values.  eg [None, None, 0, None, None, 3]
        try:
            self.relax.data.noe_r1_table
        except AttributeError:
            self.relax.data.noe_r1_table = []

        # The NMR frequency labels, eg ['600', '500']
        try:
            self.relax.data.frq_labels
        except AttributeError:
            self.relax.data.frq_labels = []

        # The NMR frequencies in Hz, eg [600.0 * 1e6, 500.0 * 1e6]
        try:
            self.relax.data.frq
        except AttributeError:
            self.relax.data.frq = []

        # The structure of self.relax_data is as follows:  The first dimension corresponds to each
        # relaxation data point.  The fields point to 2D data structures containing the data from
        # the relaxation file (missing the single header line), ie:
        #    [res][1] - Relaxation value
        #    [res][2] - Relaxation error
        #    [res][3] - Flag, 0 = no data, 1 = data.
        try:
            self.relax.data.relax_data
        except AttributeError:
            self.relax.data.relax_data = []

        # Update the number of relaxation data points.
        self.relax.data.num_ri = self.relax.data.num_ri + 1

        # Add ri_label to the data types.
        self.relax.data.ri_labels.append(self.ri_label)

        # Find if the frequency self.frq has already been loaded.
        remap = len(self.relax.data.frq)
        flag = 0
        for i in range(len(self.relax.data.frq)):
            if self.frq == self.relax.data.frq[i]:
                remap = i
                flag = 1

        # Update the data structures which have a length equal to the number of field strengths.
        if not flag:
            self.relax.data.num_frq = self.relax.data.num_frq + 1
            self.relax.data.frq_labels.append(self.frq_label)
            self.relax.data.frq.append(self.frq)

        # Update the remap table.
        self.relax.data.remap_table.append(remap)

        # Update the NOE R1 translation table.
        self.relax.data.noe_r1_table.append(None)
        if self.ri_label == 'NOE':
            # If the data corresponds to 'NOE', try to find if the corresponding 'R1' data has been loaded.
            for i in range(self.relax.data.num_ri):
                if self.relax.data.ri_labels[i] == 'R1' and self.frq_label == self.relax.data.frq_labels[self.relax.data.remap_table[i]]:
                    self.relax.data.noe_r1_table[self.relax.data.num_ri - 1] = i
        if self.ri_label == 'R1':
            # If the data corresponds to 'R1', try to find if the corresponding 'NOE' data has been loaded.
            for i in range(self.relax.data.num_ri):
                if self.relax.data.ri_labels[i] == 'NOE' and self.frq_label == self.relax.data.frq_labels[self.relax.data.remap_table[i]]:
                    self.relax.data.noe_r1_table[i] = self.relax.data.num_ri - 1
