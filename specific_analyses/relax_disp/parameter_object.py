###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""The module for the relaxation dispersion parameter list object."""

# relax module imports.
from lib.dispersion.variables import MODEL_LIST_MMQ, MODEL_M61B
from lib.mathematics import round_to_next_order
from pipe_control.mol_res_spin import return_spin
from specific_analyses.parameter_object import Param_list


def dw_lower(incs=None, model_info=None):
    """Determine the lower grid bound for the dw parameters.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The spin ID strings from the model_loop() specific API method.
    @type model_info:       list of str
    @return:                The lower grid search bound for the dw parameters.
    @rtype:                 float
    """

    # Fetch the first spin container.
    spin0 = return_spin(model_info[0])

    # The MMQ models.
    if spin0.model in MODEL_LIST_MMQ:
        return -10.0

    # All other models.
    else:
        return 0.0


def dwH_lower(incs=None, model_info=None):
    """Determine the lower grid bound for the dwH parameters.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The spin ID strings from the model_loop() specific API method.
    @type model_info:       list of str
    @return:                The lower grid search bound for the dwH parameters.
    @rtype:                 float
    """

    # Fetch the first spin container.
    spin0 = return_spin(model_info[0])

    # The MMQ models.
    if spin0.model in MODEL_LIST_MMQ:
        return -3.0

    # All other models.
    else:
        return 0.0


def pA_lower(incs=None, model_info=None):
    """Determine the lower grid bound for the pA parameter.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The spin containers and the spin ID strings from the model_loop() specific API method.
    @type model_info:       list of SpinContainer instances, list of str
    @return:                The lower grid search bound for the pA parameter.
    @rtype:                 float
    """

    # Fetch the first spin container.
    spin0 = return_spin(model_info[0])

    # The MMQ models.
    if spin0.model == MODEL_M61B:
        return 0.85

    # All other models.
    else:
        return 0.5


def i0_upper(incs=None, model_info=None):
    """Find the maximum peak intensity for the cluster.

    This is for the grid search upper bound for the I0 parameter.


    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The spin containers and the spin ID strings from the model_loop() specific API method.
    @type model_info:       list of SpinContainer instances, list of str
    @return:                The maximum peak intensity of all spins and time points.
    @rtype:                 float
    """

    # Alias.
    spin_ids = model_info

    # Find the maximum intensity.
    upper = 0.0
    for si in range(len(spin_ids)):
        spin = return_spin(spin_ids[si])
        upper = max(upper, max(spin.peak_intensity.values()))

    # Multiply the value by 2.0 and then round up to the next order - this will be the upper bound.
    return round_to_next_order(upper * 2.0)



class Relax_disp_params(Param_list):
    """The relaxation dispersion parameter list singleton."""

    # Class variable for storing the class instance (for the singleton design pattern).
    _instance = None

    def __init__(self):
        """Define all the parameters of the analysis."""

        # The object is already initialised.
        if self._initialised: return

        # Execute the base class __init__ method.
        Param_list.__init__(self)

        # Add the base data for the 'R2eff' model.
        self._add_peak_intensity()

        # Add the base information for the dispersion analysis.
        self._add(
            'relax_times',
            scope = 'spin',
            py_type = dict,
            grace_string = '\\qRelaxation time period (s)\\Q'
        )
        self._add(
            'cpmg_frqs',
            scope = 'spin',
            py_type = dict,
            grace_string = '\\qCPMG pulse train frequency (Hz)\\Q'
        )
        self._add(
            'spin_lock_nu1',
            scope = 'spin',
            py_type = dict,
            grace_string = '\\qSpin-lock field strength (Hz)\\Q'
        )

        # Add the model variables.
        self._add_model_info()

        # Add the parameters of the 'R2eff' model.
        self._add(
            'r2eff',
            scope = 'spin',
            default = 10.0,
            desc = 'The effective transversal relaxation rate',
            py_type = dict,
            set = 'params',
            grid_lower = 1.0,
            grid_upper = 40.0,
            grace_string = '\\qR\\s2,eff\\N\\Q (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'i0',
            scope = 'spin',
            default = 10000.0,
            desc = 'The initial intensity',
            py_type = dict,
            set = 'params',
            grid_lower = 0.0001,
            grid_upper = i0_upper,
            grace_string = '\\qI\\s0\\Q',
            err = True,
            sim = True
        )

        # Add the parameters of all dispersion models.
        self._add(
            'r1',
            scope = 'spin',
            default = 2.0,
            desc = 'The longitudinal relaxation rate',
            py_type = dict,
            set = 'params',
            scaling = 10,
            grid_lower = 0.1,
            grid_upper = 20.0,
            grace_string = '\\qR\\s1\\N\\Q (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'r2',
            scope = 'spin',
            default = 10.0,
            desc = 'The transversal relaxation rate',
            py_type = dict,
            set = 'params',
            scaling = 10,
            grid_lower = 5.0,
            grid_upper = 20.0,
            grace_string = '\\qR\\s2\\N\\Q (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'r2a',
            scope = 'spin',
            default = 10.0,
            desc = 'The transversal relaxation rate for state A in the absence of exchange',
            py_type = dict,
            set = 'params',
            scaling = 10,
            grid_lower = 5.0,
            grid_upper = 20.0,
            grace_string = '\\qR\\s2,A\\N\\Q (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'r2b',
            scope = 'spin',
            default = 10.0,
            desc = 'The transversal relaxation rate for state B in the absence of exchange',
            py_type = dict,
            set = 'params',
            scaling = 10,
            grid_lower = 5.0,
            grid_upper = 20.0,
            grace_string = '\\qR\\s2,B\\N\\Q (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'pA',
            scope = 'spin',
            default = 0.90,
            desc = 'The population for state A',
            py_type = float,
            set = 'params',
            grid_lower = pA_lower,
            grid_upper = 1.0,
            grace_string = '\\qp\\sA\\N\\Q',
            err = True,
            sim = True
        )
        self._add(
            'pB',
            scope = 'spin',
            default = 0.5,
            desc = 'The population for state B',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = 0.5,
            grace_string = '\\qp\\sB\\N\\Q',
            err = True,
            sim = True
        )
        self._add(
            'pC',
            scope = 'spin',
            default = 0.5,
            desc = 'The population for state C',
            py_type = float,
            set = 'params',
            grace_string = '\\qp\\sC\\N\\Q',
            err = True,
            sim = True
        )
        self._add(
            'phi_ex',
            scope = 'spin',
            default = 5.0,
            desc = 'The phi_ex = pA.pB.dw**2 value (ppm^2)',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = 10.0,
            grace_string = '\\xF\\B\\sex\\N = \\q p\\sA\\N.p\\sB\\N.\\xDw\\B\\S2\\N\\Q  (ppm\\S2\\N)',
            err = True,
            sim = True
        )
        self._add(
            'phi_ex_B',
            scope = 'spin',
            default = 5.0,
            desc = 'The fast exchange factor between sites A and B (ppm^2)',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = 10.0,
            grace_string = '\\xF\\B\\sex,B\\N (ppm\\S2\\N)',
            err = True,
            sim = True
        )
        self._add(
            'phi_ex_C',
            scope = 'spin',
            default = 5.0,
            desc = 'The fast exchange factor between sites A and C (ppm^2)',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = 10.0,
            grace_string = '\\xF\\B\\sex,C\\N (ppm\\S2\\N)',
            err = True,
            sim = True
        )
        self._add(
            'padw2',
            scope = 'spin',
            default = 1.0,
            desc = 'The pA.dw**2 value (ppm^2)',
            py_type = float,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = 10.0,
            grace_string = '\\qp\\sA\\N.\\xDw\\B\\S2\\N\\Q  (ppm\\S2\\N)',
            err = True,
            sim = True
        )
        self._add(
            'dw',
            scope = 'spin',
            default = 1.0,
            desc = 'The chemical shift difference between states A and B (in ppm)',
            py_type = float,
            set = 'params',
            grid_lower = dw_lower,
            grid_upper = 10.0,
            grace_string = '\\q\\xDw\\B\\Q (ppm)',
            err = True,
            sim = True
        )
        self._add(
            'dw_AB',
            scope = 'spin',
            default = 1.0,
            desc = 'The chemical shift difference between states A and B for 3-site exchange (in ppm)',
            py_type = float,
            set = 'params',
            grid_lower = dw_lower,
            grid_upper = 10.0,
            grace_string = '\\q\\xDw\\B\\Q\\SAB\\N (ppm)',
            err = True,
            sim = True
        )
        self._add(
            'dw_AC',
            scope = 'spin',
            default = 1.0,
            desc = 'The chemical shift difference between states A and C for 3-site exchange (in ppm)',
            py_type = float,
            set = 'params',
            grid_lower = dw_lower,
            grid_upper = 10.0,
            grace_string = '\\q\\xDw\\B\\Q\\SAC\\N (ppm)',
            err = True,
            sim = True
        )
        self._add(
            'dw_BC',
            scope = 'spin',
            default = 1.0,
            desc = 'The chemical shift difference between states B and C for 3-site exchange (in ppm)',
            py_type = float,
            set = 'params',
            grid_lower = dw_lower,
            grid_upper = 10.0,
            grace_string = '\\q\\xDw\\B\\Q\\SBC\\N (ppm)',
            err = True,
            sim = True
        )
        self._add(
            'dwH',
            scope = 'spin',
            default = 1.0,
            desc = 'The proton chemical shift difference between states A and B (in ppm)',
            py_type = float,
            set = 'params',
            grid_lower = dwH_lower,
            grid_upper = 3.0,
            grace_string = '\\q\\xDw\\B\\sH\\N\\Q (ppm)',
            err = True,
            sim = True
        )
        self._add(
            'dwH_AB',
            scope = 'spin',
            default = 1.0,
            desc = 'The proton chemical shift difference between states A and B for 3-site exchange (in ppm)',
            py_type = float,
            set = 'params',
            grid_lower = dwH_lower,
            grid_upper = 3.0,
            grace_string = '\\q\\xDw\\B\\sH\\N\\Q\\SAB\\N (ppm)',
            err = True,
            sim = True
        )
        self._add(
            'dwH_AC',
            scope = 'spin',
            default = 1.0,
            desc = 'The proton chemical shift difference between states A and C for 3-site exchange (in ppm)',
            py_type = float,
            set = 'params',
            grid_lower = dwH_lower,
            grid_upper = 3.0,
            grace_string = '\\q\\xDw\\B\\sH\\N\\Q\\SAC\\N (ppm)',
            err = True,
            sim = True
        )
        self._add(
            'dwH_BC',
            scope = 'spin',
            default = 1.0,
            desc = 'The proton chemical shift difference between states B and C for 3-site exchange (in ppm)',
            py_type = float,
            set = 'params',
            grid_lower = dwH_lower,
            grid_upper = 3.0,
            grace_string = '\\q\\xDw\\B\\sH\\N\\Q\\SBC\\N (ppm)',
            err = True,
            sim = True
        )
        self._add(
            'kex',
            scope = 'spin',
            default = 1000.0,
            desc = 'The exchange rate',
            py_type = float,
            set = 'params',
            scaling = 10000,
            grid_lower = 1.0,
            grid_upper = 10000.0,
            grace_string = '\\qk\\sex\\N\\Q (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'kex_AB',
            scope = 'spin',
            default = 1000.0,
            desc = 'The exchange rate between sites A and B for 3-site exchange with kex_AB = k_AB + k_BA (rad.s^-1)',
            py_type = float,
            set = 'params',
            scaling = 10000,
            grid_lower = 1.0,
            grid_upper = 10000.0,
            grace_string = '\\qk\\sex\\N\\Q\\SAB\\N (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'kex_AC',
            scope = 'spin',
            default = 1000.0,
            desc = 'The exchange rate between sites A and C for 3-site exchange with kex_AC = k_AC + k_CA (rad.s^-1)',
            py_type = float,
            set = 'params',
            scaling = 10000,
            grid_lower = 1.0,
            grid_upper = 10000.0,
            grace_string = '\\qk\\sex\\N\\Q\\SAC\\N (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'kex_BC',
            scope = 'spin',
            default = 1000.0,
            desc = 'The exchange rate between sites B and C for 3-site exchange with kex_BC = k_BC + k_CB (rad.s^-1)',
            py_type = float,
            set = 'params',
            scaling = 10000,
            grid_lower = 1.0,
            grid_upper = 10000.0,
            grace_string = '\\qk\\sex\\N\\Q\\SBC\\N (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'kB',
            scope = 'spin',
            default = 1000.0,
            desc = 'Approximate chemical exchange rate constant between sites A and B (rad.s^-1)',
            py_type = float,
            set = 'params',
            scaling = 10000,
            grid_lower = 1.0,
            grid_upper = 10000.0,
            grace_string = '\\qk\\sB\\N\\Q (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'kC',
            scope = 'spin',
            default = 1000.0,
            desc = 'Approximate chemical exchange rate constant between sites A and C (rad.s^-1)',
            py_type = float,
            set = 'params',
            scaling = 10000,
            grid_lower = 1.0,
            grid_upper = 10000.0,
            grace_string = '\\qk\\sC\\N\\Q (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'tex',
            scope = 'spin',
            default = 1.0/1000.0,
            desc = 'The time of exchange (tex = 1/kex)',
            py_type = float,
            set = 'params',
            scaling = 1e-4,
            grid_lower = 1/10000.0,
            grid_upper = 1.0,
            grace_string = '\\q\\xt\\B\\sex\\N\\Q (s.rad\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'theta',
            scope = 'spin',
            desc = 'Rotating frame tilt angle : ( theta = arctan(w_1 / Omega) ) (rad)',
            grace_string = 'Rotating frame tilt angle (rad)',
            py_type = dict,
            set = 'all',
            err = False,
            sim = False
        )
        self._add(
            'w_eff',
            scope = 'spin',
            desc = 'Effective field in rotating frame : ( w_eff = sqrt(Omega^2 + w_1^2) ) (rad.s^-1)',
            grace_string = 'Effective field in rotating frame (rad.s\\S-1\\N)',
            py_type = dict,
            set = 'all',
            err = False,
            sim = False
        )
        self._add(
            'k_AB',
            scope = 'spin',
            default = 2.0,
            desc = 'The exchange rate from state A to state B',
            py_type = float,
            set = 'params',
            scaling = 100,
            grid_lower = 0.1,
            grid_upper = 100.0,
            grace_string = '\\qk\\sAB\\N\\Q (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )
        self._add(
            'k_BA',
            scope = 'spin',
            default = 1000.0,
            desc = 'The exchange rate from state B to state A',
            py_type = float,
            set = 'params',
            scaling = 10000,
            grid_lower = 1.0,
            grid_upper = 10000.0,
            grace_string = '\\qk\\sBA\\N\\Q (rad.s\\S-1\\N)',
            err = True,
            sim = True
        )

        # Add the minimisation data.
        self._add_min_data(min_stats_global=False, min_stats_spin=True)

        # Set up the user function documentation.
        self._set_uf_title("Relaxation dispersion parameters")
        self._uf_param_table(label="table: dispersion parameters", caption="Relaxation dispersion parameters.", type=True)
        self._uf_param_table(label="table: dispersion parameters and min stats", caption="Relaxation dispersion parameters and minimisation statistics.", sets=['params', 'fixed', 'min'])
        self._uf_param_table(label="table: dispersion parameter value setting", caption="Relaxation dispersion parameters.", type=True)
        self._uf_param_table(label="table: dispersion parameter value setting with defaults", caption="Relaxation dispersion parameter value setting.", default=True, type=True)

        # Value setting documentation.
        for doc in self._uf_doc_loop(["table: dispersion parameter value setting", "table: dispersion parameter value setting with defaults"]):
            doc.add_paragraph("Any of the relaxation dispersion parameters which are of the 'float' type can be set.  Note that setting values for parameters which are not part of the model will have no effect.")
