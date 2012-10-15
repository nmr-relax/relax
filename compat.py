###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Temporary module for allowing relax to support both Python 2 and 3."""

# Python module imports.
import sys
from copy import deepcopy
import os
import platform
if sys.version_info[0] == 2:
    from Queue import Queue as Queue2
else:
    from queue import Queue as Queue3
import threading


# The operating system.
SYSTEM = platform.uname()[0]


def sorted(data):
    """Python 2.3 and earlier replacement function for the builtin sorted() function."""

    # Make a copy of the data.
    new_data = deepcopy(data)

    # Sort.
    new_data.sort()

    # Return the new data.
    return new_data



class TaskQueue(Queue2):
    """Python 2.4 and earlier Queuing class replacement.

    This code comes from http://code.activestate.com/recipes/475160/ and is part of the Python sources from 2.5 onwards.
    """

    def __init__(self):
        Queue2.__init__(self)        
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    def _put(self, item):
        Queue2._put(self, item)
        self.unfinished_tasks += 1        

    def task_done(self):
        """Indicate that a formerly enqueued task is complete.

        Used by Queue consumer threads.  For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task is complete.

        If a join() is currently blocking, it will resume when all items
        have been processed (meaning that a task_done() call was received
        for every item that had been put() into the queue).

        Raises a ValueError if called more times than there were items
        placed in the queue.
        """
        self.all_tasks_done.acquire()
        try:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notifyAll()
            self.unfinished_tasks = unfinished
        finally:
            self.all_tasks_done.release()

    def join(self):
        """Blocks until all items in the Queue have been gotten and processed.

        The count of unfinished tasks goes up whenever an item is added to the
        queue. The count goes down whenever a consumer thread calls task_done()
        to indicate the item was retrieved and all work on it is complete.

        When the count of unfinished tasks drops to zero, join() unblocks.
        """
        self.all_tasks_done.acquire()
        try:
            while self.unfinished_tasks:
                self.all_tasks_done.wait()
        finally:
            self.all_tasks_done.release()


# Alias the correct Queue.
if sys.version_info[0] == 2 and sys.version_info[1] <= 4:
    Queue = TaskQueue    # Alias the TaskQueue for Python 2.4 and earlier.
elif sys.version_info[0] == 2:
    Queue = Queue2
else:
    Queue = Queue3


# The Python version.
py_version = sys.version_info[0]

# Python 2 hacks.
if py_version == 2:
    # Python 2 only imports.
    import __builtin__

    # Switch all range() calls to xrange() for increased speed and memory reduction.
    # This should work as all range() usage for Python 3 in relax must match the old xrange() usage.
    __builtin__.range = __builtin__.xrange

    # The sorted() builtin function for Python 2.3 and earlier.
    if sys.version_info[1] <= 3:
        setattr(__builtin__, 'sorted', sorted)

    # The os.devnull object for Python 2.3 and earlier.
    if sys.version_info[1] <= 3:
        if SYSTEM == 'Linux':
            os.devnull = '/dev/null'
        elif SYSTEM == 'Windows' or SYSTEM == 'Microsoft':
            os.devnull = 'nul'
        elif SYSTEM == 'Darwin':
            os.devnull = 'Dev:Null'
        else:
            os.devnull = None


# Python 3 work-arounds.
if py_version == 3:
    # Python 3 only imports.
    import builtins

    # The unicode conversion function - essential for the GUI in Python 2.
    builtins.unicode = builtins.str
