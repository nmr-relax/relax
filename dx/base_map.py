###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


from LinearAlgebra import inverse
from Numeric import Float64, array, matrixmultiply, zeros
from os import mkdir


class Base_Map:
    def __init__(self):
        """The space mapping base class."""


    def map_space(self, run, index, n, inc, lower, upper, swap, file, dir, point, point_file, remap, labels):
        """Generic function for mapping a space."""

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Equation type specific function setup.
        map_bounds = self.relax.specific_setup.setup('map_bounds', function_type)
        if map_bounds == None:
            raise RelaxFuncSetupError, ('map bounds', function_type)

        # Function arguments.
        self.run = run
        self.index = index
        self.n = n
        self.inc = inc
        self.swap = swap
        self.file = file
        self.dir = dir
        self.point_file = point_file
        if remap != None:
            self.remap = remap
        self.labels = labels

        # Axis swapping.
        if self.swap == None:
            self.swap = range(self.n)

        # Points.
        if point != None:
            self.point = array(point, Float64)
            self.num_points = 1
        else:
            self.num_points = 0

        # The OpenDX directory.
        if self.dir:
            try:
                mkdir(self.dir)
            except OSError:
                pass

        # Create the scaling matrix.
        self.scaling_matrix = self.assemble_scaling_matrix(self.run, self.relax.data.res[self.res_index], self.res_index)
        import sys; sys.exit()

        # Get the map bounds.
        self.bounds = self.map_bounds(self.run, self.index)
        if lower != None:
            self.bounds[:, 0] = array(lower, Float64)
        if upper != None:
            self.bounds[:, 1] = array(upper, Float64)

        # Diagonal scaling.
        #if self.relax.data.res[index].scaling.has_key(self.run):
        #    for i in xrange(len(self.bounds[0])):
        #        self.bounds[:, i] = matrixmultiply(inverse(self.scaling_matrix), self.bounds[:, i])
        #    if point != None:
        #        self.point = matrixmultiply(inverse(self.scaling_matrix), self.point)

        # Setup the step sizes.
        self.step_size = zeros(self.n, Float64)
        for i in xrange(self.n):
            self.step_size[i] = (self.bounds[i, 1] - self.bounds[i, 0]) / self.inc

        # Map the space.
        self.program()
        self.general()
        if self.num_points == 1:
            self.create_point()
        self.create_map()


    def remap(self, values):
        """Base class remapping function which returns the values unmodified."""

        return values
