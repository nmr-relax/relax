/*
 * Copyright (C) 2006 Edward d'Auvergne
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

/* The Numeric array object header file, must come second */
#include <Numeric/arrayobject.h>

/* The header for all functions which will be called */
#include "relax_fit.h"



static PyObject *
setup(PyObject *self, PyObject *args, PyObject *keywords) {
    /* Python declarations */
    PyObject *intensities_arg, *relax_times_arg, *scaling_matrix_arg;
    extern PyArrayObject *numpy_intensities, *numpy_relax_times, *numpy_scaling_matrix;

    /* Normal declarations */
    extern double *relax_time_array;
    extern int *num_params, *num_times;
    extern double *sd;

    /* The keyword list */
    static char *keyword_list[] = {"num_params", "num_times", "intensities", "sd", "relax_times", "scaling_matrix", NULL};


    /* Parse the function arguments */
    if (!PyArg_ParseTupleAndKeywords(args, keywords, "iiOdOO", keyword_list, &num_params, &num_times, &intensities_arg, &sd, &relax_times_arg, &scaling_matrix_arg))
        return NULL;

    /* Make the Numeric arrays contiguous */
    numpy_intensities = (PyArrayObject *) PyArray_ContiguousFromObject(intensities_arg, PyArray_DOUBLE, 1, 1);
    numpy_relax_times = (PyArrayObject *) PyArray_ContiguousFromObject(relax_times_arg, PyArray_DOUBLE, 1, 1);
    numpy_scaling_matrix = (PyArrayObject *) PyArray_ContiguousFromObject(scaling_matrix_arg, PyArray_DOUBLE, 2, 2);

    /* Pointers to the Numeric arrays */
    intensities = (double *) numpy_intensities->data;
    relax_times = (double *) numpy_relax_times->data;
    scaling_matrix = (double *) numpy_scaling_matrix->data;

    /* Return nothing */
    Py_INCREF(Py_None);
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
    PyObject *arg1;
    extern PyArrayObject *numpy_params;
    void exponential(void);


    /* Parse the function arguments, the only argument should be the parameter array */
    if (!PyArg_ParseTuple(args, "O", &arg1))
        return NULL;

    /* Convert the Numeric array to be contiguous */
    numpy_params = (PyArrayObject *) PyArray_ContiguousFromObject(arg1, PyArray_DOUBLE, 1, 1);

    /* Pointers to the Numeric arrays */
    params = (double *) numpy_params->data;

    /* Back calculated the peak intensities */
    exponential();

    return Py_BuildValue("f", 0.0);
}


static PyObject *
dfunc(PyObject *self, PyObject *args) {
    /* Function for calculating and returning the chi-squared value. */
    return Py_BuildValue("f", 0.0);
}

static PyObject *
d2func(PyObject *self, PyObject *args) {
    /* Function for calculating and returning the chi-squared value. */
    return Py_BuildValue("f", 0.0);
}


/* The method table for the functions called by Python */
static PyMethodDef relax_fit_methods[] = {
    {"setup", (PyCFunction)setup, METH_VARARGS | METH_KEYWORDS, "The main relaxation curve fitting setup function."},
    {"func", func, METH_VARARGS},
    {"dfunc", dfunc, METH_VARARGS},
    {"d2func", d2func, METH_VARARGS},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


/* Initialise as a Python module */
PyMODINIT_FUNC
initrelax_fit(void)
{
    (void) Py_InitModule("relax_fit", relax_fit_methods);

    /* Import the Numeric array module.  This is essential. */
    import_array();
}
