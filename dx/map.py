###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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


from isosurface_3D import Iso3D


class Map:
    def __init__(self, relax, run=None, res_num=None, inc=20, lower=None, upper=None, swap=None, file="map", dir="dx", point=None, point_file="point", remap=None, labels=None):
        """Class for the creation of OpenDX format space maps."""

        # Base class
        self.relax = relax

        # Residue index.
        index = None
        for i in xrange(len(self.relax.data.res)):
            if self.relax.data.res[i].num == res_num:
                index = i
                break
        if index == None:
            raise RelaxNoResError, res_num

        # The number of parameters.
        n = len(self.relax.data.res[index].params[run])

        # Lower bounds.
        if lower != None:
            if len(lower) != n:
                raise RelaxLenError, ('lower bounds', n)

        # Upper bounds.
        if upper != None:
            if len(upper) != n:
                raise RelaxLenError, ('upper bounds', n)

        # Axes swapping.
        if swap != None:
            if len(swap) != n:
                raise RelaxLenError, ('axes swapping', n)
            test = zeros(n)
            for i in xrange(n):
                if swap[i] >= n:
                    raise RelaxError, "The integer " + `swap[i]` + " is greater than the final array element."
                elif swap[i] < 0:
                    raise RelaxError, "All integers of the swap argument must be positive."
                test[swap[i]] = 1
            for i in xrange(n):
                if test[i] != 1:
                    raise RelaxError, "The swap argument is invalid (possibly duplicated integer values)."

        # Point.
        if point != None:
            if len(point) != n:
                raise RelaxLenError, ('point', n)

        # Axis labels.
        if labels != None:
            if len(labels) != n:
                raise RelaxLenError, ('axis labels', n)

        # Space type.
        if match("^[Ii]so3[Dd]", map_type):
            if n != 3:
                raise RelaxError, "The 3D isosurface map requires a 3 parameter model."
        else:
            raise RelaxError, "The map type '" + map_type + "' is not supported."

        self.Iso3D = Iso3D(relax)
