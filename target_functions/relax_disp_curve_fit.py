###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
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
"""Target functions for relaxation fit."""

# Python module imports.
from copy import deepcopy
from numpy import exp, multiply, sum

# relax module imports.


class Exponential:
    def __init__(self, num_params=None, num_times=None, values=None, sd=None, relax_times=None, scaling_matrix=None):
        """Relaxation dispersion target functions for optimisation.
        """

        # Store variables.
        self.num_params = num_params
        self.num_times = num_times
        self.values = values
        self.errors = sd
        self.relax_times = relax_times
        self.scaling_matrix = scaling_matrix

        # Create the structure for holding the back-calculated R2eff values (matching the dimensions of the values structure).
        self.back_calc = deepcopy(self.values)

        # Define function to minimise.
        self.func = self.func_exp
        self.calc = self.calc_exp


    def chi2_rankN(self, data, back_calc_vals, errors):
        """Function to calculate the chi-squared value for multiple numpy array axis.

        @param data:            The multi dimensional vectors of yi values.
        @type data:             numpy multi dimensional array
        @param back_calc_vals:  The multi dimensional vectors of yi(theta) values.
        @type back_calc_vals:   numpy multi dimensional array
        @param errors:          The multi dimensional vectors of sigma_i values.
        @type errors:           numpy multi dimensional array
        @return:                The chi-squared value.
        @rtype:                 float
        """

        # Calculate the chi-squared statistic.
        return sum((1.0 / errors * (data - back_calc_vals))**2)


    def calc_exp(self, times=None, r2eff=None, i0=None):
        """Calculate the function values of exponential function.

        @keyword times: The time points.
        @type times:    float
        @keyword r2eff: The effective transversal relaxation rate.
        @type r2eff:    float
        @keyword i0:    The initial intensity.
        @type i0:       float
        @return:        The function values.
        @rtype:         float
        """

        # Calculate.
        return i0 * exp( -times * r2eff)


    def calc_exp_chi2(self, r2eff=None, i0=None):
        """Calculate the chi-squared value of exponential function.


        @keyword r2eff: The effective transversal relaxation rate.
        @type r2eff:    float
        @keyword i0:    The initial intensity.
        @type i0:       float
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Calculate.
        self.back_calc[:] = self.calc_exp(times=self.relax_times, r2eff=r2eff, i0=i0)

        # Return the total chi-squared value.
        return self.chi2_rankN(data=self.values, back_calc_vals=self.back_calc, errors=self.errors)    


    def func_exp(self, params):
        """Target function for exponential fit.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Unpack the parameter values.
        r2eff = params[0]
        i0 = params[1]

        # Calculate and return the chi-squared value.
        return self.calc_exp_chi2(r2eff=r2eff, i0=i0)


    def func_exp_general(self, params, xdata, ydata):
        """Target function for minimisation with scipy.optimize.leastsq
        """

        return self.calc_exp(xdata, *params) - ydata


    def func_exp_weighted_general(self, params, xdata, ydata, weights):
        """Target function for minimisation with scipy.optimize.leastsq
        """

        return weights * (self.calc_exp(xdata, *params) - ydata)