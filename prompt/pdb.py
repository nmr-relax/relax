###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


class PDB:
    def __init__(self, relax):
        """Class containing the function for loading a pdb file."""

        self.relax = relax


    def pdb(self, file=None, model=None, load_seq=1):
        """The pdb loading function.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the PDB file.

        model:  The PDB model number.

        load_seq:  A flag specifying whether the sequence should be loaded from the PDB file.


        Description
        ~~~~~~~~~~~

        The model argument can have several values:

            None - If the argument is set to None, the default value, then the first structure in
        the PDB file will be extracted.  This should be the value used if the structure is
        determined using X-ray crystalography.

            i - If the argument is set to the integer, i, then the structure extracted will be the
        one begining with the line 'MODEL i' in the PDB file.  If no such model exists, then nothing
        will be loaded.  For example, if the lowest energy structure in an NMR ensemble is structure
        3, to load just this structure for an analysis, set the argument to 3.

            'all' - If the arguement is set to the string value 'all', then all structures in an NMR
        ensemble will be loaded.


        To load the sequence from the PDB file, set the 'load_seq' flag to 1.  If the sequence has
        previously been loaded, then this flag will be ignored.


        Example
        ~~~~~~~

        To load the first structure from the PDB file 'test.pdb' in the directory 'pdb', type:

        relax> pdb('pdb/test.pdb')
        relax> pdb('pdb/test.pdb', None)
        relax> pdb(file='pdb/test.pdb', model=None)
        relax> pdb(file='pdb/test.pdb', model=1)

        To load the 10th model from the file 'test.pdb', use:

        relax> pdb('test.pdb', 10)
        relax> pdb('test.pdb', model=10)
        relax> pdb(file='test.pdb', model=10)

        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "pdb("
            text = text + "file=" + `file`
            text = text + ", model=" + `model`
            text = text + ", load_seq=" + `load_seq` + ")"
            print text

        # The file argument.
        if type(file) != str:
            raise RelaxStrError, ('file', file)

        # The model argument.
        if model != None:
            if type(model) != int and type(model) != str:
                raise RelaxNoneIntStrError, ('model', model)

        # The load sequence argument.
        if type(load_seq) != int or (load_seq != 0 and load_seq != 1):
            raise RelaxBinError, ('load sequence flag', load_seq)

        # Execute the functional code.
        self.relax.pdb.pdb(file=file, model=model, load_seq=load_seq)
