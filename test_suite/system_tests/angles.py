###############################################################################
#                                                                             #
# Copyright (C) 2006-2010 Edward d'Auvergne                                   #
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
from os import sep
import sys

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from status import Status


class Angles(SystemTestCase):
    """Class for testing the angle calculation function."""

    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_angles(self):
        """The user function angles()."""

        # Execute the script.
        self.interpreter.run(script_file=Status().install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'angles.py')

        # Res info.
        res_name = ['GLY', 'PRO', 'LEU', 'GLY', 'SER', 'MET', 'ASP', 'SER', 'PRO', 'PRO', 'GLU', 'GLY']
        spin_num = [1, 11, 28, 51, 59, 71, 91, 104, 116, 133, 150, 167]
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
        alpha = [None, None, 1.9520343757367986, 2.7290472392365279, 2.419205013244329, 2.8233982819255239, 0.82721388443178889, 0.84005102282930511, None, None, 0.7056707530666082, 2.0797049142007396]

        # Molecule checks.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'Ap4Aase_res1-12_mol1')
        self.assertEqual(len(cdp.mol[0].res), 12)

        # Checks for the first 12 residues.
        for i in xrange(12):
            print((cdp.mol[0].res[i].spin[0]))
            # Check the residue and spin info.
            self.assertEqual(cdp.mol[0].res[i].num, i+1)
            self.assertEqual(cdp.mol[0].res[i].name, res_name[i])
            self.assertEqual(len(cdp.mol[0].res[i].spin), 1)
            self.assertEqual(cdp.mol[0].res[i].spin[0].num, spin_num[i])
            self.assertEqual(cdp.mol[0].res[i].spin[0].name, spin_name[i])

            # Angles have been calculated.
            if hasattr(cdp.mol[0].res[i].spin[0], 'attached_atom'):
                # The attached proton.
                self.assertEqual(cdp.mol[0].res[i].spin[0].attached_atom, attached_atoms[i])

                # The XH vector.
                for j in xrange(3):
                    self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].xh_vect[j], xh_vects[i][j])

                # Check the alpha angles.
                self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].alpha, alpha[i])

            # No angles calculated.
            else:
                self.assertEqual(attached_atoms[i], None)
                self.assert_(not hasattr(cdp.mol[0].res[i].spin[0], 'xh_vect'))
                self.assert_(not hasattr(cdp.mol[0].res[i].spin[0], 'alpha'))
