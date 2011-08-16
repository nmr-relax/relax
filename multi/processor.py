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

# Module docstring.
'''The processor class is the central class in the multi python multiprocessor framework.

Overview
========

The framework has two main responsibilities:

     1. Process management - if needed the processor can create the slave processes it manages if
        they haven't been created by the operating system. It is also responsible for reporting
        exceptions and shutting down the multiprocessor in the face of errors.
     2. Scheduling commands on the slave processors via an interprocess communication fabric (MPI,
        PVM, threads etc) and processing returned text and result commands.


Using the processor framework
=============================

Users of the processor framework will typically use the following methodology:

     1. At application startup determine the name of the required processor implementation and the number of slave processors requested.

     2. Create an Application_callback object.  For example:
            relax_instance = Relax()
            callbacks = Application_callback(master=relax_instance)

     3. Dynamically load a processor implementation using the name of the processor and the number of required slave processors.  For example:
            processor = Processor.load_multiprocessor(relax_instance.multiprocessor_type, callbacks, processor_size=relax_instance.n_processors)

     4. Call run on the processor instance returned above and handle all Exceptions.  For example:
            processor.run()

     5. After calling run, the processor will call back to Application_callback.init_master from which you should call you main program (Application_callback defaults to self.master.run()).

     6. Once in the main program you should call processor.add_to_queue with a series of multi.Slave_command objects you wish to be run across the slave processor pool and then call processor.run_queue to actually execute the commands remotely while blocking.
        >>>
        example here...

     7. Processor.Slave_commands will then run remotely on the slaves and any thrown exceptions and processor.result_commands queued to processor.return_object will be returned to the master processor and handled or executed. The slave processors also provide facilities for capturing the STDERR and STDOUT streams and returning their contents as strings for display on the master's STDOUT and STDERR streams (***more**?).


Extending the processor framework with a new interprocess communication fabric
==============================================================================

The processor class acts as a base class that defines all the commands that a processor implementing
a new inter processor communication fabric needs. All that is required is to implement a subclass of
processor providing the required methods (of course as python provides dynamic typing and
polymorphism 'duck typing' you can always implement a class with the same set of method and it will
also work). Currently processor classes are loaded from the processor module and are modules with
names of the form:

>>> multi.<type>_processor.<Type>_processor

where <Type> is the name of the processor with the correct capitalisation e.g.

>>> processor_name = 'mpi4py'
>>> callback = My_application-callback()
>>> proccesor_size = 6
>>> processor.load_multiprocessor(processor_name, callback, processor_size)

will load multi.mpi4py_processor.Mpi4py_Processor.


TODO
====

The following are yet to be implemented:

    1. There is no ability of the processor to request command line arguments.

    2. The processor can't currently be loaded from somewhere other than the multi directory.

'''

#FIXME: better requirement of inherited commands.
#TODO: check exceptions on master.

# Python module imports.
import time, datetime, math, sys, os
import traceback, textwrap

# relax module imports.
from multi.prependStringIO import PrependStringIO, PrependOut
from relax_errors import RelaxError


def import_module(module_path, verbose=False):
    '''Import the python module named by module_path.

    @param module_path: A module path in python dot separated format.  Note: this currently doesn't
                        support relative module paths as defined by pep328 and python 2.5.
    @type module_path:  str
    @keyword verbose:   Whether to report successes and failures for debugging.
    @type verbose:      bool
    @return:            The module path as a list of module instances or None if the module path
                        cannot be found in the python path.
    @rtype:             list of class module instances or None
    '''

    result = None

    #try:
    module = __import__(module_path, globals(), locals(), [])
    if verbose:
        print('loaded module %s' % module_path)
    #except Exception, e:
    #    if verbose:
    #        print 'failed to load module_path %s' % module_path
    #        print 'exception:', e

    #FIXME: needs more failure checking
    if module != None:
        result = [module]
        components = module_path.split('.')
        for component in components[1:]:
            module = getattr(module, component)
            result.append(module)
    return result


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
        raise RelaxError("The processor type '%s' is not supported." % processor_name)

    # The Processor details.
    processor_name = processor_name + '_processor'
    class_name = processor_name[0].upper() + processor_name[1:]
    module_path = '.'.join(('multi', processor_name))

    # Load the module containing the specific processor.
    modules = import_module(module_path)

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


# FIXME useful debugging code but where to put it
def print_file_lineno(range=xrange(1, 2)):
    for level in range:
        print('<< ', level)
        try:
            file_name = sys._getframe(level).f_code.co_filename
            function_name = sys._getframe(level).f_code.co_name
            line_number = sys._getframe(level).f_lineno
            msg = ': %s - %s - %d>>' % (file_name, function_name, line_number)
            print(msg)
        except Exception, e:
            print(e)
            break


#FIXME: useful for debugging but where to put it
def print_message(processor, message):
    f = open('error' + repr(processor.rank()) + '.txt', 'a')
    f.write(message + '\n')
    f.flush()
    f.close()


#requires 2.4 decorators@abstract
#def abstract(f):
#    raise_unimplemented(f)

#    return f


def raise_unimplemented(method):
    '''Standard function for raising NotImplementedError for unimplemented abstract methods.

    @todo:  For python versions >= 2.4 it is possible to use annotations and meta classes to provide
            a very elegant implementation of abstract methods that check on class instantiation that
            the derived class is a complete implementation of the abstract class. Note some people
            think abstract classes shouldn't be used with python, however.  They are proposed for
            python 3k by Guido van Rossum in pep3119 ;-)

    @see:   http://soiland.no/blog/py/abstract
    @see:   http://www.python.org/dev/peps/pep-3119

    @param method:              The method which should be abstract.
    @type method:               class method
    @raise NotImplementedError: A not implemented exception with the method name as a parameter.
    '''

    msg = "Attempt to invoke unimplemented abstract method %s"
    raise NotImplementedError(msg % method.__name__)



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

        #TODO: should use stderr?
        # note we print to __stdout__ as sys.stdout may be a wrapper we applied
        traceback.print_exc(file=sys.__stdout__)
        processor.abort()


    def default_init_master(self, processor):
        '''Start the main loop of the host application.

        @param processor:   The processor instance.
        @type processor:    multi.processor.Processor instance
        '''

        self.master.run()


class Capturing_exception(Exception):
    '''A wrapper exception for an exception captured on a slave processor.

    The wrapper will remember the stack trace on the remote machine and when raised and caught has a
    string that includes the remote stack trace, which will be displayed along with the stack trace
    on the master.
    '''

    def __init__(self, exc_info=None, rank='unknown', name='unknown'):
        '''Initialise the wrapping exception.

        @todo:   Would it be easier to pass a processor here.

        @keyword exc_info:  Exception information as produced by sys.exc_info().
        @type exc_info:     tuple
        @keyword rank:      The rank of the processor on which the exception was raised.  The value
                            is always greater than 1.
        @type rank:         int
        @keyword name:      The name of the processor on which the exception was raised as returned
                            by processor.get_name().
        @type name:         str
        '''

        Exception.__init__(self)
        self.rank = rank
        self.name = name
        if exc_info == None:
            (exception_type, exception_instance, exception_traceback) = sys.exc_info()
        else:
            (exception_type, exception_instance, exception_traceback) = exc_info

        # This is not an exception!
        if not exception_type:
            return

        #PY3K: this check can be removed once string based exceptions are no longer used
        if isinstance(exception_type, str):
                self.exception_name = exception_type + ' (legacy string exception)'
                self.exception_string = exception_type
        else:
            self.exception_name = exception_type.__name__
            self.exception_string = exception_instance.__str__()

        self.traceback = traceback.format_tb(exception_traceback)


    def __str__(self):
        '''Get the string describing this exception.

        @return:    The string describing this exception.
        @rtype:     str
        '''
        message = '''

                     %s

                     %s

                     Nested Exception from sub processor
                     Rank: %s Name: %s
                     Exception type: %s
                     Message: %s

                     %s


                  '''
        message = textwrap.dedent(message)
        result =  message % ('-'*120, ''.join(self.traceback), self.rank, self.name, self.exception_name, self.exception_string, '-'*120)
        return result


class Memo(object):
    '''A memo of objects and data.

    This is for a slave_command to provide to its results-commands upon return to the master
    processor - designed for overriding by users.
    '''

    def memo_id(self):
        '''Get the unique id for the memo.

        Currently this is the objects unique python id (note these ids can be recycled once the memo
        has been garbage collected it cannot be used as a unique longterm hash).

        @return:    A unique id for this memo.
        @rtype:     int
        '''
        return id(self)


class Processor(object):
    '''The central class of the multi processor framework.

    This provides facilities for process management, command queueing, command scheduling, remote
    execution of commands, and handling of results and error from commands. The class is abstract
    and should be overridden to implement new interprocess communication methods, however, even then
    users are encouraged to override the more full implemented multi.multi_processor.Multi_processor
    class. Most users should instantiate instances of this class by calling the static method
    Processor.load_multiprocessor.

    The class is designed to be subclassed and has abstract methods that a subclass needs to
    override. Methods which can be overridden are clearly marked with a note annotation stating that
    they can be overridden.

    @todo:  It maybe a good idea to separate out the features of the class that purely deal with the
            interprocess communication fabric.
    @todo:  The processor can't currently harvest the required command line arguments from the
            current command line.
    '''

    # Register load multi_processor as a static function of the class.
    # FIXME: cleanup move function into class
    load_multiprocessor = staticmethod(load_multiprocessor)


    def __init__(self, processor_size, callback, stdio_capture=None):
        '''Initialise the processor.

        @param processor_size:  The requested number of __slave__processors, if the number of
                                processors is set by the environment (e.g. in the case of MPI via
                                mpiexec -np <n-processors> on the command line the processor is free
                                free to ignore this value.  The default value from the command line
                                is -1, and subclasses on receiving this value either raise and
                                exception or determine the correct number of slaves to create (e.g.
                                on a multi-cored machine using a threaded implementation the correct
                                number of slaves would be equal to the number of cores available).
        @type processor_size:   int
        @param callback:        The application callback which allows the host application to start
                                its main loop and handle exceptions from the processor.
        @type callback:         multi.processor.Application_callback instance
        @keyword stdio_capture: An array of streams used for writing to STDOUT and STDERR while
                                using the processor. STDOUT and STDERR should be in slots 0 and 1 of
                                the array. This facility is provided for subclasses to use so that
                                they can install there on file like classes for manipulation STDOUT
                                and STDERR including decorating them merging them and storing them.
                                Subclasses should replace sys.stdout and sys.stderr as needed but
                                not touch sys.__stdout__ and sys.__stderr__.  If a value of None is
                                provided a default implementation that decorates STDERR and STDOUT
                                if more than one slave processor is available is used otherwise
                                STDOUT and STDERR are used.
        @type stdio_capture:    list of 2 file-like objects
        '''

        self.callback = callback
        '''Callback to interface to the host application

        @see Application_callback.'''

        self.grainyness = 1
        '''The number of sub jobs to queue for each processor if we have more jobs than processors.'''

#        # CHECKME: am I implemented?, should I be an application callback function
#        self.pre_queue_command = None
#        ''' command to call before the queue is run'''
#        # CHECKME: am I implemented?, should I be an application callback function
#        self.post_queue_command = None
#        ''' command to call after the queue has completed running'''
#
        #CHECKME: should I be a singleton
        self.NULL_RESULT = Null_result_command(processor=self)
        '''Empty result command used by commands which do not return a result (a singleton?).'''


        self._processor_size = processor_size
        '''Number of slave processors available in this processor.'''

        # Default STDOUT and STDERR for restoring later on.
        self.orig_stdout = sys.__stdout__
        self.orig_stderr = sys.__stderr__

        # CHECKME: integration with with stdo capture on slaves
        # setup captured std output and error streams used for capturing and modifying proccessor
        # output on masters and slaves
        # processor id the replacement stdio file like objects are stored in the modulevariable
        # global_stdio_capture
        self.setup_stdio_capture(stdio_capture)


    def abort(self):
        '''Shutdown the multi processor in exceptional conditions - designed for overriding.

        This method is called after an exception from the master or slave has been raised and
        processed and is responsible for the shutdown of the multi processor fabric and terminating
        the application. The functions should be called as the last thing that
        Application_callback.handle_exception does.

        As an example of the methods use see Mpi4py_processor.abort which calls
        MPI.COMM_WORLD.Abort() to cleanly shutdown the mpi framework and remove dangling processes.

        The default action is to call sys.exit()

        @see:   multi.processor.Application_callback.
        @see:   multi.mpi4py_processor.Mpi4py_processor.abort().
        @see:   mpi4py.MPI.COMM_WORLD.Abort().
        '''

        sys.exit()


    def add_to_queue(self, command, memo=None):
        '''Add a command for remote execution to the queue - an abstract method.

        @see: multi.processor.Slave_command
        @see: multi.processor.Result_command
        @see: multi.processor.Memo

        @param command: A command to execute on a slave processor.
        @type command:  ? subclass instance
        @keyword memo:  A place to place data needed on command completion (e.g. where to save the
                        results) the data stored in the memo is provided to Result_commands
                        generated by the command submitted.
        @type memo:     Memo subclass instance
        '''

        raise_unimplemented(self.add_to_queue)


    def capture_stdio(self, stdio_capture=None):
        '''Enable capture of the STDOUT and STDERR by self.stdio_capture or user supplied streams.

        @note:  On slave processors the replacement STDOUT and STDERR streams should be file like
                objects which implement the methods truncate and getvalue (see PrependStringIO).
        @note:  Both or neither stream has to be replaced you can't just replace one!

        @keyword stdio_capture: A pair of file like objects used to replace sys.stdout and
                                sys.stderr respectively.
        @type stdio_capture:    list of two file-like objects
        '''

        # Store the original STDOUT and STDERR for restoring later on.
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr

        # Default to self.stdio_capture if stdio_capture is not supplied.
        if stdio_capture == None:
            stdio_capture = self.stdio_capture

        # First flush.
        sys.stdout.flush()
        sys.stderr.flush()

        # Then redirect IO.
        sys.stdout = stdio_capture[0]
        sys.stderr = stdio_capture[1]


    # FIXME is this used?
#    def exit(self):
#        raise_unimplemented(self.exit)


    def get_intro_string(self):
        '''Get a string describing the multi processor - designed for overriding.

        The string should be suitable for display at application startup and should be less than 100
        characters wide. A good example is the string returned by mpi4py_processor:

        >>> MPI running via mpi4py with <n> slave processors & 1 master, mpi version = <x>.<y>

        @see:       multi.processor.mpi4py_processor.Mpi4py_processor.get_intro_string.

        @return:    A string describing the multi processor.
        @rtype:     str
        '''

        raise_unimplemented(self.get_intro_string)


    def get_name(self):
        '''Get the name of the current processor - an abstract method.

        The string should identify the current master or slave processor uniquely but is purely for
        information and debugging. For example the mpi implementation uses the string
        <host-name>-<process-id> whereas the thread implementation uses the id of the current thread
        as provided by python.

        @return:    The processor identifier.
        @rtype:     str
        '''

        raise_unimplemented(self.get_name)


    def get_stdio_capture(self):
        '''Get the file like objects currently replacing sys.stdout and sys.stderr.

        @return:    The file like objects currently replacing sys.stdout and sys.stderr.
        @rtype:     tuple of two file-like objects
        '''

        return self.stdio_capture


    def get_stdio_pre_strings(self):
        '''Get the strings used prepend STDOUT and STDERR dependant on the current rank.

        For processors with only one slave the result should be ('', '') - designed for overriding.

        @note:  The defaults are ('M S|', 'M E|') and ('NN S|' , 'NN E|') for masters and slaves
                respectively with NN replaced by the rank of the processor.

        @return:    A list of two strings for prepending to each line of STDOUT and STDERR.
        @rtype:     list of 2 str
        '''

        # Initialise.
        pre_string = ''
        stdout_string = ''
        stderr_string = ''
        rank = self.rank()

        # Start of the slave string.
        if self.processor_size() > 1 and rank > 0:
            pre_string = self.rank_format_string() % rank

        # Start of the master string.
        elif self.processor_size() > 1 and rank == 0:
            pre_string = 'M'*self.rank_format_string_width()

        # For multi-processors, the STDOUT and STDERR indicators, and the separator.
        if self.processor_size() > 1:
            stderr_string = pre_string + ' E| '
            stdout_string = pre_string + '  | '

        # Return the strings to prepend to the STDOUT and STDERR streams.
        return stdout_string, stderr_string


    def get_time_delta(self, start_time, end_time):
        '''Utility function called to format the difference between application start and end times.

        @todo:  Check my format is correct.

        @param start_time:  The time the application started in seconds since the epoch.
        @type start_time:   float
        @param end_time:    The time the application ended in seconds since the epoch.
        @type end_time:     float
        @return:            The time difference in the format 'hours:minutes:seconds'.
        @rtype:             str
        '''

        time_diff = end_time - start_time
        time_delta = datetime.timedelta(seconds=time_diff)
        time_delta_str = time_delta.__str__()
        (time_delta_str, millis) = time_delta_str.split('.', 1)
        return time_delta_str


    def post_run(self):
        '''Method called after the application main loop has finished - designed for overriding.

        The default implementation outputs the application runtime to STDOUT. All subclasses should
        call the base method as their last action via super().  Only called on the master on normal
        exit from the applications run loop.
        '''

        if self.rank() == 0:
            end_time = time.time()
            time_delta_str = self.get_time_delta(self.start_time, end_time)
            print('\nOverall runtime: ' + time_delta_str + '\n')


    def pre_run(self):
        '''Method called before starting the application main loop - designed for overriding.

        The default implementation just saves the start time for application timing. All subclasses
        should call the base method via super(). Only called on the master.
        '''

        if self.rank() == 0:
            self.start_time = time.time()


    def processor_size(self):
        '''Get the number of slave processors - designed for overriding.

        @return:    The number of slave processors.
        @rtype:     int
        '''

        return self._processor_size


    def rank(self):
        '''Get the rank of this processor - an abstract method.

        The rank of the processor should be a number between 0 and n where n is the number of slave
        processors, the rank of 0 is reserved for the master processor.

        @return:    The rank of the processor.
        @rtype:     int
        '''

        raise_unimplemented(self.rank)


    def rank_format_string(self):
        '''Get a formatted string with the rank of a slave.

        Only called on slaves.

        @return:    The string designating the rank of the slave.
        @rtype:     str
        '''

        digits = self.rank_format_string_width()
        format = '%%%di' % digits
        return format


    def rank_format_string_width(self):
        '''Get the width of the string designating the rank of a slave process.

        Typically this will be the number of digits in the slaves rank.

        @return:    The number of digits in the biggest slave processor's rank.
        @rtype:     int
        '''

        return int(math.ceil(math.log10(self.processor_size())))


    def restore_stdio(self):
        '''Restore sys.stdout and sys.stderr to the system defaults.

        @note:  sys.stdout and sys.stderr are replaced with sys.__stdout__ ans sys.__stderr__.
        '''

        # First flush.
        sys.stdout.flush()
        sys.stderr.flush()

        # Then restore the IO streams.
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr


    def return_object(self, result):
        '''Return a result to the master processor from a slave - an abstract method.

        @param result:  A result to be returned to the master processor.
        @type result:   Result_string, Result_command or Exception instance

        @see:   multi.processor.Result_string.
        @see:   multi.processor.Resulf_command.
        '''

        raise_unimplemented(self.return_object)


    def run(self):
        '''Run the processor - an abstract method.

        This function runs the processor main loop and is called after all processor setup has been
        completed. It does remote execution setup and teardown round either side of a call to
        Application_callback.init_master.

        @see:   multi.processor.Application_callback.
        '''

        raise_unimplemented(self.run)


    def run_command_globally(self, command):
        '''Run the same command on all slave processors.

        @see:   multi.processor.processor.Slave_command.

        @param command: A slave command.
        @type command:  Slave_command instance
        '''

        queue = [command for i in range(self.processor_size())]
        self.run_command_queue(queue)


    def run_queue(self):
        '''Run the processor queue - an abstract method.

        All commands queued with add_to_queue will be executed, this function causes the current
        thread to block until the command has completed.
        '''

        raise_unimplemented(self.run_queue)


    # fixme: is an argument of the form stio_capture needed
    def setup_stdio_capture(self, stdio_capture=None):
        '''Default fn to setup capturing and manipulating of stdio on slaves and master processors.

        This is designed for overriding.

        @note:  These function will replace sys.stdout and sys.stderr with custom functions
                restore_stdio should be called to return the system to a pristine state the original
                STDOUT and STDERR are always available in sys.__stdout__ and sys.__stderr__.
        @note:  The sys.stdout and sys.stderr streams are not replaced by this function but by
                calling capture_stdio all it does is save replacements to self.stdio_capture.
        @see:   multi.prependStringIO.
        @see:   multi.processor.restore_stdio.
        @see:   multi.processor.capture_stdio.
        @see:   sys.
        @todo:  Remove useless stdio_capture parameter.
        '''

        rank = self.rank()
        pre_strings = ('', '')

        if stdio_capture == None:
            pre_strings = self.get_stdio_pre_strings()
            stdio_capture = self.std_stdio_capture(pre_strings=pre_strings)

        self.stdio_capture = stdio_capture


    #TODO check if pre_strings are used anyhere if not delete
    def std_stdio_capture(self, pre_strings=('', '')):
        '''Get the default sys.stdout and sys.stderr replacements.

        On the master the replacement prepend output with 'MM S]' or MM E]' for the STDOUT and
        STDERR channels respectively on slaves the outputs are replaced by StringIO objects that
        prepend 'NN S]' or NN E]' for STDOUT and STDERR where NN is the rank of the processor. On
        the slave processors the saved strings are retrieved for return to the master processor by
        calling getvalue() on sys.stdout and sys.stderr.

        @note:  By default STDOUT and STDERR are conjoined as otherwise the context of STDOUT and
                STDERR messages are lost.
        @todo:  Improve segregation of sys.sdout and sys.stderr.

        @keyword pre_strings:   Pre strings for the sys.stdout and sys.stderr channels.
        @type pre_strings:      list of 2 str
        @return:                File like objects to replace STDOUT and STDERR respectively in
                                order.
        @rtype:                 tuple of two file-like objects
        '''

        stdout_capture = None
        stderr_capture = None

        if self.rank() == 0:
            stdout_capture = PrependOut(pre_strings[0], sys.stdout)
            #FIXME: seems to be that writing to stderr results leads to incorrect serialisation of output
            stderr_capture = PrependOut(pre_strings[1], sys.stderr)
        else:
            stdout_capture = PrependStringIO(pre_strings[0])
            stderr_capture = PrependStringIO(pre_strings[1], target_stream=stdout_capture)

        return (stdout_capture, stderr_capture)


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


# TODO currently uni_processor doesn't have a process_result should this be integrated
class Result(object):
    '''A basic result object returned from a slave processor via return_object.

    This a very basic result and shouldn't be overridden unless you are also modifying the
    process_result method in all the processors in the framework (i.e. currently for implementors
    only). Most users should override Result_command.

    This result basically acts as storage for the following fields completed, memo_id,
    processor_rank.

    Results should only be created on slave processors.

    @see:   multi.processor.return_object.
    @see:   multi.processor.process_result.
    @see:   multi.processor.Result_command.
    '''

    def __init__(self, processor, completed):
        '''Initialise a result.

        This object is designed for subclassing and __init__ should be called via the super()
        function.

        @see:   multi.processor.Processor.

        @note:  The requirement for the user to know about completed will hopefully disappear with
                some slight of hand in the Slave_command and it may even disappear completely.

        @param processor:   Processor the processor instance we are running in.
        @type processor:    Processor instance
        @param completed:   A flag used in batching result returns to indicate that the sequence of
                            batched result commands has completed, the flag should be set by
                            slave_commands. The value should be the value passed to a Slave_commands
                            run method if it is the final result being returned otherwise it should
                            be False.
        @type completed:    bool
        '''

        #TODO: assert on slave if processor_size > 1
        #TODO: check if a completed command will add a noticeable overhead (I doubt it will)
        self.completed = completed
        '''A flag used in batching result returns to indicate that the sequence has completed.

        This is an optimisation to prevent the sending an extra batched result queue completion
        result being sent, it may be an over early optimisation.'''
        self.memo_id = None
        '''The memo_id of the Slave_command currently being processed on this processor.

        This value is set by the return_object method to the current Slave_commands memo_id.'''
        self.rank = processor.rank()
        '''The rank of the current processor, used in command scheduling on the master processor.'''


class Result_command(Result):
    '''A general result command - designed to be subclassed by users.

    This is a general result command from a Slave command that will have its run() method called on
    return to the master processor.

    @see:   multi.processor.Slave_command.
    '''

    def __init__(self, processor, completed, memo_id=None):
        #TODO: check this method is documnted by its parent
        super(Result_command, self).__init__(processor=processor, completed=completed)
        self.memo_id = memo_id


    def run(self, processor, memo):
        '''The run method of the result command.

        This method will be called when the result command is processed by the master and should
        carry out any actions the slave command needs carried out on the master (e.g. save or
        register results).

        @see:   multi.processor.Processor.
        @see:   multi.processor.Slave_command.
        @see:   multi.processor.Memo.

        @param processor:   The master processor that queued the original Slave_command.
        @type processor:    Processor instance
        @param memo:        A memo that was registered when the original slave command was placed on
                            the queue. This provides local storage on the master.
        @type memo:         Memo instance or None
        '''

        pass


class Null_result_command(Result_command):
    '''An empty result command.

    This command should be returned from slave_command if no other Result_command is returned. This
    allows the queue processor to register that the slave processor has completed its processing and
    schedule new Slave-commands to it.
    '''

    def __init__(self, processor, completed=True):
        super(Null_result_command, self).__init__(processor=processor, completed=completed)


class Result_exception(Result_command):
    '''Return and raise an exception from the salve processor.'''

    def __init__(self, processor, exception, completed=True):
        '''Initialise the result command with an exception.

        @param exception:   An exception that was raised on the slave processor (note the real
                            exception will be wrapped in a Capturing_exception.
        @type exception:    Exception instance
        '''

        super(Result_exception, self).__init__(processor=processor, completed=completed)
        self.exception = exception


    def run(self, processor, memo):
        '''Raise the exception from the Slave_processor.'''

        raise self.exception


# TODO: make this a result_command
class Result_string(Result):
    '''A simple result from a slave containing a result.

    The processor will print this string via sys.__stdout__.

    @note:  This may become a result_command so as to simplify things in the end.
    '''

    #TODO: correct order of parameters should be string, processor, completed
    def __init__(self, processor, string, completed):
        '''Initialiser.

        @see:   multi.processor.Processor.std_stdio_capture.
        @todo:  Check inherited parameters are documented.

        @param string:  A string to return the master processor for output to STDOUT (note the
                        master may split the string into components for STDOUT and STDERR depending
                        on the prefix string. This class is not really designed for subclassing.
        @type string:   str
        '''

        super(Result_string, self).__init__(processor=processor, completed=completed)
        self.string = string


class Slave_command(object):
    '''A command to executed remotely on the slave processor - designed to be subclassed by users.

    The command should be queued with the command queue using the add_to_queue command of the master
    and B{must} return at least one Result_command even if it is a processor.NULL_RESULT. Results
    are returned from the Slave_command to the master processor using the return_object method of
    the processor passed to the command. Any exceptions raised will be caught wrapped and returned
    to the master processor by the slave processor.

    @note:  Good examples of subclassing a slave command include multi.commands.MF_minimise_command
            and multi.commands.Get_name_command.
    @see:   multi.commands.MF_minimise_command.
    @see:   multi.commands.Get_name_command.
    '''

    def __init__(self):
        self.memo_id = None


    def run(self, processor, completed):
        '''Run the slave command on the slave processor.

        The run command B{must} return at least one Result_command even if it is a
        processor.NULL_RESULT.  Results are returned from the Slave_command to the master processor
        using the return_object method of the processor passed to the command. Any exceptions raised
        will be caught wrapped and returned to the master processor by the slave processor.

        @param processor:   The slave processor the command is running on.  Results from the command
                            are returned via calls to processor.return_object.
        @type processor:    Processor instance
        @param completed:   The flag used in batching result returns to indicate that the sequence
                            of batched result commands has completed. This value should be returned
                            via the last result object retuned by this method or methods it calls.
                            All other Result_commands should be initialised with completed=False.
                            This is an optimisation to prevent the sending an extra batched result
                            queue completion result command being sent, it may be an over early
                            optimisation.
        @type completed:    bool
        '''

        pass


    def set_memo_id(self, memo):
        '''Called by the master processor to remember this Slave_commands memo.

        @param memo:    The memo to remember, memos are remembered by getting the memo_id of the
                        memo.
        '''

        if memo != None:
            self.memo_id = memo.memo_id()
        else:
            self.memo_id = None
