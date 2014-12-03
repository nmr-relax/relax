###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""Module for the using of pipe_control.io."""

# relax module imports.
from lib.errors import RelaxError
from pipe_control.pipes import check_pipe


def add_io_data(object_name=None, io_id=None, io_data=None):
    """Add the io data to the data store under the the given object_name within a dictionary with io_id key.

    @keyword object_name:   The object name for where to store the data.  As cdp.object_name.
    @type object_name:      str
    @keyword io_id:         The dictionary key, to access the data.  As As cdp.object_name['io_id']
    @type io_id:            str
    @keyword io_data:       The type of data depending on called function.
    @type io_data:          depend on function
    """

    # Initialise the structure, if needed.
    if not hasattr(cdp, object_name):
        setattr(cdp, object_name, {})

    # Add the data under the dictionary key.
    obj_dict = getattr(cdp, object_name)
    obj_dict[io_id] = io_data
