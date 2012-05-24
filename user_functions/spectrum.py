###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
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
"""The spectrum user function definitions."""

# Python module imports.
from os import sep
import wx

# relax module imports.
from generic_fns import spectrum
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('spectrum')
uf_class.title = "Class for supporting the input of spectral data."
uf_class.menu_text = "&spectrum"
uf_class.gui_icon = "relax.fid"


# The spectrum.baseplane_rmsd user function.
uf = uf_info.add_uf('spectrum.baseplane_rmsd')
uf.title = "Set the baseplane RMSD of a given spin in a spectrum for error analysis."
uf.title_short = "Baseplane RMSD setting."
uf.add_keyarg(
    name = "error",
    default = 0.0,
    py_type = "num",
    desc_short = "error",
    desc = "The baseplane RMSD error value."
)
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
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin ID string.",
    can_be_none = True
)
uf.desc = """
The spectrum ID identifies the spectrum associated with the error and must correspond to a previously loaded set of intensities.  If the spin ID is unset, then the error value for all spins will be set to the supplied value.
"""
uf.backend = spectrum.baseplane_rmsd
uf.menu_text = "&baseplane_rmsd"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_size = (800, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'


# The spectrum.delete user function.
uf = uf_info.add_uf('spectrum.delete')
uf.title = "Delete the spectral data corresponding to the spectrum ID string."
uf.title_short = "Spectral data deletion."
uf.add_keyarg(
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum ID string",
    desc = "The unique spectrum ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
uf.desc = """
The spectral data corresponding to the given spectrum ID string will be removed from the current data pipe.
"""
uf.prompt_examples = """
To delete the peak height data corresponding to the ID 'R1 ncyc5', type:

relax> spectrum.delete('R1 ncyc5')
"""
uf.backend = spectrum.delete
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_size = (700, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'


# The spectrum.error_analysis user function.
uf = uf_info.add_uf('spectrum.error_analysis')
uf.title = "Perform an error analysis for peak intensities."
uf.title_short = "Peak intensity error analysis."
uf.desc = """
This user function must only be called after all peak intensities have been loaded and all other necessary spectral information set.  This includes the baseplane RMSD and the number of points used in volume integration, both of which are only used if spectra have not been replicated.

Six different types of error analysis are supported depending on whether peak heights or volumes are supplied, whether noise is determined from replicated spectra or the RMSD of the baseplane noise, and whether all spectra or only a subset have been duplicated.  These are:

____________________________________________________________________________________________
|          |                                        |                                      |
| Int type | Noise source                           | Error scope                          |
|__________|________________________________________|______________________________________|
|          |                                        |                                      |
| Heights  | RMSD baseplane                         | One sigma per peak per spectrum      |
|          |                                        |                                      |
| Heights  | Partial duplicate + variance averaging | One sigma for all peaks, all spectra |
|          |                                        |                                      |
| Heights  | All replicated + variance averaging    | One sigma per replicated spectra set |
|          |                                        |                                      |
| Volumes  | RMSD baseplane                         | One sigma per peak per spectrum      |
|          |                                        |                                      |
| Volumes  | Partial duplicate + variance averaging | One sigma for all peaks, all spectra |
|          |                                        |                                      |
| Volumes  | All replicated + variance averaging    | One sigma per replicated spectra set |
|__________|________________________________________|______________________________________|
"""
uf.additional = [
["Peak heights with baseplane noise RMSD", """
When none of the spectra have been replicated, then the peak height errors are calculated using the RMSD of the baseplane noise, the value of which is set by the spectrum.baseplane_rmsd() user function.  This results in a different error per peak per spectrum.  The standard deviation error measure for the peak height, sigma_I, is set to the RMSD value."""],
["Peak heights with partially replicated spectra", """
When spectra are replicated, the variance for a single spin at a single replicated spectra set is calculated by the formula

-----

    sigma^2 =  sum({Ii - Iav}^2) / (n - 1) ,

-----

where sigma^2 is the variance, sigma is the standard deviation, n is the size of the replicated spectra set with i being the corresponding index, Ii is the peak intensity for spectrum i, and Iav is the mean over all spectra i.e. the sum of all peak intensities divided by n.

As the value of n in the above equation is always very low since normally only a couple of spectra are collected per replicated spectra set, the variance of all spins is averaged for a single replicated spectra set.  Although this results in all spins having the same error, the accuracy of the error estimate is significantly improved.

If there are in addition to the replicated spectra loaded peak intensities which only consist of a single spectrum, i.e. not all spectra are replicated, then the variances of replicated replicated spectra sets will be averaged.  This will be used for the entire experiment so that there will be only a single error value for all spins and for all spectra."""],
["Peak heights with all spectra replicated", """
If all spectra are collected in duplicate (triplicate or higher number of spectra are supported), the each replicated spectra set will have its own error estimate.  The error for a single peak is calculated as when partially replicated spectra are collected, and these are again averaged to give a single error per replicated spectra set.  However as all replicated spectra sets will have their own error estimate, variance averaging across all spectra sets will not be performed."""],
["Peak volumes with baseplane noise RMSD", """
The method of error analysis when no spectra have been replicated and peak volumes are used is highly dependent on the integration method.  Many methods simply sum the number of points within a fixed region, either a box or oval object.  The number of points used, N, must be specified by another user function in this class.  Then the error is simply given by the sum of variances:

-----

    sigma_vol^2 = sigma_i^2 * N,

-----

where sigma_vol is the standard deviation of the volume, sigma_i is the standard deviation of a single point assumed to be equal to the RMSD of the baseplane noise, and N is the total number of points used in the summation integration method.  For a box integration method, this converts to the Nicholson, Kay, Baldisseri, Arango, Young, Bax, and Torchia (1992) Biochemistry, 31: 5253-5263 equation:

-----

    sigma_vol = sigma_i * sqrt(n*m),

-----

where n and m are the dimensions of the box.  Note that a number of programs, for example peakint (http://hugin.ethz.ch/wuthrich/software/xeasy/xeasy_m15.html) does not use all points within the box.  And if the number N can not be determined, this category of error analysis is not possible.

Also note that non-point summation methods, for example when line shape fitting is used to determine peak volumes, the equations above cannot be used.  Hence again this category of error analysis cannot be used.  This is the case for one of the three integration methods used by Sparky (http://www.cgl.ucsf.edu/home/sparky/manual/peaks.html#Integration).  And if fancy techniques are used, for example as Cara does to deconvolute overlapping peaks (http://www.cara.ethz.ch/Wiki/Integration), this again makes this error analysis impossible."""],
["Peak volumes with partially replicated spectra", """
When peak volumes are measured by any integration method and a few of the spectra are replicated, then the intensity errors are calculated identically as described in the 'Peak heights with partially replicated spectra' section above."""],
["Peak volumes with all spectra replicated", """
With all spectra replicated and again using any integration methodology, the intensity errors can be calculated as described in the 'Peak heights with all spectra replicated' section above.
"""]
]
uf.backend = spectrum.error_analysis
uf.menu_text = "&error_analysis"
uf.gui_icon = "oxygen.categories.applications-education"
uf.wizard_height_desc = 550
uf.wizard_size = (1000, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'
uf.wizard_apply_button = False


# The spectrum.integration_points user function.
uf = uf_info.add_uf('spectrum.integration_points')
uf.title = "Set the number of summed points used in volume integration of a given spin in a spectrum."
uf.title_short = "Number of integration points."
uf.add_keyarg(
    name = "N",
    py_type = "int",
    min = 1,
    max = 10000000,
    desc_short = "number of summed points",
    desc = "The number of points used by the summation volume integration method."
)
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
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "Restrict setting the number to certain spins.",
    can_be_none = True
)
uf.desc = """
For a complete description of which integration methods and how many points N are used for different integration techniques, please see the spectrum.error_analysis user function documentation.

The spectrum ID identifies the spectrum associated with the value of N and must correspond to a previously loaded set of intensities.  If the spin ID is unset, then the number of summed points for all spins will be set to the supplied value.
"""
uf.backend = spectrum.integration_points
uf.menu_text = "&integration_points"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'


# The spectrum.read_intensities user function.
uf = uf_info.add_uf('spectrum.read_intensities')
uf.title = "Read peak intensities from a file."
uf.title_short = "Peak intensity reading."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file containing the intensity data.",
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
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum ID string",
    desc = "The unique spectrum ID string to associate with the peak intensity values."
)
uf.add_keyarg(
    name = "heteronuc",
    default = "N",
    py_type = "str",
    desc_short = "heteronucleus name",
    desc = "The name of the heteronucleus as specified in the peak intensity file."
)
uf.add_keyarg(
    name = "proton",
    default = "HN",
    py_type = "str",
    desc_short = "proton name",
    desc = "The name of the proton as specified in the peak intensity file."
)
uf.add_keyarg(
    name = "int_method",
    default = "height",
    py_type = "str",
    desc_short = "peak integration method",
    desc = "The method by which peaks were integrated.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["height", "point sum", "other"],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "int_col",
    py_type = "int_or_int_list",
    desc_short = "intensity column",
    desc = "The optional column containing the peak intensity data (used by the generic intensity file format, or if the intensities are in a non-standard column).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin ID string column",
    desc = "The spin ID string column used by the generic intensity file format (an alternative to the mol, res, and spin name and number columns).",
    can_be_none = True
)
uf.add_keyarg(
    name = "mol_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "molecule name column",
    desc = "The molecule name column used by the generic intensity file format (alternative to the spin ID column).",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_num_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "residue number column",
    desc = "The residue number column used by the generic intensity file format (alternative to the spin ID column).",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "residue name column",
    desc = "The residue name column used by the generic intensity file format (alternative to the spin ID column).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_num_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin number column",
    desc = "The spin number column used by the generic intensity file format (alternative to the spin ID column).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_name_col",
    py_type = "int",
    arg_type = "free format",
    desc_short = "spin name column",
    desc = "The spin name column used by the generic intensity file format (alternative to the spin ID column).",
    can_be_none = True
)
uf.add_keyarg(
    name = "sep",
    py_type = "str",
    arg_type = "free format",
    desc_short = "column separator",
    desc = "The column separator used by the generic intensity format (the default is white space).",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin ID string used by the generic intensity file format to restrict the loading of data to certain spin subsets.",
    can_be_none = True
)
uf.add_keyarg(
    name = "ncproc",
    py_type = "int",
    desc_short = "Bruker ncproc parameter",
    desc = "The Bruker specific FID intensity scaling factor.",
    can_be_none = True
)
uf.desc = """
The peak intensity can either be from peak heights or peak volumes.

The spectrum ID is a label which is subsequently utilised by other user functions.  If this identifier matches that of a previously loaded set of intensities, then this indicates a replicated spectrum.

The heteronucleus and proton should be set respectively to the name of the heteronucleus and proton in the file.  Only those lines which match these labels will be used.

The integration method is required for the subsequent error analysis.  When peak heights are measured, this should be set to 'height'.  Volume integration methods are a bit varied and hence two values are accepted.  If the volume integration involves pure point summation, with no deconvolution algorithms or other methods affecting peak heights, then the value should be set to 'point sum'.  All other volume integration methods, e.g. line shape fitting, the value should be set to 'other'.

If a series of intensities extracted from Bruker FID files processed in Topspin or XWinNMR are to be compared, the ncproc parameter may need to be supplied.  This is because this FID is stored using integer representation and is scaled using ncproc to avoid numerical truncation artifacts.  If two spectra have significantly different maximal intensities, then ncproc will be different for both.  The intensity scaling is binary, i.e. 2**ncproc. Therefore if spectrum A has an ncproc of 6 and and spectrum B a value of 7, then a reference intensity in B will be double that of A.  Internally, relax stores the intensities scaled by 2**ncproc.
"""
uf.additional = [
["File formats", """
The peak list or intensity file will be automatically determined.

Sparky peak list:  The file should be a Sparky peak list saved after typing the command 'lt'.  The default is to assume that columns 0, 1, 2, and 3 (1st, 2nd, 3rd, and 4th) contain the Sparky assignment, w1, w2, and peak intensity data respectively.  The frequency data w1 and w2 are ignored while the peak intensity data can either be the peak height or volume displayed by changing the window options.  If the peak intensity data is not within column 3, set the integration column to the appropriate number (column numbering starts from 0 rather than 1).

XEasy peak list:  The file should be the saved XEasy text window output of the list peak entries command, 'tw' followed by 'le'.  As the columns are fixed, the peak intensity column is hardwired to number 10 (the 11th column) which contains either the peak height or peak volume data.  Because the columns are fixed, the integration column number will be ignored.

NMRView:  The file should be a NMRView peak list. The default is to use column 16 (which contains peak heights) for peak intensities. To use use peak volumes (or evolumes), int_col must be set to 15.

Generic intensity file:  This is a generic format which can be created by scripting to support non-supported peak lists.  It should contain in the first few columns enough information to identify the spin.  This can include columns for the molecule name, residue number, residue name, spin number, and spin name.  Alternatively a spin ID string column can be used. The peak intensities can be placed in another column specified by the integration column number.  Intensities from multiple spectra can be placed into different columns, and these can then be specified simultaneously by setting the integration column value to a list of columns.  This list must be matched by setting the spectrum ID to a list of the same length.  If columns are delimited by a character other than whitespace, this can be specified with the column separator.  The spin ID can be used to restrict the loading to specific spin subsets.
"""]
]
uf.prompt_examples = """
To read the reference and saturated spectra peak heights from the Sparky formatted files
'ref.list' and 'sat.list', type:

relax> spectrum.read_intensities(file='ref.list', spectrum_id='ref')
relax> spectrum.read_intensities(file='sat.list', spectrum_id='sat')

To read the reference and saturated spectra peak heights from the XEasy formatted files
'ref.text' and 'sat.text', type:

relax> spectrum.read_intensities(file='ref.text', spectrum_id='ref')
relax> spectrum.read_intensities(file='sat.text', spectrum_id='sat')
"""
uf.backend = spectrum.read
uf.menu_text = "&read"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 140
uf.wizard_size = (1000, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'


# The spectrum.replicated user function.
uf = uf_info.add_uf('spectrum.replicated')
uf.title = "Specify which spectra are replicates of each other."
uf.title_short = "Replicate spectra."
uf.add_keyarg(
    name = "spectrum_ids",
    py_type = "str_or_str_list",
    desc_short = "spectrum ID strings",
    desc = "The list of replicated spectra ID strings.",
    wiz_element_type = 'combo_list',
    wiz_combo_iter = spectrum.get_ids,
    wiz_combo_list_min = 2,
    wiz_read_only = True
)
uf.desc = """
This is used to identify which of the loaded spectra are replicates of each other.  Specifying the replicates is essential for error analysis if the baseplane RMSD has not been supplied.
"""
uf.prompt_examples = """
To specify that the NOE spectra labelled 'ref1', 'ref2', and 'ref3' are the same spectrum
replicated, type one of:

relax> spectrum.replicated(['ref1', 'ref2', 'ref3'])
relax> spectrum.replicated(spectrum_ids=['ref1', 'ref2', 'ref3'])

To specify that the two R2 spectra 'ncyc2' and 'ncyc2b' are the same time point, type:

relax> spectrum.replicated(['ncyc2', 'ncyc2b'])
"""
uf.backend = spectrum.replicated
uf.menu_text = "re&plicated"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'
