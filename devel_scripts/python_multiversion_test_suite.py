#! /usr/bin/env python

"""Script for blasting the relax test-suite through all possible Python versions.

This assumes that there is a directory called 'bin' in your home directory containing the Python versions to be tested.  This must be executed from the base relax directory.
"""

# Python module imports.
from os import system
from subprocess import PIPE, Popen
import sys


def execute_sh(cmd, log=sys.stdout, err=sys.stderr):
    """Execute the shell command, sending the output to the given log and error files.

    @param cmd:     The shell command to execute.
    @type cmd:      str
    @keyword log:   The name of the log file to redirect output to.
    @type log:      file object
    @keyword err:   The name of the error file to redirect output to.
    @type err:      file object
    """

    # Execute the command.
    pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

    # Redirect STDOUT to the log file.
    for line in pipe.stdout.readlines():
        log.write(line)

    # Redirect STDERR to the error file.
    for line in pipe.stderr.readlines():
        err.write(line)

    # Flush.
    log.flush()
    err.flush()


# The Python versions to be tested.
PY_VER = [
    '1.0',
    '1.5',
    '1.6',
    '2.0',
    '2.1',
    '2.2',
    '2.3',
    '2.4',
    '2.5',
    '2.6',
    '2.7',
    '3.0',
    '3.1',
    '3.2',
    '3.3'
]

# The log file.
LOG = open('python_multiversion_test_suite.log', 'w')
ERR = open('python_multiversion_test_suite.err', 'w')

# Loop over the versions.
for version in PY_VER:
    # A header.
    header = "\n\n\n\n\n"
    header += "##################\n"
    header += "### Python %s ###\n" % version
    header += "##################\n\n\n\n"
    LOG.write(header)
    ERR.write(header)

    # Clean up.
    execute_sh('scons clean_all', log=ERR, err=ERR)

    # Build the C modules for the current Python version.
    execute_sh('devel_scripts/manual_c_module.py %s' % (version), log=LOG, err=LOG)

    # Run the test suite.
    execute_sh('~/bin/python%s relax -x' % (version), log=LOG, err=LOG)
