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

/* The header for all functions which will be called */
#include "exp_fn.h"

/* The Numeric array object header file */
#include <Numeric/arrayobject.h>



static PyObject *
exponential_fn(PyObject *self, PyObject *args, PyObject *keywords) {
    /* Declarations */
    PyObject *init_params;
    PyArrayObject *params, *scaling_matrix;
    char *name;
    double *test;

    static char *keyword_list[] = {"init_params", "scaling_matrix", "name", NULL};


    /* Parse the function arguments */
    if (!PyArg_ParseTupleAndKeywords(args, keywords, "OOs", keyword_list, &init_params, &scaling_matrix, &name))
        return NULL;

    /* Convert the Numeric array to be contiguous */
    params = (PyArrayObject *) PyArray_ContiguousFromObject(init_params, PyArray_DOUBLE, 1, 1);

    /* Testing */
    printf(name);
    printf("\n");
    printf("%-20f\n", *(double *)(params->data));
    printf("%-20f\n", *(double *)(params->data + params->strides[0]));
    test = (double *)params->data;
    printf("%-20f\n", test[0]);
    printf("%-20f\n", test[1]);

    /* Destroy the necessary references */
    Py_DECREF(params);

    /* Return nothing */
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject *
exponential_test_fn(PyObject *self, PyObject *args) {
    /* Declarations */
    PyArrayObject *init_params;

    /* Parse the function arguments */
    if (!PyArg_ParseTuple(args, "O", &init_params))
        return NULL;

    printf("%-20g\n", *(double *)(init_params->data + 0*init_params->strides[0]));
    printf("%-20g\n", *(double *)(init_params->data + 1*init_params->strides[0]));

    /* Return nothing */
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject *
func(PyObject *self, PyObject *args) {
    /* Function for calculating and returning the chi-squared value. */

    PyArrayObject *params;

    /* Parse the function arguments */
    if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &params))
        return NULL;

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
static PyMethodDef exp_fn_methods[] = {
    {"exponential_fn", (PyCFunction)exponential_fn, METH_VARARGS | METH_KEYWORDS, "The main exponential function."},
    {"exponential_test_fn", exponential_test_fn, METH_VARARGS, "The main exponential function."},
    {"func", func, METH_VARARGS},
    {"dfunc", dfunc, METH_VARARGS},
    {"d2func", d2func, METH_VARARGS},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


/* Initialise as a Python module */
PyMODINIT_FUNC
initexp_fn(void)
{
    (void) Py_InitModule("exp_fn", exp_fn_methods);

    /* Import the Numeric array module.  This is essential. */
    import_array();
}
