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


class Results:
    def __init__(self, relax):
        """Class containing functions for reading and writing data."""

        self.relax = relax


    def copy(self, run1=None, run2=None, sim=None):
        """Function for copying all results from run1 to run2."""

        # Test if run1 exists.
        if not run1 in self.relax.data.run_names:
            raise RelaxNoRunError, run1

        # Test if run2 exists.
        if not run2 in self.relax.data.run_names:
            raise RelaxNoRunError, run2

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run1)]

        # Copy function.
        copy = self.relax.specific_setup.setup('copy', function_type, raise_error=0)

        # Copy the results.
        copy(run1=run1, run2=run2, sim=sim)


    def display(self, run=None, format='columnar'):
        """Function for displaying the results."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific results writing function.
        if format == 'xml':
            format = 'XML'
            self.write_function = self.relax.specific_setup.setup('write_xml_results', function_type, raise_error=0)
        elif format == 'columnar':
            self.write_function = self.relax.specific_setup.setup('write_columnar_results', function_type, raise_error=0)
        else:
            raise RelaxError, "Unknown format " + `format` + "."

        # No function.
        if not self.write_function:
            raise RelaxError, "The " + format + " format is not currently supported for " + self.relax.specific_setup.get_string(function_type) + "."

        # Write the results.
        self.write_function(sys.stdout, run)


    def read(self, run=None, file='results', directory=None, file_data=None, format='columnar', print_flag=1):
        """Function for reading the data out of a file."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Equation type specific function setup.
        if format == 'xml':
            format = 'XML'
            self.read_function = self.relax.specific_setup.setup('read_xml_results', function_type)
        elif format == 'columnar':
            self.read_function = self.relax.specific_setup.setup('read_columnar_results', function_type)
        else:
            raise RelaxError, "Unknown format " + `format` + "."

        # No function.
        if not self.read_function:
            raise RelaxError, "The " + format + " format is not currently supported for " + self.relax.specific_setup.get_string(function_type) + "."

        # The directory.
        if directory == 'run':
            directory = run

        # Make sure that there are no data structures corresponding to the run.
        for data_name in dir(self.relax.data):
            # Get the object.
            data = getattr(self.relax.data, data_name)

            # Skip the data if it is not a dictionary (or equivalent).
            if not hasattr(data, 'has_key'):
                continue

            # Skip the data if it doesn't contain the key 'old_run'.
            if data.has_key(run):
                raise RelaxError, "Data corresponding to the run " + `run` + " exists."

        # Extract the data from the file.
        file_data = self.relax.IO.extract_data(file_name=file, dir=directory, file_data=file_data)

        # Strip data.
        file_data = self.relax.IO.strip(file_data)

        # Do nothing if the file does not exist.
        if not file_data:
            raise RelaxFileEmptyError

        # Read the results.
        self.read_function(run, file_data, print_flag)


    def write(self, run=None, file="results", directory=None, force=0, format='columnar', compress_type=1, print_flag=1):
        """Create the results file."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # The directory.
        if directory == 'run':
            directory = run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific results writing function.
        if format == 'xml':
            format = 'XML'
            self.write_function = self.relax.specific_setup.setup('write_xml_results', function_type, raise_error=0)
        elif format == 'columnar':
            self.write_function = self.relax.specific_setup.setup('write_columnar_results', function_type, raise_error=0)
        else:
            raise RelaxError, "Unknown format " + `format` + "."

        # No function.
        if not self.write_function:
            raise RelaxError, "The " + format + " format is not currently supported for " + self.relax.specific_setup.get_string(function_type) + "."

        # Open the file for writing.
        results_file = self.relax.IO.open_write_file(file_name=file, dir=directory, force=force, compress_type=compress_type, print_flag=print_flag)

        # Write the results.
        self.write_function(results_file, run)

        # Close the results file.
        results_file.close()
