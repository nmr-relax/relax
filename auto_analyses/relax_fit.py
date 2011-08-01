###############################################################################
#                                                                             #
# Copyright (C) 2004-2011 Edward d'Auvergne                                   #
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

# Module docstring.
"""The automatic relaxation curve fitting protocol."""

# Python module imports.
from os import sep

# relax module imports.
from generic_fns.pipes import cdp_name, has_pipe, switch
import generic_fns.structure.main
from prompt.interpreter import Interpreter
from status import Status; status = Status()



class Relax_fit:
    def __init__(self, pipe_name=None, file_root='rx', results_dir=None, grid_inc='11', mc_sim_num=500, view_plots=True):
        """Perform relaxation curve fitting.

        To use this auto-analysis, a data pipe with all the required data needs to be set up.  This data pipe should contain the following:

            - All the spins loaded.
            - Unresolved spins deselected.
            - All the peak intensities loaded and relaxation delay times set.
            - Either the baseplane noise RMDS values should be set or replicated spectra loaded.

        @keyword pipe_name:     The name of the data pipe containing all of the data for the analysis.
        @type pipe_name:        str
        @keyword file_root:     File root of the output filea.
        @type file_root:        str
        @keyword results_dir:   The directory where results files are saved.
        @type results_dir:      str
        @keyword grid_inc:      Number of grid search increments.
        @type grid_inc:         int
        @keyword mc_sim_num:    The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_sim_num:       int
        @keyword view_plots:    Flag to automatically view grace plots after calculation.
        @type view_plots:       bool
        """

        # Execution lock.
        status.exec_lock.acquire('auto relax fit')

        # Set up the analysis status object.
        status.init_auto_analysis(pipe_name, type='relax_fit')

        # Store the args.
        self.pipe_name = pipe_name
        self.file_root = file_root
        self.results_dir = results_dir
        if self.results_dir:
            self.grace_dir = results_dir + sep + 'grace'
        else:
            self.grace_dir = 'grace'
        self.mc_sim_num = mc_sim_num
        self.grid_inc = grid_inc
        self.view_plots = view_plots

        # Data checks.
        self.check_vars()

        # Set the data pipe to the current data pipe.
        if self.pipe_name != cdp_name():
            switch(self.pipe_name)

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Execute.
        self.run()

        # Finish and unlock execution.
        status.auto_analysis[self.pipe_name].fin = True
        status.exec_lock.release()


    def run(self):
        """Set up and run the curve-fitting."""

        # Peak intensity error analysis.
        self.interpreter.spectrum.error_analysis()

        # Set the relaxation curve type.
        self.interpreter.relax_fit.select_model('exp')

        # Grid search.
        self.interpreter.grid_search(inc=self.grid_inc)

        # Minimise.
        self.interpreter.minimise('simplex', scaling=False, constraints=False)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=self.mc_sim_num)
        self.interpreter.monte_carlo.create_data()
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise('simplex', scaling=False, constraints=False)
        self.interpreter.monte_carlo.error_analysis()

        # Save the relaxation rates.
        self.interpreter.value.write(param='rx', file=self.file_root+'.out', dir=self.results_dir, force=True)

        # Save the results.
        self.interpreter.results.write(file='results', dir=self.results_dir, force=True)

        # Create Grace plots of the data.
        self.interpreter.grace.write(y_data_type='chi2', file='chi2.agr', dir=self.grace_dir, force=True)    # Minimised chi-squared value.
        self.interpreter.grace.write(y_data_type='i0', file='i0.agr', dir=self.grace_dir, force=True)    # Initial peak intensity.
        self.interpreter.grace.write(y_data_type='rx', file=self.file_root+'.agr', dir=self.grace_dir, force=True)    # Relaxation rate.
        self.interpreter.grace.write(x_data_type='relax_times', y_data_type='int', file='intensities.agr', dir=self.grace_dir, force=True)    # Average peak intensities.
        self.interpreter.grace.write(x_data_type='relax_times', y_data_type='int', norm=True, file='intensities_norm.agr', dir=self.grace_dir, force=True)    # Average peak intensities (normalised).

        # Display the Grace plots if selected.
        if self.view_plots:
            self.interpreter.grace.view(file='chi2.agr', dir=self.grace_dir)
            self.interpreter.grace.view(file='i0.agr', dir=self.grace_dir)
            self.interpreter.grace.view(file=self.file_root+'.agr', dir=self.grace_dir)
            self.interpreter.grace.view(file='intensities.agr', dir=self.grace_dir)
            self.interpreter.grace.view(file='intensities_norm.agr', dir=self.grace_dir)

        # Save the program state.
        self.interpreter.state.save(state=self.file_root+'.save', dir=self.results_dir, force=True)


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # The pipe name.
        if not has_pipe(self.pipe_name):
            raise RelaxNoPipeError(self.pipe_name)
