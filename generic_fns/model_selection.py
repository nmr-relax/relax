###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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

from copy import deepcopy
from math import log


class Model_selection:
    def __init__(self, relax):
        """Class containing functions specific to model selection."""

        self.relax = relax


    def select(self, method=None, modsel_run=None, runs=None):
        """Model selection function."""

        # The runs argument.
        if runs == None:
            # Use the runs from 'self.relax.data.run_names'.
            self.runs = deepcopy(self.relax.data.run_names)

            # Remove the model selection run name if it is in the list.
            if modsel_run in self.runs:
                self.runs.remove(modsel_run)
        else:
            self.runs = runs

        # Select the model selection technique.
        if method == 'AIC':
            self.formula = self.aic
        elif method == 'AICc':
            self.formula = self.aicc
        elif method == 'BIC':
            self.formula = self.bic
        elif method == 'CV':
            pass
        else:
            raise RelaxError, "The model selection technique " + `method` + " is not currently supported."

        # No runs.
        if len(self.runs) == 0:
            raise RelaxError, "No runs are availible for use in model selection."

        # Store the first run.
        if type(self.runs[0]) == list:
            self.first_run = self.runs[0][0]
        else:
            self.first_run = self.runs[0]

        # Function type.
        self.function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.first_run)]

        # Specific duplicate data, number of instances, and model statistics functions.
        self.duplicate_data = self.relax.specific_setup.setup('duplicate_data', self.function_type)
        self.count_num_instances = self.relax.specific_setup.setup('num_instances', self.function_type)
        self.model_statistics = self.relax.specific_setup.setup('model_stats', self.function_type)
        self.skip_function = self.relax.specific_setup.setup('skip_function', self.function_type)

        # The number of instances.
        self.num_instances = self.count_num_instances(self.first_run)

        # Tests for all runs.
        for run in self.runs:
            # An array of arrays - for cross validation model selection.
            if type(run) == list:
                # No runs.
                if len(run) == 0:
                    raise RelaxError, "No runs are availible for use in model selection in the array " + `run` + "."

                # Loop over the nested array.
                for run2 in run:
                    # Run various tests.
                    self.tests(run2)

            # runs is a normal array.
            else:
                # Run various tests.
                self.tests(run)

        # Loop over the number of instances.
        for i in xrange(self.num_instances):
            # Initial model.
            best_model = None
            best_crit = float('inf')

            # Loop over the runs.
            for j in xrange(len(self.runs)):
                # Single-item-out cross validation.
                if method == 'CV':
                    # Reassign the run.
                    run = self.runs[j][0]

                    # Sum of chi-squared values.
                    sum_crit = 0.0

                    # Loop over the validation samples and sum the chi-squared values.
                    for k in xrange(len(self.runs[j])):
                        # Skip function.
                        if self.skip_function(run=self.runs[j][k], instance=i):
                            continue

                        # Get the model statistics.
                        k, n, chi2 = self.model_statistics(run=self.runs[j][k], instance=i)

                        # Chi2 sum.
                        sum_crit = sum_crit + chi2

                    # Cross-validation criterion (average chi-squared value).
                    crit = sum_crit / float(len(self.runs[j]))

                # Other model selection methods.
                else:
                    # Reassign the run.
                    run = self.runs[j]

                    # Skip function.
                    if self.skip_function(run=run, instance=i):
                        continue

                    # Get the model statistics.
                    k, n, chi2 = self.model_statistics(run=run, instance=i)

                    # Calculate the criterion value.
                    crit = self.formula(chi2, float(k), float(n))

                # Select model.
                if crit < best_crit:
                    best_model = run
                    best_crit = crit

            # Duplicate the data from the 'best_model' to the model selection run 'modsel_run'.
            self.duplicate_data(new_run=modsel_run, old_run=best_model, instance=i)

            # Add the modsel_run to 'self.relax.data.run_names' and 'self.relax.data.run_types'.
            self.relax.data.run_names.append(modsel_run)
            self.relax.data.run_types.append(self.function_type)


    def aic(self, chi2, k, n):
        """Akaike's Information Criteria (AIC).

        The formula is:

            AIC = chi2 + 2k

        where:
            chi2 is the minimised chi-squared value.
            k is the number of parameters in the model.
        """

        return chi2 + 2.0*k


    def aicc(self, chi2, k, n):
        """Small sample size corrected AIC.

        The formula is:

                               2k(k + 1)
            AICc = chi2 + 2k + ---------
                               n - k - 1

        where:
            chi2 is the minimised chi-squared value.
            k is the number of parameters in the model.
            n is the dimension of the relaxation data set.
        """

        return chi2 + 2.0*k + 2.0*k*(k + 1.0) / (n - k - 1.0)


    def bic(self, chi2, k, n):
        """Bayesian or Schwarz Information Criteria.

        The formula is:

            BIC = chi2 + k ln n

        where:
            chi2 - is the minimised chi-squared value.
            k - is the number of parameters in the model.
            n is the dimension of the relaxation data set.
        """

        return chi2 + k * log(n)


    def tests(self, run):
        """Function containing tests the given run."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Find the index of the run.
        index = self.relax.data.run_names.index(run)

        # Test if the function type is the same as 'self.function_type'.
        if self.relax.data.run_types[index] != self.function_type:
            raise RelaxError, "The runs supplied are not all of the same function type."

        # Test if sequence data is loaded.
        if not len(self.relax.data.res[run]):
            raise RelaxSequenceError

        # Sequence lengths.
        if len(self.relax.data.res[self.first_run]) != len(self.relax.data.res[run]):
            raise RelaxDiffSeqError, (self.first_run, run)

        # Loop over the sequence and test that the residue number and residue name are the same.
        for i in xrange(len(self.relax.data.res[self.first_run])):
            # Residue number.
            if self.relax.data.res[self.first_run][i].num != self.relax.data.res[run][i].num:
                raise RelaxDiffSeqError, (self.first_run, run)

            # Residue name.
            if self.relax.data.res[self.first_run][i].name != self.relax.data.res[run][i].name:
                raise RelaxDiffSeqError, (self.first_run, run)

        # Test if the number of instances are all the same.
        local_num_instances = self.count_num_instances(run)
        if self.num_instances != local_num_instances:
            raise RelaxError, "The number of instances are not the same between runs " + `self.first_run` + " and " + `run` + "."
