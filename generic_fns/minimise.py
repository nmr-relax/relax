###############################################################################
#                                                                             #
# Copyright (C) 2003-2005, 2007-2008 Edward d'Auvergne                        #
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

# Python module imports.
from Queue import Queue
from re import search

# relax module imports.
from data import Data as relax_data_store
from selection import spin_loop
#from processes import RelaxPopen3
from relax_errors import RelaxError, RelaxNoPipeError
from specific_fns import get_specific_fn
from thread_classes import RelaxParentThread, RelaxThread


def reset_min_stats(data_pipe=None, spin=None):
    """Function for resetting the minimisation statistics.

    @param data_pipe:   The name of the data pipe to reset the minimisation statisics of.  This
                        defaults to the current data pipe.
    @type data_pipe:    str
    @param spin:        The spin data container if spin specific data is to be reset.
    @type spin:         SpinContainer
    """

    # The data pipe.
    if data_pipe == None:
        data_pipe = relax_data_store.current_pipe

    # Alias the current data pipe.
    cdp = relax_data_store[data_pipe]


    # Global minimisation statistics.
    #################################

    # Chi-squared.
    if hasattr(cdp, 'chi2'):
        cdp.chi2 = None

    # Iteration count.
    if hasattr(cdp, 'iter'):
        cdp.iter = None

    # Function count.
    if hasattr(cdp, 'f_count'):
        cdp.f_count = None

    # Gradient count.
    if hasattr(cdp, 'g_count'):
        cdp.g_count = None

    # Hessian count.
    if hasattr(cdp, 'h_count'):
        cdp.h_count = None

    # Warning.
    if hasattr(cdp, 'warning'):
        cdp.warning = None


    # Sequence specific minimisation statistics.
    ############################################

    # Loop over all spins.
    for spin in spin_loop():
        # Chi-squared.
        if hasattr(spin, 'chi2'):
            spin.chi2 = None

        # Iteration count.
        if hasattr(spin, 'iter'):
            spin.iter = None

        # Function count.
        if hasattr(spin, 'f_count'):
            spin.f_count = None

        # Gradient count.
        if hasattr(spin, 'g_count'):
            spin.g_count = None

        # Hessian count.
        if hasattr(spin, 'h_count'):
            spin.h_count = None

        # Warning.
        if hasattr(spin, 'warning'):
            spin.warning = None



def calc(print_flag=1):
    """Function for calculating the function value.

    @param print_flag:  A flag specifying the amount of information to print.  The higher the value,
                        the greater the verbosity.
    @type print_flag:   int
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Specific calculate function setup.
    calculate = get_specific_fn('calculate', cdp.pipe_type)
    overfit_deselect = get_specific_fn('overfit_deselect', cdp.pipe_type)

    # Deselect residues lacking data:
    overfit_deselect()

    # Monte Carlo simulation calculation.
    if hasattr(cdp, 'sim_state') and cdp.sim_state == 1:
        # Loop over the simulations.
        for i in xrange(cdp.sim_number):
            if print_flag:
                print "Simulation " + `i+1`
            calculate(print_flag=print_flag-1, sim_index=i)

    # Minimisation.
    else:
        calculate(print_flag=print_flag)


def grid_search(lower=None, upper=None, inc=None, constraints=1, print_flag=1):
    """The grid search function.

    @param lower:       The lower bounds of the grid search which must be equal to the number of
                        parameters in the model.
    @type lower:        array of numbers
    @param upper:       The upper bounds of the grid search which must be equal to the number of
                        parameters in the model.
    @type upper:        array of numbers
    @param inc:         The increments for each dimension of the space for the grid search.  The
                        number of elements in the array must equal to the number of parameters in
                        the model.
    @type inc:          array of int
    @param constraints: If true, constraints are applied during the grid search (elinating parts of
                        the grid).  If false, no constraints are used.
    @type constraints:  bool
    @param print_flag:  A flag specifying the amount of information to print.  The higher the value,
                        the greater the verbosity.
    @type print_flag:   int
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Specific grid search function.
    grid_search = get_specific_fn('grid_search', cdp.pipe_type)
    overfit_deselect = get_specific_fn('overfit_deselect', cdp.pipe_type)

    # Deselect residues lacking data:
    overfit_deselect()

    # Monte Carlo simulation grid search.
    if hasattr(cdp, 'sim_state') and cdp.sim_state == 1:
        # Loop over the simulations.
        for i in xrange(cdp.sim_number):
            if print_flag:
                print "Simulation " + `i+1`
            grid_search(lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag-1, sim_index=i)

    # Grid search.
    else:
        grid_search(lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag)


def minimise(min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=1, scaling=1, print_flag=1, sim_index=None):
    """Minimisation function.

    @param min_algor:       The minimisation algorithm to use.
    @type min_algor:        str
    @param min_options:     An array of options to be used by the minimisation algorithm.
    @type min_options:      array of str
    @param func_tol:        The function tolerence which, when reached, terminates optimisation.
                            Setting this to None turns of the check.
    @type func_tol:         None or float
    @param grad_tol:        The gradient tolerence which, when reached, terminates optimisation.
                            Setting this to None turns of the check.
    @type grad_tol:         None or float
    @param max_iterations:  The maximum number of iterations for the algorithm.
    @type max_iterations:   int
    @param constraints:     If true, constraints are used during optimisation.
    @type constraints:      bool
    @param scaling:         If true, diagonal scaling is enabled during optimisation to allow the
                            problem to be better conditioned.
    @type scaling:          bool
    @param print_flag:      A flag specifying the amount of information to print.  The higher the
                            value, the greater the verbosity.
    @type print_flag:       int
    @param sim_index:       The index of the simulation to optimise.  This should be None if normal
                            optimisation is desired.
    @type sim_index:        None or int
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Specific minimisation function.
    minimise = get_specific_fn('minimise', cdp.pipe_type)
    overfit_deselect = get_specific_fn('overfit_deselect', cdp.pipe_type)

    # Deselect residues lacking data:
    overfit_deselect()

    # Single Monte Carlo simulation.
    if sim_index != None:
        minimise(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag, sim_index=sim_index)

    # Monte Carlo simulation minimisation.
    elif hasattr(relax_data_store, 'sim_state') and relax_data_store.sim_state == 1:
        # Threaded minimisation of simulations.
        if self.relax.thread_data.status:
            # Print out.
            print "Threaded minimisation of Monte Carlo simulations.\n"

            # Run the main threading loop.
            RelaxMinParentThread(self.relax, min_algor, min_options, func_tol, grad_tol, max_iterations, constraints, scaling, print_flag)

        # Non-threaded minimisation of simulations.
        else:
            for i in xrange(relax_data_store.sim_number):
                if print_flag:
                    print "Simulation " + `i+1`
                minimise(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag-1, sim_index=i)

    # Standard minimisation.
    else:
        minimise(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag)


def return_conversion_factor(stat_type):
    """Dummy function for returning 1.0.

    @param stat_type:   The name of the statistic.  This is unused!
    @type stat_type:    str
    @return:            A conversion factor of 1.0.
    @type return:       float
    """

    return 1.0


def return_data_name(name):
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
    __docformat__ = "plaintext"

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


def return_grace_string(stat_type):
    """Function for returning the Grace string representing the data type for axis labelling.

    @param stat_type:   The name of the statistic to return the Grace string for.
    @type stat_type:    str
    @return:            The Grace string.
    @type return:       str
    """

    # Get the object name.
    object_name = return_data_name(stat_type)

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


def return_units(stat_type):
    """Dummy function which returns None as the stats have no units.

    @param stat_type:   The name of the statistic.  This is unused!
    @type stat_type:    str
    @return:            Nothing.
    @type return:       None
    """

    return None


def return_value(spin=None, stat_type=None, sim=None):
    """Function for returning the minimisation statistic corresponding to 'stat_type'.

    @param spin:        The spin data container if spin specific data is to be reset.
    @type spin:         SpinContainer
    @param stat_type:   The name of the statistic to return the value for.
    @type stat_type:    str
    @param sim:         The index of the simulation to return the value for.  If None, then the
                        normal value is returned.
    @type sim:          None or int
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Get the object name.
    object_name = return_data_name(stat_type)

    # The statistic type does not exist.
    if not object_name:
        raise RelaxError, "The statistic type " + `stat_type` + " does not exist."

    # The simulation object name.
    object_sim = object_name + '_sim'

    # Get the global statistic.
    if spin == None:
        # Get the statistic.
        if sim == None:
            if hasattr(cdp, object_name):
                stat = getattr(cdp, object_name)
            else:
                stat = None

        # Get the simulation statistic.
        else:
            if hasattr(cdp, object_sim):
                stat = getattr(cdp, object_sim)[sim]
            else:
                stat = None

    # Residue specific statistic.
    else:
        # Get the statistic.
        if sim == None:
            if hasattr(spin, object_name):
                stat = getattr(spin, object_name)
            else:
                stat = None

        # Get the simulation statistic.
        else:
            if hasattr(spin, object_sim):
                stat = getattr(spin, object_sim)[sim]
            else:
                stat = None

    # Return the statistic (together with None to indicate that there are no errors associated with the statistic).
    return stat, None


def set(value=None, error=None, param=None, scaling=None, spin=None):
    """
        Minimisation statistic set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        This shouldn't really be executed by a user.
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Get the parameter name.
    param_name = return_data_name(param)

    # Global minimisation stats.
    if index == None:
        # Chi-squared.
        if param_name == 'chi2':
            cdp.chi2 = value

        # Iteration count.
        elif param_name == 'iter':
            cdp.iter = value

        # Function call count.
        elif param_name == 'f_count':
            cdp.f_count = value

        # Gradient call count.
        elif param_name == 'g_count':
            cdp.g_count = value

        # Hessian call count.
        elif param_name == 'h_count':
            cdp.h_count = value

    # Residue specific minimisation.
    else:
        # Chi-squared.
        if param_name == 'chi2':
            spin.chi2 = value

        # Iteration count.
        elif param_name == 'iter':
            spin.iter = value

        # Function call count.
        elif param_name == 'f_count':
            spin.f_count = value

        # Gradient call count.
        elif param_name == 'g_count':
            spin.g_count = value

        # Hessian call count.
        elif param_name == 'h_count':
            spin.h_count = value



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
        self.num_jobs = relax_data_store.sim_number[self.parent_run]

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
        self.relax.generic.runs.create(run=self.thread_run, run_type=relax_data_store.run_types[relax_data_store.run_names.index(self.parent_run)])

        # Read the data into the run.
        self.relax.generic.results.read(run=self.thread_run, file_data=self.results, print_flag=0)

        # Copy the results from the thread run to the parent run.
        self.relax.generic.results.copy(run1=self.thread_run, run2=self.parent_run, sim=self.job_number)

        # Delete the thread run.
        self.relax.generic.runs.delete(self.thread_run)

        # Print out.
        print "Simulation: " + `self.job_number`
