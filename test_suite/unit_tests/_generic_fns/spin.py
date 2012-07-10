###############################################################################
#                                                                             #
# Copyright (C) 2008-2009 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""Dummy spin module used for renaming the generic_fns.mol_res_spin fns."""

# relax module imports.
from generic_fns import mol_res_spin


copy = mol_res_spin.copy_spin
create = mol_res_spin.create_spin
create_pseudo = mol_res_spin.create_pseudo_spin
delete = mol_res_spin.delete_spin
display = mol_res_spin.display_spin
name = mol_res_spin.name_spin
number = mol_res_spin.number_spin
