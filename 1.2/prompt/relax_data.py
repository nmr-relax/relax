###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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

import help


class Relax_data:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating R1, R2, and NOE relaxation data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def back_calc(self, run=None, ri_label=None, frq_label=None, frq=None):
        """Function for back calculating relaxation data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength label.

        frq:  The spectrometer frequency in Hz.

        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_data.back_calc("
            text = text + "run=" + `run`
            text = text + ", ri_label=" + `ri_label`
            text = text + ", frq_label=" + `frq_label`
            text = text + ", frq=" + `frq` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relaxation data type.
        if type(ri_label) != str:
            raise RelaxStrError, ('relaxation label', ri_label)

        # Frequency label.
        if type(frq_label) != str:
            raise RelaxStrError, ('frequency label', frq_label)

        # Frequency.
        if type(frq) != float:
            raise RelaxFloatError, ('frequency', frq)

        # Execute the functional code.
        self.__relax__.specific.relax_data.back_calc(run=run, ri_label=ri_label, frq_label=frq_label, frq=frq)


    def copy(self, run1=None, run2=None, ri_label=None, frq_label=None):
        """Function for copying relaxation data from run1 to run2.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run1:  The name of the run to copy the sequence from.

        run2:  The name of the run to copy the sequence to.

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength label.


        Description
        ~~~~~~~~~~~

        This function will copy relaxation data from 'run1' to 'run2'.  If ri_label and frq_label
        are not given then all relaxation data will be copied, otherwise only a specific data set
        will be copied.


        Examples
        ~~~~~~~~

        To copy all relaxation data from run 'm1' to run 'm9', type one of:

        relax> relax_data.copy('m1', 'm9')
        relax> relax_data.copy(run1='m1', run2='m9')
        relax> relax_data.copy('m1', 'm9', None, None)
        relax> relax_data.copy(run1='m1', run2='m9', ri_label=None, frq_label=None)

        To copy only the NOE relaxation data with the frq_label of '800' from 'm3' to 'm6', type one
        of:

        relax> relax_data.copy('m3', 'm6', 'NOE', '800')
        relax> relax_data.copy(run1='m3', run2='m6', ri_label='NOE', frq_label='800')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_data.copy("
            text = text + "run1=" + `run1`
            text = text + ", run2=" + `run2`
            text = text + ", ri_label=" + `ri_label`
            text = text + ", frq_label=" + `frq_label` + ")"
            print text

        # The run1 argument.
        if type(run1) != str:
            raise RelaxStrError, ('run1', run1)

        # The run2 argument.
        if type(run2) != str:
            raise RelaxStrError, ('run2', run2)

        # Relaxation data type.
        if ri_label != None and type(ri_label) != str:
            raise RelaxNoneStrError, ('relaxation label', ri_label)

        # Frequency label.
        if frq_label != None and type(frq_label) != str:
            raise RelaxNoneStrError, ('frequency label', frq_label)

        # Execute the functional code.
        self.__relax__.specific.relax_data.copy(run1=run1, run2=run2, ri_label=ri_label, frq_label=frq_label)


    def delete(self, run=None, ri_label=None, frq_label=None):
        """Function for deleting the relaxation data corresponding to ri_label and frq_label.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength label.


        Examples
        ~~~~~~~~

        To delete the relaxation data corresponding to ri_label='NOE', frq_label='600', and the run
        'm4', type:

        relax> relax_data.delete('m4', 'NOE', '600')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_data.delete("
            text = text + "run=" + `run`
            text = text + ", ri_label=" + `ri_label`
            text = text + ", frq_label=" + `frq_label` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relaxation data type.
        if type(ri_label) != str:
            raise RelaxStrError, ('relaxation label', ri_label)

        # Frequency label.
        if type(frq_label) != str:
            raise RelaxStrError, ('frequency label', frq_label)

        # Execute the functional code.
        self.__relax__.specific.relax_data.delete(run=run, ri_label=ri_label, frq_label=frq_label)


    def display(self, run=None, ri_label=None, frq_label=None):
        """Function for displaying the relaxation data corresponding to ri_label and frq_label.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength label.


        Examples
        ~~~~~~~~

        To display the NOE relaxation data at 600 MHz from the run 'm4', type

        relax> relax_data.display('m4', 'NOE', '600')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_data.display("
            text = text + "run=" + `run`
            text = text + ", ri_label=" + `ri_label`
            text = text + ", frq_label=" + `frq_label` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relaxation data type.
        if type(ri_label) != str:
            raise RelaxStrError, ('relaxation label', ri_label)

        # Frequency label.
        if type(frq_label) != str:
            raise RelaxStrError, ('frequency label', frq_label)

        # Execute the functional code.
        self.__relax__.specific.relax_data.display(run=run, ri_label=ri_label, frq_label=frq_label)


    def read(self, run=None, ri_label=None, frq_label=None, frq=None, file=None, dir=None, num_col=0, name_col=1, data_col=2, error_col=3, sep=None):
        """Function for reading R1, R2, or NOE relaxation data from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength label.

        frq:  The spectrometer frequency in Hz.

        file:  The name of the file containing the relaxation data.

        dir:  The directory where the file is located.

        num_col:  The residue number column (the default is 0, ie the first column).

        name_col:  The residue name column (the default is 1).

        data_col:  The relaxation data column (the default is 2).

        error_col:  The experimental error column (the default is 3).

        sep:  The column separator (the default is white space).


        Description
        ~~~~~~~~~~~

        The frequency label argument can be anything as long as data collected at the same field
        strength have the same label.


        Examples
        ~~~~~~~~

        The following commands will read the NOE relaxation data collected at 600 MHz out of a file
        called 'noe.600.out' where the residue numbers, residue names, data, errors are in the
        first, second, third, and forth columns respectively.

        relax> relax_data.read('m1', 'NOE', '600', 599.7 * 1e6, 'noe.600.out')
        relax> relax_data.read('m1', ri_label='NOE', frq_label='600', frq=600.0 * 1e6,
                               file='noe.600.out')


        The following commands will read the R2 data out of the file 'r2.out' where the residue
        numbers, residue names, data, errors are in the second, third, fifth, and sixth columns
        respectively.  The columns are separated by commas.

        relax> relax_data.read('m1', 'R2', '800 MHz', 8.0 * 1e8, 'r2.out', 1, 2, 4, 5, ',')
        relax> relax_data.read('m1', ri_label='R2', frq_label='800 MHz', frq=8.0*1e8,
                               file='r2.out', num_col=1, name_col=2, data_col=4, error_col=5,
                               sep=',')


        The following commands will read the R1 data out of the file 'r1.out' where the columns are
        separated by the symbol '%'

        relax> relax_data.read('m1', 'R1', '300', 300.1 * 1e6, 'r1.out', sep='%')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_data.read("
            text = text + "run=" + `run`
            text = text + ", ri_label=" + `ri_label`
            text = text + ", frq_label=" + `frq_label`
            text = text + ", frq=" + `frq`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", num_col=" + `num_col`
            text = text + ", name_col=" + `name_col`
            text = text + ", data_col=" + `data_col`
            text = text + ", error_col=" + `error_col`
            text = text + ", sep=" + `sep` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relaxation data type.
        if type(ri_label) != str:
            raise RelaxStrError, ('relaxation label', ri_label)

        # Frequency label.
        if type(frq_label) != str:
            raise RelaxStrError, ('frequency label', frq_label)

        # Frequency.
        if type(frq) != float:
            raise RelaxFloatError, ('frequency', frq)

        # The file name.
        if type(file) != str:
            raise RelaxStrError, ('file', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The number column.
        if type(num_col) != int:
            raise RelaxIntError, ('residue number column', num_col)

        # The name column.
        if type(name_col) != int:
            raise RelaxIntError, ('residue name column', name_col)

        # The data column.
        if type(data_col) != int:
            raise RelaxIntError, ('data column', data_col)

        # The error column.
        if type(error_col) != int:
            raise RelaxIntError, ('error column', error_col)

        # Column separator.
        if sep != None and type(sep) != str:
            raise RelaxNoneStrError, ('column separator', sep)

        # Execute the functional code.
        self.__relax__.specific.relax_data.read(run=run, ri_label=ri_label, frq_label=frq_label, frq=frq, file=file, dir=dir, num_col=num_col, name_col=name_col, data_col=data_col, error_col=error_col, sep=sep)


    def write(self, run=None, ri_label=None, frq_label=None, file=None, dir=None, force=0):
        """Function for writing R1, R2, or NOE relaxation data to a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength label.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which, if set to 1, will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the file will be placed in the current working directory.
        The 'ri_label' and 'frq_label' arguments are required for selecting which relaxation data
        to write to file.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_data.write("
            text = text + "run=" + `run`
            text = text + ", ri_label=" + `ri_label`
            text = text + ", frq_label=" + `frq_label`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relaxation data type.
        if type(ri_label) != str:
            raise RelaxStrError, ('relaxation label', ri_label)

        # Frequency label.
        if type(frq_label) != str:
            raise RelaxStrError, ('frequency label', frq_label)

        # File.
        if file != None and type(file) != str:
            raise RelaxNoneStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # Execute the functional code.
        self.__relax__.specific.relax_data.write(run=run, ri_label=ri_label, frq_label=frq_label, file=file, dir=dir, force=force)
