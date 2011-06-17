/*
 * Copyright (C) 2006 Edward d'Auvergne
 * Copyright (C) 2011 Sebastien Morin
 *
 * This file is part of the program relax.
 *
 * relax is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * relax is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with relax; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

/* This include must come first */
#include <Python.h>

/* The header for all functions which will be called */
#include "relax_fit.h"

/* functions for chi2 and exponential */
#include "c_chi2.h"
#include "exponential.h"

static PyObject *
setup(PyObject *self, PyObject *args, PyObject *keywords) {
    /* Python object declarations */
    PyObject *values_arg, *sd_arg, *relax_times_arg, *scaling_matrix_arg;
    PyObject *element;

    /* Normal declarations */
    extern double *params, *values, *sd, *relax_times, *scaling_matrix;
    extern double relax_time_array;
    extern int num_params, num_times;
    int i;

    /* The keyword list */
    static char *keyword_list[] = {"num_params", "num_times", "values", "sd", "relax_times", "scaling_matrix", NULL};

    /* Parse the function arguments */
    if (!PyArg_ParseTupleAndKeywords(args, keywords, "iiOOOO", keyword_list, &num_params, &num_times, &values_arg, &sd_arg, &relax_times_arg, &scaling_matrix_arg))
        return NULL;

    /* Dynamic C arrays */
    params = (double *) malloc(sizeof(double)*num_params);
    values = (double *) malloc(sizeof(double)*num_times);
    sd = (double *) malloc(sizeof(double)*num_times);
    relax_times = (double *) malloc(sizeof(double)*num_times);
    scaling_matrix = (double *) malloc(sizeof(double)*num_params);

    /* Place the value elements into the C array */
    for (i = 0; i < num_times; i++) {
        /* Get the element */
        element = PySequence_GetItem(values_arg, i);

        /* Convert to a C double */
        values[i] = PyFloat_AsDouble(element);
    }

    /* Place the sd elements into the C array */
    for (i = 0; i < num_times; i++) {
        /* Get the element */
        element = PySequence_GetItem(sd_arg, i);

        /* Convert to a C double */
        sd[i] = PyFloat_AsDouble(element);
    }

    /* Place the relax_times elements into the C array */
    for (i = 0; i < num_times; i++) {
        /* Get the element */
        element = PySequence_GetItem(relax_times_arg, i);

        /* Convert to a C double */
        relax_times[i] = PyFloat_AsDouble(element);
    }

    /* Place the scaling matrix elements into the C array */
    for (i = 0; i < num_params; i++) {
        /* Get the element */
        element = PySequence_GetItem(values_arg, i);

        /* Convert to a C double */
        scaling_matrix[i] = PyFloat_AsDouble(element);
    }

    /* Return nothing */
    return Py_None;
}


static PyObject *
func(PyObject *self, PyObject *args) {
    /* Function for calculating and returning the chi-squared value.
     *
     * Firstly the back calculated intensities are generated, then the chi-squared statistic is
     * calculated
     */

    /* Declarations */
    PyObject *params_arg;
    PyObject *element;
    extern double *params;
    int i;

    /* Parse the function arguments, the only argument should be the parameter array */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Place the parameter array elements into the C array */
    for (i = 0; i < num_params; i++) {
        /* Get the element */
        element = PySequence_GetItem(params_arg, i);

        /* Convert to a C double */
        params[i] = PyFloat_AsDouble(element);
    }

    /* Back calculated the peak intensities */
    exp_2param_neg(params, relax_times, back_calc, num_times);

    /* Calculate and return the chi-squared value */
    return Py_BuildValue("f", chi2(values,sd,back_calc,num_times));
}


static PyObject *
dfunc(PyObject *self, PyObject *args) {
    /* Function for calculating and returning the chi-squared gradient. */

    /* Declarations */
    PyObject *params_arg;

    /* Temp Declarations */
    double aaa[MAXPARAMS] = {1.0, 2.0};
    int i;
    double* params;

    /* Parse the function arguments, the only argument should be the parameter array */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Back calculated the peak intensities */
    exp_2param_neg(params, relax_times, back_calc, num_times);

    return NULL;
}

static PyObject *
d2func(PyObject *self, PyObject *args) {
    /* Function for calculating and returning the chi-squared Hessian. */
    return Py_BuildValue("f", 0.0);
}


static PyObject *
back_calc_I(PyObject *self, PyObject *args) {
    /* Function for returning as a numpy array the back calculated peak intensities */

    /* Declarations */
    PyObject *back_calc_py = PyList_New(num_times);
    extern double back_calc[];
    extern int num_times;
    int i;

    /* Copy the values out of the C array into the Python array */
    for (i = 0; i < num_times; i++)
        PyList_SetItem(back_calc_py, i, Py_BuildValue("f", back_calc[i]));

    /* Return the numpy array */
    return back_calc_py;
}


/* The method table for the functions called by Python */
static PyMethodDef relax_fit_methods[] = {
    {"setup", (PyCFunction)setup, METH_VARARGS | METH_KEYWORDS, "The main relaxation curve fitting setup function."},
    {"func", func, METH_VARARGS},
    {"dfunc", dfunc, METH_VARARGS},
    {"d2func", d2func, METH_VARARGS},
    {"back_calc_I", back_calc_I, METH_VARARGS},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


/* Initialise as a Python module */
PyMODINIT_FUNC
initrelax_fit(void)
{
    (void) Py_InitModule("relax_fit", relax_fit_methods);
}
