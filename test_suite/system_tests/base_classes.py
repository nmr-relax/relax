###############################################################################
#                                                                             #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Base classes for the system tests."""

# Python module imports.
from shutil import rmtree
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.reset import reset
from prompt.interpreter import Interpreter
from relax_io import delete


class SystemTestCase(TestCase):
    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the TestCase __init__ method.
        super(SystemTestCase, self).__init__(methodName)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)


    def tearDown(self):
        """Default tearDown operation - delete temp directories and files and reset relax."""

        # Remove the temporary directories.
        if hasattr(ds, 'tmpdir'):
            # Delete the directory.
            rmtree(ds.tmpdir)

            # Remove the variable.
            del ds.tmpdir

        # Remove the temporary directories.
        if hasattr(self, 'tmpdir'):
            # Delete the directory.
            rmtree(self.tmpdir)

            # Remove the variable.
            del self.tmpdir

        # Remove temporary files.
        if hasattr(ds, 'tmpfile'):
            # Delete the file.
            delete(ds.tmpfile, fail=False)

            # Remove the variable.
            del ds.tmpfile

        # Remove temporary files.
        if hasattr(self, 'tmpfile'):
            # Delete the file.
            delete(self.tmpfile, fail=False)

            # Remove the variable.
            del self.tmpfile

        # Reset relax.
        reset()
