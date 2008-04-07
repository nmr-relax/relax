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

The full API is documented within this base class object.  Each available API call is given as a
prototype method stub with all arguments, raised errors, and return values documented.
"""

# relax module import.
from relax_errors import RelaxImplementError


class Str_object:
    """The structural object base class."""

    # The parser specific data object.
    structural_data = []


    def atom_add(self, atom_id=None, record_name='', atom_name='', res_name='', chain_id='', res_num=None, pos=[None, None, None], segment_id='', element=''):
        """Prototype method stub for adding an atom to the structural data object.

        This method will create the key-value pair for the given atom.


        @param atom_id:     The atom identifier.  This is used as the key within the dictionary.
        @type atom_id:      str
        @param record_name: The record name, e.g. 'ATOM', 'HETATM', or 'TER'.
        @type record_name:  str
        @param atom_name:   The atom name, e.g. 'H1'.
        @type atom_name:    str
        @param res_name:    The residue name.
        @type res_name:     str
        @param chain_id:    The chain identifier.
        @type chain_id:     str
        @param res_num:     The residue number.
        @type res_num:      int
        @param pos:         The position vector of coordinates.
        @type pos:          list (length = 3)
        @param segment_id:  The segment identifier.
        @type segment_id:   str
        @param element:     The element symbol.
        @type element:      str
        """

        # Raise the error.
        raise RelaxImplementError


    def atom_connect(self, atom_id=None, bonded_id=None):
        """Prototype method stub for connecting two atoms within the data structure object.

        This method will connect the atoms corresponding to atom_id and bonded_id.


        @param atom_id:     The atom identifier.
        @type atom_id:      str
        @param bonded_id:   The second atom identifier.
        @type bonded_id:    str
        """

        # Raise the error.
        raise RelaxImplementError


    def load_structures(self, file_path, model, verbosity=False):
        """Prototype method stub for loading structures from a file.

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


    def terminate(self, atom_id_ext='', res_num=None):
        """Prototype method stub for terminating the structural chain.

        @param atom_id_ext:     The atom identifier extension.
        @type atom_id_ext:      str
        @param res_num:         The residue number.
        @type res_num:          int
        """

        # Raise the error.
        raise RelaxImplementError


    def xh_vector(self, spin, structure=None, unit=True):
        """Prototype method stub for calculating/extracting the XH vector from the loaded structure.

        @param spin:        The spin system data container.
        @type spin:         SpinContainer instance
        @keyword structure: The structure number to get the XH vector from.  If set to None and
                            multiple structures exist, then the XH vector will be averaged across
                            all structures.
        @type structure:    int
        @keyword unit:      A flag which if set will cause the method to return the unit XH vector
                            rather than the full vector.
        @type unit:         bool
        @return:            The XH vector (or unit vector if the unit flag is set).
        @rtype:             list or None
        """

        # Raise the error.
        raise RelaxImplementError
