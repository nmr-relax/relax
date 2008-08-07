###############################################################################
#                                                                             #
# Copyright (C) 2003-2006 Edward d'Auvergne                                   #
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

# Python module imports.
import sys

# relax module imports.
import help
from generic_fns import palmer
from relax_errors import RelaxBinError, RelaxFloatError, RelaxIntError, RelaxNoneStrError, RelaxStrError


class Palmer:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for interfacing with Art Palmer's Modelfree 4."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def create(self, dir=None, force=False, binary='modelfree4', diff_search='none', sims=0, sim_type='pred', trim=0, steps=20, constraints=1, heteronuc_type='15N', atom1='N', atom2='H', spin_id=None):
        """Function for creating the Modelfree4 input files.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        dir:  The directory to place the files.

        force:  A flag which if set to True will cause the results file to be overwritten if it
        already exists.

        binary:  The name of the executable Modelfree program file.

        diff_search:  See the Modelfree4 manual for 'diffusion_search'.

        sims:  The number of Monte Carlo simulations.

        sim_type:  See the Modelfree4 manual.

        trim:  See the Modelfree4 manual.

        steps:  See the Modelfree4 manual.

        constraints:  A flag specifying whether the parameters should be constrained.  The default
        is to turn constraints on (constraints=1).

        heteronuc_type:  A three letter string describing the heteronucleus type, ie 15N, 13C, etc.

        atom1:  The symbol of the X heteronucleus in the pdb file.

        atom2:  The symbol of the H nucleus in the pdb file.

        spin_id:  The spin identification string.


        Description
        ~~~~~~~~~~~

        The following files are created

            'dir/mfin',
            'dir/mfdata',
            'dir/mfpar',
            'dir/mfmodel',
            'dir/run.sh'.

        The file 'dir/run.sh' contains the single command,

        'modelfree4 -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out',

        which can be used to execute modelfree4.

        If you would like to use a different Modelfree executable file, change the keyword argument
        'binary' to the appropriate file name.  If the file is not located within the environment's
        path, include the full path infront of the binary file name.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "palmer.create("
            text = text + "dir=" + `dir`
            text = text + ", force=" + `force`
            text = text + ", binary=" + `binary`
            text = text + ", diff_search=" + `diff_search`
            text = text + ", sims=" + `sims`
            text = text + ", sim_type=" + `sim_type`
            text = text + ", trim=" + `trim`
            text = text + ", steps=" + `steps`
            text = text + ", constraints=" + `constraints`
            text = text + ", heteronucleus=" + `heteronuc_type`
            text = text + ", atom1=" + `atom1`
            text = text + ", atom2=" + `atom2`
            text = text + ", spin_id" + `spin_id` + ")"
            print text

        # Directory.
        if dir != None:
            if type(dir) != str:
                raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != bool:
            raise RelaxBoolError, ('force flag', force)

        # The Modelfree executable file.
        if type(binary) != str:
            raise RelaxStrError, ('Modelfree binary', binary)

        # The diff_search argument.
        if type(diff_search) != str:
            raise RelaxStrError, ('diff_search', diff_search)

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

        # The heteronucleus argument.
        if type(heteronuc_type) != str:
            raise RelaxStrError, ('heteronucleus', heteronuc_type)

        # The atom1 argument.
        if type(atom1) != str:
            raise RelaxStrError, ('atom1', atom1)

        # The atom2 argument.
        if type(atom2) != str:
            raise RelaxStrError, ('atom2', atom2)

        # Execute the functional code.
        palmer.create(dir=dir, force=force, binary=binary, diff_search=diff_search, sims=sims, sim_type=sim_type, trim=trim, steps=steps, constraints=constraints, heteronuc_type=heteronuc_type, atom1=atom1, atom2=atom2, spin_id=spin_id)


    def execute(self, dir=None, force=False, binary='modelfree4'):
        """Function for executing Modelfree4.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        dir:  The directory to place the files.

        force:  A flag which if set to True will cause the results file to be overwritten if it
        already exists.

        binary:  The name of the executable Modelfree program file.


        Description
        ~~~~~~~~~~~

        Modelfree 4 will be executed as

        $ modelfree4 -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out

        If a PDB file is loaded and non-isotropic diffusion is selected, then the file name will be
        placed on the command line as '-s pdb_file_name'.


        If you would like to use a different Modelfree executable file, change the keyword argument
        'binary' to the appropriate file name.  If the file is not located within the environment's
        path, include the full path in front of the binary file name.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "palmer.execute("
            text = text + "dir=" + `dir`
            text = text + ", force=" + `force`
            text = text + ", binary=" + `binary` + ")"
            print text

        # Directory.
        if dir != None:
            if type(dir) != str:
                raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != bool:
            raise RelaxBoolError, ('force flag', force)

        # The Modelfree executable file.
        if type(binary) != str:
            raise RelaxStrError, ('Modelfree binary', binary)

        # Execute the functional code.
        palmer.execute(dir=dir, force=force, binary=binary)


    def extract(self, dir=None):
        """Function for extracting data from the Modelfree4 'mfout' star formatted file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        dir:  The directory where the file 'mfout' is found.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "palmer.extract("
            text = text + "dir=" + `dir` + ")"
            print text

        # Directory.
        if dir != None:
            if type(dir) != str:
                raise RelaxNoneStrError, ('directory name', dir)

        # Execute the functional code.
        palmer.extract(dir=dir)
