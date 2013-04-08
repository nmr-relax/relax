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
"""Module for interfacing with Grace (also known as Xmgrace, Xmgr, and ace)."""

# Python module imports.
from numpy import array, ndarray
from os import system
from warnings import warn

# relax module imports.
import pipe_control
from pipe_control.mol_res_spin import count_molecules, count_residues, count_spins, exists_mol_res_spin_data, generate_spin_id, spin_loop
from pipe_control import pipes
from pipe_control.result_files import add_result_file
from pipe_control.plotting import determine_functions
from lib.errors import RelaxError, RelaxNoSequenceError, RelaxNoSimError
from lib.io import get_file_path, open_write_file, test_binary
from lib.software.grace import write_xy_data, write_xy_header
from lib.warnings import RelaxWarning
import specific_analyses
from status import Status; status = Status()


def axis_setup(data_type=None, norm=True):
    """Determine the axis information for relax data store specific data.

    @keyword data_type: The axis data category (in the [X, Y] list format).
    @type data_type:    list of str
    @keyword norm:      The normalisation flag which if set to True will cause all graphs to be normalised to a starting value of 1.
    @type norm:         bool
    @return:            The axis information.  This includes the sequence type, the list of lower bounds, the list of upper bounds, and the axis labels.
    @rtype:             list of str or None, list of int or None, list of int or None, list of str or None
    """

    # Axis specific settings.
    axes = ['x', 'y']
    axis_min = [None, None]
    axis_max = [None, None]
    seq_type = [None, None]
    axis_labels = [None, None]
    for i in range(2):
        # Determine the sequence data type.
        if data_type[i] == 'spin':
            seq_type[i] = 'res'

        # Analysis specific methods for making labels.
        analysis_spec = False
        if pipes.cdp_name():
            # Flag for making labels.
            analysis_spec = True

            # Specific value and error, conversion factor, and units returning functions.
            return_units = specific_analyses.setup.get_specific_fn('return_units', pipes.get_type())
            return_grace_string = specific_analyses.setup.get_specific_fn('return_grace_string', pipes.get_type())

            # Test if the axis data type is a minimisation statistic.
            if data_type[i] and data_type[i] != 'spin' and pipe_control.minimise.return_data_name(data_type[i]):
                return_units = pipe_control.minimise.return_units
                return_grace_string = pipe_control.minimise.return_grace_string

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

    # Return the data.
    return seq_type, axis_min, axis_max, axis_labels


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
    data_dict = False

    # Specific x and y value returning functions.
    x_return_value, x_return_conversion_factor, x_get_type = determine_functions(category=x_data_type)
    y_return_value, y_return_conversion_factor, y_get_type = determine_functions(category=y_data_type)

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
        for spin, mol_name, res_num, res_name, id in spin_loop(full_info=True, selection=spin_id, return_id=True):
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
            if data_list or isinstance(x_val, list):
                # Append a new set structure and set the name to the spin ID.
                data[0].append([])
                set_labels.append("Spin %s" % id)

                # The set index.
                index = len(data[0]) - 1

                # No errors.
                if x_err == None:
                    x_err = [None]*len(x_val)
                if y_err == None:
                    y_err = [None]*len(y_val)

                # Data list flag.
                data_list = True

            # One set per spin (dictionary data has been returned).
            if data_dict or isinstance(x_val, dict):
                # Append a new set structure and set the name to the spin ID.
                data[0].append([])
                set_labels.append("Spin %s" % id)

                # The set index.
                index = len(data[0]) - 1

                # Convert to lists.
                list_data = []
                for key in x_val.keys():
                    list_data.append([x_val[key], y_val[key]])
                list_data.sort()

                # Overwrite the data structures.
                x_val = []
                y_val = []
                for i in range(len(list_data)):
                    x_val.append(list_data[i][0])
                    y_val.append(list_data[i][1])

                # No errors.
                if x_err == None:
                    x_err = [None]*len(x_val)
                if y_err == None:
                    y_err = [None]*len(y_val)

                # Data list flag.
                data_dict = True

            # Convert the data to lists for packing into 1 point.
            else:
                x_val = [x_val]
                y_val = [y_val]
                x_err = [x_err]
                y_err = [y_err]

            # A new spin type (one data set per spin type).
            if not data_list and not data_dict:
                if spin.name not in spin_names:
                    # Append a new set structure.
                    data[0].append([])

                    # Append the label.
                    set_labels.append("%s spins. " % spin.name + set_label)

                    # Add the spin name to the list.
                    spin_names.append(spin.name)

                    # The set index.
                    index = i * len(spin_names) + spin_names.index(spin.name)

                # Existing spin type, so change the index to match the correct data category (fix for bug #20120, https://gna.org/bugs/?20120).
                else:
                    index = spin_names.index(spin.name)

            # Loop over the points.
            for j in range(len(x_val)):
                # Initialise and alias point structure.
                data[0][index].append([])
                point = data[0][index][-1]

                # Conversion factors.
                if x_data_type != 'spin':
                    x_val[j] = x_val[j] / x_return_conversion_factor(x_data_type)
                if x_err[j] and x_data_type != 'spin':
                    x_err[j] = x_err[j] / x_return_conversion_factor(x_data_type)
                y_val[j] = y_val[j] / y_return_conversion_factor(y_data_type)
                if y_err[j] and y_data_type != 'spin':
                    y_err[j] = y_err[j] / y_return_conversion_factor(y_data_type)

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

    # Remodel the data.
    new_data = []
    for i in range(len(data)):
        new_data.append([])
        for j in range(len(data[i])):
            new_data[i].append([])
            for k in range(len(data[i][j])):
                # The xy data.
                new_data[i][j].append([])
                new_data[i][j][k].append(data[i][j][k][0])
                new_data[i][j][k].append(data[i][j][k][1])

                # First error set.
                if graph_type in ['xydx', 'xydxdy']:
                    new_data[i][j][k].append(data[i][j][k][2])

                # Second error set.
                if graph_type in ['xydy', 'xydxdy']:
                    new_data[i][j][k].append(data[i][j][k][3])

    # Return the data.
    return new_data, set_labels, graph_type


def get_data_types():
    """Get all of the data types to plot for the current data pipe.

    @return:    A list of lists of all the allowable data type descriptions and their values.
    @rtype:     list of list of str
    """

    # Get the specific functions (return an empty list if a RelaxError occurs).
    try:
        data_names = specific_analyses.setup.get_specific_fn('data_names', cdp.pipe_type, raise_error=False)
        return_data_desc = specific_analyses.setup.get_specific_fn('return_data_desc', cdp.pipe_type, raise_error=False)
    except:
        return []

    # The data names, if they exist.
    names = data_names(set='params')

    # Initialise the list and then add the sequence data.
    data = []
    data.append(["Spin sequence", 'spin'])

    # Loop over the parameters.
    for name in (data_names(set='params') + data_names(set='generic')):
        # Get the description.
        try:
            desc = return_data_desc(name)
        except:
            return []

        # No description.
        if not desc:
            text = name

        # The text.
        else:
            text = "'%s':  %s" % (name, desc)

        # Append the description.
        data.append([text, name])

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
    @param force:           Boolean argument which if True causes the file to be overwritten if it already exists.
    @type force:            bool
    @keyword norm:          The normalisation flag which if set to True will cause all graphs to be normalised to a starting value of 1.
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
    file_path = get_file_path(file, dir)
    file = open_write_file(file, dir, force)

    # Get the data.
    data, set_names, graph_type = get_data(spin_id, x_data_type=x_data_type, y_data_type=y_data_type, plot_data=plot_data)

    # No data, so close the empty file and exit.
    if not len(data) or not len(data[0]) or not len(data[0][0]):
        warn(RelaxWarning("No data could be found, creating an empty file."))
        file.close()
        return

    # Get the axis information.
    data_type = [x_data_type, y_data_type]
    seq_type, axis_min, axis_max, axis_labels = axis_setup(data_type=data_type, norm=norm)

    # Write the header.
    write_xy_header(sets=len(data[0]), file=file, data_type=data_type, seq_type=seq_type, set_names=set_names, axis_labels=axis_labels, axis_min=axis_min, axis_max=axis_max, norm=norm)

    # Write the data.
    write_xy_data(data, file=file, graph_type=graph_type, norm=norm)

    # Close the file.
    file.close()

    # Add the file to the results file list.
    add_result_file(type='grace', label='Grace', file=file_path)
