#!/usr/bin/env python

import sys
import os


# load mpi
try:
    from  mpi4py import MPI
except ImportError:
    sys.stderr.write("The dependency 'mpi4py' has not been installed.\n")
    sys.exit()

# save original sys.exit to call after wrapper
if MPI.rank == 0:
    _sys_exit =  sys.exit

# wrapper sys.exit function
def exit(status=None):

    exit_mpi()
    _sys_exit(status)

def exit_mpi():
    if MPI.Is_initialized() and not MPI.Is_finalized() and MPI.rank == 0:
        sendbuf = Exit_command()
        for i in range(MPI.size):
            if i != 0:
                MPI.COMM_WORLD.Send(buf=sendbuf,dest=i)

#FIXME do some inheritance
class Exit_command(object):
    def run(self,relax,processor):
        processor.do_quit=True

class Get_name_command(object):
    def run(self,relax,processor):
        result = '%s-%s' % (MPI.Get_processor_name(),os.getpid())
        processor.return_object(result)

#FIXME do some inheritance
class Mpi4py_processor:



    def __init__(self,relax_instance):
        self.relax_instance= relax_instance

        # wrap sys.exit to close down mpi before exiting
        sys.exit= exit
        self.do_quit=False

    def exit(self):
        exit_mpi()

    def return_object(self,result):
        MPI.COMM_WORLD.Send(buf=result, dest=0)

    def run_command(self,command):
        for i in range(1,MPI.size):
            if i != 0:
                MPI.COMM_WORLD.Send(buf=command,dest=i)
        for i in range(1,MPI.size):
            buf=[]
            if i !=0:
                elem = MPI.COMM_WORLD.Recv(source=i)
                if type(elem) == 'object':
                    elem.run(relax_instance, relax_instance.processor)
                else:
                    #FIXME can't cope with multiple lines
                    print i,elem


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

        if MPI.rank == 0:
            self.relax_instance.multi_mode='multi_master'
        else:
            self.relax_instance.multi_mode='multi_slave'
            self.relax_instance.mode='slave'
            self.relax_instance.script_file=None
            self.relax_instance.dummy_mode=True
            self.relax_instance.run()


        if MPI.rank ==0:
            self.relax_instance.run()
            sys.exit()
        else:
            #self.relax_instance.run(deamon=True)
            while not self.do_quit:
                command = MPI.COMM_WORLD.Recv(source=0)
                command.run(self.relax_instance, self.relax_instance.processor)


            #if data=='close':
            #    exit_mpi()
            #    return




if __name__ == '__main__':
    test = Mpi4py_processor(None)
    print test
    print MPI.rank