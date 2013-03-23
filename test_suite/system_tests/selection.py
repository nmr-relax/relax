###############################################################################
#                                                                             #
# Copyright (C) 2012-2013 Edward d'Auvergne                                   #
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

"""System tests for testing the select and deselect user functions."""

# relax module imports.
from pipe_control.mol_res_spin import spin_loop
from test_suite.system_tests.base_classes import SystemTestCase


class Selection(SystemTestCase):
    """Class for testing the select and deselect user functions."""

    def setUp(self):
        """Initialise some molecule, residue and spin data for testing."""

        # Create a data pipe.
        self.interpreter.pipe.create('spin data', 'mf')

        # Add a molecule.
        self.interpreter.molecule.create(mol_name='X', mol_type='protein')

        # Add some residues.
        self.interpreter.residue.create(1, 'a')
        self.interpreter.residue.create(2, 'b')
        self.interpreter.residue.create(3, 'c')

        # Add some spins.
        for i in range(3):
            self.interpreter.spin.create('C', res_num=i+1)
            self.interpreter.spin.create('N', res_num=i+1)
            self.interpreter.spin.create('H', res_num=i+1)


    def check_spin_selection(self, selection):
        """Check if the given selection matches the spin selections.

        @param selection:   The list of spin selections in the spin order created in the setUp() method.
        @type selection:    list of bool
        """

        # Loop over the spins.
        i = 0
        for spin, spin_id in spin_loop(return_id=True):
            # Print out.
            print("Checking the selection state of spin '%s'." % spin_id)

            # Check.
            self.assertEqual(selection[i], spin.select)

            # Increment the counter.
            i += 1


    def test_deselect_all(self):
        """Check the operation of the deselect.all user function."""

        # The user function.
        self.interpreter.deselect.all()

        # Check the data.
        self.check_spin_selection([False]*9)


    def test_select_domain_bool_and(self):
        """Check the operation of the select.domain user function using the AND boolean."""

        # First deselect some spins.
        self.interpreter.deselect.spin(":1@C")
        self.interpreter.deselect.spin(":2@H")
        self.interpreter.deselect.spin(":2@C")
        self.interpreter.deselect.spin(":3@H")

        # Display the sequence.
        self.interpreter.sequence.display()

        # Define the domain.
        self.interpreter.domain(id='N', spin_id=":1-2")

        # Select the domain.
        self.interpreter.select.domain(domain_id='N', boolean="AND")

        # Check the selections.
        selection = [False, True, True, False, True, False] + [False]*3
        self.check_spin_selection(selection)


    def test_select_domain_bool_or(self):
        """Check the operation of the select.domain user function using the OR boolean."""

        # First deselect some spins.
        self.interpreter.deselect.spin(":1@C")
        self.interpreter.deselect.spin(":2@H")
        self.interpreter.deselect.spin(":2@C")
        self.interpreter.deselect.spin(":3@H")

        # Display the sequence.
        self.interpreter.sequence.display()

        # Define the domain.
        self.interpreter.domain(id='N', spin_id=":1-2")

        # Select the domain.
        self.interpreter.select.domain(domain_id='N', boolean="OR", change_all=False)

        # Check the selections.
        selection = [True]*6 + [True, True, False]
        self.check_spin_selection(selection)
