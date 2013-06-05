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
from lib.list import unique_elements
from lib.text.sectioning import title, subtitle
from pipe_control.pipes import has_pipe
from prompt.interpreter import Interpreter
from specific_analyses.relax_disp.disp_data import loop_frq
from specific_analyses.relax_disp.variables import CPMG_EXP, FIXED_TIME_EXP, MODEL_CR72, MODEL_LM63, MODEL_R2EFF
from status import Status; status = Status()


class Relax_disp:
    """The relaxation dispersion auto-analysis."""

    # Some class variables.
    opt_func_tol = 1e-25
    opt_max_iterations = int(1e7)

    def __init__(self, pipe_name=None, pipe_bundle=None, results_dir=None, models=[MODEL_R2EFF], grid_inc=11, mc_sim_num=500, bootstrap_sim_num=100000):
        """Perform a full relaxation dispersion analysis for the given list of models.

        @keyword pipe_name:         The name of the data pipe containing all of the data for the analysis.
        @type pipe_name:            str
        @keyword pipe_bundle:       The data pipe bundle to associate all spawned data pipes with.
        @type pipe_bundle:          str
        @keyword results_dir:       The directory where results files are saved.
        @type results_dir:          str
        @keyword models:            The list of relaxation dispersion models to optimise.
        @type models:               list of str
        @keyword grid_inc:          Number of grid search increments.
        @type grid_inc:             int
        @keyword mc_sim_num:        The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_sim_num:           int
        @keyword bootstrap_sim_num: The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type bootstrap_sim_num:    int
        """

        # Printout.
        title(file=sys.stdout, text="Relaxation dispersion auto-analysis", prespace=4)

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
        self.bootstrap_sim_num = bootstrap_sim_num

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


    def error_analysis(self):
        """Perform an error analysis of the peak intensities for each field strength separately."""

        # Loop over the spectrometer frequencies.
        for frq in loop_frq():
            # Generate a list of spectrum IDs matching the frequency.
            ids = []
            for id in cdp.spectrum_ids:
                # Check that the spectrometer frequency matches.
                match_frq = True
                if frq != None and cdp.spectrometer_frq[id] != frq:
                    match_frq = False

                # Add the ID.
                if match_frq:
                    ids.append(id)

            # Run the error analysis on the subset.
            self.interpreter.spectrum.error_analysis(subset=ids)


    def optimise(self):
        """Optimise the model."""

        # Grid search.
        self.interpreter.grid_search(inc=self.grid_inc)

        # Minimise.
        self.interpreter.minimise('simplex', func_tol=self.opt_func_tol, max_iter=self.opt_max_iterations, constraints=True)

        # Monte Carlo simulations.
        self.interpreter.monte_carlo.setup(number=self.mc_sim_num)
        self.interpreter.monte_carlo.create_data()
        self.interpreter.monte_carlo.initial_values()
        self.interpreter.minimise('simplex', func_tol=self.opt_func_tol, max_iter=self.opt_max_iterations, constraints=True)
        self.interpreter.monte_carlo.error_analysis()


    def run(self):
        """Execute the auto-analysis."""

        # Peak intensity error analysis.
        self.error_analysis()

        # Loop over the models.
        model_pipes = []
        for model in self.models:
            # Printout.
            subtitle(file=sys.stdout, text="The '%s' model" % model, prespace=3)

            # The name of the data pipe for the model.
            model_pipe = model
            if model != 'R2eff':
                model_pipes.append(model_pipe)

            # Create the data pipe by copying the base pipe, then switching to it.
            self.interpreter.pipe.copy(pipe_from=self.pipe_name, pipe_to=model_pipe, bundle_to=self.pipe_bundle)
            self.interpreter.pipe.switch(model_pipe)

            # Select the model.
            self.interpreter.relax_disp.select_model(model)

            # Copy the R2eff values from R2eff model data pipe.
            if model != MODEL_R2EFF:
                self.interpreter.value.copy(pipe_from=MODEL_R2EFF, pipe_to=model, param='r2eff')

            # Calculate the R2eff values for the fixed relaxation time period data types.
            if model == MODEL_R2EFF and cdp.exp_type in FIXED_TIME_EXP:
                # Set up the simulation number.
                self.interpreter.relax_disp.r2eff_setup(sim_num=self.bootstrap_sim_num)

                # Calculate the values.
                self.interpreter.calc()

            # Optimise the model.
            else:
                self.optimise()

            # Write out the results.
            self.write_results(path=self.results_dir+sep+model)

        # Perform model selection.
        self.interpreter.model_selection(method='AIC', modsel_pipe='final', pipes=model_pipes)

        # Write out the final results.
        self.write_results(path=self.results_dir+sep+'final')


    def write_results(self, path=None):
        """Create a set of results, text and Grace files for the current data pipe.

        @keyword path:  The directory to place the files into.
        @type path:     str
        """

        # Save the results.
        self.interpreter.results.write(file='results', dir=path, force=True)

        # Exponential curves.
        if cdp.model == MODEL_R2EFF and cdp.exp_type not in FIXED_TIME_EXP:
            self.interpreter.relax_disp.plot_exp_curves(file='intensities.agr', dir=path, force=True)    # Average peak intensities.
            self.interpreter.relax_disp.plot_exp_curves(file='intensities_norm.agr', dir=path, force=True, norm=True)    # Average peak intensities (normalised).

        # Dispersion curves.
        self.interpreter.relax_disp.plot_disp_curves(dir=path, force=True)

        # The R2eff parameter.
        if cdp.model == MODEL_R2EFF:
            self.interpreter.value.write(param='r2eff', file='r2eff.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='r2eff', file='r2eff.agr', dir=path, force=True)

        # The I0 parameter.
        if cdp.model == MODEL_R2EFF and cdp.exp_type not in FIXED_TIME_EXP:
            self.interpreter.value.write(param='i0', file='i0.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='i0', file='i0.agr', dir=path, force=True)

        # The Phi_ex parameter.
        if cdp.model in [MODEL_LM63]:
            self.interpreter.value.write(param='phi_ex', file='phi_ex.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='phi_ex', file='phi_ex.agr', dir=path, force=True)

        # Minimisation statistics.
        if not (cdp.model == MODEL_R2EFF and cdp.exp_type in FIXED_TIME_EXP):
            self.interpreter.grace.write(y_data_type='chi2', file='chi2.agr', dir=path, force=True)
