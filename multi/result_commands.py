###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
# Copyright (C) 2008-2012 Edward d'Auvergne                                   #
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
"""Module containing command objects sent from the slaves back to the master."""

# Python module imports.
import sys

# multi module imports.
from multi.misc import raise_unimplemented, Result, Result_string


class Result_command(Result):
    """A general result command - designed to be subclassed by users.

    This is a general result command from a Slave command that will have its run() method called on
    return to the master processor.

    @see:   multi.processor.Slave_command.
    """

    def __init__(self, processor, completed, memo_id=None):
        #TODO: check this method is documnted by its parent
        super(Result_command, self).__init__(processor=processor, completed=completed)
        self.memo_id = memo_id


    def run(self, processor, memo):
        """The run method of the result command.

        This method will be called when the result command is processed by the master and should
        carry out any actions the slave command needs carried out on the master (e.g. save or
        register results).

        @see:   multi.processor.Processor.
        @see:   multi.processor.Slave_command.
        @see:   multi.memo.Memo.

        @param processor:   The master processor that queued the original Slave_command.
        @type processor:    Processor instance
        @param memo:        A memo that was registered when the original slave command was placed on
                            the queue. This provides local storage on the master.
        @type memo:         Memo instance or None
        """

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
    """An empty result command.

    This command should be returned from slave_command if no other Result_command is returned. This
    allows the queue processor to register that the slave processor has completed its processing and
    schedule new Slave-commands to it.
    """

    def __init__(self, processor, completed=True):
        super(Null_result_command, self).__init__(processor=processor, completed=completed)



class Result_exception(Result_command):
    """Return and raise an exception from the salve processor."""

    def __init__(self, processor, exception, completed=True):
        """Initialise the result command with an exception.

        @param exception:   An exception that was raised on the slave processor (note the real
                            exception will be wrapped in a Capturing_exception.
        @type exception:    Exception instance
        """

        super(Result_exception, self).__init__(processor=processor, completed=completed)
        self.exception = exception


    def run(self, processor, memo):
        """Raise the exception from the Slave_processor."""

        raise self.exception
