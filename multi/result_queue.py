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
"""Module containing the results queue objects."""

# Python module imports.
import Queue
import sys
import threading
import traceback

# multi module imports.
from multi.misc import raise_unimplemented
from multi.result_commands import Result_command, Result_exception


class Exit_queue_result_command(Result_command):
    def __init__(self, completed=True):
        pass

RESULT_QUEUE_EXIT_COMMAND = Exit_queue_result_command()



class Result_queue(object):
    def __init__(self, processor):
        self.processor = processor


    def put(self, job):
        if isinstance(job, Result_exception) :
            self.processor.process_result(job)


    def run_all(self):
        raise_unimplemented(self.run_all)



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
