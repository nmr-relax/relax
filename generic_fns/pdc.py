###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""Module for the reading of Bruker Protein Dynamics Centre (PDC) files."""

# Python module imports.
from re import search, split

# relax module imports.
from generic_fns import pipes
from generic_fns import value
from generic_fns.mol_res_spin import exists_mol_res_spin_data, name_spin, spin_loop
from generic_fns.relax_data import pack_data, peak_intensity_type
from relax_errors import RelaxError
from relax_io import extract_data


def get_relax_data(data):
    """Determine the relaxation data from the given PDC data.

    @param data:    The list of Tx, Tx error, and scaling factor for a given residue from the PDC file.
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


def get_res_num(data):
    """Determine the residue number from the given PDC data.

    @param data:    The list of residue info, split by whitespace, from the PDC file.
    @type data:     list of str
    """

    # Init.
    res_num = None

    # Loop over the list.
    for i in range(len(data)):
        # Split the data.
        row = split('([0-9]+)', data[i])

        # Loop over the new list.
        for j in range(len(row)):
            try:
                res_num = int(row[j])
            except ValueError:
                pass

    # Return the value.
    return ":%s" % res_num


def read(file=None, dir=None):
    """Read the PDC data file and place all the data into the relax data store.

    @keyword file:          The name of the file to open.
    @type file:             str
    @keyword dir:           The directory containing the file (defaults to the current directory if None).
    @type dir:              str or None
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Extract the data from the file.
    file_data = extract_data(file, dir)

    # Init.
    values = []
    errors = []
    res_nums = []

    # Loop over the data.
    in_ri_data = False
    for line in file_data:
        # The PDC version.
        if len(line) > 2 and line[0] == 'generated' and line[1] == 'by:':
            version = line[2]
            for i in range(len(line)-3):
                version = version + ' ' + line[i+3]

        # The data type.
        if len(line) == 3 and search('T1', line[2]):
            ri_label = 'R1'
        elif len(line) == 3 and search('T2', line[2]):
            ri_label = 'R2'
        elif len(line) == 4 and line[3] == 'NOE':
            ri_label = 'NOE'

        # Get the frequency.
        elif len(line) == 3 and line[0] == 'Proton' and line[1] == 'frequency[MHz]:':
            frq = float(line[2])
            frq_label = str(int(round(float(line[2])/10)*10))

        # Inside the relaxation data section.
        elif len(line) == 2 and line[0] == 'SECTION:' and line[1] == 'results':
            in_ri_data = True

        # The relaxation data.
        elif in_ri_data and line[0] != 'Peak':
            # Differences in the Rx and NOE files.
            if ri_label == 'NOE':
                index1 = -4
                index2 = -4
            else:
                index1 = -5
                index2 = -3

            # The residue info.
            res_nums.append(get_res_num(line[:index1]))

            # Get the relaxation data.
            if ri_label != 'NOE':
                rx, rx_err = get_relax_data(line[index2:])
            else:
                rx = float(line[-2])
                rx_err = float(line[-1])

            # Append the data.
            values.append(rx)
            errors.append(rx_err)

        # The temperature.
        elif len(line) == 3 and line[0] == 'Temperature':
            # Set the value (not implemented yet).
            pass

        # The labelling.
        elif len(line) == 2 and line[0] == 'Labelling:':
            # Set the heteronucleus value.
            value.set(line[1], 'heteronucleus')

            # Name the spins.
            name = split('([A-Z]+)', line[1])[1]
            name_spin(name=name)

        # The integration method.
        elif len(line) == 4 and line[0] == 'Used' and line[1] == 'integrals:':
            # Peak heights.
            if line[2] == 'peak' and line[3] == 'intensities':
                peak_intensity_type(ri_label=ri_label, frq_label=frq_label, type='height')

            # Peak volumes:
            if line[2] == 'area' and line[3] == 'integral':
                peak_intensity_type(ri_label=ri_label, frq_label=frq_label, type='volume')

    # Pack the data.
    pack_data(ri_label, frq_label, frq, values, errors, spin_ids=res_nums)
