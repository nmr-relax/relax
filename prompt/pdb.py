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

import sys


class PDB:
    def __init__(self, relax):
        """Class containing the macro for loading a pdb file."""

        self.relax = relax


    def pdb(self, file=None):
        """The pdb loading macro.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the pdb file.


        Example
        ~~~~~~~

        To load the pdb file 'test.pdb' in the directory 'pdb', type:

        relax> pdb('pdb/test.pdb')
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "pdb("
            text = text + "file=" + `file` + ")"
            print text

        # The file argument.
        if type(file) != str:
            raise RelaxStrError, ('file', file)

        # Execute the functional code.
        self.relax.pdb.pdb(file=file)
