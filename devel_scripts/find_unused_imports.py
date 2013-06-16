#! /usr/bin/env python

"""Find all unused imports within all relax *.py files using the pylint program."""

# Python module imports.
from os import getcwd, path, waitpid, sep, walk
from re import search
from subprocess import PIPE, Popen


# Walk through the current dir.
for root, dirs, files in walk(getcwd()):
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
        pipe = Popen(cmd, shell=True, stdout=PIPE, close_fds=False)
        waitpid(pipe.pid, 0)

        # The STDOUT data.
        data = pipe.stdout.readlines()

        # Only display the import information.
        for line in data:
            if search("Unused import", line):
                print("File:  %s;  %s" % (path, line[:-1]))
