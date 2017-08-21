###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""relax script for regenerating the 'basic_single_pipe.bz2' saved state.

This is for when the saved state becomes incompatible with relax.
"""

# The relax data store.
from data_store import Relax_data_store; ds = Relax_data_store()


# Add a data pipe to the data store.
ds.add(pipe_name='orig', pipe_type='mf')

# Add a single object to the 'orig' data pipe.
ds['orig'].x = 1

# Add a single object to the storage object.
ds.y = 'Hello'

# Save the state.
state.save('basic_single_pipe', force=True)
