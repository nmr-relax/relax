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
from pipe_control.mol_res_spin import spin_loop

# Test if running as script or through GUI.
is_script = False
if not hasattr(cdp, "pipe_type"):
    is_script = True
    # We need to create a data pipe, which will tell relax which type of data we are expecting 
    pipe_name = 'relax_disp'
    pipe_bundle = 'relax_disp'
    pipe.create(pipe_name, pipe_bundle)

# Minimum: Just read the sequence data, but this misses a lot of information.
sequence.read(file='residues.txt', res_num_col=1)

# Name the spins
for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
    spin.name(name="HN", spin_id=spin_id)
    # Manually force the model to be R2eff, so plotting can be performed later
    cur_spin.model = "R2eff"

# Name the isotope for field strength scaling.
spin.isotope(isotope='15N')


# Open the settings file
set_file = open("exp_settings.txt")
set_file_lines = set_file.readlines()

for line in set_file_lines:
    if "#" in line[0]:
        continue

    # Get data
    field, RF_field_strength_kHz, f_name = line.split()

    # Assign data
    spec_id = f_name
    relax_disp.exp_type(spectrum_id=spec_id, exp_type='R1rho')

    # Set the spectrometer frequency
    spectrometer.frequency(id=spec_id, frq=float(field), units='MHz')

    # Is in kHz, som convert to Hz
    #http://wiki.nmr-relax.com/Relax_disp.spin_lock_offset%2Bfield
    #http://www.nmr-relax.com/manual/relax_disp_spin_lock_field.html
    disp_frq = float(RF_field_strength_kHz)*1000

    # Set The spin-lock field strength, nu1, in Hz
    relax_disp.spin_lock_field(spectrum_id=spec_id, field=disp_frq)

    # Read the R2eff data
    relax_disp.r2eff_read(id=spec_id, file=f_name, dir=None, disp_frq=disp_frq, res_num_col=1, data_col=2, error_col=3)

    # Is this necessary? The time, in seconds, of the relaxation period.
    #relax_disp.relax_time(spectrum_id=spec_id, time=time_sl)


# Plot data
relax_disp.plot_disp_curves(dir='grace', y_axis='r2_eff', x_axis='disp', num_points=1000, extend_hz=500.0, extend_ppm=500.0, interpolate='disp', force=True)

state.save("temp_state", force=True)


# Do it through script
#if False:
#if True:
if is_script:
    # Deselect spin 51, due to weid data point
    #deselect.spin(spin_id=":51@HN", change_all=False)

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
    result_dir_name = os.getcwd() + os.sep + "results"
    # Which models to analyse ?
    #MODELS = [MODEL_R2EFF, MODEL_NOREX, MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MP05, MODEL_NS_R1RHO_2SITE]
    #MODELS = [MODEL_R2EFF, MODEL_NOREX]
    # R2EFF shall be skipped here
    #MODELS = [MODEL_NOREX]
    # http://wiki.nmr-relax.com/M61
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