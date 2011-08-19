###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
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
from StringIO import StringIO
import sys
from threading import currentThread


class PrependOut:
    """Class for adding a token to the end of all newlines."""

    def __init__(self, token, stream):
        """Set up the class for stream manipulation.

        @param token:   The string to add to the end of all newlines.
        @type token:    str
        @param stream:  The IO stream
        @type stream:   IO stream
        """

        # Execute the base class __init__() method.
        StringIO.__init__(self)

        # Store the args.
        self.token = token
        self.stream = stream


    def write(self, string):
        """Replacement write() method for prepending the token to each line of STDOUT and STDERR.

        @param string:  The line of text to write to STDOUT or STDERR.
        @type string:   str
        """

        # Append the token to all newline chars.
        string = string.replace('\n', '\n' + self.token)

        # Write the string to the stream.
        self.stream.write(string)

        # Flush both STDOUT and STDERR.
        sys.stdout.flush()
        sys.stderr.flush()


class PrependStringIO(StringIO):
    """Class for adding a token to the end of all newlines."""

    def __init__(self, token, stream=None):
        """Set up the class for stream manipulation.

        @param token:   The string to add to the end of all newlines.
        @type token:    str
        @param stream:  The IO stream
        @type stream:   IO stream
        """

        # Execute the base class __init__() method.
        StringIO.__init__(self)

        # Store the args.
        self.token = token

        # Set up the stream.
        if stream == None:
            self.stream = self
        else:
            self.stream = stream

        # Initialise.
        self.token_length = len(token)
        self.first_time = True


    def write(self, string):
        """Replacement write() method for prepending the token to each line of STDOUT and STDERR.

        @param string:  The line of text to write to STDOUT or STDERR.
        @type string:   str
        """

        # FIXME: raising an exception here wedges mpi4py

        # Append the token to all newline chars.
        string = string.replace('\n', '\n' + self.token)

        # Handle the first line of output.
        if self.first_time == True:
            string = '\n' + self.token + string
            self.first_time = False

        # Write the string to the stream.
        StringIO.write(self.stream, string)

        # Flush both STDOUT and STDERR.
        sys.stdout.flush()
        sys.stderr.flush()
