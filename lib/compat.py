###############################################################################
#                                                                             #
# Copyright (C) 2012-2014,2019 Edward d'Auvergne                              #
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

# Python module imports.
try:
    import bz2
    from bz2 import BZ2File
    bz2_module = True
except ImportError:
    BZ2File = object
    bz2_module = False
    message = sys.exc_info()[1]
    bz2_module_message = message.args[0]
try:
    import gzip
    gzip_module = True
except ImportError:
    gzip = object
    gzip_module = False
    message = sys.exc_info()[1]
    gzip_module_message = message.args[0]
try:
    import io
    io_module = True
    from io import IOBase
except ImportError:
    io_module = False
    IOBase = None
import itertools
import os
import platform
import sys
import threading


# The operating system.
SYSTEM = platform.uname()[0]
if SYSTEM == 'Microsoft':
    SYSTEM == 'Windows'

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
elif io_module:
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

# Numpy.
import numpy
try:
    numpy.linalg.norm(numpy.ones((3, 3)), axis=1)
    numpy_norm_axis = True
except:
    numpy_norm_axis = False

# Linux distribution information.
try:
    from platform import linux_distribution
except ImportError:
    try:
        from distro import linux_distribution
    except ImportError:
        def linux_distribution(): return ["", "", ""]


def bz2_open(file, mode='r'):
    """Abstract the numerous ways BZ2 files are handled in Python.

    @param file:    The file path to open.
    @type file:     str
    @keyword mode:  The mode to open the file with.  Only the values of 'r' and 'w' for reading and writing respectively are supported.
    @type mode:     str
    @return:        The bzip2 file object.
    @rtype:         file object
    """

    # Check the mode.
    if mode not in ['r', 'w']:
        raise RelaxError("The mode '%s' must be one or 'r' or 'w'." % mode)

    # Check if the bz2 module exists.
    if not bz2_module:
        if mode == 'r':
            raise RelaxError("Cannot open the file %s, try uncompressing first.  %s." % (file, bz2_module_message))
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
    @type mode:     str
    @return:        The gzipped file object.
    @rtype:         file object
    """

    # Check the mode.
    if mode not in ['r', 'w']:
        raise RelaxError("The mode '%s' must be one or 'r' or 'w'." % mode)

    # Check if the bz2 module exists.
    if not gzip_module:
        if mode == 'r':
            raise RelaxError("Cannot open the file %s, try uncompressing first.  %s." % (file, gzip_module_message))
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


def from_iterable(items):
    """Implementation of the itertools.chain.from_iterable() function for all Python versions.

    @param items:   The normal argument for itertools.chain.from_iterable().
    @type items:    list
    @return:        The items of the list.
    @rtype:         unknown
    """

    # Default to the normal function.
    if hasattr(itertools.chain, 'from_iterable'):
        return itertools.chain.from_iterable(items)

    # Reimplement the function for earlier Python versions.
    return from_iterable_pre_2_6(items)


def from_iterable_pre_2_6(items):
    """Replacement itertools.chain.from_iterable() function for Python < 2.6.

    @param items:   The normal argument for itertools.chain.from_iterable().
    @type items:    list
    @return:        The elements
    @rtype:         unknown
    """

    for item in items:
        for element in item:
            yield element


def norm(x, ord=None, axis=None):
    """Replacement numpy.linalg.norm() function to handle the axis argument for old numpy.

    @param x:       Input array.  If `axis` is None, `x` must be 1-D or 2-D.
    @type x:        array_like
    @keyword ord:   Order of the norm (see table under ``Notes``). inf means numpy's `inf` object.
    @type ord:      {non-zero int, inf, -inf, 'fro'}, optional
    @keyword axis:  If `axis` is an integer, it specifies the axis of `x` along which to compute the vector norms.  If `axis` is a 2-tuple, it specifies the axes that hold 2-D matrices, and the matrix norms of these matrices are computed.  If `axis` is None then either a vector norm (when `x` is 1-D) or a matrix norm (when `x` is 2-D) is returned.
    @type axis:     {int, 2-tuple of ints, None}, optional
    """

    # No axis argument given.
    if axis == None:
        return numpy.linalg.norm(x, ord=ord)

    # The axis argument exists.
    if numpy_norm_axis:
        return numpy.linalg.norm(x, ord=ord, axis=axis)

    # Support for older version (this is much slower).
    return numpy.apply_along_axis(numpy.linalg.norm, axis, x)



# The inspect module.
inspect_getfullargspec = False
try:
    from inspect import getfullargspec
    inspect_getfullargspec = True
except ImportError:
    from inspect import getargspec


def getfullargspec_replacement(obj):
    """Replacement inspect.getfullargspec() function for Python versions without it."""

    return getargspec(obj) + (None, None, None)


if not inspect_getfullargspec:
    getfullargspec = getfullargspec_replacement


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
    #builtins.range = builtins.xrange

    # The os.devnull object for Python 2.3 and earlier.
    if sys.version_info[1] <= 3:
        if SYSTEM == 'Linux':
            os.devnull = '/dev/null'
        elif SYSTEM == 'Windows':
            os.devnull = 'nul'
        elif SYSTEM == 'Darwin':
            os.devnull = 'Dev:Null'
        else:
            os.devnull = None

    # The unicode conversion function - essential for the GUI in Python 2.
    unicode = builtins.unicode

    # Unicode string handling.
    from codecs import unicode_escape_decode
    def u(text):
        """Create a unicode string for Python 2.

        @param text:    The text to convert.
        @type text:     str
        @return:        The text converted to unicode.
        @rtype:         unicode
        """

        return unicode_escape_decode(text)[0]


# Python 3 work-arounds.
if PY_VERSION == 3:
    # The unicode conversion function - essential for the GUI in Python 2.
    unicode = builtins.str

    # Unicode string handling.
    def u(text):
        """Create a unicode string for Python 3.

        @param text:    The text to convert.
        @type text:     str
        @return:        The unmodified text, as all strings in Python 3 are unicode and the unicode type does not exist.
        @rtype:         str
        """

        return text
