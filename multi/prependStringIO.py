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


class Multiplex_stdout(StringIO):
    def __init__(self):
        StringIO.__init__(self)
        self.thread_stream_map = {}


    def add_stream(self, stream):
        thread_id = self.current_thread_id()
        self.thread_stream_map[thread_id] = stream


    def current_thread_id(self):
        return self.thread_id(currentThread())


    def get_stream(self, thread=None):
        if thread == None:
            thread_id = self.current_thread_id()
        else:
            thread_id = self.thread_id(thread)

        return self.thread_stream_map[thread_id]


    def getvalue(self):
        return self.get_stream().getvalue()


    def thread_id(self, thread):
        # wanted to use thread.get_ident but main thread barfes on it could use -1?
        return id(thread)


    def write(self, string):
        thread = currentThread()
        thread_id = self.thread_id(thread)

        stream = self.thread_stream_map[thread_id]
        return stream.write(string)



class PrependOut(StringIO):
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

        # Write the string to the stream and flush.
        self.stream.write(string)
        self.stream.flush()


#TODO: maybe this hsould be a delegate to a stringio rather than being a stringio as this will speed things up and simplify things
class PrependStringIO(StringIO):
    def __init__(self, token, target_stream=None):
        StringIO.__init__(self)
        self.token = token
        self.token_length = len(token)
        self.first_time = True
        if target_stream == None:
            self.target_stream = self
        else:
            self.target_stream = target_stream


    def getvalue(self):
        result = StringIO.getvalue(self)
        if len(result) > 0 and result[-1] == '\n':
           result = result[0:-self.token_length-1]
           result = result+'\n'

        return result


    def truncate(self, size=None):
        if size == 0:
           self.first_time = True
        #PY3K: should be a call to super but StringIO is a old style class
        StringIO.truncate(self, size)


    def write(self, string):
        # FIXME: raising an exception here wedges mpi4py

        string = string.replace('\n', '\n' + self.token)
        if self.first_time == True:
            string = '\n' + self.token + string
            self.first_time = False

        StringIO.write(self.target_stream, string)
