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
"""The MPI processor fabric via the mpi4py Python implementation."""


# TODO: clone communicators & resize
# TODO: check exceptions on master

# Python module imports.
try:
    from mpi4py import MPI
except ImportError:
    MPI = None
import os
import sys
import textwrap

# relax module imports.
from multi.commands import Exit_command
from multi.multi_processor_base import Multi_processor, Too_few_slaves_exception



def broadcast_command(command):
    for i in range(1, MPI.COMM_WORLD.size):
        if i != 0:
            MPI.COMM_WORLD.send(obj=command, dest=i)


def ditch_all_results():
    for i in range(1, MPI.COMM_WORLD.size):
        if i != 0:
            while True:
                result = MPI.COMM_WORLD.recv(source=i)
                if result.completed:
                    break


class Mpi4py_processor(Multi_processor):
    """The mpi4py multi-processor class."""

    def __init__(self, processor_size, callback):
        """Initialise the mpi4py processor."""

        mpi_processor_size = MPI.COMM_WORLD.size-1

        if processor_size == -1:
            processor_size = mpi_processor_size

        # FIXME: needs better support in relax generates stack trace
        if mpi_processor_size == 0:
            raise Too_few_slaves_exception()

        msg = 'warning: mpi4py_processor is using 1 masters and %d slave processors you requested %d slaves\n'
        if processor_size != (mpi_processor_size):
            print(msg % (mpi_processor_size, processor_size))

        super(Mpi4py_processor, self).__init__(processor_size=mpi_processor_size, callback=callback)

        # Initialise a flag for determining if we are in the run() method or not.
        self.in_main_loop = False


    def abort(self):
        MPI.COMM_WORLD.Abort()


    def data_upload(self, name=None, value=None, rank=None):
        """API function for sending data to be stored on the Processor of the given rank.

        This can be used for transferring data from Processor instance i to the data store of Processor instance j.


        @keyword name:  The name of the data structure to store.
        @type name:     str
        @keyword value: The data structure.
        @type value:    anything
        @keyword rank:  An optional argument to send data only to the Processor of the given rank.  If None, then the data will be sent to all Processor instances.
        @type rank:     None or int
        """

        # Send the data to all slaves.
        for i in range(MPI.COMM_WORLD.size):
            # Only send to the given rank.
            if rank != None and rank != 0:
                continue

            # Send the data to the given slave (using a special tag for the data store).
            MPI.COMM_WORLD.send([name, value], dest=i, tag=10)


    def exit(self, status=0):
        """Exit the mpi4py processor with the given status.

        @keyword status:    The program exit status.
        @type status:       int
        """

        # Execution on the slave.
        if MPI.COMM_WORLD.rank != 0:
            # Catch sys.exit being called on an executing slave.
            if self.in_main_loop:
                raise Exception('sys.exit unexpectedly called on slave!')

            # Catch sys.exit
            else:
                sys.stderr.write('\n')
                sys.stderr.write('***********************************************\n')
                sys.stderr.write('\n')
                sys.stderr.write('warning sys.exit called before mpi4py main loop\n')
                sys.stderr.write('\n')
                sys.stderr.write('***********************************************\n')
                sys.stderr.write('\n')
                MPI.COMM_WORLD.Abort()

        # Execution on the master.
        else:
            # Slave clean up.
            if MPI.Is_initialized() and not MPI.Is_finalized() and MPI.COMM_WORLD.rank == 0:
                # Send the exit command to all slaves.
                broadcast_command(Exit_command())

                # Dump all results.
                ditch_all_results()

            # Exit the program with the given status.
            sys.exit(status)


    def get_intro_string(self):
        """Return the string to append to the end of the relax introduction string.

        @return:    The string describing this Processor fabric.
        @rtype:     str
        """

        # Get the specific MPI version.
        version_info = MPI.Get_version()

        # The vendor info.
        vendor = MPI.get_vendor()
        vendor_name = vendor[0]
        vendor_version = str(vendor[1][0])
        for i in range(1, len(vendor[1])):
            vendor_version = vendor_version + '.%i' % vendor[1][i]

        # Return the string.
        return "MPI %s.%s running via mpi4py with %i slave processors & 1 master.  Using %s %s." % (version_info[0], version_info[1], self.processor_size(), vendor_name, vendor_version)


    def get_name(self):
        return '%s-pid%s' % (MPI.Get_processor_name(), os.getpid())


    def master_queue_command(self, command, dest):
        MPI.COMM_WORLD.send(obj=command, dest=dest)


    def master_receive_result(self):
        return MPI.COMM_WORLD.recv(source=MPI.ANY_SOURCE)


    def rank(self):
        return MPI.COMM_WORLD.rank


    def return_result_command(self, result_object):
        MPI.COMM_WORLD.send(obj=result_object, dest=0)


    def run(self):
        self.in_main_loop = True
        super(Mpi4py_processor, self).run()
        self.in_main_loop = False


    def slave_receive_commands(self):
        return MPI.COMM_WORLD.recv(source=0)
