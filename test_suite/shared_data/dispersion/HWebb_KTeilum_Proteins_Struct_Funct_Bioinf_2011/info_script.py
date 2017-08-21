###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

from numpy import array
DIC_KEY_FORMAT = "%.8f"

# Setup dictionary with settings.
sdic = {}

# Spectrometer frqs in list.
sfrq_1 = 750.2171495
sfrqs = [sfrq_1]

# Store in dictionary.
sdic['sfrqs'] = sfrqs

# Store unit for frq.
sdic['sfrq_unit'] = 'MHz'

# Store exp_type
sdic['exp_type'] = 'SQ CPMG'

# Store spin isotope
sdic['isotope'] = '15N'

# How intensity was measured.
sdic['int_method'] = 'height'

# Initialize frq dics.
for frq in sfrqs:
    key = DIC_KEY_FORMAT % (frq)
    sdic[key] = {}

# Set keys.
e_1 = DIC_KEY_FORMAT % (sfrq_1)

# Store time T2.
sdic[e_1]['time_T2'] = 0.06

# Set ncyc.
ncyc_1 = array([0, 8, 10, 20, 2, 60, 40, 12, 6, 14, 4, 24, 18, 28, 16, 32, 48, 56, 0])

# Calculate the cpmg_frq and store.
sdic[e_1]['cpmg_frqs'] = ncyc_1 / sdic[e_1]['time_T2']

for i, sfrq in enumerate(sfrqs):
    key = DIC_KEY_FORMAT % (sfrq)

    # Loop over cpmg_frqs.
    cpmg_frqs = sdic[key]['cpmg_frqs']

    for j, cpmg_frq in enumerate(cpmg_frqs):
        # Set the relaxation dispersion CPMG frequencies.
        if cpmg_frq == 0.0:
           cpmg_frq = None

        # Relaxation dispersion CPMG constant time delay T (in s).
        time_T2 = sdic[key]['time_T2']

        print(cpmg_frq, time_T2)
