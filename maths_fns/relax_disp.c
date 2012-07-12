/*
 * Copyright (C) 2006 Edward d'Auvergne
 * Copyright (C) 2009 Sebastien Morin
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

/* This include must come first */
#include <Python.h>

/* The numpy array object header file, must come second */
#include <numpy/arrayobject.h>

/* The header for all functions which will be called */
#include "relax_disp.h"

/* functions for chi2 and dispersion */
#include "c_chi2.h"
#include "dispersion.h"

static PyObject *
setup(PyObject *self, PyObject *args, PyObject *keywords) {
    /* Python declarations */
    PyObject *values_arg, *sd_arg, *cpmg_frqs_arg, *scaling_matrix_arg;
    extern PyArrayObject *numpy_values, *numpy_sd, *numpy_cpmg_frqs, *numpy_scaling_matrix;

    /* Normal declarations */
    extern double *values, *sd, *cpmg_frqs, *scaling_matrix;
    extern double cpmg_frq_array;
    extern int num_params, num_times;

    /* The keyword list */
    static char *keyword_list[] = {"num_params", "num_times", "values", "sd", "cpmg_frqs", "scaling_matrix", NULL};

    /* Parse the function arguments */
    if (!PyArg_ParseTupleAndKeywords(args, keywords, "iiOOOO", keyword_list, &num_params, &num_times, &values_arg, &sd_arg, &cpmg_frqs_arg, &scaling_matrix_arg))
        return NULL;

    Py_XDECREF(numpy_values);
    Py_XDECREF(numpy_sd);
    Py_XDECREF(numpy_cpmg_frqs);
    Py_XDECREF(numpy_scaling_matrix);

    /* Make the numpy arrays contiguous */
    numpy_values = (PyArrayObject *) PyArray_ContiguousFromObject(values_arg, PyArray_DOUBLE, 1, 1);
    numpy_sd = (PyArrayObject *) PyArray_ContiguousFromObject(sd_arg, PyArray_DOUBLE, 1, 1);
    numpy_cpmg_frqs = (PyArrayObject *) PyArray_ContiguousFromObject(cpmg_frqs_arg, PyArray_DOUBLE, 1, 1);
    numpy_scaling_matrix = (PyArrayObject *) PyArray_ContiguousFromObject(scaling_matrix_arg, PyArray_DOUBLE, 2, 2);

    /* Pointers to the numpy arrays */
    values = (double *) numpy_values->data;
    sd = (double *) numpy_sd->data;
    cpmg_frqs = (double *) numpy_cpmg_frqs->data;
    scaling_matrix = (double *) numpy_scaling_matrix->data;

    /* Return nothing */
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject *
func(PyObject *self, PyObject *args) {
    /* Function for calculating and returning the chi-squared value.
     *
     * Firstly the back calculated effective transversal relaxation rates are generated, then the
     * chi-squared statistic is calculated
     */

    /* Declarations */
    PyObject *arg1;
    PyArrayObject *numpy_params;
    double* params;


    /* Parse the function arguments, the only argument should be the parameter array */
    if (!PyArg_ParseTuple(args, "O", &arg1))
        return NULL;

    /* Convert the numpy array to be contiguous */
    numpy_params = (PyArrayObject *) PyArray_ContiguousFromObject(arg1, PyArray_DOUBLE, 1, 1);

    /* Pointers to the numpy arrays */
    params = (double *) numpy_params->data;

    /* Back calculated the effective transversal relaxation rates */
    dispersion(params, cpmg_frqs, back_calc, num_times);

    Py_DECREF(numpy_params);
    /* Calculate and return the chi-squared value */
    return Py_BuildValue("f", chi2(values,sd,back_calc,num_times));
}


static PyObject *
dfunc(PyObject *self, PyObject *args) {
    /* Function for calculating and returning the chi-squared gradient. */

    /* Declarations */
    PyObject *arg1;
    PyArrayObject *numpy_params;

    /* Temp Declarations */
    PyArrayObject *aaa_numpy;
    double aaa[MAXPARAMS] = {1.0, 2.0};
    double *aaa_pointer;
    int i;
    double* params;

    /* Parse the function arguments, the only argument should be the parameter array */
    if (!PyArg_ParseTuple(args, "O", &arg1))
        return NULL;

    /* Convert the numpy array to be contiguous */
    numpy_params = (PyArrayObject *) PyArray_ContiguousFromObject(arg1, PyArray_DOUBLE, 1, 1);

    /* Pointers to the numpy arrays */
    params = (double *) numpy_params->data;

    /* Back calculated the effective transversal relaxation rates */
    dispersion(params, cpmg_frqs, back_calc, num_times);


    /* Test code (convert aaa to a numpy array */
    /* aaa_numpy = (PyArrayObject *) PyArray_FromDimsAndData(1, num_params, PyArray_DOUBLE, aaa_pointer); */
    /*aaa_numpy = (PyArrayObject *) PyArray_FromDims(1, &num_params, PyArray_DOUBLE);
    aaa_pointer = (double *) aaa_numpy->data;*/

    /* Fill the numpy array */
    /*for (i = 0; i < 2; i++)
        aaa_pointer[i] = aaa[i];*/

    Py_DECREF(numpy_params);
    return NULL;
    return PyArray_Return(aaa_numpy);
}

static PyObject *
d2func(PyObject *self, PyObject *args) {
    /* Function for calculating and returning the chi-squared Hessian. */
    return Py_BuildValue("f", 0.0);
}


static PyObject *
back_calc_I(PyObject *self, PyObject *args) {
    /* Function for returning as a numpy array the back calculated effective transversal relaxation
     * rates */

    /* Declarations */
    extern double back_calc[];
    extern int num_times;
    int i;

    PyObject *back_calc_py = PyList_New(num_times);
    assert(PyList_Check(back_calc_py));

    /* Copy the values out of the C array into the Python array */
    for (i = 0; i < num_times; i++)
        PyList_SetItem(back_calc_py, i, Py_BuildValue("f", back_calc[i]));

    /* Return the numpy array */
    return back_calc_py;
}


/* The method table for the functions called by Python */
static PyMethodDef relax_disp_methods[] = {
    {"setup", (PyCFunction)setup, METH_VARARGS | METH_KEYWORDS, "The main relaxation dispersion curve fitting setup function."},
    {"func", func, METH_VARARGS},
    {"dfunc", dfunc, METH_VARARGS},
    {"d2func", d2func, METH_VARARGS},
    {"back_calc_I", back_calc_I, METH_VARARGS},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


/* Initialise as a Python module */
PyMODINIT_FUNC
initrelax_disp(void)
{
    (void) Py_InitModule("relax_disp", relax_disp_methods);

    /* Import the numpy array module.  This is essential. */
    import_array();
}
