###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxNoPipeError



class Spin_base_class:
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

        The IDs correspond to the molecule, residue and spin indecies.
        """

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')

        # Add a second data pipe for copying tests.
        relax_data_store.add(pipe_name='test', pipe_type='mf')

        # Set the current data pipe to 'orig'.
        relax_data_store.current_pipe = 'orig'

        # Alias the 'orig' relax data store.
        cdp = relax_data_store['orig']

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


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_copy_spin_between_molecules(self):
        """Test the copying of the spin data between different molecules.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy the spin '111' from the first molecule, first residue to the second molecule, fifth residue.
        self.spin.copy(spin_from='#Old mol:1@111', spin_to='#New mol:5@334')

        # Test the original spin.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].name, 'C8')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 1)

        # Test the new spin.
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].num, 5)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].name, 'Lys')
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].num, 239)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].name, 'NH')
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[1].num, 334)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[1].name, 'C8')
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[1].x, 1)


    def test_copy_spin_between_residues(self):
        """Test the copying of the spin data between different residues.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy the spin '111' from the first residue to the third residue.
        self.spin.copy(spin_from='#Old mol:1@111', spin_to='#Old mol:2')

        # Test the original spin.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].name, 'C8')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 1)

        # Test the new spin.
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].name, 'Arg')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].num, 78)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].name, 'NH')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[1].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[1].name, 'C8')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[1].x, 1)


    def test_copy_spin_between_pipes(self):
        """Test the copying of the spin data between different data pipes.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy the spin data.
        self.spin.copy(spin_from='#Old mol:1@111', pipe_to='test')

        # Change the first spin's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 222
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 2

        # Test the original spin.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 2)

        # Test the new spin.
        self.assertEqual(relax_data_store['test'].mol[0].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].spin[0].x, 1)


    def test_copy_spin_between_pipes_fail(self):
        """Test the copying of the spin data between different data pipes.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy the spin to the second data pipe.
        self.assertRaises(RelaxNoPipeError, self.spin.copy, spin_from='#Old mol:1@111', pipe_to='test2')



    def test_copy_spin_fail1(self):
        """Test the failure of the copying of the spin data of a non-existent residue.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy a non-existent residue (1 Met, @111).
        self.assertRaises(RelaxError, self.spin.copy, spin_from=':Met@111', spin_to=':2,Gly')


    def test_copy_spin_fail2(self):
        """Test the failure of the copying of the spin data of a non-existent spin.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy a non-existent spin (1 Ala, @234).
        self.assertRaises(RelaxError, self.spin.copy, spin_from=':Ala@234', spin_to=':2,Gly')


    def test_copy_spin_fail3(self):
        """Test the failure of the copying of the spin data to a non-existent residue.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy to a non-existent residue (3).
        self.assertRaises(RelaxError, self.spin.copy, spin_from='#Old mol:1@111', spin_to='#Old mol:3')


    def test_copy_spin_fail4(self):
        """Test the failure of the copying of the spin data to a number which already exists.

        The function tested is both generic_fns.mol_res_spin.copy_spin() and
        prompt.spin.copy().
        """

        # Copy a spin to a number which already exists.
        self.assertRaises(RelaxError, self.spin.copy, spin_from=':1', spin_to=':2@78')


    def test_create_spin(self):
        """Test the creation of a spin.

        The function tested is both generic_fns.mol_res_spin.create_spin() and
        prompt.spin.create().
        """

        # Create a few new spins.
        self.spin.create(1, 'C3')
        self.spin.create(2, 'C17')
        self.spin.create(-3, 'N7', res_id='#New mol:6')

        # Test that the spin numbers are correct.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[5].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[6].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[1].res[1].spin[2].num, -3)

        # Test that the spin names are correct.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[5].name, 'C3')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[6].name, 'C17')
        self.assertEqual(relax_data_store['orig'].mol[1].res[1].spin[2].name, 'N7')


    def test_create_spin_fail(self):
        """Test the failure of spin creation (by supplying two spins with the same number).

        The function tested is both generic_fns.mol_res_spin.create_spin() and
        prompt.spin.create().
        """

        # Create the first spin.
        self.spin.create(1, 'P1')

        # Assert that a RelaxError occurs when the next added spin has the same number as the first.
        self.assertRaises(RelaxError, self.spin.create, 1, 'P3')


    def test_delete_spin_name(self):
        """Test spin deletion using spin name identifiers.

        The function tested is both generic_fns.mol_res_spin.delete_spin() and
        prompt.spin.delete().
        """

        # Delete the first spin.
        self.spin.delete(spin_id='@C8')

        # Test that the first spin is now 6, C19.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 6)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].name, 'C19')
        self.assert_(not hasattr(relax_data_store['orig'].mol[0].res[0].spin[0], 'x'))


    def test_delete_spin_num(self):
        """Test spin deletion using spin number identifiers.

        The function tested is both generic_fns.mol_res_spin.delete_spin() and
        prompt.spin.delete().
        """

        # Delete the first spin.
        self.spin.delete(spin_id='@111')

        # Test that the first spin is now 6, C19.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 6)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].name, 'C19')
        self.assert_(not hasattr(relax_data_store['orig'].mol[0].res[0].spin[0], 'x'))


    def test_delete_spin_all(self):
        """Test the deletion of all spins in one residue.

        The function tested is both generic_fns.mol_res_spin.delete_spin() and
        prompt.spin.delete().
        """

        # Delete all spins.
        self.spin.delete(spin_id='@1-200')

        # Test that the first spin defaults back to the empty spin.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, None)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].name, None)


    def test_delete_spin_shift(self):
        """Test the deletion of multiple spins.

        The function tested is both generic_fns.mol_res_spin.delete_spin() and
        prompt.spin.delete().
        """

        # Delete the first and third spins.
        self.spin.delete(spin_id='@111,7')

        # Test that the remaining spins.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 6)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].name, 'C19')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[1].num, 8)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[1].name, 'C24')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[2].num, 9)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[2].name, 'C26')


    def test_display_spin(self):
        """Test the display of spin information.

        The function tested is both generic_fns.mol_res_spin.display_spin() and
        prompt.spin.display().
        """

        # The following should all work without error.
        self.spin.display()
        self.spin.display(':1')
        self.spin.display('#Old mol:1')
        self.spin.display('#New mol:5')
        self.spin.display('#New mol:6@3239')


    def test_name_spin(self):
        """Test the renaming of a spin.

        The function tested is both generic_fns.mol_res_spin.name_spin() and
        prompt.spin.name().
        """

        # Rename some spins.
        self.spin.name(spin_id='@C26', name='C25')
        self.spin.name(spin_id=':2@78', name='Ca')
        self.spin.name(spin_id='#New mol:6@3239', name='NHe')

        # Test that the spins have been named (and that the others have not).
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].name, 'C8')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[1].name, 'C19')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[2].name, 'C21')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[3].name, 'C24')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[4].name, 'C25')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].name, 'Ca')
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].name, 'NH')
        self.assertEqual(relax_data_store['orig'].mol[1].res[1].spin[0].name, None)
        self.assertEqual(relax_data_store['orig'].mol[1].res[1].spin[1].name, 'NHe')


    def test_name_spin_many(self):
        """Test the renaming of multiple spins.

        The function tested is both generic_fns.mol_res_spin.name_spin() and
        prompt.spin.name().
        """

        # Rename all NHs.
        self.spin.name(spin_id='@NH', name='N')

        # Test the renaming of the NHs (and that the other spins have not changed).
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].name, 'C8')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[1].name, 'C19')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[2].name, 'C21')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[3].name, 'C24')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[4].name, 'C26')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].name, 'N')
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].name, 'N')
        self.assertEqual(relax_data_store['orig'].mol[1].res[1].spin[0].name, None)
        self.assertEqual(relax_data_store['orig'].mol[1].res[1].spin[1].name, 'N')


    def test_number_spin(self):
        """Test the numbering of a spin.

        The function tested is both generic_fns.mol_res_spin.number_spin() and
        prompt.spin.number().
        """

        # Rename a few spins.
        self.spin.number(spin_id='@111', number=1)
        self.spin.number(spin_id='@6', number=2)
        self.spin.number(spin_id='@7', number=3)
        self.spin.number(spin_id='@8', number=4)
        self.spin.number(spin_id='@9', number=5)
        self.spin.number(spin_id='@78', number=6)
        self.spin.number(spin_id='@239', number=7)
        self.spin.number(spin_id='@3239', number=9)

        # Test that the spins have been numbered.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[1].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[2].num, 3)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[3].num, 4)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[4].num, 5)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].num, 6)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].num, 7)
        self.assertEqual(relax_data_store['orig'].mol[1].res[1].spin[1].num, 9)


    def test_number_spin_many_fail(self):
        """Test the renaming of multiple spins.

        The function tested is both generic_fns.mol_res_spin.number_spin() and
        prompt.spin.number().
        """

        # Try numbering all NHs.
        self.assertRaises(RelaxError, self.spin.number, spin_id='@NH', number=-6)
