###############################################################################
#                                                                             #
# Copyright (C) 2006-2015 Edward d'Auvergne                                   #
# Copyright (C) 2013-2014 Troels E. Linnet                                    #
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

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Sequence(SystemTestCase):
    """Class for testing the sequence functions."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def test_align_molecules(self):
        """Test of the sequence.align user function."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'

        # Load the two rotated structures.
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=path, set_model_num=1, set_mol_name='CaM A')
        self.interpreter.structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=path, set_model_num=1, set_mol_name='CaM B')

        # Perform the alignment.
        self.interpreter.sequence.align(msa_algorithm='Central Star', algorithm='NW70', matrix='BLOSUM62', gap_open_penalty=10.0, gap_extend_penalty=1.0, end_gap_open_penalty=0.5, end_gap_extend_penalty=0.1)

        # Save the relax state.
        self.tmpfile = mktemp()
        self.interpreter.state.save(self.tmpfile, dir=None, force=True)

        # Reset relax.
        self.interpreter.reset()

        # Load the results.
        self.interpreter.state.load(self.tmpfile)

        # The real data.
        object_ids = ['mf', 'mf']
        models = [1, 1]
        molecules = ['CaM A', 'CaM B']
        sequences = [
            'EEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTAK***',
            'EEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTAK***'
        ]
        strings = [
            'EEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTAK***',
            'EEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTAK***'
        ]
        gaps = []
        for i in range(len(strings)):
            gaps.append([])
            for j in range(len(strings[0])):
                gaps[i].append(0)
        msa_algorithm = 'Central Star'
        pairwise_algorithm = 'NW70'
        matrix = 'BLOSUM62'
        gap_open_penalty = 10.0
        gap_extend_penalty = 1.0
        end_gap_open_penalty = 0.5
        end_gap_extend_penalty = 0.1

        # Check the data.
        for i in range(2):
            print("Checking \"%s\"" % molecules[i])
            self.assertEqual(ds.sequence_alignments[0].ids[i], ids[i])
            self.assertEqual(ds.sequence_alignments[0].object_ids[i], object_ids[i])
            self.assertEqual(ds.sequence_alignments[0].models[i], models[i])
            self.assertEqual(ds.sequence_alignments[0].molecules[i], molecules[i])
            self.assertEqual(ds.sequence_alignments[0].sequences[i], sequences[i])
            self.assertEqual(ds.sequence_alignments[0].strings[i], strings[i])
            self.assertEqual(ds.sequence_alignments[0].gaps[i], gaps[i])
            self.assertEqual(ds.sequence_alignments[0].msa_algorithm, msa_algorithm)
            self.assertEqual(ds.sequence_alignments[0].pairwise_algorithm, pairwise_algorithm)
            self.assertEqual(ds.sequence_alignments[0].matrix, matrix)
            self.assertEqual(ds.sequence_alignments[0].gap_open_penalty, gap_open_penalty)
            self.assertEqual(ds.sequence_alignments[0].gap_extend_penalty, gap_extend_penalty)
            self.assertEqual(ds.sequence_alignments[0].end_gap_open_penalty, end_gap_open_penalty)
            self.assertEqual(ds.sequence_alignments[0].end_gap_extend_penalty, end_gap_extend_penalty)


    def test_load_protein_asp_atoms_from_pdb(self):
        """Load all aspartic acid atoms from the single residue in a loaded protein PDB file."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)

        # Load all the ASP atoms (1 molecule, 1 ASP residue, and all atoms).
        self.interpreter.structure.load_spins(spin_id=':ASP')

        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'Ap4Aase_res1-12_mol1')
        self.assertEqual(len(cdp.mol[0].res), 1)

        # 1st residue.
        self.assertEqual(cdp.mol[0].res[0].num, 7)
        self.assertEqual(cdp.mol[0].res[0].name, 'ASP')
        self.assertEqual(len(cdp.mol[0].res[0].spin), 12)
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, 78)
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'N')
        self.assertEqual(cdp.mol[0].res[0].spin[1].num, 79)
        self.assertEqual(cdp.mol[0].res[0].spin[1].name, 'H')
        self.assertEqual(cdp.mol[0].res[0].spin[2].num, 80)
        self.assertEqual(cdp.mol[0].res[0].spin[2].name, 'CA')
        self.assertEqual(cdp.mol[0].res[0].spin[3].num, 81)
        self.assertEqual(cdp.mol[0].res[0].spin[3].name, 'HA')
        self.assertEqual(cdp.mol[0].res[0].spin[4].num, 82)
        self.assertEqual(cdp.mol[0].res[0].spin[4].name, 'CB')
        self.assertEqual(cdp.mol[0].res[0].spin[5].num, 83)
        self.assertEqual(cdp.mol[0].res[0].spin[5].name, '1HB')
        self.assertEqual(cdp.mol[0].res[0].spin[6].num, 84)
        self.assertEqual(cdp.mol[0].res[0].spin[6].name, '2HB')
        self.assertEqual(cdp.mol[0].res[0].spin[7].num, 85)
        self.assertEqual(cdp.mol[0].res[0].spin[7].name, 'CG')
        self.assertEqual(cdp.mol[0].res[0].spin[8].num, 86)
        self.assertEqual(cdp.mol[0].res[0].spin[8].name, 'OD1')
        self.assertEqual(cdp.mol[0].res[0].spin[9].num, 87)
        self.assertEqual(cdp.mol[0].res[0].spin[9].name, 'OD2')
        self.assertEqual(cdp.mol[0].res[0].spin[10].num, 88)
        self.assertEqual(cdp.mol[0].res[0].spin[10].name, 'C')
        self.assertEqual(cdp.mol[0].res[0].spin[11].num, 89)
        self.assertEqual(cdp.mol[0].res[0].spin[11].name, 'O')


    def test_load_protein_gly_N_Ca_spins_from_pdb(self):
        """Load the glycine backbone amide N and Ca spins from a loaded protein PDB file."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)

        # Generate the sequence of nitrogen spins (1 molecule, all GLY residues, and only N spins).
        self.interpreter.structure.load_spins(spin_id=':GLY@N')

        # Append to the sequence the alpha carbon spins (1 molecule, all GLY residues, and only Ca spins).
        self.interpreter.structure.load_spins(spin_id=':GLY@CA')

        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'Ap4Aase_res1-12_mol1')
        self.assertEqual(len(cdp.mol[0].res), 3)

        # 1st residue.
        self.assertEqual(cdp.mol[0].res[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[0].spin), 2)
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'N')
        self.assertEqual(cdp.mol[0].res[0].spin[1].num, 2)
        self.assertEqual(cdp.mol[0].res[0].spin[1].name, 'CA')

        # 2nd residue.
        self.assertEqual(cdp.mol[0].res[1].num, 4)
        self.assertEqual(cdp.mol[0].res[1].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[1].spin), 2)
        self.assertEqual(cdp.mol[0].res[1].spin[0].num, 43)
        self.assertEqual(cdp.mol[0].res[1].spin[0].name, 'N')
        self.assertEqual(cdp.mol[0].res[1].spin[1].num, 45)
        self.assertEqual(cdp.mol[0].res[1].spin[1].name, 'CA')

        # 3rd residue.
        self.assertEqual(cdp.mol[0].res[2].num, 12)
        self.assertEqual(cdp.mol[0].res[2].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[2].spin), 2)
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, 144)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')
        self.assertEqual(cdp.mol[0].res[2].spin[1].num, 146)
        self.assertEqual(cdp.mol[0].res[2].spin[1].name, 'CA')


    def test_load_protein_gly_N_spins_from_pdb(self):
        """Load the glycine backbone amide N spins from a loaded protein PDB file."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)

        # Generate the sequence (1 molecule, all GLY residues, and only N spins).
        self.interpreter.structure.load_spins(spin_id=':GLY@N')

        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'Ap4Aase_res1-12_mol1')
        self.assertEqual(len(cdp.mol[0].res), 3)

        # 1st residue.
        self.assertEqual(cdp.mol[0].res[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[0].spin), 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'N')

        # 2nd residue.
        self.assertEqual(cdp.mol[0].res[1].num, 4)
        self.assertEqual(cdp.mol[0].res[1].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[1].spin), 1)
        self.assertEqual(cdp.mol[0].res[1].spin[0].num, 43)
        self.assertEqual(cdp.mol[0].res[1].spin[0].name, 'N')

        # 3rd residue.
        self.assertEqual(cdp.mol[0].res[2].num, 12)
        self.assertEqual(cdp.mol[0].res[2].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[2].spin), 1)
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, 144)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')


    def test_load_protein_N_spins_from_pdb(self):
        """Load the protein backbone amide N spins from a loaded PDB file."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)

        # Generate the sequence (1 molecule, all residues, and only N spins).
        self.interpreter.structure.load_spins(spin_id='@N')

        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'Ap4Aase_res1-12_mol1')
        self.assertEqual(len(cdp.mol[0].res), 12)

        # 1st residue.
        self.assertEqual(cdp.mol[0].res[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[0].spin), 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'N')

        # 2nd residue.
        self.assertEqual(cdp.mol[0].res[1].num, 2)
        self.assertEqual(cdp.mol[0].res[1].name, 'PRO')
        self.assertEqual(len(cdp.mol[0].res[1].spin), 1)
        self.assertEqual(cdp.mol[0].res[1].spin[0].num, 10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].name, 'N')

        # 3rd residue.
        self.assertEqual(cdp.mol[0].res[2].num, 3)
        self.assertEqual(cdp.mol[0].res[2].name, 'LEU')
        self.assertEqual(len(cdp.mol[0].res[2].spin), 1)
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, 24)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')

        # 4th residue.
        self.assertEqual(cdp.mol[0].res[3].num, 4)
        self.assertEqual(cdp.mol[0].res[3].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[3].spin), 1)
        self.assertEqual(cdp.mol[0].res[3].spin[0].num, 43)
        self.assertEqual(cdp.mol[0].res[3].spin[0].name, 'N')

        # 5th residue.
        self.assertEqual(cdp.mol[0].res[4].num, 5)
        self.assertEqual(cdp.mol[0].res[4].name, 'SER')
        self.assertEqual(len(cdp.mol[0].res[4].spin), 1)
        self.assertEqual(cdp.mol[0].res[4].spin[0].num, 50)
        self.assertEqual(cdp.mol[0].res[4].spin[0].name, 'N')

        # 6th residue.
        self.assertEqual(cdp.mol[0].res[5].num, 6)
        self.assertEqual(cdp.mol[0].res[5].name, 'MET')
        self.assertEqual(len(cdp.mol[0].res[5].spin), 1)
        self.assertEqual(cdp.mol[0].res[5].spin[0].num, 61)
        self.assertEqual(cdp.mol[0].res[5].spin[0].name, 'N')

        # 7th residue.
        self.assertEqual(cdp.mol[0].res[6].num, 7)
        self.assertEqual(cdp.mol[0].res[6].name, 'ASP')
        self.assertEqual(len(cdp.mol[0].res[6].spin), 1)
        self.assertEqual(cdp.mol[0].res[6].spin[0].num, 78)
        self.assertEqual(cdp.mol[0].res[6].spin[0].name, 'N')

        # 8th residue.
        self.assertEqual(cdp.mol[0].res[7].num, 8)
        self.assertEqual(cdp.mol[0].res[7].name, 'SER')
        self.assertEqual(len(cdp.mol[0].res[7].spin), 1)
        self.assertEqual(cdp.mol[0].res[7].spin[0].num, 90)
        self.assertEqual(cdp.mol[0].res[7].spin[0].name, 'N')

        # 9th residue.
        self.assertEqual(cdp.mol[0].res[8].num, 9)
        self.assertEqual(cdp.mol[0].res[8].name, 'PRO')
        self.assertEqual(len(cdp.mol[0].res[8].spin), 1)
        self.assertEqual(cdp.mol[0].res[8].spin[0].num, 101)
        self.assertEqual(cdp.mol[0].res[8].spin[0].name, 'N')

        # 10th residue.
        self.assertEqual(cdp.mol[0].res[9].num, 10)
        self.assertEqual(cdp.mol[0].res[9].name, 'PRO')
        self.assertEqual(len(cdp.mol[0].res[9].spin), 1)
        self.assertEqual(cdp.mol[0].res[9].spin[0].num, 115)
        self.assertEqual(cdp.mol[0].res[9].spin[0].name, 'N')

        # 11th residue.
        self.assertEqual(cdp.mol[0].res[10].num, 11)
        self.assertEqual(cdp.mol[0].res[10].name, 'GLU')
        self.assertEqual(len(cdp.mol[0].res[10].spin), 1)
        self.assertEqual(cdp.mol[0].res[10].spin[0].num, 129)
        self.assertEqual(cdp.mol[0].res[10].spin[0].name, 'N')

        # 12th residue.
        self.assertEqual(cdp.mol[0].res[11].num, 12)
        self.assertEqual(cdp.mol[0].res[11].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[11].spin), 1)
        self.assertEqual(cdp.mol[0].res[11].spin[0].num, 144)
        self.assertEqual(cdp.mol[0].res[11].spin[0].name, 'N')


    def test_read(self):
        """The sequence.read() test."""

        # Read the sequence.
        self.interpreter.sequence.read(file='test_seq', dir=status.install_path + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)
        
        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, None)
        self.assertEqual(len(cdp.mol[0].res), 5)

        # 1st residue.
        self.assertEqual(cdp.mol[0].res[0].num, -2)
        self.assertEqual(cdp.mol[0].res[0].name, 'Gly')
        self.assertEqual(len(cdp.mol[0].res[0].spin), 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, None)
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, None)

    def test_sequence_copy(self):
        """Test the sequence.copy user function."""

        # First create some spins.
        self.interpreter.spin.create(spin_name='A', spin_num=1, res_num=1)
        self.interpreter.spin.create(spin_name='A', spin_num=2, res_num=1)
        self.interpreter.spin.create(spin_name='B', spin_num=3, res_num=1)
        self.interpreter.spin.create(spin_name='B2', spin_num=4, res_num=1)
        self.interpreter.spin.create(spin_name='A', spin_num=1, res_num=2)
        self.interpreter.spin.create(spin_name='A', spin_num=2, res_num=2)
        self.interpreter.spin.create(spin_name='B', spin_num=3, res_num=2)
        self.interpreter.spin.create(spin_name='B2', spin_num=4, res_num=2)

        # Create a new data pipe to copy to.
        self.interpreter.pipe.create('seq copy test', 'mf')

        # Copy the sequence.
        self.interpreter.sequence.copy(pipe_from='mf')

        # Alias the data pipes.
        pipe1 = ds['mf']
        pipe2 = ds['seq copy test']

        # Check the residue count.
        self.assertEqual(len(pipe1.mol[0].res), len(pipe2.mol[0].res))

        # Check the spin counts.
        for i in range(len(pipe1.mol[0].res)):
            self.assertEqual(len(pipe1.mol[0].res[i].spin), len(pipe2.mol[0].res[i].spin))
