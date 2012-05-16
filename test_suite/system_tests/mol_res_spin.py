###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""System tests of the molecule, residue, and spin sequence operators."""


# Python module imports.
from os import sep

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


class Mol_res_spin(SystemTestCase):
    """Class for testing the mol_res_spin functions."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def test_residue_delete(self):
        """Test residue deletion."""

        # Read a PDB file.
        self.interpreter.structure.read_pdb(file='sphere.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'sphere')

        # Load the spins.
        self.interpreter.structure.load_spins()

        # Test the original sequence data.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(len(cdp.mol[0].res), 9)

        # Delete the first residue.
        self.interpreter.residue.delete(res_id='#sphere_mol1:1&:GLY')

        # Test the remaining sequence data.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(len(cdp.mol[0].res), 8)
