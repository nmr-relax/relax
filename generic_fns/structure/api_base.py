###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""The API for accessing, creating, and modifying structural information.

The API is set up as a series of methods attached to the structural object defined in this module.
"""

# relax module import.
from relax_errors import RelaxImplementError


class Str_object:
    """The structural object base class."""

    # The parser specific data object.
    structural_data = []


    def load_structures(self, file_path, model, verbosity=False):
        """Prototype method for loading structures from a file.

        This inherited prototype method is a stub which, if the functionality is desired, should be
        overwritten by the derived class.


        @param file_path:   The full path of the file.
        @type file_path:    str
        @param model:       The structural model to use.
        @type model:        int
        @keyword verbosity: A flag which if True will cause messages to be printed.
        @type verbosity:    bool
        """

        # Raise the error.
        raise RelaxImplementError


    def xh_vector(self, spin, structure=None, unit=True):
        """Prototype method for calculating/extracting the XH vector from the loaded structure.

        @param spin:        The spin system data container.
        @type spin:         SpinContainer instance
        @keyword structure: The structure number to get the XH vector from.  If set to None and
                            multiple structures exist, then the XH vector will be averaged across
                            all structures.
        @type structure:    int
        @keyword unit:      A flag which if set will cause the function to return the unit XH vector
                            rather than the full vector.
        @type unit:         bool
        @return:            The XH vector (or unit vector if the unit flag is set).
        @rtype:             list or None
        """

        # Raise the error.
        raise RelaxImplementError
