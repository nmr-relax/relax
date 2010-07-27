###############################################################################
#                                                                             #
# Copyright (C) 2004-2010 Edward d'Auvergne                                   #
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

"""Script for black-box model-free analysis.

This script is designed for those who appreciate black-boxes or those who appreciate complex code.  Importantly data at multiple magnetic field strengths is essential for this analysis.  The script will need to be heavily tailored to the molecule in question by changing the variables just below this documentation.  If you would like to change how model-free analysis is performed, the code in the class Main can be changed as needed.  For a description of object-oriented coding in python using classes, functions/methods, self, etc., see the python tutorial.

If you have obtained this script without the program relax, please visit http://nmr-relax.com.


References
==========

The model-free optimisation methodology herein is that of:

    - d'Auvergne, E. J. and Gooley, P. R. (2008b). Optimisation of NMR dynamic models II. A new methodology for the dual optimisation of the model-free parameters and the Brownian rotational diffusion tensor. J. Biomol. NMR, 40(2), 121-133

Other references for features of this script include model-free model selection using Akaike's Information Criterion:

    - d'Auvergne, E. J. and Gooley, P. R. (2003). The use of model selection in the model-free analysis of protein dynamics. J. Biomol. NMR, 25(1), 25-39.

The elimination of failed model-free models and Monte Carlo simulations:

    - d'Auvergne, E. J. and Gooley, P. R. (2006). Model-free model elimination: A new step in the model-free dynamic analysis of NMR relaxation data. J. Biomol. NMR, 35(2), 117-135.

Significant model-free optimisation improvements:

    - d'Auvergne, E. J. and Gooley, P. R. (2008a). Optimisation of NMR dynamic models I. Minimisation algorithms and their performance within the model-free and Brownian rotational diffusion spaces. J. Biomol. NMR, 40(2), 107-109.

Rather than searching for the lowest chi-squared value, this script searches for the model with the lowest AIC criterion.  This complex multi-universe, multi-dimensional search is formulated using set theory as the universal solution:

    - d'Auvergne, E. J. and Gooley, P. R. (2007). Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm. 3(7), 483-494.

The basic three references for the original and extended model-free theories are:

    - Lipari, G. and Szabo, A. (1982a). Model-free approach to the interpretation of nuclear magnetic-resonance relaxation in macromolecules I. Theory and range of validity. J. Am. Chem. Soc., 104(17), 4546-4559.

    - Lipari, G. and Szabo, A. (1982b). Model-free approach to the interpretation of nuclear magnetic-resonance relaxation in macromolecules II. Analysis of experimental results. J. Am. Chem. Soc., 104(17), 4559-4570.

    - Clore, G. M., Szabo, A., Bax, A., Kay, L. E., Driscoll, P. C., and Gronenborn, A.M. (1990). Deviations from the simple 2-parameter model-free approach to the interpretation of N-15 nuclear magnetic-relaxation of proteins. J. Am. Chem. Soc., 112(12), 4989-4991.


How to use this script
======================

The value of the variable diff_model will determine the behaviour of this script.  The five diffusion models used in this script are:

    - Model I   (MI)   - Local tm.
    - Model II  (MII)  - Sphere.
    - Model III (MIII) - Prolate spheroid.
    - Model IV  (MIV)  - Oblate spheroid.
    - Model V   (MV)   - Ellipsoid.

Model I must be optimised prior to any of the other diffusion models, while the Models II to V can be optimised in any order.  To select the various models, set the variable diff_model to the following strings:

    - MI   - 'local_tm'
    - MII  - 'sphere'
    - MIII - 'prolate'
    - MIV  - 'oblate'
    - MV   - 'ellipsoid'

This approach has the advantage of eliminating the need for an initial estimate of a global diffusion tensor and removing all the problems associated with the initial estimate.

It is important that the number of parameters in a model does not exceed the number of relaxation data sets for that spin.  If this is the case, the list of models in the mf_models and local_tm_models variables will need to be trimmed.


Model I - Local tm
------------------

This will optimise the diffusion model whereby all spin of the molecule have a local tm value, i.e. there is no global diffusion tensor.  This model needs to be optimised prior to optimising any of the other diffusion models.  Each spin is fitted to the multiple model-free models separately, where the parameter tm is included in each model.

AIC model selection is used to select the models for each spin.


Model II - Sphere
-----------------

This will optimise the isotropic diffusion model.  Multiple steps are required, an initial optimisation of the diffusion tensor, followed by a repetitive optimisation until convergence of the diffusion tensor.  Each of these steps requires this script to be rerun. For the initial optimisation, which will be placed in the directory './sphere/init/', the following steps are used:

The model-free models and parameter values for each spin are set to those of diffusion model MI.

The local tm parameter is removed from the models.

The model-free parameters are fixed and a global spherical diffusion tensor is minimised.


For the repetitive optimisation, each minimisation is named from 'round_1' onwards.  The initial 'round_1' optimisation will extract the diffusion tensor from the results file in './sphere/init/', and the results will be placed in the directory './sphere/round_1/'.  Each successive round will take the diffusion tensor from the previous round.  The following steps are used:

The global diffusion tensor is fixed and the multiple model-free models are fitted to each spin.

AIC model selection is used to select the models for each spin.

All model-free and diffusion parameters are allowed to vary and a global optimisation of all parameters is carried out.


Model III - Prolate spheroid
----------------------------

The methods used are identical to those of diffusion model MII, except that an axially symmetric diffusion tensor with Da >= 0 is used.  The base directory containing all the results is './prolate/'.


Model IV - Oblate spheroid
--------------------------

The methods used are identical to those of diffusion model MII, except that an axially symmetric diffusion tensor with Da <= 0 is used.  The base directory containing all the results is './oblate/'.


Model V - Ellipsoid
-------------------

The methods used are identical to those of diffusion model MII, except that a fully anisotropic diffusion tensor is used (also known as rhombic or asymmetric diffusion).  The base directory is './ellipsoid/'.



Final run
---------

Once all the diffusion models have converged, the final run can be executed.  This is done by setting the variable diff_model to 'final'.  This consists of two steps, diffusion tensor model selection, and Monte Carlo simulations.  Firstly AIC model selection is used to select between the diffusion tensor models.  Monte Carlo simulations are then run solely on this selected diffusion model.  Minimisation of the model is bypassed as it is assumed that the model is already fully optimised (if this is not the case the final run is not yet appropriate).

The final black-box model-free results will be placed in the file 'final/results'.
"""

# Python module imports.
from os import getcwd, listdir, sep
from re import search
from string import lower

# relax module imports.
from float import floatAsByteArray
from generic_fns.mol_res_spin import generate_spin_id, spin_index_loop, spin_loop
from generic_fns import pipes
from prompt.interpreter import Interpreter
from relax_errors import RelaxError
from status import Status



class dAuvergne_protocol:
    def __init__(self, save_dir=None, diff_model=None, mf_models=['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9'], local_tm_models=['tm0', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9'], pdb_file=None, seq_args=None, het_name=None, relax_data=None, unres=None, exclude=None, bond_length=None, csa=None, hetnuc=None, proton='1H', grid_inc=11, min_algor='newton', mc_num=500, max_iter=None, user_fns=None, conv_loop=True):
        """Perform the full model-free analysis protocol of d'Auvergne and Gooley, 2008b.

        @keyword save_dir:          The directory, where files are saved in.
        @type save_dir:             str
        @keyword diff_model:        The global diffusion model to optimise.  This can be one of 'local_tm', 'sphere', 'oblate', 'prolate', 'ellipsoid', or 'final'.
        @type diff_model:           str
        @keyword mf_models:         The model-free models.
        @type mf_models:            list of str
        @keyword local_tm_models:   The model-free models.
        @type local_tm_models:      list of str
        @keyword pdb_file:          The PDB file (set this to None if no structure is available).
        @type pdb_file:             None or str
        @keyword seq_args:          The sequence data (file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, sep).  These are the arguments to the  sequence.read() user function, for more information please see the documentation for that function.
        @type seq_args:             list of lists of [str, None or str, None or int, None or int, None or int, None or int, None or int, None or int, None or int, None or str]
        @keyword het_name:          The heteronucleus atom name corresponding to that of the PDB file (used if the spin name is not in the sequence data).
        @type het_name:             None or str
        @keyword relax_data:        The relaxation data (data type, frequency label, frequency, file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, error_col, sep).  These are the arguments to the relax_data.read() user function, please see the documentation for that function for more information.
        @type relax_data:           list of lists of [str, str, float, str, None or str, None or int, None or int, None or int, None or int, None or int, None or int, None or int, None or str]
        @keyword unres:             The file containing the list of unresolved spins to exclude from the analysis (set this to None if no spin is to be excluded).
        @type unres:                None or str
        @keyword exclude:           A file containing a list of spins which can be dynamically excluded at any point within the analysis (when set to None, this variable is not used).
        @type exclude:              None or str
        @keyword bond_length:       The bond length in metres.
        @type bond_length:          float
        @keyword csa:               The chemical shift anisotropy value (multiply by 1e-6 to convert out of ppm).
        @type csa:                  float
        @keyword hetnuc:            The heteronucleus type, i.e. '15N', '13C', etc.
        @type hetnuc:               str
        @keyword proton:            The proton type, i.e. '1H'.
        @type proton:               str
        @keyword grid_inc:          The grid search size (the number of increments per dimension).
        @type grid_inc:             int
        @keyword min_algor:         The minimisation algorithm (in most cases this should not be changed).
        @type min_algor:            str
        @keyword mc_num:            The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_num:               int
        @keyword max_iter:          The maximum number of iterations for the global iteration.  Set to None, then the algorithm iterates until convergence.
        @type max_iter:             int or None.
        @keyword user_fns:          A dictionary of replacement user functions.  These will overwrite the standard user functions.  The key should be the name of the user function or user function class and the value should be the function or class instance.
        @type user_fns:             dict
        @keyword conv_loop:         Automatic looping over all rounds until convergence.
        @type conv_loop:            bool
        """

        # Store the args.
        self.diff_model = diff_model
        self.mf_models = mf_models
        self.local_tm_models = local_tm_models
        self.pdb_file = pdb_file
        self.seq_args = seq_args
        self.het_name = het_name
        self.relax_data = relax_data
        self.unres = unres
        self.exclude = exclude
        self.bond_length = bond_length
        self.csa = csa
        self.hetnuc = hetnuc
        self.proton = proton
        self.grid_inc = grid_inc
        self.min_algor = min_algor
        self.mc_num = mc_num
        self.max_iter = max_iter
        self.conv_loop = conv_loop

        # Project directory (i.e. directory containing the model-free model results and the newly generated files)
        if save_dir:
            self.save_dir = save_dir+sep
        else:
            self.save_dir = ''

        # User variable checks.
        self.check_vars()

        # Initialise the status.
        self.status = Status()
        self.status.dAuvergne_protocol.diff_model = diff_model
        self.status.dAuvergne_protocol.mf_models = mf_models
        self.status.dAuvergne_protocol.local_mf_models = local_tm_models

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


        # MI - Local tm.
        ################

        if self.diff_model == 'local_tm':
            # Base directory to place files into.
            self.base_dir = self.save_dir+'local_tm'+sep

            # Sequential optimisation of all model-free models (function must be modified to suit).
            self.multi_model(local_tm=True)

            # Model selection.
            self.model_selection(modsel_pipe='aic', dir=self.base_dir + 'aic')


        # Diffusion models MII to MV.
        #############################

        elif self.diff_model == 'sphere' or self.diff_model == 'prolate' or self.diff_model == 'oblate' or self.diff_model == 'ellipsoid':
            # The initial round of optimisation - not zero if calculations were interrupted.
            self.start_round = self.determine_rnd(model=self.diff_model)

            # Loop until convergence if conv_loop is set, otherwise just loop once.
            # This looping could be made much cleaner by removing the dependence on the determine_rnd() function.
            while True:
                # Determine which round of optimisation to do (init, round_1, round_2, etc).
                self.round = self.determine_rnd(model=self.diff_model)
                self.status.dAuvergne_protocol.round = self.round

                # Inital round of optimisation for diffusion models MII to MV.
                if self.round == 0:
                    # Base directory to place files into.
                    self.base_dir = self.save_dir+self.diff_model+sep+'init'+sep

                    # Run name.
                    name = self.diff_model

                    # Create the data pipe.
                    self.interpreter.pipe.create(name, 'mf')

                    # Load the local tm diffusion model MI results.
                    self.interpreter.results.read(file='results', dir=self.save_dir+'local_tm'+sep+'aic')

                    # Remove the tm parameter.
                    self.interpreter.model_free.remove_tm()

                    # Deselect the spins in the exclude list.
                    if self.exclude:
                        self.interpreter.deselect.read(file=self.exclude)

                    # Name the spins if necessary.
                    if self.seq_args[6] == None:
                        self.interpreter.spin.name(name=self.het_name)

                    # Load the PDB file and calculate the unit vectors parallel to the XH bond.
                    if self.pdb_file:
                        self.interpreter.structure.read_pdb(self.pdb_file)
                        self.interpreter.structure.vectors(attached='H')

                    # Add an arbitrary diffusion tensor which will be optimised.
                    if self.diff_model == 'sphere':
                        self.interpreter.diffusion_tensor.init(10e-9, fixed=False)
                        inc = 11
                    elif self.diff_model == 'prolate':
                        self.interpreter.diffusion_tensor.init((10e-9, 0, 0, 0), spheroid_type='prolate', fixed=False)
                        inc = 11
                    elif self.diff_model == 'oblate':
                        self.interpreter.diffusion_tensor.init((10e-9, 0, 0, 0), spheroid_type='oblate', fixed=False)
                        inc = 11
                    elif self.diff_model == 'ellipsoid':
                        self.interpreter.diffusion_tensor.init((10e-09, 0, 0, 0, 0, 0), fixed=False)
                        inc = 6

                    # Minimise just the diffusion tensor.
                    self.interpreter.fix('all_spins')
                    self.interpreter.grid_search(inc=inc)
                    self.interpreter.minimise(self.min_algor)

                    # Write the results.
                    self.interpreter.results.write(file='results', dir=self.base_dir, force=True)


                # Normal round of optimisation for diffusion models MII to MV.
                else:
                    # Base directory to place files into.
                    self.base_dir = self.save_dir+self.diff_model + sep+'round_'+repr(self.round)+sep

                    # Load the optimised diffusion tensor from either the previous round.
                    self.load_tensor()

                    # Sequential optimisation of all model-free models (function must be modified to suit).
                    self.multi_model()

                    # Model selection.
                    self.model_selection(modsel_pipe='aic', dir=self.base_dir + 'aic')

                    # Final optimisation of all diffusion and model-free parameters.
                    self.interpreter.fix('all', fixed=False)

                    # Minimise all parameters.
                    self.interpreter.minimise(self.min_algor)

                    # Write the results.
                    dir = self.base_dir + 'opt'
                    self.interpreter.results.write(file='results', dir=dir, force=True)

                    # Test for convergence.
                    converged = self.convergence()

                    # Break out of the infinite while loop if automatic looping is not activated or if convergence has occurred.
                    if converged or not self.conv_loop:
                        break

                # Unset the status.
                self.status.dAuvergne_protocol.round = None


        # Final run.
        ############

        elif self.diff_model == 'final':
            # Diffusion model selection.
            ############################

            # All the global diffusion models to be used in the model selection.
            self.pipes = ['local_tm', 'sphere', 'prolate', 'oblate', 'ellipsoid']

            # Create the local_tm data pipe.
            self.interpreter.pipe.create('local_tm', 'mf')

            # Load the local tm diffusion model MI results.
            self.interpreter.results.read(file='results', dir=self.save_dir+'local_tm'+sep+'aic')

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
                self.interpreter.results.read(file='results', dir=self.save_dir+model + sep+'round_'+repr(self.round)+sep+'opt')

            # Model selection between MI to MV.
            self.model_selection(modsel_pipe='final', write_flag=False)


            # Monte Carlo simulations.
            ##########################

            # Fix the diffusion tensor, if it exists.
            if hasattr(pipes.get_pipe('final'), 'diff_tensor'):
                self.interpreter.fix('diff')

            # Simulations.
            self.interpreter.monte_carlo.setup(number=self.mc_num)
            self.interpreter.monte_carlo.create_data()
            self.interpreter.monte_carlo.initial_values()
            self.interpreter.minimise(self.min_algor)
            self.interpreter.eliminate()
            self.interpreter.monte_carlo.error_analysis()


            # Write the final results.
            ##########################

            self.interpreter.results.write(file='results', dir=self.save_dir+'final', force=True)


        # Unknown script behaviour.
        ###########################

        else:
            raise RelaxError("Unknown diffusion model, change the value of 'self.diff_model'")

        # Unset the status info.
        self.status.dAuvergne_protocol.diff_model = None
        self.status.dAuvergne_protocol.mf_models = None
        self.status.dAuvergne_protocol.local_tm_models = None


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

        # PDB file.
        if self.pdb_file and not isinstance(self.pdb_file, str):
            raise RelaxError("The pdb_file user variable '%s' is incorrectly set.  It should either be a string or None." % self.pdb_file)

        # Sequence data.
        if not isinstance(self.seq_args, list):
            raise RelaxError("The seq_args user variable '%s' must be a list." % self.seq_args)
        if len(self.seq_args) != 8:
            raise RelaxError("The seq_args user variable '%s' must be a list with eight elements." % self.seq_args)
        if not isinstance(self.seq_args[0], str):
            raise RelaxError("The file name component of the seq_args user variable '%s' must be a string." % self.seq_args)
        for i in range(1, 8):
            if self.seq_args[i] != None and not isinstance(self.seq_args[i], int):
                raise RelaxError("The column components of the seq_args user variable '%s' must be either None or integers." % self.seq_args)

        # Atom name.
        if not isinstance(self.het_name, str):
            raise RelaxError("The het_name heteronucleus atom name user variable '%s' must be a string." % self.het_name)

        # Relaxation data.
        if not isinstance(self.relax_data, list):
            raise RelaxError("The relax_data user variable '%s' must be a list." % self.relax_data)
        labels = []
        for i in range(len(self.relax_data)):
            if self.relax_data[i][1] not in labels:
                labels.append(self.relax_data[i][1])
            if len(self.relax_data[i]) != 13:
                raise RelaxError("The relax_data user variable component '%s' must be a list of 13 elements." % self.relax_data[i])
            if not isinstance(self.relax_data[i][0], str):
                raise RelaxError("The data type component '%s' of the relax_data user variable must be a string." % self.relax_data[i][0])
            if not isinstance(self.relax_data[i][1], str):
                raise RelaxError("The frequency label component '%s' of the relax_data user variable must be a string." % self.relax_data[i][1])
            if not isinstance(self.relax_data[i][2], float):
                raise RelaxError("The frequency component '%s' of the relax_data user variable must be a floating point number." % self.relax_data[i][2])
            if not isinstance(self.relax_data[i][3], str):
                raise RelaxError("The file name component '%s' of the relax_data user variable must be a string." % self.relax_data[i][3])
            for j in range(4, 13):
                if self.relax_data[i][j] != None and not isinstance(self.relax_data[i][j], int):
                    raise RelaxError("The column components of the relax_data user variable '%s' must be either None or integers." % self.relax_data[i])

        # Insufficient data.
        if len(self.relax_data) <= 3:
            raise RelaxError("Insufficient relaxation data, 4 or more data sets are essential for the execution of this script.")
        if len(labels) == 1:
            raise RelaxError("Relaxation data at multiple magnetic field strengths is essential for this analysis.")

        # Unresolved and exclude files. FIXME
        #if self.unres and not isinstance(self.unres, str):
        #    raise RelaxError("The unres user variable '%s' is incorrectly set.  It should either be a string or None." % self.unres)
        if self.exclude and not isinstance(self.exclude, str):
            raise RelaxError("The exclude user variable '%s' is incorrectly set.  It should either be a string or None." % self.exclude)

        # Spin vars.
        if not isinstance(self.bond_length, float):
            raise RelaxError("The bond_length user variable '%s' is incorrectly set.  It should be a floating point number." % self.bond_length)
        if not isinstance(self.csa, float):
            raise RelaxError("The csa user variable '%s' is incorrectly set.  It should be a floating point number." % self.csa)
        if not isinstance(self.hetnuc, str):
            raise RelaxError("The hetnuc user variable '%s' is incorrectly set.  It should be a string." % self.hetnuc)
        if not isinstance(self.proton, str):
            raise RelaxError("The proton user variable '%s' is incorrectly set.  It should be a string." % self.proton)

        # Min vars.
        if not isinstance(self.grid_inc, int):
            raise RelaxError("The grid_inc user variable '%s' is incorrectly set.  It should be an integer." % self.grid_inc)
        if not isinstance(self.min_algor, str):
            raise RelaxError("The min_algor user variable '%s' is incorrectly set.  It should be a string." % self.min_algor)
        if not isinstance(self.mc_num, int):
            raise RelaxError("The mc_num user variable '%s' is incorrectly set.  It should be an integer." % self.mc_num)

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
            self.status.dAuvergne_protocol.convergence = True

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
            if self.save_dir =='':
                dir_list = listdir(getcwd()+sep+model)

            # Directory is specified
            else:
                dir_list = listdir(self.save_dir+model)
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


    def load_tensor(self):
        """Function for loading the optimised diffusion tensor."""

        # Create the data pipe for the previous data (deleting the old data pipe first if necessary).
        if pipes.has_pipe('previous'):
            self.interpreter.pipe.delete('previous')
        self.interpreter.pipe.create('previous', 'mf')

        # Load the optimised diffusion tensor from the initial round.
        if self.round == 1:
            self.interpreter.results.read('results', self.save_dir+self.diff_model + sep+'init')

        # Load the optimised diffusion tensor from the previous round.
        else:
            self.interpreter.results.read('results', self.save_dir+self.diff_model + sep+'round_'+repr(self.round-1)+sep+'opt')


    def model_selection(self, modsel_pipe=None, dir=None, write_flag=True):
        """Model selection function."""

        # Model elimination.
        if modsel_pipe != 'final':
            self.interpreter.eliminate()

        # Model selection (delete the model selection pipe if it already exists).
        if pipes.has_pipe(modsel_pipe):
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
            self.status.dAuvergne_protocol.current_model = name

            # Create the data pipe.
            if pipes.has_pipe(name):
                self.interpreter.pipe.delete(name)
            self.interpreter.pipe.create(name, 'mf')

            # Load the sequence.
            self.interpreter.sequence.read(file=self.seq_args[0], dir=self.seq_args[1], mol_name_col=self.seq_args[2], res_num_col=self.seq_args[3], res_name_col=self.seq_args[4], spin_num_col=self.seq_args[5], spin_name_col=self.seq_args[6], sep=self.seq_args[7])

            # Name the spins if necessary.
            if self.seq_args[6] == None:
                self.interpreter.spin.name(name=self.het_name)

            # Load the PDB file and calculate the unit vectors parallel to the XH bond.
            if not local_tm and self.pdb_file:
                self.interpreter.structure.read_pdb(self.pdb_file)
                self.interpreter.structure.vectors(attached='H')

            # Load the relaxation data.
            for data in self.relax_data:
                self.interpreter.relax_data.read(ri_label=data[0], frq_label=data[1], frq=data[2], file=data[3], dir=data[4], mol_name_col=data[5], res_num_col=data[6], res_name_col=data[7], spin_num_col=data[8], spin_name_col=data[9], data_col=data[10], error_col=data[11], sep=data[12])

            # Deselect spins to be excluded (including unresolved and specifically excluded spins).
            if self.unres:
                self.interpreter.deselect.read(file=self.unres, spin_id_col=1)
            if self.exclude:
                self.interpreter.deselect.read(file=self.exclude, spin_id_col=1)

            # Copy the diffusion tensor from the 'opt' data pipe and prevent it from being minimised.
            if not local_tm:
                self.interpreter.diffusion_tensor.copy('previous')
                self.interpreter.fix('diff')

            # Set all the necessary values.
            self.interpreter.value.set(self.bond_length, 'bond_length')
            self.interpreter.value.set(self.csa, 'csa')
            self.interpreter.value.set(self.hetnuc, 'heteronucleus')
            self.interpreter.value.set(self.proton, 'proton')

            # Select the model-free model.
            self.interpreter.model_free.select_model(model=name)

            # Minimise.
            self.interpreter.grid_search(inc=self.grid_inc)
            self.interpreter.minimise(self.min_algor)

            # Write the results.
            dir = self.save_dir+self.base_dir + name
            self.interpreter.results.write(file='results', dir=dir, force=True)

        # Unset the status.
        self.status.dAuvergne_protocol.current_model = None


class Container:
    """Empty container for data storage."""
