from re import match
from string import split

class Star:
    def __init__(self, relax):
        """Class to extract model-free data from the STAR formatted mfout file."""

        self.relax = relax


    def extract(self, mfout, num_res, chi2_lim=0.90, ftest_lim=0.80, ftest='n'):
        """Extract the data from the mfout file and Return it as a 2D data structure."""

        self.mfout = mfout
        self.num_res = num_res
        self.chi2_lim = chi2_lim
        self.ftest_lim = ftest_lim
        self.ftest = ftest

        self.data = []
        for i in range(self.num_res):
            self.data.append({})
        self.line_num = 0

        if match('n', self.ftest):
            self.get_relax_values()
            self.get_s2()
            self.get_s2f()
            self.get_s2s()
            self.get_te()
            self.get_rex()
            self.get_chi2()
        elif match('y', self.ftest):
            self.get_ftest()

        return self.data


    def get_chi2(self):
        # Jump to Chi2 data.
        for line in range(len(self.mfout)):
            self.row = split(self.mfout[line])
            try:
                self.row[0]
            except IndexError:
                continue

            if match('data_sse', self.row[0]):
                self.line_num = line + 3
                break
        if match('y', self.relax.data.mfin.sims):
            self.line_num = self.line_num + 2
            for i in range(self.num_res):
                self.row = [[]]
                self.row[0] = split(self.mfout[self.line_num])
                percentile = int(self.chi2_lim * 100.0 / 5.0)
                self.line_num = self.line_num + percentile
                self.row.append(split(self.mfout[self.line_num]))
                lines_next_res = 2 + ( 20 - int(percentile) )
                self.line_num = self.line_num + lines_next_res
                self.data[i]['chi2'] = float(self.row[0][1])
                self.data[i]['chi2_lim'] = float(self.row[1][1])
        else:
            self.split_rows(self.line_num, self.num_res)
            for i in range(self.num_res):
                self.data[i]['chi2'] = float(self.row[i][1])


    def get_ftest(self):
        # Jump to first line of data.
        for line in range(len(self.mfout)):
            self.row = [[]]
            self.row[0] = split(self.mfout[line])
            try:
                self.row[0][0]
            except IndexError:
                continue
            if match('data_F_dist', self.row[0][0]):
                self.line_num = line + 5
                break
        for i in range(self.num_res):
            self.row = [[]]
            self.row[0] = split(self.mfout[self.line_num])
            percentile = int(self.ftest_lim * 100.0 / 5.0)
            self.line_num = self.line_num + percentile
            self.row.append(split(self.mfout[self.line_num]))
            lines_next_res = 2 + ( 20 - int(percentile) )
            self.line_num = self.line_num + lines_next_res
            self.data[i]['res_num'] = self.row[0][0]
            self.data[i]['fstat'] = float(self.row[0][1])
            self.data[i]['fstat_lim'] = float(self.row[1][1])


    def get_relax_values(self):
        # Jump to first line of data.
        for line in range(len(self.mfout)):
            self.row = split(self.mfout[line])
            try:
                self.row[0]
            except IndexError:
                continue

            if match('data_relaxation', self.row[0]):
                self.line_num = line + 7
                break
        for i in range(self.relax.data.num_ri):
            self.split_rows(self.line_num, self.num_res)

            label = self.relax.data.frq_label[self.relax.data.remap_table[i]] + "_" + self.relax.data.data_types[i]
            label_err = self.relax.data.frq_label[self.relax.data.remap_table[i]] + "_" + self.relax.data.data_types[i] + "_err"
            label_fit = self.relax.data.frq_label[self.relax.data.remap_table[i]] + "_" + self.relax.data.data_types[i] + "_fit"

            for i in range(self.num_res):
                self.data[i][label] = float(self.row[i][1])
                self.data[i][label_err] = float(self.row[i][2])
                self.data[i][label_fit] = float(self.row[i][4])

            self.line_num = self.line_num + self.num_res + 3


    def get_rex(self):
        # Jump to Rex data.
        for line in range(len(self.mfout)):
            self.row = split(self.mfout[line])
            try:
                self.row[0]
            except IndexError:
                continue

            if match('Rex', self.row[0]):
                self.line_num = line + 1
                break
        self.split_rows(self.line_num, self.num_res)
        for i in range(self.num_res):
            self.data[i]['rex'] = float(self.row[i][1])
            self.data[i]['rex_err'] = float(self.row[i][5])


    def get_s2(self):
        # Jump to S2 data.
        for line in range(len(self.mfout)):
            self.row = split(self.mfout[line])
            try:
                self.row[0]
            except IndexError:
                continue

            if match('S2', self.row[0]):
                self.line_num = line + 1
                break
        self.split_rows(self.line_num, self.num_res)
        for i in range(self.num_res):
            self.data[i]['res_num'] = self.row[i][0]
            self.data[i]['s2'] = float(self.row[i][1])
            self.data[i]['s2_err'] = float(self.row[i][5])


    def get_s2f(self):
        # Jump to S2f data.
        for line in range(len(self.mfout)):
            self.row = split(self.mfout[line])
            try:
                self.row[0]
            except IndexError:
                continue

            if match('S2f', self.row[0]):
                self.line_num = line + 1
                break
        self.split_rows(self.line_num, self.num_res)
        for i in range(self.num_res):
            self.data[i]['s2f'] = float(self.row[i][1])
            self.data[i]['s2f_err'] = float(self.row[i][5])


    def get_s2s(self):
        # Jump to S2s data.
        for line in range(len(self.mfout)):
            self.row = split(self.mfout[line])
            try:
                self.row[0]
            except IndexError:
                continue

            if match('S2s', self.row[0]):
                self.line_num = line + 1
                break
        self.split_rows(self.line_num, self.num_res)
        for i in range(self.num_res):
            self.data[i]['s2s'] = float(self.row[i][1])
            self.data[i]['s2s_err'] = float(self.row[i][5])


    def get_te(self):
        # Jump to te data.
        for line in range(len(self.mfout)):
            self.row = split(self.mfout[line])
            try:
                self.row[0]
            except IndexError:
                continue

            if match('te', self.row[0]):
                self.line_num = line + 1
                break
        self.split_rows(self.line_num, self.num_res)
        for i in range(self.num_res):
            self.data[i]['te'] = float(self.row[i][1])
            self.data[i]['te_err'] = float(self.row[i][5])


    def split_rows(self, line_num, num_lines):
        """Get the next 'num_res' lines after a match."""

        for i in range(num_lines):
            if i == 0:
                self.row = [[]]
                self.row[0] = split(self.mfout[line_num])
            else:
                self.row.append(split(self.mfout[line_num + i]))
