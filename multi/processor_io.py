###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""Module containing classes for IO stream capture on slave processors."""


class Redirect_text(object):
    """Store the data of the IO streams, prepending a token to each line of written text."""

    def __init__(self, data, token='', stream=0):
        """Set up the text redirection object.

        @param data:        The data object to store all IO in.
        @type data:         list of lists
        @param token:       The string to add to the end of all newlines.
        @type token:        str
        @keyword stream:    The type of steam (0 for STDOUT and 1 for STDERR).
        @type stream:       int
        """

        # Store the args.
        self.data = data
        self.token = token
        self.stream = stream


    def flush(self):
        """Dummy flush method."""


    def isatty(self):
        """Answer that this is not a TTY.

        @return:    False, as this is not a TTY.
        @rtype:     bool
        """

        return False


    def write(self, string):
        """Replacement write() method.
        
        This prepends the token to each line of STDOUT and STDERR and stores the result together with the stream number.

        @param string:  The text to write.
        @type string:   str
        """

        # Append the token to all newline chars.
        string = string.replace('\n', '\n' + self.token)

        # Store the text.
        self.data.append([string, self.stream])
