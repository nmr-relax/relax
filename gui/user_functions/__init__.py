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

    def __init__(self, gui):
        """Set up the container."""

        # Store the args.
        self.gui = gui

        # The user functions.
        self.deselect = Deselect(self.gui)
        self.gpl = Gpl(self.gui)
        self.grace = Grace(self.gui)
        self.molecule = Molecule(self.gui)
        self.molmol = Molmol(self.gui)
        self.noe = Noe(self.gui)
        self.pipe = Pipe(self.gui)
        self.residue = Residue(self.gui)
        self.results = Results(self.gui)
        self.relax_data = Relax_data(self.gui)
        self.relax_fit = Relax_fit(self.gui)
        self.script = Script(self.gui)
        self.select = Select(self.gui)
        self.sequence = Sequence(self.gui)
        self.spectrum = Spectrum(self.gui)
        self.spin = Spin(self.gui)
        self.structure = Structure(self.gui)
        self.value = Value(self.gui)


    def destroy(self):
        """Close all windows."""

        # Send the commands onwards to the user function classes.
        self.deselect.destroy()
        self.gpl.destroy()
        self.grace.destroy()
        self.molecule.destroy()
        self.molmol.destroy()
        self.noe.destroy()
        self.pipe.destroy()
        self.residue.destroy()
        self.results.destroy()
        self.relax_data.destroy()
        self.relax_fit.destroy()
        self.select.destroy()
        self.sequence.destroy()
        self.spectrum.destroy()
        self.spin.destroy()
        self.structure.destroy()
        self.value.destroy()
