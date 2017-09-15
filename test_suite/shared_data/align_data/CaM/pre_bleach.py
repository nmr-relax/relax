###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
"""relax script for generating synthetic RDC and PCS data for the bax_C_1J7P_N_H_Ca.pdb structure."""

# Python module imports.
from numpy.linalg import norm
from os import sep

# relax module imports.
from pipe_control.mol_res_spin import return_spin, spin_loop
from status import Status; status = Status()


# PRE cut-off (in Angstrom).
PRE = 15.0


# Path to files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep

# Create a data pipe.
pipe.create('pre', 'N-state')

# Load the structure.
structure.read_pdb('bax_C_1J7P_N_H_Ca.pdb', dir=path+sep+'structures')

# Load all atoms as spins.
structure.load_spins()

# Get the first calcium position.
spin = return_spin(spin_id=':1000@CA')
centre = spin.pos

# Open the unresolved file.
file = open('unresolved', 'w')

# Find the atoms within X Angstrom.
print("\n\nBleached spins:")
for spin, mol, res_num, res_name in spin_loop(full_info=True):
    # Skip calciums.
    if spin.name == "CA":
        continue

    # Calculate the distance between the PCS centre and the atom (in metres).
    r = spin.pos - centre

    # PRE.
    if norm(r) < PRE:
        # Print out.
        print("\t%20s %20s %20s %20s %20s" % (mol, res_num, res_name, spin.num, spin.name))

        file.write("%20s %20s %20s %20s %20s\n" % (mol, res_num, res_name, spin.num, spin.name))

# Close the file.
file.close()
