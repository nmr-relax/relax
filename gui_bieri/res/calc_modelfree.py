###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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

# script to calculate model-free models

# Python module imports.
from os import getcwd, listdir, sep
from string import replace
from re import search
import time
import sys
import os

# relax module imports.
from float import floatAsByteArray
from generic_fns.mol_res_spin import generate_spin_id, spin_index_loop, spin_loop
from generic_fns import pipes
from relax_errors import RelaxError
from specific_fns.setup import relax_fit_obj, model_free_obj
from generic_fns.state import save_state
from generic_fns import monte_carlo, results
from minfx.generic import generic_minimise
import generic_fns.structure.geometric

# relaxGUI module import
from results_analysis import color_code_noe
from message import relax_run_ok


### Model-free

def start_model_free(self, model):

        target_dir = str(self.resultsdir_t21_copy_2.GetValue())
        unres = str(self.unresolved_t21_copy_1_copy.GetValue())
        nmr_freq1 = str(self.modelfreefreq1.GetValue())
        nmr_freq2 = str(self.modelfreefreq2.GetValue())
        nmr_freq3 = str(self.modelfreefreq3.GetValue())

        # detect 2 or 3 field strength
        num_field = 3
        if self.modelfreefreq3.GetValue() == '':
            num_field = 2
        if self.m_noe_3.GetValue() == '':
            num_field = 2
        if self.m_r1_3.GetValue() == '':
            num_field = 2
        if self.m_r1_3.GetValue() == '':
            num_field = 2

        if self.aic.GetValue() == True:
            selection = "AIC"
        if self.bic.GetValue() == True:
            selection = "BIC" 

        #create unresolved file
        filename2 =  target_dir + sep + 'unresolved'
        file = open(filename2, 'w')
        unres = replace(unres, ",","\n")
        file.write(unres)
        file.close()

        #create models list
        models = []

        if self.m0.GetValue() == True:
            models.append('m0')
        if self.m1.GetValue() == True:
            models.append('m1')
        if self.m2.GetValue() == True:
            models.append('m2')
        if self.m3.GetValue() == True:
            models.append('m3')
        if self.m4.GetValue() == True:
            models.append('m4')
        if self.m5.GetValue() == True:
            models.append('m5')
        if self.m6.GetValue() == True:
            models.append('m6')
        if self.m7.GetValue() == True:
            models.append('m7')
        if self.m8.GetValue() == True:
            models.append('m8')
        if self.m9.GetValue() == True:
            models.append('m9')

        #create tm models list
        tmodels = []

        if self.m0.GetValue() == True:
            tmodels.append('tm0')
        if self.m1.GetValue() == True:
            tmodels.append('tm1')
        if self.m2.GetValue() == True:
            tmodels.append('tm2')
        if self.m3.GetValue() == True:
            tmodels.append('tm3')
        if self.m4.GetValue() == True:
            tmodels.append('tm4')
        if self.m5.GetValue() == True:
            tmodels.append('tm5')
        if self.m6.GetValue() == True:
            tmodels.append('tm6')
        if self.m7.GetValue() == True:
            tmodels.append('tm7')
        if self.m8.GetValue() == True:
            tmodels.append('tm8')
        if self.m9.GetValue() == True:
            tmodels.append('tm9')

        MF_MODELS = models
        LOCAL_TM_MODELS = tmodels

        # User variables.
        #################

        PDB_FILE = str(self.structure_t21_copy_1_copy.GetValue())
        gracedir = target_dir + sep + 'grace'
        resultsdir = target_dir + sep
        m_method = selection

        if selection == "AIC":
             msel = "aic"
        if selection == "BIC":
             msel = "bic"
        modelselection = msel

        #parameter files
        noe_1 = str(self.m_noe_1.GetValue())
        r1_1 = str(self.m_r1_1.GetValue())
        r2_1 = str(self.m_r2_1.GetValue())
        noe_2 = str(self.m_noe_2.GetValue())
        r1_2 = str(self.m_r1_2.GetValue())
        r2_2 = str(self.m_r2_2.GetValue())
        noe_3 = str(self.m_noe_3.GetValue())
        r1_3 = str(self.m_r1_3.GetValue())
        r2_3 = str(self.m_r2_3.GetValue())

        HETNUC = 'N'
        SEQ_ARGS = [noe_1, None, None, 1, 2, 3, 4, None]

        nmr_freq1 = int(self.modelfreefreq1.GetValue())
        nmr_freq2 = int(self.modelfreefreq2.GetValue())
        if num_field == 3:
           nmr_freq3 = int(self.modelfreefreq3.GetValue())

        # The relaxation data (data type, frequency label, frequency, file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, error_col, sep).  These are the arguments to the relax_data.read() user function, please see the documentation for that function for more information.

        if num_field == 2:
         RELAX_DATA = [['R1', str(nmr_freq1), nmr_freq1 * 1e6, r1_1,  None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq1), nmr_freq1 * 1e6, r2_1,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['NOE', str(nmr_freq1), nmr_freq1 * 1e6, noe_1,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['R1', str(nmr_freq2), nmr_freq2 * 1e6, r1_2,  None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq2), nmr_freq2 * 1e6, r2_2,  None, None, 1, 2, 3, 4, 5, 6, None]]

        if num_field == 3:
         RELAX_DATA = [['R1', str(nmr_freq1), nmr_freq1 * 1e6, r1_1,  None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq1), nmr_freq1 * 1e6, r2_1,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['NOE', str(nmr_freq1), nmr_freq1 * 1e6, noe_1,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['R1', str(nmr_freq2), nmr_freq2 * 1e6, r1_2,  None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq2), nmr_freq2 * 1e6, r2_2,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['NOE', str(nmr_freq2), nmr_freq2 * 1e6, noe_2,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['R1', str(nmr_freq3), nmr_freq3 * 1e6, r1_3,  None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq3), nmr_freq3 * 1e6, r2_3,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['NOE', str(nmr_freq3), nmr_freq3 * 1e6, noe_3,  None, None, 1, 2, 3, 4, 5, 6, None]] 
        
        
        # The diffusion model.
        DIFF_MODEL = model
        
        
        # The file containing the list of unresolved spins to exclude from the analysis (set this to None if no spin is to be excluded).
        UNRES = resultsdir + 'unresolved'
        
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
        
        
        class Model:
            def __init__(self):
                """Execute the model-free analysis."""
        
                # Setup.
                #self = relax
        
        
                # MI - Local tm.
                ################
        
                if DIFF_MODEL == 'local_tm':
                    # Base directory to place files into.
                    self.base_dir = resultsdir + 'local_tm' + sep
        
                    # Sequential optimisation of all model-free models (function must be modified to suit).
                    self.multi_model(local_tm=True)
        
                    # Model selection.
                    self.model_selection(modsel_pipe=modelselection, dir=self.base_dir + modelselection)
        
        
                # Diffusion models MII to MV.
                #############################
        
                elif DIFF_MODEL == 'sphere' or DIFF_MODEL == 'prolate' or DIFF_MODEL == 'oblate' or DIFF_MODEL == 'ellipsoid':
                    # Loop until convergence if CONV_LOOP is set, otherwise just loop once.
                    # This looping could be made much cleaner by removing the dependence on the determine_rnd() function.
                    while 1:
                        # Determine which round of optimisation to do (init, round_1, round_2, etc).
                        self.round = self.determine_rnd(model=DIFF_MODEL)
        
                        # Inital round of optimisation for diffusion models MII to MV.
                        if self.round == 0:
                            # Base directory to place files into.
                            self.base_dir = resultsdir + DIFF_MODEL + sep + 'init' + sep
        
                            # Run name.
                            name = DIFF_MODEL
        
                            # Create the data pipe.
                            pipe.create(name, 'mf')
        
                            # Load the local tm diffusion model MI results.
                            results.read(file='results', dir=resultsdir + 'local_tm' + sep+modelselection)
        
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
                            fix(element='all_spins')
                            grid_search(inc=inc)
                            minimise(MIN_ALGOR)
        
                            # Write the results.
                            results.write(file='results', dir=self.base_dir, force=True)
        
        
                        # Normal round of optimisation for diffusion models MII to MV.
                        else:
                            # Base directory to place files into.
                            self.base_dir = resultsdir + DIFF_MODEL + sep + 'round_' + `self.round` + sep
        
                            # Load the optimised diffusion tensor from either the previous round.
                            self.load_tensor()
        
                            # Sequential optimisation of all model-free models (function must be modified to suit).
                            self.multi_model()
        
                            # Model selection.
                            self.model_selection(modsel_pipe='final', dir=self.base_dir + modelselection)
        
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
                    results.read(file='results', dir=resultsdir + 'local_tm' + sep+modelselection)
        
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
                            raise RelaxError, "Multiple rounds of optimisation of the " + name + " (between 8 to 15) are required for the proper execution of this script."
        
                        # Create the data pipe.
                        pipe.create(model, 'mf')
        
                        # Load the diffusion model results.
                        results.read(file='results', dir=resultsdir + model + sep + 'round_' + `self.round` + sep + 'opt')
        
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
        
                    results.write(file='results', dir=resultsdir + 'final', force=True)
        
        
                # Unknown script behaviour.
                ###########################
        
                else:
                    raise RelaxError, "Unknown diffusion model, change the value of 'DIFF_MODEL'"
        
        
            def convergence(self):
                """Test for the convergence of the global model."""
        
                # Alias the data pipes.
                cdp = pipes.get_pipe()
                prev_pipe = pipes.get_pipe('previous')
        
                # Print out.
                print "\n\n\n"
                print "#####################"
                print "# Convergence tests #"
                print "#####################\n\n"
        
                # Convergence flags.
                chi2_converged = True
                models_converged = True
                params_converged = True
        
        
                # Chi-squared test.
                ###################
        
                print "Chi-squared test:"
                print "    chi2 (k-1):          " + `prev_pipe.chi2`
                print "        (as an IEEE-754 byte array: " + `floatAsByteArray(prev_pipe.chi2)` + ')'
                print "    chi2 (k):            " + `cdp.chi2`
                print "        (as an IEEE-754 byte array: " + `floatAsByteArray(cdp.chi2)` + ')'
                print "    chi2 (difference):   " + `prev_pipe.chi2 - cdp.chi2`
                if prev_pipe.chi2 == cdp.chi2:
                    print "    The chi-squared value has converged.\n"
                else:
                    print "    The chi-squared value has not converged.\n"
                    chi2_converged = False
        
        
                # Identical model-free model test.
                ##################################
        
                print "Identical model-free models test:"
        
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
                    print "    The model-free models have converged.\n"
                else:
                    print "    The model-free models have not converged.\n"
                    models_converged = False
        
        
                # Identical parameter value test.
                #################################
        
                print "Identical parameter test:"
        
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
                            print "    Parameter:   " + param
                            print "    Value (k-1): " + `prev_val`
                            print "        (as an IEEE-754 byte array: " + `floatAsByteArray(prev_val)` + ')'
                            print "    Value (k):   " + `curr_val`
                            print "        (as an IEEE-754 byte array: " + `floatAsByteArray(curr_val)` + ')'
                            print "    The diffusion parameters have not converged.\n"
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
                                    print "    Spin ID:     " + `spin_id`
                                    print "    Parameter:   " + curr_spin.params[j]
                                    print "    Value (k-1): " + `prev_val`
                                    print "        (as an IEEE-754 byte array: " + `floatAsByteArray(prev_val)` + ')'
                                    print "    Value (k):   " + `curr_val`
                                    print "        (as an IEEE-754 byte array: " + `floatAsByteArray(prev_val)` + ')'
                                    print "    The model-free parameters have not converged.\n"
                                    params_converged = False
                                    break
        
                # The model-free models haven't converged hence the parameter values haven't converged.
                else:
                    print "    The model-free models haven't converged hence the parameters haven't converged.\n"
                    params_converged = False
        
                # Print out.
                if params_converged:
                    print "    The diffusion tensor and model-free parameters have converged.\n"
        
        
                # Final print out.
                ##################
        
                print "\nConvergence:"
                if chi2_converged and models_converged and params_converged:
                    print "    [ Yes ]"
                    return True
                else:
                    print "    [ No ]"
                    return False
        
        
            def determine_rnd(self, model=None):
                """Function for returning the name of next round of optimisation."""
        
                # Get a list of all files in the directory model.  If no directory exists, set the round to 'init' or 0.
                try:
                    dir_list = listdir(resultsdir + model)
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
                    results.read('results', resultsdir + DIFF_MODEL + sep + 'init')
        
                # Load the optimised diffusion tensor from the previous round.
                else:
                    results.read('results', resultsdir + DIFF_MODEL + sep + 'round_' + `self.round - 1` + sep + 'opt')
        
        
            def model_selection(self, modsel_pipe=None, dir=None, write_flag=True):
                """Model selection function."""
        
                # Model elimination.
                if modsel_pipe != 'final':
                    eliminate()
        
                # Model selection (delete the model selection pipe if it already exists).
                if pipes.has_pipe(modsel_pipe):
                    pipe.delete(modsel_pipe)
                model_selection(method=m_method, modsel_pipe=modsel_pipe, pipes=self.pipes)
        
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
        Model()
        
        print ""
        print ""
        print "_____________________________________________________________________________"
        print ""
        print "calculation finished"
        print ""
        msgbox(msg='Model-free ' + str(model) + ' calculation was successfull !', title='relaxGUI ', ok_button='OK', image=sys.path[-1]+sep+'gui_bieri'+sep+'res'+sep+'pics'+sep+'relax.gif', root=None)

        #create results file
        if model == 'final':
           model_free_results(self, target_dir)
           self.list_modelfree.Append(target_dir + sep + 'final' + sep + 'grace' + sep + 's2.agr')
           self.list_modelfree.Append(target_dir + sep + 'final' + sep + 'Model-free_Results.txt')
           self.list_modelfree.Append(target_dir + sep + 'final' + sep + 's2.pml')
           self.list_modelfree.Append(target_dir + sep + 'final' + sep + 'rex.pml')



