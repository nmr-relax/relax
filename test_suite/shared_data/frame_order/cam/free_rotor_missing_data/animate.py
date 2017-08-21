###############################################################################
#                                                                             #
# Copyright (C) 2011-2013 Edward d'Auvergne                                   #
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
"""Script for creating an animation of the model and results."""


# Load the frame order results.
state.load('frame_order')

# Launch PyMOL.
pymol.view()

# The cone representation.
pymol.cone_pdb('cone.pdb')

# View all.
pymol.command('zoom')

# Load the distribution of structures.
pymol.command('load distribution.pdb')

# Structure display.
pymol.command('hide everything, 1J7O_1st_NH')
pymol.command('hide everything, 1J7P_1st_NH_rot')
pymol.command('hide everything, distribution')
pymol.command('show spheres, 1J7O_1st_NH')
pymol.command('show spheres, 1J7P_1st_NH_rot')
pymol.command('show sticks, distribution')
pymol.command('color firebrick, 1J7P_1st_NH_rot and n. N')
pymol.command('color salmon, 1J7P_1st_NH_rot and n. H')

# Animate.
pymol.command('cmd.mplay()')

# Load the original domain position.
pymol.command('load ../1J7P_1st_NH.pdb')
pymol.command('hide everything, 1J7P_1st_NH')
pymol.command('show spheres, 1J7P_1st_NH')
