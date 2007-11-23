###############################################################################
#                                                                             #
# Copyright (C) 2006 Chris MacRaild                                           #
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
import sys

# relax module imports.
from data import Data as relax_data_store
from generic_fns.selection import residue_loop
from physical_constants import N15_CSA, NH_BOND_LENGTH

# The relax data storage object.




class Jw:
    def __init__(self, relax, test_name):
        """Class for testing various aspects specific to reduced spectral density mapping."""

        self.relax = relax

        # Results reading test.
        if test_name == 'set':

            # The name of the test.
            self.name = "The user function value.set()"

            # The test.
            self.test = self.set_value

        # Spectral density calculation test.
        if test_name == 'calc':

            # The name of the test.
            self.name = "Spectral density calculation"

            # The test.
            self.test = self.calc


    def calc(self, pipe):
        """The spectral density calculation test."""

        # Arguments.
        self.pipe = pipe

        # Setup.
        self.calc_setup()

        # Try the reduced spectral density mapping.
        self.relax.interpreter._Minimisation.calc()

        # Success.
        return self.calc_integrity()


    def calc_integrity(self):

        # Correct jw values:
        j0 = [4.0703318681008998e-09, 3.7739393907014834e-09]
        jwx = [1.8456254300773903e-10, 1.6347516082378241e-10]
        jwh = [1.5598167512718012e-12, 2.9480536599037041e-12]

        # Loop over residues.
        for res in residue_loop:
            # Residues -2 and -1 have data.
            if res.num == -2 or res.num == -1:
                if not res.spin[0].select:
                    print 'Residue', res.num, 'unexpectedly not selected'
                    return

                if abs(res.spin[0].j0 - j0[index]) > j0[index]/1e6:
                    print 'Error in residue', res.num, 'j0 calculated value'
                    return
                if abs(res.spin[0].jwh - jwh[index]) > jwh[index]/1e6:
                    print 'Error in residue', res.num, 'jwh calculated value'
                    return
                if abs(res.spin[0].jwx - jwx[index]) > jwx[index]/1e6:
                    print 'Error in residue', res.num, 'jwx calculated value'
                    return

            # Other residues have insufficient data.
            else:
                if res.spin[0].select:
                    print 'Residue', res.num, 'unexpectedly selected'
                    return

        # Success.
        return 1


    def calc_setup(self):
        """Setup for the calculation test."""

        dir = sys.path[-1] + '/test_suite/system_tests/data/jw_mapping/'

        dataPaths = [dir + 'noe.dat',
                     dir + 'R1.dat',
                     dir + 'R2.dat']

        dataTypes = [('NOE', '600', 600.0e6),
                     ('R1', '600', 600.0e6),
                     ('R2', '600', 600.0e6)]

        # Create the data pipe.
        self.relax.interpreter._Pipe.create(self.pipe, 'jw')

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='test_seq', dir=sys.path[-1] + '/test_suite/system_tests/data')

        # Read the data.
        for dataSet in xrange(len(dataPaths)):
            self.relax.interpreter._Relax_data.read(dataTypes[dataSet][0], dataTypes[dataSet][1], dataTypes[dataSet][2], dataPaths[dataSet])

        # Nuclei type.
        self.relax.interpreter._Nuclei.nuclei('N')

        # Set r and csa.
        self.relax.interpreter._Value.set(NH_BOND_LENGTH, 'bond_length')
        self.relax.interpreter._Value.set(N15_CSA, 'csa')

        # Select the frequency.
        self.relax.interpreter._Jw_mapping.set_frq(frq=600.0 * 1e6)


    def set_value(self, pipe):
        """The value.set test."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create(pipe, 'jw')

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='test_seq', dir=sys.path[-1] + '/test_suite/system_tests/data')

        # Try to set the values.
        bond_length = NH_BOND_LENGTH
        csa = N15_CSA
        self.relax.interpreter._Value.set(bond_length, 'bond_length')
        self.relax.interpreter._Value.set(csa, 'csa')

        # Test values.
        for i in xrange(len(relax_data_store[pipe].mol[0].res)):
            if relax_data_store[pipe].mol[0].res[i].spin[0].r != bond_length:
                print 'Value of bond_length has not been set correctly'
                return
            if relax_data_store[pipe].mol[0].res[i].spin[0].csa != csa:
                print 'Value of csa has not been set correctly'
                return

        # Success.
        return 1

