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
"""The non-public module for storing the API functions and classes of the multi-processor package.

This is for internal use only.  To access the multi-processor API, see the __init__ module.
"""

# Python module imports.
import sys
import traceback, textwrap

# relax module imports.
from multi.processor_io import Redirect_text


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



class Batched_result_command(Result_command):
    def __init__(self, processor, result_commands, io_data=None, completed=True):
        super(Batched_result_command, self).__init__(processor=processor, completed=completed)
        self.result_commands = result_commands

        # Store the IO data to print out via the run() method called by the master.
        self.io_data = io_data


    def run(self, processor, batched_memo):
        """The results command to be run by the master.

        @param processor:       The processor instance.
        @type processor:        Processor instance
        @param batched_memo:    The batched memo object.
        @type batched_memo:     Memo instance
        """

        # First check that we are on the master.
        processor.assert_on_master()

        # Unravel the IO stream data on the master in the correct order.
        for line, stream in self.io_data:
            if stream == 0:
                sys.stdout.write(line)
            else:
                sys.stderr.write(line)

        if batched_memo != None:
            msg = "batched result commands shouldn't have memo values, memo: " + repr(batched_memo)

        if batched_memo != None:
            msg = "batched result commands shouldn't have memo values, memo: " + repr(batched_memo)
            raise ValueError(msg)

        for result_command in self.result_commands:
            processor.process_result(result_command)



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

    The processor will print this string via sys.stdout.

    @note:  This may become a result_command so as to simplify things in the end.
    '''

    #TODO: correct order of parameters should be string, processor, completed
    def __init__(self, processor, string, completed):
        '''Initialiser.

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
