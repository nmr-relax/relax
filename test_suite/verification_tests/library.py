###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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

# Module docstring.
"""Verification tests for the relax library."""

# Python module imports.
from os import sep
from shutil import copytree, rmtree
from subprocess import PIPE, Popen
import sys
from tempfile import mkdtemp
from unittest import TestCase

# relax module imports.
from status import Status; status = Status()
from test_suite.clean_up import deletion


class Library(TestCase):
    """Test the relax library."""

    def setUp(self):
        """Set up for all of the library tests."""

        # Initialise a temporary directory.
        self.tmpdir = mkdtemp()


    def tearDown(self):
        """Clean up after the library tests."""

        # Remove the temporary directory and all its contents.
        deletion(obj=self, name='tmpdir', dir=True)


    def test_library_independence(self):
        """Throughly check the independence of the relax library by importing it from a non-relax directory.

        It will do this by copying just that package into a temporary directory, modifying the Python system path to include the directory, and then to recursively import all packages and modules.  All import failures will be reported at the end.
        """

        # Copy the entire library to the temporary directory.
        tmplib = self.tmpdir + sep + 'lib'
        copytree(status.install_path+sep+'lib', tmplib)

        # Create a Python script for testing the import independently of relax.
        script_name = self.tmpdir + sep + 'test.py'
        script = open(script_name, 'w')

        # Script contents.
        lines = [
            "",
            "# Python module imports.",
            "import pkgutil",
            "import sys",
            "",
            "# Direct copy of the Python 2.7 importlib function.",
            "def _resolve_name(name, package, level):",
            "    \"\"\"Return the absolute name of the module to be imported.\"\"\"",
            "    if not hasattr(package, 'rindex'):",
            "        raise ValueError(\"'package' not set to a string\")",
            "    dot = len(package)",
            "    for x in range(level, 1, -1):",
            "        try:",
            "            dot = package.rindex('.', 0, dot)",
            "        except ValueError:",
            "            raise ValueError(\"attempted relative import beyond top-level package\")",
            "    return \"%s.%s\" % (package[:dot], name)",
            "",
            "",
            "# Direct copy of the Python 2.7 importlib function.",
            "def import_module(name, package=None):",
            "    \"\"\"Import a module.",
            "",
            "    The 'package' argument is required when performing a relative import. It",
            "    specifies the package to use as the anchor point from which to resolve the",
            "    relative import to an absolute import.",
            "",
            "    \"\"\"",
            "    if name.startswith('.'):",
            "        if not package:",
            "            raise TypeError(\"relative imports require the 'package' argument\")",
            "        level = 0",
            "        for character in name:",
            "            if character != '.':",
            "                break",
            "            level += 1",
            "        name = _resolve_name(name[level:], package, level)",
            "    __import__(name)",
            "    return sys.modules[name]",
            "",
            "",
            "# Initialise a structure for later reporting of failed imports.",
            "failed = []",
            "",
            "# Import each part of the library.",
            "import lib",
            "for importer, name, is_pkg in pkgutil.iter_modules(lib.__path__):",
            "    # The full name.",
            "    full_name = 'lib.%s' % name",
            "",
            "    # Printout.",
            "    if is_pkg:",
            "        print(\"Package '%s'.\" % full_name)",
            "    else:",
            "        print(\"Module '%s'.\" % full_name)",
            "",
            "    # Import it.",
            "    module = None",
            "    try:",
            "        module = import_module(full_name)",
            "    except:",
            "        message = sys.exc_info()[1]",
            "        failed.append([full_name, message])",
            "",
            "    # Nothing more to do.",
            "    if not is_pkg or module is None:",
            "        continue",
            "",
            "    # First recursion.",
            "    for importer2, name2, is_pkg2 in pkgutil.iter_modules(module.__path__):",
            "        # The full name.",
            "        full_name2 = 'lib.%s.%s' % (name, name2)",
            "",
            "        # Printout.",
            "        if is_pkg2:",
            "            print(\"  Package '%s'.\" % full_name2)",
            "        else:",
            "            print(\"  Module '%s'.\" % full_name2)",
            "",
            "        # Import it.",
            "        module2 = None",
            "        try:",
            "            module2 = import_module(full_name2)",
            "        except:",
            "            message = sys.exc_info()[1]",
            "            failed.append([full_name2, message])",
            "",
            "        # Nothing more to do.",
            "        if not is_pkg2 or module2 is None:",
            "            continue",
            "",
            "        # 2nd recursion (the last for now).",
            "        for importer3, name3, is_pkg3 in pkgutil.iter_modules(module2.__path__):",
            "            # The full name.",
            "            full_name3 = 'lib.%s.%s.%s' % (name, name2, name3)",
            "",
            "            # Printout.",
            "            if is_pkg3:",
            "                print(\"    Package '%s'.\" % full_name3)",
            "                raise NameError(\"Recursion limit exceeded.\")",
            "            else:",
            "                print(\"    Module '%s'.\" % full_name3)",
            "",
            "            # Import it.",
            "            try:",
            "                module3 = import_module(full_name3)",
            "            except:",
            "                message = sys.exc_info()[1]",
            "                failed.append([full_name3, message])",
            "",
            "# Printout of all import failures.",
            "if len(failed):",
            "    sys.stderr.write('\\n\\nImport failures:\\n')",
            "    for name, message in failed:",
            "        sys.stderr.write(\"  %s:  %s\\n\" % (name, message))",
            "    sys.stderr.write('\\n')",
        ]
        for line in lines:
            script.write(line + '\n')

        # Close the script.
        script.close()

        # Execute the script using the same Python executable as relax.
        cmd = "%s %s" % (sys.executable, script_name)
        pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

        # Close the pipe.
        pipe.stdin.close()

        # Write to stdout.
        for line in pipe.stdout.readlines():
            # Decode Python 3 byte arrays.
            if hasattr(line, 'decode'):
                line = line.decode()

            # Write.
            sys.stdout.write(line)

        # Write to stderr.
        err_lines = pipe.stderr.readlines()
        for line in err_lines:
            # Decode Python 3 byte arrays.
            if hasattr(line, 'decode'):
                line = line.decode()

            # Write.
            sys.stderr.write(line)

        # An import failure occurred, so print the error message and fail.
        if len(err_lines):
            for line in err_lines:
                print(line)
            self.fail()
