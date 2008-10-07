###############################################################################
#                                                                             #
# Copyright (C) 2004-2005,2007-2008 Edward d'Auvergne                         #
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

# Python module imports.
from math import sqrt
from re import match

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import intensity, pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data, spin_loop
from relax_errors import RelaxArgNotInListError, RelaxError, RelaxInvalidDataError, RelaxNoSequenceError, RelaxRegExpError
from relax_io import open_write_file


class Noe:
    def __init__(self):
        """Class containing functions for relaxation data."""


    def assign_function(self, spin=None, intensity=None, spectrum_type=None):
        """Place the peak intensity data into the spin container.

        The intensity data can be either that of the reference or saturated spectrum.

        @keyword spin:          The spin container.
        @type spin:             SpinContainer instance
        @keyword intensity:     The intensity value.
        @type intensity:        float
        @keyword spectrum_type: The type of spectrum, one of 'ref' or 'sat'.
        @type spectrum_type:    str
        """

        # Add the data.
        if spectrum_type == 'ref':
            spin.ref = intensity
        elif spectrum_type == 'sat':
            spin.sat = intensity
        else:
            raise RelaxError, "The spectrum type '%s' is unknown." % spectrum_type


    def calculate(self, verbosity=1):
        """Calculate the NOE and its error.

        The error for each peak is calculated using the formula::
                          ___________________________________________
                       \/ {sd(sat)*I(unsat)}^2 + {sd(unsat)*I(sat)}^2
            sd(NOE) = -----------------------------------------------
                                          I(unsat)^2

        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        """

        # Test if the current pipe exists.
        pipes.test()

        # Loop over the spins.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Calculate the NOE.
            spin.noe = spin.sat / spin.ref

            # Calculate the error.
            spin.noe_err = sqrt((spin.sat_err * spin.ref)**2 + (spin.ref_err * spin.sat)**2) / spin.ref**2


    def overfit_deselect(self):
        """Deselect spins which have insufficient data to support calculation"""

        # Test the sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over spin data.
        for spin in spin_loop():
            # Check for sufficient data.
            if not (hasattr(spin, 'ref') and hasattr(spin, 'sat') and hasattr(spin, 'ref_err') and hasattr(spin, 'sat_err')):
                spin.select = False


    def read(self, file=None, dir=None, spectrum_type=None, format=None, heteronuc=None, proton=None, int_col=None):
        """Read in the peak intensity data.

        @keyword file:          The name of the file containing the peak intensities.
        @type file:             str
        @keyword dir:           The directory where the file is located.
        @type dir:              str
        @keyword spectrum_type: The type of spectrum, one of 'ref' or 'sat'.
        @type spectrum_type:    str
        @keyword format:        The type of file containing peak intensities.  This can currently be
                                one of 'sparky' or 'xeasy'.
        @type format:           str
        @keyword heteronuc:     The name of the heteronucleus as specified in the peak intensity
                                file.
        @type heteronuc:        str
        @keyword proton:        The name of the proton as specified in the peak intensity file.
        @type proton:           str
        @keyword int_col:       The column containing the peak intensity data (for a non-standard
                                formatted file).
        @type int_col:          int
        """

        # Spectrum type argument.
        spect_type_list = ['ref', 'sat']
        if spectrum_type not in spect_type_list:
            raise RelaxArgNotInListError, ('spectrum type', spectrum_type, spect_type_list)
        if spectrum_type == 'ref':
            print "Reference spectrum."
        if spectrum_type == 'sat':
            print "Saturated spectrum."

        # Generic intensity function.
        intensity.read(file=file, dir=dir, format=format, heteronuc=heteronuc, proton=proton, int_col=int_col, assign_func=self.assign_function, spectrum_type=spectrum_type)


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
            for j in xrange(len(ds.res[self.run])):
                if ds.res[self.run][j].num == res_num and ds.res[self.run][j].name == res_name:
                    index = j
                    break
            if index == None:
                raise RelaxError, "Residue " + `res_num` + " " + res_name + " cannot be found in the sequence."

            # Reassign data structure.
            data = ds.res[self.run][index]

            # Skip deselected residues.
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

        # Remap the data structure 'ds.res[run][i]'.
        data = ds.res[run][i]

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


    def set_error(self, error=0.0, spectrum_type=None, spin_id=None):
        """Set the peak intensity errors.

        @param error:           The peak intensity error value defined as the RMSD of the base plane
                                noise.
        @type error:            float
        @keyword spectrum_type: The type of spectrum, one of 'ref' or 'sat'.
        @type spectrum_type:    str
        @param spin_id:         The spin identification string.
        @type spin_id:          str
        """

        # Test if the current pipe exists
        pipes.test()

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over the spins.
        for spin in spin_loop(spin_id):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Set the error.
            if spectrum_type == 'ref':
                spin.ref_err = float(error)
            elif spectrum_type == 'sat':
                spin.sat_err = float(error)


    def write(self, run=None, file=None, dir=None, force=False):
        """Function for writing NOE values and errors to a file."""

        # Arguments
        self.run = run

        # Test if the current pipe exists.
        pipes.test()

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Open the file for writing.
        noe_file = open_write_file(file, dir, force)

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

        # Test if the current pipe exists.
        pipes.test()

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError


        # Header.
        #########


        # Write the header line.
        self.write_columnar_line(file=file, num='Num', name='Name', select='Selected', ref_int='Ref_intensity', ref_err='Ref_error', sat_int='Sat_intensity', sat_err='Sat_error', noe='NOE', noe_err='NOE_error')


        # Values.
        #########

        # Loop over the sequence.
        for i in xrange(len(ds.res[self.run])):
            # Reassign data structure.
            data = ds.res[self.run][i]

            # Deselected residues.
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
