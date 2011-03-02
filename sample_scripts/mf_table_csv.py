###############################################################################
#                                                                             #
# Copyright (C) 2007-2011 Edward d'Auvergne                                   #
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

"""Script for converting the model-free results into a CSV table."""


# Python module imports.
from string import replace

# relax module imports.
from generic_fns.mol_res_spin import spin_loop
from generic_fns import pipes


# Name of the results file.
RESULTS_FILE = 'results'


class CSV:
    def __init__(self):
        """Convert the final results into a CSV table."""

        # Create the data pipe.
        pipe.create(RESULTS_FILE, 'mf')

        # Load the model-free results.
        results.read(RESULTS_FILE, dir=None)

        # Open the file.
        self.file = open('results.csv', 'w')

        # Table headings.
        self.headings()

        # The table body.
        self.table_body()

        # Close the file.
        self.file.close()


    def headings(self):
        """Create the table headings."""

        # Headings.
        self.file.write("Spin, ")
        self.file.write("Model, ")
        self.file.write("S2, ")
        self.file.write("S2f, ")
        self.file.write("te < 100 or tf, ")
        self.file.write("te > 100 or ts, ")
        self.file.write("Rex (" + repr(cdp.frq[0] / 1e6) + " MHz)")
        self.file.write("\n")

        # Units.
        self.file.write(",")
        self.file.write(",")
        self.file.write(",")
        self.file.write(",")
        self.file.write("ps,")
        self.file.write("ps,")
        self.file.write("s^-1")
        self.file.write("\n")


    def table_body(self):
        """Create the table body.

        This function need not be modified.
        """

        # Loop over the spin systems.
        for spin, spin_id in spin_loop(return_id=True):
            # The spin ID string.
            self.file.write("%s, " % (spin_id))

            # The spin is not selected.
            if not spin.select:
                self.file.write("\n")
                continue

            # The model-free model.
            if hasattr(spin, 'model'):
                self.file.write("%s, " % spin.model)
            else:
                self.file.write("\n")
                continue

            # S2.
            if spin.s2 == None:
                self.file.write(", ")
            elif not hasattr(spin, 's2_err'):
                self.file.write("%.3f, " % spin.s2)
            else:
                self.file.write("%.3f±%.3f, " % (spin.s2, spin.s2_err))

            # S2f.
            if spin.s2f == None:
                self.file.write(", ")
            elif not hasattr(spin, 's2f_err'):
                self.file.write("%.3f, " % spin.s2f)
            else:
                self.file.write("%.3f±%.3f, " % (spin.s2f, spin.s2f_err))

            # Fast motion (te < 100 ps or tf).
            if spin.te != None and spin.te <= 100 * 1e-12:
                if not hasattr(spin, 'te_err'):
                    self.file.write("%.2f, " % (spin.te * 1e12))
                else:
                    self.file.write("%.2f±%.2f, " % (spin.te * 1e12, spin.te_err * 1e12))
            elif spin.tf != None:
                if not hasattr(spin, 'tf_err'):
                    self.file.write("%.2f, " % (spin.tf * 1e12))
                else:
                    self.file.write("%.2f±%.2f, " % (spin.tf * 1e12, spin.tf_err * 1e12))
            else:
                self.file.write(", ")

            # Slow motion (te > 100 ps or ts).
            if spin.te != None and spin.te > 100 * 1e-12:
                if not hasattr(spin, 'te_err'):
                    self.file.write("%.2f, " % (spin.te * 1e12))
                else:
                    self.file.write("%.2f±%.2f, " % (spin.te * 1e12, spin.te_err * 1e12))
            elif spin.ts != None:
                if not hasattr(spin, 'ts_err'):
                    self.file.write("%.2f, " % (spin.ts * 1e12))
                else:
                    self.file.write("%.2f±%.2f, " % (spin.ts * 1e12, spin.ts_err * 1e12))
            else:
                self.file.write(", ")

            # Rex.
            if spin.rex == None:
                self.file.write(", ")
            elif not hasattr(spin, 'rex_err'):
                self.file.write("%.3f, " % (spin.rex * (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2))
            else:
                self.file.write("%.3f±%.3f, " % (spin.rex * (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2, spin.rex_err * (2.0 * pi * cdp.frq[cdp.ri_ids[0]])**2))

            # Start a new line.
            self.file.write("\n")


CSV()
