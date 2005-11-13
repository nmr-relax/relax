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


class State:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for saving or loading the program state."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def load(self, file=None, dir=None):
        """Function for loading a saved program state.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The file name, which must be a string, of a saved program state.

        dir:  Directory which the file is found in.


        Description
        ~~~~~~~~~~~

        This function is able to handle uncompressed, bzip2 compressed files, or gzip compressed
        files automatically.  The full file name including extension can be supplied, however, if
        the file cannot be found, this function will search for the file name with '.bz2' appended
        followed by the file name with '.gz' appended.


        Examples
        ~~~~~~~~

        The following commands will load the state saved in the file 'save'.

        relax> state.load('save')
        relax> state.load(file='save')


        The following commands will load the state saved in the bzip2 compressed file 'save.bz2'.

        relax> state.load('save')
        relax> state.load(file='save')
        relax> state.load('save.bz2')
        relax> state.load(file='save.bz2')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "state.load("
            text = text + "file=" + `file`
            text = text + ", dir=" + `dir` + ")"
            print text

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory', dir)

        # Execute the functional code.
        self.__relax__.generic.state.load(file=file, dir=dir)


    def save(self, file=None, dir=None, force=0, compress_type=1):
        """Function for saving the program state.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The file name, which must be a string, to save the current program state in.

        dir:  The directory to place the file in.

        force:  A flag which if set to 1 will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        The default behaviour of this function is to compress the file using bzip2 compression.  If
        the extension '.bz2' is not included in the file name, it will be added.  The compression
        can, however, be changed to either no compression or gzip compression.  This is controlled
        by the compress_type argument which can be set to

            0:  No compression (no file extension).
            1:  bzip2 compression ('.bz2' file extension).
            2:  gzip compression ('.gz' file extension).


        Examples
        ~~~~~~~~

        The following commands will save the current program state into the file 'save':

        relax> state.save('save', compress_type=0)
        relax> state.save(file='save', compress_type=0)


        The following commands will save the current program state into the bzip2 compressed file
        'save.bz2':

        relax> state.save('save')
        relax> state.save(file='save')
        relax> state.save('save.bz2')
        relax> state.save(file='save.bz2')


        If the file 'save' already exists, the following commands will save the current program
        state by overwriting the file.

        relax> state.save('save', 1)
        relax> state.save(file='save', force=1)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "state.save("
            text = text + "file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force`
            text = text + ", compress_type=" + `compress_type` + ")"
            print text

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory', dir)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # Compression type.
        if type(compress_type) != int:
            raise RelaxIntError, ('compression type', compress_type)

        # Execute the functional code.
        self.__relax__.generic.state.save(file=file, dir=dir, force=force, compress_type=compress_type)
