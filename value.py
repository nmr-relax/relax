###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


from re import match


class Value:
    def __init__(self, relax):
        """Class containing functions for the setting up of data structures."""

        self.relax = relax


    def set(self, run=None, data_type=None, val=None, err=None):
        """Function for setting data structure values."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Add the run to the runs list.
        if not run in self.relax.data.runs:
            self.relax.data.runs.append(run)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Bond length.
            if match('[Bb]ond[ -_][Ll]ength', data_type):
                if hasattr(self.relax.data.res[i], 'r'):
                    if self.relax.data.res[i].r.has_key(run):
                        print "Warning: The bond length of residue " + `self.relax.data.res[i].num` + " " + self.relax.data.res[i].name + " has already been specified."
                        continue
                else:
                    self.relax.data.res[i].r = {}
                    if err:
                        self.relax.data.res[i].r_error = {}

                self.relax.data.res[i].r[run] = float(val)
                if err:
                    self.relax.data.res[i].r_error[run] = float(err)

            # CSA.
            elif match('[Cc][Ss][Aa]', data_type):
                if hasattr(self.relax.data.res[i], 'csa'):
                    if self.relax.data.res[i].csa.has_key(run):
                        print "Warning: The CSA of residue " + `self.relax.data.res[i].num` + " " + self.relax.data.res[i].name + " has already been specified."
                        continue
                else:
                    self.relax.data.res[i].csa = {}
                    if err:
                        self.relax.data.res[i].csa_error = {}

                self.relax.data.res[i].csa[run] = float(val)
                if err:
                    self.relax.data.res[i].csa_error[run] = float(err)

            # Bad type.
            else:
                raise RelaxError, "The data type " + `data_type` + " is not supported."
