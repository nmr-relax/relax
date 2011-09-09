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

# Package docstring.
"""User function GUI elements."""

# relax module imports.
from relax_errors import RelaxError

# GUI module imports.
from deselect import Deselect
from gpl import Gpl
from grace import Grace
from molecule import Molecule
from molmol import Molmol
from noe import Noe
from pipe import Pipe
from pymol import Pymol
from residue import Residue
from results import Results
from relax_data import Relax_data
from relax_fit import Relax_fit
from script import Script
from select import Select
from sequence import Sequence
from spectrum import Spectrum
from spin import Spin
from structure import Structure
from value import Value


# The package __all__ list.
__all__ = ['base',
           'deselect',
           'gpl',
           'grace',
           'molecule',
           'molmol',
           'noe',
           'pipe',
           'pymol',
           'residue',
           'results',
           'relax_data',
           'relax_fit',
           'script',
           'select',
           'sequence',
           'spectrum',
           'spin',
           'structure',
           'value']


class User_functions:
    """Container for all the user function GUI elements.

    This uses the observer design pattern to allow for GUI updates upon completion of a user function.
    """

    def __init__(self):
        """Set up the container."""

        # The user functions.
        self.deselect = Deselect()
        self.gpl = Gpl()
        self.grace = Grace()
        self.molecule = Molecule()
        self.molmol = Molmol()
        self.noe = Noe()
        self.pipe = Pipe()
        self.pymol = Pymol()
        self.residue = Residue()
        self.results = Results()
        self.relax_data = Relax_data()
        self.relax_fit = Relax_fit()
        self.script = Script()
        self.select = Select()
        self.sequence = Sequence()
        self.spectrum = Spectrum()
        self.spin = Spin()
        self.structure = Structure()
        self.value = Value()
