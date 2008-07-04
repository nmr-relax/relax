###############################################################################
#                                                                             #
# Copyright (C) 2004-2005 Edward d'Auvergne                                   #
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

# Python module imports.
import sys

# relax module imports.
from relax_errors import RelaxBinError, RelaxNoneIntStrError, RelaxNoneStrError, RelaxStrError
from doc_string import regexp_doc
import help
from generic_fns import grace, minimise
from specific_fns.model_free import Model_free
from specific_fns.jw_mapping import Jw_mapping
from specific_fns.noe import Noe
from specific_fns.relax_fit import Relax_fit


class Grace:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for interfacing with Grace."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def view(self, file=None, dir='grace', grace_exe='xmgrace'):
        """Function for running Grace.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the file.

        dir:  The directory name.

        grace_exe:  The Grace executable file.


        Description
        ~~~~~~~~~~~

        This function can be used to execute Grace to view the specified file the Grace '.agr' file
        and the execute Grace. If the directory name is set to None, the file will be assumed to be
        in the current working directory.


        Examples
        ~~~~~~~~

        To view the file 's2.agr' in the directory 'grace', type:

        relax> grace.view(file='s2.agr')
        relax> grace.view(file='s2.agr', dir='grace')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "grace.view("
            text = text + "file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", grace_exe=" + `grace_exe` + ")"
            print text

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Grace executable file.
        if type(grace_exe) != str:
            raise RelaxStrError, ('Grace executable file', grace_exe)

        # Execute the functional code.
        self.__relax__.generic.grace.view(file=file, dir=dir, grace_exe=grace_exe)


    def write(self, x_data_type='res', y_data_type=None, res_num=None, res_name=None, plot_data='value', norm=0, file=None, dir='grace', force=False):
        """Function for creating a grace '.agr' file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        x_data_type:  The data type for the X-axis (no regular expression is allowed).

        y_data_type:  The data type for the Y-axis (no regular expression is allowed).

        res_num:  The residue number (regular expression is allowed).

        res_name:  The residue name (regular expression is allowed).

        plot_data:  The data to use for the plot.

        norm:  Flag for the normalisation of series type data.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which, if set to True, will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        This function is designed to be as flexible as possible so that any combination of data can
        be plotted.  The output is in the format of a Grace plot (also known as ACE/gr, Xmgr, and
        xmgrace) which only supports two dimensional plots.  Three types of keyword arguments can
        be used to create various types of plot.  These include the X-axis and Y-axis data types,
        the residue number and name selection arguments, and an argument for selecting what to
        actually plot.

        The X-axis and Y-axis data type arguments should be plain strings, regular expression is not
        allowed.  If the X-axis data type argument is not given, the plot will default to having the
        residue number along the x-axis.  The two axes of the Grace plot can be absolutely any of
        the data types listed in the tables below.  The only limitation, currently anyway, is that
        the data must belong to the same run.

        The residue number and name arguments can be used to limit the residues used in the plot.
        The default is that all residues will be used, however, these arguments can be used to
        select a subset of all residues, or a single residue for plots of Monte Carlo simulations,
        etc.  Regular expression is allowed for both the residue number and name, and the number can
        either be an integer or a string.

        The property which is actually plotted can be controlled by the 'plot_data' argument.  It
        can be one of the following:
            'value':  Plot values (with errors if they exist).
            'error':  Plot errors.
            'sims':   Plot the simulation values.

        Normalisation is only allowed for series type data, for example the R2 exponential curves,
        and will be ignored for all other data types.  If the norm flag is set to one then the
        y-value of the first point of the series will be set to 1.  This normalisation is useful for
        emphasising errors in the data sets.


        Examples
        ~~~~~~~~

        To write the NOE values for all residues to the Grace file 'noe.agr',
        type:

        relax> grace.write('res', 'noe', file='noe.agr')
        relax> grace.write(y_data_type='noe', file='noe.agr')
        relax> grace.write(x_data_type='res', y_data_type='noe', file='noe.agr')
        relax> grace.write(y_data_type='noe', file='noe.agr', force=True)


        To create a Grace file of 'S2' vs. 'te' for all residues, type:

        relax> grace.write('S2', 'te', file='s2_te.agr')
        relax> grace.write(x_data_type='S2', y_data_type='te', file='s2_te.agr')
        relax> grace.write(x_data_type='S2', y_data_type='te', file='s2_te.agr', force=True)


        To create a Grace file of the Monte Carlo simulation values of 'Rex' vs. 'te' for residue
        123, type:

        relax> grace.write('Rex', 'te', res_num=123, plot_data='sims', file='s2_te.agr')
        relax> grace.write(x_data_type='Rex', y_data_type='te', res_num=123,
                           plot_data='sims', file='s2_te.agr')


        By plotting the peak intensities, the integrity of exponential relaxation curves can be
        checked and anomalies searched for prior to model-free analysis or reduced spectral density
        mapping.  For example the normalised average peak intensities can be plotted verses the
        relaxation time periods for the relaxation curves of all residues of a protein.  The
        normalisation, whereby the initial peak intensity of each residue I(0) is set to 1,
        emphasises any problems.  To produce this Grace file, type:

        relax> grace.write(name, x_data_type='relax_times', y_data_type='ave_int',
                           norm=1, file='intensities_norm.agr', force=True)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "grace.write("
            text = text + "x_data_type=" + `x_data_type`
            text = text + ", y_data_type=" + `y_data_type`
            text = text + ", res_num=" + `res_num`
            text = text + ", res_name=" + `res_name`
            text = text + ", plot_data=" + `plot_data`
            text = text + ", norm=" + `norm`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # Data type for x-axis.
        if type(x_data_type) != str:
            raise RelaxStrError, ('x data type', x_data_type)

        # Data type for y-axis.
        if type(y_data_type) != str:
            raise RelaxStrError, ('y data type', y_data_type)

        # Residue number.
        if res_num != None and type(res_num) != int and type(res_num) != str:
            raise RelaxNoneIntStrError, ('residue number', res_num)

        # Residue name.
        if res_name != None and type(res_name) != str:
            raise RelaxNoneStrError, ('residue name', res_name)

        # The plot data.
        if type(plot_data) != str:
            raise RelaxStrError, ('plot data', plot_data)

        # File.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != bool:
            raise RelaxBoolError, ('force flag', force)

        # Execute the functional code.
        grace.write(x_data_type=x_data_type, y_data_type=y_data_type, res_num=res_num, res_name=res_name, plot_data=plot_data, norm=norm, file=file, dir=dir, force=force)



    # Docstring modification.
    #########################

    # Write function.
    write.__doc__ = write.__doc__ + "\n\n" + regexp_doc() + "\n"
    write.__doc__ = write.__doc__ + minimise.return_data_name.__doc__ + "\n\n"
    write.__doc__ = write.__doc__ + Noe.return_data_name.__doc__ + "\n"
    write.__doc__ = write.__doc__ + Relax_fit.return_data_name.__doc__ + "\n"
    write.__doc__ = write.__doc__ + Jw_mapping.return_data_name.__doc__ + "\n\n"
    write.__doc__ = write.__doc__ + Model_free.return_data_name.__doc__ + "\n\n"
