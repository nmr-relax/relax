###############################################################################
#                                                                              #
# Copyright (C) 2007  Gary S Thompson (see https://gna.org/users/varioustoxins #
#                                      for contact details)                    #
#                                                                              #
#                                                                              #
# This file is part of the program relax.                                      #
#                                                                              #
# relax is free software; you can redistribute it and/or modify                #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation; either version 2 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# relax is distributed in the hope that it will be useful,                     #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with relax; if not, write to the Free Software                         #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    #
#                                                                              #
################################################################################


import threading
import math
import sys

from copy import  copy
import Queue

from multi.processor import Processor
from multi.processor import Result,Result_command,Result_string,Result_exception
from multi.processor import raise_unimplimented
from multi.processor import Capturing_exception





class Batched_result_command(Result_command):

    def __init__(self,processor,result_commands,completed=True):
        super(Batched_result_command,self).__init__(processor=processor,completed=completed)
        self.result_commands=result_commands


    def run(self,processor,batched_memo):

        processor.assert_on_master()
        if batched_memo != None:
            msg = "batched result commands shouldn't have memo values, memo: " + `batched_memo`
            raise ValueError(msg)

        for result_command in self.result_commands:
            processor.process_result(result_command)


class Exit_queue_result_command(Result_command):
    def __init__(self,completed=True):
        pass

RESULT_QUEUE_EXIT_COMMAND = Exit_queue_result_command()
#FIXME: move  up a level or more
class Result_queue(object):
    def __init__(self,mpi4py_processor):
        self.mpi4py_processor = mpi4py_processor

    def put(self,job):
        if isinstance(job, Result_exception) :
            self.mpi4py_processor.process_result(job)

    def run_all(self):
        raise_unimplimented(self.run_all)

#FIXME: move  up a level or more
class Threaded_result_queue(Result_queue):
    def __init__(self,mpi4py_processor):
        super(Threaded_result_queue,self).__init__(mpi4py_processor)
        self.queue = Queue.Queue()
        self.sleep_time =0.05

        self.running=1
        # FIXME: syntax error here produces exception but no quit
        self.thread1 = threading.Thread(target=self.workerThread)
        self.thread1.setDaemon(1)
        self.thread1.start()

    def workerThread(self):

            while True:
                job=self.queue.get()
                if job == RESULT_QUEUE_EXIT_COMMAND:
                    break
                self.mpi4py_processor.process_result(job)


    def put(self,job):
        super(Threaded_result_queue,self).put(job)
        self.queue.put_nowait(job)

    def run_all(self):
        self.queue.put_nowait(RESULT_QUEUE_EXIT_COMMAND)
        self.thread1.join()

#FIXME: move  up a level or more
class Immediate_result_queue(Result_queue):
    def __init(self,mpi4py_processor):
        super(Threaded_result_queue,self).__init__(mpi4py_processor)

    def put(self,job):
        super(Immediate_result_queue,self).put(job)
        self.mpi4py_processor.process_result(job)

    def run_all(self):
        pass

class Too_few_slaves_exception(Exception):
    def __init__(self):
        msg = 'master slave processing requires at least 2  processors to run you only provided 1, exiting....'
        Exception.__init__(self,msg)



class Multi_processor(Processor):

    def __init__(self,processor_size,callback):
        super(Multi_processor,self).__init__(processor_size=processor_size,callback=callback)

        self.do_quit=False

        #FIXME un clone from uniprocessor
        #command queue and memo queue
        self.command_queue=[]
        self.memo_map={}

        self.batched_returns=True
        self.result_list=None

        self.threaded_result_processing=True

    #TODO: move up a level
    def assert_on_master(self):
        if self.on_slave():
            msg = 'running on slave when expected master with MPI.rank == 0, rank was %d'% self.rank()
            raise Exception(msg)

    #FIXME: fill out generic result processing move to processor
    def process_result(self,result):



        if isinstance(result, Result):

            if isinstance(result, Result_command):
                memo=None
                if result.memo_id != None:
                    memo=self.memo_map[result.memo_id]
                result.run(self,memo)
                if result.memo_id != None and result.completed:
                    del self.memo_map[result.memo_id]

            elif isinstance(result, Result_string):
                #FIXME can't cope with multiple lines
                self.save_stdout.write(result.string),
        else:
            message = 'Unexpected result type \n%s \nvalue%s' %(result.__class__.__name__,result)
            raise Exception(message)

    #TODO: move up a level
    def add_to_queue(self,command,memo=None):
        self.command_queue.append(command)
        if memo != None:
            command.set_memo_id(memo)
            self.memo_map[memo.memo_id()]=memo

    # FIXME move to lower level
    def on_master(self):
        if self.rank() == 0:
            return True

    # FIXME move to lower level
    def on_slave(self):
        return not self.on_master()

        #TODO: move up a level
    def chunk_queue(self,queue):
        lqueue=copy(queue)
        result = []
        processors = self.processor_size()
        chunks = processors * self.chunkyness
        chunk_size = int(math.floor(float(len(queue)) / float(chunks)))

        if chunk_size < 1:
            result = queue
        else:
            for i in range(chunks):
                result.append(lqueue[:chunk_size])
                del lqueue[:chunk_size]
            for i,elem in enumerate(lqueue):
                result[i].append(elem)
        return result

    #TODO: move up a level
    def run_queue(self):
        #FIXME: need a finally here to cleanup exceptions states
         lqueue =  self.chunk_queue(self.command_queue)
         self.run_command_queue(lqueue)

         del self.command_queue[:]
         self.memo_map.clear()

        #TODO: move up a level add send and revieve virtual functions
    def return_object(self,result):
        result_object = None
        #raise Exception('dummy')
        if isinstance(result,  Result_exception):
            result_object=result
        elif self.batched_returns:
            is_batch_result = isinstance(result, Batched_result_command)


            if is_batch_result:
                result_object = result
            else:
                if self.result_list != None:
                    self.result_list.append(result)
        else:
            result_object=result


        if result_object != None:
            #FIXME check is used?
            result_object.rank=self.rank()
            self.return_result_command(result_object=result_object)

    #TODO: move up a level  add virtaul send and revieve functions
    def run_command_queue(self,queue):
            self.assert_on_master()

            running_set=set()
            idle_set=set([i for i in range(1,self.processor_size())])

            if self.threaded_result_processing:
                result_queue=Threaded_result_queue(self)
            else:
                result_queue=Immediate_result_queue(self)

            while len(queue) != 0:

                while len(idle_set) != 0:
                    if len(queue) != 0:
                        command = queue.pop()
                        dest=idle_set.pop()
                        self.master_queue_command(command=command,dest=dest)
                        running_set.add(dest)
                    else:
                        break


                while len(running_set) !=0:
                    result = self.master_recieve_result()
                    #if isinstance(result, Result_exception):
                    #    print 'result', result
                    #    sys.exit()

                    if result.completed:
                        idle_set.add(result.rank)
                        running_set.remove(result.rank)

                    result_queue.put(result)

            if self.threaded_result_processing:
                result_queue.run_all()

    def create_slaves(self,processor_size):
        pass

    #TODO: move up a level and add virtual send and recieve
    def run(self):



        if self.on_master():
            try:
                self.pre_run()
                self.create_slaves(self.processor_size())
                self.callback.init_master(self)
                self.post_run()
            except Exception,e:
                self.callback.handle_exception(self,e)



            # note this a modified exit that kills all MPI processors
            sys.exit()
        else:

            while not self.do_quit:
                try:

                    commands = self.slave_recieve_commands()



                    if not isinstance(commands,list):
                        commands =  [commands]
                    last_command = len(commands)-1

                    if self.batched_returns:
                        self.result_list = []
                    else:
                        self.result_list = None

                    for i,command  in enumerate(commands):

                        #raise Exception('dummy')
                        completed = (i == last_command)
                        command.run(self,completed)



                    if self.batched_returns:
                        self.return_object(Batched_result_command(processor=self,result_commands=self.result_list))
                        self.result_list=None


                except:

                    capturing_exception = Capturing_exception(rank=self.rank(),name=self.get_name())
                    exception_result = Result_exception(exception=capturing_exception,processor=self,completed=True)

                    self.return_object(exception_result)
                    self.result_list=None

