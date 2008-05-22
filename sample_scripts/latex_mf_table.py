# Script for converting the model-free results into a LaTeX table.
#
# The longtable LaTeX package is necessary to allow the table to span multiple pages.  The package
# can be included using the LaTeX command:
#
# \usepackage{longtable}
#
# Assuming the file name 'results.tex', the resultant table can be placed into a LaTeX manuscript
# with the command:
#
# \input{results}
#


# The relax data storage object.
from data import Relax_data_store; ds = Relax_data_store()



class Latex:
    def __init__(self, relax):
        """Convert the final results into a LaTeX table."""

        self.relax = relax

        # Create the run.
        self.run = 'final'
        pipe.create(self.run, 'mf')

        # Load the model-free results.
        results.read(self.run, dir=None)

        # Open the file.
        self.file = open('results.tex', 'w')

        # LaTeX header.
        self.latex_header()

        # Table headings.
        self.headings()

        # Table footer (longtable repeating footers come just after the headings).
        self.footer()

        # The table body.
        self.table_body()

        # LaTeX ending.
        self.latex_ending()

        # Close the file.
        self.file.close()


    def footer(self):
        """Create the end of the table."""

        # Bottomrule.
        self.file.write("\\bottomrule\n")

        # End the repeating footer.
        self.file.write("\\endfoot\n\n")


    def headings(self):
        """Create the LaTeX table headings."""

        # Spacing.
        self.file.write("\\\\[-5pt]\n")

        # Toprule.
        self.file.write("\\toprule\n\n")

        # Headings.
        self.file.write("% Headings.\n")
        self.file.write("Residue &%\n")
        self.file.write("Model &%\n")
        self.file.write("\multicolumn{2}{c}{$S^2$} &%\n")
        self.file.write("\multicolumn{2}{c}{$S^2_f$} &%\n")
        self.file.write("\multicolumn{2}{c}{$\\tau_e < 100$ or $\\tau_f$} &%\n")
        self.file.write("\multicolumn{2}{c}{$\\tau_e > 100$ or $\\tau_s$} &%\n")
        self.file.write("\multicolumn{2}{c}{$R_{ex}$ (" + `ds.frq[self.run][0] / 1e6` + " MHz)} \\\\\n")
        self.file.write("\n")

        # Units.
        self.file.write("% Units.\n")
        self.file.write("&%\n")
        self.file.write("&%\n")
        self.file.write("\multicolumn{2}{c}{} &%\n")
        self.file.write("\multicolumn{2}{c}{} &%\n")
        self.file.write("\multicolumn{2}{c}{($ps$)} &%\n")
        self.file.write("\multicolumn{2}{c}{($ps$)} &%\n")
        self.file.write("\multicolumn{2}{c}{($s^{-1}$)} \\\\\n")
        self.file.write("\n")

        # Midrule.
        self.file.write("\\midrule\n")

        # End the repeating heading.
        self.file.write("\\endhead\n\n")


    def latex_ending(self):
        """Create the end of the table."""

        # End the longtable environment.
        self.file.write("\\end{longtable}\n")

        # End the font size.
        self.file.write("\\end{small}\n")


    def latex_header(self):
        """Create the LaTeX header.

        This function will need to be heavily modified to suit your needs.
        """

        # Font size.
        self.file.write("% Small font.\n")
        self.file.write("\\begin{small}\n\n")

        # The longtable environment.
        self.file.write("% The longtable environment.\n")
        self.file.write("\\begin{longtable}{l l r @{$\\pm$} l r @{$\\pm$} l r @{$\\pm$} l r @{$\\pm$} l r @{$\\pm$} l}\n\n")

        # The caption.
        self.file.write("% Caption.\n")
        self.file.write("\\caption[Sample list of figures caption]{Sample full caption}\n\n")

        # The LaTeX label.
        self.file.write("% Label.\n")
        self.file.write("\\label{table: model-free results}\n\n")


    def table_body(self):
        """Create the table body.

        This function need not be modified.
        """

        # Comment.
        self.file.write("% The table body.\n")

        # Loop over the spin systems.
        for i in xrange(len(ds.res[self.run])):
            # Alias the spin system data container.
            data = ds.res[self.run][i]

            # The residue tag.
            self.file.write("%-7s & " % (data.name + `data.num`))

            # The residue is not selected.
            if not data.select:
                self.file.write("\\\n")

            # The model-free model.
            self.file.write("$%s$ & " % data.model)

            # S2.
            if data.s2 == None:
                self.file.write("%21s & " % "\\multicolumn{2}{c}{}")
            else:
                self.file.write("%9.3f & %9.3f & " % (data.s2, data.s2_err))

            # S2f.
            if data.s2f == None:
                self.file.write("%21s & " % "\\multicolumn{2}{c}{}")
            else:
                self.file.write("%9.3f & %9.3f & " % (data.s2f, data.s2f_err))

            # Fast motion (te < 100 ps or tf).
            if data.te != None and data.te <= 100 * 1e-12:
                self.file.write("%9.2f & %9.2f & " % (data.te * 1e12, data.te_err * 1e12))
            elif data.tf != None:
                self.file.write("%9.2f & %9.2f & " % (data.tf * 1e12, data.tf_err * 1e12))
            else:
                self.file.write("%21s & " % "\\multicolumn{2}{c}{}")

            # Slow motion (te > 100 ps or ts).
            if data.te != None and data.te > 100 * 1e-12:
                self.file.write("%9.2f & %9.2f & " % (data.te * 1e12, data.te_err * 1e12))
            elif data.ts != None:
                self.file.write("%9.2f & %9.2f & " % (data.ts * 1e12, data.ts_err * 1e12))
            else:
                self.file.write("%21s & " % "\\multicolumn{2}{c}{}")

            # Rex.
            if data.rex == None:
                self.file.write("%21s \\\\\n" % "\\multicolumn{2}{c}{}")
            else:
                self.file.write("%9.3f & %9.3f \\\\\n" % (data.rex * (2.0 * pi * ds.frq[self.run][0])**2, data.rex_err * (2.0 * pi * ds.frq[self.run][0])**2))

        # Start a new line.
        self.file.write("\n")


Latex(self.relax)
