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
from data_classes import SpecificData
from diff_tensor import DiffTensorData
from mol_res_spin import MoleculeList
from prototype import Prototype



class PipeContainer(Prototype):
    """Class containing all the program data."""

    # Molecular structure data.
    structure = SpecificData()

    # Diffusion data.
    diff = DiffTensorData()

    # The molecule-residue-spin object.
    mol = MoleculeList()

    # The data pipe type.
    pipe_type = None

    # Hybrid models.
    hybrid_runs = {}

    # Global minimisation statistics.
    chi2 = None
    iter = None
    f_count = None
    g_count = None
    h_count = None
    warning = None


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro text.
        text = "The data pipe storage object.\n"

        # Special objects/methods (to avoid the getattr() function call on).
        spec_obj = ['mol', 'diff', 'structure']

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            # Molecular list.
            if name == 'mol':
                text = text + "  mol: The molecule list (for the storage of the spin system specific data)\n"

            # Diffusion tensor.
            if name == 'diff':
                text = text + "  diff: The Brownian rotational diffusion tensor data object\n"

            # Molecular structure.
            if name == 'structure':
                text = text + "  structure: The 3D molecular data object\n"

            # Skip certain objects.
            if match("^_", name) or name in spec_obj:
                continue

            # Add the object's attribute to the text string.
            text = text + "  " + name + ": " + `getattr(self, name)` + "\n"

        # Return the text representation.
        return text
