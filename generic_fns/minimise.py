###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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
from exceptions import Exception
from os import popen3, popen4
from random import randint
from string import ascii_letters
import sys
from time import sleep
from generic_fns.thread import RelaxThread


class Minimise:
    def __init__(self, relax):
        """Class containing the calc, grid_search, minimise, and set functions."""

        self.relax = relax


    def calc(self, run=None, print_flag=1):
        """Function for calculating the function value."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific calculate function setup.
        calculate = self.relax.specific_setup.setup('calculate', function_type)

        # Monte Carlo simulation calculation.
        if hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state[run] == 1:
            # Loop over the simulations.
            for i in xrange(self.relax.data.sim_number[run]):
                if print_flag:
                    print "Simulation " + `i+1`
                calculate(run=run, print_flag=print_flag-1, sim_index=i)

        # Minimisation.
        else:
            calculate(run=run, print_flag=print_flag)


    def grid_search(self, run=None, lower=None, upper=None, inc=None, constraints=1, print_flag=1):
        """The grid search function."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific grid search function.
        grid_search = self.relax.specific_setup.setup('grid_search', function_type)

        # Monte Carlo simulation grid search.
        if hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state[run] == 1:
            # Loop over the simulations.
            for i in xrange(self.relax.data.sim_number[run]):
                if print_flag:
                    print "Simulation " + `i+1`
                grid_search(run=run, lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag-1, sim_index=i)

        # Grid search.
        else:
            grid_search(run=run, lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag)


    def minimise(self, run=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=1, scaling=1, print_flag=1, sim_index=None):
        """Minimisation function."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific minimisation function.
        minimise = self.relax.specific_setup.setup('minimise', function_type)

        # Minimisation of a single Monte Carlo simulation.
        if sim_index != None:
            minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag, sim_index=sim_index)

        # Monte Carlo simulation minimisation.
        elif hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state[run] == 1:
            # Threaded minimisation of simulations.
            if self.relax.data.thread.status:
                self.minimise_sim_thread(run, min_algor, min_options, func_tol, grad_tol, max_iterations, constraints, scaling, print_flag)

            # Non-threaded minimisation of simulations.
            else:
                for i in xrange(self.relax.data.sim_number[run]):
                    if print_flag:
                        print "Simulation " + `i+1`
                    minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag-1, sim_index=i)

        # Standard minimisation.
        else:
            minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag)


    def minimise_sim_thread(self, run, *min_args):
        """Function for the minimisation of Monte Carlo simulations using threading."""

        # Print out.
        print "Threaded minimisation of Monte Carlo simulations.\n"

        # Generate a random string tag to add to all thread files.
        tag = ''
        for i in xrange(5):
            index = randint(0, len(ascii_letters)-1)
            tag = tag + ascii_letters[index]
        print "All files generated for or by the threads will be placed in the directory " + `tag` + "."

        # Generate a temporary results file.
        self.temp_file = tag + '_initial_results'
        print "Saving the current results for run " + `run` + " in the file 'initial_results' for initialising all threads."
        self.relax.generic.results.write(run=run, file=self.temp_file, directory='/tmp', force=1, compress_type=0)
        print ""

        # Initialise the job and results queues.
        job_queue = Queue()
        results_queue = Queue()

        # Fill the job queue.
        for i in xrange(self.relax.data.sim_number[run]):
            job_queue.put(i)

        # Start all threads.
        self.threads = []
        for i in xrange(len(self.relax.data.thread.host_name)):
            self.threads.append(RelaxMinimiseThread(self.relax, i, job_queue, results_queue, tag, run, min_args))
            self.threads[i].start()

        # The main loop.
        terminated = 0
        num_fin = 0
        try:
            while not terminated:
                # Get the next results off the results_queue.
                sim_number = results_queue.get()
                num_fin = num_fin + 1

                # A thread has caused a RelaxError.
                if sim_number == RelaxError:
                    raise RelaxError

                # A thread has caused an Exception.
                if sim_number == Exception:
                    raise RelaxError

                # Keyboard interrupt caught by the thread.
                if sim_number == KeyboardInterrupt:
                    raise KeyboardInterrupt

                # All jobs have finished.
                if num_fin == self.relax.data.sim_number[run]:
                    # Add None to the job_queue to signal the threads to finish.
                    job_queue.put(None)

                    # Set the terminate flag to 1 to stop this main loop.
                    terminated = 1

                # Print the simulation number.
                print "Simulation " + `sim_number+1`

        # Catch RelaxErrors and Exceptions.
        except RelaxError:
            self.thread_clean_up()
            sys.exit()

        # Catch the Keyboard Interrupt.
        except KeyboardInterrupt:
            self.thread_clean_up()
            raise KeyboardInterrupt

        # All other errors.
        except:
            self.thread_clean_up()
            sys.exit()


    def thread_clean_up(self):
        """Function for cleaning up the threads."""

        # Kill all threads.
        for thread in self.threads:
            thread.stop(killed=1)

        # Delete the temporary results file.
        self.relax.IO.delete(file_name=self.temp_file, dir='/tmp')



class RelaxMinimiseThread(RelaxThread):
    def __init__(self, relax, i, job_queue, results_queue, tag, parent_run, min_args):
        """Initialisation of the thread."""

        # Arguments.
        self.relax = relax
        self.i = i
        self.tag = tag
        self.parent_run = parent_run
        self.min_args = min_args

        # Run the RelaxThread __init__ function (this is 'asserted' by the Thread class).
        RelaxThread.__init__(self, job_queue, results_queue)

        # Expand the minimisation arguments.
        self.min_algor, self.min_options, self.func_tol, self.grad_tol, self.max_iterations, self.constraints, self.scaling, self.print_flag = self.min_args

        # Make the directory with the name of tag in the thread's working directory if it doesn't exist.
        if not self.test_dir():
            self.mkdir()

        # Results file.
        self.results_file = "%s/%s/initial_results" % (self.relax.data.thread.swd[self.i], self.tag)

        # Copy the temporary results file to the thread's working directory once during initialisation.
        if not self.test_results_file():
            self.copy_results()


    def copy_results(self):
        """Function for the once off copying of the temporary results file to the thread's wd."""

        # Copy command.
        if self.relax.data.thread.host_name[self.i] == 'localhost':
            cmd = "cp -p /tmp/%s_initial_results %s/%s/initial_results" % (self.tag, self.relax.data.thread.swd[self.i], self.tag)
        else:
            cmd = "scp -p /tmp/%s_initial_results %s:%s/%s/initial_results" % (self.tag, self.relax.data.thread.login[self.i], self.relax.data.thread.swd[self.i], self.tag)

        # Open a pipe for the copy.
        child_stdin, child_stdout, child_stderr = popen3(cmd, 'r')

        # Stderr.
        err = child_stderr.readlines()

        # Close all pipes.
        child_stdin.close()
        child_stdout.close()
        child_stderr.close()

        # The file could not be copied.
        if len(err):
            raise RelaxError, "The copy command `%s` could not be executed." % cmd


    def exec_relax(self):
        """Function for running an instance of relax in threading mode on the host machine."""

        # Command.
        cmd = "%s --thread --log %s %s" % (self.relax.data.thread.prog_path[self.i], self.log_file, self.script_file)
        cmd = self.relax.generic.threading.remote_command(cmd=cmd, login_cmd=self.relax.data.thread.login_cmd[self.i])
        print cmd

        # Open a pipe.
        child_stdin, child_stdout, child_stderr = popen3(cmd, 'r')

        # Catch the results.
        self.results = child_stdout.readlines()

        # Close all pipes.
        child_stdin.close()
        child_stdout.close()

        # Errors.
        err = child_stderr.readlines()
        if len(err):
            for line in err:
                print line[0:-1]

        # Close the error pipe.
        child_stderr.close()


    def exec_thread_code(self, data):
        """Function containing the thread specific code.
        
        This code is for the minimisation of a single Monte Carlo simulation.
        """

        # Place the job queue data, which in this case is the simulation number, in self.
        self.sim = data

        # Thread run name.
        self.thread_run = '%s_sim_%s' % (self.tag, self.sim)

        # Script and log files.
        self.script_file = "%s/%s/script_sim_%s.py" % (self.relax.data.thread.swd[self.i], self.tag, self.sim)
        self.log_file = "%s/%s/sim_%s.log" % (self.relax.data.thread.swd[self.i], self.tag, self.sim)

        # Generate the script file for the minimisation of sim number `sim`.
        self.generate_script()

        # Execute relax and run the script.
        self.exec_relax()

        # Create a run in the parent to temporarily store the data prior to copying into the main run.
        self.relax.generic.runs.create(run=self.thread_run, run_type=self.relax.data.run_types[self.relax.data.run_names.index(self.parent_run)])

        # Read the data into the run.
        self.relax.generic.results.read(run=self.thread_run, file_data=self.results)

        # Copy the results from the thread run to the parent run.
        self.relax.generic.results.copy(run1=self.thread_run, run2=self.parent_run, sim=self.sim)

        # Delete the thread run
        self.relax.generic.runs.delete(self.thread_run)

        # Set the results to the completed simulation number.
        self.results = self.sim


    def generate_script(self):
        """Function for generating the script for the thread to minimise sim `sim`."""

        # Function array.
        fn = []

        # Function: Create the run.
        fn.append("self.relax.generic.runs.create(run='%s', run_type='%s')" % (self.thread_run, self.relax.data.run_types[self.relax.data.run_names.index(self.parent_run)]))

        # Function: Read the results.
        fn.append("self.relax.generic.results.read(run='%s', file='%s')" % (self.thread_run, self.results_file))

        # Function: Minimise.
        fn.append("self.relax.generic.minimise.minimise(run='%s', min_algor='%s', min_options=%s, func_tol=%s, grad_tol=%s, max_iterations=%s, constraints=%s, scaling=%s, print_flag=%s, sim_index=%s)" % (self.thread_run, self.min_algor, self.min_options, self.func_tol, self.grad_tol, self.max_iterations, self.constraints, self.scaling, self.print_flag, self.sim))

        # Function: Turn logging off.  This is so that the results can come back through the pipe's stdout.
        fn.append("self.relax.IO.logging_off()")

        # Generate the main text of the script file.
        text = ''
        for i in xrange(len(fn)):
            text = text + "print \"\\n" + fn[i] + "\"\n"
            text = text + fn[i] + "\n"

        # Function: Write the to stdout.
        text = text + "self.relax.generic.results.display(run='%s')\n" % (self.thread_run)

        # Cat the text into the script file.
        cmd = "cat > %s" % self.script_file
        cmd = self.relax.generic.threading.remote_command(cmd=cmd, login_cmd=self.relax.data.thread.login_cmd[self.i])

        # Open a pipe.
        child_stdin, child_stdout, child_stderr = popen3(cmd, 'r')

        # Write the text to the pipe's stdin, then close it.
        child_stdin.write(text)
        child_stdin.close()

        # Stderr.
        err = child_stderr.readlines()

        # Close all pipes.
        child_stdout.close()
        child_stderr.close()

        # The file could not be copied.
        if len(err):
            raise RelaxError, "The command `%s` could not be executed." % cmd


    def mkdir(self):
        """Function for creating the directory 'tag' in the working directory."""

        # Command for creating the directory.
        cmd = "mkdir %s/%s" % (self.relax.data.thread.swd[self.i], self.tag)
        cmd = self.relax.generic.threading.remote_command(cmd=cmd, login_cmd=self.relax.data.thread.login_cmd[self.i])

        # Open a pipe.
        child_stdin, child_stdout, child_stderr = popen3(cmd, 'r')

        # Stderr.
        err = child_stderr.readlines()

        # Close all pipes.
        child_stdin.close()
        child_stdout.close()
        child_stderr.close()

        # Cannot make the directory.
        if len(err):
            raise RelaxError, "The directory `%s/%s` could not be created on %s." % (self.relax.data.thread.swd[self.i], self.tag, self.relax.data.thread.host_name[self.i])


    def test_dir(self):
        """Function for testing if the directory corresponding to tag exists."""

        # Command for testing if directory exists.
        test_cmd = "ls %s/%s" % (self.relax.data.thread.swd[self.i], self.tag)
        test_cmd = self.relax.generic.threading.remote_command(cmd=test_cmd, login_cmd=self.relax.data.thread.login_cmd[self.i])

        # Open a pipe.
        child_stdin, child_stdout, child_stderr = popen3(test_cmd, 'r')

        # Stderr.
        err = child_stderr.readlines()

        # Close all pipes.
        child_stdin.close()
        child_stdout.close()
        child_stderr.close()

        # No directory.
        if len(err):
            return 0

        # Directory exists.
        else:
            return 1


    def test_results_file(self):
        """Function for testing if results file is already copied."""

        # Command for testing if results file is already copied.
        test_cmd = "ls %s" % self.results_file
        test_cmd = self.relax.generic.threading.remote_command(cmd=test_cmd, login_cmd=self.relax.data.thread.login_cmd[self.i])

        # Open a pipe.
        child_stdin, child_stdout, child_stderr = popen3(test_cmd, 'r')

        # Stderr.
        err = child_stderr.readlines()

        # Close all pipes.
        child_stdin.close()
        child_stdout.close()
        child_stderr.close()

        # No file.
        if len(err):
            return 0

        # File exists.
        else:
            return 1
