###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
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

"""Script for reduced spectral density mapping."""


# Create the data pipe.
pipe.create(pipe_name='my_protein', pipe_type='jw')

# Set up the 15N spins.
sequence.read(file='noe.600.out', res_num_col=1, res_name_col=2)
spin.name(name='N')
spin.element(element='N')
spin.isotope(isotope='15N', spin_id='@N')

# Load the 15N relaxation data.
relax_data.read(ri_id='R1_600',  ri_type='R1',  frq=600.0*1e6, file='r1.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='R2_600',  ri_type='R2',  frq=600.0*1e6, file='r2.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.0*1e6, file='noe.600.out', res_num_col=1, data_col=3, error_col=4)

# Generate 1H spins for the magnetic dipole-dipole relaxation interaction.
sequence.attach_protons()

# Define the magnetic dipole-dipole relaxation interaction.
interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

# Define the chemical shift relaxation interaction.
value.set(val=-172 * 1e-6, param='csa')

# Select the frequency.
jw_mapping.set_frq(frq=600.0 * 1e6)

# Reduced spectral density mapping.
calc()

# Monte Carlo simulations (well, bootstrapping as this is a calculation and not a fit!).
monte_carlo.setup(number=500)
monte_carlo.create_data()
calc()
monte_carlo.error_analysis()

# Create grace files.
grace.write(y_data_type='j0', file='j0.agr', force=True)
grace.write(y_data_type='jwx', file='jwx.agr', force=True)
grace.write(y_data_type='jwh', file='jwh.agr', force=True)

# View the grace files.
grace.view(file='j0.agr')
grace.view(file='jwx.agr')
grace.view(file='jwh.agr')

# Write out the values.
value.write(param='j0', file='j0.txt', force=True)
value.write(param='jwx', file='jwx.txt', force=True)
value.write(param='jwh', file='jwh.txt', force=True)

# Finish.
results.write(file='results', force=True)
state.save('save', force=True)
