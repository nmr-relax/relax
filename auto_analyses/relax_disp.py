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
from specific_analyses.relax_disp import CPMG_EXP, FIXED_TIME_EXP
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


    def error_analysis(self):
        """Perform an error analysis of the peak intensities.

        The error analysis is separated into subsets for each spectrometer frequency and dispersion point.
        """

        # The number of spectrometer field strengths.
        frqs = [None]
        if hasattr(cdp, 'frq'):
            frqs = unique_elements(cdp.frq.values())
            frqs.sort()

        # Dispersion points.
        if cdp.exp_type in CPMG_EXP:
            disp_points = cdp.cpmg_frqs
        else:
            disp_points = cdp.spin_lock_nu1
        fields = unique_elements(disp_points.values())
        fields.sort()

        # Fixed relaxation time periods.
        if cdp.exp_type in FIXED_TIME_EXP:
            fields = [None]

        # Loop over the spectrometer frequencies, then the dispersion points.
        for frq in frqs:
            for field in fields:
                # Generate a list of spectrum IDs matching the frequency and field.
                ids = []
                for id in cdp.spectrum_ids:
                    # Check that the spectrometer frequency matches.
                    match_frq = True
                    if frq != None and cdp.frq[id] != frq:
                        match_frq = False

                    # Check that the dispersion point matches.
                    match_disp_point = True
                    if field != None and disp_points[id] != field:
                        match_disp_point = False

                    # Add the ID.
                    if match_frq and match_disp_point:
                        ids.append(id)

                # Run the error analysis on the subset.
                self.interpreter.spectrum.error_analysis(subset=ids)


    def optimise(self):
        """Optimise the model."""

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


    def run(self):
        """Execute the auto-analysis."""

        # Peak intensity error analysis.
        self.error_analysis()

        # Loop over the models.
        for model in self.models:
            # Printout.
            subtitle(file=sys.stdout, text="The '%s' model" % model)

            # Create the data pipe by copying the base pipe.
            self.interpreter.pipe.copy(pipe_from=self.pipe_name, pipe_to=model, bundle_to=self.pipe_bundle)

            # Select the model.
            self.interpreter.relax_disp.select_model(model)

            # Calculate the R2eff values for the fixed relaxation time period data types.
            if model == 'R2eff' and cdp.exp_type in ['cpmg fixed']:
                self.interpreter.calc()

            # Optimise the model.
            else:
                self.optimise()

            # Write out the results.
            self.write_results(path=self.results_dir+sep+model)


    def write_results(self, path=None):
        """Create a set of results, text and Grace files for the current data pipe.

        @keyword path:  The directory to place the files into.
        @type path:     str
        """

        # Save the results.
        self.interpreter.results.write(file='results', dir=path, force=True)

        # Save the relaxation dispersion parameters.
        if cdp.model not in ['exp_fit']:
            self.interpreter.value.write(param='rex', file='Rex.out', dir=path, force=True)

        # Create Grace plots of the data.
        self.interpreter.grace.write(y_data_type='chi2', file='chi2.agr', dir=path, force=True)
        self.interpreter.grace.write(x_data_type='res_num', y_data_type='r2eff', file='R2eff.agr', dir=path, force=True)
        self.interpreter.grace.write(x_data_type='res_num', y_data_type='i0', file='I0.agr', dir=path, force=True)
        if hasattr(cdp, 'spin_lock_nu1'):
            self.interpreter.grace.write(x_data_type='spin_lock_nu1', y_data_type='r2eff', file='dispersion_curves.agr', dir=path, force=True)
        elif hasattr(cdp, 'cpmg_frq'):
            self.interpreter.grace.write(x_data_type='cpmg_frq', y_data_type='r2eff', file='dispersion_curves.agr', dir=path, force=True)
        if cdp.model not in ['exp_fit']:
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='rex', file='Rex.agr', dir=path, force=True)

        # Special Grace plots.
        self.interpreter.relax_disp.plot_exp_curves(file='intensities.agr', dir=path, force=True)    # Average peak intensities.
        self.interpreter.relax_disp.plot_exp_curves(file='intensities_norm.agr', dir=path, force=True, norm=True)    # Average peak intensities (normalised).
