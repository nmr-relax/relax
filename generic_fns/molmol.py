###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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

from os import popen


class Molmol:
    def __init__(self, relax):
        """Class containing the functions for viewing molecules."""

        self.relax = relax


    def open_pdb(self):
        """Open the loaded PDB into Molmol."""

        # Test if a pipe has been opened.
        if not hasattr(self.relax.data, 'molmol'):
            return

        # Run InitAll to remove everything from molmol.
        try:
            self.relax.data.molmol.write('InitAll yes\n')
        except IOError:
            return

        # Open the PDB.
        command = "ReadPdb " + self.relax.data.pdb.filename + "\n"
        self.relax.data.molmol.write(command)


    def view(self):
        """Function for running Molmol."""

        # Open a molmol pipe.
        self.relax.data.molmol = popen("molmol -f -", 'w', 0)

        # Run InitAll to remove everything from molmol.
        self.relax.data.molmol.write('InitAll yes\n')

        # Test if the PDB file has been loaded.
        if hasattr(self.relax.data, 'pdb'):
            self.open_pdb()
