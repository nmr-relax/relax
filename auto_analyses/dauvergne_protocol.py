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

# Python module imports.
from os import getcwd, listdir, sep
from re import search
from string import lower

# relax module imports.
from doc_builder import LIST, PARAGRAPH, SECTION, SUBSECTION, TITLE, to_docstring
from float import floatAsByteArray
from info import Info_box; info = Info_box()
from generic_fns.mol_res_spin import exists_mol_res_spin_data, generate_spin_id, spin_index_loop, spin_loop
from generic_fns.pipes import cdp_name, get_pipe, has_pipe, switch
from generic_fns import selection
from prompt.interpreter import Interpreter
from relax_errors import RelaxError, RelaxNoSequenceError, RelaxNoValueError
from relax_io import DummyFileObject
from status import Status; status = Status()


doc = [
        [TITLE, "Automatic analysis for black-box model-free results."],
        [PARAGRAPH, "The dauvergne_protocol auto-analysis is designed for those who appreciate black-boxes or those who appreciate complex code.  Importantly, data at multiple magnetic field strengths is essential for this analysis.  If you would like to change how model-free analysis is performed, the code in the file auto_analyses/dauvergne_protocol.py in the base relax directory can be copied and modified as needed and used with the relax script interface.  This file is simply a complex relax script.  For a description of object-oriented coding in python using classes, functions/methods, self, etc., please see the python tutorial."],

        [SECTION, "References"],

        [SUBSECTION, "Auto-analysis primary reference"],
        [PARAGRAPH, "The model-free optimisation methodology herein is that of:"],
        [LIST, info.bib['dAuvergneGooley08b'].cite_short()],

        [SUBSECTION, "Techniques used in the auto-analysis"],
        [PARAGRAPH, "Other references for features of this dauvergne_protocol auto-analysis include model-free model selection using Akaike's Information Criterion:"],
        [LIST, info.bib['dAuvergneGooley03'].cite_short()],
        [PARAGRAPH, "The elimination of failed model-free models and Monte Carlo simulations:"],
        [LIST, info.bib['dAuvergneGooley06'].cite_short()],
        [PARAGRAPH, "Significant model-free optimisation improvements:"],
        [LIST, info.bib['dAuvergneGooley08a'].cite_short()],
        [PARAGRAPH, "Rather than searching for the lowest chi-squared value, this auto-analysis searches for the model with the lowest AIC criterion.  This complex multi-universe, multi-dimensional problem is formulated, using set theory, as the universal solution:"],
        [LIST, info.bib['dAuvergneGooley07'].cite_short()],
        [PARAGRAPH, "The basic three references for the original and extended model-free theories are:"],
        [LIST, info.bib['LipariSzabo82a'].cite_short()],
        [LIST, info.bib['LipariSzabo82b'].cite_short()],
        [LIST, info.bib['Clore90'].cite_short()],

        [SECTION, "How to use this auto-analysis"],
        [PARAGRAPH, "The five diffusion models used in this auto-analysis are:"],
        [LIST, "Model I   (MI)   - Local tm."],
        [LIST, "Model II  (MII)  - Sphere."],
        [LIST, "Model III (MIII) - Prolate spheroid."],
        [LIST, "Model IV  (MIV)  - Oblate spheroid."],
        [LIST, "Model V   (MV)   - Ellipsoid."],
        [PARAGRAPH, "If using the script-based user interface (UI), changing the value of the variable diff_model will determine the behaviour of this auto-analysis.  Model I must be optimised prior to any of the other diffusion models, while the Models II to V can be optimised in any order.  To select the various models, set the variable diff_model to the following strings:"],
        [LIST, "MI   - 'local_tm'"],
        [LIST, "MII  - 'sphere'"],
        [LIST, "MIII - 'prolate'"],
        [LIST, "MIV  - 'oblate'"],
        [LIST, "MV   - 'ellipsoid'"],
        [PARAGRAPH, "This approach has the advantage of eliminating the need for an initial estimate of a global diffusion tensor and removing all the problems associated with the initial estimate."],
        [PARAGRAPH, "It is important that the number of parameters in a model does not exceed the number of relaxation data sets for that spin.  If this is the case, the list of models in the mf_models and local_tm_models variables will need to be trimmed."],

        [SUBSECTION, "Model I - Local tm"],
        [PARAGRAPH, "This will optimise the diffusion model whereby all spin of the molecule have a local tm value, i.e. there is no global diffusion tensor.  This model needs to be optimised prior to optimising any of the other diffusion models.  Each spin is fitted to the multiple model-free models separately, where the parameter tm is included in each model."],
        [PARAGRAPH, "AIC model selection is used to select the models for each spin."],

        [SUBSECTION, "Model II - Sphere"],
        [PARAGRAPH, "This will optimise the isotropic diffusion model.  Multiple steps are required, an initial optimisation of the diffusion tensor, followed by a repetitive optimisation until convergence of the diffusion tensor.  In the relax script UI each of these steps requires this script to be rerun, unless the conv_loop flag is True.  In the GUI (graphical user interface), the procedure is repeated automatically until convergence.  For the initial optimisation, which will be placed in the directory './sphere/init/', the following steps are used:"],
        [PARAGRAPH, "The model-free models and parameter values for each spin are set to those of diffusion model MI."],
        [PARAGRAPH, "The local tm parameter is removed from the models."],
        [PARAGRAPH, "The model-free parameters are fixed and a global spherical diffusion tensor is minimised."],
        [PARAGRAPH, "For the repetitive optimisation, each minimisation is named from 'round_1' onwards.  The initial 'round_1' optimisation will extract the diffusion tensor from the results file in './sphere/init/', and the results will be placed in the directory './sphere/round_1/'.  Each successive round will take the diffusion tensor from the previous round.  The following steps are used:"],
        [PARAGRAPH, "The global diffusion tensor is fixed and the multiple model-free models are fitted to each spin."],
        [PARAGRAPH, "AIC model selection is used to select the models for each spin."],
        [PARAGRAPH, "All model-free and diffusion parameters are allowed to vary and a global optimisation of all parameters is carried out."],

        [SUBSECTION, "Model III - Prolate spheroid"],
        [PARAGRAPH, "The methods used are identical to those of diffusion model MII, except that an axially symmetric diffusion tensor with Da >= 0 is used.  The base directory containing all the results is './prolate/'."],

        [SUBSECTION, "Model IV - Oblate spheroid"],
        [PARAGRAPH, "The methods used are identical to those of diffusion model MII, except that an axially symmetric diffusion tensor with Da <= 0 is used.  The base directory containing all the results is './oblate/'."],

        [SUBSECTION, "Model V - Ellipsoid"],
        [PARAGRAPH, "The methods used are identical to those of diffusion model MII, except that a fully anisotropic diffusion tensor is used (also known as rhombic or asymmetric diffusion).  The base directory is './ellipsoid/'."],

        [SUBSECTION, "Final run"],
        [PARAGRAPH, "Once all the diffusion models have converged, the final run can be executed.  This is done by setting the variable diff_model to 'final'.  This consists of two steps, diffusion tensor model selection, and Monte Carlo simulations.  Firstly AIC model selection is used to select between the diffusion tensor models.  Monte Carlo simulations are then run solely on this selected diffusion model.  Minimisation of the model is bypassed as it is assumed that the model is already fully optimised (if this is not the case the final run is not yet appropriate)."],
        [PARAGRAPH, "The final black-box model-free results will be placed in the file 'final/results'."]
]


# Build the module docstring.
__doc__ = to_docstring(doc)



class dAuvergne_protocol:
    """The model-free auto-analysis."""

    # Some class variables.
    opt_func_tol = 1e-25
    opt_max_iterations = int(1e7)

    def __init__(self, pipe_name=None, results_dir=None, diff_model=None, mf_models=['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9'], local_tm_models=['tm0', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9'], grid_inc=11, diff_tensor_grid_inc={'sphere': 11, 'prolate': 11, 'oblate': 11, 'ellipsoid': 6}, min_algor='newton', mc_sim_num=500, max_iter=None, user_fns=None, conv_loop=True):
        """Perform the full model-free analysis protocol of d'Auvergne and Gooley, 2008b.

        @keyword pipe_name:             The name of the data pipe containing the sequence info.  This data pipe should have all values set including the CSA value, the bond length, the heteronucleus name and proton name.  It should also have all relaxation data loaded.
        @keyword results_dir:           The directory, where files are saved in.
        @type results_dir:              str
        @keyword diff_model:            The global diffusion model to optimise.  This can be one of 'local_tm', 'sphere', 'oblate', 'prolate', 'ellipsoid', or 'final'.
        @type diff_model:               str
        @keyword mf_models:             The model-free models.
        @type mf_models:                list of str
        @keyword local_tm_models:       The model-free models.
        @type local_tm_models:          list of str
        @keyword grid_inc:              The grid search size (the number of increments per dimension).
        @type grid_inc:                 int
        @keyword diff_tensor_grid_inc:  A list of grid search sizes for the optimisation of the sphere, prolate spheroid, oblate spheroid, and ellipsoid.
        @type diff_tensor_grid_inc:     list of int
        @keyword min_algor:             The minimisation algorithm (in most cases this should not be changed).
        @type min_algor:                str
        @keyword mc_sim_num:            The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_sim_num:               int
        @keyword max_iter:              The maximum number of iterations for the global iteration.  Set to None, then the algorithm iterates until convergence.
        @type max_iter:                 int or None.
        @keyword user_fns:              A dictionary of replacement user functions.  These will overwrite the standard user functions.  The key should be the name of the user function or user function class and the value should be the function or class instance.
        @type user_fns:                 dict
        @keyword conv_loop:             Automatic looping over all rounds until convergence.
        @type conv_loop:                bool
        """

        # Execution lock.
        status.exec_lock.acquire(pipe_name, mode='auto-analysis')

        # Store the args.
        self.pipe_name = pipe_name
        self.diff_model = diff_model
        self.mf_models = mf_models
        self.local_tm_models = local_tm_models
        self.grid_inc = grid_inc
        self.diff_tensor_grid_inc = diff_tensor_grid_inc
        self.min_algor = min_algor
        self.mc_sim_num = mc_sim_num
        self.max_iter = max_iter
        self.conv_loop = conv_loop

        # Project directory (i.e. directory containing the model-free model results and the newly generated files)
        if results_dir:
            self.results_dir = results_dir + sep
        else:
            self.results_dir = getcwd() + sep

        # Data checks.
        self.check_vars()

        # Set the data pipe to the current data pipe.
        if self.pipe_name != cdp_name():
            switch(self.pipe_name)

        # Some info for the status.
        self.status_setup()

        # Initialise the convergence data structures.
        self.conv_data = Container()
        self.conv_data.chi2 = []
        self.conv_data.models = []
        self.conv_data.diff_vals = []
        if self.diff_model == 'sphere':
            self.conv_data.diff_params = ['tm']
        elif self.diff_model == 'oblate' or self.diff_model == 'prolate':
            self.conv_data.diff_params = ['tm', 'Da', 'theta', 'phi']
        elif self.diff_model == 'ellipsoid':
            self.conv_data.diff_params = ['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma']
        self.conv_data.spin_ids = []
        self.conv_data.mf_params = []
        self.conv_data.mf_vals = []

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Replacement user functions.
        if user_fns:
            for name in user_fns:
                setattr(self.interpreter, name, user_fns[name])

        # Execute the protocol.
        try:
            self.execute()
        finally:
            # Finish and unlock execution.
            status.auto_analysis[self.pipe_name].fin = True
            status.current_analysis = None
            status.exec_lock.release()


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # The diff model.
        valid_models = ['local_tm', 'sphere', 'oblate', 'prolate', 'ellipsoid', 'final']
        if self.diff_model not in valid_models:
            raise RelaxError("The self.diff_model user variable '%s' is incorrectly set.  It must be one of %s." % (self.diff_model, valid_models))

        # Model-free models.
        mf_models = ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']
        local_tm_models = ['tm0', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9']
        if not isinstance(self.mf_models, list):
            raise RelaxError("The self.mf_models user variable must be a list.")
        if not isinstance(self.local_tm_models, list):
            raise RelaxError("The self.local_tm_models user variable must be a list.")
        for i in range(len(self.mf_models)):
            if self.mf_models[i] not in mf_models:
                raise RelaxError("The self.mf_models user variable '%s' is incorrectly set.  It must be one of %s." % (self.mf_models, mf_models))
        for i in range(len(self.local_tm_models)):
            if self.local_tm_models[i] not in local_tm_models:
                raise RelaxError("The self.local_tm_models user variable '%s' is incorrectly set.  It must be one of %s." % (self.local_tm_models, local_tm_models))

        # Sequence data.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError(self.pipe_name)

        # Relaxation data.
        if not hasattr(cdp, 'ri_ids') or len(cdp.ri_ids) == 0:
            raise RelaxNoRiError(ri_id)

        # Insufficient data.
        if len(cdp.ri_ids) <= 3:
            raise RelaxError("Insufficient relaxation data, 4 or more data sets are essential for the execution of this script.")

        # Spin vars.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Print.
            print("Checking spin '%s'." % spin_id)

            # Test if the bond length has been set.
            if not hasattr(spin, 'r') or spin.r == None:
                raise RelaxNoValueError("bond length")

            # Test if the CSA value has been set.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError("CSA")

            # Test if the heteronucleus type has been set.
            if not hasattr(spin, 'heteronuc_type') or spin.heteronuc_type == None:
                raise RelaxNoValueError("heteronucleus type")

            # Test if the proton type has been set.
            if not hasattr(spin, 'proton_type') or spin.proton_type == None:
                raise RelaxNoValueError("proton type")

        # Min vars.
        if not isinstance(self.grid_inc, int):
            raise RelaxError("The grid_inc user variable '%s' is incorrectly set.  It should be an integer." % self.grid_inc)
        if not isinstance(self.diff_tensor_grid_inc, dict):
            raise RelaxError("The diff_tensor_grid_inc user variable '%s' is incorrectly set.  It should be a dictionary." % self.diff_tensor_grid_inc)
        for tensor in ['sphere', 'prolate', 'oblate', 'ellipsoid']:
            if not self.diff_tensor_grid_inc.has_key(tensor):
                raise RelaxError("The diff_tensor_grid_inc user variable '%s' is incorrectly set.  It should contain the '%s' key." % (self.diff_tensor_grid_inc, tensor))
            if not isinstance(self.diff_tensor_grid_inc[tensor], int):
                raise RelaxError("The diff_tensor_grid_inc user variable '%s' is incorrectly set.  The value corresponding to the key '%s' should be an integer." % (self.diff_tensor_grid_inc, tensor))
        if not isinstance(self.min_algor, str):
            raise RelaxError("The min_algor user variable '%s' is incorrectly set.  It should be a string." % self.min_algor)
        if not isinstance(self.mc_sim_num, int):
            raise RelaxError("The mc_sim_num user variable '%s' is incorrectly set.  It should be an integer." % self.mc_sim_num)

        # Looping.
        if not isinstance(self.conv_loop, bool):
            raise RelaxError("The conv_loop user variable '%s' is incorrectly set.  It should be one of the booleans True or False." % self.conv_loop)


    def convergence(self):
        """Test for the convergence of the global model."""

        # Print out.
        print("\n\n\n")
        print("#####################")
        print("# Convergence tests #")
        print("#####################\n")

        # Maximum number of iterations reached.
        if self.max_iter and self.round > self.max_iter:
            print("Maximum number of global iterations reached.  Terminating the protocol before convergence has been reached.")
            return True

        # Store the data of the current data pipe.
        self.conv_data.chi2.append(cdp.chi2)

        # Create a string representation of the model-free models of the current data pipe.
        curr_models = ''
        for spin in spin_loop():
            if hasattr(spin, 'model'):
                if not spin.model == 'None':
                    curr_models = curr_models + spin.model
        self.conv_data.models.append(curr_models)

        # Store the diffusion tensor parameters.
        self.conv_data.diff_vals.append([])
        for param in self.conv_data.diff_params:
            # Get the parameter values.
            self.conv_data.diff_vals[-1].append(getattr(cdp.diff_tensor, param))

        # Store the model-free parameters.
        self.conv_data.mf_vals.append([])
        self.conv_data.mf_params.append([])
        self.conv_data.spin_ids.append([])
        for spin, spin_id in spin_loop(return_id=True):
            # Skip spin systems with no 'params' object.
            if not hasattr(spin, 'params'):
                continue

            # Add the spin ID, parameters, and empty value list.
            self.conv_data.spin_ids[-1].append(spin_id)
            self.conv_data.mf_params[-1].append([])
            self.conv_data.mf_vals[-1].append([])

            # Loop over the parameters.
            for j in xrange(len(spin.params)):
                # Get the parameters and values.
                self.conv_data.mf_params[-1][-1].append(spin.params[j])
                self.conv_data.mf_vals[-1][-1].append(getattr(spin, lower(spin.params[j])))

        # No need for tests.
        if self.round == 1:
            print("First round of optimisation, skipping the convergence tests.\n\n\n")
            return False

        # Loop over the iterations.
        converged = False
        for i in range(self.start_round, self.round - 1):
            # Print out.
            print("\n\n\n# Comparing the current iteration to iteration %i.\n" % (i+1))

            # Index.
            index = i - self.start_round

            # Chi-squared test.
            print("Chi-squared test:")
            print("    chi2 (iter %i):  %s" % (i+1, self.conv_data.chi2[index]))
            print("        (as an IEEE-754 byte array:  %s)" % floatAsByteArray(self.conv_data.chi2[index]))
            print("    chi2 (iter %i):  %s" % (self.round, self.conv_data.chi2[-1]))
            print("        (as an IEEE-754 byte array:  %s)" % floatAsByteArray(self.conv_data.chi2[-1]))
            print("    chi2 (difference):  %s" % (self.conv_data.chi2[index] - self.conv_data.chi2[-1]))
            if self.conv_data.chi2[index] == self.conv_data.chi2[-1]:
                print("    The chi-squared value has converged.\n")
            else:
                print("    The chi-squared value has not converged.\n")
                continue

            # Identical model-free model test.
            print("Identical model-free models test:")
            if self.conv_data.models[index] == self.conv_data.models[-1]:
                print("    The model-free models have converged.\n")
            else:
                print("    The model-free models have not converged.\n")
                continue

            # Identical diffusion tensor parameter value test.
            print("Identical diffusion tensor parameter test:")
            params_converged = True
            for k in range(len(self.conv_data.diff_params)):
                # Test if not identical.
                if self.conv_data.diff_vals[index][k] != self.conv_data.diff_vals[-1][k]:
                    print("    Parameter:   %s" % param)
                    print("    Value (iter %i):  %s" % (i+1, self.conv_data.diff_vals[index][k]))
                    print("        (as an IEEE-754 byte array:  %s)" % floatAsByteArray(self.conv_data.diff_vals[index][k]))
                    print("    Value (iter %i):  %s" % (self.round, self.conv_data.diff_vals[-1][k]))
                    print("        (as an IEEE-754 byte array:  %s)" % floatAsByteArray(self.conv_data.diff_vals[-1][k]))
                    print("    The diffusion parameters have not converged.\n")
                    params_converged = False
                    break
            if not params_converged:
                continue
            print("    The diffusion tensor parameters have converged.\n")

            # Identical model-free parameter value test.
            print("\nIdentical model-free parameter test:")
            if len(self.conv_data.spin_ids[index]) != len(self.conv_data.spin_ids[-1]):
                print("    Different number of spins.")
                continue
            for j in range(len(self.conv_data.spin_ids[-1])):
                # Loop over the parameters.
                for k in range(len(self.conv_data.mf_params[-1][j])):
                    # Test if not identical.
                    if self.conv_data.mf_vals[index][j][k] != self.conv_data.mf_vals[-1][j][k]:
                        print("    Spin ID:     %s" % self.conv_data.spin_ids[-1][j])
                        print("    Parameter:   %s" % self.conv_data.mf_params[-1][j][k])
                        print("    Value (iter %i): %s" % (i+1, self.conv_data.mf_vals[index][j][k]))
                        print("        (as an IEEE-754 byte array:  %s)" % floatAsByteArray(self.conv_data.mf_vals[index][j][k]))
                        print("    Value (iter %i): %s" % (self.round, self.conv_data.mf_vals[-1][j][k]))
                        print("        (as an IEEE-754 byte array:  %s)" % floatAsByteArray(self.conv_data.mf_vals[index][j][k]))
                        print("    The model-free parameters have not converged.\n")
                        params_converged = False
                        break
            if not params_converged:
                continue
            print("    The model-free parameters have converged.\n")

            # Convergence.
            converged = True
            break


        # Final print out.
        ##################

        print("\nConvergence:")
        if converged:
            # Update the status.
            status.auto_analysis[self.pipe_name].convergence = True

            # Print out.
            print("    [ Yes ]")

            # Return the termination condition.
            return True
        else:
            # Print out.
            print("    [ No ]")

            # Return False to not terminate.
            return False


    def determine_rnd(self, model=None):
        """Function for returning the name of next round of optimisation."""

        # Get a list of all files in the directory model.  If no directory exists, set the round to 'init' or 0.
        try:
            # Files are in same directory / no directory specified
            if self.results_dir =='':
                dir_list = listdir(self.results_dir+sep+model)

            # Directory is specified
            else:
                dir_list = listdir(self.results_dir+model)
        except:
            return 0

        # Set the round to 'init' or 0 if there is no directory called 'init'.
        if 'init' not in dir_list:
            return 0

        # Create a list of all files which begin with 'round_'.
        rnd_dirs = []
        for file in dir_list:
            if search('^round_', file):
                rnd_dirs.append(file)

        # Create a sorted list of integer round numbers.
        numbers = []
        for dir in rnd_dirs:
            try:
                numbers.append(int(dir[6:]))
            except:
                pass
        numbers.sort()

        # No directories begining with 'round_' exist, set the round to 1.
        if not len(numbers):
            return 1

        # Determine the number for the next round (add 1 to the highest number).
        return numbers[-1] + 1


    def execute(self):
        """Execute the protocol."""

        # MI - Local tm.
        ################

        if self.diff_model == 'local_tm':
            # Base directory to place files into.
            self.base_dir = self.results_dir+'local_tm'+sep

            # Sequential optimisation of all model-free models (function must be modified to suit).
            self.multi_model(local_tm=True)

            # Model selection.
            self.model_selection(modsel_pipe='aic', dir=self.base_dir + 'aic')


        # Diffusion models MII to MV.
        #############################

        elif self.diff_model == 'sphere' or self.diff_model == 'prolate' or self.diff_model == 'oblate' or self.diff_model == 'ellipsoid':
            # No local_tm directory!
            dir_list = listdir(self.results_dir)
            if 'local_tm' not in dir_list:
                raise RelaxError("The local_tm model must be optimised first.")

            # The initial round of optimisation - not zero if calculations were interrupted.
            self.start_round = self.determine_rnd(model=self.diff_model)

            # Loop until convergence if conv_loop is set, otherwise just loop once.
            # This looping could be made much cleaner by removing the dependence on the determine_rnd() function.
            while True:
                # Determine which round of optimisation to do (init, round_1, round_2, etc).
                self.round = self.determine_rnd(model=self.diff_model)
                status.auto_analysis[self.pipe_name].round = self.round

                # Inital round of optimisation for diffusion models MII to MV.
                if self.round == 0:
                    # Base directory to place files into.
                    self.base_dir = self.results_dir+self.diff_model+sep+'init'+sep

                    # Run name.
                    name = self.diff_model

                    # Create the data pipe (deleting the old one if it exists).
                    if has_pipe(name):
                        self.interpreter.pipe.delete(name)
                    self.interpreter.pipe.create(name, 'mf')

                    # Load the local tm diffusion model MI results.
                    self.interpreter.results.read(file='results', dir=self.results_dir+'local_tm'+sep+'aic')

                    # Remove the tm parameter.
                    self.interpreter.model_free.remove_tm()

                    # Add an arbitrary diffusion tensor which will be optimised.
                    if self.diff_model == 'sphere':
                        self.interpreter.diffusion_tensor.init(10e-9, fixed=False)
                        inc = self.diff_tensor_grid_inc['sphere']
                    elif self.diff_model == 'prolate':
                        self.interpreter.diffusion_tensor.init((10e-9, 0, 0, 0), spheroid_type='prolate', fixed=False)
                        inc = self.diff_tensor_grid_inc['prolate']
                    elif self.diff_model == 'oblate':
                        self.interpreter.diffusion_tensor.init((10e-9, 0, 0, 0), spheroid_type='oblate', fixed=False)
                        inc = self.diff_tensor_grid_inc['oblate']
                    elif self.diff_model == 'ellipsoid':
                        self.interpreter.diffusion_tensor.init((10e-09, 0, 0, 0, 0, 0), fixed=False)
                        inc = self.diff_tensor_grid_inc['ellipsoid']

                    # Minimise just the diffusion tensor.
                    self.interpreter.fix('all_spins')
                    self.interpreter.grid_search(inc=inc)
                    self.interpreter.minimise(self.min_algor, func_tol=self.opt_func_tol, max_iterations=self.opt_max_iterations)

                    # Write the results.
                    self.interpreter.results.write(file='results', dir=self.base_dir, force=True)


                # Normal round of optimisation for diffusion models MII to MV.
                else:
                    # Base directory to place files into.
                    self.base_dir = self.results_dir+self.diff_model + sep+'round_'+repr(self.round)+sep

                    # Load the optimised diffusion tensor from either the previous round.
                    self.load_tensor()

                    # Sequential optimisation of all model-free models (function must be modified to suit).
                    self.multi_model()

                    # Model selection.
                    self.model_selection(modsel_pipe='aic', dir=self.base_dir + 'aic')

                    # Final optimisation of all diffusion and model-free parameters.
                    self.interpreter.fix('all', fixed=False)

                    # Minimise all parameters.
                    self.interpreter.minimise(self.min_algor, func_tol=self.opt_func_tol, max_iterations=self.opt_max_iterations)

                    # Write the results.
                    dir = self.base_dir + 'opt'
                    self.interpreter.results.write(file='results', dir=dir, force=True)

                    # Test for convergence.
                    converged = self.convergence()

                    # Break out of the infinite while loop if automatic looping is not activated or if convergence has occurred.
                    if converged or not self.conv_loop:
                        break

                # Unset the status.
                status.auto_analysis[self.pipe_name].round = None


        # Final run.
        ############

        elif self.diff_model == 'final':
            # Diffusion model selection.
            ############################

            # All the global diffusion models to be used in the model selection.
            self.pipes = ['local_tm', 'sphere', 'prolate', 'oblate', 'ellipsoid']

            # Close all pipes that might be craeted.
            for name in self.pipes:
                # Close the pipe
                if has_pipe(name):
                    self.interpreter.pipe.delete(name)

            # Missing optimised model.
            dir_list = listdir(self.results_dir)
            for name in self.pipes:
                if name not in dir_list:
                    raise RelaxError("The %s model must be optimised first." % name)

            # Create the local_tm data pipe.
            self.interpreter.pipe.create('local_tm', 'mf')

            # Load the local tm diffusion model MI results.
            self.interpreter.results.read(file='results', dir=self.results_dir+'local_tm'+sep+'aic')

            # Loop over models MII to MV.
            for model in ['sphere', 'prolate', 'oblate', 'ellipsoid']:
                # Determine which was the last round of optimisation for each of the models.
                self.round = self.determine_rnd(model=model) - 1

                # If no directories begining with 'round_' exist, the script has not been properly utilised!
                if self.round < 1:
                    # Construct the name of the diffusion tensor.
                    name = model
                    if model == 'prolate' or model == 'oblate':
                        name = name + ' spheroid'

                    # Throw an error to prevent misuse of the script.
                    raise RelaxError("Multiple rounds of optimisation of the " + name + " (between 8 to 15) are required for the proper execution of this script.")

                # Create the data pipe.
                self.interpreter.pipe.create(model, 'mf')

                # Load the diffusion model results.
                self.interpreter.results.read(file='results', dir=self.results_dir+model + sep+'round_'+repr(self.round)+sep+'opt')

            # Model selection between MI to MV.
            self.model_selection(modsel_pipe='final', write_flag=False)


            # Monte Carlo simulations.
            ##########################

            # Fix the diffusion tensor, if it exists.
            if hasattr(get_pipe('final'), 'diff_tensor'):
                self.interpreter.fix('diff')

            # Simulations.
            self.interpreter.monte_carlo.setup(number=self.mc_sim_num)
            self.interpreter.monte_carlo.create_data()
            self.interpreter.monte_carlo.initial_values()
            self.interpreter.minimise(self.min_algor, func_tol=self.opt_func_tol, max_iterations=self.opt_max_iterations)
            self.interpreter.eliminate()
            self.interpreter.monte_carlo.error_analysis()


            # Write the final results.
            ##########################

            self.interpreter.results.write(file='results', dir=self.results_dir+'final', force=True)


        # Unknown script behaviour.
        ###########################

        else:
            raise RelaxError("Unknown diffusion model, change the value of 'self.diff_model'")

        # Unset the status info.
        self.status_reset()


    def load_tensor(self):
        """Function for loading the optimised diffusion tensor."""

        # Create the data pipe for the previous data (deleting the old data pipe first if necessary).
        if has_pipe('previous'):
            self.interpreter.pipe.delete('previous')
        self.interpreter.pipe.create('previous', 'mf')

        # Load the optimised diffusion tensor from the initial round.
        if self.round == 1:
            self.interpreter.results.read('results', self.results_dir+self.diff_model + sep+'init')

        # Load the optimised diffusion tensor from the previous round.
        else:
            self.interpreter.results.read('results', self.results_dir+self.diff_model + sep+'round_'+repr(self.round-1)+sep+'opt')


    def model_selection(self, modsel_pipe=None, dir=None, write_flag=True):
        """Model selection function."""

        # Model selection (delete the model selection pipe if it already exists).
        if has_pipe(modsel_pipe):
            self.interpreter.pipe.delete(modsel_pipe)
        self.interpreter.model_selection(method='AIC', modsel_pipe=modsel_pipe, pipes=self.pipes)

        # Write the results.
        if write_flag:
            self.interpreter.results.write(file='results', dir=dir, force=True)


    def multi_model(self, local_tm=False):
        """Function for optimisation of all model-free models."""

        # Set the data pipe names (also the names of preset model-free models).
        if local_tm:
            self.pipes = self.local_tm_models
        else:
            self.pipes = self.mf_models

        # Loop over the data pipes.
        for name in self.pipes:
            # Place the model name into the status container.
            status.auto_analysis[self.pipe_name].current_model = name

            # Create the data pipe (by copying).
            if has_pipe(name):
                self.interpreter.pipe.delete(name)
            self.interpreter.pipe.copy(self.pipe_name, name)
            self.interpreter.pipe.switch(name)

            # Copy the diffusion tensor from the 'opt' data pipe and prevent it from being minimised.
            if not local_tm:
                self.interpreter.diffusion_tensor.copy('previous')
                self.interpreter.fix('diff')

            # Select the model-free model.
            self.interpreter.model_free.select_model(model=name)

            # Minimise.
            self.interpreter.grid_search(inc=self.grid_inc)
            self.interpreter.minimise(self.min_algor, func_tol=self.opt_func_tol, max_iterations=self.opt_max_iterations)

            # Model elimination.
            self.interpreter.eliminate()

            # Write the results.
            dir = self.base_dir + name
            self.interpreter.results.write(file='results', dir=dir, force=True)

        # Unset the status.
        status.auto_analysis[self.pipe_name].current_model = None


    def status_setup(self):
        """Initialise the status object."""

        # Initialise the status object for this auto-analysis.
        status.init_auto_analysis(self.pipe_name, type='dauvergne_protocol')
        status.current_analysis = self.pipe_name

        # The global diffusion model.
        status.auto_analysis[self.pipe_name].diff_model = self.diff_model

        # The round of optimisation, i.e. the global iteration.
        status.auto_analysis[self.pipe_name].round = None

        # The list of model-free local tm models for optimisation, i.e. the global iteration.
        status.auto_analysis[self.pipe_name].local_tm_models = self.local_tm_models

        # The list of model-free models for optimisation, i.e. the global iteration.
        status.auto_analysis[self.pipe_name].mf_models = self.mf_models

        # The current model-free model.
        status.auto_analysis[self.pipe_name].current_model = None

        # The maximum number of iterations of the global model.
        status.auto_analysis[self.pipe_name].max_iter = self.max_iter

        # The convergence of the global model.
        status.auto_analysis[self.pipe_name].convergence = False


    def status_reset(self):
        """Initialise the status object."""

        # The global diffusion model.
        status.auto_analysis[self.pipe_name].diff_model = None

        # The round of optimisation, i.e. the global iteration.
        status.auto_analysis[self.pipe_name].round = None

        # The list of model-free local tm models for optimisation, i.e. the global iteration.
        status.auto_analysis[self.pipe_name].local_tm_models = None

        # The list of model-free models for optimisation, i.e. the global iteration.
        status.auto_analysis[self.pipe_name].mf_models = None

        # The current model-free model.
        status.auto_analysis[self.pipe_name].current_model = None

        # The convergence of the global model.
        status.auto_analysis[self.pipe_name].convergence = False



class Container:
    """Empty container for data storage."""
