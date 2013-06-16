###############################################################################
#                                                                             #
# Copyright (C) 2011-2013 Edward d'Auvergne                                   #
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
from lib.software.bruker_dc import parse_file
from pipe_control import pipes
from pipe_control.exp_info import software_select
from pipe_control.mol_res_spin import exists_mol_res_spin_data, name_spin
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
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Extract the data from the file.
    values, errors, res_nums, int_type, frq, ri_type, spin_name, isotope, version = parse_file(file=file, dir=dir)

    # Name the spins if needed.
    name_spin(name=spin_name, force=False)

    # Modify the residue numbers by adding the heteronucleus name.
    if isotope:
        atom_name = element_from_isotope(isotope)
        for i in range(len(res_nums)):
            res_nums[i] += '@' + atom_name

    # Pack the data.
    pack_data(ri_id, ri_type, frq, values, errors, spin_ids=res_nums)

    # Set the integration method.
    peak_intensity_type(ri_id=ri_id, type=int_type)

    # Set the DC as used software.
    software_select('Bruker DC', version=version)
