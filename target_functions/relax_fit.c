/*
 * Copyright (C) 2006-2014 Edward d'Auvergne
 *
 * This file is part of the program relax (http://www.nmr-relax.com).
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/* This include must come first. */
#include <Python.h>
#include "structmember.h"

/* The numpy array object header file, must come second */
#include <numpy/arrayobject.h>
#include <numpy/libnumarray.h>


/* Allow for debugging printouts. */
#include <stdio.h>

/* Include all of the variable definitions. */
#include "relax_fit.h"

/* The chi2 and exponential functions. */
#include "c_chi2.h"
#include "exponential.h"


/* Declaration of the Relax_fit class and its contents. */
typedef struct {
    PyObject_HEAD
    PyObject *model;    /* The exponential curve type.  This can be 'exp' for the standard two parameter exponential curve, 'inv' for the inversion recovery experiment, and 'sat' for the saturation recovery experiment. */
    int num_params;
    int num_times;
    PyArrayObject *dchi2;
    PyArrayObject *d2chi2;
    PyArrayObject *jacobian;
    PyArrayObject *jacobian_chi2;
} Relax_fit;


void param_to_c(Relax_fit *self, PyArrayObject *params_arg) {
    /* Convert the Python parameter list to a C array. */

    /* Declarations. */
    int i;

    /* Place the parameter array elements into the C array. */
    for (i = 0; i < self->num_params; i++) {
        /* Scale the parameter. */
        params[i] = *(double *)(params_arg->data + i*params_arg->strides[0]) * scaling_matrix[i];
    }
}

static PyObject *
func_exp(Relax_fit *self, PyObject *args) {
    /* Target function for the two parameter exponential for calculating and returning the chi-squared value.
     *
     * Firstly the back calculated intensities are generated, then the chi-squared statistic is
     * calculated.
     */

    /* Declarations. */
    PyArrayObject *params_arg;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters numpy array to a C array. */
    param_to_c(self, params_arg);


    /* Back calculated the peak intensities. */
    exponential(params[index_I0], params[index_R], relax_times, back_calc, self->num_times);

    /* Calculate and return the chi-squared value. */
    return PyFloat_FromDouble(chi2(values, variance, back_calc, self->num_times));
}


static PyObject *
func_inv(Relax_fit *self, PyObject *args) {
    /* Inversion recovery experiment target function for calculating and returning the chi-squared value.
     *
     * Firstly the back calculated intensities are generated, then the chi-squared statistic is
     * calculated.
     */

    /* Declarations. */
    PyArrayObject *params_arg;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* Back calculated the peak intensities. */
    exponential_inv(params[index_I0], params[index_inv_Iinf], params[index_R], relax_times, back_calc, self->num_times);

    /* Calculate and return the chi-squared value. */
    return PyFloat_FromDouble(chi2(values, variance, back_calc, self->num_times));
}


static PyObject *
func_sat(Relax_fit *self, PyObject *args) {
    /* Saturation recovery experiment target function for calculating and returning the chi-squared value.
     *
     * Firstly the back calculated intensities are generated, then the chi-squared statistic is
     * calculated.
     */

    /* Declarations. */
    PyArrayObject *params_arg;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* Back calculated the peak intensities. */
    exponential_sat(params[index_Iinf], params[index_R], relax_times, back_calc, self->num_times);

    /* Calculate and return the chi-squared value. */
    return PyFloat_FromDouble(chi2(values, variance, back_calc, self->num_times));
}


static PyObject *
dfunc_exp(Relax_fit *self, PyObject *args) {
    /* Target function for the two parameter exponential for calculating and returning the chi-squared gradient.
     *
     */

    /* Declarations. */
    PyArrayObject *params_arg;
    int i;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* Back calculated the peak intensities. */
    exponential(params[index_I0], params[index_R], relax_times, back_calc, self->num_times);

    /* The partial derivates. */
    exponential_dR(params[index_I0], params[index_R], index_R, relax_times, back_calc_grad, self->num_times);
    exponential_dI0(params[index_I0], params[index_R], index_I0, relax_times, back_calc_grad, self->num_times);

    /* The chi-squared gradient. */
    dchi2(dchi2_vals, values, back_calc, back_calc_grad, variance, self->num_times, self->num_params);

    /* Store in the numpy array, and scale the values. */
    for (i = 0; i < self->num_params; i++) {
        NA_set1_Float64(self->dchi2, i, dchi2_vals[i] * scaling_matrix[i]);
    }

    /* Return the gradient, incrementing the reference count. */
    Py_INCREF(self->dchi2);
    return PyArray_Return(self->dchi2);
}


static PyObject *
dfunc_inv(Relax_fit *self, PyObject *args) {
    /* Inversion recovery experiment target function for the two parameter exponential for calculating and returning the chi-squared gradient. */

    /* Declarations. */
    PyArrayObject *params_arg;
    int i;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* Back calculated the peak intensities. */
    exponential_inv(params[index_I0], params[index_inv_Iinf], params[index_R], relax_times, back_calc, self->num_times);

    /* The partial derivates. */
    exponential_inv_dR(params[index_I0], params[index_inv_Iinf], params[index_R], index_R, relax_times, back_calc_grad, self->num_times);
    exponential_inv_dI0(params[index_I0], params[index_inv_Iinf], params[index_R], index_I0, relax_times, back_calc_grad, self->num_times);
    exponential_inv_dIinf(params[index_I0], params[index_inv_Iinf], params[index_R], index_inv_Iinf, relax_times, back_calc_grad, self->num_times);

    /* The chi-squared gradient. */
    dchi2(dchi2_vals, values, back_calc, back_calc_grad, variance, self->num_times, self->num_params);

    /* Store in the numpy array, and scale the values. */
    for (i = 0; i < self->num_params; i++) {
        NA_set1_Float64(self->dchi2, i, dchi2_vals[i] * scaling_matrix[i]);
    }

    /* Return the gradient, incrementing the reference count. */
    Py_INCREF(self->dchi2);
    return PyArray_Return(self->dchi2);
}


static PyObject *
dfunc_sat(Relax_fit *self, PyObject *args) {
    /* Saturation recovery experiment target function for the two parameter exponential for calculating and returning the chi-squared gradient.
     *
     */

    /* Declarations. */
    PyArrayObject *params_arg;
    int i;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* Back calculated the peak intensities. */
    exponential_sat(params[index_Iinf], params[index_R], relax_times, back_calc, self->num_times);

    /* The partial derivates. */
    exponential_sat_dR(params[index_Iinf], params[index_R], index_R, relax_times, back_calc_grad, self->num_times);
    exponential_sat_dIinf(params[index_Iinf], params[index_R], index_Iinf, relax_times, back_calc_grad, self->num_times);

    /* The chi-squared gradient. */
    dchi2(dchi2_vals, values, back_calc, back_calc_grad, variance, self->num_times, self->num_params);

    /* Store in the numpy array, and scale the values. */
    for (i = 0; i < self->num_params; i++) {
        NA_set1_Float64(self->dchi2, i, dchi2_vals[i] * scaling_matrix[i]);
    }

    /* Return the gradient, incrementing the reference count. */
    Py_INCREF(self->dchi2);
    return PyArray_Return(self->dchi2);
}


static PyObject *
d2func_exp(Relax_fit *self, PyObject *args) {
    /* Target function for the two parameter exponential for calculating and returning the chi-squared Hessian.
     *
     */

    /* Declarations. */
    PyArrayObject *params_arg;
    int j, k;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* Back calculated the peak intensities. */
    exponential(params[index_I0], params[index_R], relax_times, back_calc, self->num_times);

    /* The partial derivatives. */
    exponential_dR(params[index_I0], params[index_R], index_R, relax_times, back_calc_grad, self->num_times);
    exponential_dI0(params[index_I0], params[index_R], index_I0, relax_times, back_calc_grad, self->num_times);

    /* The second partial derivatives. */
    exponential_dR2(params[index_I0], params[index_R], index_R, relax_times, back_calc_hess, self->num_times);
    exponential_dI02(params[index_I0], params[index_R], index_I0, relax_times, back_calc_hess, self->num_times);
    exponential_dR_dI0(params[index_I0], params[index_R], index_R, index_I0, relax_times, back_calc_hess, self->num_times);

    /* The chi-squared Hessian. */
    d2chi2(d2chi2_vals, values, back_calc, back_calc_grad, back_calc_hess, variance, self->num_times, self->num_params);

    /* Store in the numpy array, and scale the values. */
    for (j = 0; j < self->num_params; j++) {
        for (k = 0; k < self->num_params; k++) {
            NA_set2_Float64(self->d2chi2, j, k, d2chi2_vals[j][k] * scaling_matrix[j] * scaling_matrix[k]);
        }
    }

    /* Return the Hessian, incrementing the reference count. */
    Py_INCREF(self->d2chi2);
    return PyArray_Return(self->d2chi2);
}


static PyObject *
d2func_inv(Relax_fit *self, PyObject *args) {
    /* Target function for the two parameter exponential for calculating and returning the chi-squared Hessian.
     *
     */

    /* Declarations. */
    PyArrayObject *params_arg;
    int j, k;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* Back calculated the peak intensities. */
    exponential_inv(params[index_I0], params[index_inv_Iinf], params[index_R], relax_times, back_calc, self->num_times);

    /* The partial derivatives. */
    exponential_inv_dR(params[index_I0], params[index_inv_Iinf], params[index_R], index_R, relax_times, back_calc_grad, self->num_times);
    exponential_inv_dI0(params[index_I0], params[index_inv_Iinf], params[index_R], index_I0, relax_times, back_calc_grad, self->num_times);
    exponential_inv_dIinf(params[index_I0], params[index_inv_Iinf], params[index_R], index_inv_Iinf, relax_times, back_calc_grad, self->num_times);

    /* The second partial derivatives. */
    exponential_inv_dR2(params[index_I0], params[index_inv_Iinf], params[index_R], index_R, relax_times, back_calc_hess, self->num_times);
    exponential_inv_dI02(params[index_I0], params[index_inv_Iinf], params[index_R], index_I0, relax_times, back_calc_hess, self->num_times);
    exponential_inv_dIinf2(params[index_I0], params[index_inv_Iinf], params[index_R], index_inv_Iinf, relax_times, back_calc_hess, self->num_times);
    exponential_inv_dR_dI0(params[index_I0], params[index_inv_Iinf], params[index_R], index_R, index_I0, relax_times, back_calc_hess, self->num_times);
    exponential_inv_dR_dIinf(params[index_I0], params[index_inv_Iinf], params[index_R], index_R, index_inv_Iinf, relax_times, back_calc_hess, self->num_times);
    exponential_inv_dI0_dIinf(params[index_I0], params[index_inv_Iinf], params[index_R], index_I0, index_inv_Iinf, relax_times, back_calc_hess, self->num_times);

    /* The chi-squared Hessian. */
    d2chi2(d2chi2_vals, values, back_calc, back_calc_grad, back_calc_hess, variance, self->num_times, self->num_params);

    /* Store in the numpy array, and scale the values. */
    for (j = 0; j < self->num_params; j++) {
        for (k = 0; k < self->num_params; k++) {
            NA_set2_Float64(self->d2chi2, j, k, d2chi2_vals[j][k] * scaling_matrix[j] * scaling_matrix[k]);
        }
    }

    /* Return the Hessian, incrementing the reference count. */
    Py_INCREF(self->d2chi2);
    return PyArray_Return(self->d2chi2);
}


static PyObject *
d2func_sat(Relax_fit *self, PyObject *args) {
    /* Saturation recovery experiment target function for the two parameter exponential for calculating and returning the chi-squared Hessian.
     *
     */

    /* Declarations. */
    PyArrayObject *params_arg;
    int j, k;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* Back calculated the peak intensities. */
    exponential_sat(params[index_Iinf], params[index_R], relax_times, back_calc, self->num_times);

    /* The partial derivatives. */
    exponential_sat_dR(params[index_Iinf], params[index_R], index_R, relax_times, back_calc_grad, self->num_times);
    exponential_sat_dIinf(params[index_Iinf], params[index_R], index_Iinf, relax_times, back_calc_grad, self->num_times);

    /* The second partial derivatives. */
    exponential_sat_dR2(params[index_Iinf], params[index_R], index_R, relax_times, back_calc_hess, self->num_times);
    exponential_sat_dIinf2(params[index_Iinf], params[index_R], index_Iinf, relax_times, back_calc_hess, self->num_times);
    exponential_sat_dR_dIinf(params[index_Iinf], params[index_R], index_R, index_Iinf, relax_times, back_calc_hess, self->num_times);

    /* The chi-squared Hessian. */
    d2chi2(d2chi2_vals, values, back_calc, back_calc_grad, back_calc_hess, variance, self->num_times, self->num_params);

    /* Store in the numpy array, and scale the values. */
    for (j = 0; j < self->num_params; j++) {
        for (k = 0; k < self->num_params; k++) {
            NA_set2_Float64(self->d2chi2, j, k, d2chi2_vals[j][k] * scaling_matrix[j] * scaling_matrix[k]);
        }
    }

    /* Return the Hessian, incrementing the reference count. */
    Py_INCREF(self->d2chi2);
    return PyArray_Return(self->d2chi2);
}


static PyObject *
back_calc_data(Relax_fit *self, PyObject *args) {
    /* Return the back calculated peak intensities as a Python list. */

    /* Declarations. */
    PyArrayObject *back_calc_array;
    int i, dims[1];

    dims[0] = self->num_times;
    back_calc_array = (PyArrayObject *) PyArray_FromDims(1, dims, NPY_DOUBLE);

    /* Copy the values out of the C array into the Python array. */
    for (i = 0; i < self->num_times; i++) {
        NA_set1_Float64(back_calc_array, i, back_calc[i]);
    }

    /* Return the numpy array. */
    return PyArray_Return(back_calc_array);
}


static PyObject *
jacobian_exp(Relax_fit *self, PyObject *args) {
    /* Return the Jacobian for the two parameter exponential as a Python list of lists. */

    /* Declarations. */
    PyArrayObject *params_arg;
    int i, j;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* The partial derivatives. */
    exponential_dR(params[index_I0], params[index_R], index_R, relax_times, back_calc_grad, self->num_times);
    exponential_dI0(params[index_I0], params[index_R], index_I0, relax_times, back_calc_grad, self->num_times);

    /* Store in the numpy array. */
    for (i = 0; i < self->num_params; i++) {
        for (j = 0; j < self->num_times; j++) {
            NA_set2_Float64(self->jacobian, i, j, back_calc_grad[i][j]);
        }
    }

    /* Return the Jacobian, incrementing the reference count. */
    Py_INCREF(self->jacobian);
    return PyArray_Return(self->jacobian);
}


static PyObject *
jacobian_inv(Relax_fit *self, PyObject *args) {
    /* Return the Jacobian for the two parameter exponential as a Python list of lists. */

    /* Declarations. */
    PyArrayObject *params_arg;
    int i, j;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* The partial derivatives. */
    exponential_inv_dR(params[index_I0], params[index_inv_Iinf], params[index_R], index_R, relax_times, back_calc_grad, self->num_times);
    exponential_inv_dI0(params[index_I0], params[index_inv_Iinf], params[index_R], index_I0, relax_times, back_calc_grad, self->num_times);
    exponential_inv_dIinf(params[index_I0], params[index_inv_Iinf], params[index_R], index_inv_Iinf, relax_times, back_calc_grad, self->num_times);

    /* Store in the numpy array. */
    for (i = 0; i < self->num_params; i++) {
        for (j = 0; j < self->num_times; j++) {
            NA_set2_Float64(self->jacobian, i, j, back_calc_grad[i][j]);
        }
    }

    /* Return the Jacobian, incrementing the reference count. */
    Py_INCREF(self->jacobian);
    return PyArray_Return(self->jacobian);
}


static PyObject *
jacobian_sat(Relax_fit *self, PyObject *args) {
    /* Return the Jacobian for the two parameter exponential as a Python list of lists. */

    /* Declarations. */
    PyArrayObject *params_arg;
    int i, j;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* The partial derivatives. */
    exponential_sat_dR(params[index_Iinf], params[index_R], index_R, relax_times, back_calc_grad, self->num_times);
    exponential_sat_dIinf(params[index_Iinf], params[index_R], index_Iinf, relax_times, back_calc_grad, self->num_times);

    /* Store in the numpy array. */
    for (i = 0; i < self->num_params; i++) {
        for (j = 0; j < self->num_times; j++) {
            NA_set2_Float64(self->jacobian, i, j, back_calc_grad[i][j]);
        }
    }

    /* Return the Jacobian, incrementing the reference count. */
    Py_INCREF(self->jacobian);
    return PyArray_Return(self->jacobian);
}


static PyObject *
jacobian_chi2_exp(Relax_fit *self, PyObject *args) {
    /* Return the Jacobian for the two parameter exponential as a Python list of lists.

    The Jacobian
    ============

    The equation is::

                     / yi - yi(theta)     dyi(theta) \
        J_ji  =  -2  | --------------  .  ---------- |
                     \   sigma_i**2        dthetaj   /

    where
        - i is the index over data sets.
        - j is the parameter index.
        - theta is the parameter vector.
        - yi are the values of the measured data set.
        - yi(theta) are the values of the back calculated data set.
        - dyi(theta)/dthetaj are the values of the back calculated gradient for parameter j.
        - sigma_i are the values of the error set.

     */

    /* Declarations. */
    PyArrayObject *params_arg;
    int i, j;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* Back calculated the peak intensities. */
    exponential(params[index_I0], params[index_R], relax_times, back_calc, self->num_times);

    /* The partial derivatives. */
    exponential_dR(params[index_I0], params[index_R], index_R, relax_times, back_calc_grad, self->num_times);
    exponential_dI0(params[index_I0], params[index_R], index_I0, relax_times, back_calc_grad, self->num_times);

    /* Assemble the chi-squared Jacobian. */
    for (j = 0; j < self->num_params; ++j) {
        for (i = 0; i < self->num_times; ++i) {
            jacobian_matrix[j][i] = -2.0 / variance[i] * (values[i] - back_calc[i]) * back_calc_grad[j][i];
        }
    }

    /* Store in the numpy array. */
    for (i = 0; i < self->num_params; i++) {
        for (j = 0; j < self->num_times; j++) {
            NA_set2_Float64(self->jacobian_chi2, i, j, jacobian_matrix[i][j]);
        }
    }

    /* Return the Jacobian, incrementing the reference count. */
    Py_INCREF(self->jacobian_chi2);
    return PyArray_Return(self->jacobian_chi2);
}


static PyObject *
jacobian_chi2_inv(Relax_fit *self, PyObject *args) {
    /* Return the Jacobian for the inversion recovery experiment as a Python list of lists.

    The Jacobian
    ============

    The equation is::

                     / yi - yi(theta)     dyi(theta) \
        J_ji  =  -2  | --------------  .  ---------- |
                     \   sigma_i**2        dthetaj   /

    where
        - i is the index over data sets.
        - j is the parameter index.
        - theta is the parameter vector.
        - yi are the values of the measured data set.
        - yi(theta) are the values of the back calculated data set.
        - dyi(theta)/dthetaj are the values of the back calculated gradient for parameter j.
        - sigma_i are the values of the error set.

     */

    /* Declarations. */
    PyArrayObject *params_arg;
    int i, j;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* Back calculated the peak intensities. */
    exponential_inv(params[index_I0], params[index_inv_Iinf], params[index_R], relax_times, back_calc, self->num_times);

    /* The partial derivatives. */
    exponential_inv_dR(params[index_I0], params[index_inv_Iinf], params[index_R], index_R, relax_times, back_calc_grad, self->num_times);
    exponential_inv_dI0(params[index_I0], params[index_inv_Iinf], params[index_R], index_I0, relax_times, back_calc_grad, self->num_times);
    exponential_inv_dIinf(params[index_I0], params[index_inv_Iinf], params[index_R], index_inv_Iinf, relax_times, back_calc_grad, self->num_times);

    /* Assemble the chi-squared Jacobian. */
    for (j = 0; j < self->num_params; ++j) {
        for (i = 0; i < self->num_times; ++i) {
            jacobian_matrix[j][i] = -2.0 / variance[i] * (values[i] - back_calc[i]) * back_calc_grad[j][i];
        }
    }

    /* Store in the numpy array. */
    for (i = 0; i < self->num_params; i++) {
        for (j = 0; j < self->num_times; j++) {
            NA_set2_Float64(self->jacobian_chi2, i, j, jacobian_matrix[i][j]);
        }
    }

    /* Return the Jacobian, incrementing the reference count. */
    Py_INCREF(self->jacobian_chi2);
    return PyArray_Return(self->jacobian_chi2);
}


static PyObject *
jacobian_chi2_sat(Relax_fit *self, PyObject *args) {
    /* Return the Jacobian for the saturation recovery experiment as a Python list of lists.

    The Jacobian
    ============

    The equation is::

                     / yi - yi(theta)     dyi(theta) \
        J_ji  =  -2  | --------------  .  ---------- |
                     \   sigma_i**2        dthetaj   /

    where
        - i is the index over data sets.
        - j is the parameter index.
        - theta is the parameter vector.
        - yi are the values of the measured data set.
        - yi(theta) are the values of the back calculated data set.
        - dyi(theta)/dthetaj are the values of the back calculated gradient for parameter j.
        - sigma_i are the values of the error set.

     */

    /* Declarations. */
    PyArrayObject *params_arg;
    int i, j;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(self, params_arg);

    /* Back calculated the peak intensities. */
    exponential_sat(params[index_Iinf], params[index_R], relax_times, back_calc, self->num_times);

    /* The partial derivatives. */
    exponential_sat_dR(params[index_Iinf], params[index_R], index_R, relax_times, back_calc_grad, self->num_times);
    exponential_sat_dIinf(params[index_Iinf], params[index_R], index_Iinf, relax_times, back_calc_grad, self->num_times);

    /* Assemble the chi-squared Jacobian. */
    for (j = 0; j < self->num_params; ++j) {
        for (i = 0; i < self->num_times; ++i) {
            jacobian_matrix[j][i] = -2.0 / variance[i] * (values[i] - back_calc[i]) * back_calc_grad[j][i];
        }
    }

    /* Store in the numpy array. */
    for (i = 0; i < self->num_params; i++) {
        for (j = 0; j < self->num_times; j++) {
            NA_set2_Float64(self->jacobian_chi2, i, j, jacobian_matrix[i][j]);
        }
    }

    /* Return the Jacobian, incrementing the reference count. */
    Py_INCREF(self->jacobian_chi2);
    return PyArray_Return(self->jacobian_chi2);
}


/* Definition of all functions of the relax_fit module. */
static PyMethodDef relax_fit_methods[] = {
    {NULL, NULL, 0, NULL}        /* Sentinel. */
};


/* Definition of all methods of the Relax_fit class. */
static PyMethodDef Relax_fit_methods[] = {
    {
        "func",
        NULL,
        METH_VARARGS,
        "Target function alias."
    }, {
        "func_exp",
        (PyCFunction)func_exp,
        METH_VARARGS,
        "Target function for the two parameter exponential for calculating and returning the chi-squared value.\n\nFirstly the back calculated intensities are generated, then the chi-squared statistic is calculated."
    }, {
        "func_inv",
        (PyCFunction)func_inv,
        METH_VARARGS,
        "Target function for the inversion recovery experiment for calculating and returning the chi-squared value.\n\nFirstly the back calculated intensities are generated, then the chi-squared statistic is calculated."
    }, {
        "func_sat",
        (PyCFunction)func_sat,
        METH_VARARGS,
        "Target function for the saturation recovery experiment for calculating and returning the chi-squared value.\n\nFirstly the back calculated intensities are generated, then the chi-squared statistic is calculated."
    }, {
        "dfunc",
        NULL,
        METH_VARARGS,
        "Target function alias."
    }, {
        "dfunc_exp",
        (PyCFunction)dfunc_exp,
        METH_VARARGS,
        "Target function for the two parameter exponential for calculating and returning the chi-squared gradient."
    }, {
        "dfunc_inv",
        (PyCFunction)dfunc_inv,
        METH_VARARGS,
        "Target function for the inversion recovery experiment for calculating and returning the chi-squared gradient."
    }, {
        "dfunc_sat",
        (PyCFunction)dfunc_sat,
        METH_VARARGS,
        "Target function for the saturation recovery experiment for calculating and returning the chi-squared gradient."
    }, {
        "d2func",
        NULL,
        METH_VARARGS,
        "Target function alias."
    }, {
        "d2func_exp",
        (PyCFunction)d2func_exp,
        METH_VARARGS,
        "Target function for the two parameter exponential for calculating and returning the chi-squared Hessian."
    }, {
        "d2func_inv",
        (PyCFunction)d2func_inv,
        METH_VARARGS,
        "Target function for the inversion recovery experiment for calculating and returning the chi-squared Hessian."
    }, {
        "d2func_sat",
        (PyCFunction)d2func_sat,
        METH_VARARGS,
        "Target function for the saturation recovery experiment for calculating and returning the chi-squared Hessian."
    }, {
        "jacobian",
        NULL,
        METH_VARARGS,
        "Jacobian matrix function alias."
    }, {
        "jacobian_exp",
        (PyCFunction)jacobian_exp,
        METH_VARARGS,
        "Return the Jacobian matrix for the two parameter exponential as a Python list."
    }, {
        "jacobian_inv",
        (PyCFunction)jacobian_inv,
        METH_VARARGS,
        "Return the Jacobian matrix for the inversion recovery experiment as a Python list."
    }, {
        "jacobian_sat",
        (PyCFunction)jacobian_sat,
        METH_VARARGS,
        "Return the Jacobian matrix for the saturation recovery experiment as a Python list."
    }, {
        "jacobian_chi2",
        NULL,
        METH_VARARGS,
        "Chi-squared Jacobian matrix function alias."
    }, {
        "jacobian_chi2_exp",
        (PyCFunction)jacobian_chi2_exp,
        METH_VARARGS,
        "Return the Jacobian matrix of the chi-squared function for the two parameter exponential as a Python list."
    }, {
        "jacobian_chi2_inv",
        (PyCFunction)jacobian_chi2_inv,
        METH_VARARGS,
        "Return the Jacobian matrix of the chi-squared function for the inversion recovery experiment as a Python list."
    }, {
        "jacobian_chi2_sat",
        (PyCFunction)jacobian_chi2_sat,
        METH_VARARGS,
        "Return the Jacobian matrix of the chi-squared function for the saturation recovery experiment as a Python list."
    }, {
        "back_calc_data",
        (PyCFunction)back_calc_data,
        METH_VARARGS,
        "Return the back calculated peak intensities as a Python list."
    }, {
        NULL  /* Sentinel */
    }
};


/* Definition of the class instance objects. */
static PyMemberDef Relax_fit_members[] = {
    {
        "model",
        T_OBJECT_EX,
        offsetof(Relax_fit, model),
        0,
        "The exponential curve type.  This can be 'exp' for the standard two parameter exponential curve, 'inv' for the inversion recovery experiment, and 'sat' for the saturation recovery experiment."
    }, {
        "num_params",
        T_INT,
        offsetof(Relax_fit, num_params),
        0,
        "The number of model parameters."
    }, {
        "num_times",
        T_INT,
        offsetof(Relax_fit, num_times),
        0,
        "The number of relaxation times."
    }, {
        "dchi2",
        T_OBJECT, 
        offsetof(Relax_fit, dchi2), 
        0,
        "The gradient numpy array data structure."
    }, {
        "d2chi2",
        T_OBJECT, 
        offsetof(Relax_fit, d2chi2), 
        0,
        "The Hessian numpy array data structure."
    }, {
        "jacobian",
        T_OBJECT, 
        offsetof(Relax_fit, jacobian), 
        0,
        "The Jacobian numpy array data structure."
    }, {
        "jacobian_chi2",
        T_OBJECT, 
        offsetof(Relax_fit, jacobian_chi2), 
        0,
        "The chi-squared Jacobian numpy array data structure."
    },
      {NULL}  /* Sentinel */
};


/* Class destruction. */
static void
Relax_fit_dealloc(Relax_fit *self)
{
    Py_XDECREF(self->model);
    Py_XDECREF(self->dchi2);
    Py_XDECREF(self->d2chi2);
    Py_XDECREF(self->jacobian);
    Py_XDECREF(self->jacobian_chi2);
    #if PY_MAJOR_VERSION >= 3
        Py_TYPE(self)->tp_free((PyObject*)self);
    #else
        self->ob_type->tp_free((PyObject*)self);
    #endif
}


/* The Relax_fit.__getattr__() instance method for obtaining instance attributes. */
static PyObject *
Relax_fit_getattro(Relax_fit *self, PyObject *object)
{
    PyObject *objname_bytes, *result = NULL;
    char *objname;

    /* The object name. */
    #if PY_MAJOR_VERSION >= 3
        objname_bytes = PyUnicode_AsEncodedString(object, "utf-8", "strict");
        objname = PyBytes_AsString(objname_bytes);
    #else
        objname = PyString_AsString(object);
    #endif

    /* Target function aliasing. */
    if (strcmp(objname, "func") == 0) {
        if (strcmp(model_str, model_list[0]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "func_exp");
        else if (strcmp(model_str, model_list[1]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "func_inv");
        else if (strcmp(model_str, model_list[2]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "func_sat");
    }

    /* Target function gradient aliasing. */
    else if (strcmp(objname, "dfunc") == 0) {
        if (strcmp(model_str, model_list[0]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "dfunc_exp");
        else if (strcmp(model_str, model_list[1]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "dfunc_inv");
        else if (strcmp(model_str, model_list[2]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "dfunc_sat");
    }

    /* Target function Hessian aliasing. */
    else if (strcmp(objname, "d2func") == 0) {
        if (strcmp(model_str, model_list[0]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "d2func_exp");
        else if (strcmp(model_str, model_list[1]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "d2func_inv");
        else if (strcmp(model_str, model_list[2]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "d2func_sat");
    }

    /* Jacobian aliasing. */
    else if (strcmp(objname, "jacobian") == 0) {
        if (strcmp(model_str, model_list[0]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "jacobian_exp");
        else if (strcmp(model_str, model_list[1]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "jacobian_inv");
        else if (strcmp(model_str, model_list[2]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "jacobian_sat");
    }

    /* Chi-squared Jacobian aliasing. */
    else if (strcmp(objname, "jacobian_chi2") == 0) {
        if (strcmp(model_str, model_list[0]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "jacobian_chi2_exp");
        else if (strcmp(model_str, model_list[1]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "jacobian_chi2_inv");
        else if (strcmp(model_str, model_list[2]) == 0)
            result = PyObject_GetAttrString((PyObject *)self, "jacobian_chi2_sat");
    }

    /* Normal attribute handling (nothing else to return). */
    else
        result = PyObject_GenericGetAttr((PyObject *)self, object);

    return result;
}


/* The Relax_fit.__new__() method definition for creating the class. */
static PyObject *
Relax_fit_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Relax_fit *self;

    self = (Relax_fit *)type->tp_alloc(type, 0);
    if (self != NULL) {
        /* Set up the model name to the empty string. */
        #if PY_MAJOR_VERSION >= 3
            self->model = PyUnicode_FromString("");
        #else
            self->model = PyString_FromString("");
        #endif
        if (self->model == NULL)
          {
            Py_DECREF(self);
            return NULL;
          }

        /* The number of model parameters. */
        self->num_params = 0;

        /* The number of relaxation times. */
        self->num_times = 0;
    }

    return (PyObject *)self;
}


/* The Relax_fit.__init__() method definition for initialising the class. */
static int
Relax_fit_init(Relax_fit *self, PyObject *args, PyObject *keywords)
{
    /* Python object declarations. */
    PyObject *model=NULL, *values_arg=NULL, *sd_arg=NULL, *relax_times_arg=NULL, *scaling_matrix_arg=NULL, *tmp;
    PyObject *element;

    /* Normal declarations. */
    int i, dims_gradient[1], dims_hessian[2], dims_jacobian[2];

    /* The keyword list. */
    static char *keyword_list[] = {"model", "num_params", "num_times", "values", "sd", "relax_times", "scaling_matrix", NULL};

    /* Parse the function arguments. */
    if (! PyArg_ParseTupleAndKeywords(args, keywords, "|SiiOOOO", keyword_list, &model, &self->num_params, &self->num_times, &values_arg, &sd_arg, &relax_times_arg, &scaling_matrix_arg))
        return -1;

    /* Store the arguments in self. */
    if (model) {
        tmp = self->model;
        Py_INCREF(model);
        self->model = model;
        Py_XDECREF(tmp);
    }

    /* Convert the model to a C character array. */
    model_str = PyString_AsString(model);

    /* Place the parameter related arguments into C arrays. */
    for (i = 0; i < self->num_params; i++) {
        /* The diagonalised scaling matrix list argument element. */
        element = PySequence_GetItem(scaling_matrix_arg, i);
        scaling_matrix[i] = PyFloat_AsDouble(element);
        Py_CLEAR(element);
    }

    /* Place the time related arguments into C arrays. */
    for (i = 0; i < self->num_times; i++) {
        /* The value argument element. */
        element = PySequence_GetItem(values_arg, i);
        values[i] = PyFloat_AsDouble(element);
        Py_CLEAR(element);

        /* The sd argument element. */
        element = PySequence_GetItem(sd_arg, i);
        sd[i] = PyFloat_AsDouble(element);
        Py_CLEAR(element);

        /* Convert the errors to variances to avoid duplicated maths operations for faster calculations. */
        variance[i] = square(sd[i]);

        /* The relax_times argument element. */
        element = PySequence_GetItem(relax_times_arg, i);
        relax_times[i] = PyFloat_AsDouble(element);
        Py_CLEAR(element);
    }

    /* Initialise the gradient, Hessian, and Jacobians. */
    dims_gradient[0] = self->num_params;
    self->dchi2 = (PyArrayObject *) PyArray_FromDims(1, dims_gradient, NPY_DOUBLE);
    dims_hessian[0] = self->num_params;
    dims_hessian[1] = self->num_params;
    self->d2chi2 = (PyArrayObject *) PyArray_FromDims(2, dims_hessian, NPY_DOUBLE);
    dims_jacobian[0] = self->num_params;
    dims_jacobian[1] = self->num_times;
    self->jacobian = (PyArrayObject *) PyArray_FromDims(2, dims_jacobian, NPY_DOUBLE);
    self->jacobian_chi2 = (PyArrayObject *) PyArray_FromDims(2, dims_jacobian, NPY_DOUBLE);

    return 0;
}


/* Define the type object to create the class. */
static PyTypeObject Relax_fit_type = {
    #if PY_MAJOR_VERSION >= 3
        PyVarObject_HEAD_INIT(NULL, 0)
    #else
        PyObject_HEAD_INIT(NULL)
        0,                                  /*ob_size*/
    #endif
    "relax_fit.Relax_fit",                  /*tp_name*/
    sizeof(Relax_fit),                      /*tp_basicsize*/
    0,                                      /*tp_itemsize*/
    (destructor)Relax_fit_dealloc,          /*tp_dealloc*/
    0,                                      /*tp_print*/
    0,                                      /*tp_getattr*/
    0,                                      /*tp_setattr*/
    0,                                      /*tp_compare*/
    0,                                      /*tp_repr*/
    0,                                      /*tp_as_number*/
    0,                                      /*tp_as_sequence*/
    0,                                      /*tp_as_mapping*/
    0,                                      /*tp_hash */
    0,                                      /*tp_call*/
    0,                                      /*tp_str*/
    (getattrofunc)Relax_fit_getattro,       /*tp_getattro*/
    0,                                      /*tp_setattro*/
    0,                                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,    /*tp_flags*/
    "The exponential curve-fitting C module target function class.",    /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    Relax_fit_methods,                      /* tp_methods */
    Relax_fit_members,                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)Relax_fit_init,               /* tp_init */
    0,                                      /* tp_alloc */
    Relax_fit_new,                          /* tp_new */
};


/* Define the Python 3 module. */
#if PY_MAJOR_VERSION >= 3
    static PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "relax_fit",         /* m_name */
        "Relaxation curve-fitting C module.",  /* m_doc */
        -1,                  /* m_size */
        NULL,                /* m_reload */
        NULL,                /* m_traverse */
        NULL,                /* m_clear */
        NULL,                /* m_free */
    };
#endif


/* Declarations for DLL import/export */
#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif


/* Initialise as a Python module. */
PyMODINIT_FUNC
#if PY_MAJOR_VERSION >= 3
    PyInit_relax_fit(void)
    {
        PyObject* m;

        if (PyType_Ready(&Relax_fit_type) < 0)
            return NULL;

        m = PyModule_Create(&moduledef);
        if (m == NULL)
            return NULL;

        Py_INCREF(&Relax_fit_type);
        PyModule_AddObject(m, "Relax_fit", (PyObject *)&Relax_fit_type);

        /* Import the numpy array and numarray modules.  This is essential. */
        import_libnumarray();
        import_array();

        return m;
    }
#else
    initrelax_fit(void)
    {
        PyObject* m;

        if (PyType_Ready(&Relax_fit_type) < 0)
            return;

        m = Py_InitModule3("relax_fit", relax_fit_methods,
                           "Example module that creates an extension type.");
        if (m == NULL)
            return;

        Py_INCREF(&Relax_fit_type);
        PyModule_AddObject(m, "Relax_fit", (PyObject *)&Relax_fit_type);

        /* Import the numpy array and numarray modules.  This is essential. */
        import_libnumarray();
        import_array();
    }
#endif
