###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
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

# TODO: clone communicators & resize
# TODO: check exceptions on master

# Python module imports.
import os
import sys
import textwrap

# relax module imports.
from multi.commands import Exit_command
from multi.multi_processor_base import Multi_processor, Too_few_slaves_exception


# save original sys.exit to call after wrapper
_sys_exit = sys.exit

in_main_loop = False

# load mpi
try:
    from mpi4py import MPI
except ImportError:
    msg = '''The dependency 'mpi4py' has not been installed. You should either

                 1. Run without multiprocessor support i.e. remove the
                    --multi mpi4py flag from the command line.

                 2. Install mpi4py.

                 3. Choose another multi processor method to give to the
                    --multi command line flag.\n'''
    #FIXME dedent not working
    msg = textwrap.dedent(msg)
    sys.stderr.write(msg)
    sys.stderr.write('exiting...\n\n')
    sys.exit()


def broadcast_command(command):
    for i in range(1, MPI.COMM_WORLD.size):
        if i != 0:
            MPI.COMM_WORLD.Send(buf=command, dest=i)


def ditch_all_results():
    for i in range(1, MPI.COMM_WORLD.size):
        if i != 0:
            while 1:
                result = MPI.COMM_WORLD.Recv(source=i)
                if result.completed:
                    break


# wrapper sys.exit function
# CHECKME is status ok
def exit(status=None):
    if MPI.COMM_WORLD.rank != 0:
        if in_main_loop:
            raise Exception('sys.exit unexpectedley called on slave!')
        else:
            sys.__stderr__.write('\n')
            sys.__stderr__.write('***********************************************\n')
            sys.__stderr__.write('\n')
            sys.__stderr__.write('warning sys.exit called before mpi4py main loop\n')
            sys.__stderr__.write('\n')
            sys.__stderr__.write('***********************************************\n')
            sys.__stderr__.write('\n')
            MPI.COMM_WORLD.Abort()
    else:
        #print 'here'
        exit_mpi()
        #MPI.COMM_WORLD.Abort(1)
        _sys_exit(status)


def exit_mpi():
    if MPI.Is_initialized() and not MPI.Is_finalized() and MPI.COMM_WORLD.rank == 0:
        broadcast_command(Exit_command())
        ditch_all_results()


class Mpi4py_processor(Multi_processor):
    """The mpi4py multi-processor class."""

    def __init__(self, processor_size, callback):
        mpi_processor_size = MPI.COMM_WORLD.size-1

        if processor_size == -1:
            processor_size = mpi_processor_size

        # FIXME: needs better support in relax generates stack trace
        if mpi_processor_size == 0:
            raise Too_few_slaves_exception()

        msg = 'warning: mpi4py_processor is using 1 masters and %d slave processors you requested %d slaves\n'
        if processor_size != (mpi_processor_size):
            print msg % (mpi_processor_size, processor_size)

        super(Mpi4py_processor, self).__init__(processor_size=mpi_processor_size, callback=callback)

        # wrap sys.exit to close down mpi before exiting
        sys.exit = exit


    def abort(self):
        MPI.COMM_WORLD.Abort()


    #TODO: MAY NEED support for widths?
    def get_intro_string(self):
        version_info = MPI.Get_version()
        return '''MPI running via mpi4py with %d slave processors & 1 master, mpi version = %s.%s''' % (self.processor_size(), version_info[0], version_info[1])


    def get_name(self):
        return '%s-pid%s' % (MPI.Get_processor_name(), os.getpid())


    def master_queue_command(self, command, dest):
        MPI.COMM_WORLD.Send(buf=command, dest=dest)


    def master_recieve_result(self):
        return MPI.COMM_WORLD.Recv(source=MPI.ANY_SOURCE)


    def rank(self):
        return MPI.COMM_WORLD.rank


    def return_result_command(self, result_object):
        MPI.COMM_WORLD.Send(buf=result_object, dest=0)


    def run(self):
        global in_main_loop
        in_main_loop = True
        super(Mpi4py_processor, self).run()
        in_main_loop = False


    def slave_recieve_commands(self):
        return MPI.COMM_WORLD.Recv(source=0)
