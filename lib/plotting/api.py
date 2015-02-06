###############################################################################
#                                                                             #
# Copyright (C) 2014-2015 Edward d'Auvergne                                   #
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
"""The relax library plotting API."""

# relax module imports.
from lib.errors import RelaxError
from lib.plotting import gnuplot
from lib.plotting import grace
from lib.plotting import text


def correlation_matrix(format=None, matrix=None, labels=None, file=None, dir=None, force=False):
    """Plotting API function for representing correlation matrices.

    @keyword format:    The specific backend to use.
    @type format:       str
    @keyword matrix:    The correlation matrix.  This must be a square matrix.
    @type matrix:       numpy rank-2 array.
    @keyword labels:    The labels for each element of the matrix.  The same label is assumed for each [i, i] pair in the matrix.
    @type labels:       list of str
    @keyword file:      The name of the file to create.
    @type file:         str
    @keyword dir:       The directory where the PDB file will be placed.  If set to None, then the file will be placed in the current directory.
    @type dir:          str or None
    """

    # The supported formats.
    function = {
        'gnuplot': gnuplot.correlation_matrix,
        'text': text.correlation_matrix
    }

    # Unsupported format.
    if format not in function:
        raise RelaxError("The plotting of correlation matrix data using the '%s' format is not supported." % format)

    # Call the backend function.
    function[format](matrix=matrix, labels=labels, file=file, dir=dir, force=force)


def write_xy_data(format=None, data=None, file=None, graph_type=None, norm_type='first', norm=None, autoscale=True):
    """Write the data into a XY-scatter plot.

    The numerical data should be supplied as a 4 dimensional list or array object.  The first dimension corresponds to the graphs.  The second corresponds the sets of each graph.  The third corresponds to the data series (i.e. each data point).  The forth is a list of the information about each point, it is a list where the first element is the x value, the second is the y value, the third is the optional dx or dy error (either dx or dy dependent upon the graph_type arg), and the forth is the optional dy error when graph_type is xydxdy (the third position is then dx).


    @keyword format:        The specific backend to use.  The currently support backends are 'grace'.
    @type format:           str
    @keyword data:          The 4D structure of numerical data to graph (see docstring).
    @type data:             list of lists of lists of float
    @keyword file:          The file object to write the data to.
    @type file:             file object
    @keyword graph_type:    The graph type which can be one of xy, xydy, xydx, or xydxdy.
    @type graph_type:       str
    @keyword norm_type:     The point to normalise to 1.  This can be 'first' or 'last'.
    @type norm_type:        str
    @keyword norm:          The normalisation flag which if set to True will cause all graphs to be normalised to 1.  The first dimension is the graph.
    @type norm:             None or list of bool
    @keyword autoscale:     A flag which if True will cause the each graph to be autoscaled.  If you have supplied a world view for the header or the tick spacing, this argument should be set to False to prevent that world view from being overwritten.
    @type autoscale:        bool
    """

    # The supported formats.
    function = {
        'grace': grace.write_xy_data,
    }

    # Unsupported format.
    if format not in function:
        raise RelaxError("The plotting of XY data using the '%s' format is not supported." % format)

    # Call the backend function.
    function[format](data=data, file=file, graph_type=graph_type, norm_type=norm_type, norm=norm, autoscale=autoscale)


def write_xy_header(format=None, file=None, paper_size='A4', title=None, subtitle=None, world=None, view=None, graph_num=1, sets=None, set_names=None, set_colours=None, x_axis_type_zero=None, y_axis_type_zero=None, symbols=None, symbol_sizes=None, symbol_fill=None, linestyle=None, linetype=None, linewidth=None, data_type=None, seq_type=None, axis_labels=None, tick_major_spacing=None, tick_minor_count=None, legend=None, legend_pos=None, legend_box_fill_pattern=None, legend_char_size=None, norm=None):
    """Write the header for XY-scatter plots.

    Many of these keyword arguments should be supplied in a [X, Y] list format, where the first element corresponds to the X data, and the second the Y data.  Defaults will be used for any non-supplied args (or lists with elements set to None).


    @keyword format:                    The specific backend to use.  The currently support backends are 'grace'.
    @type format:                       str
    @keyword file:                      The file object to write the data to.
    @type file:                         file object
    @keyword paper_size:                The paper size, i.e. 'A4'.  For the software Grace, if not set this will default to letter size.
    @type paper_size:                   str
    @keyword title:                     The title of the graph.
    @type title:                        None or str
    @keyword subtitle:                  The sub-title of the graph.
    @type subtitle:                     None or str
    @keyword world:                     The plot default zoom.  This consists of a list of the X-axis minimum, Y-axis minimum, X-axis maximum, and Y-axis maximum values.  Each graph should supply its own world view.
    @type world:                        Nor or list of list of numbers
    @keyword view:                      List of 4 coordinates defining the graph view port.
    @type view:                         None or list of float
    @keyword graph_num:                 The total number of graphs.
    @type graph_num:                    int
    @keyword sets:                      The number of data sets in each graph.
    @type sets:                         list of int
    @keyword set_names:                 The names associated with each graph data set (Gx.Sy in Grace).  For example this can be a list of spin identification strings.  The first dimension is the graph, the second is the set.
    @type set_names:                    None or list of list of str
    @keyword set_colours:               The colours for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type set_colours:                  None or list of list of int
    @keyword x_axis_type_zero:          The flags specifying if the X-axis should be placed at zero.
    @type x_axis_type_zero:             None or list of lists of bool
    @keyword y_axis_type_zero:          The flags specifying if the Y-axis should be placed at zero.
    @type y_axis_type_zero:             None or list of lists of bool
    @keyword symbols:                   The symbol style for each graph data set (Gx.Sy in Grace).  The first dimension is the graph, the second is the set.
    @type symbols:                      None or list of list of int
    @keyword symbol_sizes:              The symbol size for each graph data set (Gx.Sy in Grace).  The first dimension is the graph, the second is the set.
    @type symbol_sizes:                 None or list of list of int
    @keyword symbol_fill:               The symbol file style for each graph data set (Gx.Sy in Grace).  The first dimension is the graph, the second is the set.
    @type symbol_fill:                  None or list of list of int
    @keyword linestyle:                 The line style for each graph data set (Gx.Sy in Grace).  The first dimension is the graph, the second is the set.
    @type linestyle:                    None or list of list of int
    @keyword linetype:                  The line type for each graph data set (Gx.Sy in Grace).  The first dimension is the graph, the second is the set.
    @type linetype:                     None or list of list of int
    @keyword linewidth:                 The line width for all elements of each graph data set (Gx.Sy in Grace).  The first dimension is the graph, the second is the set.
    @type linewidth:                    None or list of float
    @keyword data_type:                 The axis data category (in the [X, Y] list format).
    @type data_type:                    None or list of list of str
    @keyword seq_type:                  The sequence data type (in the [X, Y] list format).  This is for molecular sequence specific data and can be one of 'res', 'spin', or 'mixed'.
    @type seq_type:                     None or list of list of str
    @keyword tick_major_spacing:        The spacing between major ticks.  This is in the [X, Y] list format whereby the first dimension corresponds to the graph number.
    @type tick_major_spacing:           None or list of list of numbers
    @keyword tick_minor_count:          The number of minor ticks between the major ticks.  This is in the [X, Y] list format whereby the first dimension corresponds to the graph number.
    @type tick_minor_count:             None or list of list of int
    @keyword axis_labels:               The labels for the axes (in the [X, Y] list format).  The first dimension is the graph.
    @type axis_labels:                  None or list of list of str
    @keyword legend:                    If True, the legend will be visible.  The first dimension is the graph.
    @type legend:                       list of bool
    @keyword legend_pos:                The position of the legend, e.g. [0.3, 0.8].  The first dimension is the graph.
    @type legend_pos:                   None or list of list of float
    @keyword legend_box_fill_pattern:   The legend box fill.  If set to 0, it will become transparent.
    @type legend_box_fill_pattern:      int
    @keyword legend_char_size:          The size of the legend box text.
    @type legend_char_size:             float
    @keyword norm:                      The normalisation flag which if set to True will cause all graphs to be normalised to 1.  The first dimension is the graph.
    @type norm:                         list of bool
    """

    # The supported formats.
    function = {
        'grace': grace.write_xy_header,
    }

    # Unsupported format.
    if format not in function:
        raise RelaxError("The plotting of XY data using the '%s' format is not supported." % format)

    # Call the backend function.
    function[format](file=file, paper_size=paper_size, title=title, subtitle=subtitle, world=world, view=view, graph_num=graph_num, sets=sets, set_names=set_names, set_colours=set_colours, x_axis_type_zero=x_axis_type_zero, y_axis_type_zero=y_axis_type_zero, symbols=symbols, symbol_sizes=symbol_sizes, symbol_fill=symbol_fill, linestyle=linestyle, linetype=linetype, linewidth=linewidth, data_type=data_type, seq_type=seq_type, axis_labels=axis_labels, tick_major_spacing=tick_major_spacing, tick_minor_count=tick_minor_count, legend=legend, legend_pos=legend_pos, legend_box_fill_pattern=legend_box_fill_pattern, legend_char_size=legend_char_size, norm=norm)
