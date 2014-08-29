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

/* Include all of the variable definitions. */
#include "relax_fit.h"

/* The chi2 and exponential functions. */
#include "c_chi2.h"
#include "exponential.h"


static PyObject *
setup(PyObject *self, PyObject *args, PyObject *keywords) {
    /* Set up the module in preparation for calls to the target function. */

    /* Python object declarations. */
    PyObject *values_arg, *sd_arg, *relax_times_arg, *scaling_matrix_arg;
    PyObject *element;

    /* Normal declarations. */
    int i;

    /* The keyword list. */
    static char *keyword_list[] = {"num_params", "num_times", "values", "sd", "relax_times", "scaling_matrix", NULL};

    /* Parse the function arguments. */
    if (!PyArg_ParseTupleAndKeywords(args, keywords, "iiOOOO", keyword_list, &num_params, &num_times, &values_arg, &sd_arg, &relax_times_arg, &scaling_matrix_arg))
        return NULL;

    /* Place the parameter related arguments into C arrays. */
    for (i = 0; i < num_params; i++) {
        /* The diagonalised scaling matrix list argument element. */
        element = PySequence_GetItem(scaling_matrix_arg, i);
        scaling_matrix[i] = PyFloat_AsDouble(element);
        Py_CLEAR(element);
    }

    /* Place the time related arguments into C arrays. */
    for (i = 0; i < num_times; i++) {
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

    /* The macro for returning the Python None object. */
    Py_RETURN_NONE;
}


void param_to_c(PyObject *params_arg) {
    /* Convert the Python parameter list to a C array. */

    /* Declarations. */
    PyObject *element;
    int i;

    /* Place the parameter array elements into the C array. */
    for (i = 0; i < num_params; i++) {
        /* Get the element. */
        element = PySequence_GetItem(params_arg, i);

        /* Convert to a C double, then free the memory. */
        params[i] = PyFloat_AsDouble(element);
        Py_CLEAR(element);

        /* Scale the parameter. */
        params[i] = params[i] * scaling_matrix[i];
    }
}

static PyObject *
func(PyObject *self, PyObject *args) {
    /* Target function for calculating and returning the chi-squared value.
     *
     * Firstly the back calculated intensities are generated, then the chi-squared statistic is
     * calculated.
     */

    /* Declarations. */
    PyObject *params_arg;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(params_arg);

    /* Back calculated the peak intensities. */
    exponential(params[index_I0], params[index_R], relax_times, back_calc, num_times);

    /* Calculate and return the chi-squared value. */
    return PyFloat_FromDouble(chi2(values, variance, back_calc, num_times));
}


static PyObject *
dfunc(PyObject *self, PyObject *args) {
    /* Target function for calculating and returning the chi-squared gradient.
     * 
     */

    /* Declarations. */
    PyObject *params_arg;
    PyObject *list;
    int i;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(params_arg);

    /* Back calculated the peak intensities. */
    exponential(params[index_I0], params[index_R], relax_times, back_calc, num_times);

    /* The partial derivates. */
    exponential_dR(params[index_I0], params[index_R], index_R, relax_times, back_calc_grad, num_times);
    exponential_dI0(params[index_I0], params[index_R], index_I0, relax_times, back_calc_grad, num_times);

    /* The chi-squared gradient. */
    dchi2(dchi2_vals, values, back_calc, back_calc_grad, variance, num_times, num_params);

    /* Convert to a Python list, and scale the values. */
    list = PyList_New(0);
    Py_INCREF(list);
    for (i = 0; i < num_params; i++) {
        PyList_Append(list, PyFloat_FromDouble(dchi2_vals[i] * scaling_matrix[i]));
    }

    /* Return the gradient. */
    return list;
}

static PyObject *
d2func(PyObject *self, PyObject *args) {
    /* Target function for calculating and returning the chi-squared Hessian.
     * 
     */

    /* Declarations. */
    PyObject *params_arg;
    PyObject *list, *list2;
    int j, k;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(params_arg);

    /* Back calculated the peak intensities. */
    exponential(params[index_I0], params[index_R], relax_times, back_calc, num_times);

    /* The partial derivatives. */
    exponential_dR(params[index_I0], params[index_R], index_R, relax_times, back_calc_grad, num_times);
    exponential_dI0(params[index_I0], params[index_R], index_I0, relax_times, back_calc_grad, num_times);

    /* The second partial derivatives. */
    exponential_dR2(params[index_I0], params[index_R], index_R, relax_times, back_calc_hess, num_times);
    exponential_dI02(params[index_I0], params[index_R], index_I0, relax_times, back_calc_hess, num_times);
    exponential_dR_dI0(params[index_I0], params[index_R], index_R, index_I0, relax_times, back_calc_hess, num_times);

    /* The chi-squared Hessian. */
    d2chi2(d2chi2_vals, values, back_calc, back_calc_grad, back_calc_hess, variance, num_times, num_params);

    /* Convert to a Python list, and scale the values. */
    list = PyList_New(0);
    Py_INCREF(list);
    for (j = 0; j < num_params; j++) {
        list2 = PyList_New(0);
        Py_INCREF(list2);
        for (k = 0; k < num_params; k++) {
            PyList_Append(list2, PyFloat_FromDouble(d2chi2_vals[j][k] * scaling_matrix[j] * scaling_matrix[k]));
        }
        PyList_Append(list, list2);
    }

    /* Return the Hessian. */
    return list;
}


static PyObject *
back_calc_I(PyObject *self, PyObject *args) {
    /* Return the back calculated peak intensities as a Python list. */

    /* Declarations. */
    PyObject *back_calc_py = PyList_New(num_times);
    int i;

    /* Copy the values out of the C array into the Python array. */
    for (i = 0; i < num_times; i++)
        PyList_SetItem(back_calc_py, i, PyFloat_FromDouble(back_calc[i]));

    /* Return the Python list. */
    return back_calc_py;
}


static PyObject *
jacobian(PyObject *self, PyObject *args) {
    /* Return the Jacobian as a Python list of lists. */

    /* Declarations. */
    PyObject *params_arg;
    PyObject *list, *list2;
    int i, j;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(params_arg);

    /* The partial derivatives. */
    exponential_dR(params[index_I0], params[index_R], index_R, relax_times, back_calc_grad, num_times);
    exponential_dI0(params[index_I0], params[index_R], index_I0, relax_times, back_calc_grad, num_times);

    /* Convert to a Python list of lists. */
    list = PyList_New(0);
    Py_INCREF(list);
    for (i = 0; i < num_params; i++) {
        list2 = PyList_New(0);
        Py_INCREF(list2);
        for (j = 0; j < num_times; j++) {
            PyList_Append(list2, PyFloat_FromDouble(back_calc_grad[i][j]));
        }
        PyList_Append(list, list2);
    }

    /* Return the Jacobian. */
    return list;
}


static PyObject *
jacobian_chi2(PyObject *self, PyObject *args) {
    /* Return the Jacobian as a Python list of lists.

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
    PyObject *params_arg;
    PyObject *list, *list2;
    int i, j;

    /* Parse the function arguments, the only argument should be the parameter array. */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Convert the parameters Python list to a C array. */
    param_to_c(params_arg);

    /* Back calculated the peak intensities. */
    exponential(params[index_I0], params[index_R], relax_times, back_calc, num_times);

    /* The partial derivatives. */
    exponential_dR(params[index_I0], params[index_R], index_R, relax_times, back_calc_grad, num_times);
    exponential_dI0(params[index_I0], params[index_R], index_I0, relax_times, back_calc_grad, num_times);

    /* Assemble the chi-squared Jacobian. */
    for (j = 0; j < num_params; ++j) {
        for (i = 0; i < num_times; ++i) {
            jacobian_matrix[j][i] = -2.0 / variance[i] * (values[i] - back_calc[i]) * back_calc_grad[j][i];
        }
    }

    /* Convert to a Python list of lists. */
    list = PyList_New(0);
    Py_INCREF(list);
    for (i = 0; i < num_params; i++) {
        list2 = PyList_New(0);
        Py_INCREF(list2);
        for (j = 0; j < num_times; j++) {
            PyList_Append(list2, PyFloat_FromDouble(jacobian_matrix[i][j]));
        }
        PyList_Append(list, list2);
    }

    /* Return the Jacobian. */
    return list;
}


/* The method table for the functions called by Python. */
static PyMethodDef relax_fit_methods[] = {
    {
        "setup",
        (PyCFunction)setup,
        METH_VARARGS | METH_KEYWORDS,
        "Set up the module in preparation for calls to the target function."
    }, {
        "func",
        func,
        METH_VARARGS,
        "Target function for calculating and returning the chi-squared value.\n\nFirstly the back calculated intensities are generated, then the chi-squared statistic is calculated."
    }, {
        "dfunc",
        dfunc,
        METH_VARARGS,
        "Target function for calculating and returning the chi-squared gradient."
    }, {
        "d2func",
        d2func,
        METH_VARARGS,
        "Target function for calculating and returning the chi-squared Hessian."
    }, {
        "back_calc_I",
        back_calc_I,
        METH_VARARGS,
        "Return the back calculated peak intensities as a Python list."
    }, {
        "jacobian",
        jacobian,
        METH_VARARGS,
        "Return the Jacobian matrix as a Python list."
    },
        {NULL, NULL, 0, NULL}        /* Sentinel. */
};


/* Define the Python 3 module. */
#if PY_MAJOR_VERSION >= 3
    static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "relax_fit",         /* m_name */
        "Relaxation curve-fitting C module.",  /* m_doc */
        -1,                  /* m_size */
        relax_fit_methods,   /* m_methods */
        NULL,                /* m_reload */
        NULL,                /* m_traverse */
        NULL,                /* m_clear */
        NULL,                /* m_free */
    };
#endif

/* Initialise as a Python module. */
PyMODINIT_FUNC
#if PY_MAJOR_VERSION >= 3
    PyInit_relax_fit(void)
    {
        return PyModule_Create(&moduledef);
    }
#else
    initrelax_fit(void)
    {
        (void) Py_InitModule("relax_fit", relax_fit_methods);
    }
#endif
