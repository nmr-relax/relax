###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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


def heading(text):
    """Function for printing the headings.

    @param text:    The text of the heading to be printed.
    @type text:     str
    """

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


def summary_line(name, passed, width=84):
    """Print a summary line.

    @param name:    The name of the test, test category, etc.
    @type name:     str
    @param passed:  An argument which if True causes '[ OK ]' to be printed and if False causes '[ Failed ]' to be printed.
    @type passed:   bool
    @keyword width: The width of the line, excluding the terminal '[ OK ]' or '[ Failed ]'.
    @type width:    int
    """

    # Name.
    sys.stdout.write(name + " ")

    # Dots.
    for j in xrange(width - len(name)):
        sys.stdout.write(".")

    # Passed.
    if passed:
        sys.stdout.write(" %-10s\n" % "[ OK ]")

    # Failed.
    else:
        sys.stdout.write(" %-10s\n" % "[ Failed ]")
