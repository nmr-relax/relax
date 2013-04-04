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

# Python module imports.
from numpy import dot, float64, zeros

# relax module imports.
from lib.curve_fit.exponential import exponential_2param_neg
from lib.dispersion.equations import fast_2site
from lib.errors import RelaxError
from target_functions.chi2 import chi2


class Dispersion:
    def __init__(self, model=None, num_params=None, num_spins=None, num_exp_curves=None, num_times=None, values=None, errors=None, cpmg_frqs=None, spin_lock_nu1=None, relax_times=None, scaling_matrix=None):
        """Relaxation dispersion target functions for optimisation.

        Models
        ======

        The following models are currently supported:

            - 'exp_fit':  Simple fitting of the exponential curves with parameters {R2eff, I0},
            - 'fast 2-site':  The 2-site fast exchange equation with parameters {R2eff, I0, R2, Rex, kex},
            - 'slow 2-site':  The 2-site slow exchange equation with parameters {R2eff, I0, R2A, kA, dw}.


        @keyword model:             The relaxation dispersion model to fit.
        @type model:                str
        @keyword num_param:         The number of parameters in the model.
        @type num_param:            int
        @keyword num_spins:         The number of spins in the cluster.
        @type num_spins:            int
        @keyword num_exp_curves:    The number of exponential curves.
        @type num_exp_curves:       int
        @keyword num_times:         The number of relaxation times.
        @type num_times:            int
        @keyword values:            The peak intensities.  The first dimension is that of the spin cluster (each element corresponds to a different spin in the block), the second dimension is the exponential curves, and the third are the relaxation times along the exponential curve.
        @type values:               numpy rank-3 float array
        @keyword errors:            The peak intensity errors.  The three dimensions must correspond to those of the values argument.
        @type errors:               numpy rank-3 float array
        @keyword cpmg_frqs:         The CPMG frequencies in Hertz for each separate exponential curve.  This will be ignored for R1rho experiments.
        @type cpmg_frqs:            numpy rank-1 float array
        @keyword spin_lock_nu1:     The spin-lock field strengths in Hertz for each separate exponential curve.  This will be ignored for CPMG experiments.
        @type spin_lock_nu1:        numpy rank-1 float array
        @keyword relax_times:       The relaxation time points in seconds for the exponential curve.
        @type relax_times:          numpy rank-1 float array
        @keyword scaling_matrix:    The square and diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 float array
        """

        # Check the args.
        if model not in ['exp_fit', 'fast 2-site', 'slow 2-site']:
            raise RelaxError("The model '%s' is unknown." % model)

        # Store the arguments.
        self.num_params = num_params
        self.num_spins = num_spins
        self.num_exp_curves = num_exp_curves
        self.num_times = num_times
        self.values = values
        self.errors = errors
        self.cpmg_frqs = cpmg_frqs
        self.spin_lock_nu1 = spin_lock_nu1
        self.relax_times = relax_times
        self.scaling_matrix = scaling_matrix

        # Scaling initialisation.
        self.scaling_flag = False
        if self.scaling_matrix != None:
            self.scaling_flag = True

        # Create the structure for holding the back-calculated peak intensities.
        self.back_calc = zeros(num_times, float64)

        # Set up the model.
        if model == 'exp_fit':
            self.func = self.func_exp_fit
        elif model == 'fast 2-site':
            self.func = self.func_fast_2site


    def func_exp_fit(self, params):
        """Target function for the simple exponential curve-fitting.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Loop over the spins.
        chi2_sum = 0.0
        for spin_index in range(self.num_spins):
            # Loop over the exponential curves.
            for exp_index in range(self.num_exp_curves):
                # Unpack the exponential curve parameters.
                index = spin_index * 2 * self.num_exp_curves + exp_index * self.num_exp_curves
                r2eff = params[index]
                i0 = params[index + 1]

                # Back-calculate the points on the exponential curve.
                exponential_2param_neg(rate=r2eff, i0=i0, x=self.relax_times, y=self.back_calc)

                # Calculate the chi-squared value for this curve.
                chi2_sum += chi2(self.values[spin_index, exp_index], self.back_calc, self.errors[spin_index, exp_index])

        # Return the chi-squared value.
        return chi2_sum


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
