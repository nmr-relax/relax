###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Package docstring.
"""Module containing objects used to handle peak list data.

These objects are only temporary.  In the future, they may be made permanent by shifting them into the relax data storage object.
"""

# relax module imports.
from lib.errors import RelaxError


class Assignment:
    """A special container for a single assignment in a peak list."""



class Peak_list(list):
    """The object used to represent a peak list."""

    def __init__(self, dim=2):
        """Set up the object.

        @keyword dim:   The dimensionality of the peak list.
        @type dim:      int
        """

        # Store the dimensionality.
        self._dim = dim


    def add(self, mol_names=None, res_nums=None, res_names=None, spin_nums=None, spin_names=None, shifts=None, intensity=None):
        """Add a peak list element.


        @keyword mol_names:     The list of molecule names for each dimension of the assignment.
        @type mol_names:        list of str or None
        @keyword res_nums:      The list of residue numbers for each dimension of the assignment.
        @type res_nums:         list of int or None
        @keyword res_names:     The list of residue names for each dimension of the assignment.
        @type res_names:        list of str or None
        @keyword spin_nums:     The list of spin numbers for each dimension of the assignment.
        @type spin_nums:        list of int or None
        @keyword spin_names:    The list of spin names for each dimension of the assignment.
        @type spin_names:       list of str or None
        @keyword shifts:        The chemical shifts for each dimension of the assignment in ppm.
        @type shifts:           list of float or None
        @keyword intensity:     The single intensity value for the peak.
        @type intensity:        float or None
        """

        # Check the arguments.
        if mol_names != None and len(mol_names) != self._dim:
            raise RelaxError("The molecule names %s must be a list of %s dimensions." % (mol_names, self._dim))
        if res_nums != None and len(res_nums) != self._dim:
            raise RelaxError("The residue numbers %s must be a list of %s dimensions." % (res_nums, self._dim))
        if res_names != None and len(res_names) != self._dim:
            raise RelaxError("The residue names %s must be a list of %s dimensions." % (res_names, self._dim))
        if spin_nums != None and len(spin_nums) != self._dim:
            raise RelaxError("The spin numbers %s must be a list of %s dimensions." % (spin_nums, self._dim))
        if spin_names != None and len(spin_names) != self._dim:
            raise RelaxError("The spin names %s must be a list of %s dimensions." % (spin_names, self._dim))
        if shifts != None and len(shifts) != self._dim:
            raise RelaxError("The chemical shifts %s must be a list of %s dimensions." % (shifts, self._dim))

        # Add a new element.
        self.append(Assignment)

        # Store the data.
        assign = self[-1]
        assign.mol_names = mol_names
        assign.res_nums = res_nums
        assign.res_names = res_names
        assign.spin_nums = spin_nums
        assign.spin_names = spin_names
        assign.shifts = shifts
        assign.intensity = intensity
