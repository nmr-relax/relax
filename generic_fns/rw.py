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



class RW:
    def __init__(self, relax):
        """Class containing functions for reading and writing data."""

        self.relax = relax


    def read_results(self, run=None, data_type=None, file='results', directory=None, format='columnar'):
        """Function for reading the data out of a file."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Equation type specific function setup.
        if format == 'xml':
            format = 'XML'
            self.read_function = self.relax.specific_setup.setup('read_xml_results', data_type)
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
        file_data = self.relax.file_ops.extract_data(file_name=file, dir=directory)

        # Strip data.
        file_data = self.relax.file_ops.strip(file_data)

        # Do nothing if the file does not exist.
        if not file_data:
            raise RelaxFileEmptyError

        # Read the results.
        self.read_function(run, file, file_data)


    def write_results(self, run=None, file="results", directory=None, force=0, format='columnar', compress_type=1):
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
        results_file = self.relax.file_ops.open_write_file(file_name=file, dir=directory, force=force, compress_type=compress_type)

        # Write the results.
        self.write_function(results_file, run)

        # Close the results file.
        results_file.close()
