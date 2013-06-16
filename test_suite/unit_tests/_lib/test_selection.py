###############################################################################
#                                                                             #
# Copyright (C) 2007-2013 Edward d'Auvergne                                   #
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

# relax module imports.
from lib.selection import Selection, parse_token, tokenise
from lib.errors import RelaxError
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_selection(UnitTestCase):
    """Unit tests for the functions of the 'lib.selection' module."""

    def test_Selection_boolean_and(self):
        """Test the Selection object for boolean '&' mol-res-spin selections."""

        # The Selection object.
        obj = Selection("#Ap4Aase:4 & :Pro@Ca")

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
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

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
        obj = Selection("#Ap4Aase:4 & :Pro | #RNA")

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
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_mol('RNA'))


    def test_Selection_contains_mol2(self):
        """The Selection object "#Ap4Aase:Glu & #RNA@C8" does not contain the molecule 'RNA'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu & #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_mol('RNA'))


    def test_Selection_contains_mol3(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" does not contain the molecule 'XXX'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_mol('XXX'))


    def test_Selection_contains_mol4(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" does not contain the molecule None."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_mol())


    def test_Selection_contains_mol5(self):
        """The Selection object ":Glu" does contain the molecule None."""

        # The Selection object.
        obj = Selection(":Glu")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_mol())


    def test_Selection_contains_mol_re1(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the molecule 'R*'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_mol('R*'))


    def test_Selection_contains_mol_re2(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the molecule '*R*'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_mol('*R*'))


    def test_Selection_contains_res1(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" does not contain the res 'Glu' (without the mol name)."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_res(res_name='Glu'))


    def test_Selection_contains_res2(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the res 'Glu' of the mol 'Ap4Aase'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_res(res_name='Glu', mol='Ap4Aase'))


    def test_Selection_contains_res3(self):
        """The Selection object "#Ap4Aase:Glu & #RNA@C8" does not contain the res 'Glu'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu & #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_res(res_name='Glu'))


    def test_Selection_contains_res4(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" does not contain the res 'Ala'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_res(res_name='Ala'))


    def test_Selection_contains_res5(self):
        """The Selection object "#Ap4Aase:Glu | #RNA:14@C8" does not contain the res None."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA:14@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_res())


    def test_Selection_contains_res6(self):
        """The Selection object "#Ap4Aase" does contains the res None."""

        # The Selection object.
        obj = Selection("#Ap4Aase")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_res(mol='Ap4Aase'))


    def test_Selection_contains_res7(self):
        """The Selection object "#Ap4Aase" does not contain the res None of the mol 'RNA'."""

        # The Selection object.
        obj = Selection("#Ap4Aase")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_res(mol='RNA'))


    def test_Selection_contains_res_re1(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the res 'G*' of the mol 'Ap4Aase'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_res(res_name='G*', mol='Ap4Aase'))


    def test_Selection_contains_res_re2(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the res '*G*' of the mol 'Ap4Aase'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_res(res_name='*G*', mol='Ap4Aase'))


    def test_Selection_contains_spin1(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" does not contain the spin 'C8' (without the mol name)."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_spin(spin_name='C8'))


    def test_Selection_contains_spin2(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the spin 'C8' of the mol 'RNA'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_spin(spin_name='C8', mol='RNA'))


    def test_Selection_contains_spin3(self):
        """The Selection object "#Ap4Aase:Glu & #RNA@C8" does not contain the spin 'C8'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu & #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_spin(spin_name='C8'))


    def test_Selection_contains_spin4(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" does not contain the spin 'N3'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_spin(spin_name='N3'))


    def test_Selection_contains_spin5(self):
        """The Selection object "#Ap4Aase:Glu | #RNA:14@C8" does not contain the spin None."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA:14@C8")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_spin())


    def test_Selection_contains_spin6(self):
        """The Selection object "#Ap4Aase" does contains the spin None."""

        # The Selection object.
        obj = Selection("#Ap4Aase")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_spin(mol='Ap4Aase'))


    def test_Selection_contains_spin7(self):
        """The Selection object "#Ap4Aase" does not contain the spin None of the mol 'RNA'."""

        # The Selection object.
        obj = Selection("#Ap4Aase")

        # Check if the molecule is in the selection.
        self.assert_(not obj.contains_spin(mol='RNA'))


    def test_Selection_contains_spin_re1(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the spin 'C*' of the mol 'RNA'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_spin(spin_name='C*', mol='RNA'))


    def test_Selection_contains_spin_re2(self):
        """The Selection object "#Ap4Aase:Glu | #RNA@C8" contains the spin '*C*' of the mol 'RNA'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:Glu | #RNA@C8")

        # Check if the molecule is in the selection.
        self.assert_(obj.contains_spin(spin_name='*C*', mol='RNA'))


    def test_Selection_full_spin_id(self):
        """Test the Selection object for the single spin identifier '#Ap4Aase:2@63'."""

        # The Selection object.
        obj = Selection("#Ap4Aase:2@63")

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
        obj = Selection(":1@16")

        # The new Selection object.
        obj = Selection(":13")

        # Test the highest level object.
        self.assertEqual(obj._union, None)
        self.assertEqual(obj._intersect, None)
        self.assertEqual(obj.molecules, [])
        self.assertEqual(obj.residues, [13])
        self.assertEqual(obj.spins, [])


    def test_Selection_range_contains_resid(self):
        """The Selection object ":1-70" contains the res ':1'."""

        # The Selection object.
        obj = Selection(":1-70")

        # Check that the residue ID is in the selection.
        self.assert_(':1' in obj)


    def test_Selection_range_contains_resid2(self):
        """The Selection object ":1-70" does not contain the res ':71'."""

        # The Selection object.
        obj = Selection(":1-70")

        # Check that the residue ID is in the selection.
        self.assert_(':71' not in obj)


    def test_Selection_range_contains_spinid(self):
        """The Selection object ":1-70" contains the spin ':1@N'."""

        # The Selection object.
        obj = Selection(":1-70")

        # Check that the residue ID is in the selection.
        self.assert_(':1@N' in obj)


    def test_Selection_range_contains_spinid2(self):
        """The Selection object ":1-70" does not contain the spin ':71@C'."""

        # The Selection object.
        obj = Selection(":1-70")

        # Check that the residue ID is in the selection.
        self.assert_(':71@C' not in obj)


    def test_parse_token_single_element_num(self):
        """Test the lib.selection.parse_token() function on the string '1'."""

        # Parse the token.
        list = parse_token('1')

        # Check the list elements.
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], 1)


    def test_parse_token_single_element_neg_num(self):
        """Test the lib.selection.parse_token() function on the string '-4'."""

        # Parse the token.
        list = parse_token('-4')

        # Check the list elements.
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], -4)


    def test_parse_token_single_element_name(self):
        """Test the lib.selection.parse_token() function on the string 'G'."""

        # Parse the token.
        list = parse_token('G')

        # Check the list elements.
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], 'G')


    def test_parse_token_single_element_wildcard_name(self):
        """Test the lib.selection.parse_token() function on the string 'N*'."""

        # Parse the token.
        list = parse_token('N*')

        # Check the list elements.
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0], 'N*')


    def test_parse_token_single_element_range(self):
        """Test the lib.selection.parse_token() function on the string '1-10'."""

        # Parse the token.
        list = parse_token('1-10')

        # Check the list elements.
        self.assertEqual(len(list), 10)
        for i in range(1, 11):
            self.assertEqual(list[i-1], i)


    def test_parse_token_single_element_neg_range(self):
        """Test the lib.selection.parse_token() function on the string '-10--1'."""

        # Parse the token.
        list = parse_token('-10--1')

        # Check the list elements.
        self.assertEqual(len(list), 10)
        j = 0
        for i in range(-10, -2):
            self.assertEqual(list[j], i)
            j = j + 1


    def test_parse_token_multi_element_num(self):
        """Test the lib.selection.parse_token() function on the string '-2, 1'."""

        # Parse the token.
        list = parse_token('-2, 1')

        # Check the list elements.
        self.assertEqual(len(list), 2)
        self.assertEqual(list[0], -2)
        self.assertEqual(list[1], 1)


    def test_parse_token_multi_element_name(self):
        """Test the lib.selection.parse_token() function on the string 'N,CA'."""

        # Parse the token.
        list = parse_token('N,CA')

        # Check the list elements.
        self.assertEqual(len(list), 2)
        self.assertEqual(list[0], 'N')
        self.assertEqual(list[1], 'CA')


    def test_parse_token_multi_element_num_name(self):
        """Test the lib.selection.parse_token() function on the string '76,Ala'."""

        # Parse the token.
        list = parse_token('76,Ala')

        # Check the list elements.
        self.assertEqual(len(list), 2)
        self.assertEqual(list[0], 76)
        self.assertEqual(list[1], 'Ala')


    def test_parse_token_multi_element_num_range(self):
        """Test the lib.selection.parse_token() function on the string '1,3-5'."""

        # Parse the token.
        list = parse_token('1,3-5')

        # Check the list elements.
        self.assertEqual(len(list), 4)
        self.assertEqual(list[0], 1)
        self.assertEqual(list[1], 3)
        self.assertEqual(list[2], 4)
        self.assertEqual(list[3], 5)


    def test_parse_token_multi_element_range_name(self):
        """Test the lib.selection.parse_token() function on the string '3-5,NH'."""

        # Parse the token.
        list = parse_token('3-5,NH')

        # Check the list elements.
        self.assertEqual(len(list), 4)
        self.assertEqual(list[0], 3)
        self.assertEqual(list[1], 4)
        self.assertEqual(list[2], 5)
        self.assertEqual(list[3], 'NH')


    def test_parse_token_multi_element_range_num_name(self):
        """Test the lib.selection.parse_token() function on the string '3-6, 8, Gly'."""

        # Parse the token.
        list = parse_token('3-6, 8, Gly')

        # Check the list elements.
        self.assertEqual(len(list), 6)
        self.assertEqual(list[0], 3)
        self.assertEqual(list[1], 4)
        self.assertEqual(list[2], 5)
        self.assertEqual(list[3], 6)
        self.assertEqual(list[4], 8)
        self.assertEqual(list[5], 'Gly')


    def test_tokenise1(self):
        """Test the lib.selection.tokenise() function on the string '@1'."""

        # Tokenise.
        mol_token, res_token, spin_token = tokenise('@1')

        # Check the tokens.
        self.assertEqual(mol_token, None)
        self.assertEqual(res_token, None)
        self.assertEqual(spin_token, '1')


    def test_tokenise2(self):
        """Test the lib.selection.tokenise() function on the string ':-4'."""

        # Tokenise.
        mol_token, res_token, spin_token = tokenise(':-4')

        # Check the tokens.
        self.assertEqual(mol_token, None)
        self.assertEqual(res_token, '-4')
        self.assertEqual(spin_token, None)


    def test_tokenise3(self):
        """Test the lib.selection.tokenise() function on the string '#CaM'."""

        # Tokenise.
        mol_token, res_token, spin_token = tokenise('#CaM')

        # Check the tokens.
        self.assertEqual(mol_token, 'CaM')
        self.assertEqual(res_token, None)
        self.assertEqual(spin_token, None)


    def test_tokenise4(self):
        """Test the lib.selection.tokenise() function on the string ':G@N3'."""

        # Tokenise.
        mol_token, res_token, spin_token = tokenise(':G@N3')

        # Check the tokens.
        self.assertEqual(mol_token, None)
        self.assertEqual(res_token, 'G')
        self.assertEqual(spin_token, 'N3')


    def test_tokenise5(self):
        """Test the lib.selection.tokenise() function on the string '#OMP@NH'."""

        # Tokenise.
        mol_token, res_token, spin_token = tokenise('#OMP@NH')

        # Check the tokens.
        self.assertEqual(mol_token, 'OMP')
        self.assertEqual(res_token, None)
        self.assertEqual(spin_token, 'NH')


    def test_tokenise6(self):
        """Test the lib.selection.tokenise() function on the string '#Lyso:20-50'."""

        # Tokenise.
        mol_token, res_token, spin_token = tokenise('#Lyso:20-50')

        # Check the tokens.
        self.assertEqual(mol_token, 'Lyso')
        self.assertEqual(res_token, '20-50')
        self.assertEqual(spin_token, None)


    def test_tokenise7(self):
        """Test the lib.selection.tokenise() function on the string '#Ap4Aase:*@N,CA'."""

        # Tokenise.
        mol_token, res_token, spin_token = tokenise('#Ap4Aase:*@N,CA')

        # Check the tokens.
        self.assertEqual(mol_token, 'Ap4Aase')
        self.assertEqual(res_token, '*')
        self.assertEqual(spin_token, 'N,CA')


    def test_tokenise8(self):
        """Test the lib.selection.tokenise() function on the string '@N*'."""

        # Tokenise.
        mol_token, res_token, spin_token = tokenise('@N*')

        # Check the tokens.
        self.assertEqual(mol_token, None)
        self.assertEqual(res_token, None)
        self.assertEqual(spin_token, 'N*')


    def test_tokenise_dup_atom_id_fail1(self):
        """Test failure of the lib.selection.tokenise() function on the string '@N@1'.

        This tests for a duplicated atom identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '@N@1')


    def test_tokenise_dup_atom_id_fail2(self):
        """Test failure of the lib.selection.tokenise() function on the string ':*@N@1'.

        This tests for a duplicated atom identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, ':*@N@1')


    def test_tokenise_dup_atom_id_fail3(self):
        """Test failure of the lib.selection.tokenise() function on the string '@N:*@1'.

        This tests for a duplicated atom identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '@N:*@1')


    def test_tokenise_dup_res_id_fail1(self):
        """Test failure of the lib.selection.tokenise() function on the string ':1:2'.

        This tests for a duplicated residue identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, ':1:2')


    def test_tokenise_dup_res_id_fail2(self):
        """Test failure of the lib.selection.tokenise() function on the string '#None:1:Ala'.

        This tests for a duplicated residue identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '#None:1:Ala')


    def test_tokenise_dup_res_id_fail3(self):
        """Test failure of the lib.selection.tokenise() function on the string ':1:Ala@N'.

        This tests for a duplicated residue identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, ':1:Ala@N')


    def test_tokenise_dup_mol_id_fail1(self):
        """Test failure of the lib.selection.tokenise() function on the string '#A#B'.

        This tests for a duplicated molecule identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '#A#B')


    def test_tokenise_dup_mol_id_fail2(self):
        """Test failure of the lib.selection.tokenise() function on the string '#A#B:Leu'.

        This tests for a duplicated molecule identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '#A#B:Leu')


    def test_tokenise_dup_mol_id_fail3(self):
        """Test failure of the lib.selection.tokenise() function on the string '#A#C@CA'.

        This tests for a duplicated molecule identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '#A#C@CA')


    def test_tokenise_out_of_order_atom_id_fail1(self):
        """Test failure of the lib.selection.tokenise() function on the string '@CA#A'.

        This tests for an out of order '@' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '@CA#A')


    def test_tokenise_out_of_order_atom_id_fail2(self):
        """Test failure of the lib.selection.tokenise() function on the string '@CA:Pro'.

        This tests for an out of order '@' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '@CA:Pro')


    def test_tokenise_out_of_order_atom_id_fail3(self):
        """Test failure of the lib.selection.tokenise() function on the string '@CA#Z:Pro'.

        This tests for an out of order '@' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '@CA#Z:Pro')


    def test_tokenise_out_of_order_res_id_fail1(self):
        """Test failure of the lib.selection.tokenise() function on the string '@CA:Pro'.

        This tests for an out of order ':' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '@CA:Pro')


    def test_tokenise_out_of_order_res_id_fail2(self):
        """Test failure of the lib.selection.tokenise() function on the string ':Glu#X'.

        This tests for an out of order ':' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, ':Glu#X')


    def test_tokenise_out_of_order_res_id_fail3(self):
        """Test failure of the lib.selection.tokenise() function on the string '#1@12423:Glu'.

        This tests for an out of order ':' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, ':Glu#X')


    def test_tokenise_out_of_order_mol_id_fail1(self):
        """Test failure of the lib.selection.tokenise() function on the string ':1-160#A'.

        This tests for an out of order '#' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, ':1-160#A')


    def test_tokenise_out_of_order_mol_id_fail2(self):
        """Test failure of the lib.selection.tokenise() function on the string '@N,CA#A'.

        This tests for an out of order '#' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '@N,CA#A')


    def test_tokenise_out_of_order_mol_id_fail3(self):
        """Test failure of the lib.selection.tokenise() function on the string '@N:-10#Zip'.

        This tests for an out of order '#' identifier.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '@N:-10#Zip')


    def test_tokenise_bad_string_fail1(self):
        """Test failure of the lib.selection.tokenise() function on the string '13'.

        This tests for an improper selection string.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '13')


    def test_tokenise_bad_string_fail2(self):
        """Test failure of the lib.selection.tokenise() function on the string 'XXX'.

        This tests for an improper selection string.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, 'XXX')


    def test_tokenise_bad_string_fail3(self):
        """Test failure of the lib.selection.tokenise() function on the string ''.

        This tests for an improper selection string.
        """

        # Tokenise an invalid string.
        self.assertRaises(RelaxError, tokenise, '')
