###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
"""The molecule, residue, spin base classes."""

# Python module imports.
from string import split

# relax module imports.
from generic_fns.mol_res_spin import generate_spin_id, residue_loop, spin_loop
from generic_fns import pipes

# GUI module imports.
from base import UF_base, UF_window
from gui_bieri.misc import gui_to_int, gui_to_str
from gui_bieri.paths import WIZARD_IMAGE_PATH


class Mol_res_spin:
    """The molecule, residue, spin base class."""

    def _get_res_id(self, suffix=''):
        """Generate the residue ID from the residue selection.

        @keyword suffix:    The suffix to be added to the residue data structure name.
        @type suffix:       str
        @return:            The residue ID string.
        @rtype:             str
        """

        # The molecule name.
        obj = getattr(self, 'mol'+suffix)
        mol_name = str(obj.GetValue())
        if mol_name == '':
            mol_name = None

        # The residue info.
        res_info = self._get_res_info(suffix)
        if not res_info:
            return
        res_num, res_name = res_info

        # Generate and return the ID.
        return generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name)


    def _get_res_info(self, suffix=''):
        """Extract the residue info from the residue selection.

        @keyword suffix:    The suffix to be added to the residue data structure name.
        @type suffix:       str
        @return:            The residue number and name from the residue selection self.res.
        @rtype:             int, str
        """

        # Single residue object.
        if hasattr(self, 'res'+suffix):
            # The residue info.
            obj = getattr(self, 'res'+suffix)
            res = gui_to_str(obj.GetValue())

            # Nothing.
            if not res:
                return

            # Split.
            res_num, res_name = split(res)

            # Convert.
            if res_name == '':
                res_name = None
            if res_num == '':
                res_num = None
            else:
                res_num = int(res_num)

        # 2 objects.
        else:
            # The residue number.
            obj = getattr(self, 'res_num'+suffix)
            res_num = gui_to_int(obj.GetValue())

            # The residue name.
            obj = getattr(self, 'res_name'+suffix)
            res_name = gui_to_str(obj.GetValue())

        # Return the number and name.
        return res_num, res_name


    def _get_spin_id(self, suffix=''):
        """Generate the spin ID from the molecule, residue, and spin selection.

        @keyword suffix:    The suffix to be added to the spin data structure name.
        @type suffix:       str
        @return:            The spin ID string.
        @rtype:             str
        """

        # The molecule name.
        obj = getattr(self, 'mol'+suffix)
        mol_name = str(obj.GetValue())
        if mol_name == '':
            mol_name = None

        # The residue info.
        res_num, res_name = self._get_res_info(suffix=suffix)

        # The spin info.
        spin_info = self._get_spin_info(suffix=suffix)
        if not spin_info:
            return
        spin_num, spin_name = spin_info

        # Generate and return the ID.
        return generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name)


    def _get_spin_info(self, suffix=''):
        """Extract the spin info from the spin selection.

        @keyword suffix:    The suffix to be added to the spin data structure name.
        @type suffix:       str
        @return:            The spin number and name from the spin selection self.spin.
        @rtype:             int, str
        """

        # Single spin object.
        if hasattr(self, 'spin'+suffix):
            # The spin info.
            obj = getattr(self, 'spin'+suffix)
            spin = str(obj.GetValue())

            # Nothing.
            if spin == '':
                return

            # Split.
            spin_num, spin_name = split(spin)

            # Convert.
            if spin_name == '':
                spin_name = None
            if spin_num == '':
                spin_num = None
            else:
                spin_num = int(spin_num)

        # 2 objects.
        else:
            # The spin number.
            obj = getattr(self, 'spin_num'+suffix)
            spin_num = gui_to_int(obj.GetValue())

            # The spin name.
            obj = getattr(self, 'spin_name'+suffix)
            spin_name = gui_to_str(obj.GetValue())

        # Return the number and name.
        return spin_num, spin_name


    def _update_residues(self, event):
        """Update the residue combo box self.res.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.res.Clear()

        # Clear the text.
        self.res.SetValue('')

        # The list of residue names.
        mol_id = generate_spin_id(str(self.mol.GetValue()))
        for res in residue_loop(mol_id):
            self.res.Append("%s %s" % (res.num, res.name))


    def _update_spins(self, event):
        """Update the spin combo box self.spin.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.spin.Clear()

        # Clear the text.
        self.spin.SetValue('')

        # Get the residue ID.
        res_id = self._get_res_id()
        if not res_id:
            return

        # Build the list of spin names.
        for spin in spin_loop(res_id):
            self.spin.Append("%s %s" % (spin.num, spin.name))
