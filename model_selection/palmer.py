# The method given by (Mandel et al., 1995) is divided into the three stages:
#
#    Stage 1:  Creation of the files for the initial model-free calculations for models 1 to 5,
#        and f-tests between them.
#    Stage 2:  Model selection and the creation of the final run.  Monte Carlo simulations are used to
#        find errors.  This stage has the option of optimizing the diffusion tensor along with the
#        model-free parameters.
#    Stage 3:  Extraction of the data.
#
# These stages are repeated until the data converges.

import sys
from re import match

from common_ops import common_operations


class palmer(common_operations):
    def __init__(self, relax):
        """The model-free analysis of Palmer.

        print "Palmer's method for model-free analysis. (Mandel et al., 1995)"
        """
        self.relax = relax


    def anova_tests(self):
        """Do the chi squared and F-tests."""

        for res in range(len(self.relax.data.relax_data[0])):
            for run in self.relax.data.runs:
                if match('^m', run):
                    # Chi squared test.
                    if self.relax.data.data[run][res]['chi2'] <= self.relax.data.data[run][res]['chi2_lim']:
                        self.relax.data.data[run][res]['chi2_test'] = 1
                    else:
                        self.relax.data.data[run][res]['chi2_test'] = 0

                    # Large chi squared test.
                    if self.relax.data.data[run][res]['chi2'] >= float(self.relax.usr_param.large_chi2):
                        self.relax.data.data[run][res]['large_chi2'] = 1
                    else:
                        self.relax.data.data[run][res]['large_chi2'] = 0

                    # Zero chi squared test.
                    if self.relax.data.data[run][res]['chi2'] == 0.0:
                        self.relax.data.data[run][res]['zero_chi2'] = 1
                    else:
                        self.relax.data.data[run][res]['zero_chi2'] = 0

                else:
                    # F-test.
                    if self.relax.data.data[run][res]['fstat_lim'] < 1.5:
                        if self.relax.data.data[run][res]['fstat'] > 1.5:
                            self.relax.data.data[run][res]['ftest'] = 1
                        else:
                            self.relax.data.data[run][res]['ftest'] = 0
                    elif self.relax.data.data[run][res]['fstat_lim'] >= 1.5:
                        if self.relax.data.data[run][res]['fstat'] > self.relax.data.data[run][res]['fstat_lim']:
                            self.relax.data.data[run][res]['ftest'] = 1
                        else:
                            self.relax.data.data[run][res]['ftest'] = 0

    def model_selection(self):
        """Palmer's model selection."""

        self.anova_tests()
        if self.relax.data.num_data_sets > 3:
            # ie degrees of freedom > 0 in all models.
            print "The number of data sets is greater than 3."
            print "\tRunning Palmer's model selection, with additional chi-squared and F-tests"
            print "\tfor models 4 and 5 (the degrees of freedom for these models are greater than 0).\n"

            if self.relax.debug:
                self.relax.log.write("Extended model selection.\n\n")

            self.model_selection_extended()
        else:
            print "The number of data sets is equal to 3."
            print "\tRunning Palmer's model selection.\n"

            if self.relax.debug:
                self.relax.log.write("Normal model selection.\n\n")

            self.model_selection_normal()


    def model_selection_normal(self):
        """Palmer's model selection."""

        data = self.relax.data.data

        if self.relax.debug:
            self.relax.log.write("\n\n<<< Palmer's model selection >>>\n\n")

        for res in range(len(self.relax.data.relax_data[0])):
            self.relax.data.results.append({})

            if self.relax.debug:
                self.relax.log.write('%-22s\n' % ( "Checking res " + data['m1'][res]['res_num'] ))

            # Model 1 test.
            if data['m1'][res]['chi2_test']:
                self.relax.data.results[res] = self.fill_results(data['m1'][res], model='1')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 1]')

            # Test if both model 2 and 3 fit!!! (Should not occur)
            elif data['m2'][res]['chi2_test'] and data['f-m1m2'][res]['ftest'] \
                and data['m3'][res]['chi2_test'] and data['f-m1m3'][res]['ftest']:
                self.relax.data.results[res] = self.fill_results(data['m1'][res], model='2+3')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 2 and 3]')

            # Model 2 test.
            elif data['m2'][res]['chi2_test'] and data['f-m1m2'][res]['ftest']:
                self.relax.data.results[res] = self.fill_results(data['m2'][res], model='2')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 2]')

            # Model 3 test.
            elif data['m3'][res]['chi2_test'] and data['f-m1m3'][res]['ftest']:
                self.relax.data.results[res] = self.fill_results(data['m3'][res], model='3')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 3]')

            # Large chi squared test for model 1.
            elif data['m1'][res]['large_chi2'] == 0:
                self.relax.data.results[res] = self.fill_results(data['m1'][res], model='1')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 1*]')

            # Test if both model 4 and 5 fit!!! (Should not occur)
            elif data['m4'][res]['zero_chi2'] and data['m5'][res]['zero_chi2']:
                self.relax.data.results[res] = self.fill_results(data['m1'][res], model='4+5')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 4 and 5]')

            # Model 4 test.
            elif data['m4'][res]['zero_chi2']:
                self.relax.data.results[res] = self.fill_results(data['m4'][res], model='4')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 4]')

            # Model 5 test.
            elif data['m5'][res]['zero_chi2']:
                self.relax.data.results[res] = self.fill_results(data['m5'][res], model='5')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 5]')

            # No model fits!
            else:
                self.relax.data.results[res] = self.fill_results(data['m1'][res], model='0')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 0]')


    def model_selection_extended(self):
        """Palmer's model selection (extended).

        Palmer's model selection, but with additional chi-squared and F-tests for models 4 and 5
        because the number of degrees of freedom for these models are greater than 0.  See the code
        below for details of these changes.
        """

        data = self.relax.data.data

        if self.relax.debug:
            self.relax.log.write("\n\n<<< Palmer's model selection (extended) >>>\n\n")

        for res in range(len(self.relax.data.relax_data[0])):
            self.relax.data.results.append({})

            if self.relax.debug:
                self.relax.log.write('%-22s\n' % ( "Checking res " + data['m1'][res]['res_num'] ))

            # Model 1 test.
            if data['m1'][res]['chi2_test']:
                self.relax.data.results[res] = self.fill_results(data['m1'][res], model='1')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 1]')

            # Test if both model 2 and 3 fit!!! (Should not occur)
            elif data['m2'][res]['chi2_test'] and data['f-m1m2'][res]['ftest'] \
                and data['m3'][res]['chi2_test'] and data['f-m1m3'][res]['ftest']:
                self.relax.data.results[res] = self.fill_results(data['m1'][res], model='2+3')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 2 and 3]')

            # Model 2 test.
            elif data['m2'][res]['chi2_test'] and data['f-m1m2'][res]['ftest']:
                self.relax.data.results[res] = self.fill_results(data['m2'][res], model='2')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 2]')

            # Model 3 test.
            elif data['m3'][res]['chi2_test'] and data['f-m1m3'][res]['ftest']:
                self.relax.data.results[res] = self.fill_results(data['m3'][res], model='3')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 3]')

            # Large chi squared test for model 1.
            elif data['m1'][res]['large_chi2'] == 0:
                self.relax.data.results[res] = self.fill_results(data['m1'][res], model='1')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 1*]')

            # Test if both model 4 and 5 fit!!! (Should not occur)
            elif data['m4'][res]['chi2_test'] and ( data['f-m2m4'][res]['ftest'] or data['f-m3m4'][res]['ftest'] ) \
                and data['m5'][res]['chi2_test'] and data['f-m2m5'][res]['ftest']:
                self.relax.data.results[res] = self.fill_results(data['m1'][res], model='4+5')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 4 and 5]')

            # Model 4 test.
            elif data['m4'][res]['chi2_test'] and ( data['f-m2m4'][res]['ftest'] or data['f-m3m4'][res]['ftest'] ):
                self.relax.data.results[res] = self.fill_results(data['m4'][res], model='4')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 4]')

            # Model 5 test.
            elif data['m5'][res]['chi2_test'] and data['f-m2m5'][res]['ftest']:
                self.relax.data.results[res] = self.fill_results(data['m5'][res], model='5')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 5]')

            # No model fits!
            else:
                self.relax.data.results[res] = self.fill_results(data['m1'][res], model='0')
                if self.relax.debug:
                    self.relax.log.write('%-12s' % '[Model 0]')


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
            for run in self.relax.data.runs:
                if match('^m', run):
                    file.write('%9.3f' % self.relax.data.data[run][res]['s2'])
                    file.write('%1s' % '±')
                    file.write('%-9.3f' % self.relax.data.data[run][res]['s2_err'])

            # S2f.
            file.write('\n%-20s' % 'S2f')
            for run in self.relax.data.runs:
                if match('^m', run):
                    file.write('%9.3f' % self.relax.data.data[run][res]['s2f'])
                    file.write('%1s' % '±')
                    file.write('%-9.3f' % self.relax.data.data[run][res]['s2f_err'])

            # S2s.
            file.write('\n%-20s' % 'S2s')
            for run in self.relax.data.runs:
                if match('^m', run):
                    file.write('%9.3f' % self.relax.data.data[run][res]['s2s'])
                    file.write('%1s' % '±')
                    file.write('%-9.3f' % self.relax.data.data[run][res]['s2s_err'])

            # te.
            file.write('\n%-20s' % 'te')
            for run in self.relax.data.runs:
                if match('^m', run):
                    file.write('%9.2f' % self.relax.data.data[run][res]['te'])
                    file.write('%1s' % '±')
                    file.write('%-9.2f' % self.relax.data.data[run][res]['te_err'])

            # Rex.
            file.write('\n%-20s' % 'Rex')
            for run in self.relax.data.runs:
                if match('^m', run):
                    file.write('%9.3f' % self.relax.data.data[run][res]['rex'])
                    file.write('%1s' % '±')
                    file.write('%-9.3f' % self.relax.data.data[run][res]['rex_err'])

            # Chi2.
            file.write('\n%-20s' % 'Chi2')
            for run in self.relax.data.runs:
                if match('^m', run):
                    file.write('%-19.3f' % self.relax.data.data[run][res]['chi2'])

            # Chi2 limit.
            file.write('\n%-20s' % 'Chi2 limit')
            for run in self.relax.data.runs:
                if match('^m', run):
                    file.write('%-19.3f' % self.relax.data.data[run][res]['chi2_lim'])

            # Chi2 test.
            file.write('\n%-20s' % 'Chi2 test')
            for run in self.relax.data.runs:
                if match('^m', run):
                    file.write('%-19s' % self.relax.data.data[run][res]['chi2_test'])

            # large Chi2.
            file.write('\n%-20s' % 'large Chi2')
            for run in self.relax.data.runs:
                if match('^m', run):
                    file.write('%-19s' % self.relax.data.data[run][res]['large_chi2'])

            # zero Chi2.
            file.write('\n%-20s' % 'zero Chi2')
            for run in self.relax.data.runs:
                if match('^m', run):
                    file.write('%-19s' % self.relax.data.data[run][res]['zero_chi2'])

        file.write('\n')
        sys.stdout.write("]\n")
        file.close()
