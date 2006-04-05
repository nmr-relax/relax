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


class Hybrid:
    def __init__(self, relax):
        """Class containing function specific to hybrid models."""

        self.relax = relax


    def hybridise(self, hybrid=None, runs=None):
        """Function for creating the hybrid run."""

        # Test if the hybrid run already exists.
        if hybrid in self.relax.data.run_names:
            raise RelaxRunError, hybrid

        # Loop over the runs to be hybridised.
        for run in runs:
            # Test if the run exists.
            if not run in self.relax.data.run_names:
                raise RelaxNoRunError, run

            # Test if sequence data is loaded.
            if not self.relax.data.res.has_key(run):
                raise RelaxNoSequenceError, run

        # Check the sequence.
        for i in xrange(len(self.relax.data.res[runs[0]])):
            # Reassign the data structure.
            data1 = self.relax.data.res[runs[0]][i]

            # Loop over the rest of the runs.
            for run in runs[1:]:
                # Reassign the data structure.
                data2 = self.relax.data.res[run][i]

                # Test if the sequence is the same.
                if data1.name != data2.name or data1.num != data2.num:
                    raise RelaxError, "The residues '" + data1.name + " " + `data1.num` + "' of the run " + `runs[0]` + " and '" + data2.name + " " + `data2.num` + "' of the run " + `run` + " are not the same."

        # Add the run and type to the runs list.
        self.relax.data.run_names.append(hybrid)
        self.relax.data.run_types.append('hybrid')

        # Create the data structure of the runs which form the hybrid.
        self.relax.data.hybrid[hybrid] = runs
