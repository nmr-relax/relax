###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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


# Create a data pipe.
pipe.create('subset', 'N-state')

# Load the sequence from one of the PCS files.
sequence.read('pcs_dy.txt', mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5)

# Deselect all spins.
deselect.all()

# Select the five spins for the subset.
select.spin(':99@H')
select.spin(':108@H')
select.spin(':114@H')
select.spin(':119@H')
select.spin(':126@H')

# Load the PCS data and write out the subset.
lns = ['dy', 'er', 'tb', 'tm']
for ln in lns:
    # Read.
    pcs.read(align_id=ln, file='pcs_%s.txt'%ln, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

    # Write.
    pcs.write(align_id=ln, file='pcs_%s_subset.txt'%ln, force=True)
