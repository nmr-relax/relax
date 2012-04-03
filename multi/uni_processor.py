###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
"""The uni-processor fabric for running on a single CPU."""


# Python module imports.
import sys, os

# multi module imports.
from multi.misc import Result_string
from multi.processor import Processor
from multi.result_commands import Result_command


class Uni_processor(Processor):
    """The uni-processor class."""

    def __init__(self, processor_size, callback):
        """Initialise the class.

        @param processor_size:  The number of processors.
        @type processor_size:   int
        @param callback:        The callback object.
        @type callback:         ?
        """
        super(Uni_processor, self).__init__(processor_size=1, callback=callback)

        if processor_size > 1:
            print('warning: uniprocessor can only support 1 processor you requested %d' % processor_size)
            print('continuing...\n')

        self.command_queue = []
        self.memo_map = {}


    def add_to_queue(self, command, memo=None):
        self.command_queue.append(command)
        if memo != None:
            command.set_memo_id(memo)
            self.memo_map[memo.memo_id()] = memo


    def assert_on_master(self):
        """Make sure that this is the master processor and not a slave.

        As this is the Uni-processor, the processor is always the master.  Hence this method does nothing.
        """


    def get_intro_string(self):
        """Return the string to append to the end of the relax introduction string.

        @return:    The string describing this Processor fabric.
        @rtype:     str
        """

        # Return the string.
        return "Uni-processor."


    def get_name(self):
        # FIXME may need system dependent changes
        return '%s-%s' % (os.getenv('HOSTNAME'), os.getpid())


    def on_master(self):
        """For the uni-processor fabric, we are always on the master.

        @return:    The flag specifying if we are on the master or slave processors.
        @rtype:     bool
        """

        # Always master.
        return True


    def master_queue_command(self, command, dest):
        """Slave to master processor data transfer - send the result command from the slave.

        This mimics a slave to master data transfer initiated by a slave by holding the result command so that the matching self.master_receive_result(), which is called by the master processor, can return it.  As the master and slave processors are one and the same, the command is just held as a private class variable.


        @param command: The results command to send to the master.
        @type command:  Results_command instance
        @param dest:    The destination processor's rank.
        @type dest:     int
        """

        # Hold the result command so that the matching self.master_receive_result() can return it.
        self._result_command_queue = command


    def master_receive_result(self):
        """Slave to master processor data transfer - receive the result command from the slave.

        This mimics a slave to master data transfer initiated by a slave by holding the result command so that the matching self.master_receive_result(), which is called by the master processor, can return it.  As the master and slave processors are one and the same, the command is just held as a private class variable.


        @return:        The result command sent by the slave.
        @rtype:         Result_command instance
        """

        # Remove the command from the class namespace.
        command = self._result_command_queue
        del self._result_command_queue

        # Return the command
        return command


    def post_run(self):
        """Dummy function for preventing the printing of the run time."""


    def processor_size(self):
        """Return 1 as this is the uni-processor.

        @return:    The number of processors.
        @rtype:     int
        """

        return 1


    def rank(self):
        """The uni-processor is always of rank 0.

        @return:    The processor rank.
        @rtype:     int
        """

        return 0


    def return_object(self, result):

        if isinstance(result, Exception):
            #FIXME: clear command queue
		    #       and finalise mpi (or restart it if we can!
            raise result
        elif isinstance(result, Result_command):
            memo = None
            if result.memo_id != None:
                memo = self.memo_map[result.memo_id]
            result.run(self, memo)
            if result.memo_id != None and result.completed:
                del self.memo_map[result.memo_id]

        elif isinstance(result, Result_string):
            sys.stdout.write(result.string)
        else:
            message = 'Unexpected result type \n%s \nvalue%s' %(result.__class__.__name__, result)
            raise Exception(message)


    def run_queue(self):
        #FIXME: need a finally here to cleanup exceptions states for windows etc

        last_command = len(self.command_queue)-1
        for i, command  in enumerate(self.command_queue):
            completed = (i == last_command)

            command.run(self, completed)

        #self.run_command_queue()
        #TODO: add cheques for empty queues and maps if now warn
        del self.command_queue[:]
        self.memo_map.clear()
