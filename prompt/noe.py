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

import sys

import help


class Noe:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for calculating NOE data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def error(self, run=None, error=0.0, spectrum_type=None, res_num=None, res_name=None):
        """Function for setting the errors in the reference or saturated NOE spectra.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        error:  The error.

        spectrum_type:  The type of spectrum.

        res_num:  The residue number.

        res_name:  The residue name.


        Description
        ~~~~~~~~~~~

        The spectrum_type argument can have the following values:
            'ref':  The NOE reference spectrum.
            'sat':  The NOE spectrum with proton saturation turned on.

        If the 'res_num' and 'res_name' arguments are left as the defaults of None, then the error
        value for all residues will be set to the supplied value.  Otherwise the residue number can
        be set to either an integer for selecting a single residue or a python regular expression
        string for selecting multiple residues.  The residue name argument must be a string and can
        use regular expression as well.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "noe.error("
            text = text + "run=" + `run`
            text = text + ", error=" + `error`
            text = text + ", spectrum_type=" + `spectrum_type`
            text = text + ", res_num=" + `res_num`
            text = text + ", res_name=" + `res_name` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The error.
        if type(error) != float and type(error) != int:
            raise RelaxNumError, ('error', error)

        # The spectrum type.
        if type(spectrum_type) != str:
            raise RelaxStrError, ('spectrum type', spectrum_type)

        # Residue number.
        if res_num != None and type(res_num) != int and type(res_num) != str:
            raise RelaxNoneIntStrError, ('residue number', res_num)

        # Residue name.
        if res_name != None and type(res_name) != str:
            raise RelaxNoneStrError, ('residue name', res_name)

        # Execute the functional code.
        self.__relax__.specific.noe.set_error(run=run, error=error, spectrum_type=spectrum_type, res_num=res_num, res_name=res_name)


    def read(self, run=None, file=None, dir=None, spectrum_type=None, format='sparky', heteronuc='N', proton='HN', int_col=None):
        """Function for reading peak intensities from a file for NOE calculations.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the file containing the sequence data.

        dir:  The directory where the file is located.

        spectrum_type:  The type of spectrum.

        format:  The type of file containing peak intensities.

        heteronuc:  The name of the heteronucleus as specified in the peak intensity file.

        proton:  The name of the proton as specified in the peak intensity file.

        int_col:  The column containing the peak intensity data (for a non-standard formatted file).


        Description
        ~~~~~~~~~~~

        The peak intensity can either be from peak heights or peak volumes.


        The 'spectrum_type' argument can have the following values:
            'ref':  The NOE reference spectrum.
            'sat':  The NOE spectrum with proton saturation turned on.


        The 'format' argument can currently be set to:
            'sparky'
            'xeasy'

        If the 'format' argument is set to 'sparky', the file should be a Sparky peak list saved
        after typing the command 'lt'.  The default is to assume that columns 0, 1, 2, and 3 (1st,
        2nd, 3rd, and 4th) contain the Sparky assignment, w1, w2, and peak intensity data
        respectively.  The frequency data w1 and w2 are ignored while the peak intensity data can
        either be the peak height or volume displayed by changing the window options.  If the peak
        intensity data is not within column 3, set the argument 'int_col' to the appropriate value
        (column numbering starts from 0 rather than 1).

        If the 'format' argument is set to 'xeasy', the file should be the saved XEasy text window
        output of the list peak entries command, 'tw' followed by 'le'.  As the columns are fixed,
        the peak intensity column is hardwired to number 10 (the 11th column) which contains either
        the peak height or peak volume data.  Because the columns are fixed, the 'int_col' argument
        will be ignored.


        The 'heteronuc' and 'proton' arguments should be set respectively to the name of the
        heteronucleus and proton in the file.  Only those lines which match these labels will be
        used.


        Examples
        ~~~~~~~~

        To read the reference and saturated spectra peak heights from the Sparky formatted files
        'ref.list' and 'sat.list' to the run 'noe', type:

        relax> noe.read('noe', file='ref.list', spectrum_type='ref')
        relax> noe.read('noe', file='sat.list', spectrum_type='sat')

        To read the reference and saturated spectra peak heights from the XEasy formatted files
        'ref.text' and 'sat.text' to the run 'noe', type:

        relax> noe.read('noe', file='ref.text', spectrum_type='ref', format='xeasy')
        relax> noe.read('noe', file='sat.text', spectrum_type='sat', format='xeasy')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "noe.read("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", spectrum_type=" + `spectrum_type`
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

        # The spectrum type.
        if type(spectrum_type) != str:
            raise RelaxStrError, ('spectrum type', spectrum_type)

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
        self.__relax__.specific.noe.read(run=run, file=file, dir=dir, spectrum_type=spectrum_type, format=format, heteronuc=heteronuc, proton=proton, int_col=int_col)
