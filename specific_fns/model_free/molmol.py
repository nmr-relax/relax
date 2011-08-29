###############################################################################
#                                                                             #
# Copyright (C) 2003-2011 Edward d'Auvergne                                   #
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
"""The model-free Molmol macro module."""

# relax module imports.
from specific_fns.model_free.macro_base import Macro


class Molmol(Macro):
    """Class containing the Molmol specific functions for model-free analysis."""

    def _classic_colour(self, res_num=None, width=None, rgb_array=None):
        """Colour the given peptide bond."""

        # Ca to C bond.
        self.commands.append("SelectBond 'atom1.name = \"CA\"  & atom2.name = \"C\" & res.num = " + repr(res_num-1) + "'")
        self.commands.append("StyleBond neon")
        self.commands.append("RadiusBond " + repr(width))
        self.commands.append("ColorBond " + repr(rgb_array[0]) + " " + repr(rgb_array[1]) + " " + repr(rgb_array[2]))

        # C to N bond.
        self.commands.append("SelectBond 'atom1.name = \"C\"  & atom2.name = \"N\" & res.num = " + repr(res_num-1) + "'")
        self.commands.append("StyleBond neon")
        self.commands.append("RadiusBond " + repr(width))
        self.commands.append("ColorBond " + repr(rgb_array[0]) + " " + repr(rgb_array[1]) + " " + repr(rgb_array[2]))

        # N to Ca bond.
        self.commands.append("SelectBond 'atom1.name = \"N\"  & atom2.name = \"CA\" & res.num = " + repr(res_num) + "'")
        self.commands.append("StyleBond neon")
        self.commands.append("RadiusBond " + repr(width))
        self.commands.append("ColorBond " + repr(rgb_array[0]) + " " + repr(rgb_array[1]) + " " + repr(rgb_array[2]))

        # Blank line.
        self.commands.append("")


    def _classic_header(self):
        """Create the header for the molmol macro."""

        # Hide all bonds.
        self.commands.append("SelectBond ''")
        self.commands.append("StyleBond invisible")

        # Show the backbone bonds as lines.
        self.commands.append("SelectBond 'bb'")
        self.commands.append("StyleBond line")

        # Colour the backbone black.
        self.commands.append("ColorBond 0 0 0")


    def molmol_macro(self, data_type, style=None, colour_start=None, colour_end=None, colour_list=None, spin_id=None):
        """Wrapper method for the _create_macro method.

        @param data_type:       The parameter name or data type.
        @type data_type:        str
        @keyword style:         The Molmol style.
        @type style:            None or str
        @keyword colour_start:  The starting colour (must be a MOLMOL or X11 name).
        @type colour_start:     str
        @keyword colour_end:    The ending colour (must be a MOLMOL or X11 name).
        @type colour_end:       str
        @keyword colour_list:   The colour list used, either 'molmol' or 'x11'.
        @type colour_list:      str
        @keyword spin_id:       The spin identification string.
        @type spin_id:          str
        """

        self._create_macro(data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list, spin_id=spin_id)
