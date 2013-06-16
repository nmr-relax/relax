###############################################################################
#                                                                             #
# Copyright (C) 2010-2013 Edward d'Auvergne                                   #
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
"""Module for the automatic R1 analysis frame."""

# relax GUI module imports.
from graphics import ANALYSIS_IMAGE_PATH, IMAGE_PATH
from gui.analyses.auto_rx_base import Auto_rx


class Auto_r1(Auto_rx):
    """Class for building the automatic R1 analysis frame."""

    # Hardcoded variables.
    analysis_type = 'r1'
    bitmap = [ANALYSIS_IMAGE_PATH+"r1_200x200.png",
              IMAGE_PATH+'r1.png']
    label = "R1"
    gui_label = u"R\u2081"
