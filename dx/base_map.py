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


from Numeric import Float64, array, zeros


class Base_Map:
    def __init__(self):
        """The space mapping base class."""


    def map_space(self, run, index, n, inc, lower, upper, swap, file, dir, point, point_file, remap, labels):
        """Generic function for mapping a space."""

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific map bounds, map labels, and calculation functions.
        self.map_bounds = self.relax.specific_setup.setup('map_bounds', function_type)
        self.map_labels = self.relax.specific_setup.setup('map_labels', function_type, raise_error=0)
        self.calculate = self.relax.specific_setup.setup('calculate', function_type)

        # Function arguments.
        self.run = run
        self.index = index
        self.n = n
        self.inc = inc
        self.swap = swap
        self.file = file
        self.dir = dir
        self.point_file = point_file
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
        self.relax.IO.mkdir(self.dir, print_flag=0)

        # Get the map bounds.
        self.bounds = self.map_bounds(self.run, self.index)
        if lower != None:
            self.bounds[:, 0] = array(lower, Float64)
        if upper != None:
            self.bounds[:, 1] = array(upper, Float64)

        # Setup the step sizes.
        self.step_size = zeros(self.n, Float64)
        for i in xrange(self.n):
            self.step_size[i] = (self.bounds[i, 1] - self.bounds[i, 0]) / self.inc

        # Create the OpenDX .net program file.
        self.program()

        # Create the OpenDX .general file.
        self.general()

        # Create the OpenDX .general and data files for the given point.
        if self.num_points == 1:
            self.create_point()

        # Generate the map.
        self.create_map()
