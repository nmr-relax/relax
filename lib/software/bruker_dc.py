###############################################################################
#                                                                             #
# Copyright (C) 2011-2013,2019 Edward d'Auvergne                              #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the reading of Bruker Dynamics Centre (DC) files."""

# Python module imports.
from re import search, split
from warnings import warn

# relax module imports.
from lib.errors import RelaxError
from lib.io import open_read_file
from lib.physical_constants import element_from_isotope
from lib.warnings import RelaxWarning


def convert_relax_data(data):
    """Determine the relaxation data from the given DC data.

    @param data:    The list of Tx, Tx error, and scaling factor for a given residue from the DC file.
    @type data:     list of str
    """

    # Convert the value from Tx to Rx.
    rx = 1.0 / float(data[0])

    # Remove the scaling.
    rx_err = float(data[1]) / float(data[2])

    # Convert the Tx error to an Rx error.
    rx_err = rx**2 * rx_err

    # Return the value and error.
    return rx, rx_err


def create_object(file=None, dir=None):
    """Parse the DC data file and create and return an object representation of the data.

    @keyword file:  The name of the file to open.
    @type file:     str
    @keyword dir:   The directory containing the file (defaults to the current directory if None).
    @type dir:      str or None
    @return:        The object representation of the Bruker DC file.
    @rtype:         DCObject instance
    """

    # Extract the data from the file.
    file_handle = open_read_file(file, dir)
    lines = file_handle.readlines()
    file_handle.close()

    # Create the object.
    obj = DCObject()
    obj.populate(lines)
    obj.process()

    # Return the object.
    return obj


def get_res_num(data):
    """Determine the residue number from the given DC data.

    @param data:    The list of residue info, split by whitespace, from the DC file.
    @type data:     list of str
    """

    # Init.
    res_num = None

    # Split the data.
    row = split('([0-9]+)', data)

    # Loop over the new list.
    for j in range(len(row)):
        try:
            res_num = int(row[j])
        except ValueError:
            pass

    # Return the value.
    return ":%s" % res_num



class DCObject:
    """An object representation of the Bruker DC file data."""

    def __init__(self):
        """Initialise the object."""

        # The dictionary of header information.
        self._header = {}

        # The sections of the file.
        self._sections = []

        # Initialise some structure.
        self.ri_type = None
        self.version = None


    def populate(self, lines):
        """Populate the object with the file data.

        @param lines:   The Bruker DC file data with each list element being a line of the data file.
        @type lines:    list of str
        """

        # Loop over the data.
        in_sections = False
        for i in range(len(lines)):
            # Check the file.
            if i == 0:
                if lines[0].strip() != "$##1.0":
                    raise RelaxError("Unknown file format, Bruker DC files must start with $##1.0 on the first line.")
                else:
                    continue

            # Split the line.
            row = split("\t", lines[i])

            # Strip the rubbish.
            for j in range(len(row)):
                row[j] = row[j].strip()

            # Skip empty lines.
            if len(row) == 0 or row == ['']:
                continue

            # Inside a new section.
            if row[0] == "SECTION:":
                # No longer in the header.
                in_sections = True

                # Create a new section.
                if row[1] == "sample information":
                    self.sample_information = DCSampleInfo()
                    self._sections.append(self.sample_information)
                elif row[1] == "relevant parameters":
                    self.parameters = DCParams()
                    self._sections.append(self.parameters)
                elif row[1] == "integrals":
                    self.intensities = DCIntegrals(err=False, bc=False)
                    self._sections.append(self.intensities)
                elif row[1] == "integral errors":
                    self.intensity_errors = DCIntegrals(err=True, bc=False)
                    self._sections.append(self.intensity_errors)
                elif row[1] == "integrals back calculated from fit":
                    self.intensities_bc = DCIntegrals(err=True, bc=True)
                    self._sections.append(self.intensities_bc)
                elif row[1] == "details":
                    self.details = DCDetails()
                    self._sections.append(self.details)
                elif row[1] == "results":
                    self.results = DCResults()
                    self._sections.append(self.results)

                # Unknown section.
                else:
                    warn(RelaxWarning("The Bruker DC file section \"%s\" is unknown." % row[1]))

            # Store the header info.
            if not in_sections:
                self._header[row[0]] = row[1]

            # Or store the section info.
            else:
                self._sections[-1].add(row)


    def process(self):
        """Process the Bruker DC data already present in the object."""

        # Experiment type.
        if search('T1', self._header['Project:']):
            self.ri_type = 'R1'
        elif search('T2', self._header['Project:']):
            self.ri_type = 'R2'
        elif search('NOE', self._header['Project:']):
            self.ri_type = 'NOE'

        # The DC version.
        if 'generated by:' in self._header:
            self.version = self._header['generated by:']

        # Loop over the sections.
        for section in self._sections:
            section.process()



class DCSection(object):
    """Base class for the various Bruker DC sections."""

    def __init__(self):
        """Initialise the Bruker DC section object."""

        # The file data.
        self._data = []


    def add(self, elements):
        """Store the data.

        @param elements:    The Bruker DC file line split by tabs, with whitespace removed.
        @type elements:     list of str
        """

        # Skip the section line.
        if elements[0] == "SECTION:":
            return

        # Store the data.
        self._data.append(elements)



class DCDetails(DCSection):
    """Class for the Bruker DC analysis information."""

    def __init__(self):
        """Initialise the Bruker DC section object."""

        # Initialise the base class.
        super(DCDetails, self).__init__()

        # Initialise some structures.
        self.int_type = None


    def process(self):
        """Process the Bruker DC data already present in the section object."""

        # Loop over the data.
        for i in range(len(self._data)):
            # Check for bad errors.
            if self._data[i][0] == 'Systematic error estimation of data:':
                # Badness.
                if self._data[i][1] == 'worst case per peak scenario':
                    raise RelaxError("The errors estimation method \"worst case per peak scenario\" is not suitable for model-free analysis.  Please go back to the DC and switch to \"average variance calculation\".")

            # Extract the integration method.
            if self._data[i][0] == 'Used integrals:':
                # Peak heights.
                if self._data[i][1] == 'peak intensities':
                    self.int_type = 'height'

                # Peak volumes:
                if self._data[i][1] == 'area integral':
                    self.int_type = 'volume'



class DCIntegrals(DCSection):
    """Class for the Bruker DC peak intensity information."""

    def __init__(self, err=False, bc=False):
        """Initialise the Bruker DC section object.

        @keyword err:   A flag which if True means that the data if for the peak intensity errors.
        @type err:      bool
        @keyword bc:    A flag which if True means that this is the back-calculated peak intensity data.
        @type bc:       bool
        """

        # Initialise the base class.
        super(DCIntegrals, self).__init__()

        # Store the peak intensity type info.
        self.err = err
        self.bc = bc

        # Initialise some structures.
        self.ids = []
        self.relaxation_time = []
        self.peak_intensity = {}


    def process(self):
        """Process the Bruker DC data already present in the section object."""

        # Loop over the data.
        for i in range(len(self._data)):
            # The mixing times.
            if self._data[i][0] == 'Mixing time [s]:':
                for j in range(1, len(self._data[i])):
                    self.relaxation_time.append(float(self._data[i][j]))

            # The spectra names.
            elif self._data[i][0] == 'Peak name':
                for j in range(1, len(self._data[i])):
                    self.ids.append(self._data[i][j])

            # The peak intensities.
            else:
                # The residue info.
                res_num = get_res_num(self._data[i][0])
                if res_num not in self.peak_intensity:
                    self.peak_intensity[res_num] = []

                # Store the data.
                for j in range(1, len(self._data[i])):
                    self.peak_intensity[res_num].append(float(self._data[i][j]))



class DCParams(DCSection):
    """Class for the Bruker DC parameter information."""

    def process(self):
        """Process the Bruker DC data already present in the section object."""

        # Loop over the data.
        for i in range(len(self._data)):
            # Get the frequency, converting to Hz.
            if self._data[i][0] == 'Proton frequency[MHz]:':
                self.frq = float(self._data[i][1]) * 1e6



class DCResults(DCSection):
    """Class for the Bruker DC results."""

    def __init__(self):
        """Initialise the Bruker DC section object."""

        # Initialise the base class.
        super(DCResults, self).__init__()

        # Initialise some structures.
        self.sequence = []
        self.f1 = {}
        self.f2 = {}
        self.I0 = {}
        self.I0_err = {}
        self.Tx = {}
        self.Tx_err = {}
        self.Tx_err_scale = {}
        self.Rx = {}
        self.Rx_err = {}
        self.fit_info = {}

        # Data indices.
        self.indices = {
            'f1': None,
            'f2': None,
            'I0': None,
            'I0_err': None,
            'Tx': None,
            'Tx_err': None,
            'Tx_err_scale': None,
            'Rx': None,
            'Rx_err': None,
            'fit_info': None
        }


    def process(self):
        """Process the Bruker DC data already present in the section object."""

        # Loop over the data.
        for i in range(len(self._data)):
            # The metadata.
            if self._data[i][0] == 'Peak name':
                for j in range(1, len(self._data[i])):
                    if self._data[i][j] == 'F1 [ppm]':
                        self.indices['f1'] = j
                    elif self._data[i][j] == 'F2 [ppm]':
                        self.indices['f2'] = j
                    elif self._data[i][j] == 'Io':
                        self.indices['I0'] = j
                    elif self._data[i][j] == 'error' and self._data[i][j-1] == 'Io':
                        self.indices['I0_err'] = j
                    elif self._data[i][j] in ['T1 [s]', 'T2 [s]']:
                        self.indices['Tx'] = j
                    elif self._data[i][j] == 'error' and self._data[i][j-1] in ['T1 [s]', 'T2 [s]']:
                        self.indices['Tx_err'] = j
                    elif self._data[i][j] == 'errorScale' and self._data[i][j-2] in ['T1 [s]', 'T2 [s]']:
                        self.indices['Tx_err_scale'] = j
                    elif self._data[i][j] in ['R1 [rad/s]', 'R2 [rad/s]', 'NOE', 'NOE [none]']:
                        self.indices['Rx'] = j
                    elif self._data[i][j] in ['R1 sd [rad/s]', 'R2 sd [rad/s]']:
                        self.indices['Rx_err'] = j
                    elif self._data[i][j] == 'error' and self._data[i][j-1] in ['NOE', 'NOE [none]']:
                        self.indices['Rx_err'] = j
                    elif self._data[i][j] == 'fitInfo':
                        self.indices['fit_info'] = j

                # Catch old PDC files (to fix https://web.archive.org/web/https://gna.org/bugs/?20152).
                if self.indices['Rx'] == None:
                    raise RelaxError("The old Protein Dynamics Center (PDC) files with relaxation times but no relaxation rates are not supported.")

            # The relaxation data.
            else:
                # The residue info.
                res_id = get_res_num(self._data[i][0])
                self.sequence.append(res_id)

                # Store the data.
                if self.indices['f1'] != None:
                    self.f1[res_id] = float(self._data[i][self.indices['f1']])
                if self.indices['f2'] != None:
                    self.f2[res_id] = float(self._data[i][self.indices['f2']])
                if self.indices['I0'] != None:
                    self.I0[res_id] = float(self._data[i][self.indices['I0']])
                if self.indices['I0_err'] != None:
                    self.I0_err[res_id] = float(self._data[i][self.indices['I0_err']])
                if self.indices['Tx'] != None:
                    self.Tx[res_id] = float(self._data[i][self.indices['Tx']])
                if self.indices['Tx_err'] != None:
                    self.Tx_err[res_id] = float(self._data[i][self.indices['Tx_err']])
                if self.indices['Tx_err_scale'] != None:
                    self.Tx_err_scale[res_id] = float(self._data[i][self.indices['Tx_err_scale']])
                if self.indices['Rx'] != None:
                    self.Rx[res_id] = float(self._data[i][self.indices['Rx']])
                if self.indices['Rx_err'] != None:
                    self.Rx_err[res_id] = float(self._data[i][self.indices['Rx_err']])
                if self.indices['fit_info'] != None:
                    self.fit_info[res_id] = self._data[i][self.indices['fit_info']]



class DCSampleInfo(DCSection):
    """Class for the Bruker DC sample information."""

    def process(self):
        """Process the Bruker DC data already present in the section object."""

        # Loop over the data.
        for i in range(len(self._data)):
            # The labelling.
            if self._data[i][0] == 'Labelling:':
                # The spin isotope.
                self.isotope = self._data[i][1]

                # The name of the spins.
                self.spin_name = split('([A-Z]+)', self._data[i][1])[1]

                # The atom name.
                self.atom_name = element_from_isotope(self.isotope)
