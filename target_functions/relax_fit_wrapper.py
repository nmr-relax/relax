###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
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
"""The R1 and R2 exponential relaxation curve fitting optimisation functions."""

# Python module imports.
from numpy import array, float64, ndarray, nan_to_num

# relax module imports.
from dep_check import C_module_exp_fn
from specific_analyses.relax_fit.parameters import assemble_param_vector

# C modules.
if C_module_exp_fn:
    from target_functions.relax_fit import back_calc_I, d2func_exp, d2func_inv, d2func_sat, dfunc_exp, dfunc_inv, dfunc_sat, func_exp, func_inv, func_sat, jacobian_chi2_exp, jacobian_chi2_inv, jacobian_chi2_sat, jacobian_exp, jacobian_inv, jacobian_sat, setup 


class Relax_fit_opt:
    """The exponential curve-fitting Python to C wrapper target function class."""

    def __init__(self, model=None, num_params=None, values=None, errors=None, relax_times=None, scaling_matrix=None):
        """Set up the target function class and alias the target functions.

        @keyword model:             The exponential curve type.  This can be 'exp' for the standard two parameter exponential curve, 'inv' for the inversion recovery experiment, and 'sat' for the saturation recovery experiment.
        @type model:                str
        @keyword num_params:        The number of parameters in the model.
        @type num_params:           int
        @keyword values:            The peak intensities.
        @type values:               list of float
        @keyword errors:            The peak intensity errors.
        @type errors:               list of float
        @keyword relax_times:       The list of relaxation times.
        @type relax_times:          list of float
        @keyword scaling_matrix:    The scaling matrix in a diagonalised list form.
        @type scaling_matrix:       list of float
        """

        # Store the args.
        self.model = model

        # Initialise the C code.
        setup(num_params=num_params, num_times=len(relax_times), values=values, sd=errors, relax_times=relax_times, scaling_matrix=scaling_matrix)

        # Alias the target functions.
        if model == 'exp':
            self.func = self.func_exp
            self.dfunc = self.dfunc_exp
            self.d2func = self.d2func_exp
        elif model == 'inv':
            self.func = self.func_inv
            self.dfunc = self.dfunc_inv
            self.d2func = self.d2func_inv
        elif model == 'sat':
            self.func = self.func_sat
            self.dfunc = self.dfunc_sat
            self.d2func = self.d2func_sat

        # Alias the Jacobian C functions.
        if model == 'exp':
            self.jacobian = jacobian_exp
            self.jacobian_chi2 = jacobian_chi2_exp
        elif model == 'inv':
            self.jacobian = jacobian_inv
            self.jacobian_chi2 = jacobian_chi2_inv
        elif model == 'sat':
            self.jacobian = jacobian_sat
            self.jacobian_chi2 = jacobian_chi2_sat


    def back_calc_data(self):
        """Return the back-calculated data from the C code.

        @return:    The back-calculated peak intensities.
        @rtype:     list of float
        """

        # Return the data.
        return back_calc_I()


    def func_exp(self, params):
        """Wrapper function for the C module, for converting numpy arrays.

        @param params:  The parameter array from the minimisation code.
        @type params:   numpy array
        @return:        The function value generated by the C module.
        @rtype:         float
        """

        # Convert if necessary.
        if isinstance(params, ndarray):
            params = params.tolist()

        # Call the C code.
        chi2 = func_exp(params)

        # Return the chi2 value.
        return nan_to_num(chi2)


    def func_inv(self, params):
        """Wrapper function for the C module, for converting numpy arrays.

        @param params:  The parameter array from the minimisation code.
        @type params:   numpy array
        @return:        The function value generated by the C module.
        @rtype:         float
        """

        # Convert if necessary.
        if isinstance(params, ndarray):
            params = params.tolist()

        # Call the C code.
        chi2 = func_inv(params)

        # Return the chi2 value.
        return nan_to_num(chi2)


    def func_sat(self, params):
        """Wrapper function for the C module, for converting numpy arrays.

        @param params:  The parameter array from the minimisation code.
        @type params:   numpy array
        @return:        The function value generated by the C module.
        @rtype:         float
        """

        # Convert if necessary.
        if isinstance(params, ndarray):
            params = params.tolist()

        # Call the C code.
        chi2 = func_sat(params)

        # Return the chi2 value.
        return nan_to_num(chi2)


    def dfunc_exp(self, params):
        """Wrapper function for the C module, for converting numpy arrays.

        @param params:  The parameter array from the minimisation code.
        @type params:   numpy array
        @return:        The gradient generated by the C module converted to numpy format.
        @rtype:         numpy float64 array
        """

        # Convert if necessary.
        if isinstance(params, ndarray):
            params = params.tolist()

        # Call the C code.
        dchi2 = dfunc_exp(params)

        # Return the chi2 gradient as a numpy array.
        return array(dchi2, float64)


    def dfunc_inv(self, params):
        """Wrapper function for the C module, for converting numpy arrays.

        @param params:  The parameter array from the minimisation code.
        @type params:   numpy array
        @return:        The gradient generated by the C module converted to numpy format.
        @rtype:         numpy float64 array
        """

        # Convert if necessary.
        if isinstance(params, ndarray):
            params = params.tolist()

        # Call the C code.
        dchi2 = dfunc_inv(params)

        # Return the chi2 gradient as a numpy array.
        return array(dchi2, float64)


    def dfunc_sat(self, params):
        """Wrapper function for the C module, for converting numpy arrays.

        @param params:  The parameter array from the minimisation code.
        @type params:   numpy array
        @return:        The gradient generated by the C module converted to numpy format.
        @rtype:         numpy float64 array
        """

        # Convert if necessary.
        if isinstance(params, ndarray):
            params = params.tolist()

        # Call the C code.
        dchi2 = dfunc_sat(params)

        # Return the chi2 gradient as a numpy array.
        return array(dchi2, float64)


    def d2func_exp(self, params):
        """Wrapper function for the C module, for converting numpy arrays.

        @param params:  The parameter array from the minimisation code.
        @type params:   numpy array
        @return:        The Hessian generated by the C module converted to numpy format.
        @rtype:         numpy float64 rank-2 array
        """

        # Convert if necessary.
        if isinstance(params, ndarray):
            params = params.tolist()

        # Call the C code.
        d2chi2 = d2func_exp(params)

        # Return the chi2 Hessian as a numpy array.
        return array(d2chi2, float64)


    def d2func_inv(self, params):
        """Wrapper function for the C module, for converting numpy arrays.

        @param params:  The parameter array from the minimisation code.
        @type params:   numpy array
        @return:        The Hessian generated by the C module converted to numpy format.
        @rtype:         numpy float64 rank-2 array
        """

        # Convert if necessary.
        if isinstance(params, ndarray):
            params = params.tolist()

        # Call the C code.
        d2chi2 = d2func_inv(params)

        # Return the chi2 Hessian as a numpy array.
        return array(d2chi2, float64)


    def d2func_sat(self, params):
        """Wrapper function for the C module, for converting numpy arrays.

        @param params:  The parameter array from the minimisation code.
        @type params:   numpy array
        @return:        The Hessian generated by the C module converted to numpy format.
        @rtype:         numpy float64 rank-2 array
        """

        # Convert if necessary.
        if isinstance(params, ndarray):
            params = params.tolist()

        # Call the C code.
        d2chi2 = d2func_sat(params)

        # Return the chi2 Hessian as a numpy array.
        return array(d2chi2, float64)
