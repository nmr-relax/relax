# Script for testing optimisation for software version and architecture differences.

# Python module imports.
from re import search
from string import split
import sys

# relax module imports.
from test_suite.system_tests import model_free

# The testing class.
mf = model_free.Mf('run')

# Execute the tests, storing the messages.
tests = []
messages = []
for name in dir(mf):
    # Skip all non-opt tests.
    if not search('test_opt', name):
        continue

    # Print out.
    sys.stderr.write("Test: %s\n" % name)

    # Set up.
    mf.setUp()

    # Run the test.
    test = getattr(mf, name)
    test()

    # Alias the relevent spin container.
    spin = cdp.mol[0].res[1].spin[0]

    # Get the message.
    tests.append(name)
    messages.append(split(mf.mesg_opt_debug(spin), '\n'))

    # Tear down.
    mf.tearDown()

# Write the messages to STDERR.
for i in range(len(messages)):
    # Header.
    sys.stderr.write("\n\n\n\nTest: %s\n" % tests[i])

    # The message lines.
    for j in range(len(messages[i])):
        # Clean up.
        if j < 2 or j == len(messages[i]) - 1:
            continue

        # Write the line.
        sys.stderr.write("        # %s\n" % messages[i][j])
sys.stderr.write("\n\n")
