###############################################################################
#                                                                             #
# Copyright (C) 2003-2010 Edward d'Auvergne                                   #
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
"""Module containing the model-free analysis 'model_free' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from specific_fns.setup import model_free_obj


class Model_free(User_fn_class):
    """Class for holding the preset model functions."""

    def create_model(self, model=None, equation=None, params=None, spin_id=None):
        """Function to create a model-free model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model-free model.

        equation:  The model-free equation.

        params:  The array of parameter names of the model.

        spin_id:  The spin identification string.


        Model-free equation
        ~~~~~~~~~~~~~~~~~~~

        'mf_orig' selects the original model-free equations with parameters {S2, te}.
        'mf_ext' selects the extended model-free equations with parameters {S2f, tf, S2, ts}.
        'mf_ext2' selects the extended model-free equations with parameters {S2f, tf, S2s, ts}.


        Model-free parameters
        ~~~~~~~~~~~~~~~~~~~~~

        The following parameters are accepted for the original model-free equation:

            'S2':   The square of the generalised order parameter.
            'te':   The effective correlation time.

        The following parameters are accepted for the extended model-free equation:

            'S2f':  The square of the generalised order parameter of the faster motion.
            'tf':   The effective correlation time of the faster motion.
            'S2':   The square of the generalised order parameter S2 = S2f * S2s.
            'ts':   The effective correlation time of the slower motion.

        The following parameters are accepted for the extended 2 model-free equation:

            'S2f':  The square of the generalised order parameter of the faster motion.
            'tf':   The effective correlation time of the faster motion.
            'S2s':  The square of the generalised order parameter of the slower motion.
            'ts':   The effective correlation time of the slower motion.

        The following parameters are accepted for all equations:

            'Rex':  The chemical exchange relaxation.
            'r':    The average bond length <r>.
            'CSA':  The chemical shift anisotropy.


        Spin identification string
        ~~~~~~~~~~~~~~~~~~~~~~~~~~

        If 'spin_id' is supplied then the model will only be created for the corresponding spins.
        Otherwise the model will be created for all spins.


        Examples
        ~~~~~~~~

        The following commands will create the model-free model 'm1' which is based on the original
        model-free equation and contains the single parameter 'S2'.

        relax> model_free.create_model('m1', 'mf_orig', ['S2'])
        relax> model_free.create_model(model='m1', params=['S2'], equation='mf_orig')


        The following commands will create the model-free model 'large_model' which is based on the
        extended model-free equation and contains the seven parameters 'S2f', 'tf', 'S2', 'ts',
        'Rex', 'CSA', 'r'.

        relax> model_free.create_model('large_model', 'mf_ext', ['S2f', 'tf', 'S2', 'ts', 'Rex',
                                       'CSA', 'r'])
        relax> model_free.create_model(model='large_model', params=['S2f', 'tf', 'S2', 'ts', 'Rex',
                                       'CSA', 'r'], equation='mf_ext')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "model_free.create_model("
            text = text + "model=" + repr(model)
            text = text + ", equation=" + repr(equation)
            text = text + ", params=" + repr(params)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(model, 'model-free model')
        arg_check.is_str(equation, 'model-free equation')
        arg_check.is_str_list(params, 'model-free parameters')
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)

        # Execute the functional code.
        model_free_obj._create_model(model=model, equation=equation, params=params, spin_id=spin_id)


    def delete(self):
        """Function for deleting all model-free data from the current data pipe.

        Examples
        ~~~~~~~~

        To delete all model-free data, type:

        relax> model_free.delete()
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "model_free.delete()"
            print(text)

        # Execute the functional code.
        model_free_obj._delete()


    def remove_tm(self, spin_id=None):
        """Function for removing the local tm parameter from a model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string.


        Description
        ~~~~~~~~~~~

        This function will remove the local tm parameter from the model-free parameter set.  If
        there is no local tm parameter within the set nothing will happen.

        If no spin identification string is given, then the function will apply to all spins.


        Examples
        ~~~~~~~~

        The following command will remove the parameter 'tm':

        relax> model_free.remove_tm()
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "model_free.remove_tm("
            text = text + "spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)

        # Execute the functional code.
        model_free_obj._remove_tm(spin_id=spin_id)


    def select_model(self, model=None, spin_id=None):
        """Function for the selection of a preset model-free model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the preset model.


        The preset models
        ~~~~~~~~~~~~~~~~~

        The standard preset model-free models are
            'm0' = {},
            'm1' = {S2},
            'm2' = {S2, te},
            'm3' = {S2, Rex},
            'm4' = {S2, te, Rex},
            'm5' = {S2f, S2, ts},
            'm6' = {S2f, tf, S2, ts},
            'm7' = {S2f, S2, ts, Rex},
            'm8' = {S2f, tf, S2, ts, Rex},
            'm9' = {Rex}.

        The preset model-free models with optimisation of the CSA value are
            'm10' = {CSA},
            'm11' = {CSA, S2},
            'm12' = {CSA, S2, te},
            'm13' = {CSA, S2, Rex},
            'm14' = {CSA, S2, te, Rex},
            'm15' = {CSA, S2f, S2, ts},
            'm16' = {CSA, S2f, tf, S2, ts},
            'm17' = {CSA, S2f, S2, ts, Rex},
            'm18' = {CSA, S2f, tf, S2, ts, Rex},
            'm19' = {CSA, Rex}.

        The preset model-free models with optimisation of the bond length are
            'm20' = {r},
            'm21' = {r, S2},
            'm22' = {r, S2, te},
            'm23' = {r, S2, Rex},
            'm24' = {r, S2, te, Rex},
            'm25' = {r, S2f, S2, ts},
            'm26' = {r, S2f, tf, S2, ts},
            'm27' = {r, S2f, S2, ts, Rex},
            'm28' = {r, S2f, tf, S2, ts, Rex},
            'm29' = {r, CSA, Rex}.

        The preset model-free models with both optimisation of the bond length and CSA are
            'm30' = {r, CSA},
            'm31' = {r, CSA, S2},
            'm32' = {r, CSA, S2, te},
            'm33' = {r, CSA, S2, Rex},
            'm34' = {r, CSA, S2, te, Rex},
            'm35' = {r, CSA, S2f, S2, ts},
            'm36' = {r, CSA, S2f, tf, S2, ts},
            'm37' = {r, CSA, S2f, S2, ts, Rex},
            'm38' = {r, CSA, S2f, tf, S2, ts, Rex},
            'm39' = {r, CSA, Rex}.

        Warning:  The models in the thirties range fail when using standard R1, R2, and NOE
        relaxation data.  This is due to the extreme flexibly of these models where a change in the
        parameter 'r' is compensated by a corresponding change in the parameter 'CSA' and
        vice versa.


        Additional preset model-free models, which are simply extensions of the above models with
        the addition of a local tm parameter are:
            'tm0' = {tm},
            'tm1' = {tm, S2},
            'tm2' = {tm, S2, te},
            'tm3' = {tm, S2, Rex},
            'tm4' = {tm, S2, te, Rex},
            'tm5' = {tm, S2f, S2, ts},
            'tm6' = {tm, S2f, tf, S2, ts},
            'tm7' = {tm, S2f, S2, ts, Rex},
            'tm8' = {tm, S2f, tf, S2, ts, Rex},
            'tm9' = {tm, Rex}.

        The preset model-free models with optimisation of the CSA value are
            'tm10' = {tm, CSA},
            'tm11' = {tm, CSA, S2},
            'tm12' = {tm, CSA, S2, te},
            'tm13' = {tm, CSA, S2, Rex},
            'tm14' = {tm, CSA, S2, te, Rex},
            'tm15' = {tm, CSA, S2f, S2, ts},
            'tm16' = {tm, CSA, S2f, tf, S2, ts},
            'tm17' = {tm, CSA, S2f, S2, ts, Rex},
            'tm18' = {tm, CSA, S2f, tf, S2, ts, Rex},
            'tm19' = {tm, CSA, Rex}.

        The preset model-free models with optimisation of the bond length are
            'tm20' = {tm, r},
            'tm21' = {tm, r, S2},
            'tm22' = {tm, r, S2, te},
            'tm23' = {tm, r, S2, Rex},
            'tm24' = {tm, r, S2, te, Rex},
            'tm25' = {tm, r, S2f, S2, ts},
            'tm26' = {tm, r, S2f, tf, S2, ts},
            'tm27' = {tm, r, S2f, S2, ts, Rex},
            'tm28' = {tm, r, S2f, tf, S2, ts, Rex},
            'tm29' = {tm, r, CSA, Rex}.

        The preset model-free models with both optimisation of the bond length and CSA are
            'tm30' = {tm, r, CSA},
            'tm31' = {tm, r, CSA, S2},
            'tm32' = {tm, r, CSA, S2, te},
            'tm33' = {tm, r, CSA, S2, Rex},
            'tm34' = {tm, r, CSA, S2, te, Rex},
            'tm35' = {tm, r, CSA, S2f, S2, ts},
            'tm36' = {tm, r, CSA, S2f, tf, S2, ts},
            'tm37' = {tm, r, CSA, S2f, S2, ts, Rex},
            'tm38' = {tm, r, CSA, S2f, tf, S2, ts, Rex},
            'tm39' = {tm, r, CSA, Rex}.



        Spin identification string
        ~~~~~~~~~~~~~~~~~~~~~~~~~~

        If 'spin_id' is supplied then the model will only be selected for the corresponding spins.
        Otherwise the model will be selected for all spins.



        Examples
        ~~~~~~~~

        To pick model 'm1' for all selected spins, type:

        relax> model_free.select_model('m1')
        relax> model_free.select_model(model='m1')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "model_free.select_model("
            text = text + "model=" + repr(model)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(model, 'preset model name')
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)

        # Execute the functional code.
        model_free_obj._select_model(model=model, spin_id=spin_id)
