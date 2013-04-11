###############################################################################
#                                                                             #
# Copyright (C) 2006-2013 Edward d'Auvergne                                   #
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
from tempfile import mktemp

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.mol_res_spin import spin_loop
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Noe(SystemTestCase):
    """Class for testing various aspects specific to the NOE analysis."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('noe', 'noe')

        # Create a temporary file.
        ds.tmpfile = mktemp()


    def test_noe_analysis(self):
        """Test the NOE analysis."""

        # Execute the script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'noe.py')

        # The real data.
        sat = [5050.0, 51643.0, 53663.0, -65111.0, -181131.0, -105322.0]
        ref = [148614.0, 166842.0, 128690.0, 99566.0, 270047.0, 130959.0]
        noe = [0.033980647852826784, 0.30953237194471417, 0.4169943274535706, -0.6539481349054899, -0.6707387973204665, -0.8042364404126482]
        noe_err = [0.02020329903276632, 0.2320024671657343, 0.026067523940084526, 0.038300618865378507, 0.014260663438353431, 0.03183614777183591]

        # Check the data.
        i = 0
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Check the intensity data.
            self.assertEqual(sat[i], spin.intensities['sat_ave'])
            self.assertEqual(ref[i], spin.intensities['ref_ave'])

            # Check the NOE data.
            self.assertEqual(noe[i], spin.noe)
            self.assertAlmostEqual(noe_err[i], spin.noe_err)

            # Increment the spin index.
            i += 1

        # The real Grace file data.
        data = [
            '@version 50121\n',
            '@page size 842, 595\n',
            '@with g0\n',
            '@    view 0.15, 0.15, 1.28, 0.85\n',
            '@    world xmin 0\n',
            '@    world xmax 166\n',
            '@    xaxis  label "Residue number"\n',
            '@    xaxis  label char size 1.48\n',
            '@    xaxis  tick major size 0.75\n',
            '@    xaxis  tick major linewidth 0.5\n',
            '@    xaxis  tick minor linewidth 0.5\n',
            '@    xaxis  tick minor size 0.45\n',
            '@    xaxis  ticklabel char size 1.00\n',
            '@    yaxis  label "\\qNOE\\Q"\n',
            '@    yaxis  label char size 1.48\n',
            '@    yaxis  tick major size 0.75\n',
            '@    yaxis  tick major linewidth 0.5\n',
            '@    yaxis  tick minor linewidth 0.5\n',
            '@    yaxis  tick minor size 0.45\n',
            '@    yaxis  ticklabel char size 1.00\n',
            '@    frame linewidth 0.5\n',
            '@    s0 symbol 1\n',
            '@    s0 symbol size 0.45\n',
            '@    s0 symbol linewidth 0.5\n',
            '@    s0 errorbar size 0.5\n',
            '@    s0 errorbar linewidth 0.5\n',
            '@    s0 errorbar riser linewidth 0.5\n',
            '@    s0 legend "N spins"\n',
            '@    s1 symbol 2\n',
            '@    s1 symbol size 0.45\n',
            '@    s1 symbol linewidth 0.5\n',
            '@    s1 errorbar size 0.5\n',
            '@    s1 errorbar linewidth 0.5\n',
            '@    s1 errorbar riser linewidth 0.5\n',
            '@    s1 legend "NE1 spins"\n',
            '@target G0.S0\n',
            '@type xydy\n',
            '4                              0.033980647852827              0.020203299032766             \n',
            '5                              0.309532371944714              0.232002467165734             \n',
            '6                              0.416994327453571              0.026067523940085             \n',
            '40                             -0.653948134905490             0.038300618865379             \n',
            '55                             -0.804236440412648             0.031836147771836             \n',
            '&\n',
            '@target G0.S1\n',
            '@type xydy\n',
            '40                             -0.670738797320466             0.014260663438353             \n',
            '&\n'
        ]

        # Check the Grace file.
        file = open(ds.tmpfile)
        lines = file.readlines()
        file.close()
        for i in range(len(lines)):
            self.assertEqual(data[i], lines[i])
