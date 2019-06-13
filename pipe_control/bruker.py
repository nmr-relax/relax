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

# relax module imports.
from lib.errors import RelaxNoSequenceError
from lib.physical_constants import element_from_isotope
from lib.software.bruker_dc import create_object
from pipe_control.exp_info import software_select
from pipe_control.mol_res_spin import exists_mol_res_spin_data, name_spin
from pipe_control.pipes import check_pipe
from pipe_control.relax_data import pack_data, peak_intensity_type


def read(ri_id=None, file=None, dir=None):
    """Read the DC data file and place all the data into the relax data store.

    @keyword ri_id: The relaxation data ID string.
    @type ri_id:    str
    @keyword file:  The name of the file to open.
    @type file:     str
    @keyword dir:   The directory containing the file (defaults to the current directory if None).
    @type dir:      str or None
    """

    # Test if the current pipe exists.
    check_pipe()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Extract the data from the file.
    dc_object = create_object(file=file, dir=dir)

    # Name the spins if needed.
    name_spin(name=dc_object.sample_information.spin_name, force=False, warn_flag=False)

    # Pack the data.
    values = []
    errors = []
    spin_ids = []
    for res_id in dc_object.results.sequence:
        spin_ids.append('%s@%s' % (res_id, dc_object.sample_information.atom_name))
        values.append(dc_object.results.Rx[res_id])
        errors.append(dc_object.results.Rx_err[res_id])
    pack_data(ri_id, dc_object.ri_type, dc_object.parameters.frq, values, errors, spin_ids=spin_ids)

    # Set the integration method.
    peak_intensity_type(ri_id=ri_id, type=dc_object.details.int_type)

    # Set the DC as used software.
    software_select('Bruker DC', version=dc_object.version)
