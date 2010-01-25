###############################################################################
#                                                                             #
# Copyright (C) 2003-2006, 2009-2010 Edward d'Auvergne                        #
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

# Module docstring.
"""Module containing the 'palmer' user function class for controlling the Modelfree4 software."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from generic_fns import palmer


class Palmer(User_fn_class):
    """Class for interfacing with Art Palmer's Modelfree 4."""

    def create(self, dir=None, force=False, binary='modelfree4', diff_search='none', sims=0, sim_type='pred', trim=0, steps=20, constraints=True, heteronuc_type='15N', atom1='N', atom2='H', spin_id=None):
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
        is to turn constraints on (constraints=True).

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
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "palmer.create("
            text = text + "dir=" + repr(dir)
            text = text + ", force=" + repr(force)
            text = text + ", binary=" + repr(binary)
            text = text + ", diff_search=" + repr(diff_search)
            text = text + ", sims=" + repr(sims)
            text = text + ", sim_type=" + repr(sim_type)
            text = text + ", trim=" + repr(trim)
            text = text + ", steps=" + repr(steps)
            text = text + ", constraints=" + repr(constraints)
            text = text + ", heteronucleus=" + repr(heteronuc_type)
            text = text + ", atom1=" + repr(atom1)
            text = text + ", atom2=" + repr(atom2)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')
        arg_check.is_str(binary, 'Modelfree executable file')
        arg_check.is_str(diff_search, 'diffusion search')
        arg_check.is_int(sims, 'number of Monte Carlo simulations')
        arg_check.is_str(sim_type, 'simulation type')
        arg_check.is_num(trim, 'trimming')
        arg_check.is_int(steps, 'steps')
        arg_check.is_bool(constraints, 'constraints flag')
        arg_check.is_str(heteronuc_type, 'heteronucleus')
        arg_check.is_str(atom1, 'atom1')
        arg_check.is_str(atom2, 'atom2')

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
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "palmer.execute("
            text = text + "dir=" + repr(dir)
            text = text + ", force=" + repr(force)
            text = text + ", binary=" + repr(binary) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')
        arg_check.is_str(binary, 'Modelfree executable file')

        # Execute the functional code.
        palmer.execute(dir=dir, force=force, binary=binary)


    def extract(self, dir=None):
        """Function for extracting data from the Modelfree4 'mfout' star formatted file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        dir:  The directory where the file 'mfout' is found.
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "palmer.extract("
            text = text + "dir=" + repr(dir) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(dir, 'directory name', can_be_none=True)

        # Execute the functional code.
        palmer.extract(dir=dir)
