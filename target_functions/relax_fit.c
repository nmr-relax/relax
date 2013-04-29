/*
 * Copyright (C) 2006-2013 Edward d'Auvergne
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

/* The header for all functions which will be called */
#include "relax_fit.h"

/* functions for chi2 and exponential */
#include "c_chi2.h"
#include "exponential.h"

static PyObject *
setup(PyObject *self, PyObject *args, PyObject *keywords) {
    /* Set up the module in preparation for calls to the target function. */

    /* Python object declarations */
    PyObject *values_arg, *sd_arg, *relax_times_arg, *scaling_matrix_arg;
    PyObject *element;

    /* Normal declarations */
    int i;

    /* The keyword list */
    static char *keyword_list[] = {"num_params", "num_times", "values", "sd", "relax_times", "scaling_matrix", NULL};

    /* Parse the function arguments */
    if (!PyArg_ParseTupleAndKeywords(args, keywords, "iiOOOO", keyword_list, &num_params, &num_times, &values_arg, &sd_arg, &relax_times_arg, &scaling_matrix_arg))
        return NULL;

    /* Place the parameter related arguments into C arrays */
    for (i = 0; i < num_params; i++) {
        /* The diagonalised scaling matrix list argument element */
        element = PySequence_GetItem(scaling_matrix_arg, i);
        scaling_matrix[i] = PyFloat_AsDouble(element);
    }

    /* Place the time related arguments into C arrays */
    for (i = 0; i < num_times; i++) {
        /* The value argument element */
        element = PySequence_GetItem(values_arg, i);
        values[i] = PyFloat_AsDouble(element);

        /* The sd argument element */
        element = PySequence_GetItem(sd_arg, i);
        sd[i] = PyFloat_AsDouble(element);

        /* The relax_times argument element */
        element = PySequence_GetItem(relax_times_arg, i);
        relax_times[i] = PyFloat_AsDouble(element);
    }

    /* The macro for returning the Python None object */
    Py_RETURN_NONE;
}


static PyObject *
func(PyObject *self, PyObject *args) {
    /* Target function for calculating and returning the chi-squared value.
     *
     * Firstly the back calculated intensities are generated, then the chi-squared statistic is
     * calculated.
     */

    /* Declarations */
    PyObject *params_arg;
    PyObject *element;
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

        /* Scale the parameter */
        params[i] = params[i] * scaling_matrix[i];
    }

    /* Back calculated the peak intensities */
    exponential(params, relax_times, back_calc, num_times);

    /* Calculate and return the chi-squared value */
    return PyFloat_FromDouble(chi2(values, sd, back_calc, num_times));
}


static PyObject *
dfunc(PyObject *self, PyObject *args) {
    /* Target function for calculating and returning the chi-squared gradient.
     * 
     * This is currently unimplemented.
     */

    /* Declarations */
    PyObject *params_arg;

    /* Temp Declarations */
    double aaa[MAXPARAMS] = {1.0, 2.0};
    int i;
    double *params;

    /* Parse the function arguments, the only argument should be the parameter array */
    if (!PyArg_ParseTuple(args, "O", &params_arg))
        return NULL;

    /* Back calculated the peak intensities */
    exponential(params, relax_times, back_calc, num_times);

    return NULL;
}

static PyObject *
d2func(PyObject *self, PyObject *args) {
    /* Target function for calculating and returning the chi-squared Hessian.
     * 
     * This is currently unimplemented.
     */

    return PyFloat_FromDouble(0.0);
}


static PyObject *
back_calc_I(PyObject *self, PyObject *args) {
    /* Return the back calculated peak intensities as a Python list. */

    /* Declarations */
    PyObject *back_calc_py = PyList_New(num_times);
    int i;

    /* Copy the values out of the C array into the Python array */
    for (i = 0; i < num_times; i++)
        PyList_SetItem(back_calc_py, i, PyFloat_FromDouble(back_calc[i]));

    /* Return the numpy array */
    return back_calc_py;
}


/* The method table for the functions called by Python */
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
        "Target function for calculating and returning the chi-squared gradient.\n\nThis is currently unimplemented."
    }, {
        "d2func",
        d2func,
        METH_VARARGS,
        "Target function for calculating and returning the chi-squared Hessian.\n\nThis is currently unimplemented."
    }, {
        "back_calc_I",
        back_calc_I,
        METH_VARARGS,
        "Return the back calculated peak intensities as a Python list."
    },
        {NULL, NULL, 0, NULL}        /* Sentinel */
};


/* Define the Python 3 module */
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

/* Initialise as a Python module */
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
