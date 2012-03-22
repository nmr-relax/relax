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
"""Module containing a Processor base class to be used by any multi-processor fabric.

This is used by the mpi4py clustering code.  It can also be used by any new implementation
including, for example:

    - Other implementations using different python MPI libraries (pypar, etc.).
    - Use of ssh tunnels for parallel programming.
    - Use of the twisted frame work for communication (http://twistedmatrix.com/projects/).
    - The parallel virtual machine (pvm) via pypvm (http://pypvm.sourceforge.net).
"""

# Python module imports.
import Queue
from copy import copy
import math
import sys
import threading
import traceback

# multi module imports.
from multi.commands import Batched_result_command, Result_command, Result_exception
from multi.misc import raise_unimplemented, Result, Result_string, Verbosity; verbosity = Verbosity()
from multi.processor import Processor


class Exit_queue_result_command(Result_command):
    def __init__(self, completed=True):
        pass

RESULT_QUEUE_EXIT_COMMAND = Exit_queue_result_command()



class Multi_processor(Processor):
    """The multi-processor base class."""

    def __init__(self, processor_size, callback):
        super(Multi_processor, self).__init__(processor_size=processor_size, callback=callback)

        self.do_quit = False

        #FIXME un clone from uniprocessor
        #command queue and memo queue
        self.command_queue = []
        self.memo_map = {}

        self.batched_returns = True
        self.result_list = None

        self.threaded_result_processing = True


    #TODO: move up a level
    def add_to_queue(self, command, memo=None):
        self.command_queue.append(command)
        if memo != None:
            command.set_memo_id(memo)
            self.memo_map[memo.memo_id()] = memo


    #TODO: move up a level
    def assert_on_master(self):
        if self.on_slave():
            msg = 'running on slave when expected master with MPI.rank == 0, rank was %d'% self.rank()
            raise Exception(msg)


    #TODO: move up a level
    def chunk_queue(self, queue):
        lqueue = copy(queue)
        result = []
        processors = self.processor_size()
        chunks = processors * self.grainyness
        chunk_size = int(math.floor(float(len(queue)) / float(chunks)))

        if chunk_size < 1:
            result = queue
        else:
            for i in range(chunks):
                result.append(lqueue[:chunk_size])
                del lqueue[:chunk_size]
            for i, elem in enumerate(lqueue):
                result[i].append(elem)
        return result


    def master_queue_command(self, command, dest):
        raise_unimplemented(self.master_queue_command)


    def master_receive_result(self):
        raise_unimplemented(self.master_receive_result)


    # FIXME move to lower level
    def on_master(self):
        if self.rank() == 0:
            return True


    # FIXME move to lower level
    def on_slave(self):
        return not self.on_master()


    def post_run(self):

        super(Multi_processor, self).post_run()


    def pre_run(self):
        """Method called before starting the application main loop"""

        # Execute the base class method.
        super(Multi_processor, self).pre_run()


    #FIXME: fill out generic result processing move to processor
    def process_result(self, result):
        if isinstance(result, Result):
            if isinstance(result, Result_command):
                memo = None
                if result.memo_id != None:
                    memo = self.memo_map[result.memo_id]
                result.run(self, memo)
                if result.memo_id != None and result.completed:
                    del self.memo_map[result.memo_id]

            elif isinstance(result, Result_string):
                #FIXME can't cope with multiple lines
                sys.stdout.write(result.string)
        else:
            message = 'Unexpected result type \n%s \nvalue%s' %(result.__class__.__name__, result)
            raise Exception(message)


    #TODO: move up a level add send and revieve virtual functions
    def return_object(self, result):
        result_object = None
        #raise Exception('dummy')
        if isinstance(result, Result_exception):
            result_object = result
        elif self.batched_returns:
            is_batch_result = isinstance(result, Batched_result_command)

            if is_batch_result:
                result_object = result
            else:
                if self.result_list != None:
                    self.result_list.append(result)
        else:
            result_object = result

        if result_object != None:
            #FIXME check is used?
            result_object.rank = self.rank()
            self.return_result_command(result_object=result_object)


    def return_result_command(self, result_object):
        raise_unimplemented(self.slave_queue_result)


    #TODO: move up a level add virtaul send and revieve functions
    def run_command_queue(self, queue):
        """Process all commands on the queue and wait for completion.

        @param queue:   The command queue.
        @type queue:    list of Command instances
        """

        # This must only be run on the master processor.
        self.assert_on_master()

        running_set = set()
        idle_set = set([i for i in range(1, self.processor_size()+1)])

        if self.threaded_result_processing:
            result_queue = Threaded_result_queue(self)
        else:
            result_queue = Immediate_result_queue(self)

        while len(queue) != 0:

            while len(idle_set) != 0:
                if len(queue) != 0:
                    command = queue.pop()
                    dest = idle_set.pop()
                    self.master_queue_command(command=command, dest=dest)
                    running_set.add(dest)
                else:
                    break

            # Loop until the queue of calculations is depleted.
            while len(running_set) != 0:
                # Get the result.
                result = self.master_receive_result()

                # Debugging print out.
                if verbosity.level():
                    print('\nIdle set:    %s' % idle_set)
                    print('Running set: %s' % running_set)

                # Shift the processor rank to the idle set.
                if result.completed:
                    idle_set.add(result.rank)
                    running_set.remove(result.rank)

                # Add to the result queue for instant or threaded processing.
                result_queue.put(result)

        # Process the threaded results.
        if self.threaded_result_processing:
            result_queue.run_all()


    #TODO: move up a level
    def run_queue(self):
        #FIXME: need a finally here to cleanup exceptions states
         lqueue = self.chunk_queue(self.command_queue)
         self.run_command_queue(lqueue)

         del self.command_queue[:]
         self.memo_map.clear()


    def slave_receive_commands(self):
        raise_unimplemented(self.slave_receive_commands)



#FIXME: move up a level or more
class Result_queue(object):
    def __init__(self, processor):
        self.processor = processor


    def put(self, job):
        if isinstance(job, Result_exception) :
            self.processor.process_result(job)


    def run_all(self):
        raise_unimplemented(self.run_all)



#FIXME: move up a level or more
class Immediate_result_queue(Result_queue):
    def put(self, job):
        super(Immediate_result_queue, self).put(job)
        try:
            self.processor.process_result(job)
        except:
            traceback.print_exc(file=sys.stdout)
            # FIXME: this doesn't work because this isn't the main thread so sys.exit fails...
            self.processor.abort()


    def run_all(self):
        pass



class Threaded_result_queue(Result_queue):
    def __init__(self, processor):
        super(Threaded_result_queue, self).__init__(processor)
        self.queue = Queue.Queue()
        self.sleep_time = 0.05
        self.processor = processor
        self.running = 1
        # FIXME: syntax error here produces exception but no quit
        self.thread1 = threading.Thread(target=self.workerThread)
        self.thread1.setDaemon(1)
        self.thread1.start()


    def put(self, job):
        super(Threaded_result_queue, self).put(job)
        self.queue.put_nowait(job)


    def run_all(self):
        self.queue.put_nowait(RESULT_QUEUE_EXIT_COMMAND)
        self.thread1.join()


    def workerThread(self):
            try:
                while True:
                    job = self.queue.get()
                    if job == RESULT_QUEUE_EXIT_COMMAND:
                        break
                    self.processor.process_result(job)
            except:
                traceback.print_exc(file=sys.stdout)
                # FIXME: this doesn't work because this isn't the main thread so sys.exit fails...
                self.processor.abort()



class Too_few_slaves_exception(Exception):
    def __init__(self):
        msg = 'master slave processing requires at least 2 processors to run you only provided 1, exiting....'
        Exception.__init__(self, msg)
