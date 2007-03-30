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
from relax_errors import RelaxError


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
        name = ['Ap4Aase', 'RNA']

        # Loop over the molecules.
        i = 0
        for mol in selection.molecule_loop():
            # Test the molecule names.
            self.assertEqual(mol.name, name[i])

            # Increment i.
            i = i + 1


    def test_parse_token_single_element_num(self):
        """Test the generic_fns.selection.parse_token() function on the string '1'."""

        # Parse the token.
        list = selection.parse_token('1')

        # Check the list elements.
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], 1)


    def test_parse_token_single_element_neg_num(self):
        """Test the generic_fns.selection.parse_token() function on the string '-4'."""

        # Parse the token.
        list = selection.parse_token('-4')

        # Check the list elements.
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], -4)


    def test_parse_token_single_element_name(self):
        """Test the generic_fns.selection.parse_token() function on the string 'G'."""

        # Parse the token.
        list = selection.parse_token('G')

        # Check the list elements.
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], 'G')


    def test_parse_token_single_element_range(self):
        """Test the generic_fns.selection.parse_token() function on the string '1-10'."""

        # Parse the token.
        list = selection.parse_token('1-10')

        # Check the list elements.
        self.assertEqual(len(list), 10)
        for i in range(1, 11):
            self.assertEqual(list[i-1], i)


    def test_parse_token_single_element_neg_range(self):
        """Test the generic_fns.selection.parse_token() function on the string '-10--1'."""

        # Parse the token.
        list = selection.parse_token('-10--1')

        # Check the list elements.
        self.assertEqual(len(list), 10)
        j = 0
        for i in range(-10, -2):
            self.assertEqual(list[j], i)
            j = j + 1


    def test_parse_token_multi_element_num(self):
        """Test the generic_fns.selection.parse_token() function on the string '-2, 1'."""

        # Parse the token.
        list = selection.parse_token('-2, 1')

        # Check the list elements.
        self.assertEqual(len(list), 2)
        self.assertEqual(list[0], -2)
        self.assertEqual(list[1], 1)


    def test_parse_token_multi_element_name(self):
        """Test the generic_fns.selection.parse_token() function on the string 'N,CA'."""

        # Parse the token.
        list = selection.parse_token('N,CA')

        # Check the list elements.
        self.assertEqual(len(list), 2)
        self.assertEqual(list[0], 'CA')
        self.assertEqual(list[1], 'N')


    def test_parse_token_multi_element_num_name(self):
        """Test the generic_fns.selection.parse_token() function on the string '76,Ala'."""

        # Parse the token.
        list = selection.parse_token('76,Ala')

        # Check the list elements.
        self.assertEqual(len(list), 2)
        self.assertEqual(list[0], 76)
        self.assertEqual(list[1], 'Ala')


    def test_parse_token_multi_element_num_range(self):
        """Test the generic_fns.selection.parse_token() function on the string '1,3-5'."""

        # Parse the token.
        list = selection.parse_token('1,3-5')

        # Check the list elements.
        self.assertEqual(len(list), 4)
        self.assertEqual(list[0], 1)
        self.assertEqual(list[1], 3)
        self.assertEqual(list[2], 4)
        self.assertEqual(list[3], 5)


    def test_parse_token_multi_element_range_name(self):
        """Test the generic_fns.selection.parse_token() function on the string '3-5,NH'."""

        # Parse the token.
        list = selection.parse_token('3-5,NH')

        # Check the list elements.
        self.assertEqual(len(list), 4)
        self.assertEqual(list[0], 3)
        self.assertEqual(list[1], 4)
        self.assertEqual(list[2], 5)
        self.assertEqual(list[3], 'NH')


    def test_parse_token_multi_element_range_num_name(self):
        """Test the generic_fns.selection.parse_token() function on the string '3-6, 8, Gly'."""

        # Parse the token.
        list = selection.parse_token('3-6, 8, Gly')

        # Check the list elements.
        self.assertEqual(len(list), 6)
        self.assertEqual(list[0], 3)
        self.assertEqual(list[1], 4)
        self.assertEqual(list[2], 5)
        self.assertEqual(list[3], 6)
        self.assertEqual(list[4], 8)
        self.assertEqual(list[5], 'Gly')


    def test_parse_token_range_fail1(self):
        """Failure of the generic_fns.selection.parse_token() function on the string '1-5-7'."""

        # Parse the invalid token.
        self.assertRaises(RelaxError, selection.parse_token, '1-5-7')


    def test_parse_token_range_fail2(self):
        """Failure of the generic_fns.selection.parse_token() function on the string '1--3'."""

        # Parse the invalid token.
        self.assertRaises(RelaxError, selection.parse_token, '1--3')


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
            self.assertEqual(res.num, num[i])

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

    def test_boolean_selection1(self):
        """Test boolean mol-res-spin selections."""

        # The selection object:
        sel = selection.Selection("#Ap4Aase | #RNA@N5")

    def test_tokenise1(self):
        """Test the generic_fns.selection.tokenise() function on the string '@1'."""

        # Tokenise.
        mol_token, res_token, spin_token = selection.tokenise('@1')

        # Check the tokens.
        self.assertEqual(mol_token, None)
        self.assertEqual(res_token, None)
        self.assertEqual(spin_token, '1')


    def test_tokenise2(self):
        """Test the generic_fns.selection.tokenise() function on the string ':-4'."""

        # Tokenise.
        mol_token, res_token, spin_token = selection.tokenise(':-4')

        # Check the tokens.
        self.assertEqual(mol_token, None)
        self.assertEqual(res_token, '-4')
        self.assertEqual(spin_token, None)


    def test_tokenise3(self):
        """Test the generic_fns.selection.tokenise() function on the string '#CaM'."""

        # Tokenise.
        mol_token, res_token, spin_token = selection.tokenise('#CaM')

        # Check the tokens.
        self.assertEqual(mol_token, 'CaM')
        self.assertEqual(res_token, None)
        self.assertEqual(spin_token, None)


    def test_tokenise4(self):
        """Test the generic_fns.selection.tokenise() function on the string ':G@N3'."""

        # Tokenise.
        mol_token, res_token, spin_token = selection.tokenise(':G@N3')

        # Check the tokens.
        self.assertEqual(mol_token, None)
        self.assertEqual(res_token, 'G')
        self.assertEqual(spin_token, 'N3')


    def test_tokenise5(self):
        """Test the generic_fns.selection.tokenise() function on the string '#OMP@NH'."""

        # Tokenise.
        mol_token, res_token, spin_token = selection.tokenise('#OMP@NH')

        # Check the tokens.
        self.assertEqual(mol_token, 'OMP')
        self.assertEqual(res_token, None)
        self.assertEqual(spin_token, 'NH')


    def test_tokenise6(self):
        """Test the generic_fns.selection.tokenise() function on the string '#Lyso:20-50'."""

        # Tokenise.
        mol_token, res_token, spin_token = selection.tokenise('#Lyso:20-50')

        # Check the tokens.
        self.assertEqual(mol_token, 'Lyso')
        self.assertEqual(res_token, '20-50')
        self.assertEqual(spin_token, None)


    def test_tokenise7(self):
        """Test the generic_fns.selection.tokenise() function on the string '#Ap4Aase:*@N,CA'."""

        # Tokenise.
        mol_token, res_token, spin_token = selection.tokenise('#Ap4Aase:*@N,CA')

        # Check the tokens.
        self.assertEqual(mol_token, 'Ap4Aase')
        self.assertEqual(res_token, '*')
        self.assertEqual(spin_token, 'N,CA')


    def test_tokenise_dup_atom_id_fail1(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '@N@1'.

        This tests for a duplicated atom identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '@N@1')


    def test_tokenise_dup_atom_id_fail2(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string ':*@N@1'.

        This tests for a duplicated atom identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, ':*@N@1')


    def test_tokenise_dup_atom_id_fail3(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '@N:*@1'.

        This tests for a duplicated atom identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '@N:*@1')


    def test_tokenise_dup_res_id_fail1(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string ':1:2'.

        This tests for a duplicated residue identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, ':1:2')


    def test_tokenise_dup_res_id_fail2(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '#None:1:Ala'.

        This tests for a duplicated residue identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '#None:1:Ala')


    def test_tokenise_dup_res_id_fail3(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string ':1:Ala@N'.

        This tests for a duplicated residue identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, ':1:Ala@N')


    def test_tokenise_dup_mol_id_fail1(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '#A#B'.

        This tests for a duplicated molecule identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '#A#B')


    def test_tokenise_dup_mol_id_fail2(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '#A#B:Leu'.

        This tests for a duplicated molecule identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '#A#B:Leu')


    def test_tokenise_dup_mol_id_fail3(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '#A#C@CA'.

        This tests for a duplicated molecule identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '#A#C@CA')


    def test_tokenise_out_of_order_atom_id_fail1(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '@CA#A'.

        This tests for an out of order '@' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '@CA#A')


    def test_tokenise_out_of_order_atom_id_fail2(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '@CA:Pro'.

        This tests for an out of order '@' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '@CA:Pro')


    def test_tokenise_out_of_order_atom_id_fail3(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '@CA#Z:Pro'.

        This tests for an out of order '@' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '@CA#Z:Pro')


    def test_tokenise_out_of_order_res_id_fail1(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '@CA:Pro'.

        This tests for an out of order ':' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '@CA:Pro')


    def test_tokenise_out_of_order_res_id_fail2(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string ':Glu#X'.

        This tests for an out of order ':' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, ':Glu#X')


    def test_tokenise_out_of_order_res_id_fail3(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '#1@12423:Glu'.

        This tests for an out of order ':' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, ':Glu#X')


    def test_tokenise_out_of_order_mol_id_fail1(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string ':1-160#A'.

        This tests for an out of order '#' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, ':1-160#A')


    def test_tokenise_out_of_order_mol_id_fail2(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '@N,CA#A'.

        This tests for an out of order '#' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '@N,CA#A')


    def test_tokenise_out_of_order_mol_id_fail3(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '@N:-10#Zip'.

        This tests for an out of order '#' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '@N:-10#Zip')


    def test_tokenise_bad_string_fail1(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string '13'.

        This tests for an improper selection string.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '13')


    def test_tokenise_bad_string_fail2(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string 'XXX'.

        This tests for an improper selection string.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, 'XXX')


    def test_tokenise_bad_string_fail3(self):
        """Test failure of the generic_fns.selection.tokenise() function on the string ''.

        This tests for an improper selection string.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, selection.tokenise, '')
   
   
    def test_boolean_or_selection(self):
        """Test boolean or in mol-res-spin selections."""

        self.assert_(list(selection.spin_loop("#Ap4Aase | #RNA@N5")) == list(selection.spin_loop())
   
                
    def test_boolean_and_selection(self):
        """Test boolean and in mol-res-spin selections."""
        
        # The selection loop:
        sel = selection.residue_loop("#Ap4Aase:4 & :Pro")
        
        # Test:
        for res in sel:
            self.assert_(res.name == "Pro" and res.num == 4)
       
                
    def test_boolean_complex_selection(self):
        """Test complex boolean mol-res-spin selections."""
        a syntax error
        # The selection loops:
        sel = selection.residue_loop("#Ap4Aase:4 & :Pro | #RNA@N5")

        # Test:
        for res in sel:
            self.assert_(res.num in [-5,-4,4])
