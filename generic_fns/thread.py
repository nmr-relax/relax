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

from Queue import Queue
from os import popen3
from re import search
from threading import Thread


class Threading:
    def __init__(self, relax):
        """Class containing the function to calculate the XH vector from the loaded structure."""

        self.relax = relax


    def execute(self):
        """Run relax in threading mode."""

        # Execute the script.
        execfile(self.relax.script_file)


    def read(self, file=None, dir=None):
        """Function for reading a hosts file."""

        # Extract the data from the file.
        file_data = self.relax.IO.extract_data(file, dir)

        # Strip data.
        file_data = self.relax.IO.strip(file_data)

        # Do nothing if the file does not exist.
        if not file_data:
            raise RelaxFileEmptyError

        # Loop over the hosts.
        self.host_data = []
        for i in xrange(len(file_data)):
            # Test to see if the correct number of columns exist.
            if len(file_data[i]) != 6:
                raise RelaxError, "The number of columns in the hosts file line " + `file_data[i]` + " should be six."

            # Host name.
            host_name = file_data[i][0]
            if host_name == '-':
                host_name = 'localhost'

            # User name.
            user = file_data[i][1]
            if user == '-':
                user = None

            # Host login
            if host_name == 'localhost':
                login = None
            elif user:
                login = user + '@' + host_name
            else:
                login = host_name

            # Login command.
            if host_name == 'localhost':
                login_cmd = None
            else:
                login_cmd = 'ssh ' + login + ' '

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
                priority = int(priority)
            except ValueError:
                raise RelaxIntError, ('priority', priority)

            # Number of CPUs.
            num_cpus = file_data[i][5]
            if num_cpus == '-':
                num_cpus = 1
            try:
                num_cpus = int(num_cpus)
            except ValueError:
                raise RelaxIntError, ('CPUs', num_cpus)

            # Update the host data structure.
            for j in xrange(num_cpus):
                self.host_data.append([host_name, user, login, login_cmd, prog_path, swd, priority])

        # Total number of hosts in hosts file.
        num_jobs = len(self.host_data)


        # Threading.
        ############

        # Initialise the job and results queues.
        host_queue = Queue()
        results_queue = Queue()

        # Fill the job queue.
        for i in xrange(num_jobs):
            host_queue.put((self.host_data[i], i))

        # Start threads for each host where each thread will run on the local machine.
        for i in xrange(num_jobs):
            RelaxHostThread(self.relax, host_queue, results_queue).start()

        # The main loop.
        terminated = 0
        num_fin = 0
        while not terminated:
            # Get the next results off the results_queue.
            results, job_index, fail = results_queue.get()
            num_fin = num_fin + 1

            # Print the results.
            print "\n\nThread " + `job_index` + "\n"
            for line in results:
                print line

            # Add all good hosts to self.relax.data.thread
            if not fail:
                # Status.
                if not self.relax.data.thread.status:
                    self.relax.data.thread.status = 1

                # Store the details.
                self.relax.data.thread.host_name.append(self.host_data[job_index][0])
                self.relax.data.thread.user.append(self.host_data[job_index][1])
                self.relax.data.thread.login.append(self.host_data[job_index][2])
                self.relax.data.thread.login_cmd.append(self.host_data[job_index][3])
                self.relax.data.thread.prog_path.append(self.host_data[job_index][4])
                self.relax.data.thread.swd.append(self.host_data[job_index][5])
                self.relax.data.thread.priority.append(self.host_data[job_index][6])

            # All jobs have finished.
            if num_fin == num_jobs:
                # Add None to the host_queue to signal the threads to finish.
                host_queue.put(None)

                # Set the terminate flag to 1 to stop this main loop.
                terminated = 1

        # Final print out.
        print "\nTotal number of active threads: " + `len(self.relax.data.thread.host_name)`


    def remote_command(self, cmd, login_cmd):
        """Return the string required for either local or remote execution of the command."""

        # Remote execution.
        if login_cmd:
            return login_cmd + " \"" + cmd + "\""

        # Local execution.
        return cmd



class RelaxThread(Thread):
    def __init__(self, job_queue, results_queue):

        # Arguements.
        self.job_queue = job_queue
        self.results_queue = results_queue

        # Initial killed flag.
        self.killed = 0

        # Run the Thread __init__ function (this is 'asserted' by the Thread class).
        Thread.__init__(self)

        # Set the Thread method _Thread__stop to self.stop.
        self._Thread__stop = self.stop


    def run(self):
        """Function for execution of the specific threading code."""

        # Run until all results are returned.
        try:
            while 1:
                # Get the data for the next queued job.
                data = self.job_queue.get()

                # Quit if the queue data is None.  None is the signal within relax for when all jobs have been completed.
                if data == None:
                    # Place None back into the job queue so that all the other waiting threads will terminate.
                    self.job_queue.put(None)

                    # Thread termination.
                    break

                # Run the thread specific code.
                self.exec_thread_code(data)

                # Place the results in the results queue.
                self.results_queue.put(self.results)

        # RelaxError.
        except RelaxError, message:
            print message
            self.results_queue.put(RelaxError)

        # KeyboardInterupt.
        except KeyboardInterrupt:
            self.results_queue.put(KeyboardInterrupt)

        # All other errors.
        except:
            self.results_queue.put(Exception)
            if not self.killed:
                raise


    def stop(self, killed=0):
        """Modified stop function."""

        # Set a class specific flag.
        if killed:
            self.killed = 1

        # From the Thread class.
        self._Thread__block.acquire()
        self._Thread__stopped = True
        self._Thread__block.notifyAll()
        self._Thread__block.release()



class RelaxHostThread(RelaxThread):
    def __init__(self, relax, hosts_queue, results_queue):
        """Initialisation of the thread."""

        # Arguments.
        self.relax = relax

        # Run the RelaxThread __init__ function (this is 'asserted' by the Thread class).
        RelaxThread.__init__(self, hosts_queue, results_queue)


    def exec_thread_code(self, data):
        """Function containing the thread specific code.
        
        This code is for the testing of the hosts used in threading.
        """

        # Expand the data structures.
        host_data, job_index = data
        self.host_name, self.user, self.login, self.login_cmd, self.prog_path, self.swd, self.priority = host_data

        # Host failure flag.
        fail = 0

        # Text.
        self.text = []
        self.text.append("%-20s%-10s" % ("Host name:", self.host_name))
        self.text.append("%-20s%-10s" % ("User name:", self.user))
        self.text.append("%-20s%-10s" % ("Program path:", self.prog_path))
        self.text.append("%-20s%-10s" % ("Working directory:", self.swd))
        self.text.append("%-20s%-10i" % ("Priority:", self.priority))

        # Test the SSH connection.
        if self.host_name != 'localhost' and not fail and not self.test_ssh():
            fail = 1

        # Test the working directory.
        if not fail and not self.test_wd():
            fail = 1

        # Test if relax works.
        if not fail and not self.test_relax():
            fail = 1

        # Host is accessible.
        if not fail:
            self.text.append("%-20s%-10s" % ("Host status:", "[ OK ]"))

        # Package the results.
        self.results = (self.text, job_index, fail)


    def test_relax(self):
        """Function for testing if the program path is valid and that relax can execute."""

        # Test command.
        test_cmd = "%s --test" % self.prog_path
        if self.login_cmd:
            test_cmd = self.login_cmd + test_cmd

        # Open a pipe.
        child_stdin, child_stdout, child_stderr = popen3(test_cmd, 'r')

        # Stdout and stderr.
        err = child_stderr.readlines()

        # Close all pipes.
        child_stdin.close()
        child_stdout.close()
        child_stderr.close()

        # Error. 
        if len(err):
            # Print out.
            self.text.append("Cannot execute relax on %s using the program path %s" % (self.login, `self.prog_path`))
            for line in err:
                self.text.append(line[0:-1])

            # Return fail.
            return 0

        # No errors.
        else:
            return 1


    def test_ssh(self):
        """Function for testing the SSH connection."""

        # Test command.
        test_cmd = "ssh -o PasswordAuthentication=no %s echo 'relax, ssh ok'" % self.login

        # Open a pipe.
        child_stdin, child_stdout, child_stderr = popen3(test_cmd, 'r')

        # Stdout and stderr.
        out = child_stdout.readlines()
        err = child_stderr.readlines()

        # Close all pipes.
        child_stdin.close()
        child_stdout.close()
        child_stderr.close()

        # Test if the string 'relax, ssh ok' is in child_stdout.
        for line in out:
            if search('relax, ssh ok', line):
                return 1

        # Error.
        if len(err):
            # Print out.
            self.text.append("Cannot establish a SSH connection to %s." % self.login)

            # Public key auth fail.
            key_auth = 1
            for line in err:
                if search('Permission denied', line):
                    key_auth = 0
            if not key_auth:
                self.text.append("Public key authenication failed.")
                return

            # All other errors.
            for line in err:
                self.text.append(line[0:-1])


    def test_wd(self):
        """Function for testing if the working directory on the host machine exist."""

        # Test command.
        test_cmd = "if test -d %s; then echo 'OK'; fi" % self.swd
        test_cmd = self.relax.generic.threading.remote_command(cmd=test_cmd, login_cmd=self.login_cmd)

        # Open a pipe.
        child_stdin, child_stdout, child_stderr = popen3(test_cmd, 'r')

        # Stdout.
        out = child_stdout.readlines()

        # Close all pipes.
        child_stdin.close()
        child_stdout.close()
        child_stderr.close()

        # Directory exists. 
        for line in out:
            if search('OK', line):
                return 1

        # No directory.
        self.text.append("Cannot find the working directory %s on %s." % (self.swd, self.host_name))
        return 0
