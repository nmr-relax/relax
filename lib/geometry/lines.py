###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
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
"""Functions relating to line geometry."""

# Python module imports.
from numpy import dot
from numpy.linalg import norm


def closest_point(line_pt1=None, line_pt2=None, point=None):
    """Determine the closest position on the line to the given point.

    This function defines the line using any two points on the line.


    @keyword line_pt1:  The first point defining the line.
    @type line_pt1:     numpy rank-1 array
    @keyword line_pt2:  The second point defining the line.
    @type line_pt2:     numpy rank-1 array
    @keyword point:     The point.
    @type point:        numpy rank-1 array
    @return:            The position on the line closest to the point.
    @rtype:             numpy rank-1 array
    """

    # The vector along the line.
    vect = line_pt2 - line_pt1

    # Forward.
    return closest_point_ax(line_pt=line_pt1, axis=vect, point=point)


def closest_point_ax(line_pt=None, axis=None, point=None):
    """Determine the closest position on the line to the given point.

    This function defines the line using any point on the line and the axis.


    @keyword line_pt1:  The point defining the line.
    @type line_pt1:     numpy rank-1 array
    @keyword axis:      The axis defining the line.
    @type axis:         numpy rank-1 array
    @keyword point:     The point.
    @type point:        numpy rank-1 array
    @return:            The position on the line closest to the point.
    @rtype:             numpy rank-1 array
    """

    # Check if the two points are the same, returning the point to avoid NaNs.
    if norm(line_pt - point) < 1e-6:
        return point

    # The hypotenuse.
    hypo = point - line_pt
    hypo_len = norm(hypo)
    unit_hypo = hypo / hypo_len

    # Normalise the axis.
    axis = axis / norm(axis)

    # The distance from the point defining the line to the closest point.
    d = hypo_len * dot(axis, unit_hypo)

    # The closest point.
    return line_pt + d*axis
