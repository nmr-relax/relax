###############################################################################
#                                                                             #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
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

"""Script for generating Molmol macros for highlighting model-free motions.

Note that the most important macros are:
    'amp_fast' - The order parameters for fast motions (< 200 ps).
    'amp_slow' - The order parameters for slow motions (> 200 ps).
    'time_fast' - The correlation time for fast motions (< 200 ps).
    'time_slow' - The correlation time for slow motions (> 200 ps).
    'Rex' - Chemical exchange relaxation.

These are more important than 'S2', 'S2f', 'S2s', 'te', 'tf', and 'ts' as they are model independent
reporters of the motions of the molecule.  Note that which model is selected is not important,
rather the motions that that model represents is of interest.  A standard concept in mathematical
modelling is that simpler models can approximate more complex ones.  But this does not mean that the
more complex motion is not present, just that it cannot be statistically differentiated from the
data being analysed.

Please read the documentation for the molmol.macro_write() user function before using this script.
"""

# Load the program state.
state.load(file='final_state', dir=None)

# Create the Molmol macros.
molmol.macro_write(data_type='s2', colour_start='red', colour_end='blue', force=True)
molmol.macro_write(data_type='s2f', force=True)
molmol.macro_write(data_type='s2s', force=True)
molmol.macro_write(data_type='amp_fast', colour_start='red', colour_end='blue', force=True)
molmol.macro_write(data_type='amp_slow', colour_start='red', colour_end='blue', force=True)
molmol.macro_write(data_type='te', force=True)
molmol.macro_write(data_type='tf', force=True)
molmol.macro_write(data_type='ts', force=True)
molmol.macro_write(data_type='time_fast', force=True)
molmol.macro_write(data_type='time_slow', force=True)
molmol.macro_write(data_type='rex', force=True)
