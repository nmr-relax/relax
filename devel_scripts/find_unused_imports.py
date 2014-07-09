#! /usr/bin/env python

"""Find all unused imports within all relax *.py files using the pylint program."""

# Python module imports.
from os import getcwd, path, sep, walk
from re import search
from subprocess import PIPE, Popen
import sys


# Walk through the current dir.
for root, dirs, files in walk(getcwd()):
    # Skip SVN directories.
    if search("svn", root):
        continue

    # Loop over the files.
    for file in files:
        # Only check Python files.
        if not search("\.py$", file):
            continue

        # Full path to the file.
        path = root + sep + file

        # The command.
        cmd = 'pylint %s' % path

        # Execute.
        pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

        # Close the pipe.
        pipe.stdin.close()

        # Only display the import information.
        title_flag = True
        for line in pipe.stdout.readlines():
            if search("Unused import", line):
                # First write out the file name, once.
                if title_flag:
                    sys.stdout.write("File %s :\n" % path)
                    title_flag = False

                # Then the unused import line.
                sys.stdout.write("    %s\n" % line[:-1])
