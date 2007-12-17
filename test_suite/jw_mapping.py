###############################################################################
#                                                                             #
# Copyright (C) 2006 Chris MacRaild                                           #
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

import sys


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


    def calc(self, run):
        """The spectral density calculation test."""

        # Arguments.
        self.run = run

        # Setup.
        self.calc_setup()
        
        # Try the reduced spectral density mapping.
        self.relax.interpreter._Minimisation.calc(self.run)
        
        # Success.
        return self.calc_integrity()
        

    def calc_integrity(self):
        
        # Correct jw values:
        j0 = [4.0703318681008998e-09, 3.7739393907014834e-09]
        jwx = [1.8456254300773903e-10, 1.6347516082378241e-10]
        jwh = [1.5598167512718012e-12, 2.9480536599037041e-12]

        # Loop over residues.
        for index,residue in enumerate(self.relax.data.res[self.run]):
            # Residues -2 and -1 have data.
            if index == 0 or index == 1:
                if not self.relax.data.res[self.run][index].select:
                    print 'Residue', self.relax.data.res[self.run][index].num, 'unexpectedly not selected'
                    return

                if abs(self.relax.data.res[self.run][index].j0 - j0[index]) > j0[index]/1e6:
                    print 'Error in residue', self.relax.data.res[self.run][index].num, 'j0 calculated value'
                    return
                if abs(self.relax.data.res[self.run][index].jwh - jwh[index]) > jwh[index]/1e6:
                    print 'Error in residue', self.relax.data.res[self.run][index].num, 'jwh calculated value'
                    return
                if abs(self.relax.data.res[self.run][index].jwx - jwx[index]) > jwx[index]/1e6:
                    print 'Error in residue', self.relax.data.res[self.run][index].num, 'jwx calculated value'
                    return

            # Other residues have insufficient data.
            else:
                if self.relax.data.res[self.run][index].select:
                    print 'Residue', self.relax.data.res[self.run][index].num, 'unexpectedly selected'
                    return

        # Success.
        return 1


    def calc_setup(self):
        """Setup for the calculation test."""

        dir = sys.path[-1] + '/test_suite/data/jw_mapping/'

        dataPaths = [dir + 'noe.dat',
                     dir + 'R1.dat',
                     dir + 'R2.dat']

        dataTypes = [('NOE', '600', 600.0e6),
                     ('R1', '600', 600.0e6),
                     ('R2', '600', 600.0e6)]
        
        # Create the run.
        self.relax.generic.runs.create(self.run, 'jw')

        # Read the sequence.
        self.relax.interpreter._Sequence.read(self.run, file='test_seq', dir=sys.path[-1] + '/test_suite/data')

        # Read the data.
        for dataSet in xrange(len(dataPaths)):
            self.relax.interpreter._Relax_data.read(self.run, dataTypes[dataSet][0], dataTypes[dataSet][1], dataTypes[dataSet][2], dataPaths[dataSet])

        # Nuclei type.
        self.relax.interpreter._Nuclei.nuclei('N')

        # Set r and csa.
        self.relax.interpreter._Value.set(self.run, 1.02 * 1e-10, 'bond_length')
        self.relax.interpreter._Value.set(self.run, -172 * 1e-6, 'csa')

        # Select the frequency.
        self.relax.interpreter._Jw_mapping.set_frq(self.run, frq=600.0 * 1e6)


    def set_value(self, run):
        """The value.set test."""

        # Arguments.
        self.run = run

        # Create the run.
        self.relax.generic.runs.create(self.run, 'jw')

        # Read the sequence.
        self.relax.interpreter._Sequence.read(self.run, file='test_seq', dir=sys.path[-1] + '/test_suite/data')

        # Try to set the values.
        bond_length = 1.02 * 1e-10
        csa = -172 * 1e-6
        self.relax.interpreter._Value.set(self.run, bond_length, 'bond_length')
        self.relax.interpreter._Value.set(self.run, csa, 'csa')

        # Test values.
        for i in xrange( len(self.relax.data.res[self.run]) ):
            if self.relax.data.res[self.run][i].r != bond_length:
                print 'Value of bond_length has not been set correctly'
                return
            if self.relax.data.res[self.run][i].csa != csa:
                print 'Value of csa has not been set correctly'
                return

        # Success.
        return 1

