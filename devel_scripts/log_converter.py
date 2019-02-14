#! /usr/bin/python
###############################################################################
#                                                                             #
# Copyright (C) 2012,2019 Edward d'Auvergne                                   #
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

"""Convert git logs into the format for the "Full list of changes" component of the release message."""

# Python module imports.
from os import F_OK, access
from re import search
import sys


# Test for a single argument.
if len(sys.argv) == 1:
    sys.stderr.write("A file name must be given.\n")
    sys.exit()
elif len(sys.argv) != 2:
    sys.stderr.write("Only a single argument is allowed.\n")
    sys.exit()

# Test that the argument is a file.
if not access(sys.argv[1], F_OK):
    sys.stderr.write(repr(sys.argv[1]) + " is not accessible as a file.\n")
    sys.exit()

# Open the file, read the lines, then close it.
file = open(sys.argv[1], 'r')
lines = file.readlines()
file.close()

# Loop over the lines, determining what to do next.
log = []
msg = ''
for line in lines:
    # The next commit.
    if search('^commit ', line):
        # First, store the old message, removing bracketing whitespace.
        text = msg.strip()
        if text:
            log.append(text)

        # Reinitialise.
        msg = ''

        # Go to the next line.
        continue

    # Only process commit message lines.
    if not search('^    ', line):
        continue

    # Line unwrapping whitespace.
    if len(msg) and msg[-1] != ' ':
        if msg[-1] in ['.', '!', '?']:
            msg += '  '
        else:
            msg += ' '

    # Add the line (with no bracketing whitespace).
    msg += line.strip()

# The last commit.
text = msg.strip()
if text:
    log.append(text)

# Printout.
for i in range(len(log)):
    # Add a missing final full stop.
    if log[i][-1] not in ['.', '!', '?']:
        log[i] += '.'

    # Output.
    print("        * " + log[i])
