###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
# Copyright (C) 2013 Troels E. Linnet                                         #
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

# relax module imports.
import pipe_control
from pipe_control import pipes
import specific_analyses


def script_grace2images(file=None):
    """Write a python "grace to PNG/EPS/SVG..." conversion script..

    The makes a conversion script to image types as PNG/EPS/SVG. The conversion is looping over a directory list of *.agr files, and making function calls to xmgrace. Successful conversion of images depends on the compilation of xmgrace. The input is a list of image types which is wanted, f.ex: PNG EPS SVG. PNG is default.

    @keyword file:          The file object to write the data to.
    @type file:             file object
    """

    # Write to file
    file.write("#!/usr/bin/env python\n")
    file.write("\n")
    file.write("import glob, os, sys\n")
    file.write("import shlex, subprocess\n")
    file.write("import optparse\n")
    file.write("\n")
    file.write("# Define a callback function, for a multiple input of PNG, EPS, SVG\n")
    file.write("def foo_callback(option, opt, value, parser):\n")
    file.write("    setattr(parser.values, option.dest, value.split(','))\n")
    file.write("\n")
    file.write("# Add functioning for argument parsing\n")
    file.write("parser = optparse.OptionParser(description='Process grace files to images')\n")
    file.write("# Add argument type. Destination instance is set to types.\n")
    file.write("parser.add_option('-g', action='store_true', dest='relax_gui', default=False, help='Make it possible to run script through relax GUI. Run by using User-functions -> script')\n")
    file.write("parser.add_option('-l', action='callback', callback=foo_callback, dest='l', type=\"string\", default=False, help='Make in possible to run scriptif relax has logfile turned on. Run by using User-functions -> script')\n")
    file.write("parser.add_option('-t', action='callback', callback=foo_callback, dest='types', type=\"string\", default=[], help='List image types for conversion. Execute script with: python %s -t PNG,EPS ...'%(sys.argv[0]))\n")
    file.write("\n")
    file.write("# Parse the arguments to a Class instance object\n")
    file.write("args = parser.parse_args()\n")
    file.write("\n")
    file.write("# Lets print help if no arguments are passed\n")
    file.write("if len(sys.argv) == 1 or len(args[0].types) == 0:\n")
    file.write("    print('system argument is:', sys.argv)\n")
    file.write("    parser.print_help()\n")
    file.write("    print('Performing a default PNG conversion')\n")
    file.write("    # If no input arguments, we make a default PNG option\n")
    file.write("    args[0].types = ['PNG']\n")
    file.write("\n")
    file.write("# If we run through the GUI we cannot pass input arguments so we make a default PNG option\n")
    file.write("if args[0].relax_gui:\n")
    file.write("    args[0].types = ['PNG']\n")
    file.write("\n")
    file.write("types = list(args[0].types)\n")
    file.write("\n")
    file.write("# A easy search for files with *.agr, is to use glob, which is pathnames matching a specified pattern according to the rules used by the Unix shell, not opening a shell\n")
    file.write("gracefiles = glob.glob(\"*.agr\")\n")
    file.write("\n")
    file.write("# For png conversion, several parameters can be passed to xmgrace. These can be altered later afterwards and the script rerun. \n")
    file.write("# The option for transparent is good for poster or insertion in color backgrounds. The ability for this still depends on xmgrace compilation\n")
    file.write("if \"PNG\" in types:\n")
    file.write("    pngpar = \"png.par\"\n")
    file.write("    if not os.path.isfile(pngpar):\n")
    file.write("        wpngpar = open(pngpar, \"w\")\n")
    file.write("        wpngpar.write(\"DEVICE \\\"PNG\\\" FONT ANTIALIASING on\\n\")\n")
    file.write("        wpngpar.write(\"DEVICE \\\"PNG\\\" OP \\\"transparent:on\\\"\\n\")\n")
    file.write("        wpngpar.write(\"DEVICE \\\"PNG\\\" OP \\\"compression:9\\\"\\n\")\n")
    file.write("        wpngpar.close()\n")
    file.write("\n")
    file.write("# Now loop over the grace files\n")
    file.write("for grace in gracefiles:\n")
    file.write("    # Get the filename without extension\n")
    file.write("    fname = grace.split(\".agr\")[0]\n")
    file.write("    if (\"PNG\" in types or \".PNG\" in types or \"png\" in types or \".png\" in types):\n")
    file.write("        # Produce the argument string\n")
    file.write("        im_args = r\"xmgrace -hdevice PNG -hardcopy -param %s -printfile %s.png %s\" % (pngpar, fname, grace)\n")
    file.write("        # Split the arguments the right way to call xmgrace\n")
    file.write("        im_args = shlex.split(im_args)\n")
    file.write("        return_code = subprocess.call(im_args)\n")
    file.write("    if (\"EPS\" in types or \".EPS\" in types or \"eps\" in types or \".eps\" in types):\n")
    file.write("        im_args = r\"xmgrace -hdevice EPS -hardcopy -printfile %s.eps %s\" % (fname, grace)\n")
    file.write("        im_args = shlex.split(im_args)\n")
    file.write("        return_code = subprocess.call(im_args)\n")
    file.write("    if (\"JPG\" in types or \".JPG\" in types or \"jpg\" in types or \".jpg\" in types):\n")
    file.write("        im_args = r\"xmgrace -hdevice JPEG -hardcopy -printfile %s.jpg %s\" % (fname, grace)\n")
    file.write("        im_args = shlex.split(im_args)\n")
    file.write("    if (\"JPEG\" in types or \".JPEG\" in types or \"jpeg\" in types or \".jpeg\" in types):\n")
    file.write("        im_args = r\"xmgrace -hdevice JPEG -hardcopy -printfile %s.jpg %s\" % (fname, grace)\n")
    file.write("        im_args = shlex.split(im_args)\n")
    file.write("        return_code = subprocess.call(im_args)\n")
    file.write("    if (\"SVG\" in types or \".SVG\" in types or \"svg\" in types or \".svg\" in types):\n")
    file.write("        im_args = r\"xmgrace -hdevice SVG -hardcopy -printfile %s.svg %s\" % (fname, grace)\n")
    file.write("        im_args = shlex.split(im_args)\n")
    file.write("        return_code = subprocess.call(im_args)\n")


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

    # Comment columns.
    comment_col = 2
    if graph_type in ['xydx', 'xydy']:
        comment_col = 3
    elif graph_type == 'xydxdy':
        comment_col = 4

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
                # Bad data.
                if point[0] == None or point[1] == None:
                    continue

                # X and Y data.
                file.write("%-30s %-30.15f" % (point[0], point[1]/norm_fact))

                # The dx and dy errors.
                if graph_type in ['xydx', 'xydy', 'xydxdy']:
                    # Catch x or y-axis errors of None.
                    error = point[2]
                    if error == None:
                        error = 0.0

                    # Write the error.
                    file.write(" %-30.15f" % (error/norm_fact))

                # The dy errors of xydxdy.
                if graph_type == 'xydxdy':
                    # Catch y-axis errors of None.
                    error = point[3]
                    if error == None:
                        error = 0.0

                    # Write the error.
                    file.write(" %-30.15f" % (error/norm_fact))

                # The comment if given.
                try:
                    file.write("%30s \"# %s\"" % ('', point[comment_col]))
                except IndexError:
                    pass

                # End the point.
                file.write("\n")

            # End of the data set i.
            file.write("&\n")

    # Autoscaling of all graphs to avoid user confusion.
    file.write("@autoscale\n")


def write_xy_header(file=None, paper_size='A4', title=None, subtitle=None, view=None, sets=1, set_names=None, set_colours=None, symbols=None, symbol_sizes=None, symbol_fill=None, linestyle=None, linetype=None, linewidth=0.5, data_type=None, seq_type=None, axis_labels=None, legend=True, legend_pos=None, legend_box_fill_pattern=1, legend_char_size=1.0, norm=False):
    """Write the grace header for xy-scatter plots.

    Many of these keyword arguments should be supplied in a [X, Y] list format, where the first element corresponds to the X data, and the second the Y data.  Defaults will be used for any non-supplied args (or lists with elements set to None).


    @keyword file:                      The file object to write the data to.
    @type file:                         file object
    @keyword paper_size:                The paper size, i.e. 'A4'.  If set to None, this will default to letter size.
    @type paper_size:                   str
    @keyword title:                     The title of the graph.
    @type title:                        None or str
    @keyword subtitle:                  The sub-title of the graph.
    @type subtitle:                     None or str
    @keyword view:                      List of 4 coordinates defining the graph view port.
    @type view:                         None or list of float
    @keyword sets:                      The number of data sets in the graph G0.
    @type sets:                         int
    @keyword set_names:                 The names associated with each graph data set G0.Sx.  For example this can be a list of spin identification strings.
    @type set_names:                    None or list of str
    @keyword set_colours:               The colours for each graph data set G0.Sx.
    @type set_colours:                  None or list of int
    @keyword symbols:                   The symbol style for each graph data set G0.Sx.
    @type symbols:                      None or list of int
    @keyword symbol_sizes:              The symbol size for each graph data set G0.Sx.
    @type symbol_sizes:                 None or list of int
    @keyword symbol_fill:               The symbol file style for each graph data set G0.Sx.
    @type symbol_fill:                  None or list of int
    @keyword linestyle:                 The line style for each graph data set G0.Sx.
    @type linestyle:                    None or list of int
    @keyword linetype:                  The line type for each graph data set G0.Sx.
    @type linetype:                     None or list of int
    @keyword linewidth:                 The line width for all elements of each graph data set G0.Sx.
    @type linewidth:                    None or float
    @keyword data_type:                 The axis data category (in the [X, Y] list format).
    @type data_type:                    None or list of str
    @keyword seq_type:                  The sequence data type (in the [X, Y] list format).  This is for molecular sequence specific data and can be one of 'res', 'spin', or 'mixed'.
    @type seq_type:                     None or list of str
    @keyword axis_labels:               The labels for the axes (in the [X, Y] list format).
    @type axis_labels:                  None or list of str
    @keyword legend:                    If True, the legend will be visible.
    @type legend:                       bool
    @keyword legend_pos:                The position of the legend, e.g. [0.3, 0.8].
    @type legend_pos:                   None or list of float
    @keyword legend_box_fill_pattern:   The legend box fill.  If set to 0, it will become transparent.
    @type legend_box_fill_pattern:      int
    @keyword legend_char_size:          The size of the legend box text.
    @type legend_char_size:             float
    @keyword norm:                      The normalisation flag which if set to True will cause all graphs to be normalised to 1.
    @type norm:                         bool
    """

    # Set the None args to lists as needed.
    if not data_type:
        data_type = [None, None]
    if not seq_type:
        seq_type = [None, None]
    if not axis_labels:
        axis_labels = [None, None]

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
        if axis_labels[i]:
            file.write("@    %saxis  label \"%s\"\n" % (axes[i], axis_labels[i]))
        file.write("@    %saxis  label char size 1.48\n" % axes[i])
        file.write("@    %saxis  tick major size 0.75\n" % axes[i])
        file.write("@    %saxis  tick major linewidth %s\n" % (axes[i], linewidth))
        file.write("@    %saxis  tick minor linewidth %s\n" % (axes[i], linewidth))
        file.write("@    %saxis  tick minor size 0.45\n" % axes[i])
        file.write("@    %saxis  ticklabel char size 1.00\n" % axes[i])

    # Legend box.
    if legend:
        file.write("@    legend on\n")
    else:
        file.write("@    legend off\n")
    if legend_pos:
        file.write("@    legend %s, %s\n" % (legend_pos[0], legend_pos[1]))
    file.write("@    legend box fill pattern %s\n" % legend_box_fill_pattern)
    file.write("@    legend char size %s\n" % legend_char_size)

    # Frame.
    file.write("@    frame linewidth %s\n" % linewidth)

    # Loop over each graph set.
    for i in range(sets):
        # Symbol style (default to all different symbols).
        if symbols:
            file.write("@    s%i symbol %i\n" % (i, symbols[i]))
        else:
            # The symbol number (cycle between 1 and 10).
            num = i % 10 + 1

            # Write out.
            file.write("@    s%i symbol %i\n" % (i, num))

        # Symbol sizes (default to a small size).
        if symbol_sizes:
            file.write("@    s%i symbol size %s\n" % (i, symbol_sizes[i]))
        else:
            file.write("@    s%i symbol size 0.45\n" % i)

        # The symbol fill.
        if symbol_fill:
            file.write("@    s%i symbol fill pattern %i\n" % (i, symbol_fill[i]))

        # The symbol line width.
        file.write("@    s%i symbol linewidth %s\n" % (i, linewidth))

        # Symbol colour (default to nothing).
        if set_colours:
            file.write("@    s%i symbol color %s\n" % (i, set_colours[i]))

        # Error bars.
        file.write("@    s%i errorbar size 0.5\n" % i)
        file.write("@    s%i errorbar linewidth %s\n" % (i, linewidth))
        file.write("@    s%i errorbar riser linewidth %s\n" % (i, linewidth))

        # Line linestyle (default to nothing).
        if linestyle:
            file.write("@    s%i line linestyle %s\n" % (i, linestyle[i]))

        # Line linetype (default to nothing).
        if linetype:
            file.write("@    s%i line type %s\n" % (i, linetype[i]))

        # Line colours (default to nothing).
        if set_colours:
            file.write("@    s%i line color %s\n" % (i, set_colours[i]))

        # Legend.
        if set_names and set_names[i]:
            file.write("@    s%i legend \"%s\"\n" % (i, set_names[i]))
