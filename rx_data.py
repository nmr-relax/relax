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


class Rx_data:
    def __init__(self, relax):
        """Class containing functions for relaxation data."""

        self.relax = relax


    def initialise_rx_data(self, data):
        """Function for initialisation of relaxation data structures.

        Only data structures which do not exist are created.
        """

        # The Relaxation data.
        if not hasattr(data, 'relax_data'):
            data.relax_data = []

        # The Relaxation error.
        if not hasattr(data, 'relax_error'):
            data.relax_error = []

        # The number of data points, eg 6.
        if not hasattr(data, 'num_ri'):
            data.num_ri = 0

        # The number of field strengths, eg 2.
        if not hasattr(data, 'num_frq'):
            data.num_frq = 0

        # Labels corresponding to the data type, eg ['NOE', 'R1', 'R2', 'NOE', 'R1', 'R2']
        if not hasattr(data, 'ri_labels'):
            data.ri_labels = []

        # A translation table to map relaxation data points to their frequencies, eg [0, 0, 0, 1, 1, 1]
        if not hasattr(data, 'remap_table'):
            data.remap_table = []

        # A translation table to direct the NOE data points to the R1 data points.  Used to speed up
        # calculations by avoiding the recalculation of R1 values.  eg [None, None, 0, None, None, 3]
        if not hasattr(data, 'noe_r1_table'):
            data.noe_r1_table = []

        # The NMR frequency labels, eg ['600', '500']
        if not hasattr(data, 'frq_labels'):
            data.frq_labels = []

        # The NMR frequencies in Hz, eg [600.0 * 1e6, 500.0 * 1e6]
        if not hasattr(data, 'frq'):
            data.frq = []


    def macro_read(self, ri_label=None, frq_label=None, frq=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None, header_lines=1):
        """Macro for loading R1, R2, or NOE relaxation data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength in MHz, ie '600'.  This string can be anything as long as
        data collected at the same field strength have the same label.

        frq:  The spectrometer frequency in Hz.

        file_name:  The name of the file containing the relaxation data.

        num_col:  The residue number column (the default is 0, ie the first column).

        name_col:  The residue name column (the default is 1).

        data_col:  The relaxation data column (the default is 2).

        error_col:  The experimental error column (the default is 3).

        sep:  The column separator (the default is white space).

        header_lines:  The number of lines at the top of the file to skip (the default is 1 line).


        Examples
        ~~~~~~~~

        The following commands will load the NOE relaxation data collected at 600 MHz out of a file
        called 'noe.600.out' where the residue numbers, residue names, data, errors are in the
        first, second, third, and forth columns respectively.

        relax> load.relax_data('NOE', '600', 599.7 * 1e6, 'noe.600.out')
        relax> load.relax_data(ri_label='NOE', frq_label='600', frq=600.0 * 1e6,
                               file_name='noe.600.out')


        The following commands will load the R2 data out of the file 'r2.out' where the residue
        numbers, residue names, data, errors are in the second, third, fifth, and sixth columns
        respectively.  The columns are separated by commas.

        relax> load.relax_data('R2', '800 MHz', 8.0 * 1e8, 'r2.out', 1, 2, 4, 5, ',')
        relax> load.relax_data(ri_label='R2', frq_label='800 MHz', frq=8.0*1e8, file_name='r2.out',
                               num_col=1, name_col=2, data_col=4, error_col=5, sep=',',
                               header_lines=1)


        The following commands will load the R1 data out of the file 'r1.out' where the columns are
        separated by the symbol '%'

        relax> load.relax_data('R1', '300', 300.1 * 1e6, 'r1.out', sep='%')
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "load.relax_data("
            text = text + "ri_label=" + `ri_label`
            text = text + ", frq_label=" + `frq_label`
            text = text + ", frq=" + `frq`
            text = text + ", file_name=" + `file_name`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", data_col=" + `data_col`
            text = text + ", error_col=" + `error_col`
            text = text + ", sep=" + `sep`
            text = text + ", header_lines=" + `header_lines` + ")\n"
            print text

        # Relaxation data type.
        if not ri_label or type(ri_label) != str:
            print "The relaxation label 'ri_label' has not been supplied correctly."
            return

        # Frequency label.
        elif type(frq_label) != str:
            print "The frequency label 'frq_label' has not been supplied correctly."
            return

        # Frequency.
        elif type(frq) != float:
            print "The frequency argument 'frq' should be a floating point number."
            return

        # The file name.
        elif not file_name:
            print "No file has been specified."
            return
        elif type(file_name) != str:
            print "The file name should be a string."
            return

        # The columns.
        elif type(num_col) != int or type(name_col) != int or type(data_col) != int or type(error_col) != int:
            print "The column arguments 'num_col', 'name_col', 'data_col', and 'error_col' should be integers."
            return

        # Column separator.
        elif sep != None and type(sep) != str:
            print "The column separator argument 'sep' should be either a string or None."
            return

        # Header lines.
        elif type(header_lines) != int:
            print "The number of header lines argument 'header_lines' should be an integer."
            return

        # Execute the functional code.
        self.read(ri_label=ri_label, frq_label=frq_label, frq=frq, file_name=file_name, num_col=num_col, name_col=name_col, data_col=data_col, error_col=error_col, sep=sep, header_lines=header_lines)


    def read(self, ri_label=None, frq_label=None, frq=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None, header_lines=None):
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
        if not len(self.relax.data.res):
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

        # Strip the data.
        file_data = self.relax.file_ops.strip(file_data)

        # Test the validity of the relaxation data.
        for i in range(len(file_data)):
            try:
                int(file_data[i][self.num_col])
                float(file_data[i][self.data_col])
                float(file_data[i][self.error_col])
            except ValueError:
                print "The relaxation data is invalid."
                return

        # Loop over the relaxation data.
        for i in range(len(file_data)):
            # Get the data.
            res_num = int(file_data[i][self.num_col])
            res_name = file_data[i][self.name_col]
            value = float(file_data[i][self.data_col])
            error = float(file_data[i][self.error_col])

            # Find the index of self.relax.data.res which corresponds to the relaxation data set i.
            index = None
            for j in range(len(self.relax.data.res)):
                if self.relax.data.res[j].num == res_num and self.relax.data.res[j].name == res_name:
                    index = j
                    break
            if index == None:
                print "Warning: Residue " + `res_num` + " " + res_name + " cannot be found in the sequence, skipping data."
                continue

            # Initialise the relaxation data structures (if needed).
            self.initialise_rx_data(self.relax.data.res[index])

            # Test if relaxation data corresponding to 'ri_label' and 'frq_label' already exists, and if so, do not load or update the data.
            for j in range(self.relax.data.res[index].num_ri):
                if self.ri_label == self.relax.data.res[index].ri_labels[j] and self.frq_label == self.relax.data.res[index].frq_labels[self.relax.data.res[index].remap_table[j]]:
                    print "Warning: The relaxation data corresponding to " + `ri_label` + " and " + `frq_label` + " has already been loaded."
                    continue

            # Relaxation data and errors.
            self.relax.data.res[index].relax_data.append(value)
            self.relax.data.res[index].relax_error.append(error)

            # Update the number of relaxation data points.
            self.relax.data.res[index].num_ri = self.relax.data.res[index].num_ri + 1

            # Add ri_label to the data types.
            self.relax.data.res[index].ri_labels.append(self.ri_label)

            # Find if the frequency self.frq has already been loaded.
            remap = len(self.relax.data.res[index].frq)
            flag = 0
            for i in range(len(self.relax.data.res[index].frq)):
                if self.frq == self.relax.data.res[index].frq[i]:
                    remap = i
                    flag = 1

            # Update the data structures which have a length equal to the number of field strengths.
            if not flag:
                self.relax.data.res[index].num_frq = self.relax.data.res[index].num_frq + 1
                self.relax.data.res[index].frq_labels.append(self.frq_label)
                self.relax.data.res[index].frq.append(self.frq)

            # Update the remap table.
            self.relax.data.res[index].remap_table.append(remap)

            # Update the NOE R1 translation table.
            self.relax.data.res[index].noe_r1_table.append(None)
            if self.ri_label == 'NOE':
                # If the data corresponds to 'NOE', try to find if the corresponding 'R1' data has been loaded.
                for i in range(self.relax.data.res[index].num_ri):
                    if self.relax.data.res[index].ri_labels[i] == 'R1' and self.frq_label == self.relax.data.res[index].frq_labels[self.relax.data.res[index].remap_table[i]]:
                        self.relax.data.res[index].noe_r1_table[self.relax.data.res[index].num_ri - 1] = i
            if self.ri_label == 'R1':
                # If the data corresponds to 'R1', try to find if the corresponding 'NOE' data has been loaded.
                for i in range(self.relax.data.res[index].num_ri):
                    if self.relax.data.res[index].ri_labels[i] == 'NOE' and self.frq_label == self.relax.data.res[index].frq_labels[self.relax.data.res[index].remap_table[i]]:
                        self.relax.data.res[index].noe_r1_table[i] = self.relax.data.res[index].num_ri - 1
