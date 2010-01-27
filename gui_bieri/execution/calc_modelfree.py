###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
import math
from os import listdir, sep
from re import search
from string import replace
import time
import wx

# relax module imports.
from auto_analyses.dauvergne_protocol import dAuvergne_protocol
from float import floatAsByteArray
from generic_fns import diffusion_tensor, eliminate, fix, grace, minimise, model_selection, monte_carlo, pipes, relax_data, results, selection, sequence, spectrum, value
from generic_fns.mol_res_spin import generate_spin_id, spin_index_loop, spin_loop
import generic_fns.structure.main
from relax_errors import RelaxError
from specific_fns.setup import model_free_obj

# relaxGUI module imports.
from gui_bieri.message import relax_run_ok


def start_model_free(self, model, automatic, global_setting, file_setting, sequencefile, logpanel):
    # Number of Monte Carlo simulations
    global montecarlo
    montecarlo = int(global_setting[6]) 

    # value for progress bar during monte carlo simulation
    global progress
    progress = 5.0

    # redirect relax output and errors to relaxGUI - log panel
    redir=RedirectText(logpanel)
    sys.stdout=redir
    sys.stderr=redir

    wx.CallAfter(logpanel.log_panel.AppendText, ('Starting Model-free calculation\n------------------------------------------\n\n') )
    time.sleep(0.5)

    # Set relax and file settings from dialog
    bondlength = converttofloat(global_setting[0])
    csa = converttofloat(global_setting[1])    
    hetero = global_setting[2]
    prot = global_setting[3]
    gridinc = global_setting[4]
    minalgor = global_setting[5]
    intcol = int(file_setting[5])
    mol_name = int(file_setting[0])
    res_num = int(file_setting[1])
    res_name = int(file_setting[2])
    spin_num = int(file_setting[3])
    spin_name = int(file_setting[4])

    # get target directory, unresolved residues and NMR frequencies
    target_dir = str(self.resultsdir_r21_copy_2.GetValue())
    unres = str(self.unresolved_r21_copy_1_copy.GetValue())
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
        selection_mode = "AIC"
    if self.bic.GetValue() == True:
        selection_mode = "BIC"

    #create unresolved file
    if not unres == '':
        filename2 = target_dir + sep + 'unresolved'
        file = open(filename2, 'w')
        unres = replace(unres, ",", "\n")
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

    PDB_FILE = str(self.structure_r21_copy_1_copy.GetValue())
    gracedir = target_dir + sep + 'grace'
    resultsdir = target_dir + sep
    m_method = selection_mode

    if selection_mode == "AIC":
        msel = "aic"
    if selection_mode == "BIC":
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

    nmr_freq1 = int(self.modelfreefreq1.GetValue())
    nmr_freq2 = int(self.modelfreefreq2.GetValue())
    if num_field == 3:
        nmr_freq3 = int(self.modelfreefreq3.GetValue())

        # (data type, frequency label, frequency, file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, error_col, sep)

    if num_field == 2:
         RELAX_DATA = [['R1', str(nmr_freq1), nmr_freq1 * 1e6, r1_1, None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq1), nmr_freq1 * 1e6, r2_1, None, None, 1, 2, 3, 4, 5, 6, None],
                       ['NOE', str(nmr_freq1), nmr_freq1 * 1e6, noe_1, None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R1', str(nmr_freq2), nmr_freq2 * 1e6, r1_2, None, None, 1, 2, 3, 4, 5, 6, None],
                       ['NOE', str(nmr_freq2), nmr_freq2 * 1e6, noe_2, None, None, 1, 2, 3, 4, 5, 6, None]]

    if num_field == 3:
         RELAX_DATA = [['R1', str(nmr_freq1), nmr_freq1 * 1e6, r1_1, None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq1), nmr_freq1 * 1e6, r2_1, None, None, 1, 2, 3, 4, 5, 6, None],
                       ['NOE', str(nmr_freq1), nmr_freq1 * 1e6, noe_1, None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R1', str(nmr_freq2), nmr_freq2 * 1e6, r1_2, None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq2), nmr_freq2 * 1e6, r2_2, None, None, 1, 2, 3, 4, 5, 6, None],
                       ['NOE', str(nmr_freq2), nmr_freq2 * 1e6, noe_2, None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R1', str(nmr_freq3), nmr_freq3 * 1e6, r1_3, None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq3), nmr_freq3 * 1e6, r2_3, None, None, 1, 2, 3, 4, 5, 6, None],
                       ['NOE', str(nmr_freq3), nmr_freq3 * 1e6, noe_3, None, None, 1, 2, 3, 4, 5, 6, None]]

    HETNUC = hetero

    # [file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, sep]
    SEQ_ARGS = [noe_1, None, None, 2, 3, 4, 5, None]

    # The diffusion model.
    DIFF_MODEL = model

    # The heteronucleus atom name corresponding to that of the PDB file (used if the spin name is not in the sequence data).
    HET_NAME = hetero

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

    # Minimisation Options
    MIN_OPT = ('back', 'gmw')

    # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
    MC_NUM = 500

    # Automatic looping over all rounds until convergence (must be a boolean value of True or False).
    CONV_LOOP = True

    # Execute the automatic model-free protocol.
    dAuvergne_protocol(diff_model=DIFF_MODEL, mf_models=MF_MODELS, local_tm_models=LOCAL_TM_MODELS, pdb_file=PDB_FILE, seq_args=SEQ_ARGS, het_name=HET_NAME, relax_data=RELAX_DATA, unres=UNRES, exclude=EXCLUDE, bond_length=BOND_LENGTH, csa=CSA, hetnuc=HETNUC, proton=PROTON, grid_inc=GRID_INC, min_algor=MIN_ALGOR, mc_num=MC_NUM, conv_loop=CONV_LOOP)

    #create results file
    if model == 'final':
        results_analysis = model_free_results(self)
        return results_analysis     # return data for results table dialog

    # return successful value to automatic mode to proceed to next step
    if automatic == True:
        return 'successful'

    # Feedback about successful Calculation in manual mode and after final calculation in autamatic mode
    if not automatic:
        if model == 'local_tm':
            relax_run_ok('Local Tm calculation was successful !')

            # enable m1 - m5 to choose for calculation
            return True

        if model == 'sphere':
            relax_run_ok('Sphere calculation was successful !')
        if model == 'prolate':
            relax_run_ok('Prolate calculation was successful !')
        if model == 'oblate':
            relax_run_ok('Oblate calculation was successful !')
        if model == 'ellipsoid':
            relax_run_ok('Ellipsoid calculation was successful !')
        if model == 'Final':
            relax_run_ok('Final Model-free calculation was successful !')



class RedirectText(object):
    """Class to redirect relax output to relaxGUI - log panel and progress bar."""

    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl
 
    def write(self,string):
        global progress

        wx.CallAfter(self.out.log_panel.WriteText, string)
        time.sleep(0.001)  # allow relaxGUI log panel to get refreshed

        # split print out into list
        a = str(string)
        check = []
        check = a.split()
        
        # update progress bar
        if 'Simulation' in string:          
            add = round(progress)
            add_int = int(add)
            wx.CallAfter(self.out.progress_bar.SetValue, add_int)
            progress = ( (int(check[1]) * 100) / float(montecarlo + 6)) + 5
            time.sleep(0.001)  # allow relaxGUI progressbar to get refreshed
