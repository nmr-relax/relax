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

# Module docstring.
"""The processor class is the central class in the multi python multiprocessor framework.

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

"""

#FIXME: better requirement of inherited commands.
#TODO: check exceptions on master.

# Python module imports.
import time, datetime, math, sys

# multi module imports.
from multi.misc import Capturing_exception, raise_unimplemented, Verbosity; verbosity = Verbosity()
from multi.processor_io import Redirect_text
from multi.result_commands import Batched_result_command, Null_result_command, Result_exception


class Data_store:
    """A special Processor specific data storage container."""


class Processor(object):
    """The central class of the multi processor framework.

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
    """


    def __init__(self, processor_size, callback):
        """Initialise the processor.

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
        """

        self.callback = callback
        """Callback to interface to the host application

        @see:  Application_callback."""

        self.grainyness = 1
        """The number of sub jobs to queue for each processor if we have more jobs than processors."""

#        # CHECKME: am I implemented?, should I be an application callback function
#        self.pre_queue_command = None
#        """ command to call before the queue is run"""
#        # CHECKME: am I implemented?, should I be an application callback function
#        self.post_queue_command = None
#        """ command to call after the queue has completed running"""
#
        #CHECKME: should I be a singleton
        self.NULL_RESULT = Null_result_command(processor=self)
        """Empty result command used by commands which do not return a result (a singleton?)."""

        # Initialise the processor specific data store.
        self.data_store = Data_store()
        """The processor data store."""


        self._processor_size = processor_size
        """Number of slave processors available in this processor."""


    def abort(self):
        """Shutdown the multi processor in exceptional conditions - designed for overriding.

        This method is called after an exception from the master or slave has been raised and processed and is responsible for the shutdown of the multi processor fabric and terminating the application. The functions should be called as the last thing that Application_callback.handle_exception does.

        As an example of the methods use see Mpi4py_processor.abort which calls MPI.COMM_WORLD.Abort() to cleanly shutdown the mpi framework and remove dangling processes.

        The default action is to call the special self.exit() method.

        @see:   multi.processor.Application_callback.
        @see:   multi.mpi4py_processor.Mpi4py_processor.abort().
        @see:   mpi4py.MPI.COMM_WORLD.Abort().
        """

        self.exit()


    def add_to_queue(self, command, memo=None):
        """Add a command for remote execution to the queue - an abstract method.

        @see: multi.processor.Slave_command
        @see: multi.processor.Result_command
        @see: multi.processor.Memo

        @param command: A command to execute on a slave processor.
        @type command:  ? subclass instance
        @keyword memo:  A place to place data needed on command completion (e.g. where to save the
                        results) the data stored in the memo is provided to Result_commands
                        generated by the command submitted.
        @type memo:     Memo subclass instance
        """

        raise_unimplemented(self.add_to_queue)


    def exit(self, status=0):
        """Exit the processor with the given status.

        This default method allows the program to drop off the end and terminate as it normally would - i.e. this method does nothing.

        @keyword status:    The program exit status.
        @type status:       int
        """


    def data_upload(self, name=None, value=None, rank=None):
        """API function for sending data to be stored on the Processor of the given rank.

        This can be used for transferring data from Processor instance i to the data store of Processor instance j.


        @keyword name:  The name of the data structure to store.
        @type name:     str
        @keyword value: The data structure.
        @type value:    anything
        @keyword rank:  An optional argument to send data only to the Processor of the given rank.  If None, then the data will be sent to all Processor instances.
        @type rank:     None or int
        """

        raise_unimplemented(self.data_upload)


    def get_intro_string(self):
        """Get a string describing the multi processor - designed for overriding.

        The string should be suitable for display at application startup and should be less than 100
        characters wide. A good example is the string returned by mpi4py_processor:

        >>> MPI running via mpi4py with <n> slave processors & 1 master, mpi version = <x>.<y>

        @see:       multi.processor.mpi4py_processor.Mpi4py_processor.get_intro_string.

        @return:    A string describing the multi processor.
        @rtype:     str
        """

        raise_unimplemented(self.get_intro_string)


    def get_name(self):
        """Get the name of the current processor - an abstract method.

        The string should identify the current master or slave processor uniquely but is purely for
        information and debugging. For example the mpi implementation uses the string
        <host-name>-<process-id> whereas the thread implementation uses the id of the current thread
        as provided by python.

        @return:    The processor identifier.
        @rtype:     str
        """

        raise_unimplemented(self.get_name)


    def get_stdio_pre_strings(self):
        """Get the strings used prepend STDOUT and STDERR dependant on the current rank.

        For processors with only one slave the result should be ('', '') - designed for overriding.

        @note:  The defaults are ('M S|', 'M E|') and ('NN S|' , 'NN E|') for masters and slaves
                respectively with NN replaced by the rank of the processor.

        @return:    A list of two strings for prepending to each line of STDOUT and STDERR.
        @rtype:     list of 2 str
        """

        # Only prepend test if the verbosity level is set.
        if not verbosity.level():
            return '', ''

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
        """Utility function called to format the difference between application start and end times.

        @todo:  Check my format is correct.

        @param start_time:  The time the application started in seconds since the epoch.
        @type start_time:   float
        @param end_time:    The time the application ended in seconds since the epoch.
        @type end_time:     float
        @return:            The time difference in the format 'hours:minutes:seconds'.
        @rtype:             str
        """

        time_diff = end_time - start_time
        time_delta = datetime.timedelta(seconds=time_diff)
        time_delta_str = time_delta.__str__()
        (time_delta_str, millis) = time_delta_str.split('.', 1)
        return time_delta_str


    def post_run(self):
        """Method called after the application main loop has finished - designed for overriding.

        The default implementation outputs the application runtime to STDOUT. All subclasses should
        call the base method as their last action via super().  Only called on the master on normal
        exit from the applications run loop.
        """

        if self.rank() == 0:
            end_time = time.time()
            time_delta_str = self.get_time_delta(self.start_time, end_time)

            # Print out of the total run time.
            if verbosity.level():
                print('\nOverall runtime: ' + time_delta_str + '\n')


    def pre_run(self):
        """Method called before starting the application main loop - designed for overriding.

        The default implementation just saves the start time for application timing. All subclasses
        should call the base method via super(). Only called on the master.
        """

        if self.rank() == 0:
            self.start_time = time.time()


    def processor_size(self):
        """Get the number of slave processors - designed for overriding.

        @return:    The number of slave processors.
        @rtype:     int
        """

        return self._processor_size


    def rank(self):
        """Get the rank of this processor - an abstract method.

        The rank of the processor should be a number between 0 and n where n is the number of slave
        processors, the rank of 0 is reserved for the master processor.

        @return:    The rank of the processor.
        @rtype:     int
        """

        raise_unimplemented(self.rank)


    def rank_format_string(self):
        """Get a formatted string with the rank of a slave.

        Only called on slaves.

        @return:    The string designating the rank of the slave.
        @rtype:     str
        """

        digits = self.rank_format_string_width()
        format = '%%%di' % digits
        return format


    def rank_format_string_width(self):
        """Get the width of the string designating the rank of a slave process.

        Typically this will be the number of digits in the slaves rank.

        @return:    The number of digits in the biggest slave processor's rank.
        @rtype:     int
        """

        return int(math.ceil(math.log10(self.processor_size())))


    def return_object(self, result):
        """Return a result to the master processor from a slave - an abstract method.

        @param result:  A result to be returned to the master processor.
        @type result:   Result_string, Result_command or Exception instance

        @see:   multi.processor.Result_string.
        @see:   multi.processor.Resulf_command.
        """

        raise_unimplemented(self.return_object)


    def run(self):
        """Run the processor - an abstract method.

        This function runs the processor main loop and is called after all processor setup has been completed.  It does remote execution setup and teardown (via self.pre_run() and self.post_run()) round either side of a call to Application_callback.init_master.

        @see:   multi.processor.Application_callback.
        """

        # Execute any setup code needed for the specific processor fabrics.
        self.pre_run()

        # Execution of the master processor.
        if self.on_master():
            # Execute the program's run() method, as specified by the Application_callback.
            try:
                self.callback.init_master(self)

            # Allow sys.exit() calls.
            except SystemExit:
                # Allow the processor fabric to clean up.
                self.exit()

                # Continue with the sys.exit().
                raise

            # Handle all errors nicely.
            except Exception, e:
                self.callback.handle_exception(self, e)

        # Execution of the slave processor.
        else:
            # Loop until the slave is asked to die via an Exit_command setting the do_quit flag.
            while not self.do_quit:
                # Execute the slave by catching commands, catching all exceptions.
                try:
                    # Fetch any commands on the queue.
                    commands = self.slave_receive_commands()

                    # Convert to a list, if needed.
                    if not isinstance(commands, list):
                        commands = [commands]

                    # Initialise the results list.
                    if self.batched_returns:
                        self.result_list = []
                    else:
                        self.result_list = None

                    # Execute each command, one by one.
                    for i, command in enumerate(commands):
                        # Capture the standard IO streams for the slaves.
                        self.stdio_capture()

                        # Set the completed flag if this is the last command.
                        completed = (i == len(commands)-1)

                        # Execute the calculation.
                        command.run(self, completed)

                        # Restore the IO.
                        self.stdio_restore()

                    # Process the batched results.
                    if self.batched_returns:
                        self.return_object(Batched_result_command(processor=self, result_commands=self.result_list, io_data=self.io_data))
                        self.result_list = None

                # Capture and process all slave exceptions.
                except:
                    capturing_exception = Capturing_exception(rank=self.rank(), name=self.get_name())
                    exception_result = Result_exception(exception=capturing_exception, processor=self, completed=True)

                    self.return_object(exception_result)
                    self.result_list = None

        # Execute any tear down code needed for the specific processor fabrics.
        self.post_run()

        # End of execution, so perform any exiting actions needed by the specific processor fabrics.
        if self.on_master():
            self.exit()


    def run_command_globally(self, command):
        """Run the same command on all slave processors.

        @see:   multi.processor.processor.Slave_command.

        @param command: A slave command.
        @type command:  Slave_command instance
        """

        queue = [command for i in range(self.processor_size())]
        self.run_command_queue(queue)


    def run_queue(self):
        """Run the processor queue - an abstract method.

        All commands queued with add_to_queue will be executed, this function causes the current
        thread to block until the command has completed.
        """

        raise_unimplemented(self.run_queue)


    def stdio_capture(self):
        """Enable capture of the STDOUT and STDERR.
        
        This is currently used to capture the IO streams of the slaves to return back to the master.
        """

        # Store the original STDOUT and STDERR for restoring later on.
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr

        # The data object.
        self.io_data = []

        # Get the strings to prepend to the IO streams.
        pre_strings = self.get_stdio_pre_strings()

        # Then redirect IO.
        sys.stdout = Redirect_text(self.io_data, token=pre_strings[0], stream=0)
        sys.stderr = Redirect_text(self.io_data, token=pre_strings[1], stream=1)


    def stdio_restore(self):
        """Restore the original STDOUT and STDERR streams."""

        # Restore the original streams.
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr
