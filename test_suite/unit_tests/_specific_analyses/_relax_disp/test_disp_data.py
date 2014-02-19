###############################################################################
#                                                                             #
# Copyright (C) 2008-2014 Edward d'Auvergne                                   #
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
from pipe_control import state
from specific_analyses.relax_disp.disp_data import loop_exp_frq_offset_point_time
from status import Status; status = Status()
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_disp_data(UnitTestCase):
    """Unit tests for the functions of the specific_analyses.relax_disp.disp_data module."""

    def setUp(self):
        """Setup some structures for the unit tests."""

        # Create a dispersion data pipe.
        ds.add(pipe_name='orig', pipe_type='relax_disp')


    def test_loop_exp_time(self):
        """U{Bug #21665<https://gna.org/bugs/?21665>} catch, the failure due to a a CPMG analysis recorded at two fields at two delay times, using calc()."""

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Original data
        ncyc_1 = [20, 16, 10, 36, 2, 12, 4, 22, 18, 40, 14, 26, 8, 32, 24, 6, 28]
        sfrq_1 = 499.86214*1E6
        time_T2_1 = 0.04
        cpmg_1 = [ncyc/time_T2_1 for ncyc in ncyc_1]
        cpmg_1.sort()

        ncyc_2 = [28, 4, 32, 60, 2, 10, 16, 8, 20, 52, 18, 40, 6, 12, 24, 14]
        sfrq_2 = 599.8908587*1E6
        time_T2_2 = 0.06
        cpmg_2 = [ncyc/time_T2_2 for ncyc in ncyc_2]
        cpmg_2.sort()

        # Test the loop function.
        for exp_type, frq, offset, point, time, ei, mi, oi, di, ti in loop_exp_frq_offset_point_time(return_indices=True):
            if frq == sfrq_1:
                self.assertEqual(time, time_T2_1)
            if frq == sfrq_2:
                self.assertEqual(time, time_T2_2)
