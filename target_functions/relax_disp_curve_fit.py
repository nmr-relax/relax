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
"""Target functions for relaxation exponential curve fitting with both minfx and scipy.optimize.leastsq."""

# Python module imports.
from copy import deepcopy
from numpy import dot, exp, log, multiply, sum

# relax module imports.
from target_functions.chi2 import chi2_rankN


class Exponential:
    def __init__(self, num_params=2, num_times=None, values=None, sd=None, relax_times=None, scaling_matrix=None):
        """Relaxation dispersion target functions for optimisation.

        This class contains minimisation functions for both minfx and scipy.optimize.leastsq.

        @keyword num_param:         The number of parameters in the model.
        @type num_param:            int
        @keyword num_times:         The number of time points.
        @type num_times:            int
        @keyword values:            The measured intensity values per time point.
        @type values:               numpy array
        @keyword sd:                The standard deviation of the measured intensity values per time point.
        @type sd:                   numpy array
        @keyword relax_times:       The time points.
        @type relax_times:          numpy array
        @keyword scaling_matrix:    The square and diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 float array
        """

        # Store variables.
        self.num_params = num_params
        self.num_times = num_times

        self.values = values
        self.errors = sd
        self.relax_times = relax_times
        self.scaling_matrix = scaling_matrix

        # Scaling initialisation.
        self.scaling_flag = False
        if self.scaling_matrix != None:
            self.scaling_flag = True

        # Create the structure for holding the back-calculated R2eff values (matching the dimensions of the values structure).
        self.back_calc = deepcopy(self.values)

        # Define function to minimise for minfx.
        self.func = self.func_exp


    def calc_exp(self, times=None, r2eff=None, i0=None):
        """Calculate the function values of exponential function.

        @keyword times: The time points.
        @type times:    numpy array
        @keyword r2eff: The effective transversal relaxation rate.
        @type r2eff:    float
        @keyword i0:    The initial intensity.
        @type i0:       float
        @return:        The function values.
        @rtype:         float
        """

        # Calculate.
        return i0 * exp( -times * r2eff)


    def estimate_x0_exp(self, intensities=None, times=None):
        """Estimate starting parameter x0 = [r2eff_est, i0_est], by converting the exponential curve to a linear problem.
         Then solving by linear least squares of: ln(Intensity[j]) = ln(i0) - time[j]* r2eff.

        @keyword intensities:   The measured intensity values per time point.
        @type intensities:      numpy array
        @keyword times:         The time points.
        @type times:            numpy array
        @return:                The list with estimated r2eff and i0 parameter for optimisation, [r2eff_est, i0_est]
        @rtype:                 list
        """

        # Convert to linear problem.
        w = log(intensities)
        x = - 1. * times
        n = len(times)

        # Solve by linear least squares.
        b = (sum(x*w) - 1./n * sum(x) * sum(w) ) / ( sum(x**2) - 1./n * (sum(x))**2 )
        a = 1./n * sum(w) - b * 1./n * sum(x)

        # Convert back from linear to exp function. Best estimate for parameter.
        r2eff_est = b
        i0_est = exp(a)

        # Return.
        return [r2eff_est, i0_est]


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
        return chi2_rankN(data=self.values, back_calc_vals=self.back_calc, errors=self.errors)


    def func_exp(self, params):
        """Target function for exponential fit in minfx.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        r2eff = params[0]
        i0 = params[1]

        # Calculate and return the chi-squared value.
        return self.calc_exp_chi2(r2eff=r2eff, i0=i0)


    def func_exp_general(self, params, times, intensities):
        """Target function for minimisation with scipy.optimize.leastsq.

        @param params:          The vector of parameter values.
        @type params:           numpy rank-1 float array
        @keyword times:         The time points.
        @type times:            numpy array
        @keyword intensities:   The measured intensity values per time point.
        @type intensities:      numpy array
        @return:                The difference between function evaluation with fitted parameters and measured values.
        @rtype:                 numpy array
        """

        # Return
        return self.calc_exp(times, *params) - intensities


    def func_exp_weighted_general(self, params, times, intensities, weights):
        """Target function for weighted minimisation with scipy.optimize.leastsq.

        @param params:          The vector of parameter values.
        @type params:           numpy rank-1 float array
        @keyword times:         The time points.
        @type times:            numpy array
        @keyword intensities:   The measured intensity values per time point.
        @type intensities:      numpy array
        @keyword weights:       The weights to multiply the function evaluation.  Should be supplied as '1/sd', where sd is the standard deviation of the measured intensity values.
        @type weights:          numpy array
        @return:                The weighted difference between function evaluation with fitted parameters and measured values.
        @rtype:                 numpy array
        """

        # Return
        return weights * (self.calc_exp(times, *params) - intensities)