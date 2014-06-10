###############################################################################
#                                                                             #
# Copyright (C) 2007-2014 Edward d'Auvergne                                   #
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

# Python module imports.
from os import sep
from unittest import TestCase

# relax module imports.
import lib.io


class Test_io(TestCase):
    """Unit tests for the functions of the 'lib.io' module."""


    def test_file_root(self):
        """Test the lib.io.file_root() function with '/tmp/test.xyz'."""

        # The data.
        file = '/tmp/test.xyz'
        root = 'test'

        # Check the function.
        self.assertEqual(lib.io.file_root(file), root)


    def test_file_root2(self):
        """Test the lib.io.file_root() function with '/tmp/test.xyz.gz'."""

        # The data.
        file = '/tmp/test.xyz.gz'
        root = 'test'

        # Check the function.
        self.assertEqual(lib.io.file_root(file), root)


    def test_get_file_path(self):
        """Test for file paths which should remain unmodified by lib.io.get_file_path."""

        # Some file paths that shouldn't change.
        file1 = 'test'
        file2 = 'test'+sep+'aaa'
        file3 = sep+'home'+sep+'test'+sep+'aaa'

        # Check that nothing changes.
        self.assertEqual(lib.io.get_file_path(file1), file1)
        self.assertEqual(lib.io.get_file_path(file2), file2)
        self.assertEqual(lib.io.get_file_path(file3), file3)


    def test_get_file_path_with_dir(self):
        """The modification of file paths by lib.io.get_file_path when a directory is supplied."""

        # Some file paths.
        file1 = 'test'
        file2 = 'test'+sep+'aaa'
        file3 = sep+'home'+sep+'test'+sep+'aaa'

        # Some directories.
        dir1 = sep+'usr'
        dir2 = 'usr'
        dir3 = sep+'usr'

        # Check that nothing changes.
        self.assertEqual(lib.io.get_file_path(file1, dir1), dir1+sep+file1)
        self.assertEqual(lib.io.get_file_path(file2, dir2), dir2+sep+file2)
        self.assertEqual(lib.io.get_file_path(file3, dir=dir3), dir3+sep+file3)


    def test_get_file_path_with_homedir(self):
        """The modification of file paths with '~', by lib.io.get_file_path."""

        # Some file paths.
        file1 = '~'+sep+'test'
        file2 = '~'+sep+'test'+sep+'aaa'

        # Check that nothing changes.
        self.assertNotEqual(lib.io.get_file_path(file1), file1)
        self.assertNotEqual(lib.io.get_file_path(file2), file2)
