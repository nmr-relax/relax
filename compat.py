###############################################################################
#                                                                             #
# Copyright (C) 2012-2013 Edward d'Auvergne                                   #
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

# The platform script message.
try:
    import platform
except ImportError:
    print("The platform module cannot be imported.  For Python <= 2.2, try copying the platform.py file from http://hg.python.org/cpython/file/2.3/Lib/platform.py into your lib/pythonX.X/ directory.")
    raise

# Dependency check module.
import dep_check

# Python module imports.
if dep_check.bz2_module:
    import bz2
    from bz2 import BZ2File
else:
    BZ2File = object
if dep_check.gzip_module:
    import gzip
else:
    gzip = object
from copy import deepcopy
if dep_check.io_module:
    import io
import os
import platform
import sys
import threading


# The operating system.
SYSTEM = platform.uname()[0]

# The Python version.
PY_VERSION = sys.version_info[0]


# Special Python version specific imports.  These will be imported from here from the rest of relax.
####################################################################################################

# The built-in module.
if PY_VERSION == 2:
    import __builtin__ as builtins
else:
    import builtins

# The queue module.
if PY_VERSION == 2:
    import Queue as queue
else:
    import queue

# The queue.Queue class
if PY_VERSION == 2:
    from Queue import Queue as Queue2
else:
    from queue import Queue as Queue3
    Queue2 = Queue3

# The StringIO class.
if PY_VERSION == 2:
    from cStringIO import StringIO
elif dep_check.io_module:
    from io import StringIO
else:
    StringIO = None

# The unit test TextTestResult class.
try:
    from unittest import TextTestResult    # Python 2.7 and above.
except ImportError:
    from unittest import _TextTestResult as TextTestResult    # Python 2.6 and below.

# The pickle package.
if PY_VERSION == 2:
    import cPickle as pickle
else:
    import pickle


def bz2_open(file, mode='r'):
    """Abstract the numerous ways BZ2 files are handled in Python.

    @param file:    The file path to open.
    @type file:     str
    @keyword mode:  The mode to open the file with.  Only the values of 'r' and 'w' for reading and writing respectively are supported.
    @type model:    str
    @return:        The bzip2 file object.
    @rtype:         file object
    """

    # Check the mode.
    if mode not in ['r', 'w']:
        raise RelaxError("The mode '%s' must be one or 'r' or 'w'." % mode)

    # Check if the bz2 module exists.
    if not dep_check.bz2_module:
        if mode == 'r':
            raise RelaxError("Cannot open the file %s, try uncompressing first.  %s." % (file, dep_check.bz2_module_message))
        else:
            raise RelaxError("Cannot create bzip2 file %s, the bz2 Python module cannot be found." % file)

    # Open the file for reading.
    if mode == 'r':
        # Python 3.3 text mode.
        if sys.version_info[0] == 3 and sys.version_info[1] >= 3:
            file_obj = bz2.open(file, 't')

        # Python 3.0, 3.1 and 3.2 text mode.
        elif sys.version_info[0] == 3 and sys.version_info[1] < 3:
            file_obj = io.TextIOWrapper(Bzip2Fixed(file, 'r'))

        # Python 2 text mode.
        else:
            file_obj = bz2.BZ2File(file, 'r')

    # Open the file for writing.
    elif mode == 'w':
        # Python 3.3 text mode.
        if sys.version_info[0] == 3 and sys.version_info[1] >= 3:
            file_obj = bz2.open(file, 'wt')

        # Python 3.0, 3.1 and 3.2 text mode.
        elif sys.version_info[0] == 3 and sys.version_info[1] < 3:
            file_obj = io.TextIOWrapper(Bzip2Fixed(file, 'w'))

        # Python 2 text mode.
        else:
            file_obj = bz2.BZ2File(file, 'w')

    # Return the file object.
    return file_obj


def gz_open(file, mode='r'):
    """Abstract the numerous ways gzipped files are handled in Python.

    @param file:    The file path to open.
    @type file:     str
    @keyword mode:  The mode to open the file with.  Only the values of 'r' and 'w' for reading and writing respectively are supported.
    @type model:    str
    @return:        The gzipped file object.
    @rtype:         file object
    """

    # Check the mode.
    if mode not in ['r', 'w']:
        raise RelaxError("The mode '%s' must be one or 'r' or 'w'." % mode)

    # Check if the bz2 module exists.
    if not dep_check.gzip_module:
        if mode == 'r':
            raise RelaxError("Cannot open the file %s, try uncompressing first.  %s." % (file, dep_check.gzip_module_message))
        else:
            raise RelaxError("Cannot create gzipped file %s, the bz2 Python module cannot be found." % file)

    # Open the file for reading.
    if mode == 'r':
        # Python 3.3 text mode.
        if sys.version_info[0] == 3 and sys.version_info[1] >= 3:
            file_obj = gzip.open(file, 'rt')

        # Python 3.0, 3.1 and 3.2 text mode.
        elif sys.version_info[0] == 3 and sys.version_info[1] < 3:
            file_obj = io.TextIOWrapper(GzipFixed(file, 'r'))

        # Python 2 text mode.
        else:
            file_obj = gzip.GzipFile(file, 'r')

    # Open the file for writing.
    elif mode == 'w':
        # Python 3.3 text mode.
        if sys.version_info[0] == 3 and sys.version_info[1] >= 3:
            file_obj = gzip.open(file, 'wt')

        # Python 3.0, 3.1 and 3.2 text mode.
        elif sys.version_info[0] == 3 and sys.version_info[1] < 3:
            file_obj = io.TextIOWrapper(GzipFixed(file, 'w'))

            # Python 2 text mode.
        else:
            file_obj = gzip.GzipFile(file, 'w')

    # Return the file object.
    return file_obj


def sorted(data):
    """Python 2.3 and earlier replacement function for the builtin sorted() function."""

    # Make a copy of the data.
    new_data = deepcopy(data)

    # Sort.
    new_data.sort()

    # Return the new data.
    return new_data



class Bzip2Fixed(BZ2File):
    """Incredibly nasty hack for bzip2 files support in Python 3.0, 3.1 and 3.2."""

    def flush(self):
        pass

    def read1(self, n):
        return self.read(n)

    def readable(self):
        return True

    def seekable(self):
        return True

    def writable(self):
        return True



class GzipFixed(gzip.GzipFile):
    """Incredibly nasty hack for gzipped files support in Python 3.0, 3.1 and 3.2."""

    closed = False

    def read1(self, n):
        return self.read(n)

    def readable(self):
        return True

    def seekable(self):
        return True

    def writable(self):
        return True



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
if PY_VERSION == 2 and sys.version_info[1] <= 4:
    Queue = TaskQueue    # Alias the TaskQueue for Python 2.4 and earlier.
elif PY_VERSION == 2:
    Queue = Queue2
else:
    Queue = Queue3


# Python 2 hacks.
if PY_VERSION == 2:
    # Switch all range() calls to xrange() for increased speed and memory reduction.
    # This should work as all range() usage for Python 3 in relax must match the old xrange() usage.
    builtins.range = builtins.xrange

    # The sorted() builtin function for Python 2.3 and earlier.
    if sys.version_info[1] <= 3:
        setattr(builtins, 'sorted', sorted)

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
if PY_VERSION == 3:
    # The unicode conversion function - essential for the GUI in Python 2.
    builtins.unicode = builtins.str
