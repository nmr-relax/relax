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

import sys

class Rx_data:
    def __init__(self, relax):
        """Class containing functions for relaxation data."""

        self.relax = relax


    def delete_rx_data(self, run):
        """Funciton for removal of relaxation data structures."""


    def initialise_rx_data(self, data, run):
        """Function for initialisation of relaxation data structures.

        Only data structures which do not exist are created.
        """

        # Relaxation data.
        if not hasattr(data, 'relax_data'):
            data.relax_data = {}
        if not data.relax_data.has_key(run):
            data.relax_data[run] = []

        # Relaxation error.
        if not hasattr(data, 'relax_error'):
            data.relax_error = {}
        if not data.relax_error.has_key(run):
            data.relax_error[run] = []

        # Number of data points, eg 6.
        if not hasattr(data, 'num_ri'):
            data.num_ri = {}
        if not data.num_ri.has_key(run):
            data.num_ri[run] = 0

        # Number of field strengths, eg 2.
        if not hasattr(data, 'num_frq'):
            data.num_frq = {}
        if not data.num_frq.has_key(run):
            data.num_frq[run] = 0

        # Labels corresponding to the data type, eg ['NOE', 'R1', 'R2', 'NOE', 'R1', 'R2']
        if not hasattr(data, 'ri_labels'):
            data.ri_labels = {}
        if not data.ri_labels.has_key(run):
            data.ri_labels[run] = []

        # A translation table to map relaxation data points to their frequencies, eg [0, 0, 0, 1, 1, 1]
        if not hasattr(data, 'remap_table'):
            data.remap_table = {}
        if not data.remap_table.has_key(run):
            data.remap_table[run] = []

        # A translation table to direct the NOE data points to the R1 data points.  Used to speed up
        # calculations by avoiding the recalculation of R1 values.  eg [None, None, 0, None, None, 3]
        if not hasattr(data, 'noe_r1_table'):
            data.noe_r1_table = {}
        if not data.noe_r1_table.has_key(run):
            data.noe_r1_table[run] = []

        # NMR frequency labels, eg ['600', '500']
        if not hasattr(data, 'frq_labels'):
            data.frq_labels = {}
        if not data.frq_labels.has_key(run):
            data.frq_labels[run] = []

        # NMR frequencies in Hz, eg [600.0 * 1e6, 500.0 * 1e6]
        if not hasattr(data, 'frq'):
            data.frq = {}
        if not data.frq.has_key(run):
            data.frq[run] = []


    def macro_read(self, run=None, ri_label=None, frq_label=None, frq=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None, header_lines=1):
        """Macro for reading R1, R2, or NOE relaxation data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

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

        The following commands will read the NOE relaxation data collected at 600 MHz out of a file
        called 'noe.600.out' where the residue numbers, residue names, data, errors are in the
        first, second, third, and forth columns respectively.

        relax> read.relax_data('m1', 'NOE', '600', 599.7 * 1e6, 'noe.600.out')
        relax> read.relax_data('m1', ri_label='NOE', frq_label='600', frq=600.0 * 1e6,
                               file_name='noe.600.out')


        The following commands will read the R2 data out of the file 'r2.out' where the residue
        numbers, residue names, data, errors are in the second, third, fifth, and sixth columns
        respectively.  The columns are separated by commas.

        relax> read.relax_data('m1', 'R2', '800 MHz', 8.0 * 1e8, 'r2.out', 1, 2, 4, 5, ',')
        relax> read.relax_data('m1', ri_label='R2', frq_label='800 MHz', frq=8.0*1e8,
                               file_name='r2.out', num_col=1, name_col=2, data_col=4, error_col=5,
                               sep=',', header_lines=1)


        The following commands will read the R1 data out of the file 'r1.out' where the columns are
        separated by the symbol '%'

        relax> read.relax_data('m1', 'R1', '300', 300.1 * 1e6, 'r1.out', sep='%')
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "read.relax_data("
            text = text + "run=" + `run`
            text = text + ", ri_label=" + `ri_label`
            text = text + ", frq_label=" + `frq_label`
            text = text + ", frq=" + `frq`
            text = text + ", file_name=" + `file_name`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", data_col=" + `data_col`
            text = text + ", error_col=" + `error_col`
            text = text + ", sep=" + `sep`
            text = text + ", header_lines=" + `header_lines` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise UserError, "The run name must be supplied as a string."

        # Relaxation data type.
        if not ri_label or type(ri_label) != str:
            raise UserError, "The relaxation label 'ri_label' must be supplied as a string."

        # Frequency label.
        elif type(frq_label) != str:
            raise UserError, "The frequency label 'frq_label' must be supplied as a string."

        # Frequency.
        elif type(frq) != float:
            raise UserError, "The frequency argument 'frq' should be a floating point number."

        # The file name.
        elif not file_name:
            raise UserError, "No file has been specified."
        elif type(file_name) != str:
            raise UserError, "The file name should be a string."

        # The columns.
        elif type(num_col) != int or type(name_col) != int or type(data_col) != int or type(error_col) != int:
            raise UserError, "The column arguments 'num_col', 'name_col', 'data_col', and 'error_col' should be integers."

        # Column separator.
        elif sep != None and type(sep) != str:
            raise UserError, "The column separator argument 'sep' should be either a string or None."

        # Header lines.
        elif type(header_lines) != int:
            raise UserError, "The number of header lines argument 'header_lines' should be an integer."

        # Execute the functional code.
        self.read(run=run, ri_label=ri_label, frq_label=frq_label, frq=frq, file_name=file_name, num_col=num_col, name_col=name_col, data_col=data_col, error_col=error_col, sep=sep, header_lines=header_lines)


    def read(self, run=None, ri_label=None, frq_label=None, frq=None, file_name=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None, header_lines=None):
        """Function for reading R1, R2, or NOE relaxation data."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise UserError, "Sequence data has to be loaded first."

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(file_name)

        # Do nothing if the file does not exist.
        if not file_data:
            raise UserError, "No relaxation data read."

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip the data.
        file_data = self.relax.file_ops.strip(file_data)

        # Test the validity of the relaxation data.
        for i in range(len(file_data)):
            try:
                int(file_data[i][num_col])
                float(file_data[i][data_col])
                float(file_data[i][error_col])
            except ValueError:
                raise UserError, "The relaxation data is invalid (num=" + file_data[i][num_col] + ", name=" + file_data[i][name_col] + ", data=" + file_data[i][data_col] + ", error=" + file_data[i][error_col] + ")."

        # Add the run to the runs list.
        if not run in self.relax.data.runs:
            self.relax.data.runs.append(run)

        # Loop over the relaxation data.
        for i in range(len(file_data)):
            # Get the data.
            res_num = int(file_data[i][num_col])
            res_name = file_data[i][name_col]
            value = float(file_data[i][data_col])
            error = float(file_data[i][error_col])

            # Find the index of self.relax.data.res which corresponds to the relaxation data set i.
            index = None
            for j in range(len(self.relax.data.res)):
                if self.relax.data.res[j].num == res_num and self.relax.data.res[j].name == res_name:
                    index = j
                    break
            if index == None:
                raise UserError, "Residue " + `res_num` + " " + res_name + " cannot be found in the sequence."

            # Initialise the relaxation data structures (if needed).
            self.initialise_rx_data(self.relax.data.res[index], run)

            # Test if relaxation data corresponding to 'ri_label' and 'frq_label' already exists, and if so, do not load or update the data.
            for j in range(self.relax.data.res[index].num_ri[run]):
               if ri_label == self.relax.data.res[index].ri_labels[run][j] and frq_label == self.relax.data.res[index].frq_labels[run][self.relax.data.res[index].remap_table[run][j]]:
                    raise UserError, "The relaxation data corresponding to " + `ri_label` + " and " + `frq_label` + " has already been read."

            # Relaxation data and errors.
            self.relax.data.res[index].relax_data[run].append(value)
            self.relax.data.res[index].relax_error[run].append(error)

            # Update the number of relaxation data points.
            self.relax.data.res[index].num_ri[run] = self.relax.data.res[index].num_ri[run] + 1

            # Add ri_label to the data types.
            self.relax.data.res[index].ri_labels[run].append(ri_label)

            # Find if the frequency self.frq has already been loaded.
            remap = len(self.relax.data.res[index].frq[run])
            flag = 0
            for i in range(len(self.relax.data.res[index].frq[run])):
                if frq == self.relax.data.res[index].frq[run][i]:
                    remap = i
                    flag = 1

            # Update the data structures which have a length equal to the number of field strengths.
            if not flag:
                self.relax.data.res[index].num_frq[run] = self.relax.data.res[index].num_frq[run] + 1
                self.relax.data.res[index].frq_labels[run].append(frq_label)
                self.relax.data.res[index].frq[run].append(frq)

            # Update the remap table.
            self.relax.data.res[index].remap_table[run].append(remap)

            # Update the NOE R1 translation table.
            self.relax.data.res[index].noe_r1_table[run].append(None)
            if ri_label == 'NOE':
                # If the data corresponds to 'NOE', try to find if the corresponding 'R1' data has been read.
                for i in range(self.relax.data.res[index].num_ri[run]):
                    if self.relax.data.res[index].ri_labels[run][i] == 'R1' and frq_label == self.relax.data.res[index].frq_labels[run][self.relax.data.res[index].remap_table[run][i]]:
                        self.relax.data.res[index].noe_r1_table[run][self.relax.data.res[index].num_ri[run] - 1] = i
            if ri_label == 'R1':
                # If the data corresponds to 'R1', try to find if the corresponding 'NOE' data has been read.
                for i in range(self.relax.data.res[index].num_ri[run]):
                    if self.relax.data.res[index].ri_labels[run][i] == 'NOE' and frq_label == self.relax.data.res[index].frq_labels[run][self.relax.data.res[index].remap_table[run][i]]:
                        self.relax.data.res[index].noe_r1_table[run][i] = self.relax.data.res[index].num_ri[run] - 1
