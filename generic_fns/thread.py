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

from os import popen3
from re import search


class Thread:
    def __init__(self, relax):
        """Class containing the function to calculate the XH vector from the loaded structure."""

        self.relax = relax


    def read(self, file=None, dir=None):
        """Function for reading a hosts file."""

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(file, dir)

        # Strip data.
        file_data = self.relax.file_ops.strip(file_data)

        # Do nothing if the file does not exist.
        if not file_data:
            raise RelaxFileEmptyError

        # Loop over the hosts.
        for i in xrange(len(file_data)):
            # Host name.
            host_name = file_data[i][0]
            if host_name == '-':
                host_name = 'localhost'

            # User name.
            user = file_data[i][1]
            if user == '-':
                user = None

            # Program path.
            prog_path = file_data[i][2]
            if prog_path == '-':
                prog_path = 'relax'

            # Working directory.
            swd = file_data[i][3]
            if swd == '-':
                swd = '~/.relax'

            # Priority.
            priority = file_data[i][4]
            if priority == '-':
                priority = 15
            try:
                int(priority)
            except ValueError:
                raise RelaxIntError, ('priority', priority)

            # Print out.
            print "\n\nHost " + `i` + "\n"
            print "Host name:         " + host_name
            if user:
                print "User name:         " + user
            print "Program path:      " + prog_path
            print "Working directory: " + swd
            print "Priority:          " + `priority`

            # Test the SSH connection.
            if not self.test_ssh(host_name, user):
                continue


    def test_ssh(self, host_name, user):
        """Function for testing the SSH connection."""

        # Host login
        if user:
            login = user + "@" + host_name
        else:
            login = host_name
        
        # Test command.
        test_cmd = "ssh -o PasswordAuthentication=no " + login + " echo 'relax, ssh ok'"

        # Open a pipe.
        child_stdin, child_stdout, child_stderr = popen3(test_cmd, 'r')

        # Stdout and stderr.
        out = child_stdout.readlines()
        err = child_stderr.readlines()

        # Test if the string 'relax, ssh ok' is in child_stdout.
        for line in out:
            if search('relax, ssh ok', line):
                return 1

        # Print out.
        print "Cannot establish a SSH connection to " + login + "."
        if len(err) > 0:
            # Public key auth fail.
            key_auth = 1
            for line in err:
                if search('Permission denied', line):
                    key_auth = 0
            if not key_auth:
                print "Public key authenication failed."
                return

            # All other errors.
            for line in err:
                print line[0:-1]
