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

from os import system
from re import match


class Grace:
    def __init__(self, relax):
        """Operations, functions, etc common to the different model-free analysis methods."""

        self.relax = relax


    def data(self):
        """Write the data into the grace file."""

        # Determine the graph type.
        errors = 0
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Get the value and error.
            value, error = self.return_value(self.run, i, self.data_type)

            # Skip the data if there is no value.
            if value == None:
                continue

            # Test if there is an error.
            if error != None:
                errors = 1
                break

        if errors:
            graph_type = 'xydy'
        else:
            graph_type = 'xy'


        # Graph 0, set 0.
        self.file.write("@target G0.S0\n")
        self.file.write("@type " + graph_type + "\n")

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Get the value and error.
            value, error = self.return_value(self.run, i, self.data_type)

            # Skip the data if there is no value.
            if value == None:
                continue

            # Graph type xy.
            if graph_type == 'xy':
                # Write the data.
                self.file.write("%-5i%-30s\n" % (data.num, `value`))

            # Graph type xydy.
            elif graph_type == 'xydy':
                # Missing error.
                if error == None:
                    error = 0.0

                # Write the data.
                self.file.write("%-5i%-30s%-30s\n" % (data.num, `value`, `error`))

        # End of graph 0, set 0.
        self.file.write("&\n")


    def header(self):
        """Write the grace header."""

        # Grace version number (presumably for grace to interpret the header info).
        self.file.write("@version 50114\n")

        # Graph G0.
        self.file.write("@with g0\n")

        # X axis start and end.
        self.file.write("@    world xmin " + `self.relax.data.res[self.run][0].num - 1` + "\n")
        self.file.write("@    world xmax " + `self.relax.data.res[self.run][-1].num + 1` + "\n")

        # Y axis start and end.
        min_value = 0.0
        max_value = -1e99
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Get the value and error.
            value, error = self.return_value(self.run, i, self.data_type)

            # Skip the data if there is no value.
            if value == None:
                continue

            # Max check.
            if value > max_value:
                max_value = value

            # Min check.
            if value < min_value:
                min_value = value

        self.file.write("@    world ymin " + `min_value - min_value * 0.05` + "\n")
        self.file.write("@    world ymax " + `max_value + max_value * 0.05` + "\n")

        # Residue specific ticks.
        self.file.write("@    xaxis  tick major 10\n")
        self.file.write("@    xaxis  tick major size 0.48\n")
        self.file.write("@    xaxis  tick major linewidth 0.5\n")
        self.file.write("@    xaxis  tick minor linewidth 0.5\n")
        self.file.write("@    xaxis  tick minor size 0.24\n")
        self.file.write("@    xaxis  ticklabel char size 0.79\n")

        # Data specific ticks.
        self.file.write("@    yaxis  tick major size 0.48\n")
        self.file.write("@    yaxis  tick major linewidth 0.5\n")
        self.file.write("@    yaxis  tick minor linewidth 0.5\n")
        self.file.write("@    yaxis  tick minor size 0.24\n")
        self.file.write("@    yaxis  ticklabel char size 0.79\n")

        # Frame.
        self.file.write("@    frame linewidth 0.5\n")

        # Symbols.
        self.file.write("@    s0 symbol 1\n")
        self.file.write("@    s0 symbol size 0.35\n")
        self.file.write("@    s0 symbol fill pattern 1\n")
        self.file.write("@    s0 symbol linewidth 0.5\n")
        self.file.write("@    s0 line linestyle 0\n")

        # Error bars.
        self.file.write("@    s0 errorbar size 0.5\n")
        self.file.write("@    s0 errorbar linewidth 0.5\n")
        self.file.write("@    s0 errorbar riser linewidth 0.5\n")


    def view(self, run=None, data_type=None, file=None, dir=None, grace_exe='xmgrace', force=0):
        """Function for running Grace."""

        # Write the grace file (if the run in not None).
        if run != None:
            self.write(run=run, data_type=data_type, file=file, dir=dir, force=force)

        # File path.
        self.file_path = file
        if dir:
            self.file_path = dir + '/' + self.file_path

        # Run Grace.
        system(grace_exe + " " + self.file_path + " &")


    def write(self, run=None, data_type=None, file=None, dir=None, force=0):
        """Function for writing data to a file."""

        # Arguments.
        self.run = run
        self.data_type = data_type

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Open the file for writing.
        self.file = self.relax.file_ops.open_write_file(file, dir, force)

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific value and error returning function.
        self.return_value = self.relax.specific_setup.setup('return_value', function_type)

        # Write the header.
        self.header()

        # Write the data.
        self.data()

        # Close the file.
        self.file.close()
