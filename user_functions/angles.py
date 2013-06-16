###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""The angles user function definitions."""

# relax module imports.
from pipe_control import angles
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('angles')
uf_class.title = "Class containing the function for calculating XH bond angles."
uf_class.menu_text = "&angles"

# The angles.diff_frame user function.
uf = uf_info.add_uf('angles.diff_frame')
uf.title = "Calculate the angles defining the XH bond vector within the diffusion frame."
uf.title_short = "Diffusion frame XH vector angle calculation."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("If the diffusion tensor is isotropic, then nothing will be done.")
uf.desc[-1].add_paragraph("If the diffusion tensor is axially symmetric, then the angle alpha will be calculated for each XH bond vector.")
uf.desc[-1].add_paragraph("If the diffusion tensor is asymmetric, then the three angles will be calculated.")
uf.backend = angles.angle_diff_frame
uf.menu_text = "&diff_frame"
uf.wizard_size = (800, 400)
uf.gui_icon = "oxygen.categories.applications-education"
uf.wizard_height_desc = 250
