###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""The automatic relaxation dispersion protocol."""

# Python module imports.
from os import getcwd, sep
import sys

# relax module imports.
from lib.text.sectioning import title, subtitle
from pipe_control.pipes import has_pipe
from prompt.interpreter import Interpreter
from status import Status; status = Status()


class Relax_disp:
    def __init__(self, pipe_name=None, pipe_bundle=None, results_dir=None, models=['exp_fit'], grid_inc=11, mc_sim_num=500):
        """Perform a full relaxation dispersion analysis for the given list of models.

        @keyword pipe_name:     The name of the data pipe containing all of the data for the analysis.
        @type pipe_name:        str
        @keyword pipe_bundle:   The data pipe bundle to associate all spawned data pipes with.
        @type pipe_bundle:      str
        @keyword results_dir:   The directory where results files are saved.
        @type results_dir:      str
        @keyword models:        The list of relaxation dispersion models to optimise.
        @type models:           list of str
        @keyword grid_inc:      Number of grid search increments.
        @type grid_inc:         int
        @keyword mc_sim_num:    The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_sim_num:       int
        """

        # Printout.
        title(file=sys.stdout, text="Relaxation dispersion auto-analysis")

        # Execution lock.
        status.exec_lock.acquire(pipe_bundle, mode='auto-analysis')

        # Set up the analysis status object.
        status.init_auto_analysis(pipe_bundle, type='relax_disp')
        status.current_analysis = pipe_bundle

        # Store the args.
        self.pipe_name = pipe_name
        self.pipe_bundle = pipe_bundle
        self.results_dir = results_dir
        self.models = models
        self.grid_inc = grid_inc
        self.mc_sim_num = mc_sim_num

        # No results directory, so default to the current directory.
        if not self.results_dir:
            self.results_dir = getcwd()

        # Data checks.
        self.check_vars()

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Execute.
        self.run()

        # Finish and unlock execution.
        status.auto_analysis[self.pipe_bundle].fin = True
        status.current_analysis = None
        status.exec_lock.release()


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # The pipe name.
        if not has_pipe(self.pipe_name):
            raise RelaxNoPipeError(self.pipe_name)


    def exponential_fit(self):
        """Optimise the simple exponential fit relaxation dispersion model."""

        # Printout.
        subtitle(file=sys.stdout, text="Simple exponential curve-fitting")

        # Create the data pipe by copying the base pipe.o
        self.interpreter.pipe.copy(pipe_from=self.pipe_name, pipe_to='exp_fit', bundle_to=self.pipe_bundle)

        # Grid search.
        self.interpreter.grid_search(inc=self.grid_inc)

        # Minimise.
        self.interpreter.minimise('simplex', constraints=False)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=self.mc_sim_num)
        self.interpreter.monte_carlo.create_data()
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise('simplex', constraints=False)
        self.interpreter.monte_carlo.error_analysis()

        # Write out the results.
        self.write_results()


    def run(self):
        """Execute the auto-analysis."""

        # First optimise the exponential curves to obtain the initial R2eff values for all other models.
        self.exponential_fit()


    def write_results(self):
        """Create a set of results, text and Grace files for the current data pipe."""

        # The directory name.
        path = self.results_dir + sep + cdp.model

        # Save the results.
        self.interpreter.results.write(file='results', dir=path, force=True)

        # Save the relaxation dispersion parameters.
        self.interpreter.value.write(param='rex', file='rex.out', dir=path, force=True)

        # Create Grace plots of the data.
        self.interpreter.grace.write(y_data_type='chi2', file='chi2.agr', dir=path, force=True)
        self.interpreter.grace.write(x_data_type='res_num', y_data_type='r2eff', file='r2eff.agr', dir=path, force=True)
        self.interpreter.grace.write(x_data_type='spin_lock_nu1', y_data_type='r2eff', file='dispersion_curves.agr', dir=path, force=True)
