###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
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
"""The specific analysis API.

This module is for directly accessing the specific analysis API.  The individual API objects should not be accessed directly, but instead the functions here should be used.
"""

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from lib.errors import RelaxError
from pipe_control import pipes


def get_string(function_type):
    """Function for returning a string corresponding to the function type."""

    # Consistency testing.
    if function_type == 'ct':
        return "consistency testing"

    # The Frame Order theories.
    if function_type == 'frame order':
        return "Frame Order theories"

    # NOE calculation.
    if function_type == 'noe':
        return "NOE calculations"

    # The N-state model.
    if function_type == 'N-state':
        return "the N-state model"

    # Relaxation dispersion curve fitting.
    if function_type == 'relax_disp':
        return "relaxation dispersion curve fitting"

    # Relaxation curve fitting.
    if function_type == 'relax_fit':
        return "relaxation curve fitting"

    # Reduced spectral density mapping.
    if function_type == 'jw':
        return "reduced spectral density mapping"

    # Model-free analysis.
    if function_type == 'mf':
        return "Model-free analysis"

    # Hybrid models.
    if function_type == 'hybrid':
        return "hybrid models"

    # Unknown analysis.
    raise RelaxError("The function_type " + repr(function_type) + " is unknown.")


def return_api(analysis_type=None, pipe_name=None):
    """Return the specific analysis API class instance corresponding to the function type.

    @keyword analysis_type:     The specific analysis type.  This overrides the pipe_name argument.
    @type analysis_type:        str or None
    @keyword pipe_name:         The name of the data pipe to obtain the analysis type from.  This is ignored if the analysis_type argument is given.  If both arguments are None, then the current data pipe will be used.
    """

    # The analysis type, if not given.
    if analysis_type is None:
        # Check if a data pipe exists.
        pipes.test()

        # Use a custom data pipe name.
        if pipe_name:
            analysis_type = ds[pipe_name].pipe_type

        # Use the current data pipe.
        else:
            analysis_type = cdp.pipe_type

    # Initialise the analysis object.
    obj = None

    # Consistency testing.
    if analysis_type == 'ct':
        from specific_analyses.consistency_tests.api import Consistency_tests
        obj = Consistency_tests()

    # The Frame Order theories.
    elif analysis_type == 'frame order':
        from specific_analyses.frame_order.api import Frame_order
        obj = Frame_order()

    # Hybrid models.
    elif analysis_type == 'hybrid':
        from specific_analyses.hybrid import Hybrid
        obj = Hybrid()

    # Reduced spectral density mapping.
    elif analysis_type == 'jw':
        from specific_analyses.jw_mapping.api import Jw_mapping
        obj = Jw_mapping()

    # Model-free analysis.
    elif analysis_type == 'mf':
        from specific_analyses.model_free.api import Model_free
        obj = Model_free()

    # The N-state model.
    elif analysis_type == 'N-state':
        from specific_analyses.n_state_model.api import N_state_model
        obj = N_state_model()

    # NOE calculation.
    elif analysis_type == 'noe':
        from specific_analyses.noe.api import Noe
        obj = Noe()

    # Relaxation dispersion curve fitting.
    elif analysis_type == 'relax_disp':
        from specific_analyses.relax_disp.api import Relax_disp
        obj = Relax_disp()

    # Relaxation curve fitting.
    elif analysis_type == 'relax_fit':
        from specific_analyses.relax_fit.api import Relax_fit
        obj = Relax_fit()

    # Return the object.
    if obj != None:
        return obj

    # Unknown analysis.
    raise RelaxError("The analysis type '%s' is unknown." % analysis_type)

