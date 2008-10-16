###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006 Edward d'Auvergne                                  #
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

import sys

import help


class Relax_fit:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for relaxation curve fitting."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def mean_and_error(self, run=None):
        """Function for calculating the average intensity and standard deviation of all spectra.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.


        Errors of individual residues at a single time point
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The standard deviation for a single residue at a single time point is calculated by the
        formula

        -----

            sigma =  sum({Ii - Iav}^2) / (n - 1) ,

        -----

        where sigma is the variance or square of the standard deviation, n is the total number of
        collected spectra for the time point and i is the corresponding index, Ii is the peak
        intensity for spectrum i, Iav is the mean over all spectra, ie the sum of all peak
        intensities divided by n.


        Averaging of the errors
        ~~~~~~~~~~~~~~~~~~~~~~~

        As the value of n in the above equation is always very low, normally only a couple of
        spectra are collected per time point, the variance of all spins is averaged for a single
        time point.  Although this results in all spins having the same error, the accuracy of the
        error estimate is significantly improved.


        Errors across multiple time points
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        If all spectra are collected in duplicate (triplicate or higher number of spectra are
        supported), the each time point will have its own error estimate.  However, if there are
        time points in the series which only consist of a single spectrum, then the variances of
        replicated time points will be averaged.  Hence, for the entire experiment there will be a
        single error value for all spins and for all time points.

        A better approach rather than averaging across all time points would be to use a form of
        interpolation as the errors across time points generally decreases for longer time periods.
        This is currently not implemented.
        """


        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_fit.mean_and_error("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.specific.relax_fit.mean_and_error(run=run)


    def read(self, run=None, file=None, dir=None, relax_time=0.0, format='sparky', heteronuc='N', proton='HN', int_col=None):
        """Function for reading peak intensities from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the file containing the sequence data.

        dir:  The directory where the file is located.

        relax_time:  The time, in seconds, of the relaxation period.

        format:  The type of file containing peak intensities.

        heteronuc:  The name of the heteronucleus as specified in the peak intensity file.

        proton:  The name of the proton as specified in the peak intensity file.

        int_col:  The column containing the peak intensity data (for a non-standard formatted file).


        Description
        ~~~~~~~~~~~

        The peak intensity can either be from peak heights or peak volumes.


        The format argument can currently be set to:
            'sparky'
            'xeasy'

        If the format argument is set to 'sparky', the file should be a Sparky peak list saved after
        typing the command 'lt'.  The default is to assume that columns 0, 1, 2, and 3 (1st, 2nd,
        3rd, and 4th) contain the Sparky assignment, w1, w2, and peak intensity data respectively.
        The frequency data w1 and w2 are ignored while the peak intensity data can either be the
        peak height or volume displayed by changing the window options.  If the peak intensity data
        is not within column 3, set the argument int_col to the appropriate value (column numbering
        starts from 0 rather than 1).

        If the format argument is set to 'xeasy', the file should be the saved XEasy text window
        output of the list peak entries command, 'tw' followed by 'le'.  As the columns are fixed,
        the peak intensity column is hardwired to number 10 (the 11th column) which contains either
        the peak height or peak volume data.  Because the columns are fixed, the int_col argument
        will be ignored.


        The heteronuc and proton arguments should be set respectively to the name of the
        heteronucleus and proton in the file.  Only those lines which match these labels will be
        used.


        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_fit.read("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", relax_time=" + `relax_time`
            text = text + ", format=" + `format`
            text = text + ", heteronuc=" + `heteronuc`
            text = text + ", proton=" + `proton`
            text = text + ", int_col=" + `int_col` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The file name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The relaxation time.
        if type(relax_time) != float:
            raise RelaxFloatError, ('relaxation time', relax_time)

        # The format.
        if type(format) != str:
            raise RelaxStrError, ('format', format)

        # The heteronucleus name.
        if type(heteronuc) != str:
            raise RelaxStrError, ('heteronucleus name', heteronuc)

        # The proton name.
        if type(proton) != str:
            raise RelaxStrError, ('proton name', proton)

        # The intensity column.
        if int_col and type(int_col) != int:
            raise RelaxNoneIntError, ('intensity column', int_col)

        # Execute the functional code.
        self.__relax__.specific.relax_fit.read(run=run, file=file, dir=dir, relax_time=relax_time, format=format, heteronuc=heteronuc, proton=proton, int_col=int_col)


    def select_model(self, run=None, model='exp'):
        """Function for the selection of the relaxation curve type.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        model:  The type of relaxation curve to fit.


        The preset models
        ~~~~~~~~~~~~~~~~~

        The supported relaxation experiments include the default two parameter exponential fit,
        selected by setting the 'fit_type' argument to 'exp', and the three parameter inversion
        recovery experiment in which the peak intensity limit is a non-zero value, selected by
        setting the argument to 'inv'.

        The parameters of these two models are
            'exp': [Rx, I0],
            'inv': [Rx, I0, Iinf].
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_fit.select_model("
            text = text + "run=" + `run`
            text = text + ", model=" + `model` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The model argument.
        if type(model) != str:
            raise RelaxStrError, ('model', model)

        # Execute the functional code.
        self.__relax__.specific.relax_fit.select_model(run=run, model=model)
