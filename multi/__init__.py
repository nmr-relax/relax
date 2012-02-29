###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
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


__all__ = ['commands',
           'mpi4py_processor',
           'multi_processor_base',
           'processor_io',
           'processor',
           'uni_processor']

__doc__ = \
"""Package for multi-processor code execution."""

# Python module imports.
import sys as _sys
import traceback as _traceback

# Multi-processor module imports.
from api import Result_command, Slave_command
from memo import Memo
from misc import import_module as _import_module


#FIXME error checking for if module required not found.
#FIXME module loading code needs to be in a util module.
#FIXME: remove parameters that are not required to load the module (processor_size).
def load_multiprocessor(processor_name, callback, processor_size):
    '''Load a multi processor given its name.

    Dynamically load a multi processor, the current algorithm is to search in module multi for a
    module called <processor_name>.<Processor_name> (note capitalisation).


    @todo:  This algorithm needs to be improved to allow users to load processors without altering
            the relax source code.

    @todo:  Remove non-essential parameters.

    @param processor_name:  Name of the processor module/class to load.
    @type processor_name:   str
    @return:                A loaded processor object or None to indicate failure.
    @rtype:                 multi.processor.Processor instance
    '''

    # Check that the processor type is supported.
    if processor_name not in ['uni', 'mpi4py']:
        _sys.stderr.write("The processor type '%s' is not supported.\n" % processor_name)
        _sys.exit()

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



class Application_callback(object):
    '''Call backs provided to the host application by the multi processor framework.

    This class allows for independence from the host class/application.

    @note:  B{The logic behind the design} the callbacks are defined as two attributes
            self.init_master and self.handle_exception as handle_exception can be null (which is
            used to request the use of the processors default error handling code). Note, however,
            that a class with the equivalent methods would also works as python effectively handles
            methods as attributes of a class. The signatures for the callback methods are documented
            by the default methods default_init_master & default_handle_exception.
    '''

    def __init__(self, master):
        '''Initialise the callback interface.

        @param master:  The data for the host application. In the default implementation this is an
                        object we call methods on but it could be anything...
        @type master:   object
        '''

        self.master = master
        '''The host application.'''

        self.init_master = self.default_init_master
        self.handle_exception = self.default_handle_exception


    def default_handle_exception(self, processor, exception):
        '''Handle an exception raised in the processor framework.

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
        '''

        # Print the traceback.
        _traceback.print_exc(file=_sys.stderr)

        # Stop the processor.
        processor.abort()


    def default_init_master(self, processor):
        '''Start the main loop of the host application.

        @param processor:   The processor instance.
        @type processor:    multi.processor.Processor instance
        '''

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
