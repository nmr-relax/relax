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
from Numeric import sum, zeros
from exceptions import Exception
from os import popen3
from random import randint
from re import search
from string import ascii_letters
import sys
from threading import Lock, Thread


# Class for setting up threading.
#################################

class ThreadSetup:
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
                priority = 5
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

        # Threaded threading setup (for faster ssh responses).
        RelaxHostParentThread(self.relax, self.host_data)

        # Final print out.
        print "\nTotal number of active threads: " + `len(self.relax.data.thread.host_name)`




# The parent class containing the main threading loop.
#######################################################

class RelaxParentThread:
    def __init__(self):
        """Parent class containing the main threading loop."""

        # The number of threads.
        self.num_threads = len(self.relax.data.thread.host_name)


    def run(self, tag=1, save_state=1):
        """Run the main threading loop."""

        # Generate a random string tag to add to all thread files.
        if tag:
            print "Generating a random tag:"
            self.tag = ''
            for i in xrange(5):
                index = randint(0, len(ascii_letters)-1)
                self.tag = self.tag + ascii_letters[index]
            print "    %s\n" % self.tag
            print "All files will be placed in the directory '%s' within the thread's working directory.\n" % self.tag

        # Save the program state.
        if save_state:
            self.save_state_file = 'save_%s.gz' % self.tag
            print "Saving the program state to send to the threads."
            self.relax.generic.state.save(file=self.save_state_file, force=1, compress_type=2)

        # Initialise the job and results queues.
        self.job_queue = Queue()
        self.results_queue = Queue()

        # Fill the job queue with the job indecies.
        for i in xrange(self.num_jobs):
            self.job_queue.put(i)

        # Initialise an array of finished jobs.
        self.finished_jobs = zeros(self.num_jobs)

        # Initialise an array of locks for the jobs.
        self.job_locks = []
        for i in xrange(self.num_threads):
            self.job_locks.append(Lock())

        # Start all threads.
        print "\nStarting all threads.\n"
        self.threads = []
        for i in xrange(self.num_threads):
            self.threads.append(self.thread_object(i))
            self.threads[i].start()

        # The main loop.
        terminated = 0
        while not terminated:
            # Get the next results off the results_queue.
            job_number = self.results_queue.get()

            # The thread has caused a RelaxError.
            if job_number == RelaxError:
                self.thread_clean_up()
                sys.exit()

            # The thread has caused an Exception.
            if job_number == Exception:
                self.thread_clean_up()
                sys.exit()

            # Keyboard interrupt caught by the thread.
            if job_number == KeyboardInterrupt:
                self.thread_clean_up()
                raise KeyboardInterrupt

            # Update the finished jobs.
            self.finished_jobs[job_number] = 1

            # All jobs have finished.
            if sum(self.finished_jobs) == self.num_jobs:
                # Add None to the job_queue to signal the threads to finish.
                self.job_queue.put(None)

                # Set the terminate flag to 1 to stop this main loop.
                terminated = 1


    def thread_clean_up(self):
        """Function for cleaning up the threads."""

        # Kill all threads.
        for thread in self.threads:
            thread.stop(killed=1)

        # Delete the saved state file.
        if hasattr(self, 'save_state_file'):
            self.relax.IO.delete(file_name=self.save_state_file)



# The relax threading base class.
#################################

class RelaxThread(Thread):
    def __init__(self, i, job_queue, results_queue, finished_jobs, job_locks):
        """The base class of all threads in relax."""

        # Run the Thread __init__ function (this is 'asserted' by the Thread class).
        Thread.__init__(self)

        # Arguements.
        self.job_queue = job_queue
        self.results_queue = results_queue
        self.finished_jobs = finished_jobs
        self.job_locks = job_locks

        # Specific thread details.
        self.host_name = self.relax.data.thread.host_name[i]
        self.user      = self.relax.data.thread.user[i]
        self.login     = self.relax.data.thread.login[i]
        self.login_cmd = self.relax.data.thread.login_cmd[i]
        self.prog_path = self.relax.data.thread.prog_path[i]
        self.swd       = self.relax.data.thread.swd[i]
        self.priority  = self.relax.data.thread.priority[i]

        # Initial killed flag.
        self.killed = 0

        # Set the Thread method _Thread__stop to self.stop.
        self._Thread__stop = self.stop

        # Make the directory with the name of tag in the thread's working directory if it doesn't exist.
        if not self.test_dir():
            self.mkdir()

        # Save state file.
        self.save_state_file = "%s/%s/save.gz" % (self.swd, self.tag)

        # Copy the temporary results file to the thread's working directory once during initialisation.
        if not self.test_save_file():
            self.copy_save_file()


    def close_all_pipes(self):
        """Function for closing all the stdin, stdout, and stderr pipes."""

        self.stdin.close()
        self.stdout.close()
        self.stderr.close()


    def copy_save_file(self):
        """Function for the once off copying of the temporary results file to the thread's wd."""

        # Copy command.
        if self.host_name == 'localhost':
            cmd = "cp -p save_%s.gz %s/%s/save.gz" % (self.tag, self.swd, self.tag)
        else:
            cmd = "scp -p save_%s.gz %s:%s/%s/save.gz" % (self.tag, self.login, self.swd, self.tag)
        err = self.open_pipe(cmd=cmd, remote_exe=0, catch_err=1)

        # The file could not be copied.
        if len(err):
            raise RelaxError, "The copy command `%s` could not be executed." % cmd


    def exec_relax(self):
        """Function for running an instance of relax in threading mode on the host machine."""

        # Command.
        cmd = "nice -n %s %s --thread --log %s %s" % (self.priority, self.prog_path, self.log_file, self.script_file)
        self.open_pipe(cmd=cmd, close=0)

        # Catch the results.
        self.results = self.stdout.readlines()

        # Close all pipes.
        self.stdin.close()
        self.stdout.close()

        # Errors.
        err = self.stderr.readlines()
        if len(err):
            for line in err:
                print line[0:-1]

        # Close the error pipe.
        self.stderr.close()


    def job_completed(self):
        """Function for determining if a job has completed successfully."""

        # The job has been finished by a faster thread.
        if self.finished_jobs[self.sim] == 1:
            return 0

        # Success.
        return self.completion_flag


    def mkdir(self):
        """Function for creating the directory 'self.tag' in the working directory."""

        # Command for creating the directory.
        cmd = "mkdir %s/%s" % (self.swd, self.tag)
        err = self.open_pipe(cmd=cmd, catch_err=1)

        # Cannot make the directory.
        if len(err):
            raise RelaxError, "The directory `%s/%s` could not be created on %s." % (self.swd, self.tag, self.host_name)


    def open_pipe(self, cmd, catch_out=0, catch_err=0, remote_exe=1, close=1):
        """Function for opening the stdin, stdout, and stderr pipes and placing them into 'self'."""

        # Initialise text.
        text = None

        # Disallow racing.
        if catch_out and catch_err:
            raise RelaxError, "Cannot catch both stdout and stderr simultaneously, this causes racing."

        # Modify the command for remote execution if necessary.
        if remote_exe:
            cmd = self.remote_command(cmd=cmd, login_cmd=self.login_cmd)

        # Open the pipes.
        self.stdin, self.stdout, self.stderr = popen3(cmd, 'r')

        # Read the output.
        if catch_out:
            text = self.stdout.readlines()

        # Read the errors.
        if catch_err:
            text = self.stderr.readlines()

        # Close all pipes.
        if close:
            self.close_all_pipes()

        # Return the caught text.
        return text


    def remote_command(self, cmd, login_cmd):
        """Return the string required for either local or remote execution of the command."""

        # Remote execution.
        if login_cmd:
            return login_cmd + " \"" + cmd + "\""

        # Local execution.
        return cmd


    def run(self):
        """Main function for execution of the specific threading code."""

        # Run until all results are returned.
        try:
            while 1:
                # Get the job number for the next queued job.
                self.job_number = self.job_queue.get()

                # Quit if the job number is None, this is the signal for when all jobs have been completed.
                if self.job_number == None:
                    # Place None back into the job queue so that all the other waiting threads will terminate.
                    self.job_queue.put(None)

                    # Thread termination (breaking of the while loop).
                    break

                # Run the thread specific code.
                self.exec_thread_code(self.job_number)

                # If the job has completed successfully, place the results in the results queue.
                if self.job_completed():
                    # Place the job number into the results queue.
                    self.results_queue.put(self.job_number)

        # RelaxError.
        except RelaxError, message:
            sys.stderr.write(message)
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
        self._Thread__stopped = 1
        self._Thread__block.notifyAll()
        self._Thread__block.release()



    def test_dir(self):
        """Function for testing if the directory corresponding to tag exists."""

        # Command for testing if directory exists.
        cmd = "ls %s/%s" % (self.swd, self.tag)
        err = self.open_pipe(cmd=cmd, catch_err=1)

        # No directory.
        if len(err):
            return 0

        # Directory exists.
        else:
            return 1


    def test_save_file(self):
        """Function for testing if results file is already copied."""

        # Command for testing if results file is already copied.
        cmd = "ls %s" % self.save_state_file
        err = self.open_pipe(cmd=cmd, catch_err=1)

        # No file.
        if len(err):
            return 0

        # File exists.
        else:
            return 1




# Main threading loop for setting up threading.
###############################################

class RelaxHostParentThread(RelaxParentThread):
    def __init__(self, relax, host_data):
        """Threaded threading setup (for faster ssh responses)."""

        # Arguments.
        self.relax = relax
        self.host_data = host_data

        # Number of threads and number of jobs.
        self.num_threads = self.num_jobs = len(self.host_data)

        # Run the main loop.
        self.run(tag=0, save_state=0)


    def thread_object(self, i):
        """Function for returning an initialised thread object."""

        # Return the thread object.
        return RelaxHostThread(self.relax, self.job_queue, self.results_queue, self.finished_jobs, self.job_locks, self.host_data[i])



# Threads for setting up threading.
###################################

class RelaxHostThread(RelaxThread):
    def __init__(self, relax, job_queue, results_queue, finished_jobs, job_locks, host_data):
        """Initialisation of the thread."""

        # Run the Thread __init__ function (this is 'asserted' by the Thread class).
        Thread.__init__(self)

        # Arguements.
        self.relax = relax
        self.job_queue = job_queue
        self.results_queue = results_queue
        self.finished_jobs = finished_jobs
        self.job_locks = job_locks
        self.host_data = host_data

        # Initial killed flag.
        self.killed = 0

        # Set the Thread method _Thread__stop to self.stop.
        self._Thread__stop = self.stop


    def exec_thread_code(self, data):
        """Function for testing the hosts used in threading."""

        # Expand the data structures.
        self.host_name, self.user, self.login, self.login_cmd, self.prog_path, self.swd, self.priority = self.host_data

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

        # Print the results.
        print "\n\nThread " + `self.job_number` + "\n"
        for line in self.text:
            print line

        # Add all good hosts to self.relax.data.thread
        if not fail:
            # Status.
            if not self.relax.data.thread.status:
                self.relax.data.thread.status = 1

            # Store the details.
            self.relax.data.thread.host_name.append(self.host_name)
            self.relax.data.thread.user.append(self.user)
            self.relax.data.thread.login.append(self.login)
            self.relax.data.thread.login_cmd.append(self.login_cmd)
            self.relax.data.thread.prog_path.append(self.prog_path)
            self.relax.data.thread.swd.append(self.swd)
            self.relax.data.thread.priority.append(self.priority)


    def job_completed(self):
        """Dummy job completion testing function, always return 1."""

        return 1


    def test_relax(self):
        """Function for testing if the program path is valid and that relax can execute."""

        # Test command.
        cmd = "%s --test" % self.prog_path
        err = self.open_pipe(cmd=cmd, catch_err=1)

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
        """Function for testing the SSH connection and public key authentication."""

        # Initialise flag.
        ssh_ok = 0

        # Test command.
        cmd = "ssh -o PasswordAuthentication=no %s echo 'relax> ssh ok'" % self.login
        self.open_pipe(cmd=cmd, remote_exe=0, close=0)

        # Test if the string 'relax, ssh ok' is in self.stdout.
        out = self.stdout.readlines()
        for line in out:
            if search('relax> ssh ok', line):
                ssh_ok = 1
        self.stdout.close()

        # Read the errors.
        err = self.stderr.readlines()
        if len(err):
            # SSH failure message.
            self.text.append("Cannot establish a SSH connection to %s." % self.login)

            # Public key authentication has failed.
            key_auth = 1
            for line in err:
                if search('Permission denied', line):
                    key_auth = 0
            if not key_auth:
                self.text.append("Public key authenication failed.")

            # All other errors.
            for line in err:
                self.text.append(line[0:-1])


    def test_wd(self):
        """Function for testing if the working directory on the host machine exist."""

        # Test command.
        cmd = "if test -d %s; then echo 'OK'; fi" % self.swd
        out = self.open_pipe(cmd=cmd, catch_out=1)

        # Directory exists.
        for line in out:
            if search('OK', line):
                return 1

        # No directory.
        self.text.append("Cannot find the working directory %s on %s." % (self.swd, self.host_name))
        return 0
