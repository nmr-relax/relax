###############################################################################
#                                                                             #
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
"""Taken from the relax disp manual, section 10.6.1 Dispersion script mode - the sample script.

To run the script, simply type:

$ ../../../../../relax relax_1_ini.py --tee relax_1_ini.log
"""

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# Create the spins
script(file='relax_2_spins.py', dir=None)

# Name the isotope for field strength scaling.
spin.isotope(isotope='15N')

# Read the spectrum from NMRSeriesTab file. The "auto" will generate spectrum name of form: Z_A{i}
spectrum.read_intensities(file="peaks_list_max_standard.ser", dir=None, spectrum_id='auto', int_method='height')

# Set the spectra experimental properties/settings.
script(file='relax_3_spectra_settings.py', dir=None)

# Save the program state before run.
# This state file will also be used for loading, before a later cluster/global fit analysis.
state.save('ini_setup', force=True)
