###############################################################################
#                                                                             #
# Copyright (C) 2015 Troels E. Linnet                                         #
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

# relax import
from pipe_control.mol_res_spin import generate_spin_string, return_spin, spin_loop

import os

# Load the final state with all pipes
state.load(os.getcwd() + os.sep + "results" + os.sep + "final_state", force=True)

# Now simulate that all spins are first deselected, and then selected.
deselect.all()
sel_ids = [
":2",
":51",
]

for sel_spin in sel_ids:
    print("Selecting spin %s"%sel_spin)
    select.spin(spin_id=sel_spin, change_all=False)
 
# Inspect which residues should be analysed together for a clustered/global fit.
cluster_ids = sel_ids
 
# Cluster spins
for curspin in cluster_ids:
    print("Adding spin %s to cluster"%curspin)
    relax_disp.cluster('model_cluster', curspin)
 
# Show the pipe
print("\nPrinting all the available pipes.")
pipe.display()
 
# Get the selected models
print("\nChecking which model is stored per spin.")
for curspin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=False):
    print("For spin_id '%s the model is '%s''"%(spin_id, curspin.model))
 
# Copy pipe and switch to it.
pipe.copy(pipe_from="final - relax_disp", pipe_to="relax_disp_cluster", bundle_to="relax_disp_cluster")
pipe.switch(pipe_name="relax_disp_cluster")
pipe.display()
  

# Do it through script
#if False:
if True:
#if is_script:
    import os
    from auto_analyses import relax_disp as aa_relax_disp
    from lib.dispersion.variables import EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_PROTON_MQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_ZQ, EXP_TYPE_LIST, EXP_TYPE_R1RHO, MODEL_B14_FULL, MODEL_CR72, MODEL_CR72_FULL, MODEL_DPL94, MODEL_IT99, MODEL_LIST_ANALYTIC_CPMG, MODEL_LIST_FULL, MODEL_LIST_NUMERIC_CPMG, MODEL_LM63, MODEL_M61, MODEL_M61B, MODEL_MP05, MODEL_NOREX, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR, MODEL_PARAMS, MODEL_R2EFF, MODEL_TP02, MODEL_TAP03
    # Number of grid search increments.  If set to None, then the grid search will be turned off and the default parameter values will be used instead.
    #GRID_INC = None
    GRID_INC = 21
    # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
    MC_NUM = 3
    # Model selection technique.
    MODSEL = 'AIC'
    result_dir_name = os.getcwd() + os.sep + "results_cluster"
    # Which models to analyse ?
    #MODELS = [MODEL_R2EFF, MODEL_NOREX, MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MP05, MODEL_NS_R1RHO_2SITE]
    #MODELS = [MODEL_R2EFF, MODEL_NOREX]
    # R2EFF shall be skipped here
    #MODELS = [MODEL_NOREX]
    # http://wiki.nmr-relax.com/M61
    pipe_name = 'relax_disp_cluster'
    pipe_bundle = 'relax_disp_cluster'
    MODELS = [MODEL_NOREX, MODEL_M61]

    # Fit, instead of read
    #r1_fit = True
    r1_fit = False

    # Set the initial guess from the minimum R2eff point
    set_grid_r20=True

    """
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
        @keyword exp_mc_sim_num:            The number of Monte Carlo simulations for the error analysis in the 'R2eff' model when exponential curves are fitted.  This defaults to the value of the mc_sim_num argument when not given.  When set to '-1', the R2eff errors are estimated from the Covariance matrix.  For the 2-point fixed-time calculation for the 'R2eff' model, this argument is ignored.
        @type exp_mc_sim_num:               int or None
        @keyword modsel:                    The model selection technique to use in the analysis to determine which model is the best for each spin cluster.  This can currently be one of 'AIC', 'AICc', and 'BIC'.
        @type modsel:                       str
        @keyword pre_run_dir:               The optional directory containing the dispersion auto-analysis results from a previous run.  The optimised parameters from these previous results will be used as the starting point for optimisation rather than performing a grid search.  This is essential for when large spin clusters are specified, as a grid search becomes prohibitively expensive with clusters of three or more spins.  At some point a RelaxError will occur because the grid search is impossibly large.  For the cluster specific parameters, i.e. the populations of the states and the exchange parameters, an average value will be used as the starting point.  For all other parameters, the R20 values for each spin and magnetic field, as well as the parameters related to the chemical shift difference dw, the optimised values of the previous run will be directly copied.
        @type pre_run_dir:                  None or str
        @keyword optimise_r2eff:            Flag to specify if the read previous R2eff results should be optimised.  For R1rho models where the error of R2eff values are determined by Monte-Carlo simulations, it can be valuable to make an initial R2eff run with a high number of Monte-Carlo simulations.  Any subsequent model analysis can then be based on these R2eff values, without optimising the R2eff values.
        @type optimise_r2eff:               bool
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
        @keyword r1_fit:                    A flag which if True will activate R1 parameter fitting via relax_disp.r1_fit for the models that support it.  If False, then the relax_disp.r1_fit user function will not be called.
    """


    # Go
    aa_relax_disp.Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=result_dir_name, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM, exp_mc_sim_num=None, modsel=MODSEL,  pre_run_dir=None, optimise_r2eff=False, insignificance=0.0, numeric_only=False, mc_sim_all_models=False, eliminate=True, set_grid_r20=set_grid_r20, r1_fit=r1_fit)


# Get the clustered fitted values
print("\nChecking which value is stored per spin.")
for curspin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=False):
    if hasattr(curspin, "kex"):
        print("For spin_id %s the kex is %.3f"%(spin_id, curspin.kex))
