###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
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
"""Module containing the 'pipe' user function data."""

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
from generic_fns import pipes
from relax_errors import RelaxError
from specific_fns.setup import hybrid_obj
from user_functions.objects import Container
from user_functions import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('pipe')
uf_class.title = "Class for holding the user functions for manipulating data pipes."

# The pipe.copy user function.
uf = uf_info.add_uf('pipe.copy')
uf.title = "Copy a data pipe."
uf.title_short = "Data pipe copying."
uf.add_keyarg(name="pipe_from", default=None, py_type="str", desc_short="pipe from", desc="The name of the source data pipe to copy the data from.", can_be_none=True)
uf.add_keyarg(name="pipe_to", default=None, py_type="str", desc_short="pipe to", desc="The name of the target data pipe to copy the data to.", can_be_none=True)
uf.backend = 'generic_fns.pipes.copy'
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

# The pipe.create user function.
uf = uf_info.add_uf('pipe.create')
uf.title = "Add a new data pipe to the relax data store."
uf.title_short = "Data pipe creation."
uf.add_keyarg(name="pipe_name", default=None, py_type="str", desc_short="data pipe name", desc="The name of the data pipe.")
uf.add_keyarg(name="pipe_type", default=None, py_type="str", desc_short="data pipe type", desc="The type of data pipe.")
uf.backend = 'generic_fns.pipes.create'
uf.desc = """
The data pipe name can be any string however the data pipe type can only be one of the following:

    'ct':  Consistency testing,
    'frame order':  The Frame Order theories,
    'jw':  Reduced spectral density mapping,
    'hybrid':  A special hybrid pipe,
    'mf':  Model-free analysis,
    'N-state':  N-state model of domain motions,
    'noe':  Steady state NOE calculation,
    'relax_fit':  Relaxation curve fitting,
"""
uf.prompt_examples = """
To set up a model-free analysis data pipe with the name 'm5', type:

relax> pipe.create('m5', 'mf')
"""

# The pipe.current user function.
uf = uf_info.add_uf('pipe.current')
uf.title = "Print the name of the current data pipe."
uf.title_short = "Current data pipe printing."
uf.backend = 'generic_fns.pipes.current'
uf.prompt_examples = """
To run the user function, type:

relax> pipe.current()
"""

# The pipe.delete user function.
uf = uf_info.add_uf('pipe.delete')
uf.title = "Delete a data pipe from the relax data store."
uf.title_short = "Data pipe deletion."
uf.add_keyarg(name="pipe_name", default=None, py_type="str", desc_short="data pipe name", desc="The name of the data pipe to delete.", can_be_none=True)
uf.backend = 'generic_fns.pipes.delete'
uf.desc = """
This will permanently remove the data pipe and all of its contents from the relax data store.  If the pipe name is not given, then all data pipes will be deleted.
"""

# The pipe.display user function.
uf = uf_info.add_uf('pipe.display')
uf.title = "Print a list of all the data pipes."
uf.title_short = "Data pipe listing."
uf.backend = 'generic_fns.pipes.display'
uf.prompt_examples = """
To run the user function, type:

relax> pipe.display()
"""

# The pipe.hybridise user function.
uf = uf_info.add_uf('pipe.hybridise')
uf.title = "Create a hybrid data pipe by fusing a number of other data pipes."
uf.title_short = "Hybrid data pipe creation."
uf.add_keyarg(name="hybrid", default=None, py_type="str", desc_short="hybrid pipe name", desc="The name of the hybrid data pipe to create.")
uf.add_keyarg(name="pipes", default=None, py_type="str_list", desc_short="data pipes", desc="An array containing the names of all data pipes to hybridise.")
uf.backend = 'specific_fns.setup.hybrid_obj._hybridise'
uf.desc = """
This user function can be used to construct hybrid models.  An example of the use of a hybrid model could be if the protein consists of two independent domains.  These two domains could be analysed separately, each having their own optimised diffusion tensors.  The N-terminal domain data pipe could be called 'N_sphere' while the C-terminal domain could be called 'C_ellipsoid'.  These two data pipes could then be hybridised into a single data pipe.  This hybrid data pipe can then be compared via model selection to a data pipe whereby the entire protein is assumed to have a single diffusion tensor.

The requirements for data pipes to be hybridised is that the molecules, sequences, and spin systems for all the data pipes is the same, and that no spin system is allowed to be selected in two or more data pipes.  The selections must not overlap to allow for rigorous statistical comparisons.
"""
uf.prompt_examples = """
The two data pipes 'N_sphere' and 'C_ellipsoid' could be hybridised into a single data pipe
called 'mixed model' by typing:

relax> pipe.hybridise('mixed model', ['N_sphere', 'C_ellipsoid'])
relax> pipe.hybridise(hybrid='mixed model', pipes=['N_sphere', 'C_ellipsoid'])
"""

# The pipe.switch user function.
uf = uf_info.add_uf('pipe.switch')
uf.title = "Switch between the data pipes of the relax data store."
uf.title_short = "Data pipe switching."
uf.add_keyarg(name="pipe_name", default=None, py_type="str", desc_short="data pipe name", desc="The name of the data pipe."]
uf.backend = 'generic_fns.pipes.switch'
uf.desc = """
This will switch between the various data pipes within the relax data store.
"""
uf.prompt_examples = """
To switch to the 'ellipsoid' data pipe, type:

relax> pipe.switch('ellipsoid')
relax> pipe.switch(pipe_name='ellipsoid')
"""
