###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  0205-1307  USA   #
#                                                                             #
###############################################################################

# Python module imports.
from os import sep
import sys

# relax module imports.
from status import Status; status = Status()


# Script for relaxation curve fitting.
######################################


# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists'+sep+'ccpn_analysis'

# Create the 'rx' data pipe.
pipe.create('rx', 'relax_fit')

# Load sequence and spins
sequence.read('sequence.out', dir=data_path, res_num_col=1, res_name_col=2, spin_name_col=3)

# Spectrum names.
names = [
    'T1A_0010',
    'T1A_0020',
    'T1A_0030',
    'T1A_0050',
    'T1A_0070',
    'T1A_0100',
    'T1A_0150',
    'T1A_0200',
    'T1A_0300',
    'T1A_0400',
    'T1A_0600',
    'T1A_0800',
    'T1A_1000',
    'T1A_1200'
]

# Relaxation times (in seconds).
times = [
    0.01,
    0.02,
    0.03,
    0.05,
    0.07,
    0.1,
    0.15,
    0.2,
    0.3,
    0.4,
    0.6,
    0.8,
    1.0,
    1.2
]

# Loop over the spectra.
for i in xrange(len(names)):
    # Load the peak intensities.
    spectrum.read_intensities(file=names[i]+'.list', dir=data_path, spectrum_id=names[i], int_method='height')

    # Set the relaxation times.
    relax_fit.relax_time(time=times[i], spectrum_id=names[i])

# Specify the duplicated spectra.
spectrum.baseplane_rmsd(error=22980, spectrum_id='T1A_0010')
spectrum.baseplane_rmsd(error=21982, spectrum_id='T1A_0020')
spectrum.baseplane_rmsd(error=21916, spectrum_id='T1A_0030')
spectrum.baseplane_rmsd(error=21780, spectrum_id='T1A_0050')
spectrum.baseplane_rmsd(error=21015, spectrum_id='T1A_0070')
spectrum.baseplane_rmsd(error=19957, spectrum_id='T1A_0100')
spectrum.baseplane_rmsd(error=19064, spectrum_id='T1A_0150')
spectrum.baseplane_rmsd(error=17618, spectrum_id='T1A_0200')
spectrum.baseplane_rmsd(error=15592, spectrum_id='T1A_0300')
spectrum.baseplane_rmsd(error=13681, spectrum_id='T1A_0400')
spectrum.baseplane_rmsd(error=10938, spectrum_id='T1A_0600')
spectrum.baseplane_rmsd(error=8898.4, spectrum_id='T1A_0800')
spectrum.baseplane_rmsd(error=7541.9, spectrum_id='T1A_1000')
spectrum.baseplane_rmsd(error=6772.1, spectrum_id='T1A_1200')


# Peak intensity error analysis.
spectrum.error_analysis()

# Deselect unresolved spins.
#deselect.read(file='unresolved')

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
grid_search(inc=11)

# Minimise.
minimise('simplex', scaling=False, constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=2)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', scaling=False, constraints=False)
monte_carlo.error_analysis()

# Save the relaxation rates.
value.write(param='rx', file='devnull', force=True)

# Save the results.
results.write(file='devnull', force=True)

# Create Grace plots of the data.
grace.write(y_data_type='rx', file='devnull', force=True)    # Relaxation rate.

# Display the Grace plots.
#grace.view(file='rx.agr', grace_exe='')

# Save the program state.
state.save('devnull', force=True)
