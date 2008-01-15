###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
import sys

# relax module imports.
import help
from specific_fns import n_state_model
from relax_errors import RelaxBoolError, RelaxIntError, RelaxStrError


class N_state_model:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the alignment tensor."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def model(self, N=None):
        """Set up the N-state model by specifying the number of states N.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        N:  The number of states.


        Description
        ~~~~~~~~~~~

        Prior to optimisation, the N-state model must be set up.  This simply involves the setting
        of the number of states N.


        Examples
        ~~~~~~~~

        To set up a 5-state model, type:

        relax> n_state_model.model(N=5)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "n_state_model.model("
            text = text + "N=" + `N` + ")"
            print text

        # Number of states argument.
        if type(N) != int:
            raise RelaxIntError, ('the number of states N', N)

        # Execute the functional code.
        n_state_model.model_setyp(N=N)


    def set_domain(self, tensor=None, domain=None):
        """Set the domain label for the alignment tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor:  The alignment tensor to assign the domain label to.

        domain:  The domain label.


        Description
        ~~~~~~~~~~~

        Prior to optimisation of the N-state model, the domain to which each alignment tensor
        belongs must be specified.


        Examples
        ~~~~~~~~

        To link the alignment tensor loaded as 'chi3 C-dom' to the C-terminal domain 'C', type:

        relax> n_state_model.set_domain(tensor='chi3 C-dom', domain='C')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "n_state_model.set_domain("
            text = text + "tensor=" + `tensor`
            text = text + ", domain=" + `domain` + ")"
            print text

        # Tensor argument.
        if type(tensor) != str:
            raise RelaxStrError, ('tensor', tensor)

        # Domain argument.
        if type(domain) != str:
            raise RelaxStrError, ('domain', domain)

        # Execute the functional code.
        n_state_model.set_domain(tensor=tensor, domain=domain)


    def set_type(self, tensor=None, red=False):
        """Set whether the alignment tensor is the full or reduced tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor:  The alignment tensor identification string.

        red:  The state of the alignment tensor.  If True, then it is labelled as the full tensor.
        If False, then it is labelled as the tensor reduced because of domain motions.


        Description
        ~~~~~~~~~~~

        Prior to optimisation of the N-state model the state of alignment tensor, whether it is the
        full or reduced tensor, must be set using this user function.


        Examples
        ~~~~~~~~

        To state that the alignment tensor loaded as 'chi3 C-dom' is the reduced tensor, type:

        relax> n_state_model.set_type(tensor='chi3 C-dom', red=True)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "n_state_model.set_type("
            text = text + "tensor=" + `tensor`
            text = text + ", red=" + `red` + ")"
            print text

        # Tensor argument.
        if type(tensor) != str:
            raise RelaxStrError, ('tensor', tensor)

        # Red argument.
        if type(red) != bool:
            raise RelaxBoolError, ('red', red)

        # Execute the functional code.
        n_state_model.set_type(tensor=tensor, red=red)
