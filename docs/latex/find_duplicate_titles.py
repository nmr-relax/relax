#! /usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2015 Edward d'Auvergne                                        #
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
# along with relax; if not, write to the Free Software                        #
#                                                                             #
###############################################################################

# Python module imports.
from os import getcwd, path, walk
from re import search
import sys


# The data structure for holding the unique title names.
titles = []

# The duplicate count structure.
duplicate = {}

# Walk through the directories.
for root, dirs, files in walk(getcwd()):
    # Loop over the files in the current directory.
    for file_name in files:
        # Skip non-LaTeX files.
        if not search("tex$", file_name):
            continue

        # The full path.
        file_path = path.join(root, file_name)

        # Read the contents of the file.
        file = open(file_path)
        lines = file.readlines()
        file.close()

        # Loop over the file contents.
        for line in lines:
            # Skip everything that is not a chapter or section.
            if not (search("\\\\chapter{", line) or search("\\\\section{", line) or search("\\\\subsection{", line)):
                continue

            # Strip off the newline character.
            line = line.replace('\n', '')

            # Strip off any label.
            if search(' \\\\label', line):
                line = line[:line.index(' \label')]

            # Extract the title string by finding the first '{' and chop off the final '}'.
            title = line[line.index('{')+1:-1]

            # Is the title new?
            if not title in titles:
                titles.append(title)

            # Replicate!
            else:
                # No duplicates yet, so 2 identical titles exist.
                if not title in duplicate:
                    duplicate[title] = 2

                # At least two identical titles exist, so increment the counter.
                else:
                    duplicate[title] += 1

# Final printout.
if len(duplicate):
    # The duplicate titles.
    print("%-80s %-10s" % ("Title", "Count"))
    for title in duplicate:
        print("%-80s %10i" % (title, duplicate[title]))

    # Return a failed exit status.
    sys.exit(1)

# No duplicates.
sys.exit(0)
