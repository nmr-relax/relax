###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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

import message


class Skin:
    def __init__(self, relax):
        """The class accessible to the interpreter.

        The purpose of this class is to hide the variables and functions found within the namespace
        of the macro class, found below, except for those required for interactive use.  This is an
        abstraction layer designed to avoid user confusion as none of the macro class data
        structures are accessible.  For more flexibility use the macro class directly.
        """

        # Load the macro class into the namespace of this __init__ function.
        x = Macro_class(relax)

        # Place references to the interactive functions within the namespace of this skin class.
        self.create = x.create
        self.execute = x.execute
        self.extract = x.extract

        # __repr__.
        self.__repr__ = message.macro_class


class Macro_class:
    def __init__(self, relax):
        """Class containing the macros for interoperability with Modelfree4."""

        self.relax = relax


    def create(self, run=None, dir=None, force=0, sims=0, sim_type='pred', trim=0, steps=20, constraints=1, nucleus='15N', atom1='N', atom2='H'):
        """Macro for creating the Modelfree4 input files.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        dir:  The directory to place the files.  The default is the value of 'run'.

        force:  A flag which if set to 1 will cause the results file to be overwitten if it already
        exists.

        sims:  The number of Monte Carlo simulations.

        sim_type:  See the Modelfree4 manual.

        trim:  See the Modelfree4 manual.

        steps:  See the Modelfree4 manual.

        constraints:  A flag specifying whether the parameters should be constrained.  The default
        is to turn constraints on (constraints=1).

        nucleus:  A three letter string describing the nucleus type, ie 15N, 13C, etc.

        atom1:  The symbol of the X nucleus in the pdb file.

        atom2:  The symbol of the H nucleus in the pdb file.


        Description
        ~~~~~~~~~~~

        The following files are created:
            dir/mfin
            dir/mfdata
            dir/mfpar
            dir/mfmodel
            dir/run.sh

        The file 'run/run.sh' contains the single command:
            modelfree4 -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out
        This can be used to execute modelfree4.
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "palmer.create("
            text = text + "run=" + `run`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force`
            text = text + ", sims=" + `sims`
            text = text + ", sim_type=" + `sim_type`
            text = text + ", trim=" + `trim`
            text = text + ", steps=" + `steps`
            text = text + ", constraints=" + `constraints`
            text = text + ", nucleus=" + `nucleus`
            text = text + ", atom1=" + `atom1`
            text = text + ", atom2=" + `atom2` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Directory.
        if dir != None:
            if type(dir) != str:
                raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # The number of Monte Carlo simulations.
        if type(sims) != int:
            raise RelaxIntError, ('sims', sims)

        # The sim_type argument.
        if type(sim_type) != str:
            raise RelaxStrError, ('sim_type', sim_type)

        # The trim argument.
        if type(trim) != float and type(trim) != int:
            raise RelaxFloatError, ('trim', trim)

        # The steps argument.
        if type(steps) != int:
            raise RelaxIntError, ('steps', steps)

        # Constraint flag.
        if type(constraints) != int or (constraints != 0 and constraints != 1):
            raise RelaxBinError, ('constraint flag', constraints)

        # The nucleus argument.
        if type(nucleus) != str:
            raise RelaxStrError, ('nucleus', nucleus)

        # The atom1 argument.
        if type(atom1) != str:
            raise RelaxStrError, ('atom1', atom1)

        # The atom2 argument.
        if type(atom2) != str:
            raise RelaxStrError, ('atom2', atom2)

        # Execute the functional code.
        self.relax.palmer.create(run=run, dir=dir, force=force, sims=sims, sim_type=sim_type, trim=trim, steps=steps, constraints=constraints, nucleus=nucleus, atom1=atom1, atom2=atom2)


    def execute(self, run=None, dir=None, force=0):
        """Macro for executing Modelfree4.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        dir:  The directory to place the files.  The default is the value of 'run'.

        force:  A flag which if set to 1 will cause the results file to be overwitten if it already
        exists.


        Description
        ~~~~~~~~~~~

        Modelfree 4 will be executed as:
            modelfree4 -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out

        If a PDB file is loaded and non-isotropic diffusion is selected, then the file name will be
        placed on the command line as '-s pdb_file_name'.
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "palmer.execute("
            text = text + "run=" + `run`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Directory.
        if dir != None:
            if type(dir) != str:
                raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # Execute the functional code.
        self.relax.palmer.execute(run=run, dir=dir, force=force)


    def extract(self, run=None, dir=None):
        """Macro for extracting data from the Modelfree4 'mfout' star formatted file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        dir:  The directory where the file 'mfout' is found.  The default is the value of 'run'.
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "palmer.extract("
            text = text + "run=" + `run`
            text = text + ", dir=" + `dir` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Directory.
        if dir != None:
            if type(dir) != str:
                raise RelaxNoneStrError, ('directory name', dir)

        # Execute the functional code.
        self.relax.palmer.extract(run=run, dir=dir)
