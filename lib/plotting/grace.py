###############################################################################
#                                                                             #
# Copyright (C) 2001-2005,2007-2010,2012-2015,2017 Edward d'Auvergne          #
# Copyright (C) 2008 Sebastien Morin                                          #
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

# Python module imports.
from math import ceil, sqrt
from os import chmod
from os.path import expanduser
from stat import S_IRWXU, S_IRGRP, S_IROTH

# relax module imports.
from lib.errors import RelaxError
from lib.io import get_file_path, open_write_file


# This script is used to batch convert the Grace *.agr files into graphics files using the Grace
# program itself.
GRACE2IMAGES = """\
#!/usr/bin/env python3

###############################################################################
#                                                                             #
# Copyright (C) 2013 Troels E. Linnet                                         #
# Copyright (C) 2013,2017 Edward d'Auvergne                                   #
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

# Script docstring.
\"\"\"Scripted conversion of Grace *.agr graphs into vector or bitmap graphics files.

This script is used to batch convert the Grace *.agr files into graphics bitmap files using the Grace program itself.  Therefore you will need to install grace on your system using one of the programs:
    Xmgrace - http://plasma-gate.weizmann.ac.il/Grace/,
    qtgrace - http://sourceforge.net/projects/qtgrace/,
    gracegtk - http://sourceforge.net/projects/gracegtk/.
\"\"\"

# Python module imports.
from argparse import Action, ArgumentParser
import sys
from os import getcwd, listdir, path
import shlex, subprocess


# Define a callback class for handling the multiple input of PNG, EPS, SVG, etc.
class SplitFormats(Action):
     def __call__(self, parser, namespace, values, option_string=None):
         setattr(namespace, self.dest, values.split(','))


# Add script argument parsing.
parser = ArgumentParser(description="Scripted conversion of Grace *.agr graphs into vector or bitmap graphics files.")

# Add the script arguments.
parser.add_argument('types', action=SplitFormats, nargs='?', default='EPS', help="The different image types to convert to.  E.g. execute script with: %s -t JPG,EPS,SVG,PNG ..." % (sys.argv[0]))
parser.add_argument('-g', action='store_true', dest='relax_gui', default=False, help="Allow the script to be run through the relax GUI via the 'User-functions -> script' submenu, by only allowing for PNG conversions.")

# Parse the arguments.
args = parser.parse_args()

# If we run through the GUI we cannot pass input arguments so we fall back to EPS-only conversion.
if args.relax_gui:
    args.types = ['EPS']

# For PNG conversion, several parameters can be passed to xmgrace.  These can be altered later and the script rerun.
# The option for transparency is good for poster or insertion in color backgrounds.  This ability depends on the Grace compilation.
if "PNG" in args.types:
    pngpar = "png.par"
    if not path.isfile(pngpar):
        wpngpar = open(pngpar, "w")
        wpngpar.write("DEVICE \\\"PNG\\\" FONT ANTIALIASING on\\n")
        wpngpar.write("DEVICE \\\"PNG\\\" OP \\\"transparent:off\\\"\\n")
        wpngpar.write("DEVICE \\\"PNG\\\" OP \\\"compression:9\\\"\\n")
        wpngpar.close()

# Convert the different possible graphics type options into Grace format.
types = []
text = []
ext = []
param = []
for type in args.types:
    # PNG bitmap graphics.
    if type in ["PNG", ".PNG", "png", ".png"]:
        types.append("PNG")
        text.append("portable network graphics (PNG)")
        ext.append("png")
        param.append(pngpar)

    # Encapsulated postscript vector graphics.
    elif type in ["EPS", ".EPS", "eps", ".eps"]:
        types.append("EPS")
        text.append("encapsulated postscript (EPS)")
        ext.append("eps")
        param.append(None)

    # JPG bitmap graphics.
    elif type in ["JPG", ".JPG", "jpg", ".jpg", "JPEG", ".JPEG", "jpeg", ".jpeg"]:
        types.append("JPEG")
        text.append("JPEG")
        ext.append("jpg")
        param.append(None)

    # Scalable vector graphics.
    elif type in ["SVG", ".SVG", "svg", ".svg"]:
        types.append("SVG")
        text.append("scalable vector graphics (SVG)")
        ext.append("svg")
        param.append(None)

    # Unknown graphic.
    else:
        print("Unknown graphic type '%s', skipping the format." % type)
        continue

# Loop over all files in the current directory.
for filename in listdir(getcwd()):
    # Skip non-Grace files.
    if not filename.endswith(".agr"):
        continue

    # Get the filename without extension.
    basename = path.splitext(filename)[0]

    # Loop over each output format.
    for i in range(len(types)):
        im_args = r"xmgrace -hdevice %s -hardcopy" % types[i]
        if param[i]:
            im_args += r" -param %s" % param[i]
        im_args += r" -printfile %s.%s %s" % (basename, ext[i], filename)

        # Split the arguments the right way to call xmgrace.
        im_args = shlex.split(im_args)

        # Generate the graphic.
        print("Converting '%s' into a %s graphic." % (filename, text[i]))
        return_code = subprocess.call(im_args)
"""


def create_grace2images(dir=None):
    """Create the grace2images.py executable script.

    @keyword dir:   The directory to place the script into.
    @type dir:      str
    """

    # Expand any ~ characters.
    dir = expanduser(dir)

    # Open the file.
    print("\nCreating the Python \"grace to PNG/EPS/SVG...\" conversion script.")
    file_name = "grace2images.py"
    file_path = get_file_path(file_name=file_name, dir=dir)
    file = open_write_file(file_name=file_name, dir=dir, force=True)

    # Write the Python "grace to PNG/EPS/SVG..." conversion script.
    script_grace2images(file=file)

    # Close the batch script, then make it executable (expanding any ~ characters).
    file.close()
    chmod(file_path, S_IRWXU|S_IRGRP|S_IROTH)


def script_grace2images(file=None):
    """Write a python "grace to PNG/EPS/SVG..." conversion script..

    The makes a conversion script to image types as PNG/EPS/SVG. The conversion is looping over a directory list of *.agr files, and making function calls to xmgrace. Successful conversion of images depends on the compilation of xmgrace. The input is a list of image types which is wanted, f.ex: PNG EPS SVG. PNG is default.

    @keyword file:          The file object to write the data to.
    @type file:             file object
    """

    # Write to file
    file.write(GRACE2IMAGES)


def write_xy_data(data, file=None, graph_type=None, norm_type='first', norm=None, autoscale=True):
    """Write the data into the Grace xy-scatter plot.

    The numerical data should be supplied as a 4 dimensional list or array object.  The first dimension corresponds to the graphs, Gx.  The second corresponds the sets of each graph, Sx.  The third corresponds to the data series (i.e. each data point).  The forth is a list of the information about each point, it is a list where the first element is the x value, the second is the y value, the third is the optional dx or dy error (either dx or dy dependent upon the graph_type arg), and the forth is the optional dy error when graph_type is xydxdy (the third position is then dx).


    @param data:            The 4D structure of numerical data to graph (see docstring).
    @type data:             list of lists of lists of float
    @keyword file:          The file object to write the data to.
    @type file:             file object
    @keyword graph_type:    The graph type which can be one of xy, xydy, xydx, or xydxdy.
    @type graph_type:       str
    @keyword norm_type:     The point to normalise to 1.  This can be 'first' or 'last'.
    @type norm_type:        str
    @keyword norm:          The normalisation flag which if set to True will cause all graphs to be normalised to 1.  The first dimension is the graph.
    @type norm:             None or list of bool
    @keyword autoscale:     A flag which if True will cause the world view of each graph to be autoscaled (by placing the Grace command "@autoscale" at the end of the file).  If you have supplied a world view for the header or the tick spacing, this argument should be set to False to prevent that world view from being overwritten.
    @type autoscale:        bool
    """

    # Graph number.
    graph_num = len(data)

    # Defaults.
    if not norm:
        norm = []
        for gi in range(graph_num):
            norm.append(False)

    # Comment columns.
    comment_col = 2
    if graph_type in ['xydx', 'xydy']:
        comment_col = 3
    elif graph_type == 'xydxdy':
        comment_col = 4

    # Loop over the graphs.
    for gi in range(graph_num):
        # Loop over the data sets of the graph.
        for si in range(len(data[gi])):
            # The target and type.
            file.write("@target G%s.S%s\n" % (gi, si))
            file.write("@type %s\n" % graph_type)

            # Catch missing data sets.
            if len(data[gi][si]) == 0:
                file.write("&\n")
                continue

            # Normalisation (to the first data point y value!).
            norm_fact = 1.0
            if norm[gi]:
                if norm_type == 'first':
                    norm_fact = data[gi][si][0][1]
                elif norm_type == 'last':
                    norm_fact = data[gi][si][-1][1]
                else:
                    raise RelaxError("The normalisation type '%s' must be one of ['first', 'last']." % norm_fact)

            # Loop over the data points.
            for point in data[gi][si]:
                # Bad data.
                if point[0] == None or point[1] == None:
                    continue

                # X and Y data.
                file.write("%30.15f %30.15f" % (point[0], point[1]/norm_fact))

                # The dx and dy errors.
                if graph_type in ['xydx', 'xydy', 'xydxdy']:
                    # Catch if graph is a mix with and without error.
                    if len(point) < 3:
                        error = None
                    else:
                        error = point[2]
                    # Catch x or y-axis errors of None.
                    if error == None:
                        error = 0.0

                    # Write the error.
                    file.write(" %30.15f" % (error/norm_fact))

                # The dy errors of xydxdy.
                if graph_type == 'xydxdy':
                    # Catch y-axis errors of None.
                    error = point[3]
                    if error == None:
                        error = 0.0

                    # Write the error.
                    file.write(" %30.15f" % (error/norm_fact))

                # The comment if given.
                try:
                    file.write("    \"%s\"" % point[comment_col])
                except IndexError:
                    pass

                # End the point.
                file.write("\n")

            # End of the data set i.
            file.write("&\n")

    # Autoscaling of all graphs to avoid user confusion.
    if autoscale:
        for i in range(graph_num):
            file.write("@with g%i\n" % i)
            file.write("@autoscale\n")

    # Auto-arrange the graphs if multiple are present.
    if len(data) > 1:
        row_num = int(round(sqrt(len(data))))
        col_num = int(ceil(sqrt(len(data))))
        file.write("@arrange(%i, %i, .1, .1, .1, OFF, OFF, OFF)\n" % (row_num, col_num))


def write_xy_header(file=None, paper_size='A4', title=None, subtitle=None, world=None, view=None, graph_num=1, sets=None, set_names=None, set_colours=None, x_axis_type_zero=None, y_axis_type_zero=None, symbols=None, symbol_sizes=None, symbol_fill=None, linestyle=None, linetype=None, linewidth=None, data_type=None, seq_type=None, axis_labels=None, tick_major_spacing=None, tick_minor_count=None, legend=None, legend_pos=None, legend_box_fill_pattern=None, legend_char_size=None, norm=None):
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
    @keyword world:                     The Grace plot default zoom.  This consists of a list of the X-axis minimum, Y-axis minimum, X-axis maximum, and Y-axis maximum values.  Each graph should supply its own world view.
    @type world:                        Nor or list of list of numbers
    @keyword view:                      List of 4 coordinates defining the graph view port.
    @type view:                         None or list of float
    @keyword graph_num:                 The total number of graphs.
    @type graph_num:                    int
    @keyword sets:                      The number of data sets in each graph.
    @type sets:                         list of int
    @keyword set_names:                 The names associated with each graph data set Gx.Sy.  For example this can be a list of spin identification strings.  The first dimension is the graph, the second is the set.
    @type set_names:                    None or list of list of str
    @keyword set_colours:               The colours for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type set_colours:                  None or list of list of int
    @keyword x_axis_type_zero:          The flags specifying if the X-axis should be placed at zero.
    @type x_axis_type_zero:             None or list of lists of bool
    @keyword y_axis_type_zero:          The flags specifying if the Y-axis should be placed at zero.
    @type y_axis_type_zero:             None or list of lists of bool
    @keyword symbols:                   The symbol style for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type symbols:                      None or list of list of int
    @keyword symbol_sizes:              The symbol size for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type symbol_sizes:                 None or list of list of int
    @keyword symbol_fill:               The symbol file style for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type symbol_fill:                  None or list of list of int
    @keyword linestyle:                 The line style for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type linestyle:                    None or list of list of int
    @keyword linetype:                  The line type for each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
    @type linetype:                     None or list of list of int
    @keyword linewidth:                 The line width for all elements of each graph data set Gx.Sy.  The first dimension is the graph, the second is the set.
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

    # Defaults.
    if sets == None:
        sets = []
        for gi in range(graph_num):
            sets.append(1)
    if x_axis_type_zero == None:
        x_axis_type_zero = []
        for gi in range(graph_num):
            x_axis_type_zero.append(False)
    if y_axis_type_zero == None:
        y_axis_type_zero = []
        for gi in range(graph_num):
            y_axis_type_zero.append(False)
    if linewidth == None:
        linewidth = []
        for gi in range(graph_num):
            linewidth.append(0.5)
    if norm == None:
        norm = []
        for gi in range(graph_num):
            norm.append(False)
    if legend == None:
        legend = []
        for gi in range(graph_num):
            legend.append(True)
    if not legend_box_fill_pattern:
        legend_box_fill_pattern = []
        for gi in range(graph_num):
            legend_box_fill_pattern.append(1)
    if not legend_char_size:
        legend_char_size = []
        for gi in range(graph_num):
            legend_char_size.append(1.0)

    # Set the None args to lists as needed.
    if not data_type:
        data_type = [None, None]
    if not seq_type:
        seq_type = [None, None]
    if not axis_labels:
        axis_labels = []
        for gi in range(graph_num):
            axis_labels.append([None, None])

    # Set the Grace version number of the header's formatting for compatibility.
    file.write("@version 50121\n")

    # The paper size.
    if paper_size == 'A4':
        file.write("@page size 842, 595\n")

    # Loop over each graph.
    for gi in range(graph_num):
        # Graph Gi.
        file.write("@with g%i\n" % gi)

        # The world view.
        if world:
            file.write("@    world %s, %s, %s, %s\n" % (world[gi][0], world[gi][1], world[gi][2], world[gi][3]))

        # The view port.
        if not view:
            view = [0.15, 0.15, 1.28, 0.85]
        file.write("@    view %s, %s, %s, %s\n" % (view[0], view[1], view[2], view[3]))

        # The title and subtitle.
        if title:
            file.write("@    title \"%s\"\n" % title)
        if subtitle:
            file.write("@    subtitle \"%s\"\n" % subtitle)

        # Axis at zero.
        if x_axis_type_zero[gi]:
            file.write("@    xaxis  type zero true\n")
        if y_axis_type_zero[gi]:
            file.write("@    yaxis  type zero true\n")

        # Axis specific settings.
        axes = ['x', 'y']
        for i in range(2):
            # Some axis default values for spin data.
            if data_type[i] == 'spin':
                # Residue only data.
                if seq_type[i] == 'res':
                    # X-axis label.
                    if not axis_labels[gi][i]:
                        axis_labels[gi][i] = "Residue number"

                # Spin only data.
                if seq_type[i] == 'spin':
                    # X-axis label.
                    if not axis_labels[gi][i]:
                        axis_labels[gi][i] = "Spin number"

                # Mixed data.
                if seq_type[i] == 'mixed':
                    # X-axis label.
                    if not axis_labels[gi][i]:
                        axis_labels[gi][i] = "Spin ID string"

            # Write out the data.
            if axis_labels[gi][i]:
                file.write("@    %saxis  label \"%s\"\n" % (axes[i], axis_labels[gi][i]))
            file.write("@    %saxis  label char size 1.00\n" % axes[i])
            if tick_major_spacing != None:
                file.write("@    %saxis  tick major %s\n" % (axes[i], tick_major_spacing[gi][i]))
            file.write("@    %saxis  tick major size 0.50\n" % axes[i])
            file.write("@    %saxis  tick major linewidth %s\n" % (axes[i], linewidth[gi]))
            if tick_minor_count != None:
                file.write("@    %saxis  tick minor ticks %s\n" % (axes[i], tick_minor_count[gi][i]))
            file.write("@    %saxis  tick minor linewidth %s\n" % (axes[i], linewidth[gi]))
            file.write("@    %saxis  tick minor size 0.25\n" % axes[i])
            file.write("@    %saxis  ticklabel char size 0.70\n" % axes[i])

        # Legend box.
        if legend != None and legend[gi]:
            file.write("@    legend on\n")
        else:
            file.write("@    legend off\n")
        if legend_pos != None:
            file.write("@    legend %s, %s\n" % (legend_pos[gi][0], legend_pos[gi][1]))
        file.write("@    legend box fill pattern %s\n" % legend_box_fill_pattern[gi])
        file.write("@    legend char size %s\n" % legend_char_size[gi])

        # Frame.
        file.write("@    frame linewidth %s\n" % linewidth[gi])

        # Loop over each graph set.
        for i in range(sets[gi]):
            # Symbol style (default to all different symbols).
            if symbols:
                file.write("@    s%i symbol %i\n" % (i, symbols[gi][i]))
            else:
                # The symbol number (cycle between 1 and 10).
                num = i % 10 + 1

                # Write out.
                file.write("@    s%i symbol %i\n" % (i, num))

            # Symbol sizes (default to a small size).
            if symbol_sizes:
                file.write("@    s%i symbol size %s\n" % (i, symbol_sizes[gi][i]))
            else:
                file.write("@    s%i symbol size 0.45\n" % i)

            # The symbol fill.
            if symbol_fill:
                file.write("@    s%i symbol fill pattern %i\n" % (i, symbol_fill[gi][i]))

            # The symbol line width.
            file.write("@    s%i symbol linewidth %s\n" % (i, linewidth[gi]))

            # Symbol colour (default to nothing).
            if set_colours:
                file.write("@    s%i symbol color %s\n" % (i, set_colours[gi][i]))
                file.write("@    s%i symbol fill color %s\n" % (i, set_colours[gi][i]))

            # Error bars.
            file.write("@    s%i errorbar size 0.5\n" % i)
            file.write("@    s%i errorbar linewidth %s\n" % (i, linewidth[gi]))
            file.write("@    s%i errorbar riser linewidth %s\n" % (i, linewidth[gi]))

            # Line linestyle (default to nothing).
            if linestyle:
                file.write("@    s%i line linestyle %s\n" % (i, linestyle[gi][i]))

            # Line linetype (default to nothing).
            if linetype:
                file.write("@    s%i line type %s\n" % (i, linetype[gi][i]))

            # Line and all other colours (default to nothing).
            if set_colours:
                file.write("@    s%i line color %s\n" % (i, set_colours[gi][i]))
                file.write("@    s%i fill color %s\n" % (i, set_colours[gi][i]))
                file.write("@    s%i avalue color %s\n" % (i, set_colours[gi][i]))
                file.write("@    s%i errorbar color %s\n" % (i, set_colours[gi][i]))

            # Legend.
            if set_names and len(set_names) and len(set_names[gi]) and set_names[gi][i]:
                file.write("@    s%i legend \"%s\"\n" % (i, set_names[gi][i]))
