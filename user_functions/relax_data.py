###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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

# Module docstring.
"""The relax_data user function definitions."""

# Python module imports.
from os import sep
import wx

# relax module imports.
from generic_fns import pipes, relax_data
from graphics import WIZARD_IMAGE_PATH
from physical_constants import NH_BOND_LENGTH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('relax_data')
uf_class.title = "Class for manipulating R1, R2, and NOE relaxation data."
uf_class.menu_text = "&relax_data"
uf_class.gui_icon = "relax.fid"


# The relax_data.back_calc user function.
uf = uf_info.add_uf('relax_data.back_calc')
uf.title = "Back calculate the relaxation data at the given frequency."
uf.title_short = "Relaxation data back calculation."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation ID string",
    desc = "The relaxation data ID string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "ri_type",
    py_type = "str",
    desc_short = "relaxation type",
    desc = "The relaxation data type, ie 'R1', 'R2', or 'NOE'.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["R1", "R2", "NOE"],
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "frq",
    py_type = "num",
    desc_short = "frequency",
    desc = "The spectrometer frequency in Hz.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows relaxation data of the given type and frequency to be back calculated from the model parameter values.  If the relaxation data ID, type and frequency are not given, then relaxation data matching that currently loaded in the relax data store will be back-calculated.")
uf.backend = relax_data.back_calc
uf.menu_text = "&back_calc"
uf.gui_icon = "oxygen.categories.applications-education"
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'


# The relax_data.copy user function.
uf = uf_info.add_uf('relax_data.copy')
uf.title = "Copy relaxation data from one pipe to another."
uf.title_short = "Relaxation data copying."
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "source data pipe",
    desc = "The name of the pipe to copy the relaxation data from.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "pipe_to",
    py_type = "str",
    desc_short = "destination data pipe",
    desc = "The name of the pipe to copy the relaxation data to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will copy relaxation data from one data pipe to another.  If the relaxation ID data string is not given then all relaxation data will be copied, otherwise only a specific data set will be copied.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To copy all relaxation data from pipe 'm1' to pipe 'm9', type one of:")
uf.desc[-1].add_prompt("relax> relax_data.copy('m1', 'm9')")
uf.desc[-1].add_prompt("relax> relax_data.copy(pipe_from='m1', pipe_to='m9')")
uf.desc[-1].add_prompt("relax> relax_data.copy('m1', 'm9', None)")
uf.desc[-1].add_prompt("relax> relax_data.copy(pipe_from='m1', pipe_to='m9', ri_id=None)")
uf.desc[-1].add_paragraph("To copy only the NOE relaxation data with the ID string of 'NOE_800' from 'm3' to 'm6', type one of:")
uf.desc[-1].add_prompt("relax> relax_data.copy('m3', 'm6', 'NOE_800')")
uf.desc[-1].add_prompt("relax> relax_data.copy(pipe_from='m3', pipe_to='m6', ri_id='NOE_800')")
uf.backend = relax_data.copy
uf.menu_text = "&copy"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'


# The relax_data.delete user function.
uf = uf_info.add_uf('relax_data.delete')
uf.title = "Delete the data corresponding to the relaxation data ID string."
uf.title_short = "Relaxation data deletion."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The relaxation data corresponding to the given relaxation data ID string will be removed from the current data pipe.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To delete the relaxation data corresponding to the ID 'NOE_600', type:")
uf.desc[-1].add_prompt("relax> relax_data.delete('NOE_600')")
uf.backend = relax_data.delete
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_size = (700, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'


# The relax_data.dipole_pair user function.
uf = uf_info.add_uf('relax_data.dipole_pair')
uf.title = "Define the pairs of spins involved in magnetic dipole-dipole relaxation interactions."
uf.title_short = "Magnetic dipole-dipole interaction setup."
uf.add_keyarg(
    name = "spin_id1",
    default = "@N",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "first spin ID string",
    desc = "The spin identification string for the first spin of the dipolar relaxation pair."
)
uf.add_keyarg(
    name = "spin_id2",
    default = "@H",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "second spin ID string",
    desc = "The spin identification string for the second spin of the dipolar relaxation pair."
)
uf.add_keyarg(
    name = "ave_dist",
    default = NH_BOND_LENGTH,
    py_type = "float",
    desc_short = "averaged interatomic distance (meters)",
    desc = "The r^-3 averaged distance between the two spins to be used in the magnetic dipole constant."
)
uf.add_keyarg(
    name = "direct_bond",
    default = True,
    py_type = "bool",
    desc_short = "directly bonded atoms flag",
    desc = "This is a flag which if True means that the two spins are directly bonded.  This flag is useful to simply the set up of the main heteronuclear relaxation mechanism."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("To analyse relaxation data, the relaxation mechanism and related parameters needs to be defined.  This user function allows pairs of spins which are coupled via the magnetic dipole-dipole interaction to be defined.  Hence the dipolar relaxation mechanism between the two spins is to be considered active.")
uf.desc[-1].add_paragraph("For an orientational dependent analysis, such as model-free analysis with the spheroidal and ellipsoidal global diffusion tensors, the two spins should already possess positional information.  This information will be used by this user function to calculate unit vectors between the two spins.  Without positional information, no vectors can be calculated and an orientational dependent analysis will not be possible.")
uf.desc[-1].add_paragraph("As the magnetic dipole-dipole interaction is averaged in NMR over the interatomic distance to the inverse third power, the interatomic distances within a 3D structural file are of no use for defining the interaction.  Therefore these average distances must be explicitly defined.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set up the protein 15N heteronuclear relaxation mechanism, type on of the following:")
uf.desc[-1].add_prompt("relax> relax_data.dipole_pair('@N', '@H', 1.02 * 1e-10, True)")
uf.desc[-1].add_prompt("relax> relax_data.dipole_pair(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10, direct_bond=True)")
uf.backend = relax_data.dipole_pair
uf.menu_text = "dipole_&pair"
uf.wizard_height_desc = 350
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'dipole_pair' + sep + 'NH_dipole_pair.png'


# The relax_data.display user function.
uf = uf_info.add_uf('relax_data.display')
uf.title = "Display the data corresponding to the relaxation data ID string."
uf.title_short = "Displaying relaxation data."
uf.display = True
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will display the relaxation data corresponding to the given ID.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To display the NOE relaxation data at 600 MHz with the ID string 'NOE_600', type:")
uf.desc[-1].add_prompt("relax> relax_data.display('NOE_600')")
uf.backend = relax_data.display
uf.menu_text = "dis&play"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_size = (700, 400)
uf.wizard_height_desc = 140
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'


# The relax_data.frq user function.
uf = uf_info.add_uf('relax_data.frq')
uf.title = "Set the spectrometer proton frequency of the relaxation data in Hz."
uf.title_short = "Relaxation data frequency setting."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation ID string",
    desc = "The relaxation data ID string of the data to set the frequency of.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "frq",
    py_type = "num",
    desc_short = "frequency in Hz",
    desc = "The exact proton frequency of the spectrometer in Hertz.  See the 'sfrq' parameter in the Varian procpar file or the 'SFO1' parameter in the Bruker acqus file."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the relaxation data type to be either set or reset.  The frequency must be the that of the proton in Hertz.  This value must be exact and match that of the 'sfrq' parameter in the Varian procpar file or the 'SFO1' parameter in the Bruker acqus file.")
uf.backend = relax_data.frq
uf.menu_text = "&frq"
uf.gui_icon = "relax.frq"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'



# The relax_data.peak_intensity_type user function.
uf = uf_info.add_uf('relax_data.peak_intensity_type')
uf.title = "Specify if heights or volumes were used to measure the peak intensities."
uf.title_short = "How were peak intensities measured?"
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "type",
    default = "height",
    py_type = "str",
    desc_short = "peak intensity type",
    desc = "The peak intensity type.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["height", "volume"],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is essential for BMRB data deposition.  It is used to specify whether peak heights or peak volumes were measured.  The two currently allowed values for the peak intensity type are 'height' and 'volume'.")
uf.backend = relax_data.peak_intensity_type
uf.menu_text = "peak_&intensity_type"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_height_desc = 300
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'


# The relax_data.read user function.
uf = uf_info.add_uf('relax_data.read')
uf.title = "Read R1, R2, or NOE relaxation data from a file."
uf.title_short = "Reading relaxation data from file."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation ID string",
    desc = "The relaxation data ID string.  This must be a unique identifier."
)
uf.add_keyarg(
    name = "ri_type",
    py_type = "str",
    desc_short = "relaxation type",
    desc = "The relaxation data type, i.e. 'R1', 'R2', or 'NOE'.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["R1", "R2", "NOE"],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "frq",
    py_type = "num",
    desc_short = "frequency in Hz",
    desc = "The exact proton frequency of the spectrometer in Hertz.  See the 'sfrq' parameter in the Varian procpar file or the 'SFO1' parameter in the Bruker acqus file."
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file containing the relaxation data.",
    wiz_filesel_style = wx.FD_OPEN
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the file is located.",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin ID string column",
    desc = "The spin ID string column (an alternative to the mol, res, and spin name and number columns).",
    can_be_none = True
)
uf.add_keyarg(
    name = "mol_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "molecule name column",
    desc = "The molecule name column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_num_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "residue number column",
    desc = "The residue number column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "residue name column",
    desc = "The residue name column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_num_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin number column",
    desc = "The spin number column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin name column",
    desc = "The spin name column (alternative to the spin_id_col).",
    can_be_none = True
)
uf.add_keyarg(
    name = "data_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "data column",
    desc = "The relaxation data column."
)
uf.add_keyarg(
    name = "error_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "error column",
    desc = "The experimental error column."
)
uf.add_keyarg(
    name = "sep",
    py_type = "str",
    arg_type = "free format",
    desc_short = "column separator",
    desc = "The column separator (the default is white space).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "spin ID string",
    desc = "The spin ID string to restrict the loading of data to certain spin subsets.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will load the relaxation data into the relax data store.  The data is associated with the spectrometer frequency in Hertz.  For subsequent analysis, this frequency must be set to the exact field strength.  This value is stored in the 'sfrq' parameter in the Varian procpar file or the 'SFO1' parameter in the Bruker acqus file.")
uf.desc[-1].add_paragraph("The spin system can be identified in the file using two different formats.  The first is the spin ID string column which can include the molecule name, the residue name and number, and the spin name and number.  Alternatively the molecule name, residue number, residue name, spin number and/or spin name columns can be supplied allowing this information to be in separate columns.  Note that the numbering of columns starts at one.  The spin ID string can be used to restrict the reading to certain spin types, for example only 15N spins when only residue information is in the file.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following commands will read the protein NOE relaxation data collected at 600 MHz out of a file called 'noe.600.out' where the residue numbers, residue names, data, errors are in the first, second, third, and forth columns respectively.")
uf.desc[-1].add_prompt("relax> relax_data.read('NOE_600', 'NOE', 599.7 * 1e6, 'noe.600.out', res_num_col=1, res_name_col=2, data_col=3, error_col=4)")
uf.desc[-1].add_prompt("relax> relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.0 * 1e6, file='noe.600.out', res_num_col=1, res_name_col=2, data_col=3, error_col=4)")
uf.desc[-1].add_paragraph("The following commands will read the R2 data out of the file 'r2.out' where the residue numbers, residue names, data, errors are in the second, third, fifth, and sixth columns respectively.  The columns are separated by commas.")
uf.desc[-1].add_prompt("relax> relax_data.read('R2_800', 'R2', 8.0 * 1e8, 'r2.out', res_num_col=2, res_name_col=3, data_col=5, error_col=6, sep=',')")
uf.desc[-1].add_prompt("relax> relax_data.read(ri_id='R2_800', ri_type='R2', frq=8.0*1e8, file='r2.out', res_num_col=2, res_name_col=3, data_col=5, error_col=6, sep=',')")
uf.desc[-1].add_paragraph("The following commands will read the R1 data out of the file 'r1.out' where the columns are separated by the symbol '%'")
uf.desc[-1].add_prompt("relax> relax_data.read('R1_300', 'R1', 300.1 * 1e6, 'r1.out', sep='%')")
uf.backend = relax_data.read
uf.menu_text = "&read"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 140
uf.wizard_size = (1000, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'


# The relax_data.temp_calibration user function.
uf = uf_info.add_uf('relax_data.temp_calibration')
uf.title = "Specify the per-experiment temperature calibration method used."
uf.title_short = "The per-experiment temperature calibration method."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "method",
    py_type = "str",
    desc_short = "per-experiment calibration method",
    desc = "The per-experiment temperature calibration method.",
    wiz_element_type = 'combo',
    wiz_combo_choices = [
        'methanol',
        'monoethylene glycol',
        'no calibration applied'
    ]
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("For the proper measurement of relaxation data, per-experiment temperature calibration is essential.  This user function is not for inputting standard MeOH/ethylene glycol/etc. calibration of a spectrometer - this temperature setting is of no use when you are running experiments which pump in large amounts of power into the probe head.")
uf.desc[-1].add_paragraph("The R1 experiment should be about the same temperature as a HSQC and hence be close to the standard MeOH/ethylene glycol sepectrometer calibration.  However the R2 CPMG or spin lock and, to a lesser extent, the NOE pre-saturation pump a lot more power into the probe head.  The power differences can either cause the temperature in the sample to be too high or too low.  This is unpredictable as the thermometer used by the VT unit is next to the coils in the probe head and not inside the NMR sample.  So the VT unit tries to control the temperature inside the probe head rather than in the NMR sample.  However between the thermometer and the sample is the water of the sample, the glass of the NMR tube, the air gap where the VT unit controls air flow and the outside components of the probe head protecting the electronics.  If the sample, the probe head or the VT unit is changed, this will have a different affect on the per-experiment temperature.  The VT unit responds differently under different conditions and may sometimes over or under compensate by a couple of degrees.  Therefore each relaxation data set from each spectrometer requires a per-experiment calibration.")
uf.desc[-1].add_paragraph("Specifying the per-experiment calibration method is needed for BMRB data deposition.  The currently allowed methods are:")
uf.desc[-1].add_list_element("'methanol',")
uf.desc[-1].add_list_element("'monoethylene glycol',")
uf.desc[-1].add_list_element("'no calibration applied'.")
uf.desc[-1].add_paragraph("Other methods will be accepted if supplied.")
uf.backend = relax_data.temp_calibration
uf.menu_text = "&temp_calibration"
uf.gui_icon = "oxygen.status.weather-clear"
uf.wizard_height_desc = 550
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'oxygen-icon-weather-clear.png'


# The relax_data.temp_control user function.
uf = uf_info.add_uf('relax_data.temp_control')
uf.title = "Specify the temperature control method used."
uf.title_short = "The temperature control method."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "method",
    py_type = "str",
    desc_short = "temperature control method",
    desc = "The control method.",
    wiz_element_type = 'combo',
    wiz_combo_choices = [
        'single scan interleaving',
        'temperature compensation block',
        'single scan interleaving and temperature compensation block',
        'single fid interleaving',
        'single experiment interleaving',
        'no temperature control applied'
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("For the proper measurement of relaxation data, explicit temperature control techniques are essential.  A number of factors can cause significant temperature fluctuations between individual relaxation experiments.  This includes the daily temperature cycle of the room housing the spectrometer, different amounts of power for the individual experiments, .  The best methods for eliminating such problems are single scan interleaving and the application of off-resonance temperature compensation")
uf.desc[-1].add_paragraph("The best methods for eliminating such problems are single scan interleaving and temperature compensation block.  Single scan interleaving is the most powerful technique for averaging the temperature fluctuations not only across different experiments, but also across the entire measurement time.  The application of off-resonance temperature compensation blocks at the start of the experiment is useful for the R2 and will normalise the temperature between the individual experiments, but single scan or single fid interleaving is nevertheless required for normalising the temperature across the entire measurement.")
uf.desc[-1].add_paragraph("Specifying the temperature control method is needed for BMRB data deposition.  The currently allowed methods are:")
uf.desc[-1].add_list_element("'single scan interleaving',")
uf.desc[-1].add_list_element("'temperature compensation block',")
uf.desc[-1].add_list_element("'single scan interleaving and temperature compensation block',")
uf.desc[-1].add_list_element("'single fid interleaving',")
uf.desc[-1].add_list_element("'single experiment interleaving',")
uf.desc[-1].add_list_element("'no temperature control applied'.")
uf.backend = relax_data.temp_control
uf.menu_text = "temp_contro&l"
uf.gui_icon = "oxygen.status.weather-clear"
uf.wizard_size = (1000, 750)
uf.wizard_height_desc = 500
uf.wizard_image = WIZARD_IMAGE_PATH + 'oxygen-icon-weather-clear.png'


# The relax_data.type user function.
uf = uf_info.add_uf('relax_data.type')
uf.title = "Set the type of relaxation data."
uf.title_short = "Relaxation data type setting."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation ID string",
    desc = "The relaxation data ID string of the data to set the frequency of.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "ri_type",
    py_type = "str",
    desc_short = "relaxation type",
    desc = "The relaxation data type, i.e. 'R1', 'R2', or 'NOE'.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["R1", "R2", "NOE"],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the type associated with the relaxation data to be either set or reset.  This type must be one of 'R1', 'R2', or 'NOE'.")
uf.backend = relax_data.type
uf.menu_text = "&type"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'



# The relax_data.write user function.
uf = uf_info.add_uf('relax_data.write')
uf.title = "Write relaxation data to a file."
uf.title_short = "Relaxation data writing."
uf.add_keyarg(
    name = "ri_id",
    py_type = "str",
    desc_short = "relaxation data ID string",
    desc = "The relaxation data ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = relax_data.get_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file.",
    wiz_filesel_style = wx.FD_SAVE
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
    name = "bc",
    default = False,
    py_type = "bool",
    desc_short = "back calculated data flag",
    desc = "A flag which if True will cause the back-calculated data to be written to the file."
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will cause the file to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("If no directory name is given, the file will be placed in the current working directory.  The relaxation data ID string is required for selecting which relaxation data to write to file.")
uf.backend = relax_data.write
uf.menu_text = "&write"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'fid.png'
