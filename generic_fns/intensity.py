###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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

from re import split

class Intensity:
    def __init__(self, relax):
        """Class containing functions for handelling peak intensities."""

        self.relax = relax


    def extract_int_data(self, line):
        """Function for returning relevant data from the peak intensity line.

        The residue number, heteronucleus and proton names, and peak intensity will be returned.
        """

        # Sparky formatted line.
        if self.format == 'sparky':
            # The Sparky assignment.
            assignment = split('([A-Z]+)', line[0])
            assignment = assignment[1:-1]

            # The residue number.
            try:
                res_num = int(assignment[1])
            except:
                raise RelaxError, "Improperly formatted Sparky file."

            # Nuclei names.
            x_name = assignment[2]
            h_name = assignment[4]

            # Intensity.
            intensity = line[self.int_col]

        # XEasy formatted line.
        elif self.format == 'xeasy':
            # Test for invalid assignment lines which have the column numbers changed and return empty data.
            if line[4] == 'inv.':
                return None, None, None, 0.0

            # The residue number.
            try:
                res_num = int(line[5])
            except:
                raise RelaxError, "Improperly formatted XEasy file."

            # Nuclei names.
            x_name = line[7]
            h_name = line[4]

            # Intensity.
            intensity = line[self.int_col]

        # Test the validity of the peak intensity data.
        try:
            intensity = float(intensity)
        except ValueError:
            raise RelaxError, "The peak height value " + `intensity` + " from the line " + `line` + " is invalid."

        return res_num, x_name, h_name, intensity


    def read(self, run=None, file=None, dir=None, format=None, heteronuc=None, proton=None, int_col=None, assign_func=None):
        """Function for reading peak intensity data."""

        # Arguments.
        self.run = run
        self.format = format
        self.heteronuc = heteronuc
        self.proton = proton
        self.int_col = int_col
        self.assign_func = assign_func

        # Format argument.
        format_list = ['sparky', 'xeasy']
        if self.format not in format_list:
            raise RelaxArgNotInListError, ('format', self.format, format_list)
        if self.format == 'sparky':
            print "Sparky formatted data file.\n"
        elif self.format == 'xeasy':
            print "XEasy formatted data file.\n"

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # File path.
        self.file_path = file
        if dir:
            self.file_path = dir + '/' + self.file_path

        # Extract the data from the file.
        if self.file_path:
            file_data = self.relax.file_ops.extract_data(self.file_path)

        # Remove the header.
        file_data = file_data[2:]

        # Strip the data.
        file_data = self.relax.file_ops.strip(file_data)

        # The peak intensity column.
        if self.format == 'sparky':
            if int_col:
                self.int_col = int_col
            else:
                self.int_col = 3
        elif self.format == 'xeasy':
            self.int_col = 10

        # Loop over the peak intensity data.
        for i in xrange(len(file_data)):
            # Extract the data.
            res_num, X_name, H_name, intensity = self.extract_int_data(file_data[i])

            # Skip data.
            if X_name != self.heteronuc or H_name != self.proton:
                print "Skipping the data: " + `file_data[i]`
                continue

            # Find the index of self.relax.data.res[self.run] which corresponds to res_num.
            index = None
            for j in xrange(len(self.relax.data.res[self.run])):
                if self.relax.data.res[self.run][j].num == res_num:
                    index = j
                    break
            if index == None:
                print "Skipping the data: " + `file_data[i]`
                continue

            # Remap the data structure 'self.relax.data.res[self.run][index]'.
            data = self.relax.data.res[self.run][index]

            # Skip unselected residues.
            if not data.select:
                continue

            # Assign the data.
            self.assign_func(run=self.run, i=index, intensity=intensity)
