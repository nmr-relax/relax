###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
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
from os import mkdir
from re import match


class Base_Map:
    def __init__(self):
        """The space mapping base class."""


    def map_space(self, model=None, res_num=None, inc=20, lower=None, upper=None, swap=None, file="map", dir="dx", point=None, point_file="point", remap=None, labels=None):
        """Generic function for mapping a space."""

        # Equation type specific function setup.
        fns = self.relax.specific_setup.setup("map_space", self.relax.data.equations[model][res_num])
        if fns == None:
            return
        self.map_bounds, self.minimise = fns

        # Function arguments.
        self.model = model
        self.res_num = res_num
        self.inc = inc
        self.swap = swap
        self.file = file
        self.dir = dir
        if remap != None:
            self.remap = remap
        self.labels = labels

        # Number of parameters.
        self.n = len(self.relax.data.param_types[self.model][self.res_num])

        # Axis swapping.
        if swap == None:
            self.swap = range(self.n)
        else:
            self.swap = swap

        # Points.
        if point != None:
            self.point = point
            self.point_file = point_file
            self.num_points = 1
        else:
            self.num_points = 0

        # The OpenDX directory.
        if self.dir:
            try:
                mkdir(self.dir)
            except OSError:
                pass

        # Get the map bounds.
        self.bounds = self.map_bounds(self.model, self.relax.data.param_types[self.model][self.res_num])
        if lower != None:
            self.bounds[:, 0] = array(lower, Float64)
        if upper != None:
            self.bounds[:, 1] = array(upper, Float64)

        # Diagonal scaling.
        if self.relax.data.scaling.has_key(self.model):
            for i in range(len(self.bounds[0])):
                self.bounds[:, i] = self.bounds[:, i] / self.relax.data.scaling[self.model][self.res_num]
            if point != None:
                self.point = self.point / self.relax.data.scaling[self.model][self.res_num]

        # Setup the step sizes.
        self.step_size = zeros(self.n, Float64)
        for i in range(self.n):
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
