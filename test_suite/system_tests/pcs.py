###############################################################################
#                                                                             #
# Copyright (C) 2011-2016 Edward d'Auvergne                                   #
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
from tempfile import mkdtemp, mktemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.mol_res_spin import count_spins, spin_loop
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Pcs(SystemTestCase):
    """Class for testing PCS operations."""

    def test_corr_plot(self):
        """Test the operation of the pcs.corr_plot user function."""

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

        # Create back-calculated PCS values from the real values.
        for spin in spin_loop():
            if hasattr(spin, 'pcs'):
                if not hasattr(spin, 'pcs_bc'):
                    spin.pcs_bc = {}
                spin.pcs_bc['tb'] = spin.pcs['tb']
                if spin.pcs_bc['tb'] != None:
                    spin.pcs_bc['tb'] += 1.0

        # Correlation plot.
        ds.tmpfile = mktemp()
        self.interpreter.pcs.corr_plot(format='grace', title='Test', subtitle='Test2', file=ds.tmpfile, dir=None, force=True)

        # The expected file contents.
        real_contents = [
            "@version 50121",
            "@page size 842, 595",
            "@with g0",
            "@    world 0.0, 0.0, 2.0, 2.0",
            "@    view 0.15, 0.15, 1.28, 0.85",
            "@    title \"Test\"",
            "@    subtitle \"Test2\"",
            "@    xaxis  label \"Back-calculated PCS (ppm)\"",
            "@    xaxis  label char size 1.00",
            "@    xaxis  tick major 1",
            "@    xaxis  tick major size 0.50",
            "@    xaxis  tick major linewidth 0.5",
            "@    xaxis  tick minor ticks 9",
            "@    xaxis  tick minor linewidth 0.5",
            "@    xaxis  tick minor size 0.25",
            "@    xaxis  ticklabel char size 0.70",
            "@    yaxis  label \"Measured PCS (ppm)\"",
            "@    yaxis  label char size 1.00",
            "@    yaxis  tick major 1",
            "@    yaxis  tick major size 0.50",
            "@    yaxis  tick major linewidth 0.5",
            "@    yaxis  tick minor ticks 9",
            "@    yaxis  tick minor linewidth 0.5",
            "@    yaxis  tick minor size 0.25",
            "@    yaxis  ticklabel char size 0.70",
            "@    legend on",
            "@    legend 1, 0.5",
            "@    legend box fill pattern 1",
            "@    legend char size 1.0",
            "@    frame linewidth 0.5",
            "@    s0 symbol 1",
            "@    s0 symbol size 0.45",
            "@    s0 symbol linewidth 0.5",
            "@    s0 errorbar size 0.5",
            "@    s0 errorbar linewidth 0.5",
            "@    s0 errorbar riser linewidth 0.5",
            "@    s0 line linestyle 2",
            "@    s1 symbol 2",
            "@    s1 symbol size 0.45",
            "@    s1 symbol linewidth 0.5",
            "@    s1 errorbar size 0.5",
            "@    s1 errorbar linewidth 0.5",
            "@    s1 errorbar riser linewidth 0.5",
            "@    s1 line linestyle 0",
            "@    s1 legend \"tb (None)\"",
            "@target G0.S0",
            "@type xy",
            "          -100.000000000000000           -100.000000000000000    \"0\"",
            "           100.000000000000000            100.000000000000000    \"0\"",
            "&",
            "@target G0.S1",
            "@type xy",
            "             1.004000000000000              0.004000000000000    \"@C1\"",
            "             1.008000000000000              0.008000000000000    \"@C2\"",
            "             1.021000000000000              0.021000000000000    \"@C3\"",
            "             1.029000000000000              0.029000000000000    \"@C4\"",
            "             1.016000000000000              0.016000000000000    \"@C5\"",
            "             1.010000000000000              0.010000000000000    \"@C6\"",
            "             1.008000000000000              0.008000000000000    \"@H1\"",
            "             1.003000000000000              0.003000000000000    \"@H2\"",
            "             1.006000000000000              0.006000000000000    \"@H3\"",
            "             1.003000000000000              0.003000000000000    \"@H4\"",
            "             1.007000000000000              0.007000000000000    \"@H5\"",
            "             1.005000000000000              0.005000000000000    \"@H6\"",
            "             1.001000000000000              0.001000000000000    \"@H7\"",
            "             1.070000000000000              0.070000000000000    \"@C7\"",
            "             1.025000000000000              0.025000000000000    \"@C9\"",
            "             1.098000000000000              0.098000000000000    \"@C10\"",
            "             1.054000000000000              0.054000000000000    \"@C11\"",
            "             1.075000000000000              0.075000000000000    \"@C12\"",
            "             1.065000000000000              0.065000000000000    \"@H12\"",
            "             1.070000000000000              0.070000000000000    \"@H14\"",
            "             1.015000000000000              0.015000000000000    \"@H15\"",
            "             1.098000000000000              0.098000000000000    \"@H16\"",
            "             1.060000000000000              0.060000000000000    \"@H17\"",
            "             1.120000000000000              0.120000000000000    \"@H18\"",
            "&"
        ]

        # Check the data.
        print("\nChecking the Grace file contents.")
        file = open(ds.tmpfile)
        lines = file.readlines()
        file.close()
        self.assertEqual(len(real_contents), len(lines))
        for i in range(len(lines)):
            print(lines[i][:-1])
            self.assertEqual(real_contents[i], lines[i][:-1])


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
        self.assert_(hasattr(cdp, 'align_ids'))
        self.assert_('tb' in cdp.align_ids)
        self.assert_(hasattr(cdp, 'pcs_ids'))
        self.assert_('tb' in cdp.pcs_ids)
        self.assertEqual(count_spins(), 26)
        self.assertEqual(len(cdp.interatomic), 0)
        i = 0
        for spin in spin_loop():
            self.assertEqual(pcs[i], spin.pcs['tb'])
            i += 1


    def test_pcs_copy_different_spins(self):
        """Test the operation of the pcs.copy user function for two data pipes with different spin system."""

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Set up two data identical pipes.
        pipes = ['orig', 'new']
        delete = ['@C2', '@H17']
        for i in range(2):
            # Create a data pipe.
            self.interpreter.pipe.create(pipes[i], 'N-state')

            # Load the spins.
            self.interpreter.sequence.read(file='pcs.txt', dir=dir, spin_name_col=1)

            # Delete the spin.
            self.interpreter.spin.delete(delete[i])
            self.interpreter.sequence.display()

        # Load the PCSs into the first data pipe.
        self.interpreter.pipe.switch('orig')
        self.interpreter.pcs.read(align_id='tb', file='pcs.txt', dir=dir, spin_name_col=1, data_col=2)

        # Copy the PCSs into the second data pipe.
        self.interpreter.pcs.copy(pipe_from='orig', pipe_to='new', align_id='tb')

        # Checks.
        pcs = [
            [0.004, 0.021, 0.029, 0.016, 0.010, 0.008, 0.003, 0.006, 0.003, 0.007, 0.005, 0.001, 0.070, None, 0.025, 0.098, 0.054, 0.075, 0.065, None, 0.070, 0.015, 0.098, 0.060, 0.120],
            [0.004, 0.008, 0.021, 0.029, 0.016, 0.010, 0.008, 0.003, 0.006, 0.003, 0.007, 0.005, 0.001, 0.070, None, 0.025, 0.098, 0.054, 0.075, 0.065, None, 0.070, 0.015, 0.098, 0.120]
        ]
        for i in range(2):
            print("\nChecking data pipe '%s'." % pipes[i])
            self.assert_(hasattr(ds[pipes[i]], 'align_ids'))
            self.assert_('tb' in ds[pipes[i]].align_ids)
            self.assert_(hasattr(ds[pipes[i]], 'pcs_ids'))
            self.assert_('tb' in ds[pipes[i]].pcs_ids)
            self.assertEqual(count_spins(), 25)
            self.assertEqual(len(cdp.interatomic), 0)
            j = 0
            for spin in spin_loop(pipe=pipes[i]):
                # Atom C2 in the 'new' data pipe has no PCSs.
                if i == 1 and j == 1:
                    self.assert_(not hasattr(spin, 'pcs'))
                else:
                    if pcs[i][j] == None:
                        self.assertEqual(pcs[i][j], spin.pcs['tb'])
                    else:
                        self.assertAlmostEqual(pcs[i][j], spin.pcs['tb'])
                j += 1


    def test_pcs_copy_back_calc(self):
        """Test the operation of the pcs.copy user function for back-calculated values."""

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Set up two data identical pipes.
        pipes = ['orig', 'new']
        delete = ['@C2', '@H17']
        for i in range(2):
            # Create a data pipe.
            self.interpreter.pipe.create(pipes[i], 'N-state')

            # Load the spins.
            self.interpreter.sequence.read(file='pcs.txt', dir=dir, spin_name_col=1)

            # Delete the spin.
            self.interpreter.spin.delete(delete[i])
            self.interpreter.sequence.display()

        # Load the PCSs into the first data pipe.
        self.interpreter.pipe.switch('orig')
        self.interpreter.pcs.read(align_id='tb', file='pcs.txt', dir=dir, spin_name_col=1, data_col=2)

        # Create back-calculated PCS values from the real values.
        for spin in spin_loop():
            if hasattr(spin, 'pcs'):
                if not hasattr(spin, 'pcs_bc'):
                    spin.pcs_bc = {}
                spin.pcs_bc['tb'] = spin.pcs['tb']
                if spin.pcs_bc['tb'] != None:
                    spin.pcs_bc['tb'] += 1.0

        # Copy the PCSs into the second data pipe.
        self.interpreter.pcs.copy(pipe_from='orig', pipe_to='new', align_id='tb', back_calc=True)

        # Checks.
        pcs = [
            [0.004, 0.021, 0.029, 0.016, 0.010, 0.008, 0.003, 0.006, 0.003, 0.007, 0.005, 0.001, 0.070, None, 0.025, 0.098, 0.054, 0.075, 0.065, None, 0.070, 0.015, 0.098, 0.060, 0.120],
            [0.004, 0.008, 0.021, 0.029, 0.016, 0.010, 0.008, 0.003, 0.006, 0.003, 0.007, 0.005, 0.001, 0.070, None, 0.025, 0.098, 0.054, 0.075, 0.065, None, 0.070, 0.015, 0.098, 0.120]
        ]
        for i in range(2):
            print("\nChecking data pipe '%s'." % pipes[i])
            self.assert_(hasattr(ds[pipes[i]], 'align_ids'))
            self.assert_('tb' in ds[pipes[i]].align_ids)
            self.assert_(hasattr(ds[pipes[i]], 'pcs_ids'))
            self.assert_('tb' in ds[pipes[i]].pcs_ids)
            self.assertEqual(count_spins(), 25)
            self.assertEqual(len(cdp.interatomic), 0)
            j = 0
            for spin in spin_loop(pipe=pipes[i]):
                # Atom C2 in the 'new' data pipe has no PCSs.
                if i == 1 and j == 1:
                    self.assert_(not hasattr(spin, 'pcs'))
                else:
                    if pcs[i][j] == None:
                        self.assertEqual(None, spin.pcs['tb'])
                        self.assertEqual(None, spin.pcs_bc['tb'])
                    else:
                        self.assertAlmostEqual(pcs[i][j], spin.pcs['tb'])
                        self.assertAlmostEqual(pcs[i][j]+1.0, spin.pcs_bc['tb'])
                j += 1


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
        self.interpreter.pcs.structural_noise(rmsd=0.2, sim_num=20000, file='devnull', dir=None, force=True)

        # The simulated data (from 1,000,000 randomisations of 0.2 Angstrom RMSD).
        pcs_struct_err = {
            'Dy N-dom': 0.0253,
            'Er N-dom': 0.0081,
            'Tm N-dom': 0.0181,
            'Tb N-dom': 0.0280
        }
        pcs_err = {
            'Dy N-dom': 0.1031,
            'Er N-dom': 0.1001,
            'Tm N-dom': 0.1016,
            'Tb N-dom': 0.1038
        }

        # Alias the single spin.
        spin = cdp.mol[0].res[0].spin[0]

        # Test the PCS data.
        for id in ['Dy N-dom', 'Tb N-dom', 'Tm N-dom', 'Er N-dom']:
            self.assertAlmostEqual(spin.pcs_struct_err[id], pcs_struct_err[id], 2)
            self.assertAlmostEqual(spin.pcs_err[id], pcs_err[id], 2)
