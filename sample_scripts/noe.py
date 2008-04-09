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

# Script for calculating NOEs.
##############################

# Create the run
name = 'noe'
run.create(name, 'noe')

# Load the sequence from a PDB file.
pdb(name, 'Ap4Aase_new_3.pdb', load_seq=1)

# Load the reference spectrum and saturated spectrum peak intensities.
noe.read(name, file='ref.list', spectrum_type='ref')
noe.read(name, file='sat.list', spectrum_type='sat')

# Set the errors.
noe.error(name, error=3600, spectrum_type='ref')
noe.error(name, error=3000, spectrum_type='sat')

# Individual residue errors.
noe.error(name, error=122000, spectrum_type='ref', res_num=114)
noe.error(name, error=8500, spectrum_type='sat', res_num=114)

# Unselect unresolved residues.
unselect.read(name, file='unresolved')

# Calculate the NOEs.
calc(name)

# Save the NOEs.
value.write(name, param='noe', file='noe.out', force=1)

# Create grace files.
grace.write(name, y_data_type='ref', file='ref.agr', force=1)
grace.write(name, y_data_type='sat', file='sat.agr', force=1)
grace.write(name, y_data_type='noe', file='noe.agr', force=1)

# View the grace files.
grace.view(file='ref.agr')
grace.view(file='sat.agr')
grace.view(file='noe.agr')

# Write the results.
results.write(name, file='results', dir=None, force=1)

# Save the program state.
state.save('save', force=1)
