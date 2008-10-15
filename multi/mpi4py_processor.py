#!/usr/bin/env python

#TODO clone communicators & resize
import sys
import os
import math


# load mpi
try:
    from  mpi4py import MPI
except ImportError:
    sys.stderr.write("The dependency 'mpi4py' has not been installed.\n")
    sys.exit()

# save original sys.exit to call after wrapper
if MPI.rank == 0:
    _sys_exit =  sys.exit


def rank_format_string():
    digits  = math.ceil(math.log10(MPI.size))
    format = '%%%di' % digits
    return format

RANK_FORMAT_STRING = rank_format_string

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


class Result(object):
    def __init__(self):
        self.rank=MPI.rank

class Result_string(Result):
    #FIXME move result up a level
    def __init__(self,string,completed):
        super(Result_string,self).__init__()
        self.string=string
        self.completed=completed

class Result_command(Result):
    def __init__(self,completed):
        super(Result_command,self).__init__()
        self.completed=completed

    def run(self,relax,processor):
        pass

class Null_result_command(Result_command):
    def __init__(self):
        super(Null_result_command,self).__init__(completed=True)

NULL_RESULT=Null_result_command()

class Slave_command(object):
    def run(self,processor):
        pass

#FIXME do some inheritance

class Exit_command(Slave_command):
    def run(self,processor):
        processor.return_object(NULL_RESULT)
        processor.do_quit=True



class Get_name_command(Slave_command):
    def run(self,processor):
        msg = processor.get_name()
        result = Result_string(msg,True)
        processor.return_object(result)

#FIXME do some inheritance
class Mpi4py_processor:



    def __init__(self,relax_instance):
        self.relax_instance= relax_instance

        # wrap sys.exit to close down mpi before exiting
        sys.exit= exit
        self.do_quit=False

    def assert_on_master(self):
        if MPI.rank != 0:
            msg = 'running on slave when expected master with MPI.rank == 0, rank was %d'% MPI.rank
            raise Exception(msg)


    def get_name(self):
        return '%s-%s' % (MPI.Get_processor_name(),os.getpid())

    def exit(self):
        exit_mpi()

    def return_object(self,result):
        MPI.COMM_WORLD.Send(buf=result, dest=0)

    def run_command_queue(self,commands):
        self.assert_on_master()

        for i in range(1,MPI.size):
            MPI.COMM_WORLD.Send(buf=command,dest=i)

    def run_command_globally(self,command):
        queue = [command for i in range(1,MPI.size)]
        self.run_command_queue(queue)

    def run_command_queue(self,queue):
        self.assert_on_master()

#        for i in range(1,MPI.size):
#                MPI.COMM_WORLD.Send(buf=command,dest=i)
#        for i in range(1,MPI.size):
#            elem = MPI.COMM_WORLD.Recv(source=i)
#            if type(elem) == 'object':
#                elem.run(relax_instance, relax_instance.processor)
#            else:
#                #FIXME can't cope with multiple lines
#                print i,elem
        #queue = [command for i in range(1,MPI.size*2)]

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
                    raise result

                if isinstance(result, Result):
                    if result.completed:
                        idle_set.add(result.rank)
                        running_set.remove(result.rank)

                    if isinstance(result, Result_command):
                        result.run(self.relax,self)
                    elif isinstance(result, Result_string):
                        #FIXME can't cope with multiple lines
                        print result.rank,result.string
                    else:
                        message = 'Unexpected result type \n%s \nvalue%s' %(result.__class__.__name__,result)
                        raise Exception(message)


#        for i in range(MPI.size):
#            buf=[]
#            if i !=0:
#                print 'try',i
#                MPI.COMM_WORLD.Recv(buf=buf, source=i)
#                for i,elem in enumerate(buf):
#                    if elem.type!='object':
#                        print i,elem
#                    else:
#                        elem.run()

    def run(self):

#        if MPI.rank == 0:
#            self.relax_instance.multi_mode='multi_master'
#        else:
#            self.relax_instance.multi_mode='multi_slave'
#            self.relax_instance.mode='slave'
#            self.relax_instance.script_file=None
#            self.relax_instance.dummy_mode=True
#            #self.relax_instance.run()


        if MPI.rank ==0:
            self.relax_instance.run()
            sys.exit()
        else:
            #self.relax_instance.run(deamon=True)
            while not self.do_quit:
                command = MPI.COMM_WORLD.Recv(source=0)
                try:
                    command.run(self)
                except Exception,e:
                    self.return_object(e)



            #if data=='close':
            #    exit_mpi()
            #    return




if __name__ == '__main__':
    test = Mpi4py_processor(None)
    print test
    print MPI.rank