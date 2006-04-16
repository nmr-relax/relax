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


class Mf:
    def __init__(self, relax, test_name):
        """Class for testing various aspects specific to model-free analysis."""

        self.relax = relax

        # Relaxation data reading test.
        if test_name == 'read relaxation data':
            # The name of the test.
            self.name = "The user function relax_data.read()"

            # The test.
            self.test = self.read_relax_data

        # Results reading test.
        if test_name == 'read results':
            # The name of the test.
            self.name = "the user function results.read()"

            # The test.
            self.test = self.read_results


    def read_relax_data(self, run):
        """The relaxation data reading test."""

        # Arguments.
        self.run = run

        # Create the run.
        self.relax.generic.runs.create(self.run, 'mf')

        # Path of the files.
        path = sys.path[-1] + '/test_suite/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read(self.run, file='noe.500.out', dir=path)

        # Read the relaxation data.
        self.relax.interpreter._Relax_data.read(self.run, 'R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)

        # Test the data.
        if self.relax.data.res[self.run][0].relax_data[0] != 1.3874977659397683:
            print "The relaxation data does not match."
            return

        # Test the error.
        if self.relax.data.res[self.run][0].relax_error[0] != 0.027749955318795365:
            print "The relaxation error does not match."
            return

        return 1


    def read_results(self, run):
        """The results reading test."""

        # Arguments.
        self.run = run

        # Load the original state.
        self.relax.interpreter._State.load(file='orig_state', dir=sys.path[-1] + '/test_suite/data/model_free')

        # Create the run.
        self.relax.generic.runs.create(self.run, 'mf')

        # Read the results.
        self.relax.interpreter._Results.read(self.run, dir=sys.path[-1] + '/test_suite/data/model_free')

        # Print out.
        print "\nTesting the integrity of the loaded data.\n"

        # Diffusion tensor type.
        if self.relax.data.diff['orig'].type != self.relax.data.diff[self.run].type:
            print "The diffusion tensor types do not match."
            return

        # tm.
        if self.relax.data.diff['orig'].tm != self.relax.data.diff[self.run].tm:
            print "The tm values do not match."
            return

        # Loop over the residues of the original data.
        for i in xrange(len(self.relax.data.res['orig'])):
            # Aliases
            orig_data = self.relax.data.res['orig'][i]
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

            # Selection.
            if orig_data.select != new_data.select:
                self.print_error('selection flags')
                return

            # Skip unselected residues.
            if not orig_data.select:
                continue

            # Model-free model test.
            if orig_data.model != new_data.model:
                self.print_error('model-free models')
                return

            # Model-free parameter set test.
            if orig_data.params != new_data.params:
                self.print_error('model-free parameter sets')
                return

            # S2 test.
            if orig_data.s2 != new_data.s2:
                self.print_error('S2 values')
                return

            # S2f test.
            if orig_data.s2f != new_data.s2f:
                self.print_error('S2f values')
                return

            # S2s test.
            if orig_data.s2s != new_data.s2s:
                self.print_error('S2s values')
                return

            # local tm test.
            if orig_data.tm != new_data.tm:
                self.print_error('local tm values')
                return

            # te test.
            if orig_data.te != new_data.te:
                self.print_error('te values')
                return

            # tf test.
            if orig_data.tf != new_data.tf:
                self.print_error('tf values')
                return

            # ts test.
            if orig_data.ts != new_data.ts:
                self.print_error('ts values')
                return

            # Rex test.
            if orig_data.rex != new_data.rex:
                self.print_error('Rex values')
                return

            # bond length test.
            if orig_data.r != new_data.r:
                self.print_error('bond length values')
                return

            # CSA test.
            if orig_data.csa != new_data.csa:
                self.print_error('CSA values')
                return

            # Chi-squared test.
            if orig_data.chi2 != new_data.chi2:
                self.print_error('Chi-squared values')
                return

            # Iteration number test.
            if orig_data.iter != new_data.iter:
                self.print_error('iteration numbers')
                return

            # Function count test.
            if orig_data.f_count != new_data.f_count:
                self.print_error('function counts')
                return

            # Gradient count test.
            if orig_data.g_count != new_data.g_count:
                self.print_error('gradient counts')
                return

            # Hessian count test.
            if orig_data.h_count != new_data.h_count:
                self.print_error('Hessian counts')
                return

            # Warning test.
            if orig_data.warning != new_data.warning:
                self.print_error('warnings')
                return

            # Relaxation data lables test.
            if orig_data.ri_labels != new_data.ri_labels:
                self.print_error('relaxation data labels')
                return

            # Relaxation data remap table test.
            if orig_data.remap_table != new_data.remap_table:
                self.print_error('relaxation data remap tables')
                return

            # Frequency lables test.
            if orig_data.frq_labels != new_data.frq_labels:
                self.print_error('frequency labels')
                return

            # Relaxation data test.
            if orig_data.relax_data != new_data.relax_data:
                self.print_error('relaxation data')
                return

            # Relaxation data error test.
            if orig_data.relax_error != new_data.relax_error:
                self.print_error('relaxation data errors')
                return

        # Success.
        print "The data structures have been created successfully."
        return 1


    def print_error(self, name):
        """Function for printing a residue mismatch."""

        print "The " + name + " of " + self.orig_res + " and " + self.new_res + " do not match."
