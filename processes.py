###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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

from os import kill, popen3
from popen2 import Popen3


class RelaxPopen3(Popen3):
    def __init__(self, cmd, capturestderr=0, bufsize=-1):
        """Extended Popen3 class."""

        # Run the init function of the Popen3 class.
        Popen3.__init__(self, cmd, capturestderr, bufsize)


    def kill(self, login_cmd=None, sig=9):
        """Function for killing the child process."""

        # Kill the relax process spawned by the thread.
        if hasattr(self, 'relax_pid'):
            # Kill command.
            kill_cmd = 'kill -%s %s' % (sig, self.relax_pid)

            # Remote relax process.
            if login_cmd:
                kill_cmd = login_cmd + " \"" + kill_cmd + "\""

            # Kill relax.
            try:
                stdin, stdout, stderr = popen3(kill_cmd)
            except:
                pass

        # Kill the child process.
        try:
            kill(self.pid, sig)
        except:
            pass
