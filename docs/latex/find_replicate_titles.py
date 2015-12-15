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


class Replicated_titles:
    """Class used to find replicated titles in the LaTeX sources."""

    def __init__(self):
        """Set up the required data structures."""

        # The data structure for holding the unique title names.
        self.titles = []

        # The replicate count structure.
        self.replicate = {}


    def find(self):
        """Find the replicates."""

        # Reset the data structures if necessary.
        if len(self.titles):
            self.titles = []
            self.replicate = {}

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
                    if not (search("\\\\chapter", line) or search("\\\\section", line) or search("\\\\subsection", line)):
                        continue

                    # Strip off the newline character.
                    line = line.replace('\n', '')

                    # Strip off any label.
                    if search(' \\\\label', line):
                        line = line[:line.index(' \label')]

                    # Extract the short title string, if it exists.
                    if '[' in line:
                        title = line[line.index('[')+1:line.index(']')]

                    # Extract the full title string by finding the first '{' and chop off the final '}'.
                    else:
                        title = line[line.index('{')+1:-1]

                    # Is the title new?
                    if not title in self.titles:
                        self.titles.append(title)

                    # Replicate!
                    else:
                        # No replicates yet, so 2 identical titles exist.
                        if not title in self.replicate:
                            self.replicate[title] = 2

                        # At least two identical titles exist, so increment the counter.
                        else:
                            self.replicate[title] += 1

        # Final printout.
        if len(self.replicate):
            # The replicate titles.
            print("%-80s %-10s" % ("Title", "Count"))
            for title in self.replicate:
                print("%-80s %10i" % (title, self.replicate[title]))

            # Return a status that replicates have been found.
            return True

        # No replicates.
        return False



if __name__ == "__main__":
    repli = Replicated_titles()
    if repli.find():
        sys.exit(1)
    else:
        sys.exit(0)
