###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


# The method given by Farrow et al., 1994:
#
#    Stage 1:   Creation of the files for the initial model-free calculations for models 1 to 5,
#        and f-tests between them.
#    Stage 2:   Model selection.
#

import sys
from re import match

from common_ops import Common_operations


class Farrow(Common_operations):
    def __init__(self, relax):
        """The model-free analysis of Farrow.

        Farrow's method for model-free analysis. (Farrow et al., 1994)
        """

        self.relax = relax


    def farrows_tests(self):
        """Check the 95% confidence limits and if the parameter is greater than its error."""

        data = self.relax.data.data
        relax_data = self.relax.data.relax_data

        for res in range(len(relax_data[0])):
            for model in self.relax.data.runs:
                # 95% confidence limit test.
                fail = 0
                for i in range(self.relax.data.num_ri):
                    label_fit = self.relax.data.frq_label[self.relax.data.remap_table[i]] + "_" + self.relax.data.data_types[i] + "_fit"
                    diff = self.relax.data.relax_data[i][res][2] - self.relax.data.data[model][res][label_fit]
                    if diff < 0:
                        diff = -diff
                    limit = 1.96 * float(relax_data[i][res][3])
                    if diff > limit:
                        fail = fail + 1
                if fail == 0:
                    data[model][res]['conf_lim'] = 1
                else:
                    data[model][res]['conf_lim'] = 0

                # Parameter greater than err test.
                if match('m1', model):
                    params = [ data[model][res]['s2'] ]
                    errs = [ data[model][res]['s2_err'] ]
                if match('m2', model):
                    params = [ data[model][res]['s2'], data[model][res]['te'] ]
                    errs = [ data[model][res]['s2_err'], data[model][res]['te_err'] ]
                if match('m3', model):
                    params = [ data[model][res]['s2'], data[model][res]['rex'] ]
                    errs = [ data[model][res]['s2_err'], data[model][res]['rex_err'] ]
                if match('m4', model):
                    params = [ data[model][res]['s2'], data[model][res]['te'], data[model][res]['rex'] ]
                    errs = [ data[model][res]['s2_err'], data[model][res]['te_err'], data[model][res]['rex_err'] ]
                if match('m5', model):
                    params = [ data[model][res]['s2f'], data[model][res]['s2s'], data[model][res]['te'] ]
                    errs = [ data[model][res]['s2f_err'], data[model][res]['s2s_err'], data[model][res]['te_err'] ]
                data[model][res]['param_test'] = self.test_param(params, errs)


    def model_selection(self):
        """Farrow's model selection."""

        data = self.relax.data.data
        self.farrows_tests()

        if self.relax.debug:
            self.relax.log.write("\n\n<<< Farrow's model selection >>>\n\n")

        for res in range(len(self.relax.data.relax_data[0])):
            self.relax.data.results.append({})

            if self.relax.debug:
                self.relax.log.write('%-22s\n' % ( "Checking res " + data['m1'][res]['res_num'] ))

            self.model = '0'

            # Model 1 to 5 tests.
            model_tests = [ 0, 0, 0, 0, 0 ]
            if data['m1'][res]['conf_lim'] and data['m1'][res]['param_test']:
                model_tests[0] = 1
            if data['m2'][res]['conf_lim'] and data['m2'][res]['param_test']:
                model_tests[1] = 1
            if data['m3'][res]['conf_lim'] and data['m3'][res]['param_test']:
                model_tests[2] = 1
            if data['m4'][res]['conf_lim'] and data['m4'][res]['param_test']:
                model_tests[3] = 1
            if data['m5'][res]['conf_lim'] and data['m5'][res]['param_test']:
                model_tests[4] = 1

            # Check if multiple models pass (m1 to m4).
            # Pick the model with the lowest chi squared value.
            for i in range(4):
                if match('0', self.model) and model_tests[i]:
                    self.model = `i + 1`
                elif not match('0', self.model) and model_tests[i]:
                    # Test if the chi2 of this new model is lower than the chi2 of the old.
                    if data["m"+`i+1`][res]['chi2'] < data["m"+self.model][res]['chi2']:
                        self.model = `i + 1`

            # Model 5 test (only if no other models fit).
            if match('0', self.model) and model_tests[4]:
                self.model = '5'

            # Fill in the results.
            if not match('0', self.model):
                self.relax.data.results[res] = self.fill_results(data["m"+self.model][res], model=self.model)
            else:
                self.relax.data.results[res] = self.fill_results(data['m1'][res], model='0')


    def print_data(self):
        """Print all the data into the 'data_all' file."""

        file = open('data_all', 'w')

        sys.stdout.write("[")
        for res in range(len(self.relax.data.results)):
            sys.stdout.write("-")
            file.write("\n\n<<< Residue " + self.relax.data.results[res]['res_num'])
            file.write(", Model " + self.relax.data.results[res]['model'] + " >>>\n")
            file.write('%-20s' % '')
            file.write('%-19s' % 'Model 1')
            file.write('%-19s' % 'Model 2')
            file.write('%-19s' % 'Model 3')
            file.write('%-19s' % 'Model 4')
            file.write('%-19s' % 'Model 5')

            # S2.
            file.write('\n%-20s' % 'S2')
            for model in self.relax.data.runs:
                file.write('%9.3f' % self.relax.data.data[model][res]['s2'])
                file.write('%1s' % '±')
                file.write('%-9.3f' % self.relax.data.data[model][res]['s2_err'])

            # S2f.
            file.write('\n%-20s' % 'S2f')
            for model in self.relax.data.runs:
                file.write('%9.3f' % self.relax.data.data[model][res]['s2f'])
                file.write('%1s' % '±')
                file.write('%-9.3f' % self.relax.data.data[model][res]['s2f_err'])

            # S2s.
            file.write('\n%-20s' % 'S2s')
            for model in self.relax.data.runs:
                file.write('%9.3f' % self.relax.data.data[model][res]['s2s'])
                file.write('%1s' % '±')
                file.write('%-9.3f' % self.relax.data.data[model][res]['s2s_err'])

            # te.
            file.write('\n%-20s' % 'te')
            for model in self.relax.data.runs:
                file.write('%9.2f' % self.relax.data.data[model][res]['te'])
                file.write('%1s' % '±')
                file.write('%-9.2f' % self.relax.data.data[model][res]['te_err'])

            # Rex.
            file.write('\n%-20s' % 'Rex')
            for model in self.relax.data.runs:
                file.write('%9.3f' % self.relax.data.data[model][res]['rex'])
                file.write('%1s' % '±')
                file.write('%-9.3f' % self.relax.data.data[model][res]['rex_err'])

            # Chi2.
            file.write('\n%-20s' % 'Chi2')
            for model in self.relax.data.runs:
                file.write('%-19.3f' % self.relax.data.data[model][res]['chi2'])

            # 95% confidence limits.
            file.write('\n%-20s' % '95% conf limits')
            for model in self.relax.data.runs:
                file.write('%-19i' % self.relax.data.data[model][res]['conf_lim'])

            # Parameters greater than errors test.
            file.write('\n%-20s' % 'params > errs')
            for model in self.relax.data.runs:
                file.write('%-19i' % self.relax.data.data[model][res]['param_test'])

            # Relaxation values
            for i in range(self.relax.data.num_ri):
                file.write('\n%-20s' % (self.relax.data.frq_label[self.relax.data.remap_table[i]] + " " + self.relax.data.data_types[i]))
                for model in self.relax.data.runs:
                    label_fit = self.relax.data.frq_label[self.relax.data.remap_table[i]] + "_" + self.relax.data.data_types[i] + "_fit"
                    file.write('%9.3f' % self.relax.data.relax_data[i][res][2])
                    file.write('%1s' % "|")
                    file.write('%-9.3f' % self.relax.data.data[model][res][label_fit])
                file.write('\n   %-20s' % "diff ± 95%")
                for model in self.relax.data.runs:
                    label_fit = self.relax.data.frq_label[self.relax.data.remap_table[i]] + "_" + self.relax.data.data_types[i] + "_fit"
                    diff = self.relax.data.relax_data[i][res][2] - self.relax.data.data[model][res][label_fit]
                    if diff < 0:
                        diff = -diff
                    file.write('%9.3f' % diff)
                    file.write('%1s' % '±')
                    file.write('%-9.3f' % (1.96 * float(self.relax.data.relax_data[i][res][3])))


        file.write('\n')
        sys.stdout.write("]\n")
        file.close()
