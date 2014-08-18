###############################################################################
#                                                                             #
# Copyright (C) 2008-2014 Edward d'Auvergne                                   #
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
from pipe_control import mol_res_spin, pipes, relax_data, spectrometer, state
from specific_analyses.relax_disp.checks import check_missing_r1, get_times
from specific_analyses.relax_disp.data import set_exp_type
from specific_analyses.relax_disp.variables import MODEL_DPL94, MODEL_R2EFF
from status import Status; status = Status()
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_checks(UnitTestCase):
    """Unit tests for the functions of the specific_analyses.relax_disp.checks module."""

    def setUp(self):
        """Setup some structures for the unit tests."""

        # Create a dispersion data pipe.
        ds.add(pipe_name='orig', pipe_type='relax_disp')


    def set_up_spins(self, pipe_name=None):
        """Function for setting up a few spins for the given pipe."""

        # Alias the pipe.
        pipe = pipes.get_pipe(pipe_name)

        # Path to file.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013'

        # File with spins.
        file = open(data_path+sep+'R1_fitted_values.txt')
        lines = file.readlines()
        file.close()

        for i, line in enumerate(lines):
            # Make the string test
            line_split = line.split()

            if line_split[0] == "#":
                continue

            mol_name = line_split[0]
            mol_name = None
            res_num = int(line_split[1])
            res_name = line_split[2]
            spin_num = line_split[3]
            spin_num = None
            spin_name = line_split[4]

            # Create the spin.
            mol_res_spin.create_spin(spin_num=spin_num, spin_name=spin_name, res_num=res_num, res_name=res_name, mol_name=mol_name, pipe=pipe_name)


    def test_check_missing_r1(self):
        """Unit test of the check_missing_r1() function."""

        # Set up some spins.
        self.set_up_spins(pipe_name='orig')

        # Set variables.
        exp_type = 'R1rho'
        frq = 800.1 * 1E6

        # Set an experiment type to the pipe.
        set_exp_type(spectrum_id='test', exp_type=exp_type)

        # Set a frequency to loop through.
        spectrometer.set_frequency(id='test', frq=frq, units='Hz')

        # Check R1 for DPL94.
        check_missing_r1_return = check_missing_r1(model=MODEL_DPL94)
        self.assertEqual(check_missing_r1_return, True)

        # Check R1 for R2eff.
        check_missing_r1_return = check_missing_r1(model=MODEL_R2EFF)
        self.assertEqual(check_missing_r1_return, False)

        # The path to the data files.
        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013'

        # Now load some R1 data.
        relax_data.read(ri_id='R1', ri_type='R1', frq=cdp.spectrometer_frq_list[0], file='R1_fitted_values.txt', dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

        # Check R1.
        check_missing_r1_return = check_missing_r1(model=MODEL_DPL94)
        self.assertEqual(check_missing_r1_return, False)


    def test_get_times_cpmg(self):
        """Unit test of the get_times() function.

        This uses the data of the saved state attached to U{bug #21665<https://gna.org/bugs/?21665>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Check the return of get_times().
        times = get_times()
        for exp_type in times:
            print(times[exp_type])
            self.assertEqual(len(times[exp_type]), 2)






