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

# Python module imports.
from copy import deepcopy
from math import log

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import same_sequence
from pipes import copy, switch
from relax_errors import RelaxDiffSeqError, RelaxError, RelaxNoPipeError, RelaxNoSequenceError
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

    return chi2 + 2.0*k + 2.0*k*(k + 1.0) / (n - k - 1.0)


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

    # Use all pipes (but the current).
    if pipes == None:
        # Get all data pipe names from the relax data store.
        pipes = ds.keys()

    # Select the model selection technique.
    if method == 'AIC':
        print "AIC model selection."
        formula = aic
    elif method == 'AICc':
        print "AICc model selection."
        formula = aicc
    elif method == 'BIC':
        print "BIC model selection."
        formula = bic
    elif method == 'CV':
        print "CV model selection."
        raise RelaxError, "The model selection technique " + `method` + " is not currently supported."
    else:
        raise RelaxError, "The model selection technique " + `method` + " is not currently supported."

    # No pipes.
    if len(pipes) == 0:
        raise RelaxError, "No data pipes are available for use in model selection."

    # Initialise.
    first_run = None
    function_type = {}
    count_num_instances = {}
    duplicate_data = {}
    model_statistics = {}
    skip_function = {}

    # Cross validation setup.
    if type(pipes[0]) == list:
        # No pipes.
        if len(pipes[0]) == 0:
            raise RelaxError, "No pipes are available for use in model selection in the array " + `pipes[0]` + "."

        # Loop over the data pipes.
        for i in xrange(len(pipes)):
            for j in xrange(len(pipes[i])):
                # Alias the data pipe name.
                pipe = pipes[i][j]

                # Specific duplicate data, number of instances, and model statistics functions.
                count_num_instances[pipe] = get_specific_fn('num_instances', ds[pipe].pipe_type)
                duplicate_data[pipe] = get_specific_fn('duplicate_data', ds[pipe].pipe_type)
                model_statistics[pipe] = get_specific_fn('model_stats', ds[pipe].pipe_type)
                skip_function[pipe] = get_specific_fn('skip_function', ds[pipe].pipe_type)

                # Check that the sequence is the same in all data pipes.
                same_sequence(pipes[0][0], pipe)

    # All other model selection setup.
    else:
        # Loop over the data pipes.
        for i in xrange(len(pipes)):
            # Alias the data pipe name.
            pipe = pipes[i]

            # Specific duplicate data, number of instances, and model statistics functions.
            count_num_instances[pipe] = get_specific_fn('num_instances', ds[pipe].pipe_type)
            duplicate_data[pipe] = get_specific_fn('duplicate_data', ds[pipe].pipe_type)
            model_statistics[pipe] = get_specific_fn('model_stats', ds[pipe].pipe_type)
            skip_function[pipe] = get_specific_fn('skip_function', ds[pipe].pipe_type)

            # Check that the sequence is the same in all data pipes.
            same_sequence(pipes[0], pipe)


    # Number of instances.  If the number is not the same for each data pipe, then the minimum
    # number will give the specific function model_statistics the opportunity to consolidate the
    # instances to the minimum number if possible.
    min_instances = 1e99
    num_instances = []
    for i in xrange(len(pipes)):
        # An array of arrays - for cross validation model selection.
        if type(pipes[i]) == list:
            num_instances.append([])

            # Loop over the nested array.
            for j in xrange(len(pipes[i])):
                # Switch pipes.
                switch(pipes[i][j])

                # Number of instances.
                num = count_num_instances[pipes[i][j]]()
                num_instances[i].append(num)

                # Minimum.
                if num < min_instances:
                    min_instances = num

        # All other model selection techniques.
        else:
            # Switch pipes.
            switch(pipes[i])

            # Number of instances.
            num = count_num_instances[pipes[i]]()
            num_instances.append(num)

            # Minimum.
            if num < min_instances:
                min_instances = num


    # Loop over the number of instances.
    for i in xrange(min_instances):
        # Print out.
        print "\nInstance " + `i` + ".\n"
        print "%-20s %-20s %-20s %-20s %-20s" % ("Run", "Num_params_(k)", "Num_data_sets_(n)", "Chi2", "Criterion")

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
                    if skip_function[pipe](instance=i):
                        continue

                    # Get the model statistics.
                    k, n, chi2 = model_statistics[pipe](instance=i, min_instances=min_instances)

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
                if skip_function[pipe](instance=i, min_instances=min_instances, num_instances=num_instances[j]):
                    continue

                # Global stats.
                if num_instances[j] > min_instances or num_instances[j] == 1:
                    global_stats = 1
                else:
                    global_stats = 0

                # Get the model statistics.
                k, n, chi2 = model_statistics[pipe](instance=i, global_stats=global_stats)

                # Missing data sets.
                if k == None or n == None or chi2 == None:
                    continue

                # Calculate the criterion value.
                crit = formula(chi2, float(k), float(n))

                # Print out.
                print "%-20s %-20i %-20i %-20.5f %-20.5f" % (pipe, k, n, chi2, crit)

            # Select model.
            if crit < best_crit:
                best_model = pipe
                best_crit = crit

        # Print out of selected model.
        print "\nThe model from the run " + `best_model` + " has been selected."

        # Duplicate the data from the 'best_model' to the model selection data pipe.
        if best_model != None:
            duplicate_data[best_model](pipe_from=best_model, pipe_to=modsel_pipe, model_index=i, global_stats=global_stats)
