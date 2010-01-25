###############################################################################
#                                                                             #
# Copyright (C) 2003-2005,2008-2010 Edward d'Auvergne                         #
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
"""Module containing the 'results' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from generic_fns import results


class Results(User_fn_class):
    """Class for manipulating results."""

    def display(self):
        """Function for displaying the results.

        Description
        ~~~~~~~~~~~

        This will print to screen (STDOUT) the results contained within the current data pipe.
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "results.display()"
            print(text)

        # Execute the functional code.
        results.display()


    def read(self, file='results', dir=None):
        """Function for reading results from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the file to read results from.

        dir:  The directory where the file is located.


        Description
        ~~~~~~~~~~~

        To search for the results file in the current working directory, set dir to None.

        This function is able to handle uncompressed, bzip2 compressed files, or gzip compressed
        files automatically.  The full file name including extension can be supplied, however, if
        the file cannot be found, this function will search for the file name with '.bz2' appended
        followed by the file name with '.gz' appended.
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "results.read("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)

        # Execute the functional code.
        results.read(file=file, directory=dir)


    def write(self, file='results', dir='pipe_name', compress_type=1, force=False):
        """Function for writing results to a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the file to output results to.  The default is 'results'.  Optionally
        this can be a file object, or any object with a write() method.

        dir:  The directory name.

        compress_type:  The type of compression to use when creating the file.

        force:  A flag which if True will cause the results file to be overwritten.


        Description
        ~~~~~~~~~~~

        To place the results file in the current working directory, set dir to None.  If dir is set
        to the special name 'pipe_name', then the results file will be placed into a directory with
        the same name as the current data pipe.

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
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "results.write("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", compress_type=" + repr(compress_type)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str_or_inst(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_int(compress_type, 'compression type')
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        results.write(file=file, directory=dir, force=force, compress_type=compress_type)
