###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
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

# Python module imports.
from os import sep
from shutil import rmtree
from string import split
import sys
from tempfile import mkdtemp
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import spin_index_loop
from generic_fns import pipes


class Relax_fit(TestCase):
    """Class for testing various aspects specific to relaxation curve-fitting."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()
        self.tmpdir = ds.tmpdir


    def tearDown(self):
        """Reset the relax data storage object."""

        # Remove the temporary directory.
        rmtree(self.tmpdir)

        # Reset the relax data storage object.
        ds.__reset__()


    def test_bug_12670_12679(self):
        """Test the relaxation curve fitting, replicating bug #12670 and bug #12679."""

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/1UBQ_relax_fit.py')

        # Open the intensities.agr file.
        file = open(ds.tmpdir + sep + 'intensities.agr')
        lines = file.readlines()
        file.close()

        # Split up the lines.
        for i in xrange(len(lines)):
            lines[i] = split(lines[i])

        # Check some of the Grace data.
        self.assertEqual(len(lines[23]), 2)
        self.assertEqual(lines[23][0], '0.004')
        self.assertEqual(lines[23][1], '487178.0')


    def test_curve_fitting(self):
        """Test the relaxation curve fitting C modules."""

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/relax_fit.py')


    def test_read_sparky(self):
        """The Sparky peak height loading test."""

        # Load the original state.
        self.relax.interpreter._State.load(state='basic_heights_T2_ncyc1', dir_name=sys.path[-1] + '/test_suite/shared_data/saved_states')

        # Create a new data pipe for the new data.
        self.relax.interpreter._Pipe.create('new', 'relax_fit')

        # Load the Lupin Ap4Aase sequence.
        self.relax.interpreter._Sequence.read(file="Ap4Aase.seq", dir=sys.path[-1] + "/test_suite/shared_data")

        # Name the spins so they can be matched to the assignments.
        self.relax.interpreter._Spin.name(name='N')

        # Read the peak heights.
        self.relax.interpreter._Spectrum.read_intensities(file="T2_ncyc1_ave.list", dir=sys.path[-1] + "/test_suite/shared_data/curve_fitting", spectrum_id='0.0176')


        # Test the integrity of the data.
        #################################

        # Get the data pipes.
        dp_new = pipes.get_pipe('new')
        dp_rx = pipes.get_pipe('rx')

        # Loop over the spins of the original data.
        for mol_index, res_index, spin_index in spin_index_loop():
            # Alias the spin containers.
            new_spin = dp_new.mol[mol_index].res[res_index].spin[spin_index]
            orig_spin = dp_rx.mol[mol_index].res[res_index].spin[spin_index]

            # Check the sequence info.
            self.assertEqual(dp_new.mol[mol_index].name, dp_rx.mol[mol_index].name)
            self.assertEqual(dp_new.mol[mol_index].res[res_index].num, dp_rx.mol[mol_index].res[res_index].num)
            self.assertEqual(dp_new.mol[mol_index].res[res_index].name, dp_rx.mol[mol_index].res[res_index].name)
            self.assertEqual(new_spin.num, orig_spin.num)
            self.assertEqual(new_spin.name, orig_spin.name)

            # Skip deselected spins.
            if not orig_spin.select:
                continue

            # Check intensities (if they exist).
            if hasattr(orig_spin, 'intensities'):
                self.assertEqual(orig_spin.intensities[0], new_spin.intensities[0])
