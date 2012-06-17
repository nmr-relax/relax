#!/usr/bin/python

# Python module imports.
from math import pi

# Imports.
from VectorFieldPlot import FieldplotDocument, Field, FieldLine


# The plot setup.
plot_range = 20
inc = 50
pt_spacing = plot_range / float(inc)

# Debugging flag.
debug = False

# Generate the document.
size = 1000
doc = FieldplotDocument('NH_dipole_pair', width=size, height=size, unit=size/plot_range, commons=False)

# The B0 magnetic field.
B0 = [0.0, 0.1]

# The N and H dipoles.
n = [-1, -3, 0, -2.7126]
h = [1, 2, 0, 26.7522212]

# Create the field.
#field = Field({'homogeneous': [B0]})
field = Field({'homogeneous': [B0], 'dipoles':[n, h]})

## Grid.
#if debug:
#    grid_inc = 20
#    for i in range(grid_inc+1):
#        for j in range(grid_inc+1):
#            pos_x = (i - (grid_inc)/2.0) / grid_inc * plot_range
#            pos_y = (j - (grid_inc)/2.0) / grid_inc * plot_range
#            doc.draw_object('circle', {'cx': pos_x, 'cy': pos_y, 'r': 0.05})

# The styles.
linecolor = '#0017aa'
arrows_style = {'dist': 0.2, 'min_arrows': 1, 'max_arrows': 5, 'scale': 1}

# The background field lines.
pos_y = -7
for i in range(inc+1):
    # The points along x.
    pos_x = (i - (inc)/2.0) / inc * plot_range

    # Create the field line.
    line = FieldLine(field, [pos_x, pos_y], maxr=1000, directions='both', pass_dipoles=1)

    # Draw the line.
    doc.draw_line(line, linecolor=linecolor, arrows_style=arrows_style, linewidth=1)

    # Debugging dots.
    if debug:
        doc.draw_object('circle', {'cx': pos_x, 'cy': pos_y, 'r': 0.05})

# Internal 15N field lines (from -1 +/- 1.5).
n_range = 3
n_inc = int(n_range / pt_spacing)
pos_y = n[1]
for i in range(n_inc+1):
    # The points along x.
    pos_x = (i - (n_inc)/2.0) / inc * plot_range + n[0]

    # Create the field line.
    line = FieldLine(field, [pos_x, pos_y], maxr=1000, directions='both', pass_dipoles=0)

    # Draw the line.
    doc.draw_line(line, linecolor=linecolor, arrows_style=arrows_style, linewidth=1)

    # Debugging dots.
    if debug:
        doc.draw_object('circle', {'cx': pos_x, 'cy': pos_y, 'r': 0.05})

# Internal 1H field lines (from 1 +/- 3.5).
h_range = 7
h_inc = int(h_range / pt_spacing)
pos_y = h[1]
for i in range(h_inc+1):
    # The points along x.
    pos_x = (i - (h_inc)/2.0) / inc * plot_range + h[0]

    # Create the field line.
    line = FieldLine(field, [pos_x, pos_y], maxr=1000, directions='both', pass_dipoles=0)

    # Draw the line.
    doc.draw_line(line, linecolor=linecolor, arrows_style=arrows_style, linewidth=1)

    # Debugging dots.
    if debug:
        doc.draw_object('circle', {'cx': pos_x, 'cy': pos_y, 'r': 0.05})

# Draw dots at the atom positions.
#doc.draw_object('circle', {'cx': n[0], 'cy': n[1], 'r': 0.1})
#doc.draw_object('circle', {'cx': h[0], 'cy': h[1], 'r': 0.1})

# Create the SVG file.
doc.write()
