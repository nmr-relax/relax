###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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
"""Module for interfacing with Grace (also known as Xmgrace, Xmgr, and ace)."""

# Python module imports.
from numpy import array
from os import system
from re import match

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
import generic_fns
from generic_fns.mol_res_spin import exists_mol_res_spin_data, spin_loop
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoSimError, RelaxRegExpError
from relax_io import get_file_path, open_write_file, test_binary
from specific_fns.setup import get_specific_fn


def determine_graph_type(data, x_data_type=None, plot_data=None):
    """Determine if the graph is of type xy, xydy, xydx, or xydxdy.

    @param data:            The graph numerical data.
    @type data:             list of lists of float
    @keyword x_data_type:   The category of the X-axis data.
    @type x_data_type:      str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @return:                The graph type, which can be one of xy, xydy, xydx, or xydxdy.
    @rtype:                 str
    """

    # Initial flags.
    x_errors = 0
    y_errors = 0

    # Loop over the data.
    for i in xrange(len(data)):
        # X-axis errors.
        if x_data_type != 'res' and data[i][3] != None:
            x_errors = 1

        # Y-axis errors.
        if data[i][5] != None:
            y_errors = 1

    # Plot of values.
    if plot_data == 'value':
        # xy plot with errors along both axes.
        if x_errors and y_errors:
            graph_type = 'xydxdy'

        # xy plot with errors along the Y-axis.
        elif y_errors:
            graph_type = 'xydy'

        # xy plot with errors along the X-axis.
        elif x_errors:
            graph_type = 'xydx'

        # xy plot with no errors.
        else:
            graph_type = 'xy'

    # Plot of errors.
    elif plot_data == 'error':
        # xy plot of residue number vs error.
        if x_data_type == 'res' and y_errors:
            graph_type = 'xy'

        # xy plot of error vs error.
        elif x_errors and y_errors:
            graph_type = 'xy'

        # Invalid argument combination.
        else:
            raise RelaxError, "When plotting errors, the errors must exist."

    # Plot of simulation values.
    else:
        # xy plot with no errors.
        graph_type = 'xy'

    # Return the graph type.
    return graph_type


def get_data(spin_id=None, plot_data=None):
    """Get all the xy data.

    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @keyword x_data_type:   The category of the X-axis data.
    @type x_data_type:      str
    @keyword y_data_type:   The category of the Y-axis data.
    @type y_data_type:      str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @return:                The graph numerical data.
    @rtype:                 list of lists of float
    """

    # Initialise the data structure.
    data = []

    # Specific x and y value returning functions.
    x_return_value = y_return_value = get_specific_fn('return_value', ds[ds.current_pipe].pipe_type)
    x_return_conversion_factor = y_return_conversion_factor = get_specific_fn('return_conversion_factor', ds[ds.current_pipe].pipe_type)

    # Test if the X-axis data type is a minimisation statistic.
    if x_data_type != 'res' and generic_fns.minimise.return_data_name(x_data_type):
        x_return_value = generic_fns.minimise.return_value
        x_return_conversion_factor = generic_fns.minimise.return_conversion_factor

    # Test if the Y-axis data type is a minimisation statistic.
    if y_data_type != 'res' and generic_fns.minimise.return_data_name(y_data_type):
        y_return_value = generic_fns.minimise.return_value
        y_return_conversion_factor = generic_fns.minimise.return_conversion_factor

    # Loop over the residues.
    for spin in spin_loop(spin_id):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Number of data points per spin.
        if plot_data == 'sim':
            points = ds[ds.current_pipe].sim_number
        else:
            points = 1

        # Loop over the data points.
        for j in xrange(points):
            # Initialise an empty array for the individual residue data.
            spin_data = [spin.num, spin.name, None, None, None, None]

            # Residue number on the x-axis.
            if x_data_type == 'res':
                spin_data[2] = spin.num

            # Parameter value for the x-axis.
            else:
                # Get the x-axis values and errors.
                if plot_data == 'sim':
                    spin_data[2], spin_data[3] = x_return_value(i, x_data_type, sim=j)
                else:
                    spin_data[2], spin_data[3] = x_return_value(i, x_data_type)

            # Get the y-axis values and errors.
            if plot_data == 'sim':
                spin_data[4], spin_data[5] = y_return_value(i, y_data_type, sim=j)
            else:
                spin_data[4], spin_data[5] = y_return_value(i, y_data_type)

            # Go to the next residue if there is missing data.
            if spin_data[2] == None or spin_data[4] == None:
                continue

            # X-axis conversion factors.
            if x_data_type != 'res':
                spin_data[2] = array(spin_data[2]) / x_return_conversion_factor(x_data_type)
                if spin_data[3]:
                    spin_data[3] = array(spin_data[3]) / x_return_conversion_factor(x_data_type)

            # Y-axis conversion factors.
            spin_data[4] = array(spin_data[4]) / y_return_conversion_factor(y_data_type)
            if spin_data[5]:
                spin_data[5] = array(spin_data[5]) / y_return_conversion_factor(y_data_type)

            # Append the array to the full data structure.
            data.append(spin_data)

    # Return the data.
    return data


def view(file=None, dir=None, grace_exe='xmgrace'):
    """Execute Grace.

    @keyword file:      The name of the file to open in Grace.
    @type file:         str
    @keyword dir:       The optional directory containing the file.
    @type dir:          str
    @keyword grace_exe: The name of the Grace executable file.  This should be located within the
                        system path.
    @type grace_exe:    str
    """

    # Test the binary file string corresponds to a valid executable.
    test_binary(grace_exe)

    # File path.
    file_path = get_file_path(file, dir)

    # Run Grace.
    system(grace_exe + " " + file_path + " &")


def write(x_data_type='res', y_data_type=None, spin_id=None, plot_data='value', norm=True, file=None, dir=None, force=False):
    """Writing data to a file.

    @keyword x_data_type:   The category of the X-axis data.
    @type x_data_type:      str
    @keyword y_data_type:   The category of the Y-axis data.
    @type y_data_type:      str
    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @keyword norm:          The normalisation flag which if set to True will cause all graphs to be
                            normalised to 1.
    @type norm:             bool
    @keyword file:          The name of the Grace file to create.
    @type file:             str
    @keyword dir:           The optional directory to place the file into.
    @type dir:              str
    @param force:           Boolean argument which if True causes the file to be overwritten if it
                            already exists.
    @type force:            bool
    """

    # Test if the current pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if the plot_data argument is one of 'value', 'error', or 'sim'.
    if plot_data not in ['value', 'error', 'sim']:
        raise RelaxError, "The plot data argument " + `plot_data` + " must be set to either 'value', 'error', 'sim'."

    # Test if the simulations exist.
    if plot_data == 'sim' and not hasattr(ds[ds.current_pipe], 'sim_number'):
        raise RelaxNoSimError

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Specific value and error, conversion factor, and units returning functions.
    x_return_units =             y_return_units =             get_specific_fn('return_units', ds[ds.current_pipe].pipe_type)
    x_return_grace_string =      y_return_grace_string =      get_specific_fn('return_grace_string', ds[ds.current_pipe].pipe_type)

    # Test if the X-axis data type is a minimisation statistic.
    if x_data_type != 'res' and generic_fns.minimise.return_data_name(x_data_type):
        x_return_units = generic_fns.minimise.return_units
        x_return_grace_string = generic_fns.minimise.return_grace_string

    # Test if the Y-axis data type is a minimisation statistic.
    if generic_fns.minimise.return_data_name(y_data_type):
        y_return_units = generic_fns.minimise.return_units
        y_return_grace_string = generic_fns.minimise.return_grace_string

    # Get the data.
    data = get_data(spin_id)

    # Determine the graph type (ie xy, xydy, xydx, or xydxdy).
    graph_type = determine_graph_type(data, x_data_type=x_data_type, plot_data=plot_data)

    # Test for multiple data sets.
    multi = True
    try:
        len(self.data[0][2])
    except TypeError:
        multi = False

    # Multiple data sets.
    if multi:
        # Write the header.
        write_multi_header(data, file=file, x_data_type=x_data_type, y_data_type=y_data_type, x_return_units=x_return_units, y_return_units=y_return_units, x_return_grace_string=x_return_grace_string, y_return_grace_string=y_return_grace_string, norm=norm)

        # Write the data.
        write_multi_data(data, file=file, graph_type=graph_type, norm=norm)

    # Single data set.
    else:
        # Write the header.
        write_header(file=file, x_data_type=x_data_type, y_data_type=y_data_type, x_return_units=x_return_units, y_return_units=y_return_units, x_return_grace_string=x_return_grace_string, y_return_grace_string=y_return_grace_string)

        # Write the data.
        write_data(data, file=file, graph_type=graph_type)

    # Close the file.
    file.close()


def write_data(data, file=None, graph_type=None):
    """Write the data into the Grace file.

    @param data:            The graph numerical data.
    @type data:             list of lists of float
    @keyword file:          The file object to write the data to.
    @type file:             file object
    @keyword graph_type:    The graph type which can be one of xy, xydy, xydx, or xydxdy.
    @type graph_type:       str
    """

    # First graph and data set (graph 0, set 0).
    file.write("@target G0.S0\n")
    file.write("@type " + graph_type + "\n")

    # Loop over the data.
    for i in xrange(len(data)):
        # Graph type xy.
        if graph_type == 'xy':
            # Write the data.
            file.write("%-30s%-30s\n" % (data[i][2], data[i][4]))

        # Graph type xydy.
        elif graph_type == 'xydy':
            # Catch y-axis errors of None.
            y_error = data[i][5]
            if y_error == None:
                y_error = 0.0

            # Write the data.
            file.write("%-30s%-30s%-30s\n" % (data[i][2], data[i][4], y_error))

        # Graph type xydxdy.
        elif graph_type == 'xydxdy':
            # Catch x-axis errors of None.
            x_error = data[i][3]
            if x_error == None:
                x_error = 0.0

            # Catch y-axis errors of None.
            y_error = data[i][5]
            if y_error == None:
                y_error = 0.0

            # Write the data.
            file.write("%-30s%-30s%-30s%-30s\n" % (data[i][2], data[i][4], x_error, y_error))

    # End of graph and data set.
    file.write("&\n")


def write_header(file=None, x_data_type=None, y_data_type=None, x_return_units=None, y_return_units=None, x_return_grace_string=None, y_return_grace_string=None):
    """Write the grace header.

    @keyword file:                  The file object to write the data to.
    @type file:                     file object
    @keyword x_data_type:           The category of the X-axis data.
    @type x_data_type:              str
    @keyword y_data_type:           The category of the Y-axis data.
    @type y_data_type:              str
    @keyword x_return_units:        The analysis specific function for returning the Grace formatted
                                    units string for the X-axis.
    @type x_return_units:           function
    @keyword y_return_units:        The analysis specific function for returning the Grace formatted
                                    units string for the Y-axis.
    @type y_return_units:           function
    @keyword x_return_grace_string: The analysis specific function for returning the Grace X-axis
                                    string.
    @type x_return_grace_string:    function
    @keyword y_return_grace_string: The analysis specific function for returning the Grace Y-axis
                                    string.
    @type y_return_grace_string:    function
    """

    # Graph G0.
    file.write("@with g0\n")

    # X axis start and end.
    if x_data_type == 'res':
        file.write("@    world xmin " + `cdp.res[0].num - 1` + "\n")
        file.write("@    world xmax " + `cdp.res[-1].num + 1` + "\n")

    # X-axis label.
    if x_data_type == 'res':
        file.write("@    xaxis  label \"Residue number\"\n")
    else:
        # Get the units.
        units = x_return_units(x_data_type)

        # Label.
        if units:
            file.write("@    xaxis  label \"" + x_return_grace_string(x_data_type) + "\\N (" + units + ")\"\n")
        else:
            file.write("@    xaxis  label \"" + x_return_grace_string(x_data_type) + "\"\n")

    # X-axis specific settings.
    file.write("@    xaxis  label char size 1.48\n")
    file.write("@    xaxis  tick major size 0.75\n")
    file.write("@    xaxis  tick major linewidth 0.5\n")
    file.write("@    xaxis  tick minor linewidth 0.5\n")
    file.write("@    xaxis  tick minor size 0.45\n")
    file.write("@    xaxis  ticklabel char size 1.00\n")

    # Y-axis label.
    units = y_return_units(y_data_type)
    if units:
        file.write("@    yaxis  label \"" + y_return_grace_string(y_data_type) + "\\N (" + units + ")\"\n")
    else:
        file.write("@    yaxis  label \"" + y_return_grace_string(y_data_type) + "\"\n")

    # Y-axis specific settings.
    file.write("@    yaxis  label char size 1.48\n")
    file.write("@    yaxis  tick major size 0.75\n")
    file.write("@    yaxis  tick major linewidth 0.5\n")
    file.write("@    yaxis  tick minor linewidth 0.5\n")
    file.write("@    yaxis  tick minor size 0.45\n")
    file.write("@    yaxis  ticklabel char size 1.00\n")

    # Frame.
    file.write("@    frame linewidth 0.5\n")

    # Symbols.
    file.write("@    s0 symbol 1\n")
    file.write("@    s0 symbol size 0.45\n")
    file.write("@    s0 symbol fill pattern 1\n")
    file.write("@    s0 symbol linewidth 0.5\n")
    file.write("@    s0 line linestyle 0\n")

    # Error bars.
    file.write("@    s0 errorbar size 0.5\n")
    file.write("@    s0 errorbar linewidth 0.5\n")
    file.write("@    s0 errorbar riser linewidth 0.5\n")


def write_multi_data(data, file=None, graph_type=None, norm=False):
    """Write the data into the Grace file.

    @param data:            The graph numerical data.
    @type data:             list of lists of float
    @keyword file:          The file object to write the data to.
    @type file:             file object
    @keyword graph_type:    The graph type which can be one of xy, xydy, xydx, or xydxdy.
    @type graph_type:       str
    @keyword norm:          The normalisation flag which if set to True will cause all graphs to be
                            normalised to 1.
    @type norm:             bool
    """

    # Loop over the data.
    for i in xrange(len(data)):
        # Multi data set (graph 0, set i).
        file.write("@target G0.S" + `i` + "\n")
        file.write("@type " + graph_type + "\n")

        # Normalisation.
        norm_fact = 1.0
        if norm:
            norm_fact = data[i][4][0]

        # Loop over the data of the set.
        for j in xrange(len(data[i][2])):
            # Graph type xy.
            if graph_type == 'xy':
                # Write the data.
                file.write("%-30s%-30s\n" % (data[i][2][j], data[i][4][j]/norm_fact))

            # Graph type xydy.
            elif graph_type == 'xydy':
                # Catch y-axis errors of None.
                y_error = data[i][5][j]
                if y_error == None:
                    y_error = 0.0

                # Write the data.
                file.write("%-30s%-30s%-30s\n" % (data[i][2][j], data[i][4][j]/norm_fact, y_error/norm_fact))

            # Graph type xydxdy.
            elif graph_type == 'xydxdy':
                # Catch x-axis errors of None.
                x_error = data[i][3][j]
                if x_error == None:
                    x_error = 0.0

                # Catch y-axis errors of None.
                y_error = data[i][5][j]
                if y_error == None:
                    y_error = 0.0

                # Write the data.
                file.write("%-30s%-30s%-30s%-30s\n" % (data[i][2][j], data[i][4][j]/norm_fact, x_error, y_error/norm_fact))

        # End of the data set i.
        file.write("&\n")


def write_multi_header(data, file=None, x_data_type=None, y_data_type=None, x_return_units=None, y_return_units=None, x_return_grace_string=None, y_return_grace_string=None, norm=False):
    """Write the grace header.

    @param data:                    The graph numerical data.
    @type data:                     list of lists of float
    @keyword file:                  The file object to write the data to.
    @type file:                     file object
    @keyword x_data_type:           The category of the X-axis data.
    @type x_data_type:              str
    @keyword y_data_type:           The category of the Y-axis data.
    @type y_data_type:              str
    @keyword x_return_units:        The analysis specific function for returning the Grace formatted
                                    units string for the X-axis.
    @type x_return_units:           function
    @keyword y_return_units:        The analysis specific function for returning the Grace formatted
                                    units string for the Y-axis.
    @type y_return_units:           function
    @keyword x_return_grace_string: The analysis specific function for returning the Grace X-axis
                                    string.
    @type x_return_grace_string:    function
    @keyword y_return_grace_string: The analysis specific function for returning the Grace Y-axis
                                    string.
    @type y_return_grace_string:    function
    @keyword norm:                  The normalisation flag which if set to True will cause all
                                    graphs to be normalised to 1.
    @type norm:                     bool
    """

    # Graph G0.
    file.write("@with g0\n")

    # X axis start and end.
    if x_data_type == 'res':
        file.write("@    world xmin " + `cdp.res[0].num - 1` + "\n")
        file.write("@    world xmax " + `cdp.res[-1].num + 1` + "\n")

    # X-axis label.
    if x_data_type == 'res':
        file.write("@    xaxis  label \"Residue number\"\n")
    else:
        # Get the units.
        units = x_return_units(x_data_type)

        # Label.
        if units:
            file.write("@    xaxis  label \"" + x_return_grace_string(x_data_type) + "\\N (" + units + ")\"\n")
        else:
            file.write("@    xaxis  label \"" + x_return_grace_string(x_data_type) + "\"\n")

    # X-axis specific settings.
    file.write("@    xaxis  label char size 1.48\n")
    file.write("@    xaxis  tick major size 0.75\n")
    file.write("@    xaxis  tick major linewidth 0.5\n")
    file.write("@    xaxis  tick minor linewidth 0.5\n")
    file.write("@    xaxis  tick minor size 0.45\n")
    file.write("@    xaxis  ticklabel char size 1.00\n")

    # Y-axis label.
    units = y_return_units(y_data_type)
    string = "@    yaxis  label \"" + y_return_grace_string(y_data_type)
    if units:
        string = string + "\\N (" + units + ")"
    if norm:
        string = string + " \\q(normalised)\\Q"
    file.write(string + "\"\n")

    # Y-axis specific settings.
    file.write("@    yaxis  label char size 1.48\n")
    file.write("@    yaxis  tick major size 0.75\n")
    file.write("@    yaxis  tick major linewidth 0.5\n")
    file.write("@    yaxis  tick minor linewidth 0.5\n")
    file.write("@    yaxis  tick minor size 0.45\n")
    file.write("@    yaxis  ticklabel char size 1.00\n")

    # Legend box.
    file.write("@    legend off\n")

    # Frame.
    file.write("@    frame linewidth 0.5\n")

    # Loop over the data sets.
    for i in xrange(len(data)):
        # Error bars.
        file.write("@    s%i errorbar size 0.5\n" % i)
        file.write("@    s%i errorbar linewidth 0.5\n" % i)
        file.write("@    s%i errorbar riser linewidth 0.5\n" % i)

        # Legend.
        file.write("@    s%i legend \"Residue %s\"\n" % (i, data[i][1] + " " + `data[i][0]`))
