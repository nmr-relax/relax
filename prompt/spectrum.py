###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
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
"""Module containing the 'spectrum' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
import help
from relax_errors import RelaxIntError, RelaxListIntError, RelaxNoneIntError, RelaxNoneIntListIntError, RelaxNoneStrError, RelaxNumError, RelaxStrError
from generic_fns import spectrum


class Spectrum:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for supporting the input of spectral data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def baseplane_rmsd(self, error=0.0, spectrum_id=None, spin_id=None):
        """Set the baseplane RMSD of a given spin in a spectrum for error analysis.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        error:  The baseplane RMSD error value.

        spectrum_id:  The spectrum identification string.

        spin_id:  The spin identification string.


        Description
        ~~~~~~~~~~~

        The spectrum_id argument identifies the spectrum associated with the error and must
        correspond to a previously loaded set of intensities.  If the 'spin_id' argument is left on
        the default of None, then the error value for all spins will be set to the supplied value.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spectrum.baseplane_rmsd("
            text = text + "error=" + repr(error)
            text = text + ", spectrum_id=" + repr(spectrum_id)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The error.
        if not isinstance(error, float) and not isinstance(error, int):
            raise RelaxNumError('error', error)

        # The spectrum identification string.
        if not isinstance(spectrum_id, str):
            raise RelaxStrError('spectrum identification string', spectrum_id)

        # Spin identification string.
        if spin_id != None and not isinstance(spin_id, str):
            raise RelaxNoneStrError('spin identification string', spin_id)

        # Execute the functional code.
        spectrum.baseplane_rmsd(error=error, spectrum_id=spectrum_id, spin_id=spin_id)


    def error_analysis(self):
        """Function for performing an error analysis for peak intensities.

        Description
        ~~~~~~~~~~~

        This user function must only be called after all peak intensities have been loaded and all
        other necessary spectral information set.  This includes the baseplane RMSD and the number
        of points used in volume integration, both of which are only used if spectra have not been
        replicated.

        Six different types of error analysis are supported depending on whether peak heights or
        volumes are supplied, whether noise is determined from replicated spectra or the RMSD of the
        baseplane noise, and whether all spectra or only a subset have been duplicated.  These are:

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


        Peak heights with baseplane noise RMSD
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        When none of the spectra have been replicated, then the peak height errors are calculated
        using the RMSD of the baseplane noise, the value of which is set by the
        spectrum.baseplane_rmsd() user function.  This results in a different error per peak per
        spectrum.  The standard deviation error measure for the peak height, sigma_I, is set to the
        RMSD value.


        Peak heights with partially replicated spectra
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        When spectra are replicated, the variance for a single spin at a single replicated spectra
        set is calculated by the formula

        -----

            sigma^2 =  sum({Ii - Iav}^2) / (n - 1) ,

        -----

        where sigma^2 is the variance, sigma is the standard deviation, n is the size of the
        replicated spectra set with i being the corresponding index, Ii is the peak intensity for
        spectrum i, and Iav is the mean over all spectra i.e. the sum of all peak intensities
        divided by n.

        As the value of n in the above equation is always very low since normally only a couple of
        spectra are collected per replicated spectra set, the variance of all spins is averaged for
        a single replicated spectra set.  Although this results in all spins having the same error,
        the accuracy of the error estimate is significantly improved.

        If there are in addition to the replicated spectra loaded peak intensities which only
        consist of a single spectrum, i.e. not all spectra are replicated, then the variances of
        replicated replicated spectra sets will be averaged.  This will be used for the entire
        experiment so that there will be only a single error value for all spins and for all
        spectra.


        Peak heights with all spectra replicated
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        If all spectra are collected in duplicate (triplicate or higher number of spectra are
        supported), the each replicated spectra set will have its own error estimate.  The error
        for a single peak is calculated as when partially replicated spectra are collected, and
        these are again averaged to give a single error per replicated spectra set.  However as all
        replicated spectra sets will have their own error estimate, variance averaging across all
        spectra sets will not be performed.


        Peak volumes with baseplane noise RMSD
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The method of error analysis when no spectra have been replicated and peak volumes are used
        is highly dependent on the integration method.  Many methods simply sum the number of points
        within a fixed region, either a box or oval object.  The number of points used, N, must be
        specified by another user function in this class.  Then the error is simply given by the sum
        of variances:

        -----

            sigma_vol^2 = sigma_i^2 * N,

        -----

        where sigma_vol is the standard deviation of the volume, sigma_i is the standard deviation
        of a single point assumed to be equal to the RMSD of the baseplane noise, and N is the total
        number of points used in the summation integration method.  For a box integration method,
        this converts to the Nicholson, Kay, Baldisseri, Arango, Young, Bax, and Torchia (1992)
        Biochemistry, 31: 5253-5263 equation:

        -----

            sigma_vol = sigma_i * sqrt(n*m),

        -----

        where n and m are the dimensions of the box.  Note that a number of programs, for example
        peakint (http://hugin.ethz.ch/wuthrich/software/xeasy/xeasy_m15.html) does not use all
        points within the box.  And if the number N can not be determined, this category of error
        analysis is not possible.

        Also note that non-point summation methods, for example when line shape fitting is used to
        determine peak volumes, the equations above cannot be used.  Hence again this category of
        error analysis cannot be used.  This is the case for one of the three integration methods
        used by Sparky (http://www.cgl.ucsf.edu/home/sparky/manual/peaks.html#Integration).  And
        if fancy techniques are used, for example as Cara does to deconvolute overlapping peaks
        (http://www.cara.ethz.ch/Wiki/Integration), this again makes this error analysis impossible.


        Peak volumes with partially replicated spectra
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        When peak volumes are measured by any integration method and a few of the spectra are
        replicated, then the intensity errors are calculated identically as described in the 'Peak
        heights with partially replicated spectra' section above.


        Peak volumes with all spectra replicated
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        With all spectra replicated and again using any integration methodology, the intensity
        errors can be calculated as described in the 'Peak heights with all spectra replicated'
        section above.
        """


        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spectrum.error_analysis()"
            print(text)

        # Execute the functional code.
        spectrum.error_analysis()


    def integration_points(self, N=None, spectrum_id=None, spin_id=None):
        """Set the number of summed points used in volume integration of a given spin in a spectrum.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        N:  The number of points used by the summation volume integration method.

        spectrum_id:  The spectrum identification string.

        spin_id:  The spin identification string.


        Description
        ~~~~~~~~~~~

        For a complete description of which integration methods and how many points N are used for
        different integration techniques, please read the spectrum.error_analysis() documentation.

        The spectrum_id argument identifies the spectrum associated with the value of N and must
        correspond to a previously loaded set of intensities.  If the 'spin_id' argument is left on
        the default of None, then the number of summed points for all spins will be set to the
        supplied value.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spectrum.integration_points("
            text = text + "N=" + repr(N)
            text = text + ", spectrum_id=" + repr(spectrum_id)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The number of summed points.
        if not isinstance(N, int):
            raise RelaxIntError('number of summed points', N)

        # The spectrum identification string.
        if not isinstance(spectrum_id, str):
            raise RelaxStrError('spectrum identification string', spectrum_id)

        # Spin identification string.
        if spin_id != None and not isinstance(spin_id, str):
            raise RelaxNoneStrError('spin identification string', spin_id)

        # Execute the functional code.
        spectrum.integration_points(N=N, spectrum_id=spectrum_id, spin_id=spin_id)


    def read_intensities(self, file=None, dir=None, spectrum_id=None, heteronuc='N', proton='HN', int_col=None, int_method='height', mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, ncproc=None):
        """Function for reading peak intensities from a file for NOE calculations.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the file containing the intensity data.

        dir:  The directory where the file is located.

        spectrum_id:  The spectrum identification string.

        heteronuc:  The name of the heteronucleus as specified in the peak intensity file.

        proton:  The name of the proton as specified in the peak intensity file.

        int_col:  The column(s) containing the peak intensity data (for a non-standard format).

        int_method:  The integration method.

        mol_name_col:  The molecule name column used by the generic intensity file format.

        res_num_col:  The residue number column used by the generic intensity file format.

        res_name_col:  The residue name column used by the generic intensity file format.

        spin_num_col:  The spin number column used by the generic intensity file format.

        spin_name_col:  The spin name column used by the generic intensity file format.

        sep:  The column separator used by the generic intensity format (defaults to white space).

        ncproc:  The Bruker specific FID intensity scaling factor.


        Description
        ~~~~~~~~~~~

        The peak intensity can either be from peak heights or peak volumes.


        The 'spectrum_id' argument is a label which is subsequently utilised by other user
        functions.  If this identifier matches that of a previously loaded set of intensities, then
        this indicates a replicated spectrum.

        The 'heteronuc' and 'proton' arguments should be set respectively to the name of the
        heteronucleus and proton in the file.  Only those lines which match these labels will be
        used.

        The 'int_method' argument is required for the subsequent error analysis.  When peak heights
        are measured, this argument should be set to 'height'.  Volume integration methods are a bit
        varied and hence two values are accepted.  If the volume integration involves pure point
        summation, with no deconvolution algorithms or other methods affecting peak heights, then
        the argument should be set to 'point sum'.  All other volume integration methods, e.g. line
        shape fitting, the argument should be set to 'other'.

        If a series of intensities extracted from Bruker FID files processed in Topspin or XWinNMR
        are to be compared, the ncproc parameter may need to be supplied.  This is because this FID
        is stored using integer representation and is scaled using ncproc to avoid numerical
        truncation artifacts.  If two spectra have significantly different maximal intensities, then
        ncproc will be different for both.  The intensity scaling is binary, i.e. 2**ncproc.
        Therefore if spectrum A has an ncproc of 6 and and spectrum B a value of 7, then a reference
        intensity in B will be double that of A.  Internally, relax stores the intensities scaled by
        2**ncproc.


        File formats
        ~~~~~~~~~~~~

        The peak list or intensity file will be automatically determined.

        Sparky peak list:  The file should be a Sparky peak list saved after typing the command
        'lt'.  The default is to assume that columns 0, 1, 2, and 3 (1st, 2nd, 3rd, and 4th) contain
        the Sparky assignment, w1, w2, and peak intensity data respectively.  The frequency data w1
        and w2 are ignored while the peak intensity data can either be the peak height or volume
        displayed by changing the window options.  If the peak intensity data is not within column
        3, set the argument 'int_col' to the appropriate value (column numbering starts from 0
        rather than 1).

        XEasy peak list:  The file should be the saved XEasy text window output of the list peak
        entries command, 'tw' followed by 'le'.  As the columns are fixed, the peak intensity column
        is hardwired to number 10 (the 11th column) which contains either the peak height or peak
        volume data.  Because the columns are fixed, the 'int_col' argument will be ignored.

        NMRView:  The file should be a NMRView peak list. The default is to use column 16 (which
        contains peak heights) for peak intensities. To use use peak volumes (or evolumes), int_col
        must be set to 15.

        Generic intensity file:  This is a generic format which can be created by scripting to
        support non-supported peak lists.  It should contain in the first few columns enough
        information to identify the spin.  This can include columns for the molecule name, residue
        number, residue name, spin number, and spin name, with each optional type positioned with
        the *name_col and *num_col arguments.  The peak intensities can be placed in another column
        specified by the int_col argument.  Intensities from multiple spectra can be placed into
        different columns, and these can then be specified simultaneously by setting the int_col
        argument to a list of columns.  This list must be matched by setting the spectrum_id
        argument to list of the same length.  If columns are delimited by a character other than
        whitespace, this can be specified with the sep argument.


        Examples
        ~~~~~~~~

        To read the reference and saturated spectra peak heights from the Sparky formatted files
        'ref.list' and 'sat.list', type:

        relax> spectrum.read_intensities(file='ref.list', spectrum_id='ref')
        relax> spectrum.read_intensities(file='sat.list', spectrum_id='sat')

        To read the reference and saturated spectra peak heights from the XEasy formatted files
        'ref.text' and 'sat.text', type:

        relax> spectrum.read_intensities(file='ref.text', spectrum_id='ref')
        relax> spectrum.read_intensities(file='sat.text', spectrum_id='sat')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spectrum.read_intensities("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", spectrum_id=" + repr(spectrum_id)
            text = text + ", heteronuc=" + repr(heteronuc)
            text = text + ", proton=" + repr(proton)
            text = text + ", int_col=" + repr(int_col)
            text = text + ", int_method=" + repr(int_method)
            text = text + ", mol_name_col=" + repr(mol_name_col)
            text = text + ", res_num_col=" + repr(res_num_col)
            text = text + ", res_name_col=" + repr(res_name_col)
            text = text + ", spin_num_col=" + repr(spin_num_col)
            text = text + ", spin_name_col=" + repr(spin_name_col)
            text = text + ", sep=" + repr(sep) + ")"
            print(text)

        # The file name.
        if not isinstance(file, str):
            raise RelaxStrError('file name', file)

        # Directory.
        if dir != None and not isinstance(dir, str):
            raise RelaxNoneStrError('directory name', dir)

        # The spectrum identification string (or list).
        if not isinstance(spectrum_id, str) and not isinstance(spectrum_id, list):
            raise RelaxStrListStrError('spectrum identification string', spectrum_id)

        # The heteronucleus name.
        if not isinstance(heteronuc, str):
            raise RelaxStrError('heteronucleus name', heteronuc)

        # The proton name.
        if not isinstance(proton, str):
            raise RelaxStrError('proton name', proton)

        # The intensity column.
        if int_col != None and not isinstance(int_col, int) and not isinstance(int_col, list):
            raise RelaxNoneIntListIntError('intensity column', int_col)
        if isinstance(int_col, list):
            # Empty list.
            if int_col == []:
                raise RelaxListIntError('intensity column', int_col)

            # Check the values.
            for i in xrange(len(int_col)):
                if not isinstance(int_col[i], int):
                    raise RelaxListIntError('intensity column', int_col)

        # The integration method name.
        if not isinstance(int_method, str):
            raise RelaxStrError('integration method', int_method)

        # Molecule name column.
        if mol_name_col != None and not isinstance(mol_name_col, int):
            raise RelaxNoneIntError('molecule name column', mol_name_col)

        # Residue number column.
        if res_num_col != None and not isinstance(res_num_col, int):
            raise RelaxNoneIntError('residue number column', res_num_col)

        # Residue name column.
        if res_name_col != None and not isinstance(res_name_col, int):
            raise RelaxNoneIntError('residue name column', res_name_col)

        # Spin number column.
        if spin_num_col != None and not isinstance(spin_num_col, int):
            raise RelaxNoneIntError('spin number column', spin_num_col)

        # Spin name column.
        if spin_name_col != None and not isinstance(spin_name_col, int):
            raise RelaxNoneIntError('spin name column', spin_name_col)

        # Column separator.
        if sep != None and not isinstance(sep, str):
            raise RelaxNoneStrError('column separator', sep)

        # Bruker ncproc parameter.
        if ncproc != None and not isinstance(ncproc, int):
            raise RelaxNoneIntError('Bruker ncproc parameter', ncproc)

        # Execute the functional code.
        spectrum.read(file=file, dir=dir, spectrum_id=spectrum_id, heteronuc=heteronuc, proton=proton, int_col=int_col, int_method=int_method, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, ncproc=ncproc)


    def replicated(self, spectrum_ids=None):
        """Function for specifying which spectra are replicates.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spectrum_ids:  The list of replicated spectra identification strings.


        Description
        ~~~~~~~~~~~

        This user function is used to identify which loaded spectra are replicates of each other.
        This is very important for error analysis.


        Examples
        ~~~~~~~~

        To specify that the NOE spectra labelled 'ref1', 'ref2', and 'ref3' are the same spectrum
        replicated, type one of:

        relax> spectrum.replicated(['ref1', 'ref2', 'ref3'])
        relax> spectrum.replicated(spectrum_ids=['ref1', 'ref2', 'ref3'])

        To specify that the two R2 spectra 'ncyc2' and 'ncyc2b' are the same time point, type:

        relax> spectrum.replicated(['ncyc2', 'ncyc2b'])
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spectrum.replicated("
            text = text + "spectrum_ids=" + repr(spectrum_ids) + ")"
            print(text)

        # Spectrum ids.
        if not isinstance(spectrum_ids, list):
            raise RelaxListStrError('spectrum ids', spectrum_ids)
        else:
            # Empty list.
            if spectrum_ids == []:
                raise RelaxListStrError('spectrum ids', spectrum_ids)

            # Check the values.
            for i in xrange(len(spectrum_ids)):
                if not isinstance(spectrum_ids[i], str):
                    raise RelaxListStrError('spectrum ids', spectrum_ids)

        # Execute the functional code.
        spectrum.replicated(spectrum_ids=spectrum_ids)
