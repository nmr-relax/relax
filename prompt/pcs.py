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
"""User functions involved with pseudocontact shifts."""

# Python module imports.
import sys

# relax module imports.
import help
from generic_fns import pcs
from relax_errors import RelaxError, RelaxBoolError, RelaxBinError, RelaxFloatError, RelaxIntError, RelaxNoneIntError, RelaxNoneStrError, RelaxStrError


class PCS:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating R1, R2, and NOE relaxation data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def back_calc(self, id=None):
        """Back calculate the pseudocontact shifts.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.back_calc("
            text = text + "id=" + `id` + ")"
            print text

        # Identification string.
        if type(id) != str:
            raise RelaxStrError, ('identification string', id)

        # Execute the functional code.
        pcs.back_calc(id=id)


    def centre(self, atom_id=None, pipe=None):
        """Specify which atom is the paramagnetic centre.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        atom_id:  The atom identification string.

        pipe:  The data pipe containing the structures to extract the centre from.


        Description
        ~~~~~~~~~~~

        This function is required for specifying where the paramagnetic centre is located in the
        loaded structure file.  If no structure number is given, then the average atom position will
        be calculated if multiple structures are loaded.

        A different set of structures than those loaded into the current data pipe can also be used
        to determine the position, or its average.  This can be achieved by loading the alternative
        structures into another data pipe, and then specifying that pipe through the pipe argument.


        Examples
        ~~~~~~~~

        If the paramagnetic centre is the lanthanide Dysprosium which is labelled as Dy in a loaded
        PDB file, then type one of:

        relax> pcs.centre('Dy')
        relax> pcs.centre(atom_id='Dy')

        If the carbon atom 'C1' of residue '4' in the PDB file is to be used as the paramagnetic
        centre, then type:

        relax> pcs.centre(':4@C1')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.centre("
            text = text + "atom_id=" + `atom_id`
            text = text + ", pipe=" + `pipe` + ")"
            print text

        # The atom identifier argument.
        if type(atom_id) != str:
            raise RelaxStrError, ('atom identification string', atom_id)

        # The data pipe argument.
        if pipe != None and type(pipe) != str:
            raise RelaxNoneStrError, ('data pipe', pipe)

        # Execute the functional code.
        pcs.centre(atom_id=atom_id, pipe=pipe)


    def copy(self, pipe_from=None, pipe_to=None, id=None):
        """Copy PCS data from pipe_from to pipe_to.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The name of the pipe to copy the PCS data from.

        pipe_to:  The name of the pipe to copy the PCS data to.

        id:  The alignment identification string.


        Description
        ~~~~~~~~~~~

        This function will copy PCS data from 'pipe_from' to 'pipe_to'.  If id is not given then all
        PCS data will be copied, otherwise only a specific data set will be.


        Examples
        ~~~~~~~~

        To copy all PCS data from pipe 'm1' to pipe 'm9', type one of:

        relax> pcs.copy('m1', 'm9')
        relax> pcs.copy(pipe_from='m1', pipe_to='m9')
        relax> pcs.copy('m1', 'm9', None)
        relax> pcs.copy(pipe_from='m1', pipe_to='m9', id=None)

        To copy only the 'Th' PCS data from 'm3' to 'm6', type one of:

        relax> pcs.copy('m3', 'm6', 'Th')
        relax> pcs.copy(pipe_from='m3', pipe_to='m6', id='Th')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.copy("
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
        pcs.copy(pipe_from=pipe_from, pipe_to=pipe_to, id=id)


    def delete(self, id=None):
        """Delete the PCS data corresponding to the alignment id.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.


        Examples
        ~~~~~~~~

        To delete the PCS data corresponding to id='PH_gel', type:

        relax> pcs.delete('PH_gel')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.delete("
            text = text + "id=" + `id` + ")"
            print text

        # Id string.
        if type(id) != str:
            raise RelaxStrError, ('alignment identification string', id)

        # Execute the functional code.
        pcs.delete(id=id)


    def display(self, id=None):
        """Display the PCS data corresponding to the alignment id.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.


        Examples
        ~~~~~~~~

        To display the 'phage' PCS data, type:

        relax> pcs.display('phage')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.display("
            text = text + "id=" + `id` + ")"
            print text

        # Id string.
        if type(id) != str:
            raise RelaxStrError, ('alignment identification string', id)

        # Execute the functional code.
        pcs.display(id=id)


    def read(self, id=None, file=None, dir=None, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, data_col=2, error_col=3, sep=None):
        """Read the PCS data from file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.

        file:  The name of the file containing the PCS data.

        dir:  The directory where the file is located.

        mol_name_col:  The molecule name column (this defaults to no column).

        res_num_col:  The residue number column (the default is 0, i.e. the first column).

        res_name_col:  The residue name column (the default is 1, i.e. the second column).

        spin_num_col:  The spin number column (this defaults to no column).

        spin_name_col:  The spin name column (this defaults to no column).

        data_col:  The PCS data column (the default is 2).

        error_col:  The experimental error column (the default is 3).

        sep:  The column separator (the default is white space).


        Examples
        ~~~~~~~~

        The following commands will read the PCS data out of the file 'Tb.txt' where the columns are
        separated by the symbol ',', and store the PCSs under the identifier 'Tb'.

        relax> pcs.read('Tb', 'Tb.txt', sep=',')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.read("
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
        if data_col != None and type(data_col) != int:
            raise RelaxNoneIntError, ('data column', data_col)

        # The error column.
        if error_col != None and type(error_col) != int:
            raise RelaxNoneIntError, ('error column', error_col)

        # Column separator.
        if sep != None and type(sep) != str:
            raise RelaxNoneStrError, ('column separator', sep)

        # Execute the functional code.
        pcs.read(id=id, file=file, dir=dir, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep)


    def write(self, id=None, file=None, dir=None, force=False):
        """Write the PCS data to file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which if True will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the file will be placed in the current working directory.
        The 'id' argument are required for selecting which PCS data set will be written to file.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.write("
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
        pcs.write(id=id, file=file, dir=dir, force=force)
