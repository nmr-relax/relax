###############################################################################
#                                                                             #
# Copyright (C) 2007-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control import io
from status import Status; status = Status()
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_io(UnitTestCase):
    """Unit tests for the functions of the 'pipe_control.io' module."""

    def setUp(self):
        """Set up for all the io data pipe unit tests."""

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')


    def test_add_io_data(self):
        """Test adding io data to the current pipe.

        The function tested is pipe_control.add_io_data().
        """

        # Add the io data object to the pipe.
        io_id = 'test_*.ft2'
        base_name = ['test_0.ft2', 'test_1.ft2']
        io.add_io_data(object_name='io_basename', io_id=io_id, io_data=base_name)

        # Test data pipe has the object 'io_basename' and that its value is the expected list.
        self.assertEqual(cdp.io_basename[io_id], base_name)


    def test_file_list(self):
        """Test storing file list to current pipe.

        The function tested is pipe_control.file_list().
        """

        # Define base path to files.
        base_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'repeated_analysis'+sep+'SOD1'

        # Define folder to all ft files.
        ft2_folder_1 = base_path +sep+ 'cpmg_disp_sod1d90a_060518' +sep+ 'cpmg_disp_sod1d90a_060518_normal.fid' +sep+ 'ft2_data'

        # Get the file list matching a glob pattern.
        ft2_glob_pat = '128_*_FT.ft2'
        io.file_list(glob=ft2_glob_pat, dir=ft2_folder_1, id=None)

        # Test the list of stored id.
        self.assertEqual(cdp.io_ids[-1], ft2_glob_pat)

        self.assertEqual(cdp.io_basename[ft2_glob_pat], ['128_0_FT.ft2', '128_1_FT.ft2'])
        self.assertEqual(cdp.io_file_root[ft2_glob_pat], ['128_0_FT', '128_1_FT'])
        self.assertEqual(cdp.io_dir[ft2_glob_pat], ft2_folder_1)
