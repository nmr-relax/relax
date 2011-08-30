###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""A threaded version of the relax interpreter for use by the GUI."""

# Python module imports.
from Queue import Queue
from re import search
from string import split
import sys
from threading import Thread
from time import sleep
from traceback import print_exc
import wx

# relax module imports.
from prompt import interpreter
from relax_errors import AllRelaxErrors
from status import Status; status = Status()

# relax GUI module imports.
from gui.errors import gui_raise


class Interpreter(Thread):
    """The threaded interpreter."""

    def __init__(self):
        """Initialise the object."""

        # Set up the thread object.
        Thread.__init__(self)

        # Set the thread to be daemonic so that relax can exit.
        self.daemon = True

        # Create a queue object for the user function calls.
        self._queue = Queue()

        # Load a copy of the relax interpreter.
        self._interpreter = interpreter.Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self._interpreter.populate_self()
        self._interpreter.on(verbose=False)

        # A flag for exiting the thread.
        self._exit = False


    def _get_uf(self, uf):
        """Return the user function object corresponding to the given string.

        @param uf:  The name of the user function.
        @type uf:   str
        @return:    The user function object.
        @rtype:     func
        """

        # Handle the user function class.
        if search('\.', uf):
            # Split the user function.
            uf_class, uf_fn = split(uf, '.')

            # Get the user function class.
            obj = getattr(self._interpreter, uf_class)

            # Get the function.
            fn = getattr(obj, uf_fn)

        # Simple user function.
        else:
            fn = getattr(self._interpreter, uf)

        # Return the user function.
        return fn


    def empty(self):
        """Wrapper method for the Queue.empty() method."""

        # Return the queue empty state.
        return self._queue.empty()


    def exit(self):
        """Cause the thread to exit once the currently running user function is complete."""

        # First set the flag.
        self._exit = True

        # Then queue a dummy user function.
        self._queue.put([None, None, None])


    def flush(self):
        """Return only once the queue is empty."""

        # Loop until empty.
        while not self.empty():
            sleep(0.2)


    def join(self):
        """Wrapper method for the Queue.join() method."""

        # Join the queue.
        self._queue.join()


    def queue(self, uf, *args, **kwds):
        """Queue up a user function."""

        # Place the user function and its args onto the queue.
        self._queue.put([uf, args, kwds])


    def run(self):
        """Execute the thread."""

        # Loop until told to exit.
        while not self._exit:
            # Get the user function from the queue.
            uf, args, kwds = self._queue.get()

            # No user function.
            if uf == None:
                continue

            # Execution lock.
            status.exec_lock.acquire('gui', mode='interpreter thread')

            # Execute the user function, catching errors.
            try:
                # Get the user function.
                fn = self._get_uf(uf)

                # Apply the user function.
                apply(fn, args, kwds)

            # Catch all RelaxErrors.
            except AllRelaxErrors, instance:
                # Display a dialog with the error.
                wx.CallAfter(gui_raise, instance, raise_flag=False)

            # Handle all other errors.
            except:
                # Print the exception.
                print_exc()

            # Release the lock.
            finally:
                status.exec_lock.release()

