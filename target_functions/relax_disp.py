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
from lib.dispersion.cr72 import r2eff_CR72
from lib.dispersion.lm63 import r2eff_LM63
from lib.errors import RelaxError
from target_functions.chi2 import chi2
from specific_analyses.relax_disp.variables import MODEL_CR72, MODEL_LM63, MODEL_R2EFF


class Dispersion:
    def __init__(self, model=None, num_params=None, num_spins=None, num_frq=None, num_disp_points=None, values=None, errors=None, missing=None, frqs=None, cpmg_frqs=None, spin_lock_nu1=None, scaling_matrix=None):
        """Relaxation dispersion target functions for optimisation.

        Models
        ======

        The following models are currently supported:

            - 'LM63':  The Luz and Meiboom (1963) 2-site fast exchange model.
            - 'CR72':  The Carver and Richards (1972) 2-site model for all time scales.


        @keyword model:             The relaxation dispersion model to fit.
        @type model:                str
        @keyword num_param:         The number of parameters in the model.
        @type num_param:            int
        @keyword num_spins:         The number of spins in the cluster.
        @type num_spins:            int
        @keyword num_frq:           The number of spectrometer field strengths.
        @type num_frq:              int
        @keyword num_disp_points:   The number of points on the dispersion curve.
        @type num_disp_points:      int
        @keyword values:            The R2eff/R1rho values.  The first dimension is that of the spin cluster (each element corresponds to a different spin in the block), the second dimension is the spectrometer field strength, and the third is the dispersion points.
        @type values:               numpy rank-3 float array
        @keyword errors:            The R2eff/R1rho errors.  The three dimensions must correspond to those of the values argument.
        @type errors:               numpy rank-3 float array
        @keyword missing:           The data structure indicating missing R2eff/R1rho data.  The three dimensions must correspond to those of the values argument.
        @type missing:              numpy rank-3 int array
        @keyword frqs:              The spectrometer frequencies in Hz.
        @type frqs:                 numpy rank-1 float array
        @keyword cpmg_frqs:         The CPMG frequencies in Hertz for each separate dispersion point.  This will be ignored for R1rho experiments.
        @type cpmg_frqs:            numpy rank-1 float array
        @keyword spin_lock_nu1:     The spin-lock field strengths in Hertz for each separate dispersion point.  This will be ignored for CPMG experiments.
        @type spin_lock_nu1:        numpy rank-1 float array
        @keyword scaling_matrix:    The square and diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 float array
        """

        # Check the args.
        if model not in [MODEL_R2EFF, MODEL_LM63, MODEL_CR72]:
            raise RelaxError("The model '%s' is unknown." % model)
        if values == None:
            raise RelaxError("No values have been supplied to the target function.")
        if errors == None:
            raise RelaxError("No errors have been supplied to the target function.")
        if missing == None:
            raise RelaxError("No missing data information has been supplied to the target function.")

        # Store the arguments.
        self.num_params = num_params
        self.num_spins = num_spins
        self.num_frq = num_frq
        self.num_disp_points = num_disp_points
        self.values = values
        self.errors = errors
        self.missing = missing
        self.frqs = frqs
        self.cpmg_frqs = cpmg_frqs
        self.spin_lock_nu1 = spin_lock_nu1
        self.scaling_matrix = scaling_matrix

        # Scaling initialisation.
        self.scaling_flag = False
        if self.scaling_matrix != None:
            self.scaling_flag = True

        # Create the structure for holding the back-calculated R2eff values (matching the dimensions of the values structure).
        self.back_calc = zeros((num_spins, num_frq, num_disp_points), float64)

        # Set up the model.
        if model == MODEL_LM63:
            self.func = self.func_LM63
        if model == MODEL_CR72:
            self.func = self.func_CR72


    def func_CR72(self, params):
        """Target function for the Carver and Richards (1972) 2-site exchange model on all time scales.

        This assumes that pA > pB, and hence this must be implemented as a constraint.


        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        index = self.num_frq - 1
        R20 = params[:index+1]
        pA = params[index+1]
        dw = params[index+2]
        kex = params[index+3]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # Convert dw from ppm to rad/s.
                dw_frq = dw * self.frqs[frq_index]

                # Back calculate the R2eff values.
                r2eff_CR72(r20=R20[frq_index], pA=pA, dw=dw_frq, kex=kex, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_LM63(self, params):
        """Target function for the Luz and Meiboom (1963) fast 2-site exchange model.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        index = self.num_frq - 1
        R20 = params[:index+1]
        phi_ex = params[index+1]
        kex = params[index+2]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # Spectrometer field strength scaling.
                phi_ex_scaled = phi_ex * self.frqs[frq_index]**2

                # Back calculate the R2eff values.
                r2eff_LM63(r20=R20[frq_index], phi_ex=phi_ex_scaled, kex=kex, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum
