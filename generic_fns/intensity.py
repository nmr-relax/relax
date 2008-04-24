###############################################################################
#                                                                             #
# Copyright (C) 2004, 2007 Edward d'Auvergne                                  #
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

# Module docstring.
"""Module containing functions for the handling of peak intensities."""


# Python module imports.
from re import split
from warnings import warn

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxArgNotInListError, RelaxNoPipeError, RelaxNoSequenceError
from relax_warnings import RelaxWarning





class Intensity:
    def __init__(self, relax):
        """Class containing functions for handelling peak intensities."""

        self.relax = relax


    def det_dimensions(self):
        """Determine which are the proton and heteronuclei dimensions of the XEasy text file.

        @return:    None
        """

        # Loop over the lines of the file until the proton and heteronucleus is reached.
        for i in xrange(len(self.file_data)):
            # Extract the data.
            res_num, w1_name, w2_name, intensity = self.intensity(self.file_data[i])

            # Proton in w1, heteronucleus in w2.
            if w1_name == self.proton and w2_name == self.heteronuc:
                # Set the proton dimension.
                self.H_dim = 'w1'

                # Print out.
                print "The proton dimension is w1"

                # Don't continue (waste of time).
                break

            # Heteronucleus in w1, proton in w2.
            if w1_name == self.heteronuc and w2_name == self.proton:
                # Set the proton dimension.
                self.H_dim = 'w2'

                # Print out.
                print "The proton dimension is w2"

                # Don't continue (waste of time).
                break


    def intensity_sparky(self, line):
        """Function for returning relevant data from the Sparky peak intensity line.

        The residue number, heteronucleus and proton names, and peak intensity will be returned.
        """

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

        # The peak intensity column.
        if self.int_col == None:
            self.int_col = 3

        # Intensity.
        try:
            intensity = float(line[self.int_col])
        except ValueError:
            raise RelaxError, "The peak intensity value " + `intensity` + " from the line " + `line` + " is invalid."

        # Return the data.
        return res_num, h_name, x_name, intensity


    def intensity_xeasy(self, line):
        """Function for returning relevant data from the XEasy peak intensity line.

        The residue number, heteronucleus and proton names, and peak intensity will be returned.
        """

        # Test for invalid assignment lines which have the column numbers changed and return empty data.
        if line[4] == 'inv.':
            return None, None, None, 0.0

        # The residue number.
        try:
            res_num = int(line[5])
        except:
            raise RelaxError, "Improperly formatted XEasy file."

        # Nuclei names.
        if self.H_dim == 'w1':
            h_name = line[4]
            x_name = line[7]
        else:
            x_name = line[4]
            h_name = line[7]

        # Intensity (located in column 10).
        try:
            intensity = float(line[10])
        except ValueError:
            raise RelaxError, "The peak intensity value " + `intensity` + " from the line " + `line` + " is invalid."

        # Return the data.
        return res_num, h_name, x_name, intensity


    def number_of_header_lines(self):
        """Function for determining how many header lines are in the intensity file.

        @return:    The number of header lines.
        @rtype:     int
        """

        # Sparky.
        #########

        # Assume the Sparky file has two header lines!
        if self.format == 'sparky':
            return 2


        # XEasy.
        ########

        # Loop over the lines of the file until a peak intensity value is reached.
        header_lines = 0
        for i in xrange(len(self.file_data)):
            # Try to see if the intensity can be extracted.
            try:
                self.intensity(self.file_data[i])
            except RelaxError:
                header_lines = header_lines + 1
            except IndexError:
                header_lines = header_lines + 1
            else:
                break

        # Return the number of lines.
        return header_lines


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

        # Sparky.
        if self.format == 'sparky':
            # Print out.
            print "Sparky formatted data file.\n"

            # Set the intensity reading function.
            self.intensity = self.intensity_sparky

        # XEasy.
        elif self.format == 'xeasy':
            # Print out.
            print "XEasy formatted data file.\n"

            # Set the intensity reading function.
            self.intensity = self.intensity_xeasy

            # Set the default proton dimension.
            self.H_dim = 'w1'

        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if sequence data is loaded.
        if not relax_data_store.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Extract the data from the file.
        self.file_data = self.relax.IO.extract_data(file, dir)

        # Determine the number of header lines.
        num = self.number_of_header_lines()
        print "Number of header lines found: " + `num`

        # Remove the header.
        self.file_data = self.file_data[num:]

        # Strip the data.
        self.file_data = self.relax.IO.strip(self.file_data)

        # Determine the proton and heteronucleus dimensions in the XEasy text file.
        if self.format == 'xeasy':
            self.det_dimensions()

        # Loop over the peak intensity data.
        for i in xrange(len(self.file_data)):
            # Extract the data.
            res_num, H_name, X_name, intensity = self.intensity(self.file_data[i])

            # Skip data.
            if X_name != self.heteronuc or H_name != self.proton:
                warn(RelaxWarning("Proton and heteronucleus names do not match, skipping the data %s: " % `self.file_data[i]`))
                continue

            # Find the index of relax_data_store.res[self.run] which corresponds to res_num.
            index = None
            for j in xrange(len(relax_data_store.res[self.run])):
                if relax_data_store.res[self.run][j].num == res_num:
                    index = j
                    break
            if index == None:
                warn(RelaxWarning("Cannot find residue number %s within the sequence." % res_num))
                continue

            # Remap the data structure 'relax_data_store.res[self.run][index]'.
            data = relax_data_store.res[self.run][index]

            # Skip unselected residues.
            if not data.select:
                continue

            # Assign the data.
            self.assign_func(run=self.run, i=index, intensity=intensity)
