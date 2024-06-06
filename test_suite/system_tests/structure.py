###############################################################################
#                                                                             #
# Copyright (C) 2008-2017,2019,2024 Edward d'Auvergne                         #
# Copyright (C) 2011 Han Sun                                                  #
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
from numpy import array, average, dot, float64, mean, sign, std, zeros
from numpy.linalg import norm
from os import path, sep
from re import search
import sys
from tempfile import mkdtemp, mkstemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.mol_res_spin import count_spins, return_spin, spin_loop
from lib.errors import RelaxError
from lib.geometry.rotations import axis_angle_to_R, euler_to_R_zyz
from lib.geometry.vectors import vector_angle_acos
from lib.io import DummyFileObject
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Structure(SystemTestCase):
    """Class for testing the structural objects."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()


    def strip_remarks(self, lines):
        """Strip out all PDB remark lines.

        @param lines:   The list of PDB lines.
        @type lines:    list of str
        """

        # Rebuild the list.
        lines[:] = [x for x in lines if x[:6] != 'REMARK']


    def test_add_secondary_structure(self):
        """Check the operation of the structure.add_helix and structure.add_sheet user functions."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file.
        self.interpreter.structure.read_pdb('2BE6.pdb', dir=path, read_mol=[1, 4], set_mol_name='CaM A', alt_loc='A')
        self.interpreter.structure.read_pdb('2BE6.pdb', dir=path, read_mol=[2, 5], set_mol_name='CaM B', alt_loc='A')
        self.interpreter.structure.read_pdb('2BE6.pdb', dir=path, read_mol=[3, 6], set_mol_name='CaM C', alt_loc='A')

        # Strip out the secondary structure.
        self.interpreter.structure.delete_ss()

        # Manually recreate the secondary structure.
        self.interpreter.structure.add_helix(start=5,    end=20,   mol_name='CaM A')
        self.interpreter.structure.add_helix(start=28,   end=39,   mol_name='CaM A')
        self.interpreter.structure.add_helix(start=44,   end=56,   mol_name='CaM A')
        self.interpreter.structure.add_helix(start=65,   end=76,   mol_name='CaM A')
        self.interpreter.structure.add_helix(start=81,   end=93,   mol_name='CaM A')
        self.interpreter.structure.add_helix(start=101,  end=112,  mol_name='CaM A')
        self.interpreter.structure.add_helix(start=117,  end=129,  mol_name='CaM A')
        self.interpreter.structure.add_helix(start=138,  end=146,  mol_name='CaM A')
        self.interpreter.structure.add_helix(start=1615, end=1638, mol_name='CaM A')
        self.interpreter.structure.add_helix(start=5,    end=20,   mol_name='CaM B')
        self.interpreter.structure.add_helix(start=28,   end=39,   mol_name='CaM B')
        self.interpreter.structure.add_helix(start=44,   end=56,   mol_name='CaM B')
        self.interpreter.structure.add_helix(start=65,   end=78,   mol_name='CaM B')
        self.interpreter.structure.add_helix(start=82,   end=93,   mol_name='CaM B')
        self.interpreter.structure.add_helix(start=101,  end=113,  mol_name='CaM B')
        self.interpreter.structure.add_helix(start=117,  end=129,  mol_name='CaM B')
        self.interpreter.structure.add_helix(start=138,  end=145,  mol_name='CaM B')
        self.interpreter.structure.add_helix(start=1612, end=1625, mol_name='CaM B')
        self.interpreter.structure.add_helix(start=5,    end=20,   mol_name='CaM C')
        self.interpreter.structure.add_helix(start=28,   end=39,   mol_name='CaM C')
        self.interpreter.structure.add_helix(start=44,   end=56,   mol_name='CaM C')
        self.interpreter.structure.add_helix(start=65,   end=75,   mol_name='CaM C')
        self.interpreter.structure.add_helix(start=82,   end=93,   mol_name='CaM C')
        self.interpreter.structure.add_helix(start=101,  end=112,  mol_name='CaM C')
        self.interpreter.structure.add_helix(start=117,  end=129,  mol_name='CaM C')
        self.interpreter.structure.add_helix(start=138,  end=145,  mol_name='CaM C')
        self.interpreter.structure.add_helix(start=1617, end=1636, mol_name='CaM C')
        self.interpreter.structure.add_sheet(strand=1, sheet_id='A', strand_count=2, strand_sense=0,  start=26,  end=27,  mol_name='CaM A')
        self.interpreter.structure.add_sheet(strand=2, sheet_id='A', strand_count=2, strand_sense=-1, start=63,  end=64,  mol_name='CaM A', current_atom='O', prev_atom='N')
        self.interpreter.structure.add_sheet(strand=1, sheet_id='B', strand_count=2, strand_sense=0,  start=99,  end=100, mol_name='CaM A')
        self.interpreter.structure.add_sheet(strand=2, sheet_id='B', strand_count=2, strand_sense=-1, start=136, end=137, mol_name='CaM A', current_atom='O', prev_atom='N')
        self.interpreter.structure.add_sheet(strand=1, sheet_id='C', strand_count=2, strand_sense=0,  start=26,  end=27,  mol_name='CaM B')
        self.interpreter.structure.add_sheet(strand=2, sheet_id='C', strand_count=2, strand_sense=-1, start=63,  end=64,  mol_name='CaM B', current_atom='O', prev_atom='N')
        self.interpreter.structure.add_sheet(strand=1, sheet_id='D', strand_count=2, strand_sense=0,  start=99,  end=100, mol_name='CaM B')
        self.interpreter.structure.add_sheet(strand=2, sheet_id='D', strand_count=2, strand_sense=-1, start=136, end=137, mol_name='CaM B', current_atom='O', prev_atom='N')
        self.interpreter.structure.add_sheet(strand=1, sheet_id='E', strand_count=2, strand_sense=0,  start=26,  end=27,  mol_name='CaM C')
        self.interpreter.structure.add_sheet(strand=2, sheet_id='E', strand_count=2, strand_sense=-1, start=63,  end=64,  mol_name='CaM C', current_atom='O', prev_atom='N')
        self.interpreter.structure.add_sheet(strand=1, sheet_id='F', strand_count=2, strand_sense=0,  start=99,  end=100, mol_name='CaM C')
        self.interpreter.structure.add_sheet(strand=2, sheet_id='F', strand_count=2, strand_sense=-1, start=136, end=137, mol_name='CaM C', current_atom='O', prev_atom='N')

        # Create a PDB file.
        file = DummyFileObject()
        self.interpreter.structure.write_pdb(file=file, force=True)

        # The HELIX and SHEET contents, as from the original 2BE6 PDB file.
        #     "HELIX    1   1 THR A    5  ASP A   20  1                                  16    "
        #     "HELIX    2   2 THR A   28  LEU A   39  1                                  12    "
        #     "HELIX    3   3 THR A   44  ASP A   56  1                                  13    "
        #     "HELIX    4   4 PHE A   65  MET A   76  1                                  12    "
        #     "HELIX    5   5 SER A   81  ASP A   93  1                                  13    "
        #     "HELIX    6   6 SER A  101  LEU A  112  1                                  12    "
        #     "HELIX    7   7 THR A  117  ASP A  129  1                                  13    "
        #     "HELIX    8   8 TYR A  138  THR A  146  1                                   9    "
        #     "HELIX    9   9 VAL D 1615  GLY D 1638  1                                  24    "
        #     "HELIX   10  10 THR B    5  ASP B   20  1                                  16    "
        #     "HELIX   11  11 THR B   28  LEU B   39  1                                  12    "
        #     "HELIX   12  12 THR B   44  ASP B   56  1                                  13    "
        #     "HELIX   13  13 PHE B   65  ASP B   78  1                                  14    "
        #     "HELIX   14  14 GLU B   82  ASP B   93  1                                  12    "
        #     "HELIX   15  15 SER B  101  GLY B  113  1                                  13    "
        #     "HELIX   16  16 THR B  117  ASP B  129  1                                  13    "
        #     "HELIX   17  17 TYR B  138  MET B  145  1                                   8    "
        #     "HELIX   18  18 GLU E 1612  GLN E 1625  1                                  14    "
        #     "HELIX   19  19 THR C    5  ASP C   20  1                                  16    "
        #     "HELIX   20  20 THR C   28  LEU C   39  1                                  12    "
        #     "HELIX   21  21 THR C   44  ASP C   56  1                                  13    "
        #     "HELIX   22  22 PHE C   65  LYS C   75  1                                  11    "
        #     "HELIX   23  23 GLU C   82  ASP C   93  1                                  12    "
        #     "HELIX   24  24 SER C  101  LEU C  112  1                                  12    "
        #     "HELIX   25  25 THR C  117  ASP C  129  1                                  13    "
        #     "HELIX   26  26 TYR C  138  MET C  145  1                                   8    "
        #     "HELIX   27  27 LYS F 1617  GLU F 1636  1                                  20    "
        #     "SHEET    1   A 2 THR A  26  ILE A  27  0                                        "
        #     "SHEET    2   A 2 ILE A  63  ASP A  64 -1  O  ILE A  63   N  ILE A  27           "
        #     "SHEET    1   B 2 TYR A  99  ILE A 100  0                                        "
        #     "SHEET    2   B 2 VAL A 136  ASN A 137 -1  O  VAL A 136   N  ILE A 100           "
        #     "SHEET    1   C 2 THR B  26  ILE B  27  0                                        "
        #     "SHEET    2   C 2 ILE B  63  ASP B  64 -1  O  ILE B  63   N  ILE B  27           "
        #     "SHEET    1   D 2 TYR B  99  ILE B 100  0                                        "
        #     "SHEET    2   D 2 VAL B 136  ASN B 137 -1  O  VAL B 136   N  ILE B 100           "
        #     "SHEET    1   E 2 THR C  26  ILE C  27  0                                        "
        #     "SHEET    2   E 2 ILE C  63  ASP C  64 -1  O  ILE C  63   N  ILE C  27           "
        #     "SHEET    1   F 2 TYR C  99  ILE C 100  0                                        "
        #     "SHEET    2   F 2 VAL C 136  ASN C 137 -1  O  VAL C 136   N  ILE C 100           "

        # The HELIX and SHEET contents, as currently supported by relax.
        contents = [
            "HELIX    1   1 THR A    5  ASP A   20  1                                  16    \n",
            "HELIX    2   2 THR A   28  LEU A   39  1                                  12    \n",
            "HELIX    3   3 THR A   44  ASP A   56  1                                  13    \n",
            "HELIX    4   4 PHE A   65  MET A   76  1                                  12    \n",
            "HELIX    5   5 SER A   81  ASP A   93  1                                  13    \n",
            "HELIX    6   6 SER A  101  LEU A  112  1                                  12    \n",
            "HELIX    7   7 THR A  117  ASP A  129  1                                  13    \n",
            "HELIX    8   8 TYR A  138  THR A  146  1                                   9    \n",
            "HELIX    9   9 VAL A 1615  GLY A 1638  1                                  24    \n",
            "HELIX   10  10 THR B    5  ASP B   20  1                                  16    \n",
            "HELIX   11  11 THR B   28  LEU B   39  1                                  12    \n",
            "HELIX   12  12 THR B   44  ASP B   56  1                                  13    \n",
            "HELIX   13  13 PHE B   65  ASP B   78  1                                  14    \n",
            "HELIX   14  14 GLU B   82  ASP B   93  1                                  12    \n",
            "HELIX   15  15 SER B  101  GLY B  113  1                                  13    \n",
            "HELIX   16  16 THR B  117  ASP B  129  1                                  13    \n",
            "HELIX   17  17 TYR B  138  MET B  145  1                                   8    \n",
            "HELIX   18  18 GLU B 1612  GLN B 1625  1                                  14    \n",
            "HELIX   19  19 THR C    5  ASP C   20  1                                  16    \n",
            "HELIX   20  20 THR C   28  LEU C   39  1                                  12    \n",
            "HELIX   21  21 THR C   44  ASP C   56  1                                  13    \n",
            "HELIX   22  22 PHE C   65  LYS C   75  1                                  11    \n",
            "HELIX   23  23 GLU C   82  ASP C   93  1                                  12    \n",
            "HELIX   24  24 SER C  101  LEU C  112  1                                  12    \n",
            "HELIX   25  25 THR C  117  ASP C  129  1                                  13    \n",
            "HELIX   26  26 TYR C  138  MET C  145  1                                   8    \n",
            "HELIX   27  27 LYS C 1617  GLU C 1636  1                                  20    \n",
            "SHEET    1   A 2 THR A  26  ILE A  27  0                                        \n",
            "SHEET    2   A 2 ILE A  63  ASP A  64 -1  O  ILE A  63   N  ILE A  27           \n",
            "SHEET    1   B 2 TYR A  99  ILE A 100  0                                        \n",
            "SHEET    2   B 2 VAL A 136  ASN A 137 -1  O  VAL A 136   N  ILE A 100           \n",
            "SHEET    1   C 2 THR B  26  ILE B  27  0                                        \n",
            "SHEET    2   C 2 ILE B  63  ASP B  64 -1  O  ILE B  63   N  ILE B  27           \n",
            "SHEET    1   D 2 TYR B  99  ILE B 100  0                                        \n",
            "SHEET    2   D 2 VAL B 136  ASN B 137 -1  O  VAL B 136   N  ILE B 100           \n",
            "SHEET    1   E 2 THR C  26  ILE C  27  0                                        \n",
            "SHEET    2   E 2 ILE C  63  ASP C  64 -1  O  ILE C  63   N  ILE C  27           \n",
            "SHEET    1   F 2 TYR C  99  ILE C 100  0                                        \n",
            "SHEET    2   F 2 VAL C 136  ASN C 137 -1  O  VAL C 136   N  ILE C 100           \n",
        ]

        # Check the created PDB file.
        lines = file.readlines()
        index = 0
        for line in lines:
            # Skip non-secondary structure records.
            if not search('^HELIX', line) and not search('^SHEET', line):
                continue

            # Check the line.
            print("\nOrig: %s" % repr(contents[index]))
            print("New:  %s" % repr(line))
            self.assertEqual(contents[index], line)

            # Increment the secondary structure index.
            index += 1

        # Check the count to make sure that secondary structure records have at all been created.
        self.assertEqual(len(contents), index)


    def test_align(self):
        """Test the U{structure.superimpose user function<http://www.nmr-relax.com/manual/structure_superimpose.html>}."""

        # Reset relax.
        self.interpreter.reset()

        # Path of the PDB file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'diffusion_tensor'+sep+'sphere'

        # Create a data pipe for the reference structure, then load it.
        self.interpreter.pipe.create('ref', 'N-state')
        self.interpreter.structure.read_pdb('uniform.pdb', dir=path)

        # Delete a residue and atom.
        self.interpreter.structure.delete(":8")
        self.interpreter.structure.delete(":2@N")

        # Output PDB to stdout to help in debugging.
        self.interpreter.structure.write_pdb(file=sys.stdout)

        # Create a second data pipe for the structures to align and superimpose.
        self.interpreter.pipe.create('align', 'N-state')

        # Load the PDB twice as different models.
        self.interpreter.structure.read_pdb('uniform.pdb', dir=path, set_model_num=1)
        self.interpreter.structure.read_pdb('uniform.pdb', dir=path, set_model_num=2)

        # Delete a residue and atom.
        self.interpreter.structure.delete(":12")
        self.interpreter.structure.delete(":20@H")

        # Translate and rotate the models.
        R = zeros((3, 3), float64)
        axis_angle_to_R(array([1, 0, 0], float64), 1.0, R)
        self.interpreter.structure.rotate(R=R, model=1)
        axis_angle_to_R(array([0, 0, 1], float64), 2.0, R)
        self.interpreter.structure.rotate(R=R, model=2)
        self.interpreter.structure.translate(T=[1., 1., 1.], model=1)
        self.interpreter.structure.translate(T=[0., 0., 1.], model=2)

        # Add some atoms that should not be aligned.
        self.interpreter.structure.add_atom(mol_name='uniform_mol1', atom_name='Ti', res_name='TST', res_num=100, pos=[[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]], element='Ti', pdb_record='HETATM')

        # The alignment.
        self.interpreter.structure.superimpose(pipes=['ref', 'align'], method='fit to first', atom_id='@N,H', displace_id='@N,H')

        # Output PDB to stdout to help in debugging.
        self.interpreter.structure.write_pdb(file=sys.stdout)

        # The atomic data.
        data = [
            ["N", "PRO",  1,    0.000,   0.000, -10.000],
            ["H", "PRO",  1,    0.000,   0.000, -11.020],
            ["N", "PRO",  2,    7.454,   0.000,  -6.667],
            ["H", "PRO",  2,    8.214,   0.000,  -7.347],
            ["N", "ILE",  3,   10.000,   0.000,   0.000],
            ["H", "ILE",  3,   11.020,   0.000,   0.000],
            ["N", "VAL",  4,    7.454,   0.000,   6.667],
            ["H", "VAL",  4,    8.214,   0.000,   7.347],
            ["N", "VAL",  5,    0.000,   0.000,  10.000],
            ["H", "VAL",  5,    0.000,   0.000,  11.020],
            ["N", "ASN",  6,    0.000,   0.000, -10.000],
            ["H", "ASN",  6,    0.000,   0.000, -11.020],
            ["N", "SER",  7,    3.727,   6.455,  -6.667],
            ["H", "SER",  7,    4.107,   7.113,  -7.347],
            ["N", "LEU",  8,    5.000,   8.660,   0.000],
            ["H", "LEU",  8,    5.510,   9.544,   0.000],
            ["N", "SER",  9,    3.727,   6.455,   6.667],
            ["H", "SER",  9,    4.107,   7.113,   7.347],
            ["N", "ASN", 10,    0.000,   0.000,  10.000],
            ["H", "ASN", 10,    0.000,   0.000,  11.020],
            ["N", "PHE", 11,   -0.000,   0.000, -10.000],
            ["H", "PHE", 11,   -0.000,   0.000, -11.020],
            #["N", "ALA", 12,   -3.727,   6.455,  -6.667],
            #["H", "ALA", 12,   -4.107,   7.113,  -7.347],
            ["N", "ILE", 13,   -5.000,   8.660,   0.000],
            ["H", "ILE", 13,   -5.510,   9.544,   0.000],
            ["N", "GLY", 14,   -3.727,   6.455,   6.667],
            ["H", "GLY", 14,   -4.107,   7.113,   7.347],
            ["N", "SER", 15,   -0.000,   0.000,  10.000],
            ["H", "SER", 15,   -0.000,   0.000,  11.020],
            ["N", "PHE", 16,   -0.000,   0.000, -10.000],
            ["H", "PHE", 16,   -0.000,   0.000, -11.020],
            ["N", "VAL", 17,   -7.454,   0.000,  -6.667],
            ["H", "VAL", 17,   -8.214,   0.000,  -7.347],
            ["N", "ILE", 18,  -10.000,   0.000,   0.000],
            ["H", "ILE", 18,  -11.020,   0.000,   0.000],
            ["N", "GLN", 19,   -7.454,   0.000,   6.667],
            ["H", "GLN", 19,   -8.214,   0.000,   7.347],
            ["N", "LEU", 20,   -0.000,   0.000,  10.000],
            #["H", "LEU", 20,   -0.000,   0.000,  11.020],
            ["N", "LEU", 21,   -0.000,  -0.000, -10.000],
            ["H", "LEU", 21,   -0.000,  -0.000, -11.020],
            ["N", "GLU", 22,   -3.727,  -6.455,  -6.667],
            ["H", "GLU", 22,   -4.107,  -7.113,  -7.347],
            ["N", "TRP", 23,   -5.000,  -8.660,   0.000],
            ["H", "TRP", 23,   -5.510,  -9.544,   0.000],
            ["N", "TYR", 24,   -3.727,  -6.455,   6.667],
            ["H", "TYR", 24,   -4.107,  -7.113,   7.347],
            ["N", "SER", 25,   -0.000,  -0.000,  10.000],
            ["H", "SER", 25,   -0.000,  -0.000,  11.020],
            ["N", "ARG", 26,    0.000,  -0.000, -10.000],
            ["H", "ARG", 26,    0.000,  -0.000, -11.020],
            ["N", "TYR", 27,    3.727,  -6.455,  -6.667],
            ["H", "TYR", 27,    4.107,  -7.113,  -7.347],
            ["N", "LEU", 28,    5.000,  -8.660,   0.000],
            ["H", "LEU", 28,    5.510,  -9.544,   0.000],
            ["N", "HIS", 29,    3.727,  -6.455,   6.667],
            ["H", "HIS", 29,    4.107,  -7.113,   7.347],
            ["N", "ALA", 30,    0.000,  -0.000,  10.000],
            ["H", "ALA", 30,    0.000,  -0.000,  11.020],
            ["Ti", "TST", 100,  1.000,   2.000,   3.000]
        ]

        # The selection object.
        selection = cdp.structure.selection()

        # Check the first model.
        self.assertEqual(len(data), len(cdp.structure.structural_data[0].mol[0].atom_name))
        i = 0
        for res_num, res_name, atom_name, pos in cdp.structure.atom_loop(selection=selection, model_num=1, res_num_flag=True, res_name_flag=True, atom_name_flag=True, pos_flag=True):
            self.assertEqual(atom_name, data[i][0])
            self.assertEqual(res_name, data[i][1])
            self.assertEqual(res_num, data[i][2])
            self.assertAlmostEqual(pos[0][0], data[i][3])
            self.assertAlmostEqual(pos[0][1], data[i][4])
            self.assertAlmostEqual(pos[0][2], data[i][5])
            i += 1

        # Check the second model.
        self.assertEqual(len(data), len(cdp.structure.structural_data[1].mol[0].atom_name))
        i = 0
        for res_num, res_name, atom_name, pos in cdp.structure.atom_loop(selection=selection, model_num=2, res_num_flag=True, res_name_flag=True, atom_name_flag=True, pos_flag=True):
            self.assertEqual(atom_name, data[i][0])
            self.assertEqual(res_name, data[i][1])
            self.assertEqual(res_num, data[i][2])
            self.assertAlmostEqual(pos[0][0], data[i][3])
            self.assertAlmostEqual(pos[0][1], data[i][4])
            self.assertAlmostEqual(pos[0][2], data[i][5])
            i += 1


    def test_align_CaM_BLOSUM62(self):
        """Test the alignment of CaM molecules from different species using the BLOSUM62 substitution matrix."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'structure_align.py')


    def test_align_molecules(self):
        """Test the U{structure.superimpose user function<http://www.nmr-relax.com/manual/structure_superimpose.html>} for aligning different molecules in one pipe."""

        # Reset relax.
        self.interpreter.reset()

        # Path of the PDB file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'diffusion_tensor'+sep+'sphere'

        # Create a data pipe for the reference structure, then load it.
        self.interpreter.pipe.create('ref', 'N-state')
        self.interpreter.structure.read_pdb('uniform.pdb', dir=path, set_mol_name='ref')

        # Delete a residue and atom.
        self.interpreter.structure.delete("#ref:8")
        self.interpreter.structure.delete("#ref:2@N")

        # Output PDB to stdout to help in debugging.
        self.interpreter.structure.write_pdb(file=sys.stdout)

        # Create a second data pipe for the structures to align and superimpose.
        self.interpreter.pipe.create('align', 'N-state')

        # Load the PDB twice as different models.
        self.interpreter.structure.read_pdb('uniform.pdb', dir=path, set_mol_name='1')
        self.interpreter.structure.read_pdb('uniform.pdb', dir=path, set_mol_name='2')

        # Delete a residue and atom from these two structures.
        self.interpreter.structure.delete("#1,2:12")
        self.interpreter.structure.delete("#1,2:20@H")

        # Translate and rotate the models.
        R = zeros((3, 3), float64)
        axis_angle_to_R(array([1, 0, 0], float64), 1.0, R)
        self.interpreter.structure.rotate(R=R, atom_id='#1')
        axis_angle_to_R(array([0, 0, 1], float64), 2.0, R)
        self.interpreter.structure.rotate(R=R, atom_id='#2')
        self.interpreter.structure.translate(T=[1., 1., 1.], atom_id='#1')
        self.interpreter.structure.translate(T=[0., 0., 1.], atom_id='#2')

        # Add some atoms that should not be aligned.
        self.interpreter.structure.add_atom(mol_name='1', atom_name='Ti', res_name='TST', res_num=100, pos=[1.0, 2.0, 3.0], element='Ti', pdb_record='HETATM')
        self.interpreter.structure.add_atom(mol_name='2', atom_name='Ti', res_name='TST', res_num=100, pos=[1.0, 2.0, 3.0], element='Ti', pdb_record='HETATM')

        # The alignment.
        self.interpreter.structure.superimpose(pipes=['ref', 'align'], molecules=[['ref'], ['1', '2']], method='fit to first', atom_id='@N,H', displace_id='@N,H')

        # Output PDB to stdout to help in debugging.
        self.interpreter.structure.write_pdb(file=sys.stdout)

        # The atomic data.
        data = [
            ["N", "PRO",  1,    0.000,   0.000, -10.000],
            ["H", "PRO",  1,    0.000,   0.000, -11.020],
            ["N", "PRO",  2,    7.454,   0.000,  -6.667],
            ["H", "PRO",  2,    8.214,   0.000,  -7.347],
            ["N", "ILE",  3,   10.000,   0.000,   0.000],
            ["H", "ILE",  3,   11.020,   0.000,   0.000],
            ["N", "VAL",  4,    7.454,   0.000,   6.667],
            ["H", "VAL",  4,    8.214,   0.000,   7.347],
            ["N", "VAL",  5,    0.000,   0.000,  10.000],
            ["H", "VAL",  5,    0.000,   0.000,  11.020],
            ["N", "ASN",  6,    0.000,   0.000, -10.000],
            ["H", "ASN",  6,    0.000,   0.000, -11.020],
            ["N", "SER",  7,    3.727,   6.455,  -6.667],
            ["H", "SER",  7,    4.107,   7.113,  -7.347],
            ["N", "LEU",  8,    5.000,   8.660,   0.000],
            ["H", "LEU",  8,    5.510,   9.544,   0.000],
            ["N", "SER",  9,    3.727,   6.455,   6.667],
            ["H", "SER",  9,    4.107,   7.113,   7.347],
            ["N", "ASN", 10,    0.000,   0.000,  10.000],
            ["H", "ASN", 10,    0.000,   0.000,  11.020],
            ["N", "PHE", 11,   -0.000,   0.000, -10.000],
            ["H", "PHE", 11,   -0.000,   0.000, -11.020],
            #["N", "ALA", 12,   -3.727,   6.455,  -6.667],
            #["H", "ALA", 12,   -4.107,   7.113,  -7.347],
            ["N", "ILE", 13,   -5.000,   8.660,   0.000],
            ["H", "ILE", 13,   -5.510,   9.544,   0.000],
            ["N", "GLY", 14,   -3.727,   6.455,   6.667],
            ["H", "GLY", 14,   -4.107,   7.113,   7.347],
            ["N", "SER", 15,   -0.000,   0.000,  10.000],
            ["H", "SER", 15,   -0.000,   0.000,  11.020],
            ["N", "PHE", 16,   -0.000,   0.000, -10.000],
            ["H", "PHE", 16,   -0.000,   0.000, -11.020],
            ["N", "VAL", 17,   -7.454,   0.000,  -6.667],
            ["H", "VAL", 17,   -8.214,   0.000,  -7.347],
            ["N", "ILE", 18,  -10.000,   0.000,   0.000],
            ["H", "ILE", 18,  -11.020,   0.000,   0.000],
            ["N", "GLN", 19,   -7.454,   0.000,   6.667],
            ["H", "GLN", 19,   -8.214,   0.000,   7.347],
            ["N", "LEU", 20,   -0.000,   0.000,  10.000],
            #["H", "LEU", 20,   -0.000,   0.000,  11.020],
            ["N", "LEU", 21,   -0.000,  -0.000, -10.000],
            ["H", "LEU", 21,   -0.000,  -0.000, -11.020],
            ["N", "GLU", 22,   -3.727,  -6.455,  -6.667],
            ["H", "GLU", 22,   -4.107,  -7.113,  -7.347],
            ["N", "TRP", 23,   -5.000,  -8.660,   0.000],
            ["H", "TRP", 23,   -5.510,  -9.544,   0.000],
            ["N", "TYR", 24,   -3.727,  -6.455,   6.667],
            ["H", "TYR", 24,   -4.107,  -7.113,   7.347],
            ["N", "SER", 25,   -0.000,  -0.000,  10.000],
            ["H", "SER", 25,   -0.000,  -0.000,  11.020],
            ["N", "ARG", 26,    0.000,  -0.000, -10.000],
            ["H", "ARG", 26,    0.000,  -0.000, -11.020],
            ["N", "TYR", 27,    3.727,  -6.455,  -6.667],
            ["H", "TYR", 27,    4.107,  -7.113,  -7.347],
            ["N", "LEU", 28,    5.000,  -8.660,   0.000],
            ["H", "LEU", 28,    5.510,  -9.544,   0.000],
            ["N", "HIS", 29,    3.727,  -6.455,   6.667],
            ["H", "HIS", 29,    4.107,  -7.113,   7.347],
            ["N", "ALA", 30,    0.000,  -0.000,  10.000],
            ["H", "ALA", 30,    0.000,  -0.000,  11.020],
            ["Ti", "TST", 100,  1.000,   2.000,   3.000]
        ]

        # The selection object.
        selection = cdp.structure.selection()

        # Check the molecules.
        self.assertEqual(len(data), len(cdp.structure.structural_data[0].mol[0].atom_name))
        self.assertEqual(len(data), len(cdp.structure.structural_data[0].mol[1].atom_name))
        current_mol = ''
        for mol_name, res_num, res_name, atom_name, pos in cdp.structure.atom_loop(selection=selection, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_name_flag=True, pos_flag=True):
            print("Molecule '%s', residue '%s %s', atom '%s', position %s" % (mol_name, res_num, res_name, atom_name, pos))
            if mol_name != current_mol:
                current_mol = mol_name
                i = 0
            self.assertEqual(atom_name, data[i][0])
            self.assertEqual(res_name, data[i][1])
            self.assertEqual(res_num, data[i][2])
            self.assertAlmostEqual(pos[0][0], data[i][3])
            self.assertAlmostEqual(pos[0][1], data[i][4])
            self.assertAlmostEqual(pos[0][2], data[i][5])
            i += 1


    def test_align_molecules2(self):
        """Test of the structure.superimpose user function, fitting to the mean structure."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'

        # Load the two rotated structures.
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=path, set_model_num=1, set_mol_name='CaM A')
        self.interpreter.structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=path, set_model_num=1, set_mol_name='CaM B')

        # Add an atom that should not be superimposed.
        self.interpreter.structure.add_atom(mol_name='CaM A', atom_name='Ti', res_name='TST', res_num=1, pos=[1.0, 2.0, 3.0], element='Ti', pdb_record='HETATM')
        self.interpreter.structure.add_atom(mol_name='CaM B', atom_name='Ti', res_name='TST', res_num=1, pos=[2.0, 3.0, 4.0], element='Ti', pdb_record='HETATM')

        # Superimpose the backbone heavy atoms.
        self.interpreter.structure.superimpose(method='fit to mean', atom_id='@N,C,CA,O', displace_id=':82-5000')

        # Check that the two structures now have the same atomic coordinates.
        mol1 = cdp.structure.structural_data[0].mol[0]
        mol2 = cdp.structure.structural_data[0].mol[1]
        for i in range(len(mol1.atom_name)):
            if mol1.res_num[i] == 1:
                continue
            self.assertAlmostEqual(mol1.x[i], mol2.x[i], 2)
            self.assertAlmostEqual(mol1.y[i], mol2.y[i], 2)
            self.assertAlmostEqual(mol1.z[i], mol2.z[i], 2)

        # The first 'Ti' atom must be different - it is not displaced.
        self.assertAlmostEqual(mol1.x[0] - mol2.x[0], -1.0, 2)
        self.assertAlmostEqual(mol1.y[0] - mol2.y[0], -1.0, 2)
        self.assertAlmostEqual(mol1.z[0] - mol2.z[0], -1.0, 2)


    def test_align_molecules_end_truncation(self):
        """Test of the structure.superimpose user function, fitting to the mean structure."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the two rotated structures.
        self.interpreter.structure.read_pdb('1J7O.pdb', dir=path, read_model=1, set_model_num=1, set_mol_name='CaM A')
        self.interpreter.structure.read_pdb('1J7O.pdb', dir=path, read_model=1, set_model_num=1, set_mol_name='CaM B')
        self.interpreter.structure.read_pdb('1J7O.pdb', dir=path, read_model=1, set_model_num=1, set_mol_name='CaM C')

        # Delete some end residues.
        self.interpreter.structure.delete(atom_id="#CaM A:1-4")
        self.interpreter.structure.delete(atom_id="#CaM A:60-100")
        self.interpreter.structure.delete(atom_id="#CaM C:1-3")
        self.interpreter.structure.delete(atom_id="#CaM C:75-100")
        self.interpreter.structure.delete(atom_id=":1000-1001")

        # Copy the data pipe for late comparison.
        self.interpreter.pipe.copy('mf', 'comp')

        # Superimpose the backbone heavy atoms.
        self.interpreter.structure.superimpose(method='fit to mean', atom_id='@N,C,CA,O')

        # Check that nothing has moved.
        for mol_index in range(3):
            mol1 = ds['mf'].structure.structural_data[0].mol[mol_index]
            mol2 = ds['comp'].structure.structural_data[0].mol[mol_index]
            for i in range(len(mol1.atom_name)):
                self.assertAlmostEqual(mol1.x[i], mol2.x[i])
                self.assertAlmostEqual(mol1.y[i], mol2.y[i])
                self.assertAlmostEqual(mol1.z[i], mol2.z[i])


    def test_alt_loc_missing(self):
        """Test that a RelaxError occurs when the alternate location indicator is present but not specified."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file, load the spins, and attach the protons.
        self.assertRaises(RelaxError, self.interpreter.structure.read_pdb, '1OGT_trunc.pdb', dir=path)


    def test_atomic_fluctuations(self):
        """Check the operation of the structure.atomic_fluctuations user function.

        This checks the interatomic distance fluctuations calculated by the U{structure.atomic_fluctuations user function<http://www.nmr-relax.com/manual/structure_atomic_fluctuations.html>}.
        """

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path)

        # Run the structure.atomic_fluctuations user function and collect the results in a dummy file object.
        file = DummyFileObject()
        self.interpreter.structure.atomic_fluctuations(atom_id='@N,CA', file=file, format='text')

        # The fluctuations.
        n =  array([[ 9.464,  -9.232,  27.573], [ 9.211,  -9.425,  26.970], [ 7.761,  -6.392,  27.161]], float64)
        ca = array([[10.302,  -8.195,  26.930], [10.077,  -8.221,  26.720], [ 9.256,  -6.332,  27.183]], float64)
        sd = std(array([norm(n[0] - ca[0]), norm(n[1] - ca[1]), norm(n[2] - ca[2])], float64), ddof=1)
        expected = []
        expected.append("# %18s %20s\n" % (":4@N", ":4@CA"))
        expected.append("%20.15f %20.15f\n" % (0.0, sd))
        expected.append("%20.15f %20.15f\n" % (sd, 0.0))

        # Check the file.
        lines = file.readlines()
        self.assertEqual(len(expected), len(lines))
        for i in range(len(lines)):
            self.assertEqual(expected[i], lines[i])


    def test_atomic_fluctuations_angle(self):
        """Check the angular fluctuations calculated by the structure.atomic_fluctuations user function.

        This checks the text file (with the format argument set to text) of interatomic angle fluctuations calculated by the U{structure.atomic_fluctuations user function<http://www.nmr-relax.com/manual/structure_atomic_fluctuations.html>}.
        """

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path)

        # Run the structure.atomic_fluctuations user function and collect the results in a dummy file object.
        file = DummyFileObject()
        self.interpreter.structure.atomic_fluctuations(measure='angle', atom_id='@N,CA', file=file, format='text')

        # The atom positions.
        n =  array([[ 9.464,  -9.232,  27.573], [ 9.211,  -9.425,  26.970], [ 7.761,  -6.392,  27.161]], float64)
        ca = array([[10.302,  -8.195,  26.930], [10.077,  -8.221,  26.720], [ 9.256,  -6.332,  27.183]], float64)

        # The interatom vectors.
        vectors = ca - n

        # The inter-vector angles to the average.
        vect_ave = average(vectors, axis=0)
        angles = [
            vector_angle_acos(vect_ave, vectors[0]),
            vector_angle_acos(vect_ave, vectors[1]),
            vector_angle_acos(vect_ave, vectors[2])
        ]

        # The fluctuations.
        sd = std(array(angles, float64), ddof=1)
        expected = []
        expected.append("# %18s %20s\n" % (":4@N", ":4@CA"))
        expected.append("%20.15f %20.15f\n" % (0.0, sd))
        expected.append("%20.15f %20.15f\n" % (sd, 0.0))

        # Check the file.
        lines = file.readlines()
        self.assertEqual(len(expected), len(lines))
        for i in range(len(lines)):
            self.assertEqual(expected[i], lines[i])


    def test_atomic_fluctuations_gnuplot(self):
        """Check the operation of the structure.atomic_fluctuations user function for creating a gnuplot script.

        This checks the format argument of the U{structure.atomic_fluctuations user function<http://www.nmr-relax.com/manual/structure_atomic_fluctuations.html>} when set to 'gnuplot'.
        """

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path)

        # Run the structure.atomic_fluctuations user function.
        self.interpreter.structure.atomic_fluctuations(atom_id='@N,CA', file='matrix', dir=ds.tmpdir, format='gnuplot')

        # The fluctuations.
        n =  array([[ 9.464,  -9.232,  27.573], [ 9.211,  -9.425,  26.970], [ 7.761,  -6.392,  27.161]], float64)
        ca = array([[10.302,  -8.195,  26.930], [10.077,  -8.221,  26.720], [ 9.256,  -6.332,  27.183]], float64)
        sd = std(array([norm(n[0] - ca[0]), norm(n[1] - ca[1]), norm(n[2] - ca[2])], float64), ddof=1)
        expected = []
        expected.append("# %18s %20s\n" % (":4@N", ":4@CA"))
        expected.append("%20.15f %20.15f\n" % (0.0, sd))
        expected.append("%20.15f %20.15f\n" % (sd, 0.0))

        # Check the text file.
        file = open("%s%s%s" % (ds.tmpdir, sep, 'matrix'))
        lines = file.readlines()
        self.assertEqual(len(expected), len(lines))
        for i in range(len(lines)):
            self.assertEqual(expected[i], lines[i])

        # Check the gnuplot file.
        script = [
            "#!/usr/bin/env gnuplot\n",
            "\n",
            "# Set up the terminal type and make the plot square.\n",
            "set terminal postscript eps size 10,10 enhanced color font 'Helvetica,20' linewidth 0.1\n",
            "set size square\n",
            "\n",
            "# Blue-red colour map.\n",
            "set palette model RGB\n",
            "set palette defined\n",
            "\n",
            "# Labels.\n",
            "set xtics out rotate font \",8\" (\":4\\\\@N\" 0, \":4\\\\@CA\" 1)\n",
            "set ytics out font \",8\" (\":4\\\\@N\" 0, \":4\\\\@CA\" 1)\n",
            "\n",
            "# Output to EPS.\n",
            "set output \"matrix.eps\"\n",
            "\n",
            "# Load and show the text data\n",
            "plot \"matrix\" matrix with image\n"
        ]
        file = open("%s%s%s" % (ds.tmpdir, sep, 'matrix.gnu'))
        lines = file.readlines()
        print("Script:")
        print("\"\"\"")
        for line in lines:
            print(line[:-1])
        print("\"\"\"")
        self.assertEqual(len(script), len(lines))
        for i in range(len(lines)):
            self.assertEqual(script[i], lines[i])


    def test_atomic_fluctuations_no_match(self):
        """Check the operation of the structure.atomic_fluctuations user function when no data matches the atom ID.

        This checks the interatomic distance fluctuations calculated by the U{structure.atomic_fluctuations user function<http://www.nmr-relax.com/manual/structure_atomic_fluctuations.html>}.
        """

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path)

        # Run the structure.atomic_fluctuations user function and collect the results in a dummy file object.
        file = DummyFileObject()
        self.assertRaises(RelaxError, self.interpreter.structure.atomic_fluctuations, atom_id='@X', file=file, format='text')


    def test_atomic_fluctuations_parallax(self):
        """Check the parallax shift fluctuations calculated by the structure.atomic_fluctuations user function.

        This checks the text file (with the format argument set to text) of interatomic parallax shift fluctuations calculated by the U{structure.atomic_fluctuations user function<http://www.nmr-relax.com/manual/structure_atomic_fluctuations.html>}.
        """

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path)

        # Run the structure.atomic_fluctuations user function and collect the results in a dummy file object.
        file = DummyFileObject()
        self.interpreter.structure.atomic_fluctuations(measure='parallax shift', atom_id='@N,CA', file=file, format='text')

        # The atom positions.
        n =  array([[ 9.464,  -9.232,  27.573], [ 9.211,  -9.425,  26.970], [ 7.761,  -6.392,  27.161]], float64)
        ca = array([[10.302,  -8.195,  26.930], [10.077,  -8.221,  26.720], [ 9.256,  -6.332,  27.183]], float64)

        # The interatom vectors.
        vectors = ca - n

        # The inter-vector projections to the average.
        vect_ave = average(vectors, axis=0)
        unit = vect_ave / norm(vect_ave)
        proj = [
            dot(vectors[0], unit) * unit,
            dot(vectors[1], unit) * unit,
            dot(vectors[2], unit) * unit
        ]
        shift = [
            norm(vectors[0] - proj[0]),
            norm(vectors[1] - proj[1]),
            norm(vectors[2] - proj[2])
        ]

        # The fluctuations.
        sd = std(array(shift, float64), ddof=1)
        expected = []
        expected.append("# %18s %20s\n" % (":4@N", ":4@CA"))
        expected.append("%20.15f %20.15f\n" % (0.0, sd))
        expected.append("%20.15f %20.15f\n" % (sd, 0.0))

        # Check the file.
        lines = file.readlines()
        self.assertEqual(len(expected), len(lines))
        for i in range(len(lines)):
            self.assertEqual(expected[i], lines[i])


    def test_bug_12_hash_in_mol_name_via_arg(self):
        """Catch U{bug #12<https://sourceforge.net/p/nmr-relax/tickets/12/>}, the failure to detect '#' in the molecule name.

        This is for the case where set_mol_name argument value contains the '#' character.  The test checks both the structure.read_pdb and structure.read_xyz user functions.
        """

        # These should fail.
        self.assertRaises(RelaxError, self.interpreter.structure.read_pdb, 'bug_12_hash_in_mol_name.pdb', dir=path.join(status.install_path, 'test_suite', 'shared_data', 'structures'), set_mol_name='bug_12_#_in_mol_name')
        self.assertRaises(RelaxError, self.interpreter.structure.read_xyz, 'bug_12_hash_in_mol_name.xyz', dir=path.join(status.install_path, 'test_suite', 'shared_data', 'structures'), set_mol_name='bug_12_#_in_mol_name')


    def test_bug_12_hash_in_mol_name_via_file(self):
        """Catch U{bug #12<https://sourceforge.net/p/nmr-relax/tickets/12/>}, the failure to detect '#' in the molecule name.

        This is for the case where the PDB file itself contains the '#' character.  The test checks both the structure.read_pdb and structure.read_xyz user functions.
        """

        # These should fail.
        self.assertRaises(RelaxError, self.interpreter.structure.read_pdb, 'bug_12_#_in_mol_name.pdb', dir=path.join(status.install_path, 'test_suite', 'shared_data', 'structures'))
        self.assertRaises(RelaxError, self.interpreter.structure.read_xyz, 'bug_12_#_in_mol_name.xyz', dir=path.join(status.install_path, 'test_suite', 'shared_data', 'structures'))


    def test_bug_20470_alternate_location_indicator(self):
        """Catch U{bug #20470<https://web.archive.org/web/https://gna.org/bugs/?20470>}, the alternate location indicator problem."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file, load the spins, and attach the protons.
        self.interpreter.structure.read_pdb('1OGT_trunc.pdb', dir=path, alt_loc='A')
        self.interpreter.structure.load_spins(spin_id='@N', ave_pos=True)
        self.interpreter.sequence.attach_protons()


    def test_bug_21187_corrupted_pdb(self):
        """Catch U{bug #21187<https://web.archive.org/web/https://gna.org/bugs/?21187>}, the corrupted PDB with all proton atoms numbers set to zero."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file.
        self.interpreter.structure.read_pdb('bug_21187_molecule.pdb', dir=path)

        # Load the @N, @H, and @NE1 spins (needed to create the :60@0 spin to trigger the bug later).
        self.interpreter.structure.load_spins(spin_id='@N', ave_pos=True)
        self.interpreter.structure.load_spins(spin_id='@NE1', ave_pos=True)
        self.interpreter.structure.load_spins(spin_id='@H', ave_pos=True)

        # Load the :60@HE1 spin - this clashes with the :60@H spin as both have the spin ID of ':60@0'.
        self.interpreter.structure.load_spins(spin_id='@HE1', ave_pos=True)


    def test_bug_21522_master_record_atom_count(self):
        """Catch U{bug #21522<https://web.archive.org/web/https://gna.org/bugs/?21522>}, the structure.write_pdb user function creating an incorrect MASTER record.

        This also triggers U{bug #21520<https://web.archive.org/web/https://gna.org/bugs/?21520>}, the failure of the structure.write_pdb user function when creating the MASTER record due to too many ATOM and HETATM records being present.
        """

        # Create 2 models.
        self.interpreter.structure.add_model(model_num=1)
        self.interpreter.structure.add_model(model_num=2)

        # Add a single atom.
        self.interpreter.structure.add_atom(atom_name='N', res_name='Pro', res_num=2, pos=[1., 2., 3.], element='N')

        # Create a PDB file.
        file = DummyFileObject()
        self.interpreter.structure.write_pdb(file=file, force=True)

        # The file contents, without remarks, as they should be.
        contents = [
            "MODEL        1                                                                  \n",
            "ATOM      1  N   Pro A   2       1.000   2.000   3.000  1.00  0.00           N  \n",
            "TER       2      Pro A   2                                                      \n",
            "ENDMDL                                                                          \n",
            "MODEL        2                                                                  \n",
            "ATOM      1  N   Pro A   2       1.000   2.000   3.000  1.00  0.00           N  \n",
            "TER       2      Pro A   2                                                      \n",
            "ENDMDL                                                                          \n",
            "MASTER        0    0    0    0    0    0    0    0    1    1    0    0          \n",
            "END                                                                             \n"
        ]

        # Check the created PDB file.
        lines = file.readlines()
        self.strip_remarks(lines)
        self.assertEqual(len(contents), len(lines))
        for i in range(len(lines)):
            self.assertEqual(contents[i], lines[i])


    def test_bug_21814_pdb_no_80_space_padding(self):
        """Catch U{bug #21814<https://web.archive.org/web/https://gna.org/bugs/?21814>}, the PDB reading failure when not padded to 80 spaces."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file.
        self.interpreter.structure.read_pdb('SpUreE_dimer_H_new', dir=path)


    def test_bug_22041_atom_numbering(self):
        """Catch U{bug #22041<https://web.archive.org/web/https://gna.org/bugs/?22041>}, the atom serial number not being sequential from 1 onwards."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read a PDB file twice as two different molecules.
        self.interpreter.structure.read_pdb('1RTE_trunc.pdb', dir=path, set_mol_name='N-dom')
        self.interpreter.structure.read_pdb('1RTE_trunc.pdb', dir=path, set_mol_name='C-dom')

        # Create a PDB file.
        file = DummyFileObject()
        self.interpreter.structure.write_pdb(file=file, force=True)

        # The file contents, without remarks, as they should be.
        contents = [
            "HET    CYN  A 445       1                                                       \n",
            "HET    CYN  B 445       1                                                       \n",
            "HETNAM     CYN UNKNOWN                                                          \n",
            "FORMUL   1  CYN    C1                                                           \n",
            "ATOM      1  N   LEU A   3      49.617   4.693  46.426  1.00  0.00           N  \n",
            "ATOM      2 CA   LEU A   3      49.432   5.476  45.190  1.00  0.00           C  \n",
            "ATOM      3  C   LEU A   3      50.346   4.980  44.055  1.00  0.00           C  \n",
            "ATOM      4  O   LEU A   3      49.924   4.868  42.889  1.00  0.00           O  \n",
            "ATOM      5 CB   LEU A   3      49.673   6.968  45.457  1.00  0.00           C  \n",
            "ATOM      6 CG   LEU A   3      49.804   7.863  44.222  1.00  0.00           C  \n",
            "ATOM      7 CD1  LEU A   3      48.564   7.837  43.327  1.00  0.00           C  \n",
            "ATOM      8 CD2  LEU A   3      50.075   9.282  44.625  1.00  0.00           C  \n",
            "TER       9      LEU A   3                                                      \n",
            "HETATM   10    C CYN A 445      29.160  13.127  62.533  1.00  0.00           C  \n",
            "ATOM     11  N   LEU B   3      49.617   4.693  46.426  1.00  0.00           N  \n",
            "ATOM     12 CA   LEU B   3      49.432   5.476  45.190  1.00  0.00           C  \n",
            "ATOM     13  C   LEU B   3      50.346   4.980  44.055  1.00  0.00           C  \n",
            "ATOM     14  O   LEU B   3      49.924   4.868  42.889  1.00  0.00           O  \n",
            "ATOM     15 CB   LEU B   3      49.673   6.968  45.457  1.00  0.00           C  \n",
            "ATOM     16 CG   LEU B   3      49.804   7.863  44.222  1.00  0.00           C  \n",
            "ATOM     17 CD1  LEU B   3      48.564   7.837  43.327  1.00  0.00           C  \n",
            "ATOM     18 CD2  LEU B   3      50.075   9.282  44.625  1.00  0.00           C  \n",
            "TER      19      LEU B   3                                                      \n",
            "HETATM   20    C CYN B 445      29.160  13.127  62.533  1.00  0.00           C  \n",
            "MASTER        0    0    2    0    0    0    0    0   18    2    0    0          \n",
            "END                                                                             \n"
        ]

        # Check the created PDB file.
        lines = file.readlines()
        self.strip_remarks(lines)
        self.assertEqual(len(contents), len(lines))
        for i in range(len(lines)):
            self.assertEqual(contents[i], lines[i])


    def test_bug_22069_structure_delete_helix_attribute(self):
        """Catch U{bug #22069<https://web.archive.org/web/https://gna.org/bugs/?22069>}, the failure of the structure.delete user function with helix attribute errors."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'

        # Load the structure.
        self.interpreter.structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=path)

        # Delete the calciums.
        self.interpreter.structure.delete(atom_id='@CA')


    def test_bug_22070_structure_superimpose_after_deletion(self):
        """Catch U{bug #22070<https://web.archive.org/web/https://gna.org/bugs/?22070>}, the failure of the structure.superimpose user function after deleting atoms with structure.delete."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'

        # Load the structures to superimpose.
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=path, set_mol_name='C-dom', set_model_num=1)
        self.interpreter.structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=path, set_mol_name='C-dom', set_model_num=2)

        # Delete the calciums.
        self.interpreter.structure.delete(atom_id='@CA')

        # Check the deleted atoms of both models (the last atoms should now be the last ATOM record proton and not the HETATOM CA).
        for i in range(2):
            print("Checking the last atom of model %s." % i)
            self.assertEqual(cdp.structure.structural_data[i].mol[0].atom_name[-1], 'H')

        # Superimpose.
        self.interpreter.structure.superimpose(method='fit to first', centre_type='CoM')

        # Align.
        self.interpreter.structure.superimpose(method='fit to first', centre_type='CoM')


    def test_bug_22860_CoM_after_deletion(self):
        """Catch U{bug #22860<https://web.archive.org/web/https://gna.org/bugs/?22860>}, the failure of the structure.com user function after calling structure.delete."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'

        # Load a random structure, then delete it.
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=path, set_mol_name='C-dom', set_model_num=1)
        self.interpreter.structure.delete()

        # CoM.
        self.assertRaises(RelaxError, self.interpreter.structure.com)


    def test_bug_22861_PDB_writing_chainID_fail(self):
        """Catch U{bug #22861<https://web.archive.org/web/https://gna.org/bugs/?22861>}, the chain IDs in the structure.write_pdb user function PDB files are incorrect after calling structure.delete."""

        # Add one atom to two different molecules.
        self.interpreter.structure.add_atom(mol_name='A', atom_name='N', res_name='Phe', res_num=1, pos=[1.0, 1.0, 1.0], element='N')
        self.interpreter.structure.add_atom(mol_name='B', atom_name='N', res_name='Phe', res_num=1, pos=[1.0, 1.0, 1.0], element='N')

        # Add some metadata to demonstrate a problem with the structure.delete user function.
        cdp.structure.structural_data[0].mol[0].file_name = 'test.pdb'
        cdp.structure.structural_data[0].mol[1].file_name = 'test2.pdb'

        # Delete the first molecule.
        self.interpreter.structure.delete('#A')

        # Create a PDB file.
        file = DummyFileObject()
        self.interpreter.structure.write_pdb(file=file, force=True)

        # The file contents, without remarks, as they should be.
        contents = [
            "ATOM      1  N   Phe A   1       1.000   1.000   1.000  1.00  0.00           N  \n",
            "TER       2      Phe A   1                                                      \n",
            "MASTER        0    0    0    0    0    0    0    0    1    1    0    0          \n",
            "END                                                                             \n"
        ]

        # Check the created PDB file.
        lines = file.readlines()
        self.strip_remarks(lines)
        self.assertEqual(len(contents), len(lines))
        for i in range(len(lines)):
            self.assertEqual(contents[i], lines[i])


    def test_bug_23293_missing_hetatm(self):
        """Catch U{bug #23293<https://web.archive.org/web/https://gna.org/bugs/?23293>}, the PDB HETATM loading error whereby the last HETATM record is sometimes not read from the PDB file."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file.
        self.interpreter.structure.read_pdb('bug_23293_missing_hetatm.pdb', dir=path)

        # Create a PDB file.
        file = DummyFileObject()
        self.interpreter.structure.write_pdb(file=file, force=True)

        # The file contents, without remarks, as they should be.
        contents = [
            "HET     CA  A 501       1                                                       \n",
            "HET     CA  A 502       1                                                       \n",
            "HET     CA  B 503       1                                                       \n",
            "HET     CA  B 504       1                                                       \n",
            "HET     CA  C 505       1                                                       \n",
            "HET     CA  C 506       1                                                       \n",
            "HETNAM      CA UNKNOWN                                                          \n",
            "FORMUL   1   CA    CA1                                                          \n",
            "MODEL        1                                                                  \n",
            "ATOM      1  N   LEU A   1       1.000  -2.000  20.000  1.00  0.00           N  \n",
            "ATOM      2  H   LEU A   1       2.000  -2.000  20.000  1.00  0.00           H  \n",
            "TER       3      LEU A   1                                                      \n",
            "HETATM    4   CA  CA A 501      17.000  12.000  14.000  1.00  0.00          CA  \n",
            "HETATM    5   CA  CA A 502       6.000   9.000  14.000  1.00  0.00          CA  \n",
            "ATOM      6  N   LEU B   1       9.000  -9.000  27.000  1.00  0.00           N  \n",
            "ATOM      7  H   LEU B   1       8.000  -8.000  27.000  1.00  0.00           H  \n",
            "TER       8      LEU B   1                                                      \n",
            "HETATM    9   CA  CA B 503      17.000  12.000  14.000  1.00  0.00          CA  \n",
            "HETATM   10   CA  CA B 504       6.000   9.000  14.000  1.00  0.00          CA  \n",
            "ATOM     11  N   LEU C   1      12.000 -12.000   7.000  1.00  0.00           N  \n",
            "ATOM     12  H   LEU C   1      11.000 -12.000   7.000  1.00  0.00           H  \n",
            "TER      13      LEU C   1                                                      \n",
            "HETATM   14   CA  CA C 505      31.000 -10.000  -0.000  1.00  0.00          CA  \n",
            "HETATM   15   CA  CA C 506      31.000 -19.000   6.000  1.00  0.00          CA  \n",
            "ENDMDL                                                                          \n",
            "MASTER        0    0    6    0    0    0    0    0   12    3    0    0          \n",
            "END                                                                             \n"
        ]

        # Check the created PDB file.
        lines = file.readlines()
        self.strip_remarks(lines)
        self.assertEqual(len(contents), len(lines))
        for i in range(len(lines)):
            self.assertEqual(contents[i], lines[i])


    def test_bug_23294_multi_mol_automerge(self):
        """Catch U{bug #23294<https://web.archive.org/web/https://gna.org/bugs/?23294>}, the automatic merging of PDB molecules results in an IndexError."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file.
        self.interpreter.structure.read_pdb('bug_23294_multi_mol_automerge.pdb', dir=path, read_model=1, set_mol_name='merged mol')

        # Create a PDB file.
        file = DummyFileObject()
        self.interpreter.structure.write_pdb(file=file, force=True)

        # The file contents, without remarks, as they should be.
        contents = [
            "MODEL        1                                                                  \n",
            "ATOM      1  N   LEU A   1       1.000   0.000   0.000  1.00  0.00           N  \n",
            "ATOM      2  H   LEU A   1       2.000   0.000   0.000  1.00  0.00           H  \n",
            "ATOM      3  N   GLU A   2       3.000   0.000   0.000  1.00  0.00           N  \n",
            "ATOM      4  H   GLU A   2       4.000   0.000   0.000  1.00  0.00           H  \n",
            "TER       5      GLU A   2                                                      \n",
            "ENDMDL                                                                          \n",
            "MASTER        0    0    0    0    0    0    0    0    4    1    0    0          \n",
            "END                                                                             \n"
        ]

        # Check the created PDB file.
        lines = file.readlines()
        self.strip_remarks(lines)
        self.assertEqual(len(contents), len(lines))
        for i in range(len(lines)):
            self.assertEqual(contents[i], lines[i])


    def test_bug_23295_ss_metadata_merge(self):
        """Catch U{bug #23295<https://web.archive.org/web/https://gna.org/bugs/?23295>}, the PDB secondary structure HELIX and SHEET records not updated when merging molecules."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file.
        self.interpreter.structure.read_pdb('2BE6_secondary_structure.pdb', dir=path, read_mol=[1, 4], set_mol_name='CaM A')
        self.interpreter.structure.read_pdb('2BE6_secondary_structure.pdb', dir=path, read_mol=[2, 5], set_mol_name='CaM B')
        self.interpreter.structure.read_pdb('2BE6_secondary_structure.pdb', dir=path, read_mol=[3, 6], set_mol_name='CaM C')

        # Create a PDB file.
        file = DummyFileObject()
        self.interpreter.structure.write_pdb(file=file, force=True)

        # The HELIX and SHEET contents, as they should be.
        # First, the original contents:
        #     "HELIX    1   1 THR A    5  ASP A   20  1                                  16    "
        #     "HELIX    2   2 THR A   28  LEU A   39  1                                  12    "
        #     "HELIX    3   3 THR A   44  ASP A   56  1                                  13    "
        #     "HELIX    4   4 PHE A   65  MET A   76  1                                  12    "
        #     "HELIX    5   5 SER A   81  ASP A   93  1                                  13    "
        #     "HELIX    6   6 SER A  101  LEU A  112  1                                  12    "
        #     "HELIX    7   7 THR A  117  ASP A  129  1                                  13    "
        #     "HELIX    8   8 TYR A  138  THR A  146  1                                   9    "
        #     "HELIX    9   9 VAL D 1615  GLY D 1638  1                                  24    "
        #     "HELIX   10  10 THR B    5  ASP B   20  1                                  16    "
        #     "HELIX   11  11 THR B   28  LEU B   39  1                                  12    "
        #     "HELIX   12  12 THR B   44  ASP B   56  1                                  13    "
        #     "HELIX   13  13 PHE B   65  ASP B   78  1                                  14    "
        #     "HELIX   14  14 GLU B   82  ASP B   93  1                                  12    "
        #     "HELIX   15  15 SER B  101  GLY B  113  1                                  13    "
        #     "HELIX   16  16 THR B  117  ASP B  129  1                                  13    "
        #     "HELIX   17  17 TYR B  138  MET B  145  1                                   8    "
        #     "HELIX   18  18 GLU E 1612  GLN E 1625  1                                  14    "
        #     "HELIX   19  19 THR C    5  ASP C   20  1                                  16    "
        #     "HELIX   20  20 THR C   28  LEU C   39  1                                  12    "
        #     "HELIX   21  21 THR C   44  ASP C   56  1                                  13    "
        #     "HELIX   22  22 PHE C   65  LYS C   75  1                                  11    "
        #     "HELIX   23  23 GLU C   82  ASP C   93  1                                  12    "
        #     "HELIX   24  24 SER C  101  LEU C  112  1                                  12    "
        #     "HELIX   25  25 THR C  117  ASP C  129  1                                  13    "
        #     "HELIX   26  26 TYR C  138  MET C  145  1                                   8    "
        #     "HELIX   27  27 LYS F 1617  GLU F 1636  1                                  20    "
        #     "SHEET    1   A 2 THR A  26  ILE A  27  0                                        "
        #     "SHEET    2   A 2 ILE A  63  ASP A  64 -1  O  ILE A  63   N  ILE A  27           "
        #     "SHEET    1   B 2 TYR A  99  ILE A 100  0                                        "
        #     "SHEET    2   B 2 VAL A 136  ASN A 137 -1  O  VAL A 136   N  ILE A 100           "
        #     "SHEET    1   C 2 THR B  26  ILE B  27  0                                        "
        #     "SHEET    2   C 2 ILE B  63  ASP B  64 -1  O  ILE B  63   N  ILE B  27           "
        #     "SHEET    1   D 2 TYR B  99  ILE B 100  0                                        "
        #     "SHEET    2   D 2 VAL B 136  ASN B 137 -1  O  VAL B 136   N  ILE B 100           "
        #     "SHEET    1   E 2 THR C  26  ILE C  27  0                                        "
        #     "SHEET    2   E 2 ILE C  63  ASP C  64 -1  O  ILE C  63   N  ILE C  27           "
        #     "SHEET    1   F 2 TYR C  99  ILE C 100  0                                        "
        #     "SHEET    2   F 2 VAL C 136  ASN C 137 -1  O  VAL C 136   N  ILE C 100           "
        # Then the modified contents:
        contents = [
            "HELIX    1   1 THR A    5  ASP A   20  1                                  16    \n",
            "HELIX    2   2 THR A   28  LEU A   39  1                                  12    \n",
            "HELIX    3   3 THR A   44  ASP A   56  1                                  13    \n",
            "HELIX    4   4 PHE A   65  MET A   76  1                                  12    \n",
            "HELIX    5   5 SER A   81  ASP A   93  1                                  13    \n",
            "HELIX    6   6 SER A  101  LEU A  112  1                                  12    \n",
            "HELIX    7   7 THR A  117  ASP A  129  1                                  13    \n",
            "HELIX    8   8 TYR A  138  THR A  146  1                                   9    \n",
            "HELIX    9   9 VAL A 1615  GLY A 1638  1                                  24    \n",
            "HELIX   10  10 THR B    5  ASP B   20  1                                  16    \n",
            "HELIX   11  11 THR B   28  LEU B   39  1                                  12    \n",
            "HELIX   12  12 THR B   44  ASP B   56  1                                  13    \n",
            "HELIX   13  13 PHE B   65  ASP B   78  1                                  14    \n",
            "HELIX   14  14 GLU B   82  ASP B   93  1                                  12    \n",
            "HELIX   15  15 SER B  101  GLY B  113  1                                  13    \n",
            "HELIX   16  16 THR B  117  ASP B  129  1                                  13    \n",
            "HELIX   17  17 TYR B  138  MET B  145  1                                   8    \n",
            "HELIX   18  18 GLU B 1612  GLN B 1625  1                                  14    \n",
            "HELIX   19  19 THR C    5  ASP C   20  1                                  16    \n",
            "HELIX   20  20 THR C   28  LEU C   39  1                                  12    \n",
            "HELIX   21  21 THR C   44  ASP C   56  1                                  13    \n",
            "HELIX   22  22 PHE C   65  LYS C   75  1                                  11    \n",
            "HELIX   23  23 GLU C   82  ASP C   93  1                                  12    \n",
            "HELIX   24  24 SER C  101  LEU C  112  1                                  12    \n",
            "HELIX   25  25 THR C  117  ASP C  129  1                                  13    \n",
            "HELIX   26  26 TYR C  138  MET C  145  1                                   8    \n",
            "HELIX   27  27 LYS C 1617  GLU C 1636  1                                  20    \n",
            "SHEET    1   A 2 THR A  26  ILE A  27  0                                        \n",
            "SHEET    2   A 2 ILE A  63  ASP A  64 -1  O  ILE A  63   N  ILE A  27           \n",
            "SHEET    1   B 2 TYR A  99  ILE A 100  0                                        \n",
            "SHEET    2   B 2 VAL A 136  ASN A 137 -1  O  VAL A 136   N  ILE A 100           \n",
            "SHEET    1   C 2 THR B  26  ILE B  27  0                                        \n",
            "SHEET    2   C 2 ILE B  63  ASP B  64 -1  O  ILE B  63   N  ILE B  27           \n",
            "SHEET    1   D 2 TYR B  99  ILE B 100  0                                        \n",
            "SHEET    2   D 2 VAL B 136  ASN B 137 -1  O  VAL B 136   N  ILE B 100           \n",
            "SHEET    1   E 2 THR C  26  ILE C  27  0                                        \n",
            "SHEET    2   E 2 ILE C  63  ASP C  64 -1  O  ILE C  63   N  ILE C  27           \n",
            "SHEET    1   F 2 TYR C  99  ILE C 100  0                                        \n",
            "SHEET    2   F 2 VAL C 136  ASN C 137 -1  O  VAL C 136   N  ILE C 100           \n",
        ]

        # Check the created PDB file.
        lines = file.readlines()
        index = 0
        for line in lines:
            # Skip non-secondary structure records.
            if not search('^HELIX', line) and not search('^SHEET', line):
                continue

            # Check the line.
            print("\nOrig: %s" % repr(contents[index]))
            print("New:  %s" % repr(line))
            self.assertEqual(contents[index], line)

            # Increment the secondary structure index.
            index += 1

        # Check the count to make sure that secondary structure records have at all been created.
        self.assertEqual(len(contents), index)


    def test_bug_sr_2998_broken_conect_records(self):
        """Test the bug reported as the U{support request #2998<https://web.archive.org/web/https://gna.org/support/?2998>}, the broken CONECT records."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file.
        self.interpreter.structure.read_pdb('1RTE_trunc.pdb', dir=path)


    def test_collapse_ensemble(self):
        """Test the collapse_ensemble() method of the internal structural object."""

        # Create 2 models.
        self.interpreter.structure.add_model(model_num=1)
        self.interpreter.structure.add_model(model_num=2)

        # Add an atom.
        self.interpreter.structure.add_atom(atom_name='H', res_name='Gly', res_num=1, pos=[[0.0, 1.0, 2.0], [1.0, 2.0, 3.0]], element='H')

        # Check the atomic data.
        for i in range(2):
            mol = cdp.structure.structural_data[i].mol[0]
            self.assertEqual(len(mol.atom_name), 1)
            self.assertEqual(mol.x[0], 0.0+i)
            self.assertEqual(mol.y[0], 1.0+i)
            self.assertEqual(mol.z[0], 2.0+i)

        # Collapse the ensemble to the 2nd model.
        cdp.structure.collapse_ensemble(model_num=2, model_to=1)

        # Check the collapsed ensemble.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(cdp.structure.structural_data[0].num, 1)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 1)

        # Check the atomic data.
        mol = cdp.structure.structural_data[0].mol[0]
        self.assertEqual(len(mol.atom_name), 1)
        self.assertEqual(mol.x[0], 1.0)
        self.assertEqual(mol.y[0], 2.0)
        self.assertEqual(mol.z[0], 3.0)


    def test_create_diff_tensor_pdb(self):
        """Test the deletion of non-existent structural data."""

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Set up a diffusion tensor.
        self.interpreter.diffusion_tensor.init((8.5e-9, 1.1, 20.0, 20.0), param_types=2)

        # Create the PDB representation.
        self.interpreter.structure.create_diff_tensor_pdb(scale=1.8e-06, file='prolate.pdb', dir=ds.tmpdir, force=True)


    def test_create_diff_tensor_pdb2(self):
        """Test the creation of the diffusion tensor PDB representation, after deleting structural data."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDBs.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, set_mol_name='L1')
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_2.pdb', dir=path, set_mol_name='L2')

        # Delete all structural data.
        self.interpreter.structure.delete()

        # Set up a diffusion tensor.
        self.interpreter.diffusion_tensor.init((8.5e-9, 1.1, 20.0, 20.0), param_types=2)

        # Create the PDB representation.
        self.interpreter.structure.create_diff_tensor_pdb(scale=1.8e-06, file='prolate.pdb', dir=ds.tmpdir, force=True)


    def test_create_diff_tensor_pdb_ellipsoid(self):
        """Check that the ellipsoid diffusion tensor optimisation functions correctly."""

        # Reset relax.
        self.interpreter.reset()

        # Create a temporary file.
        ds.tmpfile_handle, ds.tmpfile = mkstemp(suffix='.pdb')

        # The diffusion type (used by the script).
        ds.diff_dir = 'ellipsoid'
        ds.diff_type = 'ellipsoid'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'diff_tensor'+sep+'tensor_opt.py')

        # Create the PDB representation.
        self.interpreter.structure.create_diff_tensor_pdb(scale=1.8e-06, file=ds.tmpfile, force=True)

        # Read the contents of the file.
        file = open(ds.tmpfile)
        lines = file.readlines()
        file.close()

        # What the contents should be, without remarks.
        real_data = [
            "HET    COM  A   1       1                                                       \n",
            "HET    TNS  A   2     240                                                       \n",
            "HET    AXS  A   3      15                                                       \n",
            "HETNAM     COM CENTRE OF MASS                                                   \n",
            "HETNAM     TNS TENSOR                                                           \n",
            "HETNAM     AXS TENSOR AXES                                                      \n",
            "FORMUL   1  COM    C1                                                           \n",
            "FORMUL   2  TNS    H240                                                         \n",
            "FORMUL   3  AXS    C9N6                                                         \n",
            "HETATM    1    R COM A   1      -0.000   0.000   0.000  1.00  0.00           C  \n",
            "HETATM    2   H2 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM    3   H3 TNS A   2      34.069 -26.135  24.079  1.00  0.00           H  \n",
            "HETATM    4   H4 TNS A   2      22.441 -24.585  22.046  1.00  0.00           H  \n",
            "HETATM    5   H5 TNS A   2      12.181 -21.601  18.895  1.00  0.00           H  \n",
            "HETATM    6   H6 TNS A   2       2.612 -17.891  15.178  1.00  0.00           H  \n",
            "HETATM    7   H7 TNS A   2      -6.450 -13.649  11.046  1.00  0.00           H  \n",
            "HETATM    8   H8 TNS A   2     -15.068  -8.941   6.552  1.00  0.00           H  \n",
            "HETATM    9   H9 TNS A   2     -23.243  -3.767   1.694  1.00  0.00           H  \n",
            "HETATM   10  H10 TNS A   2     -30.910   1.939  -3.577  1.00  0.00           H  \n",
            "HETATM   11  H11 TNS A   2     -37.886   8.372  -9.415  1.00  0.00           H  \n",
            "HETATM   12  H12 TNS A   2     -43.495  16.239 -16.370  1.00  0.00           H  \n",
            "HETATM   13  H13 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   14  H14 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   15  H15 TNS A   2      34.065 -22.779  27.601  1.00  0.00           H  \n",
            "HETATM   16  H16 TNS A   2      22.436 -19.088  27.815  1.00  0.00           H  \n",
            "HETATM   17  H17 TNS A   2      12.174 -14.935  25.891  1.00  0.00           H  \n",
            "HETATM   18  H18 TNS A   2       2.605 -10.548  22.885  1.00  0.00           H  \n",
            "HETATM   19  H19 TNS A   2      -6.458  -5.990  19.085  1.00  0.00           H  \n",
            "HETATM   20  H20 TNS A   2     -15.076  -1.281  14.590  1.00  0.00           H  \n",
            "HETATM   21  H21 TNS A   2     -23.250   3.577   9.401  1.00  0.00           H  \n",
            "HETATM   22  H22 TNS A   2     -30.917   8.606   3.419  1.00  0.00           H  \n",
            "HETATM   23  H23 TNS A   2     -37.892  13.869  -3.645  1.00  0.00           H  \n",
            "HETATM   24  H24 TNS A   2     -43.499  19.594 -12.848  1.00  0.00           H  \n",
            "HETATM   25  H25 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   26  H26 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   27  H27 TNS A   2      34.523 -19.268  30.401  1.00  0.00           H  \n",
            "HETATM   28  H28 TNS A   2      23.187 -13.335  32.402  1.00  0.00           H  \n",
            "HETATM   29  H29 TNS A   2      13.085  -7.958  31.453  1.00  0.00           H  \n",
            "HETATM   30  H30 TNS A   2       3.608  -2.863  29.011  1.00  0.00           H  \n",
            "HETATM   31  H31 TNS A   2      -5.412   2.026  25.475  1.00  0.00           H  \n",
            "HETATM   32  H32 TNS A   2     -14.030   6.734  20.981  1.00  0.00           H  \n",
            "HETATM   33  H33 TNS A   2     -22.247  11.261  15.528  1.00  0.00           H  \n",
            "HETATM   34  H34 TNS A   2     -30.006  15.583   8.982  1.00  0.00           H  \n",
            "HETATM   35  H35 TNS A   2     -37.141  19.622   0.941  1.00  0.00           H  \n",
            "HETATM   36  H36 TNS A   2     -43.041  23.105 -10.049  1.00  0.00           H  \n",
            "HETATM   37  H37 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   38  H38 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   39  H39 TNS A   2      35.399 -15.944  32.204  1.00  0.00           H  \n",
            "HETATM   40  H40 TNS A   2      24.621  -7.890  35.357  1.00  0.00           H  \n",
            "HETATM   41  H41 TNS A   2      14.824  -1.355  35.037  1.00  0.00           H  \n",
            "HETATM   42  H42 TNS A   2       5.523   4.411  32.958  1.00  0.00           H  \n",
            "HETATM   43  H43 TNS A   2      -3.414   9.612  29.592  1.00  0.00           H  \n",
            "HETATM   44  H44 TNS A   2     -12.032  14.321  25.098  1.00  0.00           H  \n",
            "HETATM   45  H45 TNS A   2     -20.332  18.535  19.475  1.00  0.00           H  \n",
            "HETATM   46  H46 TNS A   2     -28.268  22.186  12.565  1.00  0.00           H  \n",
            "HETATM   47  H47 TNS A   2     -35.707  25.067   3.896  1.00  0.00           H  \n",
            "HETATM   48  H48 TNS A   2     -42.165  26.429  -8.245  1.00  0.00           H  \n",
            "HETATM   49  H49 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   50  H50 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   51  H51 TNS A   2      36.605 -13.134  32.835  1.00  0.00           H  \n",
            "HETATM   52  H52 TNS A   2      26.597  -3.285  36.390  1.00  0.00           H  \n",
            "HETATM   53  H53 TNS A   2      17.220   4.229  36.290  1.00  0.00           H  \n",
            "HETATM   54  H54 TNS A   2       8.163  10.561  34.339  1.00  0.00           H  \n",
            "HETATM   55  H55 TNS A   2      -0.660  16.028  31.032  1.00  0.00           H  \n",
            "HETATM   56  H56 TNS A   2      -9.278  20.736  26.538  1.00  0.00           H  \n",
            "HETATM   57  H57 TNS A   2     -17.692  24.686  20.856  1.00  0.00           H  \n",
            "HETATM   58  H58 TNS A   2     -25.871  27.770  13.818  1.00  0.00           H  \n",
            "HETATM   59  H59 TNS A   2     -33.730  29.672   4.930  1.00  0.00           H  \n",
            "HETATM   60  H60 TNS A   2     -40.959  29.239  -7.614  1.00  0.00           H  \n",
            "HETATM   61  H61 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   62  H62 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   63  H63 TNS A   2      38.024 -11.112  32.231  1.00  0.00           H  \n",
            "HETATM   64  H64 TNS A   2      28.923   0.028  35.402  1.00  0.00           H  \n",
            "HETATM   65  H65 TNS A   2      20.041   8.247  35.091  1.00  0.00           H  \n",
            "HETATM   66  H66 TNS A   2      11.270  14.987  33.018  1.00  0.00           H  \n",
            "HETATM   67  H67 TNS A   2       2.580  20.644  29.654  1.00  0.00           H  \n",
            "HETATM   68  H68 TNS A   2      -6.038  25.352  25.160  1.00  0.00           H  \n",
            "HETATM   69  H69 TNS A   2     -14.585  29.111  19.535  1.00  0.00           H  \n",
            "HETATM   70  H70 TNS A   2     -23.051  31.787  12.619  1.00  0.00           H  \n",
            "HETATM   71  H71 TNS A   2     -31.405  32.985   3.941  1.00  0.00           H  \n",
            "HETATM   72  H72 TNS A   2     -39.540  31.262  -8.218  1.00  0.00           H  \n",
            "HETATM   73  H73 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   74  H74 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   75  H75 TNS A   2      39.518 -10.076  30.453  1.00  0.00           H  \n",
            "HETATM   76  H76 TNS A   2      31.370   1.725  32.487  1.00  0.00           H  \n",
            "HETATM   77  H77 TNS A   2      23.008  10.305  31.557  1.00  0.00           H  \n",
            "HETATM   78  H78 TNS A   2      14.538  17.254  29.125  1.00  0.00           H  \n",
            "HETATM   79  H79 TNS A   2       5.989  23.008  25.594  1.00  0.00           H  \n",
            "HETATM   80  H80 TNS A   2      -2.629  27.717  21.100  1.00  0.00           H  \n",
            "HETATM   81  H81 TNS A   2     -11.316  31.378  15.642  1.00  0.00           H  \n",
            "HETATM   82  H82 TNS A   2     -20.083  33.846   9.085  1.00  0.00           H  \n",
            "HETATM   83  H83 TNS A   2     -28.958  34.682   1.027  1.00  0.00           H  \n",
            "HETATM   84  H84 TNS A   2     -38.046  32.298  -9.997  1.00  0.00           H  \n",
            "HETATM   85  H85 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   86  H86 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   87  H87 TNS A   2      40.940 -10.127  27.673  1.00  0.00           H  \n",
            "HETATM   88  H88 TNS A   2      33.699   1.641  27.933  1.00  0.00           H  \n",
            "HETATM   89  H89 TNS A   2      25.832  10.202  26.033  1.00  0.00           H  \n",
            "HETATM   90  H90 TNS A   2      17.649  17.141  23.041  1.00  0.00           H  \n",
            "HETATM   91  H91 TNS A   2       9.234  22.891  19.248  1.00  0.00           H  \n",
            "HETATM   92  H92 TNS A   2       0.616  27.599  14.754  1.00  0.00           H  \n",
            "HETATM   93  H93 TNS A   2      -8.205  31.265   9.558  1.00  0.00           H  \n",
            "HETATM   94  H94 TNS A   2     -17.259  33.743   3.562  1.00  0.00           H  \n",
            "HETATM   95  H95 TNS A   2     -26.629  34.598  -3.528  1.00  0.00           H  \n",
            "HETATM   96  H96 TNS A   2     -36.624  32.246 -12.777  1.00  0.00           H  \n",
            "HETATM   97  H97 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   98  H98 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   99  H99 TNS A   2      42.150 -11.262  24.164  1.00  0.00           H  \n",
            "HETATM  100 H100 TNS A   2      35.682  -0.218  22.184  1.00  0.00           H  \n",
            "HETATM  101 H101 TNS A   2      28.237   7.949  19.062  1.00  0.00           H  \n",
            "HETATM  102 H102 TNS A   2      20.298  14.659  15.362  1.00  0.00           H  \n",
            "HETATM  103 H103 TNS A   2      11.997  20.302  11.238  1.00  0.00           H  \n",
            "HETATM  104 H104 TNS A   2       3.379  25.010   6.744  1.00  0.00           H  \n",
            "HETATM  105 H105 TNS A   2      -5.557  28.783   1.879  1.00  0.00           H  \n",
            "HETATM  106 H106 TNS A   2     -14.854  31.490  -3.410  1.00  0.00           H  \n",
            "HETATM  107 H107 TNS A   2     -24.646  32.739  -9.277  1.00  0.00           H  \n",
            "HETATM  108 H108 TNS A   2     -35.414  31.112 -16.286  1.00  0.00           H  \n",
            "HETATM  109 H109 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  110 H110 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  111 H111 TNS A   2      43.031 -13.367  20.269  1.00  0.00           H  \n",
            "HETATM  112 H112 TNS A   2      37.125  -3.668  15.803  1.00  0.00           H  \n",
            "HETATM  113 H113 TNS A   2      29.987   3.765  11.324  1.00  0.00           H  \n",
            "HETATM  114 H114 TNS A   2      22.225  10.050   6.838  1.00  0.00           H  \n",
            "HETATM  115 H115 TNS A   2      14.007  15.495   2.348  1.00  0.00           H  \n",
            "HETATM  116 H116 TNS A   2       5.389  20.203  -2.146  1.00  0.00           H  \n",
            "HETATM  117 H117 TNS A   2      -3.629  24.175  -6.645  1.00  0.00           H  \n",
            "HETATM  118 H118 TNS A   2     -13.104  27.306 -11.148  1.00  0.00           H  \n",
            "HETATM  119 H119 TNS A   2     -23.203  29.289 -15.658  1.00  0.00           H  \n",
            "HETATM  120 H120 TNS A   2     -34.533  29.006 -20.181  1.00  0.00           H  \n",
            "HETATM  121 H121 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  122 H122 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  123 H123 TNS A   2      43.495 -16.239  16.370  1.00  0.00           H  \n",
            "HETATM  124 H124 TNS A   2      37.886  -8.372   9.415  1.00  0.00           H  \n",
            "HETATM  125 H125 TNS A   2      30.910  -1.939   3.577  1.00  0.00           H  \n",
            "HETATM  126 H126 TNS A   2      23.243   3.767  -1.694  1.00  0.00           H  \n",
            "HETATM  127 H127 TNS A   2      15.068   8.941  -6.552  1.00  0.00           H  \n",
            "HETATM  128 H128 TNS A   2       6.450  13.649 -11.046  1.00  0.00           H  \n",
            "HETATM  129 H129 TNS A   2      -2.612  17.891 -15.178  1.00  0.00           H  \n",
            "HETATM  130 H130 TNS A   2     -12.181  21.601 -18.895  1.00  0.00           H  \n",
            "HETATM  131 H131 TNS A   2     -22.441  24.585 -22.046  1.00  0.00           H  \n",
            "HETATM  132 H132 TNS A   2     -34.069  26.135 -24.079  1.00  0.00           H  \n",
            "HETATM  133 H133 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  134 H134 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  135 H135 TNS A   2      43.499 -19.594  12.848  1.00  0.00           H  \n",
            "HETATM  136 H136 TNS A   2      37.892 -13.869   3.645  1.00  0.00           H  \n",
            "HETATM  137 H137 TNS A   2      30.917  -8.606  -3.419  1.00  0.00           H  \n",
            "HETATM  138 H138 TNS A   2      23.250  -3.577  -9.401  1.00  0.00           H  \n",
            "HETATM  139 H139 TNS A   2      15.076   1.281 -14.590  1.00  0.00           H  \n",
            "HETATM  140 H140 TNS A   2       6.458   5.990 -19.085  1.00  0.00           H  \n",
            "HETATM  141 H141 TNS A   2      -2.605  10.548 -22.885  1.00  0.00           H  \n",
            "HETATM  142 H142 TNS A   2     -12.174  14.935 -25.891  1.00  0.00           H  \n",
            "HETATM  143 H143 TNS A   2     -22.436  19.088 -27.815  1.00  0.00           H  \n",
            "HETATM  144 H144 TNS A   2     -34.065  22.779 -27.601  1.00  0.00           H  \n",
            "HETATM  145 H145 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  146 H146 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  147 H147 TNS A   2      43.041 -23.105  10.049  1.00  0.00           H  \n",
            "HETATM  148 H148 TNS A   2      37.141 -19.622  -0.941  1.00  0.00           H  \n",
            "HETATM  149 H149 TNS A   2      30.006 -15.583  -8.982  1.00  0.00           H  \n",
            "HETATM  150 H150 TNS A   2      22.247 -11.261 -15.528  1.00  0.00           H  \n",
            "HETATM  151 H151 TNS A   2      14.030  -6.734 -20.981  1.00  0.00           H  \n",
            "HETATM  152 H152 TNS A   2       5.412  -2.026 -25.475  1.00  0.00           H  \n",
            "HETATM  153 H153 TNS A   2      -3.608   2.863 -29.011  1.00  0.00           H  \n",
            "HETATM  154 H154 TNS A   2     -13.085   7.958 -31.453  1.00  0.00           H  \n",
            "HETATM  155 H155 TNS A   2     -23.187  13.335 -32.402  1.00  0.00           H  \n",
            "HETATM  156 H156 TNS A   2     -34.523  19.268 -30.401  1.00  0.00           H  \n",
            "HETATM  157 H157 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  158 H158 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  159 H159 TNS A   2      42.165 -26.429   8.245  1.00  0.00           H  \n",
            "HETATM  160 H160 TNS A   2      35.707 -25.067  -3.896  1.00  0.00           H  \n",
            "HETATM  161 H161 TNS A   2      28.268 -22.186 -12.565  1.00  0.00           H  \n",
            "HETATM  162 H162 TNS A   2      20.332 -18.535 -19.475  1.00  0.00           H  \n",
            "HETATM  163 H163 TNS A   2      12.032 -14.321 -25.098  1.00  0.00           H  \n",
            "HETATM  164 H164 TNS A   2       3.414  -9.612 -29.592  1.00  0.00           H  \n",
            "HETATM  165 H165 TNS A   2      -5.523  -4.411 -32.958  1.00  0.00           H  \n",
            "HETATM  166 H166 TNS A   2     -14.824   1.355 -35.037  1.00  0.00           H  \n",
            "HETATM  167 H167 TNS A   2     -24.621   7.890 -35.357  1.00  0.00           H  \n",
            "HETATM  168 H168 TNS A   2     -35.399  15.944 -32.204  1.00  0.00           H  \n",
            "HETATM  169 H169 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  170 H170 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  171 H171 TNS A   2      40.959 -29.239   7.614  1.00  0.00           H  \n",
            "HETATM  172 H172 TNS A   2      33.730 -29.672  -4.930  1.00  0.00           H  \n",
            "HETATM  173 H173 TNS A   2      25.871 -27.770 -13.818  1.00  0.00           H  \n",
            "HETATM  174 H174 TNS A   2      17.692 -24.686 -20.856  1.00  0.00           H  \n",
            "HETATM  175 H175 TNS A   2       9.278 -20.736 -26.538  1.00  0.00           H  \n",
            "HETATM  176 H176 TNS A   2       0.660 -16.028 -31.032  1.00  0.00           H  \n",
            "HETATM  177 H177 TNS A   2      -8.163 -10.561 -34.339  1.00  0.00           H  \n",
            "HETATM  178 H178 TNS A   2     -17.220  -4.229 -36.290  1.00  0.00           H  \n",
            "HETATM  179 H179 TNS A   2     -26.597   3.285 -36.390  1.00  0.00           H  \n",
            "HETATM  180 H180 TNS A   2     -36.605  13.134 -32.835  1.00  0.00           H  \n",
            "HETATM  181 H181 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  182 H182 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  183 H183 TNS A   2      39.540 -31.262   8.218  1.00  0.00           H  \n",
            "HETATM  184 H184 TNS A   2      31.405 -32.985  -3.941  1.00  0.00           H  \n",
            "HETATM  185 H185 TNS A   2      23.051 -31.787 -12.619  1.00  0.00           H  \n",
            "HETATM  186 H186 TNS A   2      14.585 -29.111 -19.535  1.00  0.00           H  \n",
            "HETATM  187 H187 TNS A   2       6.038 -25.352 -25.160  1.00  0.00           H  \n",
            "HETATM  188 H188 TNS A   2      -2.580 -20.644 -29.654  1.00  0.00           H  \n",
            "HETATM  189 H189 TNS A   2     -11.270 -14.987 -33.018  1.00  0.00           H  \n",
            "HETATM  190 H190 TNS A   2     -20.041  -8.247 -35.091  1.00  0.00           H  \n",
            "HETATM  191 H191 TNS A   2     -28.923  -0.028 -35.402  1.00  0.00           H  \n",
            "HETATM  192 H192 TNS A   2     -38.024  11.112 -32.231  1.00  0.00           H  \n",
            "HETATM  193 H193 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  194 H194 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  195 H195 TNS A   2      38.046 -32.298   9.997  1.00  0.00           H  \n",
            "HETATM  196 H196 TNS A   2      28.958 -34.682  -1.027  1.00  0.00           H  \n",
            "HETATM  197 H197 TNS A   2      20.083 -33.846  -9.085  1.00  0.00           H  \n",
            "HETATM  198 H198 TNS A   2      11.316 -31.378 -15.642  1.00  0.00           H  \n",
            "HETATM  199 H199 TNS A   2       2.629 -27.717 -21.100  1.00  0.00           H  \n",
            "HETATM  200 H200 TNS A   2      -5.989 -23.008 -25.594  1.00  0.00           H  \n",
            "HETATM  201 H201 TNS A   2     -14.538 -17.254 -29.125  1.00  0.00           H  \n",
            "HETATM  202 H202 TNS A   2     -23.008 -10.305 -31.557  1.00  0.00           H  \n",
            "HETATM  203 H203 TNS A   2     -31.370  -1.725 -32.487  1.00  0.00           H  \n",
            "HETATM  204 H204 TNS A   2     -39.518  10.076 -30.453  1.00  0.00           H  \n",
            "HETATM  205 H205 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  206 H206 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  207 H207 TNS A   2      36.624 -32.246  12.777  1.00  0.00           H  \n",
            "HETATM  208 H208 TNS A   2      26.629 -34.598   3.528  1.00  0.00           H  \n",
            "HETATM  209 H209 TNS A   2      17.259 -33.743  -3.562  1.00  0.00           H  \n",
            "HETATM  210 H210 TNS A   2       8.205 -31.265  -9.558  1.00  0.00           H  \n",
            "HETATM  211 H211 TNS A   2      -0.616 -27.599 -14.754  1.00  0.00           H  \n",
            "HETATM  212 H212 TNS A   2      -9.234 -22.891 -19.248  1.00  0.00           H  \n",
            "HETATM  213 H213 TNS A   2     -17.649 -17.141 -23.041  1.00  0.00           H  \n",
            "HETATM  214 H214 TNS A   2     -25.832 -10.202 -26.033  1.00  0.00           H  \n",
            "HETATM  215 H215 TNS A   2     -33.699  -1.641 -27.933  1.00  0.00           H  \n",
            "HETATM  216 H216 TNS A   2     -40.940  10.127 -27.673  1.00  0.00           H  \n",
            "HETATM  217 H217 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  218 H218 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  219 H219 TNS A   2      35.414 -31.112  16.286  1.00  0.00           H  \n",
            "HETATM  220 H220 TNS A   2      24.646 -32.739   9.277  1.00  0.00           H  \n",
            "HETATM  221 H221 TNS A   2      14.854 -31.490   3.410  1.00  0.00           H  \n",
            "HETATM  222 H222 TNS A   2       5.557 -28.783  -1.879  1.00  0.00           H  \n",
            "HETATM  223 H223 TNS A   2      -3.379 -25.010  -6.744  1.00  0.00           H  \n",
            "HETATM  224 H224 TNS A   2     -11.997 -20.302 -11.238  1.00  0.00           H  \n",
            "HETATM  225 H225 TNS A   2     -20.298 -14.659 -15.362  1.00  0.00           H  \n",
            "HETATM  226 H226 TNS A   2     -28.237  -7.949 -19.062  1.00  0.00           H  \n",
            "HETATM  227 H227 TNS A   2     -35.682   0.218 -22.184  1.00  0.00           H  \n",
            "HETATM  228 H228 TNS A   2     -42.150  11.262 -24.164  1.00  0.00           H  \n",
            "HETATM  229 H229 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  230 H230 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  231 H231 TNS A   2      34.533 -29.006  20.181  1.00  0.00           H  \n",
            "HETATM  232 H232 TNS A   2      23.203 -29.289  15.658  1.00  0.00           H  \n",
            "HETATM  233 H233 TNS A   2      13.104 -27.306  11.148  1.00  0.00           H  \n",
            "HETATM  234 H234 TNS A   2       3.629 -24.175   6.645  1.00  0.00           H  \n",
            "HETATM  235 H235 TNS A   2      -5.389 -20.203   2.146  1.00  0.00           H  \n",
            "HETATM  236 H236 TNS A   2     -14.007 -15.495  -2.348  1.00  0.00           H  \n",
            "HETATM  237 H237 TNS A   2     -22.225 -10.050  -6.838  1.00  0.00           H  \n",
            "HETATM  238 H238 TNS A   2     -29.987  -3.765 -11.324  1.00  0.00           H  \n",
            "HETATM  239 H239 TNS A   2     -37.125   3.668 -15.803  1.00  0.00           H  \n",
            "HETATM  240 H240 TNS A   2     -43.031  13.367 -20.269  1.00  0.00           H  \n",
            "HETATM  241 H241 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  242    R AXS A   3      -0.000   0.000   0.000  1.00  0.00           C  \n",
            "HETATM  243   Dx AXS A   3     -10.813 -11.352   8.843  1.00  0.00           C  \n",
            "HETATM  244   Dx AXS A   3      10.813  11.352  -8.843  1.00  0.00           C  \n",
            "HETATM  245   Dx AXS A   3     -11.895 -12.487   9.728  1.00  0.00           N  \n",
            "HETATM  246   Dx AXS A   3      11.895  12.487  -9.728  1.00  0.00           N  \n",
            "HETATM  247    R AXS A   3      -0.000   0.000   0.000  1.00  0.00           C  \n",
            "HETATM  248   Dy AXS A   3      -1.738  23.114  27.545  1.00  0.00           C  \n",
            "HETATM  249   Dy AXS A   3       1.738 -23.114 -27.545  1.00  0.00           C  \n",
            "HETATM  250   Dy AXS A   3      -1.912  25.425  30.300  1.00  0.00           N  \n",
            "HETATM  251   Dy AXS A   3       1.912 -25.425 -30.300  1.00  0.00           N  \n",
            "HETATM  252    R AXS A   3      -0.000   0.000   0.000  1.00  0.00           C  \n",
            "HETATM  253   Dz AXS A   3     -43.091  23.541 -22.472  1.00  0.00           C  \n",
            "HETATM  254   Dz AXS A   3      43.091 -23.541  22.472  1.00  0.00           C  \n",
            "HETATM  255   Dz AXS A   3     -47.400  25.895 -24.719  1.00  0.00           N  \n",
            "HETATM  256   Dz AXS A   3      47.400 -25.895  24.719  1.00  0.00           N  \n",
            "CONECT    2    3   14  230                                                      \n",
            "CONECT    3    2    4   15  231                                                 \n",
            "CONECT    4    3    5   16  232                                                 \n",
            "CONECT    5    4    6   17  233                                                 \n",
            "CONECT    6    5    7   18  234                                                 \n",
            "CONECT    7    6    8   19  235                                                 \n",
            "CONECT    8    7    9   20  236                                                 \n",
            "CONECT    9    8   10   21  237                                                 \n",
            "CONECT   10    9   11   22  238                                                 \n",
            "CONECT   11   10   12   23  239                                                 \n",
            "CONECT   12   11   13   24  240                                                 \n",
            "CONECT   13   12   25  241                                                      \n",
            "CONECT   14    2   15   26                                                      \n",
            "CONECT   15   14    3   16   27                                                 \n",
            "CONECT   16   15    4   17   28                                                 \n",
            "CONECT   17   16    5   18   29                                                 \n",
            "CONECT   18   17    6   19   30                                                 \n",
            "CONECT   19   18    7   20   31                                                 \n",
            "CONECT   20   19    8   21   32                                                 \n",
            "CONECT   21   20    9   22   33                                                 \n",
            "CONECT   22   21   10   23   34                                                 \n",
            "CONECT   23   22   11   24   35                                                 \n",
            "CONECT   24   23   12   25   36                                                 \n",
            "CONECT   25   24   13   37                                                      \n",
            "CONECT   26   14   27   38                                                      \n",
            "CONECT   27   26   15   28   39                                                 \n",
            "CONECT   28   27   16   29   40                                                 \n",
            "CONECT   29   28   17   30   41                                                 \n",
            "CONECT   30   29   18   31   42                                                 \n",
            "CONECT   31   30   19   32   43                                                 \n",
            "CONECT   32   31   20   33   44                                                 \n",
            "CONECT   33   32   21   34   45                                                 \n",
            "CONECT   34   33   22   35   46                                                 \n",
            "CONECT   35   34   23   36   47                                                 \n",
            "CONECT   36   35   24   37   48                                                 \n",
            "CONECT   37   36   25   49                                                      \n",
            "CONECT   38   26   39   50                                                      \n",
            "CONECT   39   38   27   40   51                                                 \n",
            "CONECT   40   39   28   41   52                                                 \n",
            "CONECT   41   40   29   42   53                                                 \n",
            "CONECT   42   41   30   43   54                                                 \n",
            "CONECT   43   42   31   44   55                                                 \n",
            "CONECT   44   43   32   45   56                                                 \n",
            "CONECT   45   44   33   46   57                                                 \n",
            "CONECT   46   45   34   47   58                                                 \n",
            "CONECT   47   46   35   48   59                                                 \n",
            "CONECT   48   47   36   49   60                                                 \n",
            "CONECT   49   48   37   61                                                      \n",
            "CONECT   50   38   51   62                                                      \n",
            "CONECT   51   50   39   52   63                                                 \n",
            "CONECT   52   51   40   53   64                                                 \n",
            "CONECT   53   52   41   54   65                                                 \n",
            "CONECT   54   53   42   55   66                                                 \n",
            "CONECT   55   54   43   56   67                                                 \n",
            "CONECT   56   55   44   57   68                                                 \n",
            "CONECT   57   56   45   58   69                                                 \n",
            "CONECT   58   57   46   59   70                                                 \n",
            "CONECT   59   58   47   60   71                                                 \n",
            "CONECT   60   59   48   61   72                                                 \n",
            "CONECT   61   60   49   73                                                      \n",
            "CONECT   62   50   63   74                                                      \n",
            "CONECT   63   62   51   64   75                                                 \n",
            "CONECT   64   63   52   65   76                                                 \n",
            "CONECT   65   64   53   66   77                                                 \n",
            "CONECT   66   65   54   67   78                                                 \n",
            "CONECT   67   66   55   68   79                                                 \n",
            "CONECT   68   67   56   69   80                                                 \n",
            "CONECT   69   68   57   70   81                                                 \n",
            "CONECT   70   69   58   71   82                                                 \n",
            "CONECT   71   70   59   72   83                                                 \n",
            "CONECT   72   71   60   73   84                                                 \n",
            "CONECT   73   72   61   85                                                      \n",
            "CONECT   74   62   75   86                                                      \n",
            "CONECT   75   74   63   76   87                                                 \n",
            "CONECT   76   75   64   77   88                                                 \n",
            "CONECT   77   76   65   78   89                                                 \n",
            "CONECT   78   77   66   79   90                                                 \n",
            "CONECT   79   78   67   80   91                                                 \n",
            "CONECT   80   79   68   81   92                                                 \n",
            "CONECT   81   80   69   82   93                                                 \n",
            "CONECT   82   81   70   83   94                                                 \n",
            "CONECT   83   82   71   84   95                                                 \n",
            "CONECT   84   83   72   85   96                                                 \n",
            "CONECT   85   84   73   97                                                      \n",
            "CONECT   86   74   87   98                                                      \n",
            "CONECT   87   86   75   88   99                                                 \n",
            "CONECT   88   87   76   89  100                                                 \n",
            "CONECT   89   88   77   90  101                                                 \n",
            "CONECT   90   89   78   91  102                                                 \n",
            "CONECT   91   90   79   92  103                                                 \n",
            "CONECT   92   91   80   93  104                                                 \n",
            "CONECT   93   92   81   94  105                                                 \n",
            "CONECT   94   93   82   95  106                                                 \n",
            "CONECT   95   94   83   96  107                                                 \n",
            "CONECT   96   95   84   97  108                                                 \n",
            "CONECT   97   96   85  109                                                      \n",
            "CONECT   98   86   99  110                                                      \n",
            "CONECT   99   98   87  100  111                                                 \n",
            "CONECT  100   99   88  101  112                                                 \n",
            "CONECT  101  100   89  102  113                                                 \n",
            "CONECT  102  101   90  103  114                                                 \n",
            "CONECT  103  102   91  104  115                                                 \n",
            "CONECT  104  103   92  105  116                                                 \n",
            "CONECT  105  104   93  106  117                                                 \n",
            "CONECT  106  105   94  107  118                                                 \n",
            "CONECT  107  106   95  108  119                                                 \n",
            "CONECT  108  107   96  109  120                                                 \n",
            "CONECT  109  108   97  121                                                      \n",
            "CONECT  110   98  111  122                                                      \n",
            "CONECT  111  110   99  112  123                                                 \n",
            "CONECT  112  111  100  113  124                                                 \n",
            "CONECT  113  112  101  114  125                                                 \n",
            "CONECT  114  113  102  115  126                                                 \n",
            "CONECT  115  114  103  116  127                                                 \n",
            "CONECT  116  115  104  117  128                                                 \n",
            "CONECT  117  116  105  118  129                                                 \n",
            "CONECT  118  117  106  119  130                                                 \n",
            "CONECT  119  118  107  120  131                                                 \n",
            "CONECT  120  119  108  121  132                                                 \n",
            "CONECT  121  120  109  133                                                      \n",
            "CONECT  122  110  123  134                                                      \n",
            "CONECT  123  122  111  124  135                                                 \n",
            "CONECT  124  123  112  125  136                                                 \n",
            "CONECT  125  124  113  126  137                                                 \n",
            "CONECT  126  125  114  127  138                                                 \n",
            "CONECT  127  126  115  128  139                                                 \n",
            "CONECT  128  127  116  129  140                                                 \n",
            "CONECT  129  128  117  130  141                                                 \n",
            "CONECT  130  129  118  131  142                                                 \n",
            "CONECT  131  130  119  132  143                                                 \n",
            "CONECT  132  131  120  133  144                                                 \n",
            "CONECT  133  132  121  145                                                      \n",
            "CONECT  134  122  135  146                                                      \n",
            "CONECT  135  134  123  136  147                                                 \n",
            "CONECT  136  135  124  137  148                                                 \n",
            "CONECT  137  136  125  138  149                                                 \n",
            "CONECT  138  137  126  139  150                                                 \n",
            "CONECT  139  138  127  140  151                                                 \n",
            "CONECT  140  139  128  141  152                                                 \n",
            "CONECT  141  140  129  142  153                                                 \n",
            "CONECT  142  141  130  143  154                                                 \n",
            "CONECT  143  142  131  144  155                                                 \n",
            "CONECT  144  143  132  145  156                                                 \n",
            "CONECT  145  144  133  157                                                      \n",
            "CONECT  146  134  147  158                                                      \n",
            "CONECT  147  146  135  148  159                                                 \n",
            "CONECT  148  147  136  149  160                                                 \n",
            "CONECT  149  148  137  150  161                                                 \n",
            "CONECT  150  149  138  151  162                                                 \n",
            "CONECT  151  150  139  152  163                                                 \n",
            "CONECT  152  151  140  153  164                                                 \n",
            "CONECT  153  152  141  154  165                                                 \n",
            "CONECT  154  153  142  155  166                                                 \n",
            "CONECT  155  154  143  156  167                                                 \n",
            "CONECT  156  155  144  157  168                                                 \n",
            "CONECT  157  156  145  169                                                      \n",
            "CONECT  158  146  159  170                                                      \n",
            "CONECT  159  158  147  160  171                                                 \n",
            "CONECT  160  159  148  161  172                                                 \n",
            "CONECT  161  160  149  162  173                                                 \n",
            "CONECT  162  161  150  163  174                                                 \n",
            "CONECT  163  162  151  164  175                                                 \n",
            "CONECT  164  163  152  165  176                                                 \n",
            "CONECT  165  164  153  166  177                                                 \n",
            "CONECT  166  165  154  167  178                                                 \n",
            "CONECT  167  166  155  168  179                                                 \n",
            "CONECT  168  167  156  169  180                                                 \n",
            "CONECT  169  168  157  181                                                      \n",
            "CONECT  170  158  171  182                                                      \n",
            "CONECT  171  170  159  172  183                                                 \n",
            "CONECT  172  171  160  173  184                                                 \n",
            "CONECT  173  172  161  174  185                                                 \n",
            "CONECT  174  173  162  175  186                                                 \n",
            "CONECT  175  174  163  176  187                                                 \n",
            "CONECT  176  175  164  177  188                                                 \n",
            "CONECT  177  176  165  178  189                                                 \n",
            "CONECT  178  177  166  179  190                                                 \n",
            "CONECT  179  178  167  180  191                                                 \n",
            "CONECT  180  179  168  181  192                                                 \n",
            "CONECT  181  180  169  193                                                      \n",
            "CONECT  182  170  183  194                                                      \n",
            "CONECT  183  182  171  184  195                                                 \n",
            "CONECT  184  183  172  185  196                                                 \n",
            "CONECT  185  184  173  186  197                                                 \n",
            "CONECT  186  185  174  187  198                                                 \n",
            "CONECT  187  186  175  188  199                                                 \n",
            "CONECT  188  187  176  189  200                                                 \n",
            "CONECT  189  188  177  190  201                                                 \n",
            "CONECT  190  189  178  191  202                                                 \n",
            "CONECT  191  190  179  192  203                                                 \n",
            "CONECT  192  191  180  193  204                                                 \n",
            "CONECT  193  192  181  205                                                      \n",
            "CONECT  194  182  195  206                                                      \n",
            "CONECT  195  194  183  196  207                                                 \n",
            "CONECT  196  195  184  197  208                                                 \n",
            "CONECT  197  196  185  198  209                                                 \n",
            "CONECT  198  197  186  199  210                                                 \n",
            "CONECT  199  198  187  200  211                                                 \n",
            "CONECT  200  199  188  201  212                                                 \n",
            "CONECT  201  200  189  202  213                                                 \n",
            "CONECT  202  201  190  203  214                                                 \n",
            "CONECT  203  202  191  204  215                                                 \n",
            "CONECT  204  203  192  205  216                                                 \n",
            "CONECT  205  204  193  217                                                      \n",
            "CONECT  206  194  207  218                                                      \n",
            "CONECT  207  206  195  208  219                                                 \n",
            "CONECT  208  207  196  209  220                                                 \n",
            "CONECT  209  208  197  210  221                                                 \n",
            "CONECT  210  209  198  211  222                                                 \n",
            "CONECT  211  210  199  212  223                                                 \n",
            "CONECT  212  211  200  213  224                                                 \n",
            "CONECT  213  212  201  214  225                                                 \n",
            "CONECT  214  213  202  215  226                                                 \n",
            "CONECT  215  214  203  216  227                                                 \n",
            "CONECT  216  215  204  217  228                                                 \n",
            "CONECT  217  216  205  229                                                      \n",
            "CONECT  218  206  219  230                                                      \n",
            "CONECT  219  218  207  220  231                                                 \n",
            "CONECT  220  219  208  221  232                                                 \n",
            "CONECT  221  220  209  222  233                                                 \n",
            "CONECT  222  221  210  223  234                                                 \n",
            "CONECT  223  222  211  224  235                                                 \n",
            "CONECT  224  223  212  225  236                                                 \n",
            "CONECT  225  224  213  226  237                                                 \n",
            "CONECT  226  225  214  227  238                                                 \n",
            "CONECT  227  226  215  228  239                                                 \n",
            "CONECT  228  227  216  229  240                                                 \n",
            "CONECT  229  228  217  241                                                      \n",
            "CONECT  230  218    2  231                                                      \n",
            "CONECT  231  230  219    3  232                                                 \n",
            "CONECT  232  231  220    4  233                                                 \n",
            "CONECT  233  232  221    5  234                                                 \n",
            "CONECT  234  233  222    6  235                                                 \n",
            "CONECT  235  234  223    7  236                                                 \n",
            "CONECT  236  235  224    8  237                                                 \n",
            "CONECT  237  236  225    9  238                                                 \n",
            "CONECT  238  237  226   10  239                                                 \n",
            "CONECT  239  238  227   11  240                                                 \n",
            "CONECT  240  239  228   12  241                                                 \n",
            "CONECT  241  240  229   13                                                      \n",
            "CONECT  242  243  244                                                           \n",
            "CONECT  243  242                                                                \n",
            "CONECT  244  242                                                                \n",
            "CONECT  247  248  249                                                           \n",
            "CONECT  248  247                                                                \n",
            "CONECT  249  247                                                                \n",
            "CONECT  252  253  254                                                           \n",
            "CONECT  253  252                                                                \n",
            "CONECT  254  252                                                                \n",
            "MASTER        0    0    3    0    0    0    0    0  256    0  249    0          \n",
            "END                                                                             \n"
        ]

        # Check the data.
        self.strip_remarks(lines)
        self.assertEqual(len(real_data), len(lines))
        for i in range(len(lines)):
            self.assertEqual(real_data[i], lines[i])


    def test_create_diff_tensor_pdb_oblate(self):
        """Check the 3D coordinates of the PDB representation of the optimised oblate diffusion tensor."""

        # Reset relax.
        self.interpreter.reset()

        # Create a temporary file.
        ds.tmpfile_handle, ds.tmpfile = mkstemp(suffix='.pdb')

        # The diffusion type and directory (used by the script).
        ds.diff_dir = 'spheroid_oblate'
        ds.diff_type = 'oblate'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'diff_tensor'+sep+'tensor_opt.py')

        # Create the PDB representation.
        self.interpreter.structure.create_diff_tensor_pdb(scale=1.8e-06, file=ds.tmpfile, force=True)

        # Read the contents of the file.
        file = open(ds.tmpfile)
        lines = file.readlines()
        file.close()

        # What the contents should be, without remarks.
        real_data = [
            "HET    COM  A   1       1                                                       \n",
            "HET    TNS  A   2     240                                                       \n",
            "HET    AXS  A   3       5                                                       \n",
            "HETNAM     COM CENTRE OF MASS                                                   \n",
            "HETNAM     TNS TENSOR                                                           \n",
            "HETNAM     AXS TENSOR AXES                                                      \n",
            "FORMUL   1  COM    C1                                                           \n",
            "FORMUL   2  TNS    H240                                                         \n",
            "FORMUL   3  AXS    C3N2                                                         \n",
            "HETATM    1    R COM A   1      -0.000   0.000   0.000  1.00  0.00           C  \n",
            "HETATM    2   H2 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM    3   H3 TNS A   2     -31.028 -24.990  -4.071  1.00  0.00           H  \n",
            "HETATM    4   H4 TNS A   2     -34.085 -23.357 -20.368  1.00  0.00           H  \n",
            "HETATM    5   H5 TNS A   2     -33.789 -20.404 -30.870  1.00  0.00           H  \n",
            "HETATM    6   H6 TNS A   2     -31.796 -16.782 -38.439  1.00  0.00           H  \n",
            "HETATM    7   H7 TNS A   2     -28.560 -12.670 -43.859  1.00  0.00           H  \n",
            "HETATM    8   H8 TNS A   2     -24.234  -8.130 -47.396  1.00  0.00           H  \n",
            "HETATM    9   H9 TNS A   2     -18.820  -3.160 -49.051  1.00  0.00           H  \n",
            "HETATM   10  H10 TNS A   2     -12.162   2.300 -48.557  1.00  0.00           H  \n",
            "HETATM   11  H11 TNS A   2      -3.807   8.428 -45.129  1.00  0.00           H  \n",
            "HETATM   12  H12 TNS A   2       7.900  15.877 -35.907  1.00  0.00           H  \n",
            "HETATM   13  H13 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM   14  H14 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM   15  H15 TNS A   2     -35.049 -19.300  -1.685  1.00  0.00           H  \n",
            "HETATM   16  H16 TNS A   2     -40.673 -14.036 -16.459  1.00  0.00           H  \n",
            "HETATM   17  H17 TNS A   2     -41.778  -9.100 -26.129  1.00  0.00           H  \n",
            "HETATM   18  H18 TNS A   2     -40.596  -4.331 -33.217  1.00  0.00           H  \n",
            "HETATM   19  H19 TNS A   2     -37.739   0.317 -38.412  1.00  0.00           H  \n",
            "HETATM   20  H20 TNS A   2     -33.413   4.857 -41.949  1.00  0.00           H  \n",
            "HETATM   21  H21 TNS A   2     -27.620   9.291 -43.829  1.00  0.00           H  \n",
            "HETATM   22  H22 TNS A   2     -20.152  13.604 -43.816  1.00  0.00           H  \n",
            "HETATM   23  H23 TNS A   2     -10.396  17.749 -41.220  1.00  0.00           H  \n",
            "HETATM   24  H24 TNS A   2       3.879  21.567 -33.521  1.00  0.00           H  \n",
            "HETATM   25  H25 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM   26  H26 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM   27  H27 TNS A   2     -37.545 -13.722   2.425  1.00  0.00           H  \n",
            "HETATM   28  H28 TNS A   2     -44.762  -4.897  -9.726  1.00  0.00           H  \n",
            "HETATM   29  H29 TNS A   2     -46.737   1.983 -17.965  1.00  0.00           H  \n",
            "HETATM   30  H30 TNS A   2     -46.058   7.877 -24.224  1.00  0.00           H  \n",
            "HETATM   31  H31 TNS A   2     -43.435  13.050 -29.032  1.00  0.00           H  \n",
            "HETATM   32  H32 TNS A   2     -39.110  17.591 -32.569  1.00  0.00           H  \n",
            "HETATM   33  H33 TNS A   2     -33.082  21.500 -34.836  1.00  0.00           H  \n",
            "HETATM   34  H34 TNS A   2     -25.110  24.687 -35.652  1.00  0.00           H  \n",
            "HETATM   35  H35 TNS A   2     -14.484  26.889 -34.487  1.00  0.00           H  \n",
            "HETATM   36  H36 TNS A   2       1.383  27.145 -29.411  1.00  0.00           H  \n",
            "HETATM   37  H37 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM   38  H38 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM   39  H39 TNS A   2     -38.271  -8.800   7.855  1.00  0.00           H  \n",
            "HETATM   40  H40 TNS A   2     -45.951   3.167  -0.830  1.00  0.00           H  \n",
            "HETATM   41  H41 TNS A   2     -48.179  11.761  -7.177  1.00  0.00           H  \n",
            "HETATM   42  H42 TNS A   2     -47.646  18.648 -12.340  1.00  0.00           H  \n",
            "HETATM   43  H43 TNS A   2     -45.092  24.284 -16.637  1.00  0.00           H  \n",
            "HETATM   44  H44 TNS A   2     -40.767  28.825 -20.174  1.00  0.00           H  \n",
            "HETATM   45  H45 TNS A   2     -34.670  32.270 -22.952  1.00  0.00           H  \n",
            "HETATM   46  H46 TNS A   2     -26.552  34.465 -24.863  1.00  0.00           H  \n",
            "HETATM   47  H47 TNS A   2     -15.673  34.952 -25.591  1.00  0.00           H  \n",
            "HETATM   48  H48 TNS A   2       0.657  32.067 -23.981  1.00  0.00           H  \n",
            "HETATM   49  H49 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM   50  H50 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM   51  H51 TNS A   2     -37.156  -5.018  14.074  1.00  0.00           H  \n",
            "HETATM   52  H52 TNS A   2     -44.124   9.364   9.360  1.00  0.00           H  \n",
            "HETATM   53  H53 TNS A   2     -45.963  19.276   5.180  1.00  0.00           H  \n",
            "HETATM   54  H54 TNS A   2     -45.206  26.926   1.271  1.00  0.00           H  \n",
            "HETATM   55  H55 TNS A   2     -42.546  32.919  -2.440  1.00  0.00           H  \n",
            "HETATM   56  H56 TNS A   2     -38.221  37.460  -5.977  1.00  0.00           H  \n",
            "HETATM   57  H57 TNS A   2     -32.230  40.549  -9.341  1.00  0.00           H  \n",
            "HETATM   58  H58 TNS A   2     -24.336  41.980 -12.507  1.00  0.00           H  \n",
            "HETATM   59  H59 TNS A   2     -13.846  41.149 -15.401  1.00  0.00           H  \n",
            "HETATM   60  H60 TNS A   2       1.772  35.849 -17.762  1.00  0.00           H  \n",
            "HETATM   61  H61 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM   62  H62 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM   63  H63 TNS A   2     -34.309  -2.744  20.474  1.00  0.00           H  \n",
            "HETATM   64  H64 TNS A   2     -39.459  13.089  19.845  1.00  0.00           H  \n",
            "HETATM   65  H65 TNS A   2     -40.307  23.794  17.895  1.00  0.00           H  \n",
            "HETATM   66  H66 TNS A   2     -38.975  31.902  15.277  1.00  0.00           H  \n",
            "HETATM   67  H67 TNS A   2     -36.048  38.109  12.169  1.00  0.00           H  \n",
            "HETATM   68  H68 TNS A   2     -31.722  42.650   8.631  1.00  0.00           H  \n",
            "HETATM   69  H69 TNS A   2     -25.999  45.525   4.665  1.00  0.00           H  \n",
            "HETATM   70  H70 TNS A   2     -18.680  46.498   0.209  1.00  0.00           H  \n",
            "HETATM   71  H71 TNS A   2      -9.182  44.875  -4.916  1.00  0.00           H  \n",
            "HETATM   72  H72 TNS A   2       4.619  38.123 -11.362  1.00  0.00           H  \n",
            "HETATM   73  H73 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM   74  H74 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM   75  H75 TNS A   2     -30.009  -2.202  26.428  1.00  0.00           H  \n",
            "HETATM   76  H76 TNS A   2     -32.414  13.977  29.600  1.00  0.00           H  \n",
            "HETATM   77  H77 TNS A   2     -31.763  24.871  29.724  1.00  0.00           H  \n",
            "HETATM   78  H78 TNS A   2     -29.565  33.089  28.307  1.00  0.00           H  \n",
            "HETATM   79  H79 TNS A   2     -26.232  39.346  25.759  1.00  0.00           H  \n",
            "HETATM   80  H80 TNS A   2     -21.907  43.887  22.222  1.00  0.00           H  \n",
            "HETATM   81  H81 TNS A   2     -16.589  46.711  17.695  1.00  0.00           H  \n",
            "HETATM   82  H82 TNS A   2     -10.136  47.575  12.038  1.00  0.00           H  \n",
            "HETATM   83  H83 TNS A   2      -2.137  45.763   4.838  1.00  0.00           H  \n",
            "HETATM   84  H84 TNS A   2       8.920  38.665  -5.408  1.00  0.00           H  \n",
            "HETATM   85  H85 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM   86  H86 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM   87  H87 TNS A   2     -24.676  -3.444  31.353  1.00  0.00           H  \n",
            "HETATM   88  H88 TNS A   2     -23.678  11.942  37.669  1.00  0.00           H  \n",
            "HETATM   89  H89 TNS A   2     -21.169  22.402  39.510  1.00  0.00           H  \n",
            "HETATM   90  H90 TNS A   2     -17.895  30.369  39.085  1.00  0.00           H  \n",
            "HETATM   91  H91 TNS A   2     -14.061  36.510  37.002  1.00  0.00           H  \n",
            "HETATM   92  H92 TNS A   2      -9.735  41.051  33.464  1.00  0.00           H  \n",
            "HETATM   93  H93 TNS A   2      -4.919  43.992  28.473  1.00  0.00           H  \n",
            "HETATM   94  H94 TNS A   2       0.458  45.106  21.823  1.00  0.00           H  \n",
            "HETATM   95  H95 TNS A   2       6.599  43.727  12.907  1.00  0.00           H  \n",
            "HETATM   96  H96 TNS A   2      14.252  37.423  -0.483  1.00  0.00           H  \n",
            "HETATM   97  H97 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM   98  H98 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM   99  H99 TNS A   2     -18.834  -6.350  34.767  1.00  0.00           H  \n",
            "HETATM  100 H100 TNS A   2     -14.106   7.181  43.262  1.00  0.00           H  \n",
            "HETATM  101 H101 TNS A   2      -9.561  16.629  46.293  1.00  0.00           H  \n",
            "HETATM  102 H102 TNS A   2      -5.109  24.011  46.557  1.00  0.00           H  \n",
            "HETATM  103 H103 TNS A   2      -0.724  29.878  44.795  1.00  0.00           H  \n",
            "HETATM  104 H104 TNS A   2       3.601  34.418  41.258  1.00  0.00           H  \n",
            "HETATM  105 H105 TNS A   2       7.867  37.633  35.945  1.00  0.00           H  \n",
            "HETATM  106 H106 TNS A   2      12.065  39.333  28.606  1.00  0.00           H  \n",
            "HETATM  107 H107 TNS A   2      16.171  38.967  18.501  1.00  0.00           H  \n",
            "HETATM  108 H108 TNS A   2      20.094  34.517   2.931  1.00  0.00           H  \n",
            "HETATM  109 H109 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM  110 H110 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM  111 H111 TNS A   2     -13.053 -10.634  36.336  1.00  0.00           H  \n",
            "HETATM  112 H112 TNS A   2      -4.635   0.162  45.833  1.00  0.00           H  \n",
            "HETATM  113 H113 TNS A   2       1.924   8.118  49.411  1.00  0.00           H  \n",
            "HETATM  114 H114 TNS A   2       7.542  14.635  49.991  1.00  0.00           H  \n",
            "HETATM  115 H115 TNS A   2      12.471  20.098  48.377  1.00  0.00           H  \n",
            "HETATM  116 H116 TNS A   2      16.797  24.639  44.840  1.00  0.00           H  \n",
            "HETATM  117 H117 TNS A   2      20.518  28.257  39.379  1.00  0.00           H  \n",
            "HETATM  118 H118 TNS A   2      23.551  30.821  31.724  1.00  0.00           H  \n",
            "HETATM  119 H119 TNS A   2      25.642  31.948  21.072  1.00  0.00           H  \n",
            "HETATM  120 H120 TNS A   2      25.875  30.233   4.500  1.00  0.00           H  \n",
            "HETATM  121 H121 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM  122 H122 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM  123 H123 TNS A   2      -7.900 -15.877  35.907  1.00  0.00           H  \n",
            "HETATM  124 H124 TNS A   2       3.807  -8.428  45.129  1.00  0.00           H  \n",
            "HETATM  125 H125 TNS A   2      12.162  -2.300  48.557  1.00  0.00           H  \n",
            "HETATM  126 H126 TNS A   2      18.820   3.160  49.051  1.00  0.00           H  \n",
            "HETATM  127 H127 TNS A   2      24.234   8.130  47.396  1.00  0.00           H  \n",
            "HETATM  128 H128 TNS A   2      28.560  12.670  43.859  1.00  0.00           H  \n",
            "HETATM  129 H129 TNS A   2      31.796  16.782  38.439  1.00  0.00           H  \n",
            "HETATM  130 H130 TNS A   2      33.789  20.404  30.870  1.00  0.00           H  \n",
            "HETATM  131 H131 TNS A   2      34.085  23.357  20.368  1.00  0.00           H  \n",
            "HETATM  132 H132 TNS A   2      31.028  24.990   4.071  1.00  0.00           H  \n",
            "HETATM  133 H133 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM  134 H134 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM  135 H135 TNS A   2      -3.879 -21.567  33.521  1.00  0.00           H  \n",
            "HETATM  136 H136 TNS A   2      10.396 -17.749  41.220  1.00  0.00           H  \n",
            "HETATM  137 H137 TNS A   2      20.152 -13.604  43.816  1.00  0.00           H  \n",
            "HETATM  138 H138 TNS A   2      27.620  -9.291  43.829  1.00  0.00           H  \n",
            "HETATM  139 H139 TNS A   2      33.413  -4.857  41.949  1.00  0.00           H  \n",
            "HETATM  140 H140 TNS A   2      37.739  -0.317  38.412  1.00  0.00           H  \n",
            "HETATM  141 H141 TNS A   2      40.596   4.331  33.217  1.00  0.00           H  \n",
            "HETATM  142 H142 TNS A   2      41.778   9.100  26.129  1.00  0.00           H  \n",
            "HETATM  143 H143 TNS A   2      40.673  14.036  16.459  1.00  0.00           H  \n",
            "HETATM  144 H144 TNS A   2      35.049  19.300   1.685  1.00  0.00           H  \n",
            "HETATM  145 H145 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM  146 H146 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM  147 H147 TNS A   2      -1.383 -27.145  29.411  1.00  0.00           H  \n",
            "HETATM  148 H148 TNS A   2      14.484 -26.889  34.487  1.00  0.00           H  \n",
            "HETATM  149 H149 TNS A   2      25.110 -24.687  35.652  1.00  0.00           H  \n",
            "HETATM  150 H150 TNS A   2      33.082 -21.500  34.836  1.00  0.00           H  \n",
            "HETATM  151 H151 TNS A   2      39.110 -17.591  32.569  1.00  0.00           H  \n",
            "HETATM  152 H152 TNS A   2      43.435 -13.050  29.032  1.00  0.00           H  \n",
            "HETATM  153 H153 TNS A   2      46.058  -7.877  24.224  1.00  0.00           H  \n",
            "HETATM  154 H154 TNS A   2      46.737  -1.983  17.965  1.00  0.00           H  \n",
            "HETATM  155 H155 TNS A   2      44.762   4.897   9.726  1.00  0.00           H  \n",
            "HETATM  156 H156 TNS A   2      37.545  13.722  -2.425  1.00  0.00           H  \n",
            "HETATM  157 H157 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM  158 H158 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM  159 H159 TNS A   2      -0.657 -32.067  23.981  1.00  0.00           H  \n",
            "HETATM  160 H160 TNS A   2      15.673 -34.952  25.591  1.00  0.00           H  \n",
            "HETATM  161 H161 TNS A   2      26.552 -34.465  24.863  1.00  0.00           H  \n",
            "HETATM  162 H162 TNS A   2      34.670 -32.270  22.952  1.00  0.00           H  \n",
            "HETATM  163 H163 TNS A   2      40.767 -28.825  20.174  1.00  0.00           H  \n",
            "HETATM  164 H164 TNS A   2      45.092 -24.284  16.637  1.00  0.00           H  \n",
            "HETATM  165 H165 TNS A   2      47.646 -18.648  12.340  1.00  0.00           H  \n",
            "HETATM  166 H166 TNS A   2      48.179 -11.761   7.177  1.00  0.00           H  \n",
            "HETATM  167 H167 TNS A   2      45.951  -3.167   0.830  1.00  0.00           H  \n",
            "HETATM  168 H168 TNS A   2      38.271   8.800  -7.855  1.00  0.00           H  \n",
            "HETATM  169 H169 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM  170 H170 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM  171 H171 TNS A   2      -1.772 -35.849  17.762  1.00  0.00           H  \n",
            "HETATM  172 H172 TNS A   2      13.846 -41.149  15.401  1.00  0.00           H  \n",
            "HETATM  173 H173 TNS A   2      24.336 -41.980  12.507  1.00  0.00           H  \n",
            "HETATM  174 H174 TNS A   2      32.230 -40.549   9.341  1.00  0.00           H  \n",
            "HETATM  175 H175 TNS A   2      38.221 -37.460   5.977  1.00  0.00           H  \n",
            "HETATM  176 H176 TNS A   2      42.546 -32.919   2.440  1.00  0.00           H  \n",
            "HETATM  177 H177 TNS A   2      45.206 -26.926  -1.271  1.00  0.00           H  \n",
            "HETATM  178 H178 TNS A   2      45.963 -19.276  -5.180  1.00  0.00           H  \n",
            "HETATM  179 H179 TNS A   2      44.124  -9.364  -9.360  1.00  0.00           H  \n",
            "HETATM  180 H180 TNS A   2      37.156   5.018 -14.074  1.00  0.00           H  \n",
            "HETATM  181 H181 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM  182 H182 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM  183 H183 TNS A   2      -4.619 -38.123  11.362  1.00  0.00           H  \n",
            "HETATM  184 H184 TNS A   2       9.182 -44.875   4.916  1.00  0.00           H  \n",
            "HETATM  185 H185 TNS A   2      18.680 -46.498  -0.209  1.00  0.00           H  \n",
            "HETATM  186 H186 TNS A   2      25.999 -45.525  -4.665  1.00  0.00           H  \n",
            "HETATM  187 H187 TNS A   2      31.722 -42.650  -8.631  1.00  0.00           H  \n",
            "HETATM  188 H188 TNS A   2      36.048 -38.109 -12.169  1.00  0.00           H  \n",
            "HETATM  189 H189 TNS A   2      38.975 -31.902 -15.277  1.00  0.00           H  \n",
            "HETATM  190 H190 TNS A   2      40.307 -23.794 -17.895  1.00  0.00           H  \n",
            "HETATM  191 H191 TNS A   2      39.459 -13.089 -19.845  1.00  0.00           H  \n",
            "HETATM  192 H192 TNS A   2      34.309   2.744 -20.474  1.00  0.00           H  \n",
            "HETATM  193 H193 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM  194 H194 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM  195 H195 TNS A   2      -8.920 -38.665   5.408  1.00  0.00           H  \n",
            "HETATM  196 H196 TNS A   2       2.137 -45.763  -4.838  1.00  0.00           H  \n",
            "HETATM  197 H197 TNS A   2      10.136 -47.575 -12.038  1.00  0.00           H  \n",
            "HETATM  198 H198 TNS A   2      16.589 -46.711 -17.695  1.00  0.00           H  \n",
            "HETATM  199 H199 TNS A   2      21.907 -43.887 -22.222  1.00  0.00           H  \n",
            "HETATM  200 H200 TNS A   2      26.232 -39.346 -25.759  1.00  0.00           H  \n",
            "HETATM  201 H201 TNS A   2      29.565 -33.089 -28.307  1.00  0.00           H  \n",
            "HETATM  202 H202 TNS A   2      31.763 -24.871 -29.724  1.00  0.00           H  \n",
            "HETATM  203 H203 TNS A   2      32.414 -13.977 -29.600  1.00  0.00           H  \n",
            "HETATM  204 H204 TNS A   2      30.009   2.202 -26.428  1.00  0.00           H  \n",
            "HETATM  205 H205 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM  206 H206 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM  207 H207 TNS A   2     -14.252 -37.423   0.483  1.00  0.00           H  \n",
            "HETATM  208 H208 TNS A   2      -6.599 -43.727 -12.907  1.00  0.00           H  \n",
            "HETATM  209 H209 TNS A   2      -0.458 -45.106 -21.823  1.00  0.00           H  \n",
            "HETATM  210 H210 TNS A   2       4.919 -43.992 -28.473  1.00  0.00           H  \n",
            "HETATM  211 H211 TNS A   2       9.735 -41.051 -33.464  1.00  0.00           H  \n",
            "HETATM  212 H212 TNS A   2      14.061 -36.510 -37.002  1.00  0.00           H  \n",
            "HETATM  213 H213 TNS A   2      17.895 -30.369 -39.085  1.00  0.00           H  \n",
            "HETATM  214 H214 TNS A   2      21.169 -22.402 -39.510  1.00  0.00           H  \n",
            "HETATM  215 H215 TNS A   2      23.678 -11.942 -37.669  1.00  0.00           H  \n",
            "HETATM  216 H216 TNS A   2      24.676   3.444 -31.353  1.00  0.00           H  \n",
            "HETATM  217 H217 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM  218 H218 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM  219 H219 TNS A   2     -20.094 -34.517  -2.931  1.00  0.00           H  \n",
            "HETATM  220 H220 TNS A   2     -16.171 -38.967 -18.501  1.00  0.00           H  \n",
            "HETATM  221 H221 TNS A   2     -12.065 -39.333 -28.606  1.00  0.00           H  \n",
            "HETATM  222 H222 TNS A   2      -7.867 -37.633 -35.945  1.00  0.00           H  \n",
            "HETATM  223 H223 TNS A   2      -3.601 -34.418 -41.258  1.00  0.00           H  \n",
            "HETATM  224 H224 TNS A   2       0.724 -29.878 -44.795  1.00  0.00           H  \n",
            "HETATM  225 H225 TNS A   2       5.109 -24.011 -46.557  1.00  0.00           H  \n",
            "HETATM  226 H226 TNS A   2       9.561 -16.629 -46.293  1.00  0.00           H  \n",
            "HETATM  227 H227 TNS A   2      14.106  -7.181 -43.262  1.00  0.00           H  \n",
            "HETATM  228 H228 TNS A   2      18.834   6.350 -34.767  1.00  0.00           H  \n",
            "HETATM  229 H229 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM  230 H230 TNS A   2     -21.627 -22.704  17.687  1.00  0.00           H  \n",
            "HETATM  231 H231 TNS A   2     -25.875 -30.233  -4.500  1.00  0.00           H  \n",
            "HETATM  232 H232 TNS A   2     -25.642 -31.948 -21.072  1.00  0.00           H  \n",
            "HETATM  233 H233 TNS A   2     -23.551 -30.821 -31.724  1.00  0.00           H  \n",
            "HETATM  234 H234 TNS A   2     -20.518 -28.257 -39.379  1.00  0.00           H  \n",
            "HETATM  235 H235 TNS A   2     -16.797 -24.639 -44.840  1.00  0.00           H  \n",
            "HETATM  236 H236 TNS A   2     -12.471 -20.098 -48.377  1.00  0.00           H  \n",
            "HETATM  237 H237 TNS A   2      -7.542 -14.635 -49.991  1.00  0.00           H  \n",
            "HETATM  238 H238 TNS A   2      -1.924  -8.118 -49.411  1.00  0.00           H  \n",
            "HETATM  239 H239 TNS A   2       4.635  -0.162 -45.833  1.00  0.00           H  \n",
            "HETATM  240 H240 TNS A   2      13.053  10.634 -36.336  1.00  0.00           H  \n",
            "HETATM  241 H241 TNS A   2      21.627  22.704 -17.687  1.00  0.00           H  \n",
            "HETATM  242    R AXS A   3      -0.000   0.000   0.000  1.00  0.00           C  \n",
            "HETATM  243 Dpar AXS A   3      21.627  22.704 -17.687  1.00  0.00           C  \n",
            "HETATM  244 Dpar AXS A   3     -21.627 -22.704  17.687  1.00  0.00           C  \n",
            "HETATM  245 Dpar AXS A   3      23.789  24.974 -19.455  1.00  0.00           N  \n",
            "HETATM  246 Dpar AXS A   3     -23.789 -24.974  19.455  1.00  0.00           N  \n",
            "CONECT    2    3   14  230                                                      \n",
            "CONECT    3    2    4   15  231                                                 \n",
            "CONECT    4    3    5   16  232                                                 \n",
            "CONECT    5    4    6   17  233                                                 \n",
            "CONECT    6    5    7   18  234                                                 \n",
            "CONECT    7    6    8   19  235                                                 \n",
            "CONECT    8    7    9   20  236                                                 \n",
            "CONECT    9    8   10   21  237                                                 \n",
            "CONECT   10    9   11   22  238                                                 \n",
            "CONECT   11   10   12   23  239                                                 \n",
            "CONECT   12   11   13   24  240                                                 \n",
            "CONECT   13   12   25  241                                                      \n",
            "CONECT   14    2   15   26                                                      \n",
            "CONECT   15   14    3   16   27                                                 \n",
            "CONECT   16   15    4   17   28                                                 \n",
            "CONECT   17   16    5   18   29                                                 \n",
            "CONECT   18   17    6   19   30                                                 \n",
            "CONECT   19   18    7   20   31                                                 \n",
            "CONECT   20   19    8   21   32                                                 \n",
            "CONECT   21   20    9   22   33                                                 \n",
            "CONECT   22   21   10   23   34                                                 \n",
            "CONECT   23   22   11   24   35                                                 \n",
            "CONECT   24   23   12   25   36                                                 \n",
            "CONECT   25   24   13   37                                                      \n",
            "CONECT   26   14   27   38                                                      \n",
            "CONECT   27   26   15   28   39                                                 \n",
            "CONECT   28   27   16   29   40                                                 \n",
            "CONECT   29   28   17   30   41                                                 \n",
            "CONECT   30   29   18   31   42                                                 \n",
            "CONECT   31   30   19   32   43                                                 \n",
            "CONECT   32   31   20   33   44                                                 \n",
            "CONECT   33   32   21   34   45                                                 \n",
            "CONECT   34   33   22   35   46                                                 \n",
            "CONECT   35   34   23   36   47                                                 \n",
            "CONECT   36   35   24   37   48                                                 \n",
            "CONECT   37   36   25   49                                                      \n",
            "CONECT   38   26   39   50                                                      \n",
            "CONECT   39   38   27   40   51                                                 \n",
            "CONECT   40   39   28   41   52                                                 \n",
            "CONECT   41   40   29   42   53                                                 \n",
            "CONECT   42   41   30   43   54                                                 \n",
            "CONECT   43   42   31   44   55                                                 \n",
            "CONECT   44   43   32   45   56                                                 \n",
            "CONECT   45   44   33   46   57                                                 \n",
            "CONECT   46   45   34   47   58                                                 \n",
            "CONECT   47   46   35   48   59                                                 \n",
            "CONECT   48   47   36   49   60                                                 \n",
            "CONECT   49   48   37   61                                                      \n",
            "CONECT   50   38   51   62                                                      \n",
            "CONECT   51   50   39   52   63                                                 \n",
            "CONECT   52   51   40   53   64                                                 \n",
            "CONECT   53   52   41   54   65                                                 \n",
            "CONECT   54   53   42   55   66                                                 \n",
            "CONECT   55   54   43   56   67                                                 \n",
            "CONECT   56   55   44   57   68                                                 \n",
            "CONECT   57   56   45   58   69                                                 \n",
            "CONECT   58   57   46   59   70                                                 \n",
            "CONECT   59   58   47   60   71                                                 \n",
            "CONECT   60   59   48   61   72                                                 \n",
            "CONECT   61   60   49   73                                                      \n",
            "CONECT   62   50   63   74                                                      \n",
            "CONECT   63   62   51   64   75                                                 \n",
            "CONECT   64   63   52   65   76                                                 \n",
            "CONECT   65   64   53   66   77                                                 \n",
            "CONECT   66   65   54   67   78                                                 \n",
            "CONECT   67   66   55   68   79                                                 \n",
            "CONECT   68   67   56   69   80                                                 \n",
            "CONECT   69   68   57   70   81                                                 \n",
            "CONECT   70   69   58   71   82                                                 \n",
            "CONECT   71   70   59   72   83                                                 \n",
            "CONECT   72   71   60   73   84                                                 \n",
            "CONECT   73   72   61   85                                                      \n",
            "CONECT   74   62   75   86                                                      \n",
            "CONECT   75   74   63   76   87                                                 \n",
            "CONECT   76   75   64   77   88                                                 \n",
            "CONECT   77   76   65   78   89                                                 \n",
            "CONECT   78   77   66   79   90                                                 \n",
            "CONECT   79   78   67   80   91                                                 \n",
            "CONECT   80   79   68   81   92                                                 \n",
            "CONECT   81   80   69   82   93                                                 \n",
            "CONECT   82   81   70   83   94                                                 \n",
            "CONECT   83   82   71   84   95                                                 \n",
            "CONECT   84   83   72   85   96                                                 \n",
            "CONECT   85   84   73   97                                                      \n",
            "CONECT   86   74   87   98                                                      \n",
            "CONECT   87   86   75   88   99                                                 \n",
            "CONECT   88   87   76   89  100                                                 \n",
            "CONECT   89   88   77   90  101                                                 \n",
            "CONECT   90   89   78   91  102                                                 \n",
            "CONECT   91   90   79   92  103                                                 \n",
            "CONECT   92   91   80   93  104                                                 \n",
            "CONECT   93   92   81   94  105                                                 \n",
            "CONECT   94   93   82   95  106                                                 \n",
            "CONECT   95   94   83   96  107                                                 \n",
            "CONECT   96   95   84   97  108                                                 \n",
            "CONECT   97   96   85  109                                                      \n",
            "CONECT   98   86   99  110                                                      \n",
            "CONECT   99   98   87  100  111                                                 \n",
            "CONECT  100   99   88  101  112                                                 \n",
            "CONECT  101  100   89  102  113                                                 \n",
            "CONECT  102  101   90  103  114                                                 \n",
            "CONECT  103  102   91  104  115                                                 \n",
            "CONECT  104  103   92  105  116                                                 \n",
            "CONECT  105  104   93  106  117                                                 \n",
            "CONECT  106  105   94  107  118                                                 \n",
            "CONECT  107  106   95  108  119                                                 \n",
            "CONECT  108  107   96  109  120                                                 \n",
            "CONECT  109  108   97  121                                                      \n",
            "CONECT  110   98  111  122                                                      \n",
            "CONECT  111  110   99  112  123                                                 \n",
            "CONECT  112  111  100  113  124                                                 \n",
            "CONECT  113  112  101  114  125                                                 \n",
            "CONECT  114  113  102  115  126                                                 \n",
            "CONECT  115  114  103  116  127                                                 \n",
            "CONECT  116  115  104  117  128                                                 \n",
            "CONECT  117  116  105  118  129                                                 \n",
            "CONECT  118  117  106  119  130                                                 \n",
            "CONECT  119  118  107  120  131                                                 \n",
            "CONECT  120  119  108  121  132                                                 \n",
            "CONECT  121  120  109  133                                                      \n",
            "CONECT  122  110  123  134                                                      \n",
            "CONECT  123  122  111  124  135                                                 \n",
            "CONECT  124  123  112  125  136                                                 \n",
            "CONECT  125  124  113  126  137                                                 \n",
            "CONECT  126  125  114  127  138                                                 \n",
            "CONECT  127  126  115  128  139                                                 \n",
            "CONECT  128  127  116  129  140                                                 \n",
            "CONECT  129  128  117  130  141                                                 \n",
            "CONECT  130  129  118  131  142                                                 \n",
            "CONECT  131  130  119  132  143                                                 \n",
            "CONECT  132  131  120  133  144                                                 \n",
            "CONECT  133  132  121  145                                                      \n",
            "CONECT  134  122  135  146                                                      \n",
            "CONECT  135  134  123  136  147                                                 \n",
            "CONECT  136  135  124  137  148                                                 \n",
            "CONECT  137  136  125  138  149                                                 \n",
            "CONECT  138  137  126  139  150                                                 \n",
            "CONECT  139  138  127  140  151                                                 \n",
            "CONECT  140  139  128  141  152                                                 \n",
            "CONECT  141  140  129  142  153                                                 \n",
            "CONECT  142  141  130  143  154                                                 \n",
            "CONECT  143  142  131  144  155                                                 \n",
            "CONECT  144  143  132  145  156                                                 \n",
            "CONECT  145  144  133  157                                                      \n",
            "CONECT  146  134  147  158                                                      \n",
            "CONECT  147  146  135  148  159                                                 \n",
            "CONECT  148  147  136  149  160                                                 \n",
            "CONECT  149  148  137  150  161                                                 \n",
            "CONECT  150  149  138  151  162                                                 \n",
            "CONECT  151  150  139  152  163                                                 \n",
            "CONECT  152  151  140  153  164                                                 \n",
            "CONECT  153  152  141  154  165                                                 \n",
            "CONECT  154  153  142  155  166                                                 \n",
            "CONECT  155  154  143  156  167                                                 \n",
            "CONECT  156  155  144  157  168                                                 \n",
            "CONECT  157  156  145  169                                                      \n",
            "CONECT  158  146  159  170                                                      \n",
            "CONECT  159  158  147  160  171                                                 \n",
            "CONECT  160  159  148  161  172                                                 \n",
            "CONECT  161  160  149  162  173                                                 \n",
            "CONECT  162  161  150  163  174                                                 \n",
            "CONECT  163  162  151  164  175                                                 \n",
            "CONECT  164  163  152  165  176                                                 \n",
            "CONECT  165  164  153  166  177                                                 \n",
            "CONECT  166  165  154  167  178                                                 \n",
            "CONECT  167  166  155  168  179                                                 \n",
            "CONECT  168  167  156  169  180                                                 \n",
            "CONECT  169  168  157  181                                                      \n",
            "CONECT  170  158  171  182                                                      \n",
            "CONECT  171  170  159  172  183                                                 \n",
            "CONECT  172  171  160  173  184                                                 \n",
            "CONECT  173  172  161  174  185                                                 \n",
            "CONECT  174  173  162  175  186                                                 \n",
            "CONECT  175  174  163  176  187                                                 \n",
            "CONECT  176  175  164  177  188                                                 \n",
            "CONECT  177  176  165  178  189                                                 \n",
            "CONECT  178  177  166  179  190                                                 \n",
            "CONECT  179  178  167  180  191                                                 \n",
            "CONECT  180  179  168  181  192                                                 \n",
            "CONECT  181  180  169  193                                                      \n",
            "CONECT  182  170  183  194                                                      \n",
            "CONECT  183  182  171  184  195                                                 \n",
            "CONECT  184  183  172  185  196                                                 \n",
            "CONECT  185  184  173  186  197                                                 \n",
            "CONECT  186  185  174  187  198                                                 \n",
            "CONECT  187  186  175  188  199                                                 \n",
            "CONECT  188  187  176  189  200                                                 \n",
            "CONECT  189  188  177  190  201                                                 \n",
            "CONECT  190  189  178  191  202                                                 \n",
            "CONECT  191  190  179  192  203                                                 \n",
            "CONECT  192  191  180  193  204                                                 \n",
            "CONECT  193  192  181  205                                                      \n",
            "CONECT  194  182  195  206                                                      \n",
            "CONECT  195  194  183  196  207                                                 \n",
            "CONECT  196  195  184  197  208                                                 \n",
            "CONECT  197  196  185  198  209                                                 \n",
            "CONECT  198  197  186  199  210                                                 \n",
            "CONECT  199  198  187  200  211                                                 \n",
            "CONECT  200  199  188  201  212                                                 \n",
            "CONECT  201  200  189  202  213                                                 \n",
            "CONECT  202  201  190  203  214                                                 \n",
            "CONECT  203  202  191  204  215                                                 \n",
            "CONECT  204  203  192  205  216                                                 \n",
            "CONECT  205  204  193  217                                                      \n",
            "CONECT  206  194  207  218                                                      \n",
            "CONECT  207  206  195  208  219                                                 \n",
            "CONECT  208  207  196  209  220                                                 \n",
            "CONECT  209  208  197  210  221                                                 \n",
            "CONECT  210  209  198  211  222                                                 \n",
            "CONECT  211  210  199  212  223                                                 \n",
            "CONECT  212  211  200  213  224                                                 \n",
            "CONECT  213  212  201  214  225                                                 \n",
            "CONECT  214  213  202  215  226                                                 \n",
            "CONECT  215  214  203  216  227                                                 \n",
            "CONECT  216  215  204  217  228                                                 \n",
            "CONECT  217  216  205  229                                                      \n",
            "CONECT  218  206  219  230                                                      \n",
            "CONECT  219  218  207  220  231                                                 \n",
            "CONECT  220  219  208  221  232                                                 \n",
            "CONECT  221  220  209  222  233                                                 \n",
            "CONECT  222  221  210  223  234                                                 \n",
            "CONECT  223  222  211  224  235                                                 \n",
            "CONECT  224  223  212  225  236                                                 \n",
            "CONECT  225  224  213  226  237                                                 \n",
            "CONECT  226  225  214  227  238                                                 \n",
            "CONECT  227  226  215  228  239                                                 \n",
            "CONECT  228  227  216  229  240                                                 \n",
            "CONECT  229  228  217  241                                                      \n",
            "CONECT  230  218    2  231                                                      \n",
            "CONECT  231  230  219    3  232                                                 \n",
            "CONECT  232  231  220    4  233                                                 \n",
            "CONECT  233  232  221    5  234                                                 \n",
            "CONECT  234  233  222    6  235                                                 \n",
            "CONECT  235  234  223    7  236                                                 \n",
            "CONECT  236  235  224    8  237                                                 \n",
            "CONECT  237  236  225    9  238                                                 \n",
            "CONECT  238  237  226   10  239                                                 \n",
            "CONECT  239  238  227   11  240                                                 \n",
            "CONECT  240  239  228   12  241                                                 \n",
            "CONECT  241  240  229   13                                                      \n",
            "CONECT  242  243  244                                                           \n",
            "CONECT  243  242                                                                \n",
            "CONECT  244  242                                                                \n",
            "MASTER        0    0    3    0    0    0    0    0  246    0  243    0          \n",
            "END                                                                             \n"
        ]

        # Check the data.
        self.strip_remarks(lines)
        self.assertEqual(len(real_data), len(lines))
        for i in range(len(lines)):
            self.assertEqual(real_data[i], lines[i])


    def test_create_diff_tensor_pdb_prolate(self):
        """Check the 3D coordinates of the PDB representation of the optimised prolate diffusion tensor."""

        # Reset relax.
        self.interpreter.reset()

        # Create a temporary file.
        ds.tmpfile_handle, ds.tmpfile = mkstemp(suffix='.pdb')

        # The diffusion type (used by the script).
        ds.diff_dir = 'spheroid_prolate'
        ds.diff_type = 'prolate'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'diff_tensor'+sep+'tensor_opt.py')

        # Create the PDB representation.
        self.interpreter.structure.create_diff_tensor_pdb(scale=1.8e-06, file=ds.tmpfile, force=True)

        # Read the contents of the file.
        file = open(ds.tmpfile)
        lines = file.readlines()
        file.close()

        # What the contents should be, without remarks.
        real_data = [
            "HET    COM  A   1       1                                                       \n",
            "HET    TNS  A   2     240                                                       \n",
            "HET    AXS  A   3       5                                                       \n",
            "HETNAM     COM CENTRE OF MASS                                                   \n",
            "HETNAM     TNS TENSOR                                                           \n",
            "HETNAM     AXS TENSOR AXES                                                      \n",
            "FORMUL   1  COM    C1                                                           \n",
            "FORMUL   2  TNS    H240                                                         \n",
            "FORMUL   3  AXS    C3N2                                                         \n",
            "HETATM    1    R COM A   1      -0.000   0.000   0.000  1.00  0.00           C  \n",
            "HETATM    2   H2 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM    3   H3 TNS A   2      48.132 -10.602  13.384  1.00  0.00           H  \n",
            "HETATM    4   H4 TNS A   2      45.482   0.862   4.523  1.00  0.00           H  \n",
            "HETATM    5   H5 TNS A   2      40.121   9.258  -2.355  1.00  0.00           H  \n",
            "HETATM    6   H6 TNS A   2      33.389  16.101  -8.229  1.00  0.00           H  \n",
            "HETATM    7   H7 TNS A   2      25.651  21.806 -13.368  1.00  0.00           H  \n",
            "HETATM    8   H8 TNS A   2      17.033  26.514 -17.862  1.00  0.00           H  \n",
            "HETATM    9   H9 TNS A   2       7.534  30.226 -21.713  1.00  0.00           H  \n",
            "HETATM   10  H10 TNS A   2      -2.970  32.799 -24.827  1.00  0.00           H  \n",
            "HETATM   11  H11 TNS A   2     -14.846  33.819 -26.938  1.00  0.00           H  \n",
            "HETATM   12  H12 TNS A   2     -29.432  31.771 -27.066  1.00  0.00           H  \n",
            "HETATM   13  H13 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   14  H14 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   15  H15 TNS A   2      48.114 -14.010   9.849  1.00  0.00           H  \n",
            "HETATM   16  H16 TNS A   2      45.452  -4.720  -1.268  1.00  0.00           H  \n",
            "HETATM   17  H17 TNS A   2      40.086   2.489  -9.378  1.00  0.00           H  \n",
            "HETATM   18  H18 TNS A   2      33.349   8.645 -15.965  1.00  0.00           H  \n",
            "HETATM   19  H19 TNS A   2      25.610  14.029 -21.436  1.00  0.00           H  \n",
            "HETATM   20  H20 TNS A   2      16.992  18.737 -25.931  1.00  0.00           H  \n",
            "HETATM   21  H21 TNS A   2       7.495  22.769 -29.448  1.00  0.00           H  \n",
            "HETATM   22  H22 TNS A   2      -3.005  26.030 -31.850  1.00  0.00           H  \n",
            "HETATM   23  H23 TNS A   2     -14.875  28.237 -32.729  1.00  0.00           H  \n",
            "HETATM   24  H24 TNS A   2     -29.450  28.364 -30.600  1.00  0.00           H  \n",
            "HETATM   25  H25 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   26  H26 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   27  H27 TNS A   2      47.182 -18.119   7.330  1.00  0.00           H  \n",
            "HETATM   28  H28 TNS A   2      43.926 -11.453  -5.396  1.00  0.00           H  \n",
            "HETATM   29  H29 TNS A   2      38.235  -5.676 -14.383  1.00  0.00           H  \n",
            "HETATM   30  H30 TNS A   2      31.311  -0.350 -21.478  1.00  0.00           H  \n",
            "HETATM   31  H31 TNS A   2      23.484   4.647 -27.187  1.00  0.00           H  \n",
            "HETATM   32  H32 TNS A   2      14.866   9.356 -31.681  1.00  0.00           H  \n",
            "HETATM   33  H33 TNS A   2       5.456  13.775 -34.961  1.00  0.00           H  \n",
            "HETATM   34  H34 TNS A   2      -4.856  17.864 -36.855  1.00  0.00           H  \n",
            "HETATM   35  H35 TNS A   2     -16.401  21.504 -36.856  1.00  0.00           H  \n",
            "HETATM   36  H36 TNS A   2     -30.382  24.254 -33.119  1.00  0.00           H  \n",
            "HETATM   37  H37 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   38  H38 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   39  H39 TNS A   2      45.428 -22.529   6.073  1.00  0.00           H  \n",
            "HETATM   40  H40 TNS A   2      41.053 -18.678  -7.455  1.00  0.00           H  \n",
            "HETATM   41  H41 TNS A   2      34.751 -14.438 -16.880  1.00  0.00           H  \n",
            "HETATM   42  H42 TNS A   2      27.473 -10.001 -24.229  1.00  0.00           H  \n",
            "HETATM   43  H43 TNS A   2      19.481  -5.419 -30.056  1.00  0.00           H  \n",
            "HETATM   44  H44 TNS A   2      10.862  -0.711 -34.550  1.00  0.00           H  \n",
            "HETATM   45  H45 TNS A   2       1.618   4.124 -37.712  1.00  0.00           H  \n",
            "HETATM   46  H46 TNS A   2      -8.341   9.103 -39.352  1.00  0.00           H  \n",
            "HETATM   47  H47 TNS A   2     -19.275  14.279 -38.915  1.00  0.00           H  \n",
            "HETATM   48  H48 TNS A   2     -32.136  19.844 -34.376  1.00  0.00           H  \n",
            "HETATM   49  H49 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   50  H50 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   51  H51 TNS A   2      43.024 -26.808   6.202  1.00  0.00           H  \n",
            "HETATM   52  H52 TNS A   2      37.114 -25.688  -7.244  1.00  0.00           H  \n",
            "HETATM   53  H53 TNS A   2      29.974 -22.939 -16.625  1.00  0.00           H  \n",
            "HETATM   54  H54 TNS A   2      22.211 -19.364 -23.948  1.00  0.00           H  \n",
            "HETATM   55  H55 TNS A   2      13.992 -15.186 -29.763  1.00  0.00           H  \n",
            "HETATM   56  H56 TNS A   2       5.374 -10.478 -34.257  1.00  0.00           H  \n",
            "HETATM   57  H57 TNS A   2      -3.644  -5.240 -37.431  1.00  0.00           H  \n",
            "HETATM   58  H58 TNS A   2     -13.117   0.602 -39.097  1.00  0.00           H  \n",
            "HETATM   59  H59 TNS A   2     -23.214   7.269 -38.705  1.00  0.00           H  \n",
            "HETATM   60  H60 TNS A   2     -34.540  15.565 -34.248  1.00  0.00           H  \n",
            "HETATM   61  H61 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   62  H62 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   63  H63 TNS A   2      40.204 -30.536   7.703  1.00  0.00           H  \n",
            "HETATM   64  H64 TNS A   2      32.494 -31.797  -4.785  1.00  0.00           H  \n",
            "HETATM   65  H65 TNS A   2      24.372 -30.346 -13.643  1.00  0.00           H  \n",
            "HETATM   66  H66 TNS A   2      16.040 -27.524 -20.663  1.00  0.00           H  \n",
            "HETATM   67  H67 TNS A   2       7.556 -23.696 -26.336  1.00  0.00           H  \n",
            "HETATM   68  H68 TNS A   2      -1.062 -18.988 -30.831  1.00  0.00           H  \n",
            "HETATM   69  H69 TNS A   2      -9.814 -13.399 -34.146  1.00  0.00           H  \n",
            "HETATM   70  H70 TNS A   2     -18.719  -6.806 -36.115  1.00  0.00           H  \n",
            "HETATM   71  H71 TNS A   2     -27.833   1.160 -36.246  1.00  0.00           H  \n",
            "HETATM   72  H72 TNS A   2     -37.360  11.837 -32.747  1.00  0.00           H  \n",
            "HETATM   73  H73 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   74  H74 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   75  H75 TNS A   2      37.246 -33.350  10.430  1.00  0.00           H  \n",
            "HETATM   76  H76 TNS A   2      27.647 -36.406  -0.318  1.00  0.00           H  \n",
            "HETATM   77  H77 TNS A   2      18.493 -35.935  -8.225  1.00  0.00           H  \n",
            "HETATM   78  H78 TNS A   2       9.565 -33.680 -14.695  1.00  0.00           H  \n",
            "HETATM   79  H79 TNS A   2       0.802 -30.118 -20.112  1.00  0.00           H  \n",
            "HETATM   80  H80 TNS A   2      -7.816 -25.409 -24.606  1.00  0.00           H  \n",
            "HETATM   81  H81 TNS A   2     -16.290 -19.556 -28.178  1.00  0.00           H  \n",
            "HETATM   82  H82 TNS A   2     -24.598 -12.395 -30.697  1.00  0.00           H  \n",
            "HETATM   83  H83 TNS A   2     -32.681  -3.448 -31.778  1.00  0.00           H  \n",
            "HETATM   84  H84 TNS A   2     -40.318   9.024 -30.020  1.00  0.00           H  \n",
            "HETATM   85  H85 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   86  H86 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   87  H87 TNS A   2      34.437 -34.972  14.115  1.00  0.00           H  \n",
            "HETATM   88  H88 TNS A   2      23.045 -39.064   5.721  1.00  0.00           H  \n",
            "HETATM   89  H89 TNS A   2      12.913 -39.159  -0.903  1.00  0.00           H  \n",
            "HETATM   90  H90 TNS A   2       3.419 -37.231  -6.629  1.00  0.00           H  \n",
            "HETATM   91  H91 TNS A   2      -5.609 -33.821 -11.699  1.00  0.00           H  \n",
            "HETATM   92  H92 TNS A   2     -14.227 -29.113 -16.193  1.00  0.00           H  \n",
            "HETATM   93  H93 TNS A   2     -22.436 -23.107 -20.112  1.00  0.00           H  \n",
            "HETATM   94  H94 TNS A   2     -30.178 -15.618 -23.374  1.00  0.00           H  \n",
            "HETATM   95  H95 TNS A   2     -37.282  -6.107 -25.740  1.00  0.00           H  \n",
            "HETATM   96  H96 TNS A   2     -43.127   7.401 -26.334  1.00  0.00           H  \n",
            "HETATM   97  H97 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM   98  H98 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM   99  H99 TNS A   2      32.054 -35.245  18.399  1.00  0.00           H  \n",
            "HETATM  100 H100 TNS A   2      19.141 -39.511  12.739  1.00  0.00           H  \n",
            "HETATM  101 H101 TNS A   2       8.178 -39.702   7.608  1.00  0.00           H  \n",
            "HETATM  102 H102 TNS A   2      -1.797 -37.829   2.746  1.00  0.00           H  \n",
            "HETATM  103 H103 TNS A   2     -11.049 -34.445  -1.921  1.00  0.00           H  \n",
            "HETATM  104 H104 TNS A   2     -19.667 -29.737  -6.415  1.00  0.00           H  \n",
            "HETATM  105 H105 TNS A   2     -27.651 -23.705 -10.738  1.00  0.00           H  \n",
            "HETATM  106 H106 TNS A   2     -34.913 -16.161 -14.864  1.00  0.00           H  \n",
            "HETATM  107 H107 TNS A   2     -41.187  -6.554 -18.722  1.00  0.00           H  \n",
            "HETATM  108 H108 TNS A   2     -45.510   7.128 -22.051  1.00  0.00           H  \n",
            "HETATM  109 H109 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  110 H110 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  111 H111 TNS A   2      30.329 -34.142  22.861  1.00  0.00           H  \n",
            "HETATM  112 H112 TNS A   2      16.316 -37.704  20.050  1.00  0.00           H  \n",
            "HETATM  113 H113 TNS A   2       4.752 -37.510  16.474  1.00  0.00           H  \n",
            "HETATM  114 H114 TNS A   2      -5.571 -35.415  12.511  1.00  0.00           H  \n",
            "HETATM  115 H115 TNS A   2     -14.985 -31.927   8.265  1.00  0.00           H  \n",
            "HETATM  116 H116 TNS A   2     -23.603 -27.219   3.771  1.00  0.00           H  \n",
            "HETATM  117 H117 TNS A   2     -31.426 -21.291  -0.972  1.00  0.00           H  \n",
            "HETATM  118 H118 TNS A   2     -38.339 -13.970  -5.998  1.00  0.00           H  \n",
            "HETATM  119 H119 TNS A   2     -44.012  -4.747 -11.411  1.00  0.00           H  \n",
            "HETATM  120 H120 TNS A   2     -47.235   8.231 -17.588  1.00  0.00           H  \n",
            "HETATM  121 H121 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  122 H122 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  123 H123 TNS A   2      29.432 -31.771  27.066  1.00  0.00           H  \n",
            "HETATM  124 H124 TNS A   2      14.846 -33.819  26.938  1.00  0.00           H  \n",
            "HETATM  125 H125 TNS A   2       2.970 -32.799  24.827  1.00  0.00           H  \n",
            "HETATM  126 H126 TNS A   2      -7.534 -30.226  21.713  1.00  0.00           H  \n",
            "HETATM  127 H127 TNS A   2     -17.033 -26.514  17.862  1.00  0.00           H  \n",
            "HETATM  128 H128 TNS A   2     -25.651 -21.806  13.368  1.00  0.00           H  \n",
            "HETATM  129 H129 TNS A   2     -33.389 -16.101   8.229  1.00  0.00           H  \n",
            "HETATM  130 H130 TNS A   2     -40.121  -9.258   2.355  1.00  0.00           H  \n",
            "HETATM  131 H131 TNS A   2     -45.482  -0.862  -4.523  1.00  0.00           H  \n",
            "HETATM  132 H132 TNS A   2     -48.132  10.602 -13.384  1.00  0.00           H  \n",
            "HETATM  133 H133 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  134 H134 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  135 H135 TNS A   2      29.450 -28.364  30.600  1.00  0.00           H  \n",
            "HETATM  136 H136 TNS A   2      14.875 -28.237  32.729  1.00  0.00           H  \n",
            "HETATM  137 H137 TNS A   2       3.005 -26.030  31.850  1.00  0.00           H  \n",
            "HETATM  138 H138 TNS A   2      -7.495 -22.769  29.448  1.00  0.00           H  \n",
            "HETATM  139 H139 TNS A   2     -16.992 -18.737  25.931  1.00  0.00           H  \n",
            "HETATM  140 H140 TNS A   2     -25.610 -14.029  21.436  1.00  0.00           H  \n",
            "HETATM  141 H141 TNS A   2     -33.349  -8.645  15.965  1.00  0.00           H  \n",
            "HETATM  142 H142 TNS A   2     -40.086  -2.489   9.378  1.00  0.00           H  \n",
            "HETATM  143 H143 TNS A   2     -45.452   4.720   1.268  1.00  0.00           H  \n",
            "HETATM  144 H144 TNS A   2     -48.114  14.010  -9.849  1.00  0.00           H  \n",
            "HETATM  145 H145 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  146 H146 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  147 H147 TNS A   2      30.382 -24.254  33.119  1.00  0.00           H  \n",
            "HETATM  148 H148 TNS A   2      16.401 -21.504  36.856  1.00  0.00           H  \n",
            "HETATM  149 H149 TNS A   2       4.856 -17.864  36.855  1.00  0.00           H  \n",
            "HETATM  150 H150 TNS A   2      -5.456 -13.775  34.961  1.00  0.00           H  \n",
            "HETATM  151 H151 TNS A   2     -14.866  -9.356  31.681  1.00  0.00           H  \n",
            "HETATM  152 H152 TNS A   2     -23.484  -4.647  27.187  1.00  0.00           H  \n",
            "HETATM  153 H153 TNS A   2     -31.311   0.350  21.478  1.00  0.00           H  \n",
            "HETATM  154 H154 TNS A   2     -38.235   5.676  14.383  1.00  0.00           H  \n",
            "HETATM  155 H155 TNS A   2     -43.926  11.453   5.396  1.00  0.00           H  \n",
            "HETATM  156 H156 TNS A   2     -47.182  18.119  -7.330  1.00  0.00           H  \n",
            "HETATM  157 H157 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  158 H158 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  159 H159 TNS A   2      32.136 -19.844  34.376  1.00  0.00           H  \n",
            "HETATM  160 H160 TNS A   2      19.275 -14.279  38.915  1.00  0.00           H  \n",
            "HETATM  161 H161 TNS A   2       8.341  -9.103  39.352  1.00  0.00           H  \n",
            "HETATM  162 H162 TNS A   2      -1.618  -4.124  37.712  1.00  0.00           H  \n",
            "HETATM  163 H163 TNS A   2     -10.862   0.711  34.550  1.00  0.00           H  \n",
            "HETATM  164 H164 TNS A   2     -19.481   5.419  30.056  1.00  0.00           H  \n",
            "HETATM  165 H165 TNS A   2     -27.473  10.001  24.229  1.00  0.00           H  \n",
            "HETATM  166 H166 TNS A   2     -34.751  14.438  16.880  1.00  0.00           H  \n",
            "HETATM  167 H167 TNS A   2     -41.053  18.678   7.455  1.00  0.00           H  \n",
            "HETATM  168 H168 TNS A   2     -45.428  22.529  -6.073  1.00  0.00           H  \n",
            "HETATM  169 H169 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  170 H170 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  171 H171 TNS A   2      34.540 -15.565  34.248  1.00  0.00           H  \n",
            "HETATM  172 H172 TNS A   2      23.214  -7.269  38.705  1.00  0.00           H  \n",
            "HETATM  173 H173 TNS A   2      13.117  -0.602  39.097  1.00  0.00           H  \n",
            "HETATM  174 H174 TNS A   2       3.644   5.240  37.431  1.00  0.00           H  \n",
            "HETATM  175 H175 TNS A   2      -5.374  10.478  34.257  1.00  0.00           H  \n",
            "HETATM  176 H176 TNS A   2     -13.992  15.186  29.763  1.00  0.00           H  \n",
            "HETATM  177 H177 TNS A   2     -22.211  19.364  23.948  1.00  0.00           H  \n",
            "HETATM  178 H178 TNS A   2     -29.974  22.939  16.625  1.00  0.00           H  \n",
            "HETATM  179 H179 TNS A   2     -37.114  25.688   7.244  1.00  0.00           H  \n",
            "HETATM  180 H180 TNS A   2     -43.024  26.808  -6.202  1.00  0.00           H  \n",
            "HETATM  181 H181 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  182 H182 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  183 H183 TNS A   2      37.360 -11.837  32.747  1.00  0.00           H  \n",
            "HETATM  184 H184 TNS A   2      27.833  -1.160  36.246  1.00  0.00           H  \n",
            "HETATM  185 H185 TNS A   2      18.719   6.806  36.115  1.00  0.00           H  \n",
            "HETATM  186 H186 TNS A   2       9.814  13.399  34.146  1.00  0.00           H  \n",
            "HETATM  187 H187 TNS A   2       1.062  18.988  30.831  1.00  0.00           H  \n",
            "HETATM  188 H188 TNS A   2      -7.556  23.696  26.336  1.00  0.00           H  \n",
            "HETATM  189 H189 TNS A   2     -16.040  27.524  20.663  1.00  0.00           H  \n",
            "HETATM  190 H190 TNS A   2     -24.372  30.346  13.643  1.00  0.00           H  \n",
            "HETATM  191 H191 TNS A   2     -32.494  31.797   4.785  1.00  0.00           H  \n",
            "HETATM  192 H192 TNS A   2     -40.204  30.536  -7.703  1.00  0.00           H  \n",
            "HETATM  193 H193 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  194 H194 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  195 H195 TNS A   2      40.318  -9.024  30.020  1.00  0.00           H  \n",
            "HETATM  196 H196 TNS A   2      32.681   3.448  31.778  1.00  0.00           H  \n",
            "HETATM  197 H197 TNS A   2      24.598  12.395  30.697  1.00  0.00           H  \n",
            "HETATM  198 H198 TNS A   2      16.290  19.556  28.178  1.00  0.00           H  \n",
            "HETATM  199 H199 TNS A   2       7.816  25.409  24.606  1.00  0.00           H  \n",
            "HETATM  200 H200 TNS A   2      -0.802  30.118  20.112  1.00  0.00           H  \n",
            "HETATM  201 H201 TNS A   2      -9.565  33.680  14.695  1.00  0.00           H  \n",
            "HETATM  202 H202 TNS A   2     -18.493  35.935   8.225  1.00  0.00           H  \n",
            "HETATM  203 H203 TNS A   2     -27.647  36.406   0.318  1.00  0.00           H  \n",
            "HETATM  204 H204 TNS A   2     -37.246  33.350 -10.430  1.00  0.00           H  \n",
            "HETATM  205 H205 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  206 H206 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  207 H207 TNS A   2      43.127  -7.401  26.334  1.00  0.00           H  \n",
            "HETATM  208 H208 TNS A   2      37.282   6.107  25.740  1.00  0.00           H  \n",
            "HETATM  209 H209 TNS A   2      30.178  15.618  23.374  1.00  0.00           H  \n",
            "HETATM  210 H210 TNS A   2      22.436  23.107  20.112  1.00  0.00           H  \n",
            "HETATM  211 H211 TNS A   2      14.227  29.113  16.193  1.00  0.00           H  \n",
            "HETATM  212 H212 TNS A   2       5.609  33.821  11.699  1.00  0.00           H  \n",
            "HETATM  213 H213 TNS A   2      -3.419  37.231   6.629  1.00  0.00           H  \n",
            "HETATM  214 H214 TNS A   2     -12.913  39.159   0.903  1.00  0.00           H  \n",
            "HETATM  215 H215 TNS A   2     -23.045  39.064  -5.721  1.00  0.00           H  \n",
            "HETATM  216 H216 TNS A   2     -34.437  34.972 -14.115  1.00  0.00           H  \n",
            "HETATM  217 H217 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  218 H218 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  219 H219 TNS A   2      45.510  -7.128  22.051  1.00  0.00           H  \n",
            "HETATM  220 H220 TNS A   2      41.187   6.554  18.722  1.00  0.00           H  \n",
            "HETATM  221 H221 TNS A   2      34.913  16.161  14.864  1.00  0.00           H  \n",
            "HETATM  222 H222 TNS A   2      27.651  23.705  10.738  1.00  0.00           H  \n",
            "HETATM  223 H223 TNS A   2      19.667  29.737   6.415  1.00  0.00           H  \n",
            "HETATM  224 H224 TNS A   2      11.049  34.445   1.921  1.00  0.00           H  \n",
            "HETATM  225 H225 TNS A   2       1.797  37.829  -2.746  1.00  0.00           H  \n",
            "HETATM  226 H226 TNS A   2      -8.178  39.702  -7.608  1.00  0.00           H  \n",
            "HETATM  227 H227 TNS A   2     -19.141  39.511 -12.739  1.00  0.00           H  \n",
            "HETATM  228 H228 TNS A   2     -32.054  35.245 -18.399  1.00  0.00           H  \n",
            "HETATM  229 H229 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  230 H230 TNS A   2      43.091 -23.541  22.472  1.00  0.00           H  \n",
            "HETATM  231 H231 TNS A   2      47.235  -8.231  17.588  1.00  0.00           H  \n",
            "HETATM  232 H232 TNS A   2      44.012   4.747  11.411  1.00  0.00           H  \n",
            "HETATM  233 H233 TNS A   2      38.339  13.970   5.998  1.00  0.00           H  \n",
            "HETATM  234 H234 TNS A   2      31.426  21.291   0.972  1.00  0.00           H  \n",
            "HETATM  235 H235 TNS A   2      23.603  27.219  -3.771  1.00  0.00           H  \n",
            "HETATM  236 H236 TNS A   2      14.985  31.927  -8.265  1.00  0.00           H  \n",
            "HETATM  237 H237 TNS A   2       5.571  35.415 -12.511  1.00  0.00           H  \n",
            "HETATM  238 H238 TNS A   2      -4.752  37.510 -16.474  1.00  0.00           H  \n",
            "HETATM  239 H239 TNS A   2     -16.316  37.704 -20.050  1.00  0.00           H  \n",
            "HETATM  240 H240 TNS A   2     -30.329  34.142 -22.861  1.00  0.00           H  \n",
            "HETATM  241 H241 TNS A   2     -43.091  23.541 -22.472  1.00  0.00           H  \n",
            "HETATM  242    R AXS A   3      -0.000   0.000   0.000  1.00  0.00           C  \n",
            "HETATM  243 Dpar AXS A   3     -43.091  23.541 -22.472  1.00  0.00           C  \n",
            "HETATM  244 Dpar AXS A   3      43.091 -23.541  22.472  1.00  0.00           C  \n",
            "HETATM  245 Dpar AXS A   3     -47.400  25.895 -24.719  1.00  0.00           N  \n",
            "HETATM  246 Dpar AXS A   3      47.400 -25.895  24.719  1.00  0.00           N  \n",
            "CONECT    2    3   14  230                                                      \n",
            "CONECT    3    2    4   15  231                                                 \n",
            "CONECT    4    3    5   16  232                                                 \n",
            "CONECT    5    4    6   17  233                                                 \n",
            "CONECT    6    5    7   18  234                                                 \n",
            "CONECT    7    6    8   19  235                                                 \n",
            "CONECT    8    7    9   20  236                                                 \n",
            "CONECT    9    8   10   21  237                                                 \n",
            "CONECT   10    9   11   22  238                                                 \n",
            "CONECT   11   10   12   23  239                                                 \n",
            "CONECT   12   11   13   24  240                                                 \n",
            "CONECT   13   12   25  241                                                      \n",
            "CONECT   14    2   15   26                                                      \n",
            "CONECT   15   14    3   16   27                                                 \n",
            "CONECT   16   15    4   17   28                                                 \n",
            "CONECT   17   16    5   18   29                                                 \n",
            "CONECT   18   17    6   19   30                                                 \n",
            "CONECT   19   18    7   20   31                                                 \n",
            "CONECT   20   19    8   21   32                                                 \n",
            "CONECT   21   20    9   22   33                                                 \n",
            "CONECT   22   21   10   23   34                                                 \n",
            "CONECT   23   22   11   24   35                                                 \n",
            "CONECT   24   23   12   25   36                                                 \n",
            "CONECT   25   24   13   37                                                      \n",
            "CONECT   26   14   27   38                                                      \n",
            "CONECT   27   26   15   28   39                                                 \n",
            "CONECT   28   27   16   29   40                                                 \n",
            "CONECT   29   28   17   30   41                                                 \n",
            "CONECT   30   29   18   31   42                                                 \n",
            "CONECT   31   30   19   32   43                                                 \n",
            "CONECT   32   31   20   33   44                                                 \n",
            "CONECT   33   32   21   34   45                                                 \n",
            "CONECT   34   33   22   35   46                                                 \n",
            "CONECT   35   34   23   36   47                                                 \n",
            "CONECT   36   35   24   37   48                                                 \n",
            "CONECT   37   36   25   49                                                      \n",
            "CONECT   38   26   39   50                                                      \n",
            "CONECT   39   38   27   40   51                                                 \n",
            "CONECT   40   39   28   41   52                                                 \n",
            "CONECT   41   40   29   42   53                                                 \n",
            "CONECT   42   41   30   43   54                                                 \n",
            "CONECT   43   42   31   44   55                                                 \n",
            "CONECT   44   43   32   45   56                                                 \n",
            "CONECT   45   44   33   46   57                                                 \n",
            "CONECT   46   45   34   47   58                                                 \n",
            "CONECT   47   46   35   48   59                                                 \n",
            "CONECT   48   47   36   49   60                                                 \n",
            "CONECT   49   48   37   61                                                      \n",
            "CONECT   50   38   51   62                                                      \n",
            "CONECT   51   50   39   52   63                                                 \n",
            "CONECT   52   51   40   53   64                                                 \n",
            "CONECT   53   52   41   54   65                                                 \n",
            "CONECT   54   53   42   55   66                                                 \n",
            "CONECT   55   54   43   56   67                                                 \n",
            "CONECT   56   55   44   57   68                                                 \n",
            "CONECT   57   56   45   58   69                                                 \n",
            "CONECT   58   57   46   59   70                                                 \n",
            "CONECT   59   58   47   60   71                                                 \n",
            "CONECT   60   59   48   61   72                                                 \n",
            "CONECT   61   60   49   73                                                      \n",
            "CONECT   62   50   63   74                                                      \n",
            "CONECT   63   62   51   64   75                                                 \n",
            "CONECT   64   63   52   65   76                                                 \n",
            "CONECT   65   64   53   66   77                                                 \n",
            "CONECT   66   65   54   67   78                                                 \n",
            "CONECT   67   66   55   68   79                                                 \n",
            "CONECT   68   67   56   69   80                                                 \n",
            "CONECT   69   68   57   70   81                                                 \n",
            "CONECT   70   69   58   71   82                                                 \n",
            "CONECT   71   70   59   72   83                                                 \n",
            "CONECT   72   71   60   73   84                                                 \n",
            "CONECT   73   72   61   85                                                      \n",
            "CONECT   74   62   75   86                                                      \n",
            "CONECT   75   74   63   76   87                                                 \n",
            "CONECT   76   75   64   77   88                                                 \n",
            "CONECT   77   76   65   78   89                                                 \n",
            "CONECT   78   77   66   79   90                                                 \n",
            "CONECT   79   78   67   80   91                                                 \n",
            "CONECT   80   79   68   81   92                                                 \n",
            "CONECT   81   80   69   82   93                                                 \n",
            "CONECT   82   81   70   83   94                                                 \n",
            "CONECT   83   82   71   84   95                                                 \n",
            "CONECT   84   83   72   85   96                                                 \n",
            "CONECT   85   84   73   97                                                      \n",
            "CONECT   86   74   87   98                                                      \n",
            "CONECT   87   86   75   88   99                                                 \n",
            "CONECT   88   87   76   89  100                                                 \n",
            "CONECT   89   88   77   90  101                                                 \n",
            "CONECT   90   89   78   91  102                                                 \n",
            "CONECT   91   90   79   92  103                                                 \n",
            "CONECT   92   91   80   93  104                                                 \n",
            "CONECT   93   92   81   94  105                                                 \n",
            "CONECT   94   93   82   95  106                                                 \n",
            "CONECT   95   94   83   96  107                                                 \n",
            "CONECT   96   95   84   97  108                                                 \n",
            "CONECT   97   96   85  109                                                      \n",
            "CONECT   98   86   99  110                                                      \n",
            "CONECT   99   98   87  100  111                                                 \n",
            "CONECT  100   99   88  101  112                                                 \n",
            "CONECT  101  100   89  102  113                                                 \n",
            "CONECT  102  101   90  103  114                                                 \n",
            "CONECT  103  102   91  104  115                                                 \n",
            "CONECT  104  103   92  105  116                                                 \n",
            "CONECT  105  104   93  106  117                                                 \n",
            "CONECT  106  105   94  107  118                                                 \n",
            "CONECT  107  106   95  108  119                                                 \n",
            "CONECT  108  107   96  109  120                                                 \n",
            "CONECT  109  108   97  121                                                      \n",
            "CONECT  110   98  111  122                                                      \n",
            "CONECT  111  110   99  112  123                                                 \n",
            "CONECT  112  111  100  113  124                                                 \n",
            "CONECT  113  112  101  114  125                                                 \n",
            "CONECT  114  113  102  115  126                                                 \n",
            "CONECT  115  114  103  116  127                                                 \n",
            "CONECT  116  115  104  117  128                                                 \n",
            "CONECT  117  116  105  118  129                                                 \n",
            "CONECT  118  117  106  119  130                                                 \n",
            "CONECT  119  118  107  120  131                                                 \n",
            "CONECT  120  119  108  121  132                                                 \n",
            "CONECT  121  120  109  133                                                      \n",
            "CONECT  122  110  123  134                                                      \n",
            "CONECT  123  122  111  124  135                                                 \n",
            "CONECT  124  123  112  125  136                                                 \n",
            "CONECT  125  124  113  126  137                                                 \n",
            "CONECT  126  125  114  127  138                                                 \n",
            "CONECT  127  126  115  128  139                                                 \n",
            "CONECT  128  127  116  129  140                                                 \n",
            "CONECT  129  128  117  130  141                                                 \n",
            "CONECT  130  129  118  131  142                                                 \n",
            "CONECT  131  130  119  132  143                                                 \n",
            "CONECT  132  131  120  133  144                                                 \n",
            "CONECT  133  132  121  145                                                      \n",
            "CONECT  134  122  135  146                                                      \n",
            "CONECT  135  134  123  136  147                                                 \n",
            "CONECT  136  135  124  137  148                                                 \n",
            "CONECT  137  136  125  138  149                                                 \n",
            "CONECT  138  137  126  139  150                                                 \n",
            "CONECT  139  138  127  140  151                                                 \n",
            "CONECT  140  139  128  141  152                                                 \n",
            "CONECT  141  140  129  142  153                                                 \n",
            "CONECT  142  141  130  143  154                                                 \n",
            "CONECT  143  142  131  144  155                                                 \n",
            "CONECT  144  143  132  145  156                                                 \n",
            "CONECT  145  144  133  157                                                      \n",
            "CONECT  146  134  147  158                                                      \n",
            "CONECT  147  146  135  148  159                                                 \n",
            "CONECT  148  147  136  149  160                                                 \n",
            "CONECT  149  148  137  150  161                                                 \n",
            "CONECT  150  149  138  151  162                                                 \n",
            "CONECT  151  150  139  152  163                                                 \n",
            "CONECT  152  151  140  153  164                                                 \n",
            "CONECT  153  152  141  154  165                                                 \n",
            "CONECT  154  153  142  155  166                                                 \n",
            "CONECT  155  154  143  156  167                                                 \n",
            "CONECT  156  155  144  157  168                                                 \n",
            "CONECT  157  156  145  169                                                      \n",
            "CONECT  158  146  159  170                                                      \n",
            "CONECT  159  158  147  160  171                                                 \n",
            "CONECT  160  159  148  161  172                                                 \n",
            "CONECT  161  160  149  162  173                                                 \n",
            "CONECT  162  161  150  163  174                                                 \n",
            "CONECT  163  162  151  164  175                                                 \n",
            "CONECT  164  163  152  165  176                                                 \n",
            "CONECT  165  164  153  166  177                                                 \n",
            "CONECT  166  165  154  167  178                                                 \n",
            "CONECT  167  166  155  168  179                                                 \n",
            "CONECT  168  167  156  169  180                                                 \n",
            "CONECT  169  168  157  181                                                      \n",
            "CONECT  170  158  171  182                                                      \n",
            "CONECT  171  170  159  172  183                                                 \n",
            "CONECT  172  171  160  173  184                                                 \n",
            "CONECT  173  172  161  174  185                                                 \n",
            "CONECT  174  173  162  175  186                                                 \n",
            "CONECT  175  174  163  176  187                                                 \n",
            "CONECT  176  175  164  177  188                                                 \n",
            "CONECT  177  176  165  178  189                                                 \n",
            "CONECT  178  177  166  179  190                                                 \n",
            "CONECT  179  178  167  180  191                                                 \n",
            "CONECT  180  179  168  181  192                                                 \n",
            "CONECT  181  180  169  193                                                      \n",
            "CONECT  182  170  183  194                                                      \n",
            "CONECT  183  182  171  184  195                                                 \n",
            "CONECT  184  183  172  185  196                                                 \n",
            "CONECT  185  184  173  186  197                                                 \n",
            "CONECT  186  185  174  187  198                                                 \n",
            "CONECT  187  186  175  188  199                                                 \n",
            "CONECT  188  187  176  189  200                                                 \n",
            "CONECT  189  188  177  190  201                                                 \n",
            "CONECT  190  189  178  191  202                                                 \n",
            "CONECT  191  190  179  192  203                                                 \n",
            "CONECT  192  191  180  193  204                                                 \n",
            "CONECT  193  192  181  205                                                      \n",
            "CONECT  194  182  195  206                                                      \n",
            "CONECT  195  194  183  196  207                                                 \n",
            "CONECT  196  195  184  197  208                                                 \n",
            "CONECT  197  196  185  198  209                                                 \n",
            "CONECT  198  197  186  199  210                                                 \n",
            "CONECT  199  198  187  200  211                                                 \n",
            "CONECT  200  199  188  201  212                                                 \n",
            "CONECT  201  200  189  202  213                                                 \n",
            "CONECT  202  201  190  203  214                                                 \n",
            "CONECT  203  202  191  204  215                                                 \n",
            "CONECT  204  203  192  205  216                                                 \n",
            "CONECT  205  204  193  217                                                      \n",
            "CONECT  206  194  207  218                                                      \n",
            "CONECT  207  206  195  208  219                                                 \n",
            "CONECT  208  207  196  209  220                                                 \n",
            "CONECT  209  208  197  210  221                                                 \n",
            "CONECT  210  209  198  211  222                                                 \n",
            "CONECT  211  210  199  212  223                                                 \n",
            "CONECT  212  211  200  213  224                                                 \n",
            "CONECT  213  212  201  214  225                                                 \n",
            "CONECT  214  213  202  215  226                                                 \n",
            "CONECT  215  214  203  216  227                                                 \n",
            "CONECT  216  215  204  217  228                                                 \n",
            "CONECT  217  216  205  229                                                      \n",
            "CONECT  218  206  219  230                                                      \n",
            "CONECT  219  218  207  220  231                                                 \n",
            "CONECT  220  219  208  221  232                                                 \n",
            "CONECT  221  220  209  222  233                                                 \n",
            "CONECT  222  221  210  223  234                                                 \n",
            "CONECT  223  222  211  224  235                                                 \n",
            "CONECT  224  223  212  225  236                                                 \n",
            "CONECT  225  224  213  226  237                                                 \n",
            "CONECT  226  225  214  227  238                                                 \n",
            "CONECT  227  226  215  228  239                                                 \n",
            "CONECT  228  227  216  229  240                                                 \n",
            "CONECT  229  228  217  241                                                      \n",
            "CONECT  230  218    2  231                                                      \n",
            "CONECT  231  230  219    3  232                                                 \n",
            "CONECT  232  231  220    4  233                                                 \n",
            "CONECT  233  232  221    5  234                                                 \n",
            "CONECT  234  233  222    6  235                                                 \n",
            "CONECT  235  234  223    7  236                                                 \n",
            "CONECT  236  235  224    8  237                                                 \n",
            "CONECT  237  236  225    9  238                                                 \n",
            "CONECT  238  237  226   10  239                                                 \n",
            "CONECT  239  238  227   11  240                                                 \n",
            "CONECT  240  239  228   12  241                                                 \n",
            "CONECT  241  240  229   13                                                      \n",
            "CONECT  242  243  244                                                           \n",
            "CONECT  243  242                                                                \n",
            "CONECT  244  242                                                                \n",
            "MASTER        0    0    3    0    0    0    0    0  246    0  243    0          \n",
            "END                                                                             \n"
        ]

        # Check the data.
        self.strip_remarks(lines)
        self.assertEqual(len(real_data), len(lines))
        for i in range(len(lines)):
            self.assertEqual(real_data[i], lines[i])


    def test_create_diff_tensor_pdb_sphere(self):
        """Check that the sphere diffusion tensor optimisation functions correctly."""

        # Reset relax.
        self.interpreter.reset()

        # Create a temporary file.
        ds.tmpfile_handle, ds.tmpfile = mkstemp(suffix='.pdb')

        # The diffusion type (used by the script).
        ds.diff_dir = 'sphere'
        ds.diff_type = 'sphere'

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'diff_tensor'+sep+'tensor_opt.py')

        # Create the PDB representation.
        self.interpreter.structure.create_diff_tensor_pdb(scale=1.8e-06, file=ds.tmpfile, force=True)

        # Read the contents of the file.
        file = open(ds.tmpfile)
        lines = file.readlines()
        file.close()

        # What the contents should be, without remarks.
        real_data = [
            "HET    COM  A   1       1                                                       \n",
            "HET    TNS  A   2     240                                                       \n",
            "HETNAM     COM CENTRE OF MASS                                                   \n",
            "HETNAM     TNS TENSOR                                                           \n",
            "FORMUL   1  COM    C1                                                           \n",
            "FORMUL   2  TNS    H240                                                         \n",
            "HETATM    1    R COM A   1      -0.000   0.000   0.000  1.00  0.00           C  \n",
            "HETATM    2   H2 TNS A   2       0.000   0.000 -36.000  1.00  0.00           H  \n",
            "HETATM    3   H3 TNS A   2      15.692   0.000 -32.400  1.00  0.00           H  \n",
            "HETATM    4   H4 TNS A   2      25.709   0.000 -25.200  1.00  0.00           H  \n",
            "HETATM    5   H5 TNS A   2      31.177   0.000 -18.000  1.00  0.00           H  \n",
            "HETATM    6   H6 TNS A   2      34.342   0.000 -10.800  1.00  0.00           H  \n",
            "HETATM    7   H7 TNS A   2      35.820   0.000  -3.600  1.00  0.00           H  \n",
            "HETATM    8   H8 TNS A   2      35.820   0.000   3.600  1.00  0.00           H  \n",
            "HETATM    9   H9 TNS A   2      34.342   0.000  10.800  1.00  0.00           H  \n",
            "HETATM   10  H10 TNS A   2      31.177   0.000  18.000  1.00  0.00           H  \n",
            "HETATM   11  H11 TNS A   2      25.709   0.000  25.200  1.00  0.00           H  \n",
            "HETATM   12  H12 TNS A   2      15.692   0.000  32.400  1.00  0.00           H  \n",
            "HETATM   13  H13 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM   14  H14 TNS A   2       0.000   0.000 -36.000  1.00  0.00           H  \n",
            "HETATM   15  H15 TNS A   2      14.924   4.849 -32.400  1.00  0.00           H  \n",
            "HETATM   16  H16 TNS A   2      24.451   7.945 -25.200  1.00  0.00           H  \n",
            "HETATM   17  H17 TNS A   2      29.651   9.634 -18.000  1.00  0.00           H  \n",
            "HETATM   18  H18 TNS A   2      32.661  10.612 -10.800  1.00  0.00           H  \n",
            "HETATM   19  H19 TNS A   2      34.066  11.069  -3.600  1.00  0.00           H  \n",
            "HETATM   20  H20 TNS A   2      34.066  11.069   3.600  1.00  0.00           H  \n",
            "HETATM   21  H21 TNS A   2      32.661  10.612  10.800  1.00  0.00           H  \n",
            "HETATM   22  H22 TNS A   2      29.651   9.634  18.000  1.00  0.00           H  \n",
            "HETATM   23  H23 TNS A   2      24.451   7.945  25.200  1.00  0.00           H  \n",
            "HETATM   24  H24 TNS A   2      14.924   4.849  32.400  1.00  0.00           H  \n",
            "HETATM   25  H25 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM   26  H26 TNS A   2       0.000   0.000 -36.000  1.00  0.00           H  \n",
            "HETATM   27  H27 TNS A   2      12.695   9.224 -32.400  1.00  0.00           H  \n",
            "HETATM   28  H28 TNS A   2      20.799  15.111 -25.200  1.00  0.00           H  \n",
            "HETATM   29  H29 TNS A   2      25.223  18.325 -18.000  1.00  0.00           H  \n",
            "HETATM   30  H30 TNS A   2      27.783  20.186 -10.800  1.00  0.00           H  \n",
            "HETATM   31  H31 TNS A   2      28.979  21.054  -3.600  1.00  0.00           H  \n",
            "HETATM   32  H32 TNS A   2      28.979  21.054   3.600  1.00  0.00           H  \n",
            "HETATM   33  H33 TNS A   2      27.783  20.186  10.800  1.00  0.00           H  \n",
            "HETATM   34  H34 TNS A   2      25.223  18.325  18.000  1.00  0.00           H  \n",
            "HETATM   35  H35 TNS A   2      20.799  15.111  25.200  1.00  0.00           H  \n",
            "HETATM   36  H36 TNS A   2      12.695   9.224  32.400  1.00  0.00           H  \n",
            "HETATM   37  H37 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM   38  H38 TNS A   2       0.000   0.000 -36.000  1.00  0.00           H  \n",
            "HETATM   39  H39 TNS A   2       9.224  12.695 -32.400  1.00  0.00           H  \n",
            "HETATM   40  H40 TNS A   2      15.111  20.799 -25.200  1.00  0.00           H  \n",
            "HETATM   41  H41 TNS A   2      18.325  25.223 -18.000  1.00  0.00           H  \n",
            "HETATM   42  H42 TNS A   2      20.186  27.783 -10.800  1.00  0.00           H  \n",
            "HETATM   43  H43 TNS A   2      21.054  28.979  -3.600  1.00  0.00           H  \n",
            "HETATM   44  H44 TNS A   2      21.054  28.979   3.600  1.00  0.00           H  \n",
            "HETATM   45  H45 TNS A   2      20.186  27.783  10.800  1.00  0.00           H  \n",
            "HETATM   46  H46 TNS A   2      18.325  25.223  18.000  1.00  0.00           H  \n",
            "HETATM   47  H47 TNS A   2      15.111  20.799  25.200  1.00  0.00           H  \n",
            "HETATM   48  H48 TNS A   2       9.224  12.695  32.400  1.00  0.00           H  \n",
            "HETATM   49  H49 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM   50  H50 TNS A   2       0.000   0.000 -36.000  1.00  0.00           H  \n",
            "HETATM   51  H51 TNS A   2       4.849  14.924 -32.400  1.00  0.00           H  \n",
            "HETATM   52  H52 TNS A   2       7.945  24.451 -25.200  1.00  0.00           H  \n",
            "HETATM   53  H53 TNS A   2       9.634  29.651 -18.000  1.00  0.00           H  \n",
            "HETATM   54  H54 TNS A   2      10.612  32.661 -10.800  1.00  0.00           H  \n",
            "HETATM   55  H55 TNS A   2      11.069  34.066  -3.600  1.00  0.00           H  \n",
            "HETATM   56  H56 TNS A   2      11.069  34.066   3.600  1.00  0.00           H  \n",
            "HETATM   57  H57 TNS A   2      10.612  32.661  10.800  1.00  0.00           H  \n",
            "HETATM   58  H58 TNS A   2       9.634  29.651  18.000  1.00  0.00           H  \n",
            "HETATM   59  H59 TNS A   2       7.945  24.451  25.200  1.00  0.00           H  \n",
            "HETATM   60  H60 TNS A   2       4.849  14.924  32.400  1.00  0.00           H  \n",
            "HETATM   61  H61 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM   62  H62 TNS A   2      -0.000   0.000 -36.000  1.00  0.00           H  \n",
            "HETATM   63  H63 TNS A   2       0.000  15.692 -32.400  1.00  0.00           H  \n",
            "HETATM   64  H64 TNS A   2       0.000  25.709 -25.200  1.00  0.00           H  \n",
            "HETATM   65  H65 TNS A   2       0.000  31.177 -18.000  1.00  0.00           H  \n",
            "HETATM   66  H66 TNS A   2       0.000  34.342 -10.800  1.00  0.00           H  \n",
            "HETATM   67  H67 TNS A   2       0.000  35.820  -3.600  1.00  0.00           H  \n",
            "HETATM   68  H68 TNS A   2       0.000  35.820   3.600  1.00  0.00           H  \n",
            "HETATM   69  H69 TNS A   2       0.000  34.342  10.800  1.00  0.00           H  \n",
            "HETATM   70  H70 TNS A   2       0.000  31.177  18.000  1.00  0.00           H  \n",
            "HETATM   71  H71 TNS A   2       0.000  25.709  25.200  1.00  0.00           H  \n",
            "HETATM   72  H72 TNS A   2       0.000  15.692  32.400  1.00  0.00           H  \n",
            "HETATM   73  H73 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM   74  H74 TNS A   2      -0.000   0.000 -36.000  1.00  0.00           H  \n",
            "HETATM   75  H75 TNS A   2      -4.849  14.924 -32.400  1.00  0.00           H  \n",
            "HETATM   76  H76 TNS A   2      -7.945  24.451 -25.200  1.00  0.00           H  \n",
            "HETATM   77  H77 TNS A   2      -9.634  29.651 -18.000  1.00  0.00           H  \n",
            "HETATM   78  H78 TNS A   2     -10.612  32.661 -10.800  1.00  0.00           H  \n",
            "HETATM   79  H79 TNS A   2     -11.069  34.066  -3.600  1.00  0.00           H  \n",
            "HETATM   80  H80 TNS A   2     -11.069  34.066   3.600  1.00  0.00           H  \n",
            "HETATM   81  H81 TNS A   2     -10.612  32.661  10.800  1.00  0.00           H  \n",
            "HETATM   82  H82 TNS A   2      -9.634  29.651  18.000  1.00  0.00           H  \n",
            "HETATM   83  H83 TNS A   2      -7.945  24.451  25.200  1.00  0.00           H  \n",
            "HETATM   84  H84 TNS A   2      -4.849  14.924  32.400  1.00  0.00           H  \n",
            "HETATM   85  H85 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM   86  H86 TNS A   2      -0.000   0.000 -36.000  1.00  0.00           H  \n",
            "HETATM   87  H87 TNS A   2      -9.224  12.695 -32.400  1.00  0.00           H  \n",
            "HETATM   88  H88 TNS A   2     -15.111  20.799 -25.200  1.00  0.00           H  \n",
            "HETATM   89  H89 TNS A   2     -18.325  25.223 -18.000  1.00  0.00           H  \n",
            "HETATM   90  H90 TNS A   2     -20.186  27.783 -10.800  1.00  0.00           H  \n",
            "HETATM   91  H91 TNS A   2     -21.054  28.979  -3.600  1.00  0.00           H  \n",
            "HETATM   92  H92 TNS A   2     -21.054  28.979   3.600  1.00  0.00           H  \n",
            "HETATM   93  H93 TNS A   2     -20.186  27.783  10.800  1.00  0.00           H  \n",
            "HETATM   94  H94 TNS A   2     -18.325  25.223  18.000  1.00  0.00           H  \n",
            "HETATM   95  H95 TNS A   2     -15.111  20.799  25.200  1.00  0.00           H  \n",
            "HETATM   96  H96 TNS A   2      -9.224  12.695  32.400  1.00  0.00           H  \n",
            "HETATM   97  H97 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM   98  H98 TNS A   2      -0.000   0.000 -36.000  1.00  0.00           H  \n",
            "HETATM   99  H99 TNS A   2     -12.695   9.224 -32.400  1.00  0.00           H  \n",
            "HETATM  100 H100 TNS A   2     -20.799  15.111 -25.200  1.00  0.00           H  \n",
            "HETATM  101 H101 TNS A   2     -25.223  18.325 -18.000  1.00  0.00           H  \n",
            "HETATM  102 H102 TNS A   2     -27.783  20.186 -10.800  1.00  0.00           H  \n",
            "HETATM  103 H103 TNS A   2     -28.979  21.054  -3.600  1.00  0.00           H  \n",
            "HETATM  104 H104 TNS A   2     -28.979  21.054   3.600  1.00  0.00           H  \n",
            "HETATM  105 H105 TNS A   2     -27.783  20.186  10.800  1.00  0.00           H  \n",
            "HETATM  106 H106 TNS A   2     -25.223  18.325  18.000  1.00  0.00           H  \n",
            "HETATM  107 H107 TNS A   2     -20.799  15.111  25.200  1.00  0.00           H  \n",
            "HETATM  108 H108 TNS A   2     -12.695   9.224  32.400  1.00  0.00           H  \n",
            "HETATM  109 H109 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM  110 H110 TNS A   2      -0.000   0.000 -36.000  1.00  0.00           H  \n",
            "HETATM  111 H111 TNS A   2     -14.924   4.849 -32.400  1.00  0.00           H  \n",
            "HETATM  112 H112 TNS A   2     -24.451   7.945 -25.200  1.00  0.00           H  \n",
            "HETATM  113 H113 TNS A   2     -29.651   9.634 -18.000  1.00  0.00           H  \n",
            "HETATM  114 H114 TNS A   2     -32.661  10.612 -10.800  1.00  0.00           H  \n",
            "HETATM  115 H115 TNS A   2     -34.066  11.069  -3.600  1.00  0.00           H  \n",
            "HETATM  116 H116 TNS A   2     -34.066  11.069   3.600  1.00  0.00           H  \n",
            "HETATM  117 H117 TNS A   2     -32.661  10.612  10.800  1.00  0.00           H  \n",
            "HETATM  118 H118 TNS A   2     -29.651   9.634  18.000  1.00  0.00           H  \n",
            "HETATM  119 H119 TNS A   2     -24.451   7.945  25.200  1.00  0.00           H  \n",
            "HETATM  120 H120 TNS A   2     -14.924   4.849  32.400  1.00  0.00           H  \n",
            "HETATM  121 H121 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM  122 H122 TNS A   2      -0.000   0.000 -36.000  1.00  0.00           H  \n",
            "HETATM  123 H123 TNS A   2     -15.692   0.000 -32.400  1.00  0.00           H  \n",
            "HETATM  124 H124 TNS A   2     -25.709   0.000 -25.200  1.00  0.00           H  \n",
            "HETATM  125 H125 TNS A   2     -31.177   0.000 -18.000  1.00  0.00           H  \n",
            "HETATM  126 H126 TNS A   2     -34.342   0.000 -10.800  1.00  0.00           H  \n",
            "HETATM  127 H127 TNS A   2     -35.820   0.000  -3.600  1.00  0.00           H  \n",
            "HETATM  128 H128 TNS A   2     -35.820   0.000   3.600  1.00  0.00           H  \n",
            "HETATM  129 H129 TNS A   2     -34.342   0.000  10.800  1.00  0.00           H  \n",
            "HETATM  130 H130 TNS A   2     -31.177   0.000  18.000  1.00  0.00           H  \n",
            "HETATM  131 H131 TNS A   2     -25.709   0.000  25.200  1.00  0.00           H  \n",
            "HETATM  132 H132 TNS A   2     -15.692   0.000  32.400  1.00  0.00           H  \n",
            "HETATM  133 H133 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM  134 H134 TNS A   2      -0.000  -0.000 -36.000  1.00  0.00           H  \n",
            "HETATM  135 H135 TNS A   2     -14.924  -4.849 -32.400  1.00  0.00           H  \n",
            "HETATM  136 H136 TNS A   2     -24.451  -7.945 -25.200  1.00  0.00           H  \n",
            "HETATM  137 H137 TNS A   2     -29.651  -9.634 -18.000  1.00  0.00           H  \n",
            "HETATM  138 H138 TNS A   2     -32.661 -10.612 -10.800  1.00  0.00           H  \n",
            "HETATM  139 H139 TNS A   2     -34.066 -11.069  -3.600  1.00  0.00           H  \n",
            "HETATM  140 H140 TNS A   2     -34.066 -11.069   3.600  1.00  0.00           H  \n",
            "HETATM  141 H141 TNS A   2     -32.661 -10.612  10.800  1.00  0.00           H  \n",
            "HETATM  142 H142 TNS A   2     -29.651  -9.634  18.000  1.00  0.00           H  \n",
            "HETATM  143 H143 TNS A   2     -24.451  -7.945  25.200  1.00  0.00           H  \n",
            "HETATM  144 H144 TNS A   2     -14.924  -4.849  32.400  1.00  0.00           H  \n",
            "HETATM  145 H145 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM  146 H146 TNS A   2      -0.000  -0.000 -36.000  1.00  0.00           H  \n",
            "HETATM  147 H147 TNS A   2     -12.695  -9.224 -32.400  1.00  0.00           H  \n",
            "HETATM  148 H148 TNS A   2     -20.799 -15.111 -25.200  1.00  0.00           H  \n",
            "HETATM  149 H149 TNS A   2     -25.223 -18.325 -18.000  1.00  0.00           H  \n",
            "HETATM  150 H150 TNS A   2     -27.783 -20.186 -10.800  1.00  0.00           H  \n",
            "HETATM  151 H151 TNS A   2     -28.979 -21.054  -3.600  1.00  0.00           H  \n",
            "HETATM  152 H152 TNS A   2     -28.979 -21.054   3.600  1.00  0.00           H  \n",
            "HETATM  153 H153 TNS A   2     -27.783 -20.186  10.800  1.00  0.00           H  \n",
            "HETATM  154 H154 TNS A   2     -25.223 -18.325  18.000  1.00  0.00           H  \n",
            "HETATM  155 H155 TNS A   2     -20.799 -15.111  25.200  1.00  0.00           H  \n",
            "HETATM  156 H156 TNS A   2     -12.695  -9.224  32.400  1.00  0.00           H  \n",
            "HETATM  157 H157 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM  158 H158 TNS A   2      -0.000  -0.000 -36.000  1.00  0.00           H  \n",
            "HETATM  159 H159 TNS A   2      -9.224 -12.695 -32.400  1.00  0.00           H  \n",
            "HETATM  160 H160 TNS A   2     -15.111 -20.799 -25.200  1.00  0.00           H  \n",
            "HETATM  161 H161 TNS A   2     -18.325 -25.223 -18.000  1.00  0.00           H  \n",
            "HETATM  162 H162 TNS A   2     -20.186 -27.783 -10.800  1.00  0.00           H  \n",
            "HETATM  163 H163 TNS A   2     -21.054 -28.979  -3.600  1.00  0.00           H  \n",
            "HETATM  164 H164 TNS A   2     -21.054 -28.979   3.600  1.00  0.00           H  \n",
            "HETATM  165 H165 TNS A   2     -20.186 -27.783  10.800  1.00  0.00           H  \n",
            "HETATM  166 H166 TNS A   2     -18.325 -25.223  18.000  1.00  0.00           H  \n",
            "HETATM  167 H167 TNS A   2     -15.111 -20.799  25.200  1.00  0.00           H  \n",
            "HETATM  168 H168 TNS A   2      -9.224 -12.695  32.400  1.00  0.00           H  \n",
            "HETATM  169 H169 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM  170 H170 TNS A   2      -0.000  -0.000 -36.000  1.00  0.00           H  \n",
            "HETATM  171 H171 TNS A   2      -4.849 -14.924 -32.400  1.00  0.00           H  \n",
            "HETATM  172 H172 TNS A   2      -7.945 -24.451 -25.200  1.00  0.00           H  \n",
            "HETATM  173 H173 TNS A   2      -9.634 -29.651 -18.000  1.00  0.00           H  \n",
            "HETATM  174 H174 TNS A   2     -10.612 -32.661 -10.800  1.00  0.00           H  \n",
            "HETATM  175 H175 TNS A   2     -11.069 -34.066  -3.600  1.00  0.00           H  \n",
            "HETATM  176 H176 TNS A   2     -11.069 -34.066   3.600  1.00  0.00           H  \n",
            "HETATM  177 H177 TNS A   2     -10.612 -32.661  10.800  1.00  0.00           H  \n",
            "HETATM  178 H178 TNS A   2      -9.634 -29.651  18.000  1.00  0.00           H  \n",
            "HETATM  179 H179 TNS A   2      -7.945 -24.451  25.200  1.00  0.00           H  \n",
            "HETATM  180 H180 TNS A   2      -4.849 -14.924  32.400  1.00  0.00           H  \n",
            "HETATM  181 H181 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM  182 H182 TNS A   2      -0.000  -0.000 -36.000  1.00  0.00           H  \n",
            "HETATM  183 H183 TNS A   2      -0.000 -15.692 -32.400  1.00  0.00           H  \n",
            "HETATM  184 H184 TNS A   2      -0.000 -25.709 -25.200  1.00  0.00           H  \n",
            "HETATM  185 H185 TNS A   2      -0.000 -31.177 -18.000  1.00  0.00           H  \n",
            "HETATM  186 H186 TNS A   2      -0.000 -34.342 -10.800  1.00  0.00           H  \n",
            "HETATM  187 H187 TNS A   2      -0.000 -35.820  -3.600  1.00  0.00           H  \n",
            "HETATM  188 H188 TNS A   2      -0.000 -35.820   3.600  1.00  0.00           H  \n",
            "HETATM  189 H189 TNS A   2      -0.000 -34.342  10.800  1.00  0.00           H  \n",
            "HETATM  190 H190 TNS A   2      -0.000 -31.177  18.000  1.00  0.00           H  \n",
            "HETATM  191 H191 TNS A   2      -0.000 -25.709  25.200  1.00  0.00           H  \n",
            "HETATM  192 H192 TNS A   2      -0.000 -15.692  32.400  1.00  0.00           H  \n",
            "HETATM  193 H193 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM  194 H194 TNS A   2       0.000  -0.000 -36.000  1.00  0.00           H  \n",
            "HETATM  195 H195 TNS A   2       4.849 -14.924 -32.400  1.00  0.00           H  \n",
            "HETATM  196 H196 TNS A   2       7.945 -24.451 -25.200  1.00  0.00           H  \n",
            "HETATM  197 H197 TNS A   2       9.634 -29.651 -18.000  1.00  0.00           H  \n",
            "HETATM  198 H198 TNS A   2      10.612 -32.661 -10.800  1.00  0.00           H  \n",
            "HETATM  199 H199 TNS A   2      11.069 -34.066  -3.600  1.00  0.00           H  \n",
            "HETATM  200 H200 TNS A   2      11.069 -34.066   3.600  1.00  0.00           H  \n",
            "HETATM  201 H201 TNS A   2      10.612 -32.661  10.800  1.00  0.00           H  \n",
            "HETATM  202 H202 TNS A   2       9.634 -29.651  18.000  1.00  0.00           H  \n",
            "HETATM  203 H203 TNS A   2       7.945 -24.451  25.200  1.00  0.00           H  \n",
            "HETATM  204 H204 TNS A   2       4.849 -14.924  32.400  1.00  0.00           H  \n",
            "HETATM  205 H205 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM  206 H206 TNS A   2       0.000  -0.000 -36.000  1.00  0.00           H  \n",
            "HETATM  207 H207 TNS A   2       9.224 -12.695 -32.400  1.00  0.00           H  \n",
            "HETATM  208 H208 TNS A   2      15.111 -20.799 -25.200  1.00  0.00           H  \n",
            "HETATM  209 H209 TNS A   2      18.325 -25.223 -18.000  1.00  0.00           H  \n",
            "HETATM  210 H210 TNS A   2      20.186 -27.783 -10.800  1.00  0.00           H  \n",
            "HETATM  211 H211 TNS A   2      21.054 -28.979  -3.600  1.00  0.00           H  \n",
            "HETATM  212 H212 TNS A   2      21.054 -28.979   3.600  1.00  0.00           H  \n",
            "HETATM  213 H213 TNS A   2      20.186 -27.783  10.800  1.00  0.00           H  \n",
            "HETATM  214 H214 TNS A   2      18.325 -25.223  18.000  1.00  0.00           H  \n",
            "HETATM  215 H215 TNS A   2      15.111 -20.799  25.200  1.00  0.00           H  \n",
            "HETATM  216 H216 TNS A   2       9.224 -12.695  32.400  1.00  0.00           H  \n",
            "HETATM  217 H217 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM  218 H218 TNS A   2       0.000  -0.000 -36.000  1.00  0.00           H  \n",
            "HETATM  219 H219 TNS A   2      12.695  -9.224 -32.400  1.00  0.00           H  \n",
            "HETATM  220 H220 TNS A   2      20.799 -15.111 -25.200  1.00  0.00           H  \n",
            "HETATM  221 H221 TNS A   2      25.223 -18.325 -18.000  1.00  0.00           H  \n",
            "HETATM  222 H222 TNS A   2      27.783 -20.186 -10.800  1.00  0.00           H  \n",
            "HETATM  223 H223 TNS A   2      28.979 -21.054  -3.600  1.00  0.00           H  \n",
            "HETATM  224 H224 TNS A   2      28.979 -21.054   3.600  1.00  0.00           H  \n",
            "HETATM  225 H225 TNS A   2      27.783 -20.186  10.800  1.00  0.00           H  \n",
            "HETATM  226 H226 TNS A   2      25.223 -18.325  18.000  1.00  0.00           H  \n",
            "HETATM  227 H227 TNS A   2      20.799 -15.111  25.200  1.00  0.00           H  \n",
            "HETATM  228 H228 TNS A   2      12.695  -9.224  32.400  1.00  0.00           H  \n",
            "HETATM  229 H229 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "HETATM  230 H230 TNS A   2       0.000  -0.000 -36.000  1.00  0.00           H  \n",
            "HETATM  231 H231 TNS A   2      14.924  -4.849 -32.400  1.00  0.00           H  \n",
            "HETATM  232 H232 TNS A   2      24.451  -7.945 -25.200  1.00  0.00           H  \n",
            "HETATM  233 H233 TNS A   2      29.651  -9.634 -18.000  1.00  0.00           H  \n",
            "HETATM  234 H234 TNS A   2      32.661 -10.612 -10.800  1.00  0.00           H  \n",
            "HETATM  235 H235 TNS A   2      34.066 -11.069  -3.600  1.00  0.00           H  \n",
            "HETATM  236 H236 TNS A   2      34.066 -11.069   3.600  1.00  0.00           H  \n",
            "HETATM  237 H237 TNS A   2      32.661 -10.612  10.800  1.00  0.00           H  \n",
            "HETATM  238 H238 TNS A   2      29.651  -9.634  18.000  1.00  0.00           H  \n",
            "HETATM  239 H239 TNS A   2      24.451  -7.945  25.200  1.00  0.00           H  \n",
            "HETATM  240 H240 TNS A   2      14.924  -4.849  32.400  1.00  0.00           H  \n",
            "HETATM  241 H241 TNS A   2      -0.000   0.000  36.000  1.00  0.00           H  \n",
            "CONECT    2    3   14  230                                                      \n",
            "CONECT    3    2    4   15  231                                                 \n",
            "CONECT    4    3    5   16  232                                                 \n",
            "CONECT    5    4    6   17  233                                                 \n",
            "CONECT    6    5    7   18  234                                                 \n",
            "CONECT    7    6    8   19  235                                                 \n",
            "CONECT    8    7    9   20  236                                                 \n",
            "CONECT    9    8   10   21  237                                                 \n",
            "CONECT   10    9   11   22  238                                                 \n",
            "CONECT   11   10   12   23  239                                                 \n",
            "CONECT   12   11   13   24  240                                                 \n",
            "CONECT   13   12   25  241                                                      \n",
            "CONECT   14    2   15   26                                                      \n",
            "CONECT   15   14    3   16   27                                                 \n",
            "CONECT   16   15    4   17   28                                                 \n",
            "CONECT   17   16    5   18   29                                                 \n",
            "CONECT   18   17    6   19   30                                                 \n",
            "CONECT   19   18    7   20   31                                                 \n",
            "CONECT   20   19    8   21   32                                                 \n",
            "CONECT   21   20    9   22   33                                                 \n",
            "CONECT   22   21   10   23   34                                                 \n",
            "CONECT   23   22   11   24   35                                                 \n",
            "CONECT   24   23   12   25   36                                                 \n",
            "CONECT   25   24   13   37                                                      \n",
            "CONECT   26   14   27   38                                                      \n",
            "CONECT   27   26   15   28   39                                                 \n",
            "CONECT   28   27   16   29   40                                                 \n",
            "CONECT   29   28   17   30   41                                                 \n",
            "CONECT   30   29   18   31   42                                                 \n",
            "CONECT   31   30   19   32   43                                                 \n",
            "CONECT   32   31   20   33   44                                                 \n",
            "CONECT   33   32   21   34   45                                                 \n",
            "CONECT   34   33   22   35   46                                                 \n",
            "CONECT   35   34   23   36   47                                                 \n",
            "CONECT   36   35   24   37   48                                                 \n",
            "CONECT   37   36   25   49                                                      \n",
            "CONECT   38   26   39   50                                                      \n",
            "CONECT   39   38   27   40   51                                                 \n",
            "CONECT   40   39   28   41   52                                                 \n",
            "CONECT   41   40   29   42   53                                                 \n",
            "CONECT   42   41   30   43   54                                                 \n",
            "CONECT   43   42   31   44   55                                                 \n",
            "CONECT   44   43   32   45   56                                                 \n",
            "CONECT   45   44   33   46   57                                                 \n",
            "CONECT   46   45   34   47   58                                                 \n",
            "CONECT   47   46   35   48   59                                                 \n",
            "CONECT   48   47   36   49   60                                                 \n",
            "CONECT   49   48   37   61                                                      \n",
            "CONECT   50   38   51   62                                                      \n",
            "CONECT   51   50   39   52   63                                                 \n",
            "CONECT   52   51   40   53   64                                                 \n",
            "CONECT   53   52   41   54   65                                                 \n",
            "CONECT   54   53   42   55   66                                                 \n",
            "CONECT   55   54   43   56   67                                                 \n",
            "CONECT   56   55   44   57   68                                                 \n",
            "CONECT   57   56   45   58   69                                                 \n",
            "CONECT   58   57   46   59   70                                                 \n",
            "CONECT   59   58   47   60   71                                                 \n",
            "CONECT   60   59   48   61   72                                                 \n",
            "CONECT   61   60   49   73                                                      \n",
            "CONECT   62   50   63   74                                                      \n",
            "CONECT   63   62   51   64   75                                                 \n",
            "CONECT   64   63   52   65   76                                                 \n",
            "CONECT   65   64   53   66   77                                                 \n",
            "CONECT   66   65   54   67   78                                                 \n",
            "CONECT   67   66   55   68   79                                                 \n",
            "CONECT   68   67   56   69   80                                                 \n",
            "CONECT   69   68   57   70   81                                                 \n",
            "CONECT   70   69   58   71   82                                                 \n",
            "CONECT   71   70   59   72   83                                                 \n",
            "CONECT   72   71   60   73   84                                                 \n",
            "CONECT   73   72   61   85                                                      \n",
            "CONECT   74   62   75   86                                                      \n",
            "CONECT   75   74   63   76   87                                                 \n",
            "CONECT   76   75   64   77   88                                                 \n",
            "CONECT   77   76   65   78   89                                                 \n",
            "CONECT   78   77   66   79   90                                                 \n",
            "CONECT   79   78   67   80   91                                                 \n",
            "CONECT   80   79   68   81   92                                                 \n",
            "CONECT   81   80   69   82   93                                                 \n",
            "CONECT   82   81   70   83   94                                                 \n",
            "CONECT   83   82   71   84   95                                                 \n",
            "CONECT   84   83   72   85   96                                                 \n",
            "CONECT   85   84   73   97                                                      \n",
            "CONECT   86   74   87   98                                                      \n",
            "CONECT   87   86   75   88   99                                                 \n",
            "CONECT   88   87   76   89  100                                                 \n",
            "CONECT   89   88   77   90  101                                                 \n",
            "CONECT   90   89   78   91  102                                                 \n",
            "CONECT   91   90   79   92  103                                                 \n",
            "CONECT   92   91   80   93  104                                                 \n",
            "CONECT   93   92   81   94  105                                                 \n",
            "CONECT   94   93   82   95  106                                                 \n",
            "CONECT   95   94   83   96  107                                                 \n",
            "CONECT   96   95   84   97  108                                                 \n",
            "CONECT   97   96   85  109                                                      \n",
            "CONECT   98   86   99  110                                                      \n",
            "CONECT   99   98   87  100  111                                                 \n",
            "CONECT  100   99   88  101  112                                                 \n",
            "CONECT  101  100   89  102  113                                                 \n",
            "CONECT  102  101   90  103  114                                                 \n",
            "CONECT  103  102   91  104  115                                                 \n",
            "CONECT  104  103   92  105  116                                                 \n",
            "CONECT  105  104   93  106  117                                                 \n",
            "CONECT  106  105   94  107  118                                                 \n",
            "CONECT  107  106   95  108  119                                                 \n",
            "CONECT  108  107   96  109  120                                                 \n",
            "CONECT  109  108   97  121                                                      \n",
            "CONECT  110   98  111  122                                                      \n",
            "CONECT  111  110   99  112  123                                                 \n",
            "CONECT  112  111  100  113  124                                                 \n",
            "CONECT  113  112  101  114  125                                                 \n",
            "CONECT  114  113  102  115  126                                                 \n",
            "CONECT  115  114  103  116  127                                                 \n",
            "CONECT  116  115  104  117  128                                                 \n",
            "CONECT  117  116  105  118  129                                                 \n",
            "CONECT  118  117  106  119  130                                                 \n",
            "CONECT  119  118  107  120  131                                                 \n",
            "CONECT  120  119  108  121  132                                                 \n",
            "CONECT  121  120  109  133                                                      \n",
            "CONECT  122  110  123  134                                                      \n",
            "CONECT  123  122  111  124  135                                                 \n",
            "CONECT  124  123  112  125  136                                                 \n",
            "CONECT  125  124  113  126  137                                                 \n",
            "CONECT  126  125  114  127  138                                                 \n",
            "CONECT  127  126  115  128  139                                                 \n",
            "CONECT  128  127  116  129  140                                                 \n",
            "CONECT  129  128  117  130  141                                                 \n",
            "CONECT  130  129  118  131  142                                                 \n",
            "CONECT  131  130  119  132  143                                                 \n",
            "CONECT  132  131  120  133  144                                                 \n",
            "CONECT  133  132  121  145                                                      \n",
            "CONECT  134  122  135  146                                                      \n",
            "CONECT  135  134  123  136  147                                                 \n",
            "CONECT  136  135  124  137  148                                                 \n",
            "CONECT  137  136  125  138  149                                                 \n",
            "CONECT  138  137  126  139  150                                                 \n",
            "CONECT  139  138  127  140  151                                                 \n",
            "CONECT  140  139  128  141  152                                                 \n",
            "CONECT  141  140  129  142  153                                                 \n",
            "CONECT  142  141  130  143  154                                                 \n",
            "CONECT  143  142  131  144  155                                                 \n",
            "CONECT  144  143  132  145  156                                                 \n",
            "CONECT  145  144  133  157                                                      \n",
            "CONECT  146  134  147  158                                                      \n",
            "CONECT  147  146  135  148  159                                                 \n",
            "CONECT  148  147  136  149  160                                                 \n",
            "CONECT  149  148  137  150  161                                                 \n",
            "CONECT  150  149  138  151  162                                                 \n",
            "CONECT  151  150  139  152  163                                                 \n",
            "CONECT  152  151  140  153  164                                                 \n",
            "CONECT  153  152  141  154  165                                                 \n",
            "CONECT  154  153  142  155  166                                                 \n",
            "CONECT  155  154  143  156  167                                                 \n",
            "CONECT  156  155  144  157  168                                                 \n",
            "CONECT  157  156  145  169                                                      \n",
            "CONECT  158  146  159  170                                                      \n",
            "CONECT  159  158  147  160  171                                                 \n",
            "CONECT  160  159  148  161  172                                                 \n",
            "CONECT  161  160  149  162  173                                                 \n",
            "CONECT  162  161  150  163  174                                                 \n",
            "CONECT  163  162  151  164  175                                                 \n",
            "CONECT  164  163  152  165  176                                                 \n",
            "CONECT  165  164  153  166  177                                                 \n",
            "CONECT  166  165  154  167  178                                                 \n",
            "CONECT  167  166  155  168  179                                                 \n",
            "CONECT  168  167  156  169  180                                                 \n",
            "CONECT  169  168  157  181                                                      \n",
            "CONECT  170  158  171  182                                                      \n",
            "CONECT  171  170  159  172  183                                                 \n",
            "CONECT  172  171  160  173  184                                                 \n",
            "CONECT  173  172  161  174  185                                                 \n",
            "CONECT  174  173  162  175  186                                                 \n",
            "CONECT  175  174  163  176  187                                                 \n",
            "CONECT  176  175  164  177  188                                                 \n",
            "CONECT  177  176  165  178  189                                                 \n",
            "CONECT  178  177  166  179  190                                                 \n",
            "CONECT  179  178  167  180  191                                                 \n",
            "CONECT  180  179  168  181  192                                                 \n",
            "CONECT  181  180  169  193                                                      \n",
            "CONECT  182  170  183  194                                                      \n",
            "CONECT  183  182  171  184  195                                                 \n",
            "CONECT  184  183  172  185  196                                                 \n",
            "CONECT  185  184  173  186  197                                                 \n",
            "CONECT  186  185  174  187  198                                                 \n",
            "CONECT  187  186  175  188  199                                                 \n",
            "CONECT  188  187  176  189  200                                                 \n",
            "CONECT  189  188  177  190  201                                                 \n",
            "CONECT  190  189  178  191  202                                                 \n",
            "CONECT  191  190  179  192  203                                                 \n",
            "CONECT  192  191  180  193  204                                                 \n",
            "CONECT  193  192  181  205                                                      \n",
            "CONECT  194  182  195  206                                                      \n",
            "CONECT  195  194  183  196  207                                                 \n",
            "CONECT  196  195  184  197  208                                                 \n",
            "CONECT  197  196  185  198  209                                                 \n",
            "CONECT  198  197  186  199  210                                                 \n",
            "CONECT  199  198  187  200  211                                                 \n",
            "CONECT  200  199  188  201  212                                                 \n",
            "CONECT  201  200  189  202  213                                                 \n",
            "CONECT  202  201  190  203  214                                                 \n",
            "CONECT  203  202  191  204  215                                                 \n",
            "CONECT  204  203  192  205  216                                                 \n",
            "CONECT  205  204  193  217                                                      \n",
            "CONECT  206  194  207  218                                                      \n",
            "CONECT  207  206  195  208  219                                                 \n",
            "CONECT  208  207  196  209  220                                                 \n",
            "CONECT  209  208  197  210  221                                                 \n",
            "CONECT  210  209  198  211  222                                                 \n",
            "CONECT  211  210  199  212  223                                                 \n",
            "CONECT  212  211  200  213  224                                                 \n",
            "CONECT  213  212  201  214  225                                                 \n",
            "CONECT  214  213  202  215  226                                                 \n",
            "CONECT  215  214  203  216  227                                                 \n",
            "CONECT  216  215  204  217  228                                                 \n",
            "CONECT  217  216  205  229                                                      \n",
            "CONECT  218  206  219  230                                                      \n",
            "CONECT  219  218  207  220  231                                                 \n",
            "CONECT  220  219  208  221  232                                                 \n",
            "CONECT  221  220  209  222  233                                                 \n",
            "CONECT  222  221  210  223  234                                                 \n",
            "CONECT  223  222  211  224  235                                                 \n",
            "CONECT  224  223  212  225  236                                                 \n",
            "CONECT  225  224  213  226  237                                                 \n",
            "CONECT  226  225  214  227  238                                                 \n",
            "CONECT  227  226  215  228  239                                                 \n",
            "CONECT  228  227  216  229  240                                                 \n",
            "CONECT  229  228  217  241                                                      \n",
            "CONECT  230  218    2  231                                                      \n",
            "CONECT  231  230  219    3  232                                                 \n",
            "CONECT  232  231  220    4  233                                                 \n",
            "CONECT  233  232  221    5  234                                                 \n",
            "CONECT  234  233  222    6  235                                                 \n",
            "CONECT  235  234  223    7  236                                                 \n",
            "CONECT  236  235  224    8  237                                                 \n",
            "CONECT  237  236  225    9  238                                                 \n",
            "CONECT  238  237  226   10  239                                                 \n",
            "CONECT  239  238  227   11  240                                                 \n",
            "CONECT  240  239  228   12  241                                                 \n",
            "CONECT  241  240  229   13                                                      \n",
            "MASTER        0    0    2    0    0    0    0    0  241    0  240    0          \n",
            "END                                                                             \n"
        ]

        # Check the data.
        self.strip_remarks(lines)
        self.assertEqual(len(real_data), len(lines))
        for i in range(len(lines)):
            self.assertEqual(real_data[i], lines[i])


    def test_delete_atom(self):
        """Test the deletion of a single atom using the U{structure.delete user function<http://www.nmr-relax.com/manual/structure_delete.html>}"""

        # Load the test structure.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'diffusion_tensor'+sep+'sphere'
        self.interpreter.structure.read_pdb(file='uniform.pdb', dir=path)

        # Delete some atoms, testing different combinations.
        self.interpreter.structure.delete(atom_id=':4@N', verbosity=1)
        self.interpreter.structure.delete(atom_id=':19', verbosity=1)
        self.interpreter.structure.delete(atom_id=':16@H', verbosity=1)
        self.interpreter.structure.delete(atom_id=':21-100', verbosity=1)

        # The expected atomic data after deletion.
        data = [
            ["N", "PRO",  1,   0.000,   0.000, -10.000,  0, [1]],
            ["H", "PRO",  1,   0.000,   0.000, -11.020,  1, [0]],
            ["N", "PRO",  2,   7.454,   0.000,  -6.667,  2, [3]],
            ["H", "PRO",  2,   8.214,   0.000,  -7.347,  3, [2]],
            ["N", "ILE",  3,  10.000,   0.000,   0.000,  4, [5]],
            ["H", "ILE",  3,  11.020,   0.000,   0.000,  5, [4]],
            ["H", "VAL",  4,   8.214,   0.000,   7.347,  6, []],
            ["N", "VAL",  5,   0.000,   0.000,  10.000,  7, [8]],
            ["H", "VAL",  5,   0.000,   0.000,  11.020,  8, [7]],
            ["N", "ASN",  6,   0.000,   0.000, -10.000,  9, [10]],
            ["H", "ASN",  6,   0.000,   0.000, -11.020, 10, [9]],
            ["N", "SER",  7,   3.727,   6.455,  -6.667, 11, [12]],
            ["H", "SER",  7,   4.107,   7.113,  -7.347, 12, [11]],
            ["N", "LEU",  8,   5.000,   8.660,   0.000, 13, [14]],
            ["H", "LEU",  8,   5.510,   9.544,   0.000, 14, [13]],
            ["N", "SER",  9,   3.727,   6.455,   6.667, 15, [16]],
            ["H", "SER",  9,   4.107,   7.113,   7.347, 16, [15]],
            ["N", "ASN", 10,   0.000,   0.000,  10.000, 17, [18]],
            ["H", "ASN", 10,   0.000,   0.000,  11.020, 18, [17]],
            ["N", "PHE", 11,  -0.000,   0.000, -10.000, 19, [20]],
            ["H", "PHE", 11,  -0.000,   0.000, -11.020, 20, [19]],
            ["N", "ALA", 12,  -3.727,   6.455,  -6.667, 21, [22]],
            ["H", "ALA", 12,  -4.107,   7.113,  -7.347, 22, [21]],
            ["N", "ILE", 13,  -5.000,   8.660,   0.000, 23, [24]],
            ["H", "ILE", 13,  -5.510,   9.544,   0.000, 24, [23]],
            ["N", "GLY", 14,  -3.727,   6.455,   6.667, 25, [26]],
            ["H", "GLY", 14,  -4.107,   7.113,   7.347, 26, [25]],
            ["N", "SER", 15,  -0.000,   0.000,  10.000, 27, [28]],
            ["H", "SER", 15,  -0.000,   0.000,  11.020, 28, [27]],
            ["N", "PHE", 16,  -0.000,   0.000, -10.000, 29, []],
            ["N", "VAL", 17,  -7.454,   0.000,  -6.667, 30, [31]],
            ["H", "VAL", 17,  -8.214,   0.000,  -7.347, 31, [30]],
            ["N", "ILE", 18, -10.000,   0.000,   0.000, 32, [33]],
            ["H", "ILE", 18, -11.020,   0.000,   0.000, 33, [32]],
            ["N", "LEU", 20,  -0.000,   0.000,  10.000, 34, [35]],
            ["H", "LEU", 20,  -0.000,   0.000,  11.020, 35, [34]]
        ]

        # The selection object.
        selection = cdp.structure.selection()

        # Check the structural object.
        mol = cdp.structure.structural_data[0].mol[0]
        self.assertEqual(len(data), len(mol.atom_name))
        for i in range(len(mol.atom_name)):
            print("Checking :%i@%s" % (data[i][2], data[i][0]))
            self.assertEqual(mol.atom_name[i], data[i][0])
            self.assertEqual(mol.res_name[i], data[i][1])
            self.assertEqual(mol.res_num[i], data[i][2])
            self.assertEqual(mol.x[i], data[i][3])
            self.assertEqual(mol.y[i], data[i][4])
            self.assertEqual(mol.z[i], data[i][5])
            self.assertEqual(mol.bonded[i], data[i][7])

        # Output PDB to stdout to help in debugging.
        self.interpreter.structure.write_pdb(file=sys.stdout)

        # Write out the file.
        self.tmpfile_handle, self.tmpfile = mkstemp(suffix='.pdb')
        self.interpreter.structure.write_pdb(self.tmpfile, force=True)

        # Read the contents of the file.
        file = open(self.tmpfile)
        lines = file.readlines()
        file.close()

        # Check the CONECT records.
        print("\nChecking CONECT records from the structure.write user function:")
        connected = [
            [ 0,  1],
            [ 1,  0],
            [ 2,  3],
            [ 3,  2],
            [ 4,  5],
            [ 5,  4],
            [ 7,  8],
            [ 8,  7],
            [ 9, 10],
            [10,  9],
            [11, 12],
            [12, 11],
            [13, 14],
            [14, 13],
            [15, 16],
            [16, 15],
            [17, 18],
            [18, 17],
            [19, 20],
            [20, 19],
            [21, 22],
            [22, 21],
            [23, 24],
            [24, 23],
            [25, 26],
            [26, 25],
            [27, 28],
            [28, 27],
            [30, 31],
            [31, 30],
            [32, 33],
            [33, 32],
            [34, 35],
            [35, 34]
        ]
        i = 0
        for line in lines:
            # Not a CONECT record.
            if not search('^CONECT', line):
                continue

            # Debugging printout.
            sys.stdout.write(line)

            # Split up the line.
            row = line.split()

            # Check and increment.
            self.assertEqual(int(row[1]), connected[i][0]+1)
            self.assertEqual(int(row[2]), connected[i][1]+1)
            i += 1


    def test_delete_empty(self):
        """Test the deletion of non-existent structural data."""

        # Delete all structural data.
        self.interpreter.structure.delete()


    def test_delete_model(self):
        """Test the deletion of a single structural model."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file as two models.
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_model_num=1)
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_model_num=2)

        # Test the structure metadata.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 2)
        self.assertEqual(cdp.structure.structural_data[0].num, 1)
        self.assertEqual(cdp.structure.structural_data[1].num, 2)

        # Delete model 1.
        self.interpreter.structure.delete(model=1)

        # Test the structure metadata.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(cdp.structure.structural_data[0].num, 2)

        # Load another model, then delete it.
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_model_num=3)
        self.interpreter.structure.delete(model=3)

        # Test the structure metadata.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(cdp.structure.structural_data[0].num, 2)

        # Load another model, then delete number 2.
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_model_num=10)
        self.interpreter.structure.delete(model=2)

        # Test the structure metadata.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(cdp.structure.structural_data[0].num, 10)


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
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertEqual(len(cdp.structure.structural_data), 0)
        self.interpreter.pipe.switch('mf')
        self.assertTrue(hasattr(cdp, 'structure'))
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
        ids = ['model 1, Ap4Aase_res1-12_mol1', 'model 2, Ap4Aase_res1-12_mol1']
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
        self.assertTrue(hasattr(cdp.structure, 'displacements'))
        for i in range(len(ids)):
            for j in range(len(ids)):
                # Check the translation.
                self.assertAlmostEqual(cdp.structure.displacements._translation_distance[ids[i]][ids[j]], dist[i][j])
                for k in range(3):
                    self.assertAlmostEqual(cdp.structure.displacements._translation_vector[ids[i]][ids[j]][k], trans_vect[i][j][k])

                # Check the rotation.
                self.assertAlmostEqual(cdp.structure.displacements._rotation_angle[ids[i]][ids[j]], angle[i][j])
                if rot_axis[i][j] != None:
                    for k in range(3):
                        self.assertAlmostEqual(cdp.structure.displacements._rotation_axis[ids[i]][ids[j]][k], rot_axis[i][j][k])

        # Save the results.
        self.tmpfile_handle, self.tmpfile = mkstemp(suffix='.bz2')
        self.interpreter.state.save(self.tmpfile, dir=None, force=True)

        # Reset relax.
        self.interpreter.reset()

        # Load the results.
        self.interpreter.state.load(self.tmpfile)

        # Test the re-loaded data.
        self.assertTrue(hasattr(cdp.structure, 'displacements'))
        for i in range(len(ids)):
            for j in range(len(ids)):
                # Check the translation.
                self.assertAlmostEqual(cdp.structure.displacements._translation_distance[ids[i]][ids[j]], dist[i][j])
                for k in range(3):
                    self.assertAlmostEqual(cdp.structure.displacements._translation_vector[ids[i]][ids[j]][k], trans_vect[i][j][k])

                # Check the rotation.
                self.assertAlmostEqual(cdp.structure.displacements._rotation_angle[ids[i]][ids[j]], angle[i][j])
                if rot_axis[i][j] != None:
                    for k in range(3):
                        self.assertAlmostEqual(cdp.structure.displacements._rotation_axis[ids[i]][ids[j]][k], rot_axis[i][j][k])


    def test_displacement_molecules(self):
        """Test of the structure.displacement user function for different molecules in one pipe.

        This checks the molecules argument of the U{structure.displacement user function<http://www.nmr-relax.com/manual/structure_displacement.html>}.
        """

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file as two molecules.
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_mol_name='1')
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_mol_name='2')

        # A rotation.
        R = zeros((3, 3), float64)
        euler_to_R_zyz(1.3, 0.4, 4.5, R)

        # Rotate the second molecule.
        self.interpreter.structure.rotate(R, atom_id='#2')

        # Calculate the displacement.
        self.interpreter.structure.displacement(molecules=[['1', '2']])

        # Shift a third structure back using the calculated displacement.
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_mol_name='3')
        self.interpreter.structure.rotate(R, atom_id='#3')

        # The data to check.
        ids = ['1', '2']
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
        self.assertTrue(hasattr(cdp.structure, 'displacements'))
        for i in range(len(ids)):
            for j in range(len(ids)):
                # Check the translation.
                self.assertAlmostEqual(cdp.structure.displacements._translation_distance[ids[i]][ids[j]], dist[i][j])
                for k in range(3):
                    self.assertAlmostEqual(cdp.structure.displacements._translation_vector[ids[i]][ids[j]][k], trans_vect[i][j][k])

                # Check the rotation.
                self.assertAlmostEqual(cdp.structure.displacements._rotation_angle[ids[i]][ids[j]], angle[i][j])
                if rot_axis[i][j] != None:
                    for k in range(3):
                        self.assertAlmostEqual(cdp.structure.displacements._rotation_axis[ids[i]][ids[j]][k], rot_axis[i][j][k])

        # Save the results.
        self.tmpfile_handle, self.tmpfile = mkstemp(suffix='.bz2')
        self.interpreter.state.save(self.tmpfile, dir=None, force=True)

        # Reset relax.
        self.interpreter.reset()

        # Load the results.
        self.interpreter.state.load(self.tmpfile)

        # Test the re-loaded data.
        self.assertTrue(hasattr(cdp.structure, 'displacements'))
        for i in range(len(ids)):
            for j in range(len(ids)):
                # Check the translation.
                self.assertAlmostEqual(cdp.structure.displacements._translation_distance[ids[i]][ids[j]], dist[i][j])
                for k in range(3):
                    self.assertAlmostEqual(cdp.structure.displacements._translation_vector[ids[i]][ids[j]][k], trans_vect[i][j][k])

                # Check the rotation.
                self.assertAlmostEqual(cdp.structure.displacements._rotation_angle[ids[i]][ids[j]], angle[i][j])
                if rot_axis[i][j] != None:
                    for k in range(3):
                        self.assertAlmostEqual(cdp.structure.displacements._rotation_axis[ids[i]][ids[j]][k], rot_axis[i][j][k])


    def test_find_pivot(self):
        """Test the structure.find_pivot user function.

        This checks the default operation of the U{structure.find_pivot user function<http://www.nmr-relax.com/manual/structure_find_pivot.html>}.
        """

        # Path of the PDB file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the PDB three times as different models.
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_model_num=1)
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_model_num=2)
        self.interpreter.structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path, set_model_num=3)

        # Rotate two of the models (the pivot will be the origin).
        pivot = [1., 2., 3.]
        R = zeros((3, 3), float64)
        axis_angle_to_R(array([1, 0, 0], float64), 0.1, R)
        self.interpreter.structure.rotate(R=R, model=2, origin=pivot)
        axis_angle_to_R(array([0, 1, 0], float64), 0.2, R)
        self.interpreter.structure.rotate(R=R, model=3, origin=pivot)

        # Find the pivot.
        self.interpreter.structure.find_pivot(init_pos=[0.95, 2.05, 3.02])

        # Check the pivot.
        self.assertAlmostEqual(cdp.structure.pivot[0], pivot[0], 3)
        self.assertAlmostEqual(cdp.structure.pivot[1], pivot[1], 3)
        self.assertAlmostEqual(cdp.structure.pivot[2], pivot[2], 3)


    def test_find_pivot_molecules(self):
        """Test the structure.find_pivot user function.

        This checks the U{structure.find_pivot user function<http://www.nmr-relax.com/manual/structure_find_pivot.html>} when the molecules argument is given.
        """

        # Path of the PDB file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'diffusion_tensor'+sep+'sphere'

        # Load the PDB twice as different molecules.
        self.interpreter.structure.read_pdb('uniform.pdb', dir=path, set_mol_name='X')
        self.interpreter.structure.read_pdb('uniform.pdb', dir=path, set_mol_name='Y')
        self.interpreter.structure.read_pdb('uniform.pdb', dir=path, set_mol_name='Z')

        # Delete some structural info.
        self.interpreter.structure.delete("#X:8")
        self.interpreter.structure.delete("#X:2@N")
        self.interpreter.structure.delete("#Y:12")
        self.interpreter.structure.delete("#Y:20@H")

        # Rotate two of the models (the pivot will be the origin).
        pivot = [1., 2., 3.]
        R = zeros((3, 3), float64)
        axis_angle_to_R(array([1, 0, 0], float64), 0.1, R)
        self.interpreter.structure.rotate(R=R, atom_id='#Y', origin=pivot)
        axis_angle_to_R(array([0, 1, 0], float64), 0.2, R)
        self.interpreter.structure.rotate(R=R, atom_id='#Z', origin=pivot)

        # Find the pivot.
        self.interpreter.structure.find_pivot(molecules=[['X', 'Y', 'Z']], init_pos=[0.95, 2.05, 3.02], func_tol=1e-7)

        # Check the pivot.
        self.assertAlmostEqual(cdp.structure.pivot[0], pivot[0], 3)
        self.assertAlmostEqual(cdp.structure.pivot[1], pivot[1], 3)
        self.assertAlmostEqual(cdp.structure.pivot[2], pivot[2], 3)


    def test_get_model(self):
        """Test the get_model() method of the internal structural object."""

        # Create 2 models.
        self.interpreter.structure.add_model(model_num=1)
        self.interpreter.structure.add_model(model_num=2)

        # Get the first model.
        model = cdp.structure.get_model(1)

        # Check it.
        self.assertNotEqual(model, None)
        self.assertEqual(model.num, 1)
        self.assertEqual(len(model.mol), 0)


    def test_load_internal_results(self):
        """Load the PDB file using the information in a results file (using the internal structural object)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the results file.
        self.interpreter.results.read(file='str_internal', dir=path)

        # Test the structure metadata.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertTrue(len(cdp.structure.structural_data))
        self.assertTrue(len(cdp.structure.structural_data[0].mol))

        mol = cdp.structure.structural_data[0].mol[0]
        self.assertEqual(mol.file_name, 'Ap4Aase_res1-12.pdb')
        self.assertEqual(mol.file_path, '')
        self.assertEqual(mol.file_model, 1)
        self.assertEqual(mol.file_mol_num, 1)

        # The real atomic data.
        atom_name = ['N', 'CA', '1HA', '2HA', 'C', 'O', '1HT', '2HT', '3HT', 'N', 'CD', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', '1HG', '2HG', '1HD', '2HD', 'C', 'O', 'N', 'H', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', 'HG', 'CD1', '1HD1', '2HD1', '3HD1', 'CD2', '1HD2', '2HD2', '3HD2', 'C', 'O', 'N', 'H', 'CA', '1HA', '2HA', 'C', 'O', 'N', 'H', 'CA', 'HA', 'CB', '1HB', '2HB', 'OG', 'HG', 'C', 'O', 'N', 'H', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', '1HG', '2HG', 'SD', 'CE', '1HE', '2HE', '3HE', 'C', 'O', 'N', 'H', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', 'OD1', 'OD2', 'C', 'O', 'N', 'H', 'CA', 'HA', 'CB', '1HB', '2HB', 'OG', 'HG', 'C', 'O', 'N', 'CD', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', '1HG', '2HG', '1HD', '2HD', 'C', 'O', 'N', 'CD', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', '1HG', '2HG', '1HD', '2HD', 'C', 'O', 'N', 'H', 'CA', 'HA', 'CB', '1HB', '2HB', 'CG', '1HG', '2HG', 'CD', 'OE1', 'OE2', 'C', 'O', 'N', 'H', 'CA', '1HA', '2HA', 'C', 'O']
        bonded = [[]]*174
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


    def test_load_spins_mol_cat(self):
        """Test the loading of spins from different molecules into one molecule container."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDBs.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, set_mol_name='L1')
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_2.pdb', dir=path, set_mol_name='L2')

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


    def test_load_spins_multi_mol(self):
        """Test the structure.load_spins user function for loading the same spins from multiple molecules."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDBs.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path, set_mol_name='L1')
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_2.pdb', dir=path, set_mol_name='L2')

        # Delete one of the atoms.
        self.interpreter.structure.delete(atom_id='#L2:900@C1')
        self.interpreter.structure.delete(atom_id='#L1:900@C3')

        # Atom renumbering of the second molecule, to follow from the last atom 103 of the first structure (simulate a single PDB file).
        for i in range(len(cdp.structure.structural_data[0].mol[1].atom_num)):
            cdp.structure.structural_data[0].mol[1].atom_num[i] = i + 104

        # Load a few carbons.
        self.interpreter.structure.load_spins(':900@C1,C2,C3', from_mols=['L1', 'L2'], mol_name_target='Lactose')

        # Check the sequence data.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'Lactose')
        self.assertEqual(len(cdp.mol[0].res), 1)
        self.assertEqual(cdp.mol[0].res[0].name, 'UNK')
        self.assertEqual(cdp.mol[0].res[0].num, 900)
        self.assertEqual(len(cdp.mol[0].res[0].spin), 3)

        # Check the @C1 spin data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'C1')
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, None)
        self.assertEqual(len(cdp.mol[0].res[0].spin[0].pos), 2)
        self.assertEqual(cdp.mol[0].res[0].spin[0].pos[0][0], 6.250)
        self.assertEqual(cdp.mol[0].res[0].spin[0].pos[0][1], 0.948)
        self.assertEqual(cdp.mol[0].res[0].spin[0].pos[0][2], 1.968)
        self.assertEqual(cdp.mol[0].res[0].spin[0].pos[1], None)

        # Check the @C2 spin data.
        self.assertEqual(cdp.mol[0].res[0].spin[1].name, 'C2')
        self.assertEqual(cdp.mol[0].res[0].spin[1].num, None)
        self.assertEqual(len(cdp.mol[0].res[0].spin[1].pos), 2)
        self.assertEqual(cdp.mol[0].res[0].spin[1].pos[0][0], 6.250)
        self.assertEqual(cdp.mol[0].res[0].spin[1].pos[0][1], 2.488)
        self.assertEqual(cdp.mol[0].res[0].spin[1].pos[0][2], 2.102)
        self.assertEqual(cdp.mol[0].res[0].spin[1].pos[1][0], 6.824)
        self.assertEqual(cdp.mol[0].res[0].spin[1].pos[1][1], 0.916)
        self.assertEqual(cdp.mol[0].res[0].spin[1].pos[1][2], 2.283)

        # Check the @C3 spin data.
        self.assertEqual(cdp.mol[0].res[0].spin[2].name, 'C3')
        self.assertEqual(cdp.mol[0].res[0].spin[2].num, None)
        self.assertEqual(len(cdp.mol[0].res[0].spin[2].pos), 2)
        self.assertEqual(cdp.mol[0].res[0].spin[2].pos[0], None)
        self.assertEqual(cdp.mol[0].res[0].spin[2].pos[1][0], 8.062)
        self.assertEqual(cdp.mol[0].res[0].spin[2].pos[1][1], 0.431)
        self.assertEqual(cdp.mol[0].res[0].spin[2].pos[1][2], 3.048)


    def test_mean(self):
        """Test the U{structure.mean user function<http://www.nmr-relax.com/manual/structure_mean.html>}."""

        # Create 2 models.
        self.interpreter.structure.add_model(model_num=1)
        self.interpreter.structure.add_model(model_num=2)

        # Add a single atom.
        self.interpreter.structure.add_atom(atom_name='N', res_name='Tyr', res_num=2, pos=[[0., 0., 0.], [1., 2., -2.]], element='N')
        self.interpreter.structure.add_atom(atom_name='N', res_name='Phe', res_num=3, pos=[[-1., -2., 2.], [1., 2., -2.]], element='N')

        # Calculate the mean.
        self.interpreter.structure.mean()

        # Test the molecule data.
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 1)
        self.assertEqual(cdp.structure.structural_data[0].num, None)
        mol = cdp.structure.structural_data[0].mol[0]
        self.assertEqual(len(mol.atom_name), 2)
        self.assertEqual(mol.atom_name, ['N', 'N'])
        self.assertEqual(mol.atom_num, [None, None])
        self.assertEqual(mol.bonded, [[], []])
        self.assertEqual(mol.element, ['N', 'N'])
        self.assertEqual(mol.pdb_record, [None, None])
        self.assertEqual(mol.res_name, ['Tyr', 'Phe'])
        self.assertEqual(mol.res_num, [2, 3])
        self.assertEqual(mol.seg_id, [None, None])
        self.assertEqual(mol.x, [0.5, 0.0])
        self.assertEqual(mol.y, [1.0, 0.0])
        self.assertEqual(mol.z, [-1.0, 0.0])


    def test_mean_models(self):
        """Test the structure.mean user function for different models.

        This checks the molecules argument of the U{structure.mean user function<http://www.nmr-relax.com/manual/structure_mean.html>}.
        """

        # Set up 3 models.
        self.interpreter.structure.add_model(model_num=1)
        self.interpreter.structure.add_model(model_num=2)
        self.interpreter.structure.add_model(model_num=4)

        # Check that the models were correctly created.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 3)

        # Create a structure with some atoms.
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=1, pos=[[1., 0., -1.], [0., 0., 0.], [-1., 0., 1.]], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=2, pos=[[1., 2., -1.], [0., 2., 0.], [-1., 2., 1.]], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=3, pos=[[1., 20., -1.], [0., 20., 0.], [-1., 20., 1.]], element='S')

        # Calculate the mean structure and store it as model 3.
        self.interpreter.structure.mean(models=[[1, 2, 4]], set_model_num=3)

        # The expected data.
        model_num = [1, 2, 4, 3]
        x = [
            [1., 1., 1.],
            [0., 0., 0.],
            [-1., -1., -1.],
            [0., 0., 0.]
        ]
        y = [0., 2., 20.]
        z = [
            [-1., -1., -1.],
            [0., 0., 0.],
            [1., 1., 1.],
            [0., 0., 0.]
        ]

        # Check the internal atomic info.
        self.assertEqual(len(cdp.structure.structural_data), 4)
        for i in range(4):
            self.assertEqual(len(cdp.structure.structural_data[i].mol), 1)
            self.assertEqual(cdp.structure.structural_data[i].num, model_num[i])
            self.assertEqual(cdp.structure.structural_data[i].mol[0].atom_num, [None, None, None])
            self.assertEqual(cdp.structure.structural_data[i].mol[0].atom_name, ['A', 'A', 'A'])
            self.assertEqual(cdp.structure.structural_data[i].mol[0].bonded, [[], [], []])
            self.assertEqual(cdp.structure.structural_data[i].mol[0].element, ['S', 'S', 'S'])
            self.assertEqual(cdp.structure.structural_data[i].mol[0].pdb_record, [None, None, None])
            self.assertEqual(cdp.structure.structural_data[i].mol[0].res_name, ['UNK', 'UNK', 'UNK'])
            self.assertEqual(cdp.structure.structural_data[i].mol[0].res_num, [1, 2, 3])
            self.assertEqual(cdp.structure.structural_data[i].mol[0].seg_id, [None, None, None])
            self.assertEqual(cdp.structure.structural_data[i].mol[0].x, x[i])
            self.assertEqual(cdp.structure.structural_data[i].mol[0].y, y)
            self.assertEqual(cdp.structure.structural_data[i].mol[0].z, z[i])


    def test_mean_molecules(self):
        """Test the structure.mean user function for different molecules in one pipe.

        This checks the molecules argument of the U{structure.mean user function<http://www.nmr-relax.com/manual/structure_mean.html>}.
        """

        # Create three molecules 'X', 'Y', and 'Z' with a some atoms.
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=1, mol_name='X', pos=[1., 0., -1.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=1, mol_name='Y', pos=[0., 0., 0.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=1, mol_name='Z', pos=[-1., 0., 1.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=2, mol_name='X', pos=[1., 2., -1.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=2, mol_name='Y', pos=[0., 2., 0.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=2, mol_name='Z', pos=[-1., 2., 1.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=3, mol_name='X', pos=[1., 20., -1.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=3, mol_name='Y', pos=[0., 20., 0.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=3, mol_name='Z', pos=[-1., 20., 1.], element='S')

        # Calculate the mean structure.
        self.interpreter.structure.mean(molecules=[['X', 'Y', 'Z']], set_mol_name='A')

        # The expected data.
        mol_name = ['X', 'Y', 'Z', 'A']
        x = [
            [1., 1., 1.],
            [0., 0., 0.],
            [-1., -1., -1.],
            [0., 0., 0.]
        ]
        y = [0., 2., 20.]
        z = [
            [-1., -1., -1.],
            [0., 0., 0.],
            [1., 1., 1.],
            [0., 0., 0.]
        ]

        # Check the internal atomic info.
        self.assertEqual(len(cdp.structure.structural_data), 1)
        for i in range(4):
            self.assertEqual(len(cdp.structure.structural_data[0].mol), 4)
            self.assertEqual(cdp.structure.structural_data[0].mol[i].mol_name, mol_name[i])
            self.assertEqual(cdp.structure.structural_data[0].mol[i].atom_num, [None, None, None])
            self.assertEqual(cdp.structure.structural_data[0].mol[i].atom_name, ['A', 'A', 'A'])
            self.assertEqual(cdp.structure.structural_data[0].mol[i].bonded, [[], [], []])
            self.assertEqual(cdp.structure.structural_data[0].mol[i].element, ['S', 'S', 'S'])
            self.assertEqual(cdp.structure.structural_data[0].mol[i].pdb_record, [None, None, None])
            self.assertEqual(cdp.structure.structural_data[0].mol[i].res_name, ['UNK', 'UNK', 'UNK'])
            self.assertEqual(cdp.structure.structural_data[0].mol[i].res_num, [1, 2, 3])
            self.assertEqual(cdp.structure.structural_data[0].mol[i].seg_id, [None, None, None])
            self.assertEqual(cdp.structure.structural_data[0].mol[i].x, x[i])
            self.assertEqual(cdp.structure.structural_data[0].mol[i].y, y)
            self.assertEqual(cdp.structure.structural_data[0].mol[i].z, z[i])


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
        self.tmpfile_handle, self.tmpfile = mkstemp(suffix='.bz2')
        self.interpreter.results.write(self.tmpfile, dir=None, force=True)

        # Create a new data pipe and load the results.
        self.interpreter.pipe.create('xml text', 'mf')
        self.interpreter.results.read(self.tmpfile)

        # What the data should look like.
        helices = [
            ['H1', 0, 'ILE', 23, 0, 'GLU', 34, 1, 12]
        ]
        sheets = [
            [1, 'BET', 5, 'GLY', 0, 10, None, 'VAL', 0, 17, None, 0, None, None, None, None, None, None, None, None, None, None],
            [2, 'BET', 5, 'MET', 0, 1, None, 'THR', 0, 7, None, -1, None, None, None, None, None, None, None, None, None, None]
        ]

        # Check the helix data.
        self.assertTrue(hasattr(cdp.structure, 'helices'))
        self.assertEqual(len(cdp.structure.helices), 1)
        self.assertEqual(cdp.structure.helices[0], helices[0])

        # Check the sheet data.
        self.assertTrue(hasattr(cdp.structure, 'sheets'))
        self.assertEqual(len(cdp.structure.sheets), 2)
        self.assertEqual(cdp.structure.sheets[0], sheets[0])
        self.assertEqual(cdp.structure.sheets[1], sheets[1])


    def test_multi_model_and_multi_molecule(self):
        """Test the loading and writing of a multi-model and multi-molecule PDB file."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Load the file.
        self.interpreter.structure.read_pdb('multi_model_and_mol_test.pdb', dir=path)

        # Check the model consistency.
        cdp.structure.validate_models()

        # Create a PDB file.
        file = DummyFileObject()
        self.interpreter.structure.write_pdb(file=file, force=True)

        # The file contents, without remarks, as they should be.
        contents = [
            "MODEL        1                                                                  \n",
            "ATOM      1  N   LEU A   1       1.000  -2.000  20.000  1.00  0.00           N  \n",
            "ATOM      2  H   LEU A   1       2.000  -2.000  20.000  1.00  0.00           H  \n",
            "TER       3      LEU A   1                                                      \n",
            "ATOM      4  N   LEU B   1       9.000  -9.000  27.000  1.00  0.00           N  \n",
            "ATOM      5  H   LEU B   1       8.000  -8.000  27.000  1.00  0.00           H  \n",
            "TER       6      LEU B   1                                                      \n",
            "ATOM      7  N   LEU C   1      12.000 -12.000   7.000  1.00  0.00           N  \n",
            "ATOM      8  H   LEU C   1      11.000 -12.000   7.000  1.00  0.00           H  \n",
            "TER       9      LEU C   1                                                      \n",
            "ENDMDL                                                                          \n",
            "MODEL        2                                                                  \n",
            "ATOM      1  N   LEU A   1       1.000  -2.000  20.000  1.00  0.00           N  \n",
            "ATOM      2  H   LEU A   1       2.000  -2.000  20.000  1.00  0.00           H  \n",
            "TER       3      LEU A   1                                                      \n",
            "ATOM      4  N   LEU B   1       9.000  -9.000  27.000  1.00  0.00           N  \n",
            "ATOM      5  H   LEU B   1       8.000  -8.000  27.000  1.00  0.00           H  \n",
            "TER       6      LEU B   1                                                      \n",
            "ATOM      7  N   LEU C   1      12.000 -12.000   7.000  1.00  0.00           N  \n",
            "ATOM      8  H   LEU C   1      11.000 -12.000   7.000  1.00  0.00           H  \n",
            "TER       9      LEU C   1                                                      \n",
            "ENDMDL                                                                          \n",
            "MASTER        0    0    0    0    0    0    0    0    6    3    0    0          \n",
            "END                                                                             \n"
        ]

        # Check the created PDB file.
        lines = file.readlines()
        self.strip_remarks(lines)
        self.assertEqual(len(contents), len(lines))
        for i in range(len(lines)):
            self.assertEqual(contents[i], lines[i])


    def test_pca(self):
        """Test the principle component analysis of the structure.pca user function."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'structure'+sep+'pca.py')

        # The Gromacs values (converted from nm to Angstrom).
        values = array([0.417808, 0.0164377, 0.000675256, 1.17952e-05], float64) * 100
        proj = array([
            [-0.38735,  0.21143, -0.02325, -0.00119],
            [ 0.96087,  0.07893,  0.02651,  0.00209],
            [-0.84236, -0.05173,  0.03651, -0.00140],
            [-0.23302, -0.11191, -0.02209,  0.00530],
            [ 0.50186, -0.12672, -0.01767, -0.00481]
        ], float64) * 10

        # Invert the 3rd and 4th Gromacs eigenvectors to match.
        proj[:, 2] = -proj[:, 2]
        proj[:, 3] = -proj[:, 3]

        # Are more inversion necessary?
        for mode in range(4):
            if sign(cdp.structure.pca_proj[mode][0]) != sign(proj[0][mode]):
                proj[:, mode] = -proj[:, mode]

        # Checks.
        self.assertTrue(hasattr(cdp.structure, 'pca_values'))
        self.assertTrue(hasattr(cdp.structure, 'pca_vectors'))
        self.assertTrue(hasattr(cdp.structure, 'pca_proj'))
        self.assertEqual(len(cdp.structure.pca_values), 4)
        for mode in range(4):
            self.assertAlmostEqual(cdp.structure.pca_values[mode], values[mode], 5)
            for struct in range(5):
                self.assertAlmostEqual(cdp.structure.pca_proj[mode, struct], proj[struct, mode], 4)


    def test_pca_observers(self):
        """Test the principle component analysis of the structure.pca user function while using observer molecules."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'structure'+sep+'pca_observers.py')

        # The Gromacs values (converted from nm to Angstrom).
        values = array([0.417808, 0.0164377, 0.000675256, 1.17952e-05], float64) * 100
        proj = array([
            [-0.38735,  0.21143, -0.02325, -0.00119],
            [ 0.96087,  0.07893,  0.02651,  0.00209],
            [-0.84236, -0.05173,  0.03651, -0.00140],
            [-0.23302, -0.11191, -0.02209,  0.00530],
            [ 0.50186, -0.12672, -0.01767, -0.00481]
        ], float64) * 10

        # Invert the 3rd and 4th Gromacs eigenvectors to match.
        proj[:, 2] = -proj[:, 2]
        proj[:, 3] = -proj[:, 3]

        # Are more inversion necessary?
        for mode in range(4):
            if sign(cdp.structure.pca_proj[mode][0]) != sign(proj[0][mode]):
                proj[:, mode] = -proj[:, mode]

        # Checks.
        self.assertTrue(hasattr(cdp.structure, 'pca_values'))
        self.assertTrue(hasattr(cdp.structure, 'pca_vectors'))
        self.assertTrue(hasattr(cdp.structure, 'pca_proj'))
        self.assertEqual(len(cdp.structure.pca_values), 4)
        for mode in range(4):
            self.assertAlmostEqual(cdp.structure.pca_values[mode], values[mode], 5)
            for struct in range(5):
                self.assertAlmostEqual(cdp.structure.pca_proj[mode, struct], proj[struct, mode], 4)


    def test_pdb_combined_secondary_structure(self):
        """Test the handling of secondary structure metadata when combining multiple PDB structures."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read a PDB file twice as two different molecules.
        self.interpreter.structure.read_pdb('1J7O.pdb', dir=path, set_mol_name='N-dom', read_model=1, set_model_num=1)
        self.interpreter.structure.read_pdb('1J7P.pdb', dir=path, set_mol_name='C-dom', read_model=1, set_model_num=1)

        # Create a PDB file.
        file = DummyFileObject()
        self.interpreter.structure.write_pdb(file=file, force=True)

        # The file secondary structure contents, as they should be.
        contents = [
            "HELIX    1   1 THR A    5  ASP A   20  1                                  16    \n",
            "HELIX    2   2 THR A   28  LEU A   39  1                                  12    \n",
            "HELIX    3   3 THR A   44  GLU A   54  1                                  11    \n",
            "HELIX    4   4 ASP A   64  MET A   76  1                                  13    \n",
            "HELIX    5   1 GLU B   82  ASP B   93  1                                  12    \n",
            "HELIX    6   2 SER B  101  LEU B  112  1                                  12    \n",
            "HELIX    7   3 THR B  117  ASP B  129  1                                  13    \n",
            "HELIX    8   4 TYR B  138  THR B  146  1                                   9    \n",
            "SHEET    1   A 2 TYR B  99  ILE B 100  0                                        \n",
            "SHEET    2   A 2 VAL B 136  ASN B 137 -1  O  VAL B 136   N  ILE B 100           \n"
        ]

        # Check secondary structure contents of the created PDB file.
        lines = file.readlines()
        index = 0
        print("\n\nChecking the records:\n")
        for i in range(len(lines)):
            # Only secondary structure records.
            if lines[i][:5] not in ['HELIX', 'SHEET']:
                continue

            # Check and increment the index.
            print(lines[i][:-1])
            self.assertEqual(contents[index], lines[i])
            index += 1


    def test_read_gaussian_strychnine(self):
        """Load the structure from the 'strychnine_opt_cdcl3_b3lyp_gaussian.log.bz2' compressed Gaussian log file."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the XYZ file.
        self.interpreter.structure.read_gaussian(file='strychnine_opt_cdcl3_b3lyp_gaussian.log.bz2', dir=path, set_mol_name='strychnine')

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

        # The actual data.
        data = [
            [ 5, 'C', -0.258837, -2.073956, -0.558021],
            [ 6, 'C', -0.824223, -1.406962, -1.808433],
            [ 7, 'C', -1.741283, -0.250780, -1.378644],
            [ 8, 'C', -0.819735,  0.828965, -0.783392],
            [ 9, 'C',  0.003153,  0.334416,  0.415455],
            [10, 'C',  2.358372,  0.448322,  0.162421],
            [11, 'C',  3.667689,  0.888405, -0.010558],
            [12, 'C',  4.632616, -0.056196, -0.360560],
            [13, 'C',  4.303015, -1.398582, -0.525823],
            [14, 'C',  2.988069, -1.825141, -0.331972],
            [15, 'C',  2.015427, -0.899636,  0.012625],
            [16, 'C',  0.561728, -1.122705,  0.360284],
            [17, 'C',  0.390886, -1.834862,  1.723978],
            [18, 'C', -1.067936, -2.282629,  1.709808],
            [19, 'C', -2.708975, -2.252045, -0.131301],
            [20, 'C', -2.815469, -0.775379, -0.431910],
            [21, 'C', -3.718174,  0.023460,  0.134879],
            [22, 'C', -3.726395,  1.516213, -0.058936],
            [23, 'C', -1.423939,  2.193179, -0.407936],
            [24, 'C', -0.372897,  3.059448,  0.332496],
            [25, 'C',  1.064718,  2.558120,  0.325331],
            [26, 'H',  0.399932, -2.896344, -0.855386],
            [27, 'H', -1.364146, -2.140645, -2.409934],
            [28, 'H', -0.007016, -1.035292, -2.430851],
            [29, 'H', -2.229948,  0.177326, -2.261725],
            [30, 'H', -0.101863,  1.055799, -1.581061],
            [31, 'H', -0.582210,  0.470722,  1.326014],
            [32, 'H',  3.918694,  1.929549,  0.116264],
            [33, 'H',  5.656588,  0.267474, -0.505165],
            [34, 'H',  5.068478, -2.115052, -0.797816],
            [35, 'H',  2.736463, -2.873299, -0.445917],
            [36, 'H',  1.059165, -2.698455,  1.760657],
            [37, 'H',  0.631843, -1.189746,  2.570301],
            [38, 'H', -1.243126, -3.142405,  2.361743],
            [39, 'H', -1.719677, -1.470258,  2.058429],
            [40, 'H', -3.410692, -2.541912,  0.651788],
            [41, 'H', -2.971493, -2.840572, -1.016009],
            [42, 'H', -4.455619, -0.395106,  0.813636],
            [43, 'H', -3.834304,  1.785629, -1.118252],
            [44, 'H', -4.559845,  1.966160,  0.480526],
            [45, 'H', -1.736135,  2.699031, -1.329897],
            [46, 'H', -0.354638,  4.078330, -0.048526],
            [47, 'H', -0.690723,  3.116119,  1.378208],
            [ 1, 'O', -2.547545,  2.139059,  0.472310],
            [ 2, 'O',  2.015408,  3.324289,  0.213156],
            [ 3, 'N',  1.207610,  1.203922,  0.478894],
            [ 4, 'N', -1.350394, -2.624460,  0.301178]
        ]

        # Check the data.
        i = 0
        for spin in spin_loop():
            self.assertEqual(spin.num, data[i][0])
            self.assertEqual(spin.name, data[i][1])
            self.assertEqual(spin.element, data[i][1])
            self.assertEqual(spin.pos[0], data[i][2])
            self.assertEqual(spin.pos[1], data[i][3])
            self.assertEqual(spin.pos[2], data[i][4])

            # Increment the spin index.
            i += 1


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


    def test_read_merge_simultaneous(self):
        """Test the simultaneous merging of two molecules into one."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB files.
        self.interpreter.structure.read_pdb(file='2BE6_core_I_IV.pdb', dir=path, read_mol=[1, 3], set_mol_name='CaM A')

        # Check that everything is ok.
        cdp.structure.validate_models()


    def test_read_not_pdb(self):
        """Test the reading of a file by structure.read_pdb that is not a PDB."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'saved_states'

        # Read the non-PDB file.
        self.interpreter.structure.read_pdb(file='basic_single_pipe.bz2', dir=path)


    def test_read_pdb_1UBQ(self):
        """Test the reading of the complete 1UBQ PDB file."""

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('1UBQ.pdb', dir=path)

        # Check the data.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 1)

        # Check the first atom.
        self.assertEqual(cdp.structure.structural_data[0].mol[0].atom_num[0], 1)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].atom_name[0], 'N')
        self.assertEqual(cdp.structure.structural_data[0].mol[0].res_name[0], 'MET')
        self.assertEqual(cdp.structure.structural_data[0].mol[0].res_num[0], 1)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].x[0], 27.340)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].y[0], 24.430)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].z[0], 2.614)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].element[0], 'N')

        # Check the last atom (from the last ATOM record, as water HETATM records are skipped).
        self.assertEqual(cdp.structure.structural_data[0].mol[0].atom_num[-1], 602)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].atom_name[-1], 'OXT')
        self.assertEqual(cdp.structure.structural_data[0].mol[0].res_name[-1], 'GLY')
        self.assertEqual(cdp.structure.structural_data[0].mol[0].res_num[-1], 76)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].x[-1], 40.862)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].y[-1], 39.575)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].z[-1], 36.251)
        self.assertEqual(cdp.structure.structural_data[0].mol[0].element[-1], 'O')


    def test_read_pdb_complex_internal(self):
        """Test the packing of models and molecules using 'gromacs.pdb' and 'lactose_MCMM4_S1_*.pdb' (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB models.
        self.interpreter.structure.read_pdb(file='gromacs.pdb', dir=path+sep+'phthalic_acid')
        self.interpreter.structure.read_pdb(file='lactose'+sep+'lactose_MCMM4_S1_1.pdb', dir=path, set_model_num=1, set_mol_name='lactose_MCMM4_S1')
        self.interpreter.structure.read_pdb(file='lactose'+sep+'lactose_MCMM4_S1_2.pdb', dir=path, set_model_num=2, set_mol_name='lactose_MCMM4_S1')
        self.interpreter.structure.read_pdb(file='lactose'+sep+'lactose_MCMM4_S1_3.pdb', dir=path, set_model_num=1, set_mol_name='lactose_MCMM4_S1b')
        self.interpreter.structure.read_pdb(file='lactose'+sep+'lactose_MCMM4_S1_4.pdb', dir=path, set_model_num=2, set_mol_name='lactose_MCMM4_S1b')

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Test the structural data.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
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


    def test_read_pdb_internal1(self):
        """Load the '1F35_N_H_molmol.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='1F35_N_H_molmol.pdb', dir=path)

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
        self.interpreter.interatom.define(spin_id1='@CA', spin_id2='#1F35_N_H_molmol_mol1:3@N')
        self.interpreter.interatom.unit_vectors()
        print(cdp.interatomic[0])
        self.assertTrue(hasattr(cdp.interatomic[0], 'vector'))


    def test_read_pdb_internal2(self):
        """Load the 'Ap4Aase_res1-12.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=path)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_internal3(self):
        """Load the 'gromacs.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'phthalic_acid'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='gromacs.pdb', dir=path)

        # Try loading a few protons, without positions averaging across models.
        self.interpreter.structure.load_spins('@*H*', ave_pos=False)

        # A test.
        self.assertEqual(len(cdp.mol[0].res[0].spin[0].pos), 2)

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins(ave_pos=False)


    def test_read_pdb_internal4(self):
        """Load the 'tylers_peptide_trunc.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='tylers_peptide_trunc.pdb', dir=path)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_internal5(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' PDB file (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDB.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_internal6(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' and 'lactose_MCMM4_S1_2.pdb' PDB files as 2 separate structures (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDB twice.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path)
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_2.pdb', dir=path)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_internal7(self):
        """Load the 'lactose_MCMM4_S1_1.pdb' PDB file twice as 2 separate structures (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Read the PDB twice.
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path)
        self.interpreter.structure.read_pdb(file='lactose_MCMM4_S1_1.pdb', dir=path)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()


    def test_read_pdb_model_2_mol_internal(self):
        """Load the 2 models of the 'gromacs.pdb' PDB file as separate molecules of the same model (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'phthalic_acid'

        # Read the PDB models.
        self.interpreter.structure.read_pdb(file='gromacs.pdb', dir=path, read_model=1, set_model_num=1)
        self.interpreter.structure.read_pdb(file='gromacs.pdb', dir=path, read_model=2, set_model_num=1)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Test the structural data.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 2)

        i = 0
        for mol in cdp.structure.structural_data[0].mol:
            self.assertEqual(mol.file_name, 'gromacs.pdb')
            self.assertEqual(mol.file_path, path)
            self.assertEqual(mol.file_model, i+1)
            self.assertEqual(mol.file_mol_num, 1)
            i = i + 1


    def test_read_pdb_mol_2_model_internal(self):
        """Load a few 'lactose_MCMM4_S1_*.pdb' PDB files as models (using the internal structural object PDB reader)."""

        # Path of the files.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

        # Files.
        files = ['lactose_MCMM4_S1_1.pdb',
                 'lactose_MCMM4_S1_2.pdb',
                 'lactose_MCMM4_S1_3.pdb']

        # Read the PDBs.
        self.interpreter.structure.read_pdb(file=files[0], dir=path, set_model_num=1)
        self.interpreter.structure.read_pdb(file=files[1], dir=path, set_model_num=1)
        self.interpreter.structure.read_pdb(file=files[2], dir=path, set_model_num=1)

        # Try loading a few protons.
        self.interpreter.structure.load_spins('@*H*')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Test the structural data.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 1)
        self.assertEqual(len(cdp.structure.structural_data[0].mol), 3)

        i = 0
        for mol in cdp.structure.structural_data[0].mol:
            self.assertEqual(mol.file_name, files[i])
            self.assertEqual(mol.file_path, path)
            self.assertEqual(mol.file_model, 1)
            self.assertEqual(mol.file_mol_num, 1)
            i = i + 1


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
        self.tmpfile_handle, self.tmpfile = mkstemp(suffix='.pdb')
        self.interpreter.structure.write_pdb(self.tmpfile, force=True)

        # Read the contents of the file.
        file = open(self.tmpfile)
        lines = file.readlines()
        file.close()

        # What the contents should be, without remarks.
        real_data = [
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
        self.strip_remarks(lines)
        self.assertEqual(len(real_data), len(lines))
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
        a=return_spin(spin_id='#SSS-cluster4-new-test_mol1@2')
        self.assertAlmostEqual(a.pos[0], -12.398)
        self.assertAlmostEqual(a.pos[1], -15.992)
        self.assertAlmostEqual(a.pos[2], 11.448)

        # Try loading a few protons.
        #self.interpreter.structure.load_spins('@H')

        # And now all the rest of the atoms.
        self.interpreter.structure.load_spins()

        # Extract a vector between first two spins.
        self.interpreter.interatom.define(spin_id1='@2', spin_id2='@10')
        self.interpreter.interatom.unit_vectors()
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
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
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
        self.assertTrue(hasattr(cdp.structure, 'rmsd'))
        self.assertAlmostEqual(cdp.structure.rmsd, sqrt(4.0/3.0))


    def test_rmsd_molecules(self):
        """Test the structure.rmsd user function for different molecules in one pipe.

        This checks the molecules argument of the U{structure.rmsd user function<http://www.nmr-relax.com/manual/structure_rmsd.html>}.
        """

        # Create three molecules 'X', 'Y', and 'Z' with a some atoms.
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=1, mol_name='X', pos=[1., 0., -1.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=1, mol_name='Y', pos=[0., 0., 0.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=1, mol_name='Z', pos=[-1., 0., 1.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=2, mol_name='X', pos=[1., 2., -1.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=2, mol_name='Y', pos=[0., 2., 0.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=2, mol_name='Z', pos=[-1., 2., 1.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=3, mol_name='X', pos=[1., 20., -1.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=3, mol_name='Y', pos=[0., 20., 0.], element='S')
        self.interpreter.structure.add_atom(atom_name='A', res_name='UNK', res_num=3, mol_name='Z', pos=[-1., 20., 1.], element='S')

        # Calculate the RMSD.
        self.interpreter.structure.rmsd(molecules=[['X', 'Y', 'Z']])

        # Checks.
        self.assertTrue(hasattr(cdp.structure, 'rmsd'))
        self.assertAlmostEqual(cdp.structure.rmsd, sqrt(4.0/3.0))


    def test_rmsd_spins(self):
        """Test the structure.rmsd user function for per-atom RMSDs."""

        # Set up 3 models.
        self.interpreter.structure.add_model(model_num=1)
        self.interpreter.structure.add_model(model_num=2)
        self.interpreter.structure.add_model(model_num=4)

        # Check that the models were correctly created.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 3)

        # Create a structure with some atoms.
        self.interpreter.structure.add_atom(atom_name='CA', res_name='UNK', res_num=1, pos=[[1., 0., -1.], [0., 0., 0.], [-1., 0., 1.]], element='S')
        self.interpreter.structure.add_atom(atom_name='CA', res_name='UNK', res_num=2, pos=[[1., 2., -1.], [0., 2., 0.], [-1., 2., 1.]], element='S')
        self.interpreter.structure.add_atom(atom_name='CA', res_name='UNK', res_num=3, pos=[[1., 20., -1.], [0., 20., 0.], [-1., 20., 1.]], element='S')

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

        # Create the spins from the structural data.
        self.interpreter.structure.load_spins(ave_pos=False)

        # Calculate the RMSD.
        self.interpreter.structure.rmsd(atomic=True)

        # Checks.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].pos_rmsd, sqrt(4.0/3.0))
        self.assertAlmostEqual(cdp.mol[0].res[1].spin[0].pos_rmsd, sqrt(4.0/3.0))
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].pos_rmsd, sqrt(4.0/3.0))


    def test_rmsd_ubi(self):
        """Test the structure.rmsd user function on the truncated ubiquitin ensemble."""

        # Load the structure.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('trunc_ubi_pcs.pdb', dir=path)

        # Calculate the RMSD.
        self.interpreter.structure.rmsd()

        # The per-structure RMSDs, and their quadratic average.
        all_rmsd = array([1.06994466835, 0.411387603119, 0.647768214719, 0.522216519591, 0.274450954939, 0.979817275482, 0.752817901842, 1.28956426491, 1.12979370978, 0.650514765397], float64)
        rmsd = sqrt(mean(all_rmsd**2))

        # Checks (the values match the VMD 1.9.1 RMSD numbers).
        self.assertTrue(hasattr(cdp.structure, 'rmsd'))
        self.assertAlmostEqual(cdp.structure.rmsd, rmsd)


    def test_sequence_alignment_central_star_nw70_blosum62(self):
        """Test of the structure.sequence_alignment user function using the 'Central Star', 'NW70', and 'BLOSUM62' options."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'

        # Load the two rotated structures.
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=path, set_model_num=1, set_mol_name='CaM A')
        self.interpreter.structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=path, set_model_num=1, set_mol_name='CaM B')

        # Delete some residues.
        self.interpreter.structure.delete("#CaM B:82")
        self.interpreter.structure.delete("#CaM A:100-120")

        # Perform the alignment.
        self.interpreter.structure.sequence_alignment(pipes=['mf'], models=[[1, 1]], molecules=[['CaM A', 'CaM B']], msa_algorithm='Central Star', pairwise_algorithm='NW70', matrix='BLOSUM62', gap_open_penalty=10.0, gap_extend_penalty=1.0, end_gap_open_penalty=0.5, end_gap_extend_penalty=0.1)

        # Save the relax state.
        self.tmpfile_handle, self.tmpfile = mkstemp(suffix='.bz2')
        self.interpreter.state.save(self.tmpfile, dir=None, force=True)

        # Reset relax.
        self.interpreter.reset()

        # Load the results.
        self.interpreter.state.load(self.tmpfile)

        # The real data.
        pipes = ['mf', 'mf']
        models = [1, 1]
        molecules = ['CaM A', 'CaM B']
        ids = ["Object 'mf'; Model 1; Molecule 'CaM A'", "Object 'mf'; Model 1; Molecule 'CaM B'"]
        sequences = [
            'EEEIREAFRVFDKDGNGYVDEMIREADIDGDGQVNYEEFVQMMTAK**',
            'EEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTAK**'
        ]
        strings = [
            'EEEIREAFRVFDKDGNGY---------------------VDEMIREADIDGDGQVNYEEFVQMMTAK**',
            '-EEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTAK**'
        ]
        gaps = []
        for i in range(len(strings)):
            gaps.append([])
            for j in range(len(strings[0])):
                gaps[i].append(0)
        for i in range(18, 39):
            gaps[0][i] = 1
        gaps[1][0] = 1
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
            self.assertEqual(ds.sequence_alignments[0].object_ids[i], pipes[i])
            self.assertEqual(ds.sequence_alignments[0].models[i], models[i])
            self.assertEqual(ds.sequence_alignments[0].molecules[i], molecules[i])
            self.assertEqual(ds.sequence_alignments[0].sequences[i], sequences[i])
            self.assertEqual(ds.sequence_alignments[0].strings[i], strings[i])
            for j in range(len(strings[0])):
                self.assertEqual(ds.sequence_alignments[0].gaps[i, j], gaps[i][j])
            self.assertEqual(ds.sequence_alignments[0].msa_algorithm, msa_algorithm)
            self.assertEqual(ds.sequence_alignments[0].pairwise_algorithm, pairwise_algorithm)
            self.assertEqual(ds.sequence_alignments[0].matrix, matrix)
            self.assertEqual(ds.sequence_alignments[0].gap_open_penalty, gap_open_penalty)
            self.assertEqual(ds.sequence_alignments[0].gap_extend_penalty, gap_extend_penalty)
            self.assertEqual(ds.sequence_alignments[0].end_gap_open_penalty, end_gap_open_penalty)
            self.assertEqual(ds.sequence_alignments[0].end_gap_extend_penalty, end_gap_extend_penalty)


    def test_sequence_alignment_residue_number(self):
        """Test of the structure.sequence_alignment user function using the 'residue number' MSA algorithm."""

        # Path of the structure file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'

        # Load the two rotated structures.
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=path, set_model_num=1, set_mol_name='CaM A')
        self.interpreter.structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=path, set_model_num=1, set_mol_name='CaM B')

        # Delete some residues.
        self.interpreter.structure.delete("#CaM B:82")
        self.interpreter.structure.delete("#CaM A:100-120")
        self.interpreter.structure.delete(":CA")

        # Perform the alignment.
        self.interpreter.structure.sequence_alignment(pipes=['mf'], models=[[1, 1]], molecules=[['CaM A', 'CaM B']], msa_algorithm='residue number')

        # Save the relax state.
        self.tmpfile_handle, self.tmpfile = mkstemp(suffix='.bz2')
        self.interpreter.state.save(self.tmpfile, dir=None, force=True)

        # Reset relax.
        self.interpreter.reset()

        # Load the results.
        self.interpreter.state.load(self.tmpfile)

        # The real data.
        pipes = ['mf', 'mf']
        models = [1, 1]
        molecules = ['CaM A', 'CaM B']
        ids = ["Object 'mf'; Model 1; Molecule 'CaM A'", "Object 'mf'; Model 1; Molecule 'CaM B'"]
        sequences = [
            'EEEIREAFRVFDKDGNGYVDEMIREADIDGDGQVNYEEFVQMMTAK',
            'EEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTAK'
        ]
        strings = [
            'EEEIREAFRVFDKDGNGY---------------------VDEMIREADIDGDGQVNYEEFVQMMTAK',
            '-EEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTAK'
        ]
        gaps = []
        for i in range(len(strings)):
            gaps.append([])
            for j in range(len(strings[0])):
                gaps[i].append(0)
        for i in range(18, 39):
            gaps[0][i] = 1
        gaps[1][0] = 1
        msa_algorithm = 'residue number'
        pairwise_algorithm = None
        matrix = None
        gap_open_penalty = None
        gap_extend_penalty = None
        end_gap_open_penalty = None
        end_gap_extend_penalty = None

        # Check the data.
        for i in range(2):
            print("Checking \"%s\"" % molecules[i])
            self.assertEqual(ds.sequence_alignments[0].ids[i], ids[i])
            self.assertEqual(ds.sequence_alignments[0].object_ids[i], pipes[i])
            self.assertEqual(ds.sequence_alignments[0].models[i], models[i])
            self.assertEqual(ds.sequence_alignments[0].molecules[i], molecules[i])
            self.assertEqual(ds.sequence_alignments[0].sequences[i], sequences[i])
            self.assertEqual(ds.sequence_alignments[0].strings[i], strings[i])
            for j in range(len(strings[0])):
                self.assertEqual(ds.sequence_alignments[0].gaps[i, j], gaps[i][j])
            self.assertEqual(ds.sequence_alignments[0].msa_algorithm, msa_algorithm)
            self.assertEqual(ds.sequence_alignments[0].pairwise_algorithm, pairwise_algorithm)
            self.assertEqual(ds.sequence_alignments[0].matrix, matrix)
            self.assertEqual(ds.sequence_alignments[0].gap_open_penalty, gap_open_penalty)
            self.assertEqual(ds.sequence_alignments[0].gap_extend_penalty, gap_extend_penalty)
            self.assertEqual(ds.sequence_alignments[0].end_gap_open_penalty, end_gap_open_penalty)
            self.assertEqual(ds.sequence_alignments[0].end_gap_extend_penalty, end_gap_extend_penalty)


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

        # Add an atom that should not be superimposed.
        self.interpreter.structure.add_atom(mol_name='CaM', atom_name='Ti', res_name='TST', res_num=1, pos=[[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]], element='Ti', pdb_record='HETATM')

        # Superimpose the backbone heavy atoms.
        self.interpreter.structure.superimpose(method='fit to mean', atom_id='@N,C,CA,O', displace_id=':82-5000')

        # Check that the two structures now have the same atomic coordinates.
        model1 = cdp.structure.structural_data[0].mol[0]
        model2 = cdp.structure.structural_data[1].mol[0]
        for i in range(len(model1.atom_name)):
            if model1.res_num[i] == 1:
                continue
            self.assertAlmostEqual(model1.x[i], model2.x[i], 2)
            self.assertAlmostEqual(model1.y[i], model2.y[i], 2)
            self.assertAlmostEqual(model1.z[i], model2.z[i], 2)

        # The first 'Ti' atom must be different - it is not displaced.
        self.assertAlmostEqual(model1.x[0] - model2.x[0], -1.0, 2)
        self.assertAlmostEqual(model1.y[0] - model2.y[0], -1.0, 2)
        self.assertAlmostEqual(model1.z[0] - model2.z[0], -1.0, 2)


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
        self.interpreter.structure.superimpose(models=[[2, 3]], method='fit to mean', atom_id='@N,C,CA,O')

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
        self.interpreter.structure.web_of_motion(file=file, models=[[1, 2]])

        # The result, without remarks.
        result = [
            "ATOM      1  N   LEU A   4       9.464  -9.232  27.573  1.00  0.00           N  ",
            "ATOM      2  N   LEU A   4       9.211  -9.425  26.970  1.00  0.00           N  ",
            "ATOM      3  H   LEU A   4       8.575  -8.953  27.963  1.00  0.00           H  ",
            "ATOM      4  H   LEU A   4       9.085  -9.743  27.919  1.00  0.00           H  ",
            "ATOM      5 CA   LEU A   4      10.302  -8.195  26.930  1.00  0.00           C  ",
            "ATOM      6 CA   LEU A   4      10.077  -8.221  26.720  1.00  0.00           C  ",
            "ATOM      7 CB   LEU A   4       9.494  -7.221  26.051  1.00  0.00           C  ",
            "ATOM      8 CB   LEU A   4       9.297  -7.096  26.024  1.00  0.00           C  ",
            "ATOM      9 CG   LEU A   4      10.107  -5.862  25.665  1.00  0.00           C  ",
            "ATOM     10 CG   LEU A   4      10.061  -5.803  25.679  1.00  0.00           C  ",
            "ATOM     11 CD1  LEU A   4      11.182  -6.007  24.608  1.00  0.00           C  ",
            "ATOM     12 CD1  LEU A   4      11.029  -6.002  24.507  1.00  0.00           C  ",
            "ATOM     13 CD2  LEU A   4       9.036  -4.875  25.171  1.00  0.00           C  ",
            "ATOM     14 CD2  LEU A   4       9.120  -4.618  25.384  1.00  0.00           C  ",
            "ATOM     15  C   LEU A   4      10.999  -7.436  28.046  1.00  0.00           C  ",
            "ATOM     16  C   LEU A   4      10.625  -7.721  28.047  1.00  0.00           C  ",
            "TER      17      LEU A   4                                                      ",
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
        self.strip_remarks(lines)
        self.assertEqual(len(result), len(lines))
        for i in range(len(lines)):
            self.assertEqual(result[i]+'\n', lines[i])


    def test_web_of_motion_12_molecules(self):
        """Check the operation of the structure.web_of_motion user function using molecules 1 and 2 (of 3)."""

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path, read_model=1, set_mol_name='1', set_model_num=1)
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path, read_model=2, set_mol_name='2', set_model_num=1)
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path, read_model=3, set_mol_name='3', set_model_num=1)

        # Run the structure.web_of_motion user function and collect the results in a dummy file object.
        file = DummyFileObject()
        self.interpreter.structure.web_of_motion(file=file, molecules=[['1', '2']])

        # The result, without remarks.
        result = [
            "ATOM      1  N   LEU A   4       9.464  -9.232  27.573  1.00  0.00           N  ",
            "ATOM      2  N   LEU A   4       9.211  -9.425  26.970  1.00  0.00           N  ",
            "ATOM      3  H   LEU A   4       8.575  -8.953  27.963  1.00  0.00           H  ",
            "ATOM      4  H   LEU A   4       9.085  -9.743  27.919  1.00  0.00           H  ",
            "ATOM      5 CA   LEU A   4      10.302  -8.195  26.930  1.00  0.00           C  ",
            "ATOM      6 CA   LEU A   4      10.077  -8.221  26.720  1.00  0.00           C  ",
            "ATOM      7 CB   LEU A   4       9.494  -7.221  26.051  1.00  0.00           C  ",
            "ATOM      8 CB   LEU A   4       9.297  -7.096  26.024  1.00  0.00           C  ",
            "ATOM      9 CG   LEU A   4      10.107  -5.862  25.665  1.00  0.00           C  ",
            "ATOM     10 CG   LEU A   4      10.061  -5.803  25.679  1.00  0.00           C  ",
            "ATOM     11 CD1  LEU A   4      11.182  -6.007  24.608  1.00  0.00           C  ",
            "ATOM     12 CD1  LEU A   4      11.029  -6.002  24.507  1.00  0.00           C  ",
            "ATOM     13 CD2  LEU A   4       9.036  -4.875  25.171  1.00  0.00           C  ",
            "ATOM     14 CD2  LEU A   4       9.120  -4.618  25.384  1.00  0.00           C  ",
            "ATOM     15  C   LEU A   4      10.999  -7.436  28.046  1.00  0.00           C  ",
            "ATOM     16  C   LEU A   4      10.625  -7.721  28.047  1.00  0.00           C  ",
            "TER      17      LEU A   4                                                      ",
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
        self.strip_remarks(lines)
        self.assertEqual(len(result), len(lines))
        for i in range(len(lines)):
            self.assertEqual(result[i]+'\n', lines[i])


    def test_web_of_motion_13(self):
        """Check the operation of the structure.web_of_motion user function using structural models 1 and 3 (of 3)."""

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path)

        # Run the structure.web_of_motion user function and collect the results in a dummy file object.
        file = DummyFileObject()
        self.interpreter.structure.web_of_motion(file=file, models=[[1, 3]])

        # The result, without remarks.
        result = [
            "ATOM      1  N   LEU A   4       9.464  -9.232  27.573  1.00  0.00           N  ",
            "ATOM      2  N   LEU A   4       7.761  -6.392  27.161  1.00  0.00           N  ",
            "ATOM      3  H   LEU A   4       8.575  -8.953  27.963  1.00  0.00           H  ",
            "ATOM      4  H   LEU A   4       7.278  -6.195  28.026  1.00  0.00           H  ",
            "ATOM      5 CA   LEU A   4      10.302  -8.195  26.930  1.00  0.00           C  ",
            "ATOM      6 CA   LEU A   4       9.256  -6.332  27.183  1.00  0.00           C  ",
            "ATOM      7 CB   LEU A   4       9.494  -7.221  26.051  1.00  0.00           C  ",
            "ATOM      8 CB   LEU A   4       9.799  -5.331  26.144  1.00  0.00           C  ",
            "ATOM      9 CG   LEU A   4      10.107  -5.862  25.665  1.00  0.00           C  ",
            "ATOM     10 CG   LEU A   4      10.293  -5.882  24.803  1.00  0.00           C  ",
            "ATOM     11 CD1  LEU A   4      11.182  -6.007  24.608  1.00  0.00           C  ",
            "ATOM     12 CD1  LEU A   4       9.404  -6.984  24.274  1.00  0.00           C  ",
            "ATOM     13 CD2  LEU A   4       9.036  -4.875  25.171  1.00  0.00           C  ",
            "ATOM     14 CD2  LEU A   4      10.355  -4.772  23.792  1.00  0.00           C  ",
            "ATOM     15  C   LEU A   4      10.999  -7.436  28.046  1.00  0.00           C  ",
            "ATOM     16  C   LEU A   4       9.816  -6.033  28.572  1.00  0.00           C  ",
            "TER      17      LEU A   4                                                      ",
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
        self.strip_remarks(lines)
        self.assertEqual(len(result), len(lines))
        for i in range(len(lines)):
            self.assertEqual(result[i]+'\n', lines[i])


    def test_web_of_motion_13_molecules(self):
        """Check the operation of the structure.web_of_motion user function using molecules 1 and 3 (of 3)."""

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path, read_model=1, set_mol_name='1', set_model_num=1)
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path, read_model=2, set_mol_name='2', set_model_num=1)
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path, read_model=3, set_mol_name='3', set_model_num=1)

        # Run the structure.web_of_motion user function and collect the results in a dummy file object.
        file = DummyFileObject()
        self.interpreter.structure.web_of_motion(file=file, molecules=[['1', '3']])

        # The result, without remarks.
        result = [
            "ATOM      1  N   LEU A   4       9.464  -9.232  27.573  1.00  0.00           N  ",
            "ATOM      2  N   LEU A   4       7.761  -6.392  27.161  1.00  0.00           N  ",
            "ATOM      3  H   LEU A   4       8.575  -8.953  27.963  1.00  0.00           H  ",
            "ATOM      4  H   LEU A   4       7.278  -6.195  28.026  1.00  0.00           H  ",
            "ATOM      5 CA   LEU A   4      10.302  -8.195  26.930  1.00  0.00           C  ",
            "ATOM      6 CA   LEU A   4       9.256  -6.332  27.183  1.00  0.00           C  ",
            "ATOM      7 CB   LEU A   4       9.494  -7.221  26.051  1.00  0.00           C  ",
            "ATOM      8 CB   LEU A   4       9.799  -5.331  26.144  1.00  0.00           C  ",
            "ATOM      9 CG   LEU A   4      10.107  -5.862  25.665  1.00  0.00           C  ",
            "ATOM     10 CG   LEU A   4      10.293  -5.882  24.803  1.00  0.00           C  ",
            "ATOM     11 CD1  LEU A   4      11.182  -6.007  24.608  1.00  0.00           C  ",
            "ATOM     12 CD1  LEU A   4       9.404  -6.984  24.274  1.00  0.00           C  ",
            "ATOM     13 CD2  LEU A   4       9.036  -4.875  25.171  1.00  0.00           C  ",
            "ATOM     14 CD2  LEU A   4      10.355  -4.772  23.792  1.00  0.00           C  ",
            "ATOM     15  C   LEU A   4      10.999  -7.436  28.046  1.00  0.00           C  ",
            "ATOM     16  C   LEU A   4       9.816  -6.033  28.572  1.00  0.00           C  ",
            "TER      17      LEU A   4                                                      ",
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
        self.strip_remarks(lines)
        self.assertEqual(len(result), len(lines))
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

        # The result, without remarks.
        result = [
            "ATOM      1  N   LEU A   4       9.464  -9.232  27.573  1.00  0.00           N  ",
            "ATOM      2  N   LEU A   4       9.211  -9.425  26.970  1.00  0.00           N  ",
            "ATOM      3  N   LEU A   4       7.761  -6.392  27.161  1.00  0.00           N  ",
            "ATOM      4  H   LEU A   4       8.575  -8.953  27.963  1.00  0.00           H  ",
            "ATOM      5  H   LEU A   4       9.085  -9.743  27.919  1.00  0.00           H  ",
            "ATOM      6  H   LEU A   4       7.278  -6.195  28.026  1.00  0.00           H  ",
            "ATOM      7 CA   LEU A   4      10.302  -8.195  26.930  1.00  0.00           C  ",
            "ATOM      8 CA   LEU A   4      10.077  -8.221  26.720  1.00  0.00           C  ",
            "ATOM      9 CA   LEU A   4       9.256  -6.332  27.183  1.00  0.00           C  ",
            "ATOM     10 CB   LEU A   4       9.494  -7.221  26.051  1.00  0.00           C  ",
            "ATOM     11 CB   LEU A   4       9.297  -7.096  26.024  1.00  0.00           C  ",
            "ATOM     12 CB   LEU A   4       9.799  -5.331  26.144  1.00  0.00           C  ",
            "ATOM     13 CG   LEU A   4      10.107  -5.862  25.665  1.00  0.00           C  ",
            "ATOM     14 CG   LEU A   4      10.061  -5.803  25.679  1.00  0.00           C  ",
            "ATOM     15 CG   LEU A   4      10.293  -5.882  24.803  1.00  0.00           C  ",
            "ATOM     16 CD1  LEU A   4      11.182  -6.007  24.608  1.00  0.00           C  ",
            "ATOM     17 CD1  LEU A   4      11.029  -6.002  24.507  1.00  0.00           C  ",
            "ATOM     18 CD1  LEU A   4       9.404  -6.984  24.274  1.00  0.00           C  ",
            "ATOM     19 CD2  LEU A   4       9.036  -4.875  25.171  1.00  0.00           C  ",
            "ATOM     20 CD2  LEU A   4       9.120  -4.618  25.384  1.00  0.00           C  ",
            "ATOM     21 CD2  LEU A   4      10.355  -4.772  23.792  1.00  0.00           C  ",
            "ATOM     22  C   LEU A   4      10.999  -7.436  28.046  1.00  0.00           C  ",
            "ATOM     23  C   LEU A   4      10.625  -7.721  28.047  1.00  0.00           C  ",
            "ATOM     24  C   LEU A   4       9.816  -6.033  28.572  1.00  0.00           C  ",
            "TER      25      LEU A   4                                                      ",
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
        self.strip_remarks(lines)
        self.assertEqual(len(result), len(lines))
        for i in range(len(lines)):
            self.assertEqual(result[i]+'\n', lines[i])


    def test_web_of_motion_all_molecules(self):
        """Check the operation of the structure.web_of_motion user function using all molecules."""

        # Load the file.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path, read_model=1, set_mol_name='1', set_model_num=1)
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path, read_model=2, set_mol_name='2', set_model_num=1)
        self.interpreter.structure.read_pdb('web_of_motion.pdb', dir=path, read_model=3, set_mol_name='3', set_model_num=1)

        # Run the structure.web_of_motion user function and collect the results in a dummy file object.
        file = DummyFileObject()
        self.interpreter.structure.web_of_motion(file=file, molecules=[['1', '2', '3']])

        # The result, without remarks.
        result = [
            "ATOM      1  N   LEU A   4       9.464  -9.232  27.573  1.00  0.00           N  ",
            "ATOM      2  N   LEU A   4       9.211  -9.425  26.970  1.00  0.00           N  ",
            "ATOM      3  N   LEU A   4       7.761  -6.392  27.161  1.00  0.00           N  ",
            "ATOM      4  H   LEU A   4       8.575  -8.953  27.963  1.00  0.00           H  ",
            "ATOM      5  H   LEU A   4       9.085  -9.743  27.919  1.00  0.00           H  ",
            "ATOM      6  H   LEU A   4       7.278  -6.195  28.026  1.00  0.00           H  ",
            "ATOM      7 CA   LEU A   4      10.302  -8.195  26.930  1.00  0.00           C  ",
            "ATOM      8 CA   LEU A   4      10.077  -8.221  26.720  1.00  0.00           C  ",
            "ATOM      9 CA   LEU A   4       9.256  -6.332  27.183  1.00  0.00           C  ",
            "ATOM     10 CB   LEU A   4       9.494  -7.221  26.051  1.00  0.00           C  ",
            "ATOM     11 CB   LEU A   4       9.297  -7.096  26.024  1.00  0.00           C  ",
            "ATOM     12 CB   LEU A   4       9.799  -5.331  26.144  1.00  0.00           C  ",
            "ATOM     13 CG   LEU A   4      10.107  -5.862  25.665  1.00  0.00           C  ",
            "ATOM     14 CG   LEU A   4      10.061  -5.803  25.679  1.00  0.00           C  ",
            "ATOM     15 CG   LEU A   4      10.293  -5.882  24.803  1.00  0.00           C  ",
            "ATOM     16 CD1  LEU A   4      11.182  -6.007  24.608  1.00  0.00           C  ",
            "ATOM     17 CD1  LEU A   4      11.029  -6.002  24.507  1.00  0.00           C  ",
            "ATOM     18 CD1  LEU A   4       9.404  -6.984  24.274  1.00  0.00           C  ",
            "ATOM     19 CD2  LEU A   4       9.036  -4.875  25.171  1.00  0.00           C  ",
            "ATOM     20 CD2  LEU A   4       9.120  -4.618  25.384  1.00  0.00           C  ",
            "ATOM     21 CD2  LEU A   4      10.355  -4.772  23.792  1.00  0.00           C  ",
            "ATOM     22  C   LEU A   4      10.999  -7.436  28.046  1.00  0.00           C  ",
            "ATOM     23  C   LEU A   4      10.625  -7.721  28.047  1.00  0.00           C  ",
            "ATOM     24  C   LEU A   4       9.816  -6.033  28.572  1.00  0.00           C  ",
            "TER      25      LEU A   4                                                      ",
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
        self.strip_remarks(lines)
        self.assertEqual(len(result), len(lines))
        for i in range(len(lines)):
            self.assertEqual(result[i]+'\n', lines[i])
