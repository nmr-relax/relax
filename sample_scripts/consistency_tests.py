###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Sebastien Morin                                     #
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

# Script for consistency testing.
#######################################################################

# Create the run.
name = 'consistency'
pipe.create(name, 'ct')

# Load the sequence.
sequence.read('noe.600.out')

# Load the relaxation data.
relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out')
relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out')
relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out')

# Set the nuclei types
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')

# Set the bond length and CSA values.
value.set(1.02 * 1e-10, 'bond_length')
value.set(-172 * 1e-6, 'csa')

# Set the angle between the 15N-1H vector and the principal axis of the 15N chemical shift tensor
value.set(15.7, 'orientation')

# Set the approximate correlation time.
value.set(13 * 1e-9, 'tc')

# Set the frequency.
consistency_tests.set_frq(frq=600.0 * 1e6)

# Consistency tests.
calc()

# Monte Carlo simulations.
monte_carlo.setup(number=500)
monte_carlo.create_data()
calc()
monte_carlo.error_analysis()

# Create grace files.
grace.write(y_data_type='j0', file='j0.agr', force=True)
grace.write(y_data_type='f_eta', file='f_eta.agr', force=True)
grace.write(y_data_type='f_r2', file='f_r2.agr', force=True)

# View the grace files.
grace.view(file='j0.agr')
grace.view(file='f_eta.agr')
grace.view(file='f_r2.agr')

# Finish.
results.write(file='results', force=True)
state.save('save', force=True)
