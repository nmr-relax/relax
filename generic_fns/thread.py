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
from Queue import Queue
from re import search
from threading import Thread


class Threading:
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
        self.host_data = []
        for i in xrange(len(file_data)):
            # Host name.
            host_name = file_data[i][0]
            if host_name == '-':
                host_name = 'localhost'


            # User name.
            user = file_data[i][1]
            if user == '-':
                user = None

            # Host login
            if user:
                login = user + "@" + host_name
            else:
                login = host_name

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

            # Update the host data structure.
            self.host_data.append([host_name, user, login, prog_path, swd, priority])

        # Total number of hosts in hosts file.
        num_hosts = len(self.host_data)


        # Threading.
        ############

        # Initialise the job and results queues and finished hosts array.
        host_queue = Queue()
        results_queue = Queue()
        finished_hosts = []

        # Fill the job queue and finished hosts array.
        for i in xrange(num_hosts):
            host_queue.put(self.host_data[i])
            finished_hosts.append(0)

        # Start threads for each host where each thread will run on the local machine.
        for i in xrange(2):
            RelaxHostThread(self.relax, host_queue, results_queue).start()

        # Determine if all results have been collected.
        num_fin = 0
        while num_fin <= num_hosts:
            print "Inside main loop."
            # Get the next results off the results_queue.
            results, host_data, fail = results_queue.get()

            # Test which host job has finished.
            for i in xrange(num_hosts):
                if self.host_data[i] == host_data:
                    finished_hosts[i] == 1
                    host = i

            # Print the results.
            print "\n\nHost " + `host` + "\n"
            for line in results:
                print line

            # Add all good hosts to self.relax.data.
            if not fail:
                pass

            num_fin = num_fin + 1

            # All jobs have finished.
            all_finished = 1
            for i in xrange(num_hosts):
                if finished_hosts[i] == 0:
                    all_finished = 0
            print all_finished
            if all_finished:
                print "\n\n\nAll finished.\n\n\n"""
                # Add None to the host_queue to signal to the threads to finish.
                host_queue.put(None)

                # Set the terminate flag to 1 to stop this main loop.
                terminated = 1


class RelaxThread(Thread):
    def __init__(self):

        # Run the Thread __init__ function.
        Thread.__init__(self)



class RelaxHostThread(RelaxThread):
    def __init__(self, relax, hosts_queue, results_queue):
        """"""

        # Arguments.
        self.relax = relax
        self.job_queue = hosts_queue
        self.results_queue = results_queue

        # Run the RelaxThread __init__ function.
        RelaxThread.__init__(self)


    def run(self):
        """Function for code execution."""

        # Run until all results are returned.
        while 1:
            print "Inside RelaxHostThread.run loop."
            # Get the data for the next queued job.
            host_data = self.job_queue.get()
            print "Host data: " + `host_data`

            # Quit if host_data is None.  When this is the case, all jobs have been completed.
            if host_data == None:
                break

            # Expand the host_data structure.
            host_name, user, login, prog_path, swd, priority = host_data

            # Host failure flag.
            fail = 0

            # Results.
            self.results = []
            self.results.append("Host name:         " + host_name)
            if user:
                self.results.append("User name:         " + user)
            self.results.append("Program path:      " + prog_path)
            self.results.append("Working directory: " + swd)
            self.results.append("Priority:          " + `priority`)

            # Test the SSH connection.
            if not fail and not self.test_ssh(login):
                fail = 1

            # Test the working directory.
            if not fail and not self.test_wd(login, swd):
                fail = 1

            # Test if relax works.
            if not fail and not self.test_relax(login, prog_path):
                fail = 1

            # Host is accessible.
            if not fail:
                self.results.append("Host OK.")

            # Place the results in the results queue.
            self.results_queue.put((self.results, host_data, fail))


    def test_relax(self, login, prog_path):
        """Function for testing if the program path is valid and that relax can execute."""

        # Test command.
        test_cmd = "ssh %s %s -t" % (login, prog_path)

        # Open a pipe.
        child_stdin, child_stdout, child_stderr = popen3(test_cmd, 'r')

        # Error. 
        err = child_stderr.readlines()
        if len(err):
            # Print out.
            self.results.append("Cannot execute relax on %s using the program path %s" % (login, `prog_path`))
            for line in err:
                self.results.append(line[0:-1])

            # Return fail.
            return 0

        # No errors.
        else:
            return 1


    def test_ssh(self, login):
        """Function for testing the SSH connection."""

        # Test command.
        test_cmd = "ssh -o PasswordAuthentication=no %s echo 'relax, ssh ok'" % login

        # Open a pipe.
        child_stdin, child_stdout, child_stderr = popen3(test_cmd, 'r')

        # Stdout.
        out = child_stdout.readlines()

        # Test if the string 'relax, ssh ok' is in child_stdout.
        for line in out:
            if search('relax, ssh ok', line):
                return 1

        # Error.
        err = child_stderr.readlines()
        if len(err):
            # Print out.
            self.results.append("Cannot establish a SSH connection to %s." % login)

            # Public key auth fail.
            key_auth = 1
            for line in err:
                if search('Permission denied', line):
                    key_auth = 0
            if not key_auth:
                self.results.append("Public key authenication failed.")
                return

            # All other errors.
            for line in err:
                self.results.append(line[0:-1])


    def test_wd(self, login, swd):
        """Function for testing if the working directory on the host machine exist."""

        # Test command.
        test_cmd = "ssh %s ls %s" % (login, swd)

        # Open a pipe.
        child_stdin, child_stdout, child_stderr = popen3(test_cmd, 'r')

        # Error. 
        err = child_stderr.readlines()
        if len(err):
            # Print out.
            self.results.append("Cannot find the working directory %s on %s." % (swd, login))
            for line in err:
                self.results.append(line[0:-1])

            # Return fail.
            return 0

        # No errors.
        else:
            return 1
