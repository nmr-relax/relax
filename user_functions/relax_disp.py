###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
from os import sep
if dep_check.wx_module:
    from wx import FD_OPEN, FD_SAVE
else:
    FD_OPEN = -1
    FD_SAVE = -1

# relax module imports.
from lib.text.gui import dw, dw_AB, dw_BC, dwH, dwH_AB, dwH_BC, i0, kex, kAB, kBC, kAC, phi_ex, phi_exB, phi_exC, nu_1, nu_cpmg, r1rho, r1rho_prime, r1, r2, r2a, r2b, r2eff, tex, theta, w_eff, w_rf
from graphics import ANALYSIS_IMAGE_PATH, WIZARD_IMAGE_PATH
from pipe_control import pipes, spectrum
from pipe_control.mol_res_spin import get_spin_ids
from specific_analyses.relax_disp.catia import catia_execute, catia_input
from specific_analyses.relax_disp.cpmgfit import cpmgfit_execute, cpmgfit_input
from specific_analyses.relax_disp.estimate_r2eff import estimate_r2eff_err
from specific_analyses.relax_disp.data import cpmg_setup, insignificance, plot_disp_curves, plot_exp_curves, r2eff_read, r2eff_read_spin, relax_time, set_exp_type, r20_from_min_r2eff, spin_lock_field, spin_lock_offset, write_disp_curves
from specific_analyses.relax_disp.data import INTERPOLATE_DISP, INTERPOLATE_OFFSET, X_AXIS_DISP, X_AXIS_W_EFF, X_AXIS_THETA, Y_AXIS_R2_R1RHO, Y_AXIS_R2_EFF
from specific_analyses.relax_disp.nessy import nessy_input
from specific_analyses.relax_disp.parameters import copy
from specific_analyses.relax_disp.sherekhan import sherekhan_input
from specific_analyses.relax_disp.variables import EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_ZQ, EXP_TYPE_CPMG_PROTON_MQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_R1RHO, MODEL_B14, MODEL_B14_FULL, MODEL_CR72, MODEL_CR72_FULL, MODEL_DPL94, MODEL_IT99, MODEL_LIST_FIT_R1, MODEL_LM63, MODEL_LM63_3SITE, MODEL_M61, MODEL_M61B, MODEL_MMQ_CR72, MODEL_MP05, MODEL_NOREX, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR, MODEL_R2EFF, MODEL_TAP03, MODEL_TP02, MODEL_TSMFK01
from specific_analyses.relax_disp import uf as relax_disp_uf
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container
from user_functions.wildcards import WILDCARD_GRACE_ALL


# The user function class.
uf_class = uf_info.add_class('relax_disp')
uf_class.title = "Class for relaxation curve fitting."
uf_class.menu_text = "&relax_disp"
uf_class.gui_icon = "relax.relax_disp"


# The relax_disp.catia_execute user function.
uf = uf_info.add_uf('relax_disp.catia_execute')
uf.title = "Perform a relaxation dispersion optimisation using Flemming Hansen's CATIA."
uf.title_short = "CATIA execution."
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory containing all of the CATIA input files.",
    can_be_none = True
)
uf.add_keyarg(
    name = "binary",
    default = "catia",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "CATIA executable file",
    desc = "The name of the executable CATIA program file.",
    wiz_filesel_style = FD_OPEN,
    wiz_filesel_preview = False
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("CATIA will be executed as")
uf.desc[-1].add_prompt("$ catia < Fit.catia")
uf.desc[-1].add_paragraph("If you would like to use a different CATIA executable file, change the binary name to the appropriate file name.  If the file is not located within the environment's path, include the full path in front of the binary file name.")
uf.backend = catia_execute
uf.gui_icon = "oxygen.categories.applications-education"
uf.menu_text = "catia_e&xecute"
uf.wizard_size = (800, 600)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.catia_input user function.
uf = uf_info.add_uf('relax_disp.catia_input')
uf.title = "Create the input files for Flemming Hansen's CATIA program."
uf.title_short = "CATIA input file creation."
uf.add_keyarg(
    name = "dir",
    default = "catia",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory to place the CATIA input files, output directory, etc.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause the files to be overwritten if they already exist."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will create all of the input file required for CATIA as well as the CATIA results output directory.")
uf.backend = catia_input
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.menu_text = "&catia_input"
uf.wizard_size = (800, 600)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


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
    wiz_combo_iter = relax_disp_uf.cluster_ids
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
uf.desc[-1].add_prompt("relax> relax_disp.cluster('cluster', ':1,3@N')")
uf.desc[-1].add_prompt("relax> relax_disp.cluster(cluster_id='cluster', spin_id=':1,3@N')")
uf.backend = relax_disp_uf.cluster
uf.menu_text = "c&luster"
uf.gui_icon = "relax.cluster"
uf.wizard_height_desc = 500
uf.wizard_size = (800, 600)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.cpmg_setup user function.
uf = uf_info.add_uf('relax_disp.cpmg_setup')
uf.title = "Set the CPMG pulse sequence information associated with a given spectrum."
uf.title_short = "CPMG experiment setup."
uf.add_keyarg(
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum ID string",
    desc = "The spectrum ID string to associate the CPMG pulse sequence information to.",
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
uf.add_keyarg(
    name = "ncyc_even",
    default = True,
    py_type = "bool",
    desc_short = "even ncyc flag",
    desc = "A flag which if True means that the number of CPMG blocks must be even.  This is pulse sequence dependant."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows all information about CPMG pulse sequence required for a relaxation dispersion analysis to be specified.  This includes:")
uf.desc[-1].add_list_element("'cpmg_frq' allows the CPMG pulse train frequency of a given spectrum to be set.  If None is given for frequency, then the spectrum will be treated as a reference spectrum.")
uf.desc[-1].add_list_element("'ncyc_even' specifies if an even number of CPMG blocks are required for the pulse sequence.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To identify the reference spectrum called 'reference_spectrum', type:")
uf.desc[-1].add_prompt("relax> relax_disp.cpmg_setup(spectrum_id='reference_spectrum', cpmg_frq=None)")
uf.desc[-1].add_paragraph("To set a frequency of 200 Hz for the spectrum '200_Hz_spectrum', type:")
uf.desc[-1].add_prompt("relax> relax_disp.cpmg_setup(spectrum_id='200_Hz_spectrum', cpmg_frq=200)")
uf.backend = cpmg_setup
uf.menu_text = "&cpmg_setup"
uf.wizard_size = (900, 600)
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
uf.title = "Select the relaxation dispersion experiment type."
uf.title_short = "Relaxation dispersion experiment type selection."
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
    name = "exp_type",
    default = EXP_TYPE_CPMG_SQ,
    py_type = "str",
    desc_short = "experiment type",
    desc = "The type of relaxation dispersion experiment performed.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "Single quantum (SQ) CPMG-type data",
        "Zero quantum (ZQ) CPMG-type data",
        "Double quantum (DQ) CPMG-type data",
        "Multiple quantum (MQ) CPMG-type data",
        "1H single quantum (SQ) CPMG-type data",
        "1H multiple quantum (SQ) CPMG-type data",
        "%s-type data" % r1rho
    ],
    wiz_combo_data = [
        EXP_TYPE_CPMG_SQ,
        EXP_TYPE_CPMG_ZQ,
        EXP_TYPE_CPMG_DQ,
        EXP_TYPE_CPMG_MQ,
        EXP_TYPE_CPMG_PROTON_SQ,
        EXP_TYPE_CPMG_PROTON_MQ,
        EXP_TYPE_R1RHO
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("For each peak intensity set loaded into relax, the type of experiment it comes from needs to be specified.  By specifying this for each spectrum ID, multiple experiment types can be analysed simultaneously.  This is assuming that an appropriate dispersion model exists for the experiment combination.")
uf.desc[-1].add_paragraph("The currently supported experiments include:")
uf.desc[-1].add_item_list_element(repr(EXP_TYPE_CPMG_SQ), "The single quantum (SQ) CPMG-type experiments,")
uf.desc[-1].add_item_list_element(repr(EXP_TYPE_CPMG_ZQ), "The zero quantum (ZQ) CPMG-type experiments,")
uf.desc[-1].add_item_list_element(repr(EXP_TYPE_CPMG_DQ), "The double quantum (DQ) CPMG-type experiments,")
uf.desc[-1].add_item_list_element(repr(EXP_TYPE_CPMG_MQ), "The multiple quantum (MQ) CPMG-type experiments,")
uf.desc[-1].add_item_list_element(repr(EXP_TYPE_CPMG_PROTON_SQ), "The 1H single quantum (SQ) CPMG-type experiments,")
uf.desc[-1].add_item_list_element(repr(EXP_TYPE_CPMG_PROTON_MQ), "The 1H multiple quantum (MQ) CPMG-type experiments,")
uf.desc[-1].add_item_list_element(repr(EXP_TYPE_R1RHO), "The R1rho-type experiments.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set the experiment type to 'SQ CPMG' for the spectrum ID 'nu_4500.0_800MHz', type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.exp_type('nu_4500.0_800MHz', 'SQ CPMG')")
uf.desc[-1].add_prompt("relax> relax_disp.exp_type(spectrum_id='nu_4500.0_800MHz', exp_type='SQ CPMG')")
uf.backend = set_exp_type
uf.menu_text = "&exp_type"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 600)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.insignificance user function.
uf = uf_info.add_uf('relax_disp.insignificance')
uf.title = "Deselect all spins with insignificant dispersion."
uf.title_short = "Insignificant spin deselection."
uf.add_keyarg(
    name = "level",
    py_type = "float",
    default = 2.0,
    desc_short = "insignificance level",
    desc = "The R2eff/R1rho value in rad/s by which to judge insignificance.  If the maximum difference between two points on all dispersion curves for a spin is less than this value, that spin will be deselected.",
    can_be_none = False
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This can be used to deselect all spins which have insignificant dispersion profiles.  The insignificance value is the R2eff/R1rho value in rad/s by which to judge the dispersion curves by.  If the maximum difference between two points on all dispersion curves for a spin is less than this value, that spin will be deselected.")
uf.backend = insignificance
uf.gui_icon = "relax.spin_grey"
uf.menu_text = "&insignificance"
uf.wizard_size = (800, 550)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'deselect.png'


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


# The relax_disp.parameter_copy user function.
uf = uf_info.add_uf('relax_disp.parameter_copy')
uf.title = "Copy dispersion specific parameters values from one data pipe to another."
uf.title_short = "Dispersion parameter copying."
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "source data pipe",
    desc = "The name of the pipe to copy from.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "pipe_to",
    py_type = "str",
    desc_short = "destination data pipe",
    desc = "The name of the pipe to copy to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is a special function for copying relaxation dispersion parameters from one data pipe to another.  It is much more advanced than the value.copy user function, in that clustering is taken into account.  When the destination data pipe has spin clusters defined, then the new parameter values, when required, will be taken as the median value.")
uf.desc[-1].add_paragraph("For the cluster specific parameters, i.e. the populations of the states and the exchange parameters, a median value will be used as the starting point.  For all other parameters, the R20 values for each spin and magnetic field, as well as the parameters related to the chemical shift difference dw, the optimised values of the previous run will be directly copied.")
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To copy the CSA values from the data pipe 'm1' to 'm2', type:")
uf.desc[-1].add_prompt("relax> value.parameter_copy('m1', 'm2', 'csa')")
uf.backend = copy
uf.menu_text = "&parameter_copy"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_size = (800, 500)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.plot_disp_curves user function.
uf = uf_info.add_uf('relax_disp.plot_disp_curves')
uf.title = "Create 2D Grace plots of the dispersion curves for each spin system."
uf.title_short = "Dispersion curve plotting."
uf.add_keyarg(
    name = "dir",
    default = "grace",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory name to place all of the spin system files into.",
    can_be_none = True
)
uf.add_keyarg(
    name = "y_axis",
    default = Y_AXIS_R2_EFF,
    py_type = "str",
    desc_short = "Y axis data type",
    desc = "Option can be either '%s' which plot 'r2eff' for CPMG experiments or 'r1rho' for R1rho experiments or option can be '%s', which for R1rho experiments plot R2."%(Y_AXIS_R2_EFF, Y_AXIS_R2_R1RHO),
    wiz_element_type = 'combo',
    wiz_combo_choices = [
        "%s/%s for CPMG/%s experiments"%(r2eff, r1rho, r1rho),
        "%s for %s experiments"%(r2, r1rho)
    ],
    wiz_combo_data = [Y_AXIS_R2_EFF, Y_AXIS_R2_R1RHO],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "x_axis",
    default = X_AXIS_DISP,
    py_type = "str",
    desc_short = "X axis data type",
    desc = "Option can be either '%s' which plot 'CPMG frequency (Hz)' for CPMG experiments or 'Spin-lock field strength (Hz)' for R1rho experiments or option can be either '%s' or '%s' for R1rho experiments, which plot 'Effective field in rotating frame (rad/s)' or 'Rotating frame tilt angle theta (rad)'"%(X_AXIS_DISP, X_AXIS_W_EFF, X_AXIS_THETA),
    wiz_element_type = 'combo',
    wiz_combo_choices = [
        "CPMG %s (Hz)/Spin-lock %s (Hz)"%(nu_cpmg, nu_1),
        "Eff. field in rot. frame %s (rad/s)"%(w_eff),
        "Rot. frame tilt ang. %s (rad)"%(theta)
    ],
    wiz_combo_data = [X_AXIS_DISP, X_AXIS_W_EFF, X_AXIS_THETA],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "num_points",
    default = 1000,
    min = 1,
    max = 10000000,
    py_type = "int",
    desc_short = "total number of interpolation points",
    desc = "The total number of points to generate the interpolated dispersion curves with.  This value has no effect for the numeric CPMG-based models.",
    can_be_none = False
)
uf.add_keyarg(
    name = "extend_hz",
    py_type = "num",
    default = 500.0,
    desc_short = "interpolated dispersion curve extension (in Hz)",
    desc = "How far to extend the interpolated dispersion curves beyond the last dispersion point, i.e. the nu_CPMG frequency or spin-lock field strength value, in Hertz.",
    can_be_none = False
)
uf.add_keyarg(
    name = "extend_ppm",
    py_type = "num",
    default = 500.0,
    desc_short = "interpolated offset curve extension (in ppm)",
    desc = "How far to extend the interpolated dispersion curves beyond the last dispersion point, i.e. the spin-lock offset value, in ppm.",
    can_be_none = False
)
uf.add_keyarg(
    name = "interpolate",
    default = INTERPOLATE_DISP,
    py_type = "str",
    desc_short = "option to interpolate the fitted curves",
    desc = "Either by option '%s' which interpolate CPMG frequency or spin-lock field strength, or by option '%s' which interpole over spin-lock offset."%(INTERPOLATE_DISP, INTERPOLATE_OFFSET),
    wiz_element_type = 'combo',
    wiz_combo_choices = [
        "Interpolate CPMG %s (Hz)/Spin-lock %s (Hz)"%(nu_cpmg, nu_1),
        "Interpolate Spin-lock %s (ppm)"%(w_rf)
    ],
    wiz_combo_data = [INTERPOLATE_DISP, INTERPOLATE_OFFSET],
    wiz_read_only = True
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
uf.desc[-1].add_paragraph("This is used to create 2D Grace plots of the dispersion curves of the nu_CPMG frequencies or spin-lock field strength verses the R2eff/R1rho values.  One file will be created per spin system with the name 'disp_x.agr', where x is related to the spin ID string.  For each file, one Grace graph will be produced for each experiment.")
uf.desc[-1].add_paragraph("Four sets of curves of R2eff/R1rho values will be produced per experiment and per magnetic field strength.  These are the experimental values, the fitted values, the interpolated dispersion curves for the fitted solution, and the residuals.  Different dispersion models result in different interpolated dispersion curves.  For the numeric models which use CPMG-type data, the maximum interpolation resolution is constrained by the frequency of a single CPMG block for the entire relaxation period.  For all other models, the interpolation resolution is not constrained and can be as fine as desired by setting the total number of interpolation points.  Interpolated curves are not produced for the 'R2eff' model as they are not necessary.")
uf.desc[-1].add_paragraph("For R1rho models, graphs can be interpolated against Spin-lock offset, but this feature is not available for CPMG experiment types.  It is also possible to select values on X-axis of 'Effective field in rotating frame %s (rad/s)' or 'Rotating frame tilt angle %s (rad)'."%("w_eff", "theta"))
uf.desc[-1].add_paragraph("For R1rho models, special Y-value %s %s can for example be plotted as function of %s.  %s is calculated as: %s=(%s - %s cos^2(%s)) / sin^2(%s)."%("R2", "R1rho", "w_eff", "R2", "R2", "R1rho", "R1", "theta", "theta"))
uf.backend = plot_disp_curves
uf.menu_text = "&plot_disp_curves"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (950, 700)
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
    wiz_filesel_wildcard = WILDCARD_GRACE_ALL,
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
uf.desc[-1].add_paragraph("This is used to create 2D Grace plots of the individual exponential curves used to find the R2eff or R1rho values.  This supplements the grace.write user function which is not capable of generating these curves in a reasonable format.")
uf.backend = plot_exp_curves
uf.menu_text = "&plot_exp_curves"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'grace.png'


# The relax_disp.r1_fit user function.
uf = uf_info.add_uf('relax_disp.r1_fit')
uf.title = "Switch between fixed or fitted R1 values for optimisation."
uf.title_short = "R1 optimisation flag."
uf.add_keyarg(
    name = "fit",
    default = True,
    py_type = "bool",
    desc_short = "R1 optimisation flag",
    desc = "The flag specifying if R1 values should be optimised or if loaded R1 values should be fixed during optimisation."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This user function allows the optimisation of R1 values to be turned on an off for the relaxation dispersion dispersion models.  If turned off, the current values of R1 will be fixed.  Otherwise the R1 values will be added to the model parameter set.  For models which do not support the R1 parameter for off-resonance effects, this setting will have no effect.  Only the models %s support R1 optimisation." % MODEL_LIST_FIT_R1)
uf.backend = relax_disp_uf.r1_fit
uf.menu_text = "r&1_fit"
uf.gui_icon = "oxygen.status.object-locked"
uf.wizard_size = (800, 500)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.r2eff_err_estimate user function.
uf = uf_info.add_uf('relax_disp.r2eff_err_estimate')
uf.title = "Estimate R2eff errors by the Jacobian matrix."
uf.title_short = "Estimate R2eff errors."
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "spin ID to restrict value setting to",
    desc = "The spin ID string to restrict value setting to.",
    can_be_none = True
)
uf.add_keyarg(
    name = "epsrel",
    py_type = "float",
    default = 0.0,
    desc_short = "parameter to remove linear-dependent columns.",
    desc = "The parameter to remove linear-dependent columns when J is rank deficient.",
    can_be_none = False
)
uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "amount of information to print.",
    desc = "The higher the value, the greater the verbosity.",
    can_be_none = False
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is a new experimental feature from version 3.3.")
uf.desc[-1].add_paragraph("This will estimate R2eff errors by using the exponential decay Jacobian matrix 'J' to compute the covariance matrix of the best-fit parameters.")
uf.desc[-1].add_paragraph("This can be an huge time saving step, when performing model fitting in R1rho.  Errors of R2eff values, are normally estimated by time-consuming Monte-Carlo simulations.")
uf.desc[-1].add_paragraph("This method is inspired from the GNU Scientific Library (GSL).")
uf.desc[-1].add_paragraph("The covariance matrix is given by: covar = Qxx = (J^T.W.J)^-1, where the weight matrix W is constructed by the multiplication of an Identity matrix I and a weight array w.  The weight array is 1/errors^2, which then gives W = I.w = I x 1/errors^2.")
uf.desc[-1].add_paragraph("Qxx is computed by QR decomposition, J^T.W.J=QR, Qxx=R^-1. Q^T.  The columns of R which satisfy: |R_{kk}| <= epsrel |R_{11}| are considered linearly-dependent and are excluded from the covariance matrix (the corresponding rows and columns of the covariance matrix are set to zero).")
uf.desc[-1].add_paragraph("The parameter 'epsrel' is used to remove linear-dependent columns when J is rank deficient.")
uf.backend = estimate_r2eff_err
uf.menu_text = "&r2eff_err_estimate"
uf.gui_icon = "relax.relax_fit"
uf.wizard_size = (800, 800)
uf.wizard_image = ANALYSIS_IMAGE_PATH + sep + 'blank_150x150.png'


# The relax_disp.r2eff_read user function.
uf = uf_info.add_uf('relax_disp.r2eff_read')
uf.title = "Read R2eff/R1rho values and errors from a file."
uf.title_short = "R2eff/R1rho value reading."
uf.add_keyarg(
    name = "id",
    py_type = "str",
    desc_short = "partial experiment ID string",
    desc = "The partial experiment ID string to identify this data with.  The full ID string will be constructed as this ID followed by an underscore and then the dispersion point value from the file.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file.",
    wiz_filesel_style = FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name.",
    can_be_none = True
)
uf.add_keyarg(
    name = "disp_frq",
    py_type = "num",
    desc_short = "CPMG frequency or spin-lock field strength (Hz)",
    desc = "For CPMG-type data, the frequency of the CPMG pulse train.  For R1rho-type data, the spin-lock field strength nu1.  The units must be Hertz",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin ID string column",
    desc = "The spin ID string column used by the generic file format (an alternative to the mol, res, and spin name and number columns).",
    can_be_none = True
)
uf.add_keyarg(
    name = "mol_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "molecule name column",
    desc = "The molecule name column used by the generic file format (alternative to the spin ID column).",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_num_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "residue number column",
    desc = "The residue number column used by the generic file format (alternative to the spin ID column).",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "residue name column",
    desc = "The residue name column used by the generic file format (alternative to the spin ID column).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_num_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin number column",
    desc = "The spin number column used by the generic file format (alternative to the spin ID column).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin name column",
    desc = "The spin name column used by the generic file format (alternative to the spin ID column).",
    can_be_none = True
)
uf.add_keyarg(
    name = "data_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "data column",
    desc = "The RDC data column.",
    can_be_none = True
)
uf.add_keyarg(
    name = "error_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "error column",
    desc = "The experimental error column.",
    can_be_none = True
)
uf.add_keyarg(
    name = "sep",
    py_type = "str",
    arg_type = "free format",
    desc_short = "column separator",
    desc = "The column separator used by the generic format (the default is white space).",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will read R2eff/R1rho data directly from a file.  The data will be associated with an experiment ID string.  A partial ID is to be supplied and then the full ID string will be constructed as this ID followed by an underscore and then the dispersion point value from the file (as '%s_%s' % (id, disp_point)).  The full IDs must already exist and have been used to set the type of dispersion experiment the data is from, spectrometer proton frequency of the data, and if needed the time of the relaxation period.")
uf.desc[-1].add_paragraph("The format of this text file must be that each row corresponds to a unique spin system and that there is one file per dispersion point (i.e. per CPMG frequency nu_CPMG or per spin-lock field strength nu1).  The file must be in columnar format and information to identify the spin must be in columns of the file.")
uf.backend = r2eff_read
uf.menu_text = "&r2eff_read"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_size = (1000, 600)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.r2eff_read_spin user function.
uf = uf_info.add_uf('relax_disp.r2eff_read_spin')
uf.title = "Read R2eff/R1rho values and errors for a single spin from a file."
uf.title_short = "Spin R2eff/R1rho value reading."
uf.add_keyarg(
    name = "id",
    py_type = "str",
    desc_short = "experiment ID string",
    desc = "The experiment ID string to identify this data with.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "spin ID string",
    desc = "The spin identification string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file.",
    wiz_filesel_style = FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name.",
    can_be_none = True
)
uf.add_keyarg(
    name = "disp_point_col",
    default = None,
    min = 1,
    py_type = "int",
    desc_short = "dispersion point column",
    desc = "The column containing the CPMG frequency or spin-lock field strength (Hz).",
    can_be_none = True
)
uf.add_keyarg(
    name = "offset_col",
    default = None,
    min = 1,
    py_type = "int",
    desc_short = "offset column",
    desc = "The column containing the offset information for R1rho-type data.",
    can_be_none = True
)
uf.add_keyarg(
    name = "data_col",
    default = 2,
    min = 1,
    py_type = "int",
    desc_short = "R2eff/R1rho data column",
    desc = "The column containing the R2eff or R1rho data."
)
uf.add_keyarg(
    name = "error_col",
    default = 3,
    min = 1,
    py_type = "int",
    desc_short = "R2eff/R1rho error column",
    desc = "The column containing the R2eff or R1rho error."
)
uf.add_keyarg(
    name = "sep",
    py_type = "str",
    desc_short = "column separator",
    desc = "The column separator (the default is white space).",
    wiz_element_type = "combo",
    wiz_combo_choices = [",", ";", "\\t"],
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will read R2eff/R1rho data for a single spin directly from a file.  The data will be associated with an experiment ID string.  This ID can be used for setting the type of dispersion experiment the data is from, spectrometer proton frequency of the data, and the time of the relaxation period.")
uf.desc[-1].add_paragraph("The format of this text file must be that each row corresponds to a dispersion point (i.e. per CPMG frequency nu_CPMG or per spin-lock field strength nu1) and that there is one file per unique spin system.  The file must be in columnar format.  For R1rho data, the dispersion point column can be substituted for the offset values in Hertz.")
uf.backend = r2eff_read_spin
uf.menu_text = "&r2eff_read_spin"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_size = (900, 700)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


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
        "%s: {%s/%s, %s}" % (MODEL_R2EFF, r2eff, r1rho, i0),
        "%s: {%s, ...}" % (MODEL_NOREX, r2),
        "%s: {%s, ..., %s, %s}" % (MODEL_LM63, r2, phi_ex, kex),
        "%s: {%s, ..., %s, kB, %s, kC}" % (MODEL_LM63_3SITE, r2, phi_exB, phi_exC),
        "%s: {%s, ..., pA, %s, %s}" % (MODEL_CR72, r2, dw, kex),
        "%s: {%s, %s, ..., pA, %s, %s}" % (MODEL_CR72_FULL, r2a, r2b, dw, kex),
        "%s: {%s, ..., pA, %s, %s}" % (MODEL_IT99, r2, dw, tex),
        "%s: {%s, ..., %s, k_AB}" % (MODEL_TSMFK01, r2a, dw),
        "%s: {%s, ..., pA, %s, %s}" % (MODEL_B14, r2, dw, kex),
        "%s: {%s, %s, ..., pA, %s, %s}" % (MODEL_B14_FULL, r2a, r2b, dw, kex),
        "%s: {%s, ..., pA, %s, %s}" % (MODEL_NS_CPMG_2SITE_3D, r2, dw, kex),
        "%s: {%s, %s, ..., pA, %s, %s}" % (MODEL_NS_CPMG_2SITE_3D_FULL, r2a, r2b, dw, kex),
        "%s: {%s, ..., pA, %s, %s}" % (MODEL_NS_CPMG_2SITE_STAR, r2, dw, kex),
        "%s: {%s, %s, ..., pA, %s, %s}" % (MODEL_NS_CPMG_2SITE_STAR_FULL, r2a, r2b, dw, kex),
        "%s: {%s, ..., pA, %s, %s}" % (MODEL_NS_CPMG_2SITE_EXPANDED, r2, dw, kex),
        "%s: {%s, ..., pA, %s, %s, %s}" % (MODEL_MMQ_CR72, r2, dw, dwH, kex),
        "%s: {%s, ..., pA, %s, %s, %s}" % (MODEL_NS_MMQ_2SITE, r2, dw, dwH, kex),
        "%s: {%s, ..., pA, %s, %s, %s, pB, %s, %s, %s}" % (MODEL_NS_MMQ_3SITE_LINEAR, r2, dw_AB, dwH_AB, kAB, dw_BC, dwH_BC, kBC),
        "%s: {%s, ..., pA, %s, %s, %s, pB, %s, %s, %s, %s}" % (MODEL_NS_MMQ_3SITE, r2, dw_AB, dwH_AB, kAB, dw_BC, dwH_BC, kBC, kAC),
        "%s: {%s, ..., %s, %s}" % (MODEL_M61, r1rho_prime, phi_ex, kex),
        "%s: {%s, ..., pA, %s, %s}" % (MODEL_M61B, r1rho_prime, dw, kex),
        "%s: {%s, ..., %s, %s}" % (MODEL_DPL94, r1rho_prime, phi_ex, kex),
        "%s: {%s, ..., pA, %s, %s}" % (MODEL_TP02, r1rho_prime, dw, kex),
        "%s: {%s, ..., pA, %s, %s}" % (MODEL_TAP03, r1rho_prime, dw, kex),
        "%s: {%s, ..., pA, %s, %s}" % (MODEL_MP05, r1rho_prime, dw, kex),
        "%s: {%s, ..., pA, %s, %s}" % (MODEL_NS_R1RHO_2SITE, r1rho_prime, dw, kex),
        "%s: {%s, ..., pA, %s, %s, pB, %s, %s}" % (MODEL_NS_R1RHO_3SITE_LINEAR, r2, dw_AB, kAB, dw_BC, kBC),
        "%s: {%s, ..., pA, %s, %s, pB, %s, %s, %s}" % (MODEL_NS_R1RHO_3SITE, r2, dw_AB, kAB, dw_BC, kBC, kAC)
    ],
    wiz_combo_data = [
        MODEL_R2EFF,
        MODEL_NOREX,
        MODEL_LM63,
        MODEL_LM63_3SITE,
        MODEL_CR72,
        MODEL_CR72_FULL,
        MODEL_IT99,
        MODEL_TSMFK01,
        MODEL_B14,
        MODEL_B14_FULL,
        MODEL_NS_CPMG_2SITE_3D,
        MODEL_NS_CPMG_2SITE_3D_FULL,
        MODEL_NS_CPMG_2SITE_STAR,
        MODEL_NS_CPMG_2SITE_STAR_FULL,
        MODEL_NS_CPMG_2SITE_EXPANDED,
        MODEL_MMQ_CR72,
        MODEL_NS_MMQ_2SITE,
        MODEL_NS_MMQ_3SITE_LINEAR,
        MODEL_NS_MMQ_3SITE,
        MODEL_M61,
        MODEL_M61B,
        MODEL_DPL94,
        MODEL_TP02,
        MODEL_TAP03,
        MODEL_MP05,
        MODEL_NS_R1RHO_2SITE,
        MODEL_NS_R1RHO_3SITE_LINEAR,
        MODEL_NS_R1RHO_3SITE
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("A number of different dispersion models are supported.  This includes both analytic models and numerical models.  Models which are independent of the experimental data type are:")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_R2EFF, "This is the model used to determine the R2eff/R1rho values and errors required as the base data for all other models,")
uf.desc.append(Desc_container('The no chemical exchange models'))
uf.desc[-1].add_item_list_element("'%s'" % MODEL_NOREX, "This is the model for no chemical exchange being present.")
# CPMG-type data.
uf.desc.append(Desc_container('The SQ CPMG-type experiments'))
uf.desc[-1].add_paragraph("The currently supported analytic models are:")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_LM63, "The original Luz and Meiboom (1963) 2-site fast exchange equation with parameters {R20, ..., phi_ex, kex},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_LM63_3SITE, "The original Luz and Meiboom (1963) 3-site fast exchange equation with parameters {R20, ..., phi_ex, kex, phi_ex2, kex2},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_CR72, "The reduced Carver and Richards (1972) 2-site equation for most time scales whereby the simplification R20A = R20B is assumed.  The parameters are {R20, ..., pA, dw, kex},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_CR72_FULL, "The full Carver and Richards (1972) 2-site equation for most time scales with parameters {R20A, R20B, ..., pA, dw, kex},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_IT99, "The Ishima and Torchia (1999) 2-site model for all time scales with pA >> pB and with parameters {R20, ..., pA, dw, kex},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_TSMFK01, "The Tollinger, Kay et al. (2001) 2-site very-slow exchange model, range of microsecond to second time scale.  Applicable in the limit of slow exchange, when |R20A-R20B| << k_AB,kB << 1/tau_CP.  R20A is the transverse relaxation rate of site A in the absence of exchange.  2*tau_CP is is the time between successive 180 deg. pulses.  The parameters are {R20A, ..., dw, k_AB}.")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_B14, "The Baldwin (2014) 2-site exact solution model for all time scales, whereby the simplification R20A = R20B is assumed. The parameters are {R20, ..., pA, dw, kex},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_B14_FULL, "The Baldwin (2014) 2-site exact solution model for all time scales with parameters {R20A, R20B, ..., pA, dw, kex},")
uf.desc[-1].add_paragraph("The currently supported numeric models are:")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_NS_CPMG_2SITE_3D, "The reduced numerical solution for the 2-site Bloch-McConnell equations using 3D magnetisation vectors whereby the simplification R20A = R20B is assumed.  Its parameters are {R20, ..., pA, dw, kex},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_NS_CPMG_2SITE_3D_FULL, "The full numerical solution for the 2-site Bloch-McConnell equations using 3D magnetisation vectors.  Its parameters are {R20A, R20B, ..., pA, dw, kex},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_NS_CPMG_2SITE_STAR, "The reduced numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices whereby the simplification R20A = R20B is assumed.  It has the parameters {R20, ..., pA, dw, kex},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_NS_CPMG_2SITE_STAR_FULL, "The full numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices with parameters {R20A, R20B, ..., pA, dw, kex},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_NS_CPMG_2SITE_EXPANDED, "The numerical solution for the 2-site Bloch-McConnell equations expanded using Maple by Nikolai Skrynnikov.  It has the parameters {R20, ..., pA, dw, kex}.")
# MMQ CPMG-type data.
uf.desc.append(Desc_container('The MMQ CPMG-type experiments'))
uf.desc[-1].add_paragraph("The currently supported models are:")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_MMQ_CR72, "The the Carver and Richards (1972) 2-site model for most time scales expanded for MMQ CPMG data by Korzhnev et al., 2004, whereby the simplification R20A = R20B is assumed.  Its parameters are {R20, ..., pA, dw, dwH, kex}.")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_NS_MMQ_2SITE, "The numerical solution for the 2-site Bloch-McConnell equations for combined proton-heteronuclear SQ, ZQ, DQ, and MQ CPMG data whereby the simplification R20A = R20B is assumed.  Its parameters are {R20, ..., pA, dw, dwH, kex}.")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_NS_MMQ_3SITE_LINEAR, "The numerical solution for the 3-site Bloch-McConnell equations linearised with kAC = kCA = 0 for combined proton-heteronuclear SQ, ZQ, DQ, and MQ CPMG data whereby the simplification R20A = R20B = R20C is assumed.  Its parameters are {R20, ..., pA, dw(AB), dwH(AB), kex(AB), pB, dw(BC), dwH(BC), kex(BC)}.")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_NS_MMQ_3SITE, "The numerical solution for the 3-site Bloch-McConnell equations for combined proton-heteronuclear SQ, ZQ, DQ, and MQ CPMG data whereby the simplification R20A = R20B = R20C is assumed.  Its parameters are {R20, ..., pA, dw(AB), dwH(AB), kex(AB), pB, dw(BC), dwH(BC), kex(BC), kex(AC)}.")
# R1rho-type data.
uf.desc.append(Desc_container('The R1rho-type experiments'))
uf.desc[-1].add_paragraph("The currently supported analytic models are:")
uf.desc[-1].add_paragraph("On-resonance models are:")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_M61, "The Meiboom (1961) 2-site fast exchange equation with parameters {R1rho', ..., phi_ex, kex},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_M61B, "The Meiboom (1961) 2-site equation for all time scales with pA >> pB and with parameters {R1rho', ..., pA, dw, kex},")
uf.desc[-1].add_paragraph("Off-resonance models are:")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_DPL94, "The Davis, Perlman and London (1994) 2-site fast exchange equation with parameters {R1rho', ..., phi_ex, kex},")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_TP02, "The Trott and Palmer (2002) 2-site equation for all time scales with parameters {R1rho', ..., pA, dw, kex}.")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_TAP03, "The Trott, Abergel and Palmer (2003) off-resonance 2-site equation for all time scales with parameters {R1rho', ..., pA, dw, kex}.")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_MP05, "The Miloushev and Palmer (2005) 2-site off-resonance equation for all time scales with parameters {R1rho', ..., pA, dw, kex}.")
uf.desc[-1].add_paragraph("The currently supported numeric models are:")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_NS_R1RHO_2SITE, "The numerical solution for the 2-site Bloch-McConnell equations using 3D magnetisation vectors whereby the simplification R20A = R20B.  Its parameters are {R1rho', ..., pA, dw, kex}.")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_NS_R1RHO_3SITE_LINEAR, "The numerical solution for the 3-site Bloch-McConnell equations using 3D magnetisation vectors whereby the simplification R20A = R20B = R20C is assumed and linearised with kAC = kCA = 0.  Its parameters are {R1rho', ..., pA, dw(AB), kex(AB), pB, dw(BC), kex(BC)}.")
uf.desc[-1].add_item_list_element("'%s'" % MODEL_NS_R1RHO_3SITE, "The numerical solution for the 3-site Bloch-McConnell equations using 3D magnetisation vectors.  Its parameters are {R1rho', ..., pA, dw(AB), kex(AB), pB, dw(BC), kex(BC), kex(AC)}.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To pick the 2-site fast exchange model for all selected spins, type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.select_model('%s')" % MODEL_LM63)
uf.desc[-1].add_prompt("relax> relax_disp.select_model(model='%s')" % MODEL_LM63)
uf.backend = relax_disp_uf.select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 700)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.r20_from_min_r2eff user function.
uf = uf_info.add_uf('relax_disp.r20_from_min_r2eff')
uf.title = "Set the R20 parameter values to that of the minimum R2eff value."
uf.title_short = "Set R20 from the minimum R2eff."
uf.add_keyarg(
    name = "force",
    default = True,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause the R20 values to be overwritten if they already exist."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Set the R20 parameter values to that of the minimum R2eff value.  This user function will look through all R2eff values per magnetic field strength, find the minimum value, and set the R20, R20A, R20B, and R1rho' parameters of the model to this value.  This can serve a number of purposes including using the values for the chi-squared space mapping via the dx.map user function, speeding up optimisation by avoiding the grid search for these parameters, and as initial parameter values for other dispersion software.")
uf.desc[-1].add_paragraph("Instead of finding the initial values for the R20 parameter using the grid search, the minimum for the R2eff points can be used instead.  This is often a good initial position for minimisation.  For example for a two field CPMG experiment with model CR72, that would drop the number of uniform grid search points from 5D to 3D, i.e. two orders of magnitude faster.  When using the standard 21 grid increments per dimension, it would allow the grid search to be 441 times faster.  Note that the relaxation dispersion auto-analysis will take all pre-set parameter values into account and will automatically exclude these from the grid search.")
uf.desc[-1].add_paragraph("Note that for optimisation, that this is an experimental and unpublished feature of the dispersion analysis.  If R20 << min(R2eff), the grid search will be performed in a region of the optimisation space quite distant from the true minimum.  If unsure, do not activate this option, and let the grid search find a better starting value.")
uf.backend = r20_from_min_r2eff
uf.menu_text = "&r20_from_min_r2eff"
uf.gui_icon = "relax.grid_search"
uf.wizard_height_desc = 500
uf.wizard_size = (900, 600)
uf.wizard_apply_button = False


# The relax_disp.sherekhan_input user function.
uf = uf_info.add_uf('relax_disp.sherekhan_input')
uf.title = "Create the input files for Adam Mazur's ShereKhan program."
uf.title_short = "ShereKhan input file creation."
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
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
    desc_short = "directory name",
    desc = "The directory name to place ShereKhan cluster folders into.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This creates the files required for the ShereKhan server located at http://sherekhan.bionmr.org/.  One file per spin cluster per field strength will be created.  These will be placed in the directory 'clusterx' and named 'sherekhan_frqy.in', where x is the cluster index starting from 1 and y is the magnetic field strength index starting from 1.")
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
    desc = "The spin-lock field strength, nu1, in Hz.",
    can_be_none = True
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


# The relax_disp.spin_lock_offset user function.
uf = uf_info.add_uf('relax_disp.spin_lock_offset')
uf.title = "Set the relaxation dispersion spin-lock offset (omega_rf)."
uf.title_short = "Spin-lock offset."
uf.add_keyarg(
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum ID string",
    desc = "The spectrum ID string to associate the spin-lock offset to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "offset",
    py_type = "num",
    desc_short = "spin-lock offset (ppm)",
    desc = "The spin-lock offset, omega_rf, in ppm.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This sets the spin-lock offset, omega_rf, for the specified R1rho spectrum in ppm.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set a spin-lock offset of 110.0 ppm for the spectrum 'nu1_2.1kHz_relaxT_0.010', type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.spin_lock_offset('nu1_2.1kHz_relaxT_0.010', 110.0)")
uf.desc[-1].add_prompt("relax> relax_disp.spin_lock_offset(spectrum_id='nu1_2.1kHz_relaxT_0.010', offset=110.0)")
uf.backend = spin_lock_offset
uf.menu_text = "spin_lock_&offset"
uf.wizard_size = (800, 500)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'


# The relax_disp.write_disp_curves user function.
uf = uf_info.add_uf('relax_disp.write_disp_curves')
uf.title = "Create text files of the dispersion curves for each spin system."
uf.title_short = "Dispersion curve writing."
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir sel",
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
uf.desc[-1].add_paragraph("This is used to created text files of the dispersion curves of R2eff/R1rho values, both measured and back calculated from the optimised dispersion model.  The columns of the text file will be the experiment name, the magnetic field strength (as the proton frequency in MHz), dispersion point (nu_CPMG or the spin-lock field strength), the experimental R2eff value, the back-calculated R2eff value, and the experimental R2eff error.  One file will be created per spin system with the name 'disp_x.out', where x is the spin ID string.")
uf.backend = write_disp_curves
uf.menu_text = "&write_disp_curves"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (700, 500)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'relax_disp_200x200.png'
