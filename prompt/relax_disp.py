###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
"""Module containing the 'relax_disp' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
import help
from relax_errors import RelaxNumError, RelaxStrError
from specific_fns.setup import relax_disp_obj


class Relax_disp:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for relaxation dispersion curve fitting."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def cpmg_delayT(self, id=None, delayT=None):
        """Set the CPMG constant time delay (T) of the experiment.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        id:  The experiment identification string.

        delayT:   The CPMG constant time delay (T) in s.


        Description
        ~~~~~~~~~~~

        This user function allows the CPMG constant time delay (T) of a given experiment to be set.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "delayT("
            text = text + "id=" + `id`
            text = text + ", delayT=" + `delayT` + ")"
            print text

        # Id string.
        if type(id) != str:
            raise RelaxStrError, ('experiment identification string', id)

        # The CPMG constant time delay (T).
        if type(delayT) != float and type(delayT) != int:
            raise RelaxNumError, ('CPMG constant time delay (T)', delayT)

        # Execute the functional code.
        specific_fns.relax_disp.cpmg_delayT(id=id, delayT=delayT)


    def exp_type(self, exp='cpmg'):
        """Function for the selection of the relaxation dispersion experiments to analyse.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        exp:  The type of relaxation dispersion experiment performed.


        The preet experiments
        ~~~~~~~~~~~~~~~~~~~~~

        The supported experiments will include CPMG ('cpmg') and R1rho ('r1rho').


        Examples
        ~~~~~~~~

        To pick the experiment type 'cpmg' for all selected spins, type:

        relax> relax_disp.exp_type('cpmg')
        relax> relax_disp.exp_type(exp='cpmg')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_disp.exp_type("
            text = text + "exp=" + `exp` + ")"
            print text

        # The exp argument.
        if type(exp) != str:
            raise RelaxStrError, ('exp', exp)

        # Execute the functional code.
        relax_disp_obj.exp_type(exp=exp)


    def select_model(self, model='fast'):
        """Function for the selection of the relaxation dispersion curve type.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The type of relaxation dispersion curve to fit (relating to the NMR time scale).


        The preset models
        ~~~~~~~~~~~~~~~~~

        The supported equations will include the default fast-exchange limit as well as the
        slow-exchange limit.

        The parameters of these two models are
            'fast': [R2, Rex, kex],
            'slow': [R2A, kA, dw].


        Examples
        ~~~~~~~~

        To pick the model 'fast' for all selected spins, type:

        relax> relax_disp.select_model('fast')
        relax> relax_disp.select_model(exp='fast')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_disp.select_model("
            text = text + "model=" + `model` + ")"
            print text

        # The model argument.
        if type(model) != str:
            raise RelaxStrError, ('model', model)

        # Execute the functional code.
        relax_disp_obj.select_model(model=model)
