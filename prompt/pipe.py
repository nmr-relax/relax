###############################################################################
#                                                                             #
# Copyright (C) 2004-2011 Edward d'Auvergne                                   #
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
"""Module containing the 'pipe' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from generic_fns import pipes
from relax_errors import RelaxError
from specific_fns.setup import hybrid_obj


class Pipe(User_fn_class):
    """Class for holding the functions for manipulating data pipes."""

    def copy(self, pipe_from=None, pipe_to=None):
        """Function for copying a data pipe.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The name of the source data pipe to copy the data from.

        pipe_to:  The name of the target data pipe to copy the data to.


        Description
        ~~~~~~~~~~~

        This user function allows the contents of a data pipe to be copied.  If the 'pipe_from'
        keyword argument is set to None the current data pipe is assumed.  The data pipe
        corresponding to 'pipe_to' must not yet exist.


        Examples
        ~~~~~~~~

        To copy the contents of the 'm1' data pipe to the 'm2' data pipe, type:

        relax> pipe.copy('m1', 'm2')
        relax> pipe.copy(pipe_from='m1', pipe_to='m2')

        If the current data pipe is 'm1', then the following command can be used:

        relax> pipe.copy(pipe_to='m2')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "pipe.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", pipe_to=" + repr(pipe_to) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(pipe_from, 'pipe from', can_be_none=True)
        arg_check.is_str(pipe_to, 'pipe to', can_be_none=True)

        # Both pipe arguments cannot be None.
        if pipe_from == None and pipe_to == None:
            raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")

        # Execute the functional code.
        pipes.copy(pipe_from=pipe_from, pipe_to=pipe_to)


    def create(self, pipe_name=None, pipe_type=None):
        """Function for initialising a data pipe.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_name:  The name of the data pipe.

        pipe_type:  The type of data pipe.


        Description
        ~~~~~~~~~~~

        The data pipe name can be any string however the data pipe type can only be one of the
        following:

            'frame order':  The Frame Order theories,
            'jw':  Reduced spectral density mapping,
            'mf':  Model-free analysis,
            'N-state':  N-state model of domain motions,
            'noe':  Steady state NOE calculation,
            'relax_disp':  Relaxation dispersion curve fitting,
            'relax_fit':  Relaxation curve fitting,


        Examples
        ~~~~~~~~

        To set up a model-free analysis data pipe with the name 'm5', type:

        relax> pipe.create('m5', 'mf')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "pipe.create("
            text = text + "pipe_name=" + repr(pipe_name)
            text = text + ", pipe_type=" + repr(pipe_type) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(pipe_name, 'data pipe name')
        arg_check.is_str(pipe_type, 'data pipe type')

        # Execute the functional code.
        pipes.create(pipe_name=pipe_name, pipe_type=pipe_type)


    def current(self):
        """Print the name of the current pipe.

        Examples
        ~~~~~~~~

        To run the user function, type:

        relax> pipe.current()
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "pipe.current()"
            print(text)

        # Execute the functional code.
        pipes.current()


    def delete(self, pipe_name=None):
        """Function for deleting a data pipe.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_name:  The name of the data pipe.


        Description
        ~~~~~~~~~~~

        This function will permanently remove the data pipe and all of its contents.  If the pipe
        name is not given, then all data pipes will be deleted.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "pipe.delete("
            text = text + "pipe_name=" + repr(pipe_name) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(pipe_name, 'data pipe name', can_be_none=True)

        # Execute the functional code.
        pipes.delete(pipe_name=pipe_name)


    def display(self):
        """Print a list of all the data pipes.

        Examples
        ~~~~~~~~

        To run the user function, type:

        relax> pipe.display()
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "pipe.display()"
            print(text)

        # Execute the functional code.
        pipes.display()


    def hybridise(self, hybrid=None, pipes=None):
        """Create a hybrid data pipe by fusing a number of other data pipes.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        hybrid:  The name of the hybrid data pipe to create.

        pipes:  An array containing the names of all data pipes to hybridise.


        Description
        ~~~~~~~~~~~

        This user function can be used to construct hybrid models.  An example of the use of a
        hybrid model could be if the protein consists of two independent domains.  These two domains
        could be analysed separately, each having their own optimised diffusion tensors.  The
        N-terminal domain data pipe could be called 'N_sphere' while the C-terminal domain could be
        called 'C_ellipsoid'.  These two data pipes could then be hybridised into a single data pipe
        called 'mixed model' by typing:

        relax> pipe.hybridise('mixed model', ['N_sphere', 'C_ellipsoid'])
        relax> pipe.hybridise(hybrid='mixed model', pipes=['N_sphere', 'C_ellipsoid'])

        This hybrid data pipe can then be compared via model selection to a data pipe whereby the
        entire protein is assumed to have a single diffusion tensor.

        The requirements for data pipes to be hybridised is that the molecules, sequences, and spin
        systems for all the data pipes is the same, and that no spin system is allowed to be
        selected in two or more data pipes.  The selections must not overlap to allow for
        rigorous statistical comparisons.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "pipe.hybridise("
            text = text + "hybrid=" + repr(hybrid)
            text = text + ", pipes=" + repr(pipes) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(hybrid, 'hybrid pipe name')
        arg_check.is_str_list(pipes, 'data pipes')

        # Execute the functional code.
        hybrid_obj._hybridise(hybrid=hybrid, pipe_list=pipes)


    def switch(self, pipe_name=None):
        """Function for switching between data pipes.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_name:  The name of the data pipe.


        Description
        ~~~~~~~~~~~

        This function will switch from the current data pipe to the given data pipe.


        Examples
        ~~~~~~~~

        To switch to the 'ellipsoid' data pipe, type:

        relax> pipe.switch('ellipsoid')
        relax> pipe.switch(pipe_name='ellipsoid')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "pipe.switch("
            text = text + "pipe_name=" + repr(pipe_name) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(pipe_name, 'data pipe name')

        # Execute the functional code.
        pipes.switch(pipe_name=pipe_name)
