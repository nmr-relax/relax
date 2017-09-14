###############################################################################
#                                                                             #
# Copyright (C) 2017 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Python module imports.
from unittest import TestCase

# relax module imports.
import lib.timing


class Test_timing(TestCase):
    """Unit tests for the functions of the 'lib.timing' module."""

    def test_print_elapsed_time_seconds(self):
        """Test the proper behaviour of the lib.timing.print_elapsed_time() function with only seconds."""

        # Test a single value.
        self.assertEqual("Elapsed time:  5.556 seconds\n", lib.timing.print_elapsed_time(5.555555, return_str=True))


    def test_print_elapsed_time_minute(self):
        """Test the proper behaviour of the lib.timing.print_elapsed_time() function with minutes."""

        # Test a single value.
        self.assertEqual("Elapsed time:  1 minute and 5.556 seconds\n", lib.timing.print_elapsed_time(65.555555, return_str=True))


    def test_print_elapsed_time_minutes(self):
        """Test the proper behaviour of the lib.timing.print_elapsed_time() function with minutes."""

        # Test a single value.
        self.assertEqual("Elapsed time:  2 minutes and 5.556 seconds\n", lib.timing.print_elapsed_time(125.555555, return_str=True))


    def test_print_elapsed_time_hour(self):
        """Test the proper behaviour of the lib.timing.print_elapsed_time() function with minutes."""

        # Test a single value.
        self.assertEqual("Elapsed time:  1 hour, 1 minute and 5.556 seconds\n", lib.timing.print_elapsed_time(3665.555555, return_str=True))


    def test_print_elapsed_time_hours(self):
        """Test the proper behaviour of the lib.timing.print_elapsed_time() function with minutes."""

        # Test a single value.
        self.assertEqual("Elapsed time:  2 hours, 1 minute and 5.556 seconds\n", lib.timing.print_elapsed_time(7265.555555, return_str=True))


    def test_print_elapsed_time_day(self):
        """Test the proper behaviour of the lib.timing.print_elapsed_time() function with minutes."""

        # Test a single value.
        self.assertEqual("Elapsed time:  1 day, 2 hours, 2 minutes and 5.556 seconds\n", lib.timing.print_elapsed_time(93725.555555, return_str=True))


    def test_print_elapsed_time_days(self):
        """Test the proper behaviour of the lib.timing.print_elapsed_time() function with minutes."""

        # Test a single value.
        self.assertEqual("Elapsed time:  2 days, 2 hours, 2 minutes and 5.556 seconds\n", lib.timing.print_elapsed_time(180125.555555, return_str=True))
