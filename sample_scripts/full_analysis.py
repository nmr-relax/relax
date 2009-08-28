###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
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

    d'Auvergne, E. J. and Gooley, P. R. (2008b). Optimisation of NMR dynamic models II. A new methodology for the dual optimisation of the model-free parameters and the Brownian rotational diffusion tensor. J. Biomol. NMR, 40(2), 121-133

Other references for features of this script include model-free model selection using Akaike's Information Criterion:

    d'Auvergne, E. J. and Gooley, P. R. (2003). The use of model selection in the model-free analysis of protein dynamics. J. Biomol. NMR, 25(1), 25-39.

The elimination of failed model-free models and Monte Carlo simulations:

    d'Auvergne, E. J. and Gooley, P. R. (2006). Model-free model elimination: A new step in the model-free dynamic analysis of NMR relaxation data. J. Biomol. NMR, 35(2), 117-135.

Significant model-free optimisation improvements:

    d'Auvergne, E. J. and Gooley, P. R. (2008a). Optimisation of NMR dynamic models I. Minimisation algorithms and their performance within the model-free and Brownian rotational diffusion spaces. J. Biomol. NMR, 40(2), 107-109.

Rather than searching for the lowest chi-squared value, this script searches for the model with the lowest AIC criterion.  This complex multi-universe, multi-dimensional search is formulated using set theory as the universal solution:

    d'Auvergne, E. J. and Gooley, P. R. (2007). Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm. 3(7), 483-494.

The basic three references for the original and extended model-free theories are:

    Lipari, G. and Szabo, A. (1982a). Model-free approach to the interpretation of nuclear magnetic-resonance relaxation in macromolecules I. Theory and range of validity. J. Am. Chem. Soc., 104(17), 4546-4559.

    Lipari, G. and Szabo, A. (1982b). Model-free approach to the interpretation of nuclear magnetic-resonance relaxation in macromolecules II. Analysis of experimental results. J. Am. Chem. Soc., 104(17), 4559-4570.

    Clore, G. M., Szabo, A., Bax, A., Kay, L. E., Driscoll, P. C., and Gronenborn, A.M. (1990). Deviations from the simple 2-parameter model-free approach to the interpretation of N-15 nuclear magnetic-relaxation of proteins. J. Am. Chem. Soc., 112(12), 4989-4991.


How to use this script
======================

The value of the variable DIFF_MODEL will determine the behaviour of this script.  The five diffusion models used in this script are:

    Model I   (MI)   - Local tm.
    Model II  (MII)  - Sphere.
    Model III (MIII) - Prolate spheroid.
    Model IV  (MIV)  - Oblate spheroid.
    Model V   (MV)   - Ellipsoid.

Model I must be optimised prior to any of the other diffusion models, while the Models II to V can be optimised in any order.  To select the various models, set the variable DIFF_MODEL to the following strings:

    MI   - 'local_tm'
    MII  - 'sphere'
    MIII - 'prolate'
    MIV  - 'oblate'
    MV   - 'ellipsoid'

This approach has the advantage of eliminating the need for an initial estimate of a global diffusion tensor and removing all the problems associated with the initial estimate.

It is important that the number of parameters in a model does not exceed the number of relaxation data sets for that spin.  If this is the case, the list of models in the MF_MODELS and LOCAL_TM_MODELS variables will need to be trimmed.


Model I - Local tm
~~~~~~~~~~~~~~~~~~

This will optimise the diffusion model whereby all spin of the molecule have a local tm value, i.e. there is no global diffusion tensor.  This model needs to be optimised prior to optimising any of the other diffusion models.  Each spin is fitted to the multiple model-free models separately, where the parameter tm is included in each model.

AIC model selection is used to select the models for each spin.


Model II - Sphere
~~~~~~~~~~~~~~~~~

This will optimise the isotropic diffusion model.  Multiple steps are required, an initial optimisation of the diffusion tensor, followed by a repetitive optimisation until convergence of the diffusion tensor.  Each of these steps requires this script to be rerun. For the initial optimisation, which will be placed in the directory './sphere/init/', the following steps are used:

The model-free models and parameter values for each spin are set to those of diffusion model MI.

The local tm parameter is removed from the models.

The model-free parameters are fixed and a global spherical diffusion tensor is minimised.


For the repetitive optimisation, each minimisation is named from 'round_1' onwards.  The initial 'round_1' optimisation will extract the diffusion tensor from the results file in './sphere/init/', and the results will be placed in the directory './sphere/round_1/'.  Each successive round will take the diffusion tensor from the previous round.  The following steps are used:

The global diffusion tensor is fixed and the multiple model-free models are fitted to each spin.

AIC model selection is used to select the models for each spin.

All model-free and diffusion parameters are allowed to vary and a global optimisation of all parameters is carried out.


Model III - Prolate spheroid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The methods used are identical to those of diffusion model MII, except that an axially symmetric diffusion tensor with Da >= 0 is used.  The base directory containing all the results is './prolate/'.


Model IV - Oblate spheroid
~~~~~~~~~~~~~~~~~~~~~~~~~~

The methods used are identical to those of diffusion model MII, except that an axially symmetric diffusion tensor with Da <= 0 is used.  The base directory containing all the results is './oblate/'.


Model V - Ellipsoid
~~~~~~~~~~~~~~~~~~~

The methods used are identical to those of diffusion model MII, except that a fully anisotropic diffusion tensor is used (also known as rhombic or asymmetric diffusion).  The base directory is './ellipsoid/'.



Final run
~~~~~~~~~

Once all the diffusion models have converged, the final run can be executed.  This is done by setting the variable DIFF_MODEL to 'final'.  This consists of two steps, diffusion tensor model selection, and Monte Carlo simulations.  Firstly AIC model selection is used to select between the diffusion tensor models.  Monte Carlo simulations are then run solely on this selected diffusion model.  Minimisation of the model is bypassed as it is assumed that the model is already fully optimised (if this is not the case the final run is not yet appropriate).

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
from relax_errors import RelaxError


# User variables.
#################

# The diffusion model.
DIFF_MODEL = 'local_tm'

# The model-free models (do not change these unless absolutely necessary).
MF_MODELS = ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']
LOCAL_TM_MODELS = ['tm0', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9']

# The PDB file (set this to None if no structure is available).
PDB_FILE = '1f3y.pdb'

# The sequence data (file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, sep).  These are the arguments to the  sequence.read() user function, for more information please see the documentation for that function.
SEQ_ARGS = ['noe.600.out', None, None, 0, 1, None, None, None]

# The heteronucleus atom name corresponding to that of the PDB file (used if the spin name is not in the sequence data).
HET_NAME = 'N'

# The relaxation data (data type, frequency label, frequency, file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, error_col, sep).  These are the arguments to the relax_data.read() user function, please see the documentation for that function for more information.
RELAX_DATA = [['R1',  '600', 599.719 * 1e6, 'r1.600.out',  None, None, 0, 1, None, None, 2, 3, None],
              ['R2',  '600', 599.719 * 1e6, 'r2.600.out',  None, None, 0, 1, None, None, 2, 3, None],
              ['NOE', '600', 599.719 * 1e6, 'noe.600.out', None, None, 0, 1, None, None, 2, 3, None],
              ['R1',  '500', 500.208 * 1e6, 'r1.500.out',  None, None, 0, 1, None, None, 2, 3, None],
              ['R2',  '500', 500.208 * 1e6, 'r2.500.out',  None, None, 0, 1, None, None, 2, 3, None],
              ['NOE', '500', 500.208 * 1e6, 'noe.500.out', None, None, 0, 1, None, None, 2, 3, None]
]

# The file containing the list of unresolved spins to exclude from the analysis (set this to None if no spin is to be excluded).
UNRES = 'unresolved'

# A file containing a list of spins which can be dynamically excluded at any point within the analysis (when set to None, this variable is not used).
EXCLUDE = None

# The bond length, CSA values, heteronucleus type, and proton type.
BOND_LENGTH = 1.02 * 1e-10
CSA = -172 * 1e-6
HETNUC = '15N'
PROTON = '1H'

# The grid search size (the number of increments per dimension).
GRID_INC = 11

# The optimisation technique.
MIN_ALGOR = 'newton'

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 500

# Automatic looping over all rounds until convergence (must be a boolean value of True or False).
CONV_LOOP = True


class Main:
    def __init__(self, relax):
        """Execute the model-free analysis."""

        # Setup.
        self.relax = relax


        # MI - Local tm.
        ################

        if DIFF_MODEL == 'local_tm':
            # Base directory to place files into.
            self.base_dir = 'local_tm'+sep

            # Sequential optimisation of all model-free models (function must be modified to suit).
            self.multi_model(local_tm=True)

            # Model selection.
            self.model_selection(modsel_pipe='aic', dir=self.base_dir + 'aic')


        # Diffusion models MII to MV.
        #############################

        elif DIFF_MODEL == 'sphere' or DIFF_MODEL == 'prolate' or DIFF_MODEL == 'oblate' or DIFF_MODEL == 'ellipsoid':
            # Loop until convergence if CONV_LOOP is set, otherwise just loop once.
            # This looping could be made much cleaner by removing the dependence on the determine_rnd() function.
            while True:
                # Determine which round of optimisation to do (init, round_1, round_2, etc).
                self.round = self.determine_rnd(model=DIFF_MODEL)

                # Inital round of optimisation for diffusion models MII to MV.
                if self.round == 0:
                    # Base directory to place files into.
                    self.base_dir = DIFF_MODEL + sep+'init'+sep

                    # Run name.
                    name = DIFF_MODEL

                    # Create the data pipe.
                    pipe.create(name, 'mf')

                    # Load the local tm diffusion model MI results.
                    results.read(file='results', dir='local_tm'+sep+'aic')

                    # Remove the tm parameter.
                    model_free.remove_tm()

                    # Deselect the spins in the EXCLUDE list.
                    if EXCLUDE:
                        deselect.read(file=EXCLUDE)

                    # Load the PDB file and calculate the unit vectors parallel to the XH bond.
                    if PDB_FILE:
                        structure.read_pdb(PDB_FILE)
                        structure.vectors(attached='H')

                    # Add an arbitrary diffusion tensor which will be optimised.
                    if DIFF_MODEL == 'sphere':
                        diffusion_tensor.init(10e-9, fixed=False)
                        inc = 11
                    elif DIFF_MODEL == 'prolate':
                        diffusion_tensor.init((10e-9, 0, 0, 0), spheroid_type='prolate', fixed=False)
                        inc = 11
                    elif DIFF_MODEL == 'oblate':
                        diffusion_tensor.init((10e-9, 0, 0, 0), spheroid_type='oblate', fixed=False)
                        inc = 11
                    elif DIFF_MODEL == 'ellipsoid':
                        diffusion_tensor.init((10e-09, 0, 0, 0, 0, 0), fixed=False)
                        inc = 6

                    # Minimise just the diffusion tensor.
                    fix('all_spins')
                    grid_search(inc=inc)
                    minimise(MIN_ALGOR)

                    # Write the results.
                    results.write(file='results', dir=self.base_dir, force=True)


                # Normal round of optimisation for diffusion models MII to MV.
                else:
                    # Base directory to place files into.
                    self.base_dir = DIFF_MODEL + sep+'round_'+repr(self.round)+sep

                    # Load the optimised diffusion tensor from either the previous round.
                    self.load_tensor()

                    # Sequential optimisation of all model-free models (function must be modified to suit).
                    self.multi_model()

                    # Model selection.
                    self.model_selection(modsel_pipe='aic', dir=self.base_dir + 'aic')

                    # Final optimisation of all diffusion and model-free parameters.
                    fix('all', fixed=False)

                    # Minimise all parameters.
                    minimise(MIN_ALGOR)

                    # Write the results.
                    dir = self.base_dir + 'opt'
                    results.write(file='results', dir=dir, force=True)

                    # Test for convergence.
                    converged = self.convergence()

                    # Break out of the infinite while loop if automatic looping is not activated or if convergence has occurred.
                    if converged or not CONV_LOOP:
                        break


        # Final run.
        ############

        elif DIFF_MODEL == 'final':
            # Diffusion model selection.
            ############################

            # All the global diffusion models to be used in the model selection.
            self.pipes = ['local_tm', 'sphere', 'prolate', 'oblate', 'ellipsoid']

            # Create the local_tm data pipe.
            pipe.create('local_tm', 'mf')

            # Load the local tm diffusion model MI results.
            results.read(file='results', dir='local_tm'+sep+'aic')

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
                pipe.create(model, 'mf')

                # Load the diffusion model results.
                results.read(file='results', dir=model + sep+'round_'+repr(self.round)+sep+'opt')

            # Model selection between MI to MV.
            self.model_selection(modsel_pipe='final', write_flag=False)


            # Monte Carlo simulations.
            ##########################

            # Fix the diffusion tensor, if it exists.
            if hasattr(pipes.get_pipe('final'), 'diff_tensor'):
                fix('diff')

            # Simulations.
            monte_carlo.setup(number=MC_NUM)
            monte_carlo.create_data()
            monte_carlo.initial_values()
            minimise(MIN_ALGOR)
            eliminate()
            monte_carlo.error_analysis()


            # Write the final results.
            ##########################

            results.write(file='results', dir='final', force=True)


        # Unknown script behaviour.
        ###########################

        else:
            raise RelaxError("Unknown diffusion model, change the value of 'DIFF_MODEL'")


    def convergence(self):
        """Test for the convergence of the global model."""

        # Alias the data pipes.
        cdp = pipes.get_pipe()
        prev_pipe = pipes.get_pipe('previous')

        # Print out.
        print("\n\n\n")
        print("#####################")
        print("# Convergence tests #")
        print("#####################\n\n")

        # Convergence flags.
        chi2_converged = True
        models_converged = True
        params_converged = True


        # Chi-squared test.
        ###################

        print("Chi-squared test:")
        print("    chi2 (k-1):          " + repr(prev_pipe.chi2))
        print("        (as an IEEE-754 byte array: " + repr(floatAsByteArray(prev_pipe.chi2)) + ')')
        print("    chi2 (k):            " + repr(cdp.chi2))
        print("        (as an IEEE-754 byte array: " + repr(floatAsByteArray(cdp.chi2)) + ')')
        print("    chi2 (difference):   " + repr(prev_pipe.chi2 - cdp.chi2))
        if prev_pipe.chi2 == cdp.chi2:
            print("    The chi-squared value has converged.\n")
        else:
            print("    The chi-squared value has not converged.\n")
            chi2_converged = False


        # Identical model-free model test.
        ##################################

        print("Identical model-free models test:")

        # Create a string representation of the model-free models of the previous data pipe.
        prev_models = ''
        for spin in spin_loop(pipe='previous'):
            if hasattr(spin, 'model'):
                if not spin.model == 'None':
                    prev_models = prev_models + spin.model

        # Create a string representation of the model-free models of the current data pipe.
        curr_models = ''
        for spin in spin_loop():
            if hasattr(spin, 'model'):
                if not spin.model == 'None':
                    curr_models = curr_models + spin.model

        # The test.
        if prev_models == curr_models:
            print("    The model-free models have converged.\n")
        else:
            print("    The model-free models have not converged.\n")
            models_converged = False


        # Identical parameter value test.
        #################################

        print("Identical parameter test:")

        # Only run the tests if the model-free models have converged.
        if models_converged:
            # Diffusion parameter array.
            if DIFF_MODEL == 'sphere':
                params = ['tm']
            elif DIFF_MODEL == 'oblate' or DIFF_MODEL == 'prolate':
                params = ['tm', 'Da', 'theta', 'phi']
            elif DIFF_MODEL == 'ellipsoid':
                params = ['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma']

            # Tests.
            for param in params:
                # Get the parameter values.
                prev_val = getattr(prev_pipe.diff_tensor, param)
                curr_val = getattr(cdp.diff_tensor, param)

                # Test if not identical.
                if prev_val != curr_val:
                    print("    Parameter:   " + param)
                    print("    Value (k-1): " + repr(prev_val))
                    print("        (as an IEEE-754 byte array: " + repr(floatAsByteArray(prev_val)) + ')')
                    print("    Value (k):   " + repr(curr_val))
                    print("        (as an IEEE-754 byte array: " + repr(floatAsByteArray(curr_val)) + ')')
                    print("    The diffusion parameters have not converged.\n")
                    params_converged = False

            # Skip the rest if the diffusion tensor parameters have not converged.
            if params_converged:
                # Loop over the spins.
                for mol_index, res_index, spin_index in spin_index_loop():
                    # Alias the spin containers.
                    prev_spin = prev_pipe.mol[mol_index].res[res_index].spin[spin_index]
                    curr_spin = cdp.mol[mol_index].res[res_index].spin[spin_index]

                    # Skip if the parameters have not converged.
                    if not params_converged:
                        break

                    # Skip spin systems with no 'params' object.
                    if not hasattr(prev_spin, 'params') or not hasattr(curr_spin, 'params'):
                        continue

                    # The spin ID string.
                    spin_id = generate_spin_id(mol_name=cdp.mol[mol_index].name, res_num=cdp.mol[mol_index].res[res_index].num, res_name=cdp.mol[mol_index].res[res_index].name, spin_num=cdp.mol[mol_index].res[res_index].spin[spin_index].num, spin_name=cdp.mol[mol_index].res[res_index].spin[spin_index].name)

                    # Loop over the parameters.
                    for j in xrange(len(curr_spin.params)):
                        # Get the parameter values.
                        prev_val = getattr(prev_spin, lower(prev_spin.params[j]))
                        curr_val = getattr(curr_spin, lower(curr_spin.params[j]))

                        # Test if not identical.
                        if prev_val != curr_val:
                            print("    Spin ID:     " + repr(spin_id))
                            print("    Parameter:   " + curr_spin.params[j])
                            print("    Value (k-1): " + repr(prev_val))
                            print("        (as an IEEE-754 byte array: " + repr(floatAsByteArray(prev_val)) + ')')
                            print("    Value (k):   " + repr(curr_val))
                            print("        (as an IEEE-754 byte array: " + repr(floatAsByteArray(prev_val)) + ')')
                            print("    The model-free parameters have not converged.\n")
                            params_converged = False
                            break

        # The model-free models haven't converged hence the parameter values haven't converged.
        else:
            print("    The model-free models haven't converged hence the parameters haven't converged.\n")
            params_converged = False

        # Print out.
        if params_converged:
            print("    The diffusion tensor and model-free parameters have converged.\n")


        # Final print out.
        ##################

        print("\nConvergence:")
        if chi2_converged and models_converged and params_converged:
            print("    [ Yes ]")
            return True
        else:
            print("    [ No ]")
            return False


    def determine_rnd(self, model=None):
        """Function for returning the name of next round of optimisation."""

        # Get a list of all files in the directory model.  If no directory exists, set the round to 'init' or 0.
        try:
            dir_list = listdir(getcwd()+sep+model)
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
            pipe.delete('previous')
        pipe.create('previous', 'mf')

        # Load the optimised diffusion tensor from the initial round.
        if self.round == 1:
            results.read('results', DIFF_MODEL + sep+'init')

        # Load the optimised diffusion tensor from the previous round.
        else:
            results.read('results', DIFF_MODEL + sep+'round_'+repr(self.round-1)+sep+'opt')


    def model_selection(self, modsel_pipe=None, dir=None, write_flag=True):
        """Model selection function."""

        # Model elimination.
        if modsel_pipe != 'final':
            eliminate()

        # Model selection (delete the model selection pipe if it already exists).
        if pipes.has_pipe(modsel_pipe):
            pipe.delete(modsel_pipe)
        model_selection(method='AIC', modsel_pipe=modsel_pipe, pipes=self.pipes)

        # Write the results.
        if write_flag:
            results.write(file='results', dir=dir, force=True)


    def multi_model(self, local_tm=False):
        """Function for optimisation of all model-free models."""

        # Set the data pipe names (also the names of preset model-free models).
        if local_tm:
            self.pipes = LOCAL_TM_MODELS
        else:
            self.pipes = MF_MODELS

        # Loop over the data pipes.
        for name in self.pipes:
            # Create the data pipe.
            if pipes.has_pipe(name):
                pipe.delete(name)
            pipe.create(name, 'mf')

            # Load the sequence.
            sequence.read(SEQ_ARGS[0], SEQ_ARGS[1], SEQ_ARGS[2], SEQ_ARGS[3], SEQ_ARGS[4], SEQ_ARGS[5], SEQ_ARGS[6], SEQ_ARGS[7])

            # Name the spins if necessary.
            if SEQ_ARGS[6] == None:
                spin.name(name=HET_NAME)

            # Load the PDB file and calculate the unit vectors parallel to the XH bond.
            if not local_tm and PDB_FILE:
                structure.read_pdb(PDB_FILE)
                structure.vectors(attached='H')

            # Load the relaxation data.
            for data in RELAX_DATA:
                relax_data.read(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data[12])

            # Deselect spins to be excluded (including unresolved and specifically excluded spins).
            if UNRES:
                deselect.read(file=UNRES)
            if EXCLUDE:
                deselect.read(file=EXCLUDE)

            # Copy the diffusion tensor from the 'opt' data pipe and prevent it from being minimised.
            if not local_tm:
                diffusion_tensor.copy('previous')
                fix('diff')

            # Set all the necessary values.
            value.set(BOND_LENGTH, 'bond_length')
            value.set(CSA, 'csa')
            value.set(HETNUC, 'heteronucleus')
            value.set(PROTON, 'proton')

            # Select the model-free model.
            model_free.select_model(model=name)

            # Minimise.
            grid_search(inc=GRID_INC)
            minimise(MIN_ALGOR)

            # Write the results.
            dir = self.base_dir + name
            results.write(file='results', dir=dir, force=True)


# The main class.
Main(self.relax)
