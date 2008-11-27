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


    def pdb(self, run=None, file=None, dir=None, model=None, heteronuc='N', proton='H', load_seq=1):
        """The pdb loading function.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the structure to.

        file:  The name of the PDB file.

        dir:  The directory where the file is located.

        model:  The PDB model number.

        heteronuc:  The name of the heteronucleus as specified in the PDB file.

        proton:  The name of the proton as specified in the PDB file.

        load_seq:  A flag specifying whether the sequence should be loaded from the PDB file.


        Description
        ~~~~~~~~~~~

        To load a specific model from the PDB file, set the model flag to an integer i.  The
        structure beginning with the line 'MODEL i' in the PDB file will be loaded.  Otherwise all
        structures will be loaded starting from the model number 1.

        To load the sequence from the PDB file, set the 'load_seq' flag to 1.  If the sequence has
        previously been loaded, then this flag will be ignored.

        Once the PDB structures are loaded, unit XH bond vectors will be calculated.  The vectors
        are calculated using the atomic coordinates of the atoms specified by the arguments
        heteronuc and proton.  If more than one model structure is loaded, the unit XH vectors for
        each model will be calculated and the final unit XH vector will be taken as the average.


        Example
        ~~~~~~~

        To load all structures from the PDB file 'test.pdb' in the directory '~/pdb' for use in the
        model-free analysis run 'm8' where the heteronucleus in the PDB file is 'N' and the proton
        is 'H', type:

        relax> pdb('m8', 'test.pdb', '~/pdb', 1, 'N', 'H')
        relax> pdb(run='m8', file='test.pdb', dir='pdb', model=1, heteronuc='N', proton='H')


        To load the 10th model from the file 'test.pdb', use:

        relax> pdb('m1', 'test.pdb', model=10)
        relax> pdb(run='m1', file='test.pdb', model=10)

        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "pdb("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", model=" + `model`
            text = text + ", heteronuc=" + `heteronuc`
            text = text + ", proton=" + `proton`
            text = text + ", load_seq=" + `load_seq` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The model argument.
        if model != None and type(model) != int:
            raise RelaxIntError, ('model', model)

        # The heteronucleus argument.
        if type(heteronuc) != str:
            raise RelaxStrError, ('heteronucleus', heteronuc)

        # The proton argument.
        if type(proton) != str:
            raise RelaxStrError, ('proton', proton)

        # The load sequence argument.
        if type(load_seq) != int or (load_seq != 0 and load_seq != 1):
            raise RelaxBinError, ('load sequence flag', load_seq)

        # Execute the functional code.
        self.relax.generic.pdb.load(run=run, file=file, dir=dir, model=model, heteronuc=heteronuc, proton=proton, load_seq=load_seq)
