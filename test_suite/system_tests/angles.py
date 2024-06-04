###############################################################################
#                                                                             #
# Copyright (C) 2006-2009,2012 Edward d'Auvergne                              #
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
from pipe_control.interatomic import return_interatom_list
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Angles(SystemTestCase):
    """Class for testing the angle calculation function."""

    def test_angles(self):
        """The user function angles()."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'angles.py')

        # Res info.
        res_name = ['GLY', 'PRO', 'LEU', 'GLY', 'SER', 'MET', 'ASP', 'SER', 'PRO', 'PRO', 'GLU', 'GLY']
        spin_num = [1, 10, 24, 43, 50, 61, 78, 90, 101, 115, 129, 144]
        spin_name = ['N']*12
        attached_atoms = [None, None, 'H', 'H', 'H', 'H', 'H', 'H', None, None, 'H', 'H']
        xh_vects = [
            None,
            None,
            [0.408991870425, -0.805744582632, 0.428370537602],
            [-0.114123686687, -0.989411605119, -0.0896686109685],
            [-0.0162975723187, -0.975817142584, 0.217980029763],
            [-0.255934111969, -0.960517663248, -0.109103386377],
            [0.922628022844, 0.38092966093, 0.0604162634271],
            [0.926402811426, 0.281593806116, 0.249965516299],
            None,
            None,
            [0.820296708196, 0.570330671495, -0.0428513205774],
            [-0.223383112106, -0.034680483158, -0.974113571055]
        ]
        alpha = [None, None, 2.8102691247870459, 2.6063738282640672, 2.9263088853837358, 2.5181004004450211, 1.3361463581932049, 1.5031623128368377, None, None, 1.0968465542222101, 1.1932423104331247]

        # Molecule checks.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'Ap4Aase_res1-12_mol1')
        self.assertEqual(len(cdp.mol[0].res), 12)

        # Checks for the first 12 residues.
        for i in range(12):
            # Check the residue and spin info.
            self.assertEqual(cdp.mol[0].res[i].num, i+1)
            self.assertEqual(cdp.mol[0].res[i].name, res_name[i])
            self.assertEqual(cdp.mol[0].res[i].spin[0].num, spin_num[i])
            self.assertEqual(cdp.mol[0].res[i].spin[0].name, spin_name[i])

            # Get the interatomic container.
            interatoms = return_interatom_list(spin_hash=cdp.mol[0].res[i].spin[0]._hash)

            # Check the containers.
            self.assertTrue(len(interatoms) <= 1)

            # No interatomic container.
            if not interatoms:
                # The spin info.
                self.assertEqual(len(cdp.mol[0].res[i].spin), 1)

            # Check the interatomic info.
            else:
                # The spin info.
                self.assertEqual(len(cdp.mol[0].res[i].spin), 2)
                self.assertEqual(cdp.mol[0].res[i].spin[1].name, attached_atoms[i])

                # The vector.
                for j in range(3):
                    self.assertAlmostEqual(interatoms[0].vector[j], xh_vects[i][j])

                # Check the alpha angles.
                self.assertAlmostEqual(interatoms[0].alpha, alpha[i])
