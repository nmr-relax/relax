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
from numpy import complex64, dot, float64, int16, zeros

# relax module imports.
from lib.dispersion.cr72 import r2eff_CR72
from lib.dispersion.dpl94 import r1rho_DPL94
from lib.dispersion.it99 import r2eff_IT99
from lib.dispersion.lm63 import r2eff_LM63
from lib.dispersion.m61 import r1rho_M61
from lib.dispersion.m61b import r1rho_M61b
from lib.dispersion.ns_2site_3d import r2eff_ns_2site_3D
from lib.dispersion.ns_2site_star import r2eff_ns_2site_star
from lib.dispersion.ns_matrices import r180x_3d
from lib.errors import RelaxError
from target_functions.chi2 import chi2
from specific_analyses.relax_disp.variables import MODEL_CR72, MODEL_CR72_RED, MODEL_DPL94, MODEL_IT99, MODEL_LIST_FULL, MODEL_LM63, MODEL_M61, MODEL_M61B, MODEL_NOREX, MODEL_NS_2SITE_3D, MODEL_NS_2SITE_3D_RED, MODEL_NS_2SITE_STAR, MODEL_NS_2SITE_STAR_RED, MODEL_R2EFF


class Dispersion:
    def __init__(self, model=None, num_params=None, num_spins=None, num_frq=None, num_disp_points=None, values=None, errors=None, missing=None, frqs=None, cpmg_frqs=None, spin_lock_nu1=None, relax_time=None, scaling_matrix=None):
        """Relaxation dispersion target functions for optimisation.

        Models
        ======

        The following analytic models are currently supported:

            - 'No Rex':  The model for no chemical exchange relaxation.
            - 'LM63':  The Luz and Meiboom (1963) 2-site fast exchange model.
            - 'CR72':  The Carver and Richards (1972) 2-site model for all time scales.
            - 'IT99':  The Ishima and Torchia (1999) 2-site model for all time scales with skewed populations (pA >> pB).
            - 'M61':  The Meiboom (1961) 2-site fast exchange model for R1rho-type experiments.
            - 'DPL94':  The Davis, Perlman and London (1994) 2-site fast exchange model for R1rho-type experiments.
            - 'M61 skew':  The Meiboom (1961) on-resonance 2-site model with skewed populations (pA >> pB) for R1rho-type experiments.

        The following numerical models are currently supported:

            - 'NS 2-site':  The numerical solution for the 2-site Bloch-McConnell equations.
            - 'NS 2-site star':  The numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices.


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
        @keyword frqs:              The spin Larmor frequencies (in MHz*2pi to speed up the ppm to rad/s conversion).  The dimensions correspond to the first two of the value, error and missing structures.
        @type frqs:                 numpy rank-2 float array
        @keyword cpmg_frqs:         The CPMG frequencies in Hertz for each separate dispersion point.  This will be ignored for R1rho experiments.
        @type cpmg_frqs:            numpy rank-1 float array
        @keyword spin_lock_nu1:     The spin-lock field strengths in Hertz for each separate dispersion point.  This will be ignored for CPMG experiments.
        @type spin_lock_nu1:        numpy rank-1 float array
        @keyword relax_time:        The fixed time period for relaxation (in seconds).
        @type relax_time:           float
        @keyword scaling_matrix:    The square and diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 float array
        """

        # Check the args.
        if model not in MODEL_LIST_FULL:
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
        self.relax_time = relax_time
        self.scaling_matrix = scaling_matrix

        # Scaling initialisation.
        self.scaling_flag = False
        if self.scaling_matrix != None:
            self.scaling_flag = True

        # Create the structure for holding the back-calculated R2eff values (matching the dimensions of the values structure).
        self.back_calc = zeros((num_spins, num_frq, num_disp_points), float64)

        # Initialise the post spin parameter indices.
        self.end_index = []

        # The spin and frequency dependent R2 parameters.
        self.end_index.append(self.num_spins * self.num_frq)
        if model in [MODEL_CR72, MODEL_NS_2SITE_3D, MODEL_NS_2SITE_STAR]:
            self.end_index.append(2 * self.num_spins * self.num_frq)

        # The spin and dependent parameters (phi_ex, dw, padw2).
        self.end_index.append(self.end_index[-1] + self.num_spins)
        if model == MODEL_IT99:
            self.end_index.append(self.end_index[-1] + self.num_spins)

        # Set up the matrices for the numerical solutions.
        if model in [MODEL_NS_2SITE_STAR_RED, MODEL_NS_2SITE_STAR]:
            # The matrix that contains only the R2 relaxation terms ("Redfield relaxation", i.e. non-exchange broadening).
            self.Rr = zeros((2, 2), complex64)

            # The matrix that contains the exchange terms between the two states A and B.
            self.Rex = zeros((2, 2), complex64)

            # The matrix that contains the chemical shift evolution.  It works here only with X magnetization, and the complex notation allows to evolve in the transverse plane (x, y).
            self.RCS = zeros((2, 2), complex64)

            # The matrix that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
            self.R = zeros((2, 2), complex64)

        # Pi-pulse propagators.
        if model in [MODEL_NS_2SITE_3D_RED, MODEL_NS_2SITE_3D]:
            self.r180x = r180x_3d()

        # This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
        if model in [MODEL_NS_2SITE_STAR_RED, MODEL_NS_2SITE_STAR]:
            self.M0 = zeros(2, float64)
        if model in [MODEL_NS_2SITE_3D_RED, MODEL_NS_2SITE_3D]:
            self.M0 = zeros(7, float64)
            self.M0[0] = 0.5

        # Some other data structures for the numerical solutions.
        if model in [MODEL_NS_2SITE_3D_RED, MODEL_NS_2SITE_3D, MODEL_NS_2SITE_STAR_RED, MODEL_NS_2SITE_STAR]:
            # The tau_cpmg times and matrix exponential power array.
            self.tau_cpmg = zeros(self.num_disp_points, float64)
            self.power = zeros(self.num_disp_points, int16)
            for i in range(self.num_disp_points):
                self.tau_cpmg[i] = 0.25 / self.cpmg_frqs[i]
                self.power[i] = int(round(self.cpmg_frqs[i] * self.relax_time))

            # The inverted relaxation delay.
            self.inv_relax_time = 1.0 / relax_time

        # Set up the model.
        if model == MODEL_NOREX:
            self.func = self.func_NOREX
        if model == MODEL_LM63:
            self.func = self.func_LM63
        if model == MODEL_CR72:
            self.func = self.func_CR72
        if model == MODEL_CR72_RED:
            self.func = self.func_CR72_red
        if model == MODEL_IT99:
            self.func = self.func_IT99
        if model == MODEL_M61:
            self.func = self.func_M61
        if model == MODEL_DPL94:
            self.func = self.func_DPL94
        if model == MODEL_M61B:
            self.func = self.func_M61b
        if model == MODEL_NS_2SITE_3D_RED:
            self.func = self.func_ns_2site_3D_red
        if model == MODEL_NS_2SITE_3D:
            self.func = self.func_ns_2site_3D
        if model == MODEL_NS_2SITE_STAR:
            self.func = self.func_ns_2site_star
        if model == MODEL_NS_2SITE_STAR_RED:
            self.func = self.func_ns_2site_star_red


    def calc_CR72_chi2(self, R20A=None, R20B=None, dw=None, pA=None, kex=None):
        """Calculate the chi-squared value of the 'NS 2-site star' models.

        @keyword R20A:  The R2 value for state A in the absence of exchange.
        @type R20A:     list of float
        @keyword R20B:  The R2 value for state B in the absence of exchange.
        @type R20B:     list of float
        @keyword dw:    The chemical shift differences in ppm for each spin.
        @type dw:       list of float
        @keyword pA:    The population of state A.
        @type pA:       float
        @keyword kex:   The rate of exchange.
        @type kex:      float
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert dw from ppm to rad/s.
                dw_frq = dw[spin_index] * self.frqs[spin_index, frq_index]

                # Back calculate the R2eff values.
                r2eff_CR72(r20a=R20A[r20_index], r20b=R20B[r20_index], pA=pA, dw=dw_frq, kex=kex, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def calc_ns_2site_3D_chi2(self, R20A=None, R20B=None, dw=None, pA=None, kex=None):
        """Calculate the chi-squared value of the 'NS 2-site' models.

        @keyword R20A:  The R2 value for state A in the absence of exchange.
        @type R20A:     list of float
        @keyword R20B:  The R2 value for state B in the absence of exchange.
        @type R20B:     list of float
        @keyword dw:    The chemical shift differences in ppm for each spin.
        @type dw:       list of float
        @keyword pA:    The population of state A.
        @type pA:       float
        @keyword kex:   The rate of exchange.
        @type kex:      float
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Once off parameter conversions.
        pB = 1.0 - pA
        k_AB = pA * kex
        k_BA = pB * kex

        # This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
        self.M0[1] = pA
        self.M0[4] = pB

        # Chi-squared initialisation.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert dw from ppm to rad/s.
                dw_frq = dw[spin_index] * self.frqs[spin_index, frq_index]

                # Back calculate the R2eff values.
                r2eff_ns_2site_3D(r180x=self.r180x, M0=self.M0, r20a=R20A[r20_index], r20b=R20B[r20_index], pA=pA, pB=pB, dw=dw_frq, k_AB=k_AB, k_BA=k_BA, inv_tcpmg=self.inv_relax_time, tcp=self.tau_cpmg, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points, power=self.power)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def calc_ns_2site_star_chi2(self, R20A=None, R20B=None, dw=None, pA=None, kex=None):
        """Calculate the chi-squared value of the 'NS 2-site star' models.

        @keyword R20A:  The R2 value for state A in the absence of exchange.
        @type R20A:     list of float
        @keyword R20B:  The R2 value for state B in the absence of exchange.
        @type R20B:     list of float
        @keyword dw:    The chemical shift differences in ppm for each spin.
        @type dw:       list of float
        @keyword pA:    The population of state A.
        @type pA:       float
        @keyword kex:   The rate of exchange.
        @type kex:      float
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Once off parameter conversions.
        pB = 1.0 - pA
        k_AB = pA * kex
        k_BA = pB * kex

        # Set up the matrix that contains the exchange terms between the two states A and B.
        self.Rex[0, 0] = -k_AB
        self.Rex[0, 1] = k_BA
        self.Rex[1, 0] = k_AB
        self.Rex[1, 1] = -k_BA

        # This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
        self.M0[0] = pA
        self.M0[1] = pB

        # Chi-squared initialisation.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert dw from ppm to rad/s.
                dw_frq = dw[spin_index] * self.frqs[spin_index, frq_index]

                # Back calculate the R2eff values.
                r2eff_ns_2site_star(Rr=self.Rr, Rex=self.Rex, RCS=self.RCS, R=self.R, M0=self.M0, r20a=R20A[r20_index], r20b=R20B[r20_index], dw=dw_frq, inv_tcpmg=self.inv_relax_time, tcp=self.tau_cpmg, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points, power=self.power)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


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
        R20A = params[:self.end_index[0]]
        R20B = params[self.end_index[0]:self.end_index[1]]
        dw = params[self.end_index[1]:self.end_index[2]]
        pA = params[self.end_index[2]]
        kex = params[self.end_index[2]+1]

        # Calculate and return the chi-squared value.
        return self.calc_CR72_chi2(R20A=R20A, R20B=R20B, dw=dw, pA=pA, kex=kex)


    def func_CR72_red(self, params):
        """Target function for the Carver and Richards (1972) 2-site exchange model on all time scales.

        This assumes that pA > pB, and hence this must be implemented as a constraint.  For this model, the simplification R20A = R20B is assumed.


        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Calculate and return the chi-squared value.
        return self.calc_CR72_chi2(R20A=R20, R20B=R20, dw=dw, pA=pA, kex=kex)


    def func_DPL94(self, params):
        """Target function for the Davis, Perlman and London (1994) fast 2-site exchange model for R1rho-type experiments.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        phi_ex = params[self.end_index[0]:self.end_index[1]]
        kex = params[self.end_index[1]]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert phi_ex from ppm^2 to (rad/s)^2.
                phi_ex_scaled = phi_ex[spin_index] * self.frqs[spin_index, frq_index]**2

                # Back calculate the R2eff values.
                r1rho_DPL94(r1rho_prime=R20[r20_index], phi_ex=phi_ex_scaled, kex=kex, spin_lock_fields=self.spin_lock_nu1, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_IT99(self, params):
        """Target function for the Ishima and Torchia (1999) 2-site model for all timescales with pA >> pB.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        phi_ex = params[self.end_index[0]:self.end_index[1]]
        padw2 = params[self.end_index[1]:self.end_index[2]]
        tex = params[self.end_index[2]]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert phi_ex and pa.dw^2 from ppm^2 to (rad/s)^2.
                phi_ex_scaled = phi_ex[spin_index] * self.frqs[spin_index, frq_index]**2
                padw2_scaled = padw2[spin_index] * self.frqs[spin_index, frq_index]**2

                # Back calculate the R2eff values.
                r2eff_IT99(r20=R20[r20_index], phi_ex=phi_ex_scaled, padw2=padw2_scaled, tex=tex, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

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
        R20 = params[:self.end_index[0]]
        phi_ex = params[self.end_index[0]:self.end_index[1]]
        kex = params[self.end_index[1]]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert phi_ex from ppm^2 to (rad/s)^2.
                phi_ex_scaled = phi_ex[spin_index] * self.frqs[spin_index, frq_index]**2

                # Back calculate the R2eff values.
                r2eff_LM63(r20=R20[r20_index], phi_ex=phi_ex_scaled, kex=kex, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_M61(self, params):
        """Target function for the Meiboom (1961) fast 2-site exchange model for R1rho-type experiments.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        phi_ex = params[self.end_index[0]:self.end_index[1]]
        kex = params[self.end_index[1]]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert phi_ex from ppm^2 to (rad/s)^2.
                phi_ex_scaled = phi_ex[spin_index] * self.frqs[spin_index, frq_index]**2

                # Back calculate the R2eff values.
                r1rho_M61(r1rho_prime=R20[r20_index], phi_ex=phi_ex_scaled, kex=kex, spin_lock_fields=self.spin_lock_nu1, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_M61b(self, params):
        """Target function for the Meiboom (1961) R1rho on-resonance 2-site model for skewed populations (pA >> pB).

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert dw from ppm to rad/s.
                dw_frq = dw[spin_index] * self.frqs[spin_index, frq_index]

                # Back calculate the R1rho values.
                r1rho_M61b(r1rho_prime=R20[r20_index], pA=pA, dw=dw_frq, kex=kex, spin_lock_fields=self.spin_lock_nu1, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_NOREX(self, params):
        """Target function for no exchange.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # The R2eff values as R20 values.
                for i in range(self.num_disp_points):
                    self.back_calc[spin_index, frq_index, i] = R20[r20_index]

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_ns_2site_3D(self, params):
        """Target function for the numerical solution for the 2-site Bloch-McConnell equations.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20A = params[:self.end_index[0]]
        R20B = params[self.end_index[0]:self.end_index[1]]
        dw = params[self.end_index[1]:self.end_index[2]]
        pA = params[self.end_index[2]]
        kex = params[self.end_index[2]+1]

        # Calculate and return the chi-squared value.
        return self.calc_ns_2site_3D_chi2(R20A=R20A, R20B=R20B, dw=dw, pA=pA, kex=kex)


    def func_ns_2site_3D_red(self, params):
        """Target function for the numerical solution for the 2-site Bloch-McConnell equations.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Calculate and return the chi-squared value.
        return self.calc_ns_2site_3D_chi2(R20A=R20, R20B=R20, dw=dw, pA=pA, kex=kex)


    def func_ns_2site_star(self, params):
        """Target function for the numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20A = params[:self.end_index[0]]
        R20B = params[self.end_index[0]:self.end_index[1]]
        dw = params[self.end_index[1]:self.end_index[2]]
        pA = params[self.end_index[2]]
        kex = params[self.end_index[2]+1]

        # Calculate and return the chi-squared value.
        return self.calc_ns_2site_star_chi2(R20A=R20A, R20B=R20B, dw=dw, pA=pA, kex=kex)


    def func_ns_2site_star_red(self, params):
        """Target function for the numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices.

        This is the model whereby the simplification R20A = R20B is assumed.


        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Calculate and return the chi-squared value.
        return self.calc_ns_2site_star_chi2(R20A=R20, R20B=R20, dw=dw, pA=pA, kex=kex)
