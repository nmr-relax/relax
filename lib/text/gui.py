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
from lib.compat import SYSTEM, u

# OS Flags.
win = False
mac = False
if SYSTEM == 'Windows':
    win = True
if SYSTEM == 'Darwin':
    mac = True

# Relaxation data GUI text elements.
r1 = u("R\u2081")
r2 = u("R\u2082")
if win:
    r1 = "R1"
    r2 = "R2"

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
if win:
    local_tm = u("local \u03C4m")
    tm = u("\u03C4m")
    rex = "Rex"
if mac:
    local_tm = u("local \u03C4m")
    tm = u("\u03C4m")

# Relaxation dispersion GUI text elements.
dw = u("d\u03C9")
dw_AB = u("d\u03C9(AB)")
dw_AC = u("d\u03C9(AC)")
dw_BC = u("d\u03C9(BC)")
dwH = u("d\u03C9H")
dwH_AB = u("d\u03C9H(AB)")
dwH_AC = u("d\u03C9H(AC)")
dwH_BC = u("d\u03C9H(BC)")
i0 = u("I\u2080")
nu_1 = u("\u03bd\u2081")
nu_cpmg = u("\u03bd")
kex = u("k\u2091\u2093")
tex = u("t\u2091\u2093")
kAB = u("k\u2091\u2093(AB)")
kAC = u("k\u2091\u2093(AC)")
kBC = u("k\u2091\u2093(BC)")
padw2 = u("pA.d\u03C9\u00B2")
phi_ex = u("\u03D5\u2091\u2093")
phi_exB = u("\u03D5\u2091\u2093B")
phi_exC = u("\u03D5\u2091\u2093C")
r1rho = u("R\u2081\u1D68")
r1rho_prime = u("R\u2081\u1D68'")
r2a = u("R\u2082A")
r2b = u("R\u2082B")
r2eff = u("R\u2082eff")
theta = u("\u03d1")
w_eff = u("\u03C9_eff")
w_rf = u("\u03C9_rf")
if win:
    i0 = "I0"
    kex = "kex"
    kAB = "kex(AB)"
    kAC = "kex(AC)"
    kBC = "kex(BC)"
    nu_1 = u("\u03bd1")
    phi_ex = u("phi_ex")
    phi_exB = u("phi_exB")
    phi_exC = u("phi_exC")
    r1rho = "R1rho"
    r1rho_prime = "R1rho'"
    r2a = "R2A"
    r2b = "R2B"
    r2eff = "R2eff"
    theta = u("theta")
