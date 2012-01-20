###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""Module containing the 'sys_info' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import Basic_class, _build_doc
from generic_fns.sys_info import sys_info


class Sys_info(Basic_class):
    """Class containing the sys_info function."""

    def sys_info(self):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "sys_info()"
            print(text)

        # Execute the functional code.
        sys_info()

    sys_info._doc_title = "Display all system information relating to this version of relax."
    sys_info._doc_title_short = "Display system information."
    sys_info._doc_desc = """
        This will display all of the relax, Python, python package and hardware information currently being used by relax.  This is useful for seeing if all packages are up to date and if the correct software versions are being used.  It is also very useful information for reporting relax bugs.
        """
    _build_doc(sys_info)

