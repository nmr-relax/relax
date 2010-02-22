###############################################################################
#                                                                             #
# Copyright (C) 2003-2009 Edward d'Auvergne                                   #
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
from numpy import array, ndarray
from os import system
from warnings import warn

# relax module imports.
import generic_fns
from generic_fns.mol_res_spin import count_molecules, count_residues, count_spins, exists_mol_res_spin_data, generate_spin_id, spin_loop
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoSequenceError, RelaxNoSimError
from relax_io import get_file_path, open_write_file, test_binary
from relax_warnings import RelaxWarning
from specific_fns.setup import get_specific_fn


def determine_seq_type(spin_id=None):
    """Determine the spin sequence data type.

    The purpose is to identify systems whereby only spins or only residues exist.

    @keyword spin_id:   The spin identification string.
    @type spin_id:      str
    @return:            The spin sequence data type.  This can be one of 'spin', 'res,' or 'mixed'.
    @rtype:             str
    """

    # Count the molecules, residues, and spins.
    num_mol = count_molecules(spin_id)
    num_res = count_residues(spin_id)
    num_spin = count_spins(spin_id)

    # Only residues.
    if num_mol == 1 and num_spin == 1:
        return 'res'

    # Only spins.
    if num_mol == 1 and num_res == 1:
        return 'spin'

    # Mixed.
    return 'mixed'


def get_data(spin_id=None, x_data_type=None, y_data_type=None, plot_data=None):
    """Return all the xy data, along with the graph type and names for the graph sets.

    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @keyword x_data_type:   The category of the X-axis data.
    @type x_data_type:      str
    @keyword y_data_type:   The category of the Y-axis data.
    @type y_data_type:      str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @return:                The 4D graph numerical data structure, the graph type (i.e. on of 'xy', 'xydy', or 'xydxdy'), and the labels for the graph sets.
    @rtype:                 list of lists of lists of float, str, and list of str
    """

    # Initialise the 4D data structure (Gx, Sx, data point, data point info), and graph set labels.
    data = [[]]
    set_labels = []
    x_err_flag = False
    y_err_flag = False
    data_list = False

    # Specific x and y value returning functions.
    x_return_value = y_return_value = get_specific_fn('return_value', pipes.get_type())
    x_return_conversion_factor = y_return_conversion_factor = get_specific_fn('return_conversion_factor', pipes.get_type())

    # Test if the X-axis data type is a minimisation statistic.
    if x_data_type != 'spin' and generic_fns.minimise.return_data_name(x_data_type):
        x_return_value = generic_fns.minimise.return_value
        x_return_conversion_factor = generic_fns.minimise.return_conversion_factor

    # Test if the Y-axis data type is a minimisation statistic.
    if y_data_type != 'spin' and generic_fns.minimise.return_data_name(y_data_type):
        y_return_value = generic_fns.minimise.return_value
        y_return_conversion_factor = generic_fns.minimise.return_conversion_factor

    # Number of graph sets.
    if plot_data == 'sim':
        sets = cdp.sim_number
    else:
        sets = 1

    # Loop over the data points.
    for i in range(sets):
        # The graph label.
        set_label = ''
        if plot_data == 'sim':
            set_label = "Sim: %i" % i

        # The sim number.
        sim = None
        if plot_data == 'sim':
            sim = i

        # Spin names list (for creating new graph sets).
        spin_names = []

        # Loop over the spins.
        for spin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # The X data (plotted as residue numbers).
            if x_data_type == 'spin':
                x_val = res_num
                x_err = None

            # The X data (plotted as values).
            else:
                # Append the x-axis values and errors.
                x_val, x_err = x_return_value(spin, x_data_type, sim=sim)

            # The Y data (plotted as residue numbers).
            if y_data_type == 'spin':
                y_val = res_num
                y_err = None

            # The Y data (plotted as values).
            else:
                # Append the y-axis values and errors.
                y_val, y_err = y_return_value(spin, y_data_type, sim=sim)

            # Go to the next spin if there is missing xy data.
            if x_val == None or y_val == None:
                continue

            # One set per spin (list data has been returned).
            if data_list or type(x_val) == list:
                # Append a new set structure and set the name to the spin ID.
                data[0].append([])
                set_labels.append("Spin %s" % spin_id)

                # The set index.
                index = len(data[0]) - 1

                # No errors.
                if x_err == None:
                    x_err = [None]*len(x_val)
                if y_err == None:
                    y_err = [None]*len(y_val)

                # Data list flag.
                data_list = True

            # Convert the data to lists for packing into 1 point.
            else:
                x_val = [x_val]
                y_val = [y_val]
                x_err = [x_err]
                y_err = [y_err]

            # A new spin type (on data set per spin type).
            if not data_list and spin.name not in spin_names:
                # Append a new set structure.
                data[0].append([])

                # Append the label.
                set_labels.append("%s spins. " % spin.name + set_label)

                # Add the spin name to the list.
                spin_names.append(spin.name)

                # The set index.
                index = i * len(spin_names) + spin_names.index(spin.name)

            # Loop over the points.
            for j in range(len(x_val)):
                # Initialise and alias point structure.
                data[0][index].append([])
                point = data[0][index][-1]

                # Conversion factors.
                x_val[j] = x_val[j] / x_return_conversion_factor(x_data_type, spin)
                if x_err[j]:
                    x_err[j] = x_err[j] / x_return_conversion_factor(x_data_type, spin)
                y_val[j] = y_val[j] / y_return_conversion_factor(y_data_type, spin)
                if y_err[j]:
                    y_err[j] = y_err[j] / y_return_conversion_factor(y_data_type, spin)

                # Append the data.
                point.append(x_val[j])
                point.append(y_val[j])
                point.append(x_err[j])
                point.append(y_err[j])

                # Error flags.
                if x_err[j] and not x_err_flag:
                    x_err_flag = True
                if y_err[j] and not y_err_flag:
                    y_err_flag = True

    # The graph type.
    graph_type = 'xy'
    if x_err_flag:
        graph_type = graph_type + 'dx'
    if y_err_flag:
        graph_type = graph_type + 'dy'

    # Return the data.
    return data, set_labels, graph_type


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


def write(x_data_type='spin', y_data_type=None, spin_id=None, plot_data='value', file=None, dir=None, force=False, norm=True):
    """Writing data to a file.

    @keyword x_data_type:   The category of the X-axis data.
    @type x_data_type:      str
    @keyword y_data_type:   The category of the Y-axis data.
    @type y_data_type:      str
    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @keyword file:          The name of the Grace file to create.
    @type file:             str
    @keyword dir:           The optional directory to place the file into.
    @type dir:              str
    @param force:           Boolean argument which if True causes the file to be overwritten if it
                            already exists.
    @type force:            bool
    @keyword norm:          The normalisation flag which if set to True will cause all graphs to be
                            normalised to a starting value of 1.
    @type norm:             bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if the plot_data argument is one of 'value', 'error', or 'sim'.
    if plot_data not in ['value', 'error', 'sim']:
        raise RelaxError("The plot data argument " + repr(plot_data) + " must be set to either 'value', 'error', 'sim'.")

    # Test if the simulations exist.
    if plot_data == 'sim' and not hasattr(cdp, 'sim_number'):
        raise RelaxNoSimError

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Get the data.
    data, set_names, graph_type = get_data(spin_id, x_data_type=x_data_type, y_data_type=y_data_type, plot_data=plot_data)

    # No data, so close the empty file and exit.
    if not len(data) or not len(data[0]) or not len(data[0][0]):
        warn(RelaxWarning("No data could be found, creating an empty file."))
        file.close()
        return

    # Determine the sequence data type.
    seq_type = [None, None]
    if x_data_type == 'spin':
        seq_type[0] = 'res'
    if y_data_type == 'spin':
        seq_type[1] = 'res'

    # Write the header.
    write_xy_header(sets=len(data[0]), file=file, data_type=[x_data_type, y_data_type], seq_type=seq_type, set_names=set_names, norm=norm)

    # Write the data.
    write_xy_data(data, file=file, graph_type=graph_type, norm=norm)

    # Close the file.
    file.close()


def write_xy_data(data, file=None, graph_type=None, norm=False):
    """Write the data into the Grace xy-scatter plot.

    The numerical data should be supplied as a 4 dimensional list or array object.  The first dimension corresponds to the graphs, Gx.  The second corresponds the sets of each graph, Sx.  The third corresponds to the data series (i.e. each data point).  The forth is a list of the information about each point, it is a list where the first element is the x value, the second is the y value, the third is the optional dx or dy error (either dx or dy dependent upon the graph_type arg), and the forth is the optional dy error when graph_type is xydxdy (the third position is then dx).


    @param data:            The 4D structure of numerical data to graph (see docstring).
    @type data:             list of lists of lists of float
    @keyword file:          The file object to write the data to.
    @type file:             file object
    @keyword graph_type:    The graph type which can be one of xy, xydy, xydx, or xydxdy.
    @type graph_type:       str
    @keyword norm:          The normalisation flag which if set to True will cause all graphs to be normalised to 1.
    @type norm:             bool
    """

    # Loop over the graphs.
    for gi in range(len(data)):
        # Loop over the data sets of the graph.
        for si in range(len(data[gi])):
            # The target and type.
            file.write("@target G%s.S%s\n" % (gi, si))
            file.write("@type %s\n" % graph_type)

            # Normalisation (to the first data point y value!).
            norm_fact = 1.0
            if norm:
                norm_fact = data[gi][si][0][1]

            # Loop over the data points.
            for point in data[gi][si]:
                # X and Y data.
                file.write("%-30s %-30s" % (point[0], point[1]/norm_fact))

                # The dx and dy errors.
                if graph_type in ['xydx', 'xydy']:
                    # Catch x or y-axis errors of None.
                    error = point[2]
                    if error == None:
                        error = 0.0

                    # Write the error.
                    file.write(" %-30s" % (error/norm_fact))

                # The dy errors of xydxdy.
                if graph_type == 'xydxdy':
                    # Catch y-axis errors of None.
                    error = point[3]
                    if error == None:
                        error = 0.0

                    # Write the error.
                    file.write(" %-30s" % (error/norm_fact))

                # End the point.
                file.write("\n")

            # End of the data set i.
            file.write("&\n")


def write_xy_header(file=None, paper_size='A4', title=None, subtitle=None, view=None, sets=1, set_names=None, set_colours=None, symbols=None, symbol_sizes=None, symbol_fill=None, linestyle=None, data_type=None, seq_type=None, axis_labels=None, axis_min=None, axis_max=None, legend_pos=None, legend=False, norm=False):
    """Write the grace header for xy-scatter plots.

    Many of these keyword arguments should be supplied in a [X, Y] list format, where the first element corresponds to the X data, and the second the Y data.  Defaults will be used for any non-supplied args (or lists with elements set to None).


    @keyword file:                  The file object to write the data to.
    @type file:                     file object
    @keyword paper_size:            The paper size, i.e. 'A4'.  If set to None, this will default to letter size.
    @type paper_size:               str
    @keyword title:                 The title of the graph.
    @type title:                    None or str
    @keyword subtitle:              The sub-title of the graph.
    @type subtitle:                 None or str
    @keyword view:                  List of 4 coordinates defining the graph view port.
    @type view:                     None or list of float
    @keyword sets:                  The number of data sets in the graph G0.
    @type sets:                     int
    @keyword set_names:             The names associated with each graph data set G0.Sx.  For example this can be a list of spin identification strings.
    @type set_names:                None or list of str
    @keyword set_colours:           The colours for each graph data set G0.Sx.
    @type set_colours:              None or list of int
    @keyword symbols:               The symbol style for each graph data set G0.Sx.
    @type symbols:                  None or list of int
    @keyword symbol_sizes:          The symbol size for each graph data set G0.Sx.
    @type symbol_sizes:             None or list of int
    @keyword symbol_fill:           The symbol file style for each graph data set G0.Sx.
    @type symbol_fill:              None or list of int
    @keyword linestyle:             The line style for each graph data set G0.Sx.
    @type linestyle:                None or list of int
    @keyword data_type:             The axis data category (in the [X, Y] list format).
    @type data_type:                None or list of str
    @keyword seq_type:              The sequence data type (in the [X, Y] list format).  This is for molecular sequence specific data and can be one of 'res', 'spin', or 'mixed'.
    @type seq_type:                 None or list of str
    @keyword axis_labels:           The labels for the axes (in the [X, Y] list format).
    @type axis_labels:              None or list of str
    @keyword axis_min:              The minimum values for specifying the graph ranges (in the [X, Y] list format).
    @type axis_min:                 None or list of str
    @keyword axis_max:              The maximum values for specifying the graph ranges (in the [X, Y] list format).
    @type axis_max:                 None or list of str
    @keyword legend_pos:            The position of the legend, e.g. [0.3, 0.8].
    @type legend_pos:               None or list of float
    @keyword legend:                If True, the legend will be visible.
    @type legend:                   bool
    @keyword norm:                  The normalisation flag which if set to True will cause all graphs to be normalised to 1.
    @type norm:                     bool
    """

    # Set the None args to lists as needed.
    if not data_type:
        data_type = [None, None]
    if not seq_type:
        seq_type = [None, None]
    if not axis_labels:
        axis_labels = [None, None]
    if not axis_min:
        axis_min = [None, None]
    if not axis_max:
        axis_max = [None, None]

    # Set the Grace version number of the header's formatting for compatibility.
    file.write("@version 50121\n")

    # The paper size.
    if paper_size == 'A4':
        file.write("@page size 842, 595\n")

    # Graph G0.
    file.write("@with g0\n")

    # The view port.
    if not view:
        view = [0.15, 0.15, 1.28, 0.85]
    file.write("@    view %s, %s, %s, %s\n" % (view[0], view[1], view[2], view[3]))

    # The title and subtitle.
    if title:
        file.write("@    title \"%s\"\n" % title)
    if subtitle:
        file.write("@    subtitle \"%s\"\n" % subtitle)

    # Axis specific settings.
    axes = ['x', 'y']
    for i in range(2):
        # Analysis specific methods for making labels.
        analysis_spec = False
        if pipes.cdp_name():
            # Flag for making labels.
            analysis_spec = True

            # Specific value and error, conversion factor, and units returning functions.
            return_units = get_specific_fn('return_units', pipes.get_type())
            return_grace_string = get_specific_fn('return_grace_string', pipes.get_type())

            # Test if the axis data type is a minimisation statistic.
            if data_type[i] != 'spin' and generic_fns.minimise.return_data_name(data_type[i]):
                return_units = generic_fns.minimise.return_units
                return_grace_string = generic_fns.minimise.return_grace_string

        # Some axis default values for spin data.
        if data_type[i] == 'spin':
            # Residue only data.
            if seq_type[i] == 'res':
                # Axis limits.
                if not axis_min[i]:
                    axis_min[i] = repr(cdp.mol[0].res[0].num - 1)
                if not axis_max[i]:
                    axis_max[i] = repr(cdp.mol[0].res[-1].num + 1)

                # X-axis label.
                if not axis_labels[i]:
                    axis_labels[i] = "Residue number"

            # Spin only data.
            if seq_type[i] == 'spin':
                # Axis limits.
                if not axis_min[i]:
                    axis_min[i] = repr(cdp.mol[0].res[0].spin[0].num - 1)
                if not axis_max[i]:
                    axis_max[i] = repr(cdp.mol[0].res[0].spin[-1].num + 1)

                # X-axis label.
                if not axis_labels[i]:
                    axis_labels[i] = "Spin number"

            # Mixed data.
            if seq_type[i] == 'mixed':
                # X-axis label.
                if not axis_labels[i]:
                    axis_labels[i] = "Spin identification string"

        # Some axis default values for other data types.
        else:
            # Label.
            if analysis_spec and not axis_labels[i]:
                # Get the units.
                units = return_units(data_type[i])

                # Set the label.
                axis_labels[i] = return_grace_string(data_type[i])

                # Add units.
                if units:
                    axis_labels[i] = axis_labels[i] + "\\N (" + units + ")"

                # Normalised data.
                if norm and axes[i] == 'y':
                    axis_labels[i] = axis_labels[i] + " \\N\\q(normalised)\\Q"

        # Write out the data.
        if axis_min[i] != None:
            file.write("@    world %smin %s\n" % (axes[i], axis_min[i]))
        if axis_max[i] != None:
            file.write("@    world %smax %s\n" % (axes[i], axis_max[i]))
        if axis_labels[i]:
            file.write("@    %saxis  label \"%s\"\n" % (axes[i], axis_labels[i]))
        file.write("@    %saxis  label char size 1.48\n" % axes[i])
        file.write("@    %saxis  tick major size 0.75\n" % axes[i])
        file.write("@    %saxis  tick major linewidth 0.5\n" % axes[i])
        file.write("@    %saxis  tick minor linewidth 0.5\n" % axes[i])
        file.write("@    %saxis  tick minor size 0.45\n" % axes[i])
        file.write("@    %saxis  ticklabel char size 1.00\n" % axes[i])

    # Legend box.
    if legend_pos:
        file.write("@    legend %s, %s\n" % (legend_pos[0], legend_pos[1]))
    if legend:
        file.write("@    legend off\n")

    # Frame.
    file.write("@    frame linewidth 0.5\n")

    # Loop over each graph set.
    for i in range(sets):
        # Symbol style (default to all different symbols).
        if symbols:
            file.write("@    s%i symbol %i\n" % (i, symbols[i]))
        else:
            file.write("@    s%i symbol %i\n" % (i, i+1))

        # Symbol sizes (default to a small size).
        if symbol_sizes:
            file.write("@    s%i symbol size %s\n" % (i, symbol_sizes[i]))
        else:
            file.write("@    s%i symbol size 0.45\n" % i)

        # The symbol fill.
        if symbol_fill:
            file.write("@    s%i symbol fill pattern %i\n" % (i, symbol_fill[i]))

        # The symbol line width.
        file.write("@    s%i symbol linewidth 0.5\n" % i)

        # Symbol colour (default to nothing).
        if set_colours:
            file.write("@    s%i symbol color %s\n" % (i, set_colours[i]))

        # Error bars.
        file.write("@    s%i errorbar size 0.5\n" % i)
        file.write("@    s%i errorbar linewidth 0.5\n" % i)
        file.write("@    s%i errorbar riser linewidth 0.5\n" % i)

        # Line linestyle (default to nothing).
        if linestyle:
            file.write("@    s%i line linestyle %s\n" % (i, linestyle[i]))

        # Line colours (default to nothing).
        if set_colours:
            file.write("@    s%i line color %s\n" % (i, set_colours[i]))

        # Legend.
        if set_names:
            file.write("@    s%i legend \"%s\"\n" % (i, set_names[i]))
