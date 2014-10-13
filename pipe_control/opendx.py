###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
from copy import deepcopy
from numpy import float64, array, zeros
from time import asctime, localtime

# relax module imports.
from lib.errors import RelaxError
from lib.io import open_write_file, write_data
from extern.numpy_future import percentile
from lib.software.opendx.files import write_config, write_general, write_point, write_program
from pipe_control import value
from specific_analyses.api import return_api

def map(params=None, map_type='Iso3D', spin_id=None, inc=20, lower=None, upper=None, axis_incs=10, file_prefix="map", dir="dx", point=None, point_file="point", chi_surface=None, create_par_file=False):
    """Map the space corresponding to the spin identifier and create the OpenDX files.

    @keyword params:        
    @type params:           
    @keyword map_type:          The type of map to create.  The available options are:
                                    - 'Iso3D', a 3D isosurface visualisation of the space.
    @type map_type:             str
    @keyword spin_id:           The spin identification string.
    @type spin_id:              str
    @keyword inc:               The resolution of the plot.  This is the number of increments per
                                dimension.
    @type inc:                  int
    @keyword lower:             The lower bounds of the space to map.  If supplied, this should be a
                                list of floats, its length equal to the number of parameters in the
                                model.
    @type lower:                None or list of float
    @keyword upper:             The upper bounds of the space to map.  If supplied, this should be a
                                list of floats, its length equal to the number of parameters in the
                                model.
    @type upper:                None or list of float
    @keyword axis_incs:         The number of tick marks to display in the OpenDX plot in each
                                dimension.
    @type axis_incs:            int
    @keyword file_prefix:       The file prefix for all the created files.
    @type file_prefix:          str
    @keyword dir:               The directory to place the files into.
    @type dir:                  str or None
    @keyword point:             If supplied, a red sphere will be placed at these coordinates.
    @type point:                None or list of float
    @keyword point_file:        The file prefix for the point output files.
    @type point_file:           str or None
    @keyword create_par_file:   Whether to create a file with parameters and associated chi2 value.
    @type point_file:           bool
    """

    # Check the args.
    if inc <= 1:
        raise RelaxError("The increment value needs to be greater than 1.")
    if axis_incs <= 1:
        raise RelaxError("The axis increment value needs to be greater than 1.")

    # Space type.
    if map_type.lower() == "iso3d":
        if len(params) != 3:
            raise RelaxError("The 3D isosurface map requires a 3 parameter model.")

        # Create the map.
        Map(params, spin_id, inc, lower, upper, axis_incs, file_prefix, dir, point, point_file, chi_surface, create_par_file)
    else:
        raise RelaxError("The map type '" + map_type + "' is not supported.")



class Map:
    """The space mapping base class."""

    def __init__(self, params, spin_id, inc, lower, upper, axis_incs, file_prefix, dir, point, point_file, chi_surface, create_par_file):
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

        # Define nested listed, which holds parameter values and chi2 value.
        self.par_chi2_vals = []

        # The specific analysis API object.
        self.api = return_api()

        # Points.
        if point != None:
            # Check if list is a nested list of lists.
            point_list = []
            if isinstance(point[0], float):
                point_list.append(array(point, float64))
                self.point = point_list
                self.num_points = 1
            else:
                for i in range(len(point)):
                    point_list.append(array(point[i], float64))
                self.point = point_list
                self.num_points = i + 1
        else:
            self.num_points = 0

        # Get the default map bounds.
        self.bounds = zeros((self.n, 2), float64)
        for i in range(self.n):
            # Get the bounds for the parameter i.
            bounds = self.api.map_bounds(self.params[i], self.spin_id)

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

        # Generate the map.
        self.create_map()

        ## Generate the file with parameters and associated chi2 value.
        if create_par_file:
            self.create_par_chi2(file_prefix=self.file_prefix, par_chi2_vals=self.par_chi2_vals)

            # Generate the matplotlib script file, to plot surfaces
            self.matplotlib_surface_plot()

        ## Generate the file with parameters and associated chi2 value for the points send to dx.
        if self.num_points >= 1 and create_par_file:
            # Calculate the parameter and associated chi2 values for the points.
            par_chi2_vals = self.calc_point_par_chi2()

            ## Generate the file with parameters and associated chi2 value.
            self.create_par_chi2(file_prefix=self.point_file, par_chi2_vals=par_chi2_vals)

        # Default the chi2 surface values, for Innermost, Inner, Middle and Outer Isosurface.
        if chi_surface == None:
            all_chi2 = array(self.all_chi, float64)
            innermost = percentile(all_chi2, 10)
            inner = percentile(all_chi2, 20)
            middle = percentile(all_chi2, 50)
            outer = percentile(all_chi2, 90)
            chi_surface = [innermost, inner, middle, outer]

        # Create the OpenDX .net program file.
        write_program(file_prefix=self.file_prefix, point_file=self.point_file, dir=self.dir, inc=self.inc, N=self.n, num_points=self.num_points, labels=self.labels, tick_locations=self.tick_locations, tick_values=self.tick_values, date=self.date, chi_surface = chi_surface)

        # Create the OpenDX .cfg program configuration file.
        write_config(file_prefix=self.file_prefix, dir=self.dir, date=self.date)

        # Create the OpenDX .general file.
        write_general(file_prefix=self.file_prefix, dir=self.dir, inc=self.inc)

        # Create the OpenDX .general and data files for the given point.
        if self.num_points >= 1:
            write_point(file_prefix=self.point_file, dir=self.dir, inc=self.inc, point=self.point, num_points=self.num_points, bounds=self.bounds, N=self.n)


    def calc_point_par_chi2(self):
        """Function for chi2 value for the points."""

        # Print out.
        print("\nCalculate chi2 value for the point parameters.")

        # Define nested listed, which holds parameter values and chi2 value.
        par_chi2_vals = []

        # Loop over the points.
        for i in range(self.num_points):
            i_point = self.point[i]

            # Set the parameter values.
            if self.spin_id:
                value.set(val=i_point, param=self.params, spin_id=self.spin_id, force=True)
            else:
                value.set(val=i_point, param=self.params, force=True)

            # Calculate the function values.
            if self.spin_id:
                self.api.calculate(spin_id=self.spin_id, verbosity=0)
            else:
                self.api.calculate(verbosity=0)

            # Get the minimisation statistics for the model.
            if self.spin_id:
                k, n, chi2 = self.api.model_statistics(spin_id=self.spin_id)
            else:
                k, n, chi2 = self.api.model_statistics(model_info=0)

            # Assign value to nested list.
            par_chi2_vals.append([i, i_point[0], i_point[1], i_point[2], chi2])

        # Return list
        return par_chi2_vals


    def create_map(self):
        """Function for creating the map."""

        # Print out.
        print("\nCreating the map.")

        # Open the file.
        map_file = open_write_file(file_name=self.file_prefix, dir=self.dir, force=True)

        # Generate and write the text of the map.
        self.map_3D_text(map_file)

        # Close the file.
        map_file.close()


    def create_par_chi2(self, file_prefix, par_chi2_vals):
        """Function for creating file with parameters and the chi2 value."""

        # Print out.
        print("\nCreating the file with parameters and the chi2 value.")

        # Open the file.
        par_file = open_write_file(file_name=file_prefix+'.par', dir=self.dir, force=True)

        # Copy the nested list to sort it.
        par_chi2_vals_sort = deepcopy(par_chi2_vals)

        # Then sort the value.
        par_chi2_vals_sort.sort(key=lambda values: values[4])

        # Collect the data structure, which is a list of list of strings.
        data = []
        for i, line in enumerate(par_chi2_vals):
            line_sort = par_chi2_vals_sort[i]

            # Convert values to strings.
            line_str = ["%3.5f"%j for j in line]
            line_sort_str = ["%3.5f"%j for j in line_sort]

            # Convert the index from float to index.
            line_str[0] = "%i" % line[0]
            line_sort_str[0] = "%i" % line_sort[0]

            # Merge the two lists and append to data.
            data_list = line_str + line_sort_str
            data.append(data_list)

        # Make the headings.
        headings = ['i'] + self.params + ['chi2']
        headings += headings

        # Add "_sort" to headings.
        headings[5] = headings[5] + "_sort"
        headings[6] = headings[6] + "_sort"
        headings[7] = headings[7] + "_sort"
        headings[8] = headings[8] + "_sort"
        headings[9] = headings[9] + "_sort"

        # Write the parameters and chi2 values to file.
        write_data(out=par_file, headings=headings, data=data)

        # Close the file.
        par_file.close()


    def get_date(self):
        """Function for creating a date string."""

        self.date = asctime(localtime())


    def map_3D_text(self, map_file):
        """Function for creating the text of a 3D map."""

        # Initialise.
        values = zeros(3, float64)
        percent = 0.0
        percent_inc = 100.0 / (self.inc + 1.0)**(self.n - 1.0)
        print("%-10s%8.3f%-1s" % ("Progress:", percent, "%"))

        # Collect all chi2, to help finding a reasobale chi level for the Innermost, Inner, Middle and Outer Isosurface.
        all_chi = []

        # Fix the diffusion tensor.
        unfix = False
        if hasattr(cdp, 'diff_tensor') and not cdp.diff_tensor.fixed:
            cdp.diff_tensor.fixed = True
            unfix = True

        # Initial value of the first parameter.
        values[0] = self.bounds[0, 0]

        # Define counter
        counter = 0

        # Loop over the first parameter.
        for i in range((self.inc + 1)):
            # Initial value of the second parameter.
            values[1] = self.bounds[1, 0]

            # Loop over the second parameter.
            for j in range((self.inc + 1)):
                # Initial value of the third parameter.
                values[2] = self.bounds[2, 0]

                # Loop over the third parameter.
                for k in range((self.inc + 1)):
                    # Set the parameter values.
                    if self.spin_id:
                        value.set(val=values, param=self.params, spin_id=self.spin_id, force=True)
                    else:
                        value.set(val=values, param=self.params, force=True)

                    # Calculate the function values.
                    if self.spin_id:
                        self.api.calculate(spin_id=self.spin_id, verbosity=0)
                    else:
                        self.api.calculate(verbosity=0)

                    # Get the minimisation statistics for the model.
                    if self.spin_id:
                        k, n, chi2 = self.api.model_statistics(spin_id=self.spin_id)
                    else:
                        k, n, chi2 = self.api.model_statistics(model_info=0)

                    # Set maximum value to 1e20 to stop the OpenDX server connection from breaking.
                    if chi2 > 1e20:
                        map_file.write("%30f\n" % 1e20)
                    else:
                        map_file.write("%30f\n" % chi2)

                        # Save all values of chi2. To help find reasonale level for the Innermost, Inner, Middle and Outer Isosurface.
                        all_chi.append(chi2)

                    # Assign value to nested list.
                    self.par_chi2_vals.append([counter, values[0], values[1], values[2], chi2])

                    # Add to counter.
                    counter += 1

                    # Increment the value of the third parameter.
                    values[2] = values[2] + self.step_size[2]

                # Progress incrementation and printout.
                percent = percent + percent_inc
                print("%-10s%8.3f%-8s%-8g" % ("Progress:", percent, "%,  " + repr(values) + ",  f(x): ", chi2))

                # Increment the value of the second parameter.
                values[1] = values[1] + self.step_size[1]

            # Increment the value of the first parameter.
            values[0] = values[0] + self.step_size[0]

        # Unfix the diffusion tensor.
        if unfix:
            cdp.diff_tensor.fixed = False

        # Save all chi2 values.
        self.all_chi = all_chi

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
            factor = self.api.return_conversion_factor(self.params[i])

            # Parameter units.
            units = self.api.return_units(self.params[i])

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


    def matplotlib_surface_plot(self):
        """Function to write matplotlib script to plot surfaces of parameters."""

        # Add ".par" to file prefix
        mapfile_name = '"%s.par"' % self.file_prefix

        # If point file_file is different from None
        if self.point_file != None:
            pointfile_name = '"%s.par"' % self.point_file
        else:
            pointfile_name = "None"

        # Open the file.
        plot_file = open_write_file(file_name=self.file_prefix+'.py', dir=self.dir, force=True)

        matplotlib_file = [
            'from copy import deepcopy'+"\n",
            'import numpy as np'+"\n",
            'import scipy.interpolate'+"\n",
            'from numpy.ma import masked_where'+"\n",
            ''+"\n",
            'from mpl_toolkits.mplot3d import axes3d'+"\n",
            'import matplotlib.pyplot as plt'+"\n",
            'from matplotlib import cm'+"\n",
            ''+"\n",
            '# Open file and get header.'+"\n",
            'mapfile_name = %s'%mapfile_name+"\n",
            'pointfile_name = %s'%pointfile_name+"\n",
            ''+"\n",
            'mapfile = open(mapfile_name, "r")'+"\n",
            'lines = mapfile.readlines()'+"\n",
            'mapfile.close()'+"\n",
            'header = lines[0].split()[1:]'+"\n",
            ''+"\n",
            '# Prepare the dtype for reading file.'+"\n",
            'dtype_str = "i8,f8,f8,f8,f8,i8,f8,f8,f8,f8"'+"\n",
            ''+"\n",
            'print("Fileheader is: %s"%header)'+"\n",
            'print("Value types are: %s"%dtype_str)'+"\n",
            ''+"\n",
            '# Load the data.'+"\n",
            'data = np.genfromtxt(fname=mapfile_name, dtype=dtype_str, names=header)'+"\n",
            ''+"\n",
            '# Load the point data'+"\n",
            'if pointfile_name:'+"\n",
            '    # Load the point data.'+"\n",
            '    data_p = np.genfromtxt(fname=pointfile_name, dtype=dtype_str, names=header)'+"\n",
            '    '+"\n",
            ''+"\n",
            '# Define where to cut the data, as the minimum.'+"\n",
            'header_min = header[6:10]'+"\n",
            ''+"\n",
            '# Define to cut at min map point.'+"\n",
            'map_min_par0 = data[header_min[0]][0]'+"\n",
            'map_min_par1 = data[header_min[1]][0]'+"\n",
            'map_min_par2 = data[header_min[2]][0]'+"\n",
            'map_min_chi2 = data[header_min[3]][0]'+"\n",
            ''+"\n",
            '# Now get the headers for the data.'+"\n",
            'header_val = header[1:5]'+"\n",
            ''+"\n",
            '# Define which 2D maps to create, as a list of 2 parameters, and at which third parameter to cut the values.'+"\n",
            'maps_xy = [header_val[0], header_val[1], header_val[2], map_min_par2]'+"\n",
            'maps_xz = [header_val[0], header_val[2], header_val[1], map_min_par1]'+"\n",
            'maps_yz = [header_val[1], header_val[2], header_val[0], map_min_par0]'+"\n",
            ''+"\n",
            'maps = [maps_xy, maps_xz, maps_yz]'+"\n",
            ''+"\n",
            '# Nr of columns is number of maps.'+"\n",
            'nr_cols = 1'+"\n",
            '# Nr of rows, is 2, for 3d projection and imshow'+"\n",
            'nr_rows = 2'+"\n",
            ''+"\n",
            '# Loop over the maps:'+"\n",
            'for x_par, y_par, z_par, z_cut in maps:'+"\n",
            '    # Define figure'+"\n",
            '    fig = plt.figure()'+"\n",
            ''+"\n",
            '    # Define c_par'+"\n",
            '    c_par = header_val[3]'+"\n",
            ''+"\n",
            '    # Now get the values for the map.'+"\n",
            '    map_x = data[x_par]'+"\n",
            '    map_y = data[y_par]'+"\n",
            '    map_z = data[z_par]'+"\n",
            '    map_c = data[c_par]'+"\n",
            ''+"\n",
            '    # Now define which map to create.'+"\n",
            '    mask_xy = masked_where(map_z == z_cut, map_z)'+"\n",
            '    map_mask_x = map_x[mask_xy.mask]'+"\n",
            '    map_mask_y = map_y[mask_xy.mask]'+"\n",
            '    map_mask_c = map_c[mask_xy.mask]'+"\n",
            ''+"\n",
            '    # Define min and max values.'+"\n",
            '    map_mask_x_min = map_mask_x.min()'+"\n",
            '    map_mask_x_max = map_mask_x.max()'+"\n",
            '    map_mask_y_min = map_mask_y.min()'+"\n",
            '    map_mask_y_max = map_mask_y.max()'+"\n",
            '    map_mask_c_min = map_mask_c.min()'+"\n",
            '    map_mask_c_max = map_mask_c.max()'+"\n",
            ''+"\n",
            '    # Set up a regular grid of interpolation points'+"\n",
            '    int_points = 300'+"\n",
            '    xi, yi = np.linspace(map_mask_x_min, map_mask_x_max, int_points), np.linspace(map_mask_y_min, map_mask_y_max, int_points)'+"\n",
            '    xi, yi = np.meshgrid(xi, yi)'+"\n",
            ''+"\n",
            '    # Interpolate to create grid'+"\n",
            '    ci = scipy.interpolate.griddata((map_mask_x, map_mask_y), map_mask_c, (xi, yi), method="linear")'+"\n",
            ''+"\n",
            '    # Set which x, y, z to plot'+"\n",
            '    x_p = xi'+"\n",
            '    y_p = yi'+"\n",
            '    c_p = deepcopy(ci)'+"\n",
            ''+"\n",
            '    # Cut map at a certain height.'+"\n",
            '    # First get index os largest values'+"\n",
            '    #z_max = map_mask_c_max'+"\n",
            '    z_max = map_mask_c_min + 0.5*map_mask_c_min'+"\n",
            '    ci_mask = masked_where(ci >= z_max, ci)'+"\n",
            ''+"\n",
            '    # Replace with 0.0'+"\n",
            '    c_p[ci_mask.mask] = 0.0'+"\n",
            '    # Find new max'+"\n",
            '    new_max = np.max(c_p)'+"\n",
            ''+"\n",
            '    # Insert values in array.'+"\n",
            '    c_p[ci_mask.mask] = new_max'+"\n",
            ''+"\n",
            '    # Define min.'+"\n",
            '    z_min = map_mask_c_min - 0.5*map_mask_c_min'+"\n",
            ''+"\n",
            '    # Create figure and plot'+"\n",
            '    ax = fig.add_subplot(nr_rows, nr_cols, 1, projection="3d")'+"\n",
            '    ax.plot_surface(x_p, y_p, c_p, rstride=8, cstride=8, alpha=0.3)'+"\n",
            ''+"\n",
            '    # Possible add scatter points for map.'+"\n",
            '    #ax.scatter(map_x, map_y, map_c, c="b", marker="o", s=5)'+"\n",
            ''+"\n",
            '    # One could also make the mesh just from the values, but this require much memory.'+"\n",
            '    ##ax.scatter(x_p, y_p, c_p, c="y", marker="o", s=5)'+"\n",
            ''+"\n",
            '    # Add contour levels on sides.'+"\n",
            '    ax.contour(x_p, y_p, c_p, zdir="z", offset=z_min, cmap=cm.coolwarm)'+"\n",
            '    ax.contour(x_p, y_p, c_p, zdir="x", offset=map_mask_x_min, cmap=cm.coolwarm)'+"\n",
            '    ax.contour(x_p, y_p, c_p, zdir="y", offset=map_mask_y_min, cmap=cm.coolwarm)'+"\n",
            ''+"\n",
            '    # Add scatter values, for 5 lowest values.'+"\n",
            '    x_par_min = x_par + "_sort"'+"\n",
            '    y_par_min = y_par + "_sort"'+"\n",
            '    c_par_min = c_par + "_sort"'+"\n",
            '    mp_x = data[x_par_min][0:5]'+"\n",
            '    mp_y = data[y_par_min][0:5]'+"\n",
            '    mp_c = data[c_par_min][0:5]'+"\n",
            '    ax.scatter(mp_x[0], mp_y[0], mp_c[0], c="r", marker="o", s=200)'+"\n",
            '    ax.scatter(mp_x[1:], mp_y[1:], mp_c[1:], c="g", marker="o", s=100)'+"\n",
            ''+"\n",
            '    # Add points from file, as the closest point in map.'+"\n",
            '    if pointfile_name:'+"\n",
            '        if data_p[x_par].ndim == 0:'+"\n",
            '            points_x = np.asarray([data_p[x_par]])'+"\n",
            '            points_y = np.asarray([data_p[y_par]])'+"\n",
            '        else:'+"\n",
            '            points_x = data_p[x_par]'+"\n",
            '            points_y = data_p[y_par]'+"\n",
            ''+"\n",
            '        # Normalize, by division of largest number of map'+"\n",
            '        points_x_norm = points_x / map_mask_x_max'+"\n",
            '        points_y_norm = points_y / map_mask_y_max'+"\n",
            '        map_mask_x_norm = map_mask_x / map_mask_x_max'+"\n",
            '        map_mask_y_norm = map_mask_y / map_mask_y_max'+"\n",
            ''+"\n",
            '        p_x = []'+"\n",
            '        p_y = []'+"\n",
            '        p_c = []'+"\n",
            '        # Now calculate the Euclidean distance in the space, to find map point best represents the point.'+"\n",
            '        for i, point_x_norm in enumerate(points_x_norm):'+"\n",
            '            point_y_norm = points_y_norm[i]'+"\n",
            ''+"\n",
            '            # Get the distance.'+"\n",
            '            dist = np.sqrt( (map_mask_x_norm - point_x_norm)**2 + (map_mask_y_norm - point_y_norm)**2)'+"\n",
            ''+"\n",
            '            # Return the indices of the minimum values along an axis.'+"\n",
            '            min_index = np.argmin(dist)'+"\n",
            '            p_x.append(map_mask_x[min_index])'+"\n",
            '            p_y.append(map_mask_y[min_index])'+"\n",
            '            p_c.append(map_mask_c[min_index])'+"\n",
            ''+"\n",
            '        # Convert to numpy array'+"\n",
            '        p_x = np.asarray(p_x)'+"\n",
            '        p_y = np.asarray(p_y)'+"\n",
            '        p_c = np.asarray(p_c)'+"\n",
            ''+"\n",
            '        # Plot points'+"\n",
            '        ax.scatter(p_x, p_y, p_c, c="m", marker="o", s=50)'+"\n",
            ''+"\n",
            ''+"\n",
            '    # Set label'+"\n",
            '    ax.set_xlabel("%s"%x_par)'+"\n",
            '    ax.set_ylabel("%s"%y_par)'+"\n",
            '    ax.set_zlabel("%s"%c_par)'+"\n",
            ''+"\n",
            ''+"\n",
            '    # Set limits'+"\n",
            '    ax.set_zlim(z_min, z_max)'+"\n",
            ''+"\n",
            ''+"\n",
            '    # Create figure and plot'+"\n",
            '    ax = fig.add_subplot(nr_rows, nr_cols, 2)'+"\n",
            '    fig_imshow = ax.imshow(ci, vmin=map_mask_c_min, vmax=map_mask_c_max, origin="lower", extent=[map_mask_x_min, map_mask_x_max, map_mask_y_min, map_mask_y_max])'+"\n",
            ''+"\n",
            '    # Add scatter values, for 5 lowest values.'+"\n",
            '    ax.scatter(mp_x[0], mp_y[0], c=mp_c[0], marker="o", s=200)'+"\n",
            '    ax.scatter(mp_x[1:], mp_y[1:], c="g", marker="o", s=100)'+"\n",
            ''+"\n",
            '    # Also add point to this map.'+"\n",
            '    if pointfile_name:'+"\n",
            '        # Plot points'+"\n",
            '        ax.scatter(p_x, p_y, c="m", marker="o", s=50)'+"\n",
            ''+"\n",
            '    # Set label'+"\n",
            '    ax.set_xlabel("%s"%x_par)'+"\n",
            '    ax.set_ylabel("%s"%y_par)'+"\n",
            ''+"\n",
            '    # Add colorbar.'+"\n",
            '    fig.subplots_adjust(right=0.8)'+"\n",
            '    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.3])'+"\n",
            '    fig.colorbar(fig_imshow, cax=cbar_ax)'+"\n",
            ''+"\n",
            '# Show plot.'+"\n",
            'plt.show()'+"\n",
            ''+"\n",
        ]

        # Loop over the lines and write.
        for line in matplotlib_file:
            plot_file.write(line)

        # Close the file.
        plot_file.close()
