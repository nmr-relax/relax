#! /usr/bin/env python

# Python module imports.
from os import sep
from shutil import copytree, rmtree
import sys
from tempfile import mkdtemp


def test_library(tmpdir=None):
    """Test the independence of the relax library by importing it from a non-relax directory.

    @keyword tmpdir:    The name of the temporary directory to perform the testing in.
    @type tmpdir:       str
    """

    # Copy the entire library to the temporary directory.
    tmplib = tmpdir+sep+'lib'
    copytree('lib', tmplib)

    # Modify the system path.
    sys.path.append(tmpdir)

    # Import the temporary library.
    from lib import *


# Initialise a temporary directory.
tmpdir = mkdtemp()
print("Testing in the temporary directory %s." % tmpdir)

# Failsafe execution of the testing.
try:
    test_library(tmpdir)

# Delete the temporary directory.
finally:
    print("Deleting the directory %s." % tmpdir)
    rmtree(tmpdir)
