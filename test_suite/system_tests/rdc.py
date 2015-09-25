###############################################################################
#                                                                             #
# Copyright (C) 2011-2015 Edward d'Auvergne                                   #
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
"""RDC-based system tests."""


# Python module imports.
from os import sep
from tempfile import mktemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import count_spins
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Rdc(SystemTestCase):
    """Class for testing RDC operations."""

    def test_calc_q_factors_no_tensor(self):
        """Test the operation of the rdc.calc_q_factors user function when no alignment tensor is present."""

        # Create a data pipe.
        self.interpreter.pipe.create('orig', 'N-state')

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Load the spins.
        self.interpreter.sequence.read(file='tb.txt', dir=dir, spin_id_col=1)
        self.interpreter.sequence.attach_protons()
        self.interpreter.sequence.display()

        # Load the RDCs.
        self.interpreter.rdc.read(align_id='tb', file='tb.txt', dir=dir, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)
        self.interpreter.sequence.display()

        # Create back-calculated RDC values from the real values.
        for interatom in interatomic_loop():
            if hasattr(interatom, 'rdc'):
                if not hasattr(interatom, 'rdc_bc'):
                    interatom.rdc_bc = {}
                interatom.rdc_bc['tb'] = interatom.rdc['tb'] + 1.0

        # Q factors.
        self.interpreter.rdc.calc_q_factors()


    def test_corr_plot(self):
        """Test the operation of the rdc.corr_plot user function."""

        # Create a data pipe.
        self.interpreter.pipe.create('orig', 'N-state')

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Load the spins.
        self.interpreter.sequence.read(file='tb.txt', dir=dir, spin_id_col=1)
        self.interpreter.sequence.attach_protons()
        self.interpreter.sequence.display()

        # Load the RDCs.
        self.interpreter.rdc.read(align_id='tb', file='tb.txt', dir=dir, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)
        self.interpreter.sequence.display()

        # Create back-calculated RDC values from the real values.
        for interatom in interatomic_loop():
            if hasattr(interatom, 'rdc'):
                if not hasattr(interatom, 'rdc_bc'):
                    interatom.rdc_bc = {}
                interatom.rdc_bc['tb'] = interatom.rdc['tb'] + 1.0

        # Correlation plot.
        ds.tmpfile = mktemp()
        self.interpreter.rdc.corr_plot(format='grace', title='Test', subtitle='Test2', file=ds.tmpfile, dir=None, force=True)

        # The expected file contents.
        real_contents = [
            "@version 50121",
            "@page size 842, 595",
            "@with g0",
            "@    world -27.0, -27.0, 16.0, 16.0",
            "@    view 0.15, 0.15, 1.28, 0.85",
            "@    title \"Test\"",
            "@    subtitle \"Test2\"",
            "@    xaxis  label \"Back-calculated RDC (Hz)\"",
            "@    xaxis  label char size 1.00",
            "@    xaxis  tick major 10",
            "@    xaxis  tick major size 0.50",
            "@    xaxis  tick major linewidth 0.5",
            "@    xaxis  tick minor ticks 9",
            "@    xaxis  tick minor linewidth 0.5",
            "@    xaxis  tick minor size 0.25",
            "@    xaxis  ticklabel char size 0.70",
            "@    yaxis  label \"Measured RDC (Hz)\"",
            "@    yaxis  label char size 1.00",
            "@    yaxis  tick major 10",
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
            "@    s1 legend \"tb\"",
            "@target G0.S0",
            "@type xydy",
            "          -100.000000000000000           -100.000000000000000              0.000000000000000",
            "           100.000000000000000            100.000000000000000              0.000000000000000",
            "&",
            "@target G0.S1",
            "@type xydy",
            "           -25.250195862900000            -26.250195862900000              1.000000000000000    \"#CaM:5@N-#CaM:5@H\"",
            "            10.930817669420000              9.930817669420000              1.000000000000000    \"#CaM:6@N-#CaM:6@H\"",
            "             8.263176141559999              7.263176141560000              1.000000000000000    \"#CaM:7@N-#CaM:7@H\"",
            "            -0.248405269810000             -1.248405269810000              0.000000000000000    \"#CaM:8@N-#CaM:8@H\"",
            "             6.318033143340000              5.318033143340000              1.000000000000000    \"#CaM:9@N-#CaM:9@H\"",
            "            15.036290945599999             14.036290945599999              1.000000000000000    \"#CaM:10@N-#CaM:10@H\"",
            "             2.336525303970000              1.336525303970000              0.000000000000000    \"#CaM:11@N-#CaM:11@H\"",
            "            -0.602167028100000             -1.602167028100000              0.000000000000000    \"#CaM:12@N-#CaM:12@H\"",
            "&",
        ]

        # Check the data.
        print("\nChecking the Grace file contents.")
        file = open(ds.tmpfile)
        lines = file.readlines()
        file.close()
        print(real_contents)
        print(lines)
        self.assertEqual(len(real_contents), len(lines))
        for i in range(len(lines)):
            print(lines[i][:-1])
            self.assertEqual(real_contents[i], lines[i][:-1])


    def test_rdc_copy(self):
        """Test the operation of the rdc.copy user function."""

        # Create a data pipe.
        self.interpreter.pipe.create('orig', 'N-state')

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Load the spins.
        self.interpreter.sequence.read(file='tb.txt', dir=dir, spin_id_col=1)
        self.interpreter.sequence.attach_protons()
        self.interpreter.sequence.display()

        # Load the RDCs.
        self.interpreter.rdc.read(align_id='tb', file='tb.txt', dir=dir, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)
        self.interpreter.sequence.display()

        # The RDCs.
        rdcs = [ -26.2501958629, 9.93081766942, 7.26317614156, -1.24840526981, 5.31803314334, 14.0362909456, 1.33652530397, -1.6021670281]

        # Create a new data pipe by copying the old, then switch to it.
        self.interpreter.pipe.copy(pipe_from='orig', pipe_to='new')
        self.interpreter.pipe.switch(pipe_name='new')

        # Delete the RDC data.
        self.interpreter.rdc.delete()

        # Copy the RDCs.
        self.interpreter.rdc.copy(pipe_from='orig', align_id='tb')

        # Checks.
        self.assert_(hasattr(cdp, 'align_ids'))
        self.assert_('tb' in cdp.align_ids)
        self.assert_(hasattr(cdp, 'rdc_ids'))
        self.assert_('tb' in cdp.rdc_ids)
        self.assertEqual(count_spins(), 16)
        self.assertEqual(len(cdp.interatomic), 8)
        i = 0
        for interatom in interatomic_loop():
            self.assertAlmostEqual(rdcs[i], interatom.rdc['tb'])
            i += 1


    def test_rdc_copy_different_spins(self):
        """Test the operation of the rdc.copy user function for two data pipes with different spin system."""

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Set up two data identical pipes.
        pipes = ['orig', 'new']
        delete = [':6', ':11']
        for i in range(2):
            # Create a data pipe.
            self.interpreter.pipe.create(pipes[i], 'N-state')

            # Load the spins.
            self.interpreter.sequence.read(file='tb.txt', dir=dir, spin_id_col=1)
            self.interpreter.spin.element('N')

            # Delete the residue.
            self.interpreter.residue.delete(delete[i])

            # Attach protons.
            self.interpreter.sequence.attach_protons()
            self.interpreter.sequence.display()

            # Create the interatomic data containers.
            self.interpreter.interatom.define(spin_id1='@N', spin_id2='@H')

        # Printout.
        print("\n\nInteratomic data containers for the 'orig' data pipe:")
        for interatom in interatomic_loop(pipe='orig'):
            print("'%s' '%s'" % (interatom.spin_id1, interatom.spin_id2))
        print("\nInteratomic data containers for the 'new' data pipe:")
        for interatom in interatomic_loop(pipe='new'):
            print("'%s' '%s'" % (interatom.spin_id1, interatom.spin_id2))

        # Load the RDCs into the first data pipe.
        self.interpreter.pipe.switch('orig')
        self.interpreter.rdc.read(align_id='tb', file='tb.txt', dir=dir, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

        # Copy the RDCs into the second data pipe.
        self.interpreter.rdc.copy(pipe_from='orig', pipe_to='new', align_id='tb')

        # Checks.
        rdcs = [
            [ -26.2501958629, 7.26317614156, -1.24840526981, 5.31803314334, 14.0362909456, 1.33652530397, -1.6021670281],
            [ -26.2501958629, 9.93081766942, 7.26317614156, -1.24840526981, 5.31803314334, 14.0362909456, -1.6021670281]
        ]
        for i in range(2):
            print("\nChecking data pipe '%s'." % pipes[i])

            # Metadata.
            self.assert_(hasattr(ds[pipes[i]], 'align_ids'))
            self.assert_('tb' in ds[pipes[i]].align_ids)
            self.assert_(hasattr(ds[pipes[i]], 'rdc_ids'))
            self.assert_('tb' in ds[pipes[i]].rdc_ids)

            # Spin data.
            self.assertEqual(count_spins(pipe=pipes[i]), 14)
            self.assertEqual(len(ds[pipes[i]].interatomic), 7)
            j = 0
            for interatom in interatomic_loop(pipe=pipes[i]):
                # Residue 6 in the 'new' data pipe has no RDCs.
                if i == 1 and j == 1:
                    self.assert_(not hasattr(interatom, 'rdc'))
                    self.assert_(not hasattr(interatom, 'rdc_data_types'))
                    self.assert_(not hasattr(interatom, 'absolute_rdc'))
                else:
                    self.assertAlmostEqual(rdcs[i][j], interatom.rdc['tb'])
                    self.assert_(hasattr(interatom, 'rdc_data_types'))
                    self.assert_('tb' in interatom.rdc_data_types)
                    self.assertEqual(interatom.rdc_data_types['tb'], 'D')
                    self.assert_(hasattr(interatom, 'absolute_rdc'))
                    self.assert_('tb' in interatom.absolute_rdc)
                    self.assertEqual(interatom.absolute_rdc['tb'], False)
                j += 1


    def test_rdc_copy_back_calc(self):
        """Test the operation of the rdc.copy user function for back-calculated values."""

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Set up two data identical pipes.
        pipes = ['orig', 'new']
        delete = [':6', ':11']
        for i in range(2):
            # Create a data pipe.
            self.interpreter.pipe.create(pipes[i], 'N-state')

            # Load the spins.
            self.interpreter.sequence.read(file='tb.txt', dir=dir, spin_id_col=1)
            self.interpreter.spin.element('N')

            # Delete the residue.
            self.interpreter.residue.delete(delete[i])

            # Attach protons.
            self.interpreter.sequence.attach_protons()
            self.interpreter.sequence.display()

            # Create the interatomic data containers.
            self.interpreter.interatom.define(spin_id1='@N', spin_id2='@H')

        # Printout.
        print("\n\nInteratomic data containers for the 'orig' data pipe:")
        for interatom in interatomic_loop(pipe='orig'):
            print("'%s' '%s'" % (interatom.spin_id1, interatom.spin_id2))
        print("\nInteratomic data containers for the 'new' data pipe:")
        for interatom in interatomic_loop(pipe='new'):
            print("'%s' '%s'" % (interatom.spin_id1, interatom.spin_id2))

        # Load the RDCs into the first data pipe.
        self.interpreter.pipe.switch('orig')
        self.interpreter.rdc.read(align_id='tb', file='tb.txt', dir=dir, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

        # Create back-calculated RDC values from the real values.
        for interatom in interatomic_loop():
            if hasattr(interatom, 'rdc'):
                if not hasattr(interatom, 'rdc_bc'):
                    interatom.rdc_bc = {}
                interatom.rdc_bc['tb'] = interatom.rdc['tb'] + 1.0

        # Copy the RDCs, including back-calculated values, into the second data pipe.
        self.interpreter.rdc.copy(pipe_from='orig', pipe_to='new', align_id='tb', back_calc=True)

        # Checks.
        rdcs = [
            [ -26.2501958629, 7.26317614156, -1.24840526981, 5.31803314334, 14.0362909456, 1.33652530397, -1.6021670281],
            [ -26.2501958629, 9.93081766942, 7.26317614156, -1.24840526981, 5.31803314334, 14.0362909456, -1.6021670281]
        ]
        for i in range(2):
            print("\nChecking data pipe '%s'." % pipes[i])

            # Metadata.
            self.assert_(hasattr(ds[pipes[i]], 'align_ids'))
            self.assert_('tb' in ds[pipes[i]].align_ids)
            self.assert_(hasattr(ds[pipes[i]], 'rdc_ids'))
            self.assert_('tb' in ds[pipes[i]].rdc_ids)

            # Spin data.
            self.assertEqual(count_spins(pipe=pipes[i]), 14)
            self.assertEqual(len(ds[pipes[i]].interatomic), 7)
            j = 0
            for interatom in interatomic_loop(pipe=pipes[i]):
                # Residue 6 in the 'new' data pipe has no RDCs.
                if i == 1 and j == 1:
                    self.assert_(not hasattr(interatom, 'rdc'))
                    self.assert_(not hasattr(interatom, 'rdc_data_types'))
                    self.assert_(not hasattr(interatom, 'absolute_rdc'))
                else:
                    self.assertAlmostEqual(rdcs[i][j], interatom.rdc['tb'])
                    self.assertAlmostEqual(rdcs[i][j]+1.0, interatom.rdc_bc['tb'])
                    self.assert_(hasattr(interatom, 'rdc_data_types'))
                    self.assert_('tb' in interatom.rdc_data_types)
                    self.assertEqual(interatom.rdc_data_types['tb'], 'D')
                    self.assert_(hasattr(interatom, 'absolute_rdc'))
                    self.assert_('tb' in interatom.absolute_rdc)
                    self.assertEqual(interatom.absolute_rdc['tb'], False)
                j += 1


    def test_rdc_load(self):
        """Test for the loading of some RDC data with the spin ID format."""

        # Create a data pipe.
        self.interpreter.pipe.create('test', 'N-state')

        # Data directory.
        dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep

        # Load the spins.
        self.interpreter.sequence.read(file='tb.txt', dir=dir, spin_id_col=1)
        self.interpreter.sequence.attach_protons()
        self.interpreter.sequence.display()

        # Load the RDCs.
        self.interpreter.rdc.read(align_id='tb', file='tb.txt', dir=dir, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)
        self.interpreter.sequence.display()

        # The RDCs.
        rdcs = [ -26.2501958629, 9.93081766942, 7.26317614156, -1.24840526981, 5.31803314334, 14.0362909456, 1.33652530397, -1.6021670281]

        # Checks.
        self.assertEqual(count_spins(), 16)
        self.assertEqual(len(cdp.interatomic), 8)
        i = 0
        for interatom in interatomic_loop():
            self.assertAlmostEqual(rdcs[i], interatom.rdc['tb'])
            i += 1
