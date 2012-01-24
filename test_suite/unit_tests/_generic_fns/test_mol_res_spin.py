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

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import mol_res_spin, pipes
from generic_fns.reset import reset
from relax_errors import RelaxError, RelaxNoPipeError
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_mol_res_spin(UnitTestCase):
    """Unit tests for the functions of the 'generic_fns.mol_res_spin' module."""

    def setUp(self):
        """Set up some molecules, residues, and spins for testing."""

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Name the first molecule.
        cdp.mol[0].name = 'Ap4Aase'

        # Add a second molecule to the system.
        cdp.mol.add_item(mol_name='RNA')

        # Add two more residues to the first molecule (and set the residue number of the first).
        cdp.mol[0].res[0].num = 1
        cdp.mol[0].res.add_item(res_num=2, res_name='Glu')
        cdp.mol[0].res.add_item(res_num=4, res_name='Pro')

        # Add some spin info to this molecule.
        cdp.mol[0].res[0].spin[0].name = 'NH'
        cdp.mol[0].res[0].spin[0].num = 60
        cdp.mol[0].res[1].spin[0].name = 'NH'
        cdp.mol[0].res[1].spin[0].num = 63

        # Add one more residue to the second molecule (and set the residue number of the first).
        cdp.mol[1].res[0].num = -5
        cdp.mol[1].res.add_item(res_num=-4)

        # Add a second set of spins to the second molecule (naming the first set first).
        cdp.mol[1].res[0].spin[0].name = 'C8'
        cdp.mol[1].res[1].spin[0].name = 'C8'
        cdp.mol[1].res[0].spin.add_item(spin_name='N5')
        cdp.mol[1].res[1].spin.add_item(spin_name='N5')
        cdp.mol[1].res[1].spin.add_item(spin_name='2H', spin_num=132)

        # Deselect a number of spins.
        cdp.mol[0].res[0].spin[0].select = 0
        cdp.mol[0].res[2].spin[0].select = 0
        cdp.mol[1].res[0].spin[0].select = 0
        cdp.mol[1].res[1].spin[1].select = 0


    def test_Selection_boolean_and(self):
        """Test the Selection object for boolean '&' mol-res-spin selections."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:4 & :Pro@Ca")

        # Test the highest level object.
        self.assertEqual(obj._union, None)
        self.assertNotEqual(obj._intersect, None)
        self.assertEqual(obj.molecules, [])
        self.assertEqual(obj.residues, [])
        self.assertEqual(obj.spins, [])

        # Test the first intersection.
        self.assertEqual(obj._intersect[0]._union, None)
        self.assertEqual(obj._intersect[0]._intersect, None)
        self.assertEqual(obj._intersect[0].molecules, ['Ap4Aase'])
        self.assertEqual(obj._intersect[0].residues, [4])
        self.assertEqual(obj._intersect[0].spins, [])

        # Test the second intersection.
        self.assertEqual(obj._intersect[1]._union, None)
        self.assertEqual(obj._intersect[1]._intersect, None)
        self.assertEqual(obj._intersect[1].molecules, [])
        self.assertEqual(obj._intersect[1].residues, ['Pro'])
        self.assertEqual(obj._intersect[1].spins, ['Ca'])


    def test_Selection_boolean_or(self):
        """Test the Selection object for boolean '|' mol-res-spin selections."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Test the highest level object.
        self.assertNotEqual(obj._union, None)
        self.assertEqual(obj._intersect, None)
        self.assertEqual(obj.molecules, [])
        self.assertEqual(obj.residues, [])
        self.assertEqual(obj.spins, [])

        # Test the 1st union.
        self.assertEqual(obj._union[0]._union, None)
        self.assertEqual(obj._union[0]._intersect, None)
        self.assertEqual(obj._union[0].molecules, ['Ap4Aase'])
        self.assertEqual(obj._union[0].residues, ['Glu'])
        self.assertEqual(obj._union[0].spins, [])

        # Test the 2nd union.
        self.assertEqual(obj._union[1]._union, None)
        self.assertEqual(obj._union[1]._intersect, None)
        self.assertEqual(obj._union[1].molecules, ['RNA'])
        self.assertEqual(obj._union[1].residues, [])
        self.assertEqual(obj._union[1].spins, ['C8'])


    def test_Selection_complex_boolean(self):
        """Test the Selection object for complex boolean mol-res-spin selections."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:4 & :Pro | #RNA")

        # Test the highest level object.
        self.assertNotEqual(obj._union, None)
        self.assertEqual(obj._intersect, None)
        self.assertEqual(obj.molecules, [])
        self.assertEqual(obj.residues, [])
        self.assertEqual(obj.spins, [])

        # Test the 1st union (this should be an intersection).
        self.assertEqual(obj._union[0]._union, None)
        self.assertNotEqual(obj._union[0]._intersect, None)
        self.assertEqual(obj._union[0].molecules, [])
        self.assertEqual(obj._union[0].residues, [])
        self.assertEqual(obj._union[0].spins, [])

        # Test the 2nd union.
        self.assertEqual(obj._union[1]._union, None)
        self.assertEqual(obj._union[1]._intersect, None)
        self.assertEqual(obj._union[1].molecules, ['RNA'])
        self.assertEqual(obj._union[1].residues, [])
        self.assertEqual(obj._union[1].spins, [])

        # Test the 1st union, 1st intersection.
        self.assertEqual(obj._union[0]._intersect[0]._union, None)
        self.assertEqual(obj._union[0]._intersect[0]._intersect, None)
        self.assertEqual(obj._union[0]._intersect[0].molecules, ['Ap4Aase'])
        self.assertEqual(obj._union[0]._intersect[0].residues, [4])
        self.assertEqual(obj._union[0]._intersect[0].spins, [])

        # Test the 1st union, 2nd intersection.
        self.assertEqual(obj._union[0]._intersect[1]._union, None)
        self.assertEqual(obj._union[0]._intersect[1]._intersect, None)
        self.assertEqual(obj._union[0]._intersect[1].molecules, [])
        self.assertEqual(obj._union[0]._intersect[1].residues, ['Pro'])
        self.assertEqual(obj._union[0]._intersect[1].spins, [])


    def test_Selection_contains_mol1(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the molecule 'RNA'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_mol('RNA'))


    def test_Selection_contains_mol2(self):
        """The Selection object "#Ap4Aase:Glu & #RNA@C8" does not contain the molecule 'RNA'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu & #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_mol('RNA'))


    def test_Selection_contains_mol3(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" does not contain the molecule 'XXX'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_mol('XXX'))


    def test_Selection_contains_mol4(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" does not contain the molecule None."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_mol())


    def test_Selection_contains_mol5(self):
        """The Selection object ":Glu" does contain the molecule None."""

        # The Selection object.
        obj = mol_res_spin.Selection(":Glu")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_mol())


    def test_Selection_contains_mol_re1(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the molecule 'R*'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_mol('R*'))


    def test_Selection_contains_mol_re2(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the molecule '*R*'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_mol('*R*'))


    def test_Selection_contains_res1(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" does not contain the res 'Glu' (without the mol name)."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_res(res_name='Glu'))


    def test_Selection_contains_res2(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the res 'Glu' of the mol 'Ap4Aase'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_res(res_name='Glu', mol='Ap4Aase'))


    def test_Selection_contains_res3(self):
        """The Selection object "#Ap4Aase:Glu & #RNA@C8" does not contain the res 'Glu'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu & #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_res(res_name='Glu'))


    def test_Selection_contains_res4(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" does not contain the res 'Ala'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_res(res_name='Ala'))


    def test_Selection_contains_res5(self):
        """The Selection object "#Ap4Aase:Glu | #RNA:14@C8" does not contain the res None."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA:14@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_res())


    def test_Selection_contains_res6(self):
        """The Selection object "#Ap4Aase" does contains the res None."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_res(mol='Ap4Aase'))


    def test_Selection_contains_res7(self):
        """The Selection object "#Ap4Aase" does not contain the res None of the mol 'RNA'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_res(mol='RNA'))


    def test_Selection_contains_res_re1(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the res 'G*' of the mol 'Ap4Aase'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_res(res_name='G*', mol='Ap4Aase'))


    def test_Selection_contains_res_re2(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the res '*G*' of the mol 'Ap4Aase'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_res(res_name='*G*', mol='Ap4Aase'))


    def test_Selection_contains_spin1(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" does not contain the spin 'C8' (without the mol name)."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_spin(spin_name='C8'))


    def test_Selection_contains_spin2(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the spin 'C8' of the mol 'RNA'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_spin(spin_name='C8', mol='RNA'))


    def test_Selection_contains_spin3(self):
        """The Selection object "#Ap4Aase:Glu & #RNA@C8" does not contain the spin 'C8'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu & #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_spin(spin_name='C8'))


    def test_Selection_contains_spin4(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" does not contain the spin 'N3'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_spin(spin_name='N3'))


    def test_Selection_contains_spin5(self):
        """The Selection object "#Ap4Aase:Glu | #RNA:14@C8" does not contain the spin None."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA:14@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_spin())


    def test_Selection_contains_spin6(self):
        """The Selection object "#Ap4Aase" does contains the spin None."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_spin(mol='Ap4Aase'))


    def test_Selection_contains_spin7(self):
        """The Selection object "#Ap4Aase" does not contain the spin None of the mol 'RNA'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_spin(mol='RNA'))


    def test_Selection_contains_spin_re1(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the spin 'C*' of the mol 'RNA'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_spin(spin_name='C*', mol='RNA'))


    def test_Selection_contains_spin_re2(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the spin '*C*' of the mol 'RNA'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_spin(spin_name='*C*', mol='RNA'))


    def test_Selection_full_spin_id(self):
        """Test the Selection object for the single spin identifier '#Ap4Aase:2&:Glu@63&@NH'."""

        # The Selection object.
        obj = mol_res_spin.Selection("#Ap4Aase:2&:Glu@63&@NH")

        # Test if various spins are in the selection.
        self.assert_((cdp.mol[0], cdp.mol[0].res[0], cdp.mol[0].res[0].spin[0]) not in obj)
        self.assert_((cdp.mol[0], cdp.mol[0].res[1], cdp.mol[0].res[1].spin[0]) in obj)
        self.assert_((cdp.mol[0], cdp.mol[0].res[2], cdp.mol[0].res[2].spin[0]) not in obj)
        self.assert_((cdp.mol[1], cdp.mol[1].res[0], cdp.mol[1].res[0].spin[0]) not in obj)
        self.assert_((cdp.mol[1], cdp.mol[1].res[0], cdp.mol[1].res[0].spin[1]) not in obj)
        self.assert_((cdp.mol[1], cdp.mol[1].res[1], cdp.mol[1].res[1].spin[0]) not in obj)
        self.assert_((cdp.mol[1], cdp.mol[1].res[1], cdp.mol[1].res[1].spin[1]) not in obj)


    def test_Selection_memory(self):
        """Test that the Selection object has no memory of previous selections."""

        # The original Selection object.
        obj = mol_res_spin.Selection(":1&:Glu@16&@N")

        # The new Selection object.
        obj = mol_res_spin.Selection(":13&:Pro")

        # Test the highest level object.
        self.assertEqual(obj._union, None)
        self.assertNotEqual(obj._intersect, None)
        self.assertEqual(obj.molecules, [])
        self.assertEqual(obj.residues, [])
        self.assertEqual(obj.spins, [])

        # Test the 1st intersection.
        self.assertEqual(obj._intersect[0]._union, None)
        self.assertEqual(obj._intersect[0]._intersect, None)
        self.assertEqual(obj._intersect[0].molecules, [])
        self.assertEqual(obj._intersect[0].residues, [13])
        self.assertEqual(obj._intersect[0].spins, [])

        # Test the 2nd intersection.
        self.assertEqual(obj._intersect[1]._union, None)
        self.assertEqual(obj._intersect[1]._intersect, None)
        self.assertEqual(obj._intersect[1].molecules, [])
        self.assertEqual(obj._intersect[1].residues, ['Pro'])
        self.assertEqual(obj._intersect[1].spins, [])


    def test_count_spins(self):
        """Test that the number of spins can be properly counted.

        The function tested is generic_fns.mol_res_spin.count_spins().
        """

        # Test the number of spins counted.
        self.assertEqual(mol_res_spin.count_spins(), 4)
        self.assertEqual(mol_res_spin.count_spins(skip_desel=False), 8)
        self.assertEqual(mol_res_spin.count_spins(selection='@N5'), 1)
        self.assertEqual(mol_res_spin.count_spins(selection='@N5', skip_desel=False), 2)


    def test_count_no_spins(self):
        """Test that the number of spins (zero) can be properly counted.

        The function tested is generic_fns.mol_res_spin.count_spins().
        """

        # Reset relax.
        reset()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Test the number of spins counted.
        self.assertEqual(mol_res_spin.count_spins(), 0)


    def test_count_spins_no_pipe(self):
        """Test that the counting of the number of spins raises an error when no pipe exists.

        The function tested is generic_fns.mol_res_spin.count_spins().
        """

        # Reset relax.
        reset()

        # Test for the error.
        self.assertRaises(RelaxNoPipeError, mol_res_spin.count_spins)


    def test_exists_mol_res_spin_data(self):
        """Test the function for determining if molecule-residue-spin data exists.

        The function tested is generic_fns.mol_res_spin.exists_mol_res_spin_data().
        """

        # This should be True.
        self.failUnless(mol_res_spin.exists_mol_res_spin_data())


    def test_exists_mol_res_spin_data_single_mol(self):
        """Determine if molecule-residue-spin data exists (with data for a single molecule).

        The function tested is generic_fns.mol_res_spin.exists_mol_res_spin_data().
        """

        # Reset relax.
        reset()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')
        dp = pipes.get_pipe('orig')

        # Name the first molecule.
        dp.mol[0].name = 'TOM40'

        # This should be True.
        self.failUnless(mol_res_spin.exists_mol_res_spin_data())


    def test_exists_mol_res_spin_data_single_res_name(self):
        """Determine if molecule-residue-spin data exists (when a single residue is named).

        The function tested is generic_fns.mol_res_spin.exists_mol_res_spin_data().
        """

        # Reset relax.
        reset()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')
        dp = pipes.get_pipe('orig')

        # Name the first residue.
        dp.mol[0].res[0].name = 'Lys'

        # This should be True.
        self.failUnless(mol_res_spin.exists_mol_res_spin_data())


    def test_exists_mol_res_spin_data_single_res_num(self):
        """Determine if molecule-residue-spin data exists (when a single residue is numbered).

        The function tested is generic_fns.mol_res_spin.exists_mol_res_spin_data().
        """

        # Reset relax.
        reset()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')
        dp = pipes.get_pipe('orig')

        # Number the first residue.
        dp.mol[0].res[0].num = 1

        # This should be True.
        self.failUnless(mol_res_spin.exists_mol_res_spin_data())


    def test_exists_mol_res_spin_data_single_spin_name(self):
        """Determine if molecule-residue-spin data exists (when a single spin is named).

        The function tested is generic_fns.mol_res_spin.exists_mol_res_spin_data().
        """

        # Reset relax.
        reset()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')
        dp = pipes.get_pipe('orig')

        # Name the first spin.
        dp.mol[0].res[0].spin[0].name = 'NH'

        # This should be True.
        self.failUnless(mol_res_spin.exists_mol_res_spin_data())


    def test_exists_mol_res_spin_data_single_spin_num(self):
        """Determine if molecule-residue-spin data exists (when a single spin is numbered).

        The function tested is generic_fns.mol_res_spin.exists_mol_res_spin_data().
        """

        # Reset relax.
        reset()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')
        dp = pipes.get_pipe('orig')

        # Number the first spin.
        dp.mol[0].res[0].spin[0].num = 234

        # This should be True.
        self.failUnless(mol_res_spin.exists_mol_res_spin_data())


    def test_exists_mol_res_spin_data_no_data(self):
        """Determine if molecule-residue-spin data exists when no data exists.

        The function tested is generic_fns.mol_res_spin.exists_mol_res_spin_data().
        """

        # Reset relax.
        reset()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # This should be False.
        self.failIf(mol_res_spin.exists_mol_res_spin_data())


    def test_exists_mol_res_spin_data_no_pipe(self):
        """Determine if molecule-residue-spin data exists when no data pipe exists.

        The function tested is generic_fns.mol_res_spin.exists_mol_res_spin_data().
        """

        # Reset relax.
        reset()

        # This should fail.
        self.assertRaises(RelaxNoPipeError, mol_res_spin.exists_mol_res_spin_data)


    def test_generate_spin_id_data_array1(self):
        """First test of the spin ID generation function.

        The function tested is generic_fns.mol_res_spin.generate_spin_id_data_array().
        """

        # The data.
        data = ['1', 'GLY']

        # The ID.
        id = mol_res_spin.generate_spin_id_data_array(data, res_num_col=1, res_name_col=2)

        # Test the string.
        self.assertEqual(id, ':1&:GLY')


    def test_generate_spin_id_data_array2(self):
        """Second test of the spin ID generation function.

        The function tested is generic_fns.mol_res_spin.generate_spin_id_data_array().
        """

        # The data.
        data = ['1', 'GLY', '234', 'NH']

        # The ID.
        id = mol_res_spin.generate_spin_id_data_array(data, res_num_col=1, res_name_col=2, spin_num_col=3, spin_name_col=4)

        # Test the string.
        self.assertEqual(id, ':1&:GLY@234&@NH')


    def test_generate_spin_id_data_array3(self):
        """Third test of the spin ID generation function.

        The function tested is generic_fns.mol_res_spin.generate_spin_id_data_array().
        """

        # The data.
        data = ['Ap4Aase', '234', 'NH']

        # The ID.
        id = mol_res_spin.generate_spin_id_data_array(data, mol_name_col=1, res_num_col=None, res_name_col=None, spin_num_col=2, spin_name_col=3)

        # Test the string.
        self.assertEqual(id, '#Ap4Aase@234&@NH')


    def test_generate_spin_id_data_array4(self):
        """Fourth test of the spin ID generation function.

        The function tested is generic_fns.mol_res_spin.generate_spin_id_data_array().
        """

        # The data.
        data = ['Ap4Aase', '1', 'GLY']

        # The ID.
        id = mol_res_spin.generate_spin_id_data_array(data, mol_name_col=1, res_num_col=2, res_name_col=3)

        # Test the string.
        self.assertEqual(id, '#Ap4Aase:1&:GLY')


    def test_generate_spin_id_data_array5(self):
        """Fifth test of the spin ID generation function.

        The function tested is generic_fns.mol_res_spin.generate_spin_id_data_array().
        """

        # The data.
        data = ['Ap4Aase', '1', 'GLY', '234', 'NH']

        # The ID.
        id = mol_res_spin.generate_spin_id_data_array(data, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5)

        # Test the string.
        self.assertEqual(id, '#Ap4Aase:1&:GLY@234&@NH')


    def test_generate_spin_id_data_array6(self):
        """Sixth test of the spin ID generation function.

        The function tested is generic_fns.mol_res_spin.generate_spin_id_data_array().
        """

        # The data.
        data = ['1', 'GLY', None, None]

        # The ID.
        id = mol_res_spin.generate_spin_id_data_array(data, res_num_col=1, res_name_col=2)

        # Test the string.
        self.assertEqual(id, ':1&:GLY')


    def test_molecule_loop(self):
        """Test the proper operation of the molecule loop with molecule selection.

        The function tested is generic_fns.mol_res_spin.molecule_loop().
        """

        # Loop over the molecules.
        for mol in mol_res_spin.molecule_loop('#RNA'):
            # Test the molecule name.
            self.assertEqual(mol.name, 'RNA')

        # Test loop length.
        self.assertEqual(len(list(mol_res_spin.molecule_loop('#RNA'))), 1)


    def test_molecule_loop_no_data(self):
        """Test the proper operation of the molecule loop when no data is present.

        The function tested is generic_fns.mol_res_spin.molecule_loop().
        """

        # Reset relax.
        reset()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Loop over the molecules.
        i = 0
        for molecule in mol_res_spin.molecule_loop():
            i = i + 1

        # Test loop length.
        self.assertEqual(i, 0)


    def test_molecule_loop_no_pipe(self):
        """Test the proper operation of the molecule loop when no data pipe is present.

        The function tested is generic_fns.mol_res_spin.molecule_loop().
        """

        # Reset relax.
        reset()

        # Function for the problem of catching an error in a generator function.
        def fail_test():
            for molecule in mol_res_spin.molecule_loop():
                pass

        # Test for the no pipe error.
        self.assertRaises(RelaxNoPipeError, fail_test)


    def test_molecule_loop_no_selection(self):
        """Test the proper operation of the molecule loop when no selection is present.

        The function tested is generic_fns.mol_res_spin.molecule_loop().
        """

        # Molecule data.
        name = ['Ap4Aase', 'RNA']

        # Loop over the molecules.
        i = 0
        for mol in mol_res_spin.molecule_loop():
            # Test the molecule names.
            self.assertEqual(mol.name, name[i])

            # Increment i.
            i = i + 1

        # Test loop length.
        self.assertEqual(len(list(mol_res_spin.molecule_loop())), 2)



    def test_parse_token_single_element_num(self):
        """Test the generic_fns.mol_res_spin.parse_token() function on the string '1'."""

        # Parse the token.
        list = mol_res_spin.parse_token('1')

        # Check the list elements.
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], 1)


    def test_parse_token_single_element_neg_num(self):
        """Test the generic_fns.mol_res_spin.parse_token() function on the string '-4'."""

        # Parse the token.
        list = mol_res_spin.parse_token('-4')

        # Check the list elements.
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], -4)


    def test_parse_token_single_element_name(self):
        """Test the generic_fns.mol_res_spin.parse_token() function on the string 'G'."""

        # Parse the token.
        list = mol_res_spin.parse_token('G')

        # Check the list elements.
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], 'G')


    def test_parse_token_single_element_wildcard_name(self):
        """Test the generic_fns.mol_res_spin.parse_token() function on the string 'N*'."""

        # Parse the token.
        list = mol_res_spin.parse_token('N*')

        # Check the list elements.
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], 'N*')


    def test_parse_token_single_element_range(self):
        """Test the generic_fns.mol_res_spin.parse_token() function on the string '1-10'."""

        # Parse the token.
        list = mol_res_spin.parse_token('1-10')

        # Check the list elements.
        self.assertEqual(len(list), 10)
        for i in range(1, 11):
            self.assertEqual(list[i-1], i)


    def test_parse_token_single_element_neg_range(self):
        """Test the generic_fns.mol_res_spin.parse_token() function on the string '-10--1'."""

        # Parse the token.
        list = mol_res_spin.parse_token('-10--1')

        # Check the list elements.
        self.assertEqual(len(list), 10)
        j = 0
        for i in range(-10, -2):
            self.assertEqual(list[j], i)
            j = j + 1


    def test_parse_token_multi_element_num(self):
        """Test the generic_fns.mol_res_spin.parse_token() function on the string '-2, 1'."""

        # Parse the token.
        list = mol_res_spin.parse_token('-2, 1')

        # Check the list elements.
        self.assertEqual(len(list), 2)
        self.assertEqual(list[0], -2)
        self.assertEqual(list[1], 1)


    def test_parse_token_multi_element_name(self):
        """Test the generic_fns.mol_res_spin.parse_token() function on the string 'N,CA'."""

        # Parse the token.
        list = mol_res_spin.parse_token('N,CA')

        # Check the list elements.
        self.assertEqual(len(list), 2)
        self.assertEqual(list[0], 'CA')
        self.assertEqual(list[1], 'N')


    def test_parse_token_multi_element_num_name(self):
        """Test the generic_fns.mol_res_spin.parse_token() function on the string '76,Ala'."""

        # Parse the token.
        list = mol_res_spin.parse_token('76,Ala')

        # Check the list elements.
        self.assertEqual(len(list), 2)
        self.assertEqual(list[0], 76)
        self.assertEqual(list[1], 'Ala')


    def test_parse_token_multi_element_num_range(self):
        """Test the generic_fns.mol_res_spin.parse_token() function on the string '1,3-5'."""

        # Parse the token.
        list = mol_res_spin.parse_token('1,3-5')

        # Check the list elements.
        self.assertEqual(len(list), 4)
        self.assertEqual(list[0], 1)
        self.assertEqual(list[1], 3)
        self.assertEqual(list[2], 4)
        self.assertEqual(list[3], 5)


    def test_parse_token_multi_element_range_name(self):
        """Test the generic_fns.mol_res_spin.parse_token() function on the string '3-5,NH'."""

        # Parse the token.
        list = mol_res_spin.parse_token('3-5,NH')

        # Check the list elements.
        self.assertEqual(len(list), 4)
        self.assertEqual(list[0], 3)
        self.assertEqual(list[1], 4)
        self.assertEqual(list[2], 5)
        self.assertEqual(list[3], 'NH')


    def test_parse_token_multi_element_range_num_name(self):
        """Test the generic_fns.mol_res_spin.parse_token() function on the string '3-6, 8, Gly'."""

        # Parse the token.
        list = mol_res_spin.parse_token('3-6, 8, Gly')

        # Check the list elements.
        self.assertEqual(len(list), 6)
        self.assertEqual(list[0], 3)
        self.assertEqual(list[1], 4)
        self.assertEqual(list[2], 5)
        self.assertEqual(list[3], 6)
        self.assertEqual(list[4], 8)
        self.assertEqual(list[5], 'Gly')


    def test_residue_loop(self):
        """Test the proper operation of the residue loop with residue selection.

        The function tested is generic_fns.mol_res_spin.residue_loop().
        """

        # Loop over the residues.
        for res in mol_res_spin.residue_loop('#Ap4Aase:Glu'):
            # Test the selection.
            self.assertEqual(res.num, 2)

        # Test loop length.
        self.assertEqual(len(list(mol_res_spin.residue_loop('#Ap4Aase:Glu'))), 1)


    def test_residue_loop_no_data(self):
        """Test the proper operation of the residue loop when no data is present.

        The function tested is generic_fns.mol_res_spin.residue_loop().
        """

        # Reset relax.
        reset()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Loop over the residues.
        i = 0
        for residue in mol_res_spin.residue_loop():
            i = i + 1

        # Test loop length.
        self.assertEqual(i, 0)


    def test_residue_loop_no_pipe(self):
        """Test the proper operation of the residue loop when no data pipe is present.

        The function tested is generic_fns.mol_res_spin.residue_loop().
        """

        # Reset relax.
        reset()

        # Function for the problem of catching an error in a generator function.
        def fail_test():
            for residue in mol_res_spin.residue_loop():
                pass

        # Test for the no pipe error.
        self.assertRaises(RelaxNoPipeError, fail_test)


    def test_residue_loop_no_selection(self):
        """Test the proper operation of the residue loop when no selection is present.

        The function tested is generic_fns.mol_res_spin.residue_loop().
        """

        # Spin data.
        num = [1, 2, 4, -5, -4]
        name = [None, 'Glu', 'Pro', None, None]

        # Loop over the residues.
        i = 0
        for res in mol_res_spin.residue_loop():
            # Test the residue numbers.
            self.assertEqual(res.num, num[i])

            # Test the residue names.
            self.assertEqual(res.name, name[i])

            # Increment i.
            i = i + 1

        # Test loop length.
        self.assertEqual(i, 5)


    def test_return_molecule(self):
        """Test the function for returning the desired molecule data container.

        The function tested is generic_fns.mol_res_spin.return_molecule().
        """

        # Ask for a few molecules.
        mol1 = mol_res_spin.return_molecule('#Ap4Aase')
        mol2 = mol_res_spin.return_molecule(selection='#RNA', pipe='orig')

        # Test the data of molecule 1.
        self.assertEqual(mol1.name, 'Ap4Aase')

        # Test the data of molecule 2.
        self.assertEqual(mol2.name, 'RNA')


    def test_return_molecule_pipe_fail(self):
        """Test the failure of the function for returning the desired molecule data container.

        The function tested is generic_fns.mol_res_spin.return_molecule().
        """

        # Try to get a molecule from a missing data pipe.
        self.assertRaises(RelaxNoPipeError, mol_res_spin.return_molecule, selection='#Ap4Aase', pipe='new')
        self.assertRaises(RelaxNoPipeError, mol_res_spin.return_molecule, selection='#RNA', pipe='new')


    def test_return_residue(self):
        """Test the function for returning the desired residue data container.

        The function tested is generic_fns.mol_res_spin.return_residue().
        """

        # Ask for a few residues.
        res1 = mol_res_spin.return_residue(':1')
        res2 = mol_res_spin.return_residue(selection=':2')
        res4 = mol_res_spin.return_residue(selection=':4', pipe='orig')
        res5 = mol_res_spin.return_residue(selection='#RNA:-5', pipe='orig')

        # Test the data of residue 1.
        self.assertEqual(res1.num, 1)
        self.assertEqual(res1.name, None)

        # Test the data of residue 2.
        self.assertEqual(res2.num, 2)
        self.assertEqual(res2.name, 'Glu')

        # Test the data of residue 4.
        self.assertEqual(res4.num, 4)
        self.assertEqual(res4.name, 'Pro')

        # Test the data of the RNA residue -5.
        self.assertEqual(res5.num, -5)
        self.assertEqual(res5.name, None)
        self.assertEqual(res5.spin[1].name, 'N5')


    def test_return_residue_pipe_fail(self):
        """Test the failure of the function for returning the desired residue data container.

        The function tested is generic_fns.mol_res_spin.return_residue().
        """

        # Try to get a residue from a missing data pipe.
        self.assertRaises(RelaxNoPipeError, mol_res_spin.return_residue, selection=':2', pipe='new')


    def test_return_single_residue_info(self):
        """Test the function for returning the desired residue data container.

        The function tested is generic_fns.mol_res_spin.return_single_residue_info().
        """

        # Ask for a few residues.
        res1 = mol_res_spin.return_single_residue_info('1')
        res2 = mol_res_spin.return_single_residue_info('2,Glu')
        res4 = mol_res_spin.return_single_residue_info('Pro,4')
        res5 = mol_res_spin.return_single_residue_info('-5')

        # Test the data of residue 1.
        self.assertEqual(res1, (1, None))

        # Test the data of residue 2.
        self.assertEqual(res2, (2, 'Glu'))

        # Test the data of residue 4.
        self.assertEqual(res4, (4, 'Pro'))

        # Test the data of the RNA residue -5.
        self.assertEqual(res5, (-5, None))


    def test_return_single_residue_info_fail(self):
        """Test the failure of the function for returning the desired residue data container.

        The function tested is generic_fns.mol_res_spin.return_single_residue_info().
        """

        # Ask for a few residues.
        self.assertRaises(RelaxError, mol_res_spin.return_single_residue_info, '1,2')
        self.assertRaises(RelaxError, mol_res_spin.return_single_residue_info, '1,Glu,Pro')
        self.assertRaises(RelaxError, mol_res_spin.return_single_residue_info, '1,2,Glu,Pro')


    def test_return_spin(self):
        """Test the function for returning the desired spin data container.

        The function tested is generic_fns.mol_res_spin.return_spin().
        """

        # Ask for a few spins.
        spin1 = mol_res_spin.return_spin(':1')
        spin2 = mol_res_spin.return_spin(selection=':2&:Glu')
        spin3 = mol_res_spin.return_spin(selection=':4&:Pro', pipe='orig')
        spin4 = mol_res_spin.return_spin(selection='#RNA:-5@N5', pipe='orig')
        spin5 = mol_res_spin.return_spin(selection=':-4@2H', pipe='orig')

        # Test the data of spin 1.
        self.assertNotEqual(spin1, None)
        self.assertEqual(spin1.num, 60)
        self.assertEqual(spin1.name, 'NH')

        # Test the data of spin 2.
        self.assertNotEqual(spin2, None)
        self.assertEqual(spin2.num, 63)
        self.assertEqual(spin2.name, 'NH')

        # Test the data of spin 3.
        self.assertNotEqual(spin3, None)
        self.assertEqual(spin3.num, None)
        self.assertEqual(spin3.name, None)

        # Test the data of the RNA res -5, spin N5.
        self.assertNotEqual(spin4, None)
        self.assertEqual(spin4.num, None)
        self.assertEqual(spin4.name, 'N5')

        # Test the data of the RNA res -4, spin 2H.
        self.assertNotEqual(spin5, None)
        self.assertEqual(spin5.num, 132)
        self.assertEqual(spin5.name, '2H')


    def test_return_spin_pipe_fail(self):
        """Test the failure of the function for returning the desired spin data container.

        The function tested is generic_fns.mol_res_spin.return_spin().
        """

        # Try to get a spin from a missing data pipe.
        self.assertRaises(RelaxNoPipeError, mol_res_spin.return_spin, selection=':2', pipe='new')


    def test_spin_loop(self):
        """Test the proper operation of the spin loop with spin selection.

        The function tested is generic_fns.mol_res_spin.spin_loop().
        """

        # Spin data.
        select = [1, 0]

        # Loop over the spins.
        i = 0
        for spin in mol_res_spin.spin_loop('@N5'):
            # Test the selection.
            self.assertEqual(spin.select, select[i])

            # Test the spin names.
            self.assertEqual(spin.name, 'N5')

            # Increment i.
            i = i + 1

        # Test loop length.
        self.assertEqual(i, 2)


    def test_spin_loop_boolean_or(self):
        """Test the operation of the spin loop with the selection "#Ap4Aase:Glu | #RNA@C8".

        The function tested is generic_fns.mol_res_spin.spin_loop().
        """

        # Selection, and spin name and number.
        select = [1, 0, 1]
        name = ['NH', 'C8', 'C8']
        num = [63, None, None]

        # Loop over the spins.
        i = 0
        for spin in mol_res_spin.spin_loop("#Ap4Aase:Glu | #RNA@C8"):
            # Test the spin.
            self.assertEqual([spin.select, spin.name, spin.num], [select[i], name[i], num[i]])

            # Increment i.
            i = i + 1

        # Test loop length.
        self.assertEqual(i, 3)


    def test_spin_loop_multiatom(self):
        """Test the proper operation of the spin loop with spin selection '@NH|@N5'.

        The function tested is generic_fns.mol_res_spin.spin_loop().
        """

        # Spin data.
        select = [0, 1, 1, 0]
        name = ['NH', 'NH', 'N5', 'N5']

        # Loop over the spins.
        i = 0
        for spin in mol_res_spin.spin_loop('@NH|@N5'):
            # Test the selection.
            self.assertEqual(spin.select, select[i])

            # Test the spin names.
            self.assertEqual(spin.name, name[i])

            # Increment i.
            i = i + 1

        # Test loop length.
        self.assertEqual(i, 4)


    def test_spin_loop_no_data(self):
        """Test the proper operation of the spin loop when no data is present.

        The function tested is generic_fns.mol_res_spin.spin_loop().
        """

        # Reset relax.
        reset()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Loop over the spins.
        i = 0
        for spin in mol_res_spin.spin_loop():
            i = i + 1

        # Test loop length.
        self.assertEqual(i, 0)


    def test_spin_loop_no_pipe(self):
        """Test the proper operation of the spin loop when no data pipe is present.

        The function tested is generic_fns.mol_res_spin.spin_loop().
        """

        # Reset relax.
        reset()

        # Function for the problem of catching an error in a generator function.
        def fail_test():
            for spin in mol_res_spin.spin_loop():
                pass

        # Test for the no pipe error.
        self.assertRaises(RelaxNoPipeError, fail_test)


    def test_spin_loop_no_selection(self):
        """Test the proper operation of the spin loop when no selection is present.

        The function tested is generic_fns.mol_res_spin.spin_loop().
        """

        # Spin data.
        select = [0, 1, 0, 0, 1, 1, 0, 1]
        name = ['NH', 'NH', None, 'C8', 'N5', 'C8', 'N5', '2H']

        # Loop over the spins.
        i = 0
        for spin in mol_res_spin.spin_loop():
            # Test the selection.
            self.assertEqual(spin.select, select[i])

            # Test the spin names.
            self.assertEqual(spin.name, name[i])

            # Increment i.
            i = i + 1

        # Test loop length.
        self.assertEqual(i, 8)


    def test_spin_loop_single_spin(self):
        """Test the operation of the spin loop with the single spin selection '#Ap4Aase:Glu@63'.

        The function tested is generic_fns.mol_res_spin.spin_loop().
        """

        # Loop over the spins.
        i = 0
        for spin in mol_res_spin.spin_loop('#Ap4Aase:Glu@63'):
            # Test the selection.
            self.assertEqual(spin.select, 1)

            # Test the spin name.
            self.assertEqual(spin.name, 'NH')

            # Test the spin number.
            self.assertEqual(spin.num, 63)

            # Increment i.
            i = i + 1

        # Test loop length.
        self.assertEqual(i, 1)


    def test_spin_loop_wildcard(self):
        """Test the proper operation of the spin loop with wildcard spin selection '@N*'.

        The function tested is generic_fns.mol_res_spin.spin_loop().
        """

        # Spin data.
        select = [0, 1, 1, 0]
        name = ['NH', 'NH', 'N5', 'N5']

        # Loop over the spins.
        i = 0
        for spin in mol_res_spin.spin_loop('@N*'):
            # Test the selection.
            self.assertEqual(spin.select, select[i])

            # Test the spin names.
            self.assertEqual(spin.name, name[i])

            # Increment i.
            i = i + 1

        # Test loop length.
        self.assertEqual(i, 4)


    def test_tokenise1(self):
        """Test the generic_fns.mol_res_spin.tokenise() function on the string '@1'."""

        # Tokenise.
        mol_token, res_token, spin_token = mol_res_spin.tokenise('@1')

        # Check the tokens.
        self.assertEqual(mol_token, None)
        self.assertEqual(res_token, None)
        self.assertEqual(spin_token, '1')


    def test_tokenise2(self):
        """Test the generic_fns.mol_res_spin.tokenise() function on the string ':-4'."""

        # Tokenise.
        mol_token, res_token, spin_token = mol_res_spin.tokenise(':-4')

        # Check the tokens.
        self.assertEqual(mol_token, None)
        self.assertEqual(res_token, '-4')
        self.assertEqual(spin_token, None)


    def test_tokenise3(self):
        """Test the generic_fns.mol_res_spin.tokenise() function on the string '#CaM'."""

        # Tokenise.
        mol_token, res_token, spin_token = mol_res_spin.tokenise('#CaM')

        # Check the tokens.
        self.assertEqual(mol_token, 'CaM')
        self.assertEqual(res_token, None)
        self.assertEqual(spin_token, None)


    def test_tokenise4(self):
        """Test the generic_fns.mol_res_spin.tokenise() function on the string ':G@N3'."""

        # Tokenise.
        mol_token, res_token, spin_token = mol_res_spin.tokenise(':G@N3')

        # Check the tokens.
        self.assertEqual(mol_token, None)
        self.assertEqual(res_token, 'G')
        self.assertEqual(spin_token, 'N3')


    def test_tokenise5(self):
        """Test the generic_fns.mol_res_spin.tokenise() function on the string '#OMP@NH'."""

        # Tokenise.
        mol_token, res_token, spin_token = mol_res_spin.tokenise('#OMP@NH')

        # Check the tokens.
        self.assertEqual(mol_token, 'OMP')
        self.assertEqual(res_token, None)
        self.assertEqual(spin_token, 'NH')


    def test_tokenise6(self):
        """Test the generic_fns.mol_res_spin.tokenise() function on the string '#Lyso:20-50'."""

        # Tokenise.
        mol_token, res_token, spin_token = mol_res_spin.tokenise('#Lyso:20-50')

        # Check the tokens.
        self.assertEqual(mol_token, 'Lyso')
        self.assertEqual(res_token, '20-50')
        self.assertEqual(spin_token, None)


    def test_tokenise7(self):
        """Test the generic_fns.mol_res_spin.tokenise() function on the string '#Ap4Aase:*@N,CA'."""

        # Tokenise.
        mol_token, res_token, spin_token = mol_res_spin.tokenise('#Ap4Aase:*@N,CA')

        # Check the tokens.
        self.assertEqual(mol_token, 'Ap4Aase')
        self.assertEqual(res_token, '*')
        self.assertEqual(spin_token, 'N,CA')


    def test_tokenise8(self):
        """Test the generic_fns.mol_res_spin.tokenise() function on the string '@N*'."""

        # Tokenise.
        mol_token, res_token, spin_token = mol_res_spin.tokenise('@N*')

        # Check the tokens.
        self.assertEqual(mol_token, None)
        self.assertEqual(res_token, None)
        self.assertEqual(spin_token, 'N*')


    def test_tokenise_dup_atom_id_fail1(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '@N@1'.

        This tests for a duplicated atom identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '@N@1')


    def test_tokenise_dup_atom_id_fail2(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string ':*@N@1'.

        This tests for a duplicated atom identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, ':*@N@1')


    def test_tokenise_dup_atom_id_fail3(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '@N:*@1'.

        This tests for a duplicated atom identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '@N:*@1')


    def test_tokenise_dup_res_id_fail1(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string ':1:2'.

        This tests for a duplicated residue identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, ':1:2')


    def test_tokenise_dup_res_id_fail2(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '#None:1:Ala'.

        This tests for a duplicated residue identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '#None:1:Ala')


    def test_tokenise_dup_res_id_fail3(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string ':1:Ala@N'.

        This tests for a duplicated residue identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, ':1:Ala@N')


    def test_tokenise_dup_mol_id_fail1(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '#A#B'.

        This tests for a duplicated molecule identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '#A#B')


    def test_tokenise_dup_mol_id_fail2(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '#A#B:Leu'.

        This tests for a duplicated molecule identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '#A#B:Leu')


    def test_tokenise_dup_mol_id_fail3(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '#A#C@CA'.

        This tests for a duplicated molecule identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '#A#C@CA')


    def test_tokenise_out_of_order_atom_id_fail1(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '@CA#A'.

        This tests for an out of order '@' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '@CA#A')


    def test_tokenise_out_of_order_atom_id_fail2(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '@CA:Pro'.

        This tests for an out of order '@' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '@CA:Pro')


    def test_tokenise_out_of_order_atom_id_fail3(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '@CA#Z:Pro'.

        This tests for an out of order '@' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '@CA#Z:Pro')


    def test_tokenise_out_of_order_res_id_fail1(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '@CA:Pro'.

        This tests for an out of order ':' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '@CA:Pro')


    def test_tokenise_out_of_order_res_id_fail2(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string ':Glu#X'.

        This tests for an out of order ':' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, ':Glu#X')


    def test_tokenise_out_of_order_res_id_fail3(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '#1@12423:Glu'.

        This tests for an out of order ':' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, ':Glu#X')


    def test_tokenise_out_of_order_mol_id_fail1(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string ':1-160#A'.

        This tests for an out of order '#' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, ':1-160#A')


    def test_tokenise_out_of_order_mol_id_fail2(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '@N,CA#A'.

        This tests for an out of order '#' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '@N,CA#A')


    def test_tokenise_out_of_order_mol_id_fail3(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '@N:-10#Zip'.

        This tests for an out of order '#' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '@N:-10#Zip')


    def test_tokenise_bad_string_fail1(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string '13'.

        This tests for an improper selection string.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '13')


    def test_tokenise_bad_string_fail2(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string 'XXX'.

        This tests for an improper selection string.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, 'XXX')


    def test_tokenise_bad_string_fail3(self):
        """Test failure of the generic_fns.mol_res_spin.tokenise() function on the string ''.

        This tests for an improper selection string.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, mol_res_spin.tokenise, '')


    def test_boolean_and_selection(self):
        """Test boolean and in mol-res-spin selections."""

        # The selection loop:
        sel = list(mol_res_spin.residue_loop("#Ap4Aase:4 & :Pro"))

        # Test:
        self.assertEqual(len(sel), 1)
        for res in sel:
            self.assert_(res.name == "Pro" and res.num == 4)


    def test_boolean_complex_selection(self):
        """Test complex boolean mol-res-spin selections."""

        # The residue selection loop.
        sel = list(mol_res_spin.residue_loop("#Ap4Aase:4 & :Pro | #RNA"))

        # Residue names and numbers.
        names = ['Pro', None, None]
        numbers = [4, -5, -4]

        # The residues.
        self.assertEqual(len(sel), 3)
        for i in xrange(3):
            self.assertEqual(sel[i].name, names[i])
            self.assertEqual(sel[i].num, numbers[i])


    ######################################################
    # Test disabled until this functionality is enabled. #
    ######################################################
    def fixme_test_boolean_parenthesis_selection(self):
        """Test complex boolean mol-res-spin selections with parenthesis."""

        # The selection loop:
        sel = list(mol_res_spin.residue_loop("(#Ap4Aase & :Pro) | (#RNA & :-4)"))

        # Test:
        self.assertEqual(len(sel), 2)
        for res in sel:
            self.assert_(res.num in [-4, 4])
