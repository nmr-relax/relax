###############################################################################
#                                                                             #
# Copyright (C) 2004-2010 Edward d'Auvergne                                   #
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

# relax module imports.
from base_class import User_fn_class
from relax_errors import RelaxNoneNumError, RelaxNumError, RelaxStrError
from specific_fns.setup import relax_disp_obj


class Relax_disp(User_fn_class):
    """Class for relaxation dispersion user functions."""

    def calc_r2eff(self, exp_type='cpmg', id=None, delayT=None, int_cpmg=1.0, int_ref=1.0):
        """Calculate the effective transversal relaxation rate from the peak intensities.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        exp_type:   The relaxation dispersion experiment type, either 'cpmg' or 'r1rho'.

        id:   The experiment identification string.

        delayT:   The CPMG constant time delay (T) in s.

        int_cpmg:   Intensity of the peak in the CPMG spectrum.

        int_ref:    Intensity of the peak in the reference spectrum.


        Description
        ~~~~~~~~~~~

        This user function allows one to extract 'r2eff' values from epak intensities.

        If 'cpmg' is chosen, the equation used is:
        r2eff = - ( 1 / delayT ) * log ( int_cpmg / int_ref )

        If 'r1rho' is chosen, nothing happens yet, as the code is not implemented.


        Examples
        ~~~~~~~~

        To calculate r2eff from a CPMG experiment, for experiment named '600', a constant time delay
        T of 20 ms (0.020 s) and intensities of CPMG and reference peak of, respectively, 0.742 and
        0.9641, type:

        relax> relax_disp.calc_r2eff('cpmg', '600', 0.020, 0.742, 0.9641)
        relax> relax_disp.calc_r2eff(exp_type='cpmg', id='600', delayT=0.020, int_cpmg=0.742, int_ref=0.9641)

        ANOTHER EXAMPLE FOR BATCH USE (FROM PEAK INTENSITY LISTS) WILL SOON BE ADDED.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_disp.calc_r2eff("
            text = text + "exp_type=" + `exp_type`
            text = text + ", id=" + `id`
            text = text + ", delayT=" + `delayT`
            text = text + ", int_cpmg=" + `int_cpmg`
            text = text + ", int_ref=" + `int_ref` + ")"
            print text

        # The exp_type argument.
        if type(exp_type) != str:
            raise RelaxStrError, ('exp_type', exp_type)

        # The id argument.
        if type(id) != str:
            raise RelaxStrError, ('experiment identification string', id)

        # The CPMG constant time delay (T).
        if type(delayT) != float and type(delayT) != int and delayT != None:
            raise RelaxNoneNumError, ('CPMG constant time delay (T)', delayT)

        # The CPMG peak intensity.
        if type(int_cpmg) != float and type(int_cpmg) != int:
            raise RelaxNumError, ('int_cpmg', int_cpmg)

        # The reference peak intensity.
        if type(int_ref) != float and type(int_ref) != int:
            raise RelaxNumError, ('int_ref', int_ref)

        # Execute the functional code.
        relax_disp_obj.calc_r2eff(exp_type=exp_type, id=id, delayT=delayT, int_cpmg=int_cpmg, int_ref=int_ref)


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
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "delayT("
            text = text + "id=" + `id`
            text = text + ", delayT=" + `delayT` + ")"
            print text

        # The CPMG constant time delay (T).
        if type(delayT) != float and type(delayT) != int and delayT != None:
            raise RelaxNoneNumError, ('CPMG constant time delay (T)', delayT)

        # The id argument.
        if type(id) != str:
            raise RelaxStrError, ('experiment identification string', id)

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
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_disp.cpmg_frq("
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


    def exp_type(self, exp_type='cpmg'):
        """Function for the selection of the relaxation dispersion experiments to analyse.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        exp_type:  The type of relaxation dispersion experiment performed.


        The preset experiments
        ~~~~~~~~~~~~~~~~~~~~~

        The supported experiments will include CPMG ('cpmg') and R1rho ('r1rho').


        Examples
        ~~~~~~~~

        To pick the experiment type 'cpmg' for all selected spins, type:

        relax> relax_disp.exp_type('cpmg')
        relax> relax_disp.exp_type(exp_type='cpmg')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_disp.exp_type("
            text = text + "exp_type=" + `exp_type` + ")"
            print text

        # The exp_type argument.
        if type(exp_type) != str:
            raise RelaxStrError, ('exp_type', exp_type)

        # Execute the functional code.
        relax_disp_obj.exp_type(exp_type=exp_type)


    def select_model(self, model='fast'):
        """Function for the selection of the relaxation dispersion curve type.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The type of relaxation dispersion curve to fit (relating to the NMR time scale).


        The preset models
        ~~~~~~~~~~~~~~~~~

        The supported equations will include the default fast-exchange limit as well as the
        slow-exchange limit.

        The parameters of these two models are:
            'fast': [R2, Rex, kex],
            'slow': [R2A, kA, dw].

        The equations for these two models are:
                                       /              /        kex       \   4 * cpmg_frq \ 
            'fast': R2eff = R2 + Rex * | 1 - 2 * Tanh | ---------------- | * ------------ |
                                       \              \ 2 * 4 * cpmg_frq /        kex     /

                                       /     /      dw      \   4 * cpmg_frq \ 
            'slow': R2eff = R2A + kA - | Sin | ------------ | * ------------ |
                                       \     \ 4 * cpmg_frq /        dw      /

            where cpmg_frq = 1 / ( 4 * cpmg_tau )

        The references for these equations are:
            'fast': Millet et al., JACS, 2000, 122. 2867 - 2877 (equation 19),
                    Kovrigin et al., JMagRes, 2006, 180. 93 - 104 (equation 1),
            'slow': Tollinger et al., JACS, 2001, 123. 11341-11352 (equation 2).


        Examples
        ~~~~~~~~

        To pick the model 'fast' for all selected spins, type:

        relax> relax_disp.select_model('fast')
        relax> relax_disp.select_model(exp_type='fast')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "relax_disp.select_model("
            text = text + "model=" + `model` + ")"
            print text

        # The model argument.
        if type(model) != str:
            raise RelaxStrError, ('model', model)

        # Execute the functional code.
        relax_disp_obj.select_model(model=model)
