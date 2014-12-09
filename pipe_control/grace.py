###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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
from os import system
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxNoSequenceError, RelaxNoSimError
from lib.io import get_file_path, open_write_file, test_binary
from lib.software.grace import write_xy_data, write_xy_header
from lib.warnings import RelaxWarning
from pipe_control.mol_res_spin import count_molecules, count_residues, count_spins, exists_mol_res_spin_data
from pipe_control import pipes
from pipe_control.pipes import check_pipe
from pipe_control.result_files import add_result_file
from pipe_control.plotting import assemble_data
from specific_analyses.api import return_api
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
    seq_type = [None, None]
    axis_labels = [None, None]
    for i in range(2):
        # Determine the sequence data type.
        if data_type[i] == 'res_num':
            seq_type[i] = 'res'

        # Analysis specific methods for making labels.
        analysis_spec = False
        if pipes.cdp_name():
            # Flag for making labels.
            analysis_spec = True

            # The specific analysis API object.
            api = return_api()

        # Some axis default values for spin data.
        if data_type[i] == 'res_num':
            # Residue only data.
            if seq_type[i] == 'res':
                # X-axis label.
                if not axis_labels[i]:
                    axis_labels[i] = "Residue number"

            # Spin only data.
            if seq_type[i] == 'spin':
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
                units = api.return_units(data_type[i])

                # Set the label.
                axis_labels[i] = api.return_grace_string(data_type[i])

                # Add units.
                if units:
                    axis_labels[i] = axis_labels[i] + "\\N (" + units + ")"

                # Normalised data.
                if norm and axes[i] == 'y':
                    axis_labels[i] = axis_labels[i] + " \\N\\q(normalised)\\Q"

    # Return the data.
    return seq_type, axis_labels


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


def get_data_types():
    """Get all of the data types to plot for the current data pipe.

    @return:    A list of lists of all the allowable data type descriptions and their values.
    @rtype:     list of list of str
    """

    # The specific analysis API object.
    api = return_api()

    # Return an empty list if the required functions are absent.
    if not hasattr(api, 'data_names') or not hasattr(api, 'return_data_desc'):
        return []

    # The data names, if they exist.
    names = api.data_names(set='params')

    # Initialise the list and then add the sequence data.
    data = []
    data.append(["Spin sequence", 'spin'])

    # Loop over the parameters.
    for name in (api.data_names(set='params') + api.data_names(set='generic') + api.data_names(set='min')):
        # Get the description.
        try:
            desc = api.return_data_desc(name)
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
    system(grace_exe + " \"" + file_path + "\" &")


def write(x_data_type='res_num', y_data_type=None, spin_id=None, plot_data='value', norm_type='first', file=None, dir=None, force=False, norm=True):
    """Writing data to a file.

    @keyword x_data_type:   The category of the X-axis data.
    @type x_data_type:      str
    @keyword y_data_type:   The category of the Y-axis data.
    @type y_data_type:      str
    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @keyword plot_data:     The type of the plotted data, one of 'value', 'error', or 'sim'.
    @type plot_data:        str
    @keyword norm_type:     The point to normalise to 1.  This can be 'first' or 'last'.
    @type norm_type:        str
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
    check_pipe()

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
    data, set_names, graph_type = assemble_data(spin_id, x_data_name=x_data_type, y_data_name=y_data_type, plot_data=plot_data)

    # Convert the graph type.
    if graph_type == 'X,Y':
        graph_type = 'xy'
    elif graph_type == 'X,Y,dX':
        graph_type = 'xydx'
    elif graph_type == 'X,Y,dY':
        graph_type = 'xydy'
    elif graph_type == 'X,Y,dX,dY':
        graph_type = 'xydxdy'

    # No data, so close the empty file and exit.
    if not len(data) or not len(data[0]) or not len(data[0][0]):
        warn(RelaxWarning("No data could be found, creating an empty file."))
        file.close()
        return

    # Get the axis information.
    data_type = [x_data_type, y_data_type]
    seq_type, axis_labels = axis_setup(data_type=data_type, norm=norm)

    # Write the header.
    write_xy_header(file=file, data_type=data_type, seq_type=seq_type, sets=[len(data[0])], set_names=[set_names], axis_labels=[axis_labels], norm=[norm])

    # Write the data.
    write_xy_data(data, file=file, graph_type=graph_type, norm_type=norm_type, norm=[norm])

    # Close the file.
    file.close()

    # Add the file to the results file list.
    add_result_file(type='grace', label='Grace', file=file_path)
