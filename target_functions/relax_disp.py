###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
# Copyright (C) 2009 Sebastien Morin                                          #
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
"""Target functions for relaxation dispersion."""

# relax module imports.
from lib.dispersion.equations import fast_2site
from lib.errors import RelaxError
from target_functions.chi2 import chi2


class Dispersion:
    def __init__(self, model=None, num_params=None, num_times=None, values=None, sd=None, cpmg_frqs=None, scaling_matrix=None):
        """Relaxation dispersion target functions for optimisation.

        @keyword model:             The relaxation dispersion model to fit.
        @type model:                str
        @keyword num_param:         The number of parameters in the model.
        @type num_param:            int
        @keyword num_times:         The number of relaxation times.
        @type num_times:            int
        @keyword values:            The peak intensities.
        @type values:               numpy rank-2 float array
        @keyword sd:                The peak intensity errors.
        @type sd:                   numpy rank-2 float array
        @keyword cpmg_frqs:         The CPMG frequencies in Hertz.
        @type cpmg_frqs:            numpy rank-1 float array
        @keyword scaling_matrix:    The square and diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 array
        """

        # Store the arguments.
        self.num_params = num_params
        self.num_times = num_times
        self.values = values
        self.sd = sd
        self.cpmg_frqs = cpmg_frqs
        self.scaling_matrix = scaling_matrix

        # Set up the model.
        if model == 'fast':
            self.func = self.func_fast_2site
        else:
            raise RelaxError("The relaxation dispersion model '%s' is not supported yet." % model)


    def func_fast_2site(self, params):
        """Target function for the fast 2-site exchange model.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Back calculated the effective transversal relaxation rates.
        fast_2site(params=params, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc, num_times=self.num_times)

        # Calculate and return the chi-squared value.
        return chi2(values, back_calc, sd)
