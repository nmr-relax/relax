###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


from re import match


class Grace:
    def __init__(self, relax):
        """Operations, functions, etc common to the different model-free analysis methods."""

        self.relax = relax


    def grace(self, file_name, type, subtitle):
        """Create grace files for the results."""

        file = open(file_name, 'w')

        if match('Chi2', type):
            file.write(self.grace_header(type + ' values', subtitle, 'Residue Number', type, 'xy'))
        else:
            file.write(self.grace_header(type + ' values', subtitle, 'Residue Number', type, 'xydy'))

        for res in range(len(self.relax.data.results)):
            if match('S2', type) and self.relax.data.results[res]['s2']:
                file.write(self.relax.data.results[res]['res_num'] + " ")
                file.write(`self.relax.data.results[res]['s2']` + " ")
                file.write(`self.relax.data.results[res]['s2_err']` + "\n")
            elif match('S2s', type) and self.relax.data.results[res]['s2s']:
                file.write(self.relax.data.results[res]['res_num'] + " ")
                file.write(`self.relax.data.results[res]['s2s']` + " ")
                file.write(`self.relax.data.results[res]['s2s_err']` + "\n")
            elif match('S2f', type) and self.relax.data.results[res]['s2f']:
                file.write(self.relax.data.results[res]['res_num'] + " ")
                file.write(`self.relax.data.results[res]['s2f']` + " ")
                file.write(`self.relax.data.results[res]['s2f_err']` + "\n")
            elif match('te', type) and self.relax.data.results[res]['te']:
                file.write(self.relax.data.results[res]['res_num'] + " ")
                file.write(`self.relax.data.results[res]['te']` + " ")
                file.write(`self.relax.data.results[res]['te_err']` + "\n")
            elif match('Rex', type) and self.relax.data.results[res]['rex']:
                file.write(self.relax.data.results[res]['res_num'] + " ")
                file.write(`self.relax.data.results[res]['rex']` + " ")
                file.write(`self.relax.data.results[res]['rex_err']` + "\n")
            elif match('Chi2', type) and self.relax.data.results[res]['chi2']:
                file.write(self.relax.data.results[res]['res_num'] + " ")
                file.write(`self.relax.data.results[res]['chi2']` + "\n")
        file.write("&\n")
        file.close()


    def grace_header(self, title, subtitle, x, y, type):
        """Create and return a grace header."""

        text = "@version 50100\n"
        text = text + "@with g0\n"
        if match('Residue Number', x):
            text = text + "@    world xmax 165\n"
        if match('R1', x) and match('Chi2', y):
            text = text + "@    world xmin 0.8\n"
            text = text + "@    world xmax 2\n"
            text = text + "@    world ymin 0\n"
            text = text + "@    world ymax 2000\n"
        if match('R2', x) and match('Chi2', y):
            text = text + "@    world xmin 5\n"
            text = text + "@    world xmax 45\n"
            text = text + "@    world ymin 0\n"
            text = text + "@    world ymax 2000\n"
        if match('NOE', x) and match('Chi2', y):
            text = text + "@    world xmin 0\n"
            text = text + "@    world xmax 1\n"
            text = text + "@    world ymin 0\n"
            text = text + "@    world ymax 2000\n"
        text = text + "@    view xmax 1.22\n"
        text = text + "@    title \"" + title + "\"\n"
        text = text + "@    subtitle \"" + subtitle + "\"\n"
        text = text + "@    xaxis  label \"" + x + "\"\n"
        if match('Residue Number', x):
            text = text + "@    xaxis  tick major 10\n"
        if match('R1', x) and match('Chi2', y):
            text = text + "@    xaxis  tick major 0.2\n"
        if match('R2', x) and match('Chi2', y):
            text = text + "@    xaxis  tick major 5\n"
        if match('NOE', x) and match('Chi2', y):
            text = text + "@    xaxis  tick major 0.1\n"
        text = text + "@    xaxis  tick major size 0.480000\n"
        text = text + "@    xaxis  tick major linewidth 0.5\n"
        text = text + "@    xaxis  tick minor linewidth 0.5\n"
        text = text + "@    xaxis  tick minor size 0.240000\n"
        text = text + "@    xaxis  ticklabel char size 0.790000\n"
        text = text + "@    yaxis  label \"" + y + "\"\n"
        if match('R1', x) and match('Chi2', y):
            text = text + "@    yaxis  tick major 200\n"
        if match('R2', x) and match('Chi2', y):
            text = text + "@    yaxis  tick major 200\n"
        if match('NOE', x) and match('Chi2', y):
            text = text + "@    yaxis  tick major 200\n"
        text = text + "@    yaxis  tick major size 0.480000\n"
        text = text + "@    yaxis  tick major linewidth 0.5\n"
        text = text + "@    yaxis  tick minor linewidth 0.5\n"
        text = text + "@    yaxis  tick minor size 0.240000\n"
        text = text + "@    yaxis  ticklabel char size 0.790000\n"
        text = text + "@    frame linewidth 0.5\n"
        text = text + "@    s0 symbol 1\n"
        text = text + "@    s0 symbol size 0.49\n"
        text = text + "@    s0 symbol fill pattern 1\n"
        text = text + "@    s0 symbol linewidth 0.5\n"
        text = text + "@    s0 line linestyle 0\n"
        text = text + "@target G0.S0\n@type " + type + "\n"
        return text
