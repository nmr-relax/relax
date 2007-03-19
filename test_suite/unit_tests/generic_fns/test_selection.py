###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store
from generic_fns import selection


class Test_selection(TestCase):
    """Unit tests for the functions of the 'generic_fns.selection' module."""

    def setUp(self):
        """Set up some residues and spins for testing their selection and deselection."""

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Add a second molecule to the system.
        cdp.mol.add_item(mol_name='RNA')

        # Rename the first molecule.
        cdp.mol[0].name = 'Ap4Aase'

        # Add two more residues to the first molecule (and set the residue number of the first).
        cdp.mol[0].res[0].num = 1
        cdp.mol[0].res.add_item(res_num=2, res_name='Glu')
        cdp.mol[0].res.add_item(res_num=4, res_name='Pro')

        # Add one more residue to the second molecule (and set the residue number of the first).
        cdp.mol[1].res[0].num = -5
        cdp.mol[1].res.add_item(res_num=-4)

        # Add a second set of spins to the second molecule.
        cdp.mol[1].res[0].spin.add_item(spin_name='N5')
        cdp.mol[1].res[1].spin.add_item(spin_name='N5')

        # Deselect a number of spins.
        cdp.mol[0].res[0].spin[0].select = 0
        cdp.mol[0].res[2].spin[0].select = 0
        cdp.mol[1].res[0].spin[0].select = 0
        cdp.mol[1].res[1].spin[1].select = 0


    def tearDown(self):
        """Reset the relax data storage object."""

        # Reset.
        relax_data_store.__reset__()


    def test_molecule_loop(self):
        """Test the proper operation of the molecule loop with molecule selection.

        The function tested is generic_fns.selection.molecule_loop().
        """

        # Loop over the molecules.
        for mol in selection.molecule_loop('#RNA'):
            # Test the molecule name.
            self.assertEqual(mol.name, 'RNA')


    def test_molecule_loop_no_selection(self):
        """Test the proper operation of the molecule loop when no selection is present.

        The function tested is generic_fns.selection.molecule_loop().
        """

        # Molecule data.
        name = [None, 'RNA']

        # Loop over the molecules.
        i = 0
        for mol in selection.molecule_loop():
            # Test the molecule names.
            self.assertEqual(mol.name, name[i])

            # Increment i.
            i = i + 1


    def test_residue_loop(self):
        """Test the proper operation of the residue loop with residue selection.

        The function tested is generic_fns.selection.residue_loop().
        """

        # Loop over the residues.
        for res in selection.residue_loop('#Ap4Aase:Glu'):
            # Test the selection.
            self.assertEqual(res.num, 2)


    def test_residue_loop_no_selection(self):
        """Test the proper operation of the residue loop when no selection is present.

        The function tested is generic_fns.selection.residue_loop().
        """

        # Spin data.
        num = [1, 2, 4, -5, -4]
        name = [None, 'Glu', 'Pro', None, None]

        # Loop over the residues.
        i = 0
        for res in selection.residue_loop():
            # Test the residue numbers.
            self.assertEqual(res.select, num[i])

            # Test the residue names.
            self.assertEqual(res.name, name[i])

            # Increment i.
            i = i + 1


    def test_reverse(self):
        """Test spin system selection reversal.

        The function tested is generic_fns.selection.reverse().
        """

        # Reverse the selection.
        selection.reverse()

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test the selection status.
        self.assertEqual(cdp.mol[0].res[0].spin[0].select, 1)
        self.assertEqual(cdp.mol[0].res[1].spin[0].select, 0)
        self.assertEqual(cdp.mol[0].res[2].spin[0].select, 1)
        self.assertEqual(cdp.mol[1].res[0].spin[0].select, 1)
        self.assertEqual(cdp.mol[1].res[0].spin[1].select, 0)
        self.assertEqual(cdp.mol[1].res[1].spin[0].select, 0)
        self.assertEqual(cdp.mol[1].res[1].spin[1].select, 1)


    def test_spin_loop(self):
        """Test the proper operation of the spin loop with spin selection.

        The function tested is generic_fns.selection.spin_loop().
        """

        # Spin data.
        select = [1, 0]

        # Loop over the spins.
        i = 0
        for spin in selection.spin_loop('@N5'):
            # Test the selection.
            self.assertEqual(spin.select, select[i])

            # Test the spin names.
            self.assertEqual(spin.name, 'N5')

            # Increment i.
            i = i + 1


    def test_spin_loop_no_selection(self):
        """Test the proper operation of the spin loop when no selection is present.

        The function tested is generic_fns.selection.spin_loop().
        """

        # Spin data.
        select = [0, 1, 0, 0, 1, 1, 0]
        name = [None, None, None, None, 'N5', None, 'N5']

        # Loop over the spins.
        i = 0
        for spin in selection.spin_loop():
            # Test the selection.
            self.assertEqual(spin.select, select[i])

            # Test the spin names.
            self.assertEqual(spin.name, name[i])

            # Increment i.
            i = i + 1
