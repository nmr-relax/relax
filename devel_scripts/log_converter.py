#! /usr/bin/python

"""Convert SVN logs into the format for the "Full list of changes" component of the release message."""

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
    sys.stderr.write(`sys.argv[1]` + " is not accessible as a file.\n")
    sys.exit()

# Open the file, read the lines, then close it.
file = open(sys.argv[1], 'r')
lines = file.readlines()
file.close()

# Loop over the lines, determining what to do next.
msg = ''
for line in lines:
    # The separator, so reinitialise everything.
    if search('^-----', line):
        # First, print the old message, removing trailing whitespace.
        print("        * " + msg.rstrip())

        # Reinitialise.
        msg = ''

        # Go to the next line.
        continue

    # The header line.
    if search('^r[1-9][0-9]', line):
        continue

    # The 'Changed paths' line.
    if search('^Changed paths:', line):
        continue

    # Files and svn message.
    if search('^  ', line):
        continue

    # Svnmerge sep.
    if search('^\.\.\.\.', line):
        continue

    # Whitespace.
    if len(msg):
        if search('\.$', msg[-1]):
            msg += '  '
        else:
            msg += ' '

    # Add the line (without the newline char).
    msg += line[:-1]
