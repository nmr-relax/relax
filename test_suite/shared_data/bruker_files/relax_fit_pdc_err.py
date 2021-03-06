###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""Script for relaxation curve fitting."""

# relax module imports.
from pipe_control.mol_res_spin import return_spin
from lib.io import extract_data


# Create the data pipe.
pipe.create('rx', 'relax_fit')

# Load the sequence.
sequence.read('seq', res_num_col=2, res_name_col=1)

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Spectrum names.
names = [        
    '0.01',
    '0.05',
    '0.10',
    '0.10b',
    '0.20',
    '0.30',
    '0.40',
    '0.50',
    '0.50b',
    '0.70',
    '1.00',
    '1.50'
]

# Relaxation times (in seconds).
times = [
    0.01000000,
    0.05000000,
    0.10000000,
    0.10000000,
    0.20000000,
    0.30000000,
    0.40000000,
    0.50000000,
    0.50000000,
    0.70000000,
    1.00000000,
    1.50000000
]

# The error file.
err_lines = extract_data('errors_R1.txt')

# Loop over the spectra.
for i in range(len(times)):
    # Load the peak intensities.
    spectrum.read_intensities(file='heights_R1.txt', spectrum_id=names[i], int_method='height', res_num_col=2, res_name_col=1, int_col=i+3)

    # Set the relaxation times.
    relax_fit.relax_time(time=times[i], spectrum_id=names[i])

    # The errors.
    for j in range(len(err_lines)):
        # Skip comments.
        if err_lines[j][0][0] == '#':
            continue

        # The spin ID.
        spin_id = ':%s' % err_lines[j][1]
        spin = return_spin(spin_id=spin_id)

        # Set the error.
        if not hasattr(spin, 'peak_intensity_err'):
            spin.peak_intensity_err = {}
        spin.peak_intensity_err[names[i]] = float(err_lines[j][i+2])

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
minimise.grid_search(inc=11)

# Minimise.
minimise.execute('simplex', constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=500)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise.execute('simplex', constraints=False)
monte_carlo.error_analysis()

# Save the relaxation rates.
value.write(param='rx', file='r1_pdc_err', force=True)

# Save the program state.
state.save('state', force=True)
