###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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

import sys


class Relax_fit:
    def __init__(self, relax, test_name):
        """Class for testing various aspects specific to relaxation curve-fitting."""

        self.relax = relax

        # Sparky loading test.
        if test_name == 'read_sparky':
            # The name of the test.
            self.name = "Loading of Sparky peak heights"

            # The test.
            self.test = self.read_sparky


    def read_sparky(self, run):
        """The Sparky peak height loading test."""

        # Arguments.
        self.run = run

        # Load the original state.
        self.relax.interpreter._State.load(file='rx.save', dir=sys.path[-1] + '/test_suite/data/curve_fitting')

        # Create the run.
        self.relax.generic.runs.create(self.run, "mf")

        # Load the Lupin Ap4Aase sequence.
        self.relax.interpreter._Sequence.read(self.run, file="Ap4Aase.seq", dir=sys.path[-1] + "/test_suite/data")

        # Read the peak heights.
        self.relax.interpreter._Relax_fit.read(self.run, file="T2_ncyc1_ave.list", dir=sys.path[-1] + "/test_suite/data/curve_fitting", relax_time=0.0176)


        # Test the integrity of the data.
        #################################

        # Print out.
        print "\nTesting the integrity of the loaded data.\n"

        # Loop over the residues of the original data.
        for i in xrange(len(self.relax.data.res['rx'])):
            # Aliases
            orig_data = self.relax.data.res['rx'][i]
            new_data = self.relax.data.res[self.run][i]

            # Residue alias.
            self.orig_res = `orig_data.num` + orig_data.name
            self.new_res = `new_data.num` + new_data.name

            # Residue numbers.
            if orig_data.num != new_data.num:
                self.print_error('residue numbers')
                return

            # Residue names.
            if orig_data.name != new_data.name:
                self.print_error('residue names')
                return

            # Skip unselected residues.
            if not orig_data.select:
                continue

            # The intensity.
            if orig_data.intensities[0][0] != new_data.intensities[0][0]:
                self.print_error('intensities')
                return

        # Success.
        print "The data structures have been created successfully."
        return 1


    def print_error(self, name):
        """Function for printing a residue mismatch."""

        print "The " + name + " of " + self.orig_res + " and " + self.new_res + " do not match."
