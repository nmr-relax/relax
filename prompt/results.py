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


class Results:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating results."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def display(self, run=None, format='columnar'):
        """Function for displaying the results of the run.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        format:  The format of the output.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "results.display("
            text = text + "run=" + `run`
            text = text + ", format=" + `format` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.results.display(run=run)


    def read(self, run=None, file='results', dir='run', format='columnar'):
        """Function for reading results from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the file to read results from.

        dir:  The directory where the file is located.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the results file will be searched for in a directory named
        after the run name.  To search for the results file in the current working directory, set
        dir to None.

        This function is able to handle uncompressed, bzip2 compressed files, or gzip compressed
        files automatically.  The full file name including extension can be supplied, however, if
        the file cannot be found, this function will search for the file name with '.bz2' appended
        followed by the file name with '.gz' appended.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "results.read("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            if dir == 'run':
                text = text + ", dir=" + `run`
            else:
                text = text + ", dir=" + `dir`
            text = text + ", format=" + `format` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Format.
        if type(format) != str:
            raise RelaxStrError, ('format', format)

        # Execute the functional code.
        self.__relax__.generic.results.read(run=run, file=file, directory=dir, format=format)


    def write(self, run=None, file='results', dir='run', force=0, format='columnar', compress_type=1):
        """Function for writing results of the run to a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the file to output results to.  The default is 'results'.

        dir:  The directory name.

        force:  A flag which, if set to 1, will cause the results file to be overwritten.

        format:  The format of the output.

        compress_type:  The type of compression to use when creating the file.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the results file will be placed in a directory named after
        the run name.  To place the results file in the current working directory, set dir to None.

        The default behaviour of this function is to compress the file using bzip2 compression.  If
        the extension '.bz2' is not included in the file name, it will be added.  The compression
        can, however, be changed to either no compression or gzip compression.  This is controlled
        by the compress_type argument which can be set to

            0:  No compression (no file extension),
            1:  bzip2 compression ('.bz2' file extension),
            2:  gzip compression ('.gz' file extension).

        The complementary read function will automatically handle the compressed files.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "results.write("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            if dir == 'run':
                text = text + ", dir=" + `run`
            else:
                text = text + ", dir=" + `dir`
            text = text + ", force=" + `force`
            text = text + ", format=" + `format`
            text = text + ", compress_type=" + `compress_type` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # Format.
        if type(format) != str:
            raise RelaxStrError, ('format', format)

        # Compression type.
        if type(compress_type) != int:
            raise RelaxIntError, ('compression type', compress_type)

        # Execute the functional code.
        self.__relax__.generic.results.write(run=run, file=file, directory=dir, force=force, format=format, compress_type=compress_type)
