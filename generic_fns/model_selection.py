###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007-2008 Edward d'Auvergne                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for selecting the best model."""

# Python module imports.
from math import log

# relax module imports.
from pipes import get_type, has_pipe, pipe_names, switch
from relax_errors import RelaxError, RelaxPipeError
from specific_fns.setup import get_specific_fn


def aic(chi2, k, n):
    """Akaike's Information Criteria (AIC).

    The formula is::

        AIC = chi2 + 2k


    @param chi2:    The minimised chi-squared value.
    @type chi2:     float
    @param k:       The number of parameters in the model.
    @type k:        int
    @param n:       The dimension of the relaxation data set.
    @type n:        int
    @return:        The AIC value.
    @rtype:         float
    """

    return chi2 + 2.0*k


def aicc(chi2, k, n):
    """Small sample size corrected AIC.

    The formula is::

                           2k(k + 1)
        AICc = chi2 + 2k + ---------
                           n - k - 1


    @param chi2:    The minimised chi-squared value.
    @type chi2:     float
    @param k:       The number of parameters in the model.
    @type k:        int
    @param n:       The dimension of the relaxation data set.
    @type n:        int
    @return:        The AIC value.
    @rtype:         float
    """

    if n > (k+1):
        return chi2 + 2.0*k + 2.0*k*(k + 1.0) / (n - k - 1.0)
    elif n == (k+1):
        raise RelaxError("The size of the dataset, n=%s, is too small for this model of size k=%s.  This situation causes a fatal division by zero as:\n    AICc = chi2 + 2k + 2k*(k + 1) / (n - k - 1).\n\nPlease use AIC model selection instead." % (n, k))
    elif n < (k+1):
        raise RelaxError("The size of the dataset, n=%s, is too small for this model of size k=%s.  This situation produces a negative, and hence nonsense, AICc score as:\n    AICc = chi2 + 2k + 2k*(k + 1) / (n - k - 1).\n\nPlease use AIC model selection instead." % (n, k))


def bic(chi2, k, n):
    """Bayesian or Schwarz Information Criteria.

    The formula is::

        BIC = chi2 + k ln n


    @param chi2:    The minimised chi-squared value.
    @type chi2:     float
    @param k:       The number of parameters in the model.
    @type k:        int
    @param n:       The dimension of the relaxation data set.
    @type n:        int
    @return:        The AIC value.
    @rtype:         float
    """

    return chi2 + k * log(n)


def select(method=None, modsel_pipe=None, pipes=None):
    """Model selection function.

    @keyword method:        The model selection method.  This can currently be one of:
                                - 'AIC', Akaike's Information Criteria.
                                - 'AICc', Small sample size corrected AIC.
                                - 'BIC', Bayesian or Schwarz Information Criteria.
                                - 'CV', Single-item-out cross-validation.
                            None of the other model selection techniques are currently supported.
    @type method:           str
    @keyword modsel_pipe:   The name of the new data pipe to be created by copying of the selected
                            data pipe.
    @type modsel_pipe:      str
    @keyword pipes:         A list of the data pipes to use in the model selection.
    @type pipes:            list of str
    """

    # Test if the pipe already exists.
    if has_pipe(modsel_pipe):
        raise RelaxPipeError(modsel_pipe)

    # Use all pipes.
    if pipes == None:
        # Get all data pipe names from the relax data store.
        pipes = pipe_names()

    # Select the model selection technique.
    if method == 'AIC':
        print("AIC model selection.")
        formula = aic
    elif method == 'AICc':
        print("AICc model selection.")
        formula = aicc
    elif method == 'BIC':
        print("BIC model selection.")
        formula = bic
    elif method == 'CV':
        print("CV model selection.")
        raise RelaxError("The model selection technique " + repr(method) + " is not currently supported.")
    else:
        raise RelaxError("The model selection technique " + repr(method) + " is not currently supported.")

    # No pipes.
    if len(pipes) == 0:
        raise RelaxError("No data pipes are available for use in model selection.")

    # Initialise.
    function_type = {}
    model_loop = {}
    model_type = {}
    duplicate_data = {}
    model_statistics = {}
    skip_function = {}
    modsel_pipe_exists = False

    # Cross validation setup.
    if isinstance(pipes[0], list):
        # No pipes.
        if len(pipes[0]) == 0:
            raise RelaxError("No pipes are available for use in model selection in the array " + repr(pipes[0]) + ".")

        # Loop over the data pipes.
        for i in xrange(len(pipes)):
            for j in xrange(len(pipes[i])):
                # Specific functions.
                model_loop[pipes[i][j]] = get_specific_fn('model_loop', get_type(pipes[i][j]))
                model_type[pipes[i][j]] = get_specific_fn('model_type', get_type(pipes[i][j]))
                duplicate_data[pipes[i][j]] = get_specific_fn('duplicate_data', get_type(pipes[i][j]))
                model_statistics[pipes[i][j]] = get_specific_fn('model_stats', get_type(pipes[i][j]))
                skip_function[pipes[i][j]] = get_specific_fn('skip_function', get_type(pipes[i][j]))

        # The model loop should be the same for all data pipes!
        for i in xrange(len(pipes)):
            for j in xrange(len(pipes[i])):
                if model_loop[pipes[0][j]] != model_loop[pipes[i][j]]:
                    raise RelaxError("The models for each data pipes should be the same.")
        model_loop = model_loop[pipes[0][0]]

        # The model description.
        model_desc = get_specific_fn('model_desc', get_type(pipes[0]))

        # Global vs. local models.
        global_flag = False
        for i in xrange(len(pipes)):
            for j in xrange(len(pipes[i])):
                if model_type[pipes[i][j]]() == 'global':
                    global_flag = True

    # All other model selection setup.
    else:
        # Loop over the data pipes.
        for i in xrange(len(pipes)):
            # Specific functions.
            model_loop[pipes[i]] = get_specific_fn('model_loop', get_type(pipes[i]))
            model_type[pipes[i]] = get_specific_fn('model_type', get_type(pipes[i]))
            duplicate_data[pipes[i]] = get_specific_fn('duplicate_data', get_type(pipes[i]))
            model_statistics[pipes[i]] = get_specific_fn('model_stats', get_type(pipes[i]))
            skip_function[pipes[i]] = get_specific_fn('skip_function', get_type(pipes[i]))

        model_loop = model_loop[pipes[0]]

        # The model description.
        model_desc = get_specific_fn('model_desc', get_type(pipes[0]))

        # Global vs. local models.
        global_flag = False
        for j in xrange(len(pipes)):
            if model_type[pipes[j]]() == 'global':
                global_flag = True


    # Loop over the base models.
    for model_info in model_loop():
        # Print out.
        print(("\n" + model_desc(model_info)))
        print(("%-20s %-20s %-20s %-20s %-20s" % ("Data pipe", "Num_params_(k)", "Num_data_sets_(n)", "Chi2", "Criterion")))

        # Initial model.
        best_model = None
        best_crit = 1e300

        # Loop over the pipes.
        for j in xrange(len(pipes)):
            # Single-item-out cross validation.
            if method == 'CV':
                # Sum of chi-squared values.
                sum_crit = 0.0

                # Loop over the validation samples and sum the chi-squared values.
                for k in xrange(len(pipes[j])):
                    # Alias the data pipe name.
                    pipe = pipes[j][k]

                    # Switch to this pipe.
                    switch(pipe)

                    # Skip function.
                    if skip_function[pipe](model_info):
                        continue

                    # Get the model statistics.
                    k, n, chi2 = model_statistics[pipe](model_info)

                    # Missing data sets.
                    if k == None or n == None or chi2 == None:
                        continue

                    # Chi2 sum.
                    sum_crit = sum_crit + chi2

                # Cross-validation criterion (average chi-squared value).
                crit = sum_crit / float(len(pipes[j]))

            # Other model selection methods.
            else:
                # Reassign the pipe.
                pipe = pipes[j]

                # Switch to this pipe.
                switch(pipe)

                # Skip function.
                if skip_function[pipe](model_info):
                    continue

                # Get the model statistics.
                k, n, chi2 = model_statistics[pipe](model_info, global_stats=global_flag)

                # Missing data sets.
                if k == None or n == None or chi2 == None:
                    continue

                # Calculate the criterion value.
                crit = formula(chi2, float(k), float(n))

                # Print out.
                print(("%-20s %-20i %-20i %-20.5f %-20.5f" % (pipe, k, n, chi2, crit)))

            # Select model.
            if crit < best_crit:
                best_model = pipe
                best_crit = crit

        # Duplicate the data from the 'best_model' to the model selection data pipe.
        if best_model != None:
            # Print out of selected model.
            print(("The model from the data pipe " + repr(best_model) + " has been selected."))

            # Switch to the selected data pipe.
            switch(best_model)

            # Duplicate.
            duplicate_data[best_model](best_model, modsel_pipe, model_info, global_stats=global_flag, verbose=False)

            # Model selection pipe now exists.
            modsel_pipe_exists = True

        # No model selected.
        else:
            # Print out of selected model.
            print("No model has been selected.")

    # Switch to the model selection pipe.
    if modsel_pipe_exists:
        switch(modsel_pipe)
