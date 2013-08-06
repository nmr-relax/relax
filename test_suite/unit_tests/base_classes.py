###############################################################################
#                                                                             #
# Copyright (C) 2010-2013 Edward d'Auvergne                                   #
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
"""Base classes for the system tests."""

# Python module imports.
from shutil import rmtree
from time import sleep
from unittest import TestCase

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.reset import reset
from lib.io import delete


class UnitTestCase(TestCase):
    """relax test case class specific for the unit tests."""

    def tearDown(self):
        """Default tearDown operation - delete temp directories and files and reset relax."""

        # Remove the temporary directory and variable.
        if hasattr(ds, 'tmpdir'):
            rmtree(ds.tmpdir)
            del ds.tmpdir

        # Remove the temporary directory and variable.
        if hasattr(self, 'tmpdir'):
            rmtree(self.tmpdir)
            del self.tmpdir

        # Remove temporary file and variable.
        if hasattr(ds, 'tmpfile'):
            try:
                delete(ds.tmpfile, fail=False)
                del ds.tmpfile

            # Handle MS Windows strangeness.
            except WindowsError:
                sleep(3)
                try:
                    delete(ds.tmpfile, fail=False)
                finally:
                    del ds.tmpfile

        # Remove temporary file and variable.
        if hasattr(self, 'tmpfile'):
            try:
                delete(self.tmpfile, fail=False)
                del self.tmpfile

            # Handle MS Windows strangeness.
            except WindowsError:
                sleep(3)
                try:
                    delete(ds.tmpfile, fail=False)
                finally:
                    del ds.tmpfile

        # Reset relax.
        reset()
