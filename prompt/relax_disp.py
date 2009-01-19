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
from relax_errors import RelaxNoneNumError, RelaxNumError, RelaxStrError
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


        Examples
        ~~~~~~~~

        To set a CPMG constant time delay T of 20 ms (0.020 s) for experiments '600', type:

        relax> relax_disp.cpmg_delayT('600', 0.020)
        relax> relax_disp.cpmg_delayT(id='600', delayT=0.020)
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
        relax_disp_obj.cpmg_delayT(id=id, delayT=delayT)


    def cpmg_frq(self, cpmg_frq=0, spectrum_id=None):
        """Set the CPMG frequency associated with a given spectrum.

        Keyword arguments.
        ~~~~~~~~~~~~~~~~~~

        cpmg_frq:   The frequency, in Hz, of the CPMG pulse train.

        spectrum_id:   The spectrum identification string.


        Description
        ~~~~~~~~~~~

        This user function allows the CPMG pulse train frequency of a given spectrum to be set.
        If None is given for frequency, then the spectrum will be treated as a reference
        spectrum.


        Examples
        ~~~~~~~~

        To identify the reference spectrum called 'reference_spectrum', type:

        relax> relax_disp.cpmg_frq(None, 'reference_spectrum')
        relax> relax_disp.cpmg_frq(cpmg_frq=None, spectrum_id='reference_spectrum')

        To set a frequency of 200 Hz for the spectrum '200_Hz_spectrum', type:

        relax> relax_disp.cpmg_frq(200, '200_Hz_spectrum')
        relax> relax_disp.cpmg_frq(fcpmg_rq=200, spectrum_id='200_Hz_spectrum')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_disp.cpmg_frq("
            text = text + ", cpmg_frq=" + `cpmg_frq`
            text = text + "spectrum_id=" + `spectrum_id` + ")"
            print text

        # The cpmg_frq argument.
        if type(cpmg_frq) != float and type(cpmg_frq) != int and cpmg_frq != None:
            raise RelaxNoneNumError, ('cpmg_frq', cpmg_frq)

        # The spectrum_id argument.
        if type(spectrum_id) != str:
             raise RelaxStrError, ('spectrum_id', spectrum_id)

        # Execute the functional code.
        relax_disp_obj.cpmg_frq(cpmg_frq=cpmg_frq, spectrum_id=spectrum_id)


    def exp_type(self, exp='cpmg'):
        """Function for the selection of the relaxation dispersion experiments to analyse.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        exp:  The type of relaxation dispersion experiment performed.


        The preset experiments
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


    def r2eff_read(self):
        """Function for reading 'R2eff' values directly, instead of calculating them within relax
        starting from the intensities.

        THIS FUNCTION IS NOT WRITTEN YET.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~


        Examples
        ~~~~~~~~

        """


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

        The equations for these two models are
                                       /              /        kex       \   4 * cpmg_frq \\
            'fast': R2eff = R2 + Rex * | 1 - 2 * Tanh | ---------------- | * ------------ |
                                       \              \ 2 * 4 * cpmg_frq /        kex     /

                                       /     /      dw      \   4 * cpmg_frq \\
            'slow': R2eff = R2A + kA - | Sin | ------------ | * ------------ |
                                       \     \ 4 * cpmg_frq /        dw      /

            where cpmg_frq = 1 / ( 4 * cpmg_tau )

        The references for these equations are
            'fast': Millet et al., JACS, 2000, 122 : 2867 - 2877 (equation 19)
                    Kovrigin et al., JMagRes, 2006, 180 : 93 - 104 (equation 1)
            'slow': Tollinger et al., JACS, 2001, 123: 11341-11352 (equation 2)


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
