###############################################################################
#                                                                             #
# Copyright (C) 2003-2010 Edward d'Auvergne                                   #
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
"""Module containing the introductory text container."""

# relax module imports.
import dep_check
from version import version



class Info_box:
    """A container storing information about relax."""

    def __init__(self):
        """Create the program introduction text stings.

        This class generates a container with the following objects:
            - title:  The program title 'relax'
            - version:  For example 'repository checkout' or '1.3.8'.
            - desc:  The short program description.
            - copyright:  A list of copyright statements.
            - licence:  Text pertaining to the licencing.
            - errors:  A list of import errors.
        """

        # Program name and version.
        self.title = "relax"
        self.version = version

        # The relax website.
        self.website = "http://nmr-relax.com"

        # Program description.
        self.desc = "Molecular dynamics by NMR data analysis"

        # Long description
        self.desc_long = "The program relax is designed for the study of the dynamics of proteins or other macromolecules though the analysis of experimental NMR data. It is a community driven project created by NMR spectroscopists for NMR spectroscopists. It supports exponential curve fitting for the calculation of the R1 and R2 relaxation rates, calculation of the NOE, reduced spectral density mapping, and the Lipari and Szabo model-free analysis."

        # Copyright printout.
        self.copyright = []
        self.copyright.append("Copyright (C) 2001-2006 Edward d'Auvergne")
        self.copyright.append("Copyright (C) 2006-2010 the relax development team")

        # Program licence and help.
        self.licence = "This is free software which you are welcome to modify and redistribute under the conditions of the GNU General Public License (GPL).  This program, including all modules, is licensed under the GPL and comes with absolutely no warranty.  For details type 'GPL' within the relax prompt."

        # ImportErrors, if any.
        self.errors = []
        if not dep_check.C_module_exp_fn:
            self.errors.append(dep_check.C_module_exp_fn_mesg)


    def centre(self, string, width=100):
        """Format the string to be centred to a certain number of spaces.

        @param string:  The string to centre.
        @type string:   str
        @keyword width: The number of characters to centre to.
        @type width:    int
        @return:        The centred string with leading whitespace added.
        @rtype:         str
        """

        # Calculate the number of spaces needed.
        spaces = (width - len(string)) / 2

        # The new string.
        string = spaces * ' ' + string

        # Return the new string.
        return string
