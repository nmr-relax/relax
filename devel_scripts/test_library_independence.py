#! /usr/bin/env python

"""This script will throughly check the independence of the relax library.

It will do this by copying just that package into a temporary directory, modifying the Python system path to include the directory, and then to recursively import all packages and modules.  All import failures will be reported at the end.
"""

# Python module imports.
import importlib
from os import sep
import pkgutil
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

    # Initialise a structure for later reporting of failed imports.
    failed = []

    # Import each part of the library.
    import lib
    for importer, name, is_pkg in pkgutil.iter_modules(lib.__path__):
        # The full name.
        full_name = 'lib.%s' % name

        # Printout.
        if is_pkg:
            print("Package '%s'." % full_name)
        else:
            print("Module '%s'." % full_name)

        # Import it.
        try:
            module = importlib.import_module(full_name)
        except:
            message = sys.exc_info()[1]
            failed.append([full_name, message])

        # Nothing more to do.
        if not is_pkg:
            continue

        # First recursion.
        for importer2, name2, is_pkg2 in pkgutil.iter_modules(module.__path__):
            # The full name.
            full_name2 = 'lib.%s.%s' % (name, name2)

            # Printout.
            if is_pkg2:
                print("  Package '%s'." % full_name2)
            else:
                print("  Module '%s'." % full_name2)

            # Import it.
            try:
                module2 = importlib.import_module(full_name2)
            except:
                message = sys.exc_info()[1]
                failed.append([full_name2, message])

            # Nothing more to do.
            if not is_pkg2:
                continue

            # 2nd recursion (the last for now).
            for importer3, name3, is_pkg3 in pkgutil.iter_modules(module2.__path__):
                # The full name.
                full_name3 = 'lib.%s.%s.%s' % (name, name2, name3)

                # Printout.
                if is_pkg3:
                    print("    Package '%s'." % full_name3)
                    raise NameError("Recursion limit exceeded.")
                else:
                    print("    Module '%s'." % full_name3)

                # Import it.
                try:
                    module3 = importlib.import_module(full_name3)
                except:
                    message = sys.exc_info()[1]
                    failed.append([full_name3, message])

    # Printout of all import failures.
    print('\n\nImport failures:')
    for name, message in failed:
        print("  %s:  %s" % (name, message))


# Initialise a temporary directory.
tmpdir = mkdtemp()
print("\nTesting in the temporary directory %s.\n" % tmpdir)

# Failsafe execution of the testing.
try:
    test_library(tmpdir)

# Delete the temporary directory.
finally:
    print("\n\nDeleting the directory %s.\n" % tmpdir)
    rmtree(tmpdir)
