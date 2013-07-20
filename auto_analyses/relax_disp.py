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
from copy import deepcopy
from os import F_OK, access, getcwd, sep
import sys
from warnings import warn

# relax module imports.
from lib.list import unique_elements
from lib.text.sectioning import title, subtitle
from lib.warnings import RelaxWarning
from pipe_control.mol_res_spin import return_spin, spin_loop
from pipe_control.pipes import has_pipe
from prompt.interpreter import Interpreter
from specific_analyses.relax_disp.disp_data import loop_frq
from specific_analyses.relax_disp.variables import CPMG_EXP, FIXED_TIME_EXP, MODEL_CR72, MODEL_CR72_FULL, MODEL_DPL94, MODEL_IT99, MODEL_LIST_CPMG, MODEL_LIST_R1RHO, MODEL_LM63, MODEL_LM63_3SITE, MODEL_M61, MODEL_M61B, MODEL_NS_2SITE_3D, MODEL_NS_2SITE_3D_FULL, MODEL_NS_2SITE_EXPANDED, MODEL_NS_2SITE_STAR, MODEL_NS_2SITE_STAR_FULL, MODEL_R2EFF, R1RHO_EXP
from status import Status; status = Status()


class Relax_disp:
    """The relaxation dispersion auto-analysis."""

    # Some class variables.
    opt_func_tol = 1e-25
    opt_max_iterations = int(1e7)

    def __init__(self, pipe_name=None, pipe_bundle=None, results_dir=None, models=[MODEL_R2EFF], grid_inc=11, mc_sim_num=500, modsel='AIC', mc_sim_all_models=False):
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
        @keyword modsel:            The model selection technique to use in the analysis to determine which model is the best for each spin cluster.  This can currently be one of 'AIC', 'AICc', and 'BIC'.
        @type modsel:               str
        @keyword mc_sim_all_models: A flag which if True will cause Monte Carlo simulations to be performed for each individual model.  Otherwise Monte Carlo simulations will be reserved for the final model.
        @type mc_sim_all_models:    bool
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
        self.modsel = modsel
        self.mc_sim_all_models = mc_sim_all_models

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

        # Check the model selection.
        allowed = ['AIC', 'AICc', 'BIC']
        if self.modsel not in allowed:
            raise RelaxError("The model selection technique '%s' is not in the allowed list of %s." % (self.modsel, allowed))


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


    def nesting(self, model=None):
        """Support for model nesting.

        If model nesting is detected, the optimised parameters from the simpler model will be used for the more complex model.  The method will then signal if the nesting condition is met for the model, allowing the grid search to be skipped.


        @keyword model: The model to be optimised.
        @type model:    str
        @return:        True if the model is the more complex model in a nested pair and the parameters of the simpler model have been copied.  False otherwise.
        @rtype:         bool
        """

        # The simpler model.
        nested_pipe = None
        if model == MODEL_CR72_FULL and MODEL_CR72 in self.models:
            nested_pipe = MODEL_CR72
        if model == MODEL_NS_2SITE_3D_FULL and MODEL_NS_2SITE_3D in self.models:
            nested_pipe = MODEL_NS_2SITE_3D
        if model == MODEL_NS_2SITE_STAR_FULL and MODEL_NS_2SITE_STAR in self.models:
            nested_pipe = MODEL_NS_2SITE_STAR

        # No nesting.
        if not nested_pipe:
            return False

        # Printout.
        print("Model nesting detected, copying the optimised parameters from the '%s' model rather than performing a grid search." % nested_pipe)

        # Loop over the spins to copy the parameters.
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            # Get the nested spin.
            nested_spin = return_spin(spin_id=spin_id, pipe=nested_pipe)

            # The R20 parameters.
            if hasattr(nested_spin, 'r2'):
                setattr(spin, 'r2a', deepcopy(nested_spin.r2))
                setattr(spin, 'r2b', deepcopy(nested_spin.r2))

            # All other spin parameters.
            for param in spin.params:
                if param in ['r2', 'r2a', 'r2b']:
                    continue

                # Copy the parameter.
                setattr(spin, param, deepcopy(getattr(nested_spin, param)))

        # Nesting.
        return True


    def optimise(self, model=None):
        """Optimise the model, taking model nesting into account.

        @keyword model: The model to be optimised.
        @type model:    str
        """

        # Nested model simplification.
        nested = self.nesting(model=model)

        # Grid search.
        if not nested:
            self.interpreter.grid_search(inc=self.grid_inc)

        # Minimise.
        self.interpreter.minimise('simplex', func_tol=self.opt_func_tol, max_iter=self.opt_max_iterations, constraints=True)

        # Monte Carlo simulations.
        if self.mc_sim_all_models or len(self.model_pipes) < 2:
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
        self.model_pipes = []
        for model in self.models:
            # Printout.
            subtitle(file=sys.stdout, text="The '%s' model" % model, prespace=3)

            # The results directory path.
            path = self.results_dir+sep+model

            # The name of the data pipe for the model.
            model_pipe = model
            if model != 'R2eff':
                self.model_pipes.append(model_pipe)

            # Check that results do not already exist - i.e. a previous run was interrupted.
            path1 = path + sep + 'results'
            path2 = path1 + '.bz2'
            path3 = path1 + '.gz'
            if access(path1, F_OK) or access(path2, F_OK) or access(path2, F_OK):
                # Printout.
                print("Detected the presence of results files for the '%s' model - loading these instead of performing optimisation for a second time." % model)

                # Create a data pipe and switch to it.
                self.interpreter.pipe.create(pipe_name=model_pipe, pipe_type='relax_disp', bundle=self.pipe_bundle)
                self.interpreter.pipe.switch(model_pipe)

                # Load the results.
                self.interpreter.results.read(file='results', dir=path)

                # Jump to the next model.
                continue

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
                self.interpreter.calc()

            # Optimise the model.
            else:
                self.optimise(model=model)

            # Write out the results.
            self.write_results(path=path, model=model)

        # The final model selection data pipe.
        if len(self.model_pipes) >= 2:
            # Perform model selection.
            self.interpreter.model_selection(method=self.modsel, modsel_pipe='final', pipes=self.model_pipes)

            # Final Monte Carlo simulations only.
            if not self.mc_sim_all_models:
                self.interpreter.monte_carlo.setup(number=self.mc_sim_num)
                self.interpreter.monte_carlo.create_data()
                self.interpreter.monte_carlo.initial_values()
                self.interpreter.minimise('simplex', func_tol=self.opt_func_tol, max_iter=self.opt_max_iterations, constraints=True)
                self.interpreter.monte_carlo.error_analysis()

            # Writing out the final results.
            self.write_results(path=self.results_dir+sep+'final')

        # No model selection.
        else:
            warn(RelaxWarning("Model selection in the dispersion auto-analysis has been skipped as only %s models have been optimised." % len(self.model_pipes)))

        # Finally save the program state.
        self.interpreter.state.save(state='final_state', dir=self.results_dir, force=True)


    def write_results(self, path=None, model=None):
        """Create a set of results, text and Grace files for the current data pipe.

        @keyword path:  The directory to place the files into.
        @type path:     str
        """

        # Exponential curves.
        if model == 'R2eff' and cdp.exp_type not in FIXED_TIME_EXP:
            self.interpreter.relax_disp.plot_exp_curves(file='intensities.agr', dir=path, force=True)    # Average peak intensities.
            self.interpreter.relax_disp.plot_exp_curves(file='intensities_norm.agr', dir=path, force=True, norm=True)    # Average peak intensities (normalised).

        # Dispersion curves.
        self.interpreter.relax_disp.plot_disp_curves(dir=path, force=True)

        # The R2eff parameter.
        if model == 'R2eff':
            self.interpreter.value.write(param='r2eff', file='r2eff.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='r2eff', file='r2eff.agr', dir=path, force=True)

        # The I0 parameter.
        if model == 'R2eff' and cdp.exp_type not in FIXED_TIME_EXP:
            self.interpreter.value.write(param='i0', file='i0.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='i0', file='i0.agr', dir=path, force=True)

        ## The R20 parameter.
        #if cdp.exp_type in CPMG_EXP and model in [None, MODEL_LM63, MODEL_CR72, MODEL_IT99, MODEL_M61, MODEL_DPL94, MODEL_M61B, MODEL_NS_2SITE_3D, MODEL_NS_2SITE_STAR, MODEL_NS_2SITE_EXPANDED]:
        #    self.interpreter.value.write(param='r2', file='r20.out', dir=path, force=True)
        #    self.interpreter.grace.write(x_data_type='res_num', y_data_type='r2', file='r20.agr', dir=path, force=True)

        ## The R20A and R20B parameters.
        #if cdp.exp_type in CPMG_EXP and model in [None, MODEL_CR72_FULL, MODEL_NS_2SITE_3D_FULL, MODEL_NS_2SITE_STAR_FULL]:
        #    self.interpreter.value.write(param='r2a', file='r20a.out', dir=path, force=True)
        #    self.interpreter.value.write(param='r2b', file='r20b.out', dir=path, force=True)
        #    self.interpreter.grace.write(x_data_type='res_num', y_data_type='r2a', file='r20a.agr', dir=path, force=True)
        #    self.interpreter.grace.write(x_data_type='res_num', y_data_type='r2b', file='r20b.agr', dir=path, force=True)

        ## The R1rho parameter.
        #if cdp.exp_type in R1RHO_EXP and model in [None] + MODEL_LIST_R1RHO:
        #    self.interpreter.value.write(param='r2', file='r1rho0.out', dir=path, force=True)
        #    self.interpreter.grace.write(x_data_type='res_num', y_data_type='r2', file='r1rho0.agr', dir=path, force=True)

        # The pA and pB parameters.
        if model in [None, MODEL_CR72, MODEL_CR72_FULL, MODEL_M61B, MODEL_NS_2SITE_3D, MODEL_NS_2SITE_3D_FULL, MODEL_NS_2SITE_STAR, MODEL_NS_2SITE_STAR_FULL, MODEL_NS_2SITE_EXPANDED]:
            self.interpreter.value.write(param='pA', file='pA.out', dir=path, force=True)
            self.interpreter.value.write(param='pB', file='pB.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='pA', file='pA.agr', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='pB', file='pB.agr', dir=path, force=True)

        # The Phi_ex parameter.
        if model in [None, MODEL_LM63, MODEL_IT99, MODEL_M61, MODEL_DPL94]:
            self.interpreter.value.write(param='phi_ex', file='phi_ex.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='phi_ex', file='phi_ex.agr', dir=path, force=True)

        # The Phi_ex_B nd Phi_ex_C parameters.
        if model in [None, MODEL_LM63_3SITE]:
            self.interpreter.value.write(param='phi_ex_B', file='phi_ex_B.out', dir=path, force=True)
            self.interpreter.value.write(param='phi_ex_C', file='phi_ex_C.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='phi_ex_B', file='phi_ex_B.agr', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='phi_ex_C', file='phi_ex_C.agr', dir=path, force=True)

        # The padw2 parameter.
        if model in [None, MODEL_IT99]:
            self.interpreter.value.write(param='padw2', file='padw2.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='padw2', file='padw2.agr', dir=path, force=True)

        # The dw parameter.
        if model in [None, MODEL_CR72, MODEL_CR72_FULL, MODEL_M61B, MODEL_NS_2SITE_3D, MODEL_NS_2SITE_3D_FULL, MODEL_NS_2SITE_STAR, MODEL_NS_2SITE_STAR_FULL, MODEL_NS_2SITE_EXPANDED]:
            self.interpreter.value.write(param='dw', file='dw.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='dw', file='dw.agr', dir=path, force=True)

        # The kex and tex parameters.
        if model in [None, MODEL_LM63, MODEL_CR72, MODEL_CR72_FULL, MODEL_IT99, MODEL_M61, MODEL_DPL94, MODEL_M61B, MODEL_NS_2SITE_3D, MODEL_NS_2SITE_3D_FULL, MODEL_NS_2SITE_STAR, MODEL_NS_2SITE_STAR_FULL, MODEL_NS_2SITE_EXPANDED]:
            self.interpreter.value.write(param='kex', file='kex.out', dir=path, force=True)
            self.interpreter.value.write(param='tex', file='tex.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='kex', file='kex.agr', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='tex', file='tex.agr', dir=path, force=True)

        # The kB and kC parameters.
        if model in [None, MODEL_LM63_3SITE]:
            self.interpreter.value.write(param='kB', file='kB.out', dir=path, force=True)
            self.interpreter.value.write(param='kC', file='kC.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='kB', file='kB.agr', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='kC', file='kC.agr', dir=path, force=True)

        # Minimisation statistics.
        if not (model == 'R2eff' and cdp.exp_type in FIXED_TIME_EXP):
            self.interpreter.grace.write(y_data_type='chi2', file='chi2.agr', dir=path, force=True)

        # Finally save the results.  This is last to allow the continuation of an interrupted analysis while ensuring that all results files have been created.
        self.interpreter.results.write(file='results', dir=path, force=True)

