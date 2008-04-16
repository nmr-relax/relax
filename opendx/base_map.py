###############################################################################
#                                                                             #
# Copyright (C) 2003-2005, 2007 Edward d'Auvergne                             #
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

# Python module imports.
from numpy import float64, array, zeros
from time import asctime, localtime

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxUnknownParamError




class Base_Map:
    def __init__(self):
        """The space mapping base class."""


    def create_config(self):
        """Function for creating the OpenDX .cfg program configuration file."""

        # Print out.
        print "\nCreating the OpenDX .cfg program configuration file."

        # Open the file.
        config_file = self.relax.IO.open_write_file(file_name=self.file+".cfg", dir=self.dir, force=1)

        # Get the text of the configuration file.
        text = self.config_text()

        # Write the text.
        config_file.write(text)

        # Close the file.
        config_file.close()


    def create_general(self):
        """Function for creating the OpenDX .general file."""

        # Print out.
        print "\nCreating the OpenDX .general file."

        # Open the file.
        general_file = self.relax.IO.open_write_file(file_name=self.file+".general", dir=self.dir, force=1)

        # Get the text of the configuration file.
        text = self.general_text()

        # Write the text.
        general_file.write(text)

        # Close the file.
        general_file.close()


    def create_map(self):
        """Function for creating the map."""

        # Print out.
        print "\nCreating the map."

        # Open the file.
        map_file = self.relax.IO.open_write_file(file_name=self.file, dir=self.dir, force=1)

        # Generate and write the text of the map.
        self.map_text(map_file)

        # Close the file.
        map_file.close()


    def create_point(self):
        """Function for creating a sphere at a given position within the 3D map.

        The formula used to calculate the coordinate position is:

                            V - L
            coord =   Inc * -----
                            U - L

        where:
            V is the coordinate or parameter value.
            L is the lower bound value.
            U is the upper bound value.
            Inc is the number of increments.

        Both a data file and .general file will be created.
        """

        # Print out.
        print "\nCreating the OpenDX .general and data files for the given point."

        # Open the files.
        point_file = self.relax.IO.open_write_file(file_name=self.point_file, dir=self.dir, force=1)
        point_file_general = self.relax.IO.open_write_file(file_name=self.point_file+".general", dir=self.dir, force=1)

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
        print "\nCreating the OpenDX .net program file."

        # Open the file.
        program_file = self.relax.IO.open_write_file(file_name=self.file+".net", dir=self.dir, force=1)

        # Create the strings associated with the map axes.
        self.map_axes()

        # Corners.
        self.corners = "{[0"
        for i in xrange(self.n - 1):
            self.corners = self.corners + " 0"
        self.corners = self.corners + "] [" + `self.inc`
        for i in xrange(self.n - 1):
            self.corners = self.corners + " "  + `self.inc`
        self.corners = self.corners + "]}"

        # Sphere size.
        self.sphere_size = `0.025 * (self.inc + 1.0)`

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
            if self.function_type == 'mf':
                # The diffusion tensor parameter name.
                diff_name = self.relax.generic.diffusion_tensor.return_data_name(self.params[i])

                # Replace the model-free parameter with the diffusion tensor parameter if it exists.
                if diff_name:
                    name = diff_name

                    # Set the flag indicating if there are diffusion tensor parameters.
                    self.diff_params[i] = 1

            # Bad parameter name.
            if not name:
                raise RelaxUnknownParamError, self.params[i]

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
            for j in xrange(self.axis_incs + 1):
                string = string + "\"" + "%.2f" % vals + "\" "
                vals = vals + val_inc
            self.tick_values.append("{" + string + "}")

            # Tick locations.
            string = ""
            val = 0.0
            for j in xrange(self.axis_incs + 1):
                string = string + " " + `val`
                val = val + loc_inc
            self.tick_locations.append("{" + string + " }")


    def map_space(self, run, params, res_num, index, inc, lower, upper, axis_incs, file, dir, point, point_file, remap):
        """Generic function for mapping a space."""

        # Initialise.
        #############

        # Function type.
        self.function_type = relax_data_store.run_types[relax_data_store.run_names.index(run)]

        # Function arguments.
        self.run = run
        self.params = params
        self.res_num = res_num
        self.index = index
        self.n = len(params)
        self.inc = inc
        self.axis_incs = axis_incs
        self.file = file
        self.dir = dir
        self.point_file = point_file
        self.remap = remap

        # Specific function setup.
        self.calculate = self.relax.specific_setup.setup('calculate', self.function_type)
        self.model_stats = self.relax.specific_setup.setup('model_stats', self.function_type)
        self.return_data_name = self.relax.specific_setup.setup('return_data_name', self.function_type)
        self.map_bounds = []
        self.return_conversion_factor = []
        self.return_units = []
        for i in xrange(self.n):
            self.map_bounds.append(self.relax.specific_setup.setup('map_bounds', self.function_type))
            self.return_conversion_factor.append(self.relax.specific_setup.setup('return_conversion_factor', self.function_type))
            self.return_units.append(self.relax.specific_setup.setup('return_units', self.function_type))

        # Diffusion tensor parameter flag.
        self.diff_params = zeros(self.n)

        # Get the parameter names.
        self.get_param_names()

        # Specific function setup (for diffusion tensor parameters).
        for i in xrange(self.n):
            if self.diff_params[i]:
                self.map_bounds[i] = self.relax.generic.diffusion_tensor.map_bounds
                self.return_conversion_factor[i] = self.relax.generic.diffusion_tensor.return_conversion_factor
                self.return_units[i] = self.relax.generic.diffusion_tensor.return_units

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
            bounds = self.map_bounds[i](self.run, self.param_names[i])

            # No bounds found.
            if not bounds:
                raise RelaxError, "No bounds for the parameter " + `self.params[i]` + " could be determined."

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
