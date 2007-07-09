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

# Import statements.
import traceback
import sys


# Import the tests.
from angles import Angles
from consistency_tests import Consistent
from diffusion_tensor import Diffusion_tensor
from generic import Generic
from jw_mapping import Jw
from model_free import Mf
from model_selection import Modsel
from relax_fit import Relax_fit
from run_create import Run_create
from sequence import Sequence


class Test_suite:
    def __init__(self, relax):
        """The relax test suite.

        This class runs a number of tests to determine if any changes to relax have caused
        breakages.
        """

        self.relax = relax


        # Introduction.
        ###############

        # Heading.
        self.heading("The relax test suite")


        # Run tests.
        ############

        # Heading.
        self.heading("The run tests")

        # Initialise the array containing each test element.
        self.run_test_array = []

        # User function run.create() test.
        self.run_test_array.append(Run_create(self.relax))

        # Execute the tests.
        self.exec_tests(self.run_test_array)


        # Sequence tests.
        #################

        # Heading.
        self.heading("The sequence tests")

        # Initialise the array containing each test element.
        self.seq_test_array = []

        # User function sequence.read() test.
        self.seq_test_array.append(Sequence(self.relax, 'read'))

        # Loading the sequence from a PDB file.
        self.seq_test_array.append(Sequence(self.relax, 'pdb'))

        # Execute the tests.
        self.exec_tests(self.seq_test_array)


        # Diffusion tensor tests.
        #########################

        # Heading.
        self.heading("The diffusion tensor tests")

        # Initialise the array containing each test element.
        self.diff_tensor_test_array = []

        # User function tests.
        self.diff_tensor_test_array.append(Diffusion_tensor(self.relax, 'init'))
        self.diff_tensor_test_array.append(Diffusion_tensor(self.relax, 'delete'))
        self.diff_tensor_test_array.append(Diffusion_tensor(self.relax, 'display'))
        self.diff_tensor_test_array.append(Diffusion_tensor(self.relax, 'copy'))

        # Execute the tests.
        self.exec_tests(self.diff_tensor_test_array)


        # Angle calculation tests.
        ##########################

        # Heading.
        self.heading("Angle calculation tests")

        # Initialise the array containing each test element.
        self.angles_test_array = []

        # User function tests.
        self.angles_test_array.append(Angles(self.relax))

        # Execute the tests.
        self.exec_tests(self.angles_test_array)


        # Relaxation curve-fitting tests.
        #################################

        # Heading.
        self.heading("The relaxation curve-fitting tests")

        # Initialise the array containing each test element.
        self.relax_fit_test_array = []

        # Loading Sparky peak heights.
        self.relax_fit_test_array.append(Relax_fit(self.relax, 'read_sparky'))

        # Execute the tests.
        self.exec_tests(self.relax_fit_test_array)


        # Model-free tests.
        ###################

        # Heading.
        self.heading("The model-free tests")

        # Initialise the array containing each test element.
        self.mf_test_array = []

        # User function results.read() test.
        self.mf_test_array.append(Mf(self.relax, 'read relaxation data'))
        self.mf_test_array.append(Mf(self.relax, 'set csa'))
        self.mf_test_array.append(Mf(self.relax, 'set bond length'))
        self.mf_test_array.append(Mf(self.relax, 'set csa and bond length'))
        self.mf_test_array.append(Mf(self.relax, 'select m4'))
        self.mf_test_array.append(Mf(self.relax, 'create m4'))
        self.mf_test_array.append(Mf(self.relax, 'read results'))
        self.mf_test_array.append(Mf(self.relax, 'opendx {S2, te, Rex} map'))
        self.mf_test_array.append(Mf(self.relax, 'opendx {theta, phi, Da} map'))
        self.mf_test_array.append(Mf(self.relax, 'opendx {local_tm, S2, te} map'))
        self.mf_test_array.append(Mf(self.relax, 'Constrained grid search {S2=0.970, te=2048, Rex=0.149}'))
        self.mf_test_array.append(Mf(self.relax, 'Constrained SD, backtracking opt {S2=0.970, te=2048, Rex=0.149}'))
        self.mf_test_array.append(Mf(self.relax, 'Constrained SD, MT opt {S2=0.970, te=2048, Rex=0.149}'))
        self.mf_test_array.append(Mf(self.relax, 'Constrained CD, backtracking opt {S2=0.970, te=2048, Rex=0.149}'))
        self.mf_test_array.append(Mf(self.relax, 'Constrained CD, MT opt {S2=0.970, te=2048, Rex=0.149}'))
        self.mf_test_array.append(Mf(self.relax, 'Constrained BFGS, backtracking opt {S2=0.970, te=2048, Rex=0.149}'))
        self.mf_test_array.append(Mf(self.relax, 'Constrained BFGS, backtracking opt {S2=0.970, te=2048, Rex=0.149}'))
        self.mf_test_array.append(Mf(self.relax, 'Constrained Newton, GMW, backtracking opt {S2=0.970, te=2048, Rex=0.149}'))
        self.mf_test_array.append(Mf(self.relax, 'Constrained Newton, GMW, MT opt {S2=0.970, te=2048, Rex=0.149}'))

        # Execute the tests.
        self.exec_tests(self.mf_test_array)


        # Reduced spectral density mapping tests.
        #########################################

        # Heading.
        self.heading("The reduced spectral density mapping tests")

        # Initialise the array containing each test element.
        self.jw_test_array = []

        # User function value.set() test.
        self.jw_test_array.append(Jw(self.relax, 'set'))
        self.jw_test_array.append(Jw(self.relax, 'calc'))

        # Execute the tests.
        self.exec_tests(self.jw_test_array)


        # Consistency tests tests.
        ##########################

        # Heading
        self.heading("The consistency tests tests")

        # Initialise the array containing each test element.
        self.consistent_test_array = []

        # User function value.set() test.
        self.consistent_test_array.append(Consistent(self.relax, 'set'))
        self.consistent_test_array.append(Consistent(self.relax, 'calc'))

        # Execute the tests.
        self.exec_tests(self.consistent_test_array)


        # Model selection tests.
        ########################

        # Heading.
        self.heading("The model selection tests")

        # Initialise the array containing each test element.
        self.modsel_test_array = []

        # The tests.
        self.modsel_test_array.append(Modsel(self.relax, 'diff tensor'))

        # Execute the tests.
        self.exec_tests(self.modsel_test_array)


        # Generic tests.
        ################

        # Heading.
        self.heading("The generic tests")

        # Initialise the array containing each test element.
        self.generic_test_array = []

        # The tests.
        self.generic_test_array.append(Generic(self.relax, 'value_diff'))

        # Execute the tests.
        self.exec_tests(self.generic_test_array)


        # Summary.
        ##########

        self.summary()



    def heading(self, text):
        """Function for printing the headings."""

        # Spacing.
        sys.stdout.write("\n\n\n\n")

        # Top bar.
        for i in xrange(len(text) + 4):
            sys.stdout.write("#")
        sys.stdout.write("\n")

        # Text.
        sys.stdout.write("# " + text + " #\n")

        # Bottom bar.
        for i in xrange(len(text) + 4):
            sys.stdout.write("#")
        sys.stdout.write("\n\n\n")


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

            # Reinitialise all data.
            self.relax.interpreter._Init_data.init()

            # The run name.
            self.run = 'test'

            # Flag indicating whether the test passed or failed.
            test_array[i].passed = 0

            # Execute the test.
            try:
                test_array[i].passed = test_array[i].test(self.run)

            # The test failed.
            except:
                traceback.print_exc()

            # Print out.
            sys.stdout.write("\n\n\n\n\n\n\n")

            # Debugging.
            if not test_array[i].passed and Debug:
                sys.exit()


    def summary(self):
        """Function for printing out a summary of all tests."""

        # Heading.
        sys.stdout.write("\n\n\n")
        self.heading("Results of the test suite")

        # Synopsis.
        global_pass = 1


        # Run tests.
        ############

        # Heading.
        sys.stdout.write("\nThe run tests:\n")

        # Loop over the tests.
        for test in self.run_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            self.summary_line(test)


        # Sequence tests.
        #################

        # Heading.
        sys.stdout.write("\nThe sequence tests:\n")

        # Loop over the tests.
        for test in self.seq_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            self.summary_line(test)


        # Diffusion tensor tests.
        #########################

        # Heading.
        sys.stdout.write("\nThe diffusion tensor tests:\n")

        # Loop over the tests.
        for test in self.diff_tensor_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            self.summary_line(test)


        # Angle calculation tests.
        ##########################

        # Heading.
        sys.stdout.write("\nAngle calculation tests:\n")

        # Loop over the tests.
        for test in self.angles_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            self.summary_line(test)


        # Relaxation curve-fitting tests.
        #################################

        # Heading.
        sys.stdout.write("\nThe relaxation curve-fitting tests:\n")

        # Loop over the tests.
        for test in self.relax_fit_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            self.summary_line(test)


        # Model-free tests.
        ###################

        # Heading.
        sys.stdout.write("\nThe model-free tests:\n")

        # Loop over the tests.
        for test in self.mf_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            self.summary_line(test)


        # Reduced spectral density Mapping tests.
        #########################################

        # Heading.
        sys.stdout.write("\nThe reduced spectral density tests:\n")

        # Loop over the tests.
        for test in self.jw_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            self.summary_line(test)


        # Consistentcy tests test.
        ##########################

        # Heading.
        sys.stdout.write("\nThe consistency tests tests:\n")

        # Loop over the tests.
        for test in self.consistent_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            self.summary_line(test)


        # Model selection tests.
        ########################

        # Heading.
        sys.stdout.write("\nThe model selection tests:\n")

        # Loop over the tests.
        for test in self.modsel_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            self.summary_line(test)


        # Generic tests.
        ################

        # Heading.
        sys.stdout.write("\nThe generic tests:\n")

        # Loop over the tests.
        for test in self.generic_test_array:
            # Synopsis.
            global_pass = global_pass and test.passed

            # Print the summary line.
            self.summary_line(test)


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


    def summary_line(self, test):
        """Function for printing the summary lines."""

        # Name.
        sys.stdout.write("    " + test.name + " ")

        # Dots.
        for j in xrange(84 - len(test.name)):
            sys.stdout.write(".")

        # Passed.
        if test.passed:
            sys.stdout.write(" %-10s\n" % "[ OK ]")

        # Failed.
        else:
            sys.stdout.write(" %-10s\n" % "[ Failed ]")
            self.global_pass = 0
