###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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

# Python module imports.
from numpy import float64, zeros
from warnings import warn

# relax module imports.
from lib.periodic_table import periodic_table
from lib.errors import RelaxError
from lib.warnings import RelaxWarning



def centre_of_mass(pos=None, elements=None, verbosity=1):
    """Calculate and return the centre of mass for the given atomic coordinates.

    @keyword pos:           The list of atomic coordinates.
    @type pos:              list of lists of float
    @keyword elements:      The list of elements corresponding to the atoms.
    @type elements:         list of str
    @keyword verbosity:     The amount of text to print out.  0 results in no printouts, 1 the full amount.
    @type verbosity:        int
    @return:                The centre of mass vector and the mass.
    @rtype:                 3D list of floats, float
    """

    # Print out.
    if verbosity:
        print("Calculating the centre of mass.")

    # Initialise the centre of mass.
    R = zeros(3, float64)

    # Initialise the total mass.
    M = 0.0

    # Loop over all atoms.
    for i in range(len(pos)):
        # Atomic mass.
        try:
            mass = periodic_table.atomic_mass(elements[i])
        except RelaxError:
            warn(RelaxWarning("Skipping the atom index %s as the element '%s' is unknown." % (i, elements[i])))

        # Total mass.
        M = M + mass

        # Sum of mass * position.
        R = R + mass * pos[i]

    # Normalise.
    R = R / M

    # Final printout.
    if verbosity:
        print("    Total mass:      M = " + repr(M))
        print("    Centre of mass:  R = " + repr(R))

    # Return the centre of mass and total mass
    return R, M
