# A method based on asymptotic model selection criteria.
#
# The following asymptotic methods are supported:
#    AIC - Akaike Information Criteria
#    AICc - Akaike Information Criteria corrected for small sample sizes
#    BIC - Schwartz Criteria
#
# The program is divided into the following stages:
#    Stage 1:  Creation of the files for the model-free calculations for models 1 to 5.  Monte Carlo
#        simulations are not used on these initial runs, because the errors are not needed (should
#        speed up analysis considerably).
#    Stage 2:  Model selection and the creation of the final run.  Monte Carlo simulations are used
#        to find errors.  This stage has the option of optimizing the diffusion tensor along with
#        the model-free parameters.
#    Stage 3:  Extraction of the data.

import sys
from math import log, pi
from re import match

from common_ops import Common_operations


class Asymptotic(Common_operations):
    def __init__(self, relax):
        """Model-free analysis based on asymptotic model selection methods."""

        self.relax = relax


    def run(self):
        """Model selection."""

        data = self.relax.data.data
        n = float(self.relax.data.num_data_sets)

        if self.relax.debug:
            self.relax.log.write("\n\n<<< " + self.relax.usr_param.method + " model selection >>>\n\n")

        for res in range(len(self.relax.data.relax_data[0])):
            self.relax.data.results.append({})

            if self.relax.debug:
                self.relax.log.write('%-22s\n' % ( "Checking res " + data['m1'][res]['res_num'] ))

            err = []
            for set in range(len(self.relax.data.relax_data)):
                err.append(float(self.relax.data.relax_data[set][res][3]))

            for model in self.relax.data.runs:
                chi2 = data[model][res]['chi2']
                crit = chi2 / (2.0 * n)

                if match('m1', model):
                    k = 1.0
                elif match('m2', model) or match('m3', model):
                    k = 2.0
                elif match('m4', model) or match('m5', model):
                    k = 3.0

                if match('^AIC$', self.relax.usr_param.method):
                    crit = crit + k / n

                elif match('^AICc$', self.relax.usr_param.method):
                    if n - k == 1:
                        crit = 1e99
                    else:
                        crit = crit + k/n + k*(k + 1.0)/((n - k - 1.0) * n)

                elif match('^BIC$', self.relax.usr_param.method):
                    crit = crit + k*log(n) / (2.0 * n)

                data[model][res]['crit'] = crit

            # Select model.
            min = 'm1'
            for run in self.relax.data.runs:
                if data[run][res]['crit'] < data[min][res]['crit']:
                    min = run
            if data[min][res]['crit'] == float('inf'):
                self.relax.data.results[res] = self.fill_results(data[min][res], model='0')
            else:
                self.relax.data.results[res] = self.fill_results(data[min][res], model=min[1])

            if self.relax.debug:
                self.relax.log.write(self.relax.usr_param.method + " (m1): " + `data['m1'][res]['crit']` + "\n")
                self.relax.log.write(self.relax.usr_param.method + " (m2): " + `data['m2'][res]['crit']` + "\n")
                self.relax.log.write(self.relax.usr_param.method + " (m3): " + `data['m3'][res]['crit']` + "\n")
                self.relax.log.write(self.relax.usr_param.method + " (m4): " + `data['m4'][res]['crit']` + "\n")
                self.relax.log.write(self.relax.usr_param.method + " (m5): " + `data['m5'][res]['crit']` + "\n")
                self.relax.log.write("The selected model is: " + min + "\n\n")


    def print_data(self):
        """Print all the data into the 'data_all' file."""

        file = open('data_all', 'w')
        file_crit = open('crit', 'w')

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

            file_crit.write('%-6s' % self.relax.data.results[res]['res_num'])
            file_crit.write('%-6s' % self.relax.data.results[res]['model'])

            # S2.
            file.write('\n%-20s' % 'S2')
            for run in self.relax.data.runs:
                file.write('%9.3f' % self.relax.data.data[run][res]['s2'])
                file.write('%1s' % '±')
                file.write('%-9.3f' % self.relax.data.data[run][res]['s2_err'])

            # S2f.
            file.write('\n%-20s' % 'S2f')
            for run in self.relax.data.runs:
                file.write('%9.3f' % self.relax.data.data[run][res]['s2f'])
                file.write('%1s' % '±')
                file.write('%-9.3f' % self.relax.data.data[run][res]['s2f_err'])

            # S2s.
            file.write('\n%-20s' % 'S2s')
            for run in self.relax.data.runs:
                file.write('%9.3f' % self.relax.data.data[run][res]['s2s'])
                file.write('%1s' % '±')
                file.write('%-9.3f' % self.relax.data.data[run][res]['s2s_err'])

            # te.
            file.write('\n%-20s' % 'te')
            for run in self.relax.data.runs:
                file.write('%9.2f' % self.relax.data.data[run][res]['te'])
                file.write('%1s' % '±')
                file.write('%-9.2f' % self.relax.data.data[run][res]['te_err'])

            # Rex.
            file.write('\n%-20s' % 'Rex')
            for run in self.relax.data.runs:
                file.write('%9.3f' % self.relax.data.data[run][res]['rex'])
                file.write('%1s' % '±')
                file.write('%-9.3f' % self.relax.data.data[run][res]['rex_err'])

            # Chi2.
            file.write('\n%-20s' % 'Chi2')
            for run in self.relax.data.runs:
                file.write('%-19.3f' % self.relax.data.data[run][res]['chi2'])

            # Model selection criteria.
            file.write('\n%-20s' % self.relax.usr_param.method)
            for run in self.relax.data.runs:
                file.write('%-19.6f' % self.relax.data.data[run][res]['crit'])

                file_crit.write('%-25s' % `self.relax.data.data[run][res]['crit']`)
            file_crit.write('\n')

        file.write('\n')
        sys.stdout.write("]\n")
        file.close()
