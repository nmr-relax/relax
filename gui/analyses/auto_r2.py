###############################################################################
#                                                                             #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module for the automatic R2 analysis frame."""

# relax GUI module imports.
from auto_rx_base import Auto_rx
from gui.paths import ANALYSIS_IMAGE_PATH, IMAGE_PATH


class Auto_r2(Auto_rx):
    """Class for building the automatic R2 analysis frame."""

    # Hardcoded variables.
    analysis_type = 'r2'
    bitmap = [ANALYSIS_IMAGE_PATH+"r2_200x200.png",
              IMAGE_PATH+'r2.png']
    label = 'R2'
