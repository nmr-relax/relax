################################################################################
#                                                                              #
# Copyright (C) 2011 Edward d'Auvergne                                         #
#                                                                              #
# This file is part of the program relax.                                      #
#                                                                              #
# relax is free software; you can redistribute it and/or modify                #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation; either version 3 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# relax is distributed in the hope that it will be useful,                     #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with relax; if not, write to the Free Software                         #
#                                                                              #
################################################################################

# Module docstring.
"""Replacement unittest.TestLoader class.

This is to handle skipping of tests when Python modules are not installed.
"""

# Python module imports
from unittest import TestLoader, TestSuite

# relax module imports.
from status import Status; status = Status()


class RelaxTestLoader(TestLoader):
    """Replacement TestLoader class."""

    def loadTestsFromTestCase(self, testCaseClass):
        """Replacement method for skipping tests."""

        # A check from the original function.
        if issubclass(testCaseClass, TestSuite):
            raise TypeError("Test cases should not be derived from TestSuite. Maybe you meant to derive from TestCase?")

        # Get the test names.
        testCaseNames = self.getTestCaseNames(testCaseClass)

        # Again from the original function.
        if not testCaseNames and hasattr(testCaseClass, 'runTest'):
            testCaseNames = ['runTest']

        # Generate a list of test cases.
        case_list = []
        for i in range(len(testCaseNames)):
            # Initialise the test case.
            test_case = testCaseClass(testCaseNames[i])

            # Skip.
            if status.skipped_tests and testCaseNames[i] in zip(*status.skipped_tests)[0]:
                continue

            # Append the test case.
            case_list.append(test_case)

        # Return the test suite.
        return self.suiteClass(case_list)


