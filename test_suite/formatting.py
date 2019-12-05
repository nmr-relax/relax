###############################################################################
#                                                                             #
# Copyright (C) 2007,2011-2012,2019 Edward d'Auvergne                         #
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
import sys
from textwrap import wrap


def divider(char, width=100):
    """Write out a divider of the given width.

    @param char:    The character to use for the divider.
    @type char:     str
    @keyword width: The number of characters to use.
    @type width:    int
    """

    # Write out the divider.
    sys.stdout.write(char*width)
    sys.stdout.write("\n")


def format_test_name(test_name, category=None):
    """Generate the compact string representation of the test name.

    @param test_name:   The original TestCase name.
    @type test_name:    str
    @keyword category:  The test category, one of 'system', 'unit', 'gui', or 'verification'.
    @type category:     str
    """

    # Change the test name for all but unit tests.
    if category != 'unit':
        test_name = test_name.split('.')
        test_name = "%s.%s" % (test_name[-2], test_name[-1])

    # Handle errors.
    elif search('Error', test_name):
        pass

    # Modify the unit test name.
    else:
        # Strip out the leading 'test_suite.unit_tests.' text.
        test_name = test_name.replace('test_suite.unit_tests.', '')

        # Split out the module name from the test name.
        module_name, test_name = split('.Test_', test_name)

        # Rebuild the test name.
        test_name = "module %s, test Test_%s" % (module_name, test_name)

    # Return the test name.
    return test_name


def subtitle(text):
    """Function for printing the subtitles.

    @param text:    The text of the subtitle to be printed.
    @type text:     str
    """

    # The width of the subtitle string.
    width = len(text) + 2

    # Text.
    sys.stdout.write("# %s\n" % text)

    # Bottom bar.
    sys.stdout.write("#" * width)

    # Spacing.
    sys.stdout.write("\n\n")


def summary_line(name, passed, width=100):
    """Print a summary line.

    @param name:    The name of the test, test category, etc.
    @type name:     str
    @param passed:  An argument which if True causes '[ OK ]' to be printed and if False causes '[ Failed ]' to be printed.  The special string 'skip' is used to indicate that this has been skipped.
    @type passed:   bool or str
    @keyword width: The width of the line, excluding the terminal '[ OK ]' or '[ Failed ]'.
    @type width:    int
    """

    # Passed.
    if passed == True:
        state = "OK"

    # Skipped.
    elif passed == 'skip':
        state = "Skipped"

    # Failed.
    else:
        state = "Failed"

    # Dots.
    dots = ''
    for j in range(width - len(name) - len(state) - 6):
        dots += '.'

    # Write out the line.
    sys.stdout.write("%s %s [ %s ]\n" % (name, dots, state))


def test_title(name, desc=None, width=100):
    """Format and write out a title for the test.

    @param name:    The name of the test.
    @type name:     str
    @keyword desc:  An optional description for the test.
    @type desc:     str
    @keyword width: The console width.
    @type width:    int
    """

    # Output the title.
    divider('=', width=width)
    sys.stdout.write("Starting test: %s\n" % name)
    if desc:
        sys.stdout.write("\n")
        for line in wrap(desc, width):
            sys.stdout.write("%s\n" % line)
    divider('-', width=width)


def title(text):
    """Function for printing the titles.

    @param text:    The text of the title to be printed.
    @type text:     str
    """

    # The width of the title string.
    width = len(text) + 4

    # Top spacing.
    sys.stdout.write("\n\n\n\n")

    # Top bar.
    sys.stdout.write("#" * width)
    sys.stdout.write("\n")

    # Text.
    sys.stdout.write("# %s #\n" % text)

    # Bottom bar.
    sys.stdout.write("#" * width)

    # Spacing.
    sys.stdout.write("\n\n\n")
