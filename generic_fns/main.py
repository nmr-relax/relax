###############################################################################
#                                                                             #
# Copyright (C) 2004-2005 Edward d'Auvergne                                   #
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

from angles import Angles
from dx.opendx import OpenDX
from diffusion_tensor import Diffusion_tensor
from dasha import Dasha
from eliminate import Eliminate
from fix import Fix
from grace import Grace
from intensity import Intensity
from minimise import Minimise
from model_selection import Model_selection
from molmol import Molmol
from monte_carlo import Monte_carlo
from nuclei import Nuclei
from palmer import Palmer
from pdb import PDB
from results import Results
from runs import Runs
from selection import Selection
from sequence import Sequence
from state import State
from value import Value
from vmd import Vmd


class Generic:
    def __init__(self, relax):
        """Class containing all the generic functions."""

        # Place the program class structure under self.relax
        self.relax = relax

        # Set up all the classes.
        self.angles = Angles(self.relax)
        self.dasha = Dasha(self.relax)
        self.diffusion_tensor = Diffusion_tensor(self.relax)
        self.eliminate = Eliminate(self.relax)
        self.fix = Fix(self.relax)
        self.grace = Grace(self.relax)
        self.intensity = Intensity(self.relax)
        self.minimise = Minimise(self.relax)
        self.model_selection = Model_selection(self.relax)
        self.molmol = Molmol(self.relax)
        self.monte_carlo = Monte_carlo(self.relax)
        self.nuclei = Nuclei(self.relax)
        self.opendx = OpenDX(self.relax)
        self.palmer = Palmer(self.relax)
        self.pdb = PDB(self.relax)
        self.results = Results(self.relax)
        self.runs = Runs(self.relax)
        self.selection = Selection(self.relax)
        self.sequence = Sequence(self.relax)
        self.state = State(self.relax)
        self.value = Value(self.relax)
        self.vmd = Vmd(self.relax)
