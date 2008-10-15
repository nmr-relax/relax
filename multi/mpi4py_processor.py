#!/usr/bin/env python

import sys



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
        sendbuf  = ['close']
        for i in range(MPI.size):
            if i != 0:
                MPI.COMM_WORLD.Send(buf=sendbuf,dest=i)




class Mpi4py_processor:



    def __init__(self,relax_instance):
        self.relax_instance= relax_instance

        # wrap sys.exit to close down mpi before exiting
        sys.exit= exit
        self.do_quit=False

    def run(self):

        if MPI.rank == 0:
            self.relax_instance.multi_mode='multi_master'
        else:
            self.relax_instance.multi_mode='multi_slave'

        if MPI.rank ==0:
            self.relax_instance.run()
            sys.exit()
        else:
            data = MPI.COMM_WORLD.Recv(source=0)
            if data=='close':
                exit_mpi()
                return




if __name__ == '__main__':
    test = Mpi4py_processor(None)
    print test
    print MPI.rank