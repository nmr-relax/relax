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

# Module docstring.
"""Module for calculating simple statistics."""

# Python module imports.
from math import sqrt


def std(values=None, skip=None, dof=1):
    """Calculate the standard deviation of the given values, skipping values if asked.

    @keyword values:    The list of values to calculate the standard deviation of.
    @type values:       list of float
    @keyword skip:      An optional list of booleans specifying if a value should be skipped.  The length of this list must match the values.  An element of True will cause the corresponding value to not be included in the calculation.
    @type skip:         list of bool or None.
    @keyword dof:       The degrees of freedom, whereby the standard deviation is multipled by 1/(N - dof).
    @type dof:          int
    @return:            The standard deviation.
    @rtype:             float
    """

    # The total number of points.
    n = 0
    for i in range(len(values)):
        # Skip deselected values.
        if skip != None and not skip[i]:
            continue

        # Increment n.
        n = n + 1

    # Calculate the sum of the values for all points.
    Xsum = 0.0
    for i in range(len(values)):
        # Skip deselected values.
        if skip != None and not skip[i]:
            continue

        # Sum.
        Xsum = Xsum + values[i]

    # Calculate the mean value for all points.
    if n == 0:
        Xav = 0.0
    else:
        Xav = Xsum / float(n)

    # Calculate the sum part of the standard deviation.
    sd = 0.0
    for i in range(len(values)):
        # Skip deselected values.
        if skip != None and not skip[i]:
            continue

        # Sum.
        sd = sd + (values[i] - Xav)**2

    # Calculate the standard deviation.
    if n <= 1:
        sd = 0.0
    else:
        sd = sqrt(sd / (float(n) - float(dof)))

    # Return the SD.
    return sd
