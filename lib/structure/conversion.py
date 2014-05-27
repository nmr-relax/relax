###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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


def get_proton_name(atom_num):
    """Return a valid PDB atom name of <4 characters.

    @param atom_num:    The number of the atom.
    @type atom_num:     int
    @return:            The atom name to use in the PDB.
    @rtype:             str
    """

    # Init the proton first letters and the atom number folding limits.
    names = ['H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q']
    lims = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]

    # Loop over the proton names.
    for i in range(len(names)):
        # In the bounds.
        if atom_num >= lims[i] and atom_num < lims[i+1]:
            return names[i] + repr(atom_num - lims[i])
