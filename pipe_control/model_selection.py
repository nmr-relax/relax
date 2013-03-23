###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for selecting the best model."""

# Python module imports.
import sys

# relax module imports.
import pipe_control.pipes
from pipe_control.pipes import get_type, has_pipe, pipe_names, switch
from lib.errors import RelaxError, RelaxPipeError
from lib.io import write_data
from lib.model_selection import aic, aicc, bic
from specific_analyses.setup import get_specific_fn


def select(method=None, modsel_pipe=None, bundle=None, pipes=None):
    """Model selection function.

    @keyword method:        The model selection method.  This can currently be one of:
                                - 'AIC', Akaike's Information Criteria.
                                - 'AICc', Small sample size corrected AIC.
                                - 'BIC', Bayesian or Schwarz Information Criteria.
                                - 'CV', Single-item-out cross-validation.
                            None of the other model selection techniques are currently supported.
    @type method:           str
    @keyword modsel_pipe:   The name of the new data pipe to be created by copying of the selected data pipe.
    @type modsel_pipe:      str
    @keyword bundle:        The optional data pipe bundle to associate the newly created pipe with.
    @type bundle:           str or None
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
        for i in range(len(pipes)):
            for j in range(len(pipes[i])):
                # Specific functions.
                model_loop[pipes[i][j]] = get_specific_fn('model_loop', get_type(pipes[i][j]))
                model_type[pipes[i][j]] = get_specific_fn('model_type', get_type(pipes[i][j]))
                duplicate_data[pipes[i][j]] = get_specific_fn('duplicate_data', get_type(pipes[i][j]))
                model_statistics[pipes[i][j]] = get_specific_fn('model_stats', get_type(pipes[i][j]))
                skip_function[pipes[i][j]] = get_specific_fn('skip_function', get_type(pipes[i][j]))

        # The model loop should be the same for all data pipes!
        for i in range(len(pipes)):
            for j in range(len(pipes[i])):
                if model_loop[pipes[0][j]] != model_loop[pipes[i][j]]:
                    raise RelaxError("The models for each data pipes should be the same.")
        model_loop = model_loop[pipes[0][0]]

        # The model description.
        model_desc = get_specific_fn('model_desc', get_type(pipes[0]))

        # Global vs. local models.
        global_flag = False
        for i in range(len(pipes)):
            for j in range(len(pipes[i])):
                if model_type[pipes[i][j]]() == 'global':
                    global_flag = True

    # All other model selection setup.
    else:
        # Loop over the data pipes.
        for i in range(len(pipes)):
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
        for j in range(len(pipes)):
            if model_type[pipes[j]]() == 'global':
                global_flag = True


    # Loop over the base models.
    for model_info in model_loop():
        # Print out.
        print("\n")
        desc = model_desc(model_info)
        if desc:
            print(desc)

        # Initial model.
        best_model = None
        best_crit = 1e300
        data = []

        # Loop over the pipes.
        for j in range(len(pipes)):
            # Single-item-out cross validation.
            if method == 'CV':
                # Sum of chi-squared values.
                sum_crit = 0.0

                # Loop over the validation samples and sum the chi-squared values.
                for k in range(len(pipes[j])):
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

                # Store the values for a later printout.
                data.append([pipe, repr(k), repr(n), "%.5f" % chi2, "%.5f" % crit])

            # Select model.
            if crit < best_crit:
                best_model = pipe
                best_crit = crit

        # Write out the table.
        write_data(out=sys.stdout, headings=["Data pipe", "Num_params_(k)", "Num_data_sets_(n)", "Chi2", "Criterion"], data=data)

        # Duplicate the data from the 'best_model' to the model selection data pipe.
        if best_model != None:
            # Print out of selected model.
            print("The model from the data pipe " + repr(best_model) + " has been selected.")

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

    # Bundle the data pipe.
    if bundle:
        pipe_control.pipes.bundle(bundle=bundle, pipe=modsel_pipe)
