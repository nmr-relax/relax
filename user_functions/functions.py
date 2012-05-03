###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""The module of all user function details."""

# relax module imports.
from user_functions.objects import Container
from user_functions import Uf_info; uf_info = Uf_info()


# The pipe user functions.
##########################

# The user function class.
uf_class = uf_info.add_class('pipe')
uf_class.title = "Class for holding the user functions for manipulating data pipes."

# The pipe.copy user function.
uf = uf_info.add_uf('pipe.copy')
uf.title = "Copy a data pipe."
uf.title_short = "Data pipe copying."
uf.add_arg("pipe_from", "The name of the source data pipe to copy the data from.")
uf.add_arg("pipe_to", "The name of the target data pipe to copy the data to.")
uf.desc = """
This allows the contents of a data pipe to be copied.  If the source data pipe is not set, the current data pipe will be assumed.  The target data pipe must not yet exist.
"""
uf.prompt_examples = """
To copy the contents of the 'm1' data pipe to the 'm2' data pipe, type:

relax> pipe.copy('m1', 'm2')
relax> pipe.copy(pipe_from='m1', pipe_to='m2')

If the current data pipe is 'm1', then the following command can be used:

relax> pipe.copy(pipe_to='m2')
"""
