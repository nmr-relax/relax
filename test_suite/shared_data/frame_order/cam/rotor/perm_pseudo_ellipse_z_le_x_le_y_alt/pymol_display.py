###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
"""relax script for displaying the frame order results of this 'pseudo-ellipse' model in PyMOL."""

# PyMOL visualisation.
pymol.frame_order(ave_pos='ave_pos_true', rep='frame_order_true', dir='..')
pymol.frame_order(ave_pos=None, rep='fo_orig')
pymol.frame_order(ave_pos=None, rep='fo_orig_perm_A')
pymol.frame_order(ave_pos=None, rep='fo_orig_perm_B')
pymol.frame_order(ave_pos=None, rep='fo')
pymol.frame_order(ave_pos=None, rep='fo_perm_A')
pymol.frame_order(ave_pos=None, rep='fo_perm_B')
