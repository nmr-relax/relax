###############################################################################
#                                                                             #
# Copyright (C) 2004-2005 Edward d'Auvergne                                   #
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

from math import sqrt
from re import match


class Noe:
    def __init__(self, relax):
        """Class containing functions for relaxation data."""

        self.relax = relax


    def assign_function(self, run=None, i=None, intensity=None):
        """Function for assigning peak intensity data to either the reference or saturated spectra."""

        # Add the data.
        if self.spectrum_type == 'ref':
            self.relax.data.res[run][i].ref = intensity
        elif self.spectrum_type == 'sat':
            self.relax.data.res[run][i].sat = intensity


    def calculate(self, run=None, print_flag=1):
        """Function for calculating the NOE and its error.

        The error for each peak is calculated using the formula:
                          ___________________________________________
                       \/ {sd(sat)*I(unsat)}^2 + {sd(unsat)*I(sat)}^2
            sd(NOE) = -----------------------------------------------
                                          I(unsat)^2
        """

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # Calculate the NOE.
            data.noe = data.sat / data.ref

            # Calculate the error.
            data.noe_err = sqrt((data.sat_err * data.ref)**2 + (data.ref_err * data.sat)**2) / data.ref**2


    def overfit_deselect(self, run):
        """Function for deselecting residues without sufficient data to support calculation"""

        # Test the sequence data exists:
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Loop over residue data:
        for residue in self.relax.data.res[run]:

            # Check for sufficient data.
            if not (hasattr(residue, 'ref') and hasattr(residue, 'sat') and hasattr(residue, 'ref_err') and hasattr(residue, 'sat_err')):
                residue.select = 0
                continue


    def read(self, run=None, file=None, dir=None, spectrum_type=None, format=None, heteronuc=None, proton=None, int_col=None):
        """Function for reading peak intensity data."""

        # Arguments.
        self.run = run
        self.spectrum_type = spectrum_type

        # Spectrum type argument.
        spect_type_list = ['ref', 'sat']
        if self.spectrum_type not in spect_type_list:
            raise RelaxArgNotInListError, ('spectrum type', self.spectrum_type, spect_type_list)
        if self.spectrum_type == 'ref':
            print "Reference spectrum."
        if self.spectrum_type == 'sat':
            print "Saturated spectrum."

        # Generic intensity function.
        self.relax.generic.intensity.read(run=run, file=file, dir=dir, format=format, heteronuc=heteronuc, proton=proton, int_col=int_col, assign_func=self.assign_function)


    def read_columnar_results(self, run, file_data):
        """Function for reading the results file."""

        # Arguments.
        self.run = run

        # Extract and remove the header.
        header = file_data[0]
        file_data = file_data[1:]

        # Sort the column numbers.
        col = {}
        for i in xrange(len(header)):
            if header[i] == 'Num':
                col['num'] = i
            elif header[i] == 'Name':
                col['name'] = i
            elif header[i] == 'Selected':
                col['select'] = i
            elif header[i] == 'Ref_intensity':
                col['ref_int'] = i
            elif header[i] == 'Ref_error':
                col['ref_err'] = i
            elif header[i] == 'Sat_intensity':
                col['sat_int'] = i
            elif header[i] == 'Sat_error':
                col['sat_err'] = i
            elif header[i] == 'NOE':
                col['noe'] = i
            elif header[i] == 'NOE_error':
                col['noe_err'] = i

        # Test the file.
        if len(col) < 2:
            raise RelaxInvalidDataError


        # Sequence.
        ###########

        # Generate the sequence.
        for i in xrange(len(file_data)):
            # Residue number and name.
            try:
                res_num = int(file_data[i][col['num']])
            except ValueError:
                raise RelaxError, "The residue number " + file_data[i][col['num']] + " is not an integer."
            res_name = file_data[i][col['name']]

            # Add the residue.
            self.relax.generic.sequence.add(self.run, res_num, res_name, select=int(file_data[i][col['select']]))


        # Data.
        #######

        # Loop over the file data.
        for i in xrange(len(file_data)):
            # Residue number and name.
            try:
                res_num = int(file_data[i][col['num']])
            except ValueError:
                raise RelaxError, "The residue number " + file_data[i][col['num']] + " is not an integer."
            res_name = file_data[i][col['name']]

            # Find the residue index.
            index = None
            for j in xrange(len(self.relax.data.res[self.run])):
                if self.relax.data.res[self.run][j].num == res_num and self.relax.data.res[self.run][j].name == res_name:
                    index = j
                    break
            if index == None:
                raise RelaxError, "Residue " + `res_num` + " " + res_name + " cannot be found in the sequence."

            # Reassign data structure.
            data = self.relax.data.res[self.run][index]

            # Skip unselected residues.
            if not data.select:
                continue

            # Reference intensity.
            try:
                data.ref = float(file_data[i][col['ref_int']])
            except ValueError:
                data.ref = None

            # Reference error.
            try:
                data.ref_err = float(file_data[i][col['ref_err']])
            except ValueError:
                data.ref_err = None

            # Saturated intensity.
            try:
                data.sat = float(file_data[i][col['sat_int']])
            except ValueError:
                data.sat = None

            # Saturated error.
            try:
                data.sat_err = float(file_data[i][col['sat_err']])
            except ValueError:
                data.sat_err = None

            # NOE.
            try:
                data.noe = float(file_data[i][col['noe']])
            except ValueError:
                data.noe = None

            # NOE error.
            try:
                data.noe_err = float(file_data[i][col['noe_err']])
            except ValueError:
                data.noe_err = None


    def return_conversion_factor(self, stat_type):
        """Dummy function for returning 1.0."""

        return 1.0


    def return_data_name(self, name):
        """
        NOE calculation data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |              |                                                  |
        | Data type              | Object name  | Patterns                                         |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Reference intensity    | 'ref'        | '^[Rr]ef$' or '[Rr]ef[ -_][Ii]nt'                |
        |                        |              |                                                  |
        | Saturated intensity    | 'sat'        | '^[Ss]at$' or '[Ss]at[ -_][Ii]nt'                |
        |                        |              |                                                  |
        | NOE                    | 'noe'        | '^[Nn][Oo][Ee]$'                                 |
        |________________________|______________|__________________________________________________|

        """

        # Reference intensity.
        if match('^[Rr]ef$', name) or match('[Rr]ef[ -_][Ii]nt', name):
            return 'ref'

        # Saturated intensity.
        if match('^[Ss]at$', name) or match('[Ss]at[ -_][Ii]nt', name):
            return 'sat'

        # NOE.
        if match('^[Nn][Oo][Ee]$', name):
            return 'noe'


    def return_grace_string(self, data_type):
        """Function for returning the Grace string representing the data type for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # Reference intensity.
        if object_name == 'ref':
            grace_string = 'Reference intensity'

        # Saturated intensity.
        if object_name == 'sat':
            grace_string = 'Saturated intensity'

        # NOE.
        if object_name == 'noe':
            grace_string = '\\qNOE\\Q'

        # Return the Grace string.
        return grace_string


    def return_units(self, stat_type):
        """Dummy function which returns None as the stats have no units."""

        return None


    def return_value(self, run, i, data_type='noe'):
        """Function for returning the NOE value and error."""

        # Arguments.
        self.run = run

        # Remap the data structure 'self.relax.data.res[run][i]'.
        data = self.relax.data.res[run][i]

        # Get the object.
        object_name = self.return_data_name(data_type)
        if not object_name:
            raise RelaxError, "The NOE calculation data type " + `data_type` + " does not exist."
        object_error = object_name + "_err"

        # Get the value.
        value = None
        if hasattr(data, object_name):
            value = getattr(data, object_name)

        # Get the error.
        error = None
        if hasattr(data, object_error):
            error = getattr(data, object_error)

        # Return the data.
        return value, error


    def set_error(self, run=None, error=0.0, spectrum_type=None, res_num=None, res_name=None):
        """Function for setting the errors."""

        # Arguments.
        self.run = run
        self.spectrum_type = spectrum_type
        self.res_num = res_num
        self.res_name = res_name

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Test if the residue number is a valid regular expression.
        if type(res_num) == str:
            try:
                compile(res_num)
            except:
                raise RelaxRegExpError, ('residue number', res_num)

        # Test if the residue name is a valid regular expression.
        if res_name:
            try:
                compile(res_name)
            except:
                raise RelaxRegExpError, ('residue name', res_name)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # If 'res_num' is not None, skip the residue if there is no match.
            if type(res_num) == int and not data.num == res_num:
                continue
            elif type(res_num) == str and not match(res_num, `data.num`):
                continue

            # If 'res_name' is not None, skip the residue if there is no match.
            if res_name != None and not match(res_name, data.name):
                continue

            # Set the error.
            if self.spectrum_type == 'ref':
                data.ref_err = float(error)
            elif self.spectrum_type == 'sat':
                data.sat_err = float(error)


    def write(self, run=None, file=None, dir=None, force=0):
        """Function for writing NOE values and errors to a file."""

        # Arguments
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Open the file for writing.
        noe_file = self.relax.IO.open_write_file(file, dir, force)

        # Write the data.
        self.relax.generic.value.write_data(self.run, None, noe_file, return_value=self.return_value)

        # Close the file.
        noe_file.close()


    def write_columnar_line(self, file=None, num=None, name=None, select=None, ref_int=None, ref_err=None, sat_int=None, sat_err=None, noe=None, noe_err=None):
        """Function for printing a single line of the columnar formatted results."""

        # Residue number and name.
        file.write("%-4s %-5s " % (num, name))

        # Selected flag and data set.
        file.write("%-9s " % select)
        if not select:
            file.write("\n")
            return

        # Reference and saturated data.
        file.write("%-25s %-25s " % (ref_int, ref_err))
        file.write("%-25s %-25s " % (sat_int, sat_err))

        # NOE and error.
        file.write("%-25s %-25s " % (noe, noe_err))

        # End of the line.
        file.write("\n")


    def write_columnar_results(self, file, run):
        """Function for printing the results into a file."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run


        # Header.
        #########


        # Write the header line.
        self.write_columnar_line(file=file, num='Num', name='Name', select='Selected', ref_int='Ref_intensity', ref_err='Ref_error', sat_int='Sat_intensity', sat_err='Sat_error', noe='NOE', noe_err='NOE_error')


        # Values.
        #########

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Reassign data structure.
            data = self.relax.data.res[self.run][i]

            # Unselected residues.
            if not data.select:
                self.write_columnar_line(file=file, num=data.num, name=data.name, select=0)
                continue

            # Reference intensity.
            ref_int = None
            if hasattr(data, 'ref'):
                ref_int = data.ref

            # Reference error.
            ref_err = None
            if hasattr(data, 'ref_err'):
                ref_err = data.ref_err

            # Saturated intensity.
            sat_int = None
            if hasattr(data, 'sat'):
                sat_int = data.sat

            # Saturated error.
            sat_err = None
            if hasattr(data, 'sat_err'):
                sat_err = data.sat_err

            # NOE
            noe = None
            if hasattr(data, 'noe'):
                noe = data.noe

            # NOE error.
            noe_err = None
            if hasattr(data, 'noe_err'):
                noe_err = data.noe_err

            # Write the line.
            self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, ref_int=ref_int, ref_err=ref_err, sat_int=sat_int, sat_err=sat_err, noe=noe, noe_err=noe_err)
