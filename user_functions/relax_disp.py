###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
"""The relax_disp user function definitions."""

# Python module imports.
import dep_check
if dep_check.wx_module:
    from wx import FD_OPEN, FD_SAVE
else:
    FD_OPEN = -1
    FD_SAVE = -1

# relax module imports.
from pipe_control import spectrum
from pipe_control.mol_res_spin import get_spin_ids
from graphics import ANALYSIS_IMAGE_PATH, WIZARD_IMAGE_PATH
from specific_analyses.relax_disp.cpmgfit import cpmgfit_execute, cpmgfit_input
from specific_analyses.relax_disp.disp_data import cpmg_frq, relax_time, spin_lock_field
from specific_analyses.relax_disp.nessy import nessy_input
from specific_analyses.relax_disp.sherekhan import sherekhan_input
from specific_analyses.relax_disp.variables import MODEL_CR72, MODEL_LM63, MODEL_R2EFF
from specific_analyses.setup import relax_disp_obj
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('relax_disp')
uf_class.title = "Class for relaxation curve fitting."
uf_class.menu_text = "&relax_disp"
uf_class.gui_icon = "relax.relax_disp"


# The relax_disp.cluster user function.
uf = uf_info.add_uf('relax_disp.cluster')
uf.title = "Define clusters of spins for joint optimisation."
uf.title_short = "Spin clustering."
uf.add_keyarg(
    name = "cluster_id",
    py_type = "str",
    desc_short = "cluster ID",
    desc = "The cluster identification string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_disp_obj._cluster_ids
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identifier string for the spin or group of spins to add to the cluster.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("In a relaxation dispersion analysis, the parameters of the model of dispersion can either be optimised for each spin system separately or a number of spins can be grouped or clustered and the dispersion model parameters optimised for all spins in the cluster together.  Clusters are identified by unique ID strings.  Any spins not within a cluster will be optimised separately and individually.")
uf.desc[-1].add_paragraph("If the cluster ID string already exists, the spins will be added to that pre-existing cluster.  If no spin ID is given, then all spins will be added to the cluster.")
uf.desc[-1].add_paragraph("The special cluster ID string 'free spins' is reserved for the pool of non-clustered spins.  This can be used to remove a spin system from an already existing cluster by specifying this cluster ID and the desired spin ID.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To add the spins ':1@N' and ':3@N' to a new cluster called 'cluster', type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.cluster('cluster', ':1,3@N)")
uf.desc[-1].add_prompt("relax> relax_disp.cluster(cluster_id='cluster', spin_id=':1,3@N)")
uf.backend = relax_disp_obj._cluster
uf.menu_text = "c&luster"
uf.wizard_height_desc = 500
uf.wizard_size = (800, 600)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.cpmg_frq user function.
uf = uf_info.add_uf('relax_disp.cpmg_frq')
uf.title = "Set the CPMG frequency associated with a given spectrum."
uf.title_short = "CPMG frequency setting."
uf.add_keyarg(
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum ID string",
    desc = "The spectrum ID string to associate the CPMG frequency to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "cpmg_frq",
    py_type = "num",
    desc_short = "CPMG frequency (Hz)",
    desc = "The frequency, in Hz, of the CPMG pulse train.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the CPMG pulse train frequency of a given spectrum to be set.  If None is given for frequency, then the spectrum will be treated as a reference spectrum.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To identify the reference spectrum called 'reference_spectrum', type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.cpmg_frq(None, 'reference_spectrum')")
uf.desc[-1].add_prompt("relax> relax_disp.cpmg_frq(cpmg_frq=None, spectrum_id='reference_spectrum')")
uf.desc[-1].add_paragraph("To set a frequency of 200 Hz for the spectrum '200_Hz_spectrum', type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.cpmg_frq(200, '200_Hz_spectrum')")
uf.desc[-1].add_prompt("relax> relax_disp.cpmg_frq(cpmg_frq=200, spectrum_id='200_Hz_spectrum')")
uf.backend = cpmg_frq
uf.menu_text = "&cpmg_frq"
uf.wizard_size = (800, 500)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.cpmgfit_execute user function.
uf = uf_info.add_uf('relax_disp.cpmgfit_execute')
uf.title = "Optimisation of the CPMG data using Art Palmer's CPMGFit program."
uf.title_short = "CPMGFit execution."
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory containing all of the CPMGFit input files.  If not given, this defaults to the model name in lower case.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause the results files to be overwritten if they already exist."
)
uf.add_keyarg(
    name = "binary",
    default = "cpmgfit",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "CPMGFit executable file",
    desc = "The name of the executable CPMGFit program file.",
    wiz_filesel_style = FD_OPEN,
    wiz_filesel_preview = False
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("CPMGFit will be executed once per spin as:")
uf.desc[-1].add_prompt("$ cpmgfit -grid -xmgr -f dir/spin_x.in | tee dir/spin_x.out")
uf.desc[-1].add_paragraph("where x is replaced by each spin ID string.  If you would like to use a different CPMGFit executable file, change the binary name to the appropriate file name.  If the file is not located within the environment's path, be sure to include the full path in front of the binary file name so it can be found.")
uf.backend = cpmgfit_execute
uf.menu_text = "&cpmgfit_execute"
uf.gui_icon = "oxygen.categories.applications-education"
uf.wizard_size = (800, 600)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.cpmgfit_input user function.
uf = uf_info.add_uf('relax_disp.cpmgfit_input')
uf.title = "Create the input files for Art Palmer's CPMGFit program."
uf.title_short = "CPMGFit input file creation."
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory to place the files.  If not given, this defaults to the model name in lower case.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause the files to be overwritten if they already exist."
)
uf.add_keyarg(
    name = "binary",
    default = "cpmgfit",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "CPMGFit executable file",
    desc = "The name of the executable CPMGFit program file.",
    wiz_filesel_style = FD_OPEN,
    wiz_filesel_preview = False
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identification string.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The following files are created:")
uf.desc[-1].add_list_element("'dir/spin_x.in',")
uf.desc[-1].add_list_element("'dir/run.sh'.")
uf.desc[-1].add_paragraph("One CPMGFit input file is created per spin and named 'dir/spin_x.in', where x is the spin ID string.  The file 'dir/run.sh' is a batch file for executing CPMGFit for all of the spin input files.  If you would like to use a different CPMGFit executable file, change the binary name to the appropriate file name.  If the file is not located within the environment's path, be sure to include the full path in front of the binary name so it can be found.")
uf.backend = cpmgfit_input
uf.menu_text = "&cpmgfit_input"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_size = (800, 600)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.exp_type user function.
uf = uf_info.add_uf('relax_disp.exp_type')
uf.title = "Select the type of relaxation dispersion experiments to be analysed."
uf.title_short = "Relaxation dispersion experiment type selection."
uf.add_keyarg(
    name = "exp_type",
    default = "cpmg",
    py_type = "str",
    desc_short = "experiment type",
    desc = "The type of relaxation dispersion experiment performed.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "CPMG",
        "CPMG, fixed time",
        "R1rho"
    ],
    wiz_combo_data = [
        "cpmg",
        "cpmg fixed",
        "r1rho"
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The currently supported experiments include:")
uf.desc[-1].add_item_list_element("'cpmg'", "The CPMG family of experiments whereby spectra consist of exponential curves by varying the total time of the CPMG block of pulses,")
uf.desc[-1].add_item_list_element("'cpmg fixed'", "The CPMG family of experiments whereby the time period for the block of CPMG pulses is fixed and a reference spectrum is present,")
uf.desc[-1].add_item_list_element("'r1rho'", "The R1rho family of experiments whereby spectra consist of exponential curves by varying the total time in which the spin-lock field is applied.")
uf.desc[-1].add_paragraph("For the 'cpmg' and 'r1rho' experiment types, 2-parameter exponentials will be fit to obtain R2,eff for each spin system as part of the optimisation of the dispersion model.")
uf.desc[-1].add_paragraph("For the 'cpmg fixed' experiment type, the R2,eff values are directly calculated prior to optimisation using the formula:")
uf.desc[-1].add_verbatim("""
                        -1         / I1(nu_CPMG) \ 
    R2,eff(nu_CPMG) = ------- * ln | ----------- |,
                      relax_T      \     I0      /
""")
uf.desc[-1].add_paragraph("where nu_CPMG is the CPMG frequency in Hz, relax_T is the fixed delay time, I0 is the reference peak intensity when relax_T is zero, and I1 is the peak intensity in a spectrum for a given nu_CPMG frequency.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To pick the experiment type 'cpmg' for all selected spins, type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.exp_type('cpmg')")
uf.desc[-1].add_prompt("relax> relax_disp.exp_type(exp_type='cpmg')")
uf.backend = relax_disp_obj._exp_type
uf.menu_text = "&exp_type"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 700)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.nessy_input user function.
uf = uf_info.add_uf('relax_disp.nessy_input')
uf.title = "Create the input files for Michael Bieri's NESSY program."
uf.title_short = "NESSY input file creation."
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory to place the file and to use as the NESSY project directory.  If not given, this defaults to the current directory.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause the files to be overwritten if they already exist."
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identification string.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will create a single NESSY save file called 'save.NESSY'.  This will contain all of the dispersion data currently loaded in the relax data store.  If the directory name is not supplied, this will default to the current directory.")
uf.backend = nessy_input
uf.menu_text = "&nessy_input"
uf.gui_icon = "relax.nessy"
uf.wizard_size = (800, 600)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'nessy.png'


# The relax_disp.plot_disp_curves user function.
uf = uf_info.add_uf('relax_disp.plot_disp_curves')
uf.title = "Create 2D Grace plots of the dispersion curves for each spin system."
uf.title_short = "Dispersion curve plotting."
uf.add_keyarg(
    name = "dir",
    default = "grace",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name to place all of the spin system files into.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which, if set to True, will cause the files to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is used to created 2D Grace plots of the dispersion curves of the spin-lock field strength or nu_CPMG frequencies verses R2eff/R1rho.  One file will be created per spin system with the name 'disp_x.agr', where x is the spin ID string.")
uf.backend = relax_disp_obj._plot_disp_curves
uf.menu_text = "&plot_disp_curves"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'grace.png'


# The relax_disp.plot_exp_curves user function.
uf = uf_info.add_uf('relax_disp.plot_exp_curves')
uf.title = "Create 2D Grace plots of the exponential curves."
uf.title_short = "Exponential curve plotting."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file.",
    wiz_filesel_wildcard = "Grace files (*.agr)|*.agr;*.AGR",
    wiz_filesel_style = FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    default = "grace",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which, if set to True, will cause the file to be overwritten."
)
uf.add_keyarg(
    name = "norm",
    default = False,
    py_type = "bool",
    desc_short = "normalisation flag",
    desc = "A flag which, if set to True, will cause all graphs to be normalised to a starting value of 1.  This is for the normalisation of series type data."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is used to created 2D Grace plots of the individual exponential curves used to find the R2eff or R1rho values.  This supplements the grace.write user function which is not capable of generating these curves in a reasonable format.")
uf.backend = relax_disp_obj._plot_exp_curves
uf.menu_text = "&plot_exp_curves"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'grace.png'


# The relax_disp.r2eff_setup user function.
uf = uf_info.add_uf('relax_disp.r2eff_setup')
uf.title = "Setup for the R2eff/R1rho model."
uf.title_short = "R2eff/R1rho model setup."
uf.add_keyarg(
    name = "sim_num",
    default = 100000,
    min = 3,
    max = 1000000000,
    py_type = "int",
    desc_short = "Bootstrapping simulation number",
    desc = "The number of Bootstrapping simulations for error propagation."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is used to setup the variables required for the calculation of the R2eff/R1rho values.  Currently only the number of Bootstrapping simulations for error propagation needs to be given.  This is only required for calculating the R2eff/R1rho values for fixed relaxation time period data, if full relaxation curves have been collected then this value will be ignored.")
uf.backend = relax_disp_obj._r2eff_setup
uf.menu_text = "&r2eff_setup"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_size = (800, 500)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'
uf.wizard_apply_button = False


# The relax_disp.relax_time user function.
uf = uf_info.add_uf('relax_disp.relax_time')
uf.title = "Set the relaxation delay time associated with each spectrum."
uf.title_short = "Relaxation delay time setting."
uf.add_keyarg(
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum ID string",
    desc = "The spectrum ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "time",
    default = 0.0,
    py_type = "num",
    desc_short = "relaxation time",
    desc = "The time, in seconds, of the relaxation period."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Peak intensities should be loaded before calling this user function via the spectrum.read_intensities user function.  The intensity values will then be associated with a spectrum identifier.  To associate each spectrum identifier with a time point in the relaxation curve prior to optimisation, this user function should be called.")
uf.backend = relax_time
uf.menu_text = "&relax_time"
uf.gui_icon = "oxygen.actions.chronometer"
uf.wizard_size = (800, 500)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.select_model user function.
uf = uf_info.add_uf('relax_disp.select_model')
uf.title = "Select the relaxation dispersion model."
uf.title_short = "Relaxation dispersion model setup."
uf.display = True
uf.add_keyarg(
    name = "model",
    default = MODEL_R2EFF,
    py_type = "str",
    desc_short = "dispersion model",
    desc = "The type of relaxation dispersion model to fit.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "%s: {R2eff/R1rho, I0}" % MODEL_R2EFF,
        "%s: {R20, phi_ex, kex}" % MODEL_LM63,
        "%s: {R2A, kA, dw}" % MODEL_CR72
    ],
    wiz_combo_data = [
        MODEL_R2EFF,
        MODEL_LM63,
        MODEL_CR72
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("A number of different dispersion models are supported.  These models are dependent upon whether the data originates from a CPMG-type or R1rho-type experiment.  For the CPMG-type experiments, the models currently supported are:")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_R2EFF, "This is the model used to determine the R2eff values and errors required as the base data for all other models,")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_LM63, "The original Luz and Meiboom (1963) 2-site fast exchange equation with parameters {R20, phi_ex, kex},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_CR72, "The Carver and Richards (1972) 2-site equation for all time scales with parameters {R2A, kA, dw}.")
uf.desc[-1].add_paragraph("For the R1rho-type experiment, the currently supported models are:")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_R2EFF, "This is the same model model as for the CPMG-type experiments except that the R1rho and not R2eff values are determined.")
uf.desc[-1].add_paragraph("Except for '%s', these CPMG and R1rho models are fit to clusterings of spins, or spin blocks.  The models are described in more detail below." % MODEL_R2EFF)
# Exp-fit model.
uf.desc.append(Desc_container("The R2eff model"))
uf.desc[-1].add_paragraph("This is the simplest of all models in that the dispersion part is not modelled.  It is used to determine the R2eff or R1rho values and errors which are required as the base data for all other models.  It can be selected by setting the model to '%s'.  Depending on the experiment type, this model will be handled differently.  The R2eff/R1rho values determined can be later copied to the data pipes of the other dispersion models using the appropriate value user function." % MODEL_R2EFF)
uf.desc[-1].add_paragraph("For the fixed relaxation time period CPMG-type experiments, the R2eff values are determined by direct calculation using the formula:")
uf.desc[-1].add_verbatim("""\
                        -1         / I1(nu_CPMG) \ 
    R2,eff(nu_CPMG) = ------- * ln | ----------- | ,
                      relax_T      \     I0      /\
""")
uf.desc[-1].add_paragraph("where nu_CPMG is the CPMG frequency in Hz, equal to:")
uf.desc[-1].add_verbatim("""\
                  1
    nu_CPMG = ---------- ,
              2 tau_CPMG\
""")
uf.desc[-1].add_paragraph("relax_T is the fixed delay time, I0 is the reference peak intensity when relax_T is zero, and I1 is the peak intensity in a spectrum for a given nu_CPMG frequency.  Errors are determined via bootstrapping.  The values and errors are determined with a single call of the calc user function.  The R1rho version of the equation is essentially the same:")
uf.desc[-1].add_verbatim("""\
                   -1         / I1(nu1) \ 
    R1rho(nu1) = ------- * ln | ------- | ,
                 relax_T      \   I0    /\
""")
uf.desc[-1].add_paragraph("where I1 is the peak intensity in a spectrum for a given spin-lock field strength nu1.")
uf.desc[-1].add_paragraph("For the variable relaxation time period type experiments, the R2eff/R1rho values are determined by fitting to the simple two parameter exponential as in a R1 or R2 analyses.  Both R2eff/R1rho and the initial peak intensity I0 are optimised using the minimise user function for each exponential curve separately.  Monte Carlo simulations are used to obtain the parameter errors.")
# LM63 model.
uf.desc.append(Desc_container("The LM63 2-site fast exchange CPMG model"))
uf.desc[-1].add_paragraph("This is the original model for 2-site fast exchange for CPMG-type experiments.  It is selected by setting the model to '%s', here named after Luz and Meiboom 1963.  The equation for the exchange process is:" % MODEL_LM63)
uf.desc[-1].add_verbatim("""\
                  phi_ex   /     4 * nu_cpmg         /     kex     \ \ 
    R2eff = R20 + ------ * | 1 - -----------  * tanh | ----------- | | ,
                   kex     \         kex             \ 4 * nu_cpmg / /\
""")
uf.desc[-1].add_paragraph("where:")
uf.desc[-1].add_verbatim("""\
    phi_ex = pA * pB * delta_omega^2 ,\
""")
uf.desc[-1].add_paragraph("kex is the chemical exchange rate constant, pA and pB are the populations of states A and B, and delta_omega is the chemical shift difference between the two states.")
uf.desc[-1].add_paragraph("The reference for this equation is:")
uf.desc[-1].add_list_element("Luz, S. and Meiboom S., 1963, Nuclear Magnetic Resonance study of protolysis of trimethylammonium ion in aqueous solution - order of reaction with respect to solvent, J. Chem. Phys. 1963, 39, 366-370 (DOI: 10.1063/1.1734254).")
# CR72 model.
uf.desc.append(Desc_container("The CR72 2-site CPMG model"))
uf.desc[-1].add_paragraph("This is the model for 2-site exchange on all times scales, named after Carver and Richards 1972.  Is it selected by setting the model to '%s'.  The equation is:" % MODEL_CR72)
uf.desc[-1].add_verbatim("""\
    R2eff = 1/2 [ R2A0 + R2B0  + kex - 2 * nu_cpmg cosh^-1 (D+ * cosh(eta+) - D- * cos(eta-) ] ,\
""")
uf.desc[-1].add_paragraph("where:")
uf.desc[-1].add_verbatim("""\
           1 /        Psi + 2delta_omega^2 \ 
    D+/- = - | +/-1 + -------------------- | ,
           2 \        sqrt(Psi^2 + zeta^2) /

             2^(2/3)
    eta+/- = ------- sqrt(+/-Psi + sqrt(Psi^2 + zeta^2)) ,
             nu_cpmg

    Psi = (R2A0 - R2B0 - pA.kex + pB.kex)^2 - delta_omega^2 + 4pA.pB.kex^2 ,

    zeta = 2delta_omega (R2A0 - R2B0 - pA.kex + pB.kex).\
""")
uf.desc[-1].add_paragraph("The reference for this equation is:")
uf.desc[-1].add_list_element("Carver, J. P. and Richards, R. E., 1972, General 2-site solution for chemical exchange produced dependence of T2 upon Carr-Purcell pulse separation. JMR, 6, 89-105 (DOI: 10.1016/0022-2364(72)90090-X).")
# 2-site slow model.
#uf.desc.append(Desc_container("The 2-site slow model"))
#uf.desc[-1].add_paragraph("This is selected by setting the model to '%s'.  The equation for slow exchange is:" % SLOW_2SITE)
#uf.desc[-1].add_verbatim("""\
#                       /     /      dw      \   4 * cpmg_frq \ 
#    R2eff = R2A + kA - | sin | ------------ | * ------------ |
#                       \     \ 4 * cpmg_frq /        dw      /\
#""")
#uf.desc[-1].add_paragraph("where:")
#uf.desc[-1].add_verbatim("""\
#    cpmg_frq = 1 / ( 4 * cpmg_tau )\
#""")
#uf.desc[-1].add_paragraph("The reference for this equation is:")
#uf.desc[-1].add_list_element("Tollinger et al., JACS, 2001, 123: 11341-11352 (equation 2).")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To pick the 2-site fast exchange model for all selected spins, type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.select_model('%s')" % MODEL_LM63)
uf.desc[-1].add_prompt("relax> relax_disp.select_model(model='%s')" % MODEL_LM63)
uf.backend = relax_disp_obj._select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 700)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.sherekhan_input user function.
uf = uf_info.add_uf('relax_disp.sherekhan_input')
uf.title = "Create the input files for Adam Mazur's ShereKhan program."
uf.title_short = "ShereKhan input file creation."
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory to place the files.  If not given, this defaults to the model name in lower case.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause the files to be overwritten if they already exist."
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identification string.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This creates the files required for the ShereKhan server located at http://sherekhan.bionmr.org/.  One file per field strength will be created.  These will be named 'dir/sherekhan_x.in', where x is a number starting from 1 and dir is the specified directory which if not given defaults to the model name in lower case.")
uf.backend = sherekhan_input
uf.menu_text = "&sherekhan_input"
uf.gui_icon = "relax.sherekhan"
uf.wizard_size = (800, 500)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'sherekhan.png'


# The relax_disp.spin_lock_field user function.
uf = uf_info.add_uf('relax_disp.spin_lock_field')
uf.title = "Set the relaxation dispersion spin-lock field strength (nu1)."
uf.title_short = "Spin-lock field strength."
uf.add_keyarg(
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum ID string",
    desc = "The spectrum ID string to associate the spin-lock field strength to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "field",
    py_type = "num",
    desc_short = "field strength nu1 (Hz)",
    desc = "The spin-lock field strength, nu1, in Hz."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This sets the spin-lock field strength, nu1, for the specified R1rho spectrum in Hertz.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set a spin-lock field strength of 2.1 kHz for the spectrum 'nu1_2.1kHz_relaxT_0.010', type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.spin_lock_field(2100, 'nu1_2.1kHz_relaxT_0.010')")
uf.desc[-1].add_prompt("relax> relax_disp.spin_lock_field(field=2100, spectrum_id='nu1_2.1kHz_relaxT_0.010')")
uf.backend = spin_lock_field
uf.menu_text = "spin_lock_&field"
uf.wizard_size = (800, 500)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'
