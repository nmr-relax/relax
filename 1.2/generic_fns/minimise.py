###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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
from re import search

#from processes import RelaxPopen3
from thread_classes import RelaxParentThread, RelaxThread


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
        overfit_deselect = self.relax.specific_setup.setup('overfit_deselect', function_type)

        # Deselect residues lacking data:
        overfit_deselect(run)

        # Monte Carlo simulation calculation.
        if hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state.has_key(run) and self.relax.data.sim_state[run] == 1:
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
        overfit_deselect = self.relax.specific_setup.setup('overfit_deselect', function_type)

        # Deselect residues lacking data:
        overfit_deselect(run)

        # Monte Carlo simulation grid search.
        if hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state.has_key(run) and self.relax.data.sim_state[run] == 1:
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
        overfit_deselect = self.relax.specific_setup.setup('overfit_deselect', function_type)

        # Deselect residues lacking data:
        overfit_deselect(run)

        # Single Monte Carlo simulation.
        if sim_index != None:
            minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag, sim_index=sim_index)

        # Monte Carlo simulation minimisation.
        elif hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state.has_key(run) and self.relax.data.sim_state[run] == 1:
            # Threaded minimisation of simulations.
            if self.relax.thread_data.status:
                # Print out.
                print "Threaded minimisation of Monte Carlo simulations.\n"

                # Run the main threading loop.
                RelaxMinParentThread(self.relax, run, min_algor, min_options, func_tol, grad_tol, max_iterations, constraints, scaling, print_flag)

            # Non-threaded minimisation of simulations.
            else:
                for i in xrange(self.relax.data.sim_number[run]):
                    if print_flag:
                        print "Simulation " + `i+1`
                    minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag-1, sim_index=i)

        # Standard minimisation.
        else:
            minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag)


    def reset_min_stats(self, run, index=None):
        """Function for resetting the minimisation statistics."""

        # Arguments.
        self.run = run

        # Global minimisation statistics.
        if index == None:
            # Chi-squared.
            if hasattr(self.relax.data, 'chi2') and self.relax.data.chi2.has_key(self.run):
                self.relax.data.chi2[self.run] = None

            # Iteration count.
            if hasattr(self.relax.data, 'iter') and self.relax.data.iter.has_key(self.run):
                self.relax.data.iter[self.run] = None

            # Function count.
            if hasattr(self.relax.data, 'f_count') and self.relax.data.f_count.has_key(self.run):
                self.relax.data.f_count[self.run] = None

            # Gradient count.
            if hasattr(self.relax.data, 'g_count') and self.relax.data.g_count.has_key(self.run):
                self.relax.data.g_count[self.run] = None

            # Hessian count.
            if hasattr(self.relax.data, 'h_count') and self.relax.data.h_count.has_key(self.run):
                self.relax.data.h_count[self.run] = None

            # Warning.
            if hasattr(self.relax.data, 'warning') and self.relax.data.warning.has_key(self.run):
                self.relax.data.warning[self.run] = None

        # Sequence specific minimisation statistics.
        else:
            # Chi-squared.
            if hasattr(self.relax.data.res[self.run][index], 'chi2'):
                self.relax.data.res[self.run][index].chi2 = None

            # Iteration count.
            if hasattr(self.relax.data.res[self.run][index], 'iter'):
                self.relax.data.res[self.run][index].iter = None

            # Function count.
            if hasattr(self.relax.data.res[self.run][index], 'f_count'):
                self.relax.data.res[self.run][index].f_count = None

            # Gradient count.
            if hasattr(self.relax.data.res[self.run][index], 'g_count'):
                self.relax.data.res[self.run][index].g_count = None

            # Hessian count.
            if hasattr(self.relax.data.res[self.run][index], 'h_count'):
                self.relax.data.res[self.run][index].h_count = None

            # Warning.
            if hasattr(self.relax.data.res[self.run][index], 'warning'):
                self.relax.data.res[self.run][index].warning = None


    def return_conversion_factor(self, stat_type):
        """Dummy function for returning 1.0."""

        return 1.0


    def return_data_name(self, name):
        """
        Minimisation statistic data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |              |                                                  |
        | Data type              | Object name  | Patterns                                         |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Chi-squared statistic  | 'chi2'       | '^[Cc]hi2$' or '^[Cc]hi[-_ ][Ss]quare'           |
        |                        |              |                                                  |
        | Iteration count        | 'iter'       | '^[Ii]ter'                                       |
        |                        |              |                                                  |
        | Function call count    | 'f_count'    | '^[Ff].*[ -_][Cc]ount'                           |
        |                        |              |                                                  |
        | Gradient call count    | 'g_count'    | '^[Gg].*[ -_][Cc]ount'                           |
        |                        |              |                                                  |
        | Hessian call count     | 'h_count'    | '^[Hh].*[ -_][Cc]ount'                           |
        |________________________|______________|__________________________________________________|

        """

        # Chi-squared.
        if search('^[Cc]hi2$', name) or search('^[Cc]hi[-_ ][Ss]quare', name):
            return 'chi2'

        # Iteration count.
        if search('^[Ii]ter', name):
            return 'iter'

        # Function call count.
        if search('^[Ff].*[ -_][Cc]ount', name):
            return 'f_count'

        # Gradient call count.
        if search('^[Gg].*[ -_][Cc]ount', name):
            return 'g_count'

        # Hessian call count.
        if search('^[Hh].*[ -_][Cc]ount', name):
            return 'h_count'


    def return_grace_string(self, stat_type):
        """Function for returning the Grace string representing the data type for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(stat_type)

        # Chi-squared.
        if object_name == 'chi2':
            grace_string = '\\xc\\S2'

        # Iteration count.
        elif object_name == 'iter':
            grace_string = 'Iteration count'

        # Function call count.
        elif object_name == 'f_count':
            grace_string = 'Function call count'

        # Gradient call count.
        elif object_name == 'g_count':
            grace_string = 'Gradient call count'

        # Hessian call count.
        elif object_name == 'h_count':
            grace_string = 'Hessian call count'

        # Return the Grace string.
        return grace_string


    def return_units(self, stat_type):
        """Dummy function which returns None as the stats have no units."""

        return None


    def return_value(self, run, index=None, stat_type=None, sim=None):
        """Function for returning the minimisation statistic corresponding to 'stat_type'."""

        # Arguments.
        self.run = run

        # Get the object name.
        object_name = self.return_data_name(stat_type)

        # The statistic type does not exist.
        if not object_name:
            raise RelaxError, "The statistic type " + `stat_type` + " does not exist."

        # The simulation object name.
        object_sim = object_name + '_sim'

        # Get the global statistic.
        if index == None:
            # Get the statistic.
            if sim == None:
                if hasattr(self.relax.data, object_name) and getattr(self.relax.data.res[self.run][index], object_name).has_key(self.run):
                    stat = getattr(self.relax.data, object_name)[self.run]
                else:
                    stat = None

            # Get the simulation statistic.
            else:
                if hasattr(self.relax.data, object_sim) and getattr(self.relax.data.res[self.run][index], object_sim).has_key(self.run):
                    stat = getattr(self.relax.data, object_sim)[self.run][sim]
                else:
                    stat = None

        # Residue specific statistic.
        else:
            # Get the statistic.
            if sim == None:
                if hasattr(self.relax.data.res[self.run][index], object_name):
                    stat = getattr(self.relax.data.res[self.run][index], object_name)
                else:
                    stat = None

            # Get the simulation statistic.
            else:
                if hasattr(self.relax.data.res[self.run][index], object_sim):
                    stat = getattr(self.relax.data.res[self.run][index], object_sim)[sim]
                else:
                    stat = None

        # Return the statistic (together with None to indicate that there are no errors associated with the statistic).
        return stat, None


    def set(self, run=None, value=None, error=None, param=None, scaling=None, index=None):
        """
        Minimisation statistic set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        This shouldn't really be executed by a user.
        """

        # Arguments.
        self.run = run

        # Get the parameter name.
        param_name = self.return_data_name(param)

        # Global minimisation stats.
        if index == None:
            # Chi-squared.
            if param_name == 'chi2':
                self.relax.data.chi2[self.run] = value

            # Iteration count.
            elif param_name == 'iter':
                self.relax.data.iter[self.run] = value

            # Function call count.
            elif param_name == 'f_count':
                self.relax.data.f_count[self.run] = value

            # Gradient call count.
            elif param_name == 'g_count':
                self.relax.data.g_count[self.run] = value

            # Hessian call count.
            elif param_name == 'h_count':
                self.relax.data.h_count[self.run] = value

        # Residue specific minimisation.
        else:
            # Chi-squared.
            if param_name == 'chi2':
                self.relax.data.res[self.run][index].chi2 = value

            # Iteration count.
            elif param_name == 'iter':
                self.relax.data.res[self.run][index].iter = value

            # Function call count.
            elif param_name == 'f_count':
                self.relax.data.res[self.run][index].f_count = value

            # Gradient call count.
            elif param_name == 'g_count':
                self.relax.data.res[self.run][index].g_count = value

            # Hessian call count.
            elif param_name == 'h_count':
                self.relax.data.res[self.run][index].h_count = value



# Main threading loop for the minimisation of Monte Carlo simulations.
######################################################################

class RelaxMinParentThread(RelaxParentThread):
    def __init__(self, relax, parent_run, *min_args):
        """Initialisation of the Monte Carlo simulation minimisation parent thread."""

        # Arguments.
        self.relax = relax
        self.parent_run = parent_run
        self.min_args = min_args

        # Run the RelaxParentThread __init__ function.
        RelaxParentThread.__init__(self)

        # The number of jobs.
        self.num_jobs = self.relax.data.sim_number[self.parent_run]

        # Run the main loop.
        self.run()


    def thread_object(self, i):
        """Function for returning an initialised thread object."""

        # Return the thread object.
        return RelaxMinimiseThread(self.relax, i, self.job_queue, self.results_queue, self.finished_jobs, self.job_locks, self.tag, self.parent_run, self.min_args)



# Threads for the minimisation of Monte Carlo simulations.
##########################################################

class RelaxMinimiseThread(RelaxThread):
    def __init__(self, relax, i, job_queue, results_queue, finished_jobs, job_locks, tag, parent_run, min_args):
        """Initialisation of the thread."""

        # Arguments.
        self.relax = relax
        self.tag = tag
        self.parent_run = parent_run
        self.min_args = min_args

        # Run the RelaxThread __init__ function (this is 'asserted' by the Thread class).
        RelaxThread.__init__(self, i, job_queue, results_queue, finished_jobs, job_locks)

        # Expand the minimisation arguments.
        self.min_algor, self.min_options, self.func_tol, self.grad_tol, self.max_iterations, self.constraints, self.scaling, self.print_flag = self.min_args


    def generate_script(self):
        """Function for generating the script for the thread to minimise sim `sim`."""

        # Function array.
        fn = []

        # Function: Load the program state.
        fn.append("self.relax.generic.state.load(file='%s')" % self.save_state_file)

        # Function: Minimise.
        fn.append("self.relax.generic.minimise.minimise(run='%s', min_algor='%s', min_options=%s, func_tol=%s, grad_tol=%s, max_iterations=%s, constraints=%s, scaling=%s, print_flag=%s, sim_index=%s)" % (self.parent_run, self.min_algor, self.min_options, self.func_tol, self.grad_tol, self.max_iterations, self.constraints, self.scaling, self.print_flag, self.job_number))

        # Function: Turn logging off.  This is so that the results can come back through the child's stdout pipe.
        fn.append("self.relax.IO.logging_off()")

        # Generate the main text of the script file.
        text = ''
        for i in xrange(len(fn)):
            text = text + "\nprint \"\\n" + fn[i] + "\"\n"
            text = text + fn[i] + "\n"

        # Function: Write the results to stdout.
        text = text + "self.relax.generic.results.display(run='%s')\n" % (self.parent_run)

        # Cat the text into the script file.
        cmd = "cat > %s" % self.script_file
        cmd = self.remote_command(cmd=cmd, login_cmd=self.login_cmd)

        # Start the child process.
        self.child = RelaxPopen3(cmd, capturestderr=1)

        # Write the text to the child's stdin, then close it.
        self.child.tochild.write(text)
        self.child.tochild.close()

        # Catch errors.
        err = self.child.childerr.readlines()

        # Close all pipes.
        self.child.fromchild.close()
        self.child.childerr.close()

        # The file could not be copied.
        if len(err):
            raise RelaxError, "The command `%s` could not be executed." % cmd


    def post_locked_code(self):
        """Code to run after locking the job."""

        # Create a run in the parent to temporarily store the data prior to copying into the main run.
        self.relax.generic.runs.create(run=self.thread_run, run_type=self.relax.data.run_types[self.relax.data.run_names.index(self.parent_run)])

        # Read the data into the run.
        self.relax.generic.results.read(run=self.thread_run, file_data=self.results, print_flag=0)

        # Copy the results from the thread run to the parent run.
        self.relax.generic.results.copy(run1=self.thread_run, run2=self.parent_run, sim=self.job_number)

        # Delete the thread run.
        self.relax.generic.runs.delete(self.thread_run)

        # Print out.
        print "Simulation: " + `self.job_number`
