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

# Python module imports.
from math import pi
from lib.physical_constants import return_gyromagnetic_ratio


H_frq = 900.21422558574e6
print("The magnetic field strength as the proton frequency in MegaHertz: %3.2f" % (H_frq / 1.E6) )

xOBS_Hz = H_frq
B0_tesla =  xOBS_Hz / return_gyromagnetic_ratio(nucleus='1H') * 2.0 * pi
print("BO in Tesla: %3.2f" % B0_tesla)

yOBS_N15_Hz = abs( xOBS_Hz / return_gyromagnetic_ratio(nucleus='1H') *
return_gyromagnetic_ratio(nucleus='15N') )
print("The precess frequency for 15N in MHz: %3.2f" % (yOBS_N15_Hz / 1.E6) )

offset_Hz = 6500.

offset_ppm_N15 = offset_Hz / yOBS_N15_Hz * 1E6
print("The offset ppm: %3.2f" % (offset_ppm_N15) )

# Position of carrier.
yCAR_N15_ppm = 118.00
print("The center position of the carrier: %3.2f" % (yCAR_N15_ppm) )

print ("The offset in Hz: %3.2f" % (offset_Hz))
omega_rf_ppm = yCAR_N15_ppm + offset_ppm_N15
print("The omega_rf in ppm: %3.2f" % (omega_rf_ppm) )
