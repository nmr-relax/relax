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

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # The runs argument.
        if runs == None:
            runs = self.relax.data.run_names
        else:
            if len(runs) == 0:
                raise RelaxError, "The runs argument " + `runs` + " must be an array of length greater than zero."
            for run in runs:
                if type(run) == list:
                    if len(run) == 0:
                        raise RelaxError, "The runs argument element " + `run` + " must be an array of length greater than zero."
                    for run2 in run:
                        if not run2 in self.relax.data.run_names:
                            raise RelaxNoRunError, run2
                elif not run in self.relax.data.run_names:
                    raise RelaxNoRunError, run

        # Test if the run 'modsel_run' does not already exist.
        if modsel_run in self.relax.data.run_names:
            raise RelaxRunError, modsel_run

        # Test that all the runs are of the same type.
        run_type = 'None'
        for run in runs:
            if type(run) == list:
                for run2 in run:
                    # Find the index of run2.
                    index = self.relax.data.run_names.index(run2)

                    # Initialise the type.
                    if run_type == 'None':
                        run_type = self.relax.data.run_types[index]

                    # Test if the run type is the same as 'run_type'.
                    if self.relax.data.run_types[index] != run_type:
                        raise RelaxError, "The run supplied are not all of the same type."
            else:
                # Find the index of run2.
                index = self.relax.data.run_names.index(run)

                # Initialise the type.
                if run_type == 'None':
                    run_type = self.relax.data.run_types[index]

                # Test if the run type is the same as 'run_type'.
                if self.relax.data.run_types[index] != run_type:
                    raise RelaxError, "The run supplied are not all of the same type."

        # Test if each run has a valid parameter and chi-squared data structure.
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Loop over the runs.
            for run in runs:
                if type(run) == list:
                    for run2 in run:
                        if not hasattr(self.relax.data.res[i], 'params'):
                            raise RelaxError, "The run " + `run2` + " does not have a valid parameter data structure."
                        elif not self.relax.data.res[i].params.has_key(run2):
                            raise RelaxError, "The run " + `run2` + " does not have a valid parameter data structure."
                        elif not hasattr(self.relax.data.res[i], 'chi2'):
                            raise RelaxError, "The run " + `run2` + " does not have a valid chi-squared data structure."
                        elif not self.relax.data.res[i].chi2.has_key(run2):
                            raise RelaxError, "The run " + `run2` + " does not have a valid chi-squared data structure."
                else:
                    if not hasattr(self.relax.data.res[i], 'params'):
                        raise RelaxError, "The run " + `run` + " does not have a valid parameter data structure."
                    elif not self.relax.data.res[i].params.has_key(run):
                        raise RelaxError, "The run " + `run` + " does not have a valid parameter data structure."
                    elif not hasattr(self.relax.data.res[i], 'chi2'):
                        raise RelaxError, "The run " + `run` + " does not have a valid chi-squared data structure."
                    elif not self.relax.data.res[i].chi2.has_key(run):
                        raise RelaxError, "The run " + `run` + " does not have a valid chi-squared data structure."

        # Initialise.
        self.runs = deepcopy(runs)

        # Select the model selection technique.
        if method == 'AIC':
            self.modsel = self.criteria_modsel
            self.formula = self.aic
        elif method == 'AICc':
            self.modsel = self.criteria_modsel
            self.formula = self.aicc
        elif method == 'BIC':
            self.modsel = self.criteria_modsel
            self.formula = self.bic
        elif method == 'CV':
            self.modsel = self.cv
        else:
            raise RelaxError, "The model selection technique " + `method` + " is not currently supported."

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Test if data exists for this residue.
            flag = 0
            for run in runs:
                # Cross-validation.
                if type(run) == list:
                    for run2 in run:
                        if not hasattr(self.relax.data.res[i], 'params'):
                            flag = 1
                        elif not self.relax.data.res[i].params.has_key(run2):
                            flag = 1
                        elif not hasattr(self.relax.data.res[i], 'chi2'):
                            flag = 1
                        elif not self.relax.data.res[i].chi2.has_key(run2):
                            flag = 1

                # All other selection methods.
                else:
                    if not hasattr(self.relax.data.res[i], 'params'):
                        flag = 1
                    elif not self.relax.data.res[i].params.has_key(run):
                        flag = 1
                    elif not hasattr(self.relax.data.res[i], 'chi2'):
                        flag = 1
                    elif not self.relax.data.res[i].chi2.has_key(run):
                        flag = 1
            if flag:
                continue

            # Model selection.
            best_model = self.modsel(i)

            # Add the modsel_run to self.relax.data.res[i].runs
            self.relax.data.res[i].runs.append(modsel_run)

            # Duplicate the data from the 'best_model' to the model selection run 'modsel_run'.
            self.duplicate_data(best_model, modsel_run, i)


    def aic(self, i, model, k, n):
        """Akaike's Information Criteria (AIC).

        The formula is:

            AIC = chi2 + 2k

        where:
            chi2 is the minimised chi-squared value.
            k is the number of parameters in the model.
        """

        return self.relax.data.res[i].chi2[model] + 2.0*k


    def aicc(self, i, model, k, n):
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

        return self.relax.data.res[i].chi2[model] + 2.0*k + 2.0*k*(k + 1.0) / (n - k - 1.0)


    def bic(self, i, model, k, n):
        """Bayesian or Schwarz Information Criteria.

        The formula is:

            BIC = chi2 + k ln n

        where:
            chi2 - is the minimised chi-squared value.
            k - is the number of parameters in the model.
            n is the dimension of the relaxation data set.
        """

        return self.relax.data.res[i].chi2[model] + k * log(n)


    def criteria_modsel(self, i):
        """Generic function for Information Criteria model selection."""

        # Initial model.
        best_model = None
        best_crit = float('inf')

        # Loop over the models.
        for model in self.runs:
            # Count the number of parameters in the model.
            k = len(self.relax.data.res[i].params[model])

            # Calculate the dimension of the relaxation data set.
            n = len(self.relax.data.res[i].relax_data[model])

            # Calculate the criterion value.
            crit = self.formula(i, model, k, n)

            # Select model.
            if crit < best_crit:
                best_model = model
                best_crit = crit

        return best_model


    def cv(self, i):
        """Single-item-out cross-validation."""

        # Initial model.
        best_model = None
        best_crit = float('inf')

        # Loop over the models.
        for k in xrange(len(self.runs[0])):
            # Sum of chi-squared values.
            sum_crit = 0.0

            # Loop over the validation samples and sum the chi-squared values.
            for j in xrange(len(self.runs)):
                sum_crit = sum_crit + self.relax.data.res[i].chi2[self.runs[j][k]]

            # Cross-validation criterion (average chi-squared value).
            crit = sum_crit / float(len(self.runs))

            # Select model.
            if crit < best_crit:
                best_model = self.runs[0][k]
                best_crit = crit

        return best_model


    def duplicate_data(self, best_model, modsel_run, i):
        """Function for duplicating of run specific data.

        The run specific data in self.relax.data.res[i] is copied from the run 'best_model' to the
        run 'modsel_run'.
        """

        # Test if 'best_model' exists.
        if not best_model in self.relax.data.run_names:
            raise RelaxRunError, best_model

        # Duplicate the diffusion tensor data.
        if self.relax.data.diff.has_key(best_model):
            self.relax.data.diff[modsel_run] = deepcopy(self.relax.data.diff[best_model])
        
        # Duplicate the residue specific data.
        for data in dir(self.relax.data.res[i]):
            # Get the data object.
            object = getattr(self.relax.data.res[i], data)

            # Test if the object is a dictionary (hash).
            if type(object) != dict:
                continue

            # Test if the object contains the key 'best_model'.
            if not object.has_key(best_model):
                continue

            # Duplicate the data.
            object[modsel_run] = deepcopy(object[best_model])
