# Model selection using the expected overall discrepancy.
#
# The input relaxation data for this method should be the true data (theoretical, back calculated relaxation values).
#
# The program is divided into the following stages:
#    Stage 1:  Creation of the files for the model-free calculations for models 1 to 5.  Monte Carlo
#        simulations are used, but the initial data rather than the backcalculated data is randomised.
#    Stage 2:  Model selection and the creation of the final run.  Monte Carlo simulations are used to
#        find errors.  This stage has the option of optimizing the diffusion tensor along with the
#        model-free parameters.
#    Stage 3:  Extraction of the data.

import sys
from math import log, pi
from re import match

from common_ops import Common_operations


class Exp_overall_disc(Common_operations):
    def __init__(self, relax):
        """Model-free analysis based on the expected overall discrepancy."""

        self.relax = relax


    def model_selection(self):
        """Model selection."""

        data = self.relax.data.data
        self.relax.data.calc_frq()
        self.relax.data.calc_constants()
        n = float(self.relax.data.num_data_sets)
        tm = float(self.relax.usr_param.tm['val']) * 1e-9

        if self.relax.debug:
            self.relax.log.write("\n\n<<< Expected overall discrepancy >>>\n\n")

        print "Calculating the expected overall discrepancy"
        for res in range(len(self.relax.data.relax_data[0])):
            print "Residue: " + self.relax.data.relax_data[0][res][1] + " " + self.relax.data.relax_data[0][res][0]
            self.relax.data.results.append({})
            file_name = self.relax.data.relax_data[0][res][1] + '_' + self.relax.data.relax_data[0][res][0] + '.out'

            if self.relax.debug:
                self.relax.log.write('%-22s\n' % ( "< Checking res " + data['m1'][res]['res_num'] + " >\n"))

            real = []
            err = []
            types = []
            for i in range(self.relax.data.num_ri):
                real.append(float(self.relax.data.relax_data[i][res][2]))
                err.append(float(self.relax.data.relax_data[i][res][3]))
                types.append([self.relax.data.data_types[i], float(self.relax.data.frq[self.relax.data.remap_table[i]])])

            for model in self.relax.data.runs:
                if self.relax.debug:
                    self.relax.log.write("\nCalculating expected overall discrepancy for res " + `res` + ", model " + model + "\n\n")
                    for i in range(self.relax.data.num_ri):
                        self.relax.log.write("-------------------")
                    self.relax.log.write("\n")
                    for i in range(self.relax.data.num_ri):
                        name = " Orig " + self.relax.data.frq_label[self.relax.data.remap_table[i]] + " " + self.relax.data.data_types[i]
                        self.relax.log.write("%-17s%2s" % (name, " |"))
                    self.relax.log.write("\n")
                    for i in range(self.relax.data.num_ri):
                        self.relax.log.write("%8.4f" % self.relax.data.relax_data[i][res][2])
                        self.relax.log.write("%1s" % "±")
                        self.relax.log.write("%-8.4f" % self.relax.data.relax_data[i][res][3])
                        self.relax.log.write("%2s" % " |")
                    self.relax.log.write("\n")
                    for i in range(self.relax.data.num_ri):
                        self.relax.log.write("-------------------")
                    self.relax.log.write("\n\n")

                file = self.relax.file_ops.open_file(model + "/" + file_name)
                sum_chi2 = 0.0
                num_sims = float(len(file))
                for sim in range(len(file)):
                    if self.relax.debug:
                        self.relax.log.write("%5s%-10i%2s" % ("Sim: ", sim, " |"))

                    if match('m1', model):
                        back_calc = self.relax.calc_relax_data.calc(tm, model, types, [ file[sim][2] ])
                    elif match('m2', model) or match('m3', model):
                        back_calc = self.relax.calc_relax_data.calc(tm, model, types, [ file[sim][2], file[sim][3] ])
                    elif match('m4', model) or match('m5', model):
                        back_calc = self.relax.calc_relax_data.calc(tm, model, types, [ file[sim][2], file[sim][3], file[sim][4] ])
                    chi2 = self.relax.calc_chi2.relax_data(real, err, back_calc)
                    sum_chi2 = sum_chi2 + chi2

                    if self.relax.debug:
                        self.relax.log.write("%7s%-10.4f%2s" % (" Chi2: ", chi2, " |"))
                        self.relax.log.write("%11s%-13.4f%2s\n" % (" Sum Chi2: ", sum_chi2, " |"))

                ave_chi2 = sum_chi2 / num_sims

                if self.relax.debug:
                    self.relax.log.write("\nAverage Chi2 is: " + `ave_chi2` + "\n\n")

                data[model][res]['expect'] = ave_chi2 / (2.0 * n)

            # Select model.
            min = 'm1'
            for model in self.relax.data.runs:
                if data[model][res]['expect'] < data[min][res]['expect']:
                    min = model
            if data[min][res]['expect'] == float('inf'):
                self.relax.data.results[res] = self.fill_results(data[min][res], model='0')
            else:
                self.relax.data.results[res] = self.fill_results(data[min][res], model=min[1])

            if self.relax.debug:
                self.relax.log.write(self.relax.usr_param.method + " (m1): " + `data['m1'][res]['expect']` + "\n")
                self.relax.log.write(self.relax.usr_param.method + " (m2): " + `data['m2'][res]['expect']` + "\n")
                self.relax.log.write(self.relax.usr_param.method + " (m3): " + `data['m3'][res]['expect']` + "\n")
                self.relax.log.write(self.relax.usr_param.method + " (m4): " + `data['m4'][res]['expect']` + "\n")
                self.relax.log.write(self.relax.usr_param.method + " (m5): " + `data['m5'][res]['expect']` + "\n")
                self.relax.log.write("The selected model is: " + min + "\n\n")

            print "   Model " + self.relax.data.results[res]['model']


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

            # Expected overall discrepancy.
            file.write('\n%-20s' % 'Expect')
            for model in self.relax.data.runs:
                file.write('%-19.3f' % self.relax.data.data[model][res]['expect'])

                file_crit.write('%-25s' % `self.relax.data.data[model][res]['expect']`)
            file_crit.write('\n')

        file.write('\n')
        sys.stdout.write("]\n")
        file.close()
