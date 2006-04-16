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


class Sequence:
    def __init__(self, relax, test_name):
        """Class for testing the sequence functions."""

        self.relax = relax

        # Sequence reading test.
        if test_name == 'read':
            # The name of the test.
            self.name = "The user function sequence.read()"

            # The test.
            self.test = self.read

        # Loading the sequence from a PDB file test.
        if test_name == 'pdb':
            # The name of the test.
            self.name = "Loading the sequence from a PDB file"

            # The test.
            self.test = self.pdb


    def pdb(self, run):
        """The sequence loading from a PDB file test."""

        # Create the run.
        self.relax.generic.runs.create(run, 'mf')

        # Read the sequence.
        self.relax.interpreter._PDB.pdb(run, file='test.pdb', dir=sys.path[-1] + '/test_suite/data', model=1, heteronuc='N', proton='H', load_seq=1)

        # Success.
        return 1


    def read(self, run):
        """The sequence.read() test."""

        # Create the run.
        self.relax.generic.runs.create(run, 'mf')

        # Read the sequence.
        self.relax.interpreter._Sequence.read(run, file='test_seq', dir=sys.path[-1] + '/test_suite/data')

        # Success.
        return 1
