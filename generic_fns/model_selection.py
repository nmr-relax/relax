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

        # Test if the model selection run exists.
        if not modsel_run in self.relax.data.run_names:
            raise RelaxNoRunError, modsel_run

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
            print "AIC model selection."
            self.formula = self.aic
        elif method == 'AICc':
            print "AICc model selection."
            self.formula = self.aicc
        elif method == 'BIC':
            print "BIC model selection."
            self.formula = self.bic
        elif method == 'CV':
            print "CV model selection."
            raise RelaxError, "The model selection technique " + `method` + " is not currently supported."
        else:
            raise RelaxError, "The model selection technique " + `method` + " is not currently supported."

        # No runs.
        if len(self.runs) == 0:
            raise RelaxError, "No runs are availible for use in model selection."

        # Initialise.
        self.first_run = None
        self.function_type = {}
        self.duplicate_data = {}
        self.count_num_instances = {}
        self.model_statistics = {}
        self.skip_function = {}

        # Cross validation setup.
        if type(self.runs[0]) == list:
            # No runs.
            if len(run) == 0:
                raise RelaxError, "No runs are availible for use in model selection in the array " + `run` + "."

            # Loop over the runs.
            for i in xrange(len(self.runs)):
                for j in xrange(len(self.runs[i])):
                    # The run name.
                    run = self.runs[i][j]

                    # Function type.
                    self.function_type[run] = self.relax.data.run_types[self.relax.data.run_names.index(run)]

                    # Store the first non-hybrid run.
                    if not self.first_run and self.function_type[run] != 'hybrid':
                        self.first_run = run

                    # Specific duplicate data, number of instances, and model statistics functions.
                    self.duplicate_data[run] = self.relax.specific_setup.setup('duplicate_data', self.function_type[run])
                    self.count_num_instances[run] = self.relax.specific_setup.setup('num_instances', self.function_type[run])
                    self.model_statistics[run] = self.relax.specific_setup.setup('model_stats', self.function_type[run])
                    self.skip_function[run] = self.relax.specific_setup.setup('skip_function', self.function_type[run])

                    # Run various tests.
                    self.tests(run)

        # All other model selection setup.
        else:
            # Loop over the runs.
            for i in xrange(len(self.runs)):
                # The run name.
                run = self.runs[i]

                # Function type.
                self.function_type[run] = self.relax.data.run_types[self.relax.data.run_names.index(run)]

                # Store the first non-hybrid run.
                if not self.first_run and self.function_type[run] != 'hybrid':
                    self.first_run = run

                # Specific duplicate data, number of instances, and model statistics functions.
                self.duplicate_data[run] = self.relax.specific_setup.setup('duplicate_data', self.function_type[run])
                self.count_num_instances[run] = self.relax.specific_setup.setup('num_instances', self.function_type[run])
                self.model_statistics[run] = self.relax.specific_setup.setup('model_stats', self.function_type[run])
                self.skip_function[run] = self.relax.specific_setup.setup('skip_function', self.function_type[run])

                # Run various tests.
                self.tests(run)


        # Number of instances.  If the number is not the same for each run, then the minimum number will give the specific function self.model_statistics the
        # opportunity to consolidate the instances to the minimum number if possible.
        self.min_instances = 1e99
        self.num_instances = []
        for i in xrange(len(self.runs)):
            # An array of arrays - for cross validation model selection.
            if type(self.runs[i]) == list:
                self.num_instances.append([])

                # Loop over the nested array.
                for j in xrange(len(self.runs[i])):
                    # Number of instances.
                    num = self.count_num_instances[self.runs[i][j]](self.runs[i][j])
                    self.num_instances[i].append(num)

                    # Minimum.
                    if num < self.min_instances:
                        self.min_instances = num

            # All other model selection techniques.
            else:
                # Number of instances.
                num = self.count_num_instances[self.runs[i]](self.runs[i])
                self.num_instances.append(num)

                # Minimum.
                if num < self.min_instances:
                    self.min_instances = num


        # Loop over the number of instances.
        for i in xrange(self.min_instances):
            # Print out.
            print "\nInstance " + `i` + ".\n"
            print "%-20s %-20s %-20s %-20s %-20s" % ("Run", "Num_params_(k)", "Num_data_sets_(n)", "Chi2", "Criterion")

            # Initial model.
            best_model = None
            best_crit = 1e300

            # Loop over the runs.
            for j in xrange(len(self.runs)):
                # Single-item-out cross validation.
                if method == 'CV':
                    # Sum of chi-squared values.
                    sum_crit = 0.0

                    # Loop over the validation samples and sum the chi-squared values.
                    for k in xrange(len(self.runs[j])):
                        # Reassign the run.
                        run = self.runs[j][k]

                        # Skip function.
                        if self.skip_function[run](run=run, instance=i):
                            continue

                        # Get the model statistics.
                        k, n, chi2 = self.model_statistics[run](run=run, instance=i, min_instances=self.min_instances)

                        # Missing data sets.
                        if k == None or n == None or chi2 == None:
                            continue

                        # Chi2 sum.
                        sum_crit = sum_crit + chi2

                    # Cross-validation criterion (average chi-squared value).
                    crit = sum_crit / float(len(self.runs[j]))

                # Other model selection methods.
                else:
                    # Reassign the run.
                    run = self.runs[j]

                    # Skip function.
                    if self.skip_function[run](run=run, instance=i, min_instances=self.min_instances, num_instances=self.num_instances[j]):
                        continue

                    # Global stats.
                    if self.num_instances[j] > self.min_instances or self.num_instances[j] == 1:
                        global_stats = 1
                    else:
                        global_stats = 0

                    # Get the model statistics.
                    k, n, chi2 = self.model_statistics[run](run=run, instance=i, global_stats=global_stats)

                    # Missing data sets.
                    if k == None or n == None or chi2 == None:
                        continue

                    # Calculate the criterion value.
                    crit = self.formula(chi2, float(k), float(n))

                    # Print out.
                    print "%-20s %-20i %-20i %-20.5f %-20.5f" % (run, k, n, chi2, crit)

                # Select model.
                if crit < best_crit:
                    best_model = run
                    best_crit = crit

            # Print out of selected model.
            print "\nThe model from the run " + `best_model` + " has been selected."

            # Duplicate the data from the 'best_model' to the model selection run 'modsel_run'.
            if best_model != None:
                self.duplicate_data[best_model](new_run=modsel_run, old_run=best_model, instance=i, global_stats=global_stats)


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

        # Test if the function type is the same as 'self.function_type' (skip the test if self.function_type is a hybrid).
        #if self.function_type != 'hybrid' and self.relax.data.run_types[index] != self.function_type:
        if self.relax.data.run_types[index] != self.function_type[run]:
            raise RelaxError, "The runs supplied are not all of the same function type."

        # Skip all tests if the model is a hybrid.
        if self.relax.data.run_types[index] == 'hybrid':
            return

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

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
