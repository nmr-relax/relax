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
"""The grace user function definitions for controlling the Grace data viewing software."""

# Python module imports.
import wx

# relax module imports.
from generic_fns import grace, minimise
from graphics import WIZARD_IMAGE_PATH
from prompt.doc_string import docs
from specific_fns.model_free import Model_free
from specific_fns.jw_mapping import Jw_mapping
from specific_fns.noe import Noe
from specific_fns.relax_fit import Relax_fit
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('grace')
uf_class.title = "Class for interfacing with Grace."
uf_class.menu_text = "&grace"
uf_class.gui_icon = "relax.grace_icon"


# The grace.view user function.
uf = uf_info.add_uf('grace.view')
uf.title = "Visualise the file within Grace."
uf.title_short = "Grace execution."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file.",
    wiz_filesel_wildcard = "Grace files (*.agr)|*.agr;*.AGR",
    wiz_filesel_style = wx.FD_OPEN
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
    name = "grace_exe",
    default = "xmgrace",
    py_type = "str",
    desc_short = "Grace executable file",
    desc = "The Grace executable file."
)
uf.desc = """
This can be used to view the specified Grace '*.agr' file by opening it with the Grace program.
"""
uf.prompt_examples = """
To view the file 's2.agr' in the directory 'grace', type:

relax> grace.view(file='s2.agr')
relax> grace.view(file='s2.agr', dir='grace')
"""
uf.backend = grace.view
uf.menu_text = "&view"
uf.gui_icon = "relax.grace_icon"
uf.wizard_size = (900, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'grace.png'


# The grace.write user function.
uf = uf_info.add_uf('grace.write')
uf.title = "Create a grace '.agr' file to visualise the 2D data."
uf.title_short = "Grace file creation."
uf.add_keyarg(
    name = "x_data_type",
    default = "spin",
    py_type = "str",
    desc_short = "x data type",
    desc = "The data type for the X-axis (no regular expression is allowed).",
    wiz_element_type = 'combo',
    wiz_combo_iter = grace.get_data_types
)
uf.add_keyarg(
    name = "y_data_type",
    py_type = "str",
    desc_short = "y data type",
    desc = "The data type for the Y-axis (no regular expression is allowed).",
    wiz_element_type = 'combo',
    wiz_combo_iter = grace.get_data_types
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identification string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "plot_data",
    default = "value",
    py_type = "str",
    desc_short = "plot data",
    desc = "The data to use for the plot.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "Values",
        "Errors",
        "Simulation values"
    ],
    wiz_combo_data = [
        "value",
        "error",
        "sims"
    ],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the file.",
    wiz_filesel_wildcard = "Grace files (*.agr)|*.agr;*.AGR",
    wiz_filesel_style = wx.FD_SAVE
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
uf.desc = """
This is designed to be as flexible as possible so that any combination of data can be plotted.  The output is in the format of a Grace plot (also known as ACE/gr, Xmgr, and xmgrace) which only supports two dimensional plots.  Three types of keyword arguments can be used to create various types of plot.  These include the X-axis and Y-axis data types, the spin identification string, and an argument for selecting what to plot.

The X-axis and Y-axis data type arguments should be plain strings, regular expression is not allowed.  If the X-axis data type argument is not given, the plot will default to having the spin sequence along the x-axis.  The two axes of the Grace plot can be absolutely any of the data types listed in the tables below.  The only limitation, currently anyway, is that the data must belong to the same data pipe.

The spin identification string can be used to limit which spins are used in the plot.  The default is that all spins will be used, however, these arguments can be used to select a subset of all spins, or a single spin for plots of Monte Carlo simulations, etc.

The property which is actually plotted can be controlled by the 'plot_data' argument.  It can be one of the following:

    'value':  Plot values (with errors if they exist).
    'error':  Plot errors.
    'sims':   Plot the simulation values.

Normalisation is only allowed for series type data, for example the R2 exponential curves, and will be ignored for all other data types.  If the norm flag is set to True then the y-value of the first point of the series will be set to 1.  This normalisation is useful for highlighting errors in the data sets.
"""
uf.additional = [
    docs.regexp.doc,
    minimise.return_data_name_doc,
    Noe.return_data_name_doc,
    Relax_fit.return_data_name_doc,
    Jw_mapping.return_data_name_doc,
    Model_free.return_data_name_doc
]
uf.prompt_examples = """
To write the NOE values for all spins to the Grace file 'noe.agr', type one of:

relax> grace.write('spin', 'noe', file='noe.agr')
relax> grace.write(y_data_type='noe', file='noe.agr')
relax> grace.write(x_data_type='spin', y_data_type='noe', file='noe.agr')
relax> grace.write(y_data_type='noe', file='noe.agr', force=True)


To create a Grace file of 's2' vs. 'te' for all spins, type one of:

relax> grace.write('s2', 'te', file='s2_te.agr')
relax> grace.write(x_data_type='s2', y_data_type='te', file='s2_te.agr')
relax> grace.write(x_data_type='s2', y_data_type='te', file='s2_te.agr', force=True)


To create a Grace file of the Monte Carlo simulation values of 'rex' vs. 'te' for residue
123, type one of:

relax> grace.write('rex', 'te', spin_id=':123', plot_data='sims', file='s2_te.agr')
relax> grace.write(x_data_type='rex', y_data_type='te', spin_id=':123',
                   plot_data='sims', file='s2_te.agr')


By plotting the peak intensities, the integrity of exponential relaxation curves can be
checked and anomalies searched for prior to model-free analysis or reduced spectral density
mapping.  For example the normalised average peak intensities can be plotted verses the
relaxation time periods for the relaxation curves of all residues of a protein.  The
normalisation, whereby the initial peak intensity of each residue I(0) is set to 1,
emphasises any problems.  To produce this Grace file, type:

relax> grace.write(x_data_type='relax_times', y_data_type='ave_int',
                   file='intensities_norm.agr', force=True, norm=True)
"""
uf.backend = grace.write
uf.menu_text = "&write"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (1000, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'grace.png'
