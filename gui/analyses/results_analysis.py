###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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

# Python module imports.
from os import sep

# relax module imports.
from generic_fns.mol_res_spin import spin_loop
from status import Status; status = Status()


def color_code_noe(target_dir, pdb_file):
    """Create PyMol Macro for NOE colouring."""

    # Open the macro file.
    file = open(target_dir + sep + 'noe.pml', 'w')

    # PDB loading.
    if pdb_file:
        file.write("load " + pdb_file + '\n')

    # PyMOL set up commands.
    file.write("bg_color white\n")
    file.write("color gray90\n")
    file.write("hide all\n")
    file.write("show ribbon\n")

    # Loop over the spins.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Skip spins with no data.
        if not hasattr(spin, 'noe') or spin.noe == None:
            continue

        # Ribbon colour.
        width = ((1.0 - spin.noe) * 2.0)
        colour = 1.0 - ((spin.noe)**3)
        colour = colour ** 3
        colour = 1.0 - colour

        # Write out the PyMOL commands.
        file.write("set_color resicolor%s, [0, %s, 1]\n" % (res_num, colour))
        file.write("color resicolor%s, resi %s\n" % (res_num, res_num))
        file.write("set_bond stick_radius, %s, resi %s\n" % (width, res_num))

    # Final PyMOL commands.
    file.write("hide all\n")
    file.write("show sticks, name C+N+CA\n")
    file.write("set stick_quality, 10\n")
    file.write("ray\n")

    # Close the macro.
    file.close()
