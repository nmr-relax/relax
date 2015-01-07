###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Andras Boeszoermenyi (https://gna.org/users/andras)      #
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

"""Script for relaxation curve fitting."""


# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Missing temporary directory.
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp'

# Create the 'rx' data pipe.
pipe.create('rx', 'relax_fit')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting'+sep+'saturation_recovery'

# Load the sequence.
spin.create(spin_name='H', res_name='G', res_num=17)
spin.element(element='H')
spin.isotope(isotope='1H', spin_id='@H')
spin.name(name='HE1')
spin.element(element='H')
spin.isotope(isotope='1H', spin_id='@HE1')

# Spectrum names.
names = [
    '0.070s',
    '0.150s',
    '0.250s',
    '0.350s',
    '0.500s',
    '0.750s',
    '1.000s',
    '2.000s',
    '3.000s',
    '5.000s'
]

# Relaxation times (in seconds).
times = [
    0.07,
    0.15,
    0.25,
    0.35,
    0.50,
    0.75,
    1.00,
    2.00,
    3.00,
    5.00
]

# Loop over the spectra.
for i in range(len(names)):
    # Load the peak intensities (first the backbone NH, then the tryptophan indole NH).
    spectrum.read_intensities(file=names[i]+'.list', dir=data_path, spectrum_id=names[i], int_method='height')

    # Set the relaxation times.
    relax_fit.relax_time(time=times[i], spectrum_id=names[i])

# Spectrum baseplane noise for non-duplicated spectra
spectrum.baseplane_rmsd(error=5e13, spectrum_id='0.070s', spin_id=None)
spectrum.baseplane_rmsd(error=5e13, spectrum_id='0.150s', spin_id=None)
spectrum.baseplane_rmsd(error=5e13, spectrum_id='0.250s', spin_id=None)
spectrum.baseplane_rmsd(error=5e13, spectrum_id='0.350s', spin_id=None)
spectrum.baseplane_rmsd(error=5e13, spectrum_id='0.500s', spin_id=None)
spectrum.baseplane_rmsd(error=5e13, spectrum_id='0.750s', spin_id=None)
spectrum.baseplane_rmsd(error=5e13, spectrum_id='1.000s', spin_id=None)
spectrum.baseplane_rmsd(error=5e13, spectrum_id='2.000s', spin_id=None)
spectrum.baseplane_rmsd(error=5e13, spectrum_id='3.000s', spin_id=None)
spectrum.baseplane_rmsd(error=5e13, spectrum_id='5.000s', spin_id=None)

# Peak intensity error analysis.
spectrum.error_analysis()

# Set the relaxation curve type for the saturation recovery.
relax_fit.select_model('sat')

# Grid search.
minimise.grid_search(inc=11)

# Minimise.
minimise.execute('newton', constraints=False)

# Try out the covariance matrix technique.
error_analysis.covariance_matrix()

# Monte Carlo simulations.
monte_carlo.setup(number=5)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise.execute('newton', constraints=False)
monte_carlo.error_analysis()

# Save the relaxation rates.
value.write(param='rx', file='rx.out', dir=ds.tmpdir, force=True)

# Save the results.
results.write(file='results', dir=ds.tmpdir, force=True)

# Create Grace plots of the data.
grace.write(y_data_type='chi2', file='chi2.agr', dir=ds.tmpdir, force=True)    # Minimised chi-squared value.
grace.write(y_data_type='i0', file='i0.agr', dir=ds.tmpdir, force=True)    # Initial peak intensity.
grace.write(y_data_type='rx', file='rx.agr', dir=ds.tmpdir, force=True)    # Relaxation rate.
grace.write(x_data_type='relax_times', y_data_type='peak_intensity', file='intensities.agr', dir=ds.tmpdir, force=True)    # Average peak intensities.
grace.write(x_data_type='relax_times', y_data_type='peak_intensity', norm_type='last', norm=True, file='intensities_norm.agr', dir=ds.tmpdir, force=True)    # Average peak intensities (normalised).

# Save the program state.
state.save('devnull', force=True)
