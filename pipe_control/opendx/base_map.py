###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""Module containing the base class for the OpenDX space mapping classes."""


# Python module imports.
from numpy import float64, array, zeros
from time import asctime, localtime

# relax module imports.
from pipe_control import diffusion_tensor
from pipe_control import pipes
from lib.errors import RelaxError, RelaxUnknownParamError
from lib.io import open_write_file
from lib.opendx.files import write_config, write_general, write_point, write_program
from specific_analyses.setup import get_specific_fn




class Base_Map:
    """The space mapping base class."""

    def __init__(self, params, spin_id, inc, lower, upper, axis_incs, file_prefix, dir, point, point_file, remap):
        """Map the space upon class instantiation."""

        # Initialise.
        #############

        # Function arguments.
        self.params = params
        self.spin_id = spin_id
        self.n = len(params)
        self.inc = inc
        self.axis_incs = axis_incs
        self.file_prefix = file_prefix
        self.dir = dir
        self.point_file = point_file
        self.remap = remap

        # Specific function setup.
        self.calculate = get_specific_fn('calculate', cdp.pipe_type)
        self.model_stats = get_specific_fn('model_stats', cdp.pipe_type)
        self.return_data_name = get_specific_fn('return_data_name', cdp.pipe_type)
        self.map_bounds = []
        self.return_conversion_factor = []
        self.return_units = []
        for i in range(self.n):
            self.map_bounds.append(get_specific_fn('map_bounds', cdp.pipe_type))
            self.return_conversion_factor.append(get_specific_fn('return_conversion_factor', cdp.pipe_type))
            self.return_units.append(get_specific_fn('return_units', cdp.pipe_type))

        # Diffusion tensor parameter flag.
        self.diff_params = zeros(self.n)

        # Get the parameter names.
        self.get_param_names()

        # Specific function setup (for diffusion tensor parameters).
        for i in range(self.n):
            if self.diff_params[i]:
                self.map_bounds[i] = diffusion_tensor.map_bounds
                self.return_conversion_factor[i] = diffusion_tensor.return_conversion_factor
                self.return_units[i] = diffusion_tensor.return_units

        # Points.
        if point != None:
            self.point = array(point, float64)
            self.num_points = 1
        else:
            self.num_points = 0

        # Get the default map bounds.
        self.bounds = zeros((self.n, 2), float64)
        for i in range(self.n):
            # Get the bounds for the parameter i.
            bounds = self.map_bounds[i](self.param_names[i], self.spin_id)

            # No bounds found.
            if not bounds:
                raise RelaxError("No bounds for the parameter " + repr(self.params[i]) + " could be determined.")

            # Assign the bounds to the global data structure.
            self.bounds[i] = bounds

        # Lower bounds.
        if lower != None:
            self.bounds[:, 0] = array(lower, float64)

        # Upper bounds.
        if upper != None:
            self.bounds[:, 1] = array(upper, float64)

        # Setup the step sizes.
        self.step_size = zeros(self.n, float64)
        self.step_size = (self.bounds[:, 1] - self.bounds[:, 0]) / self.inc


        # Create all the OpenDX data and files.
        #######################################

        # Get the date.
        self.get_date()

        # Create the strings associated with the map axes.
        self.map_axes()

        # Create the OpenDX .net program file.
        write_program(file_prefix=self.file_prefix, point_file=self.point_file, dir=self.dir, inc=self.inc, N=self.n, num_points=self.num_points, labels=self.labels, tick_locations=self.tick_locations, tick_values=self.tick_values, date=self.date)

        # Create the OpenDX .cfg program configuration file.
        write_config(file_prefix=self.file_prefix, dir=self.dir, date=self.date)

        # Create the OpenDX .general file.
        write_general(file_prefix=self.file_prefix, dir=self.dir, inc=self.inc)

        # Create the OpenDX .general and data files for the given point.
        if self.num_points == 1:
            write_point(file_prefix=self.point_file, dir=self.dir, inc=self.inc, point=self.point, bounds=self.bounds, N=self.n)

        # Generate the map.
        self.create_map()


    def create_map(self):
        """Function for creating the map."""

        # Print out.
        print("\nCreating the map.")

        # Open the file.
        map_file = open_write_file(file_name=self.file_prefix, dir=self.dir, force=True)

        # Generate and write the text of the map.
        self.map_text(map_file)

        # Close the file.
        map_file.close()


    def get_date(self):
        """Function for creating a date string."""

        self.date = asctime(localtime())


    def get_param_names(self):
        """Function for retrieving the parameter names."""

        # Initialise.
        self.param_names = []

        # Loop over the parameters.
        for i in range(self.n):
            # Get the parameter name.
            name = self.return_data_name(self.params[i])

            # Diffusion tensor parameter.
            if pipes.get_type() == 'mf':
                # The diffusion tensor parameter name.
                diff_name = diffusion_tensor.return_data_name(self.params[i])

                # Replace the model-free parameter with the diffusion tensor parameter if it exists.
                if diff_name:
                    name = diff_name

                    # Set the flag indicating if there are diffusion tensor parameters.
                    self.diff_params[i] = 1

            # Bad parameter name.
            if not name:
                raise RelaxUnknownParamError(self.params[i])

            # Append the parameter name.
            self.param_names.append(name)


    def map_axes(self):
        """Function for creating labels, tick locations, and tick values for an OpenDX map."""

        # Initialise.
        self.labels = "{"
        self.tick_locations = []
        self.tick_values = []
        loc_inc = float(self.inc) / float(self.axis_incs)

        # Loop over the parameters
        for i in range(self.n):
            # Parameter conversion factors.
            factor = self.return_conversion_factor[i](self.param_names[i])

            # Parameter units.
            units = self.return_units[i](self.param_names[i])

            # Labels.
            if units:
                self.labels = self.labels + "\"" + self.params[i] + " (" + units + ")\""
            else:
                self.labels = self.labels + "\"" + self.params[i] + "\""

            if i < self.n - 1:
                self.labels = self.labels + " "
            else:
                self.labels = self.labels + "}"

            # Tick values.
            vals = self.bounds[i, 0] / factor
            val_inc = (self.bounds[i, 1] - self.bounds[i, 0]) / (self.axis_incs * factor)

            string = ""
            for j in range(self.axis_incs + 1):
                string = string + "\"" + "%.2f" % vals + "\" "
                vals = vals + val_inc
            self.tick_values.append("{" + string + "}")

            # Tick locations.
            string = ""
            val = 0.0
            for j in range(self.axis_incs + 1):
                string = string + " " + repr(val)
                val = val + loc_inc
            self.tick_locations.append("{" + string + " }")
