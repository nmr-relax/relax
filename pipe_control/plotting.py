###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""Module for the plotting of data.

The numerical graph data handled in these functions consists of a 4 dimensional list or array object.  The first dimension corresponds to different graphs.  The second corresponds the different data sets within a single each graph.  The third corresponds to the data series (i.e. each data point).  The forth is a list of the information about each point, it is a list where the first element is the X value, the second is the Y value, the third is the optional dX or dY error, and the forth is the optional dY error when X errors are present (the third position is then dx).
"""


# relax module imports.
from lib.errors import RelaxError
from pipe_control import minimise
from pipe_control.mol_res_spin import spin_loop
import specific_analyses


def assemble_data(spin_id=None, x_data_name=None, y_data_name=None, plot_data=None):
    """Return all the xy data, along with the graph type and names for the graph sets.

    @keyword spin_id:       The spin ID string for restricting the graph to.
    @type spin_id:          str
    @keyword x_data_name:   The category of the X-axis data.
    @type x_data_name:      str
    @keyword y_data_name:   The category of the Y-axis data.
    @type y_data_name:      str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @return:                The 4D graph numerical data structure, the graph type (i.e. on of 'xy', 'xydy', or 'xydxdy'), and the labels for the graph sets.
    @rtype:                 list of lists of lists of float, str, and list of str
    """

    # Initialise the 4D data structure (Gx, Sx, data point, data point info), and graph set labels.
    data_list = False
    data_dict = False

    # The data types.
    x_type = get_data_type(data_name=x_data_name)
    y_type = get_data_type(data_name=y_data_name)

    # Determine the graph type.
    graph_type = classify_graph_2D(x_data_name=x_data_name, y_data_name=y_data_name, x_type=x_type, y_type=y_type)

    # Assemble the different graph data structures.
    if graph_type == 'seq-value':
        data, set_labels, x_err_flag, y_err_flag = assemble_data_seq_value(spin_id=spin_id, x_data_name=x_data_name, y_data_name=y_data_name, plot_data=plot_data)
    elif graph_type == 'value-value':
        data, set_labels, x_err_flag, y_err_flag = assemble_data_scatter(spin_id=spin_id, x_data_name=x_data_name, y_data_name=y_data_name, plot_data=plot_data)
    elif graph_type == 'seq-series':
        data, set_labels, x_err_flag, y_err_flag = assemble_data_seq_series(spin_id=spin_id, x_data_name=x_data_name, y_data_name=y_data_name, plot_data=plot_data, x_type=x_type, y_type=y_type)
    elif graph_type == 'series-series':
        data, set_labels, x_err_flag, y_err_flag = assemble_data_series_series(spin_id=spin_id, x_data_name=x_data_name, y_data_name=y_data_name, plot_data=plot_data, x_type=x_type, y_type=y_type)
    else:
        raise RelaxError("Unknown graph type '%s'." % graph_type)

    # The graph type.
    graph_type = 'X,Y'
    if x_err_flag:
        graph_type = graph_type + ',dX'
    if y_err_flag:
        graph_type = graph_type + ',dY'

    # Return the data.
    return data, set_labels, graph_type


def assemble_data_scatter(spin_id=None, x_data_name=None, y_data_name=None, plot_data='value'):
    """Assemble the graph data for scatter type data of one value verses another.

    For such data, only a single graph and set will be produced.


    @keyword spin_id:       The spin ID string for restricting the graph to.
    @type spin_id:          str
    @keyword x_data_name:   The name of the X-data or variable to plot.
    @type x_data_name:      str
    @keyword y_data_name:   The name of the Y-data or variable to plot.
    @type y_data_name:      str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @return:                The graph data, set labels, and flags for errors in the X and Y dimensions.
    @rtype:                 list of lists of lists of numbers, list of str, bool, bool
    """

    # Default to the assemble_data_seq_value() function, as the graphs are currently not constructed differently.
    return assemble_data_seq_value(x_data_name=x_data_name, y_data_name=y_data_name, plot_data=plot_data)


def assemble_data_seq_series(spin_id=None, x_data_name=None, y_data_name=None, plot_data='value', x_type=None, y_type=None):
    """Assemble the graph data for residue or spin sequence verses verses list or dictionary data.

    For such data, one graph will be produced.  There will be one data set in this graph per series.


    @keyword spin_id:       The spin ID string for restricting the graph to.
    @type spin_id:          str
    @keyword x_data_name:   The name of the X-data or variable to plot.
    @type x_data_name:      str
    @keyword y_data_name:   The name of the Y-data or variable to plot.
    @type y_data_name:      str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @keyword x_type:        The type of X-data to plot.
    @type x_type:           type object
    @keyword y_type:        The type of Y-data to plot.
    @type y_type:           type object
    @return:                The graph data, set labels, and flags for errors in the X and Y dimensions.
    @rtype:                 list of lists of lists of numbers, list of str, bool, bool
    """

    # Initialise some data structures.
    data = [[]]
    set_labels = []
    x_err_flag = False
    y_err_flag = False

    # The sequence and series axes.
    if x_data_name in ['res_num', 'spin_num']:
        seq_axis = 'x'
        series_type = y_type
    else:
        seq_axis = 'y'
        series_type = x_type

    # Determine the number of sets.
    for spin, mol_name, res_num, res_name, id in spin_loop(full_info=True, selection=spin_id, return_id=True, skip_desel=True):
        # Fetch the series data (ignore simulations).
        if seq_axis == 'x':
            val, err = fetch_1D_data(plot_data=plot_data, data_name=y_data_name, spin=spin, res_num=res_num)
        else:
            val, err = fetch_1D_data(plot_data=plot_data, data_name=x_data_name, spin=spin, res_num=res_num)

        # The keys.
        if series_type == dict:
            keys = list(val.keys())

        # Loop over the series data.
        for j in range(len(val)):
            # The index or key for the data.
            if series_type == list:
                elem = j
            else:
                elem = keys[j]

            # Add the set info if new.
            if elem not in set_labels:
                data[0].append([])
                set_labels.append(elem)

    # Sort the set labels.
    set_labels.sort()

    # Number of data points per spin.
    if plot_data == 'sim':
        points = cdp.sim_number
    else:
        points = 1

    # Loop over the spins.
    spin_index = 0
    for spin, mol_name, res_num, res_name, id in spin_loop(full_info=True, selection=spin_id, return_id=True, skip_desel=True):
        # Loop over the data points (for simulations).
        for i in range(points):
            # The X and Y data.
            x_val, x_err = fetch_1D_data(plot_data=plot_data, data_name=x_data_name, spin=spin, res_num=res_num, sim_num=i)
            y_val, y_err = fetch_1D_data(plot_data=plot_data, data_name=y_data_name, spin=spin, res_num=res_num, sim_num=i)

            # Alias the data.
            if seq_axis == 'x':
                series_val = y_val
            else:
                series_val = x_val

            # Go to the next spin if there is missing xy data.
            if x_val == None or y_val == None:
                continue

            # The error flags.
            if x_err != None:
                x_err_flag = True
            if y_err != None:
                y_err_flag = True

            # The keys.
            if series_type == dict:
                keys = list(series_val.keys())

            # Loop over the series data.
            for j in range(len(series_val)):
                # The index or key for the data.
                if series_type == list:
                    index = set_labels.index(j)
                    elem = index
                else:
                    index = set_labels.index(keys[j])
                    elem = set_labels[set_labels.index(keys[j])]

                # Append the data.
                if seq_axis == 'x':
                    data[0][index].append([x_val, y_val[elem]])
                else:
                    data[0][index].append([x_val[elem], y_val])
                if x_err_flag:
                    data[0][index][-1].append(x_err[elem])
                if y_err_flag:
                    data[0][index][-1].append(y_err[elem])

        # Increment the spin index.
        spin_index += 1

    # Return the data.
    return data, set_labels, x_err_flag, y_err_flag


def assemble_data_seq_value(spin_id=None, x_data_name=None, y_data_name=None, plot_data='value'):
    """Assemble the graph data for residue or spin sequence verses values.

    For such data, only a single graph and set will be produced.


    @keyword spin_id:       The spin ID string for restricting the graph to.
    @type spin_id:          str
    @keyword x_data_name:   The name of the X-data or variable to plot.
    @type x_data_name:      str
    @keyword y_data_name:   The name of the Y-data or variable to plot.
    @type y_data_name:      str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @return:                The graph data, set labels, and flags for errors in the X and Y dimensions.
    @rtype:                 list of lists of lists of numbers, list of str, bool, bool
    """

    # Initialise some data structures.
    data = [[[]]]
    set_labels = []
    x_err_flag = False
    y_err_flag = False

    # Count the different spin types.
    spin_names = []
    for spin, mol_name, res_num, res_name, id in spin_loop(full_info=True, selection=spin_id, return_id=True, skip_desel=True):
        # A new spin name.
        if spin.name not in spin_names:
            spin_names.append(spin.name)

    # The number of data sets.
    set_count = len(spin_names)

    # Expand the data structures for the number of sets.
    if set_count > 1:
        # Expand the data array.
        for i in range(set_count-1):
            data[0].append([])

        # Expand the set labels for all spin data.
        for spin, mol_name, res_num, res_name, id in spin_loop(full_info=True, selection=spin_id, return_id=True, skip_desel=True):
            label = "%s spins" % spin.name
            if label not in set_labels:
                set_labels.append(label)

    # Number of data points per spin.
    if plot_data == 'sim':
        points = cdp.sim_number
    else:
        points = 1

    # Loop over the spins.
    for spin, mol_name, res_num, res_name, id in spin_loop(full_info=True, selection=spin_id, return_id=True, skip_desel=True):
        # The set index.
        set_index = spin_names.index(spin.name)

        # Loop over the data points (for simulations).
        for i in range(points):
            # The X and Y data.
            x_val, x_err = fetch_1D_data(plot_data=plot_data, data_name=x_data_name, spin=spin, res_num=res_num, sim_num=i)
            y_val, y_err = fetch_1D_data(plot_data=plot_data, data_name=y_data_name, spin=spin, res_num=res_num, sim_num=i)

            # Go to the next spin if there is missing xy data.
            if x_val == None or y_val == None:
                continue

            # The error flags.
            if x_err != None:
                x_err_flag = True
            if y_err != None:
                y_err_flag = True

            # Append the data.
            data[0][set_index].append([x_val, y_val])
            if x_err_flag:
                data[0][set_index][-1].append(x_err)
            if y_err_flag:
                data[0][set_index][-1].append(y_err)

    # Return the data.
    return data, set_labels, x_err_flag, y_err_flag


def assemble_data_series_series(spin_id=None, x_data_name=None, y_data_name=None, plot_data='value', x_type=None, y_type=None):
    """Assemble the graph data for curves of list or dictionary data verses list or dictionary data.

    For such data, one graph will be produced.  There will be one data set in this graph per spin.


    @keyword spin_id:       The spin ID string for restricting the graph to.
    @type spin_id:          str
    @keyword x_data_name:   The name of the X-data or variable to plot.
    @type x_data_name:      str
    @keyword y_data_name:   The name of the Y-data or variable to plot.
    @type y_data_name:      str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @keyword x_type:        The type of X-data to plot.
    @type x_type:           type object
    @keyword y_type:        The type of Y-data to plot.
    @type y_type:           type object
    @return:                The graph data, set labels, and flags for errors in the X and Y dimensions.
    @rtype:                 list of lists of lists of numbers, list of str, bool, bool
    """

    # Initialise some data structures.
    data = [[]]
    set_labels = []
    x_err_flag = False
    y_err_flag = False

    # Sanity check.
    if x_type != y_type:
        raise RelaxError("The X data type '%s' and Y data type '%s' do not match." % (x_type, y_type))

    # Check if the dictionary keys are the values to plot.
    keys_for_values = None
    base_values = []
    if x_type == dict:
        for spin, mol_name, res_num, res_name, id in spin_loop(full_info=True, selection=spin_id, return_id=True, skip_desel=True):
            # Fetch the series data (ignore simulations).
            x_val, x_err = fetch_1D_data(plot_data=plot_data, data_name=x_data_name, spin=spin, res_num=res_num)
            y_val, y_err = fetch_1D_data(plot_data=plot_data, data_name=y_data_name, spin=spin, res_num=res_num)

            # Go to the next spin if there is missing xy data.
            if x_val == None or y_val == None:
                continue

            # The keys.
            x_keys = list(x_val.keys())
            y_keys = list(y_val.keys())

            # The keys do not match.
            if x_keys[0] in y_keys:
                continue

            # Are the X keys in the Y values?
            if x_keys[0] in y_val.values():
                keys_for_values = 'x'
                for key in x_keys:
                    if key not in base_values:
                        base_values.append(key)

            # Are the Y keys in the X values?
            elif y_keys[0] in x_val.values():
                keys_for_values = 'y'
                for key in y_keys:
                    if key not in base_values:
                        base_values.append(key)

    # Number of data points per spin.
    if plot_data == 'sim':
        points = cdp.sim_number
    else:
        points = 1

    # Loop over the spins.
    spin_index = 0
    for spin, mol_name, res_num, res_name, id in spin_loop(full_info=True, selection=spin_id, return_id=True, skip_desel=True):
        # Append a new set structure and set the name to the spin ID.
        data[0].append([])
        set_labels.append("Spin %s" % id)

        # Loop over the data points (for simulations).
        for i in range(points):
            # The X and Y data.
            x_val, x_err = fetch_1D_data(plot_data=plot_data, data_name=x_data_name, spin=spin, res_num=res_num, sim_num=i)
            y_val, y_err = fetch_1D_data(plot_data=plot_data, data_name=y_data_name, spin=spin, res_num=res_num, sim_num=i)

            # The base values to create the curve from.
            if keys_for_values == None:
                base_values = x_val

            # Go to the next spin if there is missing xy data.
            if x_val == None or y_val == None:
                continue

            # The error flags.
            if x_err != None:
                x_err_flag = True
            if y_err != None:
                y_err_flag = True

            # Series sanity checks.
            if keys_for_values == None and len(x_val) != len(y_val):
                raise RelaxError("The series data %s does not have the same number of elements as %s." % (x_val, y_val))

            # The keys.
            if x_type == dict:
                keys = list(x_val.keys())

            # Loop over the list data.
            for j in range(len(base_values)):
                # The index or key for the data.
                if x_type == list:
                    elem = j
                else:
                    elem = keys[j]

                # Append the data.
                if keys_for_values == None:
                    data[0][spin_index].append([x_val[elem], y_val[elem]])
                    if x_err_flag:
                        data[0][spin_index][-1].append(x_err[elem])
                    if y_err_flag:
                        data[0][spin_index][-1].append(y_err[elem])

                # Append the data (X keys in the Y values).
                elif keys_for_values == 'x':
                    data[0][spin_index].append([x_val[base_values[j]], base_values[j]])
                    if x_err_flag:
                        data[0][spin_index][-1].append(x_err[base_values[j]])
                    if y_err_flag:
                        raise RelaxError("Y errors are not possible when the Y values are keys.")

                # Append the data (Y keys in the X values).
                elif keys_for_values == 'y':
                    data[0][spin_index].append([base_values[j], y_val[base_values[j]]])
                    if x_err_flag:
                        raise RelaxError("X errors are not possible when the X values are keys.")
                    if y_err_flag:
                        data[0][spin_index][-1].append(y_err[base_values[j]])

            # Sort the data for better looking curves.
            data[0][spin_index].sort()

        # Increment the spin index.
        spin_index += 1

    # Return the data.
    return data, set_labels, x_err_flag, y_err_flag


def classify_graph_2D(x_data_name=None, y_data_name=None, x_type=None, y_type=None):
    """Determine the type of graph to produce.

    The graph type can be one of:

        - 'seq-value', the residue or spin sequence verses the parameter value.
        - 'seq-series', the residue or spin sequence verses the parameter value.
        - 'value-value', a scatter plot of one value verses another.
        - 'value-series', a curve of one value verses a list or dictionary of data.
        - 'series-series', curves of list or dictionary data verses list or dictionary data.

    @keyword x_data_name:   The name of the X-data or variable to plot.
    @type x_data_name:      str
    @keyword y_data_name:   The name of the Y-data or variable to plot.
    @type y_data_name:      str
    @keyword x_type:        The type of X-data to plot.
    @type x_type:           type object
    @keyword y_type:        The type of Y-data to plot.
    @type y_type:           type object
    @return:                The graph type.
    @rtype:                 str
    """

    # Disallow certain combinations.
    if x_data_name == y_data_name == 'res_num':
        raise RelaxError("The X and Y-axes can not both be based on residue numbers.")
    if x_data_name == y_data_name == 'spin_num':
        raise RelaxError("The X and Y-axes can not both be based on residue numbers.")

    # Some data type flags.
    x_series = False
    y_series = False
    if x_type == list or x_type == dict:
        x_series = True
    if y_type == list or y_type == dict:
        y_series = True

    # The different X and Y axis sequence types.
    if x_data_name in ['res_num', 'spin_num'] and not y_series:
        return 'seq-value'
    if x_data_name in ['res_num', 'spin_num'] and y_series:
        return 'seq-series'
    if y_data_name in ['res_num', 'spin_num'] and not x_series:
        return 'seq-value'
    if y_data_name in ['res_num', 'spin_num'] and x_series:
        return 'seq-series'

    # Scatter plots.
    if not x_series and not y_series:
        return 'value-value'

    # Series-series data.
    if not x_series and y_series:
        return 'value-series'
    if x_series and not y_series:
        return 'value-series'

    # Series-series data.
    if x_series and y_series:
        return 'series-series'

    # Unknown.
    return 'unknown'


def fetch_1D_data(plot_data=None, data_name=None, spin=None, res_num=None, sim_num=None):
    """Return the value and error for the corresponding axis.

    @keyword plot_data: The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:    str
    @keyword data_name: The name of the data or variable to plot.
    @type data_name:    str
    @keyword spin:      The spin container to fetch the values from.
    @type spin:         SpinContainer instance
    @keyword res_num:   The residue number for the given spin.
    @type res_num:      int
    @keyword sim_num:   The simulation number if simulation data is to be returned.
    @type sim_num:      int
    @return:            The value and error when available.
    @rtype:             int or float, None or float
    """

    # Specific x and y value returning functions.
    return_value, return_conversion_factor = get_functions(data_name=data_name)

    # The residue number data.
    if data_name == 'res_num':
        val, err = res_num, None

    # The spin number data.
    elif data_name == 'spin_num':
        val, err = spin.num, None

    # All other data types.
    else:
        # Get the data.
        if plot_data == 'sim':
            val, err = return_value(spin, data_name, sim=sim_num)
        else:
            val, err = return_value(spin, data_name)

        # Convert to the correct scale.
        if isinstance(val, list):
            for i in range(len(val)):
                val[i] = val[i] / return_conversion_factor(data_name)
                if err != None:
                    err[i] = err[i] / return_conversion_factor(data_name)
        elif isinstance(val, dict):
            for key in val.keys():
                val[key] = val[key] / return_conversion_factor(data_name)
                if err != None:
                    err[key] = err[key] / return_conversion_factor(data_name)
        elif val != None and err != None:
            val = val / return_conversion_factor(data_name)
            err = err / return_conversion_factor(data_name)
        elif val != None:
            val = val / return_conversion_factor(data_name)
        elif err != None:
            err = err / return_conversion_factor(data_name)

    # Convert the errors to values.
    if data_name not in ['res_num', 'spin_num'] and plot_data == 'error':
        val = err
        err = None

    # Simulation data, so turn off errors.
    if plot_data == 'sim':
        err = None

    # Return the data.
    return val, err


def get_functions(data_name=None):
    """Determine the specific functions for the given data type.

    @keyword data_name: The name of the data or variable to plot.
    @type data_name:    str
    @return:            The analysis specific return_value, return_conversion_factor, and data_type methods.
    @rtype:             tuple of methods or None
    """

    # Spin data.
    if data_name in ['res_num', 'spin_num']:
        return None, None

    # A minimisation statistic.
    if minimise.return_data_name(data_name):
        return minimise.return_value, minimise.return_conversion_factor

    # Analysis specific value returning functions.
    else:
        return_value = specific_analyses.setup.get_specific_fn('return_value')
        return_conversion_factor = specific_analyses.setup.get_specific_fn('return_conversion_factor')
        return return_value, return_conversion_factor


def get_data_type(data_name=None):
    """Determine the type for the given data.

    @keyword data_name: The name of the data or variable to plot.
    @type data_name:    str
    @return:            The data type.
    @rtype:             Python type
    """

    # Sequence data.
    if data_name in ['res_num', 'spin_num']:
        return int

    # A minimisation statistic.
    if minimise.return_data_name(data_name):
        return int

    # Analysis specific value returning functions.
    else:
        data_type = specific_analyses.setup.get_specific_fn('data_type')
        return data_type(data_name)
