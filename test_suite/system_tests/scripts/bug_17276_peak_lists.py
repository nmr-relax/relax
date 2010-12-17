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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Script for relaxation curve fitting.
######################################


# Python module imports.
import __main__
from os import sep


# Path of the files.
PATH = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists'+sep+'bug_17276'


# Create the 'rx' data pipe.
pipe.create('rx', 'relax_fit')

# Load the backbone amide 15N spins from a PDB file.
sequence.read('sequence.out', dir=PATH, res_num_col=1, res_name_col=2, spin_name_col=3)

# Spectrum names.
names = [
    'T1010Ed',
    'T10102Ed',
    'T11200Ed',
    'T112002Ed' 
]

# Relaxation times (in seconds).
times = [
    0.01,
    0.01,
    1.2,
    1.2
]

# Loop over the spectra.
for i in xrange(len(names)):
    # Load the peak intensities.
    spectrum.read_intensities(file=names[i]+'.txt', dir=PATH, spectrum_id=names[i], int_method='height')

    # Set the relaxation times.
    relax_fit.relax_time(time=times[i], spectrum_id=names[i])

# Specify the duplicated spectra.
#spectrum.replicated(spectrum_ids=['T2_ncyc1_ave', 'T2_ncyc1b_ave'])

# Set the errors.
spectrum.replicated(spectrum_ids=['T1010Ed', 'T10102Ed'])
spectrum.replicated(spectrum_ids=['T11200Ed', 'T112002Ed'])

# Peak intensity error analysis.
spectrum.error_analysis()

# Deselect unresolved spins.
#deselect.read(file='unresolved')

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
grid_search(inc=11)

# The following is not functional!
#
## Minimise.
#minimise('simplex', scaling=False, constraints=False)
#
## Monte Carlo simulations.
#monte_carlo.setup(number=500)
#monte_carlo.create_data()
#monte_carlo.initial_values()
#minimise('simplex', scaling=False, constraints=False)
#monte_carlo.error_analysis()
#
## Save the relaxation rates.
#value.write(param='rx', file='rx.out', force=True)
#
## Save the results.
#results.write(file='results', force=True)
#
## Create Grace plots of the data.
#grace.write(y_data_type='chi2', file='chi2.agr', force=True)    # Minimised chi-squared value.
#grace.write(y_data_type='i0', file='i0.agr', force=True)    # Initial peak intensity.
#grace.write(y_data_type='rx', file='rx.agr', force=True)    # Relaxation rate.
#grace.write(x_data_type='relax_times', y_data_type='int', file='intensities.agr', force=True)    # Average peak intensities.
#grace.write(x_data_type='relax_times', y_data_type='int', norm=True, file='intensities_norm.agr', force=True)    # Average peak intensities (normalised).
#
## Display the Grace plots.
#grace.view(file='chi2.agr')
#grace.view(file='i0.agr')
#grace.view(file='rx.agr')
#grace.view(file='intensities.agr')
#grace.view(file='intensities_norm.agr')
#
## Save the program state.
#state.save('rx.save', force=True)
