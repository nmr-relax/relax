###############################################################################
#                                                                             #
# Copyright (C) 2006-2007 Edward d'Auvergne                                   #
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

# Import statements.
import traceback
import sys

# Formatting.
from test_suite.formatting import *

# Import the tests.
from generic import Generic
from jw_mapping import Jw
from model_selection import Modsel
from relax_fit import Relax_fit
from sequence import Sequence


class System_tests:
    """The system/functional tests component of the relax test suite."""

    def __init__(self, relax):
        """The relax system/functional tests.

        This class runs a number of tests to determine if any changes to relax have caused
        breakages.
        """

        self.relax = relax


    def run(self):
        """Method for the execution of all system/functional tests."""

        # Introduction.
        ###############

        # Heading.
        heading("The relax test suite")


        # Sequence tests.
        #################

        # Heading.
        heading("The sequence tests")

        # Initialise the array containing each test element.
        self.seq_test_array = []

        # User function sequence.read() test.
        self.seq_test_array.append(Sequence(self.relax, 'read'))

        # Loading the sequence from a PDB file.
        self.seq_test_array.append(Sequence(self.relax, 'pdb'))

        # Execute the tests.
        self.exec_tests(self.seq_test_array)


        # Relaxation curve-fitting tests.
        #################################

        # Heading.
        heading("The relaxation curve-fitting tests")

        # Initialise the array containing each test element.
        self.relax_fit_test_array = []

        # Loading Sparky peak heights.
        self.relax_fit_test_array.append(Relax_fit(self.relax, 'read_sparky'))

        # Execute the tests.
        self.exec_tests(self.relax_fit_test_array)


        # Reduced spectral density mapping tests.
        #########################################

        # Heading.
        heading("The reduced spectral density mapping tests")

        # Initialise the array containing each test element.
        self.jw_test_array = []

        # User function value.set() test.
        self.jw_test_array.append(Jw(self.relax, 'set'))
        self.jw_test_array.append(Jw(self.relax, 'calc'))

        # Execute the tests.
        self.exec_tests(self.jw_test_array)


        # Model selection tests.
        ########################

        # Heading.
        heading("The model selection tests")

        # Initialise the array containing each test element.
        self.modsel_test_array = []

        # The tests.
        self.modsel_test_array.append(Modsel(self.relax, 'diff tensor'))

        # Execute the tests.
        self.exec_tests(self.modsel_test_array)


        # Generic tests.
        ################

        # Heading.
        heading("The generic tests")

        # Initialise the array containing each test element.
        self.generic_test_array = []

        # The tests.
        self.generic_test_array.append(Generic(self.relax, 'value_diff'))

        # Execute the tests.
        self.exec_tests(self.generic_test_array)


        # Fin.
        ######

        global_pass = self.summary()
        return global_pass


    def exec_tests(self, test_array):
        """Function for running the tests."""

        # Loop over the tests.
        for i in xrange(len(test_array)):
            # Print out.
            string = "# Executing the test of " + test_array[i].name + '.'
            sys.stdout.write(string + '\n')
            for j in range(len(string)):
                sys.stdout.write('#')
            sys.stdout.write("\n\n")

            # Reset relax.
            self.relax.interpreter._Reset.reset()

            # The data pipe name, used by many tests.
            self.pipe = 'test'

            # Flag indicating whether the test passed or failed.
            test_array[i].passed = 0

            # Execute the test.
            try:
                test_array[i].passed = test_array[i].test(self.pipe)

            # The test failed.
            except:
                traceback.print_exc()

            # Print out.
            sys.stdout.write("\n\n\n\n\n\n\n")

            # Debugging.
            if not test_array[i].passed and self.relax.Debug:
                sys.exit()


    def summary(self):
        """Function for printing out a summary of all tests."""

        # Heading.
        sys.stdout.write("\n\n\n")
        heading("Results of the test suite")

        # Synopsis.
        global_pass = 1


        # Sequence tests.
        #################

        # Heading.
        sys.stdout.write("\nThe sequence tests:\n")

        # Loop over the tests.
        for test in self.seq_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            summary_line(test.name, test.passed)


        # Relaxation curve-fitting tests.
        #################################

        # Heading.
        sys.stdout.write("\nThe relaxation curve-fitting tests:\n")

        # Loop over the tests.
        for test in self.relax_fit_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            summary_line(test.name, test.passed)


        # Reduced spectral density Mapping tests.
        #########################################

        # Heading.
        sys.stdout.write("\nThe reduced spectral density tests:\n")

        # Loop over the tests.
        for test in self.jw_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            summary_line(test.name, test.passed)


        # Model selection tests.
        ########################

        # Heading.
        sys.stdout.write("\nThe model selection tests:\n")

        # Loop over the tests.
        for test in self.modsel_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            summary_line(test.name, test.passed)


        # Generic tests.
        ################

        # Heading.
        sys.stdout.write("\nThe generic tests:\n")

        # Loop over the tests.
        for test in self.generic_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            summary_line(test.name, test.passed)


        # Synposis.
        ###########

        # Global pass print out.
        sys.stdout.write("\n\n\nSynopsis ")

        # Dots.
        for j in xrange(88 - len("Synopsis")):
            sys.stdout.write(".")

        # Global pass.
        if global_pass:
            sys.stdout.write(" %-10s\n" % "[ OK ]")

        # Global fail.
        else:
            sys.stdout.write(" %-10s\n" % "[ Failed ]")
        sys.stdout.write("\n\n")


        # Return the global_pass value.
        return global_pass
