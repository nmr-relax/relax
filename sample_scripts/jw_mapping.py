###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
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

"""Script for reduced spectral density mapping."""


# Create the data pipe.
pipe.create('my_protein', 'jw')

# Load the sequence.
sequence.read('noe.600.out', res_num_col=1)

# Load the relaxation data.
relax_data.read(ri_id='R1_600',  ri_type='R1',  frq=600.0*1e6, file='r1.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='R2_600',  ri_type='R2',  frq=600.0*1e6, file='r2.600.out', res_num_col=1, data_col=3, error_col=4)
relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.0*1e6, file='noe.600.out', res_num_col=1, data_col=3, error_col=4)

# Set the nuclei types.
value.set('15N', 'heteronuc_type')
value.set('1H', 'proton_type')

# Set the bond length and CSA values.
value.set(1.02 * 1e-10, 'r')
value.set(-172 * 1e-6, 'csa')

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
