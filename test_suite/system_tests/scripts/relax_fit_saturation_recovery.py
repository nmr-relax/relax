###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
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


# Create the 'rx' data pipe.
pipe.create('rx', 'relax_fit')

# Load the backbone amide 15N spins from a PDB file.
#structure.read_pdb('Ap4Aase_new_3.pdb')
#structure.load_spins(spin_id='@N')

# Load the sequence.
sequence.read(file='wr10_43_relax.seq', res_name_col=1, res_num_col=2, spin_num_col=3, spin_name_col=4)
spin.name(name='H')
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
    spectrum.read_intensities(file=names[i]+'.list', spectrum_id=names[i], int_method='height')

    # Set the relaxation times.
    relax_fit.relax_time(time=times[i], spectrum_id=names[i])

# Specify the duplicated spectra.
#spectrum.replicated(spectrum_ids=['T2_ncyc1_ave', 'T2_ncyc1b_ave'])
#spectrum.replicated(spectrum_ids=['T2_ncyc4_ave', 'T2_ncyc4b_ave'])
#spectrum.replicated(spectrum_ids=['T2_ncyc9_ave', 'T2_ncyc9b_ave'])
#spectrum.replicated(spectrum_ids=['T2_ncyc11_ave', 'T2_ncyc11b_ave'])

#maf# Spectrum baseplane noise for non-duplicated spectra
spectrum.baseplane_rmsd(error=92440.562999, spectrum_id='0.070s', spin_id=None)
spectrum.baseplane_rmsd(error=91770.380636, spectrum_id='0.150s', spin_id=None)
spectrum.baseplane_rmsd(error=95226.122047, spectrum_id='0.250s', spin_id=None)
spectrum.baseplane_rmsd(error=94428.183988, spectrum_id='0.350s', spin_id=None)
spectrum.baseplane_rmsd(error=92478.391627, spectrum_id='0.500s', spin_id=None)
spectrum.baseplane_rmsd(error=92167.856579, spectrum_id='0.750s', spin_id=None)
spectrum.baseplane_rmsd(error=95071.442069, spectrum_id='1.000s', spin_id=None)
spectrum.baseplane_rmsd(error=92479.274501, spectrum_id='2.000s', spin_id=None)
spectrum.baseplane_rmsd(error=95735.516944, spectrum_id='3.000s', spin_id=None)
spectrum.baseplane_rmsd(error=106627.326030, spectrum_id='5.000s', spin_id=None)


# Peak intensity error analysis.
spectrum.error_analysis()

# Deselect unresolved spins.
#deselect.read(file='unresolved', mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5)

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
minimise.grid_search(inc=11)

# Minimise.
minimise.execute('newton', constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=5)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise.execute('newton', constraints=False)
monte_carlo.error_analysis()

# Save the relaxation rates.
value.write(param='rx', file='rx.out', force=True)

# Save the results.
results.write(file='results', force=True)

# Create Grace plots of the data.
grace.write(y_data_type='chi2', file='chi2.agr', force=True)    # Minimised chi-squared value.
grace.write(y_data_type='i0', file='i0.agr', force=True)    # Initial peak intensity.
grace.write(y_data_type='rx', file='rx.agr', force=True)    # Relaxation rate.
grace.write(x_data_type='relax_times', y_data_type='peak_intensity', file='intensities.agr', force=True)    # Average peak intensities.
grace.write(x_data_type='relax_times', y_data_type='peak_intensity', norm=True, file='intensities_norm.agr', force=True)    # Average peak intensities (normalised).

# Save the program state.
state.save('rx.save', force=True)
