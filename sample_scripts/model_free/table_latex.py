###############################################################################
#                                                                             #
# Copyright (C) 2007-2009 Edward d'Auvergne                                   #
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

"""Script for converting the model-free results into a LaTeX table.

The longtable LaTeX package is necessary to allow the table to span multiple pages.  This table also
uses the more elegant booktable format.  The packages can be included using the LaTeX preamble
commands:

\usepackage{longtable}
\usepackage{booktabs}

Assuming the file name 'results.tex', the resultant table can be placed into a LaTeX manuscript
with the command:

\input{results}
"""

# Python module imports.
from string import replace

# relax module imports.
from generic_fns.mol_res_spin import spin_loop
from generic_fns import pipes


# Name of the results file.
RESULTS_FILE = 'final'


class Latex:
    def __init__(self):
        """Convert the final results into a LaTeX table."""

        # Create the data pipe.
        pipe.create(RESULTS_FILE, 'mf')

        # Load the model-free results.
        results.read(RESULTS_FILE, dir=None)

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
        self.file.write("Spin &%\n")
        self.file.write("Model &%\n")
        self.file.write("\multicolumn{2}{c}{$S^2$} &%\n")
        self.file.write("\multicolumn{2}{c}{$S^2_f$} &%\n")
        self.file.write("\multicolumn{2}{c}{$\\tau_e < 100$ or $\\tau_f$} &%\n")
        self.file.write("\multicolumn{2}{c}{$\\tau_e > 100$ or $\\tau_s$} &%\n")
        self.file.write("\multicolumn{2}{c}{$R_{ex}$ (" + repr(cdp.frq[cdp.ri_ids[0]] / 1e6) + " MHz)} \\\\\n")
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
        for spin, spin_id in spin_loop(return_id=True):
            # The spin ID string.
            spin_id = replace(spin_id, '&', '\&')
            self.file.write("%-20s & " % (spin_id))

            # The spin is not selected.
            if not spin.select:
                self.file.write("\\multicolumn{11}{c}{} \\\\\n")
                continue

            # The model-free model.
            if hasattr(spin, 'model'):
                self.file.write("$%s$ & " % spin.model)
            else:
                self.file.write("\\multicolumn{11}{c}{} \\\\\n")
                continue

            # S2.
            if spin.s2 == None:
                self.file.write("%25s & " % "\\multicolumn{2}{c}{}")
            elif not hasattr(spin, 's2_err'):
                self.file.write("%24s & " % "\\multicolumn{2}{c}{%.3f}" % spin.s2)
            else:
                self.file.write("%11.3f & %11.3f & " % (spin.s2, spin.s2_err))

            # S2f.
            if spin.s2f == None:
                self.file.write("%25s & " % "\\multicolumn{2}{c}{}")
            elif not hasattr(spin, 's2f_err'):
                self.file.write("%24s & " % "\\multicolumn{2}{c}{%.3f}" % spin.s2f)
            else:
                self.file.write("%11.3f & %11.3f & " % (spin.s2f, spin.s2f_err))

            # Fast motion (te < 100 ps or tf).
            if spin.te != None and spin.te <= 100 * 1e-12:
                if not hasattr(spin, 'te_err'):
                    self.file.write("%27s & " % ("\\multicolumn{2}{c}{%.2f}" % (spin.te * 1e12)))
                else:
                    self.file.write("%12.2f & %12.2f & " % (spin.te * 1e12, spin.te_err * 1e12))
            elif spin.tf != None:
                if not hasattr(spin, 'tf_err'):
                    self.file.write("%27s & " % ("\\multicolumn{2}{c}{%.2f}" % (spin.tf * 1e12)))
                else:
                    self.file.write("%12.2f & %12.2f & " % (spin.tf * 1e12, spin.tf_err * 1e12))
            else:
                self.file.write("%27s & " % "\\multicolumn{2}{c}{}")

            # Slow motion (te > 100 ps or ts).
            if spin.te != None and spin.te > 100 * 1e-12:
                if not hasattr(spin, 'te_err'):
                    self.file.write("%27s & " % ("\\multicolumn{2}{c}{%.2f}" % (spin.te * 1e12)))
                else:
                    self.file.write("%12.2f & %12.2f & " % (spin.te * 1e12, spin.te_err * 1e12))
            elif spin.ts != None:
                if not hasattr(spin, 'ts_err'):
                    self.file.write("%27s & " % ("\\multicolumn{2}{c}{%.2f}" % (spin.ts * 1e12)))
                else:
                    self.file.write("%12.2f & %12.2f & " % (spin.ts * 1e12, spin.ts_err * 1e12))
            else:
                self.file.write("%27s & " % "\\multicolumn{2}{c}{}")

            # Rex.
            if spin.rex == None:
                self.file.write("%27s \\\\\n" % "\\multicolumn{2}{c}{}")
            elif not hasattr(spin, 'rex_err'):
                self.file.write("%27s \\\\\n" % ("\\multicolumn{2}{c}{%.3f}" % (spin.rex * (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2)))
            else:
                self.file.write("%12.3f & %12.3f \\\\\n" % (spin.rex * (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2, spin.rex_err * (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2))

        # Start a new line.
        self.file.write("\n")


Latex()
