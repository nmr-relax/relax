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
"""Module containing the 'spectrum' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
from generic_fns import spectrum


class Spectrum(User_fn_class):
    """Class for supporting the input of spectral data."""

    def baseplane_rmsd(self, error=0.0, spectrum_id=None, spin_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spectrum.baseplane_rmsd("
            text = text + "error=" + repr(error)
            text = text + ", spectrum_id=" + repr(spectrum_id)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num(error, 'error')
        arg_check.is_str(spectrum_id, 'spectrum ID string')
        arg_check.is_str(spin_id, 'spin ID string', can_be_none=True)

        # Execute the functional code.
        spectrum.baseplane_rmsd(error=error, spectrum_id=spectrum_id, spin_id=spin_id)

    # The function doc info.
    baseplane_rmsd._doc_title = "Set the baseplane RMSD of a given spin in a spectrum for error analysis."
    baseplane_rmsd._doc_title_short = "Baseplane RMSD setting."
    baseplane_rmsd._doc_args = [
        ["error", "The baseplane RMSD error value."],
        ["spectrum_id", "The spectrum ID string."],
        ["spin_id", "The spin ID string."]
    ]
    baseplane_rmsd._doc_desc = """
        The spectrum ID identifies the spectrum associated with the error and must correspond to a previously loaded set of intensities.  If the spin ID is unset, then the error value for all spins will be set to the supplied value.
        """
    _build_doc(baseplane_rmsd)


    def error_analysis(self):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spectrum.error_analysis()"
            print(text)

        # Execute the functional code.
        spectrum.error_analysis()

    # The function doc info.
    error_analysis._doc_title = "Perform an error analysis for peak intensities."
    error_analysis._doc_title_short = "Peak intensity error analysis."
    error_analysis._doc_desc = """
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
    error_analysis._doc_additional = [
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
    _build_doc(error_analysis)


    def integration_points(self, N=None, spectrum_id=None, spin_id=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spectrum.integration_points("
            text = text + "N=" + repr(N)
            text = text + ", spectrum_id=" + repr(spectrum_id)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_int(N, 'number of summed points')
        arg_check.is_str(spectrum_id, 'spectrum ID string')
        arg_check.is_str(spin_id, 'spin ID string', can_be_none=True)

        # Execute the functional code.
        spectrum.integration_points(N=N, spectrum_id=spectrum_id, spin_id=spin_id)

    # The function doc info.
    integration_points._doc_title = "Set the number of summed points used in volume integration of a given spin in a spectrum."
    integration_points._doc_title_short = "Number of integration points."
    integration_points._doc_args = [
        ["N", "The number of points used by the summation volume integration method."],
        ["spectrum_id", "The spectrum ID string."],
        ["spin_id", "The spin ID string."]
    ]
    integration_points._doc_desc = """
        For a complete description of which integration methods and how many points N are used for different integration techniques, please see the spectrum.error_analysis user function documentation.

        The spectrum ID identifies the spectrum associated with the value of N and must correspond to a previously loaded set of intensities.  If the spin ID is unset, then the number of summed points for all spins will be set to the supplied value.
        """
    _build_doc(integration_points)


    def read_intensities(self, file=None, dir=None, spectrum_id=None, heteronuc='N', proton='HN', int_col=None, int_method='height', spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, spin_id=None, ncproc=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spectrum.read_intensities("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", spectrum_id=" + repr(spectrum_id)
            text = text + ", heteronuc=" + repr(heteronuc)
            text = text + ", proton=" + repr(proton)
            text = text + ", int_col=" + repr(int_col)
            text = text + ", int_method=" + repr(int_method)
            text = text + ", spin_id_col=" + repr(spin_id_col)
            text = text + ", mol_name_col=" + repr(mol_name_col)
            text = text + ", res_num_col=" + repr(res_num_col)
            text = text + ", res_name_col=" + repr(res_name_col)
            text = text + ", spin_num_col=" + repr(spin_num_col)
            text = text + ", spin_name_col=" + repr(spin_name_col)
            text = text + ", sep=" + repr(sep)
            text = text + ", spin_id=" + repr(spin_id)
            text = text + ", ncproc=" + repr(ncproc) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_str_or_str_list(spectrum_id, 'spectrum ID string')
        arg_check.is_str(heteronuc, 'heteronucleus name')
        arg_check.is_str(proton, 'proton name')
        arg_check.is_int_or_int_list(int_col, 'intensity column', can_be_none=True)
        arg_check.is_str(int_method, 'integration method')
        arg_check.is_int(spin_id_col, 'spin ID string column', can_be_none=True)
        arg_check.is_int(mol_name_col, 'molecule name column', can_be_none=True)
        arg_check.is_int(res_num_col, 'residue number column', can_be_none=True)
        arg_check.is_int(res_name_col, 'residue name column', can_be_none=True)
        arg_check.is_int(spin_num_col, 'spin number column', can_be_none=True)
        arg_check.is_int(spin_name_col, 'spin name column', can_be_none=True)
        arg_check.is_str(sep, 'column separator', can_be_none=True)
        arg_check.is_str(spin_id, 'spin ID string', can_be_none=True)
        arg_check.is_int(ncproc, 'Bruker ncproc parameter', can_be_none=True)

        # Execute the functional code.
        spectrum.read(file=file, dir=dir, spectrum_id=spectrum_id, heteronuc=heteronuc, proton=proton, int_col=int_col, int_method=int_method, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id, ncproc=ncproc)

    # The function doc info.
    read_intensities._doc_title = "Read peak intensities from a file."
    read_intensities._doc_title_short = "Peak intensity reading."
    read_intensities._doc_args = [
        ["file", "The name of the file containing the intensity data."],
        ["dir", "The directory where the file is located."],
        ["spectrum_id", "The spectrum ID string."],
        ["heteronuc", "The name of the heteronucleus as specified in the peak intensity file."],
        ["proton", "The name of the proton as specified in the peak intensity file."],
        ["int_col", "The column containing the peak intensity data (used by the generic intensity file format)."],
        ["int_method", "The integration method."],
        ["spin_id_col", "The spin ID string column used by the generic intensity file format (an alternative to the mol, res, and spin name and number columns)."],
        ["mol_name_col", "The molecule name column used by the generic intensity file format (alternative to the spin_id_col)."],
        ["res_num_col", "The residue number column used by the generic intensity file format (alternative to the spin_id_col)."],
        ["res_name_col", "The residue name column used by the generic intensity file format (alternative to the spin_id_col)."],
        ["spin_num_col", "The spin number column used by the generic intensity file format (alternative to the spin_id_col)."],
        ["spin_name_col", "The spin name column used by the generic intensity file format (alternative to the spin_id_col)."],
        ["sep", "The column separator used by the generic intensity format (the default is white space)."],
        ["spin_id", "The spin ID string used by the generic intensity file format to restrict the loading of data to certain spin subsets."],
        ["ncproc", "The Bruker specific FID intensity scaling factor."]
    ]
    read_intensities._doc_desc = """
        The peak intensity can either be from peak heights or peak volumes.

        The spectrum ID is a label which is subsequently utilised by other user functions.  If this identifier matches that of a previously loaded set of intensities, then this indicates a replicated spectrum.

        The heteronucleus and proton should be set respectively to the name of the heteronucleus and proton in the file.  Only those lines which match these labels will be used.

        The integration method is required for the subsequent error analysis.  When peak heights are measured, this should be set to 'height'.  Volume integration methods are a bit varied and hence two values are accepted.  If the volume integration involves pure point summation, with no deconvolution algorithms or other methods affecting peak heights, then the value should be set to 'point sum'.  All other volume integration methods, e.g. line shape fitting, the value should be set to 'other'.

        If a series of intensities extracted from Bruker FID files processed in Topspin or XWinNMR are to be compared, the ncproc parameter may need to be supplied.  This is because this FID is stored using integer representation and is scaled using ncproc to avoid numerical truncation artifacts.  If two spectra have significantly different maximal intensities, then ncproc will be different for both.  The intensity scaling is binary, i.e. 2**ncproc. Therefore if spectrum A has an ncproc of 6 and and spectrum B a value of 7, then a reference intensity in B will be double that of A.  Internally, relax stores the intensities scaled by 2**ncproc.
        """
    read_intensities._doc_additional = [
        ["File formats", """
        The peak list or intensity file will be automatically determined.

        Sparky peak list:  The file should be a Sparky peak list saved after typing the command 'lt'.  The default is to assume that columns 0, 1, 2, and 3 (1st, 2nd, 3rd, and 4th) contain the Sparky assignment, w1, w2, and peak intensity data respectively.  The frequency data w1 and w2 are ignored while the peak intensity data can either be the peak height or volume displayed by changing the window options.  If the peak intensity data is not within column 3, set the integration column to the appropriate number (column numbering starts from 0 rather than 1).

        XEasy peak list:  The file should be the saved XEasy text window output of the list peak entries command, 'tw' followed by 'le'.  As the columns are fixed, the peak intensity column is hardwired to number 10 (the 11th column) which contains either the peak height or peak volume data.  Because the columns are fixed, the integration column number will be ignored.

        NMRView:  The file should be a NMRView peak list. The default is to use column 16 (which contains peak heights) for peak intensities. To use use peak volumes (or evolumes), int_col must be set to 15.

        Generic intensity file:  This is a generic format which can be created by scripting to support non-supported peak lists.  It should contain in the first few columns enough information to identify the spin.  This can include columns for the molecule name, residue number, residue name, spin number, and spin name.  Alternatively a spin ID string column can be used. The peak intensities can be placed in another column specified by the integration column number.  Intensities from multiple spectra can be placed into different columns, and these can then be specified simultaneously by setting the integration column value to a list of columns.  This list must be matched by setting the spectrum ID to a list of the same length.  If columns are delimited by a character other than whitespace, this can be specified with the column separator.  The spin ID can be used to restrict the loading to specific spin subsets.
        """]
    ]
    read_intensities._doc_examples = """
        To read the reference and saturated spectra peak heights from the Sparky formatted files
        'ref.list' and 'sat.list', type:

        relax> spectrum.read_intensities(file='ref.list', spectrum_id='ref')
        relax> spectrum.read_intensities(file='sat.list', spectrum_id='sat')

        To read the reference and saturated spectra peak heights from the XEasy formatted files
        'ref.text' and 'sat.text', type:

        relax> spectrum.read_intensities(file='ref.text', spectrum_id='ref')
        relax> spectrum.read_intensities(file='sat.text', spectrum_id='sat')
        """
    _build_doc(read_intensities)


    def replicated(self, spectrum_ids=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "spectrum.replicated("
            text = text + "spectrum_ids=" + repr(spectrum_ids) + ")"
            print(text)

        # Spectrum ids.
        arg_check.is_str_or_str_list(spectrum_ids, 'spectrum ID strings')

        # Execute the functional code.
        spectrum.replicated(spectrum_ids=spectrum_ids)

    # The function doc info.
    replicated._doc_title = "Specify which spectra are replicates of each other."
    replicated._doc_title_short = "Replicate spectra."
    replicated._doc_args = [
        ["spectrum_ids", "The list of replicated spectra ID strings."]
    ]
    replicated._doc_desc = """
        This is used to identify which of the loaded spectra are replicates of each other.  Specifying the replicates is essential for error analysis if the baseplane RMSD has not been supplied.
        """
    replicated._doc_examples = """
        To specify that the NOE spectra labelled 'ref1', 'ref2', and 'ref3' are the same spectrum
        replicated, type one of:

        relax> spectrum.replicated(['ref1', 'ref2', 'ref3'])
        relax> spectrum.replicated(spectrum_ids=['ref1', 'ref2', 'ref3'])

        To specify that the two R2 spectra 'ncyc2' and 'ncyc2b' are the same time point, type:

        relax> spectrum.replicated(['ncyc2', 'ncyc2b'])
        """
    _build_doc(replicated)
