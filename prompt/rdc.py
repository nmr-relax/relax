###############################################################################
#                                                                             #
# Copyright (C) 2003-2005,2007-2009 Edward d'Auvergne                         #
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
"""Module containing the 'rdc' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
from base_class import User_fn_class
import check
from generic_fns import rdc
from relax_errors import RelaxError


class RDC(User_fn_class):
    """Class for handling residual dipolar coulpings."""

    def back_calc(self, id=None):
        """Back calculate RDCs.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "rdc.back_calc("
            text = text + "id=" + repr(id) + ")"
            print(text)

        # The argument checks.
        check.is_str(id, 'alignment identification string')

        # Execute the functional code.
        rdc.back_calc(id=id)


    def copy(self, pipe_from=None, pipe_to=None, id=None):
        """Copy RDC data from pipe_from to pipe_to.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The name of the pipe to copy the RDC data from.

        pipe_to:  The name of the pipe to copy the RDC data to.

        id:  The alignment identification string.


        Description
        ~~~~~~~~~~~

        This function will copy RDC data from 'pipe_from' to 'pipe_to'.  If id is not given then all
        RDC data will be copied, otherwise only a specific data set will be.


        Examples
        ~~~~~~~~

        To copy all RDC data from pipe 'm1' to pipe 'm9', type one of:

        relax> rdc.copy('m1', 'm9')
        relax> rdc.copy(pipe_from='m1', pipe_to='m9')
        relax> rdc.copy('m1', 'm9', None)
        relax> rdc.copy(pipe_from='m1', pipe_to='m9', id=None)

        To copy only the 'Th' RDC data from 'm3' to 'm6', type one of:

        relax> rdc.copy('m3', 'm6', 'Th')
        relax> rdc.copy(pipe_from='m3', pipe_to='m6', id='Th')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "rdc.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", pipe_to=" + repr(pipe_to)
            text = text + ", id=" + repr(id) + ")"
            print(text)

        # The argument checks.
        check.is_str(pipe_from, 'pipe from', can_be_none=True)
        check.is_str(pipe_to, 'pipe to', can_be_none=True)
        check.is_str(id, 'alignment identification string', can_be_none=True)

        # Both pipe arguments cannot be None.
        if pipe_from == None and pipe_to == None:
            raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")

        # Execute the functional code.
        rdc.copy(pipe_from=pipe_from, pipe_to=pipe_to, id=id)


    def delete(self, id=None):
        """Delete the RDC data corresponding to the alignment id.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.


        Examples
        ~~~~~~~~

        To delete the RDC data corresponding to id='PH_gel', type:

        relax> rdc.delete('PH_gel')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "rdc.delete("
            text = text + "id=" + repr(id) + ")"
            print(text)

        # The argument checks.
        check.is_str(id, 'alignment identification string')

        # Execute the functional code.
        rdc.delete(id=id)


    def display(self, id=None):
        """Display the RDC data corresponding to the alignment id.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.


        Examples
        ~~~~~~~~

        To display the 'phage' RDC data, type:

        relax> rdc.display('phage')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "rdc.display("
            text = text + "id=" + repr(id) + ")"
            print(text)

        # The argument checks.
        check.is_str(id, 'alignment identification string')

        # Execute the functional code.
        rdc.display(id=id)


    def read(self, id=None, file=None, dir=None, spin_id=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None):
        """Read the RDC data from file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.

        file:  The name of the file containing the RDC data.

        dir:  The directory where the file is located.

        spin_id:  The spin identification string.

        mol_name_col:  The molecule name column (this defaults to no column).

        res_num_col:  The residue number column (the default is 0, i.e. the first column).

        res_name_col:  The residue name column (the default is 1, i.e. the second column).

        spin_num_col:  The spin number column (this defaults to no column).

        spin_name_col:  The spin name column (this defaults to no column).

        data_col:  The RDC data column (the default is 2).

        error_col:  The experimental error column (the default is 3).

        sep:  The column separator (the default is white space).


        Examples
        ~~~~~~~~

        The following commands will read the RDC data out of the file 'Tb.txt' where the columns are
        separated by the symbol ',', and store the RDCs under the identifier 'Tb'.

        relax> rdc.read('Tb', 'Tb.txt', sep=',')


        If the individual spin RDC errors are located in the file 'rdc_err.txt' in column number 5,
        then to read these values into relax, type one of:

        relax> rdc.read('phage', 'rdc_err.txt', error_col=4)
        relax> rdc.read(id='phage', file='rdc_err.txt', error_col=4)


        If the RDCs correspond to the 'N' spin and other spins are loaded into relax, then type:

        relax> rdc.read('Tb', 'Tb.txt', spin_id='@N')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "rdc.read("
            text = text + "id=" + repr(id)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", spin_id=" + repr(spin_id)
            text = text + ", mol_name_col=" + repr(mol_name_col)
            text = text + ", res_num_col=" + repr(res_num_col)
            text = text + ", res_name_col=" + repr(res_name_col)
            text = text + ", spin_num_col=" + repr(spin_num_col)
            text = text + ", spin_name_col=" + repr(spin_name_col)
            text = text + ", data_col=" + repr(data_col)
            text = text + ", error_col=" + repr(error_col)
            text = text + ", sep=" + repr(sep) + ")"
            print(text)

        # The argument checks.
        check.is_str(id, 'alignment identification string')
        check.is_str(file, 'file name')
        check.is_str(dir, 'directory name', can_be_none=True)
        check.is_str(spin_id, 'spin identification string', can_be_none=True)
        check.is_int(mol_name_col, 'molecule name column', can_be_none=True)
        check.is_int(res_num_col, 'residue number column', can_be_none=True)
        check.is_int(res_name_col, 'residue name column', can_be_none=True)
        check.is_int(spin_num_col, 'spin number column', can_be_none=True)
        check.is_int(spin_name_col, 'spin name column', can_be_none=True)
        check.is_int(data_col, 'data column', can_be_none=True)
        check.is_int(error_col, 'error column', can_be_none=True)
        check.is_str(sep, 'column separator', can_be_none=True)

        # Execute the functional code.
        rdc.read(id=id, file=file, dir=dir, spin_id=spin_id, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep)


    def write(self, id=None, file=None, dir=None, force=False):
        """Write the RDC data to file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which if True will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the file will be placed in the current working directory.
        The 'id' argument are required for selecting which RDC data set will be written to file.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "rdc.write("
            text = text + "id=" + repr(id)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        check.is_str(id, 'alignment identification string')
        check.is_str(file, 'file name')
        check.is_str(dir, 'directory name', can_be_none=True)
        check.is_bool(force, 'force flag')

        # Execute the functional code.
        rdc.write(id=id, file=file, dir=dir, force=force)
