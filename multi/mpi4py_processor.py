################################################################################
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

#TODO clone communicators & resize
import sys
import os
import math
import textwrap
import traceback

from multi.processor import Processor,Memo,Slave_command
from multi.processor import Result,Result_command,Result_string
from multi.commands import Exit_command

from copy import copy
from multi.processor import Capturing_exception




# load mpi
try:
    from  mpi4py import MPI
except ImportError:
    msg = '''The dependency 'mpi4py' has not been installed. You should either

                 1. run without multiprocessor support i.e. remove the
                    --multi mpi4py flag  from the command line

                 2. install mpi4py

                 3. choose another multi processor method to give to the
                    --multi command line flag\n'''
    #FIXME dedent not working
    msg=textwrap.dedent(msg)
    sys.stderr.write(msg)
    sys.stderr.write('exiting...\n\n')
    sys.exit()

# save original sys.exit to call after wrapper
if MPI.rank == 0:
    _sys_exit =  sys.exit

#FIXME: delete me
#def rank_format_string():
#    digits  = math.ceil(math.log10(MPI.size))
#    format = '%%%di' % digits
#    return format
#
#RANK_FORMAT_STRING = rank_format_string

# wrapper sys.exit function
def exit(status=None):

    exit_mpi()
    _sys_exit(status)

def broadcast_command(command):
    for i in range(1,MPI.size):
        if i != 0:
            MPI.COMM_WORLD.Send(buf=command,dest=i)

def ditch_all_results():
    for i in range(1,MPI.size):
        if i != 0:
            while 1:
                result = MPI.COMM_WORLD.Recv(source=i)
                if result.completed:
                    break
def exit_mpi():
    if MPI.Is_initialized() and not MPI.Is_finalized() and MPI.rank == 0:
        broadcast_command(Exit_command())
        ditch_all_results()





#FIXME do some inheritance
class Mpi4py_processor(Processor):



    def __init__(self,relax_instance, chunkyness=3):
        super(Mpi4py_processor,self).__init__(relax_instance = relax_instance, chunkyness=chunkyness)


        # wrap sys.exit to close down mpi before exiting
        sys.exit= exit
        self.do_quit=False

        #FIXME un clone from uniprocessor
        #command queue and memo queue
        self.command_queue=[]
        self.memo_map={}


    def add_to_queue(self,command,memo=None):
        self.command_queue.append(command)
        if memo != None:
            command.set_memo_id(memo)
            self.memo_map[memo.memo_id()]=memo

    def rank(self):
        return MPI.rank

    def processor_size(self):
        return MPI.size -1

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

    def run_queue(self):
        #FIXME: need a finally here to cleanup exceptions states
         lqueue =  self.chunk_queue(self.command_queue)
         self.run_command_queue(lqueue)

         del self.command_queue[:]
         self.memo_map.clear()

    def assert_on_master(self):
        if self.on_slave():
            msg = 'running on slave when expected master with MPI.rank == 0, rank was %d'% MPI.rank
            raise Exception(msg)


    def get_name(self):
        return '%s-%s' % (MPI.Get_processor_name(),os.getpid())

    def exit(self):
        exit_mpi()

    def return_object(self,result):
        result.rank=MPI.rank
        MPI.COMM_WORLD.Send(buf=result, dest=0)




    def run_command_queue(self,queue):
        self.assert_on_master()

        running_set=set()
        idle_set=set([i for i in range(1,MPI.size)])

        while len(queue) != 0:

            while len(idle_set) != 0:
                if len(queue) != 0:
                    command = queue.pop()
                    dest=idle_set.pop()
                    MPI.COMM_WORLD.Send(buf=command,dest=dest)
                    running_set.add(dest)
                else:
                    break


            while len(running_set) !=0:
                result = MPI.COMM_WORLD.Recv(source=MPI.ANY_SOURCE)
                if isinstance(result, Exception):
                    #FIXME: clear command queue
                    #       and finalise mpi (or restart it if we can!
                    # also tracebacks are no good
                    raise result

                if isinstance(result, Result):
                    if result.completed:
                        idle_set.add(result.rank)
                        running_set.remove(result.rank)

                    if isinstance(result, Result_command):
                        memo=None
                        if result.memo_id != None:
                            memo=self.memo_map[result.memo_id]
                        result.run(self.relax_instance,self,memo)
                        if result.memo_id != None and result.completed:
                            del self.memo_map[result.memo_id]

                    elif isinstance(result, Result_string):
                        #FIXME can't cope with multiple lines
                        self.save_stdout.write(result.string),
                    else:
                        message = 'Unexpected result type \n%s \nvalue%s' %(result.__class__.__name__,result)
                        raise Exception(message)



    def on_master(self):
        result = False
        if MPI.rank ==0:
            result = True
        return result


    def run(self):



        if self.on_master():
            self.pre_run()
            self.relax_instance.run()
            self.post_run()

            # note this a modified exit that kills all MPI processors
            sys.exit()
        else:

            while not self.do_quit:
                commands = MPI.COMM_WORLD.Recv(source=0)

                if not isinstance(commands,list):
                    commands =  [commands]
                last_command = len(commands)-1
                for i,command  in enumerate(commands):
                    try:
                        completed = i == last_command
                        command.run(self,completed)
                        #raise Exception('dummy')
                    except Exception,e:
                        #self.return_object(e)
                        self.return_object(Capturing_exception(rank=self.rank(),name=self.get_name()))







