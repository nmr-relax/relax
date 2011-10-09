###############################################################################
#                                                                             #
# Copyright (C) 2007-2011 Edward d'Auvergne                                   #
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
from numpy import array

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoPipeError
from test_suite.unit_tests.base_classes import UnitTestCase


class Spin_base_class(UnitTestCase):
    """Testing base class for 'prompt.spin' and corresponding 'generic_fns.mol_res_spin' fns.

    This base class also contains many shared unit tests.
    """

    def setUp(self):
        """Set up for all the spin unit tests.

        The data contained within the 'orig' data pipe is:

        ID      Molecule        Res number      Res name        Spin number     Spin name
        0,0,0   Old mol         1               Ala             111             C8
        0,0,1   Old mol         1               Ala             6               C19
        0,0,2   Old mol         1               Ala             7               C21
        0,0,3   Old mol         1               Ala             8               C24
        0,0,4   Old mol         1               Ala             9               C26
        0,1,0   Old mol         2               Arg             78              NH
        1,0,0   New mol         5               Lys             239             NH
        1,1,0   New mol         6               Thr             None            None
        1,1,1   New mol         6               Thr             3239            NH

        The IDs correspond to the molecule, residue and spin indices.
        """

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Add a second data pipe for copying tests.
        ds.add(pipe_name='test', pipe_type='mf')

        # Set the current data pipe to 'orig'.
        pipes.switch('orig')

        # Name the first molecule.
        cdp.mol[0].name = 'Old mol'

        # Create the first residue and add some data to its spin container.
        cdp.mol[0].res[0].num = 1
        cdp.mol[0].res[0].name = 'Ala'
        cdp.mol[0].res[0].spin[0].num = 111
        cdp.mol[0].res[0].spin[0].name = 'C8'
        cdp.mol[0].res[0].spin[0].x = 1

        # Add some more spins.
        cdp.mol[0].res[0].spin.add_item('C19', 6)
        cdp.mol[0].res[0].spin.add_item('C21', 7)
        cdp.mol[0].res[0].spin.add_item('C24', 8)
        cdp.mol[0].res[0].spin.add_item('C26', 9)

        # Create a second residue.
        cdp.mol[0].res.add_item('Arg', 2)
        cdp.mol[0].res[1].spin[0].num = 78
        cdp.mol[0].res[1].spin[0].name = 'NH'

        # Create a second molecule.
        cdp.mol.add_item('New mol')

        # Create the first and second residue of the second molecule and add some data to its spin container.
        cdp.mol[1].res[0].num = 5
        cdp.mol[1].res[0].name = 'Lys'
        cdp.mol[1].res[0].spin[0].num = 239
        cdp.mol[1].res[0].spin[0].name = 'NH'
        cdp.mol[1].res.add_item('Thr', 6)
        cdp.mol[1].res[1].spin.add_item(None, 1433)
        cdp.mol[1].res[1].spin.add_item('NH', 3239)

        # Create a third molecule.
        cdp.mol.add_item('3rd')

        # Create the first residue of the 3rd molecule and add some data to its spin container.
        cdp.mol[2].res[0].num = 13
        cdp.mol[2].res[0].name = 'Gly'
        cdp.mol[2].res[0].spin[0].x = 'hello'


    def test_copy_spin(self):
        """Test the copying of the spin data within the same residue.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy the spin from the 3rd molecule.
        self.spin_fns.copy(spin_from='#3rd:13', spin_to='#3rd:13@NE')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test the original spin.
        self.assertEqual(dp.mol[2].res[0].num, 13)
        self.assertEqual(dp.mol[2].res[0].name, 'Gly')
        self.assertEqual(dp.mol[2].res[0].spin[0].num, None)
        self.assertEqual(dp.mol[2].res[0].spin[0].name, None)
        self.assertEqual(dp.mol[2].res[0].spin[0].x, 'hello')

        # Test the new spin.
        self.assertEqual(dp.mol[2].res[0].spin[1].num, None)
        self.assertEqual(dp.mol[2].res[0].spin[1].name, 'NE')
        self.assertEqual(dp.mol[2].res[0].spin[1].x, 'hello')


    def test_copy_spin_between_molecules(self):
        """Test the copying of the spin data between different molecules.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy the spin '111' from the first molecule, first residue to the second molecule, fifth residue.
        self.spin_fns.copy(spin_from='#Old mol:1@111', spin_to='#New mol:5@334')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test the original spin.
        self.assertEqual(dp.mol[0].res[0].num, 1)
        self.assertEqual(dp.mol[0].res[0].name, 'Ala')
        self.assertEqual(dp.mol[0].res[0].spin[0].num, 111)
        self.assertEqual(dp.mol[0].res[0].spin[0].name, 'C8')
        self.assertEqual(dp.mol[0].res[0].spin[0].x, 1)

        # Test the new spin.
        self.assertEqual(dp.mol[1].res[0].num, 5)
        self.assertEqual(dp.mol[1].res[0].name, 'Lys')
        self.assertEqual(dp.mol[1].res[0].spin[0].num, 239)
        self.assertEqual(dp.mol[1].res[0].spin[0].name, 'NH')
        self.assertEqual(dp.mol[1].res[0].spin[1].num, 334)
        self.assertEqual(dp.mol[1].res[0].spin[1].name, 'C8')
        self.assertEqual(dp.mol[1].res[0].spin[1].x, 1)


    def test_copy_spin_between_residues(self):
        """Test the copying of the spin data between different residues.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy the spin '111' from the first residue to the third residue.
        self.spin_fns.copy(spin_from='#Old mol:1@111', spin_to='#Old mol:2')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test the original spin.
        self.assertEqual(dp.mol[0].res[0].num, 1)
        self.assertEqual(dp.mol[0].res[0].name, 'Ala')
        self.assertEqual(dp.mol[0].res[0].spin[0].num, 111)
        self.assertEqual(dp.mol[0].res[0].spin[0].name, 'C8')
        self.assertEqual(dp.mol[0].res[0].spin[0].x, 1)

        # Test the new spin.
        self.assertEqual(dp.mol[0].res[1].num, 2)
        self.assertEqual(dp.mol[0].res[1].name, 'Arg')
        self.assertEqual(dp.mol[0].res[1].spin[0].num, 78)
        self.assertEqual(dp.mol[0].res[1].spin[0].name, 'NH')
        self.assertEqual(dp.mol[0].res[1].spin[1].num, 111)
        self.assertEqual(dp.mol[0].res[1].spin[1].name, 'C8')
        self.assertEqual(dp.mol[0].res[1].spin[1].x, 1)


    def test_copy_spin_between_pipes(self):
        """Test the copying of the spin data between different data pipes.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy the spin data.
        self.spin_fns.copy(spin_from='#Old mol:1@111', pipe_to='test')

        # Get the data pipes.
        dp = pipes.get_pipe('orig')
        dp_test = pipes.get_pipe('test')

        # Change the first spin's data.
        dp.mol[0].res[0].spin[0].num = 222
        dp.mol[0].res[0].spin[0].x = 2

        # Test the original spin.
        self.assertEqual(dp.mol[0].res[0].spin[0].num, 222)
        self.assertEqual(dp.mol[0].res[0].spin[0].x, 2)

        # Test the new spin.
        self.assertEqual(dp_test.mol[0].res[0].spin[0].num, 111)
        self.assertEqual(dp_test.mol[0].res[0].spin[0].x, 1)


    def test_copy_spin_between_pipes_fail(self):
        """Test the copying of the spin data between different data pipes.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy the spin to the second data pipe.
        self.assertRaises(RelaxNoPipeError, self.spin_fns.copy, spin_from='#Old mol:1@111', pipe_to='test2')



    def test_copy_spin_fail1(self):
        """Test the failure of the copying of the spin data of a non-existent residue.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy a non-existent residue (1 Met, @111).
        self.assertRaises(RelaxError, self.spin_fns.copy, spin_from=':Met@111', spin_to=':2,Gly')


    def test_copy_spin_fail2(self):
        """Test the failure of the copying of the spin data of a non-existent spin.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy a non-existent spin (1 Ala, @234).
        self.assertRaises(RelaxError, self.spin_fns.copy, spin_from=':Ala@234', spin_to=':2,Gly')


    def test_copy_spin_fail3(self):
        """Test the failure of the copying of the spin data to a non-existent residue.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy to a non-existent residue (3).
        self.assertRaises(RelaxError, self.spin_fns.copy, spin_from='#Old mol:1@111', spin_to='#Old mol:3')


    def test_copy_spin_fail4(self):
        """Test the failure of the copying of the spin data to a number which already exists.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy a spin to a number which already exists.
        self.assertRaises(RelaxError, self.spin_fns.copy, spin_from=':1', spin_to=':2@78')


    def test_create_pseudo_spin(self):
        """Test the creation of a pseudo-atom.

        The function tested is both generic_fns.mol_res_spin.create_pseudo_spin() and
        prompt.spin.create_pseudo().
        """

        # Create a few new protons.
        self.spin_fns.create(100, 'H13', res_num=1, mol_name='Old mol')
        self.spin_fns.create(101, 'H14', res_num=1, mol_name='Old mol')
        self.spin_fns.create(102, 'H15', res_num=1, mol_name='Old mol')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Set some atomic positions.
        dp.mol[0].res[0].spin[5].pos = [array([3.0, 0.0, 0.0])]
        dp.mol[0].res[0].spin[6].pos = [array([0.0, 3.0, 0.0])]
        dp.mol[0].res[0].spin[7].pos = [array([0.0, 0.0, 3.0])]

        # Create a pseudo-spin.
        self.spin_fns.create_pseudo('Q3', spin_num=105, members=['@H13', '@H14', '@H15'], averaging='linear')

        # Test that the spin numbers are correct.
        self.assertEqual(dp.mol[0].res[0].spin[5].num, 100)
        self.assertEqual(dp.mol[0].res[0].spin[6].num, 101)
        self.assertEqual(dp.mol[0].res[0].spin[7].num, 102)
        self.assertEqual(dp.mol[0].res[0].spin[8].num, 105)

        # Test that the spin names are correct.
        self.assertEqual(dp.mol[0].res[0].spin[5].name, 'H13')
        self.assertEqual(dp.mol[0].res[0].spin[6].name, 'H14')
        self.assertEqual(dp.mol[0].res[0].spin[7].name, 'H15')
        self.assertEqual(dp.mol[0].res[0].spin[8].name, 'Q3')

        # Test the averaged position.
        self.assertEqual(len(dp.mol[0].res[0].spin[8].pos), 1)
        self.assertEqual(dp.mol[0].res[0].spin[8].pos[0][0], 1.0)
        self.assertEqual(dp.mol[0].res[0].spin[8].pos[0][1], 1.0)
        self.assertEqual(dp.mol[0].res[0].spin[8].pos[0][2], 1.0)

        # Test the pseudo-spin info.
        self.assertEqual(dp.mol[0].res[0].spin[5].pseudo_name, '@Q3')
        self.assertEqual(dp.mol[0].res[0].spin[5].pseudo_num, 105)
        self.assertEqual(dp.mol[0].res[0].spin[6].pseudo_name, '@Q3')
        self.assertEqual(dp.mol[0].res[0].spin[6].pseudo_num, 105)
        self.assertEqual(dp.mol[0].res[0].spin[7].pseudo_name, '@Q3')
        self.assertEqual(dp.mol[0].res[0].spin[7].pseudo_num, 105)
        self.assertEqual(dp.mol[0].res[0].spin[8].members, ['@H13', '@H14', '@H15'])
        self.assertEqual(dp.mol[0].res[0].spin[8].averaging, 'linear')


    def test_create_pseudo_spin2(self):
        """Test the creation of a pseudo-atom (test 2).

        The function tested is both generic_fns.mol_res_spin.create_pseudo_spin() and
        prompt.spin.create_pseudo().
        """

        # Create a few new protons.
        self.spin_fns.create(100, 'H93', res_num=1, mol_name='Old mol')
        self.spin_fns.create(101, 'H94', res_num=1, mol_name='Old mol')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Set some atomic positions.
        dp.mol[0].res[0].spin[5].pos = [array([2.0, 0.0, 0.0]), array([-2.0, 0.0, 0.0])]
        dp.mol[0].res[0].spin[6].pos = [array([0.0, 2.0, 0.0]), array([0.0, -2.0, 0.0])]

        # Create a pseudo-spin.
        self.spin_fns.create_pseudo('Q10', spin_num=105, members=['@H93', '@H94'], averaging='linear')

        # Test that the spin numbers are correct.
        self.assertEqual(dp.mol[0].res[0].spin[5].num, 100)
        self.assertEqual(dp.mol[0].res[0].spin[6].num, 101)
        self.assertEqual(dp.mol[0].res[0].spin[7].num, 105)

        # Test that the spin names are correct.
        self.assertEqual(dp.mol[0].res[0].spin[5].name, 'H93')
        self.assertEqual(dp.mol[0].res[0].spin[6].name, 'H94')
        self.assertEqual(dp.mol[0].res[0].spin[7].name, 'Q10')

        # Test the averaged position.
        self.assertEqual(len(dp.mol[0].res[0].spin[7].pos), 2)
        self.assertEqual(dp.mol[0].res[0].spin[7].pos[0][0], 1.0)
        self.assertEqual(dp.mol[0].res[0].spin[7].pos[0][1], 1.0)
        self.assertEqual(dp.mol[0].res[0].spin[7].pos[0][2], 0.0)
        self.assertEqual(dp.mol[0].res[0].spin[7].pos[1][0], -1.0)
        self.assertEqual(dp.mol[0].res[0].spin[7].pos[1][1], -1.0)
        self.assertEqual(dp.mol[0].res[0].spin[7].pos[1][2], 0.0)

        # Test the pseudo-spin info.
        self.assertEqual(dp.mol[0].res[0].spin[5].pseudo_name, '@Q10')
        self.assertEqual(dp.mol[0].res[0].spin[5].pseudo_num, 105)
        self.assertEqual(dp.mol[0].res[0].spin[6].pseudo_name, '@Q10')
        self.assertEqual(dp.mol[0].res[0].spin[6].pseudo_num, 105)
        self.assertEqual(dp.mol[0].res[0].spin[7].members, ['@H93', '@H94'])
        self.assertEqual(dp.mol[0].res[0].spin[7].averaging, 'linear')


    def test_create_spin(self):
        """Test the creation of a spin.

        The function tested is both generic_fns.mol_res_spin.create_spin() and
        prompt.spin.create().
        """

        # Create a few new spins.
        self.spin_fns.create(1, 'C3', res_num=1, mol_name='Old mol')
        self.spin_fns.create(2, 'C17', res_num=1, mol_name='Old mol')
        self.spin_fns.create(-3, 'N7', res_num=6, mol_name='New mol')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test that the spin numbers are correct.
        self.assertEqual(dp.mol[0].res[0].spin[5].num, 1)
        self.assertEqual(dp.mol[0].res[0].spin[6].num, 2)
        self.assertEqual(dp.mol[1].res[1].spin[2].num, -3)

        # Test that the spin names are correct.
        self.assertEqual(dp.mol[0].res[0].spin[5].name, 'C3')
        self.assertEqual(dp.mol[0].res[0].spin[6].name, 'C17')
        self.assertEqual(dp.mol[1].res[1].spin[2].name, 'N7')


    def test_create_spin_fail(self):
        """Test the failure of spin creation (by supplying two spins with the same number).

        The function tested is both generic_fns.mol_res_spin.create_spin() and
        prompt.spin.create().
        """

        # Create the first spin.
        self.spin_fns.create(1, 'P1', res_num=1, mol_name='Old mol')

        # Assert that a RelaxError occurs when the next added spin has the same number as the first.
        self.assertRaises(RelaxError, self.spin_fns.create, 1, 'P3', res_num=1, mol_name='Old mol')


    def test_delete_spin_name(self):
        """Test spin deletion using spin name identifiers.

        The function tested is both generic_fns.mol_res_spin.delete_spin() and
        prompt.spin.delete().
        """

        # Delete the first spin.
        self.spin_fns.delete(spin_id='@C8')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test that the first spin is now 6, C19.
        self.assertEqual(dp.mol[0].res[0].spin[0].num, 6)
        self.assertEqual(dp.mol[0].res[0].spin[0].name, 'C19')
        self.assert_(not hasattr(dp.mol[0].res[0].spin[0], 'x'))


    def test_delete_spin_num(self):
        """Test spin deletion using spin number identifiers.

        The function tested is both generic_fns.mol_res_spin.delete_spin() and
        prompt.spin.delete().
        """

        # Delete the first spin.
        self.spin_fns.delete(spin_id='@111')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test that the first spin is now 6, C19.
        self.assertEqual(dp.mol[0].res[0].spin[0].num, 6)
        self.assertEqual(dp.mol[0].res[0].spin[0].name, 'C19')
        self.assert_(not hasattr(dp.mol[0].res[0].spin[0], 'x'))


    def test_delete_spin_all(self):
        """Test the deletion of all spins in one residue.

        The function tested is both generic_fns.mol_res_spin.delete_spin() and
        prompt.spin.delete().
        """

        # Delete all spins.
        self.spin_fns.delete(spin_id='@1-200')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test that the first spin defaults back to the empty spin.
        self.assertEqual(dp.mol[0].res[0].spin[0].num, None)
        self.assertEqual(dp.mol[0].res[0].spin[0].name, None)


    def test_delete_spin_shift(self):
        """Test the deletion of multiple spins.

        The function tested is both generic_fns.mol_res_spin.delete_spin() and
        prompt.spin.delete().
        """

        # Delete the first and third spins.
        self.spin_fns.delete(spin_id='@111,7')

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test that the remaining spins.
        self.assertEqual(dp.mol[0].res[0].spin[0].num, 6)
        self.assertEqual(dp.mol[0].res[0].spin[0].name, 'C19')
        self.assertEqual(dp.mol[0].res[0].spin[1].num, 8)
        self.assertEqual(dp.mol[0].res[0].spin[1].name, 'C24')
        self.assertEqual(dp.mol[0].res[0].spin[2].num, 9)
        self.assertEqual(dp.mol[0].res[0].spin[2].name, 'C26')


    def test_display_spin(self):
        """Test the display of spin information.

        The function tested is both generic_fns.mol_res_spin.display_spin() and
        prompt.spin.display().
        """

        # The following should all work without error.
        self.spin_fns.display()
        self.spin_fns.display(':1')
        self.spin_fns.display('#Old mol:1')
        self.spin_fns.display('#New mol:5')
        self.spin_fns.display('#New mol:6@3239')


    def test_name_spin(self):
        """Test the renaming of a spin.

        The function tested is both generic_fns.mol_res_spin.name_spin() and
        prompt.spin.name().
        """

        # Rename some spins.
        self.spin_fns.name(spin_id='@C26', name='C25', force=True)
        self.spin_fns.name(spin_id=':2@78', name='Ca', force=True)
        self.spin_fns.name(spin_id='#New mol:6@3239', name='NHe', force=True)

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test that the spins have been named (and that the others have not).
        self.assertEqual(dp.mol[0].res[0].spin[0].name, 'C8')
        self.assertEqual(dp.mol[0].res[0].spin[1].name, 'C19')
        self.assertEqual(dp.mol[0].res[0].spin[2].name, 'C21')
        self.assertEqual(dp.mol[0].res[0].spin[3].name, 'C24')
        self.assertEqual(dp.mol[0].res[0].spin[4].name, 'C25')
        self.assertEqual(dp.mol[0].res[1].spin[0].name, 'Ca')
        self.assertEqual(dp.mol[1].res[0].spin[0].name, 'NH')
        self.assertEqual(dp.mol[1].res[1].spin[0].name, None)
        self.assertEqual(dp.mol[1].res[1].spin[1].name, 'NHe')


    def test_name_spin_many(self):
        """Test the renaming of multiple spins.

        The function tested is both generic_fns.mol_res_spin.name_spin() and
        prompt.spin.name().
        """

        # Rename all NHs.
        self.spin_fns.name(spin_id='@NH', name='N', force=True)

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test the renaming of the NHs (and that the other spins have not changed).
        self.assertEqual(dp.mol[0].res[0].spin[0].name, 'C8')
        self.assertEqual(dp.mol[0].res[0].spin[1].name, 'C19')
        self.assertEqual(dp.mol[0].res[0].spin[2].name, 'C21')
        self.assertEqual(dp.mol[0].res[0].spin[3].name, 'C24')
        self.assertEqual(dp.mol[0].res[0].spin[4].name, 'C26')
        self.assertEqual(dp.mol[0].res[1].spin[0].name, 'N')
        self.assertEqual(dp.mol[1].res[0].spin[0].name, 'N')
        self.assertEqual(dp.mol[1].res[1].spin[0].name, None)
        self.assertEqual(dp.mol[1].res[1].spin[1].name, 'N')


    def test_number_spin(self):
        """Test the numbering of a spin.

        The function tested is both generic_fns.mol_res_spin.number_spin() and
        prompt.spin.number().
        """

        # Rename a few spins.
        self.spin_fns.number(spin_id='@111', number=1, force=True)
        self.spin_fns.number(spin_id='@6', number=2, force=True)
        self.spin_fns.number(spin_id='@7', number=3, force=True)
        self.spin_fns.number(spin_id='@8', number=4, force=True)
        self.spin_fns.number(spin_id='@9', number=5, force=True)
        self.spin_fns.number(spin_id='@78', number=6, force=True)
        self.spin_fns.number(spin_id='@239', number=7, force=True)
        self.spin_fns.number(spin_id='@3239', number=9, force=True)

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test that the spins have been numbered.
        self.assertEqual(dp.mol[0].res[0].spin[0].num, 1)
        self.assertEqual(dp.mol[0].res[0].spin[1].num, 2)
        self.assertEqual(dp.mol[0].res[0].spin[2].num, 3)
        self.assertEqual(dp.mol[0].res[0].spin[3].num, 4)
        self.assertEqual(dp.mol[0].res[0].spin[4].num, 5)
        self.assertEqual(dp.mol[0].res[1].spin[0].num, 6)
        self.assertEqual(dp.mol[1].res[0].spin[0].num, 7)
        self.assertEqual(dp.mol[1].res[1].spin[1].num, 9)


    def test_number_spin_many_fail(self):
        """Test the renaming of multiple spins.

        The function tested is both generic_fns.mol_res_spin.number_spin() and
        prompt.spin.number().
        """

        # Try numbering all NHs.
        self.assertRaises(RelaxError, self.spin_fns.number, spin_id='@NH', number=-6)
