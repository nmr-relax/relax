###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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


    def create_program(self):
        """Function for creating the OpenDX .net program file."""

        # Print out.
        print "Creating the OpenDX '.net' program file.\n"

        # Open the file.
        if self.dir:
            self.program_file = open(self.dir + "/" + self.file + ".net", "w")
        else:
            self.program_file = open(self.file + ".net", "w")

        self.program()


    def map_labels(self, param, bounds, inc):
        """Function for creating labels, tick locations, and tick values for an OpenDX map."""

        # Initialise.
        axis_incs = 5
        loc_inc = inc / axis_incs

        # Parameter conversion factors.
        factor = self.return_conversion_factor(param)

        # Parameter units.
        units = self.return_units(param)

        # Tick values.
        vals = bounds[0] / factor
        val_inc = (bounds[1] - bounds[0]) / (axis_incs * factor)

        # Tick locations.
        tick_locations = "{"
        val = 0.0
        for j in xrange(axis_incs + 1):
            tick_locations = tick_locations + " " + `val`
            val = val + loc_inc
        tick_locations = tick_locations + " }"

        # Tick values.
        tick_values = "{"
        for j in xrange(axis_incs + 1):
            tick_values = tick_values + "\"" + "%.2f" % vals + "\" "
            vals = vals + val_inc
        tick_values = tick_values + "}"

        return units, tick_locations, tick_values


    def map_space(self, run, params, index, inc, lower, upper, file, dir, point, point_file, remap):
        """Generic function for mapping a space."""

        # Initialise.
        #############

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific map bounds, map labels, and calculation functions.
        self.map_bounds = self.relax.specific_setup.setup('map_bounds', function_type)
        self.calculate = self.relax.specific_setup.setup('calculate', function_type)

        # Function arguments.
        self.run = run
        self.params = params
        self.index = index
        self.n = len(params)
        self.inc = inc
        self.file = file
        self.dir = dir
        self.point_file = point_file
        self.remap = remap

        # Points.
        if point != None:
            self.point = array(point, Float64)
            self.num_points = 1
        else:
            self.num_points = 0

        # The OpenDX directory.
        self.relax.IO.mkdir(self.dir, print_flag=0)

        # Get the default map bounds.
        self.bounds = zeros((self.n, 2), Float64)
        for i in xrange(self.n):
            self.bounds[i] = self.map_bounds(self.run, self.params[i])

        # Lower bounds.
        if lower != None:
            self.bounds[:, 0] = array(lower, Float64)

        # Upper bounds.
        if upper != None:
            self.bounds[:, 1] = array(upper, Float64)

        # Setup the step sizes.
        self.step_size = zeros(self.n, Float64)
        self.step_size = (self.bounds[:, 1] - self.bounds[:, 0]) / self.inc


        # Get the parameter names.
        self.get_param_names()


        # Create the OpenDX .net program file.
        self.create_program()

        # Create the OpenDX .cfg program configuration file.
        print "Creating the OpenDX '.cfg' program configuration file.\n"
        self.config()

        # Create the OpenDX .general file.
        print "Creating the OpenDX '.general' file.\n"
        self.general()

        # Create the OpenDX .general and data files for the given point.
        if self.num_points == 1:
            print "Creating the OpenDX '.general' and data files for the given point.\n"
            self.create_point()

        # Generate the map.
        print "Creating the map.\n"
        self.create_map()
