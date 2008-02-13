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
from specific_fns import n_state_model_obj
from relax_errors import RelaxBoolError, RelaxIntError, RelaxLenError, RelaxListError, RelaxListNumError, RelaxStrError


class N_state_model:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the alignment tensor."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def CoM(self, centre=None):
        """Set the centre of mass (CoM) for the moving domain.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        centre:  The optional argument for manually specifying the CoM.


        Description
        ~~~~~~~~~~~

        Prior to the calculation of the pivot to centre of mass (pivot-CoM) order parameter and
        subsequent cone of motions, both the pivot point and centre of mass must be specified.  This
        function is used to calculate the centre of mass from the selected parts of the structure
        previously loaded.  That is unless the centre keyword argument has been supplied, in which
        case this vector floating point numbers (of length 3) will be used as the CoM.


        Examples
        ~~~~~~~~

        To set the CoM to the N-terminal domain of a previously loaded PDB file (the C-terminal
        domain has been deselected), type:

        relax> n_state_model.CoM()


        To set the CoM to the position [0, 0, 1], type one of:

        relax> n_state_model.CoM([0, 0, 1])
        relax> n_state_model.CoM([0.0, 0.0, 1.0])
        relax> n_state_model.CoM(centre=[0.0, 0.0, 1.0])
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "n_state_model.CoM("
            text = text + "centre=" + `centre` + ")"
            print text

        # CoM argument.
        if type(centre) != list:
            raise RelaxListError, ('centre', centre)
        if len(centre) != 3:
            raise RelaxLenError, ("centre of mass", 3)
        for i in xrange(len(centre)):
            if type(centre[i]) != int and type(centre[i]) != float:
                raise RelaxListNumError, ('centre of mass', centre)

        # Execute the functional code.
        n_state_model_obj.CoM(centre=centre)


    def model(self, N=None, ref=None):
        """Set up the N-state model by specifying the number of states N and the reference domain.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        N:  The number of states.

        ref:  The domain which will act as the frame of reference.


        Description
        ~~~~~~~~~~~

        Prior to optimisation, the N-state model must be set up.  This simply involves the setting
        of the number of states N and which of the two domains will act as the frame of reference.
        The N-states will be rotations of the other domain.  To switch the frame of reference to the
        other domain, transpose the rotation matrices.


        Examples
        ~~~~~~~~

        To set up a 5-state model with 'C' domain being the frame of reference, type:

        relax> n_state_model.model(N=5, ref='C')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "n_state_model.model("
            text = text + "N=" + `N`
            text = text + ", ref=" + `ref` + ")"
            print text

        # Number of states argument.
        if type(N) != int:
            raise RelaxIntError, ('the number of states N', N)

        # Ref frame argument.
        if type(ref) != str:
            raise RelaxStrError, ('reference frame', ref)

        # Execute the functional code.
        n_state_model_obj.model_setup(N=N, ref=ref)


    def pivot_point(self, pivot=[0.0, 0.0, 0.0]):
        """Set the pivot point for the domain motions.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pivot:  The pivot point of the motions between the two domains.


        Description
        ~~~~~~~~~~~

        Prior to the calculation of the pivot to centre of mass (pivot-CoM) order parameter and
        subsequent cone of motions, both the pivot point and centre of mass must be specified.  The
        supplied pivot point must be a vector of floating point numbers of length 3.


        Examples
        ~~~~~~~~

        To set the pivot point to the origin in the PDB file (because the real pivot has been
        shifted to this position), type one of:

        relax> n_state_model.pivot_point()
        relax> n_state_model.pivot_point([0.0, 0.0, 0.0])
        relax> n_state_model.pivot_point(pivot=[0.0, 0.0, 0.0])
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "n_state_model.pivot_point("
            text = text + "pivot=" + `pivot` + ")"
            print text

        # Pivot argument.
        if type(pivot) != list:
            raise RelaxListError, ('pivot', pivot)
        if len(pivot) != 3:
            raise RelaxLenError, ("pivot point", 3)
        for i in xrange(len(pivot)):
            if type(pivot[i]) != int and type(pivot[i]) != float:
                raise RelaxListNumError, ('pivot point', pivot)

        # Execute the functional code.
        n_state_model_obj.pivot_point(pivot=pivot)


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
        n_state_model_obj.set_domain(tensor=tensor, domain=domain)


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
        n_state_model_obj.set_type(tensor=tensor, red=red)
