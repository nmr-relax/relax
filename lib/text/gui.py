###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""Module defining a number of text elements for use in the GUI.

Some of these text elements are operating system dependent due to the incompleteness of the unicode fonts on certain systems.
"""

# relax module imports.
from compat import SYSTEM, u


# Relaxation data GUI text elements.
r1 = u("R\u2081")
r2 = u("R\u2082")

# Model-free GUI text elements.
s2 = u("S\u00B2")
s2f = u("S\u00B2f")
s2s = u("S\u00B2s")
local_tm = u("local \u03C4\u2098")
tm = u("\u03C4\u2098")
te = u("\u03C4e")
tf = u("\u03C4f")
ts = u("\u03C4s")
rex = u("R\u2091\u2093")
csa = "CSA"
r = "r"
