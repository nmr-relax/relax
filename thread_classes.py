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
from random import randint
from re import search
from string import ascii_letters
import sys
from time import sleep
from threading import Lock, Thread

from data import Element
#from processes import RelaxPopen3


# Class for setting up threading.
#################################

class Threading:
    def __init__(self, relax):
        """Class containing functions for setting up and executing threading in relax."""

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
                login_cmd = 'ssh -o ForwardX11=no ' + login + ' '

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

        # Threaded threading setup (for faster ssh responses).
        RelaxHostParentThread(self.relax, self.host_data)

        # Final print out.
        print "\nTotal number of active threads: " + `len(self.relax.thread_data.host_name)`



# Class containing the thread data.
###################################

class ThreadData(Element):
    def __init__(self):
        """Class containing all the thread data."""

        # Host data for threading.
        self.status = 0
        self.host_name = []
        self.user = []
        self.login = []
        self.login_cmd = []
        self.cp_cmd = []
        self.prog_path = []
        self.swd = []
        self.priority = []



# The parent class containing the main threading loop.
#######################################################

class RelaxParentThread:
    def __init__(self):
        """Parent class containing the main threading loop."""

        # The number of threads.
        self.num_threads = len(self.relax.thread_data.host_name)


    def run(self, tag=1, save_state=1):
        """Run the main threading loop."""

        # Generate a random string tag to add to all thread files.
        if tag:
            print "Generating a random tag:"
            self.tag = ''
            for i in xrange(8):
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
        for i in xrange(self.num_jobs):
            self.job_locks.append(Lock())

        # Start the results thread.
        RelaxResultsThread(self.job_queue, self.results_queue, self.finished_jobs, self.job_locks).start()

        # Start all sub-threads.
        print "\nStarting all threads.\n"
        self.threads = []
        for i in xrange(self.num_threads):
            # Instantiate and place the thread in 'self.threads'.
            self.threads.append(self.thread_object(i))

            # Start the thread.
            self.threads[i].start()

            # Name the thread.
            self.threads[i].setName("Thread-" + `i`)

        # The main loop.
        try:
            while 1:
                # Sleep for 0.2 seconds.
                sleep(0.2)

                # All jobs have finished.
                if sum(self.finished_jobs) == self.num_jobs:
                    # Add None to the job_queue to signal the threads to finish.
                    self.job_queue.put(None)

                    # Add None to the results_queue to signal to the results thread to finish.
                    self.results_queue.put(None)

                    # Break the main loop.
                    break

        # Catch the keyboard interrupt signal.
        except KeyboardInterrupt:
            # Loop over all jobs.
            for i in xrange(self.num_jobs):
                # Tell the threads that all jobs have finished.
                self.finished_jobs[i] == 1

                # Release the job locks.
                if self.job_locks[i].locked():
                    self.job_locks[i].release()

            # Thread clean up function.
            self.thread_clean_up(print_flag=1)

            # Reraise the keyboard interrupt signal.
            raise KeyboardInterrupt

        # Thread clean up function.
        self.thread_clean_up()


    def thread_clean_up(self, print_flag=0):
        """Function for cleaning up the threads."""

        # Print out.
        if print_flag:
            print "Cleaning up threads."

        # Place None onto the results queue to terminate the results thread.
        self.results_queue.put(None)

        # Place None onto the jobs queue to terminate the threads.
        self.job_queue.put(None)

        # Kill all threads (as threads to serialise and speed up the kill process).
        kill_threads = []
        for i in xrange(self.num_threads):
            # Initialise the thread.
            kill_threads.append(RelaxKillThread(self.threads[i], print_flag))

            # Start all the threads.
            kill_threads[i].start()

        # Hang until finished.
        while 1:
            # Count the number of finished kill threads.
            num_killed = 0
            for i in xrange(self.num_threads):
                if not kill_threads[i].isAlive():
                    num_killed = num_killed + 1

            # Exit.
            if num_killed == self.num_threads:
                break

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

        # Set as a daemon.
        self.setDaemon(1)

        # Arguements.
        self.job_queue = job_queue
        self.results_queue = results_queue
        self.finished_jobs = finished_jobs
        self.job_locks = job_locks

        # Specific thread details.
        self.host_name = self.relax.thread_data.host_name[i]
        self.user      = self.relax.thread_data.user[i]
        self.login     = self.relax.thread_data.login[i]
        self.login_cmd = self.relax.thread_data.login_cmd[i]
        self.prog_path = self.relax.thread_data.prog_path[i]
        self.swd       = self.relax.thread_data.swd[i]
        self.priority  = self.relax.thread_data.priority[i]

        # Flag for when relax will be spawned on the host machine.
        self.spawn_relax_flag = 1

        # Kill flag.
        self.kill_flag = 0

        # Make the directory with the name of tag in the thread's working directory if it doesn't exist.
        if not self.test_dir():
            self.mkdir()

        # Save state file.
        self.save_state_file = "%s/%s/save.gz" % (self.swd, self.tag)

        # Copy the temporary results file to the thread's working directory once during initialisation.
        if not self.test_save_file():
            self.copy_save_file()


    def close_all_pipes(self):
        """Close all the stdin, stdout, and stderr pipes of the child (to flush the buffers)."""

        # Close stdin.
        if not self.child.tochild.closed:
            self.child.tochild.close()

        # Close stdout.
        if not self.child.fromchild.closed:
            self.child.fromchild.close()

        # Close stderr.
        if not self.child.childerr.closed:
            self.child.childerr.close()


    def copy_save_file(self):
        """Function for the once off copying of the temporary results file to the thread's wd."""

        # Copy command.
        if self.host_name == 'localhost':
            cmd = "cp -p save_%s.gz %s/%s/save.gz" % (self.tag, self.swd, self.tag)
        else:
            cmd = "scp -p save_%s.gz %s:%s/%s/save.gz" % (self.tag, self.login, self.swd, self.tag)
        err = self.start_child(cmd=cmd, remote_exe=0, catch_err=1)

        # The file could not be copied.
        if len(err):
            raise RelaxError, "The copy command `%s` could not be executed." % cmd


    def exec_relax(self):
        """Function for running an instance of relax in threading mode on the host machine."""

        # Command.
        cmd = "nice -n %s %s --thread --log %s %s" % (self.priority, self.prog_path, self.log_file, self.script_file)
        self.start_child(cmd=cmd, close=0)

        # Catch the PID.
        self.child.relax_pid = self.child.fromchild.readline()
        self.child.relax_pid = int(self.child.relax_pid[0:-1])

        # Catch the results.
        self.results = self.child.fromchild.readlines()

        # Close all pipes.
        self.child.tochild.close()
        self.child.fromchild.close()

        # Errors.
        err = self.child.childerr.readlines()
        if len(err):
            for line in err:
                print line[0:-1]

        # Close the error pipe.
        self.child.childerr.close()


    def mkdir(self):
        """Function for creating the directory 'self.tag' in the working directory."""

        # Command for creating the directory.
        cmd = "mkdir %s/%s" % (self.swd, self.tag)
        err = self.start_child(cmd=cmd, catch_err=1)

        # Cannot make the directory.
        if len(err):
            raise RelaxError, "The directory `%s/%s` could not be created on %s." % (self.swd, self.tag, self.host_name)


    def pre_locked_code(self):
        """Generic function for the pre-locked code."""

        # Generate the script file.
        self.generate_script()

        # Execute relax and run the script.
        self.exec_relax()


    def remote_command(self, cmd, login_cmd):
        """Return the string required for either local or remote execution of the command."""

        # Remote execution.
        if login_cmd:
            return login_cmd + " \"" + cmd + "\""

        # Local execution.
        return cmd


    def run(self, expanded_flag=1):
        """Main function for execution of the specific threading code."""

        # Run until all results are returned.
        while 1:
            # Catch the kill signal.
            if self.kill_flag:
                break

            # Get the job number for the next queued job.
            self.job_number = self.job_queue.get()

            # Quit if the job number is None, this is the signal for when all jobs have been completed.
            if self.job_number == None:
                # Place None back into the job queue so that all the other waiting threads will terminate.
                self.job_queue.put(None)

                # Thread termination (breaking of the while loop).
                break

            # Job termination if finished by a faster thread.
            if self.finished_jobs[self.job_number] == 1:
                continue

            # Place the job back into the job queue.  This is to make the threads fail safe and so that idle faster threads will pick up the jobs of the slower threads.
            self.job_queue.put(self.job_number)

            # Catch all exceptions in the specific code.
            try:
                # Run all the code.
                if self.spawn_relax_flag:
                    # Script and log files.
                    self.script_file = "%s/%s/script_%s_job_%s.py" % (self.swd, self.tag, self.getName(), self.job_number)
                    self.log_file = "%s/%s/%s_job_%s.log" % (self.swd, self.tag, self.getName(), self.job_number)

                    # Thread run name.
                    self.thread_run = 'job_%s' % self.job_number

                # Run the specific code prior to locking the job.
                self.pre_locked_code()

                # Lock the job.
                self.job_locks[self.job_number].acquire()

                # Job termination if finished by a faster thread.
                if self.finished_jobs[self.job_number] == 1:
                    # Release the lock.
                    self.job_locks[self.job_number].release()

                    # Job termination without running the post locked code or placing the job number in the results queue.
                    continue

                # Catch the kill signal.
                if self.kill_flag:
                    break

                # Run the specific code after locking the job.
                self.post_locked_code()

            # All other errors.
            except:
                # Catch a kill.
                if self.kill_flag:
                    break

                # Print the exception if in debugging mode.
                if Debug:
                    raise

                # Print out.
                print "%s, job %s on %s: failed.  Thread sleeping for 5 minutes." % (self.getName(), self.job_number, self.host_name)

                # Sleep for 5 min.
                sleep(300)

                # Skip to the next job.
                continue

            # Place the job number into the results queue.
            self.results_queue.put(self.job_number)


    def start_child(self, cmd, catch_out=0, catch_err=0, remote_exe=1, close=1):
        """Start the child process and place it in 'self.child'."""

        # Initialise text.
        text = None

        # Disallow racing.
        if catch_out and catch_err:
            raise RelaxError, "Cannot catch both stdout and stderr simultaneously, this causes racing."

        # Modify the command for remote execution if necessary.
        if remote_exe:
            cmd = self.remote_command(cmd=cmd, login_cmd=self.login_cmd)

        # Open the pipes.
        self.child = RelaxPopen3(cmd, capturestderr=1)

        # Read the output.
        if catch_out:
            text = self.child.fromchild.readlines()

        # Read the errors.
        if catch_err:
            text = self.child.childerr.readlines()

        # Close all pipes.
        if close:
            self.close_all_pipes()

        # Return the caught text.
        return text


    def kill(self, print_flag=0):
        """Attempt to kill the thread."""

        # Set the thread's kill flag.
        self.kill_flag = 1

        # Kill the child process.
        if hasattr(self, 'child'):
            self.child.kill(login_cmd=self.login_cmd)

        # Finish active jobs.
        if hasattr(self, 'job_number') and self.job_number != None:
            # Set the job to finished.
            self.finished_jobs[self.job_number] = 1

            # Release the job lock.
            if self.job_locks[self.job_number].locked():
                self.job_locks[self.job_number].release()

        # Print out.
        if print_flag:
            print "%s, job %s on %s terminated." % (self.getName(), self.job_number, self.host_name)


    def test_dir(self):
        """Function for testing if the directory corresponding to tag exists."""

        # Command for testing if directory exists.
        cmd = "ls %s/%s" % (self.swd, self.tag)
        err = self.start_child(cmd=cmd, catch_err=1)

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
        err = self.start_child(cmd=cmd, catch_err=1)

        # No file.
        if len(err):
            return 0

        # File exists.
        else:
            return 1




# The results thread.
#####################

class RelaxResultsThread(Thread):
    def __init__(self, job_queue, results_queue, finished_jobs, job_locks):
        """The thread for collecting results."""

        # Run the Thread __init__ function (this is 'asserted' by the Thread class).
        Thread.__init__(self)

        # Set as a daemon.
        self.setDaemon(1)

        # Arguements.
        self.job_queue = job_queue
        self.results_queue = results_queue
        self.finished_jobs = finished_jobs
        self.job_locks = job_locks


    def run(self):
        """Main function for execution of the specific threading code."""

        # Loop until all results are in.
        while 1:
            # Get the next results off the results_queue (hang here until a result is queued).
            job_number = self.results_queue.get()

            # Termination of the thread.
            if job_number == None:
                break

            # Update the finished jobs.
            self.finished_jobs[job_number] = 1

            # Release the lock (finished jobs must be updated first).
            if self.job_locks[job_number].locked():
                self.job_locks[job_number].release()




# The thread for killing a thread.
##################################

class RelaxKillThread(Thread):
    def __init__(self, thread, print_flag):
        """The thread for collecting results."""

        # Run the Thread __init__ function (this is 'asserted' by the Thread class).
        Thread.__init__(self)

        # Set as a daemon.
        self.setDaemon(1)

        # Arguments.
        self.thread = thread
        self.print_flag = print_flag


    def run(self):
        """Main function for execution of the specific threading code."""

        # Run the threads' kill code.
        self.thread.kill(self.print_flag)




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
        return RelaxHostThread(self.relax, self.job_queue, self.results_queue, self.finished_jobs, self.job_locks, self.host_data)



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

        # Relax will not be spawned on the host machine (except for testing).
        self.spawn_relax_flag = 0

        # Kill flag.
        self.kill_flag = 0


    def pre_locked_code(self):
        """Code to run prior to locking the job."""

        # Expand the data structures.
        self.host_name, self.user, self.login, self.login_cmd, self.prog_path, self.swd, self.priority = self.host_data[self.job_number]

        # Host failure flag.
        self.fail = 0

        # Text.
        self.text = []
        self.text.append("%-20s%-10s" % ("Host name:", self.host_name))
        self.text.append("%-20s%-10s" % ("User name:", self.user))
        self.text.append("%-20s%-10s" % ("Program path:", self.prog_path))
        self.text.append("%-20s%-10s" % ("Working directory:", self.swd))
        self.text.append("%-20s%-10i" % ("Priority:", self.priority))

        # Test the SSH connection.
        if self.host_name != 'localhost' and not self.fail and not self.test_ssh():
            self.fail = 1

        # Test the working directory.
        if not self.fail and not self.test_wd():
            self.fail = 1

        # Test if relax works.
        if not self.fail and not self.test_relax():
            self.fail = 1

        # Host is accessible.
        if not self.fail:
            self.text.append("%-20s%-10s" % ("Host status:", "[ OK ]"))


    def post_locked_code(self):
        """Code to run after locking the job."""

        # Print the results.
        for line in self.text:
            print line
        print "\n"

        # Add all good hosts to self.relax.thread_data
        if not self.fail:
            # Status.
            if not self.relax.thread_data.status:
                self.relax.thread_data.status = 1

            # Store the details.
            self.relax.thread_data.host_name.append(self.host_name)
            self.relax.thread_data.user.append(self.user)
            self.relax.thread_data.login.append(self.login)
            self.relax.thread_data.login_cmd.append(self.login_cmd)
            self.relax.thread_data.prog_path.append(self.prog_path)
            self.relax.thread_data.swd.append(self.swd)
            self.relax.thread_data.priority.append(self.priority)


    def test_relax(self):
        """Function for testing if the program path is valid and that relax can execute."""

        # Test command.
        cmd = "%s --test" % self.prog_path
        err = self.start_child(cmd=cmd, catch_err=1)

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

        # Test command.
        cmd = "ssh -o PasswordAuthentication=no -o ForwardX11=no %s \"echo 'relax> ssh ok'\"" % self.login
        self.start_child(cmd=cmd, remote_exe=0, close=0)

        # Test if the string 'relax, ssh ok' is in self.child.fromchild.
        out = self.child.fromchild.readlines()
        for line in out:
            if search('relax> ssh ok', line):
                return 1

        # Read the errors.
        err = self.child.childerr.readlines()
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
        out = self.start_child(cmd=cmd, catch_out=1)

        # Directory exists.
        for line in out:
            if search('OK', line):
                return 1

        # No directory.
        self.text.append("Cannot find the working directory %s on %s." % (self.swd, self.host_name))
        return 0
