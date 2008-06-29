###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
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
from numpy import fromstring
import sys
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


class Angles(TestCase):
    """Class for testing the angle calculation function."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_angles(self):
        """The user function angles()."""

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/angles.py')

        # Alias the current data pipe.
        cdp = ds[ds.current_pipe]

        # Res info.
        res_name = ['GLY', 'PRO', 'LEU', 'GLY', 'SER', 'MET', 'ASP', 'SER', 'PRO', 'PRO', 'GLU', 'GLY', 'TYR', 'ARG', 'ARG'] 
        spin_num = [1, 11, 28, 51, 59, 71, 91, 104, 116, 133, 150, 167, None, None, None]
        spin_name = ['N']*12 + [None]*3
        attached_protons = [None, None, 'H', 'H', 'H', 'H', 'H', 'H', None, None, 'H', 'H', None, None, None]
        xh_vects = [
            None,
            None,
            fromstring('\xf8s\xf3<\xec,\xda?\x01\xb4\xea\xdc\xa8\xc8\xe9\xbf\x94~dBlj\xdb?'),
            fromstring('\xd6I\x05\xbe57\xbd\xbf\x90\x96\xc8\x86B\xa9\xef\xbf\xdfp\x96\xa7\x85\xf4\xb6\xbf'),
            fromstring('\xe3\xdds\x90O\xb0\x90\xbf%\xccH\xdf\xe49\xef\xbf\xf1\xb6\x81\x05\xc5\xe6\xcb?'),
            fromstring('\x8d\xbd5x9a\xd0\xbf\xa2,\xdc\x89\x8f\xbc\xee\xbf\x8f\xb7_\x143\xee\xbb\xbf'),
            fromstring('\x03\xa2\x0f4+\x86\xed?(Y\xf1\xcc&a\xd8?\x0c\xb6!g\xe1\xee\xae?'),
            fromstring('\xe3\xee?\x82\x17\xa5\xed?\xa4\xa6\x01\x07\xa2\x05\xd2??\xd8\xd0\xba\xde\xfe\xcf?'),
            None,
            None,
            fromstring('u\xff\xd6\xe1\xde?\xea?\x9a1\xbf\x1b&@\xe2?g\xd5\xf0\xb8\x9b\xf0\xa5\xbf'),
            fromstring('\x0f\x95|\\\xd1\x97\xcc\xbfC0\xf2\xe9\xa3\xc1\xa1\xbf\xa7\xb1H9\xf0+\xef\xbf'),
            None,
            None,
            None,
        ]
        alpha = [None, None, 2.8102691247870459, 2.6063738282640672, 2.9263088853837358, 2.5181004004450211, 1.3361463581932049, 1.5031623128368377, None, None, 1.0968465542222101, 1.1932423104331247, None, None, None]

        # Molecule checks.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, None)
        self.assertEqual(len(cdp.mol[0].res), 165)

        # Checks for the first 15 residues.
        for i in xrange(15):
            # Check the residue and spin info.
            self.assertEqual(cdp.mol[0].res[i].num, i+1)
            self.assertEqual(cdp.mol[0].res[i].name, res_name[i])
            self.assertEqual(len(cdp.mol[0].res[i].spin), 1)
            self.assertEqual(cdp.mol[0].res[i].spin[0].num, spin_num[i])
            self.assertEqual(cdp.mol[0].res[i].spin[0].name, spin_name[i])

            # Angles have been calculated.
            if hasattr(cdp.mol[0].res[i].spin[0], 'attached_proton'):
                # The attached proton.
                self.assertEqual(cdp.mol[0].res[i].spin[0].attached_proton, attached_protons[i])

                # The XH vector.
                for j in xrange(3):
                    self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].xh_vect[j], xh_vects[i][j])

                # Check the alpha angles.
                self.assertAlmostEqual(cdp.mol[0].res[i].spin[0].alpha, alpha[i])

            # No angles calculated.
            else:
                self.assertEqual(attached_protons[i], None)
                self.assert_(not hasattr(cdp.mol[0].res[i].spin[0], 'xh_vect'))
                self.assert_(not hasattr(cdp.mol[0].res[i].spin[0], 'alpha'))
