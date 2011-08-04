###############################################################################
#                                                                             #
# Copyright (C) 2004-2011 Edward d'Auvergne                                   #
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
"""Module containing the 'grace' user function class for controlling the Grace data viewing software."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
from doc_string import docs
from generic_fns import grace, minimise
from specific_fns.model_free import Model_free
from specific_fns.jw_mapping import Jw_mapping
from specific_fns.noe import Noe
from specific_fns.relax_fit import Relax_fit


class Grace(User_fn_class):
    """Class for interfacing with Grace."""

    def view(self, file=None, dir='grace', grace_exe='xmgrace'):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "grace.view("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", grace_exe=" + repr(grace_exe) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_str(grace_exe, 'Grace executable file')

        # Execute the functional code.
        grace.view(file=file, dir=dir, grace_exe=grace_exe)

    # The function doc info.
    view._doc_title = "Visualise the file within Grace."
    view._doc_title_short = "Grace execution."
    view._doc_args = [
        ["file", "The name of the file."],
        ["dir", "The directory name."],
        ["grace_exe", "The Grace executable file."]
    ]
    view._doc_desc = """
        This can be used to view the specified Grace '*.agr' file by opening it with the Grace program.
        """
    view._doc_examples = """
        To view the file 's2.agr' in the directory 'grace', type:

        relax> grace.view(file='s2.agr')
        relax> grace.view(file='s2.agr', dir='grace')
        """
    _build_doc(view)


    def write(self, x_data_type='spin', y_data_type=None, spin_id=None, plot_data='value', file=None, dir='grace', force=False, norm=False):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "grace.write("
            text = text + "x_data_type=" + repr(x_data_type)
            text = text + ", y_data_type=" + repr(y_data_type)
            text = text + ", spin_id=" + repr(spin_id)
            text = text + ", plot_data=" + repr(plot_data)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force)
            text = text + ", norm=" + repr(norm) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(x_data_type, 'x data type')
        arg_check.is_str(y_data_type, 'y data type')
        arg_check.is_str(spin_id, 'spin identification string', can_be_none=True)
        arg_check.is_str(plot_data, 'plot data')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')
        arg_check.is_bool(norm, 'normalisation flag')

        # Execute the functional code.
        grace.write(x_data_type=x_data_type, y_data_type=y_data_type, spin_id=spin_id, plot_data=plot_data, file=file, dir=dir, force=force, norm=norm)

    # The function doc info.
    write._doc_title = "Create a grace '.agr' file."
    write._doc_title_short = "Grace file creation."
    write._doc_args = [
        ["x_data_type", "The data type for the X-axis (no regular expression is allowed)."],
        ["y_data_type", "The data type for the Y-axis (no regular expression is allowed)."],
        ["spin_id", "The spin identification string."],
        ["plot_data", "The data to use for the plot."],
        ["norm", "Flag for the normalisation of series type data."],
        ["file", "The name of the file."],
        ["dir", "The directory name."],
        ["force", "A flag which, if set to True, will cause the file to be overwritten."]
    ]
    write._doc_desc = """
        This is designed to be as flexible as possible so that any combination of data can be plotted.  The output is in the format of a Grace plot (also known as ACE/gr, Xmgr, and xmgrace) which only supports two dimensional plots.  Three types of keyword arguments can be used to create various types of plot.  These include the X-axis and Y-axis data types, the spin identification string, and an argument for selecting what to actually plot.

        The X-axis and Y-axis data type arguments should be plain strings, regular expression is not allowed.  If the X-axis data type argument is not given, the plot will default to having the spin sequence along the x-axis.  The two axes of the Grace plot can be absolutely any of the data types listed in the tables below.  The only limitation, currently anyway, is that the data must belong to the same data pipe.

        The spin identification string can be used to limit which spins are used in the plot.  The default is that all spins will be used, however, these arguments can be used to select a subset of all spins, or a single spin for plots of Monte Carlo simulations, etc.

        The property which is actually plotted can be controlled by the 'plot_data' argument.  It can be one of the following:

            'value':  Plot values (with errors if they exist).
            'error':  Plot errors.
            'sims':   Plot the simulation values.

        Normalisation is only allowed for series type data, for example the R2 exponential curves, and will be ignored for all other data types.  If the norm flag is set to True then the y-value of the first point of the series will be set to 1.  This normalisation is useful for highlighting errors in the data sets.
        """
    write._doc_examples = """
        To write the NOE values for all spins to the Grace file 'noe.agr', type one of:

        relax> grace.write('spin', 'noe', file='noe.agr')
        relax> grace.write(y_data_type='noe', file='noe.agr')
        relax> grace.write(x_data_type='spin', y_data_type='noe', file='noe.agr')
        relax> grace.write(y_data_type='noe', file='noe.agr', force=True)


        To create a Grace file of 'S2' vs. 'te' for all spins, type one of:

        relax> grace.write('S2', 'te', file='s2_te.agr')
        relax> grace.write(x_data_type='S2', y_data_type='te', file='s2_te.agr')
        relax> grace.write(x_data_type='S2', y_data_type='te', file='s2_te.agr', force=True)


        To create a Grace file of the Monte Carlo simulation values of 'Rex' vs. 'te' for residue
        123, type one of:

        relax> grace.write('Rex', 'te', spin_id=':123', plot_data='sims', file='s2_te.agr')
        relax> grace.write(x_data_type='Rex', y_data_type='te', spin_id=':123',
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
    write._doc_additional = [
        docs.regexp.doc,
        minimise.return_data_name_doc,
        Noe.return_data_name_doc,
        Relax_fit.return_data_name_doc,
        Jw_mapping.return_data_name_doc,
        Model_free.return_data_name_doc
    ]
    _build_doc(write)
