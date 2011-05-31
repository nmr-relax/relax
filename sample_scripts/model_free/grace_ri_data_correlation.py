###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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

"""Script for creating correlations plots of experimental verses back calculated relaxation data."""


# relax module imports.
from generic_fns.mol_res_spin import spin_loop
from generic_fns.relax_data import num_frq


def grace_header(file):
    """Generate the Grace header text."""

    # A4, portrait.
    file.write("@page size 595, 842\n")

    # Graph data.
    world = ["0, 0, 400, 3", "0, 0, 400, 20", "0, 0, 400, 1"]
    view = ["@    view 0.100000, 0.876456, 0.950000, 1.264685", "@    view 0.100000, 0.488228, 0.950000, 0.876456", "@    view 0.100000, 0.100000, 0.950000, 0.488228"]
    x_label = ["", "", "Residue number"]
    x_ticklabel = ["off", "off", "on"]
    y_label = ["R\s1\N (rad.s\S-1\N)", "R\s2\N (rad.s\S-1\N)", "Steady-state NOE"]
    legend = ["on", "off", "off"]

    # The data labels.
    data_legend = [[], [], []]
    for ri_id in cdp.ri_ids:
        # The graph numbers.
        if cdp.ri_type[ri_id] == 'R1':
            g_index = 0
        elif cdp.ri_type[ri_id] == 'R2':
            g_index = 1
        elif cdp.ri_type[ri_id] == 'NOE':
            g_index = 2

        # Frequency string.
        string = '%i MHz' % (cdp.frq[ri_id]/1e6)

        # The label.
        data_legend[g_index].append("%s Exp. data" % string)
        data_legend[g_index].append("%s BC. data" % string)

    # Loop over the graphs.
    for i in range(3):
        # Show all graphs.
        file.write("@g%s hidden false\n" % i)

        # Specific graph.
        file.write("@with g%s\n" % i)

        # World.
        file.write("@    world %s\n" % world[i])

        # Arrange graphs.
        file.write("%s\n" % view[i])

        # X-axis setting.
        file.write("@    xaxis  bar linewidth 0.5\n")
        file.write("@    xaxis  tick major 50\n")
        file.write("@    xaxis  tick minor ticks 4\n")
        file.write("@    xaxis  tick major size 0.5\n")
        file.write("@    xaxis  tick major linewidth 0.5\n")
        file.write("@    xaxis  tick minor linewidth 0.5\n")
        file.write("@    xaxis  tick minor size 0.250000\n")
        file.write("@    xaxis  ticklabel %s\n" % x_ticklabel[i])
        file.write("@    xaxis  ticklabel char size 0.74\n")
        file.write("@    xaxis  label \"%s\"\n" % x_label[i])

        # Y-axis setting.
        file.write("@    yaxis  bar linewidth 0.5\n")
        file.write("@    yaxis  tick major size 0.5\n")
        file.write("@    yaxis  tick major linewidth 0.5\n")
        file.write("@    yaxis  tick minor linewidth 0.5\n")
        file.write("@    yaxis  tick minor size 0.250000\n")
        file.write("@    yaxis  ticklabel char size 0.74\n")
        file.write("@    yaxis  label \"%s\"\n" % y_label[i])

        # Legend and frame.
        file.write("@    legend %s\n" % legend[i])
        file.write("@    legend 0.3, 0.8\n")
        file.write("@    legend box linewidth 0.5\n")
        file.write("@    legend char size 0.76\n")
        file.write("@    frame linewidth 0.5\n")

        # Data set settings.
        for j in range(len(data_legend[i])):
            # Changing values.
            colour = j/2 + 1
            linestyle = j%2
            if j%2:
                symbol = 9
            else:
                symbol = 2

            # Symbol info.
            file.write("@    s%s symbol %s\n" % (j, symbol))
            file.write("@    s%s symbol size 0.25\n" % j)
            file.write("@    s%s symbol color %s\n" % (j, colour))
            file.write("@    s%s symbol fill color %s\n" % (j, colour))
            file.write("@    s%s symbol fill pattern 0\n" % j)
            file.write("@    s%s symbol linewidth 0.5\n" % j)

            # Line info.
            file.write("@    s%s line linestyle %s\n" % (j, linestyle))
            file.write("@    s%s line linewidth 0.5\n" % j)
            file.write("@    s%s line color %s\n" % (j, colour))
            file.write("@    s%s errorbar color %s\n" % (j, colour))

            # Error bars.
            file.write("@    s%s errorbar size 0.25\n" % j)
            file.write("@    s%s errorbar linewidth 0.5\n" % j)
            file.write("@    s%s errorbar riser linestyle 2\n" % j)
            file.write("@    s%s errorbar riser linewidth 0.5\n" % j)
            file.write("@    s%s legend \"%s\"\n" % (j, data_legend[i][j]))


# Load the relax state.
state.load('results', dir='.')

# Back calculate the relaxation data.
relax_data.back_calc()

# Open the correlation plot file.
file = open('corr_plot.agr', 'w')

# Generate the header.
grace_header(file)

# Init.
s_count = [0, 0, 0]

# Loop over the relaxation data.
for ri_id in cdp.ri_ids:
    # The graph numbers.
    if cdp.ri_type[ri_id] == 'R1':
        g_index = 0
    elif cdp.ri_type[ri_id] == 'R2':
        g_index = 1
    elif cdp.ri_type[ri_id] == 'NOE':
        g_index = 2

    # The experimental data.
    file.write('@target G%s.S%s\n@type xydy\n' % (g_index, s_count[g_index]))
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        file.write('%s %s %s\n' % (res_num, spin.ri_data[ri_id], spin.ri_data_err[ri_id]))
    file.write('&\n')

    # Increment the set counter.
    s_count[g_index] += 1

    # The back-calculated data.
    file.write('@target G%s.S%s\n@type xy\n' % (g_index, s_count[g_index]))
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        file.write('%s %s\n' % (res_num, spin.ri_data_bc[ri_id]))
    file.write('&\n')

    # Increment the set counter.
    s_count[g_index] += 1
