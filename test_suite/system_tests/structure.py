###############################################################################
#                                                                             #
# Copyright (C) 2008-2010 Edward d'Auvergne                                   #
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
import sys
from os import sep

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import count_spins


class Structure(SystemTestCase):
    """Class for testing the structural objects."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_load_internal_results(self):
        """Load the PDB file using the information in a results file (using the internal structural object)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the results file.
        self.interpreter.results.read(file='str_internal', dir=path)

        # Test the structure metadata.
        self.assert_(hasattr(cdp, 'structure'))
        self.assert_(hasattr(cdp.structure, 'structural_data'))
        self.assert_(len(cdp.structure.structural_data))
        self.assert_(len(cdp.structure.structural_data[0].mol))

        mol = cdp.structure.structural_data[0].mol[0]
        self.assertEqual(mol.file_name, 'Ap4Aase_res1-12.pdb')
        self.assertEqual(mol.file_path, '')
        self.assertEqual(mol.file_model, 1)
        self.assertEqual(mol.file_mol_num, 1)

        # The real atomic data.
        atom_name = ['N', 'CA', '1HA', '2HA', 'C', 'O', '1HT', '2HT', '3HT', 'N', 'CD', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', '1HG', '2HG', '1HD', '2HD', 'C', 'O', 'N', 'H', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', 'HG', 'CD1', '1HD1', '2HD1', '3HD1', 'CD2', '1HD2', '2HD2', '3HD2', 'C', 'O', 'N', 'H', 'CA', '1HA', '2HA', 'C', 'O', 'N', 'H', 'CA', 'HA', 'CB', '1HB', '2HB', 'OG', 'HG', 'C', 'O', 'N', 'H', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', '1HG', '2HG', 'SD', 'CE', '1HE', '2HE', '3HE', 'C', 'O', 'N', 'H', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', 'OD1', 'OD2', 'C', 'O', 'N', 'H', 'CA', 'HA', 'CB', '1HB', '2HB', 'OG', 'HG', 'C', 'O', 'N', 'CD', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', '1HG', '2HG', '1HD', '2HD', 'C', 'O', 'N', 'CD', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', '1HG', '2HG', '1HD', '2HD', 'C', 'O', 'N', 'H', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', '1HG', '2HG', 'CD', 'OE1', 'OE2', 'C', 'O', 'N', 'H', 'CA', '1HA', '2HA', 'C', 'O']
        bonded = [[]]*174
        chain_id = [None]*174
        element = ['N', 'C', 'H', 'H', 'C', 'O', 'H', 'H', 'H', 'N', 'C', 'C', 'H', 'C', 'H', 'H', 'C', 'H', 'H', 'H', 'H', 'C', 'O', 'N', 'H', 'C', 'H', 'C', 'H', 'H', 'C', 'H', 'C', 'H', 'H', 'H', 'C', 'H', 'H', 'H', 'C', 'O', 'N', 'H', 'C', 'H', 'H', 'C', 'O', 'N', 'H', 'C', 'H', 'C', 'H', 'H', 'O', 'H', 'C', 'O', 'N', 'H', 'C', 'H', 'C', 'H', 'H', 'C', 'H', 'H', 'S', 'C', 'H', 'H', 'H', 'C', 'O', 'N', 'H', 'C', 'H', 'C', 'H', 'H', 'C', 'O', 'O', 'C', 'O', 'N', 'H', 'C', 'H', 'C', 'H', 'H', 'O', 'H', 'C', 'O', 'N', 'C', 'C', 'H', 'C', 'H', 'H', 'C', 'H', 'H', 'H', 'H', 'C', 'O', 'N', 'C', 'C', 'H', 'C', 'H', 'H', 'C', 'H', 'H', 'H', 'H', 'C', 'O', 'N', 'H', 'C', 'H', 'C', 'H', 'H', 'C', 'H', 'H', 'C', 'O', 'O', 'C', 'O', 'N', 'H', 'C', 'H', 'H', 'C', 'O']
        pdb_record = ['ATOM']*174
        res_name = ['GLY', 'GLY', 'GLY', 'GLY', 'GLY', 'GLY', 'GLY', 'GLY', 'GLY', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'LEU', 'GLY', 'GLY', 'GLY', 'GLY', 'GLY', 'GLY', 'GLY', 'SER', 'SER', 'SER', 'SER', 'SER', 'SER', 'SER', 'SER', 'SER', 'SER', 'SER', 'MET', 'MET', 'MET', 'MET', 'MET', 'MET', 'MET', 'MET', 'MET', 'MET', 'MET', 'MET', 'MET', 'MET', 'MET', 'MET', 'MET', 'ASP', 'ASP', 'ASP', 'ASP', 'ASP', 'ASP', 'ASP', 'ASP', 'ASP', 'ASP', 'ASP', 'ASP', 'SER', 'SER', 'SER', 'SER', 'SER', 'SER', 'SER', 'SER', 'SER', 'SER', 'SER', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'PRO', 'GLU', 'GLU', 'GLU', 'GLU', 'GLU', 'GLU', 'GLU', 'GLU', 'GLU', 'GLU', 'GLU', 'GLU', 'GLU', 'GLU', 'GLU', 'GLY', 'GLY', 'GLY', 'GLY', 'GLY', 'GLY', 'GLY']
        res_num = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12]
        seg_id = [None]*174
        x = [8.442, 7.469, 8.013, 6.825, 6.610, 6.827, 9.398, 8.180, 8.448, 5.613, 5.281, 4.714, 5.222, 3.646, 3.332, 2.800, 4.319, 4.853, 3.587, 6.162, 4.805, 4.075, 3.593, 4.074, 4.475, 3.498, 3.572, 2.025, 1.965, 1.609, 1.176, 1.823, 0.176, 0.096, 0.509, -0.789, 0.474, 0.809, -0.595, 0.707, 4.264, 4.364, 4.809, 4.697, 5.561, 6.220, 6.156, 4.659, 4.746, 3.786, 3.770, 2.851, 2.368, 1.785, 1.177, 1.165, 2.360, 1.690, 3.546, 3.804, 3.814, 3.563, 4.442, 4.984, 5.411, 6.192, 4.872, 6.068, 6.868, 5.332, 6.747, 6.155, 5.409, 6.977, 5.721, 3.369, 2.255, 3.703, 4.604, 2.753, 1.851, 3.329, 4.182, 3.644, 2.319, 1.992, 1.854, 2.419, 1.251, 3.451, 4.359, 3.267, 2.246, 4.223, 4.054, 4.040, 5.573, 6.142, 3.488, 4.276, 2.795, 1.828, 2.929, 2.810, 1.772, 0.912, 2.067, 1.505, 0.464, 2.138, 0.938, 2.273, 4.268, 4.585, 5.076, 4.776, 6.392, 6.925, 7.120, 7.968, 7.464, 6.130, 6.384, 6.135, 4.210, 4.246, 6.325, 5.263, 7.477, 8.281, 7.587, 7.039, 9.047, 9.133, 9.654, 9.590, 10.670, 9.215, 9.190, 10.055, 8.012, 7.007, 7.361, 6.144, 5.925, 5.555, 6.329, 4.814, 4.894, 4.761]
        y = [10.188, 9.889, 9.712, 10.745, 8.674, 7.991, 10.291, 11.073, 9.416, 8.385, 9.152, 7.243, 6.302, 7.443, 6.483, 7.963, 8.253, 7.605, 8.842, 9.327, 10.088, 7.251, 8.285, 6.099, 5.309, 5.986, 4.953, 6.396, 7.471, 6.106, 5.775, 5.225, 4.796, 4.954, 3.787, 4.949, 6.853, 7.828, 6.775, 6.720, 6.853, 8.068, 6.222, 5.251, 6.956, 6.273, 7.706, 7.634, 8.841, 6.847, 5.889, 7.360, 6.511, 8.230, 7.620, 8.669, 9.269, 9.652, 8.174, 9.362, 7.546, 6.604, 8.253, 9.095, 7.354, 7.976, 6.886, 6.258, 5.824, 5.499, 6.846, 5.570, 5.985, 5.190, 4.766, 8.771, 8.245, 9.789, 10.161, 10.351, 10.605, 11.610, 11.341, 12.287, 12.322, 11.787, 13.410, 9.322, 9.015, 8.776, 9.052, 7.758, 7.826, 7.990, 8.977, 7.248, 7.894, 8.285, 6.370, 6.214, 5.342, 5.431, 3.973, 3.943, 3.230, 3.234, 2.212, 3.991, 3.892, 3.624, 5.960, 5.908, 3.339, 3.179, 2.980, 3.150, 2.375, 2.876, 2.616, 3.262, 1.675, 3.264, 4.305, 2.758, 4.055, 2.299, 0.876, 0.258, 0.312, 0.871, -1.106, -1.253, -1.489, -2.564, -1.049, -1.041, -1.011, -0.052, -1.970, -2.740, -1.931, -2.037, -1.962, -2.949, -2.983, -3.917, -4.588, -4.488, -3.289, -3.932]
        z = [6.302, 7.391, 8.306, 7.526, 7.089, 6.087, 6.697, 5.822, 5.604, 7.943, 9.155, 7.752, 7.908, 8.829, 9.212, 8.407, 9.880, 10.560, 10.415, 9.754, 8.900, 6.374, 5.909, 5.719, 6.139, 4.391, 4.081, 4.415, 4.326, 5.367, 3.307, 2.640, 3.889, 4.956, 3.700, 3.430, 2.493, 2.814, 2.633, 1.449, 3.403, 3.572, 2.369, 2.281, 1.371, 0.855, 1.868, 0.359, 0.149, -0.269, -0.055, -1.268, -1.726, -0.608, 0.037, -1.377, 0.162, 0.731, -2.354, -2.175, -3.496, -3.603, -4.606, -4.199, -5.387, -5.803, -6.196, -4.563, -5.146, -4.350, -3.001, -1.895, -1.241, -1.307, -2.472, -5.551, -5.582, -6.328, -6.269, -7.274, -6.735, -7.913, -8.518, -7.133, -8.791, -9.871, -8.395, -8.346, -8.584, -8.977, -8.732, -10.002, -10.355, -11.174, -11.584, -11.936, -10.759, -11.425, -9.403, -8.469, -9.921, -11.030, -9.410, -8.336, -10.080, -9.428, -10.291, -11.333, -11.606, -12.128, -10.723, -11.893, -9.781, -10.959, -8.768, -7.344, -8.971, -9.765, -7.642, -7.816, -7.251, -6.715, -6.584, -5.765, -7.175, -6.955, -9.288, -9.222, -9.654, -9.696, -10.009, -10.928, -10.249, -10.194, -9.475, -11.596, -11.540, -11.813, -12.724, -13.193, -13.137, -8.947, -7.774, -9.383, -10.338, -8.477, -8.138, -9.017, -7.265, -6.226]

        # Test the atomic data.
        mol = cdp.structure.structural_data[0].mol[0]
        for i in xrange(len(mol.atom_name)):
            self.assertEqual(mol.atom_name[i], atom_name[i])
            self.assertEqual(mol.bonded[i], bonded[i])
            self.assertEqual(mol.chain_id[i], chain_id[i])
            self.assertEqual(mol.element[i], element[i])
            self.assertEqual(mol.pdb_record[i], pdb_record[i])
            self.assertEqual(mol.res_name[i], res_name[i])
            self.assertEqual(mol.res_num[i], res_num[i])
            self.assertEqual(mol.seg_id[i], seg_id[i])
            self.assertEqual(mol.x[i], x[i])
            self.assertEqual(mol.y[i], y[i])
            self.assertEqual(mol.z[i], z[i])


    def test_load_internal_results2(self):
        """Load the PDB file using the information in a results file (using the internal structural object)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the results file.
        self.interpreter.results.read(file=path+sep+'str_internal')


    def test_load_scientific_results(self):
        """Load the PDB file using the information in a results file (using the Scientific python structural object)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the results file.
        self.interpreter.results.read(file='str_scientific', dir=path)

        # Test the structure metadata.
        self.assert_(hasattr(cdp, 'structure'))
        self.assert_(hasattr(cdp.structure, 'structural_data'))
        self.assert_(len(cdp.structure.structural_data))
        self.assert_(len(cdp.structure.structural_data[0].mol))

        mol = cdp.structure.structural_data[0].mol[0]
        self.assertEqual(mol.file_name, 'Ap4Aase_res1-12.pdb')
        self.assertEqual(mol.file_path, 'test_suite/shared_data/structures')
        self.assertEqual(mol.file_model, 1)
        self.assertEqual(mol.file_mol_num, 1)

        # The real atomic data.
        res_list = ['GLY', 'PRO', 'LEU', 'GLY', 'SER', 'MET', 'ASP', 'SER', 'PRO', 'PRO', 'GLU', 'GLY']

        # Loop over the residues.
        i = 0
        for res_name in cdp.structure.atom_loop(atom_id='@N', res_name_flag=True):
            res_name = res_name[0]

            # Check the residue data.
            self.assertEqual(res_name, res_list[i])

            # Increment the residue counter.
            i = i + 1


    def test_read_pdb_internal1(self):
        """Load the '1F35_N_H_molmol.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='1F35_N_H_molmol.pdb', dir=path, parser='internal')

        # Test the molecule name.
        self.assertEqual(cdp.structure.structural_data[0].mol[0].mol_name, '1F35_N_H_molmol_mol1')

        # Load a single atom and test it.
        self.interpreter.structure.load_spins('#1F35_N_H_molmol_mol1:3@N')
        self.assertEqual(count_spins(), 1)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Extract a N-Ca vector.
        self.interpreter.structure.vectors('CA', spin_id='#1F35_N_H_molmol_mol1:3@N')
        print((cdp.mol[0].res[0].spin[0]))
        self.assert_(hasattr(cdp.mol[0].res[0].spin[0], 'bond_vect'))



    def test_read_pdb_internal2(self):
        """Load the 'Ap4Aase_res1-12.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=path, parser='internal')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_internal3(self):
        """Load the 'gromacs.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'phthalic_acid'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='gromacs.pdb', dir=path, parser='internal')

        # Try loading a few protons, without positions averaging across models.
        self.interpreter.structure.load_spins('@*H*', ave_pos=False)

        # A test.
        self.assertEqual(len(cdp.mol[0].res[0].spin[0].pos), 2)

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_internal4(self):
        """Load the 'tylers_peptide_trunc.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='tylers_peptide_trunc.pdb', dir=path, parser='internal')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_internal5(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, parser='internal')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_internal6(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' and 'lactose_MCMM4_S1_2.pdb' PDB files as 2 separate structures (using the internal structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDB twice.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, parser='internal')
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_2.pdb', dir=path, parser='internal')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_internal7(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' PDB file twice as 2 separate structures (using the internal structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDB twice.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, parser='internal')
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, parser='internal')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_mol_2_model_internal(self):
        """Load a few 'lactose_MCMM4_S1_*.pdb' PDB files as models (using the internal structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Files.
        files = ['lactose_MCMM4_S1_1.pdb',
                 'lactose_MCMM4_S1_2.pdb',
                 'lactose_MCMM4_S1_3.pdb']

        # Read the PDBs.
        self.interpreter.structure.read_pdb(file=files[0], dir=path, parser='internal', set_model_num=1)
        self.interpreter.structure.read_pdb(file=files[1], dir=path, parser='internal', set_model_num=1)
        self.interpreter.structure.read_pdb(file=files[2], dir=path, parser='internal', set_model_num=1)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Test the structural data.
        self.assert_(hasattr(cdp, 'structure'))
        self.assert_(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 3)

        i = 0
        for mol in cdp.structure.structural_data[0].mol:
            self.assertEqual(mol.file_name, files[i])
            self.assertEqual(mol.file_path, path)
            self.assertEqual(mol.file_model, 1)
            self.assertEqual(mol.file_mol_num, 1)
            i = i + 1


    def test_read_pdb_model_2_mol_internal(self):
        """Load the 2 models of the 'gromacs.pdb' PDB file as separate molecules of the same model (using the internal structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'phthalic_acid'

        # Read the PDB models.
        self.interpreter.structure.read_pdb(file='gromacs.pdb', dir=path, parser='internal', read_model=1, set_model_num=1)
        self.interpreter.structure.read_pdb(file='gromacs.pdb', dir=path, parser='internal', read_model=2, set_model_num=1)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Test the structural data.
        self.assert_(hasattr(cdp, 'structure'))
        self.assert_(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 2)

        i = 0
        for mol in cdp.structure.structural_data[0].mol:
            self.assertEqual(mol.file_name, 'gromacs.pdb')
            self.assertEqual(mol.file_path, path)
            self.assertEqual(mol.file_model, i+1)
            self.assertEqual(mol.file_mol_num, 1)
            i = i + 1


    def test_read_pdb_complex_internal(self):
        """Test the packing of models and molecules using 'gromacs.pdb' and 'lactose_MCMM4_S1_*.pdb' (using the internal structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB models.
        self.interpreter.structure.read_pdb(file='gromacs.pdb', dir=path+sep+'phthalic_acid', parser='internal')
        self.interpreter.structure.read_pdb(file='lactose'+sep+'lactose_MCMM4_S1_1.pdb', dir=path, parser='internal', set_model_num=1, set_mol_name='lactose_MCMM4_S1')
        self.interpreter.structure.read_pdb(file='lactose'+sep+'lactose_MCMM4_S1_2.pdb', dir=path, parser='internal', set_model_num=2, set_mol_name='lactose_MCMM4_S1')
        self.interpreter.structure.read_pdb(file='lactose'+sep+'lactose_MCMM4_S1_3.pdb', dir=path, parser='internal', set_model_num=1, set_mol_name='lactose_MCMM4_S1b')
        self.interpreter.structure.read_pdb(file='lactose'+sep+'lactose_MCMM4_S1_4.pdb', dir=path, parser='internal', set_model_num=2, set_mol_name='lactose_MCMM4_S1b')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Test the structural data.
        self.assert_(hasattr(cdp, 'structure'))
        self.assert_(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 2)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 3)
        self.assertEqual(len(cdp.structure.structural_data[1].mol), 3)

        files = [['gromacs.pdb', 'lactose_MCMM4_S1_1.pdb', 'lactose_MCMM4_S1_3.pdb'],
                 ['gromacs.pdb', 'lactose_MCMM4_S1_2.pdb', 'lactose_MCMM4_S1_4.pdb']]
        paths = [[path+sep+'phthalic_acid', path+sep+'lactose', path+sep+'lactose'],
                 [path+sep+'phthalic_acid', path+sep+'lactose', path+sep+'lactose']]
        models = [[1, 1, 1], [2, 1, 1]]

        for i in range(len(cdp.structure.structural_data)):
            for j in range(len(cdp.structure.structural_data[i].mol)):
                mol = cdp.structure.structural_data[i].mol[j]
                self.assertEqual(mol.file_name, files[i][j])
                self.assertEqual(mol.file_path, paths[i][j])
                self.assertEqual(mol.file_model, models[i][j])
                self.assertEqual(mol.file_mol_num, 1)


    def test_read_pdb_scientific1(self):
        """Load the '1F35_N_H_molmol.pdb' PDB file (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='1F35_N_H_molmol.pdb', dir=path, parser='scientific')

        # Load a single atom and test it.
        self.interpreter.structure.load_spins('#1F35_N_H_molmol_mol1:3@N')
        self.assertEqual(count_spins(), 1)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Extract a N-Ca vector.
        self.interpreter.structure.vectors('CA', spin_id='#1F35_N_H_molmol_mol1:3@N')
        self.assert_(hasattr(cdp.mol[0].res[0].spin[0], 'bond_vect'))


    def test_read_pdb_scientific2(self):
        """Load the 'Ap4Aase_res1-12.pdb' PDB file (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=path, parser='scientific')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_scientific3(self):
        """Load the 'gromacs.pdb' PDB file (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'phthalic_acid'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='gromacs.pdb', dir=path, parser='scientific')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*', ave_pos=False)

        # A test.
        self.assertEqual(len(cdp.mol[0].res[0].spin[0].pos), 2)

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_scientific4(self):
        """Load the 'tylers_peptide_trunc.pdb' PDB file (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='tylers_peptide_trunc.pdb', dir=path, parser='scientific')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_scientific5(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' PDB file (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, parser='scientific')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_scientific6(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' and 'lactose_MCMM4_S1_2.pdb' PDB files as 2 separate structures (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDB twice.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, parser='scientific')
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_2.pdb', dir=path, parser='scientific')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_scientific7(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' PDB file twice as 2 separate structures (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDB twice.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, parser='scientific')
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, parser='scientific')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_mol_2_model_scientific(self):
        """Load a few 'lactose_MCMM4_S1_*.pdb' PDB files as models (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Files.
        files = ['lactose_MCMM4_S1_1.pdb',
                 'lactose_MCMM4_S1_2.pdb',
                 'lactose_MCMM4_S1_3.pdb']

        # Read the PDBs.
        self.interpreter.structure.read_pdb(file=files[0], dir=path, parser='scientific', set_model_num=1)
        self.interpreter.structure.read_pdb(file=files[1], dir=path, parser='scientific', set_model_num=1)
        self.interpreter.structure.read_pdb(file=files[2], dir=path, parser='scientific', set_model_num=1)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Test the structural data.
        self.assert_(hasattr(cdp, 'structure'))
        self.assert_(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 6)

        i = 0
        for mol in cdp.structure.structural_data[0].mol:
            self.assertEqual(mol.file_name, files[i/2])
            self.assertEqual(mol.file_path, path)
            self.assertEqual(mol.file_model, 1)
            self.assertEqual(mol.file_mol_num, i%2+1)  # Odd i, num=1, even i, num=2.
            i = i + 1


    def test_read_pdb_model_2_mol_scientific(self):
        """Load the 2 models of the 'gromacs.pdb' PDB file as separate molecules of the same model (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'phthalic_acid'

        # Read the PDB models.
        self.interpreter.structure.read_pdb(file='gromacs.pdb', dir=path, parser='scientific', read_model=1, set_model_num=1)
        self.interpreter.structure.read_pdb(file='gromacs.pdb', dir=path, parser='scientific', read_model=2, set_model_num=1)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Test the structural data.
        self.assert_(hasattr(cdp, 'structure'))
        self.assert_(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 2)

        i = 0
        for mol in cdp.structure.structural_data[0].mol:
            self.assertEqual(mol.file_name, 'gromacs.pdb')
            self.assertEqual(mol.file_path, path)
            self.assertEqual(mol.file_model, i+1)
            self.assertEqual(mol.file_mol_num, 1)
            i = i + 1


    def test_read_pdb_complex_scientific(self):
        """Test the packing of models and molecules using 'gromacs.pdb' and 'lactose_MCMM4_S1_*.pdb' (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB models.
        self.interpreter.structure.read_pdb(file='gromacs.pdb', dir=path+sep+'phthalic_acid', parser='scientific')
        self.interpreter.structure.read_pdb(file='lactose'+sep+'lactose_MCMM4_S1_1.pdb', dir=path, parser='scientific', read_mol=1, set_model_num=1, set_mol_name='lactose_MCMM4_S1')
        self.interpreter.structure.read_pdb(file='lactose'+sep+'lactose_MCMM4_S1_2.pdb', dir=path, parser='scientific', read_mol=1, set_model_num=2, set_mol_name='lactose_MCMM4_S1')
        self.interpreter.structure.read_pdb(file='lactose'+sep+'lactose_MCMM4_S1_3.pdb', dir=path, parser='scientific', read_mol=1, set_model_num=1, set_mol_name='lactose_MCMM4_S1b')
        self.interpreter.structure.read_pdb(file='lactose'+sep+'lactose_MCMM4_S1_4.pdb', dir=path, parser='scientific', read_mol=1, set_model_num=2, set_mol_name='lactose_MCMM4_S1b')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Test the structural data.
        self.assert_(hasattr(cdp, 'structure'))
        self.assert_(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 2)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 3)
        self.assertEqual(len(cdp.structure.structural_data[1].mol), 3)

        files = [['gromacs.pdb', 'lactose_MCMM4_S1_1.pdb', 'lactose_MCMM4_S1_3.pdb'],
                 ['gromacs.pdb', 'lactose_MCMM4_S1_2.pdb', 'lactose_MCMM4_S1_4.pdb']]
        paths = [[path+sep+'phthalic_acid', path+sep+'lactose', path+sep+'lactose'],
                 [path+sep+'phthalic_acid', path+sep+'lactose', path+sep+'lactose']]
        models = [[1, 1, 1], [2, 1, 1]]

        for i in range(len(cdp.structure.structural_data)):
            for j in range(len(cdp.structure.structural_data[i].mol)):
                mol = cdp.structure.structural_data[i].mol[j]
                self.assertEqual(mol.file_name, files[i][j])
                self.assertEqual(mol.file_path, paths[i][j])
                self.assertEqual(mol.file_model, models[i][j])
                self.assertEqual(mol.file_mol_num, 1)
