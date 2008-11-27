###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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


class Generic:
    def __init__(self, relax, test_name):
        """Class for testing various aspects specific to relaxation curve-fitting."""

        self.relax = relax

        # Value difference test.
        if test_name == 'value_diff':
            # The name of the test.
            self.name = "S2 difference stored in a new run."

            # The test.
            self.test = self.value_diff


    def value_diff(self, run):
        """The test of storing an S2 difference in a new run."""

        # Arguments.
        self.run = run

        # Create three runs.
        self.relax.interpreter._Run.create('orig1', "mf")
        self.relax.interpreter._Run.create('orig2', "mf")
        self.relax.interpreter._Run.create('new', "mf")

        # Load the Lupin Ap4Aase sequence.
        self.relax.interpreter._Sequence.read('orig1', file="Ap4Aase.seq", dir=sys.path[-1] + "/test_suite/data")
        self.relax.interpreter._Sequence.read('orig2', file="Ap4Aase.seq", dir=sys.path[-1] + "/test_suite/data")
        self.relax.interpreter._Sequence.read('new', file="Ap4Aase.seq", dir=sys.path[-1] + "/test_suite/data")

        # Only select residue 8.
        self.relax.interpreter._Select.res('orig1', num=8, change_all=1)
        self.relax.interpreter._Select.res('orig2', num=8, change_all=1)
        self.relax.interpreter._Select.res('new', num=8, change_all=1)

        # Set two order parameter values.
        self.relax.interpreter._Value.set('orig1', 0.9, 'S2', res_num=8)
        self.relax.interpreter._Value.set('orig2', 0.7, 'S2', res_num=8)

        # Calculate the difference and assign it to residue 8 (located in position 7).
        diff = self.relax.data.res['orig1'][7].s2 - self.relax.data.res['orig2'][7].s2
        self.relax.interpreter._Value.set('new', diff, 'S2', res_num=8)

        # Test if the difference is 0.2!
        if abs(self.relax.data.res['new'][7].s2 - 0.2) > 0.00001:
            print "The difference of '" + `diff` + "' should be equal to 0.2."
            return

        # Success.
        else:
            return 1

