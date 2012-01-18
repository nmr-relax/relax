###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module containing the base class for the OpenDX space mapping classes."""


# Python module imports.
from numpy import float64, array, zeros
from time import asctime, localtime

# relax module imports.
from generic_fns import diffusion_tensor
from generic_fns import pipes
from relax_errors import RelaxError, RelaxUnknownParamError
from relax_io import open_write_file
from specific_fns.setup import get_specific_fn




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
        for i in xrange(self.n):
            self.map_bounds.append(get_specific_fn('map_bounds', cdp.pipe_type))
            self.return_conversion_factor.append(get_specific_fn('return_conversion_factor', cdp.pipe_type))
            self.return_units.append(get_specific_fn('return_units', cdp.pipe_type))

        # Diffusion tensor parameter flag.
        self.diff_params = zeros(self.n)

        # Get the parameter names.
        self.get_param_names()

        # Specific function setup (for diffusion tensor parameters).
        for i in xrange(self.n):
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
        for i in xrange(self.n):
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

        # Create the OpenDX .net program file.
        self.create_program()

        # Create the OpenDX .cfg program configuration file.
        self.create_config()

        # Create the OpenDX .general file.
        self.create_general()

        # Create the OpenDX .general and data files for the given point.
        if self.num_points == 1:
            self.create_point()

        # Generate the map.
        self.create_map()


    def create_config(self):
        """Function for creating the OpenDX .cfg program configuration file."""

        # Print out.
        print("\nCreating the OpenDX .cfg program configuration file.")

        # Open the file.
        config_file = open_write_file(file_name=self.file_prefix+".cfg", dir=self.dir, force=True)

        # Get the text of the configuration file.
        text = self.config_text()

        # Write the text.
        config_file.write(text)

        # Close the file.
        config_file.close()


    def create_general(self):
        """Function for creating the OpenDX .general file."""

        # Print out.
        print("\nCreating the OpenDX .general file.")

        # Open the file.
        general_file = open_write_file(file_name=self.file_prefix+".general", dir=self.dir, force=True)

        # Get the text of the configuration file.
        text = self.general_text()

        # Write the text.
        general_file.write(text)

        # Close the file.
        general_file.close()


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


    def create_point(self):
        """Function for creating a sphere at a given position within the 3D map.

        The formula used to calculate the coordinate position is::

                            V - L
            coord =   Inc * -----
                            U - L

        where:
            - V is the coordinate or parameter value.
            - L is the lower bound value.
            - U is the upper bound value.
            - Inc is the number of increments.

        Both a data file and .general file will be created.
        """

        # Print out.
        print("\nCreating the OpenDX .general and data files for the given point.")

        # Open the files.
        point_file = open_write_file(file_name=self.point_file, dir=self.dir, force=True)
        point_file_general = open_write_file(file_name=self.point_file+".general", dir=self.dir, force=True)

        # Calculate the coordinate values.
        coords = self.inc * (self.point - self.bounds[:, 0]) / (self.bounds[:, 1] - self.bounds[:, 0])
        for i in xrange(self.n):
            point_file.write("%-15.5g" % coords[i])
        point_file.write("1\n")

        # Get the text of the point .general file.
        text = self.point_text()

        # Write the text.
        point_file_general.write(text)

        # Close the data and .general files.
        point_file.close()
        point_file_general.close()


    def create_program(self):
        """Function for creating the OpenDX .net program file."""

        # Print out.
        print("\nCreating the OpenDX .net program file.")

        # Open the file.
        program_file = open_write_file(file_name=self.file_prefix+".net", dir=self.dir, force=True)

        # Create the strings associated with the map axes.
        self.map_axes()

        # Corners.
        self.corners = "{[0"
        for i in xrange(self.n - 1):
            self.corners = self.corners + " 0"
        self.corners = self.corners + "] [" + repr(self.inc)
        for i in xrange(self.n - 1):
            self.corners = self.corners + " "  + repr(self.inc)
        self.corners = self.corners + "]}"

        # Sphere size.
        self.sphere_size = repr(0.025 * (self.inc + 1.0))

        # Get the text of the program.
        text = self.program_text()

        # Write the text.
        program_file.write(text)

        # Close the file.
        program_file.close()


    def get_date(self):
        """Function for creating a date string."""

        self.date = asctime(localtime())


    def get_param_names(self):
        """Function for retrieving the parameter names."""

        # Initialise.
        self.param_names = []

        # Loop over the parameters.
        for i in xrange(self.n):
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
        for i in xrange(self.n):
            # Parameter conversion factors.
            factor = self.return_conversion_factor[i](self.param_names[i], spin_id=self.spin_id)

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
            for j in xrange(self.axis_incs + 1):
                string = string + "\"" + "%.2f" % vals + "\" "
                vals = vals + val_inc
            self.tick_values.append("{" + string + "}")

            # Tick locations.
            string = ""
            val = 0.0
            for j in xrange(self.axis_incs + 1):
                string = string + " " + repr(val)
                val = val + loc_inc
            self.tick_locations.append("{" + string + " }")
