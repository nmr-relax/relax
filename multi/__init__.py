###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
# Copyright (C) 2011-2012 Edward d'Auvergne                                   #
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

# Package docstring.
"""The multi-processor package.

1 Introduction
==============

This package is an abstraction of specific multi-processor implementations or fabrics such as MPI via mpi4py.  It is designed to be extended for use on other fabrics such as grid computing via SSH tunnelling, threading, etc.  It also has a uni-processor mode as the default fabric.


2 API
=====

The public API is available via the __init__ module.  It consists of a number of functions and classes.  Using this basic interface, code can be parallelised and executed via an MPI implementation, or default back to a single CPU when needed.  The choice of processor fabric is up to the calling program (via multi.load_multiprocessor).


2.1 Program initialisation
--------------------------

The function multi.load_multiprocessor() is the interface for how a program can load and set up a specific processor fabric.  This function returns the set up processor, which itself provides a run() method which is used to execute your application.


2.2 Access to the processor instance
------------------------------------

The multi.Processor_box class is a special singleton object which provides access to the processor object.  This is required for a number of actions:

    - Queuing of slave commands and memos via Processor_box().processor.add_to_queue().
    - Returning results (as a Results_command) from the slave processor to the master via Processor_box().processor.return_object().
    - Determining the number of processes via Processor_box().processor.processor_size().
    - Waiting for completion of the queued slave processors via Processor_box().processor.run_queue().


2.3 Slaves
----------

Slave processors are created via the multi.Slave_command class.  This is special base class which must be subclassed.  The run() function should be overridden, this provides the code to execute on the slave processors.


2.4 Results handling
--------------------

The multi.Result_command class is a special base class which must be subclassed.  The run() function should be overridden, this provides the code for the master to process the results from the slaves.

In addition, the multi.Memo should also be used.  This is a special base class which must be subclassed.  This is a data store used by the Results_command to help process the results from the slave on the master processor.



3 Parallelisation
=================

The following are the steps required to parallelise a calculation via the multi-processor package API.  It is assumed that the multi.load_multiprocessor() function has been set up at the highest level so that the entire program will be executed by the returned processor's run() method.


3.1 Subclassing command and memo objects
----------------------------------------

The first step is that the Slave_command, Result_command, and Memo classes need to be subclassed.  The Slave_command.run() method must be provided and is used for running the calculations on the slave processors.  The Result_command is used to unpack the results from the slave.  It is initialised by the Slave_command itself with the results from the calculation as arguments of __init__().  Its run() method processes the results on the master processor.  The Memo object holds data other than the calculation results required by the Result_command.run() method to process the results.


3.2 Initialisation and queuing
------------------------------

The second step is to initialise the Slave_command and Memo and add these to the processor queue.  But first access to the processor is required.  The singleton multi.Processor_box should be imported, and the processor accessed with code such as::

    # Initialise the Processor box singleton.
    processor_box = Processor_box() 

The slave command is then initialised and all required data by the slave for the calculation (via its run() method) is stored within the class instance.  The memo is also initialised with its data required for the result command for processing on the master of the results from the slave.  These are then queued on the processor::

    # Queue the slave command and memo.
    processor_box.processor.add_to_queue(command, memo)


3.3 Calculation
---------------

To execute the calculations, the final part of the calculation code on the master must feature a call to::

    processor_box.processor.run_queue().


4 Example
=========

See the script 'test_implementation.py' for a basic example of a reference, and full, implementation of the multi-processor package.


5 Issues
========

For multi-core systems and Linux 2.6, the following might be required to prevent the master processor from taking 100% of one CPU core while waiting for the slaves:

# echo "1" > /proc/sys/kernel/sched_compat_yield

This appears to be an OpenMPI problem with late 2.6 Linux kernels.
"""


__all__ = ['api',
           'commands',
           'memo',
           'misc',
           'mpi4py_processor',
           'multi_processor_base',
           'processor_io',
           'processor',
           'uni_processor']

# Python module imports.
import sys as _sys
import traceback as _traceback

# Multi-processor module imports.
from multi.memo import Memo
from multi.misc import import_module as _import_module
from multi.misc import Verbosity as _Verbosity; _verbosity = _Verbosity()
from multi.result_commands import Result_command
from multi.slave_commands import Slave_command


#FIXME error checking for if module required not found.
#FIXME module loading code needs to be in a util module.
#FIXME: remove parameters that are not required to load the module (processor_size).
def load_multiprocessor(processor_name, callback, processor_size, verbosity=1):
    """Load a multi processor given its name.

    Dynamically load a multi processor, the current algorithm is to search in module multi for a
    module called <processor_name>.<Processor_name> (note capitalisation).


    @todo:  This algorithm needs to be improved to allow users to load processors without altering the relax source code.

    @todo:  Remove non-essential parameters.

    @param processor_name:  Name of the processor module/class to load.
    @type processor_name:   str
    @keyword verbosity:     The verbosity level at initialisation.  This can be changed during program execution.  A value of 0 suppresses all output.  A value of 1 causes the basic multi-processor information to be printed.  A value of 2 will switch on a number of debugging print outs.  Values greater than 2 currently do nothing, though this might change in the future.
    @type verbosity:        int
    @return:                A loaded processor object or None to indicate failure.
    @rtype:                 multi.processor.Processor instance
    """

    # Check that the processor type is supported.
    if processor_name not in ['uni', 'mpi4py']:
        _sys.stderr.write("The processor type '%s' is not supported.\n" % processor_name)
        _sys.exit()

    # Store the verbosity level.
    _verbosity.set(verbosity)

    # The Processor details.
    processor_name = processor_name + '_processor'
    class_name = processor_name[0].upper() + processor_name[1:]
    module_path = '.'.join(('multi', processor_name))

    # Load the module containing the specific processor.
    modules = _import_module(module_path)

    # Access the class from within the module.
    if hasattr(modules[-1], class_name):
        clazz = getattr(modules[-1], class_name)
    else:
        raise Exception("can't load class %s from module %s" % (class_name, module_path))

    # Instantiate the Processor.
    object = clazz(callback=callback, processor_size=processor_size)

    # Load the Processor_box container and store the details and Processor instance.
    processor_box = Processor_box()
    processor_box.processor = object
    processor_box.processor_name = processor_name
    processor_box.class_name = class_name

    # Return the Processor instance.
    return object


def fetch_data(name=None):
    """API function for obtaining data from the Processor instance's data store.

    This is for fetching data from the data store of the Processor instance.  If run on the master, then the master's data store will be accessed.  If run on the slave, then the slave's data store will be accessed.


    @keyword name:  The name of the data structure to fetch.
    @type name:     str
    @return:        The value of the associated data structure.
    @rtype:         anything
    """

    # Load the Processor_box.
    processor_box = Processor_box()

    # Forward the call to the processor instance.
    return processor_box.processor.fetch_data(name=name)


def send_data_to_slaves(name=None, value=None):
    """API function for sending data from the master to all slaves processors.

    @keyword name:  The name of the data structure to store.
    @type name:     str
    @keyword value: The data structure.
    @type value:    anything
    """

    # Load the Processor_box.
    processor_box = Processor_box()

    # Forward the call to the processor instance.
    processor_box.processor.send_data_to_slaves(name=name, value=value)



class Application_callback(object):
    """Call backs provided to the host application by the multi processor framework.

    This class allows for independence from the host class/application.

    @note:  B{The logic behind the design} the callbacks are defined as two attributes
            self.init_master and self.handle_exception as handle_exception can be null (which is
            used to request the use of the processors default error handling code). Note, however,
            that a class with the equivalent methods would also works as python effectively handles
            methods as attributes of a class. The signatures for the callback methods are documented
            by the default methods default_init_master & default_handle_exception.
    """

    def __init__(self, master):
        """Initialise the callback interface.

        @param master:  The data for the host application. In the default implementation this is an
                        object we call methods on but it could be anything...
        @type master:   object
        """

        self.master = master
        """The host application."""

        self.init_master = self.default_init_master
        self.handle_exception = self.default_handle_exception


    def default_handle_exception(self, processor, exception):
        """Handle an exception raised in the processor framework.

        The function is responsible for aborting the processor by calling processor.abort() as its
        final act.

        @param processor:   The processor instance.
        @type processor:    multi.processor.Processor instance
        @param exception:   The exception raised by the processor or slave processor. In the case of
                            a slave processor exception this may well be a wrapped exception of type
                            multi.processor.Capturing_exception which was raised at the point the
                            exception was received on the master processor but contains an enclosed
                            exception from a slave.
        @type exception:    Exception instance
        """

        # Print the traceback.
        _traceback.print_exc(file=_sys.stderr)

        # Stop the processor.
        processor.abort()


    def default_init_master(self, processor):
        """Start the main loop of the host application.

        @param processor:   The processor instance.
        @type processor:    multi.processor.Processor instance
        """

        self.master.run()



class Processor_box(object):
    """A storage class for the Processor instance and its attributes.

    This singleton contains Processor instances and information about these Processors.  Importantly
    this container gives the calling code access to the Processor.
    """

    # Class variable for storing the class instance.
    instance = None

    def __new__(self, *args, **kargs): 
        """Replacement function for implementing the singleton design pattern."""

        # First initialisation.
        if self.instance is None:
            self.instance = object.__new__(self, *args, **kargs)

        # Already initialised, so return the instance.
        return self.instance
