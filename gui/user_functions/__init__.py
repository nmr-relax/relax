###############################################################################
#                                                                             #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
from bruker import Bruker
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
from sys_info import Sys_info
from value import Value


# The package __all__ list.
__all__ = ['base',
           'bruker',
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
           'sys_info',
           'value']


class User_functions:
    """Container for all the user function GUI elements.

    This uses the observer design pattern to allow for GUI updates upon completion of a user function.
    """

    def __init__(self, parent=None):
        """Set up the container.

        @keyword parent:    The parent window.
        @type parent:       wx.Window instance
        """

        # The user functions.
        self.bruker = Bruker(parent)
        self.deselect = Deselect(parent)
        self.gpl = Gpl(parent)
        self.grace = Grace(parent)
        self.molecule = Molecule(parent)
        self.molmol = Molmol(parent)
        self.noe = Noe(parent)
        self.pipe = Pipe(parent)
        self.pymol = Pymol(parent)
        self.residue = Residue(parent)
        self.results = Results(parent)
        self.relax_data = Relax_data(parent)
        self.relax_fit = Relax_fit(parent)
        self.script = Script(parent)
        self.select = Select(parent)
        self.sequence = Sequence(parent)
        self.spectrum = Spectrum(parent)
        self.spin = Spin(parent)
        self.structure = Structure(parent)
        self.sys_info = Sys_info(parent)
        self.value = Value(parent)
