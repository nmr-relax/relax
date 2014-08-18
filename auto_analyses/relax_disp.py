###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
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
from numpy import version
import sys
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxFileError, RelaxNoPipeError
from lib.io import determine_compression, get_file_path
from lib.text.sectioning import section, subsection, subtitle, title
from lib.warnings import RelaxWarning
from pipe_control.mol_res_spin import return_spin, spin_loop
from pipe_control.pipes import has_pipe
from prompt.interpreter import Interpreter
from specific_analyses.relax_disp.data import has_exponential_exp_type, has_cpmg_exp_type, has_fixed_time_exp_type, has_r1rho_exp_type, loop_frq
from specific_analyses.relax_disp.data import INTERPOLATE_DISP, INTERPOLATE_OFFSET, X_AXIS_DISP, X_AXIS_W_EFF, X_AXIS_THETA, Y_AXIS_R2_R1RHO, Y_AXIS_R2_EFF
from specific_analyses.relax_disp.model import nesting_model
from specific_analyses.relax_disp.variables import EQ_ANALYTIC, EQ_NUMERIC, EQ_SILICO, MODEL_LIST_ANALYTIC, MODEL_LIST_NEST, MODEL_LIST_NUMERIC, MODEL_LIST_R1RHO_FIT_R1, MODEL_LIST_R1RHO_W_R1, MODEL_LIST_R1RHO_FULL, MODEL_NOREX, MODEL_NOREX_R1RHO, MODEL_NOREX_R1RHO_FIT_R1, MODEL_PARAMS, MODEL_R2EFF, PARAMS_R20
from status import Status; status = Status()


class Relax_disp:
    """The relaxation dispersion auto-analysis."""

    # Some class variables.
    opt_func_tol = 1e-25
    opt_max_iterations = int(1e7)

    def __init__(self, pipe_name=None, pipe_bundle=None, results_dir=None, models=[MODEL_R2EFF], grid_inc=11, mc_sim_num=500, exp_mc_sim_num=None, modsel='AIC', pre_run_dir=None, optimise_pre_run_r2eff=True, insignificance=0.0, numeric_only=False, mc_sim_all_models=False, eliminate=True, set_grid_r20=False):
        """Perform a full relaxation dispersion analysis for the given list of models.

        @keyword pipe_name:                 The name of the data pipe containing all of the data for the analysis.
        @type pipe_name:                    str
        @keyword pipe_bundle:               The data pipe bundle to associate all spawned data pipes with.
        @type pipe_bundle:                  str
        @keyword results_dir:               The directory where results files are saved.
        @type results_dir:                  str
        @keyword models:                    The list of relaxation dispersion models to optimise.
        @type models:                       list of str
        @keyword grid_inc:                  Number of grid search increments.  If set to None, then the grid search will be turned off and the default parameter values will be used instead.
        @type grid_inc:                     int or None
        @keyword mc_sim_num:                The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_sim_num:                   int
        @keyword exp_mc_sim_num:            The number of Monte Carlo simulations for the error analysis in the 'R2eff' model when exponential curves are fitted.  This defaults to the value of the mc_sim_num argument when not given.  For the 2-point fixed-time calculation for the 'R2eff' model, this argument is ignored.
        @type exp_mc_sim_num:               int or None
        @keyword modsel:                    The model selection technique to use in the analysis to determine which model is the best for each spin cluster.  This can currently be one of 'AIC', 'AICc', and 'BIC'.
        @type modsel:                       str
        @keyword pre_run_dir:               The optional directory containing the dispersion auto-analysis results from a previous run.  The optimised parameters from these previous results will be used as the starting point for optimisation rather than performing a grid search.  This is essential for when large spin clusters are specified, as a grid search becomes prohibitively expensive with clusters of three or more spins.  At some point a RelaxError will occur because the grid search is impossibly large.  For the cluster specific parameters, i.e. the populations of the states and the exchange parameters, an average value will be used as the starting point.  For all other parameters, the R20 values for each spin and magnetic field, as well as the parameters related to the chemical shift difference dw, the optimised values of the previous run will be directly copied.
        @type pre_run_dir:                  None or str
        @keyword optimise_pre_run_r2eff:    Flag to specify if the read previous R2eff results should be optimised.  For R1rho models where the error of R2eff values are determined by Monte-Carlo simulations, it can be valuable to make an initial R2eff run with a high number of Monte-Carlo simulations.  Any subsequent model analysis can then be based on these R2eff values, without optimising the R2eff values. 
        @type optimise_pre_run_r2eff:       bool
        @keyword insignificance:            The R2eff/R1rho value in rad/s by which to judge insignificance.  If the maximum difference between two points on all dispersion curves for a spin is less than this value, that spin will be deselected.  This does not affect the 'No Rex' model.  Set this value to 0.0 to use all data.  The value will be passed on to the relax_disp.insignificance user function.
        @type insignificance:               float
        @keyword numeric_only:              The class of models to use in the model selection.  The default of False allows all dispersion models to be used in the analysis (no exchange, the analytic models and the numeric models).  The value of True will activate a pure numeric solution - the analytic models will be optimised, as they are very useful for replacing the grid search for the numeric models, but the final model selection will not include them.
        @type numeric_only:                 bool
        @keyword mc_sim_all_models:         A flag which if True will cause Monte Carlo simulations to be performed for each individual model.  Otherwise Monte Carlo simulations will be reserved for the final model.
        @type mc_sim_all_models:            bool
        @keyword eliminate:                 A flag which if True will enable the elimination of failed models and failed Monte Carlo simulations through the eliminate user function.
        @type eliminate:                    bool
        @keyword set_grid_r20:              A flag which if True will set the grid R20 values from the minimum R2eff values through the r20_from_min_r2eff user function. This will speed up the grid search with a factor GRID_INC^(Nr_spec_freq). For a CPMG experiment with two fields and standard GRID_INC=21, the speed-up is a factor 441.
        @type set_grid_r20:                 bool
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
        self.exp_mc_sim_num = exp_mc_sim_num
        self.modsel = modsel
        self.pre_run_dir = pre_run_dir
        self.optimise_pre_run_r2eff = optimise_pre_run_r2eff
        self.insignificance = insignificance
        self.set_grid_r20 = set_grid_r20
        self.numeric_only = numeric_only
        self.mc_sim_all_models = mc_sim_all_models
        self.eliminate = eliminate

        # No results directory, so default to the current directory.
        if not self.results_dir:
            self.results_dir = getcwd()

        # Data checks.
        self.check_vars()

        # Check for numerical model using numpy version under 1.8.
        # This will result in slow "for loop" calculation through data, making the analysis 5-6 times slower.
        self.check_numpy_less_1_8_and_numerical_model()

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Execute.
        try:
            self.run()

        # Finish and unlock execution.
        finally:
            status.auto_analysis[self.pipe_bundle].fin = True
            status.current_analysis = None
            status.exec_lock.release()


    def is_model_for_selection(self, model=None):
        """Determine if the model should be used for model selection.

        @keyword model: The model to check.
        @type model:    str
        @return:        True if the model should be included in the model selection list, False if not.
        @rtype:         bool
        """

        # Skip the 'R2eff' base model.
        if model == MODEL_R2EFF:
            return False

        # Do not use the analytic models.
        if self.numeric_only and model in MODEL_LIST_ANALYTIC:
            return False

        # All models allowed.
        return True


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # Printout.
        section(file=sys.stdout, text="Variable checking", prespace=2)

        # The pipe name.
        if not has_pipe(self.pipe_name):
            raise RelaxNoPipeError(self.pipe_name)

        # Check the model selection.
        allowed = ['AIC', 'AICc', 'BIC']
        if self.modsel not in allowed:
            raise RelaxError("The model selection technique '%s' is not in the allowed list of %s." % (self.modsel, allowed))

        # Some warning for the user if the pure numeric solution is selected.
        if self.numeric_only:
            # Loop over all models.
            for model in self.models:
                # Skip the models used for nesting.
                if model in MODEL_LIST_NEST:
                    continue

                # Warnings for all other analytic models.
                if model in MODEL_LIST_ANALYTIC:
                    warn(RelaxWarning("The analytic model '%s' will be optimised but will not be used in any way in this numeric model only auto-analysis." % model))

        # Printout.
        print("The dispersion auto-analysis variables are OK.")


    def check_numpy_less_1_8_and_numerical_model(self):
        """Check for numerical model using numpy version under 1.8.  This will result in slow "for loop" calculation through data, making the analysis 5-6 times slower."""

        # Some warning for the user if the pure numeric solution is selected.
        if float(version.version[:3]) < 1.8:
            # Store which models are in numeric.
            models = []

            # Loop through models.
            for model in self.models:
                if model in MODEL_LIST_NUMERIC:
                    models.append(model)

            # Write system message if numerical models is present and numpy version is below 1.8.
            if len(models) > 0:
                # Printout.
                section(file=sys.stdout, text="Numpy version checking for numerical models.", prespace=2)
                warn(RelaxWarning("Your version of numpy is %s, and below the recommended version of 1.8 for numerical models." % (version.version)))
                warn(RelaxWarning("Please consider upgrading your numpy version to 1.8."))

                # Loop over models.
                for model in models:
                    warn(RelaxWarning("This could make the numerical analysis with model '%s', 5 to 6 times slower." % (model)))


    def error_analysis(self):
        """Perform an error analysis of the peak intensities for each field strength separately."""

        # Printout.
        section(file=sys.stdout, text="Error analysis", prespace=2)

        # Check if intensity errors have already been calculated by the user.
        precalc = True
        for spin in spin_loop(skip_desel=True):
            # No structure.
            if not hasattr(spin, 'peak_intensity_err'):
                precalc = False
                break

            # Determine if a spectrum ID is missing from the list.
            for id in cdp.spectrum_ids:
                if id not in spin.peak_intensity_err:
                    precalc = False
                    break

        # Skip.
        if precalc:
            print("Skipping the error analysis as it has already been performed.")
            return

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


    def name_pipe(self, prefix):
        """Generate a unique name for the data pipe.

        @param prefix:  The prefix of the data pipe name.
        @type prefix:   str
        """

        # The unique pipe name.
        name = "%s - %s" % (prefix, self.pipe_bundle)

        # Return the name.
        return name


    def nesting(self, model=None):
        """Support for model nesting.

        If model nesting is detected, the optimised parameters from the simpler model will be used for the more complex model.  The method will then signal if the nesting condition is met for the model, allowing the grid search to be skipped.


        @keyword model: The model to be optimised.
        @type model:    str
        @return:        True if the model is the more complex model in a nested pair and the parameters of the simpler model have been copied.  False otherwise.
        @return:        True if the model parameters is equivalent to the nested model, and all parameters are copied.  False if none or some of the parameters have been translated from the nested model.  Here the Grid search should still be performed.
        @rtype:         bool
        """

        # Printout. 
        subsection(file=sys.stdout, text="Nesting and model equivalence checks", prespace=1)

        # The simpler model.
        model_info, comparable_model_info = nesting_model(self_models=self.models, model=model)
        if comparable_model_info != None:
            nested_pipe = self.name_pipe(comparable_model_info.model)
        else:
            nested_pipe = None

        # No nesting.
        if not nested_pipe:
            print("No model nesting or model equivalence detected.")
            return False

        # Copying the parameters to a numerical model from an analytic solution.
        if model_info.eq in [EQ_NUMERIC, EQ_SILICO] and comparable_model_info.eq == EQ_ANALYTIC:
            analytic = True
        else:
            analytic = False

        # Determine if model is equivalent or nested.
        if model_info.params == comparable_model_info.params:
            equivalent = True
        else:
            equivalent = False

        # Printout.
        if equivalent:
            print("Model equivalence detected, copying the optimised parameters from the '%s' model rather than performing a grid search." % comparable_model_info.model)
        else:
            print("Model nesting detected, translating the optimised parameters %s from the '%s' model to the parameters %s of model '%s'.  A grid search is issued for the remaining parameters." % (comparable_model_info.params, comparable_model_info.model, model_info.params, model))
        if analytic:
            print("The parameters are copied from a %s model to a %s model." % (comparable_model_info.eq, model_info.eq))

        # Loop over the parameters in comparable model.
        for param in comparable_model_info.params:
            # The R20 parameters.
            if param in PARAMS_R20:
                # If both models have same parameter.
                if param in model_info.params:
                    print("Copying %s." % param)
                    # Loop over the spins to copy the parameters.
                    for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
                        # Get the nested spin.
                        nested_spin = return_spin(spin_id=spin_id, pipe=nested_pipe)
                        setattr(spin, param, deepcopy(getattr(nested_spin, param)))

                # If copying from a simple model to a complex model
                elif param == 'r2' and 'r2a' in model_info.params and 'r2b' in model_info.params:
                    print("Copying %s, to r2a and r2b." % param)
                    # Loop over the spins to copy the parameters.
                    for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
                        # Get the nested spin.
                        nested_spin = return_spin(spin_id=spin_id, pipe=nested_pipe)
                        setattr(spin, 'r2a', deepcopy(getattr(nested_spin, 'r2')))
                        setattr(spin, 'r2b', deepcopy(getattr(nested_spin, 'r2')))

                # If copying from a complex model to a lower complex model
                elif param == 'r2a' and 'r2' in model_info.params:
                    print("Copying %s, to r2." % param)
                    # Loop over the spins to copy the parameters.
                    for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
                        # Get the nested spin.
                        nested_spin = return_spin(spin_id=spin_id, pipe=nested_pipe)
                        setattr(spin, 'r2', deepcopy(getattr(nested_spin, 'r2a')))

            # Special case for tex/kex.
            elif param == 'tex' and 'kex' in model_info.params:
                print("Translating kex from 1/%s." % param)
                # Loop over the spins to copy the parameters.
                for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
                    # Get the nested spin.
                    nested_spin = return_spin(spin_id=spin_id, pipe=nested_pipe)
                    kex = 1.0 / getattr(nested_spin, 'tex')
                    setattr(spin, 'kex', kex)

            elif param == 'kex' and 'tex' in model_info.params:
                print("Translating tex from 1/%s." % param)
                # Loop over the spins to copy the parameters.
                for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
                    # Get the nested spin.
                    nested_spin = return_spin(spin_id=spin_id, pipe=nested_pipe)
                    tex = 1.0 / getattr(nested_spin, 'kex')
                    setattr(spin, 'tex', tex)

            # All other parameters.
            elif param in model_info.params:
                print("Copying %s." % param)
                # Loop over the spins to copy the parameters.
                for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
                    # Get the nested spin.
                    nested_spin = return_spin(spin_id=spin_id, pipe=nested_pipe)
                    setattr(spin, param, deepcopy(getattr(nested_spin, param)))

        ## Special case for phi_ex.
        if 'dw' in comparable_model_info.params and 'pA' in comparable_model_info.params and 'phi_ex' in model_info.params:
            print("Translating 'phi_ex' from 'pA * pB * dw**2'.")
            # Loop over the spins to copy the parameters.
            for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
                # Get the nested spin.
                nested_spin = return_spin(spin_id=spin_id, pipe=nested_pipe)
                dw = getattr(nested_spin, 'dw')
                pA = getattr(nested_spin, 'pA')
                pB = 1.0 - pA
                phi_ex = pA * pB * dw * dw
                setattr(spin, 'phi_ex', phi_ex)

        ## The LM63 3-site model parameters.
        if 'phi_ex' in comparable_model_info.params and 'kex' in comparable_model_info.params and 'phi_ex_B' in model_info.params and 'phi_ex_C' in model_info.params and 'kB' in model_info.params and 'kC' in model_info.params:
            print("Translating phi_ex_B=phi_ex, phi_ex_C=phi_ex, kB=kex and kC=kex.")
            # Loop over the spins to copy the parameters.
            for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
                # Get the nested spin.
                nested_spin = return_spin(spin_id=spin_id, pipe=nested_pipe)
                setattr(spin, 'phi_ex_B', deepcopy(nested_spin.phi_ex))
                setattr(spin, 'phi_ex_C', deepcopy(nested_spin.phi_ex))
                setattr(spin, 'kB', deepcopy(nested_spin.kex))
                setattr(spin, 'kC', deepcopy(nested_spin.kex))

        # Determine if model is equivalent, and should not be Grid searched, or if nested, and some parameters are pre-set. Here Grid search should still be issued.
        return equivalent


    def optimise(self, model=None):
        """Optimise the model, taking model nesting into account.

        @keyword model: The model to be optimised.
        @type model:    str
        """

        # Printout. 
        section(file=sys.stdout, text="Optimisation", prespace=2)

        # Deselect insignificant spins.
        if model not in [MODEL_R2EFF, MODEL_NOREX, MODEL_NOREX_R1RHO, MODEL_NOREX_R1RHO_FIT_R1]:
            self.interpreter.relax_disp.insignificance(level=self.insignificance)

        # Speed-up grid-search by using minium R2eff value.
        if self.set_grid_r20 and model != MODEL_R2EFF:
            self.interpreter.relax_disp.r20_from_min_r2eff(force=True)

        # Use pre-run results as the optimisation starting point.
        # Test if file exists.
        if self.pre_run_dir:
            path = self.pre_run_dir + sep + model
            # File path.
            file_path = get_file_path('results', path)

            # Test if the file exists and determine the compression type.
            try:
                compress_type, file_path = determine_compression(file_path)
                res_file_exists = True

            except RelaxFileError:
                res_file_exists = False

        if self.pre_run_dir and res_file_exists:
            self.pre_run_parameters(model=model)

        # Otherwise use the normal nesting check and grid search if not nested.
        else:
            # Nested model simplification.
            nested = self.nesting(model=model)

            # Otherwise use a grid search of default values to start optimisation with.
            if not nested:
                # Grid search.
                if self.grid_inc:
                    self.interpreter.minimise.grid_search(inc=self.grid_inc)

                # Default values.
                else:
                    for param in MODEL_PARAMS[model]:
                        self.interpreter.value.set(param=param, index=None)

        # Minimise.
        if model == MODEL_R2EFF:
            if self.optimise_pre_run_r2eff:
                self.interpreter.minimise.execute('simplex', func_tol=self.opt_func_tol, max_iter=self.opt_max_iterations, constraints=True)
            else:
                pass
        else:
            self.interpreter.minimise.execute('simplex', func_tol=self.opt_func_tol, max_iter=self.opt_max_iterations, constraints=True)


        # Model elimination.
        if self.eliminate:
            self.interpreter.eliminate()

        # Monte Carlo simulations.
        if self.mc_sim_all_models or len(self.models) < 2 or (model == MODEL_R2EFF and self.optimise_pre_run_r2eff):
            if model == MODEL_R2EFF and self.exp_mc_sim_num != None:
                self.interpreter.monte_carlo.setup(number=self.exp_mc_sim_num)
            else:
                self.interpreter.monte_carlo.setup(number=self.mc_sim_num)
            self.interpreter.monte_carlo.create_data()
            self.interpreter.monte_carlo.initial_values()
            self.interpreter.minimise.execute('simplex', func_tol=self.opt_func_tol, max_iter=self.opt_max_iterations, constraints=True)
            if self.eliminate:
                self.interpreter.eliminate()
            self.interpreter.monte_carlo.error_analysis()


    def pre_run_parameters(self, model=None):
        """Copy parameters from an earlier analysis.

        @keyword model: The model to be optimised.
        @type model:    str
        """

        # Printout.
        subsection(file=sys.stdout, text="Pre-run parameters", prespace=1)

        # The data pipe name.
        pipe_name = self.name_pipe('pre')

        # Create a temporary data pipe for the previous run.
        self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type='relax_disp')

        # Load the previous results.
        path = self.pre_run_dir + sep + model
        self.interpreter.results.read(file='results', dir=path)

        # Copy the parameters.
        self.interpreter.relax_disp.parameter_copy(pipe_from=pipe_name, pipe_to=self.name_pipe(model))

        # Finally, switch back to the original data pipe and delete the temporary one.
        self.interpreter.pipe.switch(pipe_name=self.name_pipe(model))
        self.interpreter.pipe.delete(pipe_name=pipe_name)


    def run(self):
        """Execute the auto-analysis."""

        # Peak intensity error analysis.
        if MODEL_R2EFF in self.models:
            self.error_analysis()

        # Loop over the models.
        self.model_pipes = []
        for model in self.models:
            # Printout.
            subtitle(file=sys.stdout, text="The '%s' model" % model, prespace=3)

            # The results directory path.
            path = self.results_dir+sep+model

            # The name of the data pipe for the model.
            model_pipe = self.name_pipe(model)
            if self.is_model_for_selection(model):
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

            # Copy the R2eff values from the R2eff model data pipe.
            if model != MODEL_R2EFF and MODEL_R2EFF in self.models:
                self.interpreter.value.copy(pipe_from=self.name_pipe(MODEL_R2EFF), pipe_to=model_pipe, param='r2eff')

            # Calculate the R2eff values for the fixed relaxation time period data types.
            if model == MODEL_R2EFF and not has_exponential_exp_type():
                self.interpreter.minimise.calculate()

            # Optimise the model.
            else:
                self.optimise(model=model)

            # Write out the results.
            self.write_results(path=path, model=model)

        # The final model selection data pipe.
        if len(self.models) >= 2:
            # Printout.
            section(file=sys.stdout, text="Final results", prespace=2)

            # Perform model selection.
            self.interpreter.model_selection(method=self.modsel, modsel_pipe=self.name_pipe('final'), bundle=self.pipe_bundle, pipes=self.model_pipes)

            # Final Monte Carlo simulations only.
            if not self.mc_sim_all_models:
                self.interpreter.monte_carlo.setup(number=self.mc_sim_num)
                self.interpreter.monte_carlo.create_data()
                self.interpreter.monte_carlo.initial_values()
                self.interpreter.minimise.execute('simplex', func_tol=self.opt_func_tol, max_iter=self.opt_max_iterations, constraints=True)
                if self.eliminate:
                    self.interpreter.eliminate()
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

        # Printout.
        section(file=sys.stdout, text="Results writing", prespace=2)

        # If this is the final model selection round, check which models have been tested.
        if model == None:
            models_tested = []
            for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
                spin_model = spin.model

                # Add to list, if not in already.
                if spin_model not in models_tested:
                    models_tested.append(spin_model)
        else:
            models_tested = None

        # Special for R2eff model.
        if model == MODEL_R2EFF:
            # The R2eff parameter.
            self.interpreter.value.write(param='r2eff', file='r2eff.out', dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type='r2eff', file='r2eff.agr', dir=path, force=True)

            # Exponential curves.
            if has_exponential_exp_type():
                self.interpreter.relax_disp.plot_exp_curves(file='intensities.agr', dir=path, force=True)    # Average peak intensities.
                self.interpreter.relax_disp.plot_exp_curves(file='intensities_norm.agr', dir=path, force=True, norm=True)    # Average peak intensities (normalised).

                # The I0 parameter.
                self.interpreter.value.write(param='i0', file='i0.out', dir=path, force=True)
                self.interpreter.grace.write(x_data_type='res_num', y_data_type='i0', file='i0.agr', dir=path, force=True)

        # Dispersion curves.
        self.interpreter.relax_disp.plot_disp_curves(dir=path, force=True)
        self.interpreter.relax_disp.write_disp_curves(dir=path, force=True)

        # The selected models for the final run.
        if model == None:
            self.interpreter.value.write(param='model', file='model.out', dir=path, force=True)

        # For CPMG models.
        if has_cpmg_exp_type():
            # The R20 parameter.
            self.write_results_test(path=path, model=model, models_tested=models_tested, param='r2', file_name_ini='r20')

            # The R20A and R20B parameters.
            self.write_results_test(path=path, model=model, models_tested=models_tested, param='r2a', file_name_ini='r20a')
            self.write_results_test(path=path, model=model, models_tested=models_tested, param='r2b', file_name_ini='r20b')

        # For R1ho models.
        if has_r1rho_exp_type():
            # The R1 parameter.
            self.write_results_test(path=path, model=model, models_tested=models_tested, param='r1')

            # The R1rho prime parameter.
            self.write_results_test(path=path, model=model, models_tested=models_tested, param='r2', file_name_ini='r1rho_prime')

            # Plot specific R1rho graphs.
            if model in [None] + MODEL_LIST_R1RHO_W_R1 + MODEL_LIST_R1RHO_FIT_R1:
                self.interpreter.relax_disp.plot_disp_curves(dir=path, x_axis=X_AXIS_THETA, force=True)
                self.interpreter.relax_disp.plot_disp_curves(dir=path, y_axis=Y_AXIS_R2_R1RHO, x_axis=X_AXIS_W_EFF, force=True)
                self.interpreter.relax_disp.plot_disp_curves(dir=path, y_axis=Y_AXIS_R2_EFF, x_axis=X_AXIS_THETA, interpolate=INTERPOLATE_OFFSET, force=True)

            # The calculation of theta and w_eff parameter in R1rho experiments.
            if model in MODEL_LIST_R1RHO_FULL:
                self.interpreter.value.write(param='theta', file='theta.out', dir=path, force=True)
                self.interpreter.value.write(param='w_eff', file='w_eff.out', dir=path, force=True)

        # The pA and pB parameters.
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='pA')
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='pB')

        # The pC parameter.
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='pC')

        # The phi_ex parameter.
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='phi_ex')

        # The phi_ex_B nd phi_ex_C parameters.
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='phi_ex_B')
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='phi_ex_C')

        # The dw parameter.
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='dw')

        # The dw_AB, dw_BC and dw_AC parameter.
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='dw_AB')
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='dw_BC')
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='dw_AC')

        # The dwH parameter.
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='dwH')

        # The dwH_AB, dwH_BC and dwH_AC parameter.
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='dwH_AB')
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='dwH_BC')
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='dwH_AC')

        # The k_AB, kex and tex parameters.
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='k_AB')
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='kex')
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='tex')

        # The kex_AB, kex_BC, kex_AC parameters.
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='kex_AB')
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='kex_BC')
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='kex_AC')

        # The kB and kC parameters.
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='kB')
        self.write_results_test(path=path, model=model, models_tested=models_tested, param='kC')

        # Minimisation statistics.
        if not (model == MODEL_R2EFF and has_fixed_time_exp_type()):
            self.interpreter.value.write(param='chi2', file='chi2.out', dir=path, force=True)
            self.interpreter.grace.write(y_data_type='chi2', file='chi2.agr', dir=path, force=True)

        # Finally save the results.  This is last to allow the continuation of an interrupted analysis while ensuring that all results files have been created.
        self.interpreter.results.write(file='results', dir=path, force=True)


    def write_results_test(self, path=None, model=None, models_tested=None, param=None, file_name_ini=None):
        """Create a set of results, text and Grace files for the current data pipe.

        @keyword path:              The directory to place the files into.
        @type path:                 str
        @keyword model:             The model tested.
        @type path:                 None or str
        @keyword model_tested:      List of models tested, if the pipe is final.
        @type model_tested:         None or list of str.
        @keyword param:             The param to write out.
        @type param:                None or list of str.
        @keyword file_name_ini:     The initial part of the file name for the grace and text files.
        @type file_name_ini:        None or str.
        """

        # If not set, use the name of the parameter.
        if file_name_ini == None:
            file_name_ini = param

        # If the model is in the list of models which support the parameter.
        write_result = False
        if model != None:
            # Get the model params.
            model_params = MODEL_PARAMS[model]

            if param in model_params:
                write_result = True

        # If this is the final pipe, then check if the model has been tested at any time.
        elif model == None:
            # Loop through all tested models.
            for model_tested in models_tested:
                # If one of the models tested has a parameter which belong in the list of models which support the parameter, then write it out.
                model_params = MODEL_PARAMS[model_tested]

                if param in model_params:
                    write_result = True
                    break

        # Write results if some of the models supports the parameter.
        if write_result:
            self.interpreter.value.write(param=param, file='%s.out'%file_name_ini, dir=path, force=True)
            self.interpreter.grace.write(x_data_type='res_num', y_data_type=param, file='%s.agr'%file_name_ini, dir=path, force=True)
