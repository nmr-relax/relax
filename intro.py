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



class Intro_text:
    """The introductory text container."""

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

        # Program description.
        self.desc = "Protein dynamics by NMR data analysis"

        # Copyright printout.
        self.copyright = []
        self.copyright.append("Copyright (C) 2001-2006 Edward d'Auvergne")
        self.copyright.append("Copyright (C) 2006-2010 the relax development team")

        # Program licence and help.
        self.licence = "This is free software which you are welcome to modify and redistribute under the conditions of the GNU General Public License (GPL).  This program, including all modules, is licensed under the GPL and comes with absolutely no warranty.  For details type 'GPL'.  Assistance in using this program can be accessed by typing 'help'."

        # ImportErrors, if any.
        self.errors = []
        if not dep_check.C_module_exp_fn:
            self.errors.append(dep_check.C_module_exp_fn_mesg)
