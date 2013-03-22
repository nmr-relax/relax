###############################################################################
#                                                                             #
# Copyright (C) 2008-2013 Edward d'Auvergne                                   #
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
from math import sqrt
from numpy import float64, zeros
from os import sep
from tempfile import mktemp

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import count_spins, return_spin
from lib.geometry.rotations import euler_to_R_zyz
from lib.errors import RelaxError
from lib.io import DummyFileObject
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Structure(SystemTestCase):
    """Class for testing the structural objects."""

    def __init__(self, methodName='runTest'):
        """Skip scientific Python tests if not installed.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(Structure, self).__init__(methodName)


    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def test_alt_loc_missing(self):
        """Test that a RelaxError occurs when the alternate location indicator is present but not specified."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file, load the spins, and attach the protons.
        self.assertRaises(RelaxError, self.interpreter.structure.read_pdb, '1OGT_trunc.pdb', dir=path)


    def test_bug_sr_2998_broken_conect_records(self):
        """Test the bug reported as the U{support request #2998<https://gna.org/support/?2998>}, the broken CONECT records."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file.
        self.interpreter.structure.read_pdb('1RTE_trunc.pdb', dir=path)


    def test_bug_20469_scientific_parser_xray_records(self):
        """Test the U{bug #20469<https://gna.org/bugs/?20469>}, the ScientificPython parser failure with X-ray records."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file.
        self.interpreter.structure.read_pdb('1RTE_trunc.pdb', dir=path, parser='scientific')


    def test_bug_20470_alternate_location_indicator(self):
        """Catch U{bug #20470<https://gna.org/bugs/?20470>}, the alternate location indicator problem."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file, load the spins, and attach the protons.
        self.interpreter.structure.read_pdb('1OGT_trunc.pdb', dir=path, alt_loc='A')
        self.interpreter.structure.load_spins(spin_id='@N', ave_pos=True)
        self.interpreter.sequence.attach_protons()


    def test_delete_empty(self):
        """Test the deletion of non-existent structural data."""

        # Delete all structural data.
        self.interpreter.structure.delete()


    def test_delete_multi_pipe(self):
        """Test the deletion of structural data in only one pipe."""

        # Create a structure with a single atom.
        self.interpreter.structure.add_atom(atom_name='PIV', res_name='M1', res_num=1, pos=[0., 1., 2.], element='S')

        # Create a new data pipe.
        self.interpreter.pipe.create('new', 'N-state')

        # Create a structure with a single atom.
        self.interpreter.structure.add_atom(atom_name='PIV', res_name='M1', res_num=2, pos=[4., 5., 6.], element='S')

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Checks.
        self.assert_(hasattr(cdp, 'structure'))
        self.assertEqual(len(cdp.structure.structural_data), 0)
        self.interpreter.pipe.switch('mf')
        self.assert_(hasattr(cdp, 'structure'))
        self.assertEqual(len(cdp.structure.structural_data), 1)


    def test_displacement(self):
        """Test of the structure.displacement user function."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file as two models.
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_model_num=1)
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_model_num=2)

        # A rotation.
        R = zeros((3, 3), float64)
        euler_to_R_zyz(1.3, 0.4, 4.5, R)

        # Rotate the second model.
        self.interpreter.structure.rotate(R, model=2)

        # Calculate the displacement.
        self.interpreter.structure.displacement()

        # Shift a third structure back using the calculated displacement.
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_model_num=3)
        self.interpreter.structure.rotate(R, model=3)

        # The data to check.
        models = [1, 2]
        trans_vect = [
            [[0.0, 0.0, 0.0],
             [   2.270857972754659,   -1.811667138656451,    1.878400649688508]],
            [[  -2.270857972754659,    1.811667138656451,   -1.878400649688508],
             [0.0, 0.0, 0.0]]
        ]
        dist = [
            [0.0000000000000000, 3.4593818457148173],
            [3.4593818457148173, 0.0000000000000000]
        ]
        rot_axis = [
            [None,
             [   0.646165066909452,    0.018875759848125,   -0.762964227206007]],
            [[  -0.646165066909452,   -0.018875759848125,    0.762964227206007],
             None]
        ]
        angle = [
            [0.0000000000000000, 0.6247677290742989],
            [0.6247677290742989, 0.0000000000000000]
        ]

        # Test the results.
        self.assert_(hasattr(cdp.structure, 'displacements'))
        for i in range(len(models)):
            for j in range(len(models)):
                # Check the translation.
                self.assertAlmostEqual(cdp.structure.displacements._translation_distance[models[i]][models[j]], dist[i][j])
                for k in range(3):
                    self.assertAlmostEqual(cdp.structure.displacements._translation_vector[models[i]][models[j]][k], trans_vect[i][j][k])

                # Check the rotation.
                self.assertAlmostEqual(cdp.structure.displacements._rotation_angle[models[i]][models[j]], angle[i][j])
                if rot_axis[i][j] != None:
                    for k in range(3):
                        self.assertAlmostEqual(cdp.structure.displacements._rotation_axis[models[i]][models[j]][k], rot_axis[i][j][k])

        # Save the results.
        self.tmpfile = mktemp()
        self.interpreter.state.save(self.tmpfile, dir=None, force=True)

        # Reset relax.
        self.interpreter.reset()

        # Load the results.
        self.interpreter.state.load(self.tmpfile)

        # Test the re-loaded data.
        self.assert_(hasattr(cdp.structure, 'displacements'))
        for i in range(len(models)):
            for j in range(len(models)):
                # Check the translation.
                self.assertAlmostEqual(cdp.structure.displacements._translation_distance[models[i]][models[j]], dist[i][j])
                for k in range(3):
                    self.assertAlmostEqual(cdp.structure.displacements._translation_vector[models[i]][models[j]][k], trans_vect[i][j][k])

                # Check the rotation.
                self.assertAlmostEqual(cdp.structure.displacements._rotation_angle[models[i]][models[j]], angle[i][j])
                if rot_axis[i][j] != None:
                    for k in range(3):
                        self.assertAlmostEqual(cdp.structure.displacements._rotation_axis[models[i]][models[j]][k], rot_axis[i][j][k])


    def test_load_spins_mol_cat(self):
        """Test the loading of spins from different molecules into one molecule container."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDBs.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, set_mol_name='L1', parser='internal')
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_2.pdb', dir=path, set_mol_name='L2', parser='internal')

        # Load a few protons.
        self.interpreter.structure.load_spins('#L1:900@C1', mol_name_target='Lactose')
        self.interpreter.structure.load_spins('#L2:900@C2', mol_name_target='Lactose')

        # Check the spin data.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'Lactose')
        self.assertEqual(len(cdp.mol[0].res), 1)
        self.assertEqual(cdp.mol[0].res[0].name, 'UNK')
        self.assertEqual(cdp.mol[0].res[0].num, 900)
        self.assertEqual(len(cdp.mol[0].res[0].spin), 2)
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'C1')
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].spin[1].name, 'C2')
        self.assertEqual(cdp.mol[0].res[0].spin[1].num, 2)


    def test_load_internal_results(self):
        """Load the PDB file using the information in a results file (using the internal structural object)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

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
        for i in range(len(mol.atom_name)):
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
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the results file.
        self.interpreter.results.read(file=path+sep+'str_internal')


    def test_load_scientific_results(self):
        """Load the PDB file using the information in a results file (using the Scientific python structural object)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

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
            # Check the residue data.
            self.assertEqual(res_name, res_list[i])

            # Increment the residue counter.
            i = i + 1


    def test_metadata_xml(self):
        """Test the storage and loading of metadata into an XML state file."""

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('1UBQ.pdb', dir=path)

        # Delete a big chunk of the molecule.
        self.interpreter.structure.delete(":35-76")

        # Delete all waters.
        self.interpreter.structure.delete(":HOH")

        # Write out the results file.
        self.tmpfile = mktemp() + '.bz2'
        self.interpreter.results.write(self.tmpfile, dir=None)

        # Create a new data pipe and load the results.
        self.interpreter.pipe.create('xml text', 'mf')
        self.interpreter.results.read(self.tmpfile)

        # What the data should look like.
        helices = [
            ['H1', 'A', 'ILE', 23, 'A', 'GLU', 34, 1, 12]
        ]
        sheets = [
            [1, 'BET', 5, 'GLY', 'A', 10, None, 'VAL', 'A', 17, None, 0, None, None, None, None, None, None, None, None, None, None],
            [2, 'BET', 5, 'MET', 'A', 1, None, 'THR', 'A', 7, None, -1, None, None, None, None, None, None, None, None, None, None]
        ]

        # Check the helix data.
        self.assert_(hasattr(cdp.structure, 'helices'))
        self.assertEqual(len(cdp.structure.helices), 1)
        self.assertEqual(cdp.structure.helices[0], helices[0])

        # Check the sheet data.
        self.assert_(hasattr(cdp.structure, 'sheets'))
        self.assertEqual(len(cdp.structure.sheets), 2)
        self.assertEqual(cdp.structure.sheets[0], sheets[0])
        self.assertEqual(cdp.structure.sheets[1], sheets[1])


    def test_read_merge(self):
        """Test the merging of two molecules into one."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB files.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-6.pdb', dir=path, set_mol_name='Ap4Aase', set_model_num=1)
        self.interpreter.structure.read_pdb(file='Ap4Aase_res7-12.pdb', dir=path, set_mol_name='Ap4Aase', set_model_num=1, merge=True)
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=path, set_mol_name='Ap4Aase', set_model_num=2)

        # Check that everything is ok.
        cdp.structure.validate_models()


    def test_read_not_pdb(self):
        """Test the reading of a file by structure.read_pdb that is not a PDB."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'saved_states'

        # Read the non-PDB file.
        self.interpreter.structure.read_pdb(file='basic_single_pipe.bz2', dir=path, parser='internal')


    def test_read_pdb_internal1(self):
        """Load the '1F35_N_H_molmol.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

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
        self.interpreter.dipole_pair.define(spin_id1='@CA', spin_id2='#1F35_N_H_molmol_mol1:3@N')
        self.interpreter.dipole_pair.unit_vectors()
        print(cdp.interatomic[0])
        self.assert_(hasattr(cdp.interatomic[0], 'vector'))


    def test_read_pdb_internal2(self):
        """Load the 'Ap4Aase_res1-12.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=path, parser='internal')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_internal3(self):
        """Load the 'gromacs.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'phthalic_acid'

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
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='tylers_peptide_trunc.pdb', dir=path, parser='internal')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_internal5(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, parser='internal')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_internal6(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' and 'lactose_MCMM4_S1_2.pdb' PDB files as 2 separate structures (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

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
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

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
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

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
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'phthalic_acid'

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
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

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
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

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
        self.interpreter.dipole_pair.define(spin_id1='@CA', spin_id2='#1F35_N_H_molmol_mol1:3@N')
        self.interpreter.dipole_pair.unit_vectors()
        print(cdp.interatomic[0])
        self.assert_(hasattr(cdp.interatomic[0], 'vector'))


    def test_read_pdb_scientific2(self):
        """Load the 'Ap4Aase_res1-12.pdb' PDB file (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=path, parser='scientific')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_scientific3(self):
        """Load the 'gromacs.pdb' PDB file (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'phthalic_acid'

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
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='tylers_peptide_trunc.pdb', dir=path, parser='scientific')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_scientific5(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' PDB file (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, parser='scientific')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_scientific6(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' and 'lactose_MCMM4_S1_2.pdb' PDB files as 2 separate structures (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

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
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

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
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

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
            self.assertEqual(mol.file_name, files[int(i/2)])
            self.assertEqual(mol.file_path, path)
            self.assertEqual(mol.file_model, 1)
            self.assertEqual(mol.file_mol_num, i%2+1)  # Odd i, num=1, even i, num=2.
            i = i + 1


    def test_read_pdb_model_2_mol_scientific(self):
        """Load the 2 models of the 'gromacs.pdb' PDB file as separate molecules of the same model (using the Scientific python structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'phthalic_acid'

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
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

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


    def test_read_pdb_1UBQ(self):
        """Test the reading of the complete 1UBQ PDB file."""

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('1UBQ.pdb', dir=path)

        # Check the data.
        self.assert_(hasattr(cdp, 'structure'))
        self.assert_(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 1)

        # Check the first atom.
        self.assertEqual(cdp.structure.structural_data[0].mol[0].atom_num[0], 1)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].atom_name[0], 'N')
        self.assertEqual(cdp.structure.structural_data[0].mol[0].chain_id[0], 'A')
        self.assertEqual(cdp.structure.structural_data[0].mol[0].res_name[0], 'MET')
        self.assertEqual(cdp.structure.structural_data[0].mol[0].res_num[0], 1)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].x[0], 27.340)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].y[0], 24.430)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].z[0], 2.614)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].element[0], 'N')

        # Check the last atom (from the last water HETATM record).
        self.assertEqual(cdp.structure.structural_data[0].mol[0].atom_num[-1], 661)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].atom_name[-1], 'O')
        self.assertEqual(cdp.structure.structural_data[0].mol[0].chain_id[-1], None)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].res_name[-1], 'HOH')
        self.assertEqual(cdp.structure.structural_data[0].mol[0].res_num[-1], 58)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].x[-1], 37.667)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].y[-1], 43.421)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].z[-1], 17.000)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].element[-1], 'O')


    def test_read_write_pdb_1UBQ(self):
        """Test the reading and writing of the 1UBQ PDB file."""

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('1UBQ.pdb', dir=path)

        # Delete a big chunk of the molecule.
        self.interpreter.structure.delete(":35-76")

        # Delete all waters.
        self.interpreter.structure.delete(":HOH")

        # Write out the file.
        self.tmpfile = mktemp() + '.pdb'
        self.interpreter.structure.write_pdb(self.tmpfile)

        # Read the contents of the file.
        file = open(self.tmpfile)
        lines = file.readlines()
        file.close()

        # What the contents should be.
        real_data = [
            "REMARK   4 THIS FILE COMPLIES WITH FORMAT V. 3.30, JUL-2011.                    \n",
            "REMARK  40 CREATED BY RELAX (HTTP://NMR-RELAX.COM).                             \n",
            "HELIX    1  H1 ILE A   23  GLU A   34  1                                  12    \n",
            "SHEET    1 BET 5 GLY A  10  VAL A  17  0                                        \n",
            "SHEET    2 BET 5 MET A   1  THR A   7 -1                                        \n",
            "ATOM      1  N   MET A   1      27.340  24.430   2.614  1.00  0.00           N  \n",
            "ATOM      2 CA   MET A   1      26.266  25.413   2.842  1.00  0.00           C  \n",
            "ATOM      3  C   MET A   1      26.913  26.639   3.531  1.00  0.00           C  \n",
            "ATOM      4  O   MET A   1      27.886  26.463   4.263  1.00  0.00           O  \n",
            "ATOM      5 CB   MET A   1      25.112  24.880   3.649  1.00  0.00           C  \n",
            "ATOM      6 CG   MET A   1      25.353  24.860   5.134  1.00  0.00           C  \n",
            "ATOM      7 SD   MET A   1      23.930  23.959   5.904  1.00  0.00           S  \n",
            "ATOM      8 CE   MET A   1      24.447  23.984   7.620  1.00  0.00           C  \n",
            "ATOM      9  N   GLN A   2      26.335  27.770   3.258  1.00  0.00           N  \n",
            "ATOM     10 CA   GLN A   2      26.850  29.021   3.898  1.00  0.00           C  \n",
            "ATOM     11  C   GLN A   2      26.100  29.253   5.202  1.00  0.00           C  \n",
            "ATOM     12  O   GLN A   2      24.865  29.024   5.330  1.00  0.00           O  \n",
            "ATOM     13 CB   GLN A   2      26.733  30.148   2.905  1.00  0.00           C  \n",
            "ATOM     14 CG   GLN A   2      26.882  31.546   3.409  1.00  0.00           C  \n",
            "ATOM     15 CD   GLN A   2      26.786  32.562   2.270  1.00  0.00           C  \n",
            "ATOM     16 OE1  GLN A   2      27.783  33.160   1.870  1.00  0.00           O  \n",
            "ATOM     17 NE2  GLN A   2      25.562  32.733   1.806  1.00  0.00           N  \n",
            "ATOM     18  N   ILE A   3      26.849  29.656   6.217  1.00  0.00           N  \n",
            "ATOM     19 CA   ILE A   3      26.235  30.058   7.497  1.00  0.00           C  \n",
            "ATOM     20  C   ILE A   3      26.882  31.428   7.862  1.00  0.00           C  \n",
            "ATOM     21  O   ILE A   3      27.906  31.711   7.264  1.00  0.00           O  \n",
            "ATOM     22 CB   ILE A   3      26.344  29.050   8.645  1.00  0.00           C  \n",
            "ATOM     23 CG1  ILE A   3      27.810  28.748   8.999  1.00  0.00           C  \n",
            "ATOM     24 CG2  ILE A   3      25.491  27.771   8.287  1.00  0.00           C  \n",
            "ATOM     25 CD1  ILE A   3      27.967  28.087  10.417  1.00  0.00           C  \n",
            "ATOM     26  N   PHE A   4      26.214  32.097   8.771  1.00  0.00           N  \n",
            "ATOM     27 CA   PHE A   4      26.772  33.436   9.197  1.00  0.00           C  \n",
            "ATOM     28  C   PHE A   4      27.151  33.362  10.650  1.00  0.00           C  \n",
            "ATOM     29  O   PHE A   4      26.350  32.778  11.395  1.00  0.00           O  \n",
            "ATOM     30 CB   PHE A   4      25.695  34.498   8.946  1.00  0.00           C  \n",
            "ATOM     31 CG   PHE A   4      25.288  34.609   7.499  1.00  0.00           C  \n",
            "ATOM     32 CD1  PHE A   4      24.147  33.966   7.038  1.00  0.00           C  \n",
            "ATOM     33 CD2  PHE A   4      26.136  35.346   6.640  1.00  0.00           C  \n",
            "ATOM     34 CE1  PHE A   4      23.812  34.031   5.677  1.00  0.00           C  \n",
            "ATOM     35 CE2  PHE A   4      25.810  35.392   5.267  1.00  0.00           C  \n",
            "ATOM     36 CZ   PHE A   4      24.620  34.778   4.853  1.00  0.00           C  \n",
            "ATOM     37  N   VAL A   5      28.260  33.943  11.096  1.00  0.00           N  \n",
            "ATOM     38 CA   VAL A   5      28.605  33.965  12.503  1.00  0.00           C  \n",
            "ATOM     39  C   VAL A   5      28.638  35.461  12.900  1.00  0.00           C  \n",
            "ATOM     40  O   VAL A   5      29.522  36.103  12.320  1.00  0.00           O  \n",
            "ATOM     41 CB   VAL A   5      29.963  33.317  12.814  1.00  0.00           C  \n",
            "ATOM     42 CG1  VAL A   5      30.211  33.394  14.304  1.00  0.00           C  \n",
            "ATOM     43 CG2  VAL A   5      29.957  31.838  12.352  1.00  0.00           C  \n",
            "ATOM     44  N   LYS A   6      27.751  35.867  13.740  1.00  0.00           N  \n",
            "ATOM     45 CA   LYS A   6      27.691  37.315  14.143  1.00  0.00           C  \n",
            "ATOM     46  C   LYS A   6      28.469  37.475  15.420  1.00  0.00           C  \n",
            "ATOM     47  O   LYS A   6      28.213  36.753  16.411  1.00  0.00           O  \n",
            "ATOM     48 CB   LYS A   6      26.219  37.684  14.307  1.00  0.00           C  \n",
            "ATOM     49 CG   LYS A   6      25.884  39.139  14.615  1.00  0.00           C  \n",
            "ATOM     50 CD   LYS A   6      24.348  39.296  14.642  1.00  0.00           C  \n",
            "ATOM     51 CE   LYS A   6      23.865  40.723  14.749  1.00  0.00           C  \n",
            "ATOM     52 NZ   LYS A   6      22.375  40.720  14.907  1.00  0.00           N  \n",
            "ATOM     53  N   THR A   7      29.426  38.430  15.446  1.00  0.00           N  \n",
            "ATOM     54 CA   THR A   7      30.225  38.643  16.662  1.00  0.00           C  \n",
            "ATOM     55  C   THR A   7      29.664  39.839  17.434  1.00  0.00           C  \n",
            "ATOM     56  O   THR A   7      28.850  40.565  16.859  1.00  0.00           O  \n",
            "ATOM     57 CB   THR A   7      31.744  38.879  16.299  1.00  0.00           C  \n",
            "ATOM     58 OG1  THR A   7      31.737  40.257  15.824  1.00  0.00           O  \n",
            "ATOM     59 CG2  THR A   7      32.260  37.969  15.171  1.00  0.00           C  \n",
            "ATOM     60  N   LEU A   8      30.132  40.069  18.642  1.00  0.00           N  \n",
            "ATOM     61 CA   LEU A   8      29.607  41.180  19.467  1.00  0.00           C  \n",
            "ATOM     62  C   LEU A   8      30.075  42.538  18.984  1.00  0.00           C  \n",
            "ATOM     63  O   LEU A   8      29.586  43.570  19.483  1.00  0.00           O  \n",
            "ATOM     64 CB   LEU A   8      29.919  40.890  20.938  1.00  0.00           C  \n",
            "ATOM     65 CG   LEU A   8      29.183  39.722  21.581  1.00  0.00           C  \n",
            "ATOM     66 CD1  LEU A   8      29.308  39.750  23.095  1.00  0.00           C  \n",
            "ATOM     67 CD2  LEU A   8      27.700  39.721  21.228  1.00  0.00           C  \n",
            "ATOM     68  N   THR A   9      30.991  42.571  17.998  1.00  0.00           N  \n",
            "ATOM     69 CA   THR A   9      31.422  43.940  17.553  1.00  0.00           C  \n",
            "ATOM     70  C   THR A   9      30.755  44.351  16.277  1.00  0.00           C  \n",
            "ATOM     71  O   THR A   9      31.207  45.268  15.566  1.00  0.00           O  \n",
            "ATOM     72 CB   THR A   9      32.979  43.918  17.445  1.00  0.00           C  \n",
            "ATOM     73 OG1  THR A   9      33.174  43.067  16.265  1.00  0.00           O  \n",
            "ATOM     74 CG2  THR A   9      33.657  43.319  18.672  1.00  0.00           C  \n",
            "ATOM     75  N   GLY A  10      29.721  43.673  15.885  1.00  0.00           N  \n",
            "ATOM     76 CA   GLY A  10      28.978  43.960  14.678  1.00  0.00           C  \n",
            "ATOM     77  C   GLY A  10      29.604  43.507  13.393  1.00  0.00           C  \n",
            "ATOM     78  O   GLY A  10      29.219  43.981  12.301  1.00  0.00           O  \n",
            "ATOM     79  N   LYS A  11      30.563  42.623  13.495  1.00  0.00           N  \n",
            "ATOM     80 CA   LYS A  11      31.191  42.012  12.331  1.00  0.00           C  \n",
            "ATOM     81  C   LYS A  11      30.459  40.666  12.130  1.00  0.00           C  \n",
            "ATOM     82  O   LYS A  11      30.253  39.991  13.133  1.00  0.00           O  \n",
            "ATOM     83 CB   LYS A  11      32.672  41.717  12.505  1.00  0.00           C  \n",
            "ATOM     84 CG   LYS A  11      33.280  41.086  11.227  1.00  0.00           C  \n",
            "ATOM     85 CD   LYS A  11      34.762  40.799  11.470  1.00  0.00           C  \n",
            "ATOM     86 CE   LYS A  11      35.614  40.847  10.240  1.00  0.00           C  \n",
            "ATOM     87 NZ   LYS A  11      35.100  40.073   9.101  1.00  0.00           N  \n",
            "ATOM     88  N   THR A  12      30.163  40.338  10.886  1.00  0.00           N  \n",
            "ATOM     89 CA   THR A  12      29.542  39.020  10.653  1.00  0.00           C  \n",
            "ATOM     90  C   THR A  12      30.494  38.261   9.729  1.00  0.00           C  \n",
            "ATOM     91  O   THR A  12      30.849  38.850   8.706  1.00  0.00           O  \n",
            "ATOM     92 CB   THR A  12      28.113  39.049  10.015  1.00  0.00           C  \n",
            "ATOM     93 OG1  THR A  12      27.280  39.722  10.996  1.00  0.00           O  \n",
            "ATOM     94 CG2  THR A  12      27.588  37.635   9.715  1.00  0.00           C  \n",
            "ATOM     95  N   ILE A  13      30.795  37.015  10.095  1.00  0.00           N  \n",
            "ATOM     96 CA   ILE A  13      31.720  36.289   9.176  1.00  0.00           C  \n",
            "ATOM     97  C   ILE A  13      30.955  35.211   8.459  1.00  0.00           C  \n",
            "ATOM     98  O   ILE A  13      30.025  34.618   9.040  1.00  0.00           O  \n",
            "ATOM     99 CB   ILE A  13      32.995  35.883   9.934  1.00  0.00           C  \n",
            "ATOM    100 CG1  ILE A  13      33.306  34.381   9.840  1.00  0.00           C  \n",
            "ATOM    101 CG2  ILE A  13      33.109  36.381  11.435  1.00  0.00           C  \n",
            "ATOM    102 CD1  ILE A  13      34.535  34.028  10.720  1.00  0.00           C  \n",
            "ATOM    103  N   THR A  14      31.244  34.986   7.197  1.00  0.00           N  \n",
            "ATOM    104 CA   THR A  14      30.505  33.884   6.512  1.00  0.00           C  \n",
            "ATOM    105  C   THR A  14      31.409  32.680   6.446  1.00  0.00           C  \n",
            "ATOM    106  O   THR A  14      32.619  32.812   6.125  1.00  0.00           O  \n",
            "ATOM    107 CB   THR A  14      30.091  34.393   5.078  1.00  0.00           C  \n",
            "ATOM    108 OG1  THR A  14      31.440  34.513   4.487  1.00  0.00           O  \n",
            "ATOM    109 CG2  THR A  14      29.420  35.756   5.119  1.00  0.00           C  \n",
            "ATOM    110  N   LEU A  15      30.884  31.485   6.666  1.00  0.00           N  \n",
            "ATOM    111 CA   LEU A  15      31.677  30.275   6.639  1.00  0.00           C  \n",
            "ATOM    112  C   LEU A  15      31.022  29.288   5.665  1.00  0.00           C  \n",
            "ATOM    113  O   LEU A  15      29.809  29.395   5.545  1.00  0.00           O  \n",
            "ATOM    114 CB   LEU A  15      31.562  29.686   8.045  1.00  0.00           C  \n",
            "ATOM    115 CG   LEU A  15      32.631  29.444   9.060  1.00  0.00           C  \n",
            "ATOM    116 CD1  LEU A  15      33.814  30.390   9.030  1.00  0.00           C  \n",
            "ATOM    117 CD2  LEU A  15      31.945  29.449  10.436  1.00  0.00           C  \n",
            "ATOM    118  N   GLU A  16      31.834  28.412   5.125  1.00  0.00           N  \n",
            "ATOM    119 CA   GLU A  16      31.220  27.341   4.275  1.00  0.00           C  \n",
            "ATOM    120  C   GLU A  16      31.440  26.079   5.080  1.00  0.00           C  \n",
            "ATOM    121  O   GLU A  16      32.576  25.802   5.461  1.00  0.00           O  \n",
            "ATOM    122 CB   GLU A  16      31.827  27.262   2.894  1.00  0.00           C  \n",
            "ATOM    123 CG   GLU A  16      31.363  28.410   1.962  1.00  0.00           C  \n",
            "ATOM    124 CD   GLU A  16      31.671  28.291   0.498  1.00  0.00           C  \n",
            "ATOM    125 OE1  GLU A  16      30.869  28.621  -0.366  1.00  0.00           O  \n",
            "ATOM    126 OE2  GLU A  16      32.835  27.861   0.278  1.00  0.00           O  \n",
            "ATOM    127  N   VAL A  17      30.310  25.458   5.384  1.00  0.00           N  \n",
            "ATOM    128 CA   VAL A  17      30.288  24.245   6.193  1.00  0.00           C  \n",
            "ATOM    129  C   VAL A  17      29.279  23.227   5.641  1.00  0.00           C  \n",
            "ATOM    130  O   VAL A  17      28.478  23.522   4.725  1.00  0.00           O  \n",
            "ATOM    131 CB   VAL A  17      29.903  24.590   7.665  1.00  0.00           C  \n",
            "ATOM    132 CG1  VAL A  17      30.862  25.496   8.389  1.00  0.00           C  \n",
            "ATOM    133 CG2  VAL A  17      28.476  25.135   7.705  1.00  0.00           C  \n",
            "ATOM    134  N   GLU A  18      29.380  22.057   6.232  1.00  0.00           N  \n",
            "ATOM    135 CA   GLU A  18      28.468  20.940   5.980  1.00  0.00           C  \n",
            "ATOM    136  C   GLU A  18      27.819  20.609   7.316  1.00  0.00           C  \n",
            "ATOM    137  O   GLU A  18      28.449  20.674   8.360  1.00  0.00           O  \n",
            "ATOM    138 CB   GLU A  18      29.213  19.697   5.506  1.00  0.00           C  \n",
            "ATOM    139 CG   GLU A  18      29.728  19.755   4.060  1.00  0.00           C  \n",
            "ATOM    140 CD   GLU A  18      28.754  20.061   2.978  1.00  0.00           C  \n",
            "ATOM    141 OE1  GLU A  18      27.546  19.992   2.985  1.00  0.00           O  \n",
            "ATOM    142 OE2  GLU A  18      29.336  20.423   1.904  1.00  0.00           O  \n",
            "ATOM    143  N   PRO A  19      26.559  20.220   7.288  1.00  0.00           N  \n",
            "ATOM    144 CA   PRO A  19      25.829  19.825   8.494  1.00  0.00           C  \n",
            "ATOM    145  C   PRO A  19      26.541  18.732   9.251  1.00  0.00           C  \n",
            "ATOM    146  O   PRO A  19      26.333  18.536  10.457  1.00  0.00           O  \n",
            "ATOM    147 CB   PRO A  19      24.469  19.332   7.952  1.00  0.00           C  \n",
            "ATOM    148 CG   PRO A  19      24.299  20.134   6.704  1.00  0.00           C  \n",
            "ATOM    149 CD   PRO A  19      25.714  20.108   6.073  1.00  0.00           C  \n",
            "ATOM    150  N   SER A  20      27.361  17.959   8.559  1.00  0.00           N  \n",
            "ATOM    151 CA   SER A  20      28.054  16.835   9.210  1.00  0.00           C  \n",
            "ATOM    152  C   SER A  20      29.258  17.318   9.984  1.00  0.00           C  \n",
            "ATOM    153  O   SER A  20      29.930  16.477  10.606  1.00  0.00           O  \n",
            "ATOM    154 CB   SER A  20      28.523  15.820   8.182  1.00  0.00           C  \n",
            "ATOM    155 OG   SER A  20      28.946  16.445   6.967  1.00  0.00           O  \n",
            "ATOM    156  N   ASP A  21      29.599  18.599   9.828  1.00  0.00           N  \n",
            "ATOM    157 CA   ASP A  21      30.796  19.083  10.566  1.00  0.00           C  \n",
            "ATOM    158  C   ASP A  21      30.491  19.162  12.040  1.00  0.00           C  \n",
            "ATOM    159  O   ASP A  21      29.367  19.523  12.441  1.00  0.00           O  \n",
            "ATOM    160 CB   ASP A  21      31.155  20.515  10.048  1.00  0.00           C  \n",
            "ATOM    161 CG   ASP A  21      31.923  20.436   8.755  1.00  0.00           C  \n",
            "ATOM    162 OD1  ASP A  21      32.493  19.374   8.456  1.00  0.00           O  \n",
            "ATOM    163 OD2  ASP A  21      31.838  21.402   7.968  1.00  0.00           O  \n",
            "ATOM    164  N   THR A  22      31.510  18.936  12.852  1.00  0.00           N  \n",
            "ATOM    165 CA   THR A  22      31.398  19.064  14.286  1.00  0.00           C  \n",
            "ATOM    166  C   THR A  22      31.593  20.553  14.655  1.00  0.00           C  \n",
            "ATOM    167  O   THR A  22      32.159  21.311  13.861  1.00  0.00           O  \n",
            "ATOM    168 CB   THR A  22      32.492  18.193  14.995  1.00  0.00           C  \n",
            "ATOM    169 OG1  THR A  22      33.778  18.739  14.516  1.00  0.00           O  \n",
            "ATOM    170 CG2  THR A  22      32.352  16.700  14.630  1.00  0.00           C  \n",
            "ATOM    171  N   ILE A  23      31.113  20.863  15.860  1.00  0.00           N  \n",
            "ATOM    172 CA   ILE A  23      31.288  22.201  16.417  1.00  0.00           C  \n",
            "ATOM    173  C   ILE A  23      32.776  22.519  16.577  1.00  0.00           C  \n",
            "ATOM    174  O   ILE A  23      33.233  23.659  16.384  1.00  0.00           O  \n",
            "ATOM    175 CB   ILE A  23      30.520  22.300  17.764  1.00  0.00           C  \n",
            "ATOM    176 CG1  ILE A  23      29.006  22.043  17.442  1.00  0.00           C  \n",
            "ATOM    177 CG2  ILE A  23      30.832  23.699  18.358  1.00  0.00           C  \n",
            "ATOM    178 CD1  ILE A  23      28.407  22.948  16.366  1.00  0.00           C  \n",
            "ATOM    179  N   GLU A  24      33.548  21.526  16.950  1.00  0.00           N  \n",
            "ATOM    180 CA   GLU A  24      35.031  21.722  17.069  1.00  0.00           C  \n",
            "ATOM    181  C   GLU A  24      35.615  22.190  15.759  1.00  0.00           C  \n",
            "ATOM    182  O   GLU A  24      36.532  23.046  15.724  1.00  0.00           O  \n",
            "ATOM    183 CB   GLU A  24      35.667  20.383  17.447  1.00  0.00           C  \n",
            "ATOM    184 CG   GLU A  24      37.128  20.293  17.872  1.00  0.00           C  \n",
            "ATOM    185 CD   GLU A  24      37.561  18.851  18.082  1.00  0.00           C  \n",
            "ATOM    186 OE1  GLU A  24      37.758  18.024  17.195  1.00  0.00           O  \n",
            "ATOM    187 OE2  GLU A  24      37.628  18.599  19.313  1.00  0.00           O  \n",
            "ATOM    188  N   ASN A  25      35.139  21.624  14.662  1.00  0.00           N  \n",
            "ATOM    189 CA   ASN A  25      35.590  21.945  13.302  1.00  0.00           C  \n",
            "ATOM    190  C   ASN A  25      35.238  23.382  12.920  1.00  0.00           C  \n",
            "ATOM    191  O   ASN A  25      36.066  24.109  12.333  1.00  0.00           O  \n",
            "ATOM    192 CB   ASN A  25      35.064  20.957  12.255  1.00  0.00           C  \n",
            "ATOM    193 CG   ASN A  25      35.541  21.418  10.871  1.00  0.00           C  \n",
            "ATOM    194 OD1  ASN A  25      36.772  21.623  10.676  1.00  0.00           O  \n",
            "ATOM    195 ND2  ASN A  25      34.628  21.595   9.920  1.00  0.00           N  \n",
            "ATOM    196  N   VAL A  26      34.007  23.745  13.250  1.00  0.00           N  \n",
            "ATOM    197 CA   VAL A  26      33.533  25.097  12.978  1.00  0.00           C  \n",
            "ATOM    198  C   VAL A  26      34.441  26.099  13.684  1.00  0.00           C  \n",
            "ATOM    199  O   VAL A  26      34.883  27.090  13.093  1.00  0.00           O  \n",
            "ATOM    200 CB   VAL A  26      32.060  25.257  13.364  1.00  0.00           C  \n",
            "ATOM    201 CG1  VAL A  26      31.684  26.749  13.342  1.00  0.00           C  \n",
            "ATOM    202 CG2  VAL A  26      31.152  24.421  12.477  1.00  0.00           C  \n",
            "ATOM    203  N   LYS A  27      34.734  25.822  14.949  1.00  0.00           N  \n",
            "ATOM    204 CA   LYS A  27      35.596  26.715  15.736  1.00  0.00           C  \n",
            "ATOM    205  C   LYS A  27      36.975  26.826  15.107  1.00  0.00           C  \n",
            "ATOM    206  O   LYS A  27      37.579  27.926  15.159  1.00  0.00           O  \n",
            "ATOM    207 CB   LYS A  27      35.715  26.203  17.172  1.00  0.00           C  \n",
            "ATOM    208 CG   LYS A  27      34.343  26.445  17.898  1.00  0.00           C  \n",
            "ATOM    209 CD   LYS A  27      34.509  26.077  19.360  1.00  0.00           C  \n",
            "ATOM    210 CE   LYS A  27      33.206  26.311  20.122  1.00  0.00           C  \n",
            "ATOM    211 NZ   LYS A  27      33.455  25.910  21.546  1.00  0.00           N  \n",
            "ATOM    212  N   ALA A  28      37.499  25.743  14.571  1.00  0.00           N  \n",
            "ATOM    213 CA   ALA A  28      38.794  25.761  13.880  1.00  0.00           C  \n",
            "ATOM    214  C   ALA A  28      38.728  26.591  12.611  1.00  0.00           C  \n",
            "ATOM    215  O   ALA A  28      39.704  27.346  12.277  1.00  0.00           O  \n",
            "ATOM    216 CB   ALA A  28      39.285  24.336  13.566  1.00  0.00           C  \n",
            "ATOM    217  N   LYS A  29      37.633  26.543  11.867  1.00  0.00           N  \n",
            "ATOM    218 CA   LYS A  29      37.471  27.391  10.668  1.00  0.00           C  \n",
            "ATOM    219  C   LYS A  29      37.441  28.882  11.052  1.00  0.00           C  \n",
            "ATOM    220  O   LYS A  29      38.020  29.772  10.382  1.00  0.00           O  \n",
            "ATOM    221 CB   LYS A  29      36.193  27.058   9.911  1.00  0.00           C  \n",
            "ATOM    222 CG   LYS A  29      36.153  25.620   9.409  1.00  0.00           C  \n",
            "ATOM    223 CD   LYS A  29      34.758  25.280   8.900  1.00  0.00           C  \n",
            "ATOM    224 CE   LYS A  29      34.793  24.264   7.767  1.00  0.00           C  \n",
            "ATOM    225 NZ   LYS A  29      34.914  24.944   6.441  1.00  0.00           N  \n",
            "ATOM    226  N   ILE A  30      36.811  29.170  12.192  1.00  0.00           N  \n",
            "ATOM    227 CA   ILE A  30      36.731  30.570  12.645  1.00  0.00           C  \n",
            "ATOM    228  C   ILE A  30      38.148  30.981  13.069  1.00  0.00           C  \n",
            "ATOM    229  O   ILE A  30      38.544  32.150  12.856  1.00  0.00           O  \n",
            "ATOM    230 CB   ILE A  30      35.708  30.776  13.806  1.00  0.00           C  \n",
            "ATOM    231 CG1  ILE A  30      34.228  30.630  13.319  1.00  0.00           C  \n",
            "ATOM    232 CG2  ILE A  30      35.874  32.138  14.512  1.00  0.00           C  \n",
            "ATOM    233 CD1  ILE A  30      33.284  30.504  14.552  1.00  0.00           C  \n",
            "ATOM    234  N   GLN A  31      38.883  30.110  13.713  1.00  0.00           N  \n",
            "ATOM    235 CA   GLN A  31      40.269  30.508  14.115  1.00  0.00           C  \n",
            "ATOM    236  C   GLN A  31      41.092  30.808  12.851  1.00  0.00           C  \n",
            "ATOM    237  O   GLN A  31      41.828  31.808  12.681  1.00  0.00           O  \n",
            "ATOM    238 CB   GLN A  31      40.996  29.399  14.865  1.00  0.00           C  \n",
            "ATOM    239 CG   GLN A  31      42.445  29.848  15.182  1.00  0.00           C  \n",
            "ATOM    240 CD   GLN A  31      43.090  28.828  16.095  1.00  0.00           C  \n",
            "ATOM    241 OE1  GLN A  31      42.770  27.655  15.906  1.00  0.00           O  \n",
            "ATOM    242 NE2  GLN A  31      43.898  29.252  17.050  1.00  0.00           N  \n",
            "ATOM    243  N   ASP A  32      41.001  29.878  11.931  1.00  0.00           N  \n",
            "ATOM    244 CA   ASP A  32      41.718  30.022  10.643  1.00  0.00           C  \n",
            "ATOM    245  C   ASP A  32      41.399  31.338   9.967  1.00  0.00           C  \n",
            "ATOM    246  O   ASP A  32      42.260  32.036   9.381  1.00  0.00           O  \n",
            "ATOM    247 CB   ASP A  32      41.398  28.780   9.810  1.00  0.00           C  \n",
            "ATOM    248 CG   ASP A  32      42.626  28.557   8.928  1.00  0.00           C  \n",
            "ATOM    249 OD1  ASP A  32      43.666  28.262   9.539  1.00  0.00           O  \n",
            "ATOM    250 OD2  ASP A  32      42.430  28.812   7.728  1.00  0.00           O  \n",
            "ATOM    251  N   LYS A  33      40.117  31.750   9.988  1.00  0.00           N  \n",
            "ATOM    252 CA   LYS A  33      39.808  32.994   9.233  1.00  0.00           C  \n",
            "ATOM    253  C   LYS A  33      39.837  34.271   9.995  1.00  0.00           C  \n",
            "ATOM    254  O   LYS A  33      40.164  35.323   9.345  1.00  0.00           O  \n",
            "ATOM    255 CB   LYS A  33      38.615  32.801   8.320  1.00  0.00           C  \n",
            "ATOM    256 CG   LYS A  33      37.220  32.822   8.827  1.00  0.00           C  \n",
            "ATOM    257 CD   LYS A  33      36.351  33.613   7.838  1.00  0.00           C  \n",
            "ATOM    258 CE   LYS A  33      36.322  32.944   6.477  1.00  0.00           C  \n",
            "ATOM    259 NZ   LYS A  33      35.768  33.945   5.489  1.00  0.00           N  \n",
            "ATOM    260  N   GLU A  34      39.655  34.335  11.285  1.00  0.00           N  \n",
            "ATOM    261 CA   GLU A  34      39.676  35.547  12.072  1.00  0.00           C  \n",
            "ATOM    262  C   GLU A  34      40.675  35.527  13.200  1.00  0.00           C  \n",
            "ATOM    263  O   GLU A  34      40.814  36.528  13.911  1.00  0.00           O  \n",
            "ATOM    264 CB   GLU A  34      38.290  35.814  12.698  1.00  0.00           C  \n",
            "ATOM    265 CG   GLU A  34      37.156  35.985  11.688  1.00  0.00           C  \n",
            "ATOM    266 CD   GLU A  34      37.192  37.361  11.033  1.00  0.00           C  \n",
            "ATOM    267 OE1  GLU A  34      37.519  38.360  11.645  1.00  0.00           O  \n",
            "ATOM    268 OE2  GLU A  34      36.861  37.320   9.822  1.00  0.00           O  \n",
            "TER     269      GLU A  34                                                      \n",
            "MASTER        0    0    0    0    0    0    0    0  268    1    0    0          \n",
            "END                                                                             \n"
        ]

        # Check the data.
        for i in range(len(real_data)):
            self.assertEqual(real_data[i], lines[i])


    def test_read_xyz_internal1(self):
        """Load the 'Indol_test.xyz' XYZ file (using the internal structural object XYZ reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the XYZ file.
        self.interpreter.structure.read_xyz(file='Indol_test.xyz', dir=path)

        # Test the molecule name.
        self.assertEqual(cdp.structure.structural_data[0].mol[0].mol_name, 'Indol_test_mol1')

        # Load a single atom and test it.
        self.interpreter.structure.load_spins('#Indol_test_mol1@3')
        self.assertEqual(count_spins(), 1)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_xyz_internal2(self):
        """Load the 'SSS-cluster4-new-test.xyz' XYZ file (using the internal structural object XYZ reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the XYZ file.
        self.interpreter.structure.read_xyz(file='SSS-cluster4-new-test.xyz', dir=path, read_model=[1])

        # Test the molecule name.
        self.assertEqual(cdp.structure.structural_data[0].mol[0].mol_name, 'SSS-cluster4-new-test_mol1')

        # Load a single atom and test it.
        self.interpreter.structure.load_spins('#SSS-cluster4-new-test_mol1@2')
        self.assertEqual(count_spins(), 1)

        # Test the spin coordinates.
        a=return_spin('#SSS-cluster4-new-test_mol1@2')
        self.assertAlmostEqual(a.pos[0], -12.398)
        self.assertAlmostEqual(a.pos[1], -15.992)
        self.assertAlmostEqual(a.pos[2], 11.448)

        # Try loading a few protons.
        #self.interpreter.structure.load_spins('@H')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Extract a vector between first two spins.
        self.interpreter.dipole_pair.define(spin_id1='@2', spin_id2='@10')
        self.interpreter.dipole_pair.unit_vectors()
        self.assertAlmostEqual(cdp.interatomic[0].vector[0], -0.4102707)
        self.assertAlmostEqual(cdp.interatomic[0].vector[1], 0.62128879)
        self.assertAlmostEqual(cdp.interatomic[0].vector[2], -0.6675913)


    def test_read_xyz_strychnine(self):
        """Load the 'strychnine.xyz' XYZ file (using the internal structural object XYZ reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the XYZ file.
        self.interpreter.structure.read_xyz(file='strychnine.xyz', dir=path, set_mol_name='strychnine')

        # Test the molecule data.
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 1)

        # Load the carbon atoms and test it.
        self.interpreter.structure.load_spins('@C')
        self.assertEqual(count_spins(), 21)

        # Load the protons.
        self.interpreter.structure.load_spins('@H')
        self.assertEqual(count_spins(), 43)

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_rmsd(self):
        """Test the structure.rmsd user function."""

        # Set up 3 models.
        self.interpreter.structure.add_model(model_num=1)
        self.interpreter.structure.add_model(model_num=2)
        self.interpreter.structure.add_model(model_num=4)

        # Check that the models were correctly created.
        self.assert_(hasattr(cdp, 'structure'))
        self.assert_(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 3)

        # Create a structure with some atoms.
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=1, pos=[[1., 0., -1.], [0., 0., 0.], [-1., 0., 1.]], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=2, pos=[[1., 2., -1.], [0., 2., 0.], [-1., 2., 1.]], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=3, pos=[[1., 20., -1.], [0., 20., 0.], [-1., 20., 1.]], element='S')

        # Check the internal atomic info.
        self.assertEqual(cdp.structure.structural_data[0].mol[0].x, [1., 1., 1.])
        self.assertEqual(cdp.structure.structural_data[0].mol[0].y, [0., 2., 20.])
        self.assertEqual(cdp.structure.structural_data[0].mol[0].z, [-1., -1., -1.])
        self.assertEqual(cdp.structure.structural_data[1].mol[0].x, [0., 0., 0.])
        self.assertEqual(cdp.structure.structural_data[1].mol[0].y, [0., 2., 20.])
        self.assertEqual(cdp.structure.structural_data[1].mol[0].z, [0., 0., 0.])
        self.assertEqual(cdp.structure.structural_data[2].mol[0].x, [-1., -1., -1.])
        self.assertEqual(cdp.structure.structural_data[2].mol[0].y, [0., 2., 20.])
        self.assertEqual(cdp.structure.structural_data[2].mol[0].z, [1., 1., 1.])

        # Calculate the RMSD.
        self.interpreter.structure.rmsd()

        # Checks.
        self.assert_(hasattr(cdp.structure, 'rmsd'))
        self.assertAlmostEqual(cdp.structure.rmsd, 2./3*sqrt(2))


    def test_rmsd_ubi(self):
        """Test the structure.rmsd user function on the truncated ubiquitin ensemble."""

        # Load the structure.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('trunc_ubi_pcs.pdb', dir=path)

        # Calculate the RMSD.
        self.interpreter.structure.rmsd()

        # Checks (the values match the VMD 1.9.1 RMSD numbers).
        self.assert_(hasattr(cdp.structure, 'rmsd'))
        self.assertAlmostEqual(cdp.structure.rmsd, 0.77282758781333061)


    def test_superimpose_fit_to_first(self):
        """Test of the structure.superimpose user function, fitting to the first structure."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'

        # Load the two rotated structures.
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=path, set_model_num=1, set_mol_name='CaM')
        self.interpreter.structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=path, set_model_num=2, set_mol_name='CaM')
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=path, set_model_num=3, set_mol_name='CaM')

        # Superimpose the backbone heavy atoms.
        self.interpreter.structure.superimpose(method='fit to first', atom_id='@N,C,CA,O')

        # Check that the two structures now have the same atomic coordinates.
        model1 = cdp.structure.structural_data[0].mol[0]
        model2 = cdp.structure.structural_data[1].mol[0]
        model3 = cdp.structure.structural_data[2].mol[0]
        for i in range(len(model1.atom_name)):
            # Check model 2.
            self.assertAlmostEqual(model1.x[i], model2.x[i], 2)
            self.assertAlmostEqual(model1.y[i], model2.y[i], 2)
            self.assertAlmostEqual(model1.z[i], model2.z[i], 2)

            # Check model 3.
            self.assertAlmostEqual(model1.x[i], model3.x[i], 2)
            self.assertAlmostEqual(model1.y[i], model3.y[i], 2)
            self.assertAlmostEqual(model1.z[i], model3.z[i], 2)


    def test_superimpose_fit_to_mean(self):
        """Test of the structure.superimpose user function, fitting to the mean structure."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'

        # Load the two rotated structures.
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=path, set_model_num=1, set_mol_name='CaM')
        self.interpreter.structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=path, set_model_num=2, set_mol_name='CaM')

        # Superimpose the backbone heavy atoms.
        self.interpreter.structure.superimpose(method='fit to mean', atom_id='@N,C,CA,O')

        # Check that the two structures now have the same atomic coordinates.
        model1 = cdp.structure.structural_data[0].mol[0]
        model2 = cdp.structure.structural_data[1].mol[0]
        for i in range(len(model1.atom_name)):
            self.assertAlmostEqual(model1.x[i], model2.x[i], 2)
            self.assertAlmostEqual(model1.y[i], model2.y[i], 2)
            self.assertAlmostEqual(model1.z[i], model2.z[i], 2)


    def test_superimpose_fit_to_mean2(self):
        """Second test of the structure.superimpose user function, fitting to the mean structure."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'

        # Load the two rotated structures.
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=path, set_model_num=1, set_mol_name='CaM')
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=path, set_model_num=2, set_mol_name='CaM')
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=path, set_model_num=3, set_mol_name='CaM')

        # Transpose model 3.
        self.interpreter.structure.translate([20.0, 0.0, 0.0], model=3)

        # Superimpose the backbone heavy atoms.
        self.interpreter.structure.superimpose(models=[2, 3], method='fit to mean', atom_id='@N,C,CA,O')

        # Check that the two structures now have the same atomic coordinates as the original, but shifted 10 Angstrom in x.
        model1 = cdp.structure.structural_data[0].mol[0]
        model2 = cdp.structure.structural_data[1].mol[0]
        model3 = cdp.structure.structural_data[2].mol[0]
        for i in range(len(model1.atom_name)):
            # Check model 2.
            self.assertAlmostEqual(model1.x[i] + 10, model2.x[i], 2)
            self.assertAlmostEqual(model1.y[i], model2.y[i], 2)
            self.assertAlmostEqual(model1.z[i], model2.z[i], 2)

            # Check model 3.
            self.assertAlmostEqual(model2.x[i], model3.x[i], 2)
            self.assertAlmostEqual(model2.y[i], model3.y[i], 2)
            self.assertAlmostEqual(model2.z[i], model3.z[i], 2)


    def test_web_of_motion_12(self):
        """Check the operation of the structure.web_of_motion user function using structural models 1 and 2 (of 3)."""

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path)

        # Run the structure.web_of_motion user function and collect the results in a dummy file object.
        file = DummyFileObject()
        self.interpreter.structure.web_of_motion(file=file, models=[1, 2])

        # The result.
        result = [
            "REMARK   4 THIS FILE COMPLIES WITH FORMAT V. 3.30, JUL-2011.                    ",
            "REMARK  40 CREATED BY RELAX (HTTP://NMR-RELAX.COM).                             ",
            "ATOM      1  N   LEU     4       9.464  -9.232  27.573  1.00  0.00           N  ",
            "ATOM      2  N   LEU     4       9.211  -9.425  26.970  1.00  0.00           N  ",
            "ATOM      3  H   LEU     4       8.575  -8.953  27.963  1.00  0.00           H  ",
            "ATOM      4  H   LEU     4       9.085  -9.743  27.919  1.00  0.00           H  ",
            "ATOM      5 CA   LEU     4      10.302  -8.195  26.930  1.00  0.00           C  ",
            "ATOM      6 CA   LEU     4      10.077  -8.221  26.720  1.00  0.00           C  ",
            "ATOM      7 CB   LEU     4       9.494  -7.221  26.051  1.00  0.00           C  ",
            "ATOM      8 CB   LEU     4       9.297  -7.096  26.024  1.00  0.00           C  ",
            "ATOM      9 CG   LEU     4      10.107  -5.862  25.665  1.00  0.00           C  ",
            "ATOM     10 CG   LEU     4      10.061  -5.803  25.679  1.00  0.00           C  ",
            "ATOM     11 CD1  LEU     4      11.182  -6.007  24.608  1.00  0.00           C  ",
            "ATOM     12 CD1  LEU     4      11.029  -6.002  24.507  1.00  0.00           C  ",
            "ATOM     13 CD2  LEU     4       9.036  -4.875  25.171  1.00  0.00           C  ",
            "ATOM     14 CD2  LEU     4       9.120  -4.618  25.384  1.00  0.00           C  ",
            "ATOM     15  C   LEU     4      10.999  -7.436  28.046  1.00  0.00           C  ",
            "ATOM     16  C   LEU     4      10.625  -7.721  28.047  1.00  0.00           C  ",
            "TER      17      LEU     4                                                      ",
            "CONECT    1    2                                                                ",
            "CONECT    2    1                                                                ",
            "CONECT    3    4                                                                ",
            "CONECT    4    3                                                                ",
            "CONECT    5    6                                                                ",
            "CONECT    6    5                                                                ",
            "CONECT    7    8                                                                ",
            "CONECT    8    7                                                                ",
            "CONECT    9   10                                                                ",
            "CONECT   10    9                                                                ",
            "CONECT   11   12                                                                ",
            "CONECT   12   11                                                                ",
            "CONECT   13   14                                                                ",
            "CONECT   14   13                                                                ",
            "CONECT   15   16                                                                ",
            "CONECT   16   15                                                                ",
            "MASTER        0    0    0    0    0    0    0    0   16    1   16    0          ",
            "END                                                                             "
        ]

        # Check the created PDB file.
        lines = file.readlines()
        for i in range(len(lines)):
            self.assertEqual(result[i]+'\n', lines[i])


    def test_web_of_motion_13(self):
        """Check the operation of the structure.web_of_motion user function using structural models 1 and 3 (of 3)."""

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path)

        # Run the structure.web_of_motion user function and collect the results in a dummy file object.
        file = DummyFileObject()
        self.interpreter.structure.web_of_motion(file=file, models=[1, 3])

        # The result.
        result = [
            "REMARK   4 THIS FILE COMPLIES WITH FORMAT V. 3.30, JUL-2011.                    ",
            "REMARK  40 CREATED BY RELAX (HTTP://NMR-RELAX.COM).                             ",
            "ATOM      1  N   LEU     4       9.464  -9.232  27.573  1.00  0.00           N  ",
            "ATOM      2  N   LEU     4       7.761  -6.392  27.161  1.00  0.00           N  ",
            "ATOM      3  H   LEU     4       8.575  -8.953  27.963  1.00  0.00           H  ",
            "ATOM      4  H   LEU     4       7.278  -6.195  28.026  1.00  0.00           H  ",
            "ATOM      5 CA   LEU     4      10.302  -8.195  26.930  1.00  0.00           C  ",
            "ATOM      6 CA   LEU     4       9.256  -6.332  27.183  1.00  0.00           C  ",
            "ATOM      7 CB   LEU     4       9.494  -7.221  26.051  1.00  0.00           C  ",
            "ATOM      8 CB   LEU     4       9.799  -5.331  26.144  1.00  0.00           C  ",
            "ATOM      9 CG   LEU     4      10.107  -5.862  25.665  1.00  0.00           C  ",
            "ATOM     10 CG   LEU     4      10.293  -5.882  24.803  1.00  0.00           C  ",
            "ATOM     11 CD1  LEU     4      11.182  -6.007  24.608  1.00  0.00           C  ",
            "ATOM     12 CD1  LEU     4       9.404  -6.984  24.274  1.00  0.00           C  ",
            "ATOM     13 CD2  LEU     4       9.036  -4.875  25.171  1.00  0.00           C  ",
            "ATOM     14 CD2  LEU     4      10.355  -4.772  23.792  1.00  0.00           C  ",
            "ATOM     15  C   LEU     4      10.999  -7.436  28.046  1.00  0.00           C  ",
            "ATOM     16  C   LEU     4       9.816  -6.033  28.572  1.00  0.00           C  ",
            "TER      17      LEU     4                                                      ",
            "CONECT    1    2                                                                ",
            "CONECT    2    1                                                                ",
            "CONECT    3    4                                                                ",
            "CONECT    4    3                                                                ",
            "CONECT    5    6                                                                ",
            "CONECT    6    5                                                                ",
            "CONECT    7    8                                                                ",
            "CONECT    8    7                                                                ",
            "CONECT    9   10                                                                ",
            "CONECT   10    9                                                                ",
            "CONECT   11   12                                                                ",
            "CONECT   12   11                                                                ",
            "CONECT   13   14                                                                ",
            "CONECT   14   13                                                                ",
            "CONECT   15   16                                                                ",
            "CONECT   16   15                                                                ",
            "MASTER        0    0    0    0    0    0    0    0   16    1   16    0          ",
            "END                                                                             "
        ]

        # Check the created PDB file.
        lines = file.readlines()
        for i in range(len(lines)):
            self.assertEqual(result[i]+'\n', lines[i])


    def test_web_of_motion_all(self):
        """Check the operation of the structure.web_of_motion user function using all structural models."""

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path)

        # Run the structure.web_of_motion user function and collect the results in a dummy file object.
        file = DummyFileObject()
        self.interpreter.structure.web_of_motion(file=file)

        # The result.
        result = [
            "REMARK   4 THIS FILE COMPLIES WITH FORMAT V. 3.30, JUL-2011.                    ",
            "REMARK  40 CREATED BY RELAX (HTTP://NMR-RELAX.COM).                             ",
            "ATOM      1  N   LEU     4       9.464  -9.232  27.573  1.00  0.00           N  ",
            "ATOM      2  N   LEU     4       9.211  -9.425  26.970  1.00  0.00           N  ",
            "ATOM      3  N   LEU     4       7.761  -6.392  27.161  1.00  0.00           N  ",
            "ATOM      4  H   LEU     4       8.575  -8.953  27.963  1.00  0.00           H  ",
            "ATOM      5  H   LEU     4       9.085  -9.743  27.919  1.00  0.00           H  ",
            "ATOM      6  H   LEU     4       7.278  -6.195  28.026  1.00  0.00           H  ",
            "ATOM      7 CA   LEU     4      10.302  -8.195  26.930  1.00  0.00           C  ",
            "ATOM      8 CA   LEU     4      10.077  -8.221  26.720  1.00  0.00           C  ",
            "ATOM      9 CA   LEU     4       9.256  -6.332  27.183  1.00  0.00           C  ",
            "ATOM     10 CB   LEU     4       9.494  -7.221  26.051  1.00  0.00           C  ",
            "ATOM     11 CB   LEU     4       9.297  -7.096  26.024  1.00  0.00           C  ",
            "ATOM     12 CB   LEU     4       9.799  -5.331  26.144  1.00  0.00           C  ",
            "ATOM     13 CG   LEU     4      10.107  -5.862  25.665  1.00  0.00           C  ",
            "ATOM     14 CG   LEU     4      10.061  -5.803  25.679  1.00  0.00           C  ",
            "ATOM     15 CG   LEU     4      10.293  -5.882  24.803  1.00  0.00           C  ",
            "ATOM     16 CD1  LEU     4      11.182  -6.007  24.608  1.00  0.00           C  ",
            "ATOM     17 CD1  LEU     4      11.029  -6.002  24.507  1.00  0.00           C  ",
            "ATOM     18 CD1  LEU     4       9.404  -6.984  24.274  1.00  0.00           C  ",
            "ATOM     19 CD2  LEU     4       9.036  -4.875  25.171  1.00  0.00           C  ",
            "ATOM     20 CD2  LEU     4       9.120  -4.618  25.384  1.00  0.00           C  ",
            "ATOM     21 CD2  LEU     4      10.355  -4.772  23.792  1.00  0.00           C  ",
            "ATOM     22  C   LEU     4      10.999  -7.436  28.046  1.00  0.00           C  ",
            "ATOM     23  C   LEU     4      10.625  -7.721  28.047  1.00  0.00           C  ",
            "ATOM     24  C   LEU     4       9.816  -6.033  28.572  1.00  0.00           C  ",
            "TER      25      LEU     4                                                      ",
            "CONECT    1    2    3                                                           ",
            "CONECT    2    1    3                                                           ",
            "CONECT    3    1    2                                                           ",
            "CONECT    4    5    6                                                           ",
            "CONECT    5    4    6                                                           ",
            "CONECT    6    4    5                                                           ",
            "CONECT    7    8    9                                                           ",
            "CONECT    8    7    9                                                           ",
            "CONECT    9    7    8                                                           ",
            "CONECT   10   11   12                                                           ",
            "CONECT   11   10   12                                                           ",
            "CONECT   12   10   11                                                           ",
            "CONECT   13   14   15                                                           ",
            "CONECT   14   13   15                                                           ",
            "CONECT   15   13   14                                                           ",
            "CONECT   16   17   18                                                           ",
            "CONECT   17   16   18                                                           ",
            "CONECT   18   16   17                                                           ",
            "CONECT   19   20   21                                                           ",
            "CONECT   20   19   21                                                           ",
            "CONECT   21   19   20                                                           ",
            "CONECT   22   23   24                                                           ",
            "CONECT   23   22   24                                                           ",
            "CONECT   24   22   23                                                           ",
            "MASTER        0    0    0    0    0    0    0    0   24    1   24    0          ",
            "END                                                                             "
        ]

        # Check the created PDB file.
        lines = file.readlines()
        for i in range(len(lines)):
            self.assertEqual(result[i]+'\n', lines[i])
