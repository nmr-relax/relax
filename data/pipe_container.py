###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
from re import match

# relax module imports.
from data_classes import Residue, SpecificData
from diff_tensor import DiffTensorData



class PipeContainer:
    """Class containing all the program data."""

    # PDB data.
    pdb = SpecificData()

    # Diffusion data.
    diff = DiffTensorData()

    # The residue specific data.
    res = Residue()

    # The name of the runs.
    run_names = []

    # The type of the runs.
    run_types = []

    # Hybrid models.
    hybrid_runs = {}

    # Global minimisation statistics.
    chi2 = {}
    iter = {}
    f_count = {}
    g_count = {}
    h_count = {}
    warning = {}


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro text.
        text = "The data pipe storage object.\n"

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            if match("^_", name):
                continue
            text = text + "  " + name + ": " + `getattr(self, name)` + "\n"

        # Return the text representation.
        return text
