###############################################################################
#                                                                             #
# Copyright (C) 2003-2005,2007-2008 Edward d'Auvergne                         #
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
"""User functions involved with RDCs."""

# Python module imports.
import sys

# relax module imports.
import help
from generic_fns import rdc
from relax_errors import RelaxError, RelaxBoolError, RelaxBinError, RelaxFloatError, RelaxIntError, RelaxNoneIntError, RelaxNoneStrError, RelaxStrError


class RDC:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating R1, R2, and NOE relaxation data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def back_calc(self, id=None):
        """Back calculate RDCs.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "rdc.back_calc("
            text = text + "id=" + `id` + ")"
            print text

        # Identification string.
        if type(id) != str:
            raise RelaxStrError, ('identification string', id)

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
            text = text + "pipe_from=" + `pipe_from`
            text = text + ", pipe_to=" + `pipe_to`
            text = text + ", id=" + `id` + ")"
            print text

        # The pipe_from argument.
        if pipe_from != None and type(pipe_from) != str:
            raise RelaxNoneStrError, ('pipe_from', pipe_from)

        # The pipe_to argument.
        if pipe_to != None and type(pipe_to) != str:
            raise RelaxNoneStrError, ('pipe_to', pipe_to)

        # Both pipe arguments cannot be None.
        if pipe_from == None and pipe_to == None:
            raise RelaxError, "The pipe_from and pipe_to arguments cannot both be set to None."

        # Id string.
        if id != None and type(id) != str:
            raise RelaxNoneStrError, ('alignment identification string', id)

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
            text = text + "id=" + `id` + ")"
            print text

        # Id string.
        if type(id) != str:
            raise RelaxStrError, ('alignment identification string', id)

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
            text = text + "id=" + `id` + ")"
            print text

        # Id string.
        if type(id) != str:
            raise RelaxStrError, ('alignment identification string', id)

        # Execute the functional code.
        rdc.display(id=id)


    def read(self, id=None, file=None, dir=None, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, data_col=2, error_col=3, sep=None):
        """Read the RDC data from file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.

        file:  The name of the file containing the RDC data.

        dir:  The directory where the file is located.

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
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "rdc.read("
            text = text + "id=" + `id`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", mol_name_col=" + `mol_name_col`
            text = text + ", res_num_col=" + `res_num_col`
            text = text + ", res_name_col=" + `res_name_col`
            text = text + ", spin_num_col=" + `spin_num_col`
            text = text + ", spin_name_col=" + `spin_name_col`
            text = text + ", data_col=" + `data_col`
            text = text + ", error_col=" + `error_col`
            text = text + ", sep=" + `sep` + ")"
            print text

        # Id string.
        if type(id) != str:
            raise RelaxStrError, ('alignment identification string', id)

        # The file name.
        if type(file) != str:
            raise RelaxStrError, ('file', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Molecule name column.
        if mol_name_col != None and type(mol_name_col) != int:
            raise RelaxNoneIntError, ('molecule name column', mol_name_col)

        # Residue number column.
        if res_num_col != None and type(res_num_col) != int:
            raise RelaxNoneIntError, ('residue number column', res_num_col)

        # Residue name column.
        if res_name_col != None and type(res_name_col) != int:
            raise RelaxNoneIntError, ('residue name column', res_name_col)

        # Spin number column.
        if spin_num_col != None and type(spin_num_col) != int:
            raise RelaxNoneIntError, ('spin number column', spin_num_col)

        # Spin name column.
        if spin_name_col != None and type(spin_name_col) != int:
            raise RelaxNoneIntError, ('spin name column', spin_name_col)

        # The data column.
        if type(data_col) != int:
            raise RelaxIntError, ('data column', data_col)

        # The error column.
        if error_col != None and type(error_col) != int:
            raise RelaxNoneIntError, ('error column', error_col)

        # Column separator.
        if sep != None and type(sep) != str:
            raise RelaxNoneStrError, ('column separator', sep)

        # Execute the functional code.
        rdc.read(id=id, file=file, dir=dir, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep)


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
            text = text + "id=" + `id`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # Id string.
        if type(id) != str:
            raise RelaxStrError, ('alignment identification string', id)

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != bool:
            raise RelaxBoolError, ('force flag', force)

        # Execute the functional code.
        rdc.write(id=id, file=file, dir=dir, force=force)
