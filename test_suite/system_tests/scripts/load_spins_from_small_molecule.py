###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""Load a number of spin systems for a small molecule."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Read in the small molecule.
structure.read_pdb(file='gromacs.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'phthalic_acid')

# Load all protons.
structure.load_spins(spin_id='@*H*')

# Load a few carbons.
structure.load_spins(spin_id='@C5')
structure.load_spins(spin_id='@C6')
structure.load_spins(spin_id='@C19')
structure.load_spins(spin_id='@C23')
