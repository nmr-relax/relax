class write:
    def __init__(self, relax):
        """Class containing functions specific to model-free analysis."""

        self.relax = relax


    def output_init(self):
        """Create the directories and files for output.

        The directory with the name of the model will be created.  The results will be placed in the
        file 'results' in the model directory.
        """

        try:
            mkdir(self.model)
        except OSError:
            if self.overwrite_flag:
                files = listdir(self.model)
                for file in files:
                    path = self.model + "/" + file
                    remove(path)
            else:
                print "The directory ./" + self.model + " already exists."
                print "To overwrite, set the overwrite flag to 1."
                return 0

        self.relax.results = open(self.model + '/results', 'w')
        self.print_header()
        return 1


    def print_header(self):
        self.relax.results.write("%-5s" % "Num")
        self.relax.results.write("%-6s" % "Name")
        if match('m1', self.model):
            self.relax.results.write("%-30s" % "S2")
        elif match('m2', self.model):
            self.relax.results.write("%-30s" % "S2")
            self.relax.results.write("%-30s" % "te (ps)")
        elif match('m3', self.model):
            self.relax.results.write("%-30s" % "S2")
            self.relax.results.write("%-30s" % ("Rex (" + self.relax.data.frq_label[0] + " MHz)"))
        elif match('m4', self.model):
            self.relax.results.write("%-30s" % "S2")
            self.relax.results.write("%-30s" % "te (ps)")
            self.relax.results.write("%-30s" % ("Rex (" + self.relax.data.frq_label[0] + " MHz)"))
        elif match('m5', self.model):
            self.relax.results.write("%-30s" % "S2f")
            self.relax.results.write("%-30s" % "S2s")
            self.relax.results.write("%-30s" % "ts (ps)")
        self.relax.results.write("%-30s" % "Chi-squared statistic")
        self.relax.results.write("%-15s" % "Iterations")
        self.relax.results.write("%-15s" % "Func calls")
        self.relax.results.write("%-15s" % "Grad calls")
        self.relax.results.write("%-15s" % "Hessian calls")
        self.relax.results.write("%-30s\n" % "Warning")


    def print_results(self):
        self.relax.results.write("%-5s" % self.relax.data.seq[self.res][0])
        self.relax.results.write("%-6s" % self.relax.data.seq[self.res][1])
        if match('m1', self.relax.data.model):
            s2 = self.params[0]
            print "S2: " + `s2` + " Chi2: " + `self.chi2`
            self.relax.results.write("%-30s" % `s2`)
        elif match('m2', self.relax.data.model):
            s2 = self.params[0]
            if self.scaling_flag:
                te = self.params[1] * 1e12 / self.c
            else:
                te = self.params[1] * 1e12
            print "S2: " + `s2` + " te: " + `te` + " Chi2: " + `self.chi2`
            self.relax.results.write("%-30s" % `s2`)
            self.relax.results.write("%-30s" % `te`)
        elif match('m3', self.relax.data.model):
            s2 = self.params[0]
            rex = self.params[1] * (1e-8 * self.relax.data.frq[0])**2
            print "S2: " + `s2` + " Rex: " + `rex` + " Chi2: " + `self.chi2`
            self.relax.results.write("%-30s" % `s2`)
            self.relax.results.write("%-30s" % `rex`)
        elif match('m4', self.relax.data.model):
            s2 = self.params[0]
            if self.scaling_flag:
                te = self.params[1] * 1e12 / self.c
            else:
                te = self.params[1] * 1e12
            rex = self.params[2] * (1e-8 * self.relax.data.frq[0])**2
            print "S2: " + `s2` + " te: " + `te` + " Rex: " + `rex` + " Chi2: " + `self.chi2`
            self.relax.results.write("%-30s" % `s2`)
            self.relax.results.write("%-30s" % `te`)
            self.relax.results.write("%-30s" % `rex`)
        elif match('m5', self.relax.data.model):
            s2f = self.params[0]
            s2s = self.params[1]
            if self.scaling_flag:
                ts = self.params[2] * 1e12 / self.c
            else:
                ts = self.params[2] * 1e12
            print "S2f: " + `s2f` + " S2s: " + `s2s` + " ts: " + `ts` + " Chi2: " + `self.chi2`
            self.relax.results.write("%-30s" % `s2f`)
            self.relax.results.write("%-30s" % `s2s`)
            self.relax.results.write("%-30s" % `ts`)
        self.relax.results.write("%-30s" % `self.chi2`)
        self.relax.results.write("%-15s" % `self.iter_count`)
        self.relax.results.write("%-15s" % `self.f_count`)
        self.relax.results.write("%-15s" % `self.g_count`)
        self.relax.results.write("%-15s" % `self.h_count`)
        if self.warning:
            self.relax.results.write("%-30s\n" % `self.warning`)
        else:
            self.relax.results.write("\n")
