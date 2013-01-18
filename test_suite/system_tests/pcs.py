###############################################################################
#                                                                             #
# Copyright (C) 2011-2013 Edward d'Auvergne                                   #
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
"""PCS-based system tests."""


# Python module imports.
from os import sep
from re import search
from tempfile import mkdtemp

# relax module imports.
from generic_fns.mol_res_spin import count_spins, spin_loop
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Pcs(SystemTestCase):
    """Class for testing PCS operations."""

    def test_grace_plot(self):
        """Test the creation of Grace plots of PCS data."""

        # Create a data pipe for all the data.
        self.interpreter.pipe.create('CaM N-dom', 'N-state')

        # Create some spins.
        self.interpreter.spin.create(spin_name='N', spin_num=1, res_name='Gly', res_num=3)
        self.interpreter.spin.create(spin_name='H', spin_num=2, res_name='Gly', res_num=3)
        self.interpreter.spin.create(spin_name='N', spin_num=3, res_name='Gly', res_num=4)
        self.interpreter.spin.create(spin_name='H', spin_num=4, res_name='Gly', res_num=4)
        self.interpreter.sequence.display()

        # Set the element type.
        self.interpreter.spin.element(element='N', spin_id='@N')
        self.interpreter.spin.element(element='H', spin_id='@H')

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # PCSs.
        self.interpreter.pcs.read(align_id='dy', file='pcs_dy_200911.txt', dir=dir, res_num_col=1, data_col=2, error_col=4, spin_id='@N')
        self.interpreter.pcs.read(align_id='dy', file='pcs_dy_200911.txt', dir=dir, res_num_col=1, data_col=3, error_col=4, spin_id='@H')

        # Fudge the back-calculated PCS data.
        for spin in spin_loop():
            spin.pcs_bc = {}
            spin.pcs_bc['dy'] = spin.pcs['dy'] + 0.1

        # Create the grace plot.
        self.tmpdir = mkdtemp()
        self.interpreter.pcs.corr_plot(format='grace', file='pcs_corr.agr', dir=self.tmpdir, force=True)

        # Read the file data.
        file = open(self.tmpdir+sep+'pcs_corr.agr')
        lines = file.readlines()
        file.close()

        # Check the diagonal data.
        for i in range(len(lines)):
            if search('G0.S0', lines[i]):
                point1 = lines[i+2].split()
                point2 = lines[i+3].split()
                self.assertAlmostEqual(float(point1[0]), -100.0)
                self.assertAlmostEqual(float(point1[1]), -100.0)
                self.assertAlmostEqual(float(point2[0]), 100.0)
                self.assertAlmostEqual(float(point2[1]), 100.0)

        # Check the 15N data.
        for i in range(len(lines)):
            if search('G0.S1', lines[i]):
                point1 = lines[i+2].split()
                point2 = lines[i+3].split()
                self.assertAlmostEqual(float(point1[0]), 0.917+0.1)
                self.assertAlmostEqual(float(point1[1]), 0.917)
                self.assertAlmostEqual(float(point1[2]), 0.1)
                self.assertAlmostEqual(float(point2[0]), 1.131+0.1)
                self.assertAlmostEqual(float(point2[1]), 1.131)
                self.assertAlmostEqual(float(point2[2]), 0.1)

        # Check the 1H data.
        for i in range(len(lines)):
            if search('G0.S2', lines[i]):
                point1 = lines[i+2].split()
                point2 = lines[i+3].split()
                self.assertAlmostEqual(float(point1[0]), 0.843+0.1)
                self.assertAlmostEqual(float(point1[1]), 0.843)
                self.assertAlmostEqual(float(point1[2]), 0.1)
                self.assertAlmostEqual(float(point2[0]), 1.279+0.1)
                self.assertAlmostEqual(float(point2[1]), 1.279)
                self.assertAlmostEqual(float(point2[2]), 0.1)


    def test_load_multi_col_data(self):
        """Test the loading of PCS data from a file with different columns for each spin type."""

        # Create a data pipe for all the data.
        self.interpreter.pipe.create('CaM N-dom', 'N-state')

        # Create some spins.
        self.interpreter.spin.create(spin_name='N', spin_num=1, res_name='Gly', res_num=3)
        self.interpreter.spin.create(spin_name='H', spin_num=2, res_name='Gly', res_num=3)
        self.interpreter.spin.create(spin_name='N', spin_num=3, res_name='Gly', res_num=4)
        self.interpreter.spin.create(spin_name='H', spin_num=4, res_name='Gly', res_num=4)
        self.interpreter.sequence.display()

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # PCSs.
        self.interpreter.pcs.read(align_id='dy', file='pcs_dy_200911.txt', dir=dir, res_num_col=1, data_col=2, error_col=4, spin_id='@N')
        self.interpreter.pcs.read(align_id='dy', file='pcs_dy_200911.txt', dir=dir, res_num_col=1, data_col=3, error_col=4, spin_id='@H')

        # The data.
        pcs_data = {
            ':3@N': 0.917,
            ':3@H': 0.843,
            ':4@N': 1.131,
            ':4@H': 1.279,
        }

        # Check the PCS data.
        print("\n")
        for spin, spin_id in spin_loop(return_id=True):
            print("Checking the PCS data of spin '%s'." % spin_id)
            self.assert_(hasattr(spin, 'pcs'))
            self.assertEqual(spin.pcs['dy'], pcs_data[spin_id])
            self.assertEqual(spin.pcs_err['dy'], 0.1)


    def test_load_multi_col_data2(self):
        """Test the loading of PCS data from a file with different columns for each spin type."""

        # Create a data pipe for all the data.
        self.interpreter.pipe.create('CaM N-dom', 'N-state')

        # Create some spins.
        self.interpreter.spin.create(spin_name='N', spin_num=1, res_name='Gly', res_num=3, mol_name='CaM')
        self.interpreter.spin.create(spin_name='H', spin_num=2, res_name='Gly', res_num=3, mol_name='CaM')
        self.interpreter.spin.create(spin_name='N', spin_num=3, res_name='Gly', res_num=4, mol_name='CaM')
        self.interpreter.spin.create(spin_name='H', spin_num=4, res_name='Gly', res_num=4, mol_name='CaM')
        self.interpreter.sequence.display()

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # PCSs.
        self.interpreter.pcs.read(align_id='dy', file='pcs_dy_200911.txt', dir=dir, res_num_col=1, data_col=2, error_col=4, spin_id='@N')
        self.interpreter.pcs.read(align_id='dy', file='pcs_dy_200911.txt', dir=dir, res_num_col=1, data_col=3, error_col=4, spin_id='@H')

        # The data.
        pcs_data = {
            '#CaM:3@N': 0.917,
            '#CaM:3@H': 0.843,
            '#CaM:4@N': 1.131,
            '#CaM:4@H': 1.279,
        }

        # Check the PCS data.
        print("\n")
        for spin, spin_id in spin_loop(return_id=True):
            print("Checking the PCS data of spin '%s'." % spin_id)
            self.assert_(hasattr(spin, 'pcs'))
            self.assertEqual(spin.pcs['dy'], pcs_data[spin_id])
            self.assertEqual(spin.pcs_err['dy'], 0.1)


    def test_pcs_copy(self):
        """Test the operation of the pcs.copy user function."""

        # Create a data pipe.
        self.interpreter.pipe.create('orig', 'N-state')

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Load the spins.
        self.interpreter.sequence.read(file='pcs.txt', dir=dir, spin_name_col=1)
        self.interpreter.sequence.display()

        # Load the PCSs.
        self.interpreter.pcs.read(align_id='tb', file='pcs.txt', dir=dir, spin_name_col=1, data_col=2)
        self.interpreter.sequence.display()

        # The PCSs.
        pcs = [0.004, 0.008, 0.021, 0.029, 0.016, 0.010, 0.008, 0.003, 0.006, 0.003, 0.007, 0.005, 0.001, 0.070, None, 0.025, 0.098, 0.054, 0.075, 0.065, None, 0.070, 0.015, 0.098, 0.060, 0.120]

        # Create a new data pipe by copying the old, then switch to it.
        self.interpreter.pipe.copy(pipe_from='orig', pipe_to='new')
        self.interpreter.pipe.switch(pipe_name='new')

        # Delete the PCS data.
        self.interpreter.pcs.delete()

        # Copy the PCSs.
        self.interpreter.pcs.copy(pipe_from='orig', align_id='tb')

        # Checks.
        self.assertEqual(count_spins(), 26)
        self.assertEqual(len(cdp.interatomic), 0)
        i = 0
        for spin in spin_loop():
            self.assertEqual(pcs[i], spin.pcs['tb'])
            i += 1


    def test_pcs_load(self):
        """Test for the loading of some PCS data with the spin ID format."""

        # Create a data pipe.
        self.interpreter.pipe.create('test', 'N-state')

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Load the spins.
        self.interpreter.sequence.read(file='pcs.txt', dir=dir, spin_name_col=1)
        self.interpreter.sequence.display()

        # Load the PCSs.
        self.interpreter.pcs.read(align_id='tb', file='pcs.txt', dir=dir, spin_name_col=1, data_col=2)
        self.interpreter.sequence.display()

        # The PCSs.
        pcs = [0.004, 0.008, 0.021, 0.029, 0.016, 0.010, 0.008, 0.003, 0.006, 0.003, 0.007, 0.005, 0.001, 0.070, None, 0.025, 0.098, 0.054, 0.075, 0.065, None, 0.070, 0.015, 0.098, 0.060, 0.120]

        # Checks.
        self.assertEqual(count_spins(), 26)
        self.assertEqual(len(cdp.interatomic), 0)
        i = 0
        for spin in spin_loop():
            self.assertEqual(pcs[i], spin.pcs['tb'])
            i += 1


    def test_structural_noise(self):
        """Test the operation of the pcs.structural_noise user function."""

        # The file.
        state = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'saved_states'+sep+'pcs_structural_noise_test.bz2'

        # Load the state.
        self.interpreter.state.load(state)

        # Structural noise (twice to make sure old errors are removed properly from the PCS error).
        self.interpreter.pcs.structural_noise(rmsd=200.0, sim_num=100, file='devnull', dir=None, force=True)
        self.interpreter.pcs.structural_noise(rmsd=0.2, sim_num=10000, file='devnull', dir=None, force=True)

        # The simulated data (from 1,000,000 randomisations of 0.2 Angstrom RMSD).
        pcs_struct_err = {
            'Dy N-dom': 0.014643633242475744,
            'Er N-dom': 0.0047594540182391868,
            'Tm N-dom': 0.010454580925459261,
            'Tb N-dom': 0.01613972832580988
        }
        pcs_err = {
            'Dy N-dom': 0.1010664929367797,
            'Er N-dom': 0.10011319794388618,
            'Tm N-dom': 0.1005450061531003,
            'Tb N-dom': 0.10129408092495312
        }

        # Alias the single spin.
        spin = cdp.mol[0].res[0].spin[0]

        # Test the PCS data.
        for id in ['Dy N-dom', 'Tb N-dom', 'Tm N-dom', 'Er N-dom']:
            self.assertAlmostEqual(spin.pcs_struct_err[id], pcs_struct_err[id], 3)
            self.assertAlmostEqual(spin.pcs_err[id], pcs_err[id], 3)
