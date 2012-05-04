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
"""Module containing the 'noe' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
from generic_fns import noesy
from specific_fns.setup import noe_obj
from status import Status; status = Status()


class Noe(User_fn_class):
    """Class for handling steady-state NOE and NOESY data."""

    def read_restraints(self, file=None, dir=None, proton1_col=None, proton2_col=None, lower_col=None, upper_col=None, sep=None):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "noe.read_restraints("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", proton1_col=" + repr(proton1_col)
            text = text + ", proton2_col=" + repr(proton2_col)
            text = text + ", lower_col=" + repr(lower_col)
            text = text + ", upper_col=" + repr(upper_col)
            text = text + ", sep=" + repr(sep) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_int(proton1_col, 'first proton column', can_be_none=True)
        arg_check.is_int(proton2_col, 'second proton column', can_be_none=True)
        arg_check.is_int(lower_col, 'lower bound column', can_be_none=True)
        arg_check.is_int(upper_col, 'upper bound column', can_be_none=True)
        arg_check.is_str(sep, 'column separator', can_be_none=True)

        # Execute the functional code.
        noesy.read_restraints(file=file, dir=dir, proton1_col=proton1_col, proton2_col=proton2_col, lower_col=lower_col, upper_col=upper_col, sep=sep)

    # The function doc info.
    read_restraints._doc_title = "Read NOESY or ROESY restraints from a file."
    read_restraints._doc_title_short = "Restraint reading."
    read_restraints._doc_args = [
        ["file", "The name of the file containing the restraint data."],
        ["dir", "The directory where the file is located."],
        ["proton1_col", "The column containing the first proton of the NOE or ROE cross peak."],
        ["proton2_col", "The column containing the second proton of the NOE or ROE cross peak."],
        ["lower_col", "The column containing the lower NOE bound."],
        ["upper_col", "The column containing the upper NOE bound."],
        ["sep", "The column separator (the default is white space)."]
    ]
    read_restraints._doc_desc = """
        The format of the file will be automatically determined, for example Xplor formatted restraint files.  A generically formatted file is also supported if it contains minimally four columns with the two proton names and the upper and lower bounds, as specified by the column numbers.  The proton names need to be in the spin ID string format.
        """
    read_restraints._doc_examples = """
        To read the Xplor formatted restraint file 'NOE.xpl', type one of:

        relax> noe.read_restraints('NOE.xpl')
        relax> noe.read_restraints(file='NOE.xpl')


        To read the generic formatted file 'noes', type one of:

        relax> noe.read_restraints(file='NOE.xpl', proton1_col=0, proton2_col=1, lower_col=2, upper_col=3)
        """
    _build_doc(read_restraints)


    def spectrum_type(self, spectrum_type=None, spectrum_id=None):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "noe.spectrum_type("
            text = text + "spectrum_type=" + repr(spectrum_type)
            text = text + ", spectrum_id=" + repr(spectrum_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(spectrum_type, 'spectrum type')
        arg_check.is_str(spectrum_id, 'spectrum ID string')

        # Execute the functional code.
        noe_obj._spectrum_type(spectrum_type=spectrum_type, spectrum_id=spectrum_id)

    # The function doc info.
    spectrum_type._doc_title = "Set the steady-state NOE spectrum type for pre-loaded peak intensities."
    spectrum_type._doc_title_short = "Steady-state NOE spectrum type."
    spectrum_type._doc_args = [
        ["spectrum_type", "The type of steady-state NOE spectrum, one of 'ref' for the reference spectrum or 'sat' for the saturated spectrum."],
        ["spectrum_id", "The spectrum ID string."]
    ]
    spectrum_type._doc_desc = """
        The spectrum type can be one of the following:

            The steady-state NOE reference spectrum.
            The steady-state NOE spectrum with proton saturation turned on.

        Peak intensities should be loaded before this user function via the spectrum.read_intensities user function.  The intensity values will then be associated with a spectrum ID string which can be used here.
        """
    _build_doc(spectrum_type)
