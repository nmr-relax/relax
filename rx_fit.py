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


# Relaxation curve fitting.

import sys

from common_ops import Common_ops


class Relax_fit(Common_ops):
    def __init__(self):
        """Relaxation curve fitting."""

        raise NameError, "End of code."


    def curvefit_input(self):
        # Loop through each time point.
        for spectra in range(len(self.usr_param.input_info)):
            print '\nProcessing data for time point ' + self.xmf.r1_data.input[i][0] + ' sec'
            for j in range(len(self.xmf.r1_data.input[i])):     # Go through the three columns of the input file.
                if j == 0:           # The time column.
                    self.xmf.r1_data.times.append(self.xmf.r1_data.input[i][0])     # Add the time to the 'times' array.
                    self.xmf.r1_data.input_data[i][0] = self.xmf.r1_data.input[i][0]
                    continue     # Go to the next column.
                file = self.xmf.r1_data.input[i][j]
                self.xmf.r1_data.input_data[i][j] = self.xmf.file_ops.extract_data(file)
                equal_size(len(self.xmf.r1_data.input_data[0][1]),len(self.xmf.r1_data.input_data[i][j]))     # Test if both are the same length.
                if j == 2:           # The duplicate spectra column.
                    diff_list = []     # List of peak intensity differences for backbone peaks.
                bb_no = 0            # Number of backbone peaks.
                indole_no = 0        # Number of tryptophane indole peaks.
                for k in range(len(self.xmf.r1_data.input_data[i][j])):     # Go through the lines of each spectra.
                    if non_residue(self.xmf.r1_data.input_data[i][j][k]):
                        continue     # Skip all non-residue lines.
                    test_res_no(self.xmf.r1_data.input_data[0][1][k][0],self.xmf.r1_data.input_data[i][j][k][0])     # Test if residue numbers match.
                    if backbone(self.xmf.r1_data.input_data[i][j][k][4]):     # Backbone peak.
                        if unresolved_peak(self.xmf.r1_data.input_data[i][j][k][5],'test/R1/unresolved'):
                            continue     # Skip unresolved peaks.
                        self.xmf.r1_data.bb_intense = create_2Dint(i, j, k, self.xmf.r1_data.input_data, self.xmf.r1_data.bb_intense, bb_no)
                        if j == 2:     # Duplicate spectra data set.
                            diff_val = float(self.xmf.r1_data.input_data[i][1][k][10]) - float(self.xmf.r1_data.input_data[i][2][k][10])
                            diff_list.append(diff_val)
                        bb_no = bb_no + 1
                    elif indole(self.xmf.r1_data.input_data[i][j][k][4]):     # Tryptophane indole peak.
                        if unresolved_peak(self.xmf.r1_data.input_data[i][j][k][5],'R1/indole_unresolved'):
                            continue     # Skip unresolved peaks.
                        self.xmf.r1_data.indole_intense = create_2Dint(i, j, k, self.xmf.r1_data.input_data, self.xmf.r1_data.indole_intense, indole_no)
                        indole_no = indole_no + 1
                if j == 2:
                    self.xmf.r1_data.diff.append(diff_list)
        self.xmf.r1_data.bb_intense.sort()
        self.xmf.r1_data.indole_intense.sort()
        sumSd = 0     # The sum of all the standard deviations.
        for set in range(len(self.xmf.r1_data.diff)):
            sd = stand_dev(self.xmf.r1_data.diff[set])
            print '\nThe standard deviation is: ' + `sd`
            sumSd = sumSd + sd
        aveSd = sumSd / len(self.xmf.r1_data.diff)
        print '\nThe average standard deviation is: ' + `aveSd`

        print '\nCreating grace files\n'
        self.xmf.grace.intensity('R1_backbone', self.xmf.r1_data.bb_intense, self.xmf.r1_data.times, aveSd)
        self.xmf.grace.intensity('R1_trp_indole', self.xmf.r1_data.indole_intense, self.xmf.r1_data.times, aveSd)
        rx_log('r1.log', self.xmf.r1_data.times, self.xmf.r1_data.bb_intense, self.xmf.r1_data.indole_intense, self.xmf.r1_data.diff, aveSd)

    def test_res_no(self, first_no, second_no):
        if first_no != second_no:
            text = 'Residues don\'t line up\n'
            print str(first_no) + ' != ' + str(second_no)
            while 1:
                pass
