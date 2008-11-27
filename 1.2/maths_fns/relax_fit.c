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

/* functions for chi2 and exponential */
#include "c_chi2.h"
#include "exponential.h"

static PyObject *
setup(PyObject *self, PyObject *args, PyObject *keywords) {
    /* Python declarations */
    PyObject *values_arg, *sd_arg, *relax_times_arg, *scaling_matrix_arg;
    extern PyArrayObject *numpy_values, *numpy_sd, *numpy_relax_times, *numpy_scaling_matrix;

    /* Normal declarations */
    extern double *values, *sd, *relax_times, *scaling_matrix;
    extern double relax_time_array;
    extern int num_params, num_times;
            
    /* The keyword list */
    static char *keyword_list[] = {"num_params", "num_times", "values", "sd", "relax_times", "scaling_matrix", NULL};

    /* Parse the function arguments */
    if (!PyArg_ParseTupleAndKeywords(args, keywords, "iiOOOO", keyword_list, &num_params, &num_times, &values_arg, &sd_arg, &relax_times_arg, &scaling_matrix_arg))
        return NULL;
    

        
    Py_XDECREF(numpy_values);    
    Py_XDECREF(numpy_sd);
    Py_XDECREF(numpy_relax_times);
    Py_XDECREF(numpy_scaling_matrix);
             
    /* Make the Numeric arrays contiguous */
    numpy_values = (PyArrayObject *) PyArray_ContiguousFromObject(values_arg, PyArray_DOUBLE, 1, 1);
    numpy_sd = (PyArrayObject *) PyArray_ContiguousFromObject(sd_arg, PyArray_DOUBLE, 1, 1);
    numpy_relax_times = (PyArrayObject *) PyArray_ContiguousFromObject(relax_times_arg, PyArray_DOUBLE, 1, 1);
    numpy_scaling_matrix = (PyArrayObject *) PyArray_ContiguousFromObject(scaling_matrix_arg, PyArray_DOUBLE, 2, 2);

    /* Pointers to the Numeric arrays */
    values = (double *) numpy_values->data;
    sd = (double *) numpy_sd->data;
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
    PyArrayObject *numpy_params;
    double* params;


    /* Parse the function arguments, the only argument should be the parameter array */
    if (!PyArg_ParseTuple(args, "O", &arg1))
        return NULL;

    /* Convert the Numeric array to be contiguous */
    numpy_params = (PyArrayObject *) PyArray_ContiguousFromObject(arg1, PyArray_DOUBLE, 1, 1);

    /* Pointers to the Numeric arrays */
    params = (double *) numpy_params->data;

    /* Back calculated the peak intensities */
    exponential(params, relax_times, back_calc, num_times);

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

    /* Convert the Numeric array to be contiguous */
    numpy_params = (PyArrayObject *) PyArray_ContiguousFromObject(arg1, PyArray_DOUBLE, 1, 1);

    /* Pointers to the Numeric arrays */
    params = (double *) numpy_params->data;

    /* Back calculated the peak intensities */
    exponential(params, relax_times, back_calc, num_times);


    /* Test code (convert aaa to a Numeric array */
    /* aaa_numpy = (PyArrayObject *) PyArray_FromDimsAndData(1, num_params, PyArray_DOUBLE, aaa_pointer); */
    /*aaa_numpy = (PyArrayObject *) PyArray_FromDims(1, &num_params, PyArray_DOUBLE);
    aaa_pointer = (double *) aaa_numpy->data;*/

    /* Fill the Numeric array */
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
    /* Function for returning as a Numeric array the back calculated peak intensities */

    /* Declarations */
    extern double back_calc[];
    extern int num_times;
    int i;

    PyObject *back_calc_py = PyList_New(num_times);
    assert(PyList_Check(back_calc_py));

    /* Copy the values out of the C array into the Python array */
    for (i = 0; i < num_times; i++)
        PyList_SetItem(back_calc_py, i, Py_BuildValue("f", back_calc[i]));

    /* Return the Numeric array */
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

    /* Import the Numeric array module.  This is essential. */
    import_array();
}
