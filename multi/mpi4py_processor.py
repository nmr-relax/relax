#!/usr/bin/env python

import sys

try:
    from  mpi4py import MPI
except ImportError:
    sys.stderr.write("The dependency 'mpi4py' has not been installed.\n")
    sys.exit()

class Mpi4py_processor:
    def __init__(self,relax_instance):
        self.relax_instance= relax_instance

    def run(self):

        if MPI.rank == 0:
            self.relax_instance.multi_mode='multi_master'
        else:
            self.relax_instance.multi_mode='multi_slave'

        self.relax_instance.run()



if __name__ == '__main__':
    test = Mpi4py_processor(None)
    print test
    print MPI.rank